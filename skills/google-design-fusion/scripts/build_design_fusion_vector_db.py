#!/usr/bin/env python3
"""Build a local, embedding-ready design knowledge base for this workspace.

The pipeline combines:
1. design.google sitemap pages parsed from Next.js `__NEXT_DATA__`
2. local awesome-design-md `DESIGN.md` and `README.md` files

The output is a self-contained folder with:
- raw page records
- chunked retrieval documents
- sparse hashed vectors
- simple stats and manifests
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
from xml.etree import ElementTree


SITE_MAP_URL = "https://design.google/sitemap.xml"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xml,application/xhtml+xml;q=0.9,*/*;q=0.8",
}
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)
CANONICAL_RE = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]{1,}")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
JINA_TITLE_RE = re.compile(r"^Title:\s*(.+)$", re.MULTILINE)
JINA_PUBLISHED_RE = re.compile(r"^Published Time:\s*(.+)$", re.MULTILINE)
JINA_MARKDOWN_RE = re.compile(r"^Markdown Content:\s*$", re.MULTILINE)

CONTAINER_TYPES = {
    "col_1",
    "col_2",
    "col_3",
    "col_4",
    "col_5",
    "row",
    "theme",
    "spacer",
    "empty",
}
TEXT_FIELDS = (
    "title",
    "description",
    "body",
    "caption",
    "transcript",
    "eyebrow",
    "label",
    "name",
)

EXTERNAL_REFERENCE_HOST_POLICIES = {
    "m3.material.io": "jina_markdown",
    "m2.material.io": "jina_markdown",
    "research.google": "jina_markdown",
    "fonts.googleblog.com": "jina_markdown",
    "developers.google.com": "jina_markdown",
    "developers.googleblog.com": "jina_markdown",
    "pair.withgoogle.com": "jina_markdown",
    "googledesignmethod.libsyn.com": "direct_html",
    "medium.com": "jina_markdown",
    "r.jina.ai": "jina_markdown",
}

EXTERNAL_REFERENCE_DENYLIST = {
    "www.youtube.com",
    "youtube.com",
    "design-notes.show",
    "fonts.google.com",
    "www.fonts.google.com",
}

EXPLICIT_EXTERNAL_REFERENCE_OVERRIDES = {
    "https://design.google/library/how-human-interaction-shaping-future-technology": "https://medium.com/google-design/how-human-interaction-is-shaping-the-future-of-technology-c7242d75142f",
    "https://design.google/library/participatory-machine-learning": "https://medium.com/people-ai-research/participatory-machine-learning-69b77f1e5e23",
    "https://design.google/library/you-can-say-again-role-repetition-conversation-design": "https://medium.com/google-design/you-can-say-that-again-the-role-of-repetition-in-conversation-design-55937ef0f0ba",
    "https://design.google/library/how-we-designed-it-io-action-google-assistant": "https://medium.com/google-developers/how-we-designed-it-the-google-i-o-18-action-for-the-google-assistant-9370ffbaf9b0",
    "https://design.google/library/people-ai-guidebook": "https://pair.withgoogle.com/guidebook-v2/chapters",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "root"


def normalize_text(value: str) -> str:
    if not value:
        return ""
    value = value.replace("\r\n", "\n")
    value = MARKDOWN_LINK_RE.sub(r"\1", value)
    value = HTML_TAG_RE.sub("", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r" ?\n ?", "\n", value)
    return value.strip()


def tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def normalize_url_for_compare(url: str) -> str:
    """Normalize URL for loose equality checks (drop query/fragment, normalize trailing slash)."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlsplit(url.strip())
    except ValueError:
        return url.strip()

    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urllib.parse.urlunsplit((scheme, netloc, path, "", ""))


def extract_canonical_url(html_text: str) -> str:
    match = CANONICAL_RE.search(html_text or "")
    if not match:
        return ""
    return normalize_text(html.unescape(match.group(1)))


def is_design_google_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    return parsed.netloc.lower() == "design.google"


def host_for_url(url: str) -> str:
    try:
        return urllib.parse.urlsplit(url).netloc.lower()
    except ValueError:
        return ""


def classify_redirect_to_home(*, requested_url: str, final_url: str, canonical_url: str, page_location: str) -> bool:
    requested_norm = normalize_url_for_compare(requested_url)
    final_norm = normalize_url_for_compare(final_url)
    canonical_norm = normalize_url_for_compare(canonical_url)

    def is_home(norm: str) -> bool:
        if not norm:
            return False
        try:
            parsed = urllib.parse.urlsplit(norm)
        except ValueError:
            return False
        return parsed.netloc.lower() == "design.google" and (parsed.path or "/") == "/"

    def requested_is_home(norm: str) -> bool:
        if not norm:
            return False
        try:
            parsed = urllib.parse.urlsplit(norm)
        except ValueError:
            return False
        return (parsed.netloc.lower() == "design.google") and ((parsed.path or "/") == "/")

    # Hard redirect: final URL is home but requested is not.
    if is_home(final_norm) and not requested_is_home(requested_norm):
        return True

    # Soft redirect: canonical points to home, or Next.js page location says "/" while URL is not home.
    if canonical_norm and is_home(canonical_norm) and not requested_is_home(requested_norm):
        return True
    if (page_location or "") == "/" and not requested_is_home(requested_norm):
        return True
    return False


def fetch_url(url: str, timeout: int = 45, retries: int = 4, max_redirects: int = 10) -> Dict:
    """Fetch a URL while preserving redirect facts.

    Returns a dict with:
    - requested_url, final_url, status, headers, redirected, redirect_chain, text
    - used_fallback: e.g. "jina" when r.jina.ai is used for 403 Medium content.
    """
    last_error: Optional[Exception] = None
    used_fallback = ""
    requested_url = url
    for attempt in range(1, retries + 1):
        try:
            current_url = url
            redirect_chain: List[Dict[str, Union[str, int]]] = []
            for _ in range(max_redirects):
                request = urllib.request.Request(current_url, headers=REQUEST_HEADERS)
                try:
                    with urllib.request.urlopen(request, timeout=timeout) as response:
                        text = response.read().decode("utf-8", errors="replace")
                        final_url = response.geturl()
                        status = getattr(response, "status", 200)
                        headers = {k: v for k, v in response.headers.items()}
                        return {
                            "requested_url": requested_url,
                            "final_url": final_url,
                            "status": int(status),
                            "headers": headers,
                            "redirect_chain": redirect_chain,
                            "redirected": bool(redirect_chain)
                            or normalize_url_for_compare(final_url) != normalize_url_for_compare(requested_url),
                            "used_fallback": used_fallback,
                            "text": text,
                        }
                except urllib.error.HTTPError as exc:
                    location = exc.headers.get("Location")
                    if exc.code in {301, 302, 303, 307, 308} and location:
                        next_url = urllib.parse.urljoin(current_url, location)
                        redirect_chain.append({"code": int(exc.code), "from": current_url, "to": next_url})
                        current_url = next_url
                        continue
                    if exc.code == 403 and "medium.com" in current_url and not used_fallback:
                        current_url = "https://r.jina.ai/http://" + current_url.split("://", 1)[1]
                        used_fallback = "jina"
                        continue
                    raise
            raise RuntimeError(f"Too many redirects while fetching {requested_url}")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(0.6 * attempt)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(0.6 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}") from last_error


def fetch_text(url: str, timeout: int = 30, retries: int = 3) -> str:
    return fetch_url(url, timeout=timeout, retries=retries)["text"]


def parse_sitemap(xml_text: str) -> List[Dict[str, str]]:
    root = ElementTree.fromstring(xml_text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    pages: List[Dict[str, str]] = []
    for node in root.findall("sm:url", ns):
        loc = node.findtext("sm:loc", default="", namespaces=ns).strip()
        lastmod = node.findtext("sm:lastmod", default="", namespaces=ns).strip()
        if loc.startswith("https://design.google/"):
            pages.append({"url": loc, "lastmod": lastmod})
    seen = set()
    deduped = []
    for page in pages:
        if page["url"] in seen:
            continue
        seen.add(page["url"])
        deduped.append(page)
    return deduped


def extract_next_data(html_text: str) -> Dict:
    match = NEXT_DATA_RE.search(html_text)
    if not match:
        raise ValueError("Could not locate __NEXT_DATA__")
    return json.loads(match.group(1))


def extract_generic_title(html_text: str) -> str:
    jina_title = JINA_TITLE_RE.search(html_text or "")
    if jina_title:
        return normalize_text(html.unescape(jina_title.group(1)))
    title_match = re.search(r"<title>(.*?)</title>", html_text, re.DOTALL | re.IGNORECASE)
    if title_match:
        return normalize_text(html.unescape(title_match.group(1)))
    first_heading = re.search(r"^#\s+(.*)$", html_text, re.MULTILINE)
    if first_heading:
        return normalize_text(first_heading.group(1))
    return "Untitled"


def extract_generic_description(html_text: str) -> str:
    published = JINA_PUBLISHED_RE.search(html_text or "")
    if published:
        return normalize_text(f"Published Time: {html.unescape(published.group(1))}")
    meta_match = re.search(
        r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
        html_text,
        re.IGNORECASE,
    )
    if meta_match:
        return normalize_text(html.unescape(meta_match.group(1)))
    lines = [normalize_text(line) for line in html_text.splitlines()]
    body_lines = [line for line in lines if len(line) > 40]
    return body_lines[0] if body_lines else ""


def extract_generic_body(html_text: str) -> List[str]:
    markdown_marker = JINA_MARKDOWN_RE.search(html_text or "")
    if markdown_marker:
        markdown_text = html_text[markdown_marker.end() :].strip()
        lines = [normalize_text(line) for line in markdown_text.splitlines()]
        return [
            line
            for line in lines
            if len(line) > 40
            and not line.startswith(("Warning:", "URL Source:", "Title:", "Published Time:"))
            and "About this page" not in line
        ]
    if html_text.lstrip().startswith("Title:"):
        lines = [normalize_text(line) for line in html_text.splitlines()]
        return [
            line
            for line in lines
            if len(line) > 30
            and not line.startswith(("URL Source:", "Markdown Content:", "Title:", "Published Time:"))
            and "About this page" not in line
        ]

    scrubbed = re.sub(r"<script.*?</script>", " ", html_text, flags=re.DOTALL | re.IGNORECASE)
    scrubbed = re.sub(r"<style.*?</style>", " ", scrubbed, flags=re.DOTALL | re.IGNORECASE)
    scrubbed = re.sub(r"<noscript.*?</noscript>", " ", scrubbed, flags=re.DOTALL | re.IGNORECASE)
    scrubbed = HTML_TAG_RE.sub("\n", scrubbed)
    scrubbed = html.unescape(scrubbed)
    paragraphs = [normalize_text(part) for part in scrubbed.split("\n")]
    return [paragraph for paragraph in paragraphs if len(paragraph) > 40]


def derive_page_kind(location: str) -> str:
    if location == "/":
        return "home"
    if location.startswith("/library/"):
        return "library"
    if location.startswith("/category/"):
        return "category"
    return location.strip("/").replace("/", "_") or "page"


def collect_segment(
    segments: List[Dict[str, str]],
    seen: set,
    *,
    kind: str,
    text: str,
    heading: str,
    block_type: str,
) -> None:
    normalized = normalize_text(text)
    if len(normalized) < 12:
        return
    signature = (kind, heading, normalized)
    if signature in seen:
        return
    seen.add(signature)
    segments.append(
        {
            "kind": kind,
            "heading": heading.strip(),
            "block_type": block_type,
            "text": normalized,
        }
    )


def extract_segments(body: Sequence[Dict], page_title: str) -> List[Dict[str, str]]:
    segments: List[Dict[str, str]] = []
    seen = set()
    state = {"heading": page_title}

    def walk(item: Dict) -> None:
        if not isinstance(item, dict):
            return
        block_type = item.get("type", "unknown")
        value = item.get("value") or {}

        if block_type in CONTAINER_TYPES:
            for child in value.get("content", []):
                walk(child)
            return

        if "content" in value and isinstance(value["content"], list):
            for child in value["content"]:
                walk(child)

        if block_type == "title":
            title = normalize_text(value.get("title", ""))
            description = normalize_text(value.get("description", ""))
            if title:
                state["heading"] = title
                collect_segment(
                    segments,
                    seen,
                    kind="heading",
                    text="\n\n".join(part for part in (title, description) if part),
                    heading=title,
                    block_type=block_type,
                )
            return

        if block_type == "text":
            collect_segment(
                segments,
                seen,
                kind="body",
                text=value.get("body", ""),
                heading=state["heading"],
                block_type=block_type,
            )
            return

        if block_type == "feature":
            feature_parts = []
            for field in ("title", "description"):
                raw = value.get(field, "")
                cleaned = normalize_text(raw)
                if cleaned:
                    feature_parts.append(cleaned)
            category_name = normalize_text((value.get("category") or {}).get("name", ""))
            if category_name:
                feature_parts.append(f"Category: {category_name}")
            primary_tag = normalize_text((value.get("primary_tag") or {}).get("name", ""))
            if primary_tag:
                feature_parts.append(f"Primary tag: {primary_tag}")
            primary_link = value.get("primary_link") or {}
            label = normalize_text(primary_link.get("label", ""))
            url = normalize_text(primary_link.get("url", ""))
            if label and url:
                feature_parts.append(f"Primary link: {label} ({url})")
            collect_segment(
                segments,
                seen,
                kind="feature",
                text="\n".join(feature_parts),
                heading=state["heading"],
                block_type=block_type,
            )
            return

        if block_type == "image":
            image_parts = []
            for field in ("alt", "caption", "source"):
                raw = value.get(field, "")
                cleaned = normalize_text(raw)
                if cleaned:
                    image_parts.append(cleaned)
            collect_segment(
                segments,
                seen,
                kind="media",
                text="\n".join(image_parts),
                heading=state["heading"],
                block_type=block_type,
            )
            return

        if block_type == "video":
            video_parts = []
            for field in ("title", "caption", "transcript"):
                raw = value.get(field, "")
                cleaned = normalize_text(raw)
                if cleaned:
                    video_parts.append(cleaned)
            collect_segment(
                segments,
                seen,
                kind="media",
                text="\n".join(video_parts),
                heading=state["heading"],
                block_type=block_type,
            )
            return

        generic_parts = []
        for field in TEXT_FIELDS:
            raw = value.get(field, "")
            cleaned = normalize_text(raw)
            if cleaned:
                generic_parts.append(cleaned)
        if generic_parts:
            collect_segment(
                segments,
                seen,
                kind="generic",
                text="\n".join(generic_parts),
                heading=state["heading"],
                block_type=block_type,
            )

    for block in body:
        walk(block)
    return segments


def chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs:
        return []
    chunks: List[str] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = paragraph if not buffer else f"{buffer}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
        if len(paragraph) <= max_chars:
            buffer = paragraph
            continue
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        sentence_buffer = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence_candidate = sentence if not sentence_buffer else f"{sentence_buffer} {sentence}"
            if len(sentence_candidate) <= max_chars:
                sentence_buffer = sentence_candidate
            else:
                if sentence_buffer:
                    chunks.append(sentence_buffer)
                sentence_buffer = sentence
        buffer = sentence_buffer
    if buffer:
        chunks.append(buffer)
    return chunks


def build_page_record(sitemap_entry: Dict[str, str], next_data: Dict) -> Dict:
    page_props = next_data["props"]["pageProps"]
    page = page_props.get("page") or {}
    location = page.get("location") or sitemap_entry["url"].replace("https://design.google", "") or "/"
    url = page_props.get("url") or sitemap_entry["url"]
    contributors = [person.get("name", "").strip() for person in page.get("contributors", []) if person.get("name")]

    # IMPORTANT: use per-page metadata (page.tags / page.data.category) rather than global site tags.
    raw_tags = page.get("tags") or []
    tags: List[str] = []
    if isinstance(raw_tags, list):
        for tag in raw_tags:
            if isinstance(tag, str):
                cleaned = normalize_text(tag)
                if cleaned:
                    tags.append(cleaned)
            elif isinstance(tag, dict):
                name = normalize_text(tag.get("name", ""))
                if name:
                    tags.append(name)
    tags = [value for value in tags if value]

    raw_category = (page.get("data") or {}).get("category")
    category = ""
    if isinstance(raw_category, str):
        category = normalize_text(raw_category)
    elif isinstance(raw_category, dict):
        category = normalize_text(raw_category.get("name", ""))
    segments = extract_segments((page.get("data") or {}).get("body", []), page.get("title", "Untitled"))

    summary_lines = [page.get("title", "Untitled")]
    if page.get("description"):
        summary_lines.append(page["description"])
    if category:
        summary_lines.append(f"Category: {category}")
    if tags:
        summary_lines.append(f"Tags: {', '.join(tags[:12])}")
    if contributors:
        summary_lines.append(f"Contributors: {', '.join(contributors[:8])}")

    return {
        "source_family": "design.google",
        "url": url,
        "location": location,
        "page_kind": derive_page_kind(location),
        "title": page.get("title", "Untitled"),
        "description": normalize_text(page.get("description", "")),
        "publish_at": page.get("publish_at", ""),
        "lastmod": sitemap_entry.get("lastmod", ""),
        "category": category,
        "tags": tags,
        "contributors": contributors,
        "summary": normalize_text("\n".join(summary_lines)),
        "segments": segments,
    }


def build_generic_record(sitemap_entry: Dict[str, str], html_text: str) -> Dict:
    location = sitemap_entry["url"].replace("https://design.google", "") or "/"
    title = extract_generic_title(html_text)
    description = extract_generic_description(html_text)
    paragraphs = extract_generic_body(html_text)
    segments = [
        {
            "kind": "body",
            "heading": title,
            "block_type": "generic_html",
            "text": paragraph,
        }
        for paragraph in paragraphs[:24]
    ]
    return {
        "source_family": "design.google",
        "url": sitemap_entry["url"],
        "location": location,
        "page_kind": derive_page_kind(location),
        "title": title,
        "description": description,
        "publish_at": "",
        "lastmod": sitemap_entry.get("lastmod", ""),
        "category": "",
        "tags": [],
        "contributors": [],
        "summary": normalize_text("\n".join(part for part in (title, description) if part)),
        "segments": segments,
    }


def external_reference_policy(final_url: str) -> str:
    host = host_for_url(final_url)
    if host in EXTERNAL_REFERENCE_DENYLIST:
        return "blocked"
    return EXTERNAL_REFERENCE_HOST_POLICIES.get(host, "blocked")


def fetch_external_reference_text(final_url: str, current_html_text: str, policy: str) -> Tuple[str, str]:
    if policy == "direct_html":
        return current_html_text, final_url
    if policy == "jina_markdown":
        if host_for_url(final_url) == "r.jina.ai":
            return current_html_text, final_url
        target_url = "https://r.jina.ai/http://" + final_url.split("://", 1)[1]
        return fetch_text(target_url), target_url
    return "", final_url


def build_external_reference_record(
    sitemap_entry: Dict[str, str],
    *,
    requested_url: str,
    final_url: str,
    fetched_url: str,
    html_text: str,
) -> Dict:
    title = extract_generic_title(html_text)
    description = extract_generic_description(html_text)
    paragraphs = extract_generic_body(html_text)
    if not title or len(paragraphs) < 2:
        raise ValueError("External reference did not yield enough meaningful text.")
    if any(block_phrase in title.lower() for block_phrase in ("about this page", "too many requests")):
        raise ValueError("External reference appears to be a block/captcha page.")

    location = requested_url.replace("https://design.google", "") or requested_url
    source_domain = host_for_url(final_url)
    summary_lines = [title]
    if description:
        summary_lines.append(description)
    summary_lines.append(f"External source: {source_domain}")
    summary_lines.append(f"Requested from: {requested_url}")
    segments = [
        {
            "kind": "body",
            "heading": title,
            "block_type": "external_reference",
            "text": paragraph,
        }
        for paragraph in paragraphs[:24]
    ]

    return {
        "source_family": "design.google-external",
        "url": final_url,
        "external_source_url": final_url,
        "external_fetch_url": fetched_url,
        "external_source_domain": source_domain,
        "location": location,
        "page_kind": "external_reference",
        "title": title,
        "description": description,
        "publish_at": "",
        "lastmod": sitemap_entry.get("lastmod", ""),
        "category": "External reference",
        "tags": [],
        "contributors": [],
        "summary": normalize_text("\n".join(summary_lines)),
        "segments": segments,
    }


def try_explicit_external_override(sitemap_entry: Dict[str, str], requested_url: str) -> Optional[Tuple[Dict, Dict]]:
    override_url = EXPLICIT_EXTERNAL_REFERENCE_OVERRIDES.get(requested_url)
    if not override_url:
        return None

    policy = external_reference_policy(override_url)
    if policy == "blocked":
        return None

    try:
        response = fetch_url(override_url)
        external_text, fetched_url = fetch_external_reference_text(override_url, response["text"], policy)
        record = build_external_reference_record(
            sitemap_entry,
            requested_url=requested_url,
            final_url=override_url,
            fetched_url=fetched_url,
            html_text=external_text,
        )
        record["requested_url"] = requested_url
        record["final_url"] = override_url
        record["redirect_chain"] = response.get("redirect_chain", [])
        record["crawl_outcome"] = "external_ingested"
        record["include_in_index"] = True
        record["canonical_url"] = ""
        record["http_status"] = response.get("status")
        crawl = {
            "requested_url": requested_url,
            "final_url": override_url,
            "status": response.get("status"),
            "redirect_chain": response.get("redirect_chain", []),
            "canonical_url": "",
            "record_kind": "external_reference",
            "include_in_index": True,
            "outcome": "external_ingested",
            "note": f"Used explicit override target: {override_url}",
            "lastmod": sitemap_entry.get("lastmod", ""),
        }
        return record, crawl
    except Exception as exc:
        crawl = {
            "requested_url": requested_url,
            "final_url": override_url,
            "status": None,
            "redirect_chain": [],
            "canonical_url": "",
            "record_kind": "none",
            "include_in_index": False,
            "outcome": "external_ingest_failed",
            "note": f"Explicit override failed: {exc}",
            "lastmod": sitemap_entry.get("lastmod", ""),
        }
        record = build_crawl_placeholder_record(
            sitemap_entry,
            requested_url=requested_url,
            final_url=override_url,
            outcome="external_ingest_failed",
            note=f"Explicit override failed: {exc}",
        )
        return record, crawl


def build_crawl_placeholder_record(sitemap_entry: Dict[str, str], *, requested_url: str, final_url: str, outcome: str, note: str) -> Dict:
    location = requested_url.replace("https://design.google", "") or "/"
    title = f"Unresolved ({outcome})"
    summary = normalize_text("\n".join(part for part in (requested_url, final_url, note) if part))
    return {
        "source_family": "design.google",
        "url": final_url or requested_url,
        "requested_url": requested_url,
        "final_url": final_url or requested_url,
        "redirect_chain": [],
        "crawl_outcome": outcome,
        "include_in_index": False,
        "location": location,
        "page_kind": derive_page_kind(location),
        "title": title,
        "description": "",
        "publish_at": "",
        "lastmod": sitemap_entry.get("lastmod", ""),
        "category": "",
        "tags": [],
        "contributors": [],
        "summary": summary,
        "segments": [],
    }


def fetch_design_google_records(sitemap_entries: Sequence[Dict[str, str]], workers: int) -> Tuple[List[Dict], Dict]:
    records: List[Dict] = []
    crawl_rows: List[Dict] = []
    errors: List[str] = []

    def job(entry: Dict[str, str]) -> Tuple[Dict, Dict]:
        requested_url = entry["url"]
        try:
            response = fetch_url(requested_url)
        except Exception as exc:
            override_result = try_explicit_external_override(entry, requested_url)
            if override_result is not None:
                return override_result
            record = build_crawl_placeholder_record(
                entry,
                requested_url=requested_url,
                final_url=requested_url,
                outcome="fetch_error",
                note=str(exc),
            )
            crawl = {
                "requested_url": requested_url,
                "final_url": requested_url,
                "status": None,
                "redirect_chain": [],
                "canonical_url": "",
                "record_kind": "none",
                "include_in_index": False,
                "outcome": "fetch_error",
                "note": str(exc),
                "lastmod": entry.get("lastmod", ""),
            }
            return record, crawl

        html_text = response["text"]
        final_url = response.get("final_url", requested_url) or requested_url
        status = response.get("status")
        redirect_chain = response.get("redirect_chain", [])
        canonical_url = extract_canonical_url(html_text)

        next_data: Optional[Dict[str, Any]] = None
        page_location = ""
        record_kind = "generic_html"
        outcome = "generic_fallback"
        include_in_index = True
        note = ""

        try:
            next_data = extract_next_data(html_text)
            page_props = next_data.get("props", {}).get("pageProps", {})
            page = page_props.get("page") or {}
            page_location = page.get("location") or ""
            record_kind = "next_data"
            outcome = "ok"
        except Exception as exc:
            next_data = None
            record_kind = "generic_html"
            outcome = "generic_fallback"
            note = f"__NEXT_DATA__ missing/invalid: {exc}"

        if classify_redirect_to_home(
            requested_url=requested_url,
            final_url=final_url,
            canonical_url=canonical_url,
            page_location=page_location,
        ):
            outcome = "redirect_to_home"
            include_in_index = False
            record_kind = "none"
            record = build_crawl_placeholder_record(
                entry,
                requested_url=requested_url,
                final_url=final_url,
                outcome=outcome,
                note="Redirected (hard/soft) to design.google home; excluded from corpus.",
            )
        elif not is_design_google_url(final_url):
            policy = external_reference_policy(final_url)
            if policy != "blocked":
                try:
                    external_text, fetched_url = fetch_external_reference_text(final_url, html_text, policy)
                    record = build_external_reference_record(
                        entry,
                        requested_url=requested_url,
                        final_url=final_url,
                        fetched_url=fetched_url,
                        html_text=external_text,
                    )
                    include_in_index = True
                    record_kind = "external_reference"
                    outcome = "external_ingested"
                    note = f"External reference ingested via {policy}."
                except Exception as exc:
                    override_result = try_explicit_external_override(entry, requested_url)
                    if override_result is not None:
                        return override_result
                    outcome = "external_ingest_failed"
                    include_in_index = False
                    record_kind = "none"
                    note = str(exc)
                    record = build_crawl_placeholder_record(
                        entry,
                        requested_url=requested_url,
                        final_url=final_url,
                        outcome=outcome,
                        note=note,
                    )
            else:
                outcome = "external_redirect"
                include_in_index = False
                record_kind = "none"
                note = f"External source blocked from ingestion: {host_for_url(final_url)}"
                record = build_crawl_placeholder_record(
                    entry,
                    requested_url=requested_url,
                    final_url=final_url,
                    outcome=outcome,
                    note=note,
                )
        else:
            try:
                if next_data is not None and record_kind == "next_data":
                    record = build_page_record(entry, next_data)
                else:
                    record = build_generic_record(entry, html_text)
                # Canonical mismatch is a warning: keep record indexable, but record the mismatch explicitly.
                if canonical_url and normalize_url_for_compare(canonical_url) not in {
                    normalize_url_for_compare(requested_url),
                    normalize_url_for_compare(final_url),
                }:
                    outcome = "canonical_mismatch"
                    note = f"canonical={canonical_url}"
            except Exception as exc:
                include_in_index = False
                record_kind = "none"
                outcome = "parse_error"
                note = str(exc)
                record = build_crawl_placeholder_record(
                    entry,
                    requested_url=requested_url,
                    final_url=final_url,
                    outcome=outcome,
                    note=note,
                )

        record["requested_url"] = requested_url
        record["final_url"] = final_url
        record["redirect_chain"] = redirect_chain
        record["crawl_outcome"] = outcome
        record["include_in_index"] = bool(include_in_index)
        record["canonical_url"] = canonical_url
        record["http_status"] = status

        crawl = {
            "requested_url": requested_url,
            "final_url": final_url,
            "status": status,
            "redirect_chain": redirect_chain,
            "canonical_url": canonical_url,
            "record_kind": record_kind,
            "include_in_index": bool(include_in_index),
            "outcome": outcome,
            "note": note,
            "lastmod": entry.get("lastmod", ""),
        }
        return record, crawl

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(job, entry): entry for entry in sitemap_entries}
        for future in as_completed(future_map):
            entry = future_map[future]
            try:
                record, crawl = future.result()
                records.append(record)
                crawl_rows.append(crawl)
            except Exception as exc:
                errors.append(f"{entry['url']} :: {exc}")

    if errors:
        preview = "\n".join(errors[:20])
        print(f"[WARN] {len(errors)} pages failed during crawl:\n{preview}", file=sys.stderr)

    summary_counts = Counter(row.get("outcome", "unknown") for row in crawl_rows)
    include_count = sum(1 for row in crawl_rows if row.get("include_in_index"))
    unresolved_rows = [row for row in crawl_rows if not row.get("include_in_index")]
    issue_rows = [row for row in crawl_rows if row.get("outcome") != "ok"]
    crawl_summary = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "sitemap_entry_count": len(sitemap_entries),
        "record_count": len(records),
        "indexable_record_count": include_count,
        "outcomes": dict(sorted(summary_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "unresolved_count": len(unresolved_rows),
        "issue_count": len(issue_rows),
        "unresolved": sorted(unresolved_rows, key=lambda r: (r.get("outcome", ""), r.get("requested_url", ""))),
        "issues": sorted(issue_rows, key=lambda r: (r.get("outcome", ""), r.get("requested_url", ""))),
    }

    return sorted(records, key=lambda item: item.get("requested_url") or item["url"]), {
        "summary": crawl_summary,
        "rows": sorted(crawl_rows, key=lambda row: row.get("requested_url", "")),
    }


def split_markdown_sections(text: str) -> List[Dict[str, str]]:
    sections: List[Dict[str, str]] = []
    current_heading = "Document Overview"
    buffer: List[str] = []

    for line in text.splitlines():
        heading_match = HEADING_RE.match(line)
        if heading_match:
            if buffer:
                section_text = normalize_text("\n".join(buffer))
                if section_text:
                    sections.append({"heading": current_heading, "text": section_text})
            current_heading = normalize_text(heading_match.group(2))
            buffer = []
            continue
        buffer.append(line)

    if buffer:
        section_text = normalize_text("\n".join(buffer))
        if section_text:
            sections.append({"heading": current_heading, "text": section_text})

    return sections


def load_awesome_design_records(awesome_root: Path) -> List[Dict]:
    design_root = awesome_root / "design-md"
    if not design_root.exists():
        print(f"[WARN] awesome-design-md root not found: {design_root}", file=sys.stderr)
        return []

    records: List[Dict] = []
    for brand_dir in sorted(path for path in design_root.iterdir() if path.is_dir()):
        design_file = brand_dir / "DESIGN.md"
        readme_file = brand_dir / "README.md"
        if not design_file.exists():
            continue

        design_text = design_file.read_text(encoding="utf-8")
        summary = ""
        if readme_file.exists():
            summary = normalize_text(readme_file.read_text(encoding="utf-8"))
        sections = split_markdown_sections(design_text)
        records.append(
            {
                "source_family": "awesome-design-md",
                "url": "",
                "location": str(design_file.relative_to(awesome_root)).replace("\\", "/"),
                "page_kind": "style_reference",
                "title": brand_dir.name,
                "description": summary.split("\n", 1)[0] if summary else "",
                "publish_at": "",
                "lastmod": "",
                "category": "",
                "tags": [],
                "contributors": [],
                "summary": normalize_text(f"{brand_dir.name}\n{summary}"),
                "segments": [
                    {
                        "kind": "style_section",
                        "heading": section["heading"],
                        "block_type": "markdown",
                        "text": section["text"],
                    }
                    for section in sections
                ],
            }
        )
    return records


def build_chunks(records: Sequence[Dict]) -> List[Dict]:
    chunks: List[Dict] = []
    for record in records:
        if not record.get("include_in_index", True):
            continue
        slug = slugify(record["location"] or record["title"])
        chunk_counter = 0

        chunks.append(
            {
                "chunk_id": f"{record['source_family']}::{slug}::summary",
                "source_family": record["source_family"],
                "url": record["url"],
                "location": record["location"],
                "page_kind": record["page_kind"],
                "title": record["title"],
                "heading": record["title"],
                "category": record.get("category", ""),
                "tags": record.get("tags", []),
                "publish_at": record.get("publish_at", ""),
                "lastmod": record.get("lastmod", ""),
                "contributors": record.get("contributors", []),
                "chunk_kind": "summary",
                "text": record["summary"],
            }
        )

        for segment in record["segments"]:
            parts = chunk_text(segment["text"])
            for part in parts:
                chunk_counter += 1
                chunks.append(
                    {
                        "chunk_id": f"{record['source_family']}::{slug}::{chunk_counter:04d}",
                        "source_family": record["source_family"],
                        "url": record["url"],
                        "location": record["location"],
                        "page_kind": record["page_kind"],
                        "title": record["title"],
                        "heading": segment["heading"] or record["title"],
                        "category": record.get("category", ""),
                        "tags": record.get("tags", []),
                        "publish_at": record.get("publish_at", ""),
                        "lastmod": record.get("lastmod", ""),
                        "contributors": record.get("contributors", []),
                        "chunk_kind": segment["kind"],
                        "block_type": segment["block_type"],
                        "text": part,
                    }
                )
    return chunks


def build_sparse_vectors(chunks: Sequence[Dict], dimensions: int, top_dims: int) -> Dict:
    document_tokens: List[List[str]] = []
    document_frequency: Counter[str] = Counter()

    for chunk in chunks:
        tokens = tokenize(chunk["text"])
        document_tokens.append(tokens)
        document_frequency.update(set(tokens))

    doc_count = max(len(chunks), 1)
    idf = {
        token: math.log((1.0 + doc_count) / (1.0 + frequency)) + 1.0
        for token, frequency in document_frequency.items()
    }

    for chunk, tokens in zip(chunks, document_tokens):
        tf = Counter(tokens)
        buckets: Dict[int, float] = defaultdict(float)
        for token, count in tf.items():
            weight = (1.0 + math.log(count)) * idf[token]
            bucket = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16) % dimensions
            buckets[bucket] += weight

        ranked = sorted(buckets.items(), key=lambda item: abs(item[1]), reverse=True)[:top_dims]
        norm = math.sqrt(sum(weight * weight for _, weight in ranked)) or 1.0
        chunk["vector"] = [[bucket, round(weight / norm, 6)] for bucket, weight in sorted(ranked)]
        chunk["token_count"] = len(tokens)

    return {
        "dimensions": dimensions,
        "top_dims": top_dims,
        "avg_tokens_per_chunk": round(sum(len(tokens) for tokens in document_tokens) / doc_count, 2),
        "idf": idf,
    }


def write_json(path: Path, payload: Dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_catalog_markdown(records: Sequence[Dict], chunks: Sequence[Dict]) -> str:
    source_counts = Counter(record["source_family"] for record in records)
    page_kind_counts = Counter(
        record["page_kind"] for record in records if record["source_family"] in {"design.google", "design.google-external"}
    )
    category_counts = Counter(
        record["category"]
        for record in records
        if record["source_family"] in {"design.google", "design.google-external"} and record["category"]
    )
    newest_pages = sorted(
        (record for record in records if record["source_family"] == "design.google" and record["publish_at"]),
        key=lambda item: item["publish_at"],
        reverse=True,
    )[:12]

    lines = [
        "# Google Design Fusion Vector Library",
        "",
        f"- Generated: {dt.datetime.utcnow().isoformat()}Z",
        f"- Source records: {len(records)}",
        f"- Retrieval chunks: {len(chunks)}",
        f"- design.google pages: {source_counts.get('design.google', 0)}",
        f"- design.google external references: {source_counts.get('design.google-external', 0)}",
        f"- awesome-design-md references: {source_counts.get('awesome-design-md', 0)}",
        "",
        "## design.google page kinds",
        "",
    ]

    for kind, count in sorted(page_kind_counts.items()):
        lines.append(f"- `{kind}`: {count}")

    lines.extend(["", "## design.google categories", ""])
    for category, count in category_counts.most_common():
        lines.append(f"- `{category}`: {count}")

    lines.extend(["", "## Recent design.google pages", ""])
    for record in newest_pages:
        lines.append(f"- `{record['publish_at'][:10]}` [{record['title']}]({record['url']})")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "- `manifest.json`: build settings and counts",
            "- `index.json`: sparse-vector indexing data",
            "- `records.jsonl`: page-level source records",
            "- `chunks.jsonl`: retrieval-ready chunks with vectors",
            "- `site-map.json`: design.google sitemap entries",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Google Design fusion vector library.")
    parser.add_argument(
        "--output-root",
        default="",
        help="Output folder for the vector library. Defaults to the workspace google-design-vector-db folder.",
    )
    parser.add_argument(
        "--awesome-root",
        default="",
        help="Path to the awesome-design-md repository. Defaults to the sibling workspace folder.",
    )
    parser.add_argument("--workers", type=int, default=6, help="Concurrent fetch workers for design.google pages.")
    parser.add_argument(
        "--limit-pages",
        type=int,
        default=0,
        help="Limit how many design.google sitemap entries to crawl (0 = all). Useful for quick validation runs.",
    )
    parser.add_argument("--dimensions", type=int, default=768, help="Sparse vector dimensionality.")
    parser.add_argument("--top-dims", type=int, default=64, help="How many vector buckets to keep per chunk.")
    args = parser.parse_args()

    workspace_root = Path(__file__).resolve().parents[3]
    output_root = Path(args.output_root).resolve() if args.output_root else workspace_root / "google-design-vector-db"
    awesome_root = Path(args.awesome_root).resolve() if args.awesome_root else workspace_root.parent / "awesome-design-md"

    output_root.mkdir(parents=True, exist_ok=True)

    print("[1/5] Fetching design.google sitemap...")
    sitemap_entries = parse_sitemap(fetch_text(SITE_MAP_URL))
    if args.limit_pages and args.limit_pages > 0:
        sitemap_entries = sitemap_entries[: args.limit_pages]
    write_json(output_root / "site-map.json", {"entries": sitemap_entries})

    print(f"[2/5] Crawling {len(sitemap_entries)} design.google pages...")
    google_records, crawl_report = fetch_design_google_records(sitemap_entries, args.workers)
    write_jsonl(output_root / "crawl-report.jsonl", crawl_report["rows"])
    write_json(output_root / "crawl-summary.json", crawl_report["summary"])

    print("[3/5] Loading awesome-design-md references...")
    awesome_records = load_awesome_design_records(awesome_root)

    # Keep all crawl outcomes in records.jsonl for coverage audits,
    # but only index the ones marked as indexable.
    indexable_google_records = [record for record in google_records if record.get("include_in_index", True)]
    all_records = google_records + awesome_records
    records_for_index = indexable_google_records + awesome_records
    write_jsonl(output_root / "records.jsonl", all_records)

    print("[4/5] Chunking and vectorizing corpus...")
    chunks = build_chunks(records_for_index)
    index = build_sparse_vectors(chunks, args.dimensions, args.top_dims)
    write_jsonl(output_root / "chunks.jsonl", chunks)

    print("[5/5] Writing manifests...")
    outcomes = crawl_report["summary"].get("outcomes", {})
    manifest = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "workspace_root": str(workspace_root),
        "output_root": str(output_root),
        "design_google_sitemap_entry_count": len(sitemap_entries),
        "design_google_record_count": len(google_records),
        "design_google_indexable_record_count": len(indexable_google_records),
        "design_google_outcomes": outcomes,
        "design_google_coverage": {
            "indexable_ratio": round((len(indexable_google_records) / max(len(sitemap_entries), 1)), 4),
            "ok_ratio": round((float(outcomes.get("ok", 0)) / max(len(sitemap_entries), 1)), 4),
            "generic_fallback_ratio": round((float(outcomes.get("generic_fallback", 0)) / max(len(sitemap_entries), 1)), 4),
        },
        "design_google_external_reference_count": sum(
            1
            for record in google_records
            if record.get("source_family") == "design.google-external" and record.get("include_in_index")
        ),
        "awesome_design_record_count": len(awesome_records),
        "chunk_count": len(chunks),
        "dimensions": args.dimensions,
        "top_dims": args.top_dims,
    }
    write_json(output_root / "manifest.json", manifest)
    write_json(output_root / "index.json", index)
    (output_root / "README.md").write_text(build_catalog_markdown(records_for_index, chunks), encoding="utf-8")

    print(f"Vector library ready at {output_root}")
    print(f"- design.google records (all outcomes): {len(google_records)}")
    print(f"- design.google indexable records: {len(indexable_google_records)}")
    print(f"- awesome-design-md records: {len(awesome_records)}")
    print(f"- chunks: {len(chunks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

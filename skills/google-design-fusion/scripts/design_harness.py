#!/usr/bin/env python3
"""Retrieval harness for the Google Design fusion vector library."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import re
import sys
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True


TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]{1,}")

PHASE_GUIDANCE = {
    "research": "Map the design space before inventing UI.",
    "concept": "Prefer concept families with clear contrast, not minor variants of the same idea.",
    "wireframe": "Lock hierarchy, flows, and interaction rhythm before decoration.",
    "ui": "Turn hierarchy into a distinctive surface system with disciplined typography and spacing.",
    "polish": "Refine motion, copy density, contrast, and empty states until the design feels intentional.",
    "audit": "Critique the design ruthlessly against anti-patterns, accessibility, and semantic clarity.",
}

DEFAULT_GUARDRAILS = [
    "Do not add decorative microcopy, fake helper notes, or tiny labels that do not earn their space.",
    "Do not use generic dashboard cards or placeholder metrics unless the product truly needs them.",
    "Do not layer multiple accent styles at once; choose one visual thesis and reinforce it consistently.",
    "Do not treat motion as decoration; every transition must guide attention or confirm causality.",
    "Do not bury the main action under secondary content or ornamental blocks.",
]


@dataclasses.dataclass(frozen=True)
class PhaseProfile:
    """Phase-specific retrieval behaviors.

    This is intentionally lightweight: we stay in hashed sparse-vector space and
    steer retrieval by (1) a phase "lens" query and (2) metadata weighting.
    """

    phase: str
    lens_terms: Tuple[str, ...]
    lens_alpha: float
    chunk_kind_weight: Dict[str, float]
    family_prior: Dict[str, float]


PHASE_PROFILES: Dict[str, PhaseProfile] = {
    "research": PhaseProfile(
        phase="research",
        lens_terms=(
            "case study",
            "process",
            "tradeoffs",
            "constraints",
            "user research",
            "system",
            "pattern",
            "principles",
        ),
        lens_alpha=0.12,
        chunk_kind_weight={"summary": 0.03, "heading": 0.01, "body": 0.0, "media": -0.02},
        family_prior={"design.google": 0.01},
    ),
    "concept": PhaseProfile(
        phase="concept",
        lens_terms=("concept", "direction", "visual language", "mood", "metaphor", "brand"),
        lens_alpha=0.10,
        chunk_kind_weight={"summary": 0.03, "heading": 0.01, "body": 0.0, "media": -0.02},
        family_prior={"design.google": 0.008},
    ),
    "wireframe": PhaseProfile(
        phase="wireframe",
        lens_terms=("hierarchy", "flow", "navigation", "forms", "error states", "empty states", "information architecture"),
        lens_alpha=0.12,
        chunk_kind_weight={"summary": 0.02, "heading": 0.01, "body": 0.0, "media": -0.02},
        family_prior={},
    ),
    "ui": PhaseProfile(
        phase="ui",
        lens_terms=("typography", "layout", "spacing", "grid", "component", "tokens", "interaction"),
        lens_alpha=0.10,
        chunk_kind_weight={"summary": 0.02, "heading": 0.01, "body": 0.0, "media": -0.01},
        family_prior={"awesome-design-md": 0.01},
    ),
    "polish": PhaseProfile(
        phase="polish",
        lens_terms=("motion", "microinteraction", "copy", "density", "contrast", "states", "edge cases"),
        lens_alpha=0.12,
        chunk_kind_weight={"summary": 0.02, "heading": 0.01, "body": 0.0, "media": -0.01},
        family_prior={"awesome-design-md": 0.008},
    ),
    "audit": PhaseProfile(
        phase="audit",
        lens_terms=(
            "accessibility",
            "a11y",
            "contrast",
            "keyboard",
            "focus",
            "semantics",
            "labels",
            "form errors",
            "validation",
            "empty states",
            "loading states",
            "error states",
            "anti-patterns",
            "checklist",
            "aria",
        ),
        # Audit must be a distinct retrieval strategy: stronger lens, stronger metadata steering.
        lens_alpha=0.35,
        chunk_kind_weight={"summary": 0.03, "heading": 0.01, "body": 0.01, "media": -0.08},
        family_prior={"design.google": 0.006},
    ),
}


@dataclasses.dataclass(frozen=True)
class CorpusStats:
    total_pages: int
    family_page_counts: Dict[str, int]
    tag_df_global: Dict[str, int]
    tag_df_by_family: Dict[str, Dict[str, int]]
    category_df_global: Dict[str, int]
    category_df_by_family: Dict[str, Dict[str, int]]


def tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def query_vector(tokens: Iterable[str], idf: Dict[str, float], dimensions: int) -> Dict[int, float]:
    tf = Counter(tokens)
    weights: Dict[int, float] = {}
    for token, count in tf.items():
        token_idf = idf.get(token, 1.0)
        bucket = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16) % dimensions
        weights[bucket] = weights.get(bucket, 0.0) + (1.0 + math.log(count)) * token_idf
    norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
    return {bucket: value / norm for bucket, value in weights.items()}


def sparse_dot(query: Dict[int, float], vector: List[List[float]]) -> float:
    return sum(query.get(int(bucket), 0.0) * float(weight) for bucket, weight in vector)


def _normalize_url_to_page_key(url: str) -> str:
    """Normalize URL into a stable page key for dedup/caps.

    Drops query/fragment, normalizes trailing slash. Keeps netloc+path.
    """
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlsplit(url.strip())
    except ValueError:
        return url.strip()

    netloc = (parsed.netloc or "").lower()
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    if netloc:
        return f"{netloc}{path}"
    return path


def chunk_final_url(chunk: Dict) -> str:
    return (chunk.get("final_url") or chunk.get("url_final") or chunk.get("url") or "").strip()


def chunk_requested_url(chunk: Dict) -> str:
    return (chunk.get("requested_url") or chunk.get("url_requested") or "").strip()


def chunk_location(chunk: Dict) -> str:
    location = (chunk.get("location") or "").strip()
    if location.startswith("http://") or location.startswith("https://"):
        return _normalize_url_to_page_key(location)
    return location


def page_key_from_chunk(chunk: Dict) -> str:
    # Prefer crawler-fixed URLs when available, then fall back to legacy fields.
    final_url = chunk_final_url(chunk)
    if final_url:
        return _normalize_url_to_page_key(final_url)
    location = chunk_location(chunk)
    if location:
        return location
    # Last resort: chunk id prefix tends to include a stable page slug.
    chunk_id = (chunk.get("chunk_id") or "").strip()
    if "::" in chunk_id:
        return chunk_id.split("::", 2)[1]
    return chunk_id or "<unknown>"


def chunk_page_tags(chunk: Dict) -> List[str]:
    # New crawler may emit page_tags; older builds use tags.
    raw = chunk.get("page_tags")
    if isinstance(raw, list):
        return [str(item) for item in raw if item]
    raw = chunk.get("tags")
    if isinstance(raw, list):
        return [str(item) for item in raw if item]
    return []


def chunk_page_category(chunk: Dict) -> str:
    raw = chunk.get("page_category")
    if isinstance(raw, str):
        return raw.strip()
    raw = chunk.get("category")
    if isinstance(raw, str):
        return raw.strip()
    return ""


def build_corpus_stats(chunks: Sequence[Dict]) -> CorpusStats:
    page_info: Dict[str, Dict[str, object]] = {}

    for chunk in chunks:
        page_key = page_key_from_chunk(chunk)
        family = (chunk.get("source_family") or "").strip() or "<unknown>"
        info = page_info.get(page_key)
        if not info:
            info = {"family": family, "tags": set(), "category": ""}
            page_info[page_key] = info

        tags_set = info["tags"]
        if isinstance(tags_set, set):
            tags_set.update(tag.strip().lower() for tag in chunk_page_tags(chunk) if str(tag).strip())

        category = info.get("category") or ""
        if not category:
            info["category"] = chunk_page_category(chunk).strip().lower()

    family_page_counts: Counter[str] = Counter()
    tag_df_global: Counter[str] = Counter()
    tag_df_by_family: Dict[str, Counter[str]] = {}
    category_df_global: Counter[str] = Counter()
    category_df_by_family: Dict[str, Counter[str]] = {}

    for info in page_info.values():
        family = str(info.get("family") or "<unknown>")
        family_page_counts[family] += 1
        tags = info.get("tags") or set()
        if isinstance(tags, set):
            for tag in tags:
                tag_df_global[str(tag)] += 1
                tag_df_by_family.setdefault(family, Counter())[str(tag)] += 1
        category = str(info.get("category") or "")
        if category:
            category_df_global[category] += 1
            category_df_by_family.setdefault(family, Counter())[category] += 1

    return CorpusStats(
        total_pages=len(page_info),
        family_page_counts=dict(family_page_counts),
        tag_df_global=dict(tag_df_global),
        tag_df_by_family={family: dict(counter) for family, counter in tag_df_by_family.items()},
        category_df_global=dict(category_df_global),
        category_df_by_family={family: dict(counter) for family, counter in category_df_by_family.items()},
    )


def _idf(total: int, df: int) -> float:
    # Smooth; always >= 0.
    return max(math.log((total + 1.0) / (df + 1.0)), 0.0)


def metadata_boost(chunk: Dict, tokens: List[str], phase: str, stats: CorpusStats) -> float:
    score = 0.0
    profile = PHASE_PROFILES.get(phase, PHASE_PROFILES["ui"])

    source_family = (chunk.get("source_family") or "").strip() or "<unknown>"
    chunk_kind = (chunk.get("chunk_kind") or "").strip()

    # Tiny family priors: used only as a tie-breaker, never as a primary scorer.
    score += profile.family_prior.get(source_family, 0.0)

    # Chunk-kind steering (audit should avoid media-heavy chunks).
    score += profile.chunk_kind_weight.get(chunk_kind, 0.0)

    title = (chunk.get("title") or "")
    heading = (chunk.get("heading") or "")
    category = chunk_page_category(chunk)
    tags = chunk_page_tags(chunk)

    field_tokens = set(tokenize(" ".join(part for part in (title, heading, category) if part)))
    overlap = len(set(tokens) & field_tokens)
    score += min(overlap * 0.03, 0.12)

    # Category match: prefer when the category is informative/rare for that family.
    if category:
        category_tokens = set(tokenize(category))
        if category_tokens & set(tokens):
            df_global = stats.category_df_global.get(category.strip().lower(), 0)
            df_family = stats.category_df_by_family.get(source_family, {}).get(category.strip().lower(), 0)
            fam_total = stats.family_page_counts.get(source_family, 0)
            rarity = min(_idf(stats.total_pages, df_global), _idf(fam_total, df_family) if fam_total else 0.0)
            score += min(rarity * 0.03, 0.09)

    # Tag match: downweight "global tag clouds" by rarity + cap + long-tag-list penalty.
    if tags:
        tag_multiplier = 1.0
        if len(tags) > 50:
            tag_multiplier = 0.2
        elif len(tags) > 20:
            tag_multiplier = 0.35

        query_token_set = set(tokens)
        matched: List[Tuple[float, str]] = []
        for tag in tags:
            tag_norm = str(tag).strip().lower()
            if not tag_norm:
                continue
            if not (set(tokenize(tag_norm)) & query_token_set):
                continue
            df_global = stats.tag_df_global.get(tag_norm, 0)
            df_family = stats.tag_df_by_family.get(source_family, {}).get(tag_norm, 0)
            fam_total = stats.family_page_counts.get(source_family, 0)
            rarity = min(_idf(stats.total_pages, df_global), _idf(fam_total, df_family) if fam_total else 0.0)
            matched.append((rarity, tag_norm))

        if matched:
            matched.sort(reverse=True)
            # Only let a few tags contribute; avoids "tag cloud" pages accruing many weak matches.
            top = matched[:3]
            tag_score = sum(rarity for rarity, _ in top)
            score += min(tag_score * 0.015, 0.10) * tag_multiplier

    # Summary chunks are often the best "page-level" evidence.
    if chunk_kind == "summary":
        score += 0.03

    return score


def load_chunks(db_root: Path) -> List[Dict]:
    chunks_path = db_root / "chunks.jsonl"
    rows = []
    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_index(db_root: Path) -> Dict:
    with (db_root / "index.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def default_per_page_limit(phase: str) -> int:
    return 1 if phase == "audit" else 2


def _phase_lens_tokens(profile: PhaseProfile, query_tokens: Sequence[str]) -> List[str]:
    # Audit lens gets a bit of adaptive expansion based on query hints.
    extra: List[str] = []
    qset = set(query_tokens)
    if profile.phase == "audit":
        if {"form", "forms", "input", "inputs", "field", "fields"} & qset:
            extra.extend(["inline errors", "helper text", "field labels", "required", "validation messages"])
        if {"table", "tables", "dashboard", "chart", "charts", "data"} & qset:
            extra.extend(["data density", "sorting", "filtering", "empty state", "loading", "error"])
        if {"motion", "animation", "transition"} & qset:
            extra.extend(["reduced motion", "prefers-reduced-motion"])
    return tokenize(" ".join(profile.lens_terms + tuple(extra)))


def search(
    db_root: Path,
    query: str,
    phase: str = "ui",
    top_k: int = 8,
    *,
    per_page_limit: Optional[int] = None,
) -> List[Dict]:
    index = load_index(db_root)
    chunks = load_chunks(db_root)
    stats = build_corpus_stats(chunks)
    tokens = tokenize(query)
    profile = PHASE_PROFILES.get(phase, PHASE_PROFILES["ui"])
    qvec = query_vector(tokens, index.get("idf", {}), int(index.get("dimensions", 768)))
    lens_tokens = _phase_lens_tokens(profile, tokens)
    lens_vec = query_vector(lens_tokens, index.get("idf", {}), int(index.get("dimensions", 768))) if lens_tokens else {}
    scored = []
    for chunk in chunks:
        score = sparse_dot(qvec, chunk.get("vector", []))
        if lens_vec:
            score += profile.lens_alpha * sparse_dot(lens_vec, chunk.get("vector", []))
        score += metadata_boost(chunk, tokens, phase, stats)
        if score <= 0:
            continue
        scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    results = []
    seen = set()
    page_counts: Counter[str] = Counter()
    page_cap = per_page_limit if per_page_limit is not None else default_per_page_limit(phase)
    for score, chunk in scored:
        excerpt = chunk["text"][:360].strip()
        page_key = page_key_from_chunk(chunk)
        if page_cap > 0 and page_counts[page_key] >= page_cap:
            continue
        signature = (page_key, chunk.get("chunk_kind", ""), chunk.get("heading", ""), excerpt[:160])
        if signature in seen:
            continue
        seen.add(signature)
        results.append({**chunk, "score": round(score, 6), "excerpt": excerpt, "page_key": page_key})
        page_counts[page_key] += 1
        if len(results) >= top_k:
            break
    return results


def build_prompt_packet(query: str, phase: str, hits: List[Dict]) -> Dict:
    return {
        "query": query,
        "phase": phase,
        "phase_goal": PHASE_GUIDANCE.get(phase, PHASE_GUIDANCE["ui"]),
        "guardrails": DEFAULT_GUARDRAILS,
        "evidence": [
            {
                "rank": index + 1,
                "score": hit["score"],
                "source_family": hit["source_family"],
                "title": hit["title"],
                "heading": hit.get("heading", ""),
                "location": hit.get("location", ""),
                "url": hit.get("url", ""),
                "final_url": hit.get("final_url", "") or hit.get("url_final", ""),
                "requested_url": hit.get("requested_url", "") or hit.get("url_requested", ""),
                "page_key": hit.get("page_key", ""),
                "excerpt": hit["excerpt"],
            }
            for index, hit in enumerate(hits)
        ],
    }


def format_markdown(packet: Dict) -> str:
    lines = [
        f"# Retrieval Packet: {packet['phase']}",
        "",
        f"Query: {packet['query']}",
        f"Goal: {packet['phase_goal']}",
        "",
        "## Guardrails",
        "",
    ]
    for rule in packet["guardrails"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Evidence", ""])
    for item in packet["evidence"]:
        lines.append(
            f"- [{item['title']}] {item['heading']} | {item['source_family']} | "
            f"score={item['score']} | {item['location'] or item['url']}"
        )
        lines.append(f"  {item['excerpt']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the Google Design fusion retrieval harness.")
    parser.add_argument("query", help="Search query.")
    parser.add_argument("--db-root", default="", help="Vector library root.")
    parser.add_argument("--phase", default="ui", choices=sorted(PHASE_GUIDANCE.keys()))
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument(
        "--per-page-limit",
        type=int,
        default=-1,
        help="Max results allowed per page (dedup by final_url/url/location). -1 = phase default.",
    )
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()

    # Windows terminals often default to a legacy encoding; force UTF-8 to avoid
    # crashing when excerpts contain non-ASCII characters.
    try:
        if (sys.stdout.encoding or "").lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    workspace_root = Path(__file__).resolve().parents[3]
    db_root = Path(args.db_root).resolve() if args.db_root else workspace_root / "google-design-vector-db"
    per_page_limit = None if args.per_page_limit < 0 else args.per_page_limit
    hits = search(db_root, args.query, phase=args.phase, top_k=args.top_k, per_page_limit=per_page_limit)
    packet = build_prompt_packet(args.query, args.phase, hits)

    if args.format == "json":
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

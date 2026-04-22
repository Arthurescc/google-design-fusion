#!/usr/bin/env python3
"""Smoke-test the retrieval harness against a few representative queries."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

sys.dont_write_bytecode = True

from design_harness import default_per_page_limit, page_key_from_chunk, search


EXPECTATIONS = [
    {
        "query": "AI glasses notification motion on transparent screens",
        "phase": "research",
        "must_include_family": "design.google",
    },
    {
        "query": "expressive material design color motion",
        "phase": "concept",
        "must_include_family": "design.google",
    },
    {
        "query": "brand-forward landing page system with premium typography",
        "phase": "ui",
        "must_include_family": "awesome-design-md",
    },
    {
        "query": "audit a dashboard table for keyboard navigation focus order contrast empty state error state",
        "phase": "audit",
        # Audit should still find meaningful design guidance, not only decorative media chunks.
        "must_not_be_empty": True,
    },
    {
        "query": "premium landing page CTA hover loading states and microinteraction polish",
        "phase": "polish",
        "must_include_family": "galaxy-motion",
    },
]


def _safe_reconfigure_stdout() -> None:
    try:
        if (sys.stdout.encoding or "").lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def dominant_family_share(hits) -> float:
    if not hits:
        return 0.0
    counts = {}
    for hit in hits:
        fam = hit.get("source_family") or "<unknown>"
        counts[fam] = counts.get(fam, 0) + 1
    return max(counts.values()) / max(len(hits), 1)


def page_overlap_ratio(hits_a, hits_b) -> float:
    pages_a = {page_key_from_chunk(hit) for hit in hits_a}
    pages_b = {page_key_from_chunk(hit) for hit in hits_b}
    denom = max(min(len(pages_a), len(pages_b)), 1)
    return len(pages_a & pages_b) / denom


def check_per_page_caps(hits, phase: str) -> Optional[str]:
    cap = default_per_page_limit(phase)
    counts = {}
    for hit in hits:
        key = page_key_from_chunk(hit)
        counts[key] = counts.get(key, 0) + 1
    worst = max(counts.values(), default=0)
    if worst > cap:
        return f"Per-page cap violated in phase={phase}: max {worst} > cap {cap}"
    return None


def main() -> int:
    _safe_reconfigure_stdout()
    workspace_root = Path(__file__).resolve().parents[3]
    db_root = workspace_root / "google-design-vector-db"
    failures = []
    all_hits = []

    for expectation in EXPECTATIONS:
        hits = search(db_root, expectation["query"], phase=expectation["phase"], top_k=6)
        all_hits.extend(hits)
        if not hits:
            failures.append(f"No hits for query: {expectation['query']}")
            continue

        cap_issue = check_per_page_caps(hits, expectation["phase"])
        if cap_issue:
            failures.append(f"{cap_issue} (query={expectation['query']})")

        # Family skew guardrail: we enforce this primarily on "ui/polish/audit"-style queries.
        # Research/concept queries are expected to be design.google-heavy in many corpora.
        skew = dominant_family_share(hits)
        if expectation["phase"] in {"ui", "polish", "wireframe", "audit"}:
            skew_threshold = 0.90
            if skew > skew_threshold:
                families = sorted({hit.get("source_family") for hit in hits})
                failures.append(
                    f"Family skew too high (share={round(skew, 3)} > {skew_threshold}) "
                    f"for phase={expectation['phase']} query={expectation['query']}; families={families}"
                )

        families = {hit["source_family"] for hit in hits}
        must_include = expectation.get("must_include_family")
        if must_include and must_include not in families:
            failures.append(
                f"Expected family {must_include} for query {expectation['query']}, got {sorted(families)}"
            )

        if expectation.get("must_not_be_empty") and not hits:
            failures.append(f"Expected non-empty results for audit query {expectation['query']}")

    # Phase distinctiveness: audit must not be a text-only relabel of UI retrieval.
    phase_sep_queries = [
        "brand-forward landing page system with premium typography",
        "table dashboard density sorting filtering empty state loading error",
    ]
    for query in phase_sep_queries:
        ui_hits = search(db_root, query, phase="ui", top_k=6)
        audit_hits = search(db_root, query, phase="audit", top_k=6)
        overlap = page_overlap_ratio(ui_hits, audit_hits)
        if overlap >= 0.75:
            failures.append(
                f"Phase separation too low for query={query}: ui vs audit page overlap ratio={round(overlap, 3)}"
            )

    # Aggregate family skew check across all runs (helps catch "刷屏" regressions).
    if all_hits:
        counts = {}
        for hit in all_hits:
            fam = hit.get("source_family") or "<unknown>"
            counts[fam] = counts.get(fam, 0) + 1
        dominant_share = max(counts.values()) / max(len(all_hits), 1)
        if dominant_share > 0.92:
            failures.append(
                f"Aggregate family skew too high (share={round(dominant_share, 3)} > 0.92) across validations; "
                f"counts={dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))}"
            )

    if failures:
        print("Harness validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Harness validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

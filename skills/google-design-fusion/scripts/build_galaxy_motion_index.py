#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
CSS_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
MOTION_PATTERNS = {
    "hover": re.compile(r":hover|group-hover|hover:", re.IGNORECASE),
    "transition": re.compile(r"transition|duration-|ease-|cubic-bezier", re.IGNORECASE),
    "loading": re.compile(r"\bloader\b|\bloading\b|\bspinner\b", re.IGNORECASE),
    "notification": re.compile(
        r"\btoast\b|\bnotification\b|role\s*=\s*['\"](?:status|alert)['\"]|aria-live\s*=",
        re.IGNORECASE,
    ),
    "loop": re.compile(r"animation:|@keyframes|animate-", re.IGNORECASE),
}


def strip_comments(text: str) -> str:
    text = HTML_COMMENT_PATTERN.sub("", text)
    return CSS_COMMENT_PATTERN.sub("", text)


def classify_motion_kinds(text: str) -> list[str]:
    searchable_text = strip_comments(text)
    return [label for label, pattern in MOTION_PATTERNS.items() if pattern.search(searchable_text)]


def apply_family_priors(motion_kinds: list[str], family: str) -> list[str]:
    normalized = set(motion_kinds)
    family_key = family.strip().lower()
    if family_key == "loaders":
        normalized.add("loading")
    if family_key == "notifications":
        normalized.add("notification")
    return sorted(normalized)


def build_record(file_path: Path, root: Path) -> dict:
    text = file_path.read_text(encoding="utf-8")
    rel_path = file_path.relative_to(root).as_posix()
    family = rel_path.split("/", 1)[0]
    motion_kinds = apply_family_priors(classify_motion_kinds(text), family)
    return {
        "id": rel_path.replace("/", "::"),
        "component_family": family,
        "relative_path": rel_path,
        "motion_kinds": motion_kinds,
        "summary": f"{family} component with motion kinds: {', '.join(motion_kinds) or 'static'}",
        "code_excerpt": text[:800],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    input_root = Path(args.input_root).resolve()
    output_root = Path(args.output_root).resolve()
    if not input_root.exists() or not input_root.is_dir():
        parser.error(f"Input root does not exist or is not a directory: {input_root}")

    index_root = output_root / "index"
    manifest_root = output_root / "manifests"
    index_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)

    records = [build_record(path, input_root) for path in sorted(input_root.rglob("*.html"))]

    records_text = "\n".join(json.dumps(record, ensure_ascii=False) for record in records)
    if records_text:
        records_text += "\n"
    (index_root / "records.jsonl").write_text(records_text, encoding="utf-8")
    snapshot_manifest_path = input_root / ".snapshot-manifest.json"
    snapshot_manifest = {}
    if snapshot_manifest_path.exists():
        snapshot_manifest = json.loads(snapshot_manifest_path.read_text(encoding="utf-8"))
    (manifest_root / "summary.json").write_text(
        json.dumps(
            {
                "record_count": len(records),
                "snapshot_id": snapshot_manifest.get("snapshot_id", ""),
                "source_kind": snapshot_manifest.get("source_kind", ""),
                "source_url": snapshot_manifest.get("source_url", ""),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

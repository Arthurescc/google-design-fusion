#!/usr/bin/env python3
"""Validate workspace-level docs and reports for this skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    workspace_root = Path(__file__).resolve().parents[3]
    failures = []

    manifest_path = workspace_root / "google-design-vector-db" / "manifest.json"
    summary_path = workspace_root / "google-design-vector-db" / "crawl-summary.json"
    report_path = workspace_root / "research" / "validation-report.md"

    if not manifest_path.exists():
        failures.append("Missing google-design-vector-db/manifest.json")
    if not summary_path.exists():
        failures.append("Missing google-design-vector-db/crawl-summary.json")
    if not report_path.exists():
        failures.append("Missing research/validation-report.md")

    if not failures:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        report = report_path.read_text(encoding="utf-8")

        expected_pairs = {
            "design_google_sitemap_entry_count": manifest.get("design_google_sitemap_entry_count"),
            "design_google_indexable_record_count": manifest.get("design_google_indexable_record_count"),
            "awesome_design_record_count": manifest.get("awesome_design_record_count"),
            "galaxy_motion_record_count": manifest.get("galaxy_motion_record_count"),
            "chunk_count": manifest.get("chunk_count"),
        }
        for _, value in expected_pairs.items():
            if value is None:
                failures.append("Manifest is missing one or more coverage keys.")
                break

        for value in expected_pairs.values():
            if value is not None and f"`{value}`" not in report:
                failures.append(f"validation-report.md does not mention current value `{value}`.")

        unresolved_count = len(summary.get("unresolved", []))
        if f"`{unresolved_count}`" not in report:
            failures.append(
                f"validation-report.md does not mention current unresolved count `{unresolved_count}`."
            )

        if "run_full_validation.py" not in report:
            failures.append("validation-report.md should mention run_full_validation.py.")

        if re.search(r"已验证了.*guardrails", report) and "validate_workspace_docs.py" not in report:
            failures.append(
                "validation-report.md claims broad verification without mentioning workspace docs validation."
            )

    if failures:
        print("Workspace docs validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Workspace docs validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

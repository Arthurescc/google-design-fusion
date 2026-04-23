#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from build_execution_brief import build_execution_brief

sys.dont_write_bytecode = True


EXPECTED_ROUTES: dict[str, str] = {
    "retrieval_packet_ui.json": "prototype",
    "retrieval_packet_slides.json": "slides",
    "retrieval_packet_motion.json": "motion",
}


def load_packet(packet_path: Path, failures: list[str]) -> dict[str, Any] | None:
    try:
        raw = packet_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        failures.append(f"Missing fixture: {packet_path.name}")
        return None
    except OSError as exc:
        failures.append(f"Unable to read fixture {packet_path.name}: {exc}")
        return None

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        failures.append(f"Invalid JSON in fixture {packet_path.name}: {exc}")
        return None

    if not isinstance(parsed, dict):
        failures.append(f"Fixture {packet_path.name} must contain a JSON object.")
        return None
    return parsed


def main() -> int:
    workspace_root = Path(__file__).resolve().parents[3]
    fixtures_root = workspace_root / "tests" / "huashu_fusion_studio" / "fixtures"
    failures: list[str] = []

    for fixture_name, expected_mode in EXPECTED_ROUTES.items():
        packet = load_packet(fixtures_root / fixture_name, failures)
        if packet is None:
            continue

        try:
            brief = build_execution_brief(packet)
        except Exception as exc:
            failures.append(
                f"Failed to build execution brief for {fixture_name}: {type(exc).__name__}: {exc}"
            )
            continue

        actual_mode = str(brief.get("artifact_mode") or "")
        if actual_mode != expected_mode:
            failures.append(
                f"{fixture_name} expected artifact_mode={expected_mode}, got {actual_mode or '<missing>'}."
            )

    if failures:
        print("Orchestration validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Orchestration validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

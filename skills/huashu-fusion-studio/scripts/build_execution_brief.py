#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ARTIFACT_EXPORTS: dict[str, list[str]] = {
    "prototype": ["single-file-html", "playwright-check"],
    "slides": ["html-deck", "pptx", "pdf"],
    "motion": ["html-scene", "mp4", "gif"],
    "infographic": ["html-poster", "pdf", "png", "svg"],
    "critique": ["markdown-report"],
}


def infer_artifact_mode(query: str) -> str:
    normalized = query.lower()
    if any(token in normalized for token in ("ppt", "slides", "deck", "keynote", "presentation")):
        return "slides"
    if any(token in normalized for token in ("animation", "motion", "launch film", "mp4", "gif")):
        return "motion"
    if any(token in normalized for token in ("infographic", "data viz", "dataviz", "poster")):
        return "infographic"
    if any(token in normalized for token in ("review", "audit", "critique")):
        return "critique"
    return "prototype"


def _stable_titles(evidence: list[dict[str, Any]], source_family: str, cap: int) -> list[str]:
    titles: list[str] = []
    for item in evidence:
        if item.get("source_family") != source_family:
            continue
        value = str(item.get("title") or item.get("heading") or "").strip()
        if not value or value in titles:
            continue
        titles.append(value)
        if len(titles) >= cap:
            break
    return titles


def _normalize_evidence(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _default_motion_role() -> dict[str, Any]:
    return {
        "enabled": False,
        "role": "Keep motion secondary and mostly static for this request.",
        "motion_kinds": [],
        "evidence_count": 0,
        "evidence_scope": "galaxy-motion hits",
    }


def _normalize_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _normalize_dict(value: Any, default: dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return dict(default)


def load_packet(args: argparse.Namespace, workspace_root: Path) -> dict[str, Any]:
    if args.packet_in:
        packet_path = Path(args.packet_in).resolve()
        try:
            packet_text = packet_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise SystemExit(f"Packet input file not found: {packet_path}") from exc
        except OSError as exc:
            raise SystemExit(f"Failed to read packet input file: {packet_path} ({exc})") from exc

        try:
            packet = json.loads(packet_text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Packet input is not valid JSON: {packet_path} ({exc})") from exc

        if not isinstance(packet, dict):
            raise SystemExit(f"Packet input JSON must be an object: {packet_path}")
        return packet

    if not args.query:
        raise SystemExit("--query is required when --packet-in is not provided.")

    harness_path = workspace_root / "skills" / "google-design-fusion" / "scripts" / "design_harness.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(harness_path),
            args.query,
            "--phase",
            args.phase,
            "--format",
            "json",
        ],
        cwd=str(workspace_root),
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        raise SystemExit(completed.returncode)
    try:
        packet = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"design_harness returned invalid JSON: {exc}") from exc
    if not isinstance(packet, dict):
        raise SystemExit("design_harness returned non-object JSON packet.")
    return packet


def build_execution_brief(packet: dict[str, Any]) -> dict[str, Any]:
    query = str(packet.get("query") or "")
    phase = str(packet.get("phase") or "ui")
    artifact_mode = infer_artifact_mode(query)
    evidence = _normalize_evidence(packet.get("evidence"))

    principle_candidates = _stable_titles(evidence, "design.google", 1)
    style_seed_set = _stable_titles(evidence, "awesome-design-md", 3)

    if not style_seed_set:
        fallback_titles = [
            str(item.get("title") or item.get("heading") or "").strip()
            for item in evidence
            if isinstance(item, dict)
        ]
        style_seed_set = [title for title in fallback_titles if title][:2]

    motion_role = _normalize_dict(packet.get("motion_strategy"), _default_motion_role())

    brand_asset_requirements = {
        "require_logo": artifact_mode != "critique",
        "require_product_images": artifact_mode in {"prototype", "slides", "motion", "infographic"},
        "require_ui_screenshots": artifact_mode in {"prototype", "slides"},
    }
    layout_rules = _normalize_list(packet.get("guardrails"))
    execution_rules = {
        "mode": artifact_mode,
        "preserve_source_trail": True,
        "deterministic_routing": True,
    }
    verification_rules = {
        "require_source_evidence": True,
        "require_export_targets": artifact_mode != "critique",
        "run_motion_checks": bool(motion_role.get("enabled")),
    }

    return {
        "query": query,
        "phase": phase,
        "artifact_mode": artifact_mode,
        "dominant_story": str(packet.get("phase_goal") or ""),
        "principle_cluster": principle_candidates[0] if principle_candidates else "Source-backed design direction",
        "style_seed_set": style_seed_set,
        "motion_role": motion_role,
        "brand_asset_requirements": brand_asset_requirements,
        "layout_rules": layout_rules,
        "execution_rules": execution_rules,
        "verification_rules": verification_rules,
        "export_targets": ARTIFACT_EXPORTS[artifact_mode],
        "evidence": evidence,
    }


def format_markdown(brief: dict[str, Any]) -> str:
    lines = [
        "# Execution Brief",
        "",
        f"- query: {brief['query']}",
        f"- phase: {brief['phase']}",
        f"- artifact_mode: {brief['artifact_mode']}",
        f"- dominant_story: {brief['dominant_story']}",
        f"- principle_cluster: {brief['principle_cluster']}",
        f"- export_targets: {', '.join(brief['export_targets'])}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate retrieval packets into execution briefs.")
    parser.add_argument("--packet-in", default="", help="Optional retrieval packet JSON fixture path.")
    parser.add_argument("--query", default="", help="Query used when packet input is not provided.")
    parser.add_argument("--phase", default="ui", help="Retrieval phase used for harness fallback.")
    parser.add_argument("--format", default="json", choices=["json", "markdown"])
    args = parser.parse_args()

    workspace_root = Path(__file__).resolve().parents[3]
    packet = load_packet(args, workspace_root)
    brief = build_execution_brief(packet)

    if args.format == "json":
        print(json.dumps(brief, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

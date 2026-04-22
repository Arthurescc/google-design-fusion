#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True


def load_yaml_mapping(yaml_text: str, label: str, failures: list[str]) -> dict:
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        failures.append(f"{label} contains malformed YAML: {exc}")
        return {}

    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        failures.append(f"{label} must be a YAML mapping.")
        return {}
    return parsed


def parse_frontmatter(markdown_text: str, failures: list[str]) -> dict:
    lines = markdown_text.splitlines()
    if not lines or lines[0].strip() != "---":
        failures.append("SKILL.md is missing YAML frontmatter.")
        return {}

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        failures.append("SKILL.md has invalid YAML frontmatter: missing closing '---'.")
        return {}

    frontmatter_text = "\n".join(lines[1:closing_index])
    if not frontmatter_text.strip():
        failures.append("SKILL.md has invalid YAML frontmatter: empty mapping.")
        return {}
    return load_yaml_mapping(frontmatter_text, "SKILL.md frontmatter", failures)


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    skill_path = skill_root / "SKILL.md"
    if not skill_path.exists():
        failures.append("Missing required file: SKILL.md")
    else:
        frontmatter = parse_frontmatter(skill_path.read_text(encoding="utf-8"), failures)
        if frontmatter and frontmatter.get("name") != "huashu-fusion-studio":
            failures.append("SKILL.md frontmatter.name must be huashu-fusion-studio.")
        if frontmatter:
            description = str(frontmatter.get("description", "")).strip()
            if len(description) < 30:
                failures.append("SKILL.md frontmatter.description must be substantial.")

    required_files = [
        "agents/openai.yaml",
        "references/orchestration-workflow.md",
        "references/execution-brief-contract.md",
        "references/artifact-routing.md",
        "references/provenance-and-license.md",
        "references/asset-protocol.md",
    ]
    for relative_path in required_files:
        if not (skill_root / relative_path).exists():
            failures.append(f"Missing required file: {relative_path}")

    openai_path = skill_root / "agents" / "openai.yaml"
    if openai_path.exists():
        openai_data = load_yaml_mapping(openai_path.read_text(encoding="utf-8"), "agents/openai.yaml", failures)
        default_prompt = str((openai_data.get("interface") or {}).get("default_prompt") or "").strip()
        if "$huashu-fusion-studio" not in default_prompt:
            failures.append("agents/openai.yaml must explicitly mention $huashu-fusion-studio.")

    if failures:
        print("Skill contract validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Skill contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

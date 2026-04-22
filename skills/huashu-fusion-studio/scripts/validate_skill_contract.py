#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_simple_yaml_mapping(yaml_text: str, label: str, failures: list[str]) -> dict:
    lines = yaml_text.splitlines()

    def parse_mapping(start_index: int, indent: int) -> tuple[dict, int] | None:
        mapping: dict[str, object] = {}
        index = start_index

        while index < len(lines):
            raw_line = lines[index]
            stripped = raw_line.strip()

            if not stripped or stripped.startswith("#"):
                index += 1
                continue

            leading = len(raw_line) - len(raw_line.lstrip(" "))
            if "\t" in raw_line[:leading]:
                failures.append(f"{label} contains malformed YAML: tabs are not supported (line {index + 1}).")
                return None
            if leading < indent:
                break
            if leading > indent:
                failures.append(
                    f"{label} contains malformed YAML: unexpected indentation at line {index + 1}."
                )
                return None

            line = raw_line[leading:]
            if ":" not in line:
                failures.append(
                    f"{label} contains malformed YAML: expected 'key: value' at line {index + 1}."
                )
                return None

            key_part, value_part = line.split(":", 1)
            key = key_part.strip()
            if not key:
                failures.append(f"{label} contains malformed YAML: empty key at line {index + 1}.")
                return None

            value = value_part.strip()
            if value in {"|", "|-", "|+"}:
                block_lines: list[str] = []
                index += 1
                block_indent: int | None = None
                while index < len(lines):
                    block_raw = lines[index]
                    block_stripped = block_raw.strip()
                    block_leading = len(block_raw) - len(block_raw.lstrip(" "))
                    if block_stripped == "":
                        if block_indent is None:
                            block_lines.append("")
                            index += 1
                            continue
                        if block_leading >= block_indent:
                            block_lines.append("")
                            index += 1
                            continue
                    if block_leading <= indent:
                        break
                    if block_indent is None:
                        block_indent = block_leading
                    if block_leading < block_indent:
                        break
                    block_lines.append(block_raw[block_indent:])
                    index += 1
                mapping[key] = "\n".join(block_lines).rstrip("\n")
                continue

            if value == "":
                nested = parse_mapping(index + 1, indent + 2)
                if nested is None:
                    return None
                nested_mapping, index = nested
                mapping[key] = nested_mapping
                continue

            mapping[key] = parse_scalar(value)
            index += 1

        return mapping, index

    parsed_result = parse_mapping(0, 0)
    if parsed_result is None:
        return {}
    parsed, next_index = parsed_result

    for tail_line_number, tail_line in enumerate(lines[next_index:], start=next_index + 1):
        stripped = tail_line.strip()
        if stripped and not stripped.startswith("#"):
            failures.append(f"{label} contains malformed YAML: unexpected content at line {tail_line_number}.")
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
    return parse_simple_yaml_mapping(frontmatter_text, "SKILL.md frontmatter", failures)


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
        openai_data = parse_simple_yaml_mapping(
            openai_path.read_text(encoding="utf-8"),
            "agents/openai.yaml",
            failures,
        )
        interface = openai_data.get("interface")
        if interface is None:
            interface = {}
        if not isinstance(interface, dict):
            failures.append("agents/openai.yaml must define interface as a YAML mapping.")
            interface = {}
        default_prompt = str(interface.get("default_prompt") or "").strip()
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

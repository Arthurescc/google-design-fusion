#!/usr/bin/env python3
"""Validate local skill-specific invariants that quick_validate does not cover."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True


SKILL_NAME = "google-design-fusion"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BACKTICK_PATH_RE = re.compile(r"`((?:\.\.?/)?(?:references|scripts|research|docs|skills|google-design-vector-db)/[^`\s]+)`")
EXTERNAL_SCRIPT_ALLOWLIST = {"scripts/quick_validate.py"}


def candidate_paths_from_text(text: str) -> set[str]:
    paths = set()
    for raw in MARKDOWN_LINK_RE.findall(text):
        if raw.startswith(("http://", "https://", "mailto:")):
            continue
        if raw.startswith("/"):
            continue
        paths.add(raw)
    for raw in BACKTICK_PATH_RE.findall(text):
        paths.add(raw)
    return paths


def resolve_candidate(path: str, file_path: Path, skill_root: Path, workspace_root: Path) -> Path:
    normalized = path.split("#", 1)[0]
    normalized = normalized.split("?", 1)[0]
    if normalized in EXTERNAL_SCRIPT_ALLOWLIST:
        return skill_root / normalized
    if normalized.startswith(("./", "../")):
        return (file_path.parent / normalized).resolve()
    if normalized.startswith(("references/", "scripts/")):
        return (skill_root / normalized).resolve()
    return (workspace_root / normalized).resolve()


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    workspace_root = skill_root.parent.parent
    failures = []

    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "[TODO" in skill_text or "TODO:" in skill_text:
        failures.append("SKILL.md still contains TODO placeholders.")

    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not frontmatter_match:
        failures.append("SKILL.md is missing YAML frontmatter.")
    else:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        description = frontmatter.get("description")
        if not isinstance(description, str) or len(description.strip()) < 30:
            failures.append("SKILL.md frontmatter.description must be a real explanatory string.")

    openai_yaml = yaml.safe_load((skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    default_prompt = (((openai_yaml or {}).get("interface") or {}).get("default_prompt") or "").strip()
    if f"${SKILL_NAME}" not in default_prompt:
        failures.append("agents/openai.yaml default_prompt must explicitly mention $google-design-fusion.")

    markdown_files = list(skill_root.rglob("*.md"))
    missing_paths = []
    for markdown_file in markdown_files:
        text = markdown_file.read_text(encoding="utf-8")
        for candidate in sorted(candidate_paths_from_text(text)):
            resolved = resolve_candidate(candidate, markdown_file, skill_root, workspace_root)
            target = str(resolved)
            if "*" in target:
                target = target.split("*", 1)[0]
            if candidate in EXTERNAL_SCRIPT_ALLOWLIST:
                continue
            if not Path(target).exists():
                missing_paths.append(f"{markdown_file.relative_to(skill_root)} -> {candidate}")
    if missing_paths:
        failures.append("Referenced files are missing: " + ", ".join(missing_paths))

    pycache_dirs = [path for path in skill_root.rglob("__pycache__") if path.is_dir()]
    if pycache_dirs:
        failures.append(
            "Skill package contains __pycache__ directories: "
            + ", ".join(str(path.relative_to(skill_root)) for path in pycache_dirs)
        )

    if failures:
        print("Skill contract validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Skill contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

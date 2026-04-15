#!/usr/bin/env python3
"""Run the recommended validation stack for this skill."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    print("$", " ".join(command))
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=str(cwd), env=env)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    workspace_root = Path(__file__).resolve().parents[3]
    skill_root = workspace_root / "skills" / "google-design-fusion"

    run(
        [
            sys.executable,
            "C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py",
            str(skill_root),
        ],
        workspace_root,
    )
    run([sys.executable, str(skill_root / "scripts" / "validate_skill_contract.py")], workspace_root)
    run([sys.executable, str(skill_root / "scripts" / "validate_harness.py")], workspace_root)
    run([sys.executable, str(skill_root / "scripts" / "validate_workspace_docs.py")], workspace_root)
    print("Full validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the recommended validation stack for this skill."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def resolve_quick_validate_script() -> Path | None:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        base = Path(codex_home).expanduser()
    else:
        base = Path.home() / ".codex"

    quick_validate = base / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if quick_validate.exists():
        return quick_validate
    return None


def run(command: list[str], cwd: Path) -> None:
    print("$", " ".join(command))
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=str(cwd), env=env)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    workspace_root = Path(__file__).resolve().parents[3]
    skill_root = workspace_root / "skills" / "huashu-fusion-studio"
    quick_validate_script = resolve_quick_validate_script()

    if quick_validate_script is None:
        print(
            "Skipping quick_validate.py: not found under CODEX_HOME/.codex "
            "(local validators will still run)."
        )
    else:
        run(
            [
                sys.executable,
                str(quick_validate_script),
                str(skill_root),
            ],
            workspace_root,
        )
    run([sys.executable, str(skill_root / "scripts" / "validate_skill_contract.py")], workspace_root)
    run([sys.executable, str(skill_root / "scripts" / "validate_orchestration.py")], workspace_root)
    print("Full validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

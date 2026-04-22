import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "validate_skill_contract.py"
ORCHESTRATION_SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "validate_orchestration.py"
FULL_VALIDATION_SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "run_full_validation.py"
SKILL_ROOT = REPO_ROOT / "skills" / "huashu-fusion-studio"
SUBPROCESS_TIMEOUT_SECONDS = 60


class ValidateHuashuFusionSkillTests(unittest.TestCase):
    @staticmethod
    def _run_validator(
        script_path: Path,
        cwd: Path,
        env_overrides: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        if env_overrides:
            env.update(env_overrides)
        try:
            return subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                env=env,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(
                f"Validator timed out after {SUBPROCESS_TIMEOUT_SECONDS}s: {script_path}"
            ) from exc

    @staticmethod
    def _debug_output(completed: subprocess.CompletedProcess[str]) -> str:
        return f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"

    @contextmanager
    def _temp_skill_workspace(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            copied_skill_root = tmp_root / "skills" / "huashu-fusion-studio"
            copied_skill_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(SKILL_ROOT, copied_skill_root)
            yield tmp_root, copied_skill_root, copied_skill_root / "scripts" / "validate_skill_contract.py"

    def test_validate_skill_contract_passes(self) -> None:
        completed = self._run_validator(SCRIPT, REPO_ROOT)
        self.assertEqual(completed.returncode, 0, msg=self._debug_output(completed))
        self.assertIn("Skill contract validation passed.", completed.stdout, msg=self._debug_output(completed))

    def test_validate_orchestration_passes(self) -> None:
        completed = self._run_validator(ORCHESTRATION_SCRIPT, REPO_ROOT)
        self.assertEqual(completed.returncode, 0, msg=self._debug_output(completed))
        self.assertIn("Orchestration validation passed.", completed.stdout, msg=self._debug_output(completed))

    def test_run_full_validation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as codex_home:
            completed = self._run_validator(
                FULL_VALIDATION_SCRIPT,
                REPO_ROOT,
                env_overrides={"CODEX_HOME": codex_home},
            )
        self.assertEqual(completed.returncode, 0, msg=self._debug_output(completed))
        self.assertIn("Skipping quick_validate.py", completed.stdout, msg=self._debug_output(completed))
        self.assertIn("Skill contract validation passed.", completed.stdout, msg=self._debug_output(completed))
        self.assertIn("Orchestration validation passed.", completed.stdout, msg=self._debug_output(completed))
        self.assertIn("Full validation passed.", completed.stdout, msg=self._debug_output(completed))

    def test_validate_skill_contract_fails_with_wrong_frontmatter_name(self) -> None:
        with self._temp_skill_workspace() as (tmp_root, copied_skill_root, copied_script):
            skill_md = copied_skill_root / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")
            skill_md.write_text(content.replace("name: huashu-fusion-studio", "name: not-huashu", 1), encoding="utf-8")

            completed = self._run_validator(copied_script, tmp_root)
            self.assertNotEqual(completed.returncode, 0, msg=self._debug_output(completed))
            self.assertIn(
                "SKILL.md frontmatter.name must be huashu-fusion-studio.",
                completed.stdout,
                msg=self._debug_output(completed),
            )

    def test_validate_skill_contract_fails_when_required_file_missing(self) -> None:
        with self._temp_skill_workspace() as (tmp_root, copied_skill_root, copied_script):
            (copied_skill_root / "references" / "asset-protocol.md").unlink()

            completed = self._run_validator(copied_script, tmp_root)
            self.assertNotEqual(completed.returncode, 0, msg=self._debug_output(completed))
            self.assertIn(
                "Missing required file: references/asset-protocol.md",
                completed.stdout,
                msg=self._debug_output(completed),
            )

    def test_validate_skill_contract_fails_when_default_prompt_missing_skill_reference(self) -> None:
        with self._temp_skill_workspace() as (tmp_root, copied_skill_root, copied_script):
            openai_yaml = copied_skill_root / "agents" / "openai.yaml"
            openai_yaml.write_text(
                "interface:\n"
                "  default_prompt: |\n"
                "    Use the local design workflow for this task.\n",
                encoding="utf-8",
            )

            completed = self._run_validator(copied_script, tmp_root)
            self.assertNotEqual(completed.returncode, 0, msg=self._debug_output(completed))
            self.assertIn(
                "agents/openai.yaml must explicitly mention $huashu-fusion-studio.",
                completed.stdout,
                msg=self._debug_output(completed),
            )

    def test_validate_skill_contract_fails_with_empty_frontmatter(self) -> None:
        with self._temp_skill_workspace() as (tmp_root, copied_skill_root, copied_script):
            skill_md = copied_skill_root / "SKILL.md"
            skill_md.write_text("---\n---\n\n# Huashu Fusion Studio\n", encoding="utf-8")

            completed = self._run_validator(copied_script, tmp_root)
            self.assertNotEqual(completed.returncode, 0, msg=self._debug_output(completed))
            self.assertIn(
                "SKILL.md has invalid YAML frontmatter: empty mapping.",
                completed.stdout,
                msg=self._debug_output(completed),
            )

    def test_validate_skill_contract_has_no_pyyaml_dependency(self) -> None:
        script_text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("import yaml", script_text)


if __name__ == "__main__":
    unittest.main()

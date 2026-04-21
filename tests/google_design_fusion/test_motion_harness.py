import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "google-design-fusion" / "scripts" / "design_harness.py"


class MotionHarnessTests(unittest.TestCase):
    def test_polish_query_emits_motion_strategy(self) -> None:
        command = [
            sys.executable,
            str(SCRIPT),
            "premium landing page CTA hover loading states and microinteraction polish",
            "--phase",
            "polish",
            "--top-k",
            "6",
            "--format",
            "json",
        ]
        completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        packet = json.loads(completed.stdout)
        self.assertIn("motion_strategy", packet)
        self.assertIn("motion_guardrails", packet)
        self.assertTrue(packet["motion_strategy"]["enabled"])
        self.assertGreater(packet["motion_strategy"]["evidence_count"], 0)

    def test_non_motion_polish_query_keeps_motion_secondary(self) -> None:
        command = [
            sys.executable,
            str(SCRIPT),
            "improve onboarding empty states and copy hierarchy",
            "--phase",
            "polish",
            "--top-k",
            "6",
            "--format",
            "json",
        ]
        completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        packet = json.loads(completed.stdout)
        self.assertFalse(packet["motion_strategy"]["enabled"])
        self.assertEqual(packet["motion_strategy"]["evidence_count"], 0)
        self.assertEqual(packet["motion_strategy"]["motion_kinds"], [])

    def test_generic_cta_copy_query_does_not_force_motion(self) -> None:
        command = [
            sys.executable,
            str(SCRIPT),
            "improve landing page CTA copy hierarchy",
            "--phase",
            "polish",
            "--top-k",
            "6",
            "--format",
            "json",
        ]
        completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        packet = json.loads(completed.stdout)
        self.assertFalse(packet["motion_strategy"]["enabled"])

    def test_words_containing_motion_do_not_trigger_motion_path(self) -> None:
        command = [
            sys.executable,
            str(SCRIPT),
            "improve promotion banner copy hierarchy",
            "--phase",
            "polish",
            "--top-k",
            "6",
            "--format",
            "json",
        ]
        completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        packet = json.loads(completed.stdout)
        self.assertFalse(packet["motion_strategy"]["enabled"])

    def test_emotionally_wording_does_not_trigger_motion_path(self) -> None:
        command = [
            sys.executable,
            str(SCRIPT),
            "emotionally warm onboarding hierarchy",
            "--phase",
            "polish",
            "--top-k",
            "6",
            "--format",
            "json",
        ]
        completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        packet = json.loads(completed.stdout)
        self.assertFalse(packet["motion_strategy"]["enabled"])


if __name__ == "__main__":
    unittest.main()

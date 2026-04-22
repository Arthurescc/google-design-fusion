import json
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "google-design-fusion" / "scripts" / "build_galaxy_motion_index.py"
FIXTURE = REPO_ROOT / "tests" / "google_design_fusion" / "fixtures" / "galaxy_sample"


class BuildGalaxyMotionIndexTests(unittest.TestCase):
    def test_index_builds_records_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "galaxy-motion"
            command = [
                sys.executable,
                str(SCRIPT),
                "--input-root",
                str(FIXTURE),
                "--output-root",
                str(out_root),
            ]
            completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            records_path = out_root / "index" / "records.jsonl"
            summary_path = out_root / "manifests" / "summary.json"
            self.assertTrue(records_path.exists())
            self.assertTrue(summary_path.exists())

            records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()]
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["record_count"], 3)

            categories = sorted(record["component_family"] for record in records)
            self.assertEqual(categories, ["Buttons", "Loaders", "Notifications"])

            by_category = {record["component_family"]: record for record in records}
            self.assertEqual(by_category["Buttons"]["motion_kinds"], ["hover"])
            self.assertEqual(by_category["Loaders"]["motion_kinds"], ["loading"])
            self.assertEqual(by_category["Notifications"]["motion_kinds"], ["notification"])

    def test_comments_do_not_create_semantic_labels_for_generic_buttons(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_root = Path(tmp) / "galaxy-input"
            shutil.copytree(FIXTURE, input_root)
            (input_root / "Buttons" / "comment-only.html").write_text(
                "<!-- alert loading toast --><div class='plain-button'>Plain</div>",
                encoding="utf-8",
            )
            out_root = Path(tmp) / "galaxy-motion"
            command = [
                sys.executable,
                str(SCRIPT),
                "--input-root",
                str(input_root),
                "--output-root",
                str(out_root),
            ]
            completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            records_path = out_root / "index" / "records.jsonl"
            records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()]
            comment_only = next(record for record in records if record["relative_path"] == "Buttons/comment-only.html")
            self.assertEqual(comment_only["motion_kinds"], [])

    def test_missing_input_root_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "galaxy-motion"
            missing_root = Path(tmp) / "missing-input"
            command = [
                sys.executable,
                str(SCRIPT),
                "--input-root",
                str(missing_root),
                "--output-root",
                str(out_root),
            ]
            completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()

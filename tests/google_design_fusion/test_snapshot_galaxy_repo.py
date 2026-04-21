import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "google-design-fusion" / "scripts" / "snapshot_galaxy_repo.py"
FIXTURE = REPO_ROOT / "tests" / "google_design_fusion" / "fixtures" / "galaxy_sample"


class SnapshotGalaxyRepoTests(unittest.TestCase):
    def test_offline_snapshot_writes_manifest_and_copies_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "vendor"
            command = [
                "python",
                str(SCRIPT),
                "--source-dir",
                str(FIXTURE),
                "--output-root",
                str(out_root),
                "--snapshot-id",
                "fixture-sha",
            ]
            completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            manifest_path = out_root / "galaxy" / ".snapshot-manifest.json"
            self.assertTrue(manifest_path.exists())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["snapshot_id"], "fixture-sha")
            self.assertEqual(manifest["source_kind"], "local-fixture")
            self.assertGreater(manifest["file_count"], 0)

            copied_button = out_root / "galaxy" / "Buttons" / "sample-button.html"
            self.assertTrue(copied_button.exists())


if __name__ == "__main__":
    unittest.main()

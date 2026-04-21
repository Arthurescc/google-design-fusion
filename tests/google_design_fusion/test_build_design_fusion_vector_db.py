import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "google-design-fusion" / "scripts" / "build_design_fusion_vector_db.py"
MOTION_ROOT = REPO_ROOT / "skills" / "google-design-fusion" / "galaxy-motion"


class BuildDesignFusionVectorDbTests(unittest.TestCase):
    def test_manifest_mentions_galaxy_motion_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "db"
            command = [
                sys.executable,
                str(SCRIPT),
                "--output-root",
                str(out_root),
                "--skip-design-google",
                "--skip-awesome",
                "--galaxy-motion-root",
                str(MOTION_ROOT),
            ]
            completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            manifest = json.loads((out_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertIn("galaxy_motion_record_count", manifest)
            self.assertGreater(manifest["galaxy_motion_record_count"], 0)


if __name__ == "__main__":
    unittest.main()

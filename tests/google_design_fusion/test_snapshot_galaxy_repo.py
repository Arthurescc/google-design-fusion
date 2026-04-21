import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "google-design-fusion" / "scripts" / "snapshot_galaxy_repo.py"
FIXTURE = REPO_ROOT / "tests" / "google_design_fusion" / "fixtures" / "galaxy_sample"
SCRIPT_SPEC = importlib.util.spec_from_file_location("snapshot_galaxy_repo", SCRIPT)
assert SCRIPT_SPEC is not None and SCRIPT_SPEC.loader is not None
SNAPSHOT_MODULE = importlib.util.module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SNAPSHOT_MODULE)


class SnapshotGalaxyRepoTests(unittest.TestCase):
    def test_resolve_github_zip_uses_snapshot_id_path(self) -> None:
        snapshot_id = "deadbeef1234"
        url = SNAPSHOT_MODULE.resolve_github_zip(snapshot_id)
        self.assertEqual(url, f"https://codeload.github.com/uiverse-io/galaxy/zip/{snapshot_id}")
        self.assertNotIn("/refs/heads/", url)

    def test_offline_snapshot_writes_manifest_and_copies_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "vendor"
            command = [
                sys.executable,
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
            expected_file_count = sum(1 for path in FIXTURE.rglob("*") if path.is_file()) + 1
            self.assertEqual(manifest["snapshot_id"], "fixture-sha")
            self.assertEqual(manifest["source_kind"], "local-fixture")
            self.assertEqual(manifest["source_url"], str(FIXTURE.resolve()))
            self.assertEqual(manifest["license"], "MIT")
            self.assertEqual(manifest["file_count"], expected_file_count)
            self.assertEqual(
                set(manifest),
                {"snapshot_id", "source_kind", "source_url", "license", "file_count"},
            )

            copied_button = out_root / "galaxy" / "Buttons" / "sample-button.html"
            self.assertTrue(copied_button.exists())


if __name__ == "__main__":
    unittest.main()

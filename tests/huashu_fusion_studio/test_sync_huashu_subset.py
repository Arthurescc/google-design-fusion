import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "sync_huashu_subset.py"
FIXTURE = REPO_ROOT / "tests" / "huashu_fusion_studio" / "fixtures" / "huashu_sample"
EXPECTED_PATHS = [
    "references/workflow.md",
    "references/verification.md",
    "scripts/render-video.js",
    "scripts/html2pptx.js",
    "assets/animations.jsx",
    "assets/deck_stage.js",
]


class SyncHuashuSubsetTests(unittest.TestCase):
    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _run_sync(source_root: Path, output_root: Path, source_ref: str = "fixture-ref") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--source-root",
                str(source_root),
                "--output-root",
                str(output_root),
                "--source-ref",
                source_ref,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )

    def test_sync_copies_curated_subset_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "vendor"
            completed = self._run_sync(FIXTURE, output_root)
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            manifest = json.loads((output_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["upstream_repo"], "https://github.com/alchaincyf/huashu-design")
            self.assertEqual(manifest["source_ref"], "fixture-ref")
            self.assertEqual(manifest["license_kind"], "personal-use-only")
            self.assertEqual(manifest["derived_from"], "alchaincyf/huashu-design")
            self.assertEqual(manifest["copied_files"], EXPECTED_PATHS)
            self.assertEqual(set(manifest["file_hashes"].keys()), set(EXPECTED_PATHS))

            for relative in EXPECTED_PATHS:
                copied_file = output_root / Path(relative)
                self.assertTrue(copied_file.exists(), msg=f"Missing copied file: {relative}")
                expected_hash = self._sha256(FIXTURE / Path(relative))
                actual_hash = manifest["file_hashes"][relative]
                self.assertEqual(actual_hash, expected_hash, msg=f"Hash mismatch for: {relative}")
                self.assertEqual(len(actual_hash), 64, msg=f"Unexpected hash length for: {relative}")

    def test_sync_fails_when_required_source_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp) / "source"
            output_root = Path(tmp) / "vendor"
            shutil.copytree(FIXTURE, source_root)
            (source_root / "scripts" / "html2pptx.js").unlink()

            completed = self._run_sync(source_root, output_root)

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Missing required source file:", completed.stderr)

    def test_sync_fails_for_untrusted_existing_output_outside_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "untrusted-output"
            output_root.mkdir(parents=True, exist_ok=True)
            (output_root / "keep.txt").write_text("do not delete blindly\n", encoding="utf-8")

            completed = self._run_sync(FIXTURE, output_root)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Unsafe existing output root:", completed.stderr)

    def test_sync_fails_for_existing_workspace_directory_without_sentinel(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sync-guard-", dir=str(REPO_ROOT)) as tmp:
            output_root = Path(tmp)
            (output_root / "keep.txt").write_text("workspace directory without sentinel\n", encoding="utf-8")

            completed = self._run_sync(FIXTURE, output_root)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Unsafe existing output root:", completed.stderr)

    def test_sync_allows_existing_output_with_manifest_sentinel_outside_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "trusted-output"
            output_root.mkdir(parents=True, exist_ok=True)
            (output_root / "manifest.json").write_text(
                json.dumps(
                    {
                        "upstream_repo": "https://github.com/alchaincyf/huashu-design",
                        "source_ref": "previous-ref",
                        "license_kind": "personal-use-only",
                        "derived_from": "alchaincyf/huashu-design",
                        "copied_files": [],
                        "file_hashes": {},
                    }
                ),
                encoding="utf-8",
            )

            completed = self._run_sync(FIXTURE, output_root)
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            manifest = json.loads((output_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_ref"], "fixture-ref")

    def test_sync_fails_for_existing_output_with_unrelated_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "unrelated-manifest-output"
            output_root.mkdir(parents=True, exist_ok=True)
            (output_root / "manifest.json").write_text(
                json.dumps(
                    {
                        "derived_from": "other/repo",
                        "license_kind": "mit",
                        "copied_files": [],
                        "file_hashes": {},
                    }
                ),
                encoding="utf-8",
            )

            completed = self._run_sync(FIXTURE, output_root)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Unsafe existing output root:", completed.stderr)

    def test_sync_fails_when_output_root_is_workspace_root(self) -> None:
        completed = self._run_sync(FIXTURE, REPO_ROOT)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Unsafe output root: output_root must not equal workspace_root.", completed.stderr)


if __name__ == "__main__":
    unittest.main()

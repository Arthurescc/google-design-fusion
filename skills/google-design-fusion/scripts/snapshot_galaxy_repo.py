#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

NETWORK_TIMEOUT_SECONDS = 30


def copy_tree(source_dir: Path, output_root: Path) -> int:
    target = output_root / "galaxy"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source_dir, target)
    return sum(1 for path in target.rglob("*") if path.is_file())


def resolve_github_zip(ref: str) -> str:
    return f"https://codeload.github.com/uiverse-io/galaxy/zip/refs/heads/{ref}"


def resolve_github_commit_sha(ref: str) -> str:
    api_url = f"https://api.github.com/repos/uiverse-io/galaxy/commits/{ref}"
    request = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    sha = payload.get("sha")
    if not isinstance(sha, str) or len(sha) < 7:
        raise RuntimeError(f"Unable to resolve commit SHA for ref: {ref}")
    return sha


def fetch_and_extract(zip_url: str, temp_dir: Path) -> Path:
    archive_path = temp_dir / "galaxy.zip"
    with urllib.request.urlopen(zip_url, timeout=NETWORK_TIMEOUT_SECONDS) as response:
        archive_path.write_bytes(response.read())
    with zipfile.ZipFile(archive_path) as zf:
        zf.extractall(temp_dir)
    extracted_roots = [path for path in temp_dir.iterdir() if path.is_dir() and path.name.startswith("galaxy-")]
    if len(extracted_roots) != 1:
        raise RuntimeError(f"Expected one extracted Galaxy root, found {len(extracted_roots)}")
    return extracted_roots[0]


def write_manifest(
    output_root: Path,
    *,
    snapshot_id: str,
    source_kind: str,
    file_count: int,
    source_url: str,
) -> None:
    manifest = {
        "snapshot_id": snapshot_id,
        "source_kind": source_kind,
        "source_url": source_url,
        "license": "MIT",
        "file_count": file_count,
    }
    (output_root / "galaxy" / ".snapshot-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--snapshot-id")
    parser.add_argument("--ref", default="main")
    args = parser.parse_args()

    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if args.source_dir:
        source_dir = Path(args.source_dir).resolve()
        if not source_dir.is_dir():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        copied_file_count = copy_tree(source_dir, output_root)
        snapshot_id = args.snapshot_id or "local-fixture"
        source_kind = "local-fixture"
        source_url = str(source_dir)
    else:
        zip_url = resolve_github_zip(args.ref)
        with tempfile.TemporaryDirectory() as tmp_dir:
            extracted_root = fetch_and_extract(zip_url, Path(tmp_dir))
            copied_file_count = copy_tree(extracted_root, output_root)
        snapshot_id = args.snapshot_id or resolve_github_commit_sha(args.ref)
        source_kind = "github-zip"
        source_url = zip_url

    write_manifest(
        output_root,
        snapshot_id=snapshot_id,
        source_kind=source_kind,
        file_count=copied_file_count + 1,
        source_url=source_url,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

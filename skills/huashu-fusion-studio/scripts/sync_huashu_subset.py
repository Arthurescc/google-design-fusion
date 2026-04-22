#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import shutil
from pathlib import Path


SYNC_FILE_SPECS = [
    ("references/workflow.md", "references/workflow.md"),
    ("references/verification.md", "references/verification.md"),
    ("scripts/render-video.js", "scripts/render-video.js"),
    ("scripts/html2pptx.js", "scripts/html2pptx.js"),
    ("assets/animations.jsx", "assets/animations.jsx"),
    ("assets/deck_stage.js", "assets/deck_stage.js"),
    ("LICENSE", "LICENSE.upstream.txt"),
]
LOCAL_TOOLING_PACKAGE_PATH = "package.json"
LOCAL_TOOLING_PACKAGE_JSON = {
    "name": "huashu-derived-export-tooling",
    "private": True,
    "description": "Minimal local dependencies for vendored huashu-derived export scripts.",
    "dependencies": {
        "playwright": "1.59.1",
        "sharp": "0.34.5",
    },
}

EXPECTED_DERIVED_FROM = "alchaincyf/huashu-design"
EXPECTED_LICENSE_KIND = "personal-use-only"
UPSTREAM_LICENSE_SOURCE = "LICENSE"
UPSTREAM_LICENSE_DEST = "LICENSE.upstream.txt"
SOURCE_REF_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_existing_manifest_sentinel(output_root: Path) -> tuple[bool, str]:
    manifest_path = output_root / "manifest.json"
    if not manifest_path.is_file():
        return False, "missing manifest.json sentinel"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, "manifest.json sentinel is not valid JSON"
    if not isinstance(manifest, dict):
        return False, "manifest.json sentinel must be a JSON object"

    if manifest.get("derived_from") != EXPECTED_DERIVED_FROM:
        return False, "manifest.json sentinel derived_from mismatch"
    if manifest.get("license_kind") != EXPECTED_LICENSE_KIND:
        return False, "manifest.json sentinel license_kind mismatch"
    upstream_license_file = manifest.get("upstream_license_file")
    if upstream_license_file not in (None, UPSTREAM_LICENSE_DEST):
        return False, "manifest.json sentinel upstream_license_file mismatch"
    if "copied_files" not in manifest or "file_hashes" not in manifest:
        return False, "manifest.json sentinel missing required keys"
    return True, ""


def is_windows_reparse_point(path: Path) -> bool:
    if os.name != "nt":
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if reparse_flag == 0:
        return False
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return bool(getattr(st, "st_file_attributes", 0) & reparse_flag)


def validate_source_ref(source_ref: str) -> None:
    if not SOURCE_REF_SHA_PATTERN.fullmatch(source_ref):
        raise SystemExit(
            "Invalid --source-ref: expected an immutable 40-character hexadecimal commit SHA."
        )


def ensure_safe_output_root(
    source_root: Path, output_root: Path, output_root_input: Path, workspace_root: Path
) -> None:
    if output_root == Path(output_root.anchor):
        raise SystemExit(f"Unsafe output root (filesystem root): {output_root}")
    if output_root == workspace_root:
        raise SystemExit("Unsafe output root: output_root must not equal workspace_root.")
    if len(output_root.parts) < 3:
        raise SystemExit(f"Unsafe output root (path is too shallow): {output_root}")
    if output_root == source_root:
        raise SystemExit("Unsafe output root: output_root must not equal source_root.")
    if output_root in source_root.parents:
        raise SystemExit("Unsafe output root: output_root must not be an ancestor of source_root.")
    if source_root in output_root.parents:
        raise SystemExit("Unsafe output root: output_root must not be inside source_root.")
    if output_root_input.exists():
        if output_root_input.is_symlink():
            raise SystemExit(
                "Unsafe existing output root: refusing to delete symlink output root."
            )
        if is_windows_reparse_point(output_root_input):
            raise SystemExit(
                "Unsafe existing output root: refusing to delete Windows reparse-point output root."
            )
        trusted, reason = validate_existing_manifest_sentinel(output_root_input)
        if not trusted:
            raise SystemExit(
                f"Unsafe existing output root: refusing to delete directory ({reason})."
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync a curated huashu-design subset with provenance metadata.")
    parser.add_argument("--source-root", required=True, help="Path to upstream huashu-design clone.")
    parser.add_argument("--output-root", required=True, help="Path to derived subset output directory.")
    parser.add_argument(
        "--source-ref",
        required=True,
        help="Immutable upstream source commit SHA (40-character hexadecimal).",
    )
    args = parser.parse_args()

    workspace_root = Path(__file__).resolve().parents[3]
    source_root = Path(args.source_root).resolve()
    output_root_input = Path(args.output_root).expanduser()
    if not output_root_input.is_absolute():
        output_root_input = (Path.cwd() / output_root_input).absolute()
    output_root = output_root_input.resolve()

    if not source_root.exists():
        raise SystemExit(f"Source root does not exist: {source_root}")
    if not source_root.is_dir():
        raise SystemExit(f"Source root is not a directory: {source_root}")
    if output_root_input.exists() and not output_root_input.is_dir():
        raise SystemExit(f"Output root exists but is not a directory: {output_root}")

    validate_source_ref(args.source_ref)
    ensure_safe_output_root(source_root, output_root, output_root_input, workspace_root)

    if output_root_input.exists():
        shutil.rmtree(output_root_input)
    output_root_input.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    file_hashes: dict[str, str] = {}
    for source_relative, output_relative in SYNC_FILE_SPECS:
        src = source_root / source_relative
        if not src.exists():
            raise SystemExit(f"Missing required source file: {src}")
        dst = output_root_input / output_relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        normalized = output_relative.replace("\\", "/")
        copied_files.append(normalized)
        file_hashes[normalized] = sha256_file(dst)

    tooling_package_path = output_root_input / LOCAL_TOOLING_PACKAGE_PATH
    tooling_package_path.write_text(
        json.dumps(LOCAL_TOOLING_PACKAGE_JSON, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    copied_files.append(LOCAL_TOOLING_PACKAGE_PATH)
    file_hashes[LOCAL_TOOLING_PACKAGE_PATH] = sha256_file(tooling_package_path)

    manifest = {
        "upstream_repo": "https://github.com/alchaincyf/huashu-design",
        "source_ref": args.source_ref,
        "license_kind": EXPECTED_LICENSE_KIND,
        "derived_from": EXPECTED_DERIVED_FROM,
        "upstream_license_source": UPSTREAM_LICENSE_SOURCE,
        "upstream_license_file": UPSTREAM_LICENSE_DEST,
        "copied_files": copied_files,
        "file_hashes": file_hashes,
    }
    (output_root_input / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Synced {len(copied_files)} files into {output_root_input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

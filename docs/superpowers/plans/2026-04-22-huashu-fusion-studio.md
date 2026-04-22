# Huashu Fusion Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Apply `karpathy-guidelines` throughout implementation and review: state assumptions explicitly, choose the simplest solution that works, keep changes surgical, and verify before claiming success.

**Goal:** Add a new top-level skill, `huashu-fusion-studio`, that orchestrates `google-design-fusion` retrieval into a source-backed execution brief and then drives `huashu-design`-style artifact production workflows.

**Architecture:** Keep `skills/google-design-fusion/` unchanged as the retrieval and guardrail layer. Add `skills/huashu-fusion-studio/` as an orchestrator that (1) derives a controlled, attributed `huashu-design` execution subset, (2) translates `design_harness.py --format json` packets into deterministic execution briefs, and (3) validates provenance, orchestration, and packaging without claiming commercial relicensing.

**Tech Stack:** Python 3.9, `unittest`, JSON fixtures/manifests, Markdown skill docs, selective vendoring from a local upstream clone, existing Codex `quick_validate.py`

---

## File Structure

**New files and directories**

- Create: `skills/huashu-fusion-studio/`
- Create: `skills/huashu-fusion-studio/SKILL.md`
- Create: `skills/huashu-fusion-studio/agents/openai.yaml`
- Create: `skills/huashu-fusion-studio/references/orchestration-workflow.md`
- Create: `skills/huashu-fusion-studio/references/execution-brief-contract.md`
- Create: `skills/huashu-fusion-studio/references/artifact-routing.md`
- Create: `skills/huashu-fusion-studio/references/provenance-and-license.md`
- Create: `skills/huashu-fusion-studio/references/asset-protocol.md`
- Create: `skills/huashu-fusion-studio/scripts/sync_huashu_subset.py`
- Create: `skills/huashu-fusion-studio/scripts/build_execution_brief.py`
- Create: `skills/huashu-fusion-studio/scripts/validate_skill_contract.py`
- Create: `skills/huashu-fusion-studio/scripts/validate_orchestration.py`
- Create: `skills/huashu-fusion-studio/scripts/run_full_validation.py`
- Create: `skills/huashu-fusion-studio/vendor/huashu-derived/manifest.json`
- Create: `tests/huashu_fusion_studio/__init__.py`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/`
- Create: `tests/huashu_fusion_studio/fixtures/retrieval_packet_ui.json`
- Create: `tests/huashu_fusion_studio/fixtures/retrieval_packet_slides.json`
- Create: `tests/huashu_fusion_studio/fixtures/retrieval_packet_motion.json`
- Create: `tests/huashu_fusion_studio/test_sync_huashu_subset.py`
- Create: `tests/huashu_fusion_studio/test_build_execution_brief.py`
- Create: `tests/huashu_fusion_studio/test_validate_huashu_fusion_skill.py`
- Create: `research/huashu-fusion-architecture.md`

**Existing files to modify**

- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Explicit non-goals in phase 1**

- Do not modify `skills/google-design-fusion/scripts/design_harness.py`
- Do not modify `skills/google-design-fusion/scripts/build_design_fusion_vector_db.py`
- Do not mirror the full upstream `huashu-design` demos, media, or audio library

---

### Task 1: Scaffold the New Skill Package and Contract Tests

**Files:**
- Create: `skills/huashu-fusion-studio/SKILL.md`
- Create: `skills/huashu-fusion-studio/agents/openai.yaml`
- Create: `skills/huashu-fusion-studio/references/orchestration-workflow.md`
- Create: `skills/huashu-fusion-studio/references/execution-brief-contract.md`
- Create: `skills/huashu-fusion-studio/references/artifact-routing.md`
- Create: `skills/huashu-fusion-studio/references/provenance-and-license.md`
- Create: `skills/huashu-fusion-studio/references/asset-protocol.md`
- Create: `tests/huashu_fusion_studio/__init__.py`
- Create: `tests/huashu_fusion_studio/test_validate_huashu_fusion_skill.py`

- [ ] **Step 1: Write the failing contract test for the new skill**

```python
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "validate_skill_contract.py"


class ValidateHuashuFusionSkillTests(unittest.TestCase):
    def test_validate_skill_contract_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Skill contract validation passed.", completed.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.huashu_fusion_studio.test_validate_huashu_fusion_skill -v`

Expected: `FAIL` because `skills/huashu-fusion-studio/scripts/validate_skill_contract.py` does not exist yet.

- [ ] **Step 3: Create the minimal but complete skill package skeleton**

```markdown
--- a/skills/huashu-fusion-studio/SKILL.md
+++ b/skills/huashu-fusion-studio/SKILL.md
@@
+---
+name: huashu-fusion-studio
+description: Use when an agent needs to turn google-design-fusion retrieval into an execution-first design workflow for prototypes, decks, motion pieces, infographics, or critique while keeping source-backed rationale visible.
+---
+
+# Huashu Fusion Studio
+
+## Overview
+
+Use this skill when the task needs both design evidence and artifact execution. `google-design-fusion` provides the retrieval packet. `huashu-fusion-studio` translates that packet into an execution brief and routes the task into an execution-first workflow.
+
+## Core Flow
+
+1. Classify the task as `prototype`, `slides`, `motion`, `infographic`, or `critique`.
+2. Run `google-design-fusion` retrieval first.
+3. Build an execution brief from the retrieval packet.
+4. Follow the execution workflow for the selected artifact mode.
+5. Verify the result before export or final critique.
+
+## Quick Commands
+
+```bash
+python skills/huashu-fusion-studio/scripts/build_execution_brief.py --packet-in tests/huashu_fusion_studio/fixtures/retrieval_packet_ui.json
+python skills/huashu-fusion-studio/scripts/run_full_validation.py
+```
+```

```yaml
# skills/huashu-fusion-studio/agents/openai.yaml
interface:
  default_prompt: |
    You should use $huashu-fusion-studio for this task.
```

```markdown
# skills/huashu-fusion-studio/references/execution-brief-contract.md

## Execution Brief Contract

- `artifact_mode`
- `dominant_story`
- `principle_cluster`
- `style_seed_set`
- `motion_role`
- `brand_asset_requirements`
- `layout_rules`
- `execution_rules`
- `verification_rules`
- `export_targets`
```

- [ ] **Step 4: Add the local contract validator**

```python
#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    failures = []

    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not match:
        failures.append("SKILL.md is missing YAML frontmatter.")
    else:
        data = yaml.safe_load(match.group(1))
        if data.get("name") != "huashu-fusion-studio":
            failures.append("SKILL.md frontmatter.name must be huashu-fusion-studio.")
        description = str(data.get("description", "")).strip()
        if len(description) < 30:
            failures.append("SKILL.md frontmatter.description must be substantial.")

    required_paths = [
        skill_root / "agents" / "openai.yaml",
        skill_root / "references" / "orchestration-workflow.md",
        skill_root / "references" / "execution-brief-contract.md",
        skill_root / "references" / "artifact-routing.md",
        skill_root / "references" / "provenance-and-license.md",
        skill_root / "references" / "asset-protocol.md",
    ]
    for path in required_paths:
        if not path.exists():
            failures.append(f"Missing required file: {path.relative_to(skill_root)}")

    openai_data = yaml.safe_load((skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    default_prompt = (((openai_data or {}).get("interface") or {}).get("default_prompt") or "").strip()
    if "$huashu-fusion-studio" not in default_prompt:
        failures.append("agents/openai.yaml must explicitly mention $huashu-fusion-studio.")

    if failures:
        print("Skill contract validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Skill contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the test and commit the scaffold**

Run: `python -m unittest tests.huashu_fusion_studio.test_validate_huashu_fusion_skill -v`

Expected: `PASS`

```bash
git add skills/huashu-fusion-studio tests/huashu_fusion_studio
git commit -m "feat: scaffold huashu fusion studio skill"
```

---

### Task 2: Add Controlled `huashu-design` Subset Sync and Provenance Manifest

**Files:**
- Create: `skills/huashu-fusion-studio/scripts/sync_huashu_subset.py`
- Create: `skills/huashu-fusion-studio/vendor/huashu-derived/manifest.json`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/references/workflow.md`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/references/verification.md`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/scripts/render-video.js`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/scripts/html2pptx.js`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/assets/animations.jsx`
- Create: `tests/huashu_fusion_studio/fixtures/huashu_sample/assets/deck_stage.js`
- Create: `tests/huashu_fusion_studio/test_sync_huashu_subset.py`
- Modify: `skills/huashu-fusion-studio/references/provenance-and-license.md`

- [ ] **Step 1: Write the failing sync test**

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "sync_huashu_subset.py"
FIXTURE = REPO_ROOT / "tests" / "huashu_fusion_studio" / "fixtures" / "huashu_sample"


class SyncHuashuSubsetTests(unittest.TestCase):
    def test_sync_copies_curated_subset_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "vendor"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source-root",
                    str(FIXTURE),
                    "--output-root",
                    str(out_root),
                    "--source-ref",
                    "fixture-ref",
                ],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            manifest = json.loads((out_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_ref"], "fixture-ref")
            self.assertEqual(manifest["license_kind"], "personal-use-only")
            self.assertIn("references/workflow.md", manifest["copied_files"])
            self.assertTrue((out_root / "references" / "workflow.md").exists())
            self.assertTrue((out_root / "scripts" / "render-video.js").exists())
            self.assertTrue((out_root / "assets" / "animations.jsx").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.huashu_fusion_studio.test_sync_huashu_subset -v`

Expected: `FAIL` because `sync_huashu_subset.py` does not exist yet.

- [ ] **Step 3: Implement the smallest curated sync script**

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


SYNC_PATHS = [
    "references/workflow.md",
    "references/verification.md",
    "scripts/render-video.js",
    "scripts/html2pptx.js",
    "assets/animations.jsx",
    "assets/deck_stage.js",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--source-ref", required=True)
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    output_root = Path(args.output_root).resolve()
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    copied_files = []
    file_hashes = {}
    for relative in SYNC_PATHS:
        source = source_root / relative
        target = output_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied_files.append(relative.replace("\\", "/"))
        file_hashes[relative.replace("\\", "/")] = sha256_file(target)

    manifest = {
        "upstream_repo": "https://github.com/alchaincyf/huashu-design",
        "source_ref": args.source_ref,
        "license_kind": "personal-use-only",
        "derived_from": "alchaincyf/huashu-design",
        "copied_files": copied_files,
        "file_hashes": file_hashes,
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Apply the sync script to the real local upstream clone and update provenance docs**

Run:

```bash
python skills/huashu-fusion-studio/scripts/sync_huashu_subset.py ^
  --source-root ..\huashu-design-upstream ^
  --output-root skills/huashu-fusion-studio/vendor/huashu-derived ^
  --source-ref HEAD
```

Expected: `skills/huashu-fusion-studio/vendor/huashu-derived/manifest.json` exists and the curated subset is copied.

```markdown
# skills/huashu-fusion-studio/references/provenance-and-license.md

## Provenance

- Derived from `alchaincyf/huashu-design`
- Upstream repo: `https://github.com/alchaincyf/huashu-design`
- Local derived subset recorded in `vendor/huashu-derived/manifest.json`

## License Boundary

- Upstream license kind: `Personal Use License`
- This derived skill must keep upstream attribution visible.
- This repository must not present the derived subset as commercially relicensed.
```

- [ ] **Step 5: Run the sync test and commit**

Run: `python -m unittest tests.huashu_fusion_studio.test_sync_huashu_subset -v`

Expected: `PASS`

```bash
git add skills/huashu-fusion-studio tests/huashu_fusion_studio
git commit -m "feat: add huashu-derived subset sync"
```

---

### Task 3: Build the Retrieval-to-Execution Brief Translator

**Files:**
- Create: `skills/huashu-fusion-studio/scripts/build_execution_brief.py`
- Create: `tests/huashu_fusion_studio/fixtures/retrieval_packet_ui.json`
- Create: `tests/huashu_fusion_studio/fixtures/retrieval_packet_slides.json`
- Create: `tests/huashu_fusion_studio/fixtures/retrieval_packet_motion.json`
- Create: `tests/huashu_fusion_studio/test_build_execution_brief.py`
- Modify: `skills/huashu-fusion-studio/references/execution-brief-contract.md`
- Modify: `skills/huashu-fusion-studio/references/artifact-routing.md`
- Modify: `skills/huashu-fusion-studio/references/orchestration-workflow.md`
- Modify: `skills/huashu-fusion-studio/references/asset-protocol.md`

- [ ] **Step 1: Write the failing translator tests**

```python
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "build_execution_brief.py"
FIXTURES = REPO_ROOT / "tests" / "huashu_fusion_studio" / "fixtures"


class BuildExecutionBriefTests(unittest.TestCase):
    def run_brief(self, fixture_name: str) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--packet-in",
                str(FIXTURES / fixture_name),
                "--format",
                "json",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        return json.loads(completed.stdout)

    def test_ui_packet_defaults_to_prototype_mode(self) -> None:
        brief = self.run_brief("retrieval_packet_ui.json")
        self.assertEqual(brief["artifact_mode"], "prototype")
        self.assertIn("dominant_story", brief)
        self.assertGreaterEqual(len(brief["style_seed_set"]), 1)

    def test_slides_packet_routes_to_slides_mode(self) -> None:
        brief = self.run_brief("retrieval_packet_slides.json")
        self.assertEqual(brief["artifact_mode"], "slides")
        self.assertIn("export_targets", brief)

    def test_motion_packet_routes_to_motion_mode(self) -> None:
        brief = self.run_brief("retrieval_packet_motion.json")
        self.assertEqual(brief["artifact_mode"], "motion")
        self.assertEqual(brief["motion_role"]["enabled"], True)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.huashu_fusion_studio.test_build_execution_brief -v`

Expected: `FAIL` because `build_execution_brief.py` does not exist yet.

- [ ] **Step 3: Implement a deterministic translator with fixture-first support**

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


ARTIFACT_EXPORTS = {
    "prototype": ["single-file-html", "playwright-check"],
    "slides": ["html-deck", "pptx", "pdf"],
    "motion": ["html-scene", "mp4", "gif"],
    "infographic": ["html-poster", "pdf", "png", "svg"],
    "critique": ["markdown-report"],
}


def infer_artifact_mode(query: str) -> str:
    q = query.lower()
    if any(token in q for token in ("ppt", "slides", "deck", "keynote", "presentation")):
        return "slides"
    if any(token in q for token in ("animation", "motion", "launch film", "mp4", "gif")):
        return "motion"
    if any(token in q for token in ("infographic", "data viz", "dataviz", "poster")):
        return "infographic"
    if any(token in q for token in ("review", "audit", "critique")):
        return "critique"
    return "prototype"


def load_packet(args: argparse.Namespace, workspace_root: Path) -> dict:
    if args.packet_in:
        return json.loads(Path(args.packet_in).read_text(encoding="utf-8"))
    harness = workspace_root / "skills" / "google-design-fusion" / "scripts" / "design_harness.py"
    completed = subprocess.run(
        [sys.executable, str(harness), args.query, "--phase", args.phase, "--format", "json"],
        cwd=str(workspace_root),
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return json.loads(completed.stdout)


def build_execution_brief(packet: dict) -> dict:
    evidence = packet.get("evidence", [])
    design_google = next((item for item in evidence if item.get("source_family") == "design.google"), {})
    style_hits = [item for item in evidence if item.get("source_family") == "awesome-design-md"][:2]
    artifact_mode = infer_artifact_mode(packet.get("query", ""))
    return {
        "query": packet.get("query", ""),
        "phase": packet.get("phase", "ui"),
        "artifact_mode": artifact_mode,
        "dominant_story": packet.get("phase_goal", ""),
        "principle_cluster": design_google.get("title") or design_google.get("heading") or "Source-backed design direction",
        "style_seed_set": [item.get("title") or item.get("heading") for item in style_hits if item.get("title") or item.get("heading")],
        "motion_role": packet.get("motion_strategy", {}),
        "brand_asset_requirements": {
            "require_logo": artifact_mode != "critique",
            "require_product_images": artifact_mode in {"prototype", "motion", "slides"},
            "require_ui_screenshots": artifact_mode in {"prototype", "slides"},
        },
        "layout_rules": packet.get("guardrails", []),
        "execution_rules": {
            "artifact_mode": artifact_mode,
            "preserve_source_trail": True,
            "avoid_ai_slop": True,
        },
        "verification_rules": {
            "run_visual_verification": artifact_mode != "critique",
            "run_export_checks": artifact_mode in {"slides", "motion", "infographic"},
        },
        "export_targets": ARTIFACT_EXPORTS[artifact_mode],
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-in", default="")
    parser.add_argument("--query", default="")
    parser.add_argument("--phase", default="ui")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()

    workspace_root = Path(__file__).resolve().parents[3]
    packet = load_packet(args, workspace_root)
    brief = build_execution_brief(packet)
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add the execution-brief contract and routing docs**

```markdown
# skills/huashu-fusion-studio/references/artifact-routing.md

## Artifact Routing

- `prototype`: app or web interaction deliverable
- `slides`: keynote, PPT, presentation, deck deliverable
- `motion`: animation, launch film, MP4, GIF deliverable
- `infographic`: poster, chart-heavy explainer, PDF/PNG/SVG deliverable
- `critique`: review, audit, rating, punch-list deliverable
```

```markdown
# skills/huashu-fusion-studio/references/orchestration-workflow.md

## Orchestration Workflow

1. Retrieve source-backed design evidence from `google-design-fusion`.
2. Translate the retrieval packet into an execution brief.
3. Route the task into the matching artifact mode.
4. Verify the artifact mode before export or critique.
```

- [ ] **Step 5: Run the translator tests and commit**

Run: `python -m unittest tests.huashu_fusion_studio.test_build_execution_brief -v`

Expected: `PASS`

```bash
git add skills/huashu-fusion-studio tests/huashu_fusion_studio
git commit -m "feat: add execution brief translator"
```

---

### Task 4: Add Orchestration Validation and Full Validation Runner

**Files:**
- Create: `skills/huashu-fusion-studio/scripts/validate_orchestration.py`
- Create: `skills/huashu-fusion-studio/scripts/run_full_validation.py`
- Modify: `tests/huashu_fusion_studio/test_validate_huashu_fusion_skill.py`

- [ ] **Step 1: Extend the failing validation test to run the full validation stack**

```python
def test_run_full_validation_passes(self) -> None:
    runner = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "run_full_validation.py"
    completed = subprocess.run(
        [sys.executable, str(runner)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    self.assertEqual(completed.returncode, 0, msg=completed.stderr)
    self.assertIn("Full validation passed.", completed.stdout)
```

- [ ] **Step 2: Run the validation test to verify it fails**

Run: `python -m unittest tests.huashu_fusion_studio.test_validate_huashu_fusion_skill -v`

Expected: `FAIL` because the new validation scripts do not exist yet.

- [ ] **Step 3: Implement orchestration validation**

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def run_case(packet_name: str, expected_mode: str) -> None:
    workspace_root = Path(__file__).resolve().parents[3]
    script = workspace_root / "skills" / "huashu-fusion-studio" / "scripts" / "build_execution_brief.py"
    packet = workspace_root / "tests" / "huashu_fusion_studio" / "fixtures" / packet_name
    completed = subprocess.run(
        [sys.executable, str(script), "--packet-in", str(packet), "--format", "json"],
        cwd=str(workspace_root),
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    brief = json.loads(completed.stdout)
    if brief.get("artifact_mode") != expected_mode:
        raise SystemExit(f"Expected {expected_mode}, got {brief.get('artifact_mode')}")


def main() -> int:
    run_case("retrieval_packet_ui.json", "prototype")
    run_case("retrieval_packet_slides.json", "slides")
    run_case("retrieval_packet_motion.json", "motion")
    print("Orchestration validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Implement the full validation runner**

```python
#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


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
    run(
        [
            sys.executable,
            "C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py",
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
```

- [ ] **Step 5: Run validation and commit**

Run: `python skills/huashu-fusion-studio/scripts/run_full_validation.py`

Expected:

```text
Skill contract validation passed.
Orchestration validation passed.
Full validation passed.
```

```bash
git add skills/huashu-fusion-studio tests/huashu_fusion_studio
git commit -m "test: add huashu fusion validation stack"
```

---

### Task 5: Document the New Skill and Its Repository Relationship

**Files:**
- Create: `research/huashu-fusion-architecture.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `skills/huashu-fusion-studio/SKILL.md`

- [ ] **Step 1: Write the failing doc assertion as a simple grep-based check**

Run:

```bash
python - <<'PY'
from pathlib import Path
for rel in ["README.md", "README.zh-CN.md"]:
    text = Path(rel).read_text(encoding="utf-8")
    assert "huashu-fusion-studio" in text, rel
print("doc assertions passed")
PY
```

Expected: `AssertionError` before the docs are updated.

- [ ] **Step 2: Add the architecture note**

```markdown
# research/huashu-fusion-architecture.md

## Summary

`huashu-fusion-studio` is a three-layer system:

- `google-design-fusion` = retrieval doctrine
- `huashu-design` derived subset = execution doctrine
- `huashu-fusion-studio` = orchestration doctrine

## Design Rule

The fused skill must return both:

- source-backed design rationale
- execution-ready artifact instructions
```

- [ ] **Step 3: Update the repository README files**

```markdown
## Skills In This Repository

- `google-design-fusion`
  Retrieval-first design library based on `design.google`, `awesome-design-md`, and `galaxy-motion`
- `huashu-fusion-studio`
  Execution-first orchestrator that turns retrieval packets into `huashu-design`-style artifact workflows
```

```markdown
## 仓库内的 Skills

- `google-design-fusion`
  以 `design.google`、`awesome-design-md`、`galaxy-motion` 为核心的检索优先设计库
- `huashu-fusion-studio`
  把 retrieval packet 转成 `huashu-design` 风格执行工作流的执行优先编排 skill
```

- [ ] **Step 4: Tighten the new skill doc so it explains the relationship clearly**

```markdown
## Relationship to Upstream Systems

- `google-design-fusion` stays the retrieval engine.
- `huashu-fusion-studio` is the orchestrator.
- `huashu-design` derived content supplies execution doctrine and export behavior.

Do not collapse these three roles into one vague prompt.
```

- [ ] **Step 5: Run final checks and commit**

Run:

```bash
python skills/huashu-fusion-studio/scripts/run_full_validation.py
python - <<'PY'
from pathlib import Path
for rel in ["README.md", "README.zh-CN.md", "research/huashu-fusion-architecture.md"]:
    assert Path(rel).exists(), rel
print("docs exist")
PY
```

Expected:

```text
Full validation passed.
docs exist
```

```bash
git add README.md README.zh-CN.md research/huashu-fusion-architecture.md skills/huashu-fusion-studio
git commit -m "docs: document huashu fusion studio"
```

---

## Plan Self-Review

**1. Spec coverage:**  
The plan covers the new skill package, controlled `huashu-design` derivation, execution-brief translation, provenance handling, validation, and repository documentation. No spec section is left without an implementation task.

**2. Placeholder scan:**  
The plan does not use `TBD`, `TODO`, or deferred pseudo-steps. Each task names concrete files, concrete tests, concrete commands, and a minimal implementation path.

**3. Type consistency:**  
The plan uses one stable artifact contract: `artifact_mode`, `dominant_story`, `principle_cluster`, `style_seed_set`, `motion_role`, `brand_asset_requirements`, `layout_rules`, `execution_rules`, `verification_rules`, and `export_targets`.

**4. Karpathy pass:**  
The plan keeps `google-design-fusion` untouched in phase 1, uses a controlled derived subset instead of a full mirror, makes the translation seam explicit, and defines concrete validation commands before any success claim.

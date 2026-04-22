import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "huashu-fusion-studio" / "scripts" / "build_execution_brief.py"
FIXTURES = REPO_ROOT / "tests" / "huashu_fusion_studio" / "fixtures"
REQUIRED_KEYS = [
    "query",
    "phase",
    "artifact_mode",
    "dominant_story",
    "principle_cluster",
    "style_seed_set",
    "motion_role",
    "brand_asset_requirements",
    "layout_rules",
    "execution_rules",
    "verification_rules",
    "export_targets",
    "evidence",
]


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

    def run_brief_from_packet(self, packet: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "packet.json"
            packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--packet-in",
                    str(packet_path),
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
        self.assertEqual(set(brief.keys()), set(REQUIRED_KEYS))
        self.assertEqual(len(brief.keys()), len(REQUIRED_KEYS))
        self.assertEqual(
            brief["brand_asset_requirements"],
            {
                "require_logo": True,
                "require_product_images": True,
                "require_ui_screenshots": True,
            },
        )

    def test_slides_packet_routes_to_slides_mode(self) -> None:
        brief = self.run_brief("retrieval_packet_slides.json")
        self.assertEqual(brief["artifact_mode"], "slides")
        self.assertIn("export_targets", brief)
        self.assertEqual(brief["export_targets"], ["html-deck", "pptx", "pdf"])

    def test_motion_packet_routes_to_motion_mode(self) -> None:
        brief = self.run_brief("retrieval_packet_motion.json")
        self.assertEqual(brief["artifact_mode"], "motion")
        self.assertEqual(brief["motion_role"]["enabled"], True)
        self.assertEqual(
            brief["brand_asset_requirements"],
            {
                "require_logo": True,
                "require_product_images": True,
                "require_ui_screenshots": False,
            },
        )

    def test_critique_query_routes_to_critique_and_assets(self) -> None:
        packet = {
            "query": "Critique the current landing page hierarchy and copy choices.",
            "phase": "audit",
            "phase_goal": "Critique with evidence-backed findings.",
            "guardrails": [],
            "motion_strategy": {"enabled": False},
            "evidence": [
                {"source_family": "design.google", "title": "Audit heuristics"},
                "non-dict-evidence-entry",
            ],
        }
        brief = self.run_brief_from_packet(packet)
        self.assertEqual(brief["artifact_mode"], "critique")
        self.assertEqual(
            brief["brand_asset_requirements"],
            {
                "require_logo": False,
                "require_product_images": False,
                "require_ui_screenshots": False,
            },
        )

    def test_infographic_query_routes_to_infographic_and_assets(self) -> None:
        packet = {
            "query": "Create an infographic poster for annual sustainability metrics.",
            "phase": "ui",
            "phase_goal": "Render data with clear visual hierarchy.",
            "guardrails": [],
            "motion_strategy": {"enabled": False},
            "evidence": [
                {"source_family": "design.google", "title": "Data storytelling"},
            ],
        }
        brief = self.run_brief_from_packet(packet)
        self.assertEqual(brief["artifact_mode"], "infographic")
        self.assertEqual(brief["export_targets"], ["html-poster", "pdf", "png", "svg"])
        self.assertEqual(
            brief["brand_asset_requirements"],
            {
                "require_logo": True,
                "require_product_images": True,
                "require_ui_screenshots": False,
            },
        )

    def test_packet_in_missing_file_has_clear_error(self) -> None:
        missing_path = REPO_ROOT / "tests" / "huashu_fusion_studio" / "fixtures" / "missing-packet.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--packet-in",
                str(missing_path),
                "--format",
                "json",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Packet input file not found:", completed.stderr)

    def test_packet_in_invalid_json_has_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "invalid.json"
            packet_path.write_text("{not valid json", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--packet-in",
                    str(packet_path),
                    "--format",
                    "json",
                ],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Packet input is not valid JSON:", completed.stderr)

    def test_without_packet_calls_design_harness_json_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copied_script = tmp_root / "skills" / "huashu-fusion-studio" / "scripts" / "build_execution_brief.py"
            copied_script.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SCRIPT, copied_script)

            fake_harness = tmp_root / "skills" / "google-design-fusion" / "scripts" / "design_harness.py"
            fake_harness.parent.mkdir(parents=True, exist_ok=True)
            fake_harness.write_text(
                "import argparse\n"
                "import json\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('query')\n"
                "parser.add_argument('--phase', default='ui')\n"
                "parser.add_argument('--format', default='markdown')\n"
                "args = parser.parse_args()\n"
                "packet = {\n"
                "  'query': args.query,\n"
                "  'phase': args.phase,\n"
                "  'phase_goal': 'Harness-provided goal',\n"
                "  'guardrails': ['Harness guardrail'],\n"
                "  'motion_strategy': {'enabled': False, 'role': 'Harness role', 'motion_kinds': [], 'evidence_count': 0, 'evidence_scope': 'test'},\n"
                "  'motion_guardrails': ['Harness motion guardrail'],\n"
                "  'evidence': [{'source_family': 'design.google', 'title': 'Harness principle', 'heading': '', 'excerpt': 'Harness excerpt'}]\n"
                "}\n"
                "print(json.dumps(packet, ensure_ascii=False))\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(copied_script),
                    "--query",
                    "Need a prototype flow",
                    "--phase",
                    "ui",
                    "--format",
                    "json",
                ],
                cwd=str(tmp_root),
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            brief = json.loads(completed.stdout)
            self.assertEqual(brief["query"], "Need a prototype flow")
            self.assertEqual(brief["phase"], "ui")
            self.assertEqual(brief["artifact_mode"], "prototype")
            self.assertEqual(brief["principle_cluster"], "Harness principle")


if __name__ == "__main__":
    unittest.main()

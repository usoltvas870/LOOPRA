from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCE_CAROUSEL_SCRIPT = REPO_ROOT / "scripts" / "produce_carousel.py"


def _run_cli(*args):
    proc = subprocess.run(
        [sys.executable, str(PRODUCE_CAROUSEL_SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )
    return proc.returncode, proc.stdout, proc.stderr


class ProduceCarouselHelpTests(unittest.TestCase):
    def test_help_flag(self):
        ret, stdout, stderr = _run_cli("--help")
        self.assertEqual(ret, 0)
        self.assertIn("usage", stdout.lower() + stderr.lower())

    def test_h_short_flag(self):
        ret, stdout, stderr = _run_cli("-h")
        self.assertEqual(ret, 0)
        self.assertIn("usage", stdout.lower() + stderr.lower())

    def test_help_has_no_side_effects(self):
        ret, stdout, stderr = _run_cli("--help")
        self.assertEqual(ret, 0)

    def test_unknown_flag_rejected(self):
        ret, stdout, stderr = _run_cli("--unknown-flag")
        self.assertNotEqual(ret, 0)
        self.assertIn("unknown option", stderr + stdout)


class ProduceCarouselJsonModeTests(unittest.TestCase):
    def test_json_output_structure(self):
        ret, stdout, stderr = _run_cli("--project-id", "nonexistent", "--brief", "nonexistent.json", "--json")
        self.assertNotEqual(ret, 0)
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            self.fail(f"stdout is not valid JSON: {stdout[:200]}")
        self.assertEqual(data.get("status"), "error")

    def test_help_wins_over_json(self):
        ret, stdout, stderr = _run_cli("--help", "--json")
        self.assertEqual(ret, 0)
        self.assertIn("usage", stdout.lower() + stderr.lower())


class ProduceCarouselArgsTests(unittest.TestCase):
    def test_missing_project_id(self):
        ret, stdout, stderr = _run_cli("--brief", "x.json")
        self.assertNotEqual(ret, 0)
        self.assertIn("project-id", (stderr + stdout).lower())

    def test_missing_brief(self):
        ret, stdout, stderr = _run_cli("--project-id", "test")
        self.assertNotEqual(ret, 0)
        self.assertIn("brief", (stderr + stdout).lower())

    def test_brief_not_found(self):
        ret, stdout, stderr = _run_cli("--project-id", "test", "--brief", "/nonexistent/brief.json")
        self.assertNotEqual(ret, 0)
        self.assertIn("not found", (stderr + stdout).lower())

    def test_invalid_format(self):
        ret, stdout, stderr = _run_cli("--project-id", "test", "--brief", "x.json", "--format", "invalid_format")
        self.assertNotEqual(ret, 0)
        self.assertIn("format", (stderr + stdout).lower())

    def test_unknown_arg_rejected(self):
        ret, stdout, stderr = _run_cli("--project-id", "test", "--brief", "x.json", "--extra")
        self.assertNotEqual(ret, 0)
        self.assertIn("unknown option", (stderr + stdout).lower())


class ProduceCarouselDryRunTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dry_run_valid_brief(self):
        brief_data = {
            "workspace_id": "internal",
            "project_id": "test",
            "production_brief_id": "brief_test_dry",
            "scenario_id": "scenario_test",
            "content_format": "instagram_carousel",
            "production_variant": "educational_carousel",
            "slides": [
                {
                    "slide_number": 1,
                    "heading": "Hook slide",
                    "background": "bg_gradient_dark",
                },
                {
                    "slide_number": 2,
                    "heading": "Content slide",
                    "body": "Some body text",
                    "background": "bg_dark",
                },
            ],
            "output": {
                "resolution_width": 1080,
                "resolution_height": 1080,
                "slide_count": 2,
            },
        }
        brief_path = Path(self.temp_dir.name) / "brief.json"
        brief_path.write_text(json.dumps(brief_data), encoding="utf-8")

        ret, stdout, stderr = _run_cli(
            "--project-id", "test",
            "--brief", str(brief_path),
            "--dry-run",
        )
        self.assertEqual(ret, 0, f"stderr: {stderr}")
        self.assertIn("DRY RUN", stdout)

    def test_dry_run_json_mode(self):
        brief_data = {
            "workspace_id": "internal",
            "project_id": "test",
            "production_brief_id": "brief_test_dry_json",
            "scenario_id": "scenario_test",
            "content_format": "instagram_carousel",
            "slides": [
                {
                    "slide_number": 1,
                    "heading": "Test",
                    "background": "bg_gradient_dark",
                },
            ],
            "output": {
                "resolution_width": 1080,
                "resolution_height": 1080,
            },
        }
        brief_path = Path(self.temp_dir.name) / "brief_dry.json"
        brief_path.write_text(json.dumps(brief_data), encoding="utf-8")

        ret, stdout, stderr = _run_cli(
            "--project-id", "test",
            "--brief", str(brief_path),
            "--dry-run",
            "--json",
        )
        self.assertEqual(ret, 0, f"stderr: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("mode"), "dry_run")

    def test_dry_run_no_slides(self):
        brief_data = {
            "workspace_id": "internal",
            "project_id": "test",
            "production_brief_id": "brief_no_slides",
            "scenario_id": "scenario_test",
            "content_format": "instagram_carousel",
            "slides": [],
            "output": {
                "resolution_width": 1080,
                "resolution_height": 1080,
            },
        }
        brief_path = Path(self.temp_dir.name) / "brief_no_slides.json"
        brief_path.write_text(json.dumps(brief_data), encoding="utf-8")

        ret, stdout, stderr = _run_cli(
            "--project-id", "test",
            "--brief", str(brief_path),
        )
        self.assertNotEqual(ret, 0)
        self.assertIn("no slides", (stderr + stdout).lower())

    def test_format_mismatch(self):
        brief_data = {
            "workspace_id": "internal",
            "project_id": "test",
            "production_brief_id": "brief_mismatch",
            "scenario_id": "scenario_test",
            "content_format": "short_vertical_video",
            "slides": [],
            "output": {},
        }
        brief_path = Path(self.temp_dir.name) / "brief_mismatch.json"
        brief_path.write_text(json.dumps(brief_data), encoding="utf-8")

        ret, stdout, stderr = _run_cli(
            "--project-id", "test",
            "--brief", str(brief_path),
            "--format", "instagram_carousel",
        )
        self.assertNotEqual(ret, 0)
        self.assertIn("does not match", (stderr + stdout).lower())

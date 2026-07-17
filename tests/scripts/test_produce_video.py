from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCE_VIDEO_SCRIPT = REPO_ROOT / "scripts" / "produce_video.py"


def _run_cli(*args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(PRODUCE_VIDEO_SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )
    return proc.returncode, proc.stdout, proc.stderr


class ProduceVideoHelpTests(unittest.TestCase):
    def test_help_flag(self) -> None:
        ret, stdout, stderr = _run_cli("--help")
        self.assertEqual(ret, 0)
        self.assertIn("usage", stdout.lower() + stderr.lower())

    def test_h_short_flag(self) -> None:
        ret, stdout, stderr = _run_cli("-h")
        self.assertEqual(ret, 0)
        self.assertIn("usage", stdout.lower() + stderr.lower())

    def test_help_has_no_side_effects(self) -> None:
        ret, stdout, stderr = _run_cli("--help")
        self.assertEqual(ret, 0)

    def test_unknown_flag_rejected(self) -> None:
        ret, stdout, stderr = _run_cli("--unknown-flag")
        self.assertNotEqual(ret, 0)
        self.assertIn("unknown option", stderr + stdout)


class ProduceVideoJsonModeTests(unittest.TestCase):
    def test_json_output_structure(self) -> None:
        ret, stdout, stderr = _run_cli("--project-id", "nonexistent", "--brief", "nonexistent.json", "--json")
        self.assertNotEqual(ret, 0)
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            self.fail(f"stdout is not valid JSON: {stdout[:200]}")
        self.assertEqual(data.get("status"), "error")

    def test_help_wins_over_json(self) -> None:
        ret, stdout, stderr = _run_cli("--help", "--json")
        self.assertEqual(ret, 0)
        self.assertIn("usage", stdout.lower() + stderr.lower())


class ProduceVideoArgsTests(unittest.TestCase):
    def test_missing_project_id(self) -> None:
        ret, stdout, stderr = _run_cli("--brief", "x.json")
        self.assertNotEqual(ret, 0)
        self.assertIn("project-id", (stderr + stdout).lower())

    def test_missing_brief(self) -> None:
        ret, stdout, stderr = _run_cli("--project-id", "test")
        self.assertNotEqual(ret, 0)
        self.assertIn("brief", (stderr + stdout).lower())

    def test_brief_not_found(self) -> None:
        ret, stdout, stderr = _run_cli("--project-id", "test", "--brief", "/nonexistent/brief.json")
        self.assertNotEqual(ret, 0)
        self.assertIn("not found", (stderr + stdout).lower())

    def test_invalid_format(self) -> None:
        ret, stdout, stderr = _run_cli("--project-id", "test", "--brief", "x.json", "--format", "invalid_format")
        self.assertNotEqual(ret, 0)
        self.assertIn("format", (stderr + stdout).lower())

    def test_unknown_arg_rejected(self) -> None:
        ret, stdout, stderr = _run_cli("--project-id", "test", "--brief", "x.json", "--extra")
        self.assertNotEqual(ret, 0)
        self.assertIn("unknown option", (stderr + stdout).lower())

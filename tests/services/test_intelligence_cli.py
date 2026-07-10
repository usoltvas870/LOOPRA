from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class ContentIntelligenceCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._copy_project("example")
        self.env = os.environ.copy()
        self.env["LOOPRA_PROJECTS_ROOT"] = str(self.projects_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_help_json_unknown_and_human_workflow(self) -> None:
        help_result = self._run("import_market_signal.py", "--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("Usage", help_result.stdout)

        unknown = self._run("import_market_signal.py", "--bad", "--json")
        self.assertEqual(unknown.returncode, 1)
        self.assertEqual(json.loads(unknown.stdout)["status"], "error")

        signal_json = self._run(
            "import_market_signal.py",
            "--json",
            json.dumps({
                "project_id": "example",
                "title": "Manual audience observation",
                "description": "Short reflective posts are being saved.",
                "confidence": 0.7,
            }),
        )
        self.assertEqual(signal_json.returncode, 0, signal_json.stderr)
        signal = json.loads(signal_json.stdout)["market_signal"]

        pattern_human = self._run(
            "create_trend_pattern.py",
            json.dumps({
                "project_id": "example",
                "title": "Reflective pattern",
                "summary": "Manual interpretation.",
                "market_signal_ids": [signal["market_signal_id"]],
            }),
        )
        self.assertEqual(pattern_human.returncode, 0, pattern_human.stderr)
        trend_id = pattern_human.stdout.strip().splitlines()[0].split("=", 1)[1]

        opportunity_json = self._run(
            "create_content_opportunity.py",
            "--json",
            json.dumps({
                "project_id": "example",
                "trend_pattern_id": trend_id,
                "title": "Create calm explainer",
                "summary": "Recommendation only.",
                "funnel_stage": "trust",
                "score": 0.8,
            }),
        )
        self.assertEqual(opportunity_json.returncode, 0, opportunity_json.stderr)
        opportunity = json.loads(opportunity_json.stdout)["content_opportunity"]

        listed = self._run("list_content_opportunities.py", "--json", "example")
        self.assertEqual(listed.returncode, 0)
        self.assertEqual(len(json.loads(listed.stdout)["content_opportunities"]), 1)

        approved = self._run("approve_content_opportunity.py", "--json", "example", opportunity["content_opportunity_id"])
        self.assertEqual(approved.returncode, 0, approved.stderr)
        self.assertEqual(json.loads(approved.stdout)["content_opportunity"]["status"], "approved")

        idea = self._run("create_idea_from_opportunity.py", "--json", "example", opportunity["content_opportunity_id"])
        self.assertEqual(idea.returncode, 0, idea.stderr)
        self.assertTrue(json.loads(idea.stdout)["idea"]["idea_id"].startswith("idea_"))

    def _run(self, script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / script_name), *args],
            cwd=REPO_ROOT,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def _copy_project(self, project_id: str) -> None:
        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / "projects" / project_id / "project.yaml", project_dir / "project.yaml")


if __name__ == "__main__":
    unittest.main()

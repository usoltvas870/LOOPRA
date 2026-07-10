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
INTELLIGENCE_SCRIPTS = (
    "import_market_signal.py",
    "review_market_signal.py",
    "create_trend_pattern.py",
    "activate_trend_pattern.py",
    "create_content_opportunity.py",
    "list_content_opportunities.py",
    "approve_content_opportunity.py",
    "reject_content_opportunity.py",
    "defer_content_opportunity.py",
    "archive_content_opportunity.py",
    "create_idea_from_opportunity.py",
)


class ContentIntelligenceCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._copy_project("example")
        self.env = os.environ.copy()
        self.env["LOOPRA_PROJECTS_ROOT"] = str(self.projects_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_help_and_help_wins_json_for_every_intelligence_script(self) -> None:
        for script_name in INTELLIGENCE_SCRIPTS:
            with self.subTest(script=script_name, mode="help"):
                result = self._run(script_name, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Usage", result.stdout)
                self.assertEqual(result.stderr, "")

            with self.subTest(script=script_name, mode="json-help"):
                result = self._run(script_name, "--json", "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Usage", result.stdout)
                self.assertNotIn('"status"', result.stdout)
                self.assertEqual(result.stderr, "")

    def test_unknown_flags_are_rejected_for_every_intelligence_script(self) -> None:
        for script_name in INTELLIGENCE_SCRIPTS:
            with self.subTest(script=script_name, mode="human"):
                result = self._run(script_name, "--unknown")
                self.assertEqual(result.returncode, 1)
                self.assertIn("ERROR: unknown option: --unknown", result.stderr)
                self.assertEqual(result.stdout, "")

            with self.subTest(script=script_name, mode="json"):
                result = self._run(script_name, "--json", "--unknown")
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "error")
                self.assertIn("unknown option: --unknown", payload["message"])
                self.assertEqual(result.stderr, "")

    def test_full_manual_lifecycle_covers_every_intelligence_script(self) -> None:
        signal_result = self._run(
            "import_market_signal.py",
            "--json",
            json.dumps(
                {
                    "project_id": "example",
                    "title": "Manual audience observation",
                    "description": "Short reflective posts are being saved.",
                    "confidence": 0.7,
                }
            ),
        )
        self.assertEqual(signal_result.returncode, 0, signal_result.stderr)
        signal = json.loads(signal_result.stdout)["market_signal"]

        reviewed_result = self._run(
            "review_market_signal.py",
            "--json",
            "example",
            signal["market_signal_id"],
        )
        self.assertEqual(reviewed_result.returncode, 0, reviewed_result.stderr)
        self.assertEqual(json.loads(reviewed_result.stdout)["market_signal"]["status"], "reviewed")

        pattern_result = self._run(
            "create_trend_pattern.py",
            json.dumps({
                "project_id": "example",
                "title": "Reflective pattern",
                "summary": "Manual interpretation.",
                "market_signal_ids": [signal["market_signal_id"]],
            }),
        )
        self.assertEqual(pattern_result.returncode, 0, pattern_result.stderr)
        trend_id = pattern_result.stdout.strip().splitlines()[0].split("=", 1)[1]

        activated_result = self._run(
            "activate_trend_pattern.py",
            "--json",
            "example",
            trend_id,
        )
        self.assertEqual(activated_result.returncode, 0, activated_result.stderr)
        self.assertEqual(json.loads(activated_result.stdout)["trend_pattern"]["status"], "active")

        convert_opportunity = self._create_opportunity(trend_id, "Create calm explainer")
        reject_opportunity = self._create_opportunity(trend_id, "Reject this direction")
        defer_opportunity = self._create_opportunity(trend_id, "Defer this direction")
        archive_opportunity = self._create_opportunity(trend_id, "Archive this direction")

        listed = self._run("list_content_opportunities.py", "--json", "example")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(len(json.loads(listed.stdout)["content_opportunities"]), 4)

        approved = self._run(
            "approve_content_opportunity.py",
            "--json",
            "example",
            convert_opportunity["content_opportunity_id"],
        )
        self.assertEqual(approved.returncode, 0, approved.stderr)
        self.assertEqual(json.loads(approved.stdout)["content_opportunity"]["status"], "approved")

        rejected = self._run(
            "reject_content_opportunity.py",
            "example",
            reject_opportunity["content_opportunity_id"],
        )
        self.assertEqual(rejected.returncode, 0, rejected.stderr)
        self.assertIn("status=rejected", rejected.stdout)

        deferred = self._run(
            "defer_content_opportunity.py",
            "--json",
            "example",
            defer_opportunity["content_opportunity_id"],
        )
        self.assertEqual(deferred.returncode, 0, deferred.stderr)
        self.assertEqual(json.loads(deferred.stdout)["content_opportunity"]["status"], "deferred")

        archived = self._run(
            "archive_content_opportunity.py",
            "--json",
            "example",
            archive_opportunity["content_opportunity_id"],
        )
        self.assertEqual(archived.returncode, 0, archived.stderr)
        self.assertEqual(json.loads(archived.stdout)["content_opportunity"]["status"], "archived")

        idea = self._run(
            "create_idea_from_opportunity.py",
            "--json",
            "example",
            convert_opportunity["content_opportunity_id"],
        )
        self.assertEqual(idea.returncode, 0, idea.stderr)
        self.assertTrue(json.loads(idea.stdout)["idea"]["idea_id"].startswith("idea_"))

        rejected_list = self._run(
            "list_content_opportunities.py",
            "--json",
            "example",
            "rejected",
        )
        self.assertEqual(rejected_list.returncode, 0, rejected_list.stderr)
        self.assertEqual(len(json.loads(rejected_list.stdout)["content_opportunities"]), 1)

    def test_operational_errors_are_reported_without_tracebacks(self) -> None:
        payload_cases = (
            ("import_market_signal.py", json.dumps({
                "project_id": "missing",
                "title": "Signal",
                "description": "Missing project",
            })),
            ("create_trend_pattern.py", json.dumps({
                "project_id": "example",
                "title": "Pattern",
                "summary": "Missing signal",
                "market_signal_ids": ["signal_missing"],
            })),
            ("create_content_opportunity.py", json.dumps({
                "project_id": "example",
                "trend_pattern_id": "trend_missing",
                "title": "Opportunity",
                "summary": "Missing pattern",
            })),
        )
        for script_name, payload in payload_cases:
            with self.subTest(script=script_name):
                result = self._run(script_name, "--json", payload)
                self._assert_json_error(result)

        missing_entity_scripts = (
            "review_market_signal.py",
            "activate_trend_pattern.py",
            "approve_content_opportunity.py",
            "reject_content_opportunity.py",
            "defer_content_opportunity.py",
            "archive_content_opportunity.py",
            "create_idea_from_opportunity.py",
        )
        for script_name in missing_entity_scripts:
            with self.subTest(script=script_name):
                result = self._run(script_name, "--json", "example", "missing_id")
                self._assert_json_error(result)

        missing_project_list = self._run(
            "list_content_opportunities.py",
            "--json",
            "missing",
        )
        self._assert_json_error(missing_project_list)

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

    def _create_opportunity(self, trend_pattern_id: str, title: str) -> dict[str, object]:
        result = self._run(
            "create_content_opportunity.py",
            "--json",
            json.dumps(
                {
                    "project_id": "example",
                    "trend_pattern_id": trend_pattern_id,
                    "title": title,
                    "summary": "Recommendation only.",
                    "funnel_stage": "trust",
                    "score": 0.8,
                }
            ),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["content_opportunity"]

    def _assert_json_error(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(payload["message"])
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "smoke_loop.py"


class SmokeLoopScriptTests(unittest.TestCase):
    def test_script_runs_end_to_end_for_generic_example_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["CONTENT_PLANT_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self._assert_smoke_output(completed)

    def test_script_uses_loopra_smoke_projects_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self._assert_smoke_output(completed)

    def test_help_flag_prints_usage_and_exits_zero(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("Usage", completed.stdout)
        self.assertIn("smoke_loop.py", completed.stdout)

    def test_short_help_flag_prints_usage_and_exits_zero(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "-h"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("Usage", completed.stdout)
        self.assertIn("smoke_loop.py", completed.stdout)

    def test_help_does_not_create_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--help"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertFalse(runtime_projects_root.exists())

    # ------------------------------------------------------------------
    # JSON output mode
    # ------------------------------------------------------------------

    def test_json_success_produces_valid_json_with_expected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--json"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["project_id"], "example")
            self.assertTrue(result["idea_id"].startswith("idea_"))
            self.assertTrue(result["scenario_id"].startswith("scenario_"))
            self.assertTrue(result["content_item_id"].startswith("content_"))
            self.assertTrue(result["export_package_id"].startswith("export_"))
            self.assertTrue(result["publication_id"].startswith("publication_"))
            self.assertTrue(result["metric_snapshot_id"].startswith("metric_"))
            self.assertIsInstance(result["generated_export_files"], list)
            self.assertIsInstance(result["entity_statuses"], dict)

    def test_json_success_has_empty_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--json"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")

    def test_json_success_creates_lifecycle_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--json"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)

            export_dir = Path(result["export_directory"])
            self.assertTrue(export_dir.exists())
            generated = result["generated_export_files"]
            self.assertIsInstance(generated, list)
            self.assertEqual(
                sorted(generated),
                [
                    "body.txt",
                    "caption_telegram.txt",
                    "manifest.json",
                    "manual_publication_checklist.txt",
                    "metadata.json",
                    "title.txt",
                ],
            )

    def test_json_entity_statuses_are_correct(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--json"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            statuses = result["entity_statuses"]
            self.assertEqual(statuses["idea"], "scripted")
            self.assertEqual(statuses["scenario"], "approved")
            self.assertEqual(statuses["content_item"], "exported")
            self.assertEqual(statuses["export_package"], "ready")
            self.assertEqual(statuses["publication"], "published")
            self.assertEqual(statuses["metric_snapshot"], "draft")

    def test_json_respects_loopra_smoke_projects_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--json"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertTrue(runtime_projects_root.exists())

    def test_json_with_help_prints_usage_not_json(self) -> None:
        for args in (["--json", "--help"], ["--help", "--json"]):
            with self.subTest(args=args):
                completed = subprocess.run(
                    [sys.executable, str(SCRIPT_PATH), *args],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                self.assertEqual(completed.returncode, 0)
                self.assertIn("Usage", completed.stdout)
                self.assertNotIn("{", completed.stdout)

    def test_json_with_help_does_not_create_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            for args in (["--json", "--help"], ["--help", "--json"]):
                with self.subTest(args=args):
                    completed = subprocess.run(
                        [sys.executable, str(SCRIPT_PATH), *args],
                        cwd=REPO_ROOT,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    self.assertEqual(completed.returncode, 0)
                    self.assertFalse(runtime_projects_root.exists())

    def test_unknown_flag_rejected_in_human_mode(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--unknown"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unknown option", completed.stderr)
        self.assertIn("--unknown", completed.stderr)

    def test_unknown_flag_rejected_in_json_mode(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json", "--unknown"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 1)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("unknown option", result["message"])
        self.assertEqual(completed.stderr, "")

    def test_json_error_for_missing_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)
            env["LOOPRA_SMOKE_PROJECT_ID"] = "missing_project"

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--json"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "error")
            self.assertIn("missing_project", result["message"])

    def test_human_mode_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_projects_root = Path(temp_dir) / "smoke_projects"
            env = os.environ.copy()
            env["LOOPRA_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)

            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self._assert_smoke_output(completed)

    def _assert_smoke_output(self, completed: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(completed.returncode, 0, completed.stderr)
        stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        output = dict(line.split("=", 1) for line in stdout_lines)

        self.assertEqual(output["project_id"], "example")
        self.assertEqual(output["scenario_status"], "approved")
        self.assertEqual(output["content_item_status"], "exported")
        self.assertEqual(output["export_package_status"], "ready")
        self.assertEqual(output["publication_status"], "published")
        self.assertEqual(output["metric_snapshot_status"], "draft")

        export_dir = Path(output["export_directory"])
        self.assertTrue(export_dir.exists())
        self.assertEqual(
            output["generated_export_files"].split(","),
            [
                "body.txt",
                "caption_telegram.txt",
                "manifest.json",
                "manual_publication_checklist.txt",
                "metadata.json",
                "title.txt",
            ],
        )


if __name__ == "__main__":
    unittest.main()

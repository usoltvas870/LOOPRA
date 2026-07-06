from __future__ import annotations

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
                    "manual_publication_checklist.txt",
                    "metadata.json",
                    "title.txt",
                ],
            )


if __name__ == "__main__":
    unittest.main()

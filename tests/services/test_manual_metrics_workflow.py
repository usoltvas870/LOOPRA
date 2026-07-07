from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from core.domain import MetricSnapshotStatus
from core.services import (
    FileSystemIdeaRepository,
    FileSystemMetricSnapshotRepository,
    FileSystemProjectRepository,
    FileSystemPublicationRepository,
    IdeaService,
    ProjectService,
    build_analytics_service,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_LOOP_SCRIPT_PATH = REPO_ROOT / "scripts" / "smoke_loop.py"
FIND_METRIC_SNAPSHOTS_SCRIPT_PATH = REPO_ROOT / "scripts" / "find_metric_snapshots.py"
IMPORT_MANUAL_METRICS_SCRIPT_PATH = REPO_ROOT / "scripts" / "import_manual_metrics.py"


class ManualMetricsWorkflowSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name) / "smoke_projects"

        self.project_repository = FileSystemProjectRepository(self.projects_root)
        self.idea_repository = FileSystemIdeaRepository(self.projects_root)
        self.idea_service = IdeaService(self.idea_repository, ProjectService(self.project_repository))
        self.metric_repository = FileSystemMetricSnapshotRepository(self.projects_root)
        self.publication_repository = FileSystemPublicationRepository(self.projects_root)
        self.analytics_service = build_analytics_service(self.projects_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_smoke_workflow_records_manual_metrics_for_draft_snapshot(self) -> None:
        smoke_completed = self._run_script(
            SMOKE_LOOP_SCRIPT_PATH,
            env_updates={"CONTENT_PLANT_SMOKE_PROJECTS_ROOT": str(self.projects_root)},
        )
        self.assertEqual(smoke_completed.returncode, 0, smoke_completed.stderr)

        smoke_output = self._parse_key_value_lines(smoke_completed.stdout)
        project_id = smoke_output["project_id"]
        publication_id = smoke_output["publication_id"]
        metric_snapshot_id = smoke_output["metric_snapshot_id"]

        self.assertEqual(project_id, "example")
        self.assertEqual(smoke_output["metric_snapshot_status"], "draft")
        self.assertEqual(len(self.idea_service.list_ideas(project_id)), 1)

        initial_publication = self.publication_repository.load_publication(project_id, publication_id)
        self.assertIsNotNone(initial_publication.published_url)

        finder_completed = self._run_script(
            FIND_METRIC_SNAPSHOTS_SCRIPT_PATH,
            ["example"],
            env_updates={"CONTENT_PLANT_PROJECTS_ROOT": str(self.projects_root)},
        )
        self.assertEqual(finder_completed.returncode, 0, finder_completed.stderr)

        finder_lines = [line.strip() for line in finder_completed.stdout.splitlines() if line.strip()]
        self.assertEqual(finder_lines[0], "metric_snapshots_found=1")
        self.assertEqual(finder_lines[1], "project_id=example")
        self.assertEqual(finder_lines[2], "snapshots:")

        located_snapshot = self._parse_space_separated_pairs(finder_lines[3].removeprefix("- ").strip())
        self.assertEqual(located_snapshot["metric_snapshot_id"], metric_snapshot_id)
        self.assertEqual(located_snapshot["publication_id"], publication_id)
        self.assertEqual(located_snapshot["status"], "draft")

        updated_published_url = f"https://example.invalid/example/manual/workflow-{publication_id}"
        manual_metrics_path = self.projects_root / "manual_metrics_workflow.json"
        manual_metrics_path.write_text(
            json.dumps(
                {
                    "project_id": project_id,
                    "metric_snapshot_id": metric_snapshot_id,
                    "metrics": {
                        "views": 100,
                        "likes": 12,
                        "comments": 3,
                        "shares": 1,
                        "saves": 2,
                        "clicks": 5,
                        "published_url": updated_published_url,
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        import_completed = self._run_script(
            IMPORT_MANUAL_METRICS_SCRIPT_PATH,
            [str(manual_metrics_path)],
            env_updates={"CONTENT_PLANT_PROJECTS_ROOT": str(self.projects_root)},
        )
        self.assertEqual(import_completed.returncode, 0, import_completed.stderr)
        self.assertEqual(
            [line.strip() for line in import_completed.stdout.splitlines() if line.strip()],
            [
                "metrics_import_status=ok",
                "project_id=example",
                f"metric_snapshot_id={metric_snapshot_id}",
                "recorded_keys=views,likes,comments,shares,saves,clicks,published_url",
            ],
        )

        recorded_snapshot = self.metric_repository.load_metric_snapshot(project_id, metric_snapshot_id)
        updated_publication = self.publication_repository.load_publication(project_id, publication_id)

        self.assertEqual(recorded_snapshot.status, MetricSnapshotStatus.RECORDED)
        self.assertEqual(recorded_snapshot.content_metrics.views, 100)
        self.assertEqual(recorded_snapshot.content_metrics.likes, 12)
        self.assertEqual(recorded_snapshot.content_metrics.comments, 3)
        self.assertEqual(recorded_snapshot.content_metrics.shares, 1)
        self.assertEqual(recorded_snapshot.content_metrics.saves, 2)
        self.assertEqual(recorded_snapshot.content_metrics.link_clicks, 5)
        self.assertEqual(updated_publication.published_url, updated_published_url)
        self.assertNotEqual(updated_publication.published_url, initial_publication.published_url)
        self.assertNotIn("clicks", recorded_snapshot.content_metrics.model_dump())
        self.assertNotIn("published_url", recorded_snapshot.content_metrics.model_dump())

        self.assertEqual(self.analytics_service.get_insights(project_id), [])
        self.assertEqual(self.analytics_service.generate_new_ideas_from_metrics(project_id), [])
        self.assertEqual(len(self.idea_service.list_ideas(project_id)), 1)

    def _run_script(
        self,
        script_path: Path,
        args: list[str] | None = None,
        *,
        env_updates: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(env_updates)
        return subprocess.run(
            [sys.executable, str(script_path), *(args or [])],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    @staticmethod
    def _parse_key_value_lines(stdout: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for line in stdout.splitlines():
            stripped = line.strip()
            if not stripped or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            parsed[key] = value
        return parsed

    @staticmethod
    def _parse_space_separated_pairs(line: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for chunk in line.split():
            key, value = chunk.split("=", 1)
            parsed[key] = value
        return parsed


if __name__ == "__main__":
    unittest.main()

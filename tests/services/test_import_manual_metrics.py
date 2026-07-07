from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from core.domain import MetricSnapshot, MetricSnapshotStatus, PublishingPlatform
from core.services import (
    AnalyticsService,
    BrandProfileService,
    FileSystemContentItemRepository,
    FileSystemExportPackageRepository,
    FileSystemIdeaRepository,
    FileSystemMetricSnapshotRepository,
    FileSystemProjectRepository,
    FileSystemPublicationRepository,
    FileSystemScenarioRepository,
    IdeaService,
    ProductionLifecycleService,
    ProjectService,
    PublishingService,
    ScenarioService,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "import_manual_metrics.py"


class ImportManualMetricsScriptTests(unittest.TestCase):
    _forbidden_project_marker = "nu" + "ra"

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name) / "projects_root"
        self._write_project_fixture("example")

        self.project_repository = FileSystemProjectRepository(self.projects_root)
        self.idea_repository = FileSystemIdeaRepository(self.projects_root)
        self.scenario_repository = FileSystemScenarioRepository(self.projects_root)
        self.content_repository = FileSystemContentItemRepository(self.projects_root)
        self.export_repository = FileSystemExportPackageRepository(self.projects_root)
        self.publication_repository = FileSystemPublicationRepository(self.projects_root)
        self.metric_repository = FileSystemMetricSnapshotRepository(self.projects_root)

        self.project_service = ProjectService(self.project_repository)
        self.brand_profile_service = BrandProfileService(self.project_repository)
        self.idea_service = IdeaService(self.idea_repository, self.project_service)
        self.scenario_service = ScenarioService(
            self.scenario_repository,
            self.project_repository,
            self.project_service,
            self.brand_profile_service,
            self.idea_service,
            self.idea_repository,
        )
        self.production_service = ProductionLifecycleService(
            self.content_repository,
            self.scenario_repository,
            self.project_service,
        )
        self.publishing_service = PublishingService(
            self.export_repository,
            self.publication_repository,
            self.content_repository,
            self.scenario_repository,
            self.project_service,
            self.projects_root,
        )
        self.analytics_service = AnalyticsService(
            self.metric_repository,
            self.publication_repository,
            self.content_repository,
            self.project_service,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_imports_manual_metrics_from_valid_json(self) -> None:
        content_item_id, publication_id, metric_snapshot_id = self._create_draft_metric_snapshot()
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": metric_snapshot_id,
                "metrics": {
                    "views": 100,
                    "likes": 12,
                    "comments": 3,
                    "shares": 1,
                    "saves": 2,
                    "clicks": 5,
                    "published_url": "https://example.invalid/example/manual/imported-post",
                },
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.strip().splitlines(),
            [
                "metrics_import_status=ok",
                "project_id=example",
                f"metric_snapshot_id={metric_snapshot_id}",
                "recorded_keys=views,likes,comments,shares,saves,clicks,published_url",
            ],
        )

        recorded = self.metric_repository.load_metric_snapshot("example", metric_snapshot_id)
        publication = self.publication_repository.load_publication("example", publication_id)

        self.assertEqual(recorded.status, MetricSnapshotStatus.RECORDED)
        self.assertEqual(recorded.content_item_id, content_item_id)
        self.assertEqual(recorded.content_metrics.views, 100)
        self.assertEqual(recorded.content_metrics.likes, 12)
        self.assertEqual(recorded.content_metrics.comments, 3)
        self.assertEqual(recorded.content_metrics.shares, 1)
        self.assertEqual(recorded.content_metrics.saves, 2)
        self.assertEqual(recorded.content_metrics.link_clicks, 5)
        self.assertEqual(publication.published_url, "https://example.invalid/example/manual/imported-post")

    def test_returns_error_when_argument_is_missing(self) -> None:
        completed = self._run_script([])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("usage: python scripts/import_manual_metrics.py <manual_metrics_json>", completed.stderr)

    def test_returns_error_when_too_many_arguments_are_provided(self) -> None:
        payload_path = self._write_json({"project_id": "example", "metric_snapshot_id": "metric_1", "metrics": {}})

        completed = self._run_script([str(payload_path), "extra.json"])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("usage: python scripts/import_manual_metrics.py <manual_metrics_json>", completed.stderr)

    def test_returns_error_when_json_file_is_missing(self) -> None:
        completed = self._run_script([str(self.projects_root / "missing.json")])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manual metrics JSON file does not exist", completed.stderr)

    def test_returns_error_when_json_is_invalid(self) -> None:
        payload_path = self.projects_root / "invalid_metrics.json"
        payload_path.write_text("{invalid", encoding="utf-8")

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manual metrics JSON is not valid JSON", completed.stderr)

    def test_accepts_utf8_bom_json_written_by_powershell_style_tools(self) -> None:
        _, _, metric_snapshot_id = self._create_draft_metric_snapshot()
        payload_path = self.projects_root / "metrics_with_bom.json"
        payload_path.write_text(
            json.dumps(
                {
                    "project_id": "example",
                    "metric_snapshot_id": metric_snapshot_id,
                    "metrics": {"views": 8},
                },
                indent=2,
            ),
            encoding="utf-8-sig",
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        recorded = self.metric_repository.load_metric_snapshot("example", metric_snapshot_id)
        self.assertEqual(recorded.content_metrics.views, 8)

    def test_returns_error_when_required_top_level_fields_are_missing(self) -> None:
        payload_path = self._write_json({"metric_snapshot_id": "metric_1", "metrics": {"views": 1}})

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manual metrics JSON is missing required fields: project_id", completed.stderr)

    def test_returns_error_when_metrics_field_is_missing(self) -> None:
        payload_path = self._write_json({"project_id": "example", "metric_snapshot_id": "metric_1"})

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manual metrics JSON is missing required fields: metrics", completed.stderr)

    def test_returns_error_when_metrics_is_not_an_object(self) -> None:
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": "metric_1",
                "metrics": ["views", 1],
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("metrics must be an object", completed.stderr)

    def test_returns_error_when_metrics_is_empty(self) -> None:
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": "metric_1",
                "metrics": {},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("metrics must not be empty", completed.stderr)

    def test_returns_error_for_unsupported_metric_keys(self) -> None:
        _, _, metric_snapshot_id = self._create_draft_metric_snapshot()
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": metric_snapshot_id,
                "metrics": {"follows": 1},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("Unknown metric keys: follows", completed.stderr)

    def test_returns_error_for_invalid_metric_values(self) -> None:
        _, _, metric_snapshot_id = self._create_draft_metric_snapshot()
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": metric_snapshot_id,
                "metrics": {"clicks": 1.5},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("clicks must be an integer", completed.stderr)

    def test_returns_error_when_project_is_unknown(self) -> None:
        payload_path = self._write_json(
            {
                "project_id": "missing_project",
                "metric_snapshot_id": "metric_missing",
                "metrics": {"views": 1},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("Project config not found for project_id 'missing_project'", completed.stderr)

    def test_returns_error_when_metric_snapshot_is_unknown(self) -> None:
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": "metric_missing",
                "metrics": {"views": 1},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("metric_snapshot_id 'metric_missing' not found for project_id 'example'", completed.stderr)

    def test_returns_error_when_snapshot_publication_cannot_be_found(self) -> None:
        _, publication_id, metric_snapshot_id = self._create_draft_metric_snapshot()
        publication_path = self.projects_root / "example" / "data" / "publications" / f"{publication_id}.json"
        publication_path.unlink()
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": metric_snapshot_id,
                "metrics": {"views": 1},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 1)
        self.assertIn(f"publication_id '{publication_id}' not found for project_id 'example'", completed.stderr)

    def test_accepts_clicks_and_records_link_clicks(self) -> None:
        _, _, metric_snapshot_id = self._create_draft_metric_snapshot()
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": metric_snapshot_id,
                "metrics": {"clicks": 7},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        recorded = self.metric_repository.load_metric_snapshot("example", metric_snapshot_id)
        self.assertEqual(recorded.content_metrics.link_clicks, 7)

    def test_accepts_published_url_and_updates_related_publication(self) -> None:
        _, publication_id, metric_snapshot_id = self._create_draft_metric_snapshot()
        payload_path = self._write_json(
            {
                "project_id": "example",
                "metric_snapshot_id": metric_snapshot_id,
                "metrics": {"published_url": "https://example.invalid/example/manual/final-url"},
            }
        )

        completed = self._run_script([str(payload_path)])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        publication = self.publication_repository.load_publication("example", publication_id)
        self.assertEqual(publication.published_url, "https://example.invalid/example/manual/final-url")

    def test_new_script_does_not_introduce_project_specific_marker_strings(self) -> None:
        script_text = SCRIPT_PATH.read_text(encoding="utf-8").lower()

        self.assertNotIn(self._forbidden_project_marker, script_text)
        self.assertNotIn("nu" + "ra-ai", script_text)

    def _create_draft_metric_snapshot(self) -> tuple[str, str, str]:
        idea = self.idea_service.create_idea(
            "example",
            title="Manual metrics import fixture",
            description="Create a generic published content item and a draft metric snapshot.",
            funnel_stage="trust",
        )
        approved_idea = self.idea_service.approve_idea("example", idea.idea_id)
        scenario = self.scenario_service.create_from_idea("example", approved_idea.idea_id)
        scenario = self.scenario_service.approve_scenario("example", scenario.scenario_id)
        content_item = self.production_service.create_content_item("example", scenario.scenario_id)
        content_item = self.production_service.run_technical_qa("example", content_item.content_item_id)
        content_item = self.production_service.approve_content("example", content_item.content_item_id)
        export_package = self.publishing_service.create_export_package(
            "example",
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        export_package = self.publishing_service.prepare_export("example", export_package.export_package_id)
        publication = self.publishing_service.create_publication(
            "example",
            content_item.content_item_id,
            export_package.export_package_id,
        )
        publication = self.publishing_service.publish_content(
            "example",
            publication.publication_id,
            f"https://example.invalid/example/published/{publication.publication_id}",
        )
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )
        return content_item.content_item_id, publication.publication_id, metric_snapshot.metric_snapshot_id

    def _run_script(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CONTENT_PLANT_PROJECTS_ROOT"] = str(self.projects_root)
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_json(self, payload: dict[str, object]) -> Path:
        path = self.projects_root / f"payload_{next(tempfile._get_candidate_names())}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _write_project_fixture(self, project_id: str) -> None:
        payload = json.loads((REPO_ROOT / "projects" / "example" / "project.yaml").read_text(encoding="utf-8"))
        payload["project_id"] = project_id
        payload["project_name"] = "Example Project"
        payload["project_slug"] = f"{project_id}_project"
        payload["brand"]["brand_name"] = "Example Brand"

        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.yaml").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

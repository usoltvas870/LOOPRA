from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from core.domain import MetricSnapshotStatus, PublishingPlatform
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
SCRIPT_PATH = REPO_ROOT / "scripts" / "find_metric_snapshots.py"


class FindMetricSnapshotsScriptTests(unittest.TestCase):
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

    def test_lists_one_draft_metric_snapshot(self) -> None:
        _, publication_id, metric_snapshot_id = self._create_draft_metric_snapshot()

        completed = self._run_script(["example"])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.strip().splitlines(),
            [
                "metric_snapshots_found=1",
                "project_id=example",
                "snapshots:",
                (
                    f"- metric_snapshot_id={metric_snapshot_id} "
                    f"publication_id={publication_id} "
                    f"content_item_id={self.metric_repository.load_metric_snapshot('example', metric_snapshot_id).content_item_id} "
                    "platform=telegram status=draft"
                ),
            ],
        )

    def test_returns_success_when_no_draft_metric_snapshots_exist(self) -> None:
        completed = self._run_script(["example"])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.strip().splitlines(),
            [
                "metric_snapshots_found=0",
                "project_id=example",
                "snapshots:",
            ],
        )

    def test_returns_error_when_argument_is_missing(self) -> None:
        completed = self._run_script([])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("usage: python scripts/find_metric_snapshots.py <project_id>", completed.stderr)

    def test_returns_error_when_too_many_arguments_are_provided(self) -> None:
        completed = self._run_script(["example", "extra"])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("usage: python scripts/find_metric_snapshots.py <project_id>", completed.stderr)

    def test_returns_error_when_project_storage_is_missing(self) -> None:
        completed = self._run_script(["missing_project"])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("Project config not found for project_id 'missing_project'", completed.stderr)

    def test_returns_error_when_metric_snapshot_storage_cannot_be_read(self) -> None:
        project_data_dir = self.projects_root / "example" / "data"
        project_data_dir.mkdir(parents=True, exist_ok=True)
        (project_data_dir / "metric_snapshots").write_text("not-a-directory", encoding="utf-8")

        completed = self._run_script(["example"])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("metric snapshot storage is not a directory", completed.stderr)

    def test_returns_error_when_stored_snapshot_json_is_invalid(self) -> None:
        snapshot_dir = self.projects_root / "example" / "data" / "metric_snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        (snapshot_dir / "metric_invalid.json").write_text("{not-json", encoding="utf-8")

        completed = self._run_script(["example"])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("stored snapshot JSON is not valid JSON", completed.stderr)

    def test_returns_error_when_required_snapshot_fields_are_missing(self) -> None:
        _, _, metric_snapshot_id = self._create_draft_metric_snapshot()
        snapshot_path = self.projects_root / "example" / "data" / "metric_snapshots" / f"{metric_snapshot_id}.json"
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        del payload["publication_id"]
        snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        completed = self._run_script(["example"])

        self.assertEqual(completed.returncode, 1)
        self.assertIn("stored snapshot JSON is missing required fields", completed.stderr)
        self.assertIn("publication_id", completed.stderr)

    def test_recorded_metric_snapshots_are_not_listed(self) -> None:
        _, _, metric_snapshot_id = self._create_draft_metric_snapshot()
        self.analytics_service.record_metrics("example", metric_snapshot_id, {"views": 10})

        completed = self._run_script(["example"])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.strip().splitlines(),
            [
                "metric_snapshots_found=0",
                "project_id=example",
                "snapshots:",
            ],
        )
        recorded = self.metric_repository.load_metric_snapshot("example", metric_snapshot_id)
        self.assertEqual(recorded.status, MetricSnapshotStatus.RECORDED)

    def test_respects_loopra_projects_root_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            override_root = Path(temp_dir) / "override_projects_root"
            self._write_project_fixture("override_example", projects_root=override_root)
            (
                analytics_service,
                metric_repository,
            ) = self._build_services_for_projects_root(override_root)
            _, publication_id, metric_snapshot_id = self._create_draft_metric_snapshot_for_services(
                analytics_service,
                override_root,
            )
            content_item_id = metric_repository.load_metric_snapshot(
                "override_example",
                metric_snapshot_id,
            ).content_item_id

            env = os.environ.copy()
            env["LOOPRA_PROJECTS_ROOT"] = str(override_root)
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "override_example"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                completed.stdout.strip().splitlines(),
                [
                    "metric_snapshots_found=1",
                    "project_id=override_example",
                    "snapshots:",
                    (
                        f"- metric_snapshot_id={metric_snapshot_id} "
                        f"publication_id={publication_id} "
                        f"content_item_id={content_item_id} "
                        "platform=telegram status=draft"
                    ),
                ],
            )

    def test_respects_content_plant_projects_root_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            override_root = Path(temp_dir) / "override_projects_root"
            self._write_project_fixture("override_example", projects_root=override_root)
            (
                analytics_service,
                metric_repository,
            ) = self._build_services_for_projects_root(override_root)
            _, publication_id, metric_snapshot_id = self._create_draft_metric_snapshot_for_services(
                analytics_service,
                override_root,
            )
            content_item_id = metric_repository.load_metric_snapshot(
                "override_example",
                metric_snapshot_id,
            ).content_item_id

            completed = self._run_script(
                ["override_example"],
                projects_root=override_root,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                completed.stdout.strip().splitlines(),
                [
                    "metric_snapshots_found=1",
                    "project_id=override_example",
                    "snapshots:",
                    (
                        f"- metric_snapshot_id={metric_snapshot_id} "
                        f"publication_id={publication_id} "
                        f"content_item_id={content_item_id} "
                        "platform=telegram status=draft"
                    ),
                ],
            )

    def test_new_script_does_not_introduce_project_specific_marker_strings(self) -> None:
        script_text = SCRIPT_PATH.read_text(encoding="utf-8").lower()

        self.assertNotIn(self._forbidden_project_marker, script_text)
        self.assertNotIn("nu" + "ra-ai", script_text)

    def _build_services_for_projects_root(
        self,
        projects_root: Path,
    ) -> tuple[AnalyticsService, FileSystemMetricSnapshotRepository]:
        project_repository = FileSystemProjectRepository(projects_root)
        idea_repository = FileSystemIdeaRepository(projects_root)
        scenario_repository = FileSystemScenarioRepository(projects_root)
        content_repository = FileSystemContentItemRepository(projects_root)
        export_repository = FileSystemExportPackageRepository(projects_root)
        publication_repository = FileSystemPublicationRepository(projects_root)
        metric_repository = FileSystemMetricSnapshotRepository(projects_root)

        project_service = ProjectService(project_repository)
        brand_profile_service = BrandProfileService(project_repository)
        idea_service = IdeaService(idea_repository, project_service)
        scenario_service = ScenarioService(
            scenario_repository,
            project_repository,
            project_service,
            brand_profile_service,
            idea_service,
            idea_repository,
        )
        production_service = ProductionLifecycleService(
            content_repository,
            scenario_repository,
            project_service,
        )
        publishing_service = PublishingService(
            export_repository,
            publication_repository,
            content_repository,
            scenario_repository,
            project_service,
            projects_root,
        )
        analytics_service = AnalyticsService(
            metric_repository,
            publication_repository,
            content_repository,
            project_service,
        )
        self._override_idea_service = idea_service
        self._override_scenario_service = scenario_service
        self._override_production_service = production_service
        self._override_publishing_service = publishing_service
        return analytics_service, metric_repository

    def _create_draft_metric_snapshot(self) -> tuple[str, str, str]:
        return self._create_draft_metric_snapshot_for_services(self.analytics_service, self.projects_root)

    def _create_draft_metric_snapshot_for_services(
        self,
        analytics_service: AnalyticsService,
        projects_root: Path,
    ) -> tuple[str, str, str]:
        if projects_root == self.projects_root:
            idea_service = self.idea_service
            scenario_service = self.scenario_service
            production_service = self.production_service
            publishing_service = self.publishing_service
            project_id = "example"
        else:
            idea_service = self._override_idea_service
            scenario_service = self._override_scenario_service
            production_service = self._override_production_service
            publishing_service = self._override_publishing_service
            project_id = "override_example"

        idea = idea_service.create_idea(
            project_id,
            title="Metric snapshot finder fixture",
            description="Create a generic published content item and a draft metric snapshot.",
            funnel_stage="trust",
        )
        approved_idea = idea_service.approve_idea(project_id, idea.idea_id)
        scenario = scenario_service.create_from_idea(project_id, approved_idea.idea_id)
        scenario = scenario_service.approve_scenario(project_id, scenario.scenario_id)
        content_item = production_service.create_content_item(project_id, scenario.scenario_id)
        content_item = production_service.run_technical_qa(project_id, content_item.content_item_id)
        content_item = production_service.approve_content(project_id, content_item.content_item_id)
        export_package = publishing_service.create_export_package(
            project_id,
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        export_package = publishing_service.prepare_export(project_id, export_package.export_package_id)
        publication = publishing_service.create_publication(
            project_id,
            content_item.content_item_id,
            export_package.export_package_id,
        )
        publication = publishing_service.publish_content(
            project_id,
            publication.publication_id,
            f"https://example.invalid/{project_id}/published/{publication.publication_id}",
        )
        metric_snapshot = analytics_service.create_metric_snapshot(
            project_id,
            publication.publication_id,
            content_item.content_item_id,
        )
        return content_item.content_item_id, publication.publication_id, metric_snapshot.metric_snapshot_id

    def _run_script(
        self,
        args: list[str],
        *,
        projects_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CONTENT_PLANT_PROJECTS_ROOT"] = str(projects_root or self.projects_root)
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_project_fixture(self, project_id: str, *, projects_root: Path | None = None) -> None:
        payload = json.loads((REPO_ROOT / "projects" / "example" / "project.yaml").read_text(encoding="utf-8"))
        payload["project_id"] = project_id
        payload["project_name"] = "Example Project"
        payload["project_slug"] = f"{project_id}_project"
        payload["brand"]["brand_name"] = "Example Brand"

        target_root = projects_root or self.projects_root
        project_dir = target_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.yaml").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

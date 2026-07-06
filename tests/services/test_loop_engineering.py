from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import (
    ContentItemStatus,
    ExportPackageStatus,
    InvalidStatusTransitionError,
    MetricSnapshotStatus,
    PublicationStatus,
    PublishingPlatform,
    ScenarioStatus,
)
from core.services import (
    AnalyticsService,
    AnalyticsValidationError,
    BrandProfileService,
    FileSystemContentItemRepository,
    FileSystemExportPackageRepository,
    FileSystemIdeaRepository,
    FileSystemMetricSnapshotRepository,
    FileSystemProjectRepository,
    FileSystemPublicationRepository,
    FileSystemScenarioRepository,
    IdeaService,
    LoopOrchestrator,
    ProductionLifecycleService,
    ProjectService,
    PublishingService,
    PublishingValidationError,
    ScenarioService,
)


class LoopEngineeringFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._write_project_fixture("example")
        self._write_project_fixture("second", project_name="Second Project")

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
        self.loop_orchestrator = LoopOrchestrator(
            self.idea_service,
            self.scenario_service,
            self.production_service,
            self.publishing_service,
            self.analytics_service,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_approved_scenario(self, project_id: str = "example"):
        idea = self.idea_service.create_idea(
            project_id,
            title="Minimal loop demo",
            description="Turn one approved idea into a deterministic text post artifact.",
            funnel_stage="trust",
        )
        approved_idea = self.idea_service.approve_idea(project_id, idea.idea_id)
        scenario = self.scenario_service.create_from_idea(project_id, approved_idea.idea_id)
        return self.scenario_service.approve_scenario(project_id, scenario.scenario_id)

    def create_approved_content_item(self, project_id: str = "example"):
        scenario = self.create_approved_scenario(project_id)
        content_item = self.production_service.create_content_item(project_id, scenario.scenario_id)
        content_item = self.production_service.run_technical_qa(project_id, content_item.content_item_id)
        content_item = self.production_service.approve_content(project_id, content_item.content_item_id)
        return scenario, content_item

    def create_ready_export_package(self, project_id: str = "example"):
        scenario, content_item = self.create_approved_content_item(project_id)
        export_package = self.publishing_service.create_export_package(
            project_id,
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        export_package = self.publishing_service.prepare_export(project_id, export_package.export_package_id)
        return scenario, self.content_repository.load_content_item(project_id, content_item.content_item_id), export_package

    def create_published_publication(self, project_id: str = "example"):
        _, content_item, export_package = self.create_ready_export_package(project_id)
        publication = self.publishing_service.create_publication(
            project_id,
            content_item.content_item_id,
            export_package.export_package_id,
        )
        publication = self.publishing_service.publish_content(
            project_id,
            publication.publication_id,
            f"https://example.invalid/{project_id}/published/{publication.publication_id}",
        )
        return content_item, export_package, publication

    def _write_project_fixture(self, project_id: str, *, project_name: str | None = None) -> None:
        payload = json.loads(Path("projects/example/project.yaml").read_text(encoding="utf-8"))
        payload["project_id"] = project_id
        payload["project_name"] = project_name or f"{project_id.title()} Project"
        payload["project_slug"] = f"{project_id}_project"
        payload["brand"]["brand_name"] = f"{project_id.title()} Brand"

        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.yaml").write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ProductionLifecycleServiceTests(LoopEngineeringFixture):
    def test_creates_content_item_from_approved_scenario(self) -> None:
        scenario = self.create_approved_scenario()

        content_item = self.production_service.create_content_item("example", scenario.scenario_id)

        self.assertEqual(content_item.project_id, "example")
        self.assertEqual(content_item.scenario_id, scenario.scenario_id)
        self.assertEqual(content_item.status, ContentItemStatus.RENDERED)
        self.assertTrue(content_item.body.strip())

    def test_runs_minimal_technical_qa(self) -> None:
        scenario = self.create_approved_scenario()
        content_item = self.production_service.create_content_item("example", scenario.scenario_id)

        reviewed = self.production_service.run_technical_qa("example", content_item.content_item_id)

        self.assertEqual(reviewed.status, ContentItemStatus.NEEDS_REVIEW)
        self.assertTrue(reviewed.technical_qa_passed)
        self.assertEqual(reviewed.render_output_metadata["technical_qa_errors"], [])

    def test_approves_review_ready_content(self) -> None:
        scenario = self.create_approved_scenario()
        content_item = self.production_service.create_content_item("example", scenario.scenario_id)
        reviewed = self.production_service.run_technical_qa("example", content_item.content_item_id)

        approved = self.production_service.approve_content("example", reviewed.content_item_id)

        self.assertEqual(approved.status, ContentItemStatus.APPROVED)

    def test_rejects_invalid_content_approval_transition(self) -> None:
        scenario = self.create_approved_scenario()
        content_item = self.production_service.create_content_item("example", scenario.scenario_id)

        with self.assertRaises(InvalidStatusTransitionError):
            self.production_service.approve_content("example", content_item.content_item_id)


class PublishingServiceTests(LoopEngineeringFixture):
    def test_creates_and_prepares_export_package(self) -> None:
        _, content_item = self.create_approved_content_item()

        export_package = self.publishing_service.create_export_package(
            "example",
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        prepared = self.publishing_service.prepare_export("example", export_package.export_package_id)
        exported_content = self.content_repository.load_content_item("example", content_item.content_item_id)

        self.assertEqual(prepared.status, ExportPackageStatus.READY)
        self.assertEqual(exported_content.status, ContentItemStatus.EXPORTED)
        self.assertEqual(len(prepared.package_files), 2)
        for file_path in prepared.package_files:
            with self.subTest(file_path=file_path):
                self.assertTrue(Path(file_path).exists())

    def test_creates_manual_publication_and_marks_it_published(self) -> None:
        _, content_item, export_package = self.create_ready_export_package()

        publication = self.publishing_service.create_publication(
            "example",
            content_item.content_item_id,
            export_package.export_package_id,
        )
        published = self.publishing_service.publish_content(
            "example",
            publication.publication_id,
            "https://example.invalid/example/published/post",
        )

        self.assertEqual(publication.status, PublicationStatus.PLANNED)
        self.assertEqual(published.status, PublicationStatus.PUBLISHED)
        self.assertEqual(published.published_url, "https://example.invalid/example/published/post")

    def test_marks_publication_as_failed(self) -> None:
        _, content_item, export_package = self.create_ready_export_package()
        publication = self.publishing_service.create_publication(
            "example",
            content_item.content_item_id,
            export_package.export_package_id,
        )

        failed = self.publishing_service.fail_publication(
            "example",
            publication.publication_id,
            "Manual publishing failed in external channel.",
        )

        self.assertEqual(failed.status, PublicationStatus.FAILED)
        self.assertIn("failed", failed.notes.lower())

    def test_rejects_invalid_publication_transition(self) -> None:
        _, content_item, export_package, = self.create_ready_export_package()
        publication = self.publishing_service.create_publication(
            "example",
            content_item.content_item_id,
            export_package.export_package_id,
        )
        published = self.publishing_service.publish_content(
            "example",
            publication.publication_id,
            "https://example.invalid/example/published/post",
        )

        with self.assertRaises(InvalidStatusTransitionError):
            self.publishing_service.fail_publication("example", published.publication_id, "too late")

    def test_rejects_publication_creation_before_export_is_ready(self) -> None:
        _, content_item = self.create_approved_content_item()
        export_package = self.publishing_service.create_export_package(
            "example",
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )

        with self.assertRaises(PublishingValidationError):
            self.publishing_service.create_publication(
                "example",
                content_item.content_item_id,
                export_package.export_package_id,
            )


class AnalyticsServiceTests(LoopEngineeringFixture):
    def test_creates_metric_snapshot_and_records_metrics(self) -> None:
        content_item, _, publication = self.create_published_publication()

        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )
        recorded = self.analytics_service.record_metrics(
            "example",
            metric_snapshot.metric_snapshot_id,
            {"views": 120, "likes": 15, "shares": 3},
        )

        self.assertEqual(metric_snapshot.status, MetricSnapshotStatus.DRAFT)
        self.assertEqual(recorded.status, MetricSnapshotStatus.RECORDED)
        self.assertEqual(recorded.content_metrics.views, 120)
        self.assertEqual(recorded.content_metrics.likes, 15)

    def test_future_facing_analytics_stubs_return_empty_lists(self) -> None:
        self.assertEqual(self.analytics_service.get_insights("example"), [])
        self.assertEqual(self.analytics_service.generate_new_ideas_from_metrics("example"), [])

    def test_rejects_recording_metrics_twice(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )
        self.analytics_service.record_metrics(
            "example",
            metric_snapshot.metric_snapshot_id,
            {"views": 1},
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics(
                "example",
                metric_snapshot.metric_snapshot_id,
                {"views": 2},
            )


class LoopOrchestratorTests(LoopEngineeringFixture):
    def test_runs_minimal_end_to_end_loop_for_generic_project(self) -> None:
        idea = self.idea_service.create_idea(
            "second",
            title="Project-agnostic end-to-end loop",
            description="Use the smallest deterministic loop without any project-specific hardcode.",
            funnel_stage="trust",
        )

        result = self.loop_orchestrator.run_minimal_loop("second", idea.idea_id)
        loop_status = self.loop_orchestrator.get_loop_status("second")
        publication = self.publication_repository.load_publication("second", result["publication_id"])
        metric_snapshot = self.metric_repository.load_metric_snapshot("second", result["metric_snapshot_id"])

        self.assertEqual(result["project_id"], "second")
        self.assertEqual(result["idea_id"], idea.idea_id)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(publication.status, PublicationStatus.PUBLISHED)
        self.assertEqual(metric_snapshot.status, MetricSnapshotStatus.RECORDED)
        self.assertEqual(loop_status["publications"], {"published": 1})
        self.assertEqual(loop_status["metric_snapshots"], {"recorded": 1})
        self.assertEqual(publication.platform, PublishingPlatform.TELEGRAM)

        export_dir = self.projects_root / "second" / "exports" / result["export_package_id"]
        self.assertTrue(export_dir.exists())

    def test_generated_scenario_is_approved_before_content_creation(self) -> None:
        idea = self.idea_service.create_idea(
            "second",
            title="Approved scenario in orchestrator",
            description="The loop should explicitly approve the generated scenario.",
        )

        result = self.loop_orchestrator.run_minimal_loop("second", idea.idea_id)
        scenario = self.scenario_repository.load_scenario("second", result["scenario_id"])

        self.assertEqual(scenario.status, ScenarioStatus.APPROVED)


if __name__ == "__main__":
    unittest.main()

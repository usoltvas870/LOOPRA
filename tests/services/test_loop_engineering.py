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
from core.domain.models import validated_model_copy
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

    @staticmethod
    def read_publication_notes(publication) -> dict[str, object]:
        return json.loads(publication.notes)

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
    _forbidden_project_marker = "nu" + "ra"

    def test_creates_and_prepares_export_package(self) -> None:
        scenario, content_item = self.create_approved_content_item()

        export_package = self.publishing_service.create_export_package(
            "example",
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        prepared = self.publishing_service.prepare_export("example", export_package.export_package_id)
        exported_content = self.content_repository.load_content_item("example", content_item.content_item_id)
        export_dir = self.projects_root / "example" / "exports" / prepared.export_package_id
        expected_files = {
            export_dir / "title.txt",
            export_dir / "body.txt",
            export_dir / "caption_telegram.txt",
            export_dir / "manual_publication_checklist.txt",
            export_dir / "metadata.json",
            export_dir / "manifest.json",
        }

        self.assertEqual(prepared.status, ExportPackageStatus.READY)
        self.assertEqual(exported_content.status, ContentItemStatus.EXPORTED)
        self.assertEqual({Path(file_path) for file_path in prepared.package_files}, expected_files)
        for file_path in expected_files:
            with self.subTest(file_path=str(file_path)):
                self.assertTrue(file_path.exists())

        self.assertEqual((export_dir / "title.txt").read_text(encoding="utf-8"), content_item.title)
        self.assertEqual((export_dir / "body.txt").read_text(encoding="utf-8"), content_item.body)
        self.assertEqual(
            (export_dir / "caption_telegram.txt").read_text(encoding="utf-8"),
            scenario.caption_drafts["telegram"],
        )

        checklist_text = (export_dir / "manual_publication_checklist.txt").read_text(encoding="utf-8")
        self.assertIn("manual publication", checklist_text.lower())
        self.assertNotIn(self._forbidden_project_marker, checklist_text.lower())

        metadata = json.loads((export_dir / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(
            metadata,
            {
                "project_id": "example",
                "content_item_id": content_item.content_item_id,
                "scenario_id": scenario.scenario_id,
                "content_format": "text_social_post",
                "target_platform": "telegram",
                "manual_publication_only": True,
                "prepared_at": metadata["prepared_at"],
                "brand_profile_id": scenario.brand_profile_id,
                "funnel_stage": scenario.funnel_stage,
                "title": content_item.title,
                "content_item_status": "approved",
                "target_platforms": ["telegram", "threads", "vk"],
                "scenario_qa_warnings": scenario.qa_warnings,
            },
        )

        manifest = json.loads((export_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(
            manifest,
            {
                "package_id": prepared.export_package_id,
                "project_id": "example",
                "content_item_id": content_item.content_item_id,
                "scenario_id": scenario.scenario_id,
                "content_format": "text_social_post",
                "target_platform": "telegram",
                "manual_publication_only": True,
                "prepared_at": manifest["prepared_at"],
                "status": "ready",
                "files": [
                    {"name": "title.txt", "role": "title"},
                    {"name": "body.txt", "role": "body"},
                    {"name": "caption_telegram.txt", "role": "caption"},
                    {"name": "manual_publication_checklist.txt", "role": "manual_publication_checklist"},
                    {"name": "metadata.json", "role": "metadata"},
                    {"name": "manifest.json", "role": "manifest"},
                ],
            },
        )
        self.assertTrue(manifest["prepared_at"])
        self.assertTrue(all(not Path(file_info["name"]).is_absolute() for file_info in manifest["files"]))
        self.assertNotIn(self._forbidden_project_marker, json.dumps(metadata).lower())
        self.assertNotIn(self._forbidden_project_marker, json.dumps(manifest).lower())

    def test_prepare_export_prefers_scenario_caption_draft_for_target_platform(self) -> None:
        scenario, content_item = self.create_approved_content_item()
        scenario = validated_model_copy(scenario, caption_drafts={"telegram": "Scenario draft caption for export"})
        self.scenario_repository.save_scenario(scenario)
        content_item = self.production_service.create_content_item("example", scenario.scenario_id)
        content_item = self.production_service.run_technical_qa("example", content_item.content_item_id)
        content_item = self.production_service.approve_content("example", content_item.content_item_id)

        export_package = self.publishing_service.create_export_package(
            "example",
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        export_package = self.publishing_service.prepare_export("example", export_package.export_package_id)

        caption_path = self.projects_root / "example" / "exports" / export_package.export_package_id / "caption_telegram.txt"
        self.assertEqual(caption_path.read_text(encoding="utf-8"), "Scenario draft caption for export")

    def test_prepare_export_falls_back_safely_when_caption_draft_is_missing(self) -> None:
        scenario = self.create_approved_scenario()
        scenario = validated_model_copy(
            scenario,
            target_platforms=[PublishingPlatform.TELEGRAM],
            caption_drafts={},
        )
        self.scenario_repository.save_scenario(scenario)
        content_item = self.production_service.create_content_item("example", scenario.scenario_id)
        content_item = self.production_service.run_technical_qa("example", content_item.content_item_id)
        content_item = self.production_service.approve_content("example", content_item.content_item_id)

        export_package = self.publishing_service.create_export_package(
            "example",
            content_item.content_item_id,
            PublishingPlatform.TELEGRAM,
        )
        prepared = self.publishing_service.prepare_export("example", export_package.export_package_id)

        caption_path = self.projects_root / "example" / "exports" / prepared.export_package_id / "caption_telegram.txt"
        self.assertEqual(caption_path.read_text(encoding="utf-8"), content_item.body)

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
        created_metadata = self.read_publication_notes(publication)
        published_metadata = self.read_publication_notes(published)

        self.assertEqual(publication.status, PublicationStatus.PLANNED)
        self.assertEqual(publication.project_id, "example")
        self.assertEqual(publication.content_item_id, content_item.content_item_id)
        self.assertEqual(publication.export_package_id, export_package.export_package_id)
        self.assertEqual(created_metadata["project_id"], "example")
        self.assertEqual(created_metadata["content_item_id"], content_item.content_item_id)
        self.assertEqual(created_metadata["export_package_id"], export_package.export_package_id)
        self.assertTrue(created_metadata["manual_publication_only"])
        self.assertEqual(created_metadata["publication_method"], "manual")
        self.assertEqual(created_metadata["source"], "publishing_hub")
        self.assertEqual(created_metadata["target_platform"], "telegram")
        self.assertIsInstance(created_metadata["created_at"], str)
        self.assertEqual(published.status, PublicationStatus.PUBLISHED)
        self.assertEqual(published.published_url, "https://example.invalid/example/published/post")
        self.assertIsNotNone(published.published_at)
        self.assertEqual(published_metadata["published_url"], "https://example.invalid/example/published/post")
        self.assertIsInstance(published_metadata["published_at"], str)
        self.assertNotIn(self._forbidden_project_marker, publication.notes.lower())
        self.assertNotIn(self._forbidden_project_marker, published.notes.lower())

    def test_rejects_empty_published_url(self) -> None:
        _, content_item, export_package = self.create_ready_export_package()
        publication = self.publishing_service.create_publication(
            "example",
            content_item.content_item_id,
            export_package.export_package_id,
        )

        with self.assertRaises(PublishingValidationError):
            self.publishing_service.publish_content("example", publication.publication_id, "   ")

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
        failed_metadata = self.read_publication_notes(failed)

        self.assertEqual(failed.status, PublicationStatus.FAILED)
        self.assertEqual(failed_metadata["failure_reason"], "Manual publishing failed in external channel.")
        self.assertEqual(failed_metadata["publication_method"], "manual")
        self.assertTrue(failed_metadata["manual_publication_only"])
        self.assertNotIn(self._forbidden_project_marker, failed.notes.lower())

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
    _forbidden_project_marker = "nu" + "ra"

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
            {
                "views": 120,
                "likes": 15,
                "comments": 4,
                "shares": 3,
                "saves": 7,
                "clicks": 9,
                "published_url": "https://example.invalid/example/published/updated-post",
            },
        )
        updated_publication = self.publication_repository.load_publication("example", publication.publication_id)

        self.assertEqual(metric_snapshot.status, MetricSnapshotStatus.DRAFT)
        self.assertEqual(metric_snapshot.project_id, "example")
        self.assertEqual(metric_snapshot.publication_id, publication.publication_id)
        self.assertEqual(metric_snapshot.content_item_id, content_item.content_item_id)
        self.assertEqual(metric_snapshot.source_type.value, "manual")
        self.assertIsInstance(metric_snapshot.created_at, type(metric_snapshot.captured_at))
        self.assertEqual(recorded.status, MetricSnapshotStatus.RECORDED)
        self.assertEqual(recorded.content_metrics.views, 120)
        self.assertEqual(recorded.content_metrics.likes, 15)
        self.assertEqual(recorded.content_metrics.comments, 4)
        self.assertEqual(recorded.content_metrics.shares, 3)
        self.assertEqual(recorded.content_metrics.saves, 7)
        self.assertEqual(recorded.content_metrics.link_clicks, 9)
        self.assertIsInstance(recorded.captured_at, type(metric_snapshot.captured_at))
        self.assertEqual(updated_publication.published_url, "https://example.invalid/example/published/updated-post")
        self.assertNotIn(self._forbidden_project_marker, updated_publication.published_url.lower())

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

    def test_rejects_empty_metrics_dict(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics("example", metric_snapshot.metric_snapshot_id, {})

    def test_rejects_unknown_metric_keys(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics(
                "example",
                metric_snapshot.metric_snapshot_id,
                {"bookmarks": 3},
            )

    def test_rejects_follows_until_model_has_storage_field(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics(
                "example",
                metric_snapshot.metric_snapshot_id,
                {"follows": 1},
            )

    def test_rejects_negative_numeric_metrics(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics(
                "example",
                metric_snapshot.metric_snapshot_id,
                {"views": -1},
            )

    def test_rejects_non_integer_numeric_metrics(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics(
                "example",
                metric_snapshot.metric_snapshot_id,
                {"clicks": 1.5},
            )

    def test_rejects_empty_published_url_in_metrics(self) -> None:
        content_item, _, publication = self.create_published_publication()
        metric_snapshot = self.analytics_service.create_metric_snapshot(
            "example",
            publication.publication_id,
            content_item.content_item_id,
        )

        with self.assertRaises(AnalyticsValidationError):
            self.analytics_service.record_metrics(
                "example",
                metric_snapshot.metric_snapshot_id,
                {"published_url": "   "},
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
        self.assertEqual(metric_snapshot.status, MetricSnapshotStatus.DRAFT)
        self.assertEqual(loop_status["publications"], {"published": 1})
        self.assertEqual(loop_status["metric_snapshots"], {"draft": 1})
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

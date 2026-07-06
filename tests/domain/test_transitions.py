from __future__ import annotations

from datetime import datetime, timezone
import unittest

from core.domain import (
    ContentItem,
    ContentItemStatus,
    ExportPackage,
    ExportPackageStatus,
    Idea,
    IdeaStatus,
    InvalidStatusTransitionError,
    MetricSnapshot,
    MetricSnapshotStatus,
    Publication,
    PublicationStatus,
    PublishingPlatform,
    RenderJob,
    RenderJobStatus,
    Scenario,
    ScenarioStatus,
)


class StatusTransitionTests(unittest.TestCase):
    def test_idea_valid_transitions(self) -> None:
        cases = [
            (IdeaStatus.RAW, IdeaStatus.APPROVED),
            (IdeaStatus.APPROVED, IdeaStatus.SCRIPTED),
        ]

        for current_status, next_status in cases:
            with self.subTest(current_status=current_status, next_status=next_status):
                idea = Idea(
                    idea_id="idea_001",
                    workspace_id="workspace_001",
                    project_id="project_001",
                    title="Idea",
                    status=current_status,
                )
                updated = idea.transition_to(next_status)
                self.assertEqual(updated.status, next_status)

    def test_idea_invalid_transition_is_rejected(self) -> None:
        idea = Idea(
            idea_id="idea_001",
            workspace_id="workspace_001",
            project_id="project_001",
            title="Idea",
            status=IdeaStatus.RAW,
        )

        with self.assertRaises(InvalidStatusTransitionError):
            idea.transition_to(IdeaStatus.SCRIPTED)

    def test_scenario_invalid_transition_is_rejected(self) -> None:
        scenario = Scenario(
            scenario_id="scenario_001",
            workspace_id="workspace_001",
            project_id="project_001",
            idea_id="idea_001",
            brand_profile_id="brand_001",
            title="Scenario",
            status=ScenarioStatus.DRAFT,
        )

        with self.assertRaises(InvalidStatusTransitionError):
            scenario.transition_to(ScenarioStatus.APPROVED)

    def test_render_job_transition_flow(self) -> None:
        render_job = RenderJob(
            render_job_id="render_001",
            workspace_id="workspace_001",
            project_id="project_001",
            scenario_id="scenario_001",
        )

        validated = render_job.transition_to(RenderJobStatus.VALIDATING)
        rendering = validated.transition_to(RenderJobStatus.RENDERING)
        rendered = rendering.transition_to(RenderJobStatus.RENDERED)

        self.assertEqual(rendered.status, RenderJobStatus.RENDERED)

    def test_content_item_transition_flow(self) -> None:
        content_item = ContentItem(
            content_item_id="content_001",
            workspace_id="workspace_001",
            project_id="project_001",
            scenario_id="scenario_001",
            brand_profile_id="brand_001",
            title="Content",
        )

        in_production = content_item.transition_to(ContentItemStatus.IN_PRODUCTION)
        rendered = in_production.transition_to(ContentItemStatus.RENDERED)
        needs_review = rendered.transition_to(ContentItemStatus.NEEDS_REVIEW)
        approved = needs_review.transition_to(ContentItemStatus.APPROVED)
        exported = approved.transition_to(ContentItemStatus.EXPORTED)

        self.assertEqual(exported.status, ContentItemStatus.EXPORTED)

    def test_export_package_transition_flow(self) -> None:
        export_package = ExportPackage(
            export_package_id="export_001",
            workspace_id="workspace_001",
            project_id="project_001",
            content_item_id="content_001",
            target_platform=PublishingPlatform.INSTAGRAM,
        )

        ready = export_package.transition_to(ExportPackageStatus.READY)

        self.assertEqual(ready.status, ExportPackageStatus.READY)

    def test_publication_invalid_transition_is_rejected(self) -> None:
        publication = Publication(
            publication_id="publication_001",
            workspace_id="workspace_001",
            project_id="project_001",
            content_item_id="content_001",
            export_package_id="export_001",
            platform=PublishingPlatform.INSTAGRAM,
            status=PublicationStatus.PUBLISHED,
            published_at=datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc),
            published_url="https://example.com/post/1",
        )

        with self.assertRaises(InvalidStatusTransitionError):
            publication.transition_to(PublicationStatus.FAILED)

    def test_publication_transition_to_published_sets_manual_publication_data(self) -> None:
        publication = Publication(
            publication_id="publication_001",
            workspace_id="workspace_001",
            project_id="project_001",
            content_item_id="content_001",
            export_package_id="export_001",
            platform=PublishingPlatform.TELEGRAM,
        )

        published_at = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)
        published = publication.transition_to(
            PublicationStatus.PUBLISHED,
            published_at=published_at,
            published_url="https://example.com/post/1",
        )

        self.assertEqual(published.status, PublicationStatus.PUBLISHED)
        self.assertEqual(published.published_at, published_at)
        self.assertEqual(published.published_url, "https://example.com/post/1")

    def test_metric_snapshot_invalid_transition_is_rejected(self) -> None:
        metric_snapshot = MetricSnapshot(
            metric_snapshot_id="metric_001",
            workspace_id="workspace_001",
            project_id="project_001",
            publication_id="publication_001",
            content_item_id="content_001",
            platform=PublishingPlatform.TIKTOK,
            status=MetricSnapshotStatus.RECORDED,
        )

        with self.assertRaises(InvalidStatusTransitionError):
            metric_snapshot.transition_to(MetricSnapshotStatus.DRAFT)


if __name__ == "__main__":
    unittest.main()

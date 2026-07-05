from __future__ import annotations

import unittest

from pydantic import ValidationError

from core.domain import (
    BrandProfile,
    ContentFormat,
    ContentItem,
    ContentItemStatus,
    DomainModule,
    ExportPackage,
    Idea,
    MetricSnapshot,
    OutputFile,
    OutputFileType,
    Project,
    Publication,
    PublicationStatus,
    PublishingPlatform,
    RenderJob,
    Scenario,
    Workspace,
)


class DomainModelTests(unittest.TestCase):
    def test_domain_models_are_importable_and_can_be_created(self) -> None:
        workspace = Workspace(workspace_id="workspace_001", name="Internal Workspace", slug="internal")
        project = Project(
            project_id="project_001",
            workspace_id=workspace.workspace_id,
            name="Demo Project",
            slug="demo-project",
        )
        brand_profile = BrandProfile(
            brand_profile_id="brand_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            name="Demo Brand",
            positioning="Practical and clear",
            brand_values=["clarity", "trust"],
        )
        idea = Idea(
            idea_id="idea_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            title="Hook around one pain point",
        )
        scenario = Scenario(
            scenario_id="scenario_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            idea_id=idea.idea_id,
            brand_profile_id=brand_profile.brand_profile_id,
            title="Draft social post",
        )
        render_job = RenderJob(
            render_job_id="render_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            scenario_id=scenario.scenario_id,
        )
        content_item = ContentItem(
            content_item_id="content_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            scenario_id=scenario.scenario_id,
            brand_profile_id=brand_profile.brand_profile_id,
            render_job_id=render_job.render_job_id,
            title="Ready text post",
            body="A concise draft",
        )
        output_file = OutputFile(
            output_file_id="file_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            render_job_id=render_job.render_job_id,
            content_item_id=content_item.content_item_id,
            file_type=OutputFileType.TEXT,
            path="storage/projects/demo-project/renders/content_001/post.txt",
            mime_type="text/plain",
            size_bytes=128,
        )
        export_package = ExportPackage(
            export_package_id="export_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            content_item_id=content_item.content_item_id,
            target_platform=PublishingPlatform.TELEGRAM,
        )
        publication = Publication(
            publication_id="publication_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            content_item_id=content_item.content_item_id,
            export_package_id=export_package.export_package_id,
            platform=PublishingPlatform.TELEGRAM,
        )
        metric_snapshot = MetricSnapshot(
            metric_snapshot_id="metric_001",
            workspace_id=workspace.workspace_id,
            project_id=project.project_id,
            publication_id=publication.publication_id,
            content_item_id=content_item.content_item_id,
            platform=PublishingPlatform.TELEGRAM,
        )

        self.assertEqual(idea.content_format, ContentFormat.TEXT_SOCIAL_POST)
        self.assertEqual(scenario.content_format, ContentFormat.TEXT_SOCIAL_POST)
        self.assertEqual(content_item.content_format, ContentFormat.TEXT_SOCIAL_POST)
        self.assertEqual(export_package.content_format, ContentFormat.TEXT_SOCIAL_POST)
        self.assertEqual(output_file.owner_module, DomainModule.PRODUCTION_ENGINE)
        self.assertEqual(export_package.owner_module, DomainModule.PUBLISHING_HUB)
        self.assertEqual(metric_snapshot.owner_module, DomainModule.ANALYTICS)

    def test_project_level_entities_require_project_id(self) -> None:
        entity_types = [
            BrandProfile,
            Idea,
            Scenario,
            RenderJob,
            OutputFile,
            ContentItem,
            ExportPackage,
            Publication,
            MetricSnapshot,
        ]

        for entity_type in entity_types:
            with self.subTest(entity_type=entity_type.__name__):
                self.assertIn("project_id", entity_type.model_fields)
                self.assertTrue(entity_type.model_fields["project_id"].is_required())

    def test_publication_published_state_requires_url_and_timestamp(self) -> None:
        with self.assertRaises(ValidationError):
            Publication(
                publication_id="publication_001",
                workspace_id="workspace_001",
                project_id="project_001",
                content_item_id="content_001",
                export_package_id="export_001",
                platform=PublishingPlatform.INSTAGRAM,
                status=PublicationStatus.PUBLISHED,
            )

    def test_content_item_and_publication_statuses_are_separate_lifecycles(self) -> None:
        content_item = ContentItem(
            content_item_id="content_001",
            workspace_id="workspace_001",
            project_id="project_001",
            scenario_id="scenario_001",
            brand_profile_id="brand_001",
            title="Approved content",
            status=ContentItemStatus.APPROVED,
        )
        publication = Publication(
            publication_id="publication_001",
            workspace_id="workspace_001",
            project_id="project_001",
            content_item_id=content_item.content_item_id,
            export_package_id="export_001",
            platform=PublishingPlatform.INSTAGRAM,
            status=PublicationStatus.PLANNED,
        )

        self.assertEqual(content_item.status, ContentItemStatus.APPROVED)
        self.assertEqual(publication.status, PublicationStatus.PLANNED)

    def test_export_package_boundary_rejects_production_engine_owner(self) -> None:
        with self.assertRaises(ValidationError):
            ExportPackage(
                export_package_id="export_001",
                workspace_id="workspace_001",
                project_id="project_001",
                content_item_id="content_001",
                owner_module=DomainModule.PRODUCTION_ENGINE,
                target_platform=PublishingPlatform.TELEGRAM,
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import (
    ContentFormat,
    ContentItemStatus,
    OutputFile,
    OutputFileType,
    ProductionBrief,
    ProductionBriefStatus,
    ProductionOutput,
    ProductionScene,
    RenderJob,
    RenderJobStatus,
)
from core.services._storage import build_entity_id
from core.services.production import FileSystemContentItemRepository
from core.services.production_pipeline import (
    FileSystemOutputFileRepository,
    FileSystemProductionBriefRepository,
    FileSystemRenderJobRepository,
    ProductionPipelineService,
    ProductionPipelineValidationError,
)
from core.services.projects import FileSystemProjectRepository, ProjectService


class ProductionPipelineServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)

        project_dir = self.projects_root / "nura"
        project_dir.mkdir(parents=True, exist_ok=True)
        config = {
            "workspace_id": "internal",
            "project_id": "nura",
            "project_name": "NURA",
            "project_slug": "nura",
            "description": "Test project",
            "default_language": "ru",
            "status": "active",
        }
        (project_dir / "project.yaml").write_text(json.dumps(config), encoding="utf-8")

        project_repo = FileSystemProjectRepository(projects_root=self.projects_root)
        project_service = ProjectService(project_repo)
        self.brief_repo = FileSystemProductionBriefRepository(projects_root=self.projects_root)
        self.render_job_repo = FileSystemRenderJobRepository(projects_root=self.projects_root)
        self.output_file_repo = FileSystemOutputFileRepository(projects_root=self.projects_root)
        self.content_repo = FileSystemContentItemRepository(projects_root=self.projects_root)
        self.service = ProductionPipelineService(
            brief_repo=self.brief_repo,
            render_job_repo=self.render_job_repo,
            output_file_repo=self.output_file_repo,
            content_repo=self.content_repo,
            project_service=project_service,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_render_job_success(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
        )
        self.brief_repo.save_brief(brief)
        brief = brief.transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)

        render_job = self.service.create_render_job("nura", brief.production_brief_id)

        self.assertEqual(render_job.status, RenderJobStatus.VALIDATING)
        self.assertEqual(render_job.content_format, ContentFormat.SHORT_VERTICAL_VIDEO)
        self.assertEqual(render_job.scenario_id, "scenario_test")
        self.assertEqual(render_job.input_snapshot["brief_id"], brief.production_brief_id)

    def test_create_render_job_brief_not_validated(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
        )
        self.brief_repo.save_brief(brief)

        with self.assertRaises(ProductionPipelineValidationError):
            self.service.create_render_job("nura", brief.production_brief_id)

    def test_validate_assets_missing_files(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            scenes=[
                ProductionScene(
                    index=0,
                    image_source="nonexistent_test_scene_0.png",
                    duration_sec=3.0,
                ),
            ],
        )
        brief = brief.transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)

        render_job = self.service.create_render_job("nura", brief.production_brief_id)
        render_job = self.service.validate_assets("nura", render_job.render_job_id)

        self.assertEqual(render_job.status, RenderJobStatus.FAILED)
        self.assertFalse(render_job.input_snapshot["asset_report"]["passed"])
        self.assertGreater(len(render_job.input_snapshot["asset_report"]["missing_files"]), 0)

    def test_validate_assets_all_present(self) -> None:
        from PIL import Image

        img_path = Path(self.temp_dir.name) / "scene_0_test.png"
        Image.new("RGB", (10, 10), "blue").save(img_path)

        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            output=ProductionOutput(resolution_width=10, resolution_height=10),
            scenes=[
                ProductionScene(
                    index=0,
                    image_source=str(img_path),
                    duration_sec=3.0,
                ),
            ],
        )
        brief = brief.transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)

        render_job = self.service.create_render_job("nura", brief.production_brief_id)
        render_job = self.service.validate_assets("nura", render_job.render_job_id)

        self.assertEqual(render_job.status, RenderJobStatus.RENDERING)
        self.assertTrue(render_job.input_snapshot["asset_report"]["passed"])

    def test_execute_render_creates_output_files(self) -> None:
        from PIL import Image

        img_path = Path(self.temp_dir.name) / "nura" / "test_scene.png"
        img_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (1080, 1920), "blue").save(img_path)

        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            scenes=[
                ProductionScene(
                    index=0,
                    image_source=str(img_path),
                    duration_sec=1.0,
                ),
            ],
        )
        brief = brief.transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)

        render_job = RenderJob(
            render_job_id=build_entity_id("rjob"),
            workspace_id="internal",
            project_id="nura",
            scenario_id=brief.scenario_id,
            content_format=brief.content_format,
            status=RenderJobStatus.RENDERING,
            input_snapshot={"brief_id": brief.production_brief_id},
        )
        self.render_job_repo.save_render_job(render_job)

        render_job = self.service.execute_render("nura", render_job.render_job_id)

        self.assertEqual(render_job.status, RenderJobStatus.RENDERED)
        artifact_count = render_job.input_snapshot.get("artifact_count", 0)
        self.assertGreaterEqual(artifact_count, 1)

        output_files = self.output_file_repo.list_output_files_by_render_job(
            "nura", render_job.render_job_id
        )
        self.assertGreater(len(output_files), 0)
        for of in output_files:
            self.assertEqual(of.render_job_id, render_job.render_job_id)

    def test_execute_render_wrong_status(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
        )
        brief = brief.transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)

        render_job = self.service.create_render_job("nura", brief.production_brief_id)

        with self.assertRaises(ProductionPipelineValidationError):
            self.service.execute_render("nura", render_job.render_job_id)

    def test_create_content_from_render(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
        )
        brief = brief.transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)

        render_job = RenderJob(
            render_job_id=build_entity_id("rjob"),
            workspace_id="internal",
            project_id="nura",
            scenario_id=brief.scenario_id,
            content_format=brief.content_format,
            status=RenderJobStatus.RENDERED,
            input_snapshot={"brief_id": brief.production_brief_id},
        )
        self.render_job_repo.save_render_job(render_job)

        content_item = self.service.create_content_from_render("nura", render_job.render_job_id)

        self.assertEqual(content_item.status, ContentItemStatus.RENDERED)
        self.assertEqual(content_item.render_job_id, render_job.render_job_id)
        self.assertIn("render_job_id", content_item.render_output_metadata)
        self.assertEqual(
            content_item.render_output_metadata["render_job_id"], render_job.render_job_id
        )

    def test_render_job_repo_save_and_load(self) -> None:
        render_job = RenderJob(
            render_job_id=build_entity_id("rjob"),
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_test",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
        )
        self.render_job_repo.save_render_job(render_job)

        loaded = self.render_job_repo.load_render_job("nura", render_job.render_job_id)
        self.assertEqual(loaded.render_job_id, render_job.render_job_id)
        self.assertEqual(loaded.scenario_id, render_job.scenario_id)
        self.assertEqual(loaded.status, RenderJobStatus.QUEUED)

        jobs = self.render_job_repo.list_render_jobs("nura")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].render_job_id, render_job.render_job_id)

    def test_output_file_repo_save_and_filter_by_render_job(self) -> None:
        rjob_id_1 = build_entity_id("rjob")
        rjob_id_2 = build_entity_id("rjob")

        of1 = OutputFile(
            output_file_id=build_entity_id("of"),
            workspace_id="internal",
            project_id="nura",
            render_job_id=rjob_id_1,
            file_type=OutputFileType.VIDEO,
            path="renders/r1/final.mp4",
            mime_type="video/mp4",
        )
        of2 = OutputFile(
            output_file_id=build_entity_id("of"),
            workspace_id="internal",
            project_id="nura",
            render_job_id=rjob_id_1,
            file_type=OutputFileType.METADATA,
            path="renders/r1/subtitles.srt",
            mime_type="text/srt",
        )
        of3 = OutputFile(
            output_file_id=build_entity_id("of"),
            workspace_id="internal",
            project_id="nura",
            render_job_id=rjob_id_2,
            file_type=OutputFileType.IMAGE,
            path="renders/r2/cover.png",
            mime_type="image/png",
        )

        self.output_file_repo.save_output_file(of1)
        self.output_file_repo.save_output_file(of2)
        self.output_file_repo.save_output_file(of3)

        files_for_rj1 = self.output_file_repo.list_output_files_by_render_job("nura", rjob_id_1)
        self.assertEqual(len(files_for_rj1), 2)
        for of in files_for_rj1:
            self.assertEqual(of.render_job_id, rjob_id_1)

        files_for_rj2 = self.output_file_repo.list_output_files_by_render_job("nura", rjob_id_2)
        self.assertEqual(len(files_for_rj2), 1)
        self.assertEqual(files_for_rj2[0].render_job_id, rjob_id_2)

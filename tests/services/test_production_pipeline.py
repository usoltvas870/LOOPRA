from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.domain import (
    ComicOverlay,
    ComicTailAnchor,
    ContentFormat,
    ContentItemStatus,
    OutputFile,
    OutputFileType,
    ProductionBrief,
    ProductionBriefStatus,
    ProductionOutput,
    ProductionScene,
    ProductionSubtitles,
    PublishingPlatform,
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
    _build_comic_video_brief,
)
from core.services.projects import FileSystemProjectRepository, ProjectService
from core.tools.qa import QAResult


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

    def test_execute_carousel_render_registers_qa_checked_pngs(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_test",
            content_format=ContentFormat.INSTAGRAM_CAROUSEL,
            slides=[
                {"slide_number": 1, "heading": "One"},
                {"slide_number": 2, "heading": "Two"},
            ],
            output=ProductionOutput(resolution_width=1080, resolution_height=1350),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        render_job = RenderJob(
            render_job_id=build_entity_id("rjob"), workspace_id="internal", project_id="nura",
            scenario_id=brief.scenario_id, content_format=brief.content_format,
            status=RenderJobStatus.RENDERING, input_snapshot={"brief_id": brief.production_brief_id},
        )
        self.render_job_repo.save_render_job(render_job)
        output_dir = Path("storage") / "nura" / "renders" / render_job.render_job_id / "carousel"
        slides = [output_dir / "slide_01.png", output_dir / "slide_02.png"]

        with patch("core.tools.carousel.renderer.render_carousel", return_value={"slides": slides}) as render, patch(
            "core.tools.qa.check_carousel_output", return_value=QAResult()
        ) as qa:
            updated = self.service.execute_render("nura", render_job.render_job_id)

        self.assertEqual(updated.status, RenderJobStatus.RENDERED)
        self.assertEqual(len(self.output_file_repo.list_output_files_by_render_job("nura", render_job.render_job_id)), 2)
        render.assert_called_once()
        qa.assert_called_once()

    def test_execute_comic_render_registers_ordered_qa_checked_pngs(self) -> None:
        from PIL import Image
        import os
        import shutil

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        source_dir = self.projects_root / "nura" / "assets"
        source_dir.mkdir()
        scenes = []
        for index, (speaker, color) in enumerate((("nura", "blue"), ("woman", "green"), ("shadow", "purple"))):
            source_name = f"scene_{index}.png"
            Image.new("RGB", (480, 800), color).save(source_dir / source_name, "PNG")
            scenes.append(ProductionScene(
                index=index,
                image_source=f"assets/{source_name}",
                duration_sec=1.0,
                comic_overlay=ComicOverlay(
                    speaker=speaker, text=f"Scene {index}", position="top_left",
                    tail_anchor=ComicTailAnchor(x=0.8, y=0.8),
                ),
            ))
        brief = ProductionBrief(
            workspace_id="internal", project_id="nura", production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_comic", content_format=ContentFormat.DIALOG_MINISERIES,
            subtitles=ProductionSubtitles(font_path=str(font)), scenes=scenes,
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        render_job = self.service.create_render_job("nura", brief.production_brief_id)
        render_job = self.service.validate_assets("nura", render_job.render_job_id)
        self.assertEqual(render_job.status, RenderJobStatus.RENDERING)
        output_dir = Path("storage") / "nura" / "renders" / render_job.render_job_id / "comic"

        try:
            with patch("core.tools.video.render_narrative_video") as video_render:
                updated = self.service.execute_render("nura", render_job.render_job_id)
            output_files = self.output_file_repo.list_output_files_by_render_job("nura", render_job.render_job_id)
            self.assertEqual(updated.status, RenderJobStatus.RENDERED)
            self.assertEqual([Path(item.path).name for item in output_files], ["scene_01.png", "scene_02.png", "scene_03.png"])
            self.assertTrue(all(Path(item.path).is_file() for item in output_files))
            video_render.assert_not_called()
        finally:
            shutil.rmtree(output_dir.parent, ignore_errors=True)

    def test_comic_render_failure_marks_job_failed_without_output_files(self) -> None:
        import os

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        brief = ProductionBrief(
            workspace_id="internal", project_id="nura", production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_comic_failure", content_format=ContentFormat.DIALOG_MINISERIES,
            subtitles=ProductionSubtitles(font_path=str(font)),
            scenes=[ProductionScene(
                index=0, image_source="assets/missing.png", duration_sec=1.0,
                comic_overlay=ComicOverlay(speaker="nura", text="Missing", position="top_left", tail_anchor=ComicTailAnchor(x=0.8, y=0.8)),
            )],
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        job = RenderJob(
            render_job_id=build_entity_id("rjob"), workspace_id="internal", project_id="nura",
            scenario_id=brief.scenario_id, content_format=brief.content_format,
            status=RenderJobStatus.RENDERING, input_snapshot={"brief_id": brief.production_brief_id},
        )
        self.render_job_repo.save_render_job(job)

        with self.assertRaises(Exception):
            self.service.execute_render("nura", job.render_job_id)
        failed = self.render_job_repo.load_render_job("nura", job.render_job_id)
        self.assertEqual(failed.status, RenderJobStatus.FAILED)
        self.assertEqual(self.output_file_repo.list_output_files_by_render_job("nura", job.render_job_id), [])

    def test_derived_comic_video_brief_preserves_original_contract(self) -> None:
        source = ProductionScene(
            index=0,
            image_source="assets/source.png",
            duration_sec=1.25,
            narration_text="Narration",
            comic_overlay=ComicOverlay(
                speaker="nura", text="Bubble", position="top_left", tail_anchor=ComicTailAnchor(x=0.8, y=0.8)
            ),
        )
        brief = ProductionBrief(
            workspace_id="internal", project_id="nura", production_brief_id="brief_comic_copy",
            scenario_id="scenario_comic_copy", content_format=ContentFormat.DIALOG_MINISERIES,
            subtitles=ProductionSubtitles(enabled=True, font_path="font.ttf"), scenes=[source],
            output=ProductionOutput(generate_comic_master_video=True, resolution_width=270, resolution_height=480, fps=24),
        )

        derived = _build_comic_video_brief(brief, [Path("storage/nura/renders/job/comic/scene_01.png")])

        self.assertEqual(derived.scenes[0].duration_sec, brief.scenes[0].duration_sec)
        self.assertEqual(derived.scenes[0].animation, brief.scenes[0].animation)
        self.assertEqual(derived.scenes[0].transition_type, brief.scenes[0].transition_type)
        self.assertEqual(derived.output, brief.output)
        self.assertEqual(derived.audio, brief.audio)
        self.assertFalse(derived.subtitles.enabled)
        self.assertTrue(brief.subtitles.enabled)
        self.assertEqual(brief.scenes[0].image_source, "assets/source.png")
        self.assertEqual(brief.scenes[0].comic_overlay.text, "Bubble")

    def test_comic_master_video_uses_existing_renderer_after_comic_qa(self) -> None:
        from PIL import Image
        import hashlib
        import os
        import shutil

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        source_dir = self.projects_root / "nura" / "assets"
        source_dir.mkdir()
        scenes = []
        for index, color in enumerate(("blue", "green", "purple")):
            source_name = f"master_{index}.png"
            Image.new("RGB", (270, 480), color).save(source_dir / source_name, "PNG")
            scenes.append(ProductionScene(
                index=index, image_source=f"assets/{source_name}", duration_sec=0.6,
                transition_duration=0.1,
                comic_overlay=ComicOverlay(
                    speaker=("nura", "woman", "shadow")[index], text=f"Scene {index}",
                    position="top_left", tail_anchor=ComicTailAnchor(x=0.8, y=0.8),
                ),
            ))
        brief = ProductionBrief(
            workspace_id="internal", project_id="nura", production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_comic_master", content_format=ContentFormat.DIALOG_MINISERIES,
            subtitles=ProductionSubtitles(font_path=str(font)), scenes=scenes,
            output=ProductionOutput(
                resolution_width=270, resolution_height=480, fps=24,
                generate_cover=False, generate_audio_only=False, generate_comic_master_video=True,
            ),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        job = self.service.create_render_job("nura", brief.production_brief_id)
        job = self.service.validate_assets("nura", job.render_job_id)
        self.assertEqual(job.status, RenderJobStatus.RENDERING)
        output_dir = Path("storage") / "nura" / "renders" / job.render_job_id
        source_hashes = [
            hashlib.sha256((source_dir / f"master_{index}.png").read_bytes()).hexdigest()
            for index in range(3)
        ]

        try:
            updated = self.service.execute_render("nura", job.render_job_id)
            output_files = self.output_file_repo.list_output_files_by_render_job("nura", job.render_job_id)
            self.assertEqual(updated.status, RenderJobStatus.RENDERED)
            self.assertEqual([Path(item.path).name for item in output_files], [
                "scene_01.png", "scene_02.png", "scene_03.png", "final_video.mp4",
            ])
            self.assertTrue((output_dir / "comic" / "video" / "final_video.mp4").is_file())
            self.assertFalse((output_dir / "comic" / "video" / "subtitles.srt").exists())
            self.assertFalse((output_dir / "comic" / "video" / "subtitles.ass").exists())
            self.assertEqual(source_hashes, [
                hashlib.sha256((source_dir / f"master_{index}.png").read_bytes()).hexdigest()
                for index in range(3)
            ])
            self.assertTrue(all(
                hashlib.sha256((output_dir / "comic" / f"scene_{index:02d}.png").read_bytes()).hexdigest()
                != source_hashes[index - 1]
                for index in range(1, 4)
            ))
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)

    def test_comic_output_repository_failure_removes_registered_files_and_artifacts(self) -> None:
        from PIL import Image
        import os
        import shutil

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        source_dir = self.projects_root / "nura" / "assets"
        source_dir.mkdir()
        scenes = []
        for index, color in enumerate(("blue", "green")):
            source_name = f"failure_{index}.png"
            Image.new("RGB", (270, 480), color).save(source_dir / source_name, "PNG")
            scenes.append(ProductionScene(
                index=index, image_source=f"assets/{source_name}", duration_sec=1.0,
                comic_overlay=ComicOverlay(
                    speaker="nura", text=f"Failure {index}", position="top_left",
                    tail_anchor=ComicTailAnchor(x=0.8, y=0.8),
                ),
            ))
        brief = ProductionBrief(
            workspace_id="internal", project_id="nura", production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_comic_repository_failure", content_format=ContentFormat.DIALOG_MINISERIES,
            target_platforms=[PublishingPlatform.TIKTOK],
            subtitles=ProductionSubtitles(font_path=str(font)), scenes=scenes,
            output=ProductionOutput(resolution_width=270, resolution_height=480),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        job = self.service.create_render_job("nura", brief.production_brief_id)
        job = self.service.validate_assets("nura", job.render_job_id)
        output_dir = Path("storage") / "nura" / "renders" / job.render_job_id
        original_save = self.output_file_repo.save_output_file
        calls = 0

        def fail_after_first(output_file: OutputFile) -> OutputFile:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated output repository failure")
            return original_save(output_file)

        def fake_video_render(_derived_brief, render_dir, _project_root):
            render_dir.mkdir(parents=True, exist_ok=True)
            final_video = render_dir / "final_video.mp4"
            final_video.write_bytes(b"video")
            return {"final_video": final_video}

        try:
            with patch.object(
                self.output_file_repo, "save_output_file", side_effect=fail_after_first
            ), patch(
                "core.tools.video.render_narrative_video", side_effect=fake_video_render
            ), patch(
                "core.tools.qa.check_video_output", return_value=QAResult()
            ):
                with self.assertRaises(OSError):
                    self.service.execute_render("nura", job.render_job_id)
            failed = self.render_job_repo.load_render_job("nura", job.render_job_id)
            self.assertEqual(failed.status, RenderJobStatus.FAILED)
            self.assertEqual(self.output_file_repo.list_output_files_by_render_job("nura", job.render_job_id), [])
            self.assertFalse((output_dir / "comic" / "scene_01.png").exists())
            self.assertFalse((output_dir / "comic" / "scene_02.png").exists())
            self.assertFalse((output_dir / "comic" / "platforms").exists())
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)

    def test_comic_platform_targets_render_once_each_in_canonical_order(self) -> None:
        from PIL import Image
        import os
        import shutil

        from core.tools.comic import render_comic_frames as actual_render_comic_frames

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        source_dir = self.projects_root / "nura" / "assets"
        source_dir.mkdir()
        scenes = []
        for index, color in enumerate(("blue", "green", "purple")):
            source_name = f"platform_{index}.png"
            Image.new("RGB", (270, 480), color).save(source_dir / source_name, "PNG")
            scenes.append(ProductionScene(
                index=index,
                image_source=f"assets/{source_name}",
                duration_sec=1.0,
                comic_overlay=ComicOverlay(
                    speaker=("nura", "woman", "shadow")[index],
                    text=f"Platform {index}",
                    position="top_left",
                    tail_anchor=ComicTailAnchor(x=0.8, y=0.8),
                ),
            ))
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_comic_platforms",
            content_format=ContentFormat.DIALOG_MINISERIES,
            target_platforms=[
                PublishingPlatform.VK,
                PublishingPlatform.TIKTOK,
                PublishingPlatform.VK,
                PublishingPlatform.YOUTUBE_SHORTS,
            ],
            subtitles=ProductionSubtitles(font_path=str(font)),
            scenes=scenes,
            output=ProductionOutput(
                resolution_width=270,
                resolution_height=480,
                fps=24,
                generate_cover=False,
                generate_audio_only=False,
                generate_comic_master_video=True,
            ),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        job = self.service.create_render_job("nura", brief.production_brief_id)
        job = self.service.validate_assets("nura", job.render_job_id)
        output_root = Path("storage") / "nura" / "renders" / job.render_job_id
        render_calls: list[tuple[Path, int]] = []

        def fake_video_render(derived_brief, output_dir, _project_root):
            output_dir.mkdir(parents=True, exist_ok=True)
            final_video = output_dir / "final_video.mp4"
            final_video.write_bytes(b"video")
            render_calls.append((output_dir, len(derived_brief.scenes)))
            return {"final_video": final_video}

        try:
            with patch(
                "core.tools.comic.render_comic_frames",
                wraps=actual_render_comic_frames,
            ) as frame_render, patch(
                "core.tools.video.render_narrative_video",
                side_effect=fake_video_render,
            ), patch(
                "core.tools.qa.check_video_output",
                return_value=QAResult(),
            ) as video_qa:
                updated = self.service.execute_render("nura", job.render_job_id)

            self.assertEqual(updated.status, RenderJobStatus.RENDERED)
            frame_render.assert_called_once()
            self.assertEqual(
                [(path.relative_to(output_root).as_posix(), count) for path, count in render_calls],
                [
                    ("comic/video", 3),
                    ("comic/platforms/tiktok", 6),
                    ("comic/platforms/youtube_shorts", 6),
                    ("comic/platforms/vk_clips", 6),
                ],
            )
            self.assertEqual(video_qa.call_count, 4)
            output_files = self.output_file_repo.list_output_files_by_render_job("nura", job.render_job_id)
            self.assertEqual(len(output_files), 7)
            self.assertEqual(sum(item.file_type == OutputFileType.IMAGE for item in output_files), 3)
            self.assertEqual(sum(item.file_type == OutputFileType.VIDEO for item in output_files), 4)
            self.assertTrue(all(item.size_bytes for item in output_files))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_comic_platform_middle_qa_failure_cleans_package_and_registers_nothing(self) -> None:
        from PIL import Image
        import os
        import shutil

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        source_dir = self.projects_root / "nura" / "assets"
        source_dir.mkdir()
        Image.new("RGB", (270, 480), "blue").save(source_dir / "failure.png", "PNG")
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_comic_platform_failure",
            content_format=ContentFormat.DIALOG_MINISERIES,
            target_platforms=[
                PublishingPlatform.TIKTOK,
                PublishingPlatform.YOUTUBE_SHORTS,
                PublishingPlatform.VK,
            ],
            subtitles=ProductionSubtitles(font_path=str(font)),
            scenes=[ProductionScene(
                index=0,
                image_source="assets/failure.png",
                duration_sec=1.0,
                comic_overlay=ComicOverlay(
                    speaker="nura",
                    text="Failure",
                    position="top_left",
                    tail_anchor=ComicTailAnchor(x=0.8, y=0.8),
                ),
            )],
            output=ProductionOutput(resolution_width=270, resolution_height=480),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        self.brief_repo.save_brief(brief)
        job = self.service.create_render_job("nura", brief.production_brief_id)
        job = self.service.validate_assets("nura", job.render_job_id)
        output_root = Path("storage") / "nura" / "renders" / job.render_job_id
        def fake_video_render(_derived_brief, output_dir, _project_root):
            output_dir.mkdir(parents=True, exist_ok=True)
            final_video = output_dir / "final_video.mp4"
            final_video.write_bytes(b"video")
            return {"final_video": final_video}

        try:
            with patch("core.tools.video.render_narrative_video", side_effect=fake_video_render), patch(
                "core.tools.qa.check_video_output",
                side_effect=[QAResult(), QAResult(passed=False, errors=["simulated QA failure"])],
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated QA failure"):
                    self.service.execute_render("nura", job.render_job_id)
            failed = self.render_job_repo.load_render_job("nura", job.render_job_id)
            self.assertEqual(failed.status, RenderJobStatus.FAILED)
            self.assertEqual(self.output_file_repo.list_output_files_by_render_job("nura", job.render_job_id), [])
            self.assertFalse((output_root / "comic" / "platforms").exists())
            self.assertFalse((output_root / "comic" / "scene_01.png").exists())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_comic_three_platform_package_with_real_pillow_ffmpeg_and_ffprobe(self) -> None:
        from PIL import Image
        import hashlib
        import os
        import shutil

        from core.tools.comic import render_comic_frames as actual_render_comic_frames
        from core.tools.qa import check_video_output

        font = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
        if not font.is_file() or shutil.which("ffprobe") is None:
            self.skipTest("A Cyrillic font and ffprobe are required for the real platform smoke")

        source_dir = self.projects_root / "nura" / "assets"
        source_dir.mkdir()
        texts = (
            'Нура: «Всё начинается с выбора».',
            "Женщина — а если путь уже рядом?",
            'Тень отвечает: «Смотри внимательнее».',
        )
        scenes = []
        source_hashes = []
        for index, (color, duration) in enumerate(zip(("#375A7F", "#7F5539", "#343A40"), (0.9, 1.0, 1.1), strict=True)):
            source_name = f"real_platform_{index}.png"
            source_path = source_dir / source_name
            Image.new("RGB", (270, 480), color).save(source_path, "PNG")
            source_hashes.append(hashlib.sha256(source_path.read_bytes()).hexdigest())
            scenes.append(ProductionScene(
                index=index,
                image_source=f"assets/{source_name}",
                duration_sec=duration,
                comic_overlay=ComicOverlay(
                    speaker=("nura", "woman", "shadow")[index],
                    text=texts[index],
                    position=("top_left", "middle_right", "bottom_left")[index],
                    tail_anchor=(
                        ComicTailAnchor(x=0.8, y=0.8),
                        ComicTailAnchor(x=0.2, y=0.2),
                        ComicTailAnchor(x=0.8, y=0.2),
                    )[index],
                ),
            ))
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id=build_entity_id("brief"),
            scenario_id="scenario_real_comic_platforms",
            content_format=ContentFormat.DIALOG_MINISERIES,
            target_platforms=[
                PublishingPlatform.VK,
                PublishingPlatform.YOUTUBE_SHORTS,
                PublishingPlatform.TIKTOK,
            ],
            subtitles=ProductionSubtitles(enabled=False, font_path=str(font)),
            scenes=scenes,
            output=ProductionOutput(
                resolution_width=270,
                resolution_height=480,
                fps=24,
                generate_srt=False,
                generate_cover=False,
                generate_audio_only=False,
                generate_comic_master_video=False,
            ),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        original_brief = brief.model_dump(mode="json")
        self.brief_repo.save_brief(brief)
        job = self.service.create_render_job("nura", brief.production_brief_id)
        job = self.service.validate_assets("nura", job.render_job_id)
        output_root = Path("storage") / "nura" / "renders" / job.render_job_id

        try:
            with patch("core.tools.comic.render_comic_frames", wraps=actual_render_comic_frames) as frame_render:
                updated = self.service.execute_render("nura", job.render_job_id)
            frame_render.assert_called_once()
            self.assertEqual(updated.status, RenderJobStatus.RENDERED)
            self.assertEqual(brief.model_dump(mode="json"), original_brief)
            self.assertEqual(
                source_hashes,
                [
                    hashlib.sha256((source_dir / f"real_platform_{index}.png").read_bytes()).hexdigest()
                    for index in range(3)
                ],
            )
            platform_paths = [
                output_root / "comic" / "platforms" / slug / "final_video.mp4"
                for slug in ("tiktok", "youtube_shorts", "vk_clips")
            ]
            qa_results = [
                check_video_output(
                    path,
                    expected_resolution=(270, 480),
                    expected_fps=24,
                    expected_video_codec="h264",
                    expected_pixel_format="yuv420p",
                )
                for path in platform_paths
            ]
            self.assertTrue(all(result.passed for result in qa_results))
            self.assertEqual(len({round(result.duration_sec, 2) for result in qa_results}), 3)
            self.assertEqual(len(list((output_root / "comic").glob("scene_*.png"))), 3)
            self.assertFalse(list((output_root / "comic").rglob("*.srt")))
            self.assertFalse(list((output_root / "comic").rglob("*.ass")))
            self.assertFalse([path for path in (output_root / "comic").rglob("*.mp4") if ".tmp" in path.name])
            output_files = self.output_file_repo.list_output_files_by_render_job("nura", job.render_job_id)
            self.assertEqual(len(output_files), 6)
            self.assertEqual(sum(item.file_type == OutputFileType.IMAGE for item in output_files), 3)
            self.assertEqual(sum(item.file_type == OutputFileType.VIDEO for item in output_files), 3)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

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

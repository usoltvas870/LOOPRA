from __future__ import annotations

from pathlib import Path

from core.domain import (
    ContentFormat,
    ContentItem,
    ContentItemStatus,
    DomainModule,
    OutputFile,
    OutputFileType,
    ProductionBrief,
    ProductionBriefStatus,
    RenderJob,
    RenderJobStatus,
)
from core.domain.models import utc_now, validated_model_copy
from core.projects.loader import resolve_project_dir
from core.tools.validators import validate_production_assets

from ._storage import FileSystemProjectModelRepository, build_entity_id
from .ideas import FileSystemScenarioRepository
from .projects import ProjectService


class ProductionPipelineValidationError(ValueError):
    """Raised when the production pipeline cannot proceed safely."""


class FileSystemProductionBriefRepository(FileSystemProjectModelRepository[ProductionBrief]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("production_briefs", ProductionBrief, projects_root)

    def list_briefs(self, project_id: str) -> list[ProductionBrief]:
        return self.list_models(project_id)

    def load_brief(self, project_id: str, brief_id: str) -> ProductionBrief:
        return self.load_model(project_id, brief_id, entity_name="production_brief_id")

    def save_brief(self, brief: ProductionBrief) -> ProductionBrief:
        return self.save_model(brief.project_id, brief.production_brief_id, brief)


class FileSystemRenderJobRepository(FileSystemProjectModelRepository[RenderJob]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("render_jobs", RenderJob, projects_root)

    def list_render_jobs(self, project_id: str) -> list[RenderJob]:
        return self.list_models(project_id)

    def load_render_job(self, project_id: str, render_job_id: str) -> RenderJob:
        return self.load_model(project_id, render_job_id, entity_name="render_job_id")

    def save_render_job(self, render_job: RenderJob) -> RenderJob:
        return self.save_model(render_job.project_id, render_job.render_job_id, render_job)


class FileSystemOutputFileRepository(FileSystemProjectModelRepository[OutputFile]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("output_files", OutputFile, projects_root)

    def list_output_files_by_render_job(self, project_id: str, render_job_id: str) -> list[OutputFile]:
        all_files = self.list_models(project_id)
        return [f for f in all_files if f.render_job_id == render_job_id]

    def load_output_file(self, project_id: str, output_file_id: str) -> OutputFile:
        return self.load_model(project_id, output_file_id, entity_name="output_file_id")

    def save_output_file(self, output_file: OutputFile) -> OutputFile:
        return self.save_model(output_file.project_id, output_file.output_file_id, output_file)


class ProductionPipelineService:
    def __init__(
        self,
        brief_repo: FileSystemProductionBriefRepository,
        render_job_repo: FileSystemRenderJobRepository,
        output_file_repo: FileSystemOutputFileRepository,
        content_repo: "FileSystemContentItemRepository",
        project_service: ProjectService,
    ) -> None:
        self._brief_repo = brief_repo
        self._render_job_repo = render_job_repo
        self._output_file_repo = output_file_repo
        self._content_repo = content_repo
        self._project_service = project_service

    def create_render_job(self, project_id: str, brief_id: str) -> RenderJob:
        project = self._project_service.get_project(project_id)
        brief = self._brief_repo.load_brief(project_id, brief_id)
        self._ensure_brief_ready(brief)

        render_job = RenderJob(
            render_job_id=build_entity_id("rjob"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            scenario_id=brief.scenario_id,
            content_format=brief.content_format,
            status=RenderJobStatus.QUEUED,
            input_snapshot={
                "brief_id": brief.production_brief_id,
                "content_format": brief.content_format.value,
                "production_variant": brief.production_variant,
            },
        )
        render_job = render_job.transition_to(RenderJobStatus.VALIDATING)
        return self._render_job_repo.save_render_job(render_job)

    def validate_assets(self, project_id: str, render_job_id: str) -> RenderJob:
        render_job = self._render_job_repo.load_render_job(project_id, render_job_id)
        if render_job.status != RenderJobStatus.VALIDATING:
            raise ProductionPipelineValidationError(
                f"RenderJob '{render_job_id}' is in status '{render_job.status.value}'; "
                f"expected 'validating'"
            )

        brief = self._brief_repo.load_brief(project_id, render_job.input_snapshot["brief_id"])
        project_dir = resolve_project_dir(project_id)
        report = validate_production_assets(brief, project_dir)

        snapshot = dict(render_job.input_snapshot)
        snapshot["asset_report"] = {
            "passed": report.passed,
            "errors": list(report.errors),
            "warnings": list(report.warnings),
            "missing_files": list(report.missing_files),
            "corrupt_files": list(report.corrupt_files),
            "wrong_resolution": list(report.wrong_resolution),
        }

        updated = validated_model_copy(render_job, input_snapshot=snapshot)
        next_status = RenderJobStatus.RENDERING if report.passed else RenderJobStatus.FAILED
        updated = updated.transition_to(next_status)
        return self._render_job_repo.save_render_job(updated)

    def execute_render(self, project_id: str, render_job_id: str) -> RenderJob:
        render_job = self._render_job_repo.load_render_job(project_id, render_job_id)
        if render_job.status != RenderJobStatus.RENDERING:
            raise ProductionPipelineValidationError(
                f"RenderJob '{render_job_id}' is in status '{render_job.status.value}'; "
                f"expected 'rendering'"
            )

        brief = self._brief_repo.load_brief(project_id, render_job.input_snapshot["brief_id"])
        project_root = resolve_project_dir(project_id)

        render_dir_norm = f"storage/{project_id}/renders/{render_job.render_job_id}"

        if brief.content_format in (ContentFormat.SHORT_VERTICAL_VIDEO, ContentFormat.AMBIENT_VERTICAL_VIDEO):
            from core.tools.video.renderer import render_narrative_video

            render_output_dir = Path(render_dir_norm)
            render_result = render_narrative_video(brief, render_output_dir, project_root)

            artifact_map = {
                "final_video": ("final_video", "final_video.mp4", "video/mp4", OutputFileType.VIDEO),
                "subtitles": ("subtitles", "subtitles.srt", "text/srt", OutputFileType.METADATA),
                "audio_only": ("audio_only", "audio_only.mp3", "audio/mpeg", OutputFileType.AUDIO),
                "cover": ("cover", "cover.png", "image/png", OutputFileType.IMAGE),
            }
            created_artifacts: list[tuple[str, str, str, OutputFileType]] = []
            for key, spec in artifact_map.items():
                if key in render_result and render_result[key].exists():
                    suffix, rel_path, mime, file_type = spec
                    output_file = OutputFile(
                        output_file_id=build_entity_id("of"),
                        workspace_id=render_job.workspace_id,
                        project_id=render_job.project_id,
                        render_job_id=render_job.render_job_id,
                        file_type=file_type,
                        path=str(render_result[key]),
                        mime_type=mime,
                    )
                    self._output_file_repo.save_output_file(output_file)
                    created_artifacts.append(spec)

            artifact_count = len(created_artifacts)
        elif brief.content_format == ContentFormat.INSTAGRAM_CAROUSEL:
            from core.tools.carousel.renderer import render_carousel
            from core.tools.qa import check_carousel_output

            render_output_dir = Path(render_dir_norm) / "carousel"
            try:
                render_result = render_carousel(brief, render_output_dir, project_root)
                slide_paths = render_result.get("slides", [])
                if not slide_paths:
                    raise RuntimeError("Carousel renderer produced no PNG files")
                qa_result = check_carousel_output(
                    render_output_dir,
                    expected_count=len(brief.slides),
                    expected_size=(brief.output.resolution_width, brief.output.resolution_height),
                )
                if not qa_result.passed:
                    raise RuntimeError("Carousel QA failed: " + "; ".join(qa_result.errors))
            except Exception:
                failed = render_job.transition_to(RenderJobStatus.FAILED)
                self._render_job_repo.save_render_job(failed)
                raise

            created_artifacts: list[tuple[str, str, str, OutputFileType]] = []
            for i, slide_path in enumerate(slide_paths):
                slide_num = i + 1
                output_file = OutputFile(
                    output_file_id=build_entity_id("of"),
                    workspace_id=render_job.workspace_id,
                    project_id=render_job.project_id,
                    render_job_id=render_job.render_job_id,
                    file_type=OutputFileType.IMAGE,
                    path=str(slide_path),
                    mime_type="image/png",
                )
                self._output_file_repo.save_output_file(output_file)
                created_artifacts.append((f"slide_{slide_num:02d}", str(slide_path), "image/png", OutputFileType.IMAGE))

            artifact_count = len(created_artifacts)
        else:
            render_dir_path = Path(render_dir_norm)
            render_dir_path.mkdir(parents=True, exist_ok=True)
            text_path = render_dir_path / "output.txt"
            text_path.write_text("", encoding="utf-8")
            output_file = OutputFile(
                output_file_id=build_entity_id("of"),
                workspace_id=render_job.workspace_id,
                project_id=render_job.project_id,
                render_job_id=render_job.render_job_id,
                file_type=OutputFileType.TEXT,
                path=str(text_path),
                mime_type="text/plain",
            )
            self._output_file_repo.save_output_file(output_file)
            artifact_count = 1

        snapshot = dict(render_job.input_snapshot)
        snapshot["artifact_count"] = artifact_count

        updated = validated_model_copy(render_job, input_snapshot=snapshot)
        updated = updated.transition_to(RenderJobStatus.RENDERED)
        return self._render_job_repo.save_render_job(updated)

    def create_content_from_render(self, project_id: str, render_job_id: str) -> ContentItem:
        render_job = self._render_job_repo.load_render_job(project_id, render_job_id)
        if render_job.status != RenderJobStatus.RENDERED:
            raise ProductionPipelineValidationError(
                f"RenderJob '{render_job_id}' is in status '{render_job.status.value}'; "
                f"expected 'rendered'"
            )

        brief = self._brief_repo.load_brief(project_id, render_job.input_snapshot["brief_id"])
        project = self._project_service.get_project(project_id)
        brand_profile_id = self._resolve_brand_profile_id(project_id, brief.scenario_id)

        output_files = self._output_file_repo.list_output_files_by_render_job(project_id, render_job_id)
        artifact_count = len(output_files)

        content_item = ContentItem(
            content_item_id=build_entity_id("content"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            scenario_id=render_job.scenario_id,
            brand_profile_id=brand_profile_id,
            render_job_id=render_job.render_job_id,
            title=self._derive_content_title(brief),
            body=self._derive_content_body(brief),
            content_format=brief.content_format,
            status=ContentItemStatus.DRAFT,
            technical_qa_passed=None,
            render_output_metadata={
                "render_job_id": render_job.render_job_id,
                "brief_id": brief.production_brief_id,
                "content_format": brief.content_format.value,
                "production_variant": brief.production_variant,
                "artifact_count": artifact_count,
                "target_platforms": [p.value for p in brief.target_platforms],
            },
        )

        content_item = content_item.transition_to(ContentItemStatus.IN_PRODUCTION)
        content_item = content_item.transition_to(ContentItemStatus.RENDERED)
        return self._content_repo.save_content_item(content_item)

    @staticmethod
    def _ensure_brief_ready(brief: ProductionBrief) -> None:
        if brief.status not in {
            ProductionBriefStatus.VALIDATED,
            ProductionBriefStatus.APPROVED,
            ProductionBriefStatus.IN_PROGRESS,
        }:
            raise ProductionPipelineValidationError(
                f"ProductionBrief '{brief.production_brief_id}' must be validated, approved, "
                f"or in_progress before creating a RenderJob. Current status: '{brief.status.value}'"
            )

    @staticmethod
    def _derive_content_title(brief: ProductionBrief) -> str:
        if brief.scenes:
            texts = [s.narration_text.strip() for s in brief.scenes if s.narration_text.strip()]
            if texts:
                return texts[0]
        if brief.slides:
            texts = [s.heading.strip() for s in brief.slides if s.heading.strip()]
            if texts:
                return texts[0]
        return f"Production: {brief.production_brief_id}"

    @staticmethod
    def _derive_content_body(brief: ProductionBrief) -> str:
        if brief.scenes:
            parts = [s.narration_text.strip() for s in brief.scenes if s.narration_text.strip()]
            return "\n\n---\n\n".join(parts)
        if brief.slides:
            parts = []
            for s in brief.slides:
                block_parts = [p for p in (s.heading.strip(), s.subheading.strip(), s.body.strip()) if p]
                if block_parts:
                    parts.append(" | ".join(block_parts))
            return "\n\n---\n\n".join(parts)
        return f"Production render for {brief.content_format.value}"

    @staticmethod
    def _resolve_brand_profile_id(project_id: str, scenario_id: str) -> str:
        try:
            repo = FileSystemScenarioRepository()
            scenario = repo.load_scenario(project_id, scenario_id)
            return scenario.brand_profile_id
        except Exception:
            return "default"


from .production import FileSystemContentItemRepository


def build_production_pipeline_service(projects_root: Path | None = None) -> ProductionPipelineService:
    from .projects import FileSystemProjectRepository

    project_repo = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repo)

    return ProductionPipelineService(
        brief_repo=FileSystemProductionBriefRepository(projects_root),
        render_job_repo=FileSystemRenderJobRepository(projects_root),
        output_file_repo=FileSystemOutputFileRepository(projects_root),
        content_repo=FileSystemContentItemRepository(projects_root),
        project_service=project_service,
    )

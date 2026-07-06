from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from core.domain import (
    BrandContentRules,
    BrandProfile,
    BrandProfileStatus,
    BrandToneOfVoice,
    Project,
    ProjectStatus,
    Workspace,
    WorkspaceStatus,
)
from core.projects.loader import PROJECTS_ROOT, ProjectConfig, load_project, validate_project_id


DEFAULT_WORKSPACE_ID = "internal"
DEFAULT_WORKSPACE_NAME = "Internal Workspace"
DEFAULT_WORKSPACE_SLUG = "internal"


class ProjectConfigValidationError(ValueError):
    """Raised when a project config cannot be mapped to canonical domain models."""


class FileSystemProjectRepository:
    def __init__(self, projects_root: Path | None = None) -> None:
        self._projects_root = projects_root or PROJECTS_ROOT

    @property
    def projects_root(self) -> Path:
        return self._projects_root

    def list_project_ids(self) -> list[str]:
        if not self._projects_root.exists():
            return []

        project_ids: list[str] = []
        for entry in sorted(self._projects_root.iterdir(), key=lambda item: item.name):
            if not entry.is_dir():
                continue
            if not (entry / "project.yaml").exists():
                continue
            try:
                project_ids.append(validate_project_id(entry.name))
            except ValueError:
                continue
        return project_ids

    def load_project_config(self, project_id: str) -> ProjectConfig:
        return load_project(project_id, projects_root=self._projects_root)


class WorkspaceService:
    def get_workspace(self) -> Workspace:
        return Workspace(
            workspace_id=DEFAULT_WORKSPACE_ID,
            name=DEFAULT_WORKSPACE_NAME,
            slug=DEFAULT_WORKSPACE_SLUG,
            status=WorkspaceStatus.ACTIVE,
        )


class ProjectService:
    def __init__(
        self,
        repository: FileSystemProjectRepository,
        workspace_service: WorkspaceService | None = None,
    ) -> None:
        self._repository = repository
        self._workspace_service = workspace_service or WorkspaceService()

    def list_projects(self) -> list[Project]:
        return [self.get_project(project_id) for project_id in self._repository.list_project_ids()]

    def get_project(self, project_id: str) -> Project:
        config = self._repository.load_project_config(project_id)
        workspace = self._workspace_service.get_workspace()
        self._validate_required_fields(
            {
                "project_id": config.id,
                "project_name": config.name,
                "project_slug": config.slug,
                "default_language": config.language,
                "status": config.status,
            }
        )
        return Project(
            project_id=config.id,
            workspace_id=config.workspace_id or workspace.workspace_id,
            name=config.name,
            slug=config.slug,
            default_language=config.language,
            status=self._parse_project_status(config.status),
        )

    @staticmethod
    def _parse_project_status(raw_status: str) -> ProjectStatus:
        try:
            return ProjectStatus(raw_status)
        except ValueError as exc:
            raise ProjectConfigValidationError(
                f"Invalid project status '{raw_status}'. Allowed: {[status.value for status in ProjectStatus]}"
            ) from exc

    @staticmethod
    def _validate_required_fields(fields: dict[str, str]) -> None:
        missing = [field_name for field_name, value in fields.items() if not str(value or "").strip()]
        if missing:
            missing_fields = ", ".join(missing)
            raise ProjectConfigValidationError(f"Project config is missing required fields: {missing_fields}")


class BrandProfileService:
    def __init__(
        self,
        repository: FileSystemProjectRepository,
        workspace_service: WorkspaceService | None = None,
    ) -> None:
        self._repository = repository
        self._workspace_service = workspace_service or WorkspaceService()
        self._project_service = ProjectService(repository, self._workspace_service)

    def get_brand_profile(self, project_id: str) -> BrandProfile:
        config = self._repository.load_project_config(project_id)
        project = self._project_service.get_project(project_id)
        workspace = self._workspace_service.get_workspace()
        self._validate_brand_fields(config)

        tone_payload = dict(config.brand.tone_of_voice)
        if config.brand.tone and not tone_payload.get("tone_summary"):
            tone_payload["tone_summary"] = config.brand.tone

        content_rules_payload = dict(config.brand.content_rules)

        return BrandProfile(
            brand_profile_id=f"brand_{project.project_id}",
            workspace_id=config.workspace_id or workspace.workspace_id,
            project_id=project.project_id,
            name=config.brand.name,
            positioning=config.brand.positioning,
            audience_summary=config.brand.audience_summary,
            language=config.brand.language or project.default_language,
            brand_values=list(config.brand.brand_values),
            tone_of_voice=BrandToneOfVoice.model_validate(tone_payload),
            content_rules=BrandContentRules.model_validate(content_rules_payload),
            status=self._resolve_brand_status(config),
        )

    @staticmethod
    def _resolve_brand_status(config: ProjectConfig) -> BrandProfileStatus:
        raw_status = config.brand.status or config.status
        if raw_status in {status.value for status in BrandProfileStatus}:
            return BrandProfileStatus(raw_status)
        if config.brand.positioning and config.brand.audience_summary:
            return BrandProfileStatus.ACTIVE
        return BrandProfileStatus.INCOMPLETE

    @staticmethod
    def _validate_brand_fields(config: ProjectConfig) -> None:
        missing = _find_missing_required_fields(
            (
                ("brand.name", config.brand.name),
                ("brand.positioning", config.brand.positioning),
                ("brand.audience_summary", config.brand.audience_summary),
            )
        )
        if missing:
            missing_fields = ", ".join(missing)
            raise ProjectConfigValidationError(
                f"Project config is missing required BrandProfile fields: {missing_fields}"
            )


def _find_missing_required_fields(fields: Iterable[tuple[str, str]]) -> list[str]:
    missing: list[str] = []
    for field_name, value in fields:
        if not str(value or "").strip():
            missing.append(field_name)
    return missing

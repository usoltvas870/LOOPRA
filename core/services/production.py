from __future__ import annotations

from pathlib import Path

from core.domain import ContentItem, ContentItemStatus, Scenario, ScenarioStatus
from core.domain.models import utc_now, validated_model_copy

from ._storage import FileSystemProjectModelRepository, build_entity_id
from .ideas import FileSystemScenarioRepository
from .projects import FileSystemProjectRepository, ProjectService


class ProductionLifecycleValidationError(ValueError):
    """Raised when the minimal production lifecycle cannot proceed safely."""


class FileSystemContentItemRepository(FileSystemProjectModelRepository[ContentItem]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("content_items", ContentItem, projects_root)

    def list_content_items(self, project_id: str) -> list[ContentItem]:
        return self.list_models(project_id)

    def load_content_item(self, project_id: str, content_item_id: str) -> ContentItem:
        return self.load_model(project_id, content_item_id, entity_name="content_item_id")

    def save_content_item(self, content_item: ContentItem) -> ContentItem:
        return self.save_model(content_item.project_id, content_item.content_item_id, content_item)


class ProductionLifecycleService:
    def __init__(
        self,
        content_repository: FileSystemContentItemRepository,
        scenario_repository: FileSystemScenarioRepository,
        project_service: ProjectService,
    ) -> None:
        self._content_repository = content_repository
        self._scenario_repository = scenario_repository
        self._project_service = project_service

    def list_content_items(self, project_id: str) -> list[ContentItem]:
        self._project_service.get_project(project_id)
        return self._content_repository.list_content_items(project_id)

    def get_content_item(self, project_id: str, content_item_id: str) -> ContentItem:
        self._project_service.get_project(project_id)
        return self._content_repository.load_content_item(project_id, content_item_id)

    def create_content_item(self, project_id: str, scenario_id: str) -> ContentItem:
        project = self._project_service.get_project(project_id)
        scenario = self._scenario_repository.load_scenario(project_id, scenario_id)
        self._ensure_scenario_is_export_safe(scenario)

        content_item = ContentItem(
            content_item_id=build_entity_id("content"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            scenario_id=scenario.scenario_id,
            brand_profile_id=scenario.brand_profile_id,
            title=scenario.title,
            body=self._build_content_body(scenario),
            content_format=scenario.content_format,
            status=ContentItemStatus.DRAFT,
            technical_qa_passed=None,
            render_output_metadata={
                "source_type": scenario.source_type,
                "source_id": scenario.source_id,
                "target_platforms": [platform.value for platform in scenario.target_platforms],
                "content_kind": "deterministic_text_derivation",
                "scenario_qa_warnings": list(scenario.qa_warnings),
            },
        )
        content_item = content_item.transition_to(ContentItemStatus.IN_PRODUCTION)
        content_item = content_item.transition_to(ContentItemStatus.RENDERED)
        return self._content_repository.save_content_item(content_item)

    def run_technical_qa(self, project_id: str, content_item_id: str) -> ContentItem:
        content_item = self.get_content_item(project_id, content_item_id)
        qa_errors = self._collect_technical_qa_errors(content_item)
        metadata = dict(content_item.render_output_metadata)
        metadata["technical_qa_errors"] = qa_errors
        metadata["technical_qa_checked_at"] = utc_now().isoformat()

        updated = validated_model_copy(
            content_item,
            technical_qa_passed=not qa_errors,
            render_output_metadata=metadata,
            updated_at=utc_now(),
        )
        next_status = ContentItemStatus.NEEDS_REVIEW if not qa_errors else ContentItemStatus.QA_FAILED
        updated = updated.transition_to(next_status)
        return self._content_repository.save_content_item(updated)

    def approve_content(self, project_id: str, content_item_id: str) -> ContentItem:
        content_item = self.get_content_item(project_id, content_item_id)
        approved = content_item.transition_to(ContentItemStatus.APPROVED)
        return self._content_repository.save_content_item(approved)

    @staticmethod
    def _ensure_scenario_is_export_safe(scenario: Scenario) -> None:
        if scenario.status != ScenarioStatus.APPROVED:
            raise ProductionLifecycleValidationError(
                f"Scenario '{scenario.scenario_id}' must be approved before creating a ContentItem"
            )

    @staticmethod
    def _build_content_body(scenario: Scenario) -> str:
        if scenario.draft_text.strip():
            return scenario.draft_text.strip()
        return "\n\n---\n\n".join(block.text.strip() for block in scenario.blocks if block.text.strip())

    @staticmethod
    def _collect_technical_qa_errors(content_item: ContentItem) -> list[str]:
        errors: list[str] = []
        if not content_item.title.strip():
            errors.append("ContentItem title is empty.")
        if not content_item.body.strip():
            errors.append("ContentItem body is empty.")
        if not content_item.brand_profile_id.strip():
            errors.append("ContentItem is missing brand_profile_id.")
        return errors


def build_production_lifecycle_service(projects_root: Path | None = None) -> ProductionLifecycleService:
    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    return ProductionLifecycleService(
        FileSystemContentItemRepository(projects_root),
        FileSystemScenarioRepository(projects_root),
        project_service,
    )

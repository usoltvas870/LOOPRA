from __future__ import annotations

import json
from pathlib import Path

from core.domain import (
    ContentItem,
    ContentItemStatus,
    ExportPackage,
    ExportPackageStatus,
    Publication,
    PublicationStatus,
    PublishingPlatform,
)
from core.domain.models import utc_now, validated_model_copy
from core.projects.loader import resolve_project_dir

from ._storage import FileSystemProjectModelRepository, build_entity_id
from .ideas import FileSystemScenarioRepository
from .production import FileSystemContentItemRepository
from .projects import FileSystemProjectRepository, ProjectService


class PublishingValidationError(ValueError):
    """Raised when export or manual publication preconditions are not met."""


class FileSystemExportPackageRepository(FileSystemProjectModelRepository[ExportPackage]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("export_packages", ExportPackage, projects_root)

    def list_export_packages(self, project_id: str) -> list[ExportPackage]:
        return self.list_models(project_id)

    def load_export_package(self, project_id: str, export_package_id: str) -> ExportPackage:
        return self.load_model(project_id, export_package_id, entity_name="export_package_id")

    def save_export_package(self, export_package: ExportPackage) -> ExportPackage:
        return self.save_model(export_package.project_id, export_package.export_package_id, export_package)


class FileSystemPublicationRepository(FileSystemProjectModelRepository[Publication]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("publications", Publication, projects_root)

    def list_publications(self, project_id: str) -> list[Publication]:
        return self.list_models(project_id)

    def load_publication(self, project_id: str, publication_id: str) -> Publication:
        return self.load_model(project_id, publication_id, entity_name="publication_id")

    def save_publication(self, publication: Publication) -> Publication:
        return self.save_model(publication.project_id, publication.publication_id, publication)


class PublishingService:
    def __init__(
        self,
        export_repository: FileSystemExportPackageRepository,
        publication_repository: FileSystemPublicationRepository,
        content_repository: FileSystemContentItemRepository,
        scenario_repository: FileSystemScenarioRepository,
        project_service: ProjectService,
        projects_root: Path | None = None,
    ) -> None:
        self._export_repository = export_repository
        self._publication_repository = publication_repository
        self._content_repository = content_repository
        self._scenario_repository = scenario_repository
        self._project_service = project_service
        self._projects_root = projects_root

    def list_export_packages(self, project_id: str) -> list[ExportPackage]:
        self._project_service.get_project(project_id)
        return self._export_repository.list_export_packages(project_id)

    def get_export_package(self, project_id: str, export_package_id: str) -> ExportPackage:
        self._project_service.get_project(project_id)
        return self._export_repository.load_export_package(project_id, export_package_id)

    def list_publications(self, project_id: str) -> list[Publication]:
        self._project_service.get_project(project_id)
        return self._publication_repository.list_publications(project_id)

    def get_publication(self, project_id: str, publication_id: str) -> Publication:
        self._project_service.get_project(project_id)
        return self._publication_repository.load_publication(project_id, publication_id)

    def create_export_package(
        self,
        project_id: str,
        content_item_id: str,
        target_platform: PublishingPlatform | str,
    ) -> ExportPackage:
        project = self._project_service.get_project(project_id)
        content_item = self._content_repository.load_content_item(project_id, content_item_id)
        if content_item.status != ContentItemStatus.APPROVED:
            raise PublishingValidationError(
                f"ContentItem '{content_item.content_item_id}' must be approved before export preparation"
            )

        scenario = self._scenario_repository.load_scenario(project_id, content_item.scenario_id)
        platform = target_platform if isinstance(target_platform, PublishingPlatform) else PublishingPlatform(target_platform)
        caption_text = scenario.caption_drafts.get(platform.value, content_item.body).strip()

        export_package = ExportPackage(
            export_package_id=build_entity_id("export"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            content_item_id=content_item.content_item_id,
            content_format=content_item.content_format,
            target_platform=platform,
            package_files=[],
            caption_variants={platform.value: caption_text},
            publication_notes="Manual publication only. External platform APIs are out of scope for this MVP loop.",
            status=ExportPackageStatus.DRAFT,
        )
        return self._export_repository.save_export_package(export_package)

    def prepare_export(self, project_id: str, export_package_id: str) -> ExportPackage:
        export_package = self.get_export_package(project_id, export_package_id)
        if export_package.status != ExportPackageStatus.DRAFT:
            raise PublishingValidationError(
                f"ExportPackage '{export_package.export_package_id}' must be in draft status before preparation"
            )

        content_item = self._content_repository.load_content_item(project_id, export_package.content_item_id)
        if content_item.status not in {ContentItemStatus.APPROVED, ContentItemStatus.EXPORTED}:
            raise PublishingValidationError(
                f"ContentItem '{content_item.content_item_id}' must be approved or exported before export preparation"
            )

        scenario = self._scenario_repository.load_scenario(project_id, content_item.scenario_id)
        export_dir = resolve_project_dir(project_id, self._projects_root) / "exports" / export_package.export_package_id
        export_dir.mkdir(parents=True, exist_ok=True)

        title_path = export_dir / "title.txt"
        title_path.write_text(content_item.title or "", encoding="utf-8")

        body_path = export_dir / "body.txt"
        body_path.write_text(content_item.body or "", encoding="utf-8")

        caption_text = self._resolve_caption_text(export_package, scenario, content_item)
        caption_path = export_dir / f"caption_{export_package.target_platform.value}.txt"
        caption_path.write_text(caption_text, encoding="utf-8")

        checklist_path = export_dir / "manual_publication_checklist.txt"
        checklist_path.write_text(self._build_manual_publication_checklist(export_package.target_platform), encoding="utf-8")

        metadata_path = export_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(
                self._build_export_metadata(export_package, content_item, scenario),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        export_package = validated_model_copy(
            export_package,
            package_files=[
                str(title_path),
                str(body_path),
                str(caption_path),
                str(checklist_path),
                str(metadata_path),
            ],
            updated_at=utc_now(),
        )
        export_package = export_package.transition_to(ExportPackageStatus.READY)
        self._export_repository.save_export_package(export_package)

        if content_item.status == ContentItemStatus.APPROVED:
            content_item = content_item.transition_to(ContentItemStatus.EXPORTED)
            self._content_repository.save_content_item(content_item)

        return export_package

    def _resolve_caption_text(self, export_package: ExportPackage, scenario, content_item: ContentItem) -> str:
        platform_key = export_package.target_platform.value
        if platform_key in scenario.caption_drafts:
            return scenario.caption_drafts[platform_key].strip()
        if platform_key in export_package.caption_variants:
            return export_package.caption_variants[platform_key].strip()
        return content_item.body.strip()

    def _build_manual_publication_checklist(self, target_platform: PublishingPlatform) -> str:
        return "\n".join(
            [
                "Manual publication checklist",
                "",
                "This package is prepared for manual publication only.",
                f"Target platform: {target_platform.value}",
                "",
                "[ ] Review title.txt",
                "[ ] Review body.txt",
                f"[ ] Review caption_{target_platform.value}.txt",
                "[ ] Confirm metadata.json matches the intended publication context",
                "[ ] Publish manually in the target channel",
                "[ ] Record the final publication URL in Content Plant",
            ]
        )

    def _build_export_metadata(self, export_package: ExportPackage, content_item: ContentItem, scenario) -> dict[str, object]:
        return {
            "project_id": content_item.project_id,
            "content_item_id": content_item.content_item_id,
            "scenario_id": content_item.scenario_id,
            "content_format": content_item.content_format.value,
            "target_platform": export_package.target_platform.value,
            "manual_publication_only": True,
            "prepared_at": utc_now().isoformat(),
            "brand_profile_id": content_item.brand_profile_id or scenario.brand_profile_id,
            "funnel_stage": scenario.funnel_stage,
            "title": content_item.title,
            "content_item_status": content_item.status.value,
            "target_platforms": [platform.value for platform in scenario.target_platforms],
            "scenario_qa_warnings": list(scenario.qa_warnings),
        }

    def create_publication(self, project_id: str, content_item_id: str, export_package_id: str) -> Publication:
        project = self._project_service.get_project(project_id)
        content_item = self._content_repository.load_content_item(project_id, content_item_id)
        export_package = self._export_repository.load_export_package(project_id, export_package_id)

        if export_package.content_item_id != content_item.content_item_id:
            raise PublishingValidationError("ExportPackage and ContentItem do not belong to the same content unit")
        if export_package.status != ExportPackageStatus.READY:
            raise PublishingValidationError(
                f"ExportPackage '{export_package.export_package_id}' must be ready before publication creation"
            )
        if content_item.status != ContentItemStatus.EXPORTED:
            raise PublishingValidationError(
                f"ContentItem '{content_item.content_item_id}' must be exported before publication creation"
            )

        publication = Publication(
            publication_id=build_entity_id("publication"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            content_item_id=content_item.content_item_id,
            export_package_id=export_package.export_package_id,
            platform=export_package.target_platform,
            status=PublicationStatus.PLANNED,
            notes="Created for manual publication flow.",
        )
        return self._publication_repository.save_publication(publication)

    def publish_content(self, project_id: str, publication_id: str, published_url: str) -> Publication:
        publication = self.get_publication(project_id, publication_id)
        if not published_url.strip():
            raise PublishingValidationError("published_url must not be empty")
        published = publication.transition_to(
            PublicationStatus.PUBLISHED,
            published_url=published_url.strip(),
        )
        return self._publication_repository.save_publication(published)

    def fail_publication(self, project_id: str, publication_id: str, error: str) -> Publication:
        publication = self.get_publication(project_id, publication_id)
        publication = validated_model_copy(
            publication,
            notes=error.strip() or publication.notes,
            updated_at=utc_now(),
        )
        failed = publication.transition_to(PublicationStatus.FAILED)
        return self._publication_repository.save_publication(failed)


def build_publishing_service(projects_root: Path | None = None) -> PublishingService:
    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    return PublishingService(
        FileSystemExportPackageRepository(projects_root),
        FileSystemPublicationRepository(projects_root),
        FileSystemContentItemRepository(projects_root),
        FileSystemScenarioRepository(projects_root),
        project_service,
        projects_root,
    )

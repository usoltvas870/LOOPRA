from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from core.domain import ContentPerformanceMetrics, MetricSnapshot, MetricSnapshotStatus, PublicationStatus
from core.domain.models import utc_now, validated_model_copy

from ._storage import FileSystemProjectModelRepository, build_entity_id
from .production import FileSystemContentItemRepository
from .projects import FileSystemProjectRepository, ProjectService
from .publishing import FileSystemPublicationRepository


class AnalyticsValidationError(ValueError):
    """Raised when metric collection inputs or state are invalid."""


class FileSystemMetricSnapshotRepository(FileSystemProjectModelRepository[MetricSnapshot]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("metric_snapshots", MetricSnapshot, projects_root)

    def list_metric_snapshots(self, project_id: str) -> list[MetricSnapshot]:
        return self.list_models(project_id)

    def load_metric_snapshot(self, project_id: str, metric_snapshot_id: str) -> MetricSnapshot:
        return self.load_model(project_id, metric_snapshot_id, entity_name="metric_snapshot_id")

    def save_metric_snapshot(self, metric_snapshot: MetricSnapshot) -> MetricSnapshot:
        return self.save_model(metric_snapshot.project_id, metric_snapshot.metric_snapshot_id, metric_snapshot)


class AnalyticsService:
    def __init__(
        self,
        metric_repository: FileSystemMetricSnapshotRepository,
        publication_repository: FileSystemPublicationRepository,
        content_repository: FileSystemContentItemRepository,
        project_service: ProjectService,
    ) -> None:
        self._metric_repository = metric_repository
        self._publication_repository = publication_repository
        self._content_repository = content_repository
        self._project_service = project_service

    def list_metric_snapshots(self, project_id: str) -> list[MetricSnapshot]:
        self._project_service.get_project(project_id)
        return self._metric_repository.list_metric_snapshots(project_id)

    def get_metric_snapshot(self, project_id: str, metric_snapshot_id: str) -> MetricSnapshot:
        self._project_service.get_project(project_id)
        return self._metric_repository.load_metric_snapshot(project_id, metric_snapshot_id)

    def create_metric_snapshot(self, project_id: str, publication_id: str, content_item_id: str) -> MetricSnapshot:
        project = self._project_service.get_project(project_id)
        publication = self._publication_repository.load_publication(project_id, publication_id)
        content_item = self._content_repository.load_content_item(project_id, content_item_id)

        if publication.status != PublicationStatus.PUBLISHED:
            raise AnalyticsValidationError(
                f"Publication '{publication.publication_id}' must be published before metric collection"
            )
        if publication.content_item_id != content_item.content_item_id:
            raise AnalyticsValidationError("Publication and ContentItem do not belong to the same content unit")

        snapshot = MetricSnapshot(
            metric_snapshot_id=build_entity_id("metric"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            publication_id=publication.publication_id,
            content_item_id=content_item.content_item_id,
            platform=publication.platform,
            status=MetricSnapshotStatus.DRAFT,
        )
        return self._metric_repository.save_metric_snapshot(snapshot)

    def record_metrics(self, project_id: str, metric_snapshot_id: str, metrics: dict[str, int]) -> MetricSnapshot:
        snapshot = self.get_metric_snapshot(project_id, metric_snapshot_id)
        if snapshot.status != MetricSnapshotStatus.DRAFT:
            raise AnalyticsValidationError(
                f"MetricSnapshot '{snapshot.metric_snapshot_id}' must be draft before metrics are recorded"
            )

        merged_metrics = snapshot.content_metrics.model_dump(mode="python")
        merged_metrics.update(metrics)
        try:
            content_metrics = ContentPerformanceMetrics.model_validate(merged_metrics)
        except ValidationError as exc:
            raise AnalyticsValidationError(str(exc)) from exc

        updated = validated_model_copy(
            snapshot,
            content_metrics=content_metrics,
            captured_at=utc_now(),
            updated_at=utc_now(),
        )
        recorded = updated.transition_to(MetricSnapshotStatus.RECORDED)
        return self._metric_repository.save_metric_snapshot(recorded)

    @staticmethod
    def get_insights(project_id: str) -> list[dict[str, str]]:
        _ = project_id
        return []

    @staticmethod
    def generate_new_ideas_from_metrics(project_id: str) -> list[dict[str, str]]:
        _ = project_id
        return []


def build_analytics_service(projects_root: Path | None = None) -> AnalyticsService:
    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    return AnalyticsService(
        FileSystemMetricSnapshotRepository(projects_root),
        FileSystemPublicationRepository(projects_root),
        FileSystemContentItemRepository(projects_root),
        project_service,
    )

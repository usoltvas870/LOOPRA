from __future__ import annotations

from collections import Counter
from pathlib import Path

from core.domain import IdeaStatus, PublishingPlatform

from .analytics import AnalyticsService, build_analytics_service
from .ideas import (
    FileSystemIdeaRepository,
    FileSystemScenarioRepository,
    IdeaService,
    ScenarioService,
)
from .production import ProductionLifecycleService, build_production_lifecycle_service
from .projects import BrandProfileService, FileSystemProjectRepository, ProjectService
from .publishing import PublishingService, build_publishing_service


class LoopOrchestrator:
    def __init__(
        self,
        idea_service: IdeaService,
        scenario_service: ScenarioService,
        production_service: ProductionLifecycleService,
        publishing_service: PublishingService,
        analytics_service: AnalyticsService,
    ) -> None:
        self._idea_service = idea_service
        self._scenario_service = scenario_service
        self._production_service = production_service
        self._publishing_service = publishing_service
        self._analytics_service = analytics_service

    def run_minimal_loop(
        self,
        project_id: str,
        idea_id: str,
        target_platform: PublishingPlatform | str | None = None,
    ) -> dict[str, str]:
        idea = self._idea_service.get_idea(project_id, idea_id)
        if idea.status == IdeaStatus.RAW:
            idea = self._idea_service.approve_idea(project_id, idea_id)

        scenario = self._scenario_service.create_from_idea(project_id, idea.idea_id)
        scenario = self._scenario_service.approve_scenario(project_id, scenario.scenario_id)

        content_item = self._production_service.create_content_item(project_id, scenario.scenario_id)
        content_item = self._production_service.run_technical_qa(project_id, content_item.content_item_id)
        content_item = self._production_service.approve_content(project_id, content_item.content_item_id)

        resolved_platform = self._resolve_target_platform(scenario.target_platforms, target_platform)
        export_package = self._publishing_service.create_export_package(
            project_id,
            content_item.content_item_id,
            resolved_platform,
        )
        export_package = self._publishing_service.prepare_export(project_id, export_package.export_package_id)

        publication = self._publishing_service.create_publication(
            project_id,
            content_item.content_item_id,
            export_package.export_package_id,
        )
        publication = self._publishing_service.publish_content(
            project_id,
            publication.publication_id,
            self._build_published_url(project_id, publication.publication_id, resolved_platform),
        )

        metric_snapshot = self._analytics_service.create_metric_snapshot(
            project_id,
            publication.publication_id,
            content_item.content_item_id,
        )

        return {
            "project_id": project_id,
            "idea_id": idea.idea_id,
            "scenario_id": scenario.scenario_id,
            "content_item_id": content_item.content_item_id,
            "export_package_id": export_package.export_package_id,
            "publication_id": publication.publication_id,
            "metric_snapshot_id": metric_snapshot.metric_snapshot_id,
            "status": "completed",
        }

    def get_loop_status(self, project_id: str) -> dict[str, object]:
        return {
            "project_id": project_id,
            "ideas": self._status_counts(idea.status.value for idea in self._idea_service.list_ideas(project_id)),
            "scenarios": self._status_counts(
                scenario.status.value for scenario in self._scenario_service.list_scenarios(project_id)
            ),
            "content_items": self._status_counts(
                item.status.value for item in self._production_service.list_content_items(project_id)
            ),
            "export_packages": self._status_counts(
                package.status.value for package in self._publishing_service.list_export_packages(project_id)
            ),
            "publications": self._status_counts(
                publication.status.value for publication in self._publishing_service.list_publications(project_id)
            ),
            "metric_snapshots": self._status_counts(
                snapshot.status.value for snapshot in self._analytics_service.list_metric_snapshots(project_id)
            ),
        }

    @staticmethod
    def _resolve_target_platform(
        scenario_platforms: list[PublishingPlatform],
        target_platform: PublishingPlatform | str | None,
    ) -> PublishingPlatform:
        if isinstance(target_platform, PublishingPlatform):
            return target_platform
        if target_platform is None or target_platform == "generic":
            if scenario_platforms:
                return scenario_platforms[0]
            raise ValueError(
                "Target platform is not defined. Pass target_platform explicitly or provide "
                "at least one platform in Scenario.target_platforms."
            )
        return PublishingPlatform(target_platform)

    @staticmethod
    def _build_published_url(project_id: str, publication_id: str, platform: PublishingPlatform) -> str:
        return f"https://example.invalid/{project_id}/{platform.value}/{publication_id}"

    @staticmethod
    def _status_counts(statuses: list[str]) -> dict[str, int]:
        return dict(Counter(statuses))


def build_loop_orchestrator(projects_root: Path | None = None) -> LoopOrchestrator:
    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    brand_profile_service = BrandProfileService(project_repository)
    idea_repository = FileSystemIdeaRepository(projects_root)
    scenario_repository = FileSystemScenarioRepository(projects_root)
    idea_service = IdeaService(idea_repository, project_service)
    scenario_service = ScenarioService(
        scenario_repository,
        project_repository,
        project_service,
        brand_profile_service,
        idea_service,
        idea_repository,
    )
    return LoopOrchestrator(
        idea_service,
        scenario_service,
        build_production_lifecycle_service(projects_root),
        build_publishing_service(projects_root),
        build_analytics_service(projects_root),
    )

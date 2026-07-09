from __future__ import annotations

import os
import sys
from pathlib import Path
from shutil import copyfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.services import (
    AnalyticsService,
    BrandProfileService,
    FileSystemContentItemRepository,
    FileSystemExportPackageRepository,
    FileSystemIdeaRepository,
    FileSystemMetricSnapshotRepository,
    FileSystemProjectRepository,
    FileSystemPublicationRepository,
    FileSystemScenarioRepository,
    IdeaService,
    LoopOrchestrator,
    ProductionLifecycleService,
    ProjectService,
    PublishingService,
    ScenarioService,
)


DEFAULT_PROJECT_ID = "example"
DEFAULT_RUNTIME_PROJECTS_ROOT = REPO_ROOT / "storage" / "smoke_projects"

USAGE = """\
Run the smallest LOOPRA Foundation MVP lifecycle smoke loop.

Usage:
  python scripts/smoke_loop.py [--help | -h]

Environment variables:
  LOOPRA_SMOKE_PROJECT_ID         Project ID to use (default: example)
  LOOPRA_SMOKE_PROJECTS_ROOT      Runtime storage root (default: storage/smoke_projects)
  CONTENT_PLANT_SMOKE_PROJECT_ID  Legacy fallback for LOOPRA_SMOKE_PROJECT_ID
  CONTENT_PLANT_SMOKE_PROJECTS_ROOT  Legacy fallback for LOOPRA_SMOKE_PROJECTS_ROOT

Example:
  python scripts/smoke_loop.py"""


def _resolve_project_id() -> str:
    project_id = (
        os.environ.get("LOOPRA_SMOKE_PROJECT_ID")
        or os.environ.get("CONTENT_PLANT_SMOKE_PROJECT_ID")
        or DEFAULT_PROJECT_ID
    ).strip()
    return project_id or DEFAULT_PROJECT_ID


def _resolve_runtime_projects_root() -> Path:
    override = (
        os.environ.get("LOOPRA_SMOKE_PROJECTS_ROOT")
        or os.environ.get("CONTENT_PLANT_SMOKE_PROJECTS_ROOT")
        or ""
    ).strip()
    if not override:
        return DEFAULT_RUNTIME_PROJECTS_ROOT
    return Path(override).expanduser().resolve()


def _ensure_runtime_project(project_id: str, runtime_projects_root: Path) -> Path:
    source_config_path = REPO_ROOT / "projects" / project_id / "project.yaml"
    if not source_config_path.exists():
        raise FileNotFoundError(
            f"Generic smoke project config not found for project_id '{project_id}': {source_config_path}"
        )

    runtime_project_dir = runtime_projects_root / project_id
    runtime_project_dir.mkdir(parents=True, exist_ok=True)
    copyfile(source_config_path, runtime_project_dir / "project.yaml")
    return runtime_project_dir


def _build_loop_context(projects_root: Path) -> tuple[
    LoopOrchestrator,
    IdeaService,
    FileSystemIdeaRepository,
    FileSystemScenarioRepository,
    FileSystemContentItemRepository,
    FileSystemExportPackageRepository,
    FileSystemPublicationRepository,
    FileSystemMetricSnapshotRepository,
]:
    project_repository = FileSystemProjectRepository(projects_root)
    idea_repository = FileSystemIdeaRepository(projects_root)
    scenario_repository = FileSystemScenarioRepository(projects_root)
    content_repository = FileSystemContentItemRepository(projects_root)
    export_repository = FileSystemExportPackageRepository(projects_root)
    publication_repository = FileSystemPublicationRepository(projects_root)
    metric_repository = FileSystemMetricSnapshotRepository(projects_root)

    project_service = ProjectService(project_repository)
    brand_profile_service = BrandProfileService(project_repository)
    idea_service = IdeaService(idea_repository, project_service)
    scenario_service = ScenarioService(
        scenario_repository,
        project_repository,
        project_service,
        brand_profile_service,
        idea_service,
        idea_repository,
    )
    production_service = ProductionLifecycleService(
        content_repository,
        scenario_repository,
        project_service,
    )
    publishing_service = PublishingService(
        export_repository,
        publication_repository,
        content_repository,
        scenario_repository,
        project_service,
        projects_root,
    )
    analytics_service = AnalyticsService(
        metric_repository,
        publication_repository,
        content_repository,
        project_service,
    )
    loop_orchestrator = LoopOrchestrator(
        idea_service,
        scenario_service,
        production_service,
        publishing_service,
        analytics_service,
    )
    return (
        loop_orchestrator,
        idea_service,
        idea_repository,
        scenario_repository,
        content_repository,
        export_repository,
        publication_repository,
        metric_repository,
    )


def _build_smoke_summary(
    *,
    project_id: str,
    projects_root: Path,
    result: dict[str, str],
    idea_repository: FileSystemIdeaRepository,
    scenario_repository: FileSystemScenarioRepository,
    content_repository: FileSystemContentItemRepository,
    export_repository: FileSystemExportPackageRepository,
    publication_repository: FileSystemPublicationRepository,
    metric_repository: FileSystemMetricSnapshotRepository,
) -> list[str]:
    idea = idea_repository.load_idea(project_id, result["idea_id"])
    scenario = scenario_repository.load_scenario(project_id, result["scenario_id"])
    content_item = content_repository.load_content_item(project_id, result["content_item_id"])
    export_package = export_repository.load_export_package(project_id, result["export_package_id"])
    publication = publication_repository.load_publication(project_id, result["publication_id"])
    metric_snapshot = metric_repository.load_metric_snapshot(project_id, result["metric_snapshot_id"])

    export_dir = projects_root / project_id / "exports" / export_package.export_package_id
    generated_export_files = sorted(path.name for path in export_dir.iterdir() if path.is_file())

    return [
        f"project_id={project_id}",
        f"idea_id={idea.idea_id}",
        f"scenario_id={scenario.scenario_id}",
        f"content_item_id={content_item.content_item_id}",
        f"export_package_id={export_package.export_package_id}",
        f"publication_id={publication.publication_id}",
        f"metric_snapshot_id={metric_snapshot.metric_snapshot_id}",
        f"export_directory={export_dir}",
        f"generated_export_files={','.join(generated_export_files)}",
        f"idea_status={idea.status.value}",
        f"scenario_status={scenario.status.value}",
        f"content_item_status={content_item.status.value}",
        f"export_package_status={export_package.status.value}",
        f"publication_status={publication.status.value}",
        f"metric_snapshot_status={metric_snapshot.status.value}",
    ]


def main() -> int:
    if set(sys.argv[1:]) & {"--help", "-h"}:
        print(USAGE)
        return 0

    project_id = _resolve_project_id()
    projects_root = _resolve_runtime_projects_root()
    _ensure_runtime_project(project_id, projects_root)

    (
        loop_orchestrator,
        idea_service,
        idea_repository,
        scenario_repository,
        content_repository,
        export_repository,
        publication_repository,
        metric_repository,
    ) = _build_loop_context(projects_root)

    idea = idea_service.create_idea(
        project_id,
        title="Foundation smoke loop",
        description="Run the smallest project-agnostic LOOPRA loop from idea to draft metrics.",
        funnel_stage="trust",
    )
    result = loop_orchestrator.run_minimal_loop(project_id, idea.idea_id)

    for line in _build_smoke_summary(
        project_id=project_id,
        projects_root=projects_root,
        result=result,
        idea_repository=idea_repository,
        scenario_repository=scenario_repository,
        content_repository=content_repository,
        export_repository=export_repository,
        publication_repository=publication_repository,
        metric_repository=metric_repository,
    ):
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

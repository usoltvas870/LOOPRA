from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.domain import (
    ContentFormat,
    ContentOpportunityStatus,
    IdeaStatus,
    PublishingPlatform,
    RenderJobStatus,
    ScenarioStatus,
    ScenarioTextBlock,
)
from core.services import (
    BrandProfileService,
    FileSystemIdeaRepository,
    FileSystemOutputFileRepository,
    FileSystemProjectRepository,
    FileSystemScenarioRepository,
    IdeaService,
    ProjectService,
    ScenarioService,
    ScenarioToCarouselBriefValidationError,
    build_content_intelligence_service,
    build_production_pipeline_service,
    build_scenario_to_carousel_brief_service,
)
from core.services.production_pipeline import (
    FileSystemProductionBriefRepository,
    FileSystemRenderJobRepository,
)
from core.tools.qa import check_carousel_output


PROJECT_ID = "intelligence_carousel_acceptance"
WORKSPACE_ID = "acceptance"


def _write_project_config(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "workspace_id": WORKSPACE_ID,
        "project_id": PROJECT_ID,
        "project_name": "Intelligence carousel acceptance",
        "project_slug": PROJECT_ID,
        "default_language": "ru",
        "status": "active",
        "primary_url": "https://acceptance.example",
        "target_platforms": ["instagram"],
        "brand": {
            "brand_name": "Acceptance Brand",
            "positioning": "Clear, practical content operations",
            "audience_summary": "Teams building repeatable marketing workflows",
            "language": "ru",
            "tone_of_voice": {"tone_summary": "Clear and useful."},
            "colors": {
                "primary": "#1D4ED8",
                "accent": "#F59E0B",
                "background_dark": "#111827",
                "text_light": "#F9FAFB",
                "text_muted": "#D1D5DB",
            },
            "fonts": {"heading": "Arial", "body": "Arial"},
        },
    }
    (project_dir / "project.yaml").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _build_scenario_service(projects_root: Path) -> ScenarioService:
    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    idea_repository = FileSystemIdeaRepository(projects_root)
    idea_service = IdeaService(idea_repository, project_service)
    return ScenarioService(
        FileSystemScenarioRepository(projects_root),
        project_repository,
        project_service,
        BrandProfileService(project_repository),
        idea_service,
        idea_repository,
    )


def _carousel_blocks() -> list[ScenarioTextBlock]:
    return [
        ScenarioTextBlock(
            block_id="cta", order=4, role="cta", text="Сохраните структуру для следующего запуска."
        ),
        ScenarioTextBlock(
            block_id="quote", order=2, role="quote", text="Понятный процесс превращает сигнал в действие."
        ),
        ScenarioTextBlock(
            block_id="body", order=1, role="body", text="Начните с одного проверенного сигнала аудитории."
        ),
        ScenarioTextBlock(
            block_id="list", order=3, role="list", text="Сигнал. Паттерн. Возможность. Идея."
        ),
    ]


def _prepare_until_scenario(workdir: Path) -> dict[str, Any]:
    projects_root = workdir / "projects"
    _write_project_config(projects_root / PROJECT_ID)
    intelligence = build_content_intelligence_service(projects_root)
    scenario_service = _build_scenario_service(projects_root)

    signal = intelligence.create_market_signal(
        PROJECT_ID,
        title="Запрос на понятный маркетинговый процесс",
        description="Команды ищут короткий и проверяемый путь от наблюдения к контенту.",
        source_type="manual",
        source_reference="local acceptance fixture",
        audience_hint="Маркетинговые команды",
        content_format_hint=ContentFormat.INSTAGRAM_CAROUSEL.value,
        confidence=0.9,
    )
    signal = intelligence.review_market_signal(PROJECT_ID, signal.market_signal_id)
    pattern = intelligence.create_trend_pattern(
        PROJECT_ID,
        market_signal_ids=[signal.market_signal_id],
        title="Проверяемое планирование контента",
        summary="Аудитории нужен прозрачный путь от сигнала до готового материала.",
        affected_audience="Маркетинговые команды",
        related_platforms=[PublishingPlatform.INSTAGRAM.value],
        related_formats=[ContentFormat.INSTAGRAM_CAROUSEL.value],
        relevance_score=0.9,
        confidence=0.9,
    )
    pattern = intelligence.activate_trend_pattern(PROJECT_ID, pattern.trend_pattern_id)
    opportunity = intelligence.create_content_opportunity(
        PROJECT_ID,
        trend_pattern_id=pattern.trend_pattern_id,
        title="Как провести сигнал через понятный контентный путь",
        summary="Покажите короткую последовательность действий.",
        target_audience="Маркетинговые команды",
        content_format=ContentFormat.INSTAGRAM_CAROUSEL,
        funnel_stage="trust",
        content_pillar="content operations",
        recommended_angle="От сигнала к проверяемому результату.",
        evidence=["Local deterministic acceptance evidence"],
        confidence=0.9,
        score=0.9,
    )
    opportunity = intelligence.approve_content_opportunity(PROJECT_ID, opportunity.content_opportunity_id)
    idea = intelligence.create_idea_from_opportunity(PROJECT_ID, opportunity.content_opportunity_id)
    idea_service = IdeaService(FileSystemIdeaRepository(projects_root), ProjectService(FileSystemProjectRepository(projects_root)))
    idea = idea_service.approve_idea(PROJECT_ID, idea.idea_id)

    blocks = _carousel_blocks()
    scenario = scenario_service.create_from_idea(
        PROJECT_ID,
        idea.idea_id,
        content_format=ContentFormat.INSTAGRAM_CAROUSEL,
        target_platforms=[PublishingPlatform.INSTAGRAM],
        blocks=blocks,
    )
    if scenario.status != ScenarioStatus.NEEDS_REVIEW:
        raise RuntimeError("Scenario did not enter needs_review")

    return {
        "projects_root": projects_root,
        "signal": signal,
        "pattern": pattern,
        "opportunity": intelligence.get_content_opportunity(PROJECT_ID, opportunity.content_opportunity_id),
        "idea": idea,
        "scenario": scenario,
        "scenario_service": scenario_service,
        "input_blocks": blocks,
    }


def run_failure_smoke(workdir: Path) -> dict[str, Any]:
    context = _prepare_until_scenario(workdir)
    projects_root = context["projects_root"]
    scenario = context["scenario"]
    handoff = build_scenario_to_carousel_brief_service(projects_root)
    try:
        handoff.create_brief(PROJECT_ID, scenario.scenario_id)
    except ScenarioToCarouselBriefValidationError as error:
        error_message = str(error)
    else:
        raise RuntimeError("Unapproved Scenario unexpectedly produced a ProductionBrief")

    brief_count = len(FileSystemProductionBriefRepository(projects_root).list_briefs(PROJECT_ID))
    render_job_count = len(FileSystemRenderJobRepository(projects_root).list_render_jobs(PROJECT_ID))
    output_file_count = len(FileSystemOutputFileRepository(projects_root).list_models(PROJECT_ID))
    persisted_scenario = FileSystemScenarioRepository(projects_root).load_scenario(PROJECT_ID, scenario.scenario_id)
    if brief_count or render_job_count or output_file_count or persisted_scenario.status != ScenarioStatus.NEEDS_REVIEW:
        raise RuntimeError("Failure smoke left partial downstream records or changed Scenario status")
    return {
        "scenario_id": scenario.scenario_id,
        "scenario_status": persisted_scenario.status.value,
        "error": error_message,
        "production_brief_count": brief_count,
        "render_job_count": render_job_count,
        "output_file_count": output_file_count,
    }


def run_success(workdir: Path) -> dict[str, Any]:
    started = time.monotonic()
    context = _prepare_until_scenario(workdir)
    projects_root = context["projects_root"]
    signal = context["signal"]
    pattern = context["pattern"]
    opportunity = context["opportunity"]
    idea = context["idea"]
    scenario = context["scenario"]
    input_blocks = context["input_blocks"]
    scenario_service: ScenarioService = context["scenario_service"]

    scenario = scenario_service.approve_scenario(PROJECT_ID, scenario.scenario_id)
    if scenario.status != ScenarioStatus.APPROVED:
        raise RuntimeError("Scenario did not become approved")
    brief = build_scenario_to_carousel_brief_service(projects_root).create_brief(PROJECT_ID, scenario.scenario_id)
    pipeline = build_production_pipeline_service(projects_root)
    render_job = pipeline.create_render_job(PROJECT_ID, brief.production_brief_id)
    render_job = pipeline.validate_assets(PROJECT_ID, render_job.render_job_id)
    if render_job.status != RenderJobStatus.RENDERING:
        raise RuntimeError("RenderJob assets did not validate")
    render_job = pipeline.execute_render(PROJECT_ID, render_job.render_job_id)
    if render_job.status != RenderJobStatus.RENDERED:
        raise RuntimeError("RenderJob did not reach rendered")

    output_directory = workdir / "storage" / PROJECT_ID / "renders" / render_job.render_job_id / "carousel"
    qa_result = check_carousel_output(output_directory, expected_count=len(brief.slides), expected_size=(1080, 1350))
    if not qa_result.passed:
        raise RuntimeError("Carousel QA failed: " + "; ".join(qa_result.errors))
    output_records = FileSystemOutputFileRepository(projects_root).list_output_files_by_render_job(PROJECT_ID, render_job.render_job_id)
    if len(output_records) != len(brief.slides):
        raise RuntimeError("OutputFile count does not match rendered carousel PNG count")

    output_files = []
    for output in output_records:
        path = (workdir / output.path).resolve()
        if not path.is_relative_to(output_directory.resolve()) or not path.is_file():
            raise RuntimeError(f"OutputFile path is outside the render directory or missing: {output.path}")
        from PIL import Image
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        if (width, height) != (1080, 1350) or output.mime_type != "image/png" or path.stat().st_size == 0:
            raise RuntimeError(f"Invalid rendered PNG: {path}")
        output_files.append({
            "output_file_id": output.output_file_id,
            "relative_path": output.path,
            "mime_type": output.mime_type,
            "size_bytes": path.stat().st_size,
            "width": width,
            "height": height,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })

    expected_texts = [block.text for block in sorted(input_blocks, key=lambda item: item.order)]
    actual_texts = [block.text for block in scenario.blocks]
    traceability = {
        "trend_pattern_market_signal": signal.market_signal_id in pattern.market_signal_ids,
        "opportunity_trend_pattern": opportunity.trend_pattern_id == pattern.trend_pattern_id,
        "opportunity_idea": opportunity.idea_id == idea.idea_id,
        "idea_intelligence_source": idea.source_type == "trend" and idea.source_id == opportunity.content_opportunity_id,
        "scenario_idea": scenario.idea_id == idea.idea_id and scenario.source_id == idea.idea_id,
        "brief_scenario": brief.scenario_id == scenario.scenario_id,
        "render_job_brief": render_job.input_snapshot["brief_id"] == brief.production_brief_id,
        "render_job_scenario": render_job.scenario_id == scenario.scenario_id,
        "output_files_render_job": all(item.render_job_id == render_job.render_job_id for item in output_records),
    }
    checks = {
        "opportunity_converted": opportunity.status == ContentOpportunityStatus.CONVERTED,
        "idea_approved_before_planning": idea.status == IdeaStatus.APPROVED,
        "scenario_blocks_sorted": [block.order for block in scenario.blocks] == [1, 2, 3, 4],
        "scenario_texts_unchanged": actual_texts == expected_texts,
        "brief_validated": brief.status.value == "validated",
        "brief_templates": [slide.template for slide in brief.slides] == ["cover", "text_image", "quote", "list", "cta"],
        "qa_passed": qa_result.passed,
        "all_traceability_links_valid": all(traceability.values()),
    }
    if not all(checks.values()):
        raise RuntimeError("Acceptance checks failed")
    return {
        "success": True,
        "workspace_id": WORKSPACE_ID,
        "project_id": PROJECT_ID,
        "market_signal_id": signal.market_signal_id,
        "trend_pattern_id": pattern.trend_pattern_id,
        "content_opportunity_id": opportunity.content_opportunity_id,
        "idea_id": idea.idea_id,
        "scenario_id": scenario.scenario_id,
        "production_brief_id": brief.production_brief_id,
        "render_job_id": render_job.render_job_id,
        "statuses": {
            "opportunity": opportunity.status.value,
            "idea": IdeaStatus.SCRIPTED.value,
            "scenario": scenario.status.value,
            "production_brief": brief.status.value,
            "render_job": render_job.status.value,
        },
        "output_files": output_files,
        "output_file_count": len(output_files),
        "rendered_png_count": len(list(output_directory.glob("*.png"))),
        "output_directory": str(output_directory),
        "traceability": traceability,
        "checks": checks,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def run_acceptance(workdir: Path) -> dict[str, Any]:
    """Run the success path with the runtime artifact root scoped to workdir."""
    previous_cwd = Path.cwd()
    try:
        os.chdir(workdir)
        return run_success(workdir)
    finally:
        os.chdir(previous_cwd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local Intelligence-to-carousel acceptance.")
    parser.add_argument("--workdir", type=Path, help="Directory containing the acceptance project and render output.")
    parser.add_argument("--keep-output", action="store_true", help="Keep an automatically created temporary work directory.")
    parser.add_argument("--json", action="store_true", help="Write the structured acceptance result to stdout.")
    args = parser.parse_args()
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.workdir:
        workdir = args.workdir.resolve()
        workdir.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="loopra-intelligence-carousel-")
        workdir = Path(temporary.name)
    try:
        result = run_acceptance(workdir)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else "Intelligence-to-carousel acceptance: PASSED")
        return 0
    except Exception as error:
        result = {"success": False, "error": str(error), "output_directory": str(workdir)}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else f"ERROR: {error}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None and not args.keep_output:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

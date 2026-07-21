from __future__ import annotations

from pathlib import Path

from core.domain import (
    ContentFormat,
    ProductionBrand,
    ProductionBrief,
    ProductionBriefStatus,
    ProductionOutput,
    ProductionSlide,
    PublishingPlatform,
    Scenario,
    ScenarioStatus,
)

from .ideas import FileSystemScenarioRepository
from .production_pipeline import FileSystemProductionBriefRepository
from .projects import BrandProfileService, FileSystemProjectRepository, ProjectService


SCENARIO_CAROUSEL_VARIANT = "scenario_carousel_v1"
_ROLE_TO_TEMPLATE = {
    "body": "text_image",
    "quote": "quote",
    "list": "list",
    "cta": "cta",
}


class ScenarioToCarouselBriefValidationError(ValueError):
    """Raised when an approved Scenario cannot be handed off to carousel production."""


class ScenarioToCarouselBriefService:
    """Build and persist one deterministic Instagram carousel brief from a Scenario."""

    def __init__(
        self,
        scenario_repository: FileSystemScenarioRepository,
        brief_repository: FileSystemProductionBriefRepository,
        project_repository: FileSystemProjectRepository,
        project_service: ProjectService,
        brand_profile_service: BrandProfileService,
    ) -> None:
        self._scenarios = scenario_repository
        self._briefs = brief_repository
        self._projects = project_repository
        self._project_service = project_service
        self._brand_profiles = brand_profile_service

    def create_brief(self, project_id: str, scenario_id: str) -> ProductionBrief:
        project = self._project_service.get_project(project_id)
        scenario = self._scenarios.load_scenario(project_id, scenario_id)
        self._validate_scenario(scenario, project.workspace_id, project.project_id)
        self._ensure_no_duplicate(project_id, scenario.scenario_id)

        brand_profile = self._brand_profiles.get_brand_profile(project_id)
        project_config = self._projects.load_project_config(project_id)
        brief = ProductionBrief(
            production_brief_id=f"brief_{scenario.scenario_id}_{SCENARIO_CAROUSEL_VARIANT}",
            workspace_id=scenario.workspace_id,
            project_id=scenario.project_id,
            scenario_id=scenario.scenario_id,
            content_format=ContentFormat.INSTAGRAM_CAROUSEL,
            production_variant=SCENARIO_CAROUSEL_VARIANT,
            target_platforms=[PublishingPlatform.INSTAGRAM],
            output=ProductionOutput(aspect_ratio="4:5", resolution_width=1080, resolution_height=1350),
            brand=self._build_brand_snapshot(brand_profile, project_config),
            slides=self._build_slides(scenario),
        ).transition_to(ProductionBriefStatus.VALIDATED)
        return self._briefs.save_brief(brief)

    @staticmethod
    def _validate_scenario(scenario: Scenario, workspace_id: str, project_id: str) -> None:
        if scenario.workspace_id != workspace_id or scenario.project_id != project_id:
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario.scenario_id}' does not belong to project '{project_id}'"
            )
        if scenario.status != ScenarioStatus.APPROVED:
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario.scenario_id}' must be approved before carousel brief handoff"
            )
        if scenario.content_format != ContentFormat.INSTAGRAM_CAROUSEL:
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario.scenario_id}' must use content_format 'instagram_carousel'"
            )
        if not scenario.blocks:
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario.scenario_id}' must contain at least one carousel block"
            )
        block_ids = [block.block_id for block in scenario.blocks]
        if len(block_ids) != len(set(block_ids)):
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario.scenario_id}' contains duplicate block_id values"
            )
        orders = [block.order for block in scenario.blocks]
        if len(orders) != len(set(orders)):
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario.scenario_id}' contains duplicate block order values"
            )
        for block in scenario.blocks:
            if not block.text.strip():
                raise ScenarioToCarouselBriefValidationError(
                    f"Scenario block '{block.block_id}' must contain visible text"
                )
            if block.role not in _ROLE_TO_TEMPLATE:
                raise ScenarioToCarouselBriefValidationError(
                    f"Scenario block '{block.block_id}' has unsupported carousel role '{block.role}'"
                )

    def _ensure_no_duplicate(self, project_id: str, scenario_id: str) -> None:
        duplicate = next(
            (
                brief for brief in self._briefs.list_briefs(project_id)
                if brief.scenario_id == scenario_id
                and brief.content_format == ContentFormat.INSTAGRAM_CAROUSEL
                and brief.production_variant == SCENARIO_CAROUSEL_VARIANT
            ),
            None,
        )
        if duplicate is not None:
            raise ScenarioToCarouselBriefValidationError(
                f"Scenario '{scenario_id}' already has carousel brief '{duplicate.production_brief_id}' "
                f"for variant '{SCENARIO_CAROUSEL_VARIANT}'"
            )

    @staticmethod
    def _build_slides(scenario: Scenario) -> list[ProductionSlide]:
        slides = [ProductionSlide(slide_number=1, template="cover", heading=scenario.title)]
        for slide_number, block in enumerate(sorted(scenario.blocks, key=lambda item: item.order), start=2):
            template = _ROLE_TO_TEMPLATE[block.role]
            if block.role == "cta":
                slides.append(ProductionSlide(slide_number=slide_number, template=template, cta=block.text))
            else:
                slides.append(ProductionSlide(slide_number=slide_number, template=template, body=block.text))
        return slides

    @staticmethod
    def _build_brand_snapshot(_brand_profile: object, project_config: object) -> ProductionBrand:
        brand_config = getattr(project_config, "brand")
        colors = dict(getattr(brand_config, "colors", {}))
        fonts = dict(getattr(brand_config, "fonts", {}))
        return ProductionBrand(
            website_text=str(getattr(project_config, "primary_url", "") or ""),
            colors_primary=colors.get("primary", ""),
            colors_accent=colors.get("accent", ""),
            colors_background_dark=colors.get("background_dark", ""),
            colors_text_light=colors.get("text_light", ""),
            colors_text_muted=colors.get("text_muted", ""),
            fonts_heading=fonts.get("heading", ""),
            fonts_body=fonts.get("body", ""),
        )


def build_scenario_to_carousel_brief_service(
    projects_root: Path | None = None,
) -> ScenarioToCarouselBriefService:
    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    return ScenarioToCarouselBriefService(
        scenario_repository=FileSystemScenarioRepository(projects_root),
        brief_repository=FileSystemProductionBriefRepository(projects_root),
        project_repository=project_repository,
        project_service=project_service,
        brand_profile_service=BrandProfileService(project_repository),
    )

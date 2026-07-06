from __future__ import annotations

from collections.abc import Iterable, Sequence
import json
from pathlib import Path
import re
from uuid import uuid4

from core.domain import (
    BrandProfile,
    ContentFormat,
    Idea,
    IdeaStatus,
    PublishingPlatform,
    Scenario,
    ScenarioStatus,
    ScenarioTextBlock,
)
from core.projects.loader import PROJECTS_ROOT, resolve_project_dir, validate_project_id

from .projects import BrandProfileService, FileSystemProjectRepository, ProjectService


VALID_FUNNEL_STAGES = {"attention", "trust", "conversion", "retention"}
VALID_IDEA_SOURCE_TYPES = {
    "manual",
    "trend",
    "analytics_insight",
    "content_strategy",
    "past_content",
    "campaign",
    "import",
    "agent_suggestion",
}
VALID_IDEA_PRIORITIES = {"low", "medium", "high", "urgent"}
TEXT_SOCIAL_POST_DEFAULT_PLATFORMS = (
    PublishingPlatform.TELEGRAM,
    PublishingPlatform.THREADS,
    PublishingPlatform.VK,
)
TEXT_SOCIAL_POST_LENGTH_TARGETS: dict[PublishingPlatform, tuple[int, int]] = {
    PublishingPlatform.TELEGRAM: (700, 1800),
    PublishingPlatform.THREADS: (150, 700),
    PublishingPlatform.VK: (800, 2500),
}
ENTITY_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class IdeaBankValidationError(ValueError):
    """Raised when Idea Bank inputs or storage are invalid."""


class ScenarioStudioValidationError(ValueError):
    """Raised when Scenario Studio inputs or state are invalid."""


class _FileSystemProjectEntityRepository:
    def __init__(self, projects_root: Path | None = None) -> None:
        self._projects_root = projects_root or PROJECTS_ROOT

    def _project_data_dir(self, project_id: str, collection: str) -> Path:
        project_dir = resolve_project_dir(project_id, self._projects_root)
        return project_dir / "data" / collection

    @staticmethod
    def _validate_entity_id(entity_id: str, entity_name: str) -> str:
        if not isinstance(entity_id, str):
            raise IdeaBankValidationError(f"{entity_name} must be a string")

        normalized = entity_id.strip()
        if not normalized:
            raise IdeaBankValidationError(f"{entity_name} must not be empty")
        if not ENTITY_ID_PATTERN.fullmatch(normalized):
            raise IdeaBankValidationError(
                f"{entity_name} must match ^[a-z0-9][a-z0-9_-]*$ and must not contain path separators"
            )
        return normalized

    def _list_models(self, project_id: str, collection: str, model_type: type[Idea] | type[Scenario]) -> list[Idea] | list[Scenario]:
        validate_project_id(project_id)
        data_dir = self._project_data_dir(project_id, collection)
        if not data_dir.exists():
            return []

        items = [
            model_type.model_validate(json.loads(file_path.read_text(encoding="utf-8")))
            for file_path in sorted(data_dir.glob("*.json"))
        ]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    def _load_model(
        self,
        project_id: str,
        entity_id: str,
        *,
        collection: str,
        entity_name: str,
        model_type: type[Idea] | type[Scenario],
    ) -> Idea | Scenario:
        validate_project_id(project_id)
        safe_entity_id = self._validate_entity_id(entity_id, entity_name)
        file_path = self._project_data_dir(project_id, collection) / f"{safe_entity_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(
                f"{entity_name} '{safe_entity_id}' not found for project_id '{project_id}': {file_path}"
            )
        return model_type.model_validate(json.loads(file_path.read_text(encoding="utf-8")))

    def _save_model(self, project_id: str, entity_id: str, collection: str, payload: dict[str, object]) -> None:
        data_dir = self._project_data_dir(project_id, collection)
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / f"{entity_id}.json"
        file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


class FileSystemIdeaRepository(_FileSystemProjectEntityRepository):
    def list_ideas(self, project_id: str) -> list[Idea]:
        return list(self._list_models(project_id, "ideas", Idea))

    def load_idea(self, project_id: str, idea_id: str) -> Idea:
        return self._load_model(
            project_id,
            idea_id,
            collection="ideas",
            entity_name="idea_id",
            model_type=Idea,
        )

    def save_idea(self, idea: Idea) -> Idea:
        safe_idea_id = self._validate_entity_id(idea.idea_id, "idea_id")
        self._save_model(idea.project_id, safe_idea_id, "ideas", idea.model_dump(mode="json"))
        return idea


class FileSystemScenarioRepository(_FileSystemProjectEntityRepository):
    def list_scenarios(self, project_id: str) -> list[Scenario]:
        return list(self._list_models(project_id, "scenarios", Scenario))

    def load_scenario(self, project_id: str, scenario_id: str) -> Scenario:
        return self._load_model(
            project_id,
            scenario_id,
            collection="scenarios",
            entity_name="scenario_id",
            model_type=Scenario,
        )

    def save_scenario(self, scenario: Scenario) -> Scenario:
        safe_scenario_id = self._validate_entity_id(scenario.scenario_id, "scenario_id")
        self._save_model(
            scenario.project_id,
            safe_scenario_id,
            "scenarios",
            scenario.model_dump(mode="json"),
        )
        return scenario


class IdeaService:
    def __init__(
        self,
        repository: FileSystemIdeaRepository,
        project_service: ProjectService,
    ) -> None:
        self._repository = repository
        self._project_service = project_service

    def list_ideas(self, project_id: str, *, status: IdeaStatus | None = None) -> list[Idea]:
        self._project_service.get_project(project_id)
        ideas = self._repository.list_ideas(project_id)
        if status is None:
            return ideas
        return [idea for idea in ideas if idea.status == status]

    def get_idea(self, project_id: str, idea_id: str) -> Idea:
        self._project_service.get_project(project_id)
        return self._repository.load_idea(project_id, idea_id)

    def create_idea(
        self,
        project_id: str,
        *,
        title: str,
        description: str = "",
        topic: str = "",
        funnel_stage: str = "attention",
        content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST,
        source_type: str = "manual",
        source_id: str = "",
        priority: str = "medium",
        tags: Sequence[str] | None = None,
    ) -> Idea:
        project = self._project_service.get_project(project_id)
        self._validate_funnel_stage(funnel_stage)
        self._validate_source_type(source_type)
        self._validate_priority(priority)

        idea = Idea(
            idea_id=_build_entity_id("idea"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            title=title,
            description=description,
            topic=topic,
            funnel_stage=funnel_stage,
            content_format=content_format,
            source_type=source_type,
            source_id=source_id,
            priority=priority,
            tags=list(tags or []),
            status=IdeaStatus.RAW,
        )
        return self._repository.save_idea(idea)

    def approve_idea(self, project_id: str, idea_id: str) -> Idea:
        idea = self.get_idea(project_id, idea_id)
        approved = idea.transition_to(IdeaStatus.APPROVED)
        return self._repository.save_idea(approved)

    def reject_idea(self, project_id: str, idea_id: str) -> Idea:
        idea = self.get_idea(project_id, idea_id)
        rejected = idea.transition_to(IdeaStatus.REJECTED)
        return self._repository.save_idea(rejected)

    def archive_idea(self, project_id: str, idea_id: str) -> Idea:
        idea = self.get_idea(project_id, idea_id)
        archived = idea.transition_to(IdeaStatus.ARCHIVED)
        return self._repository.save_idea(archived)

    @staticmethod
    def next_action_for(idea: Idea) -> str:
        mapping = {
            IdeaStatus.RAW: "approve_or_reject",
            IdeaStatus.APPROVED: "generate_scenario",
            IdeaStatus.REJECTED: "archive",
            IdeaStatus.SCRIPTED: "open_scenarios",
            IdeaStatus.ARCHIVED: "none",
        }
        return mapping[idea.status]

    @staticmethod
    def _validate_funnel_stage(funnel_stage: str) -> None:
        if funnel_stage not in VALID_FUNNEL_STAGES:
            raise IdeaBankValidationError(
                f"Invalid funnel_stage '{funnel_stage}'. Allowed: {sorted(VALID_FUNNEL_STAGES)}"
            )

    @staticmethod
    def _validate_source_type(source_type: str) -> None:
        if source_type not in VALID_IDEA_SOURCE_TYPES:
            raise IdeaBankValidationError(
                f"Invalid source_type '{source_type}'. Allowed: {sorted(VALID_IDEA_SOURCE_TYPES)}"
            )

    @staticmethod
    def _validate_priority(priority: str) -> None:
        if priority not in VALID_IDEA_PRIORITIES:
            raise IdeaBankValidationError(
                f"Invalid priority '{priority}'. Allowed: {sorted(VALID_IDEA_PRIORITIES)}"
            )


class ScenarioService:
    def __init__(
        self,
        repository: FileSystemScenarioRepository,
        project_repository: FileSystemProjectRepository,
        project_service: ProjectService,
        brand_profile_service: BrandProfileService,
        idea_service: IdeaService,
        idea_repository: FileSystemIdeaRepository,
    ) -> None:
        self._repository = repository
        self._project_repository = project_repository
        self._project_service = project_service
        self._brand_profile_service = brand_profile_service
        self._idea_service = idea_service
        self._idea_repository = idea_repository

    def list_scenarios(
        self,
        project_id: str,
        *,
        idea_id: str | None = None,
        content_format: ContentFormat | None = None,
    ) -> list[Scenario]:
        self._project_service.get_project(project_id)
        scenarios = self._repository.list_scenarios(project_id)
        if idea_id is not None:
            scenarios = [scenario for scenario in scenarios if scenario.idea_id == idea_id]
        if content_format is not None:
            scenarios = [scenario for scenario in scenarios if scenario.content_format == content_format]
        return scenarios

    def get_scenario(self, project_id: str, scenario_id: str) -> Scenario:
        self._project_service.get_project(project_id)
        return self._repository.load_scenario(project_id, scenario_id)

    def create_manual_scenario(
        self,
        project_id: str,
        *,
        title: str,
        content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST,
        funnel_stage: str = "attention",
        target_platforms: Sequence[PublishingPlatform | str] | None = None,
        blocks: Sequence[ScenarioTextBlock | dict[str, object]] | None = None,
        draft_text: str = "",
        metadata: dict[str, object] | None = None,
    ) -> Scenario:
        project = self._project_service.get_project(project_id)
        brand_profile = self._brand_profile_service.get_brand_profile(project_id)
        self._idea_service._validate_funnel_stage(funnel_stage)

        scenario = Scenario(
            scenario_id=_build_entity_id("scenario"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            idea_id=_build_entity_id("manual"),
            brand_profile_id=brand_profile.brand_profile_id,
            source_type="manual",
            source_id="",
            title=title,
            draft_text=draft_text,
            funnel_stage=funnel_stage,
            content_format=content_format,
            target_platforms=self._normalize_platforms(
                target_platforms or self._default_platforms_for(content_format)
            ),
            blocks=self._normalize_blocks(blocks or []),
            status=ScenarioStatus.DRAFT,
            metadata=dict(metadata or {}),
        )
        return self._repository.save_scenario(scenario)

    def create_from_idea(
        self,
        project_id: str,
        idea_id: str,
        *,
        content_format: ContentFormat | None = None,
        target_platforms: Sequence[PublishingPlatform | str] | None = None,
    ) -> Scenario:
        project = self._project_service.get_project(project_id)
        idea = self._idea_service.get_idea(project_id, idea_id)
        brand_profile = self._brand_profile_service.get_brand_profile(project_id)

        if idea.status not in {IdeaStatus.APPROVED, IdeaStatus.SCRIPTED}:
            raise ScenarioStudioValidationError(
                f"Idea '{idea.idea_id}' must be approved before scenario generation"
            )

        resolved_format = content_format or idea.content_format
        if resolved_format != ContentFormat.TEXT_SOCIAL_POST:
            raise ScenarioStudioValidationError(
                f"Scenario generation currently supports only '{ContentFormat.TEXT_SOCIAL_POST.value}'"
            )

        platforms = self._resolve_target_platforms(
            project_id,
            resolved_format,
            target_platforms=target_platforms,
        )
        blocks = self._build_text_social_post_blocks(idea, brand_profile, platforms)
        draft_text = "\n\n---\n\n".join(block.text for block in blocks)
        caption_drafts = {
            platform.value: self._build_caption_draft(platform, idea, brand_profile)
            for platform in platforms
        }

        scenario = Scenario(
            scenario_id=_build_entity_id("scenario"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            idea_id=idea.idea_id,
            brand_profile_id=brand_profile.brand_profile_id,
            source_type="idea",
            source_id=idea.idea_id,
            title=f"{idea.title} - {resolved_format.value}",
            draft_text=draft_text,
            funnel_stage=idea.funnel_stage,
            content_format=resolved_format,
            target_platforms=platforms,
            blocks=blocks,
            caption_drafts=caption_drafts,
            qa_warnings=self._run_text_social_post_qa(blocks, brand_profile, idea.funnel_stage),
            status=ScenarioStatus.NEEDS_REVIEW,
            metadata={
                "post_subtype": "explainer_post",
                "source_type": idea.source_type,
                "source_id": idea.source_id,
                "topic": idea.topic,
                "priority": idea.priority,
            },
        )
        saved_scenario = self._repository.save_scenario(scenario)

        if idea.status == IdeaStatus.APPROVED:
            scripted = idea.transition_to(IdeaStatus.SCRIPTED)
            self._idea_repository.save_idea(scripted)

        return saved_scenario

    def submit_for_review(self, project_id: str, scenario_id: str) -> Scenario:
        scenario = self.get_scenario(project_id, scenario_id)
        needs_review = scenario.transition_to(ScenarioStatus.NEEDS_REVIEW)
        return self._repository.save_scenario(needs_review)

    def approve_scenario(self, project_id: str, scenario_id: str) -> Scenario:
        scenario = self.get_scenario(project_id, scenario_id)
        approved = scenario.transition_to(ScenarioStatus.APPROVED)
        return self._repository.save_scenario(approved)

    def reject_scenario(self, project_id: str, scenario_id: str) -> Scenario:
        scenario = self.get_scenario(project_id, scenario_id)
        rejected = scenario.transition_to(ScenarioStatus.REJECTED)
        return self._repository.save_scenario(rejected)

    def archive_scenario(self, project_id: str, scenario_id: str) -> Scenario:
        scenario = self.get_scenario(project_id, scenario_id)
        archived = scenario.transition_to(ScenarioStatus.ARCHIVED)
        return self._repository.save_scenario(archived)

    def _resolve_target_platforms(
        self,
        project_id: str,
        content_format: ContentFormat,
        *,
        target_platforms: Sequence[PublishingPlatform | str] | None,
    ) -> list[PublishingPlatform]:
        if target_platforms:
            return self._normalize_platforms(target_platforms)

        project_config = self._project_repository.load_project_config(project_id)
        configured_platforms = self._normalize_platforms(project_config.target_platforms)
        if configured_platforms:
            return configured_platforms
        return self._default_platforms_for(content_format)

    @staticmethod
    def _default_platforms_for(content_format: ContentFormat) -> list[PublishingPlatform]:
        if content_format == ContentFormat.TEXT_SOCIAL_POST:
            return list(TEXT_SOCIAL_POST_DEFAULT_PLATFORMS)
        return []

    @staticmethod
    def _normalize_platforms(platforms: Iterable[PublishingPlatform | str]) -> list[PublishingPlatform]:
        normalized: list[PublishingPlatform] = []
        for platform in platforms:
            resolved = platform if isinstance(platform, PublishingPlatform) else PublishingPlatform(platform)
            if resolved not in normalized:
                normalized.append(resolved)
        return normalized

    @staticmethod
    def _normalize_blocks(blocks: Sequence[ScenarioTextBlock | dict[str, object]]) -> list[ScenarioTextBlock]:
        normalized: list[ScenarioTextBlock] = []
        for index, block in enumerate(blocks, start=1):
            if isinstance(block, ScenarioTextBlock):
                normalized.append(block)
                continue
            payload = dict(block)
            payload.setdefault("block_id", _build_entity_id("block"))
            payload.setdefault("order", index)
            normalized.append(ScenarioTextBlock.model_validate(payload))
        return normalized

    def _build_text_social_post_blocks(
        self,
        idea: Idea,
        brand_profile: BrandProfile,
        platforms: Sequence[PublishingPlatform],
    ) -> list[ScenarioTextBlock]:
        blocks: list[ScenarioTextBlock] = []
        for order, platform in enumerate(platforms, start=1):
            blocks.append(
                ScenarioTextBlock(
                    block_id=_build_entity_id("block"),
                    order=order,
                    role="post_body",
                    platform=platform,
                    text=self._build_platform_post(platform, idea, brand_profile),
                )
            )
        return blocks

    def _build_platform_post(
        self,
        platform: PublishingPlatform,
        idea: Idea,
        brand_profile: BrandProfile,
    ) -> str:
        hook = idea.title.strip().rstrip(".")
        explanation = (
            idea.description.strip()
            or f"This angle helps explain the topic in a way that feels practical and easy to follow."
        )
        insight = self._build_insight_sentence(brand_profile)
        cta = self._build_cta(platform, idea.funnel_stage)

        if platform == PublishingPlatform.THREADS:
            parts = [
                hook,
                explanation,
                insight,
            ]
            if cta:
                parts.append(cta)
            return "\n".join(parts)

        if platform == PublishingPlatform.VK:
            parts = [
                hook,
                "",
                explanation,
                "",
                insight,
            ]
            if cta:
                parts.extend(["", cta])
            return "\n".join(parts)

        parts = [
            hook,
            "",
            explanation,
            "",
            insight,
        ]
        if cta:
            parts.extend(["", cta])
        return "\n".join(parts)

    @staticmethod
    def _build_insight_sentence(brand_profile: BrandProfile) -> str:
        positioning = brand_profile.positioning.strip().rstrip(".")
        audience = brand_profile.audience_summary.strip().rstrip(".")
        if positioning and audience:
            return (
                f"It keeps the message grounded in {positioning.lower()} "
                f"for {audience.lower()}."
            )
        if positioning:
            return f"It keeps the message grounded in {positioning.lower()}."
        return "It keeps the message grounded in the current Brand Profile."

    @staticmethod
    def _build_cta(platform: PublishingPlatform, funnel_stage: str) -> str:
        if funnel_stage == "attention":
            return ""
        if funnel_stage == "trust":
            return "Keep this structure nearby for the next explanatory post."
        if funnel_stage == "conversion":
            if platform == PublishingPlatform.THREADS:
                return "Use the next step that best fits the project offer."
            return "Use this as the bridge into the next project-specific call to action."
        if funnel_stage == "retention":
            return "Bring this angle back into the regular content rhythm."
        return ""

    def _build_caption_draft(
        self,
        platform: PublishingPlatform,
        idea: Idea,
        brand_profile: BrandProfile,
    ) -> str:
        return (
            f"{idea.title.strip()}\n"
            f"{self._build_insight_sentence(brand_profile)}\n"
            f"{self._build_cta(platform, idea.funnel_stage)}"
        ).strip()

    @staticmethod
    def _run_text_social_post_qa(
        blocks: Sequence[ScenarioTextBlock],
        brand_profile: BrandProfile,
        funnel_stage: str,
    ) -> list[str]:
        warnings: list[str] = []
        forbidden_phrases = [phrase.lower() for phrase in brand_profile.tone_of_voice.forbidden_phrases]
        forbidden_topics = [topic.lower() for topic in brand_profile.content_rules.forbidden_topics]

        if not forbidden_phrases:
            warnings.append("Brand Profile has no forbidden phrases list.")

        for block in blocks:
            body = block.text.strip()
            if not body:
                warnings.append(f"{block.platform.value}: body is empty.")
                continue

            if block.platform in TEXT_SOCIAL_POST_LENGTH_TARGETS:
                min_length, max_length = TEXT_SOCIAL_POST_LENGTH_TARGETS[block.platform]
                if len(body) < min_length:
                    warnings.append(
                        f"{block.platform.value}: body is shorter than the recommended {min_length} characters."
                    )
                if len(body) > max_length:
                    warnings.append(
                        f"{block.platform.value}: body is longer than the recommended {max_length} characters."
                    )

            body_lower = body.lower()
            for phrase in forbidden_phrases:
                if phrase and phrase in body_lower:
                    warnings.append(f"{block.platform.value}: forbidden phrase detected: '{phrase}'.")

            for topic in forbidden_topics:
                if topic and topic in body_lower:
                    warnings.append(f"{block.platform.value}: forbidden topic detected: '{topic}'.")

            if funnel_stage == "conversion" and "call to action" not in body_lower and "next step" not in body_lower:
                warnings.append(f"{block.platform.value}: conversion-stage post may need a clearer CTA.")

        return warnings


def _build_entity_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"

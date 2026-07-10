from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from core.domain import (
    ContentFormat,
    ContentOpportunity,
    ContentOpportunityStatus,
    Idea,
    MarketSignal,
    MarketSignalStatus,
    TrendPattern,
    TrendPatternStatus,
)
from core.domain.models import utc_now
from core.services._storage import FileSystemProjectModelRepository, build_entity_id
from core.services.ideas import IdeaService, VALID_FUNNEL_STAGES
from core.services.projects import ProjectService


class ContentIntelligenceValidationError(ValueError):
    """Raised when deterministic Content Intelligence inputs or state are invalid."""


class FileSystemMarketSignalRepository(FileSystemProjectModelRepository[MarketSignal]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("market_signals", MarketSignal, projects_root)

    def list_market_signals(self, project_id: str) -> list[MarketSignal]:
        return self.list_models(project_id)

    def load_market_signal(self, project_id: str, market_signal_id: str) -> MarketSignal:
        return self.load_model(project_id, market_signal_id, entity_name="market_signal_id")

    def save_market_signal(self, market_signal: MarketSignal) -> MarketSignal:
        return self.save_model(market_signal.project_id, market_signal.market_signal_id, market_signal)


class FileSystemTrendPatternRepository(FileSystemProjectModelRepository[TrendPattern]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("trend_patterns", TrendPattern, projects_root)

    def list_trend_patterns(self, project_id: str) -> list[TrendPattern]:
        return self.list_models(project_id)

    def load_trend_pattern(self, project_id: str, trend_pattern_id: str) -> TrendPattern:
        return self.load_model(project_id, trend_pattern_id, entity_name="trend_pattern_id")

    def save_trend_pattern(self, trend_pattern: TrendPattern) -> TrendPattern:
        return self.save_model(trend_pattern.project_id, trend_pattern.trend_pattern_id, trend_pattern)


class FileSystemContentOpportunityRepository(FileSystemProjectModelRepository[ContentOpportunity]):
    def __init__(self, projects_root: Path | None = None) -> None:
        super().__init__("content_opportunities", ContentOpportunity, projects_root)

    def list_content_opportunities(self, project_id: str) -> list[ContentOpportunity]:
        return self.list_models(project_id)

    def load_content_opportunity(self, project_id: str, content_opportunity_id: str) -> ContentOpportunity:
        return self.load_model(project_id, content_opportunity_id, entity_name="content_opportunity_id")

    def save_content_opportunity(self, content_opportunity: ContentOpportunity) -> ContentOpportunity:
        return self.save_model(
            content_opportunity.project_id,
            content_opportunity.content_opportunity_id,
            content_opportunity,
        )


class ContentIntelligenceService:
    def __init__(
        self,
        market_signal_repository: FileSystemMarketSignalRepository,
        trend_pattern_repository: FileSystemTrendPatternRepository,
        content_opportunity_repository: FileSystemContentOpportunityRepository,
        project_service: ProjectService,
        idea_service: IdeaService,
    ) -> None:
        self._market_signals = market_signal_repository
        self._trend_patterns = trend_pattern_repository
        self._opportunities = content_opportunity_repository
        self._project_service = project_service
        self._idea_service = idea_service

    def create_market_signal(self, project_id: str, **payload: object) -> MarketSignal:
        project = self._project_service.get_project(project_id)
        signal = MarketSignal(
            market_signal_id=build_entity_id("signal"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            **payload,
        )
        return self._market_signals.save_market_signal(signal)

    def list_market_signals(self, project_id: str, *, status: MarketSignalStatus | None = None) -> list[MarketSignal]:
        self._project_service.get_project(project_id)
        signals = self._market_signals.list_market_signals(project_id)
        return signals if status is None else [signal for signal in signals if signal.status == status]

    def get_market_signal(self, project_id: str, market_signal_id: str) -> MarketSignal:
        self._project_service.get_project(project_id)
        return self._market_signals.load_market_signal(project_id, market_signal_id)

    def create_trend_pattern(self, project_id: str, *, market_signal_ids: Sequence[str], **payload: object) -> TrendPattern:
        project = self._project_service.get_project(project_id)
        signal_ids = self._require_signal_ids(market_signal_ids)
        signals = [self.get_market_signal(project_id, signal_id) for signal_id in signal_ids]
        pattern = TrendPattern(
            trend_pattern_id=build_entity_id("trend"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            market_signal_ids=[signal.market_signal_id for signal in signals],
            **payload,
        )
        return self._trend_patterns.save_trend_pattern(pattern)

    def list_trend_patterns(self, project_id: str, *, status: TrendPatternStatus | None = None) -> list[TrendPattern]:
        self._project_service.get_project(project_id)
        patterns = self._trend_patterns.list_trend_patterns(project_id)
        return patterns if status is None else [pattern for pattern in patterns if pattern.status == status]

    def get_trend_pattern(self, project_id: str, trend_pattern_id: str) -> TrendPattern:
        self._project_service.get_project(project_id)
        return self._trend_patterns.load_trend_pattern(project_id, trend_pattern_id)

    def activate_trend_pattern(self, project_id: str, trend_pattern_id: str) -> TrendPattern:
        pattern = self.get_trend_pattern(project_id, trend_pattern_id)
        return self._trend_patterns.save_trend_pattern(pattern.transition_to(TrendPatternStatus.ACTIVE))

    def create_content_opportunity(self, project_id: str, *, trend_pattern_id: str, **payload: object) -> ContentOpportunity:
        project = self._project_service.get_project(project_id)
        pattern = self.get_trend_pattern(project_id, trend_pattern_id)
        funnel_stage = str(payload.get("funnel_stage", "attention"))
        if funnel_stage not in VALID_FUNNEL_STAGES:
            raise ContentIntelligenceValidationError(
                f"Invalid funnel_stage '{funnel_stage}'. Allowed: {sorted(VALID_FUNNEL_STAGES)}"
            )
        opportunity = ContentOpportunity(
            content_opportunity_id=build_entity_id("opportunity"),
            workspace_id=project.workspace_id,
            project_id=project.project_id,
            trend_pattern_id=pattern.trend_pattern_id,
            **payload,
        )
        return self._opportunities.save_content_opportunity(opportunity)

    def list_content_opportunities(
        self,
        project_id: str,
        *,
        status: ContentOpportunityStatus | None = None,
    ) -> list[ContentOpportunity]:
        self._project_service.get_project(project_id)
        opportunities = self._opportunities.list_content_opportunities(project_id)
        return opportunities if status is None else [item for item in opportunities if item.status == status]

    def get_content_opportunity(self, project_id: str, content_opportunity_id: str) -> ContentOpportunity:
        self._project_service.get_project(project_id)
        return self._opportunities.load_content_opportunity(project_id, content_opportunity_id)

    def approve_content_opportunity(self, project_id: str, content_opportunity_id: str) -> ContentOpportunity:
        return self._transition_opportunity(project_id, content_opportunity_id, ContentOpportunityStatus.APPROVED)

    def reject_content_opportunity(self, project_id: str, content_opportunity_id: str) -> ContentOpportunity:
        return self._transition_opportunity(project_id, content_opportunity_id, ContentOpportunityStatus.REJECTED)

    def defer_content_opportunity(self, project_id: str, content_opportunity_id: str) -> ContentOpportunity:
        return self._transition_opportunity(project_id, content_opportunity_id, ContentOpportunityStatus.DEFERRED)

    def archive_content_opportunity(self, project_id: str, content_opportunity_id: str) -> ContentOpportunity:
        return self._transition_opportunity(project_id, content_opportunity_id, ContentOpportunityStatus.ARCHIVED)

    def create_idea_from_opportunity(self, project_id: str, content_opportunity_id: str) -> Idea:
        opportunity = self.get_content_opportunity(project_id, content_opportunity_id)
        if opportunity.status != ContentOpportunityStatus.APPROVED:
            raise ContentIntelligenceValidationError(
                f"ContentOpportunity '{content_opportunity_id}' must be approved before conversion to Idea"
            )
        if opportunity.idea_id:
            return self._idea_service.get_idea(project_id, opportunity.idea_id)

        description = "\n\n".join(
            part for part in [opportunity.summary, opportunity.recommended_angle, self._format_evidence(opportunity)] if part
        )
        idea = self._idea_service.create_idea(
            project_id,
            title=opportunity.title,
            description=description,
            topic=opportunity.content_pillar or opportunity.strategic_goal or opportunity.title,
            funnel_stage=opportunity.funnel_stage,
            content_format=opportunity.content_format,
            source_type="trend",
            source_id=opportunity.content_opportunity_id,
            priority=self._priority_for_score(opportunity.score),
            tags=["content_intelligence", "opportunity", opportunity.trend_pattern_id],
        )
        converted = opportunity.transition_to(ContentOpportunityStatus.CONVERTED, idea_id=idea.idea_id)
        self._opportunities.save_content_opportunity(converted)
        return idea

    def _transition_opportunity(
        self,
        project_id: str,
        content_opportunity_id: str,
        status: ContentOpportunityStatus,
    ) -> ContentOpportunity:
        opportunity = self.get_content_opportunity(project_id, content_opportunity_id)
        return self._opportunities.save_content_opportunity(opportunity.transition_to(status))

    @staticmethod
    def _require_signal_ids(market_signal_ids: Sequence[str]) -> list[str]:
        signal_ids = [signal_id for signal_id in market_signal_ids if str(signal_id).strip()]
        if not signal_ids:
            raise ContentIntelligenceValidationError("At least one market_signal_id is required")
        return signal_ids

    @staticmethod
    def _priority_for_score(score: float) -> str:
        if score >= 0.8:
            return "high"
        if score <= 0.25:
            return "low"
        return "medium"

    @staticmethod
    def _format_evidence(opportunity: ContentOpportunity) -> str:
        if not opportunity.evidence:
            return ""
        return "Evidence: " + "; ".join(opportunity.evidence)


def build_content_intelligence_service(projects_root: Path | None = None) -> ContentIntelligenceService:
    from core.services.ideas import FileSystemIdeaRepository
    from core.services.projects import FileSystemProjectRepository

    project_repository = FileSystemProjectRepository(projects_root)
    project_service = ProjectService(project_repository)
    idea_service = IdeaService(FileSystemIdeaRepository(projects_root), project_service)
    return ContentIntelligenceService(
        FileSystemMarketSignalRepository(projects_root),
        FileSystemTrendPatternRepository(projects_root),
        FileSystemContentOpportunityRepository(projects_root),
        project_service,
        idea_service,
    )

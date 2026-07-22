from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import (
    BrandProfileStatus,
    ComicBubblePosition,
    ComicSpeaker,
    ContentFormat,
    ContentItemStatus,
    DomainModule,
    MarketSignalStatus,
    TrendPatternStatus,
    ContentOpportunityStatus,
    ExportPackageStatus,
    IdeaStatus,
    MetricSnapshotStatus,
    MetricSourceType,
    OutputFileType,
    ProductionBriefStatus,
    ProjectStatus,
    PublicationMethod,
    PublicationStatus,
    PublishingPlatform,
    RenderJobStatus,
    ScenarioStatus,
    WorkspaceStatus,
)
from .transitions import (
    CONTENT_ITEM_STATUS_TRANSITIONS,
    EXPORT_PACKAGE_STATUS_TRANSITIONS,
    IDEA_STATUS_TRANSITIONS,
    METRIC_SNAPSHOT_STATUS_TRANSITIONS,
    MARKET_SIGNAL_STATUS_TRANSITIONS,
    TREND_PATTERN_STATUS_TRANSITIONS,
    CONTENT_OPPORTUNITY_STATUS_TRANSITIONS,
    PRODUCTION_BRIEF_STATUS_TRANSITIONS,
    PUBLICATION_STATUS_TRANSITIONS,
    RENDER_JOB_STATUS_TRANSITIONS,
    SCENARIO_STATUS_TRANSITIONS,
    validate_status_transition,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def validated_model_copy(instance: BaseModel, **update: Any) -> Any:
    payload = instance.model_dump(mode="python")
    payload.update(update)
    return type(instance).model_validate(payload)


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class TimestampedModel(DomainModel):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ProjectScopedModel(TimestampedModel):
    workspace_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)


class Workspace(TimestampedModel):
    workspace_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE


class Project(TimestampedModel):
    project_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    default_language: str = Field(default="ru", min_length=1)
    status: ProjectStatus = ProjectStatus.ACTIVE


class BrandToneOfVoice(DomainModel):
    tone_summary: str = ""
    style_keywords: list[str] = Field(default_factory=list)
    allowed_phrases: list[str] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(default_factory=list)


class BrandContentRules(DomainModel):
    allowed_topics: list[str] = Field(default_factory=list)
    forbidden_topics: list[str] = Field(default_factory=list)
    writing_rules: list[str] = Field(default_factory=list)
    claim_restrictions: list[str] = Field(default_factory=list)


class BrandProfile(ProjectScopedModel):
    brand_profile_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    positioning: str = ""
    audience_summary: str = ""
    language: str = Field(default="ru", min_length=1)
    brand_values: list[str] = Field(default_factory=list)
    tone_of_voice: BrandToneOfVoice = Field(default_factory=BrandToneOfVoice)
    content_rules: BrandContentRules = Field(default_factory=BrandContentRules)
    status: BrandProfileStatus = BrandProfileStatus.DRAFT


class MarketSignal(ProjectScopedModel):
    market_signal_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.CONTENT_INTELLIGENCE] = DomainModule.CONTENT_INTELLIGENCE
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_type: str = Field(default="manual", min_length=1)
    source_url: str | None = None
    source_reference: str = ""
    observed_at: datetime = Field(default_factory=utc_now)
    audience_hint: str = ""
    platform_hint: str = ""
    content_format_hint: str = ""
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    status: MarketSignalStatus = MarketSignalStatus.NEW

    def transition_to(self, next_status: MarketSignalStatus) -> "MarketSignal":
        validate_status_transition(
            entity_name="MarketSignal",
            current_status=self.status,
            next_status=next_status,
            transitions=MARKET_SIGNAL_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class TrendPattern(ProjectScopedModel):
    trend_pattern_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.CONTENT_INTELLIGENCE] = DomainModule.CONTENT_INTELLIGENCE
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    market_signal_ids: list[str] = Field(default_factory=list, min_length=1)
    affected_audience: str = ""
    related_platforms: list[str] = Field(default_factory=list)
    related_formats: list[str] = Field(default_factory=list)
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    status: TrendPatternStatus = TrendPatternStatus.DRAFT

    def transition_to(self, next_status: TrendPatternStatus) -> "TrendPattern":
        validate_status_transition(
            entity_name="TrendPattern",
            current_status=self.status,
            next_status=next_status,
            transitions=TREND_PATTERN_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class ContentOpportunity(ProjectScopedModel):
    content_opportunity_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.CONTENT_INTELLIGENCE] = DomainModule.CONTENT_INTELLIGENCE
    trend_pattern_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    target_audience: str = ""
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    funnel_stage: str = "attention"
    content_pillar: str = ""
    strategic_goal: str = ""
    recommended_angle: str = ""
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    score: float = Field(default=0.5, ge=0, le=1)
    status: ContentOpportunityStatus = ContentOpportunityStatus.DRAFT
    idea_id: str | None = None

    @model_validator(mode="after")
    def validate_converted_idea_id(self) -> "ContentOpportunity":
        if self.status == ContentOpportunityStatus.CONVERTED and not (self.idea_id and self.idea_id.strip()):
            raise ValueError("Converted ContentOpportunity requires a non-empty idea_id")
        return self

    def transition_to(self, next_status: ContentOpportunityStatus, *, idea_id: str | None = None) -> "ContentOpportunity":
        validate_status_transition(
            entity_name="ContentOpportunity",
            current_status=self.status,
            next_status=next_status,
            transitions=CONTENT_OPPORTUNITY_STATUS_TRANSITIONS,
        )
        if next_status == ContentOpportunityStatus.CONVERTED and not (idea_id and idea_id.strip()):
            raise ValueError("ContentOpportunity transition to 'converted' requires a non-empty idea_id")

        update: dict[str, Any] = {"status": next_status, "updated_at": utc_now()}
        if idea_id is not None:
            update["idea_id"] = idea_id.strip()
        return validated_model_copy(self, **update)


class ScenarioTextBlock(DomainModel):
    block_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    role: str = Field(min_length=1)
    text: str = Field(min_length=1)
    platform: PublishingPlatform | None = None
    status: str = "draft"


class Idea(ProjectScopedModel):
    idea_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ""
    topic: str = ""
    funnel_stage: str = "attention"
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    source_type: str = "manual"
    source_id: str = ""
    priority: str = "medium"
    tags: list[str] = Field(default_factory=list)
    status: IdeaStatus = IdeaStatus.RAW

    def transition_to(self, next_status: IdeaStatus) -> "Idea":
        validate_status_transition(
            entity_name="Idea",
            current_status=self.status,
            next_status=next_status,
            transitions=IDEA_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class Scenario(ProjectScopedModel):
    scenario_id: str = Field(min_length=1)
    idea_id: str = Field(min_length=1)
    brand_profile_id: str = Field(min_length=1)
    source_type: str = "idea"
    source_id: str = ""
    title: str = Field(min_length=1)
    draft_text: str = ""
    funnel_stage: str = "attention"
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    target_platforms: list[PublishingPlatform] = Field(default_factory=list)
    blocks: list[ScenarioTextBlock] = Field(default_factory=list)
    caption_drafts: dict[str, str] = Field(default_factory=dict)
    qa_warnings: list[str] = Field(default_factory=list)
    status: ScenarioStatus = ScenarioStatus.DRAFT
    metadata: dict[str, Any] = Field(default_factory=dict)

    def transition_to(self, next_status: ScenarioStatus) -> "Scenario":
        validate_status_transition(
            entity_name="Scenario",
            current_status=self.status,
            next_status=next_status,
            transitions=SCENARIO_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class RenderJob(ProjectScopedModel):
    render_job_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.PRODUCTION_ENGINE] = DomainModule.PRODUCTION_ENGINE
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    status: RenderJobStatus = RenderJobStatus.QUEUED
    input_snapshot: dict[str, Any] = Field(default_factory=dict)

    def transition_to(self, next_status: RenderJobStatus) -> "RenderJob":
        validate_status_transition(
            entity_name="RenderJob",
            current_status=self.status,
            next_status=next_status,
            transitions=RENDER_JOB_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class OutputFile(ProjectScopedModel):
    output_file_id: str = Field(min_length=1)
    render_job_id: str = Field(min_length=1)
    content_item_id: str | None = None
    owner_module: Literal[DomainModule.PRODUCTION_ENGINE] = DomainModule.PRODUCTION_ENGINE
    file_type: OutputFileType
    path: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    size_bytes: int | None = Field(default=None, ge=0)


class ContentItem(ProjectScopedModel):
    content_item_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    brand_profile_id: str = Field(min_length=1)
    render_job_id: str | None = None
    owner_module: Literal[DomainModule.PRODUCTION_ENGINE] = DomainModule.PRODUCTION_ENGINE
    title: str = Field(min_length=1)
    body: str = ""
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    status: ContentItemStatus = ContentItemStatus.DRAFT
    technical_qa_passed: bool | None = None
    render_output_metadata: dict[str, Any] = Field(default_factory=dict)

    def transition_to(self, next_status: ContentItemStatus) -> "ContentItem":
        validate_status_transition(
            entity_name="ContentItem",
            current_status=self.status,
            next_status=next_status,
            transitions=CONTENT_ITEM_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class ExportPackage(ProjectScopedModel):
    export_package_id: str = Field(min_length=1)
    content_item_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.PUBLISHING_HUB] = DomainModule.PUBLISHING_HUB
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    target_platform: PublishingPlatform
    package_files: list[str] = Field(default_factory=list)
    caption_variants: dict[str, str] = Field(default_factory=dict)
    publication_notes: str = ""
    status: ExportPackageStatus = ExportPackageStatus.DRAFT

    def transition_to(self, next_status: ExportPackageStatus) -> "ExportPackage":
        validate_status_transition(
            entity_name="ExportPackage",
            current_status=self.status,
            next_status=next_status,
            transitions=EXPORT_PACKAGE_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class Publication(ProjectScopedModel):
    publication_id: str = Field(min_length=1)
    content_item_id: str = Field(min_length=1)
    export_package_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.PUBLISHING_HUB] = DomainModule.PUBLISHING_HUB
    platform: PublishingPlatform
    publication_method: Literal[PublicationMethod.MANUAL] = PublicationMethod.MANUAL
    status: PublicationStatus = PublicationStatus.PLANNED
    published_at: datetime | None = None
    published_url: str | None = None
    notes: str = ""

    @model_validator(mode="after")
    def validate_published_state(self) -> "Publication":
        if self.status == PublicationStatus.PUBLISHED:
            if not self.published_at:
                raise ValueError("Published publication requires published_at")
            if not self.published_url:
                raise ValueError("Published publication requires published_url")
        return self

    def transition_to(
        self,
        next_status: PublicationStatus,
        *,
        published_at: datetime | None = None,
        published_url: str | None = None,
    ) -> "Publication":
        validate_status_transition(
            entity_name="Publication",
            current_status=self.status,
            next_status=next_status,
            transitions=PUBLICATION_STATUS_TRANSITIONS,
        )
        update: dict[str, Any] = {"status": next_status, "updated_at": utc_now()}
        if next_status == PublicationStatus.PUBLISHED:
            update["published_at"] = published_at or utc_now()
            update["published_url"] = published_url
        return validated_model_copy(self, **update)


class ContentPerformanceMetrics(DomainModel):
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    profile_visits: int = Field(default=0, ge=0)
    link_clicks: int = Field(default=0, ge=0)


class MetricSnapshot(ProjectScopedModel):
    metric_snapshot_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    content_item_id: str = Field(min_length=1)
    owner_module: Literal[DomainModule.ANALYTICS] = DomainModule.ANALYTICS
    platform: PublishingPlatform
    source_type: MetricSourceType = MetricSourceType.MANUAL
    captured_at: datetime = Field(default_factory=utc_now)
    content_metrics: ContentPerformanceMetrics = Field(default_factory=ContentPerformanceMetrics)
    status: MetricSnapshotStatus = MetricSnapshotStatus.DRAFT

    def transition_to(self, next_status: MetricSnapshotStatus) -> "MetricSnapshot":
        validate_status_transition(
            entity_name="MetricSnapshot",
            current_status=self.status,
            next_status=next_status,
            transitions=METRIC_SNAPSHOT_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())


class ProductionSceneImageAnimation(DomainModel):
    type: str = "slow_zoom"
    from_scale: float = Field(default=1.0, ge=1.0, le=2.0)
    to_scale: float = Field(default=1.08, ge=1.0, le=2.0)
    easing: str = "cubic-in-out"
    pan_x_enabled: bool = False
    pan_y_enabled: bool = False


class SceneTextOverlay(DomainModel):
    text: str = Field(min_length=1)
    start_sec: float = Field(ge=0.0)
    duration_sec: float = Field(ge=0.0)
    font_size: int = Field(default=48, ge=8, le=200)
    color: str = "#FFFFFF"
    y_position: float = Field(default=0.15, ge=0.0, le=1.0)
    phase: str = "single"


class ComicTailAnchor(DomainModel):
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class ComicOverlay(DomainModel):
    speaker: ComicSpeaker
    text: str = Field(min_length=1)
    position: ComicBubblePosition
    tail_anchor: ComicTailAnchor

    @field_validator("text")
    @classmethod
    def text_must_contain_visible_characters(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Comic overlay text must contain visible characters")
        return value


class ProductionScene(DomainModel):
    scene_id: str = ""
    index: int = Field(ge=0)
    purpose: str = "main"
    image_source: str = Field(min_length=1)
    duration_sec: float = Field(gt=0.0)
    narration_text: str = ""
    animation: ProductionSceneImageAnimation = Field(default_factory=ProductionSceneImageAnimation)
    text_overlay: SceneTextOverlay | None = None
    comic_overlay: ComicOverlay | None = None
    transition_type: str = "dissolve"
    transition_duration: float = Field(default=0.5, ge=0.0)


class ProductionAudio(DomainModel):
    voiceover_path: str = ""
    music_path: str = ""
    music_volume: float = Field(default=0.15, ge=0.0, le=1.0)
    ducking_enabled: bool = True
    ducking_reduction_db: int = Field(default=12, ge=0, le=30)
    voiceover_enabled: bool = False
    tts_provider: str | None = None
    tts_profile: str | None = None
    tts_text: str | None = None


class ProductionSubtitles(DomainModel):
    enabled: bool = True
    mode: str = "manual"
    font_path: str = ""
    font_size: int = Field(default=50, ge=8, le=200)
    color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: float = Field(default=3.0, ge=0.0, le=10.0)
    y_position: float = Field(default=0.7, ge=0.0, le=1.0)


class ProductionOutput(DomainModel):
    aspect_ratio: str = "9:16"
    resolution_width: int = 1080
    resolution_height: int = 1920
    fps: int = 24
    output_format: str = "mp4"
    duration_sec: float | None = None
    slide_count: int | None = None
    generate_srt: bool = True
    generate_cover: bool = True
    generate_audio_only: bool = True
    generate_preview: bool = False
    generate_comic_master_video: bool = False


class ProductionBrand(DomainModel):
    logo_path: str = ""
    logo_position: str = "top-right"
    website_text: str = ""
    website_start_sec: float = 0.0
    website_duration_sec: float = 0.0
    watermark_enabled: bool = False
    colors_primary: str = ""
    colors_accent: str = ""
    colors_background_dark: str = ""
    colors_text_light: str = ""
    colors_text_muted: str = ""
    fonts_heading: str = ""
    fonts_body: str = ""
    gradient_css: str = ""


class ProductionQA(DomainModel):
    check_resolution: bool = True
    check_duration: bool = True
    check_audio: bool = True
    check_subtitles: bool = True
    check_slide_count: bool = False
    safe_zone_top: int = 120
    safe_zone_bottom: int = 200
    safe_zone_left: int = 60
    safe_zone_right: int = 60


class ProductionSlide(DomainModel):
    slide_number: int = Field(ge=1, le=10)
    template: str = "cover"
    heading: str = ""
    subheading: str = ""
    body: str = ""
    list_items: list[str] = Field(default_factory=list)
    cta: str = ""
    visual_hint: str = ""
    background: str = "bg_gradient_dark"
    brand_element: str = ""
    tone: str = ""


class ProductionBrief(ProjectScopedModel):
    schema_version: Literal[1] = 1
    title: str = ""
    production_brief_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    production_variant: str = ""
    target_platforms: list[PublishingPlatform] = Field(default_factory=list)
    scenes: list[ProductionScene] = Field(default_factory=list)
    audio: ProductionAudio = Field(default_factory=ProductionAudio)
    subtitles: ProductionSubtitles = Field(default_factory=ProductionSubtitles)
    output: ProductionOutput = Field(default_factory=ProductionOutput)
    brand: ProductionBrand = Field(default_factory=ProductionBrand)
    slides: list[ProductionSlide] = Field(default_factory=list)
    qa: ProductionQA = Field(default_factory=ProductionQA)
    status: ProductionBriefStatus = ProductionBriefStatus.DRAFT

    @model_validator(mode="after")
    def validate_dialog_miniseries_comic_scenes(self) -> "ProductionBrief":
        if self.content_format != ContentFormat.DIALOG_MINISERIES:
            return self
        if not self.scenes:
            raise ValueError("Dialog miniseries requires at least one production scene")
        if not self.subtitles.font_path.strip():
            raise ValueError("Dialog miniseries requires a comic font path")
        if any(scene.comic_overlay is None for scene in self.scenes):
            raise ValueError("Every dialog miniseries scene requires a comic overlay")
        indexes = [scene.index for scene in self.scenes]
        if indexes != sorted(indexes) or len(set(indexes)) != len(indexes):
            raise ValueError("Dialog miniseries scene indexes must be unique and ordered")
        scene_ids = [scene.scene_id.strip() for scene in self.scenes if scene.scene_id.strip()]
        if scene_ids and (
            len(scene_ids) != len(self.scenes) or len(set(scene_ids)) != len(scene_ids)
        ):
            raise ValueError(
                "Dialog miniseries scene IDs must be present for every scene and unique"
            )
        return self

    def transition_to(self, next_status: ProductionBriefStatus) -> "ProductionBrief":
        validate_status_transition(
            entity_name="ProductionBrief",
            current_status=self.status,
            next_status=next_status,
            transitions=PRODUCTION_BRIEF_STATUS_TRANSITIONS,
        )
        return validated_model_copy(self, status=next_status, updated_at=utc_now())

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import (
    BrandProfileStatus,
    ContentFormat,
    ContentItemStatus,
    DomainModule,
    ExportPackageStatus,
    IdeaStatus,
    MetricSnapshotStatus,
    MetricSourceType,
    OutputFileType,
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


class Idea(ProjectScopedModel):
    idea_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ""
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
    source_type: str = "manual"
    status: IdeaStatus = IdeaStatus.DRAFT

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
    title: str = Field(min_length=1)
    draft_text: str = ""
    content_format: ContentFormat = ContentFormat.TEXT_SOCIAL_POST
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

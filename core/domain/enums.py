from __future__ import annotations

from enum import StrEnum


class DomainModule(StrEnum):
    PRODUCTION_ENGINE = "production_engine"
    PUBLISHING_HUB = "publishing_hub"
    ANALYTICS = "analytics"
    CONTENT_INTELLIGENCE = "content_intelligence"


class WorkspaceStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class BrandProfileStatus(StrEnum):
    DRAFT = "draft"
    INCOMPLETE = "incomplete"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentFormat(StrEnum):
    TEXT_SOCIAL_POST = "text_social_post"
    DIALOG_MINISERIES = "dialog_miniseries"
    SHORT_VERTICAL_VIDEO = "short_vertical_video"
    AMBIENT_VERTICAL_VIDEO = "ambient_vertical_video"
    INSTAGRAM_CAROUSEL = "instagram_carousel"


class ComicSpeaker(StrEnum):
    NURA = "nura"
    WOMAN = "woman"
    SHADOW = "shadow"


class ComicBubblePosition(StrEnum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class PublishingPlatform(StrEnum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TELEGRAM = "telegram"
    VK = "vk"
    THREADS = "threads"
    YOUTUBE_SHORTS = "youtube_shorts"
    PINTEREST = "pinterest"


class PublicationMethod(StrEnum):
    MANUAL = "manual"


class MetricSourceType(StrEnum):
    MANUAL = "manual"


class OutputFileType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CAPTION = "caption"
    METADATA = "metadata"
    ZIP = "zip"
    OTHER = "other"


class RenderJobStatus(StrEnum):
    QUEUED = "queued"
    VALIDATING = "validating"
    RENDERING = "rendering"
    RENDERED = "rendered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class IdeaStatus(StrEnum):
    RAW = "raw"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCRIPTED = "scripted"
    ARCHIVED = "archived"


class ScenarioStatus(StrEnum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ContentItemStatus(StrEnum):
    DRAFT = "draft"
    IN_PRODUCTION = "in_production"
    RENDERED = "rendered"
    QA_FAILED = "qa_failed"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPORTED = "exported"
    ARCHIVED = "archived"


class ExportPackageStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"


class PublicationStatus(StrEnum):
    PLANNED = "planned"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class MetricSnapshotStatus(StrEnum):
    DRAFT = "draft"
    RECORDED = "recorded"
    INVALID = "invalid"


class MarketSignalStatus(StrEnum):
    NEW = "new"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class TrendPatternStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentOpportunityStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    CONVERTED = "converted"
    ARCHIVED = "archived"


class ProductionBriefStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

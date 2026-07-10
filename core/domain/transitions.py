from __future__ import annotations

from collections.abc import Mapping, Set
from enum import Enum

from .enums import (
    ContentItemStatus,
    ExportPackageStatus,
    IdeaStatus,
    MetricSnapshotStatus,
    MarketSignalStatus,
    TrendPatternStatus,
    ContentOpportunityStatus,
    PublicationStatus,
    RenderJobStatus,
    ScenarioStatus,
)


class InvalidStatusTransitionError(ValueError):
    """Raised when an entity attempts an unsupported status transition."""


TransitionMap = Mapping[Enum, Set[Enum]]


IDEA_STATUS_TRANSITIONS: dict[IdeaStatus, set[IdeaStatus]] = {
    IdeaStatus.RAW: {
        IdeaStatus.APPROVED,
        IdeaStatus.REJECTED,
        IdeaStatus.ARCHIVED,
    },
    IdeaStatus.APPROVED: {IdeaStatus.SCRIPTED, IdeaStatus.ARCHIVED},
    IdeaStatus.REJECTED: {IdeaStatus.ARCHIVED},
    IdeaStatus.SCRIPTED: {IdeaStatus.ARCHIVED},
    IdeaStatus.ARCHIVED: set(),
}


SCENARIO_STATUS_TRANSITIONS: dict[ScenarioStatus, set[ScenarioStatus]] = {
    ScenarioStatus.DRAFT: {ScenarioStatus.NEEDS_REVIEW, ScenarioStatus.ARCHIVED},
    ScenarioStatus.NEEDS_REVIEW: {
        ScenarioStatus.APPROVED,
        ScenarioStatus.REJECTED,
        ScenarioStatus.ARCHIVED,
    },
    ScenarioStatus.APPROVED: {ScenarioStatus.ARCHIVED},
    ScenarioStatus.REJECTED: {ScenarioStatus.DRAFT, ScenarioStatus.ARCHIVED},
    ScenarioStatus.ARCHIVED: set(),
}


RENDER_JOB_STATUS_TRANSITIONS: dict[RenderJobStatus, set[RenderJobStatus]] = {
    RenderJobStatus.QUEUED: {
        RenderJobStatus.VALIDATING,
        RenderJobStatus.CANCELLED,
        RenderJobStatus.ARCHIVED,
    },
    RenderJobStatus.VALIDATING: {
        RenderJobStatus.RENDERING,
        RenderJobStatus.FAILED,
        RenderJobStatus.CANCELLED,
        RenderJobStatus.ARCHIVED,
    },
    RenderJobStatus.RENDERING: {
        RenderJobStatus.RENDERED,
        RenderJobStatus.FAILED,
        RenderJobStatus.CANCELLED,
        RenderJobStatus.ARCHIVED,
    },
    RenderJobStatus.RENDERED: {RenderJobStatus.ARCHIVED},
    RenderJobStatus.FAILED: {RenderJobStatus.QUEUED, RenderJobStatus.ARCHIVED},
    RenderJobStatus.CANCELLED: {RenderJobStatus.ARCHIVED},
    RenderJobStatus.ARCHIVED: set(),
}


CONTENT_ITEM_STATUS_TRANSITIONS: dict[ContentItemStatus, set[ContentItemStatus]] = {
    ContentItemStatus.DRAFT: {
        ContentItemStatus.IN_PRODUCTION,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.IN_PRODUCTION: {
        ContentItemStatus.RENDERED,
        ContentItemStatus.QA_FAILED,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.RENDERED: {
        ContentItemStatus.NEEDS_REVIEW,
        ContentItemStatus.QA_FAILED,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.QA_FAILED: {
        ContentItemStatus.IN_PRODUCTION,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.NEEDS_REVIEW: {
        ContentItemStatus.APPROVED,
        ContentItemStatus.REJECTED,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.APPROVED: {
        ContentItemStatus.EXPORTED,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.REJECTED: {
        ContentItemStatus.NEEDS_REVIEW,
        ContentItemStatus.ARCHIVED,
    },
    ContentItemStatus.EXPORTED: {ContentItemStatus.ARCHIVED},
    ContentItemStatus.ARCHIVED: set(),
}


EXPORT_PACKAGE_STATUS_TRANSITIONS: dict[ExportPackageStatus, set[ExportPackageStatus]] = {
    ExportPackageStatus.DRAFT: {
        ExportPackageStatus.READY,
        ExportPackageStatus.FAILED,
        ExportPackageStatus.ARCHIVED,
    },
    ExportPackageStatus.READY: {ExportPackageStatus.ARCHIVED},
    ExportPackageStatus.FAILED: {
        ExportPackageStatus.DRAFT,
        ExportPackageStatus.ARCHIVED,
    },
    ExportPackageStatus.ARCHIVED: set(),
}


PUBLICATION_STATUS_TRANSITIONS: dict[PublicationStatus, set[PublicationStatus]] = {
    PublicationStatus.PLANNED: {
        PublicationStatus.PUBLISHED,
        PublicationStatus.FAILED,
        PublicationStatus.ARCHIVED,
    },
    PublicationStatus.PUBLISHED: {PublicationStatus.ARCHIVED},
    PublicationStatus.FAILED: {
        PublicationStatus.PLANNED,
        PublicationStatus.ARCHIVED,
    },
    PublicationStatus.ARCHIVED: set(),
}


METRIC_SNAPSHOT_STATUS_TRANSITIONS: dict[MetricSnapshotStatus, set[MetricSnapshotStatus]] = {
    MetricSnapshotStatus.DRAFT: {
        MetricSnapshotStatus.RECORDED,
        MetricSnapshotStatus.INVALID,
    },
    MetricSnapshotStatus.RECORDED: {MetricSnapshotStatus.INVALID},
    MetricSnapshotStatus.INVALID: {MetricSnapshotStatus.DRAFT},
}


MARKET_SIGNAL_STATUS_TRANSITIONS: dict[MarketSignalStatus, set[MarketSignalStatus]] = {
    MarketSignalStatus.NEW: {MarketSignalStatus.REVIEWED, MarketSignalStatus.ARCHIVED},
    MarketSignalStatus.REVIEWED: {MarketSignalStatus.ARCHIVED},
    MarketSignalStatus.ARCHIVED: set(),
}

TREND_PATTERN_STATUS_TRANSITIONS: dict[TrendPatternStatus, set[TrendPatternStatus]] = {
    TrendPatternStatus.DRAFT: {TrendPatternStatus.ACTIVE, TrendPatternStatus.ARCHIVED},
    TrendPatternStatus.ACTIVE: {TrendPatternStatus.ARCHIVED},
    TrendPatternStatus.ARCHIVED: set(),
}

CONTENT_OPPORTUNITY_STATUS_TRANSITIONS: dict[ContentOpportunityStatus, set[ContentOpportunityStatus]] = {
    ContentOpportunityStatus.DRAFT: {
        ContentOpportunityStatus.APPROVED,
        ContentOpportunityStatus.REJECTED,
        ContentOpportunityStatus.DEFERRED,
        ContentOpportunityStatus.ARCHIVED,
    },
    ContentOpportunityStatus.APPROVED: {
        ContentOpportunityStatus.CONVERTED,
        ContentOpportunityStatus.DEFERRED,
        ContentOpportunityStatus.ARCHIVED,
    },
    ContentOpportunityStatus.REJECTED: {ContentOpportunityStatus.ARCHIVED},
    ContentOpportunityStatus.DEFERRED: {ContentOpportunityStatus.APPROVED, ContentOpportunityStatus.ARCHIVED},
    ContentOpportunityStatus.CONVERTED: {ContentOpportunityStatus.ARCHIVED},
    ContentOpportunityStatus.ARCHIVED: set(),
}


def validate_status_transition(
    *,
    entity_name: str,
    current_status: Enum,
    next_status: Enum,
    transitions: TransitionMap,
) -> None:
    if type(current_status) is not type(next_status):
        raise TypeError(
            f"{entity_name} status transition must use the same enum type: "
            f"{type(current_status).__name__} -> {type(next_status).__name__}"
        )

    allowed_statuses = transitions.get(current_status, set())
    if next_status not in allowed_statuses:
        allowed = ", ".join(status.value for status in sorted(allowed_statuses, key=lambda item: item.value))
        raise InvalidStatusTransitionError(
            f"{entity_name} cannot transition from '{current_status.value}' to "
            f"'{next_status.value}'. Allowed: [{allowed}]"
        )


def can_transition(
    *,
    current_status: Enum,
    next_status: Enum,
    transitions: TransitionMap,
) -> bool:
    return next_status in transitions.get(current_status, set())

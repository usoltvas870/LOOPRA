"""Canonical, immutable TOP-20 selection snapshots for Trend Radar runs."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from run_data import evidence_path, utc_iso


SCHEMA_VERSION = "1.0"
MANIFEST_TYPE = "trend_radar_content_intelligence_selection"
REQUESTED_CANDIDATE_COUNT = 20


class SelectionManifestError(ValueError):
    """Raised when a selection snapshot is malformed or conflicts on disk."""


@dataclass(frozen=True)
class CandidateSelectionEntry:
    rank: int
    video_id: str
    author: str | None
    source: dict[str, Any]
    canonical_url: str | None
    caption: str | None
    metrics_snapshot: dict[str, Any]
    score_snapshot: dict[str, Any]
    classification: str | None
    radar_confidence: str | None
    identity_confidence: str | None
    provenance_references: dict[str, Any] | None
    source_artifact_references: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class ContentIntelligenceSelectionManifest:
    schema_version: str
    manifest_type: str
    manifest_id: str
    created_at: str
    radar_run_id: str
    radar_run_reference: str
    ranking_source: str
    ranking_contract_version: str
    requested_candidate_count: int
    selected_candidate_count: int
    selection_complete: bool
    selection_status: str
    selection_reason: str | None
    candidates: list[CandidateSelectionEntry]
    source_artifacts: list[str]
    manifest_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_selection_manifest(
    ranked_candidates: Sequence[dict[str, Any]],
    *,
    radar_run_id: str,
    created_at: str | None = None,
) -> ContentIntelligenceSelectionManifest:
    """Snapshot the supplied ranking without scoring, sorting, or filtering it."""
    if not radar_run_id:
        raise SelectionManifestError("radar_run_id is required")

    selected = list(ranked_candidates[:REQUESTED_CANDIDATE_COUNT])
    video_ids = [candidate.get("video_id") for candidate in selected]
    if any(not video_id for video_id in video_ids):
        raise SelectionManifestError("ranked candidates must have video_id values")
    if len(set(video_ids)) != len(video_ids):
        raise SelectionManifestError("ranked candidates must have unique video_id values")

    entries = [
        _entry_from_candidate(candidate, rank, radar_run_id)
        for rank, candidate in enumerate(selected, 1)
    ]
    selection_complete = len(selected) == REQUESTED_CANDIDATE_COUNT
    payload = {
        "schema_version": SCHEMA_VERSION,
        "manifest_type": MANIFEST_TYPE,
        "radar_run_id": radar_run_id,
        "radar_run_reference": _journal_reference(radar_run_id),
        "ranking_source": "trend_radar.compute_scores",
        "ranking_contract_version": "1",
        "requested_candidate_count": REQUESTED_CANDIDATE_COUNT,
        "selected_candidate_count": len(entries),
        "selection_complete": selection_complete,
        "selection_status": "complete" if selection_complete else "incomplete",
        "selection_reason": None if selection_complete else "fewer_ranked_candidates_than_requested",
        "candidates": [asdict(entry) for entry in entries],
        "source_artifacts": [_journal_reference(radar_run_id)],
    }
    manifest_hash = _content_hash(payload)
    manifest_payload = {key: value for key, value in payload.items() if key != "candidates"}
    return ContentIntelligenceSelectionManifest(
        manifest_id=f"trend-radar-selection-{radar_run_id}-{manifest_hash[:12]}",
        created_at=created_at or utc_iso(datetime.now(timezone.utc)),
        manifest_hash=manifest_hash,
        candidates=entries,
        **manifest_payload,
    )


def selection_manifest_path(radar_run_id: str, root: Path | None = None) -> Path:
    """Return the ignored, run-scoped runtime path for one selection manifest."""
    if not radar_run_id:
        raise SelectionManifestError("radar_run_id is required")
    base = root if root is not None else evidence_path(radar_run_id).parent
    return base / f"selection_manifest_{radar_run_id}.json"


def write_selection_manifest(
    manifest: ContentIntelligenceSelectionManifest, root: Path | None = None
) -> Path:
    """Atomically persist a manifest, allowing only content-identical retries."""
    validate_selection_manifest(manifest.to_dict())
    path = selection_manifest_path(manifest.radar_run_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = read_selection_manifest(path)
        if existing.manifest_hash != manifest.manifest_hash:
            raise SelectionManifestError(
                f"selection manifest conflict for Radar run {manifest.radar_run_id}"
            )
        return path

    serialized = _serialize(manifest.to_dict())
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp"
    ) as temporary:
        temporary.write(serialized)
        temporary_path = Path(temporary.name)
    try:
        os.link(temporary_path, path)
    except FileExistsError:
        existing = read_selection_manifest(path)
        if existing.manifest_hash != manifest.manifest_hash:
            raise SelectionManifestError(
                f"selection manifest conflict for Radar run {manifest.radar_run_id}"
            )
    finally:
        temporary_path.unlink(missing_ok=True)
    return path


def read_selection_manifest(path: Path) -> ContentIntelligenceSelectionManifest:
    """Read and validate a machine-readable selection manifest."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SelectionManifestError(f"cannot read selection manifest: {path}") from error
    validate_selection_manifest(payload)
    candidates = [CandidateSelectionEntry(**candidate) for candidate in payload.pop("candidates")]
    return ContentIntelligenceSelectionManifest(candidates=candidates, **payload)


def validate_selection_manifest(payload: dict[str, Any]) -> None:
    """Validate structural, count, uniqueness, and deterministic-hash invariants."""
    required = {
        "schema_version", "manifest_type", "manifest_id", "created_at", "radar_run_id",
        "radar_run_reference", "ranking_source", "ranking_contract_version",
        "requested_candidate_count", "selected_candidate_count", "selection_complete",
        "selection_status", "selection_reason", "candidates", "source_artifacts", "manifest_hash",
    }
    missing = required - payload.keys()
    if missing:
        raise SelectionManifestError(f"selection manifest missing fields: {sorted(missing)}")
    if payload["schema_version"] != SCHEMA_VERSION or payload["manifest_type"] != MANIFEST_TYPE:
        raise SelectionManifestError("unsupported selection manifest schema")
    candidates = payload["candidates"]
    if not isinstance(candidates, list) or payload["requested_candidate_count"] != REQUESTED_CANDIDATE_COUNT:
        raise SelectionManifestError("invalid selection manifest candidate counts")
    if payload["selected_candidate_count"] != len(candidates) or len(candidates) > REQUESTED_CANDIDATE_COUNT:
        raise SelectionManifestError("selection manifest count invariant failed")
    expected_complete = len(candidates) == REQUESTED_CANDIDATE_COUNT
    if payload["selection_complete"] != expected_complete:
        raise SelectionManifestError("selection completeness invariant failed")
    if payload["selection_status"] != ("complete" if expected_complete else "incomplete"):
        raise SelectionManifestError("selection status invariant failed")
    video_ids = [candidate.get("video_id") for candidate in candidates]
    if any(not video_id for video_id in video_ids) or len(set(video_ids)) != len(video_ids):
        raise SelectionManifestError("selection manifest video IDs must be unique")
    if [candidate.get("rank") for candidate in candidates] != list(range(1, len(candidates) + 1)):
        raise SelectionManifestError("selection manifest ranks must be contiguous")
    content = {key: value for key, value in payload.items() if key not in {"manifest_id", "created_at", "manifest_hash"}}
    if payload["manifest_hash"] != _content_hash(content):
        raise SelectionManifestError("selection manifest content hash mismatch")


def _entry_from_candidate(
    candidate: dict[str, Any], rank: int, radar_run_id: str
) -> CandidateSelectionEntry:
    warnings = []
    if candidate.get("missing_fields"):
        warnings.append("incomplete_platform_metrics")
    if not candidate.get("url"):
        warnings.append("missing_canonical_url")
    return CandidateSelectionEntry(
        rank=rank,
        video_id=str(candidate["video_id"]),
        author=candidate.get("author_username"),
        source={
            "type": candidate.get("source_type"),
            "value": candidate.get("source_value"),
            "endpoint": candidate.get("identity_source_endpoint"),
        },
        canonical_url=candidate.get("url"),
        caption=candidate.get("caption"),
        metrics_snapshot={key: candidate.get(key) for key in (
            "views", "likes", "comments", "shares", "author_followers", "published_at", "collected_at"
        )},
        score_snapshot={key: candidate.get(key) for key in (
            "final_score", "reach_score", "engagement_score", "freshness_score", "momentum_proxy",
            "like_rate", "comment_rate", "share_rate", "total_engagement_rate", "score_breakdown"
        )},
        classification=candidate.get("classification"),
        radar_confidence=candidate.get("data_confidence"),
        identity_confidence=candidate.get("identity_confidence"),
        provenance_references=_provenance(candidate.get("provenance")),
        source_artifact_references=[_journal_reference(radar_run_id)],
        warnings=warnings,
    )


def _provenance(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return {key: value.get(key) for key in (
        "primary_source_type", "primary_source_value", "first_discovery_ordinal", "matched_sources",
        "discovery_methods", "repeat_discoveries", "new_to_database"
    )}


def _journal_reference(radar_run_id: str) -> str:
    return f"data/runs/run_{radar_run_id}.json"


def _content_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_serialize(payload).encode("utf-8")).hexdigest()


def _serialize(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

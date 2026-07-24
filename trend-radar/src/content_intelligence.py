"""Offline Stage 5A Content Intelligence contracts.

This module deliberately consumes only already persisted, manifest-bound
evidence.  It contains no HTTP client, browser integration, secret lookup, or
production prompt.  A future provider must implement ``AnalysisProvider`` and
pass the same validation gate as the deterministic fake below.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from selection_manifest import read_selection_manifest
from evidence_resolution import EvidenceResolutionError, resolve_candidate_evidence


INPUT_SCHEMA_VERSION = "0.1"
CARD_SCHEMA_VERSION = "0.1"
PROVIDER_RESULT_SCHEMA_VERSION = "0.1"
BUILDER_VERSION = "0.2"
MAX_OCR_EVENTS = 12
MAX_TRANSCRIPT_SEGMENTS = 12
MAX_FRAME_REFS = 12
MAX_TEXT_CHARS = 240


class ContentIntelligenceError(ValueError):
    """Raised when offline Content Intelligence contracts are violated."""


class ClaimType(StrEnum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    AI_INTERPRETATION = "AI_INTERPRETATION"


class AnalysisStatus(StrEnum):
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    REUSED = "REUSED"


@dataclass(frozen=True)
class ProjectAnalysisContext:
    """Generic project adapter input; brand semantics remain outside the core."""

    project_id: str
    context_version: str
    target_audience_context: str | None = None
    requested_adaptation_fields: tuple[str, ...] = ()
    project_context_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "context_version": self.context_version,
            "target_audience_context": self.target_audience_context,
            "requested_adaptation_fields": list(self.requested_adaptation_fields),
            "project_context_ref": self.project_context_ref,
        }


class AnalysisProvider(Protocol):
    provider_id: str
    provider_version: str
    model_id: str
    configuration: dict[str, Any]

    def analyze(self, analysis_input: dict[str, Any]) -> dict[str, Any]: ...


def hash_payload(payload: Any) -> str:
    return hashlib.sha256(_serialize(payload).encode("utf-8")).hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_analysis_input(
    manifest_path: Path,
    candidate_id: str,
    *,
    acquisition_root: Path,
    inspection_root: Path,
    intelligence_evidence_root: Path,
    project_context: ProjectAnalysisContext,
) -> dict[str, Any]:
    """Build a bounded, deterministic, candidate-scoped input from local evidence."""
    manifest = read_selection_manifest(manifest_path)
    candidate = next((item for item in manifest.candidates if item.video_id == candidate_id), None)
    if candidate is None:
        raise ContentIntelligenceError("candidate is not present in the canonical selection manifest")
    if not project_context.project_id or not project_context.context_version:
        raise ContentIntelligenceError("project context identity is required")

    try:
        resolved = resolve_candidate_evidence(candidate=candidate, manifest_hash=manifest.manifest_hash,
            acquisition_root=acquisition_root, inspection_root=inspection_root,
            intelligence_root=intelligence_evidence_root)
    except EvidenceResolutionError as error:
        raise ContentIntelligenceError(str(error)) from error
    evidence, missing = resolved.evidence, list(resolved.missing)
    index = _build_evidence_index(candidate.video_id, evidence)
    payload = {
        "schema_version": INPUT_SCHEMA_VERSION,
        "builder_version": BUILDER_VERSION,
        "analysis_kind": "content_intelligence",
        "candidate_identity": {
            "video_id": candidate.video_id, "rank": candidate.rank,
            "canonical_url": candidate.canonical_url,
            "classification": candidate.classification,
            "metrics_snapshot": candidate.metrics_snapshot,
            "score_snapshot": candidate.score_snapshot,
        },
        "selection_manifest": {
            "reference": _portable(manifest_path, manifest_path.parent.parent),
            "sha256": hash_file(manifest_path), "manifest_hash": manifest.manifest_hash,
            "radar_run_id": manifest.radar_run_id,
        },
        "project_context": project_context.to_dict(),
        "project_context_hash": hash_payload(project_context.to_dict()),
        "evidence": evidence,
        "evidence_index": index,
        "missing_evidence": missing,
        "evidence_diagnostics": list(resolved.diagnostics),
        "input_limits": {"ocr_events": MAX_OCR_EVENTS, "transcript_segments": MAX_TRANSCRIPT_SEGMENTS, "frame_refs": MAX_FRAME_REFS, "text_chars_per_item": MAX_TEXT_CHARS},
    }
    payload["input_hash"] = hash_payload(payload)
    return payload


class FakeDeterministicProvider:
    """Offline test provider.  It never reads environment or performs I/O."""

    provider_id = "fake-deterministic"
    provider_version = "0.1"
    model_id = "fake-content-intelligence-v0"
    configuration = {"mode": "offline", "network": "disabled", "test_only": True}

    def analyze(self, analysis_input: dict[str, Any]) -> dict[str, Any]:
        identity = analysis_input["candidate_identity"]
        refs = analysis_input["evidence_index"]
        hook_ref = next((item["ref_id"] for item in refs if item["kind"] in {"ocr_first_hook", "transcript_first_words"}), None)
        evidence_refs = [hook_ref] if hook_ref else []
        return {
            "schema_version": PROVIDER_RESULT_SCHEMA_VERSION,
            "provider": self.metadata(),
            "candidate_identity": {"video_id": identity["video_id"], "rank": identity["rank"]},
            "claims": [
                {"claim_id": "inference-001", "claim_type": ClaimType.INFERENCE, "field": "evidence_completeness", "text": "Synthetic inference from the available bounded evidence.", "evidence_refs": evidence_refs, "confidence": None},
                {"claim_id": "ai-001", "claim_type": ClaimType.AI_INTERPRETATION, "field": "adaptation", "text": "Synthetic offline adaptation placeholder; not a factual finding.", "evidence_refs": evidence_refs, "confidence": None},
            ],
            "project_adaptation": {field: "synthetic fake value" for field in analysis_input["project_context"]["requested_adaptation_fields"]},
            "warnings": ["fake/test analysis; no external AI provider was called"],
        }

    def metadata(self) -> dict[str, Any]:
        return {"provider_id": self.provider_id, "provider_version": self.provider_version, "model_id": self.model_id, "configuration": self.configuration, "fake": True}


def validate_provider_result(provider_result: dict[str, Any], analysis_input: dict[str, Any], provider: AnalysisProvider) -> dict[str, Any]:
    if provider_result.get("schema_version") != PROVIDER_RESULT_SCHEMA_VERSION:
        raise ContentIntelligenceError("unsupported provider result schema")
    identity = analysis_input["candidate_identity"]
    if provider_result.get("candidate_identity") != {"video_id": identity["video_id"], "rank": identity["rank"]}:
        raise ContentIntelligenceError("provider attempted to mutate candidate identity")
    allowed_refs = {item["ref_id"] for item in analysis_input["evidence_index"]}
    claims = provider_result.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ContentIntelligenceError("provider result must contain claims")
    for claim in claims:
        claim_type = claim.get("claim_type")
        if claim_type == ClaimType.FACT:
            raise ContentIntelligenceError("AI provider cannot emit FACT claims")
        if claim_type not in {ClaimType.INFERENCE, ClaimType.AI_INTERPRETATION}:
            raise ContentIntelligenceError("unsupported claim type")
        refs = claim.get("evidence_refs", [])
        if not isinstance(refs, list) or any(ref not in allowed_refs for ref in refs):
            raise ContentIntelligenceError("claim contains an unknown evidence reference")
        if not isinstance(claim.get("text"), str) or len(claim["text"]) > 1000:
            raise ContentIntelligenceError("claim text is invalid or unbounded")
        if claim.get("confidence") is not None and not _finite(claim["confidence"]):
            raise ContentIntelligenceError("claim confidence must be finite or null")
    metadata = provider_result.get("provider", {})
    if metadata.get("provider_id") != provider.provider_id or metadata.get("model_id") != provider.model_id:
        raise ContentIntelligenceError("provider metadata does not match the active provider")
    return provider_result


def build_card(analysis_input: dict[str, Any], provider_result: dict[str, Any]) -> dict[str, Any]:
    facts = _fact_claims(analysis_input)
    claims = facts + provider_result["claims"]
    card = {
        "schema_version": CARD_SCHEMA_VERSION,
        "candidate_identity": analysis_input["candidate_identity"],
        "input_hash": analysis_input["input_hash"],
        "project_context_hash": analysis_input["project_context_hash"],
        "provider": provider_result["provider"],
        "claims": claims,
        "evidence_index": analysis_input["evidence_index"],
        "missing_evidence": analysis_input["missing_evidence"],
        "project_adaptation": provider_result.get("project_adaptation", {}),
        "status": AnalysisStatus.DEGRADED if analysis_input["missing_evidence"] else AnalysisStatus.COMPLETED,
        "warnings": provider_result.get("warnings", []),
    }
    card["card_hash"] = hash_payload(card)
    return card


def run_fake_analysis(
    manifest_path: Path, *, candidate_ids: tuple[str, ...] = (), limit: int | None = None,
    acquisition_root: Path, inspection_root: Path, intelligence_evidence_root: Path,
    output_root: Path, project_context: ProjectAnalysisContext, reuse: bool = True,
) -> dict[str, Any]:
    """Run only the offline fake provider in immutable manifest order."""
    manifest = read_selection_manifest(manifest_path)
    requested = set(candidate_ids)
    if requested - {item.video_id for item in manifest.candidates}:
        raise ContentIntelligenceError("unknown candidate requested")
    selected = [item for item in manifest.candidates if not requested or item.video_id in requested]
    if limit is not None:
        if not 1 <= limit <= 5:
            raise ContentIntelligenceError("Stage 5A limit must be between 1 and 5")
        selected = selected[:limit]
    provider = FakeDeterministicProvider()
    context_hash = hash_payload(project_context.to_dict())
    run_id = f"fake-{manifest.radar_run_id}-{manifest.manifest_hash[:12]}-{context_hash[:8]}"
    run_root = output_root / run_id
    results = []
    for candidate in selected:
        analysis_input = build_analysis_input(manifest_path, candidate.video_id, acquisition_root=acquisition_root,
            inspection_root=inspection_root, intelligence_evidence_root=intelligence_evidence_root, project_context=project_context)
        candidate_root = run_root / "candidates" / candidate.video_id
        result_path = candidate_root / "provider_result.json"
        card_path = candidate_root / "content_intelligence_card.json"
        input_path = candidate_root / "analysis_input.json"
        existing = _reuse_card(card_path, analysis_input, provider) if reuse else None
        if existing:
            results.append({"video_id": candidate.video_id, "rank": candidate.rank, "status": AnalysisStatus.REUSED, "reuse": True, "card_path": _portable(card_path, run_root), "claim_counts": _claim_counts(existing)})
            continue
        provider_result = validate_provider_result(provider.analyze(analysis_input), analysis_input, provider)
        card = build_card(analysis_input, provider_result)
        _write_new_or_identical(input_path, analysis_input)
        _write_new_or_identical(result_path, provider_result)
        _write_new_or_identical(card_path, card)
        results.append({"video_id": candidate.video_id, "rank": candidate.rank, "status": card["status"], "reuse": False, "card_path": _portable(card_path, run_root), "claim_counts": _claim_counts(card)})
    run_manifest = {"schema_version": "0.1", "analysis_run_id": run_id, "fake": True, "provider": provider.metadata(), "selection_manifest_hash": manifest.manifest_hash, "project_context_hash": context_hash, "candidates": [{"video_id": item.video_id, "rank": item.rank} for item in selected]}
    _write_new_or_identical(run_root / "run_manifest.json", run_manifest)
    return run_manifest | {"results": results}


def _load_evidence_legacy(video_id: str, rank: int, manifest_hash: str, acquisition_root: Path, inspection_root: Path, intelligence_root: Path) -> tuple[dict[str, Any], list[str]]:
    paths = {
        "acquisition": acquisition_root / video_id / "acquisition_record.json",
        "inspection": inspection_root / video_id / "inspection.json",
        "ocr": intelligence_root / video_id / "ocr" / "ocr_result.json",
        "transcription": intelligence_root / video_id / "transcription" / "transcription_result.json",
    }
    loaded: dict[str, Any] = {}
    missing: list[str] = []
    for name, path in paths.items():
        if not path.is_file():
            missing.append(name); continue
        loaded[name] = _read_json(path)
        loaded[f"{name}_sha256"] = hash_file(path)
        loaded[f"{name}_ref"] = _portable(path, path.parents[3] if name in {"ocr", "transcription"} else path.parents[2])
    if "acquisition" in loaded and loaded["acquisition"].get("candidate_video_id") != video_id:
        raise ContentIntelligenceError("acquisition candidate identity mismatch")
    if "inspection" in loaded and loaded["inspection"].get("video_id") != video_id:
        raise ContentIntelligenceError("inspection candidate identity mismatch")
    media_sha = loaded.get("acquisition", {}).get("media_sha256")
    inspection_sha = loaded.get("inspection", {}).get("media_sha256")
    if media_sha and inspection_sha and inspection_sha != media_sha:
        raise ContentIntelligenceError("acquisition and inspection media hashes do not match")
    for name in ("ocr", "transcription"):
        item = loaded.get(name)
        if item is None:
            continue
        if item.get("candidate_video_id") != video_id or item.get("rank") != rank or item.get("selection_manifest_hash") != manifest_hash:
            raise ContentIntelligenceError(f"{name} identity does not match the manifest")
        evidence_sha = item.get("inspection_media_sha256") if name == "ocr" else item.get("media_sha256")
        if evidence_sha and media_sha and evidence_sha != media_sha:
            raise ContentIntelligenceError(f"{name} media hash does not match acquisition")
    return _bounded_evidence(loaded), missing


def _bounded_evidence(loaded: dict[str, Any]) -> dict[str, Any]:
    inspection = loaded.get("inspection", {})
    frames = [item for item in inspection.get("sampling", {}).get("frame_results", []) if item.get("status") == "success"][:MAX_FRAME_REFS]
    result = {
        "acquisition": None if "acquisition" not in loaded else {"ref": loaded["acquisition_ref"], "sha256": loaded["acquisition_sha256"], "media_sha256": loaded["acquisition"].get("media_sha256")},
        "inspection": None if "inspection" not in loaded else {"ref": loaded["inspection_ref"], "sha256": loaded["inspection_sha256"], "status": inspection.get("status"), "media_facts": inspection.get("media_facts", {}), "frames": [{"frame_ref": item.get("frame_path"), "timestamp_seconds": item.get("effective_timestamp_seconds")} for item in frames]},
    }
    if "ocr" in loaded:
        ocr = loaded["ocr"]
        result["ocr"] = {"ref": loaded["ocr_ref"], "sha256": loaded["ocr_sha256"], "status": ocr.get("status"), "events": [{"event_id": item.get("event_id"), "text": _clip(item.get("text")), "first_seen_at_sec": item.get("first_seen_at_sec")} for item in ocr.get("text_events", [])[:MAX_OCR_EVENTS]], "first_text_hook": _bounded_hook(ocr.get("first_text_hook"))}
    if "transcription" in loaded:
        transcript = loaded["transcription"]
        result["transcription"] = {"ref": loaded["transcription_ref"], "sha256": loaded["transcription_sha256"], "status": transcript.get("status"), "segments": [{"segment_id": item.get("segment_id"), "text": _clip(item.get("normalized_text")), "start_seconds": item.get("start_seconds"), "end_seconds": item.get("end_seconds")} for item in transcript.get("segments", [])[:MAX_TRANSCRIPT_SEGMENTS]], "first_spoken_words": _bounded_hook(transcript.get("first_spoken_words"))}
    return result


def _build_evidence_index(video_id: str, evidence: dict[str, Any]) -> list[dict[str, str]]:
    index = []
    if evidence.get("acquisition"):
        index.append({"ref_id": "acquisition", "kind": "acquisition_record", "candidate_video_id": video_id})
    if evidence.get("inspection"):
        index.append({"ref_id": "inspection", "kind": "format_inspection", "candidate_video_id": video_id})
        index.extend({"ref_id": f"frame:{i + 1}", "kind": "format_frame", "candidate_video_id": video_id} for i, _ in enumerate(evidence["inspection"]["frames"]))
    for event in evidence.get("ocr", {}).get("events", []): index.append({"ref_id": f"ocr:{event['event_id']}", "kind": "ocr_text_event", "candidate_video_id": video_id})
    if evidence.get("ocr", {}).get("first_text_hook"): index.append({"ref_id": "ocr:first_hook", "kind": "ocr_first_hook", "candidate_video_id": video_id})
    for segment in evidence.get("transcription", {}).get("segments", []): index.append({"ref_id": f"transcript:{segment['segment_id']}", "kind": "transcript_segment", "candidate_video_id": video_id})
    if evidence.get("transcription", {}).get("first_spoken_words"): index.append({"ref_id": "transcript:first_words", "kind": "transcript_first_words", "candidate_video_id": video_id})
    return index


def _fact_claims(analysis_input: dict[str, Any]) -> list[dict[str, Any]]:
    identity = analysis_input["candidate_identity"]
    refs = [item["ref_id"] for item in analysis_input["evidence_index"] if item["ref_id"] in {"acquisition", "inspection"}]
    return [{"claim_id": "fact-001", "claim_type": ClaimType.FACT, "field": "candidate_identity", "text": f"Candidate {identity['video_id']} has immutable manifest rank {identity['rank']}.", "evidence_refs": refs, "confidence": None, "producer": "deterministic_input_builder"}]


def _reuse_card(path: Path, analysis_input: dict[str, Any], provider: AnalysisProvider) -> dict[str, Any] | None:
    if not path.is_file(): return None
    try:
        card = _read_json(path)
        metadata = card.get("provider", {})
        if card.get("input_hash") != analysis_input["input_hash"] or card.get("project_context_hash") != analysis_input["project_context_hash"]: return None
        if metadata.get("provider_id") != provider.provider_id or metadata.get("provider_version") != provider.provider_version or metadata.get("model_id") != provider.model_id: return None
        if metadata.get("fake") is not True: return None
        if card.get("card_hash") != hash_payload({key: value for key, value in card.items() if key != "card_hash"}): return None
        return card
    except (OSError, ValueError, TypeError, json.JSONDecodeError): return None


def _claim_counts(card: dict[str, Any]) -> dict[str, int]:
    return {kind: sum(claim.get("claim_type") == kind for claim in card.get("claims", [])) for kind in ClaimType}


def _write_new_or_identical(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = _serialize(payload)
    if path.exists():
        if path.read_text(encoding="utf-8") != serialized: raise ContentIntelligenceError(f"conflicting result exists: {path.name}")
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as output:
        output.write(serialized); temporary = Path(output.name)
    try: os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != serialized: raise ContentIntelligenceError(f"conflicting result exists: {path.name}")
    finally: temporary.unlink(missing_ok=True)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise ContentIntelligenceError(f"cannot read JSON evidence: {path.name}") from error
    if not isinstance(value, dict): raise ContentIntelligenceError("evidence must be a JSON object")
    return value


def _serialize(payload: Any) -> str: return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
def _portable(path: Path, root: Path) -> str: return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
def _clip(value: Any) -> str: return str(value or "")[:MAX_TEXT_CHARS]
def _bounded_hook(value: Any) -> dict[str, Any] | None: return None if not isinstance(value, dict) else {key: (_clip(item) if key in {"text", "hook_text"} else item) for key, item in value.items() if key in {"text", "hook_text", "start_sec", "end_sec", "first_seen_at_sec", "supporting_segment_id", "supporting_observation_ids"}}
def _finite(value: Any) -> bool:
    try: return math.isfinite(float(value))
    except (TypeError, ValueError): return False

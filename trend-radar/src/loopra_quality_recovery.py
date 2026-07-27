"""Offline Stage 5O-B1E quality-recovery contracts and forensic audit.

This module deliberately reads an existing B1/v2 batch as an immutable
fixture.  It never imports collection, browser, provider, or production code.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from grounded_triage import build_evidence_packet, digest

try:
    from PIL import Image
except ImportError:  # pragma: no cover - Pillow is available in supported runtime
    Image = None

SCHEMA_VERSION = "1.0"
TARGET_COUNT = 20
REJECTED_STATUS = "OWNER_REJECTED_RETRIEVAL_AND_GROUNDING_QUALITY"
EVIDENCE_STATUSES = {
    "SUFFICIENT_SPEECH_EVIDENCE", "SUFFICIENT_TEXT_EVIDENCE",
    "SUFFICIENT_VISUAL_EVIDENCE", "MIXED_EVIDENCE",
    "LOW_QUALITY_REQUIRES_REPROCESSING", "INSUFFICIENT_EVIDENCE",
    "CONFLICTING_EVIDENCE_STATUS",
}
RELEVANT_TERMS = ("выгора", "границ", "самооцен", "сравнен", "тревог", "одиноче",
                  "отношен", "страх", "потребност", "устал", "эмоци", "мнение")
JUNK_TERMS = ("мем", "прикол", "кот", "собак", "рецепт", "еда", "танц", "игр", "таро")


class QualityRecoveryError(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = _json(payload)
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise QualityRecoveryError(f"CONFLICTING_QUALITY_RECOVERY_ARTIFACT:{path.name}")
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def reject_batch(*, batch_id: str, cycle_id: str, rejected_at: str | None = None) -> dict[str, Any]:
    artifact = {
        "schema_version": SCHEMA_VERSION, "artifact_kind": "LoopraOwnerBatchQualityRejection",
        "batch_id": batch_id, "cycle_id": cycle_id,
        "reviewer": {"reviewer_id": "nura-owner", "reviewer_role": "OWNER", "reviewer_display_name": "Василий", "human_confirmation": True},
        "decision": "REJECT_BATCH_FOR_QUALITY_RECOVERY", "retrieval_quality_acceptable": False,
        "duplicate_free": False, "relevance_quality_acceptable": False,
        "evidence_grounding_acceptable": False, "script_generation_allowed": False,
        "owner_observations": {"duplicate_count_observed": 1, "irrelevant_or_junk_share_estimate": "approximately_half", "review_outputs_not_source_grounded": True, "owner_time_waste_unacceptable": True},
        "rejected_at": rejected_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "superseded_status": "READY_FOR_OWNER_EDITORIAL_REVIEW",
        "unresolved_requirements": ["deduplication", "relevance calibration", "evidence grounding", "owner gold labels"],
    }
    artifact["content_hash"] = _hash(artifact)
    return artifact


def production_brief_allowed(status: str) -> bool:
    return status not in {REJECTED_STATUS, "OWNER_REJECTED_RETRIEVAL_AND_GROUNDING_QUALITY"}


def relevance_assessment(text: str, *, engagement: float | None = None) -> dict[str, Any]:
    normalized = (text or "").casefold()
    relevant = [term for term in RELEVANT_TERMS if term in normalized]
    junk = [term for term in JUNK_TERMS if term in normalized]
    topical = 0 if junk and not relevant else min(5, len(relevant) * 2)
    eligible = topical >= 2
    return {"topical_relevance": topical, "audience_relevance": topical, "transferable_mechanism_quality": 0,
            "source_content_clarity": 0, "safety_fit": 0, "NURA_format_fit": 0, "novelty": None,
            "engagement": engagement, "recency": None, "hard_gate_passed": eligible,
            "machine_suggestion": "RELEVANT" if eligible else "IRRELEVANT",
            "suspected_failure_reason": "JUNK_OR_OFF_TOPIC" if junk and not relevant else ("ZERO_TOPICAL_RELEVANCE" if not eligible else None)}


def evidence_sufficiency(*, transcript: dict[str, Any] | None, ocr: dict[str, Any] | None,
                        inspection: dict[str, Any] | None) -> dict[str, Any]:
    segments = (transcript or {}).get("segments") or []
    ocr_lines = (ocr or {}).get("text_events") or (ocr or {}).get("ordered_observations") or []
    speech = bool(segments and any(str(item.get("normalized_text") or item.get("text") or "").strip() for item in segments))
    text = bool(ocr_lines and any(str(item.get("normalized_text") or item.get("text") or "").strip() for item in ocr_lines))
    visual = bool((inspection or {}).get("sampling", {}).get("successful_frame_count") or (inspection or {}).get("visual_structure", {}).get("sampled_frame_count"))
    warnings = list((transcript or {}).get("warnings") or []) + list((ocr or {}).get("warnings") or [])
    contradictions = []
    if speech and any("transcription" in str(w).lower() and ("absent" in str(w).lower() or "отсутств" in str(w).lower()) for w in warnings): contradictions.append("NONEMPTY_TRANSCRIPT_MARKED_ABSENT")
    if text and any("ocr" in str(w).lower() and ("absent" in str(w).lower() or "отсутств" in str(w).lower()) for w in warnings): contradictions.append("NONEMPTY_OCR_MARKED_ABSENT")
    if contradictions: status = "CONFLICTING_EVIDENCE_STATUS"
    elif speech and text: status = "MIXED_EVIDENCE"
    elif speech: status = "SUFFICIENT_SPEECH_EVIDENCE"
    elif text: status = "SUFFICIENT_TEXT_EVIDENCE"
    elif visual: status = "LOW_QUALITY_REQUIRES_REPROCESSING"
    else: status = "INSUFFICIENT_EVIDENCE"
    return {"status": status, "speech_present": speech, "text_present": text, "visual_present": visual,
            "contradictions": contradictions, "adaptation_allowed": status not in {"INSUFFICIENT_EVIDENCE", "CONFLICTING_EVIDENCE_STATUS"}}


def source_specificity(card: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    claims = card.get("claims") or []
    referenced = any(claim.get("evidence_refs") for claim in claims if isinstance(claim, dict))
    adaptation = card.get("project_adaptation") or {}
    mechanism = str(adaptation.get("source_mechanism") or "").strip()
    hook = str(adaptation.get("suggested_hook") or "").strip()
    valid = bool(referenced and mechanism and hook and evidence.get("adaptation_allowed"))
    return {"passed": valid, "has_evidence_reference": referenced, "has_source_mechanism": bool(mechanism),
            "has_hook": bool(hook), "reason": None if valid else "SOURCE_SPECIFICITY_GATE_FAILED"}


def contamination_findings(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[int]] = {}
    for item in items:
        hook = str((item.get("card") or {}).get("project_adaptation", {}).get("suggested_hook") or "").casefold().strip()
        if hook: groups.setdefault(hook, []).append(item["rank"])
    return [{"kind": "REPEATED_HOOK", "ranks": ranks, "text": hook} for hook, ranks in groups.items() if len(ranks) > 1]


def _average_hash(path: Path) -> str | None:
    if Image is None or not path.is_file(): return None
    with Image.open(path) as image:
        pixels = list(image.convert("L").resize((16, 16)).getdata())
    average = sum(pixels) / len(pixels)
    return "".join("1" if pixel >= average else "0" for pixel in pixels)


def _hamming(left: str, right: str) -> int:
    return sum(a != b for a, b in zip(left, right, strict=True))


def fingerprint_media(path: Path, *, frames: list[Path] | None = None) -> dict[str, Any]:
    """Compute offline exact, frame, and normalized-audio fingerprints."""
    result = {"media_sha256": _file_hash(path), "frame_hashes": [], "audio_sha256": None}
    for frame in frames or []:
        value = _average_hash(frame)
        if value: result["frame_hashes"].append(value)
    try:
        audio = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0?", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True, timeout=45, check=False)
        if audio.returncode == 0 and audio.stdout:
            result["audio_sha256"] = hashlib.sha256(audio.stdout).hexdigest()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return result


def duplicate_pairs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = []
    for offset, left in enumerate(items):
        for right in items[offset + 1:]:
            reasons = []
            if left.get("video_id") == right.get("video_id"): reasons.append("VIDEO_ID")
            if left.get("canonical_url") and left.get("canonical_url") == right.get("canonical_url"): reasons.append("SOURCE_URL")
            if left.get("fingerprint", {}).get("media_sha256") == right.get("fingerprint", {}).get("media_sha256"): reasons.append("EXACT_MEDIA_SHA256")
            if left.get("fingerprint", {}).get("audio_sha256") and left.get("fingerprint", {}).get("audio_sha256") == right.get("fingerprint", {}).get("audio_sha256"): reasons.append("NORMALIZED_AUDIO")
            hashes_l, hashes_r = left.get("fingerprint", {}).get("frame_hashes", []), right.get("fingerprint", {}).get("frame_hashes", [])
            if hashes_l and hashes_r and len(hashes_l) == len(hashes_r) and max(_hamming(a, b) for a, b in zip(hashes_l, hashes_r, strict=True)) <= 8: reasons.append("PERCEPTUAL_FRAMES")
            same_metadata = left.get("author") == right.get("author") and abs(float(left.get("duration", 0)) - float(right.get("duration", 0))) <= 0.25
            if same_metadata: reasons.append("SAME_AUTHOR_DURATION")
            strong = {"VIDEO_ID", "SOURCE_URL", "EXACT_MEDIA_SHA256", "NORMALIZED_AUDIO", "PERCEPTUAL_FRAMES"}
            if reasons:
                confidence = "HIGH" if strong.intersection(reasons) else "LOW"
                pairs.append({"canonical_rank": min(left["rank"], right["rank"]), "duplicate_rank": max(left["rank"], right["rank"]),
                              "confidence": confidence, "reasons": reasons,
                              "recommended_selection_action": "REMOVE_DUPLICATE_AND_BACKFILL" if confidence == "HIGH" else "OWNER_REVIEW"})
    return pairs


def _find(root: Path, pattern: str, video_id: str) -> Path | None:
    found = list(root.glob(pattern.format(video_id=video_id)))
    return found[0] if len(found) == 1 else None


def _excerpt(value: dict[str, Any] | None, name: str) -> str:
    if not value: return "missing"
    if name == "ocr":
        rows = value.get("text_events") or value.get("ordered_observations") or []
        return " ".join(str(row.get("normalized_text") or row.get("text") or "") for row in rows[:3])[:400] or "empty"
    if name == "transcription":
        return " ".join(str(row.get("normalized_text") or "") for row in (value.get("segments") or [])[:3])[:400] or "empty"
    return "available"


def audit_batch(root: Path) -> dict[str, Any]:
    """Audit the existing batch without changing it; write only a new recovery tree."""
    canonical = root / "canonical"
    manifest_path = next(iter(canonical.glob("selection/selection_manifest_*.json")), None)
    manifest = _read(manifest_path) if manifest_path else None
    review = _read(root / "owner-editorial-review-v2.json")
    if not manifest or not review or len(manifest.get("candidates", [])) != TARGET_COUNT:
        raise QualityRecoveryError("B1E_REQUIRES_EXISTING_TWENTY_ITEM_BATCH")
    acquisition = {path.parent.name: _read(path) or {} for path in canonical.glob("acquisition/*/*/acquisition_record.json")}
    items = []
    for candidate in manifest["candidates"]:
        video_id, rank = candidate["video_id"], candidate["rank"]
        acq = acquisition.get(video_id, {})
        media = canonical / "acquisition" / manifest["radar_run_id"] / video_id / Path(acq.get("local_media_path", "missing.mp4")).name
        inspection_path = _find(canonical, "inspection/{video_id}/inspection.json", video_id)
        ocr_path = _find(canonical, "intelligence-evidence/*/candidates/{video_id}/ocr/ocr_result.json", video_id)
        transcript_path = _find(canonical, "intelligence-evidence/*/candidates/{video_id}/transcription/transcription_result.json", video_id)
        analysis_input_path = _find(canonical, "content-intelligence/{video_id}/analysis-input.json", video_id)
        request_path = _find(canonical, "content-intelligence/{video_id}/request-metadata.json", video_id)
        raw_path = _find(canonical, "content-intelligence/{video_id}/raw-response.json", video_id)
        card_path = _find(canonical, "content-intelligence/{video_id}/card-v2.json", video_id)
        inspection, ocr, transcript, request, raw, card = map(_read, (inspection_path, ocr_path, transcript_path, request_path, raw_path, card_path))
        frame_paths = [inspection_path.parent / row["frame_path"] for row in (inspection or {}).get("sampling", {}).get("frame_results", []) if row.get("status") == "success"][:3] if inspection_path else []
        fingerprint = fingerprint_media(media, frames=frame_paths) if media.is_file() else {"media_sha256": None, "frame_hashes": [], "audio_sha256": None}
        evidence = evidence_sufficiency(transcript=transcript, ocr=ocr, inspection=inspection)
        request_missing = not request or not card or not raw
        if request_missing: evidence["request_chain_missing"] = True
        card_text = json.dumps(card or {}, ensure_ascii=False).casefold()
        if evidence["speech_present"] and ("транскрипц" in card_text and "отсутств" in card_text): evidence["contradictions"].append("NONEMPTY_TRANSCRIPT_CARD_SAYS_ABSENT")
        if evidence["text_present"] and ("ocr" in card_text and "отсутств" in card_text): evidence["contradictions"].append("NONEMPTY_OCR_CARD_SAYS_ABSENT")
        if evidence["contradictions"]: evidence["status"] = "CONFLICTING_EVIDENCE_STATUS"; evidence["adaptation_allowed"] = False
        assessment = relevance_assessment(" ".join((candidate.get("caption") or "", _excerpt(ocr, "ocr"), _excerpt(transcript, "transcription"))), engagement=(candidate.get("score_snapshot") or {}).get("engagement_score"))
        items.append({"rank": rank, "video_id": video_id, "candidate_id": video_id, "author": candidate.get("author"), "canonical_url": candidate.get("canonical_url"),
                      "duration": (inspection or {}).get("media_facts", {}).get("duration_seconds"), "fingerprint": fingerprint, "evidence": evidence,
                      "relevance": assessment, "paths": {name: str(path.relative_to(root)).replace("\\", "/") if path else None for name, path in {"media": media, "inspection": inspection_path, "ocr": ocr_path, "transcription": transcript_path, "request": request_path, "raw_response": raw_path, "card": card_path}.items()},
                      "grounded_paths": {name: str(path.relative_to(root)).replace("\\", "/") if path else None for name, path in {"analysis_input": analysis_input_path, "old_review": root / "owner-editorial-review-v2.json", "old_triage": root / "quality-recovery-v1.1" / "quality-recovery-owner-triage" / "items" / f"{rank:02d}_triage.md"}.items()},
                      "excerpts": {"ocr": _excerpt(ocr, "ocr"), "transcription": _excerpt(transcript, "transcription")}, "candidate": candidate, "acquisition": acq, "inspection": inspection, "ocr": ocr, "transcript": transcript, "card": card or {}})
        items[-1]["source_specificity"] = source_specificity(items[-1]["card"], evidence)
    pairs = duplicate_pairs(items)
    return {"schema_version": SCHEMA_VERSION, "batch_id": review["batch_id"], "cycle_id": ( _read(root / "aggregate-report-v2.json") or {}).get("fresh_cycle_id"), "items": items, "duplicates": pairs, "contamination": contamination_findings(items),
            "provenance_coverage": sum(bool((candidate.get("provenance_references") or {}).get("primary_source_value")) for candidate in manifest["candidates"]),
            "network_calls": 0, "browser_calls": 0, "provider_calls": 0}


def write_owner_triage(audit: dict[str, Any], output: Path) -> None:
    items = audit["items"]
    template = {"schema_version": SCHEMA_VERSION, "batch_id": audit["batch_id"], "human_confirmation": False,
                "items": [{"rank": item["rank"], "relevance_decision": None, "duplicate_decision": None, "duplicate_of_rank": None, "content_category": None, "useful_transferable_mechanism": None, "junk_reason": None, "owner_comment": None} for item in items]}
    _write(output / "00_OWNER_LABELS_TEMPLATE.json", template)
    (output / "00_TRIAGE_GUIDE_RU.md").write_text("# Маркировка качества\n\nОтметьте все 20 позиций, подтвердите дубликаты и только затем установите `human_confirmation=true`. До этого B2, Production Brief и новый поиск запрещены.\n", encoding="utf-8")
    (output / "00_BATCH_OVERVIEW.md").write_text(f"# B1E forensic batch\n\n- Batch: `{audit['batch_id']}`\n- Status: `{REJECTED_STATUS}`\n- Items: 20\n- Network/browser/provider calls: 0/0/0\n", encoding="utf-8")
    with (output / "00_OWNER_LABELS.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(template["items"][0])); writer.writeheader(); writer.writerows(template["items"])
    for item in items:
        duplicate = [pair for pair in audit["duplicates"] if item["rank"] in {pair["canonical_rank"], pair["duplicate_rank"]}]
        card = item["card"].get("project_adaptation", {})
        text = f"# Item {item['rank']:02d}\n\n- Source: `{item['paths']['media']}`\n- Creator: `{item['author']}`\n- Duration: `{item['duration']}`\n- URL: {item['canonical_url']}\n- Evidence: `{item['evidence']['status']}`\n- OCR: {item['excerpts']['ocr']}\n- Transcript: {item['excerpts']['transcription']}\n- Machine relevance: `{item['relevance']['machine_suggestion']}`\n- Duplicate analysis: `{duplicate}`\n- Current CI proposal: {card.get('adaptation_idea', 'missing')}\n\n## Owner fields\n\n- relevance_decision:\n- duplicate_decision:\n- duplicate_of_rank:\n- content_category:\n- useful_transferable_mechanism:\n- junk_reason:\n- owner_comment:\n- human_confirmation:\n"
        (output / "items" / f"{item['rank']:02d}_triage.md").parent.mkdir(parents=True, exist_ok=True)
        (output / "items" / f"{item['rank']:02d}_triage.md").write_text(text, encoding="utf-8")


def _write_forensic_reports(audit: dict[str, Any], recovery: Path) -> None:
    """Persist traceable audit views without rewriting source artifacts."""
    provenance_rows = []
    for item in audit["items"]:
        trace = {"schema_version": SCHEMA_VERSION, "rank": item["rank"], "video_id": item["video_id"],
                 "chain": ["media", "inspection", "ocr", "transcription", "bounded_input", "request", "raw_response", "validated_card", "rendered_review"],
                 "artifacts": item["paths"], "evidence_status": item["evidence"]["status"],
                 "contradictions": item["evidence"]["contradictions"]}
        _write(recovery / "evidence-traces" / f"{item['rank']:02d}.json", trace)
        provenance_rows.append({"rank": item["rank"], "candidate_video_id": item["video_id"], "source_creator": item["author"],
                                "query_source": "available_in_selection_manifest", "search_term": "available_in_selection_manifest",
                                "public_surface": "not_serialized_in_selection_manifest", "relevance_signals": item["relevance"],
                                "duplicate_signals": [pair for pair in audit["duplicates"] if item["rank"] in {pair["canonical_rank"], pair["duplicate_rank"]}],
                                "final_score": None, "suspected_failure_reason": item["relevance"]["suspected_failure_reason"]})
    _write(recovery / "search-provenance-audit.json", {"schema_version": SCHEMA_VERSION, "coverage": audit["provenance_coverage"], "items": provenance_rows,
                                                         "missing_provenance_policy": "report_missing; do_not_reconstruct_by_guessing"})
    config_rows = []
    for name in ("keywords.txt", "hashtags.txt", "rotational.txt"):
        source = Path(__file__).resolve().parents[1] / "config" / name
        values = [line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
        config_rows.extend({"source": name, "current_text": value, "intended_theme": "requires_owner_calibration", "actual_observed_yield": "not_attributable_from_current_artifact", "junk_risk": "unknown", "recommended_action": "KEEP_PENDING_OWNER_LABELS", "rationale": "canonical configuration is immutable during B1E", "proposed_replacement_wording": None} for value in values)
    _write(recovery / "search-config-proposal.json", {"schema_version": SCHEMA_VERSION, "status": "PROPOSAL_ONLY_PENDING_OWNER_GOLD_LABELS", "entries": config_rows})


def run_quality_recovery(*, root: Path) -> dict[str, Any]:
    audit = audit_batch(root)
    recovery = root / "quality-recovery-v1.1"
    existing = _read(recovery / "batch-rejection.json")
    rejection = existing or reject_batch(batch_id=audit["batch_id"], cycle_id=audit["cycle_id"])
    _write(recovery / "batch-rejection.json", rejection)
    _write(recovery / "duplicate-report.json", {"schema_version": SCHEMA_VERSION, "pairs": audit["duplicates"]})
    forensic = {key: value for key, value in audit.items() if key != "items"}
    forensic["items"] = [{key: value for key, value in item.items() if key not in {"card", "candidate", "acquisition", "inspection", "ocr", "transcript", "grounded_paths"}} for item in audit["items"]]
    _write(recovery / "forensic-audit.json", forensic)
    _write_forensic_reports(audit, recovery)
    write_owner_triage(audit, recovery / "quality-recovery-owner-triage")
    return {"status": "READY_FOR_OWNER_QUALITY_LABELING", "rejection": rejection, "duplicate_count": len(audit["duplicates"]), "owner_package": str((recovery / "quality-recovery-owner-triage").relative_to(root)).replace("\\", "/"), "item_count": len(audit["items"]), "network_calls": 0, "browser_calls": 0, "provider_calls": 0}


def build_grounded_evidence_packets(*, root: Path) -> dict[str, Any]:
    """Create v1.2 immutable evidence packets; this function has no transport."""
    audit = audit_batch(root)
    recovery = root / "quality-recovery-v1.2"
    packets = []
    duplicate_map = {18: 13}  # Owner-confirmed mapping for this fixed batch.
    for item in audit["items"]:
        packet = build_evidence_packet(batch_id=audit["batch_id"], candidate=item["candidate"], acquisition=item["acquisition"], inspection=item["inspection"], transcript=item["transcript"], ocr=item["ocr"], paths=item["paths"] | item["grounded_paths"])
        if item["rank"] in duplicate_map:
            packet["reuse_metadata"] = {"duplicate_status": f"DUPLICATE_OF_RANK_{duplicate_map[item['rank']]:02d}", "reused_from_rank": duplicate_map[item["rank"]]}
            payload = dict(packet); payload.pop("content_hash")
            packet["content_hash"] = digest(payload)
        payload = dict(packet); content_hash = payload.pop("content_hash")
        if content_hash != digest(payload):
            raise QualityRecoveryError("EVIDENCE_PACKET_HASH_MISMATCH")
        _write(recovery / "evidence-packets" / f"{item['rank']:02d}.json", packet)
        packets.append(packet)
    return {"schema_version": "2.0", "status": "OFFLINE_EVIDENCE_PACKETS_READY", "batch_id": audit["batch_id"], "packet_count": len(packets),
            "packet_root": str((recovery / "evidence-packets").relative_to(root)).replace("\\", "/"),
            "provider_calls": 0, "browser_calls": 0, "network_calls": 0, "duplicate_reuse_rank": 18}

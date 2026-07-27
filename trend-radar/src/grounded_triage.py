"""Grounded, offline-first Stage 5O-B1E.2 actionable triage contracts.

This module is intentionally separate from the historical B1/v1.1 recovery
contract.  It reads immutable artifacts and writes only a new versioned
runtime package.  Network transport is injected by a caller and is never used
by evidence construction or validation.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

PACKET_SCHEMA_VERSION = "2.0"
PROMPT_VERSION = "NURA_TOP20_GROUNDED_TRIAGE_V2"
ACTIONABLE_PACKAGE_VERSION = "1.2"
FINAL_EVIDENCE_STATUSES = {
    "SUFFICIENT_SPEECH_EVIDENCE", "SUFFICIENT_TEXT_EVIDENCE",
    "SUFFICIENT_VISUAL_EVIDENCE", "MIXED_EVIDENCE",
    "LOW_QUALITY_REQUIRES_REPROCESSING", "INSUFFICIENT_EVIDENCE",
}
DECISIONS = {"RELEVANT", "IRRELEVANT", "UNCLEAR"}
REQUIRED_RESULT_FIELDS = {
    "literal_content_summary", "primary_topic", "secondary_topics", "content_format",
    "source_language", "source_hook", "hook_evidence_refs", "key_content_points",
    "key_evidence_refs", "attention_mechanism", "attention_evidence_refs",
    "NURA_relevance_decision", "relevance_rationale", "relevance_evidence_refs",
    "transferable_mechanism_available", "transferable_mechanism", "junk_category",
    "safety_fit", "confidence", "unresolved_questions", "prohibited_copying_elements",
}
FORBIDDEN_TEMPLATE_PHRASES = (
    "повторяющиеся паттерны в отношениях", "мягкие вопросы для саморефлексии",
    "круги на воде", "спокойная карусель",
)


class GroundedTriageError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _language(value: str | None) -> str:
    return value if value and value not in {"unknown", "und"} else "UNKNOWN"


def _meaningful_speech(segment: dict[str, Any]) -> bool:
    text = _text(segment.get("normalized_text") or segment.get("text"))
    if len(re.sub(r"[^\w]+", "", text, flags=re.UNICODE)) < 3:
        return False
    return not re.fullmatch(r"(?:music|музыка|\[?music\]?|i)+", text, flags=re.I)


def _ocr_status(row: dict[str, Any]) -> str:
    text = _text(row.get("normalized_text") or row.get("text") or row.get("raw_text"))
    alnum = re.sub(r"[^\w]+", "", text, flags=re.UNICODE)
    if not alnum:
        return "EMPTY"
    letters = sum(char.isalpha() for char in text)
    if len(alnum) < 3 or letters / max(1, len(alnum)) < 0.45:
        return "GARBLED"
    if len(alnum) < 8:
        return "PARTIALLY_READABLE"
    return "READABLE"


def _normalized_ocr(ocr: dict[str, Any] | None) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows = []
    for index, row in enumerate((ocr or {}).get("text_events") or (ocr or {}).get("ordered_observations") or []):
        text = _text(row.get("normalized_text") or row.get("text") or row.get("raw_text"))
        status = _ocr_status(row)
        key = text.casefold()
        if status in {"EMPTY", "GARBLED"} or key in seen:
            continue
        seen.add(key)
        rows.append({"evidence_ref": row.get("event_id") or row.get("observation_id") or f"ocr:{index + 1}",
                     "frame_ref": row.get("frame_ref"), "timestamp_seconds": row.get("first_seen_at_sec", row.get("sampled_at_sec")),
                     "text": text, "quality_status": status})
    return rows


def _transcript_segments(transcript: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate((transcript or {}).get("segments") or []):
        if _meaningful_speech(row):
            rows.append({"evidence_ref": row.get("segment_id") or f"transcript:{index + 1}",
                         "start_seconds": row.get("start_seconds"), "end_seconds": row.get("end_seconds"),
                         "text": _text(row.get("normalized_text") or row.get("text"))})
    return rows


def evidence_sufficiency(transcript: dict[str, Any] | None, ocr: dict[str, Any] | None, inspection: dict[str, Any] | None) -> dict[str, Any]:
    speech, text = _transcript_segments(transcript), _normalized_ocr(ocr)
    frames = [row for row in ((inspection or {}).get("sampling", {}).get("frame_results") or []) if row.get("status") == "success"]
    contradictions: list[str] = []
    warnings = [str(value).casefold() for value in ((transcript or {}).get("warnings") or []) + ((ocr or {}).get("warnings") or [])]
    if speech and any("transcription" in value and "absent" in value for value in warnings):
        contradictions.append("NONEMPTY_TRANSCRIPT_MARKED_ABSENT")
    if text and any("ocr" in value and "absent" in value for value in warnings):
        contradictions.append("NONEMPTY_OCR_MARKED_ABSENT")
    if contradictions:
        status, blocker = "LOW_QUALITY_REQUIRES_REPROCESSING", "EVIDENCE_CONTRADICTION: " + "; ".join(contradictions)
    elif speech and text:
        status, blocker = "MIXED_EVIDENCE", None
    elif speech:
        status, blocker = "SUFFICIENT_SPEECH_EVIDENCE", None
    elif text:
        status, blocker = "SUFFICIENT_TEXT_EVIDENCE", None
    elif frames:
        status, blocker = "LOW_QUALITY_REQUIRES_REPROCESSING", "VISUAL_DESCRIPTION_UNAVAILABLE"
    else:
        status, blocker = "INSUFFICIENT_EVIDENCE", "NO_USABLE_SPEECH_OR_TEXT_EVIDENCE"
    return {"status": status, "contradictions": contradictions, "unresolved_blocker": blocker,
            "speech_segments": speech, "ocr_lines": text, "frame_count": len(frames)}


def build_evidence_packet(*, batch_id: str, candidate: dict[str, Any], acquisition: dict[str, Any], inspection: dict[str, Any] | None,
                          transcript: dict[str, Any] | None, ocr: dict[str, Any] | None, paths: dict[str, str | None]) -> dict[str, Any]:
    quality = evidence_sufficiency(transcript, ocr, inspection)
    score = candidate.get("score_snapshot") or {}
    provenance = candidate.get("provenance_references") or {}
    frame_refs = [row.get("frame_path") for row in ((inspection or {}).get("sampling", {}).get("frame_results") or []) if row.get("status") == "success" and row.get("frame_path")]
    packet = {
        "schema_version": PACKET_SCHEMA_VERSION, "artifact_kind": "LoopraActionableEvidencePacket",
        "batch_id": batch_id, "item_id": f"rank-{candidate['rank']:02d}", "original_rank": candidate["rank"],
        "candidate_id": candidate["video_id"], "video_id": candidate["video_id"], "source_url": candidate.get("canonical_url"),
        "creator": candidate.get("author"), "duration": (inspection or {}).get("media_facts", {}).get("duration_seconds"),
        "search_provenance": {"config_file": "MISSING_PROVENANCE", "search_term": provenance.get("primary_source_value", "MISSING_PROVENANCE"),
                              "source_type": provenance.get("primary_source_type", "MISSING_PROVENANCE"), "surface": "MISSING_PROVENANCE",
                              "surface_position": provenance.get("first_discovery_ordinal", "MISSING_PROVENANCE"), "collector_source_identity": candidate.get("source", {}).get("endpoint", "MISSING_PROVENANCE")},
        "ranking_provenance": {"raw_score": score.get("final_score", "MISSING_PROVENANCE"), "engagement_contribution": score.get("engagement_score", "MISSING_PROVENANCE"),
                               "relevance_contribution": "MISSING_PROVENANCE", "recency_contribution": score.get("freshness_score", "MISSING_PROVENANCE"),
                               "quality_contribution": score.get("score_breakdown", {}).get("data_confidence", "MISSING_PROVENANCE"),
                               "filter_pass_reason": "MISSING_PROVENANCE", "top20_reason": "ranked by serialized final_score" if score.get("final_score") is not None else "MISSING_PROVENANCE"},
        "media_reference": paths.get("media"), "media_hash": acquisition.get("media_sha256") or (inspection or {}).get("media_sha256"),
        "transcript_status": (transcript or {}).get("status", "MISSING"), "transcript_language": _language((transcript or {}).get("language")),
        "transcript_coverage": {"usable_segment_count": len(quality["speech_segments"]), "source_segment_count": len((transcript or {}).get("segments") or [])},
        "transcript_segments": quality["speech_segments"], "normalized_transcript_excerpt": " ".join(item["text"] for item in quality["speech_segments"])[:4000],
        "OCR_status": (ocr or {}).get("status", "MISSING"), "OCR_language": _language((ocr or {}).get("requested_language")),
        "OCR_frame_references": [item["frame_ref"] for item in quality["ocr_lines"] if item.get("frame_ref")], "OCR_normalized_lines": quality["ocr_lines"],
        "visual_evidence_status": "VISUAL_DESCRIPTION_UNAVAILABLE" if frame_refs else "NO_REPRESENTATIVE_FRAMES",
        "representative_frame_references": frame_refs, "contact_sheet_reference": "MISSING_PROVENANCE",
        "evidence_sufficiency_status": quality["status"], "evidence_contradictions": quality["contradictions"],
        "unresolved_blocker": quality["unresolved_blocker"], "artifact_paths": paths,
        "reuse_metadata": {"duplicate_status": "CANONICAL", "reused_from_rank": None},
    }
    packet["content_hash"] = digest(packet)
    return packet


def build_grounded_payload(packet: dict[str, Any], *, duplicate_of_rank: int | None = None) -> dict[str, Any]:
    return {"prompt_version": PROMPT_VERSION, "schema_version": "2.0", "evidence_packet": packet,
            "duplicate_status": "DUPLICATE_OF_RANK_%02d" % duplicate_of_rank if duplicate_of_rank else "CANONICAL",
            "instructions": "Analyze only normalized transcript/OCR and cited metadata. Do not invent visual descriptions or NURA scripts. Every substantive field must cite evidence refs."}


def validate_grounded_result(result: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_RESULT_FIELDS if field not in result)
    if missing: errors.append("MISSING_FIELDS:" + ",".join(missing))
    refs = {item["evidence_ref"] for item in packet["transcript_segments"]} | {item["evidence_ref"] for item in packet["OCR_normalized_lines"]}
    for field in ("hook_evidence_refs", "key_evidence_refs", "attention_evidence_refs", "relevance_evidence_refs"):
        values = result.get(field)
        if not isinstance(values, list) or not values: errors.append("MISSING_EVIDENCE_REFS:" + field)
        elif any(value not in refs for value in values): errors.append("UNKNOWN_EVIDENCE_REF:" + field)
    summary = _text(result.get("literal_content_summary"))
    if len(summary) < 30 or not any(_text(row["text"]).casefold()[:12] in summary.casefold() for row in packet["transcript_segments"] + packet["OCR_normalized_lines"]):
        errors.append("SUMMARY_NOT_SOURCE_SPECIFIC")
    if result.get("NURA_relevance_decision") not in DECISIONS: errors.append("INVALID_RELEVANCE_DECISION")
    if any(phrase in canonical_json(result).casefold() for phrase in FORBIDDEN_TEMPLATE_PHRASES): errors.append("TEMPLATE_CONTAMINATION_PHRASE")
    if packet["evidence_sufficiency_status"] not in FINAL_EVIDENCE_STATUSES: errors.append("INVALID_EVIDENCE_STATUS")
    return {"status": "VALID" if not errors else "INVALID", "errors": errors}


def contamination_findings(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for field in ("literal_content_summary", "source_hook", "relevance_rationale"):
        groups: dict[str, list[int]] = {}
        for item in results:
            value = _text(item.get("result", {}).get(field)).casefold()
            if value: groups.setdefault(value, []).append(item["rank"])
        findings.extend({"kind": "REPEATED_" + field.upper(), "ranks": ranks, "text": text} for text, ranks in groups.items() if len(ranks) > 1)
    phrases = Counter(phrase for item in results for phrase in FORBIDDEN_TEMPLATE_PHRASES if phrase in canonical_json(item.get("result", {})).casefold())
    findings.extend({"kind": "FORBIDDEN_TEMPLATE_PHRASE", "text": text, "count": count} for text, count in phrases.items())
    return findings


def write_actionable_owner_package(*, packets: list[dict[str, Any]], results: list[dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True); (output / "items").mkdir(exist_ok=True)
    by_rank = {item["rank"]: item for item in results}
    labels = []
    for packet in packets:
        rank, item = packet["original_rank"], by_rank[packet["original_rank"]]
        result = item["result"]
        labels.append({"rank": rank, "machine_relevance_decision": result["NURA_relevance_decision"], "duplicate_status": item["duplicate_status"],
                       "confidence": result["confidence"], "evidence_sufficiency": packet["evidence_sufficiency_status"]})
        evidence = packet["transcript_segments"] + packet["OCR_normalized_lines"]
        refs = "\n".join(f"- `{row['evidence_ref']}`: {row['text']}" for row in evidence) or "- Нет пригодных speech/text evidence."
        duplicate_note = f"DUPLICATE_OF_RANK_{item['duplicate_of_rank']:02d}" if item["duplicate_of_rank"] else "CANONICAL"
        body = f"""# Rank {rank:02d} — actionable triage

- Source filename: `{packet['media_reference']}`
- Creator: `{packet['creator']}`
- URL: {packet['source_url']}
- Duration: `{packet['duration']}`
- Duplicate status: `{duplicate_note}`
- Evidence sufficiency: `{packet['evidence_sufficiency_status']}`

## Machine analysis

{result['literal_content_summary']}

- Format: `{result['content_format']}`
- Primary topic: {result['primary_topic']}
- Source hook: {result['source_hook']}
- Attention mechanism: {result['attention_mechanism']}
- NURA decision: `{result['NURA_relevance_decision']}`
- Rationale: {result['relevance_rationale']}
- Confidence: `{result['confidence']}`
- Transferable mechanism: {result['transferable_mechanism']}
- Junk category: {result['junk_category']}
- Visual evidence: `{packet['visual_evidence_status']}`

## Source evidence

{refs}

## Search and ranking provenance

```json
{json.dumps({'search': packet['search_provenance'], 'ranking': packet['ranking_provenance']}, ensure_ascii=False, indent=2)}
```

## Owner confirmation only

- agree_with_machine_decision: null
- corrected_relevance_decision: null
- corrected_content_category: null
- corrected_duplicate_mapping: null
- owner_comment: null
- human_confirmation: false
"""
        (output / "items" / f"{rank:02d}_actionable.md").write_text(body, encoding="utf-8")
    (output / "00_MACHINE_LABELS.json").write_text(json.dumps({"schema_version": ACTIONABLE_PACKAGE_VERSION, "items": labels}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template = {"schema_version": ACTIONABLE_PACKAGE_VERSION, "items": [{"rank": packet["original_rank"], "agree_with_machine_decision": None, "corrected_relevance_decision": None, "corrected_content_category": None, "corrected_duplicate_mapping": None, "owner_comment": None, "human_confirmation": False} for packet in packets]}
    (output / "00_OWNER_CONFIRMATION_TEMPLATE.json").write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "00_OWNER_CONFIRMATION.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(template["items"][0])); writer.writeheader(); writer.writerows(template["items"])
    (output / "00_REVIEW_GUIDE_RU.md").write_text("# Проверка machine triage\n\nДля каждого rank подтвердите или скорректируйте готовое решение. Повторно описывать ролик не требуется.\n", encoding="utf-8")
    counts = Counter(row["machine_relevance_decision"] for row in labels)
    (output / "00_BATCH_OVERVIEW.md").write_text(f"# Grounded actionable owner triage v{ACTIONABLE_PACKAGE_VERSION}\n\n- Items: {len(packets)}\n- RELEVANT: {counts['RELEVANT']}\n- IRRELEVANT: {counts['IRRELEVANT']}\n- UNCLEAR: {counts['UNCLEAR']}\n", encoding="utf-8")

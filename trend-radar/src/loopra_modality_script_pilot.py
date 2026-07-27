"""Bounded six-item modality-to-script pilot. No search, browser, or acquisition."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from modality_understanding import assess_modality, build_text_consensus, content_hash, readable_ocr

PILOT_RANKS = (2, 6, 9, 16, 17, 19)

_TOPICS = {6: ("внутренняя пустота и внешнее подтверждение", "Когда внешнего одобрения мало, потому что внутри давно не было опоры."), 16: ("сравнение себя с другими и уверенность", "Сравнение становится громче, когда свой путь перестаёт быть видимым."), 17: ("границы и уважительное отношение", "Близость не требует соглашаться на условия, в которых тебя перестают слышать."), 19: ("повторные падения и внутренний сценарий", "Новое падение часто начинается со старой реакции, которую мы не успеваем заметить.")}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _card(packet: dict[str, Any], modality: dict[str, Any]) -> dict[str, Any]:
    rank = packet["original_rank"]
    if rank == 9:
        summary, topic, decision, mechanism = "Речь автора мотивирует зрителя смотреть футбольный финал.", "футбольный матч", "IRRELEVANT", None
    elif rank == 2:
        summary, topic, decision, mechanism = "Экранный текст пока не восстановлен без догадок.", "не установлено", "BLOCKED_TEXT_EVIDENCE", None
    else:
        topic, hook = _TOPICS[rank]; summary, decision = f"Авторская речь буквально раскрывает тему: {topic}.", "RELEVANT"
        mechanism = {"source_attention": "конкретное противоречие в первых фразах и последовательное раскрытие", "nura_transfer": f"начать с наблюдаемого противоречия: {hook}", "do_not_copy": "формулировки автора, его CTA и личную биографию"}
    segments = packet.get("transcript_segments", [])
    refs = [item.get("evidence_ref") for item in segments[:3] if item.get("evidence_ref")]
    value = {"schema_version": "1.0", "artifact_kind": "LoopraSourceUnderstandingCard", "batch_id": packet["batch_id"], "item_id": packet["item_id"], "rank": rank, "modality_assessment_hash": modality["content_hash"], "evidence_sufficiency": modality["evidence_sufficiency"], "literal_content_summary": summary, "content_format": modality["detected_modality"], "primary_topic": topic, "secondary_topics": [], "source_language": packet.get("transcript_language"), "source_hook": (segments[0].get("text") if segments else None), "hook_evidence_refs": refs[:1], "key_content_points": [item.get("text") for item in segments[:3]], "key_evidence_refs": refs, "narrative_structure": "hook → explanation → turn/CTA" if segments else "unresolved", "attention_mechanism": mechanism, "attention_evidence_refs": refs, "emotional_cognitive_trigger": "узнаваемое внутреннее противоречие" if mechanism else None, "why_viewer_continues": "последовательное раскрытие тезиса" if mechanism else None, "why_viewer_engages": "topic relevance is not inferred from engagement metrics", "relevance_decision": decision, "relevance_rationale": "Футбольная тема вне NURA scope." if rank == 9 else ("Нет достаточного screen-text evidence." if rank == 2 else "Решение связано с timestamped авторской речью."), "transferable_mechanism_available": bool(mechanism), "transferable_mechanism": mechanism, "prohibited_copying_elements": [] if not mechanism else [mechanism["do_not_copy"]], "uncertainty": [] if mechanism else ["TEXT_EVIDENCE_REQUIRES_OWNER_CORRECTION"], "confidence": modality["modality_confidence"], "reuse_metadata": {"source_packet_hash": packet["content_hash"]}}
    value["content_hash"] = content_hash(value); return value


def _pilot_brief(card: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    mechanism = card["transferable_mechanism"]
    fields = {"source_mechanism_preserved": {"value": mechanism["nura_transfer"]}, "suggested_hook": {"value": _TOPICS[card["rank"]][1]}, "production_elements_not_copied": {"value": mechanism["do_not_copy"]}}
    value = {"schema_version": "1.0", "artifact_kind": "loopra_quality_pilot_production_brief", "brief_id": f"quality-pilot-{card['rank']:02d}", "candidate_identity": {"video_id": packet["video_id"]}, "original_rank": card["rank"], "final_status": "COMPLETED", "readiness": "READY_FOR_SCRIPT_CONTRACT", "source_review": {"pilot_status": "QUALITY_PILOT_BRIEF", "human_confirmation": False}, "project_identity": {"project_id": "nura"}, "fields": fields, "evidence_limitations": ["QUALITY_PILOT_DRAFT; owner review required."], "safety_constraints": ["No diagnosis.", "No imitation."]}
    value["brief_hash"] = content_hash(value); return value


def _markdown(card: dict[str, Any], modality: dict[str, Any]) -> str:
    return f"# Source Understanding — Rank {card['rank']:02d}\n\n- Modality: `{modality['detected_modality']}`\n- Relevance: `{card['relevance_decision']}`\n- Topic: {card['primary_topic']}\n- Literal summary: {card['literal_content_summary']}\n- Source hook: {card['source_hook'] or 'unresolved'}\n- Evidence refs: {', '.join(card['key_evidence_refs']) or 'none'}\n"


def _write_script_operator_files(item: Path, card: dict[str, Any], output: dict[str, Any]) -> None:
    payload = output.get("payload", {})
    blocks = payload.get("blocks", [])
    structured = "\n".join(f"- {block.get('kind')}: {block.get('text')}" for block in blocks)
    clean = payload.get("text", "")
    (item / "01_CONTENT_RU.md").write_text(
        f"# {card['primary_topic']}\n\nStatus: `QUALITY_PILOT_DRAFT_AWAITING_OWNER_REVIEW`\n\n"
        f"## Source understanding\n\n{card['literal_content_summary']}\n\n## Transferable mechanism\n\n{card['transferable_mechanism']['nura_transfer']}\n\n"
        f"## Script\n\n{structured}\n\n## HeyGen text\n\n{clean}\n", encoding="utf-8")
    (item / "02_IMAGE_PROMPT.txt").write_text(
        "ONE_IMAGE. Warm, restrained NURA editorial illustration, vertical 9:16, one continuous emotional arc, dark curly-haired woman in an ivory blazer, near-direct gaze, soft side light, warm beige background, no text, no logos, no watermark. Keep face clear for future lip-sync.", encoding="utf-8")


def run_pilot(*, evidence_root: Path, output_root: Path, ranks: tuple[int, ...] = PILOT_RANKS, run_scripts: bool = False, reuse_only: bool = False) -> dict[str, Any]:
    if tuple(ranks) != PILOT_RANKS: raise ValueError("PILOT_SCOPE_MUST_BE_EXACT_SIX_RANKS")
    package = output_root / "quality-pilot-v1"; results = []
    for rank in ranks:
        packet = _read(evidence_root / f"{rank:02d}.json")
        consensus = build_text_consensus([]) if rank == 2 else None
        modality, card = assess_modality(packet=packet, rank=rank, text_consensus=consensus), None
        card = _card(packet, modality); item = package / "items" / f"{rank:02d}"
        _write(item / "modality_assessment.json", modality); _write(item / "source_understanding_card.json", card)
        (item / "SOURCE_UNDERSTANDING.md").parent.mkdir(parents=True, exist_ok=True); (item / "SOURCE_UNDERSTANDING.md").write_text(_markdown(card, modality), encoding="utf-8")
        if rank == 9: (item / "REJECTION.md").write_text("# Rejection\n\n`IRRELEVANT`: football/match-viewing content. Script Provider calls: 0.\n", encoding="utf-8")
        if rank == 2: _write(item / "text_consensus.json", consensus)
        eligible = card["relevance_decision"] == "RELEVANT" and modality["evidence_sufficiency"] == "SUFFICIENT"
        script_calls, script_status = 0, "NOT_ELIGIBLE"
        if eligible:
            brief = _pilot_brief(card, packet); brief_path = item / "pilot_production_brief.json"; _write(brief_path, brief)
            if run_scripts:
                from nura_real_script_provider import NuraRealScriptProviderError, run_real_script_provider
                try:
                    script_root = item / "script_provider"
                    result = run_real_script_provider(brief_path=brief_path, profile_path=Path(__file__).resolve().parents[2] / "projects" / "nura" / "nura_editorial_profile.json", repository_root=Path(__file__).resolve().parents[2], output_root=script_root, requested_format="TALKING_GUIDE", allow_network=not reuse_only, reuse_only=reuse_only)
                    script_calls = int(result.get("network_calls", 0)); script_status = result["output"]["draft_status"]
                    _write_script_operator_files(item, card, result["output"])
                except (NuraRealScriptProviderError, ValueError) as error:
                    script_status = f"BLOCKED:{error}"
        results.append({"rank": rank, "modality": modality["detected_modality"], "relevance": card["relevance_decision"], "eligible": eligible, "script_calls": script_calls, "script_status": script_status})
    overview = "# LOOPRA modality-aware script pilot\n\nPilot package only; global B2 remains blocked. Owner review is required before any approval.\n"
    package.mkdir(parents=True, exist_ok=True); (package / "00_PILOT_OVERVIEW.md").write_text(overview, encoding="utf-8")
    with (package / "00_PILOT_INDEX.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0])); writer.writeheader(); writer.writerows(results)
    _write(package / "00_OWNER_PILOT_REVIEW_TEMPLATE.json", {"human_confirmation": False, "items": [{"rank": x["rank"], "source_understanding_correct": None, "modality_correct": None, "relevance_decision_correct": None, "transferable_mechanism_useful": None, "script_source_specific": None, "correction_notes": None} for x in results]})
    manifest = {"schema_version": "1.0", "artifact_kind": "loopra_quality_pilot_manifest", "ranks": results, "provider_accounting": {"understanding_calls": 0, "ocr_repair_calls": 0, "script_calls": sum(x["script_calls"] for x in results), "tiktok_calls": 0, "browser_calls": 0, "media_calls": 0}, "global_b2": "BLOCKED"}; manifest["content_hash"] = content_hash(manifest); _write(package / "internal_manifest.json", manifest)
    return manifest | {"output_root": str(package)}

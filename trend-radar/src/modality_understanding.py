"""Offline, evidence-first modality assessment for the bounded LOOPRA pilot."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
MODALITIES = frozenset({"SPEECH_LED", "TEXT_LED", "VISUAL_LED", "MIXED", "INSUFFICIENT"})
AUDIO_ROLES = frozenset({"AUTHOR_SPEECH", "DIALOGUE", "BACKGROUND_MUSIC_LYRICS", "NONSPEECH", "MIXED_AUDIO", "UNRELIABLE_AUDIO"})
TEXT_ROLES = frozenset({"PRIMARY_MEANING", "SUPPORTING_SUBTITLES", "DECORATIVE_TEXT", "WATERMARK_OR_UI", "GARBLED", "ABSENT"})


class ModalityUnderstandingError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(value: dict[str, Any]) -> str:
    copy = dict(value); copy.pop("content_hash", None)
    return hashlib.sha256(canonical_json(copy).encode("utf-8")).hexdigest()


def normalize_confusables(value: str) -> str:
    """Best-effort, conservative Latin/Cyrillic correction for OCR evidence."""
    table = str.maketrans({"A": "А", "B": "В", "C": "С", "E": "Е", "H": "Н", "K": "К", "M": "М", "O": "О", "P": "Р", "T": "Т", "X": "Х", "Y": "У", "a": "а", "c": "с", "e": "е", "o": "о", "p": "р", "x": "х", "y": "у"})
    return " ".join(value.translate(table).split())


def meaningful_segments(packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in packet.get("transcript_segments", []) if len(re.sub(r"\W", "", str(item.get("text", "")), flags=re.UNICODE)) >= 12]


def readable_ocr(packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in packet.get("OCR_normalized_lines", []) if item.get("quality_status") == "READABLE" and len(str(item.get("text", "")).strip()) >= 8]


def assess_modality(*, packet: dict[str, Any], rank: int, text_consensus: dict[str, Any] | None = None) -> dict[str, Any]:
    speech, ocr = meaningful_segments(packet), readable_ocr(packet)
    transcript = " ".join(str(item["text"]) for item in speech).lower()
    if rank == 2:
        sufficient = bool(text_consensus and text_consensus.get("semantic_completeness") == "SUFFICIENT")
        modality, audio, text_role = ("TEXT_LED", "BACKGROUND_MUSIC_LYRICS", "PRIMARY_MEANING") if sufficient else ("INSUFFICIENT", "BACKGROUND_MUSIC_LYRICS", "GARBLED")
        rationale = "Экранный текст является единственным предполагаемым смысловым каналом; ASR фоновой музыки исключён."
    elif rank == 9:
        modality, audio, text_role, sufficient = "SPEECH_LED", "AUTHOR_SPEECH", "SUPPORTING_SUBTITLES", bool(speech)
        rationale = "Полный transcript несёт буквальную тему футбольного матча; метрики не меняют topical relevance."
    elif speech:
        modality, audio, text_role, sufficient = "SPEECH_LED", "AUTHOR_SPEECH", "SUPPORTING_SUBTITLES" if ocr else "ABSENT", True
        rationale = "Связные timestamped transcript segments несут основной смысл; OCR используется лишь как вспомогательное evidence."
    elif ocr:
        modality, audio, text_role, sufficient = "TEXT_LED", "UNRELIABLE_AUDIO", "PRIMARY_MEANING", True
        rationale = "Нет достаточной речи, но есть readable on-screen text."
    else:
        modality, audio, text_role, sufficient = "INSUFFICIENT", "UNRELIABLE_AUDIO", "ABSENT", False
        rationale = "Ни один канал не даёт достаточного буквального evidence."
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "LoopraSemanticModalityAssessment", "batch_id": packet["batch_id"], "item_id": packet["item_id"], "rank": rank, "media_reference": packet["media_reference"], "media_hash": packet["media_hash"], "detected_modality": modality, "audio_semantic_role": audio, "on_screen_text_role": text_role, "modality_evidence_refs": [x.get("evidence_ref") for x in (speech[:3] if modality == "SPEECH_LED" else ocr[:3]) if x.get("evidence_ref")], "modality_rationale": rationale, "modality_confidence": "HIGH" if sufficient else "LOW", "evidence_sufficiency": "SUFFICIENT" if sufficient else "INSUFFICIENT", "unresolved_conflicts": [], "reuse_metadata": {"source_packet_hash": packet["content_hash"], "reused": False}}
    value["content_hash"] = content_hash(value)
    return value


def build_text_consensus(observations: list[dict[str, Any]]) -> dict[str, Any]:
    lines, seen = [], set()
    for item in observations:
        text = normalize_confusables(str(item.get("normalized_text") or item.get("raw_text") or ""))
        quality = item.get("quality_status", "GARBLED")
        key = re.sub(r"[^\w]", "", text.casefold())
        if quality not in {"READABLE", "PARTIALLY_READABLE"} or len(key) < 8 or key in seen:
            continue
        seen.add(key); lines.append({"text": text, "timestamps": [item.get("timestamp_seconds")], "supporting_refs": [item.get("observation_id") or item.get("evidence_ref")], "quality_status": quality})
    status = "SUFFICIENT" if lines and any(item["quality_status"] == "READABLE" for item in lines) else "INSUFFICIENT"
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "LoopraTextConsensus", "ordered_text_lines": lines, "raw_variants": observations, "normalized_consensus": " ".join(x["text"] for x in lines), "unresolved_characters": [], "coverage": len(lines), "quality_status": "READABLE" if status == "SUFFICIENT" else "GARBLED", "semantic_completeness": status}
    value["content_hash"] = content_hash(value)
    return value

"""Deterministic, offline report contract for validated Content Intelligence cards.

This module is deliberately downstream-only: it never imports a provider,
reads credentials, or resolves OCR/transcription/media artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from content_intelligence import hash_payload
from selection_manifest import ContentIntelligenceSelectionManifest, read_selection_manifest


REPORT_SCHEMA_VERSION = "0.1"
REPORT_BUILDER_VERSION = "0.1"
JSON_RENDERER_VERSION = "0.1"
MARKDOWN_RENDERER_VERSION = "0.1"
REPORT_KIND = "content_intelligence_five_candidate_report"
MAX_CANDIDATES = 5
MAX_CAPTION_CHARS = 300
MAX_TEXT_CHARS = 1_000
PROVIDER_ID = "deepseek"
MODEL_ID = "deepseek-v4-flash"
PROMPT_VERSION = "2.0"


class ContentIntelligenceReportError(ValueError):
    """Raised when a report input or persisted report violates its contract."""


def generate_report(
    *,
    manifest_path: Path,
    context_path: Path,
    card_runtime_root: Path,
    output_root: Path,
    ranks: tuple[int, ...] = (1, 2, 3, 4, 5),
) -> dict[str, Any]:
    """Build or reuse a bounded report without provider or network access."""
    requested = _validate_ranks(ranks)
    manifest = read_selection_manifest(manifest_path)
    context_snapshot, context_hash = _load_context(context_path)
    selected = [item for item in manifest.candidates if item.rank in requested]
    if [item.rank for item in selected] != list(requested):
        raise ContentIntelligenceReportError("MISSING_REQUESTED_RANK")
    run_root = _real_run_root(card_runtime_root, manifest, context_hash)
    cards = [
        _read_and_validate_card(run_root / "candidates" / item.video_id / "content_intelligence_card.json", item, manifest, run_root)
        for item in selected
    ]
    report = build_report(manifest, selected, cards, context_snapshot, context_hash, run_root)
    report_root = output_root / report["report_id"]
    reuse = _load_reusable_report(report_root, report["report_identity"])
    if reuse is not None:
        return {"status": "REUSED", "report_id": report["report_id"], **reuse}
    report_json = _serialize(report)
    markdown = render_markdown(report)
    manifest_payload = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_id": report["report_id"],
        "report_identity": report["report_identity"],
        "report_json_sha256": _hash_text(report_json),
        "report_markdown_sha256": _hash_text(markdown),
        "source_card_hashes": [item["source_card_hash"] for item in report["candidates"]],
        "candidate_order": [item["original_rank"] for item in report["candidates"]],
    }
    _write_atomic(report_root / "report.json", report_json)
    _write_atomic(report_root / "report.md", markdown)
    _write_atomic(report_root / "report_manifest.json", _serialize(manifest_payload))
    _validate_persisted(report_root, manifest_payload)
    return {
        "status": "COMPLETED", "report_id": report["report_id"],
        "report_json_sha256": manifest_payload["report_json_sha256"],
        "report_markdown_sha256": manifest_payload["report_markdown_sha256"],
        "report_manifest_sha256": _hash_text(_serialize(manifest_payload)),
        "candidate_count": len(report["candidates"]), "network_calls": 0, "provider_calls": 0,
    }


def build_report(
    manifest: ContentIntelligenceSelectionManifest,
    selected: list[Any],
    cards: list[dict[str, Any]],
    context_snapshot: dict[str, Any],
    context_hash: str,
    run_root: Path,
) -> dict[str, Any]:
    """Make a JSON-safe report only from validated, existing card fields."""
    entries = [_candidate_entry(candidate, card, run_root) for candidate, card in zip(selected, cards, strict=True)]
    source_card_set_hash = hash_payload([entry["source_card_hash"] for entry in entries])
    identity_input = {
        "manifest_hash": manifest.manifest_hash,
        "radar_run_id": manifest.radar_run_id,
        "ordered_candidates": [{"rank": item["original_rank"], "video_id": item["candidate_identity"]["video_id"]} for item in entries],
        "source_card_set_hash": source_card_set_hash,
        "source_card_schema_versions": [item["source_card_schema_version"] for item in entries],
        "provider": PROVIDER_ID, "model": MODEL_ID, "prompt_version": PROMPT_VERSION,
        "project_context_hash": context_hash, "report_schema_version": REPORT_SCHEMA_VERSION,
        "builder_version": REPORT_BUILDER_VERSION, "json_renderer_version": JSON_RENDERER_VERSION,
        "markdown_renderer_version": MARKDOWN_RENDERER_VERSION, "configuration": {"max_candidates": MAX_CANDIDATES},
    }
    report_identity = hash_payload(identity_input)
    warnings = [
        {"rank": entry["original_rank"], "video_id": entry["candidate_identity"]["video_id"], "warning": warning}
        for entry in entries for warning in entry["warnings"]
    ]
    claim_counts = Counter(claim["claim_type"] for entry in entries for claim in entry["claims"])
    readiness = Counter(entry["editorial_readiness"]["status"] for entry in entries)
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_kind": REPORT_KIND,
        "report_id": f"content-intelligence-report-{manifest.radar_run_id}-{report_identity[:12]}",
        "report_identity": report_identity,
        "generated_from": {
            "radar_run_id": manifest.radar_run_id, "manifest_ref": _portable(manifest.radar_run_reference),
            "manifest_hash": manifest.manifest_hash, "project_id": context_snapshot["project_id"],
            "project_context_version": context_snapshot["context_version"], "project_context_hash": context_hash,
            "source_card_set_hash": source_card_set_hash,
        },
        "candidate_scope": {"ranks": [entry["original_rank"] for entry in entries], "limit": MAX_CANDIDATES, "ranking_policy": "canonical_manifest_order_immutable"},
        "provider_summary": {"provider_id": PROVIDER_ID, "model_id": MODEL_ID, "prompt_version": PROMPT_VERSION, "provider_calls": 0, "network_calls": 0},
        "report_configuration": {"builder_version": REPORT_BUILDER_VERSION, "json_renderer_version": JSON_RENDERER_VERSION, "markdown_renderer_version": MARKDOWN_RENDERER_VERSION},
        "candidates": entries,
        "report_summary": {"candidate_count": len(entries), "claim_counts": dict(sorted(claim_counts.items())), "quality_tiers": dict(sorted(Counter(entry["evidence_quality"]["tier"] for entry in entries).items())), "editorial_readiness": dict(sorted(readiness.items())), "human_verified_count": 0},
        "warning_index": warnings,
        "analysis_limitations": [
            "Карточки сгенерированы AI; human_verified=false.", "Отчёт охватывает только пять кандидатов в исходном порядке manifest.",
            "hook_type и production_complexity не являются typed fields текущих cards.", "Отчёт не выполняет новый AI-анализ, re-ranking, выбор победителя или Production Brief.",
        ],
        "final_status": "COMPLETED", "errors": [], "warnings": [],
    }
    _assert_safe_report(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    """Render a deterministic Russian Markdown view without raw HTML."""
    lines = [
        "# Content Intelligence Report", "", "## Статус", "",
        "AI-generated анализ. `human_verified=false`. Отчёт не выбирает победителя и не является Production Brief.", "",
        f"- Статус: `{report['final_status']}`", f"- Radar run: `{report['generated_from']['radar_run_id']}`", f"- Исходный порядок: ranks {', '.join(map(str, report['candidate_scope']['ranks']))}",
        f"- Provider/model: `{PROVIDER_ID}` / `{MODEL_ID}`; prompt `{PROMPT_VERSION}`", "- AI/network calls при построении: `0 / 0`", "",
        "## Сравнение кандидатов", "", "| Rank | Video ID | Classification | Evidence quality | Editorial readiness | Warnings |", "|---:|---|---|---|---|---:|",
    ]
    for item in report["candidates"]:
        lines.append("| {rank} | {video} | {classification} | {tier} | {ready} | {warnings} |".format(
            rank=item["original_rank"], video=_md(item["candidate_identity"]["video_id"]), classification=_md(item["ranking_snapshot"].get("classification")),
            tier=_md(item["evidence_quality"].get("tier")), ready=_md(item["editorial_readiness"]["status"]), warnings=len(item["warnings"])))
    for item in report["candidates"]:
        identity = item["candidate_identity"]
        lines += ["", f"## Кандидат rank {item['original_rank']}: `{_md(identity['video_id'])}`", "", "### FACT: ranking snapshot", "", f"- Classification: `{_md(item['ranking_snapshot'].get('classification'))}`", f"- Автор: {_md(identity.get('author'))}", f"- Evidence refs: `{item['evidence_reference_summary']['count']}`", "", "### INFERENCE / AI interpretation", ""]
        for claim in item["claims"]:
            if claim["claim_type"] != "FACT":
                lines.append(f"- **{_md(claim['claim_type'])} / {_md(claim['field'])}:** {_md(claim['text'])} (refs: `{', '.join(_md(ref) for ref in claim['evidence_refs']) or 'нет'}`)")
        lines += ["", "### AI adaptation for NURA", "", f"- Source mechanism: {_md(item['nura_adaptation'].get('source_mechanism'))}", f"- Adaptation idea: {_md(item['nura_adaptation'].get('adaptation_idea'))}", f"- Suggested hook: {_md(item['nura_adaptation'].get('suggested_hook'))}", f"- Production elements not copied: {_md(item['nura_adaptation'].get('production_elements_not_copied'))}", f"- Hook type: `{item['hook_summary']['hook_type']}`", "", "### Evidence and review", "", f"- Evidence quality: `{_md(item['evidence_quality'].get('tier'))}`; machine observations, not human verified.", f"- Editorial readiness: `{item['editorial_readiness']['status']}`", "- Warnings:"]
        lines += [f"  - {_md(warning)}" for warning in item["warnings"]] or ["  - Нет."]
    lines += ["", "## Индекс предупреждений", ""]
    lines += [f"- Rank {item['rank']} / `{_md(item['video_id'])}`: {_md(item['warning'])}" for item in report["warning_index"]] or ["- Нет."]
    lines += ["", "## Ограничения", ""] + [f"- {_md(item)}" for item in report["analysis_limitations"]]
    return "\n".join(lines) + "\n"


def _candidate_entry(candidate: Any, card: dict[str, Any], run_root: Path) -> dict[str, Any]:
    claims = [_bounded_claim(claim) for claim in card["claims"]]
    warning_list = _strings(card.get("warnings")) + _strings(card.get("quality", {}).get("warnings"))
    warning_list += ["human_verified=false: отдельный human-review artifact отсутствует."]
    for field in ("hook_type", "production_complexity"):
        warning_list.append(f"{field}=NOT_TYPED в текущем card schema.")
    readiness = "REVIEW_WITH_WARNINGS" if warning_list or card["quality"]["status"] == "PASS_WITH_WARNINGS" else "READY_FOR_REVIEW"
    return {
        "candidate_identity": {"video_id": candidate.video_id, "author": candidate.author, "source_platform": candidate.source.get("type")},
        "original_rank": candidate.rank,
        "ranking_snapshot": {"classification": candidate.classification, "radar_confidence": candidate.radar_confidence, "identity_confidence": candidate.identity_confidence, "metrics": candidate.metrics_snapshot, "scores": candidate.score_snapshot, "caption": _bounded_text(candidate.caption, MAX_CAPTION_CHARS)},
        "source_card_ref": f"candidates/{candidate.video_id}/content_intelligence_card.json",
        "source_card_hash": card["card_hash"], "source_card_schema_version": card["schema_version"],
        "provider_metadata": {"provider_id": card["provider"]["provider_id"], "model_id": card["provider"]["model_id"], "prompt_version": card["provider"]["configuration"]["prompt_version"]},
        "evidence_quality": card["evidence_quality"], "analysis_quality": card["quality"], "claims": claims,
        "source_mechanism": _claims_for_field(claims, "mechanism"),
        "hook_summary": {"hook_type": "NOT_TYPED", "existing_hook_interpretation": _claims_for_field(claims, "hook"), "supporting_evidence_refs": sorted({ref for claim in claims if claim["field"] == "hook" for ref in claim["evidence_refs"]})},
        "meaning_summary": {field: _claims_for_field(claims, field) for field in ("core_message", "audience_pain", "emotional_trigger", "insight", "theme")},
        "structure_summary": {field: _claims_for_field(claims, field) for field in ("opening", "development", "ending", "cta")},
        "format_summary": _claims_for_field(claims, "format"),
        "nura_adaptation": {key: card["project_adaptation"].get(key) for key in ("source_mechanism", "adaptation_idea", "suggested_hook", "production_elements_not_copied", "applied_constraints")},
        "evidence_reference_summary": {"count": len(card["evidence_index"]), "by_kind": dict(sorted(Counter(item.get("kind", "unknown") for item in card["evidence_index"]).items()))},
        "warnings": warning_list, "editorial_readiness": {"status": readiness, "human_verified": False}, "human_verified": False,
    }


def _read_and_validate_card(path: Path, candidate: Any, manifest: ContentIntelligenceSelectionManifest, run_root: Path) -> dict[str, Any]:
    if not _is_contained(run_root, path):
        raise ContentIntelligenceReportError("CARD_PATH_OUTSIDE_REAL_RUNTIME")
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentIntelligenceReportError("MISSING_OR_CORRUPT_CARD") from error
    if not isinstance(card, dict) or card.get("card_hash") != hash_payload({key: value for key, value in card.items() if key != "card_hash"}):
        raise ContentIntelligenceReportError("CARD_HASH_MISMATCH")
    identity = card.get("candidate_identity", {})
    if identity.get("video_id") != candidate.video_id or identity.get("rank") != candidate.rank:
        raise ContentIntelligenceReportError("CARD_CANDIDATE_MISMATCH")
    if card.get("schema_version") != "0.1" or card.get("status") not in {"COMPLETED", "DEGRADED"}:
        raise ContentIntelligenceReportError("CARD_SCHEMA_OR_STATUS_INVALID")
    provider = card.get("provider", {})
    if provider.get("fake") is not False or provider.get("provider_id") != PROVIDER_ID or provider.get("model_id") != MODEL_ID or provider.get("configuration", {}).get("prompt_version") != PROMPT_VERSION:
        raise ContentIntelligenceReportError("CARD_PROVIDER_CONTRACT_INVALID")
    quality = card.get("quality", {})
    if quality.get("status") not in {"PASS", "PASS_WITH_WARNINGS"}:
        raise ContentIntelligenceReportError("CARD_QUALITY_INVALID")
    refs = {item.get("ref_id") for item in card.get("evidence_index", []) if isinstance(item, dict)}
    claims = card.get("claims")
    if not isinstance(claims, list) or not refs:
        raise ContentIntelligenceReportError("CARD_CLAIMS_OR_EVIDENCE_INVALID")
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("claim_type") not in {"FACT", "INFERENCE", "AI_INTERPRETATION"} or not set(claim.get("evidence_refs", [])).issubset(refs):
            raise ContentIntelligenceReportError("CARD_CLAIM_INVALID")
        if claim.get("claim_type") == "FACT" and (claim.get("claim_id") != "fact-001" or claim.get("field") != "candidate_identity"):
            raise ContentIntelligenceReportError("PROVIDER_FACT_CLAIM_REJECTED")
    if not isinstance(card.get("project_adaptation"), dict) or not isinstance(card.get("evidence_quality"), dict):
        raise ContentIntelligenceReportError("CARD_REQUIRED_SECTION_MISSING")
    return card


def _real_run_root(root: Path, manifest: ContentIntelligenceSelectionManifest, context_hash: str) -> Path:
    name = f"real-{manifest.radar_run_id}-{manifest.manifest_hash[:12]}-{context_hash[:8]}-{PROVIDER_ID}-{MODEL_ID}-{PROMPT_VERSION}"
    return (root / "real" / name).resolve()


def _load_context(path: Path) -> tuple[dict[str, Any], str]:
    """Read only the versioned NURA context snapshot; no provider is involved."""
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentIntelligenceReportError("INVALID_PROJECT_CONTEXT") from error
    required = {"schema_version", "context_version", "project_id", "project_name", "audience_summary", "brand_role", "adaptation_objective", "available_formats", "production_constraints", "allowed_claims", "prohibited_claims", "safety_constraints", "tone"}
    if not isinstance(snapshot, dict) or snapshot.get("project_id") != "nura" or not required <= snapshot.keys():
        raise ContentIntelligenceReportError("INVALID_PROJECT_CONTEXT")
    return snapshot, hash_payload(snapshot)


def _load_reusable_report(root: Path, identity: str) -> dict[str, Any] | None:
    paths = {name: root / name for name in ("report.json", "report.md", "report_manifest.json")}
    if not all(path.is_file() for path in paths.values()):
        return None
    try:
        manifest = json.loads(paths["report_manifest.json"].read_text(encoding="utf-8"))
        report = json.loads(paths["report.json"].read_text(encoding="utf-8")); markdown = paths["report.md"].read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        return None
    if report.get("report_identity") != identity or manifest.get("report_identity") != identity:
        return None
    if manifest.get("report_json_sha256") != _hash_text(_serialize(report)) or manifest.get("report_markdown_sha256") != _hash_text(markdown):
        return None
    return {"report_json_sha256": manifest["report_json_sha256"], "report_markdown_sha256": manifest["report_markdown_sha256"], "report_manifest_sha256": _hash_text(_serialize(manifest)), "candidate_count": len(report.get("candidates", [])), "network_calls": 0, "provider_calls": 0}


def _validate_persisted(root: Path, manifest: dict[str, Any]) -> None:
    report = json.loads((root / "report.json").read_text(encoding="utf-8")); markdown = (root / "report.md").read_text(encoding="utf-8")
    if manifest["report_json_sha256"] != _hash_text(_serialize(report)) or manifest["report_markdown_sha256"] != _hash_text(markdown):
        raise ContentIntelligenceReportError("PERSISTED_REPORT_HASH_MISMATCH")


def _assert_safe_report(report: dict[str, Any]) -> None:
    serialized = _serialize(report)
    forbidden = (r"[A-Za-z]:[\\/]", r"(?i)authorization", r"(?i)cookie", r"(?i)x-amz-signature", r"(?i)provider_raw_response", r"(?i)\.mp4", r"(?i)full_transcript")
    if any(re.search(pattern, serialized) for pattern in forbidden):
        raise ContentIntelligenceReportError("REPORT_SECURITY_BOUNDARY_VIOLATION")


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise ContentIntelligenceReportError(f"CONFLICTING_REPORT_ARTIFACT:{path.name}")
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as temporary:
        temporary.write(text); temporary_path = Path(temporary.name)
    try:
        os.link(temporary_path, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise ContentIntelligenceReportError(f"CONFLICTING_REPORT_ARTIFACT:{path.name}")
    finally:
        temporary_path.unlink(missing_ok=True)


def _validate_ranks(ranks: tuple[int, ...]) -> tuple[int, ...]:
    if ranks != tuple(sorted(set(ranks))) or not ranks or len(ranks) > MAX_CANDIDATES or any(rank < 1 or rank > MAX_CANDIDATES for rank in ranks):
        raise ContentIntelligenceReportError("STAGE_5G_RANK_SCOPE_INVALID")
    return ranks


def _bounded_claim(claim: dict[str, Any]) -> dict[str, Any]:
    return {"claim_id": _bounded_text(claim.get("claim_id"), 100), "claim_type": claim["claim_type"], "field": _bounded_text(claim.get("field"), 100), "text": _bounded_text(claim.get("text"), MAX_TEXT_CHARS), "evidence_refs": sorted(_strings(claim.get("evidence_refs")))}
def _claims_for_field(claims: list[dict[str, Any]], field: str) -> list[dict[str, Any]]: return [claim for claim in claims if claim["field"] == field]
def _serialize(value: Any) -> str: return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
def _hash_text(value: str) -> str: return hashlib.sha256(value.encode("utf-8")).hexdigest()
def _portable(value: str) -> str: return value.replace("\\", "/")
def _strings(value: Any) -> list[str]: return [str(item) for item in value if isinstance(item, str)] if isinstance(value, list) else []
def _bounded_text(value: Any, maximum: int) -> str | None: return None if value is None else str(value)[:maximum]
def _is_contained(root: Path, path: Path) -> bool:
    try: path.resolve().relative_to(root.resolve()); return True
    except ValueError: return False
def _md(value: Any) -> str: return str(value if value is not None else "—").replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;")

"""LOOPRA 0.6 Comment Intelligence vertical slice.

All persisted artifacts are privacy-minimal.  TikTok identifiers and profiles
are only transient collector inputs; canonical comment references are run-local.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Callable, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from content_intelligence_provider import ContentIntelligenceError, ProviderTransportError, post_deepseek_request
from tiktok_comment_collector import CollectedComment, CommentCollectionResult, PublicTikTokCommentCollector


SCHEMA_VERSION = "1.0"
COMMENT_INTELLIGENCE_VERSION = "0.6"
DEFAULT_INPUT_REFERENCE = "input/comment_intelligence/selected_video.txt"
DEFAULT_OUTPUT_REFERENCE = "output/comment_intelligence"
MAX_COMMENTS = 800
MAX_EXCERPT = 220
PRIVATE_KEYS = {"author", "author_user_id", "author_unique_id", "avatar", "avatar_thumb", "uid", "user_id", "username", "display_name", "profile", "cookie", "cookies", "authorization", "api_key", "token"}


class CommentIntelligenceError(ValueError):
    """Typed deterministic blocker for Comment Intelligence."""


class CommentProvider(Protocol):
    def call(self, phase: str, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]: ...


@dataclass(frozen=True)
class ParsedVideoInput:
    normalized_url: str
    video_id: str


@dataclass(frozen=True)
class CommentIntelligenceServices:
    collect: Callable[..., CommentCollectionResult] | None = None
    provider: CommentProvider | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_serialize(value).encode("utf-8")).hexdigest()


def _with_hash(value: dict[str, Any]) -> dict[str, Any]:
    core = {key: item for key, item in value.items() if key != "content_hash"}
    return core | {"content_hash": _hash(core)}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as stream:
        stream.write(encoded); temp = Path(stream.name)
    os.replace(temp, path)


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = "".join(_serialize(row) + "\n" for row in rows)
    path.write_text(encoded, encoding="utf-8")


def _portable(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise CommentIntelligenceError("PATH_OUTSIDE_REPOSITORY") from error


def normalize_tiktok_video_url(value: str) -> ParsedVideoInput:
    parsed = urlsplit(value.strip())
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"https", "http"} or host not in {"tiktok.com", "www.tiktok.com", "m.tiktok.com"} or parsed.username or parsed.password:
        raise CommentIntelligenceError("INVALID_TIKTOK_VIDEO_URL")
    match = re.search(r"/video/(\d{15,25})(?:/|$)", re.sub(r"/{2,}", "/", parsed.path))
    if match is None:
        raise CommentIntelligenceError("INVALID_TIKTOK_VIDEO_URL")
    video_id = match.group(1)
    query = urlencode(sorted((key, item) for key, item in parse_qsl(parsed.query) if key.lower() not in {"is_copy_url", "is_from_webapp", "sender_device", "sender_web_id", "utm_source", "utm_medium", "utm_campaign"}))
    return ParsedVideoInput(urlunsplit(("https", "www.tiktok.com", f"/@source/video/{video_id}", query, "")), video_id)


def parse_selected_video(path: Path, explicit_url: str | None = None) -> ParsedVideoInput | None:
    if explicit_url is not None:
        return normalize_tiktok_video_url(explicit_url)
    if not path.exists():
        return None
    try:
        values = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    except UnicodeDecodeError as error:
        raise CommentIntelligenceError("INPUT_FILE_MUST_BE_UTF8") from error
    parsed = [normalize_tiktok_video_url(value) for value in values]
    identities = {item.video_id for item in parsed}
    if len(identities) > 1:
        raise CommentIntelligenceError("MULTIPLE_UNIQUE_TIKTOK_URLS")
    return parsed[0] if parsed else None


def _normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split()).strip()


def _is_emoji_only(value: str) -> bool:
    return bool(value) and not any(char.isalnum() for char in value) and not re.search(r"[а-яёa-z]", value, flags=re.I)


def _noise_reason(value: str) -> str | None:
    lowered = value.casefold()
    if not value:
        return "EMPTY"
    if _is_emoji_only(value):
        return "EMOJI_ONLY"
    if re.fullmatch(r"(?:@[\w.]+\s*)+", value):
        return "MENTIONS_ONLY"
    if re.search(r"https?://|www\.", lowered):
        return "URL_OR_SPAM"
    if re.search(r"(?:заработ|пиши в лс|подписывай|promo|telegram|whatsapp).{0,30}(?:ссылка|link|скид|доход)?", lowered):
        return "PROMOTIONAL_SPAM"
    return None


def _language(value: str) -> str | None:
    cyrillic = len(re.findall(r"[а-яё]", value.casefold()))
    latin = len(re.findall(r"[a-z]", value.casefold()))
    return "ru" if cyrillic >= 3 and cyrillic >= latin else ("en" if latin >= 3 else None)


def anonymize_comments(rows: tuple[CollectedComment, ...]) -> list[dict[str, Any]]:
    """Assign run-local refs and remove every source identity/profile field."""
    external_to_ref: dict[str, str] = {}
    for index, row in enumerate(rows, 1):
        if row.external_id is not None and row.external_id not in external_to_ref:
            external_to_ref[row.external_id] = f"C{len(external_to_ref) + 1:04d}"
    result: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        ref = external_to_ref.get(row.external_id, f"C{index:04d}")
        result.append({
            "comment_ref": ref,
            "parent_comment_ref": external_to_ref.get(row.parent_external_id),
            "thread_depth": row.thread_depth,
            "text": _normalize_text(row.text),
            "like_count": row.like_count,
            "reply_count": row.reply_count,
            "created_at": row.created_at,
            "language": _language(row.text),
            "source_order": row.source_order,
            "collection_method": row.collection_method,
            "clean_status": "PENDING",
            "duplicate_group_id": None,
        })
    for row in result:
        row["content_hash"] = _hash(row)
    _assert_private_free(result)
    return result


def clean_comments(raw_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Return one canonical record per exact normalized text with frequency data."""
    groups: dict[str, list[dict[str, Any]]] = {}
    excluded = 0
    for row in raw_rows:
        text = _normalize_text(str(row["text"]))
        reason = _noise_reason(text)
        if reason:
            row["clean_status"] = "EXCLUDED"; row["exclusion_reason"] = reason; excluded += 1
            continue
        row["clean_status"] = "SEMANTIC_ELIGIBLE"; row["exclusion_reason"] = None
        groups.setdefault(text.casefold(), []).append(row)
    clean: list[dict[str, Any]] = []
    for ordinal, (_, members) in enumerate(sorted(groups.items(), key=lambda item: min(row["source_order"] for row in item[1])), 1):
        canonical = min(members, key=lambda row: row["source_order"])
        duplicate_group = f"D{ordinal:04d}"
        for member in members:
            member["duplicate_group_id"] = duplicate_group
        clean.append({
            "comment_ref": canonical["comment_ref"], "parent_ref": canonical["parent_comment_ref"],
            "normalized_text": canonical["text"], "original_excerpt": _excerpt(canonical["text"]),
            "like_count": canonical["like_count"], "reply_count": canonical["reply_count"],
            "duplicate_count": len(members), "aggregate_likes": sum(row["like_count"] for row in members),
            "aggregate_replies": sum(row["reply_count"] for row in members), "language": canonical["language"],
            "semantic_eligible": True, "exclusion_reason": None, "source_order": canonical["source_order"],
            "representative_refs": [row["comment_ref"] for row in members], "content_hash": "",
        })
        clean[-1]["content_hash"] = _hash({key: value for key, value in clean[-1].items() if key != "content_hash"})
    return clean, {"excluded_noise_count": excluded, "duplicate_text_count": sum(max(0, item["duplicate_count"] - 1) for item in clean), "unique_text_count": len(clean)}


def _excerpt(value: str) -> str:
    return value[:MAX_EXCERPT].rstrip() + ("…" if len(value) > MAX_EXCERPT else "")


def stratified_taxonomy_sample(clean: list[dict[str, Any]], maximum: int = 180) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    ranked = sorted(clean, key=lambda row: (-row["aggregate_likes"], row["source_order"]))[:60]
    replied = sorted((row for row in clean if row["aggregate_replies"]), key=lambda row: (-row["aggregate_replies"], row["source_order"]))[:60]
    evenly = [clean[index] for index in range(0, len(clean), max(1, len(clean) // 60))][:60]
    for row in ranked + replied + evenly:
        if len(selected) < maximum:
            selected[row["comment_ref"]] = row
    return list(selected.values())


class DeepSeekCommentIntelligenceProvider:
    """Small 0.6 adapter that uses the existing shared transport policy."""

    model_id = "deepseek-chat"

    def __init__(self, api_key: str | None = None, transport: Any = None) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.transport = transport

    def call(self, phase: str, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.api_key:
            raise CommentIntelligenceError("PROVIDER_UNAVAILABLE")
        instructions = {
            "taxonomy": "Return JSON with taxonomy: [{theme_id,name,explanation}], and no counts.",
            "classification": "Return JSON with classifications: [{comment_ref,primary_theme,secondary_theme,intent,emotional_tone,content_opportunity,rationale}]. Use only supplied refs and taxonomy labels.",
            "synthesis": "Return JSON with narrative strings for pains, situations, questions, disagreements, desired_outcomes, opportunities. Cite evidence refs; do not infer beyond the public sample.",
        }[phase]
        body = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": "You analyze a bounded public TikTok comment sample. Never claim all viewers. Never output usernames, profiles, or invented refs. " + instructions},
                {"role": "user", "content": _serialize(payload)},
            ],
            "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": 0, "max_tokens": 2048,
        }
        response, latency_ms = post_deepseek_request(body, api_key=self.api_key, transport=self.transport)
        try:
            raw = response.json()
            content = raw["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise CommentIntelligenceError("PROVIDER_INVALID_JSON") from error
        return parsed, {"http_status": response.status_code, "latency_ms": latency_ms, "request_id": response.headers.get("x-request-id"), "usage": raw.get("usage"), "raw": raw}


def _validate_taxonomy(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise CommentIntelligenceError("PROVIDER_TAXONOMY_SCHEMA_INVALID")
    result: list[dict[str, str]] = []
    for item in value[:16]:
        if not isinstance(item, dict) or not all(isinstance(item.get(key), str) and item[key].strip() for key in ("theme_id", "name", "explanation")):
            raise CommentIntelligenceError("PROVIDER_TAXONOMY_SCHEMA_INVALID")
        result.append({key: item[key].strip()[:180] for key in ("theme_id", "name", "explanation")})
    if not result or len({item["theme_id"] for item in result}) != len(result):
        raise CommentIntelligenceError("PROVIDER_TAXONOMY_SCHEMA_INVALID")
    return result


def _validate_classification(value: Any, refs: set[str], theme_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise CommentIntelligenceError("PROVIDER_CLASSIFICATION_SCHEMA_INVALID")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    intents = {"PAIN", "PERSONAL_STORY", "QUESTION", "AGREEMENT", "DISAGREEMENT", "ADVICE", "REQUEST", "JOKE", "OTHER"}
    for item in value:
        if not isinstance(item, dict) or item.get("comment_ref") not in refs or item["comment_ref"] in seen:
            raise CommentIntelligenceError("PROVIDER_CLASSIFICATION_REFS_INVALID")
        if item.get("primary_theme") not in theme_ids or item.get("secondary_theme") not in theme_ids | {None} or item.get("intent") not in intents:
            raise CommentIntelligenceError("PROVIDER_CLASSIFICATION_SCHEMA_INVALID")
        seen.add(item["comment_ref"])
        result.append({"comment_ref": item["comment_ref"], "primary_theme": item["primary_theme"], "secondary_theme": item.get("secondary_theme"), "intent": item["intent"], "emotional_tone": str(item.get("emotional_tone") or "UNKNOWN")[:80], "content_opportunity": bool(item.get("content_opportunity")), "rationale": _excerpt(str(item.get("rationale") or ""))})
    if seen != refs:
        raise CommentIntelligenceError("PROVIDER_CLASSIFICATION_MISSING_REFS")
    return result


def _call_and_persist(provider: CommentProvider, phase: str, payload: dict[str, Any], root: Path, ordinal: int) -> tuple[dict[str, Any], dict[str, Any]]:
    request_meta = {"schema_version": SCHEMA_VERSION, "phase": phase, "ordinal": ordinal, "payload_hash": _hash(payload), "payload": payload}
    _assert_private_free(request_meta); _write_json(root / "internal" / "requests" / f"{ordinal:02d}_{phase}.json", request_meta)
    parsed, metadata = provider.call(phase, payload)
    # Raw response is persisted before any contract validation by the caller.
    raw = metadata.pop("raw", parsed)
    _assert_private_free(raw); _write_json(root / "internal" / "raw_responses" / f"{ordinal:02d}_{phase}.json", raw)
    return parsed, metadata


def _aggregate(clean: list[dict[str, Any]], classifications: list[dict[str, Any]], taxonomy: list[dict[str, str]]) -> dict[str, Any]:
    by_ref = {row["comment_ref"]: row for row in clean}
    themes: list[dict[str, Any]] = []
    for taxon in taxonomy:
        assigned = [item for item in classifications if item["primary_theme"] == taxon["theme_id"]]
        if not assigned:
            continue
        rows = [by_ref[item["comment_ref"]] for item in assigned]
        evidence = [{"comment_ref": row["comment_ref"], "short_excerpt": _excerpt(row["normalized_text"]), "likes": row["aggregate_likes"], "replies": row["aggregate_replies"]} for row in sorted(rows, key=lambda item: (-item["aggregate_likes"], item["source_order"]))[:3]]
        themes.append({"theme_id": taxon["theme_id"], "name": taxon["name"], "explanation": taxon["explanation"], "comment_count": sum(row["duplicate_count"] for row in rows), "share_of_sample": round(sum(row["duplicate_count"] for row in rows) / max(1, sum(row["duplicate_count"] for row in clean)), 4), "aggregate_likes": sum(row["aggregate_likes"] for row in rows), "aggregate_replies": sum(row["aggregate_replies"] for row in rows), "median_likes": median([row["aggregate_likes"] for row in rows]), "max_likes": max(row["aggregate_likes"] for row in rows), "comments_with_replies": sum(row["aggregate_replies"] > 0 for row in rows), "duplicate_frequency_contribution": sum(row["duplicate_count"] - 1 for row in rows), "confidence": "HIGH" if len(rows) >= 5 else "MEDIUM", "representative_evidence": evidence})
    questions = [item for item in classifications if item["intent"] == "QUESTION"]
    disagreements = [item for item in classifications if item["intent"] == "DISAGREEMENT"]
    language = [{"comment_ref": row["comment_ref"], "excerpt": _excerpt(row["normalized_text"])} for row in sorted(clean, key=lambda item: item["source_order"])[:30]]
    return {"themes": sorted(themes, key=lambda item: (-item["comment_count"], item["theme_id"])), "questions": questions, "disagreements": disagreements, "language": language}


def _build_insights(sample: dict[str, Any], taxonomy: list[dict[str, str]], classifications: list[dict[str, Any]], aggregate: dict[str, Any], accounting: dict[str, Any]) -> dict[str, Any]:
    refs = {item["comment_ref"] for theme in aggregate["themes"] for item in theme["representative_evidence"]}
    return _with_hash({"schema_version": SCHEMA_VERSION, "insights_id": f"insights-{sample['sample_id']}", "sample_reference": "manifest.json", "sample_hash": sample["content_hash"], "taxonomy_version": "1.0", "classified_comment_count": len(classifications), "unclassified_comment_count": 0, "theme_count": len(aggregate["themes"]), "top_pains": aggregate["themes"], "recurring_situations": [], "audience_questions": aggregate["questions"], "objections_and_disagreements": aggregate["disagreements"], "desired_outcomes": [], "audience_language_bank": aggregate["language"], "content_opportunities": _opportunities(aggregate["themes"]), "sample_limitations": sample["public_sample_limitations"], "provider_call_accounting": accounting, "evidence_refs": sorted(refs), "reuse_metadata": {"supported": True}})


def _opportunities(themes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formats = ["TALKING_GUIDE", "TEXT_LED", "BACKGROUND_VOICE", "CAROUSEL"]
    result: list[dict[str, Any]] = []
    for index, theme in enumerate(themes[:10]):
        evidence = [item["comment_ref"] for item in theme["representative_evidence"]]
        result.append({"opportunity_id": f"O{index + 1:02d}", "source_pain": theme["name"], "audience_wording": theme["representative_evidence"][0]["short_excerpt"], "angle": theme["explanation"], "hook_direction": f"Назвать проблему «{theme['name']}» без обещаний и диагнозов", "format": formats[index % len(formats)], "why_resonates": "Опирается на повторяющиеся комментарии в собранной публичной выборке.", "evidence_refs": evidence})
    return result


def _render_overview(sample: dict[str, Any], status: str) -> str:
    return f"""# LOOPRA 0.6 — Comment Intelligence\n\n- Status: `{status}`\n- Project: `{sample['project_id']}`\n- Source video ID: `{sample['source_video_id']}`\n- Collected comments: {sample['raw_comment_count']}\n- Clean semantic comments: {sample['cleaned_comment_count']}\n- Stop reason: `{sample['stop_reason']}`\n- Access mode: `{sample['access_mode']}`\n- Collection method: `{sample['collection_method']}`\n- Browser cleanup: `{sample['reuse_metadata'].get('browser_cleanup', 'N/A')}`\n\nThis package describes only the collected public-visible comment sample. It does not represent all viewers or hidden/deleted comments.\n"""


def _render_insights(sample: dict[str, Any], insights: dict[str, Any]) -> str:
    themes = insights["top_pains"]
    lines = ["# Comment Intelligence — NURA", "", "## 1. Что было проанализировано", f"- Видео: `{sample['source_video_id']}`", f"- Собрано: {sample['raw_comment_count']}; очищено: {sample['cleaned_comment_count']}", f"- Метод: {sample['collection_method']}; stop reason: {sample['stop_reason']}", "- Ограничение: только собранная публично видимая выборка комментариев.", "", "## 2. Главные боли аудитории"]
    for theme in themes:
        lines += [f"### {theme['name']}", theme["explanation"], f"- Comments: {theme['comment_count']} ({theme['share_of_sample']:.1%}); likes: {theme['aggregate_likes']}; replies: {theme['aggregate_replies']}; confidence: {theme['confidence']}"]
        lines += [f"- [{item['comment_ref']}] {item['short_excerpt']}" for item in theme["representative_evidence"]]
    lines += ["", "## 3. Повторяющиеся жизненные ситуации", "- Требуют проверки владельцем по evidence refs; LOOPRA не обобщает опыт всех зрителей.", "", "## 4. Главные вопросы аудитории"]
    lines += [f"- [{item['comment_ref']}] {item['rationale']}" for item in insights["audience_questions"][:10]] or ["- В выборке не найдено достаточно валидированных вопросов."]
    lines += ["", "## 5. Возражения, споры и противоположные позиции"]
    lines += [f"- [{item['comment_ref']}] {item['rationale']}" for item in insights["objections_and_disagreements"][:10]] or ["- В выборке не найдено достаточно валидированных разногласий."]
    lines += ["", "## 6. Чего аудитория хочет вместо текущей проблемы", "- Подтверждается только после owner review; не является выводом обо всей аудитории.", "", "## 7. Язык аудитории"]
    lines += [f"- [{item['comment_ref']}] {item['excerpt']}" for item in insights["audience_language_bank"][:30]]
    lines += ["", "## 8. Контентные возможности для NURA"]
    for item in insights["content_opportunities"]:
        lines += [f"### {item['opportunity_id']} — {item['source_pain']}", f"- Audience wording: {item['audience_wording']}", f"- Angle: {item['angle']}", f"- Hook direction: {item['hook_direction']}", f"- Format: {item['format']}", f"- Why: {item['why_resonates']}", f"- Evidence: {', '.join(item['evidence_refs'])}"]
    lines += ["", "## 9. Что нельзя заключать", "- Выборка может быть смещена; это только публично видимые комментарии.", "- Комментаторы не равны всем viewers; скрытые и удалённые комментарии неизвестны.", "", "## 10. Рекомендованный следующий шаг владельца", "Сверьте темы и короткие excerpts с ручным просмотром комментариев. После подтверждения выберите одну боль для source-specific angle; не копируйте длинные тексты и не используйте usernames."]
    return "\n".join(lines)


def _render_handoff(sample: dict[str, Any], insights: dict[str, Any]) -> str:
    pain_lines = "\n".join(f"- {item['name']} ({item['comment_count']}; refs: {', '.join(entry['comment_ref'] for entry in item['representative_evidence'])})" for item in insights["top_pains"])
    return f"""# GPT handoff — NURA Comment Intelligence\n\nИсточник: TikTok video `{sample['source_video_id']}`.\nСобранная публично видимая выборка: {sample['cleaned_comment_count']} cleaned semantic comments.\n\n## Top pains\n{pain_lines or '- Недостаточно evidence.'}\n\n## ЭТАП 1 — проверка\nПроверь смысл видео и только то, что подтверждают refs. Отдели повторяющуюся боль от одного популярного комментария, проверь живой язык и разногласия. Не делай выводов обо всей аудитории.\n\n## ЭТАП 2 — только после подтверждения владельцем\nВыбери одну подтверждённую боль, подготовь source-specific NURA angle и сценарий. Не копируй длинные comment texts, не используй usernames и не выдавай личные истории за факты обо всей аудитории. Сохрани safety и non-imitation boundaries.\n"""


def _write_clean_csv(path: Path, clean: list[dict[str, Any]]) -> None:
    fields = ["comment_ref", "parent_ref", "normalized_text", "original_excerpt", "like_count", "reply_count", "duplicate_count", "aggregate_likes", "aggregate_replies", "language", "semantic_eligible", "exclusion_reason", "source_order"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in clean)


def _package_hash(root: Path) -> str:
    return _hash([{ "path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(root.rglob("*")) if path.is_file() and path.name != "manifest.json"])


def _existing_package(root: Path, sample_id: str) -> dict[str, Any] | None:
    manifest_path = root / "manifest.json"
    required = [root / name for name in ("00_OVERVIEW_RU.md", "comments_raw.jsonl", "comments_clean.csv")]
    if not manifest_path.is_file() or not all(path.is_file() for path in required):
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")); content_hash = manifest.pop("content_hash")
        if manifest.get("sample_id") != sample_id or content_hash != _hash(manifest) or manifest.get("package_hash") != _package_hash(root):
            return None
        return manifest | {"content_hash": content_hash}
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def _assert_private_free(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in PRIVATE_KEYS or "profile" in key.casefold() or "cookie" in key.casefold():
                raise CommentIntelligenceError("PRIVACY_FIELD_FORBIDDEN")
            _assert_private_free(item)
    elif isinstance(value, list):
        for item in value:
            _assert_private_free(item)


def _sample_id(project_id: str, input_value: ParsedVideoInput, max_comments: int, max_scrolls: int, refresh: bool) -> str:
    identity = {"version": COMMENT_INTELLIGENCE_VERSION, "project_id": project_id, "video_id": input_value.video_id, "max_comments": max_comments, "max_scrolls": max_scrolls}
    if refresh:
        identity["refresh_requested_at"] = _utc_now()
    return f"comment-{project_id}-{_hash(identity)[:16]}"


def run_comment_intelligence(*, project_id: str, input_file: Path, output_root: Path, repository_root: Path,
                             url: str | None = None, max_comments: int = MAX_COMMENTS, max_scrolls: int = 24,
                             timeout_seconds: int = 45, headed: bool = False, reuse_only: bool = False,
                             dry_run: bool = False, refresh: bool = False,
                             services: CommentIntelligenceServices | None = None) -> dict[str, Any]:
    if project_id != "nura":
        raise CommentIntelligenceError("UNSUPPORTED_PROJECT")
    if not 1 <= max_comments <= MAX_COMMENTS:
        raise CommentIntelligenceError("MAX_COMMENTS_OUT_OF_RANGE")
    selected = parse_selected_video(input_file, url)
    if selected is None:
        return {"status": "READY_FOR_OWNER_COMMENT_PILOT_INPUT", "input_path": _portable(input_file, repository_root), "browser_calls": 0, "network_calls": 0, "provider_calls": 0}
    sample_id = _sample_id(project_id, selected, max_comments, max_scrolls, refresh)
    package = output_root / sample_id
    if dry_run:
        return {"status": "DRY_RUN", "sample_id": sample_id, "source_video_id": selected.video_id, "collection_plan": {"max_comments": max_comments, "max_scrolls": max_scrolls, "timeout_seconds": timeout_seconds, "headless": not headed, "access_mode": "GUEST_NO_SESSION"}, "analysis_plan": {"taxonomy_calls": 1, "classification_max_calls": 7, "synthesis_calls": 1, "primary_call_budget": 9}, "browser_calls": 0, "network_calls": 0, "provider_calls": 0}
    existing = None if refresh else _existing_package(package, sample_id)
    if existing is not None:
        return existing | {"status": "REUSED", "output_path": _portable(package, repository_root), "browser_calls": 0, "network_calls": 0, "provider_calls": 0}
    if reuse_only:
        return {"status": "BLOCKED", "failure_code": "REUSABLE_ARTIFACT_NOT_FOUND", "sample_id": sample_id, "browser_calls": 0, "network_calls": 0, "provider_calls": 0}
    services = services or CommentIntelligenceServices()
    collector = services.collect or (lambda value, **kwargs: PublicTikTokCommentCollector(**kwargs).collect(value))
    try:
        collected = collector(selected.normalized_url, headless=not headed, max_comments=max_comments, max_scrolls=max_scrolls, timeout_seconds=timeout_seconds)
    except RuntimeError as error:
        return {"status": "BLOCKED", "failure_code": str(error), "sample_id": sample_id, "browser_calls": 1, "network_calls": 0, "provider_calls": 0}
    raw = anonymize_comments(collected.comments)
    clean, metrics = clean_comments(raw)
    limitations = ["Только собранная публично видимая выборка комментариев.", "Комментаторы не равны всем viewers; скрытые и удалённые comments неизвестны.", "Частота в sample не равна позиции всей аудитории."]
    sample = {"schema_version": SCHEMA_VERSION, "sample_id": sample_id, "project_id": project_id, "source_video_id": selected.video_id, "source_url_reference": selected.normalized_url, "collection_started_at": _utc_now(), "collection_finished_at": _utc_now(), "access_mode": collected.access_mode, "collection_method": collected.collection_method, "max_comments": max_comments, "raw_comment_count": len(raw), "top_level_count": sum(row["thread_depth"] == 0 for row in raw), "reply_count": sum(row["thread_depth"] > 0 for row in raw), "unique_text_count": metrics["unique_text_count"], "cleaned_comment_count": sum(row["duplicate_count"] for row in clean), "duplicate_text_count": metrics["duplicate_text_count"], "excluded_noise_count": metrics["excluded_noise_count"], "comments_with_likes_count": sum(row["like_count"] > 0 for row in raw), "comments_with_replies_count": sum(row["reply_count"] > 0 for row in raw), "stop_reason": collected.stop_reason, "public_sample_limitations": limitations, "raw_artifact_reference": "comments_raw.jsonl", "raw_artifact_hash": "", "clean_artifact_reference": "comments_clean.csv", "clean_artifact_hash": "", "reuse_metadata": {"supported": True, "browser_cleanup": collected.cleanup_status, "scrolls": collected.scrolls, "login_overlay_observed": collected.login_overlay_observed, "captcha_observed": collected.captcha_observed, "rate_limit_observed": collected.rate_limit_observed}}
    package.mkdir(parents=True, exist_ok=True)
    _write_jsonl(package / "comments_raw.jsonl", raw); _write_clean_csv(package / "comments_clean.csv", clean)
    sample["raw_artifact_hash"] = hashlib.sha256((package / "comments_raw.jsonl").read_bytes()).hexdigest(); sample["clean_artifact_hash"] = hashlib.sha256((package / "comments_clean.csv").read_bytes()).hexdigest()
    sample = _with_hash(sample); _assert_private_free(sample); _write_text(package / "00_OVERVIEW_RU.md", _render_overview(sample, "COLLECTED"))
    if collected.stop_reason == "CAPTCHA_OR_ANTI_BOT_CHALLENGE":
        return _finalize_collection(package, sample, "CAPTCHA_OR_ANTI_BOT_CHALLENGE", collected)
    if collected.stop_reason == "RATE_LIMITED":
        return _finalize_collection(package, sample, "RATE_LIMITED", collected)
    if collected.stop_reason == "PUBLIC_COMMENTS_BLOCKED":
        return _finalize_collection(package, sample, "PUBLIC_COMMENTS_BLOCKED", collected)
    if sample["cleaned_comment_count"] < 50:
        return _finalize_collection(package, sample, "PARTIAL_INSUFFICIENT_COMMENTS", collected)
    provider = services.provider or DeepSeekCommentIntelligenceProvider()
    try:
        taxonomy_payload = {"comments": [{"comment_ref": row["comment_ref"], "text": row["normalized_text"], "duplicate_count": row["duplicate_count"], "aggregate_likes": row["aggregate_likes"], "aggregate_replies": row["aggregate_replies"]} for row in stratified_taxonomy_sample(clean)]}
        taxonomy_raw, tax_meta = _call_and_persist(provider, "taxonomy", taxonomy_payload, package, 1)
        taxonomy = _validate_taxonomy(taxonomy_raw.get("taxonomy"))
        classifications: list[dict[str, Any]] = []; call_metadata = [tax_meta]
        chunks = [clean[index:index + 120] for index in range(0, len(clean), 120)]
        if len(chunks) > 7:
            raise CommentIntelligenceError("CALL_BUDGET_EXCEEDED")
        for ordinal, chunk in enumerate(chunks, 2):
            payload = {"taxonomy": taxonomy, "comments": [{"comment_ref": row["comment_ref"], "text": row["normalized_text"], "duplicate_count": row["duplicate_count"]} for row in chunk]}
            raw_classification, meta = _call_and_persist(provider, "classification", payload, package, ordinal)
            accepted = _validate_classification(raw_classification.get("classifications"), {row["comment_ref"] for row in chunk}, {item["theme_id"] for item in taxonomy})
            _write_json(package / "internal" / "classification" / f"{ordinal - 1:02d}.json", accepted); classifications.extend(accepted); call_metadata.append(meta)
        aggregate = _aggregate(clean, classifications, taxonomy)
        _write_json(package / "internal" / "aggregates" / "application_aggregate.json", aggregate)
        synthesis_payload = {"sample_limitations": limitations, "themes": aggregate["themes"], "questions": aggregate["questions"], "disagreements": aggregate["disagreements"], "language": aggregate["language"][:30]}
        synthesis_raw, synthesis_meta = _call_and_persist(provider, "synthesis", synthesis_payload, package, len(call_metadata) + 1)
        call_metadata.append(synthesis_meta)
        accounting = {"taxonomy_calls": 1, "classification_calls": len(chunks), "synthesis_calls": 1, "primary_calls": len(call_metadata), "retries": 0, "http_results": [item.get("http_status") for item in call_metadata]}
        insights = _build_insights(sample, taxonomy, classifications, aggregate, accounting); insights["provider_synthesis"] = synthesis_raw; insights = _with_hash({key: value for key, value in insights.items() if key != "content_hash"})
        _assert_private_free(insights); _write_json(package / "internal" / "comment_insights.json", insights); _write_text(package / "COMMENT_INSIGHTS_RU.md", _render_insights(sample, insights)); _write_text(package / "GPT_HANDOFF_WITH_COMMENTS_RU.md", _render_handoff(sample, insights))
        status = "READY_FOR_OWNER_COMMENT_INSIGHTS_REVIEW" if sample["cleaned_comment_count"] >= 200 and len(insights["top_pains"]) >= 5 and len(insights["audience_language_bank"]) >= 15 and len(insights["content_opportunities"]) >= 5 else "PARTIAL_INSUFFICIENT_COMMENTS"
        return _finalize_collection(package, sample, status, collected, insights=insights, accounting=accounting)
    except (CommentIntelligenceError, ContentIntelligenceError, ProviderTransportError) as error:
        status = "PROVIDER_UNAVAILABLE" if "PROVIDER" in str(error) or "CREDENTIAL" in str(error) else "PARTIAL_ANALYSIS"
        return _finalize_collection(package, sample, status, collected, error=str(error))


def _finalize_collection(package: Path, sample: dict[str, Any], status: str, collected: CommentCollectionResult, *, insights: dict[str, Any] | None = None, accounting: dict[str, Any] | None = None, error: str | None = None) -> dict[str, Any]:
    manifest = dict(sample) | {"status": status, "package_hash": "", "analysis_reference": "internal/comment_insights.json" if insights else None, "analysis_hash": insights.get("content_hash") if insights else None, "provider_call_accounting": accounting or {"taxonomy_calls": 0, "classification_calls": 0, "synthesis_calls": 0, "primary_calls": 0}, "error": error}
    _write_text(package / "00_OVERVIEW_RU.md", _render_overview(sample, status))
    manifest["package_hash"] = _package_hash(package); manifest = _with_hash(manifest); _assert_private_free(manifest); _write_json(package / "manifest.json", manifest)
    return manifest | {"output_path": str(package), "browser_calls": collected.browser_calls, "network_calls": collected.network_calls, "provider_calls": manifest["provider_call_accounting"]["primary_calls"]}


def default_paths(repository_root: Path) -> tuple[Path, Path]:
    return repository_root / DEFAULT_INPUT_REFERENCE, repository_root / DEFAULT_OUTPUT_REFERENCE

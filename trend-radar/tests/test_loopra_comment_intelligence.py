from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "trend-radar" / "src"))

from comment_intelligence import (  # noqa: E402
    CommentIntelligenceError, CommentIntelligenceServices, anonymize_comments,
    clean_comments, normalize_tiktok_video_url, parse_selected_video,
    run_comment_intelligence, stratified_taxonomy_sample,
)
from tiktok_comment_collector import (  # noqa: E402
    CommentCollectionResult, CollectedComment, DOM, NETWORK_RESPONSE,
    classify_page_signals, extract_comments_from_dom, extract_comments_from_response,
)


class FakeProvider:
    def __init__(self): self.calls: list[str] = []

    def call(self, phase: str, payload: dict):
        self.calls.append(phase)
        if phase == "taxonomy":
            return {"taxonomy": [{"theme_id": key, "name": key.title(), "explanation": f"Повторяющаяся тема {key}."} for key in ("sleep", "anxiety", "money", "boundaries", "routine")]}, {"http_status": 200, "raw": {"phase": phase}}
        if phase == "classification":
            values = []
            for item in payload["comments"]:
                text = item["text"].casefold()
                theme = next((key for key in ("sleep", "anxiety", "money", "boundaries", "routine") if key in text), "routine")
                intent = "QUESTION" if "?" in text else ("DISAGREEMENT" if "не соглас" in text else "PAIN")
                values.append({"comment_ref": item["comment_ref"], "primary_theme": theme, "secondary_theme": None, "intent": intent, "emotional_tone": "TENSE", "content_opportunity": intent == "PAIN", "rationale": item["text"][:80]})
            return {"classifications": values}, {"http_status": 200, "raw": {"phase": phase}}
        return {"narrative": "Только собранная публичная выборка."}, {"http_status": 200, "raw": {"phase": phase}}


def _collected(count: int = 300) -> CommentCollectionResult:
    themes = ("sleep", "anxiety", "money", "boundaries", "routine")
    rows = []
    for index in range(count):
        theme = themes[index % len(themes)]
        suffix = index // len(themes)
        text = f"{theme} pain {suffix}"
        if index % 31 == 0: text += "?"
        if index % 47 == 0: text += " не соглас"
        rows.append(CollectedComment(str(index + 1), str(index) if index % 20 == 1 else None, 1 if index % 20 == 1 else 0, text, 1 if index != 2 else 9000, 1 if index % 11 == 0 else 0, None, index + 1, NETWORK_RESPONSE))
    rows += [CollectedComment("spam", None, 0, "🔥🔥", 0, 0, None, count + 1, DOM), CollectedComment("ad", None, 0, "telegram ссылка https://example.test", 0, 0, None, count + 2, DOM)]
    return CommentCollectionResult(tuple(rows), "GUEST_NO_SESSION", "MIXED", "MAX_COMMENTS", 1, 4, "PASS", True, False, False, 5)


def _collect(url: str, **kwargs) -> CommentCollectionResult:
    assert url.startswith("https://www.tiktok.com/@source/video/")
    assert kwargs["max_comments"] <= 800
    return _collected()


def _run(tmp_path: Path, **kwargs):
    input_file = tmp_path / "selected_video.txt"; input_file.write_text("https://www.tiktok.com/@person/video/1234567890123456789\n", encoding="utf-8")
    return run_comment_intelligence(project_id="nura", input_file=input_file, output_root=tmp_path / "out", repository_root=tmp_path, services=CommentIntelligenceServices(collect=_collect, provider=FakeProvider()), **kwargs)


def test_input_url_parsing_and_tiktok_video_id_extraction(tmp_path: Path) -> None:
    value = normalize_tiktok_video_url("https://m.tiktok.com/@user/video/1234567890123456789?utm_source=x")
    assert value.video_id == "1234567890123456789" and value.normalized_url.startswith("https://www.tiktok.com/@source/video/")
    path = tmp_path / "input.txt"; path.write_text("\ufeff# a\n\nhttps://www.tiktok.com/@x/video/1234567890123456789\n", encoding="utf-8")
    assert parse_selected_video(path).video_id == value.video_id


def test_multiple_urls_and_invalid_url_are_typed_blockers(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"; path.write_text("https://www.tiktok.com/@x/video/1234567890123456789\nhttps://www.tiktok.com/@x/video/2234567890123456789\n", encoding="utf-8")
    with pytest.raises(CommentIntelligenceError, match="MULTIPLE_UNIQUE"):
        parse_selected_video(path)
    with pytest.raises(CommentIntelligenceError, match="INVALID"):
        normalize_tiktok_video_url("https://example.test/video/1")


def test_guest_collection_contract_and_login_overlay_do_not_block_visible_comments() -> None:
    assert classify_page_signals(url="https://www.tiktok.com", text="login", visible_comment_count=2) is None
    assert classify_page_signals(url="https://www.tiktok.com", text="captcha", visible_comment_count=0) == "CAPTCHA_OR_ANTI_BOT_CHALLENGE"
    assert _collected().access_mode == "GUEST_NO_SESSION"


def test_network_response_and_dom_fallback_extraction_preserve_minimal_fields() -> None:
    network = extract_comments_from_response({"comments": [{"cid": "a", "text": "one", "digg_count": 2, "reply_comment": [{"cid": "b", "text": "reply"}]}]})
    dom = extract_comments_from_dom([{"id": "c", "text": "three", "like_count": "3"}])
    assert [item.text for item in network] == ["one", "reply"]
    assert network[1].parent_external_id == "a" and dom[0].collection_method == DOM


def test_anonymization_removes_source_ids_and_preserves_parent_relationships() -> None:
    raw = anonymize_comments(tuple([CollectedComment("100", None, 0, "parent", 0, 1, None, 1, NETWORK_RESPONSE), CollectedComment("101", "100", 1, "reply", 0, 0, None, 2, NETWORK_RESPONSE)]))
    assert raw[0]["comment_ref"] == "C0001" and raw[1]["parent_comment_ref"] == "C0001"
    assert "100" not in json.dumps(raw) and "username" not in json.dumps(raw)


def test_cleaning_unicode_noise_spam_and_duplicate_frequency() -> None:
    raw = anonymize_comments(tuple([CollectedComment("1", None, 0, "  Тест\u00a0боли  ", 1, 0, None, 1, DOM), CollectedComment("2", None, 0, "Тест боли", 2, 1, None, 2, DOM), CollectedComment("3", None, 0, "😀", 0, 0, None, 3, DOM), CollectedComment("4", None, 0, "https://spam.test", 0, 0, None, 4, DOM)]))
    clean, metrics = clean_comments(raw)
    assert clean[0]["duplicate_count"] == 2 and clean[0]["aggregate_likes"] == 3
    assert metrics["excluded_noise_count"] == 2 and clean[0]["normalized_text"] == "Тест боли"


def test_stratified_sample_is_bounded_and_deduplicated() -> None:
    raw = anonymize_comments(_collected(250).comments)
    clean, _ = clean_comments(raw)
    sample = stratified_taxonomy_sample(clean, maximum=50)
    assert len(sample) <= 50 and len({row["comment_ref"] for row in sample}) == len(sample)


def test_offline_acceptance_writes_evidence_backed_package_and_application_counts(tmp_path: Path) -> None:
    result = _run(tmp_path)
    package = Path(result["output_path"])
    assert result["status"] == "READY_FOR_OWNER_COMMENT_INSIGHTS_REVIEW"
    assert result["provider_calls"] <= 9
    assert (package / "COMMENT_INSIGHTS_RU.md").is_file() and (package / "GPT_HANDOFF_WITH_COMMENTS_RU.md").is_file()
    insights = json.loads((package / "internal" / "comment_insights.json").read_text(encoding="utf-8"))
    assert len(insights["top_pains"]) == 5 and all(theme["representative_evidence"] for theme in insights["top_pains"])
    assert max(theme["max_likes"] for theme in insights["top_pains"]) >= 9000
    assert "username" not in (package / "comments_raw.jsonl").read_text(encoding="utf-8").lower()
    with (package / "comments_clean.csv").open(encoding="utf-8", newline="") as stream:
        assert set(csv.DictReader(stream).fieldnames or []) >= {"comment_ref", "duplicate_count", "aggregate_likes", "semantic_eligible"}


def test_reuse_only_has_zero_calls_and_hash_equality(tmp_path: Path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path, reuse_only=True)
    assert second["status"] == "REUSED" and second["browser_calls"] == second["network_calls"] == second["provider_calls"] == 0
    assert first["content_hash"] == second["content_hash"]


def test_reuse_only_missing_is_blocked_without_collection(tmp_path: Path) -> None:
    result = _run(tmp_path, reuse_only=True)
    assert result["status"] == "BLOCKED" and result["browser_calls"] == result["provider_calls"] == 0


def test_dry_run_has_zero_side_effects(tmp_path: Path) -> None:
    input_file = tmp_path / "selected_video.txt"; input_file.write_text("https://www.tiktok.com/@person/video/1234567890123456789", encoding="utf-8")
    result = run_comment_intelligence(project_id="nura", input_file=input_file, output_root=tmp_path / "out", repository_root=tmp_path, dry_run=True)
    assert result["status"] == "DRY_RUN" and result["browser_calls"] == result["network_calls"] == result["provider_calls"] == 0
    assert not (tmp_path / "out").exists()


def test_less_than_fifty_comments_is_honest_partial_without_provider(tmp_path: Path) -> None:
    def small(url: str, **kwargs): return _collected(20)
    input_file = tmp_path / "selected_video.txt"; input_file.write_text("https://www.tiktok.com/@person/video/1234567890123456789", encoding="utf-8")
    result = run_comment_intelligence(project_id="nura", input_file=input_file, output_root=tmp_path / "out", repository_root=tmp_path, services=CommentIntelligenceServices(collect=small, provider=FakeProvider()))
    assert result["status"] == "PARTIAL_INSUFFICIENT_COMMENTS" and result["provider_calls"] == 0


@pytest.mark.parametrize(("stop_reason", "expected"), [("CAPTCHA_OR_ANTI_BOT_CHALLENGE", "CAPTCHA_OR_ANTI_BOT_CHALLENGE"), ("RATE_LIMITED", "RATE_LIMITED"), ("PUBLIC_COMMENTS_BLOCKED", "PUBLIC_COMMENTS_BLOCKED")])
def test_collection_blockers_are_preserved(tmp_path: Path, stop_reason: str, expected: str) -> None:
    def blocked(url: str, **kwargs):
        result = _collected(0)
        return CommentCollectionResult(result.comments, result.access_mode, result.collection_method, stop_reason, 1, 0, "PASS", False, stop_reason.startswith("CAPTCHA"), stop_reason == "RATE_LIMITED", 0)
    input_file = tmp_path / "selected_video.txt"; input_file.write_text("https://www.tiktok.com/@person/video/1234567890123456789", encoding="utf-8")
    result = run_comment_intelligence(project_id="nura", input_file=input_file, output_root=tmp_path / "out", repository_root=tmp_path, services=CommentIntelligenceServices(collect=blocked))
    assert result["status"] == expected and result["provider_calls"] == 0


def test_manual_intake_is_not_imported_or_changed_by_comment_runner(tmp_path: Path) -> None:
    result = run_comment_intelligence(project_id="nura", input_file=tmp_path / "missing.txt", output_root=tmp_path / "out", repository_root=tmp_path)
    assert result["status"] == "READY_FOR_OWNER_COMMENT_PILOT_INPUT"

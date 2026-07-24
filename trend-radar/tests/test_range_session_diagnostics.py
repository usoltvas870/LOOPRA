from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT / "src"))

from range_diagnostics import RangeProbeResult, _RANGE_FETCH_SCRIPT, fetch_page_range
import range_session_diagnostics as session
from range_session_diagnostics import (
    MediaResponseReference,
    SessionExperiment,
    classify_session,
    is_allowed_media_response,
    response_reference,
    run_fresh_range_session,
)


def _probe(status: str) -> RangeProbeResult:
    return RangeProbeResult("probe", 0, 3, status, 0, 3, 10, 4, "a" * 64, 1, 8_000, 12, False, False, "cancelled")


def _experiment(name: str, status: str) -> SessionExperiment:
    return SessionExperiment(name, 1, "a" * 12, "playing", 1, "default", _probe(status))


def test_classification_requires_fresh_recovery_evidence() -> None:
    assert classify_session([_experiment("immediate", "RANGE_FETCH_FORBIDDEN"), _experiment("reload", "PASS")]) == "MEDIA_URL_REFRESH_REQUIRED"
    assert classify_session([_experiment("immediate", "RANGE_FETCH_FORBIDDEN"), _experiment("reload", "RANGE_FETCH_FORBIDDEN")]) == "RANGE_FETCH_FORBIDDEN"
    assert classify_session([_experiment("immediate", "PASS"), _experiment("delayed", "RANGE_FETCH_FORBIDDEN")]) == "FRESH_THEN_REPLAY_FAILED"


def test_classification_records_the_single_safe_page_native_variant() -> None:
    experiments = [
        _experiment("immediate", "RANGE_FETCH_FORBIDDEN"),
        _experiment("reload", "RANGE_FETCH_FORBIDDEN"),
        _experiment("player_paused", "RANGE_FETCH_FORBIDDEN"),
        _experiment("page_native", "PASS"),
    ]
    assert classify_session(experiments) == "PAGE_NATIVE_FETCH_REQUIRED"


def test_response_reference_never_serializes_url() -> None:
    class _Response:
        url = "https://example.invalid/video/fixture.mp4?signature=secret"

    reference = response_reference(_Response(), 2, 1.0)
    assert reference.url_hash_prefix
    assert "secret" not in reference.url_hash_prefix
    evidence = SessionExperiment("immediate", reference.generation, reference.url_hash_prefix, "playing", 0, "default", _probe("PASS")).to_dict()
    assert "url" not in evidence
    assert "secret" not in str(evidence)


def test_page_native_variant_is_allowlisted_and_passed_to_page() -> None:
    class _Page:
        async def evaluate(self, script, data):
            assert data["fetchVariant"] == "page_native"
            return {"result": "response", "status": 206, "content_type": "video/mp4", "content_range": "bytes 0-3/10", "body_length": 4, "body_sha256": "a" * 64, "reader_cleanup": "cancelled"}

    result = asyncio.run(fetch_page_range(_Page(), "https://example.invalid/video/fixture.mp4", label="start", start=0, end=3, browser_timeout_ms=10, python_timeout_seconds=1, fetch_variant="page_native"))
    assert result.status == "PASS"
    assert "Authorization" not in _RANGE_FETCH_SCRIPT
    assert "Cookie" not in _RANGE_FETCH_SCRIPT


def test_arbitrary_fetch_variant_is_rejected() -> None:
    with pytest.raises(ValueError, match="default or page_native"):
        asyncio.run(fetch_page_range(object(), "https://example.invalid/video/fixture.mp4", label="start", start=0, end=3, browser_timeout_ms=10, python_timeout_seconds=1, fetch_variant="custom"))


def test_media_response_host_must_be_tiktok_or_subdomain() -> None:
    class _Response:
        status = 200
        headers = {"content-type": "video/mp4"}

        def __init__(self, url: str) -> None:
            self.url = url

    assert is_allowed_media_response(_Response("https://fixture.tiktok.com/video/fixture.mp4"))
    assert not is_allowed_media_response(_Response("https://fixture-tiktok.com/video/fixture.mp4"))


def test_fresh_session_tracks_generations_player_state_and_redacted_evidence(monkeypatch) -> None:
    class _Response:
        status = 200
        headers = {"content-type": "video/mp4"}

        def __init__(self, generation: int) -> None:
            self.url = f"https://fixture.tiktok.com/video/fixture.mp4?generation={generation}&signature=secret"

    class _Page:
        def __init__(self) -> None:
            self.listener = None
            self.generation = 0
            self.paused = False

        def on(self, event, listener) -> None:
            assert event == "response"
            self.listener = listener

        async def goto(self, url, **kwargs) -> None:
            assert url == "https://example.invalid/candidate/2"
            self.generation = 1
            self.listener(_Response(self.generation))

        async def reload(self, **kwargs) -> None:
            self.generation = 2
            self.listener(_Response(self.generation))

        async def wait_for_timeout(self, timeout_ms) -> None:
            assert timeout_ms >= 0

        async def evaluate(self, script, data=None):
            if "video.pause()" in script:
                self.paused = True
                return None
            if "video.paused" in script:
                return [self.paused]
            if "document.readyState" in script:
                return "complete"
            raise AssertionError("unexpected page evaluation")

    calls = []

    async def fake_fetch(page, media_url, *, label, start, end, browser_timeout_ms=8_000,
                         python_timeout_seconds=12, fetch_variant="default"):
        calls.append((label, fetch_variant, media_url))
        if label == "cancellation":
            return RangeProbeResult(label, start, end, "RANGE_FETCH_BROWSER_TIMEOUT", None, None, None, None, None, 1, browser_timeout_ms, python_timeout_seconds, True, True, "not_started")
        status = "PASS" if fetch_variant == "page_native" else "RANGE_FETCH_FORBIDDEN"
        return RangeProbeResult(label, start, end, status, start if status == "PASS" else None, end if status == "PASS" else None, 100 if status == "PASS" else None, end - start + 1, "a" * 64, 1, browser_timeout_ms, python_timeout_seconds, False, False, "cancelled")

    async def fake_activate(page) -> bool:
        page.paused = False
        return True

    async def fake_player_diagnostics(page) -> dict:
        return {"video_element_count": 1}

    monkeypatch.setattr(session, "fetch_page_range", fake_fetch)
    monkeypatch.setattr(session, "activate_first_video_once", fake_activate)
    monkeypatch.setattr(session, "page_player_diagnostics", fake_player_diagnostics)

    result = asyncio.run(run_fresh_range_session(
        _Page(), "https://example.invalid/candidate/2",
        probe_bytes=4, python_timeout_seconds=12, settle_ms=0,
    ))

    assert result["classification"] == "PAGE_NATIVE_FETCH_REQUIRED"
    assert [item["response_generation"] for item in result["experiments"]] == [1, 2, 2, 2]
    assert [item["player_state"] for item in result["experiments"]] == ["playing", "playing", "paused", "paused"]
    assert all(item["url_age_ms"] >= 0 for item in result["experiments"])
    assert result["experiments"][0]["media_url_hash_prefix"] != result["experiments"][1]["media_url_hash_prefix"]
    assert "secret" not in str(result)
    assert "https://" not in str(result)
    assert result["consistency"].startswith("NOT_RUN")
    assert result["cancellation"]["abort_confirmed"]
    assert result["page_remained_usable"]
    assert [label for label, _, _ in calls] == ["immediate", "reload", "player_paused", "page_native", "cancellation"]

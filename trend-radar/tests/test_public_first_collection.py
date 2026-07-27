import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "trend-radar/src"))

import collector as collector_module
import loopra_top20_real_pipeline_v2 as v2
from collector import (
    CAPTCHA_OR_ANTI_BOT_CHALLENGE,
    PUBLIC_ACCESS_BLOCKED,
    PUBLIC_ACCESS_LIMITED,
    PUBLIC_ACCESS_SUFFICIENT,
    RATE_LIMITED,
    RadarOperationalError,
    TikTokCollector,
)


def _candidate(rank: int) -> dict:
    return {
        "video_id": str(7600000000000000000 + rank),
        "url": f"https://www.tiktok.com/@public/video/{7600000000000000000 + rank}",
        "views": 1000 + rank,
        "likes": rank,
        "comments": rank,
        "shares": rank,
    }


def _run_start(tmp_path: Path, cookies: list[dict] | None) -> tuple[TikTokCollector, SimpleNamespace, SimpleNamespace]:
    cookie_path = tmp_path / "cookies.json"
    cookie_path.parent.mkdir(parents=True, exist_ok=True)
    if cookies is not None:
        cookie_path.write_text(json.dumps({"cookies": cookies, "origins": []}), encoding="utf-8")
    context = SimpleNamespace(close=AsyncMock(), cookies=AsyncMock(return_value=cookies or []))
    browser = SimpleNamespace(new_context=AsyncMock(return_value=context), close=AsyncMock())
    playwright = SimpleNamespace(
        chromium=SimpleNamespace(launch=AsyncMock(return_value=browser), connect_over_cdp=AsyncMock()),
        stop=AsyncMock(),
    )
    with patch.object(collector_module, "get_cookie_path", return_value=cookie_path), patch.object(collector_module, "async_playwright") as api:
        api.return_value.start = AsyncMock(return_value=playwright)
        instance = TikTokCollector(headless=True)
        instance._validate_cookies = AsyncMock(return_value=(True, ""))
        asyncio.run(instance.start())
    return instance, browser, playwright


def test_guest_and_no_cookie_states_start_public_collection(tmp_path: Path) -> None:
    for suffix, cookies, expected in (
        ("guest", [{"name": "msToken", "domain": ".tiktok.com"}], "GUEST_SESSION"),
        ("none", None, "NO_SESSION_STATE"),
    ):
        instance, browser, playwright = _run_start(tmp_path / suffix, cookies)
        assert instance.access_mode == expected
        instance._validate_cookies.assert_not_awaited()
        asyncio.run(instance.close())
        browser.close.assert_awaited_once()
        playwright.stop.assert_awaited_once()


def test_authenticated_cookie_flow_remains_supported(tmp_path: Path) -> None:
    instance, browser, playwright = _run_start(
        tmp_path, [{"name": "sessionid", "domain": ".tiktok.com"}]
    )
    assert instance.access_mode == "AUTHENTICATED_SESSION"
    assert instance.authentication_state == "authenticated"
    instance._validate_cookies.assert_awaited_once()
    asyncio.run(instance.close())
    browser.close.assert_awaited_once()
    playwright.stop.assert_awaited_once()


def test_login_overlay_with_public_cards_is_not_blocked() -> None:
    page = SimpleNamespace(
        url="https://www.tiktok.com/tag/public",
        evaluate=AsyncMock(side_effect=[20, 0, True, {"challenge": False, "rateLimited": False}]),
    )
    instance = TikTokCollector()
    blocked, reason = asyncio.run(instance._is_blocked(page, "public"))
    assert blocked is False
    assert reason == "login_overlay_with_public_results"
    assert instance.public_cards_observed == 20


@pytest.mark.parametrize("dismissed", [True, False])
def test_overlay_close_is_bounded_and_public_api_results_continue(dismissed: bool) -> None:
    class Page:
        url = "https://www.tiktok.com/tag/public"
        def on(self, *_args): pass
        def remove_listener(self, *_args): pass
        async def goto(self, *_args, **_kwargs): pass
        async def wait_for_selector(self, *_args, **_kwargs): pass
        async def close(self): pass

    instance = TikTokCollector()
    instance.context = SimpleNamespace(new_page=AsyncMock(return_value=Page()))
    instance._dismiss_overlays = AsyncMock(return_value=dismissed)
    instance._is_blocked = AsyncMock(return_value=(False, "login_overlay_with_public_results"))
    with patch.object(collector_module, "extract_from_api_responses", return_value=[_candidate(i) for i in range(1, 21)]), patch.object(collector_module.asyncio, "sleep", AsyncMock()):
        result = asyncio.run(instance._navigate_and_extract("https://www.tiktok.com/tag/public", "hashtag", "public"))
    assert len(result) == 20
    instance._dismiss_overlays.assert_awaited_once()
    assert instance.login_overlay_observed is True
    assert instance.overlay_dismissed is dismissed


@pytest.mark.parametrize(
    ("signals", "expected"),
    [
        ({"challenge": True, "rateLimited": False}, CAPTCHA_OR_ANTI_BOT_CHALLENGE),
        ({"challenge": False, "rateLimited": True}, RATE_LIMITED),
    ],
)
def test_challenge_and_rate_limit_are_classified_separately(signals: dict, expected: str) -> None:
    page = SimpleNamespace(
        url="https://www.tiktok.com/tag/public",
        evaluate=AsyncMock(side_effect=[0, 0, False, signals]),
    )
    blocked, reason = asyncio.run(TikTokCollector()._is_blocked(page, "public"))
    assert blocked is True
    assert reason == expected.lower()


@pytest.mark.parametrize(
    ("count", "expected"),
    [(20, PUBLIC_ACCESS_SUFFICIENT), (7, PUBLIC_ACCESS_LIMITED), (0, PUBLIC_ACCESS_BLOCKED)],
)
def test_collection_status_depends_on_actual_public_candidate_count(count: int, expected: str) -> None:
    instance = TikTokCollector()
    instance.collect_from_hashtag = AsyncMock(return_value=[_candidate(i) for i in range(1, count + 1)])
    with patch.object(collector_module, "async_random_sleep", AsyncMock()):
        result = asyncio.run(instance.collect_all({"hashtags": ["public"]}))
    assert len(result) == count
    assert instance.public_access_status == expected


def test_fewer_than_twenty_candidates_stops_before_deepseek() -> None:
    pool = {"candidates": [_candidate(i) for i in range(1, 20)], "public_access_status": PUBLIC_ACCESS_LIMITED, "search_run_id": "public-run"}
    deps = {
        "collect": lambda: pool,
        "select": lambda _: pytest.fail("selection must not run"),
        "acquire": lambda _: pytest.fail("acquisition must not run"),
        "inspect": lambda _: pytest.fail("inspection must not run"),
        "ocr": lambda _: pytest.fail("ocr must not run"),
        "transcribe": lambda _: pytest.fail("transcription must not run"),
        "provider": lambda _: pytest.fail("DeepSeek must not run"),
    }
    result = v2.run_fresh_top20_b1(root=Path("unused"), dependencies=deps)
    assert result["status"] == "PARTIAL_INSUFFICIENT_CANDIDATES"
    assert result["actual_candidate_count"] == 19


def test_factory_persists_secret_free_public_access_status(monkeypatch, tmp_path: Path) -> None:
    calls = {"provider": 0, "closed": 0}
    candidates = [_candidate(i) for i in range(1, 8)]

    class Collector:
        def __init__(self, headless=True):
            self.run_id = "public-run"; self.collected_at = "2026-07-27T00:00:00Z"
            self.source_attempts = []; self.access_mode = "GUEST_SESSION"
            self.public_access_status = PUBLIC_ACCESS_LIMITED; self.login_overlay_observed = True
            self.overlay_dismissed = False; self.public_cards_observed = 7
            self.captcha_observed = False; self.rate_limit_observed = False
            self.blocking_reason = "fewer_than_20_public_candidates"
        async def start(self): pass
        async def collect_all(self, sources): return list(candidates)
        async def enrich_missing_stats(self, values): return values
        async def close(self): calls["closed"] += 1

    services = v2._canonical_services()
    services.update({
        "TikTokCollector": Collector,
        "read_source_file": lambda name: ["public"],
        "get_config_bool": lambda *args: True,
        "compute_scores": lambda values: values,
    })
    monkeypatch.setattr(v2, "_canonical_services", lambda: services)
    deps = v2.build_fresh_top20_b1_production_dependencies(root=tmp_path)
    deps["provider"] = lambda _: calls.__setitem__("provider", calls["provider"] + 1)
    result = v2.run_fresh_top20_b1(root=tmp_path, dependencies=deps)
    status = json.loads((tmp_path / "canonical/collection-status.json").read_text(encoding="utf-8"))
    assert result["status"] == "PARTIAL_INSUFFICIENT_CANDIDATES"
    assert status["access_mode"] == "GUEST_SESSION"
    assert status["deduplicated_candidate_count"] == 7
    assert status["login_overlay_observed"] is True
    assert status["resumable"] is True
    assert calls == {"provider": 0, "closed": 1}
    assert all(token not in json.dumps(status).lower() for token in ("cookie", "secret", "authorization"))


def test_browser_closes_when_public_access_blocker_is_raised(monkeypatch, tmp_path: Path) -> None:
    closed = []
    class Collector:
        def __init__(self, headless=True):
            self.run_id = "blocked-run"; self.collected_at = "2026-07-27T00:00:00Z"
        async def start(self): pass
        async def collect_all(self, sources):
            raise RadarOperationalError("public_access_blocked", "no public data")
        async def enrich_missing_stats(self, values): return values
        async def close(self): closed.append(True)
    services = v2._canonical_services()
    services.update({"TikTokCollector": Collector, "read_source_file": lambda name: ["public"], "get_config_bool": lambda *args: True})
    monkeypatch.setattr(v2, "_canonical_services", lambda: services)
    with pytest.raises(v2.LoopraTop20V2Error, match="PUBLIC_ACCESS_BLOCKED"):
        v2.build_fresh_top20_b1_production_dependencies(root=tmp_path)["collect"]()
    assert closed == [True]

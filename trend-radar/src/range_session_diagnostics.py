"""Fresh-response range-session diagnostics without persisting signed media URLs."""

from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass
from urllib.parse import urlsplit

from browser_media_capture import activate_first_video_once, page_player_diagnostics
from range_diagnostics import RangeProbeResult, fetch_page_range


@dataclass(frozen=True)
class MediaResponseReference:
    generation: int
    url: str  # Kept in memory only; never included in an evidence payload.
    url_hash_prefix: str
    observed_at: float


@dataclass(frozen=True)
class SessionExperiment:
    name: str
    response_generation: int | None
    media_url_hash_prefix: str | None
    player_state: str | None
    url_age_ms: int | None
    fetch_variant: str
    probe: RangeProbeResult | None

    def to_dict(self) -> dict:
        result = asdict(self)
        result.pop("url", None)
        return result


def is_allowed_media_response(response) -> bool:
    parsed = urlsplit(response.url)
    return bool(
        response.status == 200
        and response.headers.get("content-type", "").split(";", 1)[0].lower() == "video/mp4"
        and parsed.hostname
        and (parsed.hostname == "tiktok.com" or parsed.hostname.endswith(".tiktok.com"))
        and "/video/" in parsed.path
    )


def response_reference(response, generation: int, observed_at: float) -> MediaResponseReference:
    """Keep the URL only in memory; evidence retains a non-reversible short hash."""
    url = response.url
    return MediaResponseReference(generation, url, hashlib.sha256(url.encode("utf-8")).hexdigest()[:12], observed_at)


def classify_session(experiments: list[SessionExperiment]) -> str:
    """Conservative classification based only on the bounded experiment sequence."""
    probes = {item.name: item.probe for item in experiments if item.probe is not None}
    immediate = probes.get("immediate")
    reload_probe = probes.get("reload")
    if immediate and immediate.status == "PASS":
        delayed = probes.get("delayed")
        if delayed and delayed.status != "PASS":
            return "FRESH_THEN_REPLAY_FAILED"
        return "FRESH_RANGE_AVAILABLE"
    if immediate and immediate.status == "RANGE_FETCH_FORBIDDEN" and reload_probe and reload_probe.status == "PASS":
        return "MEDIA_URL_REFRESH_REQUIRED"
    if immediate and immediate.status == "RANGE_FETCH_FORBIDDEN" and reload_probe and reload_probe.status == "RANGE_FETCH_FORBIDDEN":
        active = probes.get("player_active")
        paused = probes.get("player_paused")
        if active and paused and active.status != paused.status:
            return "PLAYER_STATE_REQUIRED"
        native = probes.get("page_native")
        if native and native.status == "PASS":
            return "PAGE_NATIVE_FETCH_REQUIRED"
        return "RANGE_FETCH_FORBIDDEN"
    return "RANGE_SESSION_INCONCLUSIVE"


async def run_fresh_range_session(page, canonical_url: str, *, probe_bytes: int, python_timeout_seconds: int,
                                  settle_ms: int = 3_000, delay_ms: int = 2_000) -> dict:
    """Run the Stage 3J decision tree in one page; no URL or headers leave this function."""
    generation = 0
    latest: MediaResponseReference | None = None
    experiments: list[SessionExperiment] = []

    def observe(response) -> None:
        nonlocal latest
        if is_allowed_media_response(response):
            latest = response_reference(response, generation, time.monotonic())

    page.on("response", observe)

    async def player_state() -> str:
        states = await page.evaluate("() => [...document.querySelectorAll('video')].map((video) => video.paused)")
        if not states:
            return "no_video"
        return "paused" if all(states) else "playing"

    async def navigate(*, reload: bool = False) -> MediaResponseReference | None:
        nonlocal generation, latest
        generation += 1
        latest = None
        if reload:
            await page.reload(wait_until="domcontentloaded", timeout=45_000)
        else:
            await page.goto(canonical_url, wait_until="domcontentloaded", timeout=45_000)
        await page.wait_for_timeout(settle_ms)
        await activate_first_video_once(page)
        await page.wait_for_timeout(settle_ms)
        return latest

    async def probe(name: str, reference: MediaResponseReference, *, player_state: str,
                    fetch_variant: str = "default") -> RangeProbeResult:
        result = await fetch_page_range(
            page, reference.url, label=name, start=0, end=probe_bytes - 1,
            python_timeout_seconds=python_timeout_seconds, fetch_variant=fetch_variant,
        )
        experiments.append(SessionExperiment(name, reference.generation, reference.url_hash_prefix, player_state,
                                             round((time.monotonic() - reference.observed_at) * 1000), fetch_variant, result))
        return result

    first = await navigate()
    if first is None:
        return {"status": "NO_MEDIA_RESPONSE", "experiments": [], "classification": "RANGE_SESSION_INCONCLUSIVE"}
    immediate = await probe("immediate", first, player_state=await player_state())
    if immediate.status == "PASS":
        await page.wait_for_timeout(delay_ms)
        await probe("delayed", first, player_state=await player_state())

    refreshed = await navigate(reload=True)
    if refreshed is not None:
        reload_probe = await probe("reload", refreshed, player_state=await player_state())
        if immediate.status == "RANGE_FETCH_FORBIDDEN" and reload_probe.status == "RANGE_FETCH_FORBIDDEN":
            await page.evaluate("() => { const video = document.querySelector('video'); if (video) video.pause(); }")
            paused_state = await player_state()
            await probe("player_paused", refreshed, player_state=paused_state)
            await probe("page_native", refreshed, player_state=paused_state, fetch_variant="page_native")

    cancellation = await fetch_page_range(page, first.url, label="cancellation", start=0, end=probe_bytes - 1,
                                          browser_timeout_ms=1, python_timeout_seconds=python_timeout_seconds)
    player = await page_player_diagnostics(page)
    return {
        "status": "COMPLETED",
        "experiments": [item.to_dict() for item in experiments],
        "classification": classify_session(experiments),
        "cancellation": cancellation.to_dict(),
        "page_remained_usable": await page.evaluate("() => document.readyState") == "complete",
        "player": {"video_element_count": player.get("video_element_count"), "final_state": await player_state()},
        "consistency": "NOT_RUN: matching repeatable 206 start probes were not established",
    }

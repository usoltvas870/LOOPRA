"""Fresh-response range-session diagnostics without persisting signed media URLs."""

from __future__ import annotations

import hashlib
import secrets
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

from browser_media_capture import activate_first_video_once, page_player_diagnostics
from range_diagnostics import RangeProbeResult, consistency_verdict, fetch_page_range
from range_replay_diagnostics import assemble_verified_ranges, prove_page_range_bridge


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
        if any(item.name.startswith("option_") and item.probe and item.probe.status == "PASS" for item in experiments):
            return "PAGE_CONTEXT_FETCH_REQUIRED"
        return "RANGE_FETCH_FORBIDDEN"
    return "RANGE_SESSION_INCONCLUSIVE"


async def run_fresh_range_session(page, canonical_url: str, *, probe_bytes: int, python_timeout_seconds: int,
                                  settle_ms: int = 3_000, delay_ms: int = 2_000,
                                  assembly_target: Path | None = None) -> dict:
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
                    fetch_variant: str = "default", start: int = 0, end: int | None = None) -> RangeProbeResult:
        requested_end = probe_bytes - 1 if end is None else end
        result = await fetch_page_range(
            page, reference.url, label=name, start=start, end=requested_end,
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
            minimal_variant = None
            for variant in ("credentials_only", "credentials_referrer", "credentials_cache", "page_native_bundle"):
                label = "page_native" if variant == "page_native_bundle" else f"option_{variant}"
                option_probe = await probe(label, refreshed, player_state=paused_state, fetch_variant=variant)
                if option_probe.status == "PASS":
                    minimal_variant = variant
                    break
            if minimal_variant is not None:
                first_start = await probe("start", refreshed, player_state=paused_state, fetch_variant=minimal_variant)
                second_start = await probe("repeat_start", refreshed, player_state=paused_state, fetch_variant=minimal_variant)
                total = first_start.total_bytes
                consistency = "FAIL"
                bridge = None
                if total is not None and first_start.status == "PASS" and second_start.status == "PASS":
                    middle_start = (total // 2 // probe_bytes) * probe_bytes
                    middle_start = min(max(probe_bytes, middle_start), max(probe_bytes, total - probe_bytes))
                    end_start = max(0, total - probe_bytes)
                    middle = await probe("middle", refreshed, player_state=paused_state, fetch_variant=minimal_variant,
                                         start=middle_start, end=min(total - 1, middle_start + probe_bytes - 1))
                    final = await probe("end", refreshed, player_state=paused_state, fetch_variant=minimal_variant,
                                        start=end_start, end=total - 1)
                    consistency = consistency_verdict([first_start, middle, final, second_start])
                    if consistency == "PASS":
                        temporary_path = str(Path(tempfile.gettempdir()) / f"loopra-range-{secrets.token_hex(12)}.part")
                        bridge_result = await prove_page_range_bridge(
                            page, refreshed.url, temporary_path=Path(temporary_path),
                            start=0, end=probe_bytes - 1, expected_sha256=first_start.body_sha256,
                            python_timeout_seconds=python_timeout_seconds,
                        )
                        bridge = bridge_result.__dict__
                        if bridge_result.status == "PASS" and assembly_target is not None:
                            assembly_result = await assemble_verified_ranges(
                                page, refreshed.url, target_path=assembly_target, total_bytes=total,
                                python_timeout_seconds=python_timeout_seconds,
                            )
                            assembly = assembly_result.__dict__
                        else:
                            assembly = None
                    else:
                        assembly = None
                else:
                    assembly = None
                # These fields are assembled below without URL or response data.
                gate_result = {"minimal_fetch_variant": minimal_variant, "consistency": consistency, "stream_bridge": bridge, "assembly": assembly}
            else:
                gate_result = {"minimal_fetch_variant": None, "consistency": "NOT_RUN: no page-native 206", "stream_bridge": None, "assembly": None}
        else:
            gate_result = {"minimal_fetch_variant": None, "consistency": "NOT_RUN: default path did not reach option isolation", "stream_bridge": None, "assembly": None}
    else:
        gate_result = {"minimal_fetch_variant": None, "consistency": "NOT_RUN: fresh response unavailable", "stream_bridge": None, "assembly": None}

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
        **gate_result,
    }

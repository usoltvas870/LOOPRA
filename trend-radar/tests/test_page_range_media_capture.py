from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

import page_range_media_capture as replay
import browser_media_capture as browser


def test_eligibility_is_limited_to_large_primary_body_failures() -> None:
    facts = {"scheme": "https", "status": 200, "content_type": "video/mp4", "accept_ranges": "bytes", "content_length": 9 * 1024 * 1024}
    assert replay.is_range_replay_eligible(facts, "unavailable", 40 * 1024 * 1024)
    assert replay.is_range_replay_eligible(facts, "response_finished_timeout", 40 * 1024 * 1024)
    assert replay.is_range_replay_eligible(facts, "capture_limit_reached", 40 * 1024 * 1024)
    assert not replay.is_range_replay_eligible({**facts, "content_length": 1024}, "unavailable", 40 * 1024 * 1024)
    assert not replay.is_range_replay_eligible({**facts, "accept_ranges": None}, "unavailable", 40 * 1024 * 1024)
    assert not replay.is_range_replay_eligible({**facts, "scheme": "http"}, "unavailable", 40 * 1024 * 1024)
    assert not replay.is_range_replay_eligible({**facts, "content_type": "text/html"}, "unavailable", 40 * 1024 * 1024)


def test_capture_uses_repeat_probe_then_sequential_ranges_without_sensitive_headers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(replay, "MIN_REPLAY_BYTES", 8)
    monkeypatch.setattr(replay, "PROBE_BYTES", 2)
    monkeypatch.setattr(replay, "CHUNK_BYTES", 3)
    calls: list[tuple[int, int]] = []

    async def fake_fetch(page, url, start, end, *, binding_name):
        calls.append((start, end))
        return bytes(range(start, end + 1)), 8

    monkeypatch.setattr(replay, "_fetch_range", fake_fetch)
    monkeypatch.setattr(replay, "_validate_media", lambda path, size: {"sha256": "a" * 64, "ffprobe": {"valid": True, "video_codec": "h264"}})
    result = asyncio.run(replay.capture_page_ranges(object(), "https://signed.example/video?secret=value", target_path=tmp_path / "video.mp4", total_bytes=8))

    assert result.status == "COMPLETED" and result.captured_bytes == 8 and result.chunk_count == 3
    assert calls == [(0, 1), (4, 5), (6, 7), (0, 1), (0, 2), (3, 5), (6, 7)]
    assert (tmp_path / "video.mp4").read_bytes() == bytes(range(8))
    assert not (tmp_path / "video.mp4.part").exists()
    assert "Authorization" not in replay._RANGE_FETCH_SCRIPT
    assert "Cookie" not in replay._RANGE_FETCH_SCRIPT


def test_repeat_mismatch_fails_and_removes_part(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(replay, "MIN_REPLAY_BYTES", 8)
    monkeypatch.setattr(replay, "PROBE_BYTES", 2)
    calls = 0

    async def fake_fetch(page, url, start, end, *, binding_name):
        nonlocal calls
        calls += 1
        return (b"aa" if calls != 4 else b"bb"), 8

    monkeypatch.setattr(replay, "_fetch_range", fake_fetch)
    result = asyncio.run(replay.capture_page_ranges(object(), "https://signed.example/video", target_path=tmp_path / "video.mp4", total_bytes=8))

    assert result.error_code == "RANGE_REPEAT_FAILED"
    assert not (tmp_path / "video.mp4.part").exists()


def test_browser_fallback_records_range_method_without_signed_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_capture(page, url, *, target_path, total_bytes):
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(b"fixture")
        return replay.PageRangeCaptureResult("COMPLETED", total_bytes, 36, "b" * 64, {"valid": True, "video_codec": "h264"})

    monkeypatch.setattr(browser, "capture_page_ranges", fake_capture)
    signed_url = "https://v16.tiktok.com/video/fixture.mp4?signature=secret"
    facts = {"url_sha256": "a" * 64, "scheme": "https", "status": 200, "content_type": "video/mp4", "accept_ranges": "bytes", "content_length": 9 * 1024 * 1024, "redacted_reference": "https://v16.tiktok.com/video/fixture.mp4"}
    manifest = SimpleNamespace(radar_run_reference="data/runs/fixture.json", manifest_hash="m" * 64, radar_run_id="fixture")
    candidate = SimpleNamespace(video_id="2", rank=2, canonical_url="https://www.tiktok.com/@fixture/video/2")
    record = asyncio.run(browser._try_range_fallback(
        object(), [(0, SimpleNamespace(url=signed_url), facts)], {facts["url_sha256"]: {"body_status": "unavailable"}},
        tmp_path / "2", tmp_path, manifest, candidate, 200, "session_valid", "2026-07-24T00:00:00Z",
        40 * 1024 * 1024, [], {},
    ))

    assert record is not None and record.acquisition_method == browser.RANGE_ACQUISITION_METHOD
    assert record.tool_metadata["chunk_count"] == 36
    assert signed_url not in json.dumps(record.to_dict())


def test_browser_fallback_uses_valid_response_skipped_by_body_capture_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[int] = []

    async def fake_capture(page, url, *, target_path, total_bytes):
        calls.append(total_bytes)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(b"fixture")
        return replay.PageRangeCaptureResult(
            "COMPLETED", total_bytes, 36, "b" * 64,
            {"valid": True, "video_codec": "h264"},
        )

    monkeypatch.setattr(browser, "capture_page_ranges", fake_capture)
    facts = {
        "url_sha256": "a" * 64, "scheme": "https", "status": 200,
        "content_type": "video/mp4", "accept_ranges": "bytes",
        "content_length": 9 * 1024 * 1024,
        "redacted_reference": "https://v16.tiktok.com/video/fixture.mp4",
    }
    manifest = SimpleNamespace(
        radar_run_reference="data/runs/fixture.json", manifest_hash="m" * 64,
        radar_run_id="fixture",
    )
    candidate = SimpleNamespace(
        video_id="2", rank=2,
        canonical_url="https://www.tiktok.com/@fixture/video/2",
    )

    record = asyncio.run(browser._try_range_fallback(
        object(), [(0, SimpleNamespace(url="https://v16.tiktok.com/video/fixture"), facts)],
        {}, tmp_path / "2", tmp_path, manifest, candidate, 200, "session_refresh_required",
        "2026-07-24T00:00:00Z", 40 * 1024 * 1024, [], {},
    ))

    assert record is not None and record.status == "COMPLETED"
    assert calls == [9 * 1024 * 1024]

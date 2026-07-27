from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import browser_media_capture as capture_module
from browser_media_capture import (
    ACQUISITION_METHOD,
    DEFAULT_MAX_FILE_BYTES,
    BrowserMediaCaptureRequest,
    MediaResponseObservation,
    _read_reusable_record,
    _persist_capture,
    _select_candidate,
    _validate_body,
    activate_first_video_once,
    capture_browser_media_in_context,
    classify_media_response,
    is_confirmed_media_response,
    response_facts,
)
from media_acquisition import MediaAcquisitionError
from selection_manifest import build_selection_manifest, write_selection_manifest


def _manifest(tmp_path: Path) -> Path:
    candidates = []
    for video_id in ("1", "2"):
        candidates.append({
            "video_id": video_id, "author_username": "author", "source_type": "keyword",
            "source_value": "fixture", "url": f"https://www.tiktok.com/@author/video/{video_id}",
            "caption": "fixture", "views": 1, "likes": 1, "comments": 0, "shares": 0,
            "author_followers": 1, "published_at": "2026-07-24T00:00:00Z",
            "collected_at": "2026-07-24T00:00:00Z", "final_score": 1, "reach_score": 1,
            "engagement_score": 1, "freshness_score": 1, "momentum_proxy": 1,
            "data_confidence": "HIGH", "identity_confidence": "HIGH", "classification": "CURRENT",
            "provenance": {"primary_source_type": "keyword", "primary_source_value": "fixture"},
        })
    return write_selection_manifest(build_selection_manifest(candidates, radar_run_id="fixture"), tmp_path / "runs")


def _mp4_bytes(tmp_path: Path) -> bytes:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg and ffprobe are required")
    source = tmp_path / "fixture.mp4"
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:r=10", "-t", "0.2", "-pix_fmt", "yuv420p", str(source)],
        capture_output=True, check=False,
    )
    assert result.returncode == 0
    return source.read_bytes()


class _Request:
    resource_type = "fetch"


class _Response:
    status = 200
    url = "https://v16-webapp-prime.tiktok.com/video/tos/fixture.mp4?expires=secret&signature=secret"
    request = _Request()
    headers = {"content-type": "video/mp4; charset=binary", "content-length": "2048", "accept-ranges": "bytes"}

    async def finished(self) -> None:
        return None


def test_response_facts_are_redacted_and_classified() -> None:
    facts = response_facts(_Response())
    assert facts["redacted_reference"] == "https://v16-webapp-prime.tiktok.com/video/tos/fixture.mp4"
    assert "secret" not in json.dumps(facts)
    assert len(facts["url_sha256"]) == 64
    assert is_confirmed_media_response(facts, 4096)
    assert not is_confirmed_media_response({**facts, "host": "eviltiktok.com"}, 4096)
    assert not is_confirmed_media_response({**facts, "status": 206}, 4096)


def test_response_diagnostics_preserve_safe_rejection_reasons() -> None:
    facts = response_facts(_Response())
    accepted = classify_media_response(facts, 3, 4096)
    assert accepted.accepted and accepted.rejection_codes == []
    assert accepted.observed_order == 3
    payload = accepted.to_dict()
    serialized = json.dumps(payload)
    assert payload["query_parameter_names"] == ["expires", "signature"]
    assert "secret" not in serialized
    assert _Response.url not in serialized
    assert not {"cookies", "authorization", "headers", "response_body"} & payload.keys()
    assert MediaResponseObservation(**json.loads(serialized)) == accepted
    ranged = classify_media_response({**facts, "status": 206}, 0, 4096)
    assert "RANGE_RESPONSE_UNSUPPORTED" in ranged.rejection_codes
    malicious = classify_media_response({**facts, "host": "eviltiktok.com"}, 1, 4096)
    assert "UNSUPPORTED_HOST" in malicious.rejection_codes
    oversized = classify_media_response({**facts, "content_length": 4097}, 2, 4096)
    assert "SIZE_ABOVE_LIMIT" in oversized.rejection_codes


def test_default_limit_accepts_evidenced_large_mp4_but_remains_bounded() -> None:
    facts = response_facts(_Response())
    assert DEFAULT_MAX_FILE_BYTES == 40 * 1024 * 1024
    evidenced = {**facts, "content_length": 35_521_949}
    assert is_confirmed_media_response(evidenced, DEFAULT_MAX_FILE_BYTES)
    oversized = {**facts, "content_length": DEFAULT_MAX_FILE_BYTES + 1}
    assert not is_confirmed_media_response(oversized, DEFAULT_MAX_FILE_BYTES)
    assert "SIZE_ABOVE_LIMIT" in classify_media_response(
        oversized, 0, DEFAULT_MAX_FILE_BYTES
    ).rejection_codes


class _Navigation:
    status = 200


class _BodyUnavailableResponse(_Response):
    async def body(self) -> bytes:
        raise RuntimeError("fixture body unavailable")


class _FakePage:
    def __init__(self, response=None, *, video_element_count: int = 1) -> None:
        self.response = response
        self.video_element_count = video_element_count
        self.listener = None
        self.evaluate_calls = 0
        self.activation_calls = 0
        self.waits: list[int] = []
        self.closed = False

    def on(self, event: str, listener) -> None:
        assert event == "response"
        self.listener = listener

    async def goto(self, url: str, **kwargs):
        assert "/video/" in url
        if self.response is not None:
            self.listener(self.response)
        return _Navigation()

    async def wait_for_timeout(self, milliseconds: int) -> None:
        self.waits.append(milliseconds)

    async def evaluate(self, script: str):
        self.evaluate_calls += 1
        if "document.querySelectorAll('video')" in script:
            return {
                "video_element_count": self.video_element_count,
                "player_source_kinds": ["blob"] if self.video_element_count else [],
                "source_element_count": 0,
                "ready_states": [4] if self.video_element_count else [],
                "network_states": [1] if self.video_element_count else [],
                "durations": [1.0] if self.video_element_count else [],
                "dimensions": [[16, 16]] if self.video_element_count else [],
                "activation_attempted": False,
            }
        self.activation_calls += 1
        return bool(self.video_element_count)

    async def close(self) -> None:
        self.closed = True

    def is_closed(self) -> bool:
        return self.closed


class _FakeContext:
    def __init__(self, page: _FakePage) -> None:
        self.page = page
        self.new_page_calls = 0

    async def new_page(self) -> _FakePage:
        self.new_page_calls += 1
        return self.page


async def _valid_page_auth(_page):
    return SimpleNamespace(result="session_valid", reason="fixture")


async def _guest_page_auth(_page):
    return SimpleNamespace(
        result="session_refresh_required", reason="authenticated_tiktok_cookie_missing"
    )


async def _challenge_page_auth(_page):
    return SimpleNamespace(result="challenge_detected", reason="challenge_detected")


def test_guest_page_can_capture_public_media_response(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from selection_manifest import read_selection_manifest

    class _PublicResponse(_Response):
        async def body(self) -> bytes:
            return b"\x00" * 8 + b"ftypisom" + b"\x00" * 2048

    manifest_path = _manifest(tmp_path)
    manifest = read_selection_manifest(manifest_path)
    page = _FakePage(_PublicResponse())
    context = _FakeContext(page)
    monkeypatch.setattr(capture_module, "inspect_page_authentication", _guest_page_auth)
    monkeypatch.setattr(capture_module, "_persist_capture", lambda **kwargs: kwargs)
    request = BrowserMediaCaptureRequest(
        manifest_path, tmp_path / "cookies.json", tmp_path / "acquisitions",
        candidate_id="1", maximum_file_bytes=4096,
    )

    result = asyncio.run(
        capture_browser_media_in_context(request, manifest, manifest.candidates[0], context)
    )

    assert result["authenticated_session_status"] == "session_refresh_required"
    assert result["body"].startswith(b"\x00" * 8 + b"ftyp")
    assert page.closed


def test_challenge_blocks_public_media_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from selection_manifest import read_selection_manifest

    manifest_path = _manifest(tmp_path)
    manifest = read_selection_manifest(manifest_path)
    page = _FakePage()
    context = _FakeContext(page)
    monkeypatch.setattr(capture_module, "inspect_page_authentication", _challenge_page_auth)
    request = BrowserMediaCaptureRequest(
        manifest_path, tmp_path / "cookies.json", tmp_path / "acquisitions",
        candidate_id="1", maximum_file_bytes=4096,
    )

    with pytest.raises(MediaAcquisitionError, match="public candidate page blocked by challenge"):
        asyncio.run(
            capture_browser_media_in_context(request, manifest, manifest.candidates[0], context)
        )
    assert page.closed


def test_body_unavailable_is_typed_after_one_bounded_body_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from selection_manifest import read_selection_manifest

    manifest_path = _manifest(tmp_path)
    manifest = read_selection_manifest(manifest_path)
    page = _FakePage(_BodyUnavailableResponse())
    context = _FakeContext(page)
    monkeypatch.setattr(capture_module, "inspect_page_authentication", _valid_page_auth)
    request = BrowserMediaCaptureRequest(
        manifest_path, tmp_path / "cookies.json", tmp_path / "acquisitions",
        candidate_id="1", maximum_file_bytes=4096,
    )

    record = asyncio.run(
        capture_browser_media_in_context(request, manifest, manifest.candidates[0], context)
    )

    assert record.status == "FAILED"
    assert record.errors == ["selected browser response body unavailable"]
    observation = record.tool_metadata["response_observations"][0]
    assert observation["body_attempted"] is True
    assert observation["body_status"] == "unavailable"
    assert observation["body_attempt_context"] == "response_event_task"
    assert observation["exception_type"] == "RuntimeError"
    assert observation["redacted_exception_message"] == "fixture body unavailable"
    assert observation["candidate_classification"] == "selected_body_unavailable"
    assert observation["rejection_codes"] == ["BODY_UNAVAILABLE"]
    assert page.activation_calls == 0
    assert page.closed and context.new_page_calls == 1
    persisted = json.loads(
        (tmp_path / "acquisitions" / "fixture" / "1" / "acquisition_record.json")
        .read_text(encoding="utf-8")
    )
    assert persisted["tool_metadata"]["response_observations"][0] == observation


def test_finished_timeout_is_classified_without_attempting_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from selection_manifest import read_selection_manifest

    class _NeverFinishedResponse(_Response):
        async def finished(self) -> None:
            await asyncio.sleep(1)

        async def body(self) -> bytes:
            raise AssertionError("body must not be attempted before finished")

    manifest_path = _manifest(tmp_path)
    manifest = read_selection_manifest(manifest_path)
    page = _FakePage(_NeverFinishedResponse())
    context = _FakeContext(page)
    monkeypatch.setattr(capture_module, "inspect_page_authentication", _valid_page_auth)
    monkeypatch.setattr(capture_module, "BODY_CAPTURE_TIMEOUT_SECONDS", 0.01)
    request = BrowserMediaCaptureRequest(
        manifest_path, tmp_path / "cookies.json", tmp_path / "acquisitions",
        candidate_id="1", maximum_file_bytes=4096,
    )

    record = asyncio.run(
        capture_browser_media_in_context(request, manifest, manifest.candidates[0], context)
    )

    observation = record.tool_metadata["response_observations"][0]
    assert observation["body_status"] == "response_finished_timeout"
    assert observation["exception_type"] == "TimeoutError"
    assert observation["body_attempt_started_at"] is None
    assert observation["rejection_codes"] == ["BODY_UNAVAILABLE", "RESPONSE_FINISHED_TIMEOUT"]


def test_body_is_retrieved_after_finished_while_page_is_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from selection_manifest import read_selection_manifest

    events: list[str] = []

    class _LifecycleResponse(_Response):
        async def finished(self) -> None:
            events.append("finished")

        async def body(self) -> bytes:
            events.append("body")
            return b"\x00" * 8 + b"ftypisom" + b"\x00" * 2048

    manifest_path = _manifest(tmp_path)
    manifest = read_selection_manifest(manifest_path)
    page = _FakePage(_LifecycleResponse())
    context = _FakeContext(page)
    monkeypatch.setattr(capture_module, "inspect_page_authentication", _valid_page_auth)
    monkeypatch.setattr(capture_module, "_persist_capture", lambda **kwargs: kwargs)
    request = BrowserMediaCaptureRequest(
        manifest_path, tmp_path / "cookies.json", tmp_path / "acquisitions",
        candidate_id="1", maximum_file_bytes=4096,
    )

    result = asyncio.run(
        capture_browser_media_in_context(request, manifest, manifest.candidates[0], context)
    )

    assert events == ["finished", "body"]
    observation = result["observations"][0]
    assert observation.body_status == "captured"
    assert observation.page_open_at_body_attempt is True
    assert observation.context_open_at_body_attempt is True
    assert page.closed


def test_player_activation_is_attempted_once_and_timeout_is_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from selection_manifest import read_selection_manifest

    manifest_path = _manifest(tmp_path)
    manifest = read_selection_manifest(manifest_path)
    page = _FakePage()
    context = _FakeContext(page)
    monkeypatch.setattr(capture_module, "inspect_page_authentication", _valid_page_auth)
    request = BrowserMediaCaptureRequest(
        manifest_path, tmp_path / "cookies.json", tmp_path / "acquisitions",
        candidate_id="1", maximum_file_bytes=4096,
    )

    record = asyncio.run(
        capture_browser_media_in_context(request, manifest, manifest.candidates[0], context)
    )

    assert record.status == "FAILED"
    assert record.tool_metadata["page_diagnostics"]["activation_attempted"] is True
    assert page.activation_calls == 1
    assert page.waits == [8_000, 3_000]
    assert page.closed


def test_activation_helper_does_not_retry_playback() -> None:
    page = _FakePage()
    assert asyncio.run(activate_first_video_once(page)) is True
    assert page.activation_calls == 1


def test_manifest_selection_defaults_to_rank_one_and_rejects_unknown(tmp_path: Path) -> None:
    from selection_manifest import read_selection_manifest

    manifest = read_selection_manifest(_manifest(tmp_path))
    assert _select_candidate(manifest, None).video_id == "1"
    assert _select_candidate(manifest, "2").rank == 2
    with pytest.raises(MediaAcquisitionError, match="unknown candidate"):
        _select_candidate(manifest, "404")


def test_capture_persists_valid_mp4_atomically_and_is_redacted(tmp_path: Path) -> None:
    from selection_manifest import read_selection_manifest

    manifest = read_selection_manifest(_manifest(tmp_path))
    body = _mp4_bytes(tmp_path)
    facts = {
        "redacted_reference": "https://v16-webapp-prime.tiktok.com/video/tos/fixture.mp4",
        "url_sha256": "a" * 64, "status": 200, "content_type": "video/mp4",
        "content_length": len(body), "accept_ranges": "bytes", "content_range": None, "resource_type": "fetch",
    }
    run_root = tmp_path / "acquisitions" / manifest.radar_run_id
    record = _persist_capture(
        candidate_root=run_root / "1", run_root=run_root, manifest=manifest, candidate=manifest.candidates[0],
        facts=facts, body=body, page_status=200, authenticated_session_status="session_valid",
        started_at="2026-07-24T00:00:00Z", maximum_file_bytes=8 * 1024 * 1024,
    )
    assert record.status == "COMPLETED"
    assert record.acquisition_method == ACQUISITION_METHOD
    assert record.ffprobe_validation["valid"] and record.local_media_path == "1/browser_source.mp4"
    assert not (run_root / "1" / "browser_source.mp4.part").exists()
    persisted = json.loads((run_root / "1" / "acquisition_record.json").read_text(encoding="utf-8"))
    assert "secret" not in json.dumps(persisted)
    assert persisted["media_url_redacted_reference"].endswith("fixture.mp4")
    reused = _read_reusable_record(run_root / "1", run_root, manifest.manifest_hash, "1", 8 * 1024 * 1024)
    assert reused is not None and reused.status == "REUSED"
    (run_root / "1" / "browser_source.mp4").write_bytes(b"corrupted")
    assert _read_reusable_record(run_root / "1", run_root, manifest.manifest_hash, "1", 8 * 1024 * 1024) is None


def test_html_body_fails_without_media(tmp_path: Path) -> None:
    from selection_manifest import read_selection_manifest

    manifest = read_selection_manifest(_manifest(tmp_path))
    run_root = tmp_path / "acquisitions" / manifest.radar_run_id
    body = b"<html>challenge</html>" + b" " * 2048
    facts = {"redacted_reference": "https://host/video/a", "url_sha256": "b" * 64, "status": 200,
             "content_type": "video/mp4", "content_length": len(body), "accept_ranges": None,
             "content_range": None, "resource_type": "fetch"}
    record = _persist_capture(
        candidate_root=run_root / "1", run_root=run_root, manifest=manifest, candidate=manifest.candidates[0],
        facts=facts, body=body, page_status=200,
        authenticated_session_status="session_valid", started_at="2026-07-24T00:00:00Z", maximum_file_bytes=8 * 1024 * 1024,
    )
    assert record.status == "FAILED"
    assert record.local_media_path is None
    assert not (run_root / "1" / "browser_source.mp4").exists()


def test_declared_size_mismatch_is_rejected() -> None:
    body = b"\x00\x00\x00\x20ftypisom" + b"\x00" * 2048
    facts = {"status": 200, "content_length": len(body) + 1}
    with pytest.raises(MediaAcquisitionError, match="does not match"):
        _validate_body(body, facts, 4096)


def test_cli_help_has_no_side_effects(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from capture_browser_media import main

    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as error:
        main(["--help"])
    assert error.value.code == 0
    assert list(tmp_path.iterdir()) == []


def test_request_does_not_accept_an_arbitrary_url(tmp_path: Path) -> None:
    request = BrowserMediaCaptureRequest(tmp_path / "manifest.json", tmp_path / "cookies.json", tmp_path / "runtime")
    assert request.candidate_id is None
    assert not hasattr(request, "url")

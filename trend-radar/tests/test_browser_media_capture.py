from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from browser_media_capture import (
    ACQUISITION_METHOD,
    BrowserMediaCaptureRequest,
    _read_reusable_record,
    _persist_capture,
    _select_candidate,
    _validate_body,
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


def test_response_facts_are_redacted_and_classified() -> None:
    facts = response_facts(_Response())
    assert facts["redacted_reference"] == "https://v16-webapp-prime.tiktok.com/video/tos/fixture.mp4"
    assert "secret" not in json.dumps(facts)
    assert len(facts["url_sha256"]) == 64
    assert is_confirmed_media_response(facts, 4096)
    assert not is_confirmed_media_response({**facts, "host": "eviltiktok.com"}, 4096)
    assert not is_confirmed_media_response({**facts, "status": 206}, 4096)


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

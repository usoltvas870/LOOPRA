from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

import browser_media_acquisition as acquisition
from browser_media_capture import _persist_capture
from media_acquisition import MediaAcquisitionError
from selection_manifest import build_selection_manifest, read_selection_manifest, write_selection_manifest


def _candidate(video_id: str) -> dict:
    return {
        "video_id": video_id, "author_username": "author", "source_type": "keyword", "source_value": "fixture",
        "url": f"https://www.tiktok.com/@author/video/{video_id}", "caption": "fixture", "views": 1, "likes": 1,
        "comments": 0, "shares": 0, "author_followers": 1, "published_at": "2026-07-24T00:00:00Z",
        "collected_at": "2026-07-24T00:00:00Z", "final_score": 1, "reach_score": 1, "engagement_score": 1,
        "freshness_score": 1, "momentum_proxy": 1, "data_confidence": "HIGH", "identity_confidence": "HIGH",
        "classification": "CURRENT", "provenance": {"primary_source_type": "keyword", "primary_source_value": "fixture"},
    }


def _manifest(tmp_path: Path, count: int = 5) -> Path:
    return write_selection_manifest(build_selection_manifest([_candidate(str(index)) for index in range(1, count + 1)], radar_run_id="fixture"), tmp_path / "runs")


def _mp4(tmp_path: Path) -> bytes:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg and ffprobe are required")
    target = tmp_path / "fixture.mp4"
    result = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:r=10", "-t", "0.2", "-pix_fmt", "yuv420p", str(target)], capture_output=True, check=False)
    assert result.returncode == 0
    return target.read_bytes()


def test_selection_defaults_to_top_five_and_preserves_manifest_order(tmp_path: Path) -> None:
    manifest = read_selection_manifest(_manifest(tmp_path))
    assert [candidate.video_id for candidate in acquisition.select_manifest_candidates(manifest)] == ["1", "2", "3", "4", "5"]
    assert [candidate.video_id for candidate in acquisition.select_manifest_candidates(manifest, ("4", "2"))] == ["2", "4"]


def test_selection_uses_all_available_candidates_when_manifest_has_less_than_five(tmp_path: Path) -> None:
    manifest = read_selection_manifest(_manifest(tmp_path, 2))
    assert [candidate.video_id for candidate in acquisition.select_manifest_candidates(manifest)] == ["1", "2"]


def test_selection_rejects_duplicate_unknown_and_invalid_limit(tmp_path: Path) -> None:
    manifest = read_selection_manifest(_manifest(tmp_path, 2))
    with pytest.raises(MediaAcquisitionError, match="duplicate"):
        acquisition.select_manifest_candidates(manifest, ("1", "1"))
    with pytest.raises(MediaAcquisitionError, match="unknown"):
        acquisition.select_manifest_candidates(manifest, ("404",))
    for limit in (0, 6):
        with pytest.raises(MediaAcquisitionError, match="between"):
            acquisition.select_manifest_candidates(manifest, limit=limit)


def test_all_reused_skips_browser_and_writes_completed_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_path = _manifest(tmp_path, 2)
    manifest = read_selection_manifest(manifest_path)
    body = _mp4(tmp_path)
    runtime = tmp_path / "runtime"
    run_root = runtime / manifest.radar_run_id
    facts = {"status": 200, "content_type": "video/mp4", "content_length": len(body), "redacted_reference": "https://v16.tiktok.com/video/fixture.mp4", "url_sha256": "a" * 64}
    for candidate in manifest.candidates:
        _persist_capture(candidate_root=run_root / candidate.video_id, run_root=run_root, manifest=manifest, candidate=candidate, facts=facts, body=body, page_status=200, authenticated_session_status="session_valid", started_at="2026-07-24T00:00:00Z", maximum_file_bytes=8 * 1024 * 1024)

    async def forbidden(*args, **kwargs):
        raise AssertionError("browser must not start for reusable artifacts")
    monkeypatch.setattr(acquisition, "_capture_pending", forbidden)
    result = acquisition.run_browser_media_acquisition(acquisition.BrowserMediaAcquisitionRunRequest(manifest_path, tmp_path / "missing.json", runtime))

    assert result.run_status == "COMPLETED"
    assert result.reused_count == 2 and result.completed_count == result.failed_count == 0
    summary_path = run_root / f"{result.acquisition_run_id}.json"
    assert json.loads(summary_path.read_text(encoding="utf-8"))["run_status"] == "COMPLETED"


def test_partial_failure_keeps_later_success_and_persists_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_path = _manifest(tmp_path, 2)
    runtime = tmp_path / "runtime"

    async def synthetic(request, manifest, pending, state, summaries):
        summaries.append(acquisition._persist_failed_summary(request, manifest, pending[0], "PAGE_UNAVAILABLE", "candidate page returned 404"))
        summaries.append(acquisition._persist_failed_summary(request, manifest, pending[1], "FAILED", "synthetic capture failed"))
        summaries[-1] = acquisition.CandidateAcquisitionSummary("2", 2, "COMPLETED", "authenticated_browser_response", "2/acquisition_record.json", "2/browser_source.mp4", "a" * 64, 1024, 1.0, "h264", False, [], [])
    monkeypatch.setattr(acquisition, "_capture_pending", synthetic)
    monkeypatch.setattr(acquisition, "storage_state_diagnostics", lambda path: ({"cookies": [{}]}, object()))
    result = acquisition.run_browser_media_acquisition(acquisition.BrowserMediaAcquisitionRunRequest(manifest_path, tmp_path / "cookies.json", runtime))

    assert result.run_status == "PARTIAL"
    assert [item.status for item in result.candidates] == ["PAGE_UNAVAILABLE", "COMPLETED"]
    assert result.completed_count == result.failed_count == 1
    assert (runtime / "fixture" / "1" / "acquisition_record.json").is_file()

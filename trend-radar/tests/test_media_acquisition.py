import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from acquire_media import main
from media_acquisition import MediaAcquisitionError, MediaAcquisitionRequest, acquire_local_media
from selection_manifest import build_selection_manifest, write_selection_manifest


def _candidate(video_id: str) -> dict:
    return {
        "video_id": video_id,
        "author_username": "author",
        "source_type": "keyword",
        "source_value": "test",
        "url": f"https://www.tiktok.com/@author/video/{video_id}",
        "caption": "test",
        "views": 1,
        "likes": 1,
        "comments": 0,
        "shares": 0,
        "author_followers": 1,
        "published_at": "2026-07-24T00:00:00Z",
        "collected_at": "2026-07-24T00:00:00Z",
        "final_score": 1,
        "reach_score": 1,
        "engagement_score": 1,
        "freshness_score": 1,
        "momentum_proxy": 1,
        "data_confidence": "HIGH",
        "identity_confidence": "HIGH",
        "classification": "CURRENT",
        "provenance": {"primary_source_type": "keyword", "primary_source_value": "test"},
    }


def _manifest(tmp_path: Path, count: int = 3) -> Path:
    manifest = build_selection_manifest([_candidate(str(index)) for index in range(1, count + 1)], radar_run_id="local-test")
    return write_selection_manifest(manifest, tmp_path / "manifests")


def _video(path: Path) -> Path:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg and ffprobe are required")
    completed = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:r=10", "-t", "0.2", "-pix_fmt", "yuv420p", str(path)],
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    return path


import shutil


def test_selection_uses_only_manifest_entries_and_preserves_manifest_order(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    video = _video(tmp_path / "operator.mp4")

    records = acquire_local_media(MediaAcquisitionRequest(
        selection_manifest_path=manifest,
        output_root=tmp_path / "runtime",
        local_file_mapping={"1": video, "2": video},
        candidate_ids=("2", "1"),
    ))

    assert [record.candidate_video_id for record in records] == ["1", "2"]
    assert [record.rank for record in records] == [1, 2]
    assert all(record.status == "COMPLETED" for record in records)
    assert all(record.ffprobe_validation["valid"] for record in records)
    assert all(record.local_media_path and not Path(record.local_media_path).is_absolute() for record in records)
    assert all("cookies" not in str(record.to_dict()).lower() for record in records)
    persisted = list((tmp_path / "runtime").rglob("acquisition_record.json"))
    assert len(persisted) == 2
    assert json.loads(persisted[0].read_text(encoding="utf-8"))["schema_version"] == "1.0"


def test_limit_and_unknown_candidate_are_explicit(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    video = _video(tmp_path / "operator.mp4")
    request = MediaAcquisitionRequest(manifest, tmp_path / "runtime", {"1": video, "2": video}, limit=2)
    assert len(acquire_local_media(request)) == 2
    with pytest.raises(MediaAcquisitionError, match="unknown candidate"):
        acquire_local_media(MediaAcquisitionRequest(manifest, tmp_path / "other", {"404": video}, candidate_ids=("404",)))
    with pytest.raises(MediaAcquisitionError, match="cannot exceed 5"):
        acquire_local_media(MediaAcquisitionRequest(manifest, tmp_path / "other", {"1": video}, limit=6))


def test_invalid_or_missing_local_files_produce_failed_records(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, count=1)
    invalid = tmp_path / "page.mp4"
    invalid.write_bytes(b"<html>challenge</html>" + b" " * 2048)

    record = acquire_local_media(MediaAcquisitionRequest(manifest, tmp_path / "runtime", {"1": invalid}))[0]

    assert record.status == "FAILED"
    assert record.local_media_path is None
    assert "HTML" in record.errors[0]

    missing = acquire_local_media(MediaAcquisitionRequest(
        manifest, tmp_path / "missing-runtime", {"1": tmp_path / "missing.mp4"}
    ))[0]
    assert missing.status == "FAILED"
    assert "does not exist" in missing.errors[0]


def test_valid_file_is_reused_with_stable_hash(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, count=1)
    video = _video(tmp_path / "operator.mp4")
    request = MediaAcquisitionRequest(manifest, tmp_path / "runtime", {"1": video})

    first = acquire_local_media(request)[0]
    second = acquire_local_media(request)[0]

    assert first.status == "COMPLETED"
    assert second.status == "REUSED"
    assert first.sha256 == hashlib.sha256(video.read_bytes()).hexdigest()
    assert second.sha256 == first.sha256


def test_cli_help_has_no_side_effects(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as error:
        main(["--help"])
    assert error.value.code == 0
    assert list(tmp_path.iterdir()) == []

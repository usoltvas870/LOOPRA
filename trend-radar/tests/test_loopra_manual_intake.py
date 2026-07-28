from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from manual_source_intake import (  # noqa: E402
    ManualIntakeServices,
    build_plan,
    discover_local_media,
    normalize_tiktok_url,
    parse_links_file,
    run_manual_intake,
)
from selection_manifest import read_selection_manifest  # noqa: E402


VIDEO = b"synthetic-mp4" * 200


class Calls:
    acquisition = 0
    inspection = 0
    transcription = 0
    ocr = 0


def _probe(audio: bool = True) -> dict:
    return {
        "valid": True, "duration_seconds": 4.0, "container": "mp4", "video_codec": "h264",
        "width": 1080, "height": 1920, "audio_stream_present": audio, "audio_codec": "aac" if audio else None,
    }


def _validate(path: Path, _maximum: int) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("invalid media")
    if path.read_bytes().startswith(b"corrupt"):
        raise ValueError("ffprobe found no video stream")
    return {"size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "ffprobe": _probe()}


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def _inspect(source: Path, output: Path, item_id: str, canonical_url: str | None) -> dict:
    Calls.inspection += 1
    output.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": "1.1", "status": "COMPLETED", "video_id": item_id,
        "canonical_url": canonical_url, "media_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "media_facts": {"duration_seconds": 4.0, "width": 1080, "height": 1920, "aspect_ratio": .5625,
                        "audio_present": True, "audio_codec": "aac", "sample_rate": "44100", "channels": 2},
        "sampling": {"frame_results": []}, "visual_structure": {"dominant_motion_level": "medium"},
        "evidence": {"contact_sheets": [], "warnings": []},
    }
    (output / "inspection.json").write_text(json.dumps(result), encoding="utf-8")
    return result


def _transcribe(request) -> dict:
    Calls.transcription += 1
    item_id = request.candidate_ids[0]
    return {"status": "COMPLETED", "candidates": [{
        "candidate_video_id": item_id, "status": "COMPLETED", "language": "ru",
        "segments": [{"segment_id": "segment-0001", "start_seconds": 0.0, "end_seconds": 1.0,
                      "normalized_text": "Это полный тестовый текст", "raw_text": "Это полный тестовый текст"}],
        "errors": [],
    }]}


def _ocr(request) -> dict:
    Calls.ocr += 1
    item_id = request.candidate_ids[0]
    return {"status": "COMPLETED", "candidates": [{
        "candidate_video_id": item_id, "status": "COMPLETED",
        "text_events": [{"text": "Текст на экране", "first_seen_at_sec": 0.5}], "errors": [],
    }]}


def _services(acquire=None) -> ManualIntakeServices:
    return ManualIntakeServices(
        validate_media=_validate, copy_media=_copy, acquire_link=acquire,
        inspect=_inspect, transcribe=_transcribe, ocr=_ocr,
    )


def _repo(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    links = tmp_path / "input" / "selected_sources" / "selected_links.txt"
    media = links.parent / "media"
    output = tmp_path / "output" / "manual_intake"
    media.mkdir(parents=True)
    links.write_text("", encoding="utf-8")
    return tmp_path, links, media, output


def _run(tmp_path: Path, **kwargs):
    repo, links, media, output = _repo(tmp_path)
    return run_manual_intake(
        project_id="nura", links_file=links, media_dir=media, output_root=output,
        repository_root=repo, services=_services(), **kwargs,
    )


def test_links_parsing_supports_bom_comments_whitespace_duplicates_and_invalid(tmp_path: Path) -> None:
    path = tmp_path / "selected_links.txt"
    path.write_text("\ufeff # comment\n\n https://www.tiktok.com/@one/video/123?utm_source=x \nhttps://m.tiktok.com/@two/video/123\nbad\n", encoding="utf-8")
    values, duplicates = parse_links_file(path)
    assert [item.status for item in values] == ["READY", "DUPLICATE_INPUT", "INVALID_URL"]
    assert values[0].normalized_url == "https://www.tiktok.com/@source/video/123"
    assert duplicates == 1 and [item.original_order for item in values] == [1, 2, 3]


@pytest.mark.parametrize("value", ["https://example.com/video/1", "file:///x", "https://u:p@www.tiktok.com/@a/video/1"])
def test_url_validation_rejects_non_public_tiktok_video_urls(value: str) -> None:
    with pytest.raises(ValueError, match="INVALID_URL"):
        normalize_tiktok_url(value)


def test_media_discovery_is_nonrecursive_mp4_only_and_ignores_part(tmp_path: Path) -> None:
    (tmp_path / "b.mp4").write_bytes(VIDEO)
    (tmp_path / "a.MP4").write_bytes(VIDEO)
    (tmp_path / "x.mov").write_bytes(VIDEO)
    (tmp_path / "x.mp4.part").write_bytes(VIDEO)
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "x.mp4").write_bytes(VIDEO)
    assert [path.name for path in discover_local_media(tmp_path)] == ["a.MP4", "b.mp4"]


@pytest.mark.parametrize("content", [b"", b"corrupt" * 300])
def test_zero_byte_and_corrupt_media_are_typed_failures(tmp_path: Path, content: bytes) -> None:
    repo, links, media, output = _repo(tmp_path)
    (media / "bad.mp4").write_bytes(content)
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services())
    assert result["status"] == "NO_VALID_INPUTS" and result["failed_source_count"] == 1
    manifest = json.loads((output / result["intake_id"] / "00_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["item_references"][0]["processing_status"] == "MEDIA_ACQUISITION_FAILED"


def test_local_media_builds_portable_complete_package_and_preserves_input(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    source = media / "owner.mp4"
    source.write_bytes(VIDEO)
    before = source.read_bytes()
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services())
    package = output / result["intake_id"]
    item = next((package / "items").iterdir())
    assert result["status"] == "COMPLETED" and source.read_bytes() == before
    assert (item / "source.mp4").read_bytes() == before
    assert {"source.mp4", "source_info.json", "transcript.txt", "transcript_segments.json", "screen_text.txt", "FORMAT_INSPECTION.md", "GPT_HANDOFF_RU.md"} <= {p.name for p in item.iterdir()}
    info = json.loads((item / "source_info.json").read_text(encoding="utf-8"))
    assert info["local_media_hash"] == hashlib.sha256(VIDEO).hexdigest()
    assert info["dimensions"] == {"width": 1080, "height": 1920} and info["audio_presence"] is True
    assert not any(":" in ref[:3] for ref in (info["local_media_reference"], info["output_folder_reference"]))
    handoff = (item / "GPT_HANDOFF_RU.md").read_text(encoding="utf-8")
    assert "ЭТАП 1 — ПОНИМАНИЕ ИСТОЧНИКА" in handoff and "ЭТАП 2 — АДАПТАЦИЯ NURA" in handoff
    assert "не утверждает, что уже поняла" in handoff


def test_duplicate_local_media_merges_by_exact_sha256_and_preserves_order(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    (media / "a.mp4").write_bytes(VIDEO)
    (media / "b.mp4").write_bytes(VIDEO)
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services())
    assert result["accepted_source_count"] == 1 and result["duplicate_input_count"] == 1
    assert [item["processing_status"] for item in result["item_references"]] == ["COMPLETED", "DUPLICATE_INPUT"]
    assert len(list((output / result["intake_id"] / "items").iterdir())) == 1


def test_public_first_link_acquisition_needs_no_session_and_one_failure_does_not_block(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    links.write_text("https://www.tiktok.com/@one/video/111\nhttps://www.tiktok.com/@two/video/222\n", encoding="utf-8")

    def acquire(*, manifest_path: Path, acquisition_output_root: Path, candidate_id: str):
        Calls.acquisition += 1
        if candidate_id.endswith("111"):
            return {"status": "FAILED", "errors": ["public source unavailable"]}
        manifest = read_selection_manifest(manifest_path)
        run_root = acquisition_output_root / manifest.radar_run_id
        target = run_root / candidate_id / "source.mp4"
        target.parent.mkdir(parents=True)
        target.write_bytes(VIDEO)
        record = {"status": "COMPLETED", "candidate_video_id": candidate_id,
                  "local_media_path": f"{candidate_id}/source.mp4", "media_sha256": hashlib.sha256(VIDEO).hexdigest(),
                  "ffprobe_validation": _probe(), "tool_metadata": {"access_mode": "GUEST_SESSION", "credentials_required": False}}
        (target.parent / "acquisition_record.json").write_text(json.dumps(record), encoding="utf-8")
        return record

    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services(acquire))
    assert result["status"] == "PARTIAL" and result["accepted_source_count"] == 1 and result["failed_source_count"] == 1
    assert Calls.acquisition >= 2 and result["search_calls"] == result["provider_calls"] == result["script_calls"] == result["image_calls"] == 0


def test_link_and_local_exact_duplicate_produce_one_item(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    links.write_text("https://www.tiktok.com/@one/video/111\n", encoding="utf-8")
    (media / "same.mp4").write_bytes(VIDEO)

    def acquire(*, manifest_path: Path, acquisition_output_root: Path, candidate_id: str):
        manifest = read_selection_manifest(manifest_path)
        run_root = acquisition_output_root / manifest.radar_run_id
        target = run_root / candidate_id / "source.mp4"
        target.parent.mkdir(parents=True)
        target.write_bytes(VIDEO)
        return {"status": "COMPLETED", "local_media_path": f"{candidate_id}/source.mp4",
                "media_sha256": hashlib.sha256(VIDEO).hexdigest(), "ffprobe_validation": _probe()}

    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services(acquire))
    assert result["accepted_source_count"] == 1 and result["duplicate_input_count"] == 1
    assert len(list((output / result["intake_id"] / "items").iterdir())) == 1


def test_transcription_and_ocr_failures_are_honest_nonblocking_warnings(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    (media / "owner.mp4").write_bytes(VIDEO)
    services = ManualIntakeServices(validate_media=_validate, copy_media=_copy, inspect=_inspect,
                                    transcribe=lambda _request: (_ for _ in ()).throw(RuntimeError("asr unavailable")),
                                    ocr=lambda _request: (_ for _ in ()).throw(RuntimeError("ocr unavailable")))
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=services)
    item = next((output / result["intake_id"] / "items").iterdir())
    assert result["status"] == "COMPLETED_WITH_WARNINGS"
    assert "TRANSCRIPTION_FAILED" in (item / "transcript.txt").read_text(encoding="utf-8")
    assert "OCR_FAILED" in (item / "screen_text.txt").read_text(encoding="utf-8")


def test_dry_run_has_zero_side_effects_and_never_calls_tools(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    (media / "owner.mp4").write_bytes(VIDEO)
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services(), dry_run=True)
    assert result["status"] == "DRY_RUN" and result["side_effects"] == 0
    assert result["browser_calls"] == result["inspection_calls"] == result["transcription_calls"] == result["ocr_calls"] == 0
    assert not output.exists()


def test_identical_run_and_reuse_only_skip_all_processing(tmp_path: Path) -> None:
    Calls.inspection = Calls.transcription = Calls.ocr = 0
    repo, links, media, output = _repo(tmp_path)
    (media / "owner.mp4").write_bytes(VIDEO)
    first = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                              repository_root=repo, services=_services())
    counts = (Calls.inspection, Calls.transcription, Calls.ocr)
    second = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services(), reuse_only=True)
    assert second["status"] == "REUSED" and second["content_hash"] == first["content_hash"]
    assert second["output_package_hash"] == first["output_package_hash"]
    assert (Calls.inspection, Calls.transcription, Calls.ocr) == counts
    assert second["browser_calls"] == second["acquisition_calls"] == second["inspection_calls"] == second["transcription_calls"] == second["ocr_calls"] == 0


def test_reuse_only_blocks_missing_artifact_without_side_effects(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    (media / "owner.mp4").write_bytes(VIDEO)
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services(), reuse_only=True)
    assert result["status"] == "BLOCKED" and result["failure_code"] == "REUSABLE_ARTIFACT_NOT_FOUND"
    assert not output.exists()


def test_manifest_has_versioned_contract_portable_references_and_no_secrets(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    (media / "owner.mp4").write_bytes(VIDEO)
    result = run_manual_intake(project_id="nura", links_file=links, media_dir=media, output_root=output,
                               repository_root=repo, services=_services())
    manifest_text = (output / result["intake_id"] / "00_MANIFEST.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    required = {"schema_version", "intake_id", "intake_version", "project_id", "created_at",
                "links_file_reference", "media_directory_reference", "parsed_link_count", "local_media_count",
                "duplicate_input_count", "accepted_source_count", "failed_source_count", "item_references",
                "output_package_reference", "output_package_hash", "provider_calls", "search_calls", "script_calls",
                "image_calls", "reuse_metadata", "content_hash"}
    assert required <= manifest.keys() and manifest["schema_version"] == "1.0"
    assert str(repo) not in manifest_text and "authorization" not in manifest_text.lower() and "cookie" not in manifest_text.lower()
    assert manifest["output_package_reference"].startswith("output/manual_intake/")


def test_limit_preserves_first_combined_input_order(tmp_path: Path) -> None:
    repo, links, media, output = _repo(tmp_path)
    links.write_text("https://www.tiktok.com/@one/video/111\nhttps://www.tiktok.com/@two/video/222\n", encoding="utf-8")
    (media / "z.mp4").write_bytes(VIDEO)
    plan = build_plan(project_id="nura", links_file=links, media_dir=media, output_root=output,
                      repository_root=repo, limit=1)
    assert [item.video_id for item in plan.parsed_links] == ["111"] and plan.local_media == ()

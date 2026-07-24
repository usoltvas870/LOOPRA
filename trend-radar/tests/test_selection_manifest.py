import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from selection_manifest import (
    REQUESTED_CANDIDATE_COUNT,
    SelectionManifestError,
    build_selection_manifest,
    read_selection_manifest,
    write_selection_manifest,
)


def _candidate(video_id: str, score: float, **overrides) -> dict:
    candidate = {
        "video_id": video_id,
        "author_username": "\u0430\u0432\u0442\u043e\u0440",
        "source_type": "keyword",
        "source_value": "\u0442\u0435\u0441\u0442",
        "url": f"https://www.tiktok.com/@author/video/{video_id}",
        "caption": "\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439 \u0440\u043e\u043b\u0438\u043a",
        "views": 1000,
        "likes": 100,
        "comments": 10,
        "shares": 5,
        "author_followers": 500,
        "published_at": "2026-07-24T00:00:00Z",
        "collected_at": "2026-07-24T01:00:00Z",
        "final_score": score,
        "reach_score": score - 1,
        "engagement_score": score - 2,
        "freshness_score": score - 3,
        "momentum_proxy": score - 4,
        "data_confidence": "HIGH",
        "identity_confidence": "HIGH",
        "classification": "CURRENT",
        "provenance": {"primary_source_type": "keyword", "primary_source_value": "\u0442\u0435\u0441\u0442"},
    }
    candidate.update(overrides)
    return candidate


def test_manifest_reuses_existing_order_score_and_tie_order() -> None:
    ranked = [_candidate("2", 99), _candidate("1", 99), _candidate("3", 50)]

    manifest = build_selection_manifest(ranked, radar_run_id="run-1", created_at="2026-07-24T00:00:00Z")

    assert [entry.video_id for entry in manifest.candidates] == ["2", "1", "3"]
    assert [entry.rank for entry in manifest.candidates] == [1, 2, 3]
    assert [entry.score_snapshot["final_score"] for entry in manifest.candidates] == [99, 99, 50]
    assert manifest.requested_candidate_count == REQUESTED_CANDIDATE_COUNT
    assert manifest.selection_complete is False
    assert manifest.selection_reason == "fewer_ranked_candidates_than_requested"


def test_manifest_is_top_twenty_without_resorting_or_filtering() -> None:
    ranked = [_candidate(str(index), float(1000 - index)) for index in range(25)]

    manifest = build_selection_manifest(ranked, radar_run_id="run-2", created_at="2026-07-24T00:00:00Z")

    assert [entry.video_id for entry in manifest.candidates] == [str(index) for index in range(20)]
    assert manifest.selected_candidate_count == 20
    assert manifest.selection_complete is True


def test_duplicate_ranked_video_ids_are_rejected() -> None:
    with pytest.raises(SelectionManifestError, match="unique"):
        build_selection_manifest([_candidate("1", 1), _candidate("1", 0)], radar_run_id="run-3")


def test_write_is_atomic_idempotent_and_readable(tmp_path: Path) -> None:
    manifest = build_selection_manifest([_candidate("1", 1)], radar_run_id="run-4", created_at="2026-07-24T00:00:00Z")

    path = write_selection_manifest(manifest, tmp_path)
    same_content_new_timestamp = build_selection_manifest(
        [_candidate("1", 1)], radar_run_id="run-4", created_at="2026-07-24T01:00:00Z"
    )
    repeated = write_selection_manifest(same_content_new_timestamp, tmp_path)
    loaded = read_selection_manifest(path)

    assert repeated == path
    assert loaded.manifest_hash == manifest.manifest_hash
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == "1.0"


def test_manifest_export_round_trip_preserves_utf8_candidate_data(tmp_path: Path) -> None:
    manifest = build_selection_manifest([_candidate("1", 1)], radar_run_id="run-utf8")

    path = write_selection_manifest(manifest, tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["candidates"][0]["caption"] == "\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439 \u0440\u043e\u043b\u0438\u043a"
    assert read_selection_manifest(path).candidates[0].author == "\u0430\u0432\u0442\u043e\u0440"


def test_content_hash_is_deterministic_and_snapshot_excludes_forbidden_fields() -> None:
    candidate = _candidate(
        "1", 1, cookies="secret", authorization="secret", transcript="not selected"
    )
    first = build_selection_manifest([candidate], radar_run_id="run-6", created_at="2026-07-24T00:00:00Z")
    second = build_selection_manifest([candidate], radar_run_id="run-6", created_at="2026-07-24T01:00:00Z")

    serialized = json.dumps(first.to_dict(), ensure_ascii=False)

    assert first.manifest_hash == second.manifest_hash
    assert first.manifest_id == second.manifest_id
    for forbidden in ("cookies", "authorization", "transcript", "production_complexity", "ocr"):
        assert forbidden not in serialized


def test_write_rejects_different_content_for_same_run(tmp_path: Path) -> None:
    first = build_selection_manifest([_candidate("1", 1)], radar_run_id="run-5", created_at="2026-07-24T00:00:00Z")
    second = build_selection_manifest([_candidate("2", 2)], radar_run_id="run-5", created_at="2026-07-24T00:00:00Z")

    write_selection_manifest(first, tmp_path)

    with pytest.raises(SelectionManifestError, match="conflict"):
        write_selection_manifest(second, tmp_path)

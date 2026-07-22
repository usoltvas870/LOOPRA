from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from core.domain import ContentFormat, ProductionBriefStatus
from core.services.episode_package import (
    EpisodePackageValidationError,
    load_episode_package,
    stage_episode_package,
)


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "episode_package"


def _copy_fixture(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    package_root = tmp_path / "episode"
    shutil.copytree(FIXTURE_ROOT, package_root)
    return package_root / "episode.json"


def _rewrite(manifest: Path, mutate) -> None:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    mutate(payload)
    manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _error_paths(manifest: Path) -> set[str]:
    with pytest.raises(EpisodePackageValidationError) as caught:
        load_episode_package(manifest)
    return {issue.path for issue in caught.value.issues}


def test_valid_manifest_maps_to_canonical_production_brief(tmp_path: Path) -> None:
    manifest = _copy_fixture(tmp_path)

    package = load_episode_package(manifest)

    assert package.brief.schema_version == 1
    assert package.brief.production_brief_id == "fixture_episode"
    assert package.brief.title == "Технический диалоговый эпизод"
    assert package.brief.content_format == ContentFormat.DIALOG_MINISERIES
    assert package.brief.status == ProductionBriefStatus.VALIDATED
    assert [scene.scene_id for scene in package.brief.scenes] == [
        "opening", "question", "warning", "route", "turn", "fear", "name", "decision", "finale"
    ]
    assert package.brief.scenes[0].duration_sec == 1.0
    assert package.brief.scenes[1].duration_sec == 1.25
    assert package.source_paths[0] == manifest.parent / "assets" / "scene_01_clean.png"


def test_staging_copies_sources_without_changing_package_paths(tmp_path: Path) -> None:
    manifest = _copy_fixture(tmp_path)
    package = load_episode_package(manifest)
    before = package.source_hashes()

    staged = stage_episode_package(package, tmp_path / "runtime_projects")

    assert package.source_hashes() == before
    assert staged.scenes[0].image_source == "episodes/fixture_episode/frames/opening.png"
    assert staged.subtitles.font_path.startswith("episodes/fixture_episode/assets/")
    assert (tmp_path / "runtime_projects" / "fixture_project" / staged.scenes[0].image_source).is_file()
    assert (tmp_path / "runtime_projects" / "fixture_project" / "project.yaml").is_file()


def test_missing_and_malformed_manifest_are_reported(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert "$" in _error_paths(missing)
    malformed = tmp_path / "episode.json"
    malformed.write_text("{not-json", encoding="utf-8")
    assert "$" in _error_paths(malformed)


@pytest.mark.parametrize(
    ("mutate", "expected_path"),
    [
        (lambda data: data.__setitem__("schema_version", 2), "$.schema_version"),
        (lambda data: data.pop("episode_id"), "$.episode_id"),
        (lambda data: data.__setitem__("unexpected", True), "$.unexpected"),
        (lambda data: data.__setitem__("content_format", "short_vertical_video"), "$.content_format"),
        (lambda data: data.__setitem__("target_platforms", ["telegram"]), "$.target_platforms[0]"),
        (lambda data: data.__setitem__("frames", []), "$.frames"),
        (lambda data: data["frames"][1].__setitem__("frame_id", "opening"), "$.frames[1].frame_id"),
        (lambda data: data["frames"][0].__setitem__("image", "assets/missing.png"), "$.frames[0].image"),
        (lambda data: data["frames"][0].__setitem__("image", "../outside.png"), "$.frames[0].image"),
        (lambda data: data["frames"][0].__setitem__("image", "assets/frame.gif"), "$.frames[0].image"),
        (lambda data: data["frames"][0].__setitem__("speaker", "unknown"), "$.frames[0].speaker"),
        (lambda data: data["frames"][0].__setitem__("position", "unknown"), "$.frames[0].position"),
        (lambda data: data["frames"][0].__setitem__("tail_anchor", {"x": 2, "y": 0}), "$.frames[0].tail_anchor.x"),
        (lambda data: data["frames"][0].__setitem__("duration_sec", 0), "$.frames[0].duration_sec"),
        (lambda data: data["frames"][0].__setitem__("transition_type", "spin"), "$.frames[0].transition_type"),
        (lambda data: data["frames"][0].__setitem__("transition_duration_sec", 1.0), "$.frames[0].transition_duration_sec"),
        (lambda data: data["frames"][0].__setitem__("duration_sec", 0.2), "$.frames[0].duration_sec"),
        (lambda data: data["frames"][0].__setitem__("text", "   "), "$.frames[0].text"),
        (lambda data: data["output"].__setitem__("resolution_width", 271), "$.output.resolution_width"),
        (lambda data: data["output"].__setitem__("generate_comic_master_video", "false"), "$.output.generate_comic_master_video"),
    ],
)
def test_invalid_manifest_fields_are_aggregated(tmp_path: Path, mutate, expected_path: str) -> None:
    manifest = _copy_fixture(tmp_path)
    _rewrite(manifest, mutate)

    assert expected_path in _error_paths(manifest)


def test_directory_and_corrupt_image_are_rejected(tmp_path: Path) -> None:
    manifest = _copy_fixture(tmp_path)
    _rewrite(manifest, lambda data: data["frames"][0].__setitem__("image", "assets"))
    assert "$.frames[0].image" in _error_paths(manifest)

    manifest = _copy_fixture(tmp_path / "second")
    corrupt = manifest.parent / "assets" / "corrupt.png"
    corrupt.write_text("not an image", encoding="utf-8")
    _rewrite(manifest, lambda data: data["frames"][0].__setitem__("image", "assets/corrupt.png"))
    assert "$.frames[0].image" in _error_paths(manifest)


def test_text_overflow_is_rejected_before_render(tmp_path: Path) -> None:
    manifest = _copy_fixture(tmp_path)
    _rewrite(
        manifest,
        lambda data: data["frames"][0].__setitem__("text", "Очень длинная реплика " * 80),
    )

    assert "$.frames[0]" in _error_paths(manifest)

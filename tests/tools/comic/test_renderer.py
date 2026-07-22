from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from PIL import Image

from core.domain import ComicOverlay, ComicTailAnchor, ContentFormat, ProductionBrief, ProductionScene, ProductionSubtitles
from core.tools.comic import ComicRenderError, render_comic_frame, render_comic_frames
from core.tools.comic.renderer import _bubble_box, _tail_polygon


FONT = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _overlay(speaker: str = "nura", position: str = "top_left", anchor: tuple[float, float] = (0.8, 0.8), text: str = "Ёлка — «тестовая реплика»") -> ComicOverlay:
    return ComicOverlay(speaker=speaker, text=text, position=position, tail_anchor=ComicTailAnchor(x=anchor[0], y=anchor[1]))


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "source.png"
    Image.new("RGB", (480, 800), (40, 80, 120)).save(path, "PNG")
    return path


@pytest.mark.parametrize("speaker", ["nura", "woman", "shadow"])
def test_themes_render_distinct_png_without_mutating_source(source: Path, tmp_path: Path, speaker: str) -> None:
    before = _hash(source)
    output = render_comic_frame(source, _overlay(speaker=speaker), tmp_path / f"{speaker}.png", FONT)
    assert output.is_file()
    assert _hash(source) == before
    assert _hash(output) != before
    with Image.open(output) as image:
        assert image.size == (480, 800)
        assert image.mode == "RGBA"


@pytest.mark.parametrize("position,anchor", [
    ("top_left", (0.8, 0.8)), ("top_center", (0.1, 0.8)), ("top_right", (0.1, 0.8)),
    ("middle_left", (0.9, 0.1)), ("middle_right", (0.1, 0.1)),
    ("bottom_left", (0.8, 0.1)), ("bottom_right", (0.1, 0.1)),
])
def test_all_positions_and_tails_stay_inside_frame(source: Path, tmp_path: Path, position: str, anchor: tuple[float, float]) -> None:
    output = render_comic_frame(source, _overlay(position=position, anchor=anchor), tmp_path / f"{position}.png", FONT)
    with Image.open(output) as image:
        assert image.size == (480, 800)


def test_top_bubble_reserves_motion_safe_space_and_tail_stays_bounded() -> None:
    box = _bubble_box("top_center", 480, 800, 240, 120)
    tail = _tail_polygon(box, (360, 700), 480, 800)
    base_center_x = (tail[0][0] + tail[1][0]) / 2
    base_center_y = (tail[0][1] + tail[1][1]) / 2
    tail_length = ((tail[2][0] - base_center_x) ** 2 + (tail[2][1] - base_center_y) ** 2) ** 0.5

    assert box[1] == 108
    assert tail_length <= 48


def test_anchor_inside_bubble_and_missing_inputs_raise_clean_errors(source: Path, tmp_path: Path) -> None:
    with pytest.raises(ComicRenderError, match="outside"):
        render_comic_frame(source, _overlay(anchor=(0.2, 0.2)), tmp_path / "partial.png", FONT)
    assert not (tmp_path / "partial.png").exists()
    with pytest.raises(ComicRenderError, match="Font"):
        render_comic_frame(source, _overlay(), tmp_path / "missing_font.png", tmp_path / "missing.ttf")
    with pytest.raises(ComicRenderError, match="Source"):
        render_comic_frame(tmp_path / "missing.png", _overlay(), tmp_path / "missing_source.png", FONT)


def test_long_text_shrinks_and_impossible_text_removes_partial_output(source: Path, tmp_path: Path) -> None:
    output = render_comic_frame(source, _overlay(text="Текст для уменьшения размера шрифта " * 3), tmp_path / "long.png", FONT)
    assert output.exists()
    with pytest.raises(ComicRenderError, match="does not fit"):
        render_comic_frame(source, _overlay(text="сверхдлинноенеразбиваемоеслово" * 20), tmp_path / "failed.png", FONT)
    assert not (tmp_path / "failed.png").exists()


def test_batch_renderer_orders_frames_cleans_stale_outputs_and_preserves_sources(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    source_paths = []
    for index, color in enumerate(((30, 70, 110), (70, 40, 100), (90, 90, 40))):
        source = project_root / f"source_{index}.png"
        Image.new("RGB", (480, 800), color).save(source, "PNG")
        source_paths.append(source)
    before = [_hash(path) for path in source_paths]
    brief = ProductionBrief(
        workspace_id="internal", project_id="nura", production_brief_id="brief_batch", scenario_id="scenario_batch",
        content_format=ContentFormat.DIALOG_MINISERIES, subtitles=ProductionSubtitles(font_path=str(FONT)),
        scenes=[ProductionScene(index=index, image_source=path.name, duration_sec=1.0, comic_overlay=_overlay(speaker=speaker, position=position, anchor=anchor)) for index, (path, speaker, position, anchor) in enumerate(zip(source_paths, ("nura", "woman", "shadow"), ("top_left", "middle_right", "bottom_left"), ((0.8, 0.8), (0.1, 0.1), (0.8, 0.1)), strict=True))],
    )
    output_dir = tmp_path / "outputs"
    (output_dir / "scene_99.png").parent.mkdir()
    (output_dir / "scene_99.png").write_bytes(b"stale")
    foreign = output_dir / "keep.txt"
    foreign.write_text("keep", encoding="utf-8")

    outputs = render_comic_frames(brief, output_dir, project_root)

    assert [path.name for path in outputs] == ["scene_01.png", "scene_02.png", "scene_03.png"]
    assert not (output_dir / "scene_99.png").exists()
    assert foreign.read_text(encoding="utf-8") == "keep"
    assert [_hash(path) for path in source_paths] == before
    assert all(_hash(output) != _hash(source) for output, source in zip(outputs, source_paths, strict=True))


def test_batch_renderer_rejects_path_traversal_and_cleans_partial_frames(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    source = project_root / "source.png"
    Image.new("RGB", (480, 800), "blue").save(source, "PNG")
    brief = ProductionBrief(
        workspace_id="internal", project_id="nura", production_brief_id="brief_escape", scenario_id="scenario_escape",
        content_format=ContentFormat.DIALOG_MINISERIES, subtitles=ProductionSubtitles(font_path=str(FONT)),
        scenes=[
            ProductionScene(index=0, image_source="source.png", duration_sec=1.0, comic_overlay=_overlay()),
            ProductionScene(index=1, image_source="../outside.png", duration_sec=1.0, comic_overlay=_overlay(speaker="woman")),
        ],
    )
    output_dir = tmp_path / "outputs"
    with pytest.raises(ComicRenderError, match="escapes"):
        render_comic_frames(brief, output_dir, project_root)
    assert not list(output_dir.glob("scene_*.png"))

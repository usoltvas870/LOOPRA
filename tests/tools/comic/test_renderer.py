from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from PIL import Image

from core.domain import ComicOverlay, ComicTailAnchor
from core.tools.comic import ComicRenderError, render_comic_frame


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
        x, y = round(anchor[0] * 479), round(anchor[1] * 799)
        assert image.size == (480, 800)
        assert image.getpixel((x, y)) != (40, 80, 120, 255)


def test_anchor_inside_bubble_and_missing_inputs_raise_clean_errors(source: Path, tmp_path: Path) -> None:
    with pytest.raises(ComicRenderError, match="outside"):
        render_comic_frame(source, _overlay(anchor=(0.2, 0.1)), tmp_path / "partial.png", FONT)
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

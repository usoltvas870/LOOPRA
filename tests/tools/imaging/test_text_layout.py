from __future__ import annotations

from pathlib import Path

import pytest
from PIL import ImageFont

from core.tools.imaging.text_layout import TextLayoutError, fit_text, wrap_text


FONT = Path(__import__("os").environ["WINDIR"]) / "Fonts" / "arial.ttf"


def test_wrap_text_preserves_newlines_and_cyrillic() -> None:
    font = ImageFont.truetype(FONT, 24)
    lines = wrap_text("Ёлка — «важный тест»\nНовая строка", font, 180)
    assert any("Ёлка" in line for line in lines)
    assert "" not in lines
    assert any("Новая" in line for line in lines)


def test_fit_text_reduces_font_size() -> None:
    layout = fit_text("слово " * 12, FONT, max_width=170, max_height=100, max_lines=4, preferred_size=36, min_size=12)
    assert layout.font_size < 36
    assert len(layout.lines) <= 4


def test_fit_text_rejects_overflow_without_clipping() -> None:
    with pytest.raises(TextLayoutError):
        fit_text("непомещаемоесверхдлинноеслово", FONT, max_width=20, max_height=20, max_lines=1, preferred_size=16, min_size=12)

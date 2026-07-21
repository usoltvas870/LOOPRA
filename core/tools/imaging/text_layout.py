from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import ImageFont


class TextLayoutError(ValueError):
    """Raised when text cannot fit inside the supplied layout bounds."""


@dataclass(frozen=True)
class TextLayout:
    font: ImageFont.FreeTypeFont
    lines: tuple[str, ...]
    line_height: int
    font_size: int

    @property
    def height(self) -> int:
        return self.line_height * len(self.lines)


def text_width(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> int:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
    if max_width <= 0:
        raise TextLayoutError("Text layout width must be positive")

    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current: list[str] = []
        for word in paragraph.split():
            candidate = " ".join([*current, word])
            if current and text_width(candidate, font) > max_width:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
    return lines


def fit_text(
    text: str,
    font_path: Path,
    *,
    max_width: int,
    max_height: int,
    max_lines: int,
    preferred_size: int,
    min_size: int,
) -> TextLayout:
    if not font_path.is_file():
        raise TextLayoutError(f"Font file does not exist: {font_path}")
    if max_lines <= 0 or max_height <= 0 or preferred_size < min_size:
        raise TextLayoutError("Invalid text layout constraints")

    for size in range(preferred_size, min_size - 1, -1):
        try:
            font = ImageFont.truetype(font_path, size=size)
        except OSError as error:
            raise TextLayoutError(f"Unable to load font: {font_path}") from error
        lines = wrap_text(text, font, max_width)
        line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
        if len(lines) <= max_lines and line_height * len(lines) <= max_height and all(text_width(line, font) <= max_width for line in lines):
            return TextLayout(font=font, lines=tuple(lines), line_height=line_height, font_size=size)
    raise TextLayoutError("Text does not fit within the configured bubble bounds")

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path

from PIL import Image, ImageDraw

from core.domain import ComicOverlay, ProductionBrief
from core.tools.imaging.text_layout import TextLayout, TextLayoutError, fit_text, text_width


class ComicRenderError(ValueError):
    """Raised when a static comic overlay cannot be rendered safely."""


@dataclass(frozen=True)
class ComicTheme:
    fill: tuple[int, int, int, int]
    outline: tuple[int, int, int, int]
    text: tuple[int, int, int, int]


THEMES: dict[str, ComicTheme] = {
    "nura": ComicTheme((250, 246, 239, 248), (32, 27, 22, 255), (26, 22, 18, 255)),
    "woman": ComicTheme((255, 238, 215, 238), (118, 83, 57, 255), (48, 35, 28, 255)),
    "shadow": ComicTheme((50, 53, 61, 235), (198, 201, 207, 255), (249, 248, 245, 255)),
}

_SAFE_MARGIN_RATIO = 0.05
_MOTION_SAFE_TOP_MARGIN_RATIO = 0.135
_BUBBLE_WIDTH_RATIO = 0.70
_BUBBLE_MIN_HEIGHT_RATIO = 0.11
_BUBBLE_MAX_HEIGHT_RATIO = 0.19
_MAX_LINES = 4


@dataclass(frozen=True)
class _PreparedComicFrame:
    image: Image.Image
    theme: ComicTheme
    bubble_width: int
    bubble_height: int
    box: tuple[int, int, int, int]
    tail: list[tuple[int, int]]
    layout: TextLayout


def _bubble_box(position: str, width: int, height: int, bubble_width: int, bubble_height: int) -> tuple[int, int, int, int]:
    margin_x = max(1, round(width * _SAFE_MARGIN_RATIO))
    margin_y = max(1, round(height * _SAFE_MARGIN_RATIO))
    if bubble_width > width - 2 * margin_x or bubble_height > height - 2 * margin_y:
        raise ComicRenderError("Bubble does not fit within the image safe margins")
    horizontal = {"top_left": "left", "top_center": "center", "top_right": "right", "middle_left": "left", "middle_right": "right", "bottom_left": "left", "bottom_right": "right"}[position]
    vertical = "top" if position.startswith("top") else "middle" if position.startswith("middle") else "bottom"
    x0 = margin_x if horizontal == "left" else (width - bubble_width) // 2 if horizontal == "center" else width - margin_x - bubble_width
    top_safe_y = max(margin_y, round(height * _MOTION_SAFE_TOP_MARGIN_RATIO))
    y0 = top_safe_y if vertical == "top" else (height - bubble_height) // 2 if vertical == "middle" else height - margin_y - bubble_height
    return x0, y0, x0 + bubble_width, y0 + bubble_height


def _tail_polygon(box: tuple[int, int, int, int], anchor: tuple[int, int], width: int, height: int) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    ax, ay = anchor
    if x0 <= ax <= x1 and y0 <= ay <= y1:
        raise ComicRenderError("Tail anchor must be outside the bubble body")
    side_distances = {"left": abs(ax - x0), "right": abs(ax - x1), "top": abs(ay - y0), "bottom": abs(ay - y1)}
    side = min(side_distances, key=side_distances.get)
    base_half = max(6, round(min(width, height) * 0.03))
    if side in {"left", "right"}:
        bx = x0 if side == "left" else x1
        by = min(max(ay, y0 + base_half), y1 - base_half)
        base = [(bx, by - base_half), (bx, by + base_half)]
    else:
        by = y0 if side == "top" else y1
        bx = min(max(ax, x0 + base_half), x1 - base_half)
        base = [(bx - base_half, by), (bx + base_half, by)]
    base_center_x = (base[0][0] + base[1][0]) / 2
    base_center_y = (base[0][1] + base[1][1]) / 2
    distance = hypot(ax - base_center_x, ay - base_center_y)
    if distance == 0:
        raise ComicRenderError("Tail anchor must not overlap the bubble edge")
    max_tail_length = max(8, round(min(width, height) * 0.10))
    tail_ratio = min(1.0, max_tail_length / distance)
    tip = (
        round(base_center_x + (ax - base_center_x) * tail_ratio),
        round(base_center_y + (ay - base_center_y) * tail_ratio),
    )
    return [base[0], base[1], tip]


def _prepare_comic_frame(
    source_image: Path, overlay: ComicOverlay | None, font_path: Path
) -> _PreparedComicFrame:
    if overlay is None:
        raise ComicRenderError("Comic overlay is required")
    if not source_image.is_file():
        raise ComicRenderError(f"Source image does not exist: {source_image}")
    if not font_path.is_file():
        raise ComicRenderError(f"Font file does not exist: {font_path}")
    try:
        with Image.open(source_image) as opened:
            image = opened.convert("RGBA").copy()
        width, height = image.size
        theme = THEMES[overlay.speaker.value]
        bubble_width = max(80, round(width * _BUBBLE_WIDTH_RATIO))
        padding_x = max(10, round(width * 0.032))
        padding_y = max(8, round(height * 0.012))
        min_bubble_height = max(48, round(height * _BUBBLE_MIN_HEIGHT_RATIO))
        max_bubble_height = max(min_bubble_height, round(height * _BUBBLE_MAX_HEIGHT_RATIO))
        layout = fit_text(
            overlay.text,
            font_path,
            max_width=bubble_width - 2 * padding_x,
            max_height=max(1, max_bubble_height - 2 * padding_y),
            max_lines=_MAX_LINES,
            preferred_size=max(18, round(min(width, height) * 0.037)),
            min_size=max(12, round(min(width, height) * 0.020)),
        )
        bubble_height = max(min_bubble_height, layout.height + 2 * padding_y)
        box = _bubble_box(overlay.position.value, width, height, bubble_width, bubble_height)
        anchor = (
            round(overlay.tail_anchor.x * (width - 1)),
            round(overlay.tail_anchor.y * (height - 1)),
        )
        tail = _tail_polygon(box, anchor, width, height)
        return _PreparedComicFrame(
            image=image,
            theme=theme,
            bubble_width=bubble_width,
            bubble_height=bubble_height,
            box=box,
            tail=tail,
            layout=layout,
        )
    except (TextLayoutError, KeyError, OSError, ValueError) as error:
        if isinstance(error, ComicRenderError):
            raise
        raise ComicRenderError(str(error)) from error


def validate_comic_frame_layout(
    source_image: Path, overlay: ComicOverlay | None, font_path: Path
) -> None:
    """Validate image, text layout, bubble, and tail geometry without writing output."""
    _prepare_comic_frame(Path(source_image), overlay, Path(font_path))


def render_comic_frame(source_image: Path, overlay: ComicOverlay | None, output_path: Path, font_path: Path) -> Path:
    """Render one comic bubble over a source image without modifying that source."""
    source_image, output_path, font_path = Path(source_image), Path(output_path), Path(font_path)
    if source_image.resolve() == output_path.resolve():
        raise ComicRenderError("Output path must differ from the source image")
    try:
        prepared = _prepare_comic_frame(source_image, overlay, font_path)
        width, height = prepared.image.size
        draw = ImageDraw.Draw(prepared.image, "RGBA")
        outline_width = max(1, round(min(width, height) * 0.003))
        draw.polygon(
            prepared.tail,
            fill=prepared.theme.fill,
            outline=prepared.theme.outline,
            width=outline_width,
        )
        draw.rounded_rectangle(
            prepared.box,
            radius=max(8, round(min(width, height) * 0.052)),
            fill=prepared.theme.fill,
            outline=prepared.theme.outline,
            width=outline_width,
        )
        text_y = prepared.box[1] + (prepared.bubble_height - prepared.layout.height) // 2
        for line in prepared.layout.lines:
            draw.text(
                (
                    prepared.box[0]
                    + (prepared.bubble_width - text_width(line, prepared.layout.font)) // 2,
                    text_y,
                ),
                line,
                font=prepared.layout.font,
                fill=prepared.theme.text,
            )
            text_y += prepared.layout.line_height
        output_path.parent.mkdir(parents=True, exist_ok=True)
        prepared.image.save(output_path, "PNG")
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise ComicRenderError(f"Comic output was not created: {output_path}")
        return output_path
    except (TextLayoutError, KeyError, OSError, ValueError) as error:
        if output_path.exists():
            output_path.unlink()
        if isinstance(error, ComicRenderError):
            raise
        raise ComicRenderError(str(error)) from error


def render_comic_frames(brief: ProductionBrief, output_dir: Path, project_root: Path) -> list[Path]:
    """Render an ordered static comic episode and remove partial frames on failure."""
    output_dir = Path(output_dir)
    project_root = Path(project_root).resolve()
    font_path = Path(brief.subtitles.font_path)
    if not font_path.is_absolute():
        font_path = project_root / font_path
    if not font_path.is_file():
        raise ComicRenderError(f"Font file does not exist: {font_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("scene_*.png"):
        stale.unlink()

    rendered: list[Path] = []
    try:
        for number, scene in enumerate(brief.scenes, start=1):
            source = (project_root / scene.image_source).resolve()
            try:
                source.relative_to(project_root)
            except ValueError as exc:
                raise ComicRenderError(f"Comic source escapes project root: {scene.image_source}") from exc
            output_path = output_dir / f"scene_{number:02d}.png"
            rendered.append(render_comic_frame(source, scene.comic_overlay, output_path, font_path))
        return rendered
    except Exception:
        for partial in output_dir.glob("scene_*.png"):
            partial.unlink()
        raise

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image

from core.domain import PublishingPlatform


class ComicInstagramRenderError(ValueError):
    """Raised when comic frames cannot be adapted safely for Instagram."""


Color = tuple[int, int, int] | tuple[int, int, int, int] | str
_OWNED_SLIDE_NAME = re.compile(r"^\d+\.png$")


@dataclass(frozen=True, slots=True)
class ComicInstagramPreset:
    platform: PublishingPlatform = PublishingPlatform.INSTAGRAM
    output_slug: str = "instagram"
    width: int = 1080
    height: int = 1350
    aspect_ratio: str = "4:5"
    fit_strategy: str = "contain"
    background_strategy: str = "solid"
    background: tuple[int, int, int, int] = (18, 18, 18, 255)
    output_format: str = "PNG"
    filename_width: int = 2
    crop_allowed: bool = False
    stretch_allowed: bool = False

    def __post_init__(self) -> None:
        if self.platform != PublishingPlatform.INSTAGRAM:
            raise ValueError("Comic Instagram preset must target Instagram")
        if self.width <= 0 or self.height <= 0 or self.filename_width < 2:
            raise ValueError("Comic Instagram dimensions and filename width must be positive")
        if self.fit_strategy != "contain" or self.crop_allowed or self.stretch_allowed:
            raise ValueError("Comic Instagram preset must use contain without crop or stretch")
        if self.output_format != "PNG":
            raise ValueError("Comic Instagram output format must be PNG")

    def filename(self, index: int) -> str:
        if index < 1:
            raise ValueError("Comic Instagram slide index must be positive")
        return f"{index:0{self.filename_width}d}.png"


INSTAGRAM_COMIC_PRESET = ComicInstagramPreset()


def contain_geometry(
    source_size: tuple[int, int], target_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    source_width, source_height = source_size
    target_width, target_height = target_size
    if min(source_width, source_height, target_width, target_height) <= 0:
        raise ComicInstagramRenderError("Contain geometry requires positive dimensions")
    scale = min(target_width / source_width, target_height / source_height)
    rendered_width = max(1, round(source_width * scale))
    rendered_height = max(1, round(source_height * scale))
    offset_x = (target_width - rendered_width) // 2
    offset_y = (target_height - rendered_height) // 2
    return rendered_width, rendered_height, offset_x, offset_y


def _normalize_color(value: Color) -> tuple[int, int, int, int]:
    if isinstance(value, str):
        raw = value.strip().lstrip("#")
        if len(raw) not in {6, 8}:
            raise ComicInstagramRenderError("Background color must be #RRGGBB or #RRGGBBAA")
        try:
            channels = tuple(int(raw[index : index + 2], 16) for index in range(0, len(raw), 2))
        except ValueError as exc:
            raise ComicInstagramRenderError("Background color contains invalid hex digits") from exc
        return (*channels, 255) if len(channels) == 3 else channels  # type: ignore[return-value]
    if len(value) not in {3, 4} or any(not 0 <= channel <= 255 for channel in value):
        raise ComicInstagramRenderError("Background color must contain three or four byte channels")
    return (*value, 255) if len(value) == 3 else value


def render_comic_instagram_carousel(
    comic_frame_paths: Sequence[Path],
    output_dir: Path,
    preset: ComicInstagramPreset = INSTAGRAM_COMIC_PRESET,
    *,
    render_job_root: Path,
    background: Color | None = None,
) -> list[Path]:
    """Adapt ordered, already-composited comic PNGs to an Instagram canvas."""
    frames = tuple(Path(path) for path in comic_frame_paths)
    if not frames:
        raise ComicInstagramRenderError("Comic Instagram export requires at least one frame")
    resolved_frames = tuple(path.resolve() for path in frames)
    if len(set(resolved_frames)) != len(resolved_frames):
        raise ComicInstagramRenderError("Comic Instagram frame paths must be unique")

    render_job_root = Path(render_job_root).resolve()
    output_dir = Path(output_dir).resolve()
    expected_dir = (render_job_root / "comic" / "platforms" / preset.output_slug).resolve()
    if output_dir != expected_dir:
        raise ComicInstagramRenderError(f"Instagram output directory must be {expected_dir}")

    for path in resolved_frames:
        try:
            path.relative_to(render_job_root)
        except ValueError as exc:
            raise ComicInstagramRenderError(f"Comic frame escapes the current RenderJob: {path}") from exc
        if not path.is_file():
            raise ComicInstagramRenderError(f"Comic frame does not exist: {path}")
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.format != "PNG":
                    raise ComicInstagramRenderError(f"Comic frame is not PNG: {path}")
        except (OSError, ValueError) as exc:
            if isinstance(exc, ComicInstagramRenderError):
                raise
            raise ComicInstagramRenderError(f"Comic frame is unreadable: {path}") from exc

    fill = _normalize_color(background if background is not None else preset.background)
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.iterdir():
        if stale.is_file() and _OWNED_SLIDE_NAME.fullmatch(stale.name):
            stale.unlink()

    rendered: list[Path] = []
    try:
        for index, frame_path in enumerate(resolved_frames, start=1):
            output_path = output_dir / preset.filename(index)
            with Image.open(frame_path) as opened:
                source = opened.convert("RGBA")
                width, height, offset_x, offset_y = contain_geometry(
                    source.size, (preset.width, preset.height)
                )
                resized = source.resize((width, height), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (preset.width, preset.height), fill)
                canvas.alpha_composite(resized, (offset_x, offset_y))
                canvas.save(output_path, preset.output_format)
            if not output_path.is_file() or output_path.stat().st_size == 0:
                raise ComicInstagramRenderError(f"Instagram slide was not created: {output_path}")
            rendered.append(output_path)
        return rendered
    except Exception:
        for output_path in rendered:
            output_path.unlink(missing_ok=True)
        for candidate in output_dir.iterdir():
            if candidate.is_file() and _OWNED_SLIDE_NAME.fullmatch(candidate.name):
                candidate.unlink(missing_ok=True)
        raise

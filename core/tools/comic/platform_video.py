from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from PIL import Image

from core.domain import ProductionBrief, ProductionScene, ProductionSceneImageAnimation

from .platform_presets import ComicPlatformVideoPreset


_TIME_QUANTUM = Decimal("0.000001")
_MILLISECONDS_PER_SECOND = Decimal("1000")


class ComicPlatformVideoBriefError(ValueError):
    """Raised when a platform-specific comic video brief cannot be derived safely."""


@dataclass(frozen=True, slots=True)
class ComicSceneTiming:
    platform_duration_sec: Decimal
    clean_duration_sec: Decimal
    bubble_duration_sec: Decimal


def _seconds_from_ms(milliseconds: int) -> Decimal:
    return (Decimal(milliseconds) / _MILLISECONDS_PER_SECOND).quantize(_TIME_QUANTUM)


def calculate_comic_scene_timing(
    base_duration_sec: float,
    preset: ComicPlatformVideoPreset,
    *,
    is_last: bool,
) -> ComicSceneTiming:
    platform_duration = (
        Decimal(str(base_duration_sec)) * preset.scene_duration_multiplier
    ).quantize(_TIME_QUANTUM, rounding=ROUND_HALF_UP)
    clean_duration = _seconds_from_ms(preset.bubble_delay_ms)
    bubble_duration = platform_duration - clean_duration
    if bubble_duration <= 0:
        raise ComicPlatformVideoBriefError(
            f"Platform scene duration {platform_duration}s must exceed bubble delay "
            f"{clean_duration}s for {preset.platform.value}"
        )
    if not is_last and preset.transition_duration_sec >= bubble_duration:
        raise ComicPlatformVideoBriefError(
            f"Transition duration {preset.transition_duration_sec}s must be shorter than "
            f"bubble phase {bubble_duration}s for {preset.platform.value}"
        )
    if is_last:
        bubble_duration += _seconds_from_ms(preset.final_hold_ms)
    return ComicSceneTiming(
        platform_duration_sec=platform_duration,
        clean_duration_sec=clean_duration,
        bubble_duration_sec=bubble_duration.quantize(_TIME_QUANTUM),
    )


def calculate_brief_video_duration(brief: ProductionBrief) -> float:
    total = sum((Decimal(str(scene.duration_sec)) for scene in brief.scenes), Decimal("0"))
    overlaps = sum(
        (Decimal(str(scene.transition_duration)) for scene in brief.scenes[:-1]),
        Decimal("0"),
    )
    return float((total - overlaps).quantize(_TIME_QUANTUM, rounding=ROUND_HALF_UP))


def build_comic_platform_video_brief(
    brief: ProductionBrief,
    clean_source_paths: list[Path],
    comic_frame_paths: list[Path],
    preset: ComicPlatformVideoPreset,
    *,
    platform_output_dir: Path,
    render_job_root: Path,
) -> ProductionBrief:
    scene_count = len(brief.scenes)
    if len(clean_source_paths) != scene_count or len(comic_frame_paths) != scene_count:
        raise ComicPlatformVideoBriefError(
            "Clean source, comic frame, and production scene counts must match"
        )

    render_job_root = Path(render_job_root).resolve()
    platform_output_dir = Path(platform_output_dir).resolve()
    expected_output_dir = (
        render_job_root / "comic" / "platforms" / preset.output_slug
    ).resolve()
    if platform_output_dir != expected_output_dir:
        raise ComicPlatformVideoBriefError(
            f"Platform output directory must be {expected_output_dir}"
        )

    resolved_sources = [Path(path).resolve() for path in clean_source_paths]
    resolved_frames = [Path(path).resolve() for path in comic_frame_paths]
    for frame_path in resolved_frames:
        try:
            frame_path.relative_to(render_job_root)
        except ValueError as exc:
            raise ComicPlatformVideoBriefError(
                f"Comic frame escapes the current RenderJob: {frame_path}"
            ) from exc

    for source_path, frame_path in zip(resolved_sources, resolved_frames, strict=True):
        if not source_path.is_file() or not frame_path.is_file():
            raise ComicPlatformVideoBriefError(
                f"Comic source/frame pair is missing: {source_path}, {frame_path}"
            )
        with Image.open(source_path) as source, Image.open(frame_path) as frame:
            if source.size != frame.size:
                raise ComicPlatformVideoBriefError(
                    f"Comic source/frame sizes differ: {source.size} vs {frame.size}"
                )

    derived_scenes: list[ProductionScene] = []
    last_index = scene_count - 1
    for index, (scene, source_path, frame_path) in enumerate(
        zip(brief.scenes, resolved_sources, resolved_frames, strict=True)
    ):
        timing = calculate_comic_scene_timing(
            scene.duration_sec,
            preset,
            is_last=index == last_index,
        )
        clean_scene = scene.model_copy(deep=True)
        clean_scene.index = index * 2
        clean_scene.image_source = str(source_path)
        clean_scene.duration_sec = float(timing.clean_duration_sec)
        clean_scene.animation = ProductionSceneImageAnimation(
            type="static",
            from_scale=1.0,
            to_scale=1.0,
            easing="cubic-in-out",
        )
        clean_scene.transition_type = preset.transition_type
        clean_scene.transition_duration = 0.0

        bubble_scene = scene.model_copy(deep=True)
        bubble_scene.index = index * 2 + 1
        bubble_scene.image_source = str(frame_path)
        bubble_scene.duration_sec = float(timing.bubble_duration_sec)
        bubble_scene.animation = ProductionSceneImageAnimation(
            type=preset.animation_type,
            from_scale=float(preset.animation_from_scale),
            to_scale=float(preset.animation_to_scale),
            easing=preset.animation_easing,
        )
        bubble_scene.transition_type = preset.transition_type
        bubble_scene.transition_duration = (
            0.0 if index == last_index else float(preset.transition_duration_sec)
        )
        derived_scenes.extend((clean_scene, bubble_scene))

    derived = brief.model_copy(deep=True)
    derived.scenes = derived_scenes
    derived.subtitles.enabled = False
    derived.output.generate_srt = False
    derived.output.generate_cover = False
    derived.output.generate_audio_only = False
    derived.output.generate_comic_master_video = False
    return derived

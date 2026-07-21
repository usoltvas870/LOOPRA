from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from core.domain import PublishingPlatform


SUPPORTED_COMIC_CAMERA_EASINGS = frozenset({"cubic-in-out", "cubic-out"})
SUPPORTED_COMIC_TRANSITIONS = frozenset({"dissolve", "fade", "wipeleft"})


@dataclass(frozen=True, slots=True)
class ComicPlatformVideoPreset:
    platform: PublishingPlatform
    output_slug: str
    scene_duration_multiplier: Decimal
    bubble_delay_ms: int
    animation_type: str
    animation_from_scale: Decimal
    animation_to_scale: Decimal
    animation_easing: str
    transition_type: str
    transition_duration_sec: Decimal
    final_hold_ms: int

    def __post_init__(self) -> None:
        if self.scene_duration_multiplier <= 0:
            raise ValueError("Scene duration multiplier must be positive")
        if self.bubble_delay_ms <= 0 or self.final_hold_ms < 0:
            raise ValueError("Bubble delay must be positive and final hold must not be negative")
        if self.animation_easing not in SUPPORTED_COMIC_CAMERA_EASINGS:
            raise ValueError(f"Unsupported comic camera easing: {self.animation_easing}")
        if self.transition_type not in SUPPORTED_COMIC_TRANSITIONS:
            raise ValueError(f"Unsupported comic transition: {self.transition_type}")
        if self.transition_duration_sec < 0:
            raise ValueError("Transition duration must not be negative")


COMIC_PLATFORM_VIDEO_PRESETS: tuple[ComicPlatformVideoPreset, ...] = (
    ComicPlatformVideoPreset(
        platform=PublishingPlatform.TIKTOK,
        output_slug="tiktok",
        scene_duration_multiplier=Decimal("0.85"),
        bubble_delay_ms=250,
        animation_type="slow_zoom",
        animation_from_scale=Decimal("1.0"),
        animation_to_scale=Decimal("1.12"),
        animation_easing="cubic-out",
        transition_type="wipeleft",
        transition_duration_sec=Decimal("0.12"),
        final_hold_ms=1500,
    ),
    ComicPlatformVideoPreset(
        platform=PublishingPlatform.YOUTUBE_SHORTS,
        output_slug="youtube_shorts",
        scene_duration_multiplier=Decimal("1.15"),
        bubble_delay_ms=500,
        animation_type="slow_zoom",
        animation_from_scale=Decimal("1.0"),
        animation_to_scale=Decimal("1.06"),
        animation_easing="cubic-in-out",
        transition_type="dissolve",
        transition_duration_sec=Decimal("0.35"),
        final_hold_ms=3000,
    ),
    ComicPlatformVideoPreset(
        platform=PublishingPlatform.VK,
        output_slug="vk_clips",
        scene_duration_multiplier=Decimal("1.0"),
        bubble_delay_ms=350,
        animation_type="slow_zoom",
        animation_from_scale=Decimal("1.0"),
        animation_to_scale=Decimal("1.08"),
        animation_easing="cubic-in-out",
        transition_type="fade",
        transition_duration_sec=Decimal("0.22"),
        final_hold_ms=2200,
    ),
)

_PRESETS_BY_PLATFORM = {preset.platform: preset for preset in COMIC_PLATFORM_VIDEO_PRESETS}


def get_comic_platform_video_preset(
    platform: PublishingPlatform | str,
) -> ComicPlatformVideoPreset:
    try:
        platform_id = PublishingPlatform(platform)
        return _PRESETS_BY_PLATFORM[platform_id]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Unsupported comic video platform: {platform}") from exc


def resolve_comic_platform_video_presets(
    target_platforms: Iterable[PublishingPlatform],
) -> tuple[ComicPlatformVideoPreset, ...]:
    requested = set(target_platforms)
    return tuple(preset for preset in COMIC_PLATFORM_VIDEO_PRESETS if preset.platform in requested)

from __future__ import annotations

PLATFORM_SAFE_ZONES: dict[str, dict[str, int]] = {
    "tiktok": {"top": 130, "bottom": 240, "left": 60, "right": 60},
    "instagram": {"top": 120, "bottom": 200, "left": 60, "right": 60},
    "youtube_shorts": {"top": 120, "bottom": 200, "left": 60, "right": 60},
    "vk": {"top": 100, "bottom": 180, "left": 50, "right": 50},
}

ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
    "16:9": (1920, 1080),
}

MAX_DURATIONS: dict[str, float] = {
    "tiktok": 600.0,
    "instagram": 90.0,
    "youtube_shorts": 60.0,
    "vk": 300.0,
}


def resolve_safe_zone(platform: str) -> dict[str, int]:
    return PLATFORM_SAFE_ZONES.get(platform, PLATFORM_SAFE_ZONES["instagram"])

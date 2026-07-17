from __future__ import annotations

from .audio import mix_audio_with_ducking, normalize_audio
from .renderer import (
    build_video_filtergraph,
    generate_srt_from_brief,
    render_narrative_video,
)
from .safe_zones import (
    ASPECT_RATIOS,
    MAX_DURATIONS,
    PLATFORM_SAFE_ZONES,
    resolve_safe_zone,
)

__all__ = [
    "ASPECT_RATIOS",
    "MAX_DURATIONS",
    "PLATFORM_SAFE_ZONES",
    "build_video_filtergraph",
    "generate_srt_from_brief",
    "mix_audio_with_ducking",
    "normalize_audio",
    "render_narrative_video",
    "resolve_safe_zone",
]

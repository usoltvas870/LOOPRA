from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from PIL import Image
from pydantic import ValidationError

from core.domain import (
    ComicOverlay,
    ComicTailAnchor,
    ContentFormat,
    ProductionAudio,
    ProductionBrief,
    ProductionOutput,
    ProductionScene,
    ProductionSubtitles,
    PublishingPlatform,
)
from core.tools.comic import (
    COMIC_PLATFORM_VIDEO_PRESETS,
    ComicPlatformVideoBriefError,
    build_comic_platform_video_brief,
    calculate_brief_video_duration,
    get_comic_platform_video_preset,
    resolve_comic_platform_video_presets,
)


def _brief(scene_durations: tuple[float, ...] = (2.0, 2.0)) -> ProductionBrief:
    return ProductionBrief(
        workspace_id="internal",
        project_id="nura",
        production_brief_id="brief_platforms",
        scenario_id="scenario_platforms",
        content_format=ContentFormat.DIALOG_MINISERIES,
        target_platforms=[PublishingPlatform.TIKTOK],
        scenes=[
            ProductionScene(
                index=index,
                image_source=f"assets/source_{index}.png",
                duration_sec=duration,
                narration_text=f"Narration {index}",
                comic_overlay=ComicOverlay(
                    speaker=("nura", "woman", "shadow")[index % 3],
                    text=f"Bubble {index}",
                    position="top_left",
                    tail_anchor=ComicTailAnchor(x=0.8, y=0.8),
                ),
            )
            for index, duration in enumerate(scene_durations)
        ],
        audio=ProductionAudio(music_path="music.mp3", music_volume=0.2),
        subtitles=ProductionSubtitles(enabled=True, font_path="font.ttf"),
        output=ProductionOutput(
            resolution_width=270,
            resolution_height=480,
            fps=24,
            generate_comic_master_video=True,
        ),
    )


def _image_pairs(tmp_path: Path, count: int, *, mismatched: bool = False) -> tuple[list[Path], list[Path], Path]:
    render_root = tmp_path / "storage" / "nura" / "renders" / "job"
    comic_dir = render_root / "comic"
    comic_dir.mkdir(parents=True)
    source_dir = tmp_path / "project" / "assets"
    source_dir.mkdir(parents=True)
    sources: list[Path] = []
    frames: list[Path] = []
    for index in range(count):
        source = source_dir / f"source_{index}.png"
        frame = comic_dir / f"scene_{index + 1:02d}.png"
        Image.new("RGB", (270, 480), "blue").save(source)
        frame_size = (271, 480) if mismatched and index == 0 else (270, 480)
        Image.new("RGB", frame_size, "white").save(frame)
        sources.append(source)
        frames.append(frame)
    return sources, frames, render_root


def test_presets_are_exactly_three_immutable_and_platform_specific() -> None:
    assert [preset.platform for preset in COMIC_PLATFORM_VIDEO_PRESETS] == [
        PublishingPlatform.TIKTOK,
        PublishingPlatform.YOUTUBE_SHORTS,
        PublishingPlatform.VK,
    ]
    assert len({preset.scene_duration_multiplier for preset in COMIC_PLATFORM_VIDEO_PRESETS}) == 3
    assert len({preset.bubble_delay_ms for preset in COMIC_PLATFORM_VIDEO_PRESETS}) == 3
    assert len({preset.final_hold_ms for preset in COMIC_PLATFORM_VIDEO_PRESETS}) == 3
    assert len({preset.animation_to_scale for preset in COMIC_PLATFORM_VIDEO_PRESETS}) == 3
    assert len({preset.transition_type for preset in COMIC_PLATFORM_VIDEO_PRESETS}) == 3
    with pytest.raises(FrozenInstanceError):
        COMIC_PLATFORM_VIDEO_PRESETS[0].bubble_delay_ms = 999  # type: ignore[misc]


def test_target_resolution_is_canonical_deduplicated_and_ignores_non_comic_targets() -> None:
    resolved = resolve_comic_platform_video_presets(
        [
            PublishingPlatform.VK,
            PublishingPlatform.TIKTOK,
            PublishingPlatform.VK,
            PublishingPlatform.INSTAGRAM,
            PublishingPlatform.YOUTUBE_SHORTS,
        ]
    )
    assert [preset.platform for preset in resolved] == [
        PublishingPlatform.TIKTOK,
        PublishingPlatform.YOUTUBE_SHORTS,
        PublishingPlatform.VK,
    ]
    assert resolve_comic_platform_video_presets([]) == ()


def test_unknown_preset_and_unknown_serialized_platform_are_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported comic video platform"):
        get_comic_platform_video_preset(PublishingPlatform.INSTAGRAM)
    with pytest.raises(ValidationError):
        ProductionBrief.model_validate({**_brief().model_dump(), "target_platforms": ["unknown"]})


@pytest.mark.parametrize("platform", [PublishingPlatform.TIKTOK, PublishingPlatform.YOUTUBE_SHORTS, PublishingPlatform.VK])
def test_derived_platform_brief_uses_hard_reveal_timing_without_mutation(
    tmp_path: Path,
    platform: PublishingPlatform,
) -> None:
    brief = _brief()
    original = brief.model_dump(mode="json")
    sources, frames, render_root = _image_pairs(tmp_path, len(brief.scenes))
    preset = get_comic_platform_video_preset(platform)
    output_dir = render_root / "comic" / "platforms" / preset.output_slug

    derived = build_comic_platform_video_brief(
        brief,
        sources,
        frames,
        preset,
        platform_output_dir=output_dir,
        render_job_root=render_root,
    )

    assert brief.model_dump(mode="json") == original
    assert len(derived.scenes) == len(brief.scenes) * 2
    assert [scene.index for scene in derived.scenes] == list(range(len(derived.scenes)))
    assert [Path(scene.image_source) for scene in derived.scenes[::2]] == [path.resolve() for path in sources]
    assert [Path(scene.image_source) for scene in derived.scenes[1::2]] == [path.resolve() for path in frames]
    assert all(scene.transition_duration == 0 for scene in derived.scenes[::2])
    assert derived.scenes[1].transition_type == preset.transition_type
    assert derived.scenes[1].transition_duration == float(preset.transition_duration_sec)
    assert derived.scenes[-1].transition_duration == 0
    assert derived.scenes[0].animation.from_scale == derived.scenes[0].animation.to_scale == 1.0
    assert derived.scenes[1].animation.to_scale == float(preset.animation_to_scale)
    assert derived.audio == brief.audio
    assert derived.output.resolution_width == brief.output.resolution_width
    assert derived.output.resolution_height == brief.output.resolution_height
    assert derived.output.fps == brief.output.fps
    assert derived.subtitles.enabled is False
    assert derived.output.generate_cover is False
    assert derived.output.generate_audio_only is False
    assert derived.output.generate_comic_master_video is False
    expected = (
        sum(float(preset.scene_duration_multiplier) * scene.duration_sec for scene in brief.scenes)
        + preset.final_hold_ms / 1000
        - float(preset.transition_duration_sec) * (len(brief.scenes) - 1)
    )
    assert calculate_brief_video_duration(derived) == pytest.approx(expected)


def test_derived_brief_rejects_frame_count_size_short_timing_and_path_escape(tmp_path: Path) -> None:
    brief = _brief()
    sources, frames, render_root = _image_pairs(tmp_path, 2)
    preset = get_comic_platform_video_preset(PublishingPlatform.YOUTUBE_SHORTS)
    output_dir = render_root / "comic" / "platforms" / preset.output_slug

    with pytest.raises(ComicPlatformVideoBriefError, match="counts must match"):
        build_comic_platform_video_brief(
            brief, sources, frames[:1], preset,
            platform_output_dir=output_dir, render_job_root=render_root,
        )

    _, bad_frames, bad_root = _image_pairs(tmp_path / "bad-size", 2, mismatched=True)
    with pytest.raises(ComicPlatformVideoBriefError, match="sizes differ"):
        build_comic_platform_video_brief(
            brief, sources, bad_frames, preset,
            platform_output_dir=bad_root / "comic" / "platforms" / preset.output_slug,
            render_job_root=bad_root,
        )

    short_brief = _brief((0.4,))
    short_sources, short_frames, short_root = _image_pairs(tmp_path / "short", 1)
    with pytest.raises(ComicPlatformVideoBriefError, match="must exceed bubble delay"):
        build_comic_platform_video_brief(
            short_brief, short_sources, short_frames, preset,
            platform_output_dir=short_root / "comic" / "platforms" / preset.output_slug,
            render_job_root=short_root,
        )

    escaped_frame = tmp_path / "escaped.png"
    Image.new("RGB", (270, 480), "white").save(escaped_frame)
    with pytest.raises(ComicPlatformVideoBriefError, match="escapes the current RenderJob"):
        build_comic_platform_video_brief(
            brief, sources, [escaped_frame, frames[1]], preset,
            platform_output_dir=output_dir, render_job_root=render_root,
        )

    with pytest.raises(ComicPlatformVideoBriefError, match="Platform output directory"):
        build_comic_platform_video_brief(
            brief, sources, frames, preset,
            platform_output_dir=tmp_path / "outside", render_job_root=render_root,
        )

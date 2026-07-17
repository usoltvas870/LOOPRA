from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import (
    ContentFormat,
    ProductionBrief,
    ProductionOutput,
    ProductionScene,
    ProductionSubtitles,
)


def _make_brief(scenes: list[ProductionScene]) -> ProductionBrief:
    return ProductionBrief(
        workspace_id="test",
        project_id="test",
        production_brief_id="brief_test",
        scenario_id="scenario_test",
        content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
        scenes=scenes,
        output=ProductionOutput(resolution_width=1080, resolution_height=1920, fps=24),
        subtitles=ProductionSubtitles(enabled=True, mode="manual", font_size=50),
    )


class GenerateSrtFromBriefTests(unittest.TestCase):
    def test_single_scene_with_narration(self) -> None:
        from core.tools.video.renderer import generate_srt_from_brief

        brief = _make_brief(
            [
                ProductionScene(
                    index=0,
                    image_source="scene0.png",
                    duration_sec=3.0,
                    narration_text="Hello world",
                ),
            ]
        )
        srt = generate_srt_from_brief(brief)
        self.assertIn("Hello world", srt)
        self.assertIn("-->", srt)

    def test_multiple_scenes(self) -> None:
        from core.tools.video.renderer import generate_srt_from_brief

        brief = _make_brief(
            [
                ProductionScene(index=0, image_source="a.png", duration_sec=2.0, narration_text="First"),
                ProductionScene(index=1, image_source="b.png", duration_sec=3.0, narration_text="Second"),
            ]
        )
        srt = generate_srt_from_brief(brief)
        self.assertIn("First", srt)
        self.assertIn("Second", srt)
        lines = srt.strip().split("\n")
        self.assertGreater(len(lines), 4)

    def test_scene_without_narration(self) -> None:
        from core.tools.video.renderer import generate_srt_from_brief

        brief = _make_brief(
            [
                ProductionScene(index=0, image_source="a.png", duration_sec=2.0, narration_text=""),
                ProductionScene(index=1, image_source="b.png", duration_sec=3.0, narration_text="Has text"),
            ]
        )
        srt = generate_srt_from_brief(brief)
        self.assertNotIn("a.png", srt)
        self.assertIn("Has text", srt)

    def test_empty_scenes(self) -> None:
        from core.tools.video.renderer import generate_srt_from_brief

        brief = _make_brief([])
        srt = generate_srt_from_brief(brief)
        self.assertEqual(srt.strip(), "")

    def test_srt_timecodes_increasing(self) -> None:
        from core.tools.video.renderer import generate_srt_from_brief

        brief = _make_brief(
            [
                ProductionScene(index=0, image_source="a.png", duration_sec=3.0, narration_text="A"),
                ProductionScene(index=1, image_source="b.png", duration_sec=4.0, narration_text="B"),
                ProductionScene(index=2, image_source="c.png", duration_sec=2.0, narration_text="C"),
            ]
        )
        srt = generate_srt_from_brief(brief)
        self.assertIn("A", srt)
        self.assertIn("B", srt)
        self.assertIn("C", srt)


class BuildVideoFiltergraphTests(unittest.TestCase):
    def test_single_scene_filtergraph(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief(
            [
                ProductionScene(index=0, image_source="a.png", duration_sec=3.0),
            ]
        )
        filter_graph, video_label = build_video_filtergraph(brief, (1080, 1920), 24)
        self.assertIn("fps=fps=24", filter_graph)
        self.assertIn("scale", filter_graph)
        self.assertIn("pad", filter_graph)
        self.assertIn("zoompan", filter_graph)
        self.assertIn("s0", video_label)

    def test_two_scenes_with_transition(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief(
            [
                ProductionScene(index=0, image_source="a.png", duration_sec=3.0),
                ProductionScene(index=1, image_source="b.png", duration_sec=3.0, transition_duration=0.5),
            ]
        )
        filter_graph, video_label = build_video_filtergraph(brief, (1080, 1920), 24)
        self.assertIn("xfade", filter_graph)
        self.assertIn("s_xfade_", video_label)

    def test_no_zoom_when_scales_equal(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief(
            [
                ProductionScene(
                    index=0,
                    image_source="a.png",
                    duration_sec=3.0,
                ),
            ]
        )
        brief.scenes[0].animation.from_scale = 1.0
        brief.scenes[0].animation.to_scale = 1.0

        filter_graph, _ = build_video_filtergraph(brief, (1080, 1920), 24)
        self.assertIn("trim", filter_graph)

    def test_empty_scenes_raises(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief([])
        with self.assertRaises(ValueError):
            build_video_filtergraph(brief, (1080, 1920), 24)

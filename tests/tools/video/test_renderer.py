from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_ass_uses_explicit_font_family_and_preserves_cyrillic_text(self) -> None:
        from core.tools.video.renderer import _generate_ass_from_brief, _resolve_subtitle_font

        font_path = Path("C:/Windows/Fonts/arial.ttf")
        if not font_path.exists():
            self.skipTest("Arial is not available for the Windows font test")

        text = 'Ещё — «многострочный»\nтекст'
        brief = _make_brief(
            [ProductionScene(index=0, image_source="a.png", duration_sec=3.0, narration_text=text)]
        )
        brief.subtitles.font_path = str(font_path)

        family, font_dir = _resolve_subtitle_font(brief, Path("."))
        ass = _generate_ass_from_brief(brief, 1080, 1920, family)

        self.assertIn(f"Style: Default,{family},", ass)
        self.assertIn(text, ass)
        self.assertEqual(font_dir, font_path.parent)

    def test_explicit_missing_font_raises_clear_error(self) -> None:
        from core.tools.video.renderer import _resolve_subtitle_font

        brief = _make_brief([])
        brief.subtitles.font_path = "missing-font.ttf"

        with self.assertRaisesRegex(FileNotFoundError, "Subtitle font not found"):
            _resolve_subtitle_font(brief, Path("."))


class AssSubtitleBurnTests(unittest.TestCase):
    def test_odd_output_resolution_fails_before_ffmpeg_invocation(self) -> None:
        from core.tools.video.renderer import render_narrative_video

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            brief = _make_brief([ProductionScene(index=0, image_source="scene.png", duration_sec=1.0)])
            brief.output.resolution_width = 941

            with patch("core.tools.video.renderer.subprocess.run") as run:
                with self.assertRaisesRegex(ValueError, "must be even"):
                    render_narrative_video(brief, root / "output", root)

            run.assert_not_called()

    def test_ass_filter_includes_font_directory(self) -> None:
        from core.tools.video.renderer import _ass_filter

        filter_value = _ass_filter(Path("C:/temp/subtitles.ass"), Path("C:/fonts"))

        self.assertIn("fontsdir='C\\:/fonts'", filter_value)
        self.assertIn("filename='C\\:/temp/subtitles.ass'", filter_value)

    def test_success_replaces_final_video_only_after_temporary_output_exists(self) -> None:
        from core.tools.video.renderer import _burn_ass_subtitles

        with tempfile.TemporaryDirectory() as temp_dir:
            output_video = Path(temp_dir) / "final_video.mp4"
            ass_path = Path(temp_dir) / "subtitles.ass"
            output_video.write_bytes(b"original")
            ass_path.write_text("[Script Info]\n", encoding="utf-8")
            temporary_video = Path(temp_dir) / "final_video.subtitles.tmp.mp4"

            def successful_run(command, **_kwargs):
                self.assertEqual(output_video.read_bytes(), b"original")
                self.assertEqual(Path(command[-1]), temporary_video)
                temporary_video.write_bytes(b"subtitled")
                return SimpleNamespace(returncode=0, stderr="")

            with patch("core.tools.video.renderer.subprocess.run", side_effect=successful_run):
                _burn_ass_subtitles("ffmpeg", output_video, ass_path, Path(temp_dir), 0)

            self.assertEqual(output_video.read_bytes(), b"subtitled")
            self.assertFalse(temporary_video.exists())

    def test_failure_preserves_final_video_and_removes_temporary_output(self) -> None:
        from core.tools.video.renderer import _burn_ass_subtitles

        with tempfile.TemporaryDirectory() as temp_dir:
            output_video = Path(temp_dir) / "final_video.mp4"
            ass_path = Path(temp_dir) / "subtitles.ass"
            temporary_video = Path(temp_dir) / "final_video.subtitles.tmp.mp4"
            output_video.write_bytes(b"original")
            ass_path.write_text("[Script Info]\n", encoding="utf-8")

            def failed_run(command, **_kwargs):
                Path(command[-1]).write_bytes(b"partial")
                return SimpleNamespace(returncode=1, stderr="burn failed")

            with patch("core.tools.video.renderer.subprocess.run", side_effect=failed_run):
                with self.assertRaisesRegex(RuntimeError, "Subtitle burn failed"):
                    _burn_ass_subtitles("ffmpeg", output_video, ass_path, Path(temp_dir), 0)

            self.assertEqual(output_video.read_bytes(), b"original")
            self.assertFalse(temporary_video.exists())

    def test_disabled_subtitles_do_not_create_subtitle_artifacts_or_second_pass(self) -> None:
        from core.tools.video.renderer import render_narrative_video

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            image_path = root / "scene.png"
            image_path.write_bytes(b"placeholder")
            brief = _make_brief([ProductionScene(index=0, image_source="scene.png", duration_sec=1.0)])
            brief.subtitles.enabled = False
            brief.output.generate_cover = False
            brief.output.generate_audio_only = False

            def render_main_video(command, **_kwargs):
                Path(command[-1]).write_bytes(b"video")
                return SimpleNamespace(returncode=0, stderr="")

            with patch("core.tools.video.renderer.subprocess.run", side_effect=render_main_video) as run:
                result = render_narrative_video(brief, root / "output", root)

            self.assertEqual(set(result), {"final_video"})
            self.assertEqual(run.call_count, 1)
            self.assertFalse((root / "output" / "subtitles.srt").exists())
            self.assertFalse((root / "output" / "subtitles.ass").exists())


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
        self.assertIn(":d=72:", filter_graph)
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

    def test_transition_uses_outgoing_scene_contract(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief(
            [
                ProductionScene(
                    index=0,
                    image_source="a.png",
                    duration_sec=3.0,
                    transition_type="wipeleft",
                    transition_duration=0.12,
                ),
                ProductionScene(
                    index=1,
                    image_source="b.png",
                    duration_sec=3.0,
                    transition_type="dissolve",
                    transition_duration=0.5,
                ),
            ]
        )
        filter_graph, _ = build_video_filtergraph(brief, (1080, 1920), 24)
        self.assertIn("transition=wipeleft:duration=0.12", filter_graph)

    def test_zero_duration_transition_uses_concat(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief(
            [
                ProductionScene(index=0, image_source="a.png", duration_sec=1.0, transition_duration=0.0),
                ProductionScene(index=1, image_source="b.png", duration_sec=1.0, transition_duration=0.0),
            ]
        )

        filter_graph, _ = build_video_filtergraph(brief, (1080, 1920), 24)
        self.assertIn("concat=n=2:v=1:a=0", filter_graph)
        self.assertNotIn("xfade=transition=dissolve:duration=0.0", filter_graph)

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
        self.assertNotIn("zoompan", filter_graph)

    def test_empty_scenes_raises(self) -> None:
        from core.tools.video.renderer import build_video_filtergraph

        brief = _make_brief([])
        with self.assertRaises(ValueError):
            build_video_filtergraph(brief, (1080, 1920), 24)

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.domain import (
    ContentFormat,
    ProductionBrief,
    ProductionAudio,
    ProductionOutput,
    ProductionQA,
    ProductionScene,
    ProductionSubtitles,
)
from core.tools.validators import (
    AssetReport,
    validate_audio,
    validate_font,
    validate_image,
    validate_production_assets,
)


class ValidateImageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_valid_png(self) -> None:
        from PIL import Image

        img_path = Path(self.temp_dir.name) / "test.png"
        im = Image.new("RGB", (1080, 1920), color=(128, 128, 128))
        im.save(img_path, "PNG")
        result = validate_image(img_path)
        self.assertFalse(result["corrupt"])
        self.assertEqual(result["width"], 1080)
        self.assertEqual(result["height"], 1920)
        self.assertIn("png", result["format"])
        self.assertGreater(result["file_size"], 0)

    def test_missing_file(self) -> None:
        result = validate_image(Path("/nonexistent/image.png"))
        self.assertTrue(result["corrupt"])
        self.assertIn("not found", result.get("error", ""))

    def test_empty_file(self) -> None:
        img_path = Path(self.temp_dir.name) / "empty.png"
        img_path.write_bytes(b"")
        result = validate_image(img_path)
        self.assertTrue(result["corrupt"])
        self.assertIn("empty", result.get("error", ""))

    def test_corrupt_image(self) -> None:
        img_path = Path(self.temp_dir.name) / "corrupt.png"
        img_path.write_bytes(b"not an image at all")
        result = validate_image(img_path)
        self.assertTrue(result["corrupt"])


class ValidateAudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_file(self) -> None:
        result = validate_audio(Path("/nonexistent/audio.wav"))
        self.assertTrue(result["corrupt"])

    def test_empty_file(self) -> None:
        audio_path = Path(self.temp_dir.name) / "empty.wav"
        audio_path.write_bytes(b"")
        result = validate_audio(audio_path)
        self.assertTrue(result["corrupt"])


class ValidateFontTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_file(self) -> None:
        result = validate_font(Path("/nonexistent/font.ttf"))
        self.assertTrue(result["corrupt"])
        self.assertFalse(result["exists"])

    def test_empty_file(self) -> None:
        font_path = Path(self.temp_dir.name) / "empty.ttf"
        font_path.write_bytes(b"")
        result = validate_font(font_path)
        self.assertTrue(result["corrupt"])

    def test_valid_ttf_extension(self) -> None:
        font_path = Path(self.temp_dir.name) / "test.ttf"
        font_path.write_bytes(b"font data here")
        result = validate_font(font_path)
        self.assertFalse(result["corrupt"])
        self.assertTrue(result["exists"])
        self.assertEqual(result["format"], "ttf")

    def test_valid_otf_extension(self) -> None:
        font_path = Path(self.temp_dir.name) / "test.otf"
        font_path.write_bytes(b"font data here")
        result = validate_font(font_path)
        self.assertFalse(result["corrupt"])
        self.assertEqual(result["format"], "otf")


class ValidateProductionAssetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_all_assets_present(self) -> None:
        from PIL import Image

        assets_dir = self.project_root / "assets"
        assets_dir.mkdir(parents=True)

        for i in range(3):
            img_path = assets_dir / f"scene_{i:02d}.png"
            im = Image.new("RGB", (1080, 1920), color=(100 + i * 50, 100, 100))
            im.save(img_path, "PNG")

        brief = ProductionBrief(
            production_brief_id="brief_test_assets",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            scenes=[
                ProductionScene(index=0, purpose="hook", image_source="assets/scene_00.png", duration_sec=3.0),
                ProductionScene(index=1, purpose="main", image_source="assets/scene_01.png", duration_sec=5.0),
                ProductionScene(index=2, purpose="cta", image_source="assets/scene_02.png", duration_sec=3.0),
            ],
            output=ProductionOutput(resolution_width=1080, resolution_height=1920),
        )

        report = validate_production_assets(brief, self.project_root)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.missing_files), 0)
        self.assertEqual(len(report.corrupt_files), 0)

    def test_missing_image(self) -> None:
        brief = ProductionBrief(
            production_brief_id="brief_missing",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            scenes=[
                ProductionScene(index=0, purpose="hook", image_source="assets/missing.png", duration_sec=3.0),
            ],
        )

        report = validate_production_assets(brief, self.project_root)
        self.assertFalse(report.passed)
        self.assertGreater(len(report.missing_files), 0)

    def test_wrong_resolution(self) -> None:
        from PIL import Image

        assets_dir = self.project_root / "assets"
        assets_dir.mkdir(parents=True)

        img_path = assets_dir / "small.png"
        im = Image.new("RGB", (100, 100), color=(128, 128, 128))
        im.save(img_path, "PNG")

        brief = ProductionBrief(
            production_brief_id="brief_res",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            scenes=[
                ProductionScene(index=0, purpose="hook", image_source="assets/small.png", duration_sec=3.0),
            ],
            output=ProductionOutput(resolution_width=1080, resolution_height=1920),
        )

        report = validate_production_assets(brief, self.project_root)
        self.assertGreater(len(report.wrong_resolution), 0)

    def test_missing_audio(self) -> None:
        brief = ProductionBrief(
            production_brief_id="brief_audio",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            audio=ProductionAudio(
                voiceover_path="assets/missing_vo.wav",
                music_path="assets/missing_bg.mp3",
            ),
        )

        report = validate_production_assets(brief, self.project_root)
        self.assertFalse(report.passed)
        self.assertGreater(len(report.missing_files), 0)

    def test_missing_font(self) -> None:
        brief = ProductionBrief(
            production_brief_id="brief_font",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
            content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
            subtitles=ProductionSubtitles(
                font_path="assets/missing_font.ttf",
            ),
        )

        report = validate_production_assets(brief, self.project_root)
        self.assertFalse(report.passed)
        self.assertGreater(len(report.missing_files), 0)

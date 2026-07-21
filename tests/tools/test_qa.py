from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.tools.qa import (
    QAResult,
    check_carousel_output,
    check_comic_output,
    check_platform_video_package,
    check_video_output,
    format_qa_result,
)


class CheckVideoOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_video(self) -> None:
        result = check_video_output(Path("/nonexistent/video.mp4"))
        self.assertFalse(result.passed)
        self.assertGreater(len(result.errors), 0)

    def test_empty_video(self) -> None:
        video_path = Path(self.temp_dir.name) / "empty.mp4"
        video_path.write_bytes(b"")
        result = check_video_output(video_path)
        self.assertFalse(result.passed)
        self.assertIn("empty", result.errors[0].lower() if result.errors else "")


class CheckCarouselOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_directory(self) -> None:
        result = check_carousel_output(Path("/nonexistent/carousel"))
        self.assertFalse(result.passed)
        self.assertGreater(len(result.errors), 0)

    def test_empty_directory(self) -> None:
        carousel_dir = Path(self.temp_dir.name) / "empty_carousel"
        carousel_dir.mkdir()
        result = check_carousel_output(carousel_dir)
        self.assertFalse(result.passed)
        self.assertIn("No PNG", result.errors[0] if result.errors else "")

    def test_valid_png_files(self) -> None:
        from PIL import Image

        carousel_dir = Path(self.temp_dir.name) / "carousel"
        carousel_dir.mkdir()

        for i in range(1, 4):
            slide_path = carousel_dir / f"slide_{i:02d}.png"
            im = Image.new("RGB", (1080, 1350), color=(100 + i * 30, 100, 100))
            im.save(slide_path, "PNG")

        result = check_carousel_output(carousel_dir)
        self.assertTrue(result.passed)
        self.assertEqual(result.subtitle_count, 3)

    def test_empty_png(self) -> None:
        carousel_dir = Path(self.temp_dir.name) / "carousel"
        carousel_dir.mkdir()

        empty_path = carousel_dir / "empty.png"
        empty_path.write_bytes(b"")

        result = check_carousel_output(carousel_dir)
        self.assertFalse(result.passed)


class CheckComicOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_validates_exact_order_and_sizes(self) -> None:
        from PIL import Image

        comic_dir = Path(self.temp_dir.name) / "comic"
        comic_dir.mkdir()
        Image.new("RGB", (480, 800), "blue").save(comic_dir / "scene_01.png", "PNG")
        Image.new("RGB", (600, 900), "green").save(comic_dir / "scene_02.png", "PNG")
        result = check_comic_output(comic_dir, expected_count=2, expected_sizes=[(480, 800), (600, 900)])
        self.assertTrue(result.passed)

    def test_rejects_missing_or_corrupt_frame(self) -> None:
        comic_dir = Path(self.temp_dir.name) / "comic"
        comic_dir.mkdir()
        (comic_dir / "scene_01.png").write_bytes(b"")
        result = check_comic_output(comic_dir, expected_count=1, expected_sizes=[(480, 800)])
        self.assertFalse(result.passed)


class CheckPlatformVideoPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.platforms_dir = Path(self.temp_dir.name) / "platforms"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_accepts_exact_requested_platform_set(self) -> None:
        expected = {}
        for slug in ("tiktok", "youtube_shorts", "vk_clips"):
            path = self.platforms_dir / slug / "final_video.mp4"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"video")
            expected[slug] = path
        result = check_platform_video_package(self.platforms_dir, expected_paths=expected)
        self.assertTrue(result.passed)

    def test_rejects_unrequested_directory_and_temporary_mp4(self) -> None:
        final_path = self.platforms_dir / "tiktok" / "final_video.mp4"
        final_path.parent.mkdir(parents=True)
        final_path.write_bytes(b"video")
        unexpected = self.platforms_dir / "vk_clips" / "final_video.tmp.mp4"
        unexpected.parent.mkdir(parents=True)
        unexpected.write_bytes(b"partial")
        result = check_platform_video_package(
            self.platforms_dir,
            expected_paths={"tiktok": final_path},
        )
        self.assertFalse(result.passed)
        self.assertGreaterEqual(len(result.errors), 2)

    def test_rejects_extra_non_temporary_mp4(self) -> None:
        final_path = self.platforms_dir / "tiktok" / "final_video.mp4"
        final_path.parent.mkdir(parents=True)
        final_path.write_bytes(b"video")
        (final_path.parent / "extra.mp4").write_bytes(b"extra")
        result = check_platform_video_package(
            self.platforms_dir,
            expected_paths={"tiktok": final_path},
        )
        self.assertFalse(result.passed)
        self.assertIn("MP4 set", result.errors[0])


class FormatQAResultTests(unittest.TestCase):
    def test_format_passed_result(self) -> None:
        result = QAResult(
            passed=True,
            video_playable=True,
            has_audio=True,
            duration_sec=15.5,
            resolution="1920x1080",
            bitrate_kbps=2000,
            subtitle_count=2,
        )
        formatted = format_qa_result(result, "Test Video")
        self.assertIn("PASSED", formatted)
        self.assertIn("15.5s", formatted)
        self.assertIn("1920x1080", formatted)

    def test_format_failed_result(self) -> None:
        result = QAResult(
            passed=False,
            errors=["Video file not found"],
        )
        formatted = format_qa_result(result, "Bad Video")
        self.assertIn("FAILED", formatted)
        self.assertIn("Video file not found", formatted)

    def test_format_with_warnings(self) -> None:
        result = QAResult(
            passed=True,
            warnings=["No audio stream"],
            video_playable=True,
            duration_sec=10.0,
        )
        formatted = format_qa_result(result)
        self.assertIn("No audio stream", formatted)

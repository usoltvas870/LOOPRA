from __future__ import annotations

import hashlib
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from core.domain import PublishingPlatform
from core.tools.comic import (
    INSTAGRAM_COMIC_PRESET,
    ComicInstagramRenderError,
    contain_geometry,
    render_comic_instagram_carousel,
)
from core.tools.qa import check_comic_instagram_output


class ComicInstagramPresetTests(unittest.TestCase):
    def test_contract_is_immutable_and_centralized(self) -> None:
        preset = INSTAGRAM_COMIC_PRESET
        self.assertEqual(preset.platform, PublishingPlatform.INSTAGRAM)
        self.assertEqual(preset.output_slug, "instagram")
        self.assertEqual((preset.width, preset.height), (1080, 1350))
        self.assertEqual(preset.aspect_ratio, "4:5")
        self.assertEqual(preset.fit_strategy, "contain")
        self.assertFalse(preset.crop_allowed)
        self.assertFalse(preset.stretch_allowed)
        self.assertEqual([preset.filename(index) for index in range(1, 4)], ["01.png", "02.png", "03.png"])
        with self.assertRaises(FrozenInstanceError):
            preset.width = 1  # type: ignore[misc]


class ComicInstagramRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.job_root = Path(self.temp.name) / "storage" / "nura" / "renders" / "job"
        self.comic_root = self.job_root / "comic"
        self.output_dir = self.comic_root / "platforms" / "instagram"
        self.comic_root.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _frame(self, number: int, color: str = "blue") -> Path:
        path = self.comic_root / f"scene_{number:02d}.png"
        image = Image.new("RGB", (270, 480), color)
        pixels = image.load()
        for point, marker in (
            ((0, 0), (255, 0, 0)),
            ((269, 0), (0, 255, 0)),
            ((0, 479), (0, 0, 255)),
            ((269, 479), (255, 255, 0)),
        ):
            pixels[point] = marker
        image.save(path, "PNG")
        return path

    def test_renders_ordered_contained_slides_without_mutating_sources_or_inputs(self) -> None:
        frames = [self._frame(1, "blue"), self._frame(2, "green")]
        original_list = list(frames)
        hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in frames]

        outputs = render_comic_instagram_carousel(
            frames, self.output_dir, render_job_root=self.job_root, background="#112233"
        )

        self.assertEqual(frames, original_list)
        self.assertEqual([path.name for path in outputs], ["01.png", "02.png"])
        self.assertEqual(hashes, [hashlib.sha256(path.read_bytes()).hexdigest() for path in frames])
        self.assertTrue(all(hashlib.sha256(path.read_bytes()).hexdigest() not in hashes for path in outputs))
        for path in outputs:
            with Image.open(path) as image:
                self.assertEqual(image.size, (1080, 1350))
        self.assertEqual(contain_geometry((270, 480), (1080, 1350)), (759, 1350, 160, 0))
        qa = check_comic_instagram_output(
            self.output_dir,
            source_frames=frames,
            expected_size=(1080, 1350),
            render_job_root=self.job_root,
        )
        self.assertTrue(qa.passed, qa.errors)

    def test_cleans_only_owned_stale_slides_and_preserves_foreign_file(self) -> None:
        frame = self._frame(1)
        self.output_dir.mkdir(parents=True)
        (self.output_dir / "99.png").write_bytes(b"stale")
        (self.output_dir / "notes.txt").write_text("keep", encoding="utf-8")
        outputs = render_comic_instagram_carousel([frame], self.output_dir, render_job_root=self.job_root)
        self.assertEqual([path.name for path in outputs], ["01.png"])
        self.assertFalse((self.output_dir / "99.png").exists())
        self.assertTrue((self.output_dir / "notes.txt").is_file())

    def test_rejects_empty_duplicate_corrupt_missing_and_foreign_frames(self) -> None:
        frame = self._frame(1)
        cases = (
            ([], "at least one"),
            ([frame, frame], "unique"),
            ([self.comic_root / "missing.png"], "does not exist"),
        )
        for frames, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ComicInstagramRenderError, message):
                render_comic_instagram_carousel(frames, self.output_dir, render_job_root=self.job_root)
        corrupt = self.comic_root / "scene_02.png"
        corrupt.write_bytes(b"not-png")
        with self.assertRaisesRegex(ComicInstagramRenderError, "unreadable"):
            render_comic_instagram_carousel([corrupt], self.output_dir, render_job_root=self.job_root)
        foreign = Path(self.temp.name) / "foreign.png"
        Image.new("RGB", (10, 10)).save(foreign, "PNG")
        with self.assertRaisesRegex(ComicInstagramRenderError, "escapes"):
            render_comic_instagram_carousel([foreign], self.output_dir, render_job_root=self.job_root)

    def test_rejects_wrong_output_directory(self) -> None:
        with self.assertRaisesRegex(ComicInstagramRenderError, "output directory"):
            render_comic_instagram_carousel(
                [self._frame(1)], self.comic_root / "instagram", render_job_root=self.job_root
            )

    def test_middle_render_failure_removes_partial_batch(self) -> None:
        frames = [self._frame(1), self._frame(2)]
        original_save = Image.Image.save
        calls = 0

        def fail_second(image, fp, format=None, **params):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated save failure")
            return original_save(image, fp, format, **params)

        with patch.object(Image.Image, "save", autospec=True, side_effect=fail_second):
            with self.assertRaises(OSError):
                render_comic_instagram_carousel(frames, self.output_dir, render_job_root=self.job_root)
        self.assertEqual(list(self.output_dir.glob("[0-9]*.png")), [])

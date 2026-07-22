from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from core.domain import (
    ComicOverlay,
    ComicTailAnchor,
    ContentFormat,
    ProductionBrief,
    ProductionScene,
    ProductionSubtitles,
    PublishingPlatform,
    RenderJob,
    RenderJobStatus,
)
from core.tools.comic import build_comic_handoff_package, verify_comic_handoff_package


class ComicHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.comic = self.root / "comic"
        (self.comic / "platforms" / "instagram").mkdir(parents=True)
        Image.new("RGB", (1080, 1350), "black").save(
            self.comic / "platforms" / "instagram" / "01.png", "PNG"
        )
        (self.comic / "manifest.json").write_text("{}", encoding="utf-8")
        self.source_manifest = self.root / "episode.json"
        self.source_manifest.write_text("{}", encoding="utf-8")
        self.brief = ProductionBrief(
            workspace_id="internal", project_id="project", production_brief_id="episode_1",
            scenario_id="scenario_1", title="Test episode", content_format=ContentFormat.DIALOG_MINISERIES,
            target_platforms=[PublishingPlatform.INSTAGRAM],
            scenes=[ProductionScene(index=0, image_source="source.png", duration_sec=1, comic_overlay=ComicOverlay(
                speaker="nura", text="Тест", position="top_left", tail_anchor=ComicTailAnchor(x=0.8, y=0.8)
            ))],
            subtitles=ProductionSubtitles(font_path="font.ttf"),
        )
        self.job = RenderJob(
            render_job_id="job_1", workspace_id="internal", project_id="project", scenario_id="scenario_1",
            content_format=ContentFormat.DIALOG_MINISERIES, status=RenderJobStatus.RENDERED,
            input_snapshot={"brief_id": "episode_1"},
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_build_verify_and_safe_failed_rebuild(self) -> None:
        internal_before = hashlib.sha256((self.comic / "platforms" / "instagram" / "01.png").read_bytes()).hexdigest()
        final_root = build_comic_handoff_package(
            self.brief, self.job, self.comic, self.root / "output", source_manifest_path=self.source_manifest
        )
        payload = json.loads((final_root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["artifacts"][0]["path"], "instagram_carousel/frame_01.png")
        self.assertEqual(payload["captions"], {"status": "manual_required"})
        self.assertEqual(verify_comic_handoff_package(final_root)["status"], "passed")
        self.assertEqual(internal_before, hashlib.sha256((self.comic / "platforms" / "instagram" / "01.png").read_bytes()).hexdigest())
        before = hashlib.sha256((final_root / "instagram_carousel" / "frame_01.png").read_bytes()).hexdigest()

        (self.comic / "platforms" / "instagram" / "01.png").unlink()
        with self.assertRaisesRegex(ValueError, "Instagram carousel"):
            build_comic_handoff_package(
                self.brief, self.job, self.comic, self.root / "output", source_manifest_path=self.source_manifest
            )
        self.assertEqual(verify_comic_handoff_package(final_root)["status"], "passed")
        self.assertEqual(before, hashlib.sha256((final_root / "instagram_carousel" / "frame_01.png").read_bytes()).hexdigest())

    def test_verifier_rejects_extra_file_checksum_and_schema(self) -> None:
        final_root = build_comic_handoff_package(
            self.brief, self.job, self.comic, self.root / "output", source_manifest_path=self.source_manifest
        )
        (final_root / "extra.txt").write_text("unexpected", encoding="utf-8")
        result = verify_comic_handoff_package(final_root)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(any("exactly match" in error for error in result["errors"]))
        (final_root / "extra.txt").unlink()
        (final_root / "instagram_carousel" / "frame_01.png").write_bytes(b"changed")
        result = verify_comic_handoff_package(final_root)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(any("Checksum mismatch" in error for error in result["errors"]))

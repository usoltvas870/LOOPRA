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
)
from core.tools.comic import (
    COMIC_PACKAGE_SCHEMA_VERSION,
    ComicPackageArtifact,
    ComicPackageError,
    build_comic_package_manifest,
    write_comic_package_manifest,
)
from core.tools.qa import QAResult, check_comic_package_manifest


class ComicPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "comic"
        self.root.mkdir()
        self.frame = self.root / "scene_01.png"
        self.slide = self.root / "platforms" / "instagram" / "01.png"
        self.video = self.root / "platforms" / "tiktok" / "final_video.mp4"
        self.slide.parent.mkdir(parents=True)
        self.video.parent.mkdir(parents=True)
        Image.new("RGB", (270, 480), "blue").save(self.frame, "PNG")
        Image.new("RGB", (1080, 1350), "black").save(self.slide, "PNG")
        self.video.write_bytes(b"video")
        scene = ProductionScene(
            index=0,
            image_source="assets/source.png",
            duration_sec=1,
            comic_overlay=ComicOverlay(
                speaker="nura", text="Привет, ёж", position="top_left", tail_anchor=ComicTailAnchor(x=0.8, y=0.8)
            ),
        )
        self.brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id="brief_1",
            scenario_id="scenario_1",
            content_format=ContentFormat.DIALOG_MINISERIES,
            target_platforms=[PublishingPlatform.TIKTOK, PublishingPlatform.INSTAGRAM],
            scenes=[scene],
            subtitles=ProductionSubtitles(font_path="font.ttf"),
        )
        self.job = RenderJob(
            render_job_id="job_1",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_1",
            content_format=ContentFormat.DIALOG_MINISERIES,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _build(self):
        qa = QAResult(duration_sec=2.5, resolution="270x480", fps=24)
        return build_comic_package_manifest(
            self.brief,
            self.job,
            self.root,
            comic_frames=[self.frame],
            instagram_slides=[self.slide],
            platform_videos={PublishingPlatform.TIKTOK: self.video},
            video_metadata={self.video: qa},
        ), qa

    def test_builds_deterministic_versioned_utf8_round_trip(self) -> None:
        original_brief = self.brief.model_dump(mode="json")
        manifest, qa = self._build()
        self.assertEqual(self.brief.model_dump(mode="json"), original_brief)
        path = write_comic_package_manifest(manifest, self.root / "manifest.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], COMIC_PACKAGE_SCHEMA_VERSION)
        self.assertEqual(payload["requested_platforms"], ["instagram", "tiktok"])
        self.assertEqual(payload["generated_platforms"], ["instagram", "tiktok"])
        self.assertEqual(
            [item["relative_path"] for item in payload["artifacts"]["intermediates"]],
            ["scene_01.png"],
        )
        self.assertEqual(
            [item["relative_path"] for item in payload["artifacts"]["deliverables"]],
            ["platforms/instagram/01.png", "platforms/tiktok/final_video.mp4"],
        )
        self.assertNotIn("manifest.json", json.dumps(payload["artifacts"]))
        self.assertEqual(payload["artifacts"]["intermediates"][0]["sha256"], hashlib.sha256(self.frame.read_bytes()).hexdigest())
        result = check_comic_package_manifest(
            path,
            comic_root=self.root,
            project_id="nura",
            production_brief_id="brief_1",
            render_job_id="job_1",
            requested_platforms=["instagram", "tiktok"],
            video_metadata={self.video: qa},
        )
        self.assertTrue(result.passed, result.errors)

    def test_artifact_rejects_absolute_traversal_duplicate_and_self_paths(self) -> None:
        kwargs = dict(kind="comic_frame", mime_type="image/png", size_bytes=1, sha256="0" * 64)
        for path in (str(self.frame.resolve()), "C:/absolute/scene.png", "../scene.png", "folder\\scene.png"):
            with self.subTest(path=path), self.assertRaises(ComicPackageError):
                ComicPackageArtifact(relative_path=path, **kwargs)
        manifest, _qa = self._build()
        with self.assertRaises(ComicPackageError):
            type(manifest)(
                **{
                    **{field: getattr(manifest, field) for field in manifest.__dataclass_fields__},
                    "deliverables": (manifest.intermediates[0],),
                }
            )
        self_artifact = ComicPackageArtifact(relative_path="manifest.json", **kwargs)
        with self.assertRaises(ComicPackageError):
            type(manifest)(
                **{
                    **{field: getattr(manifest, field) for field in manifest.__dataclass_fields__},
                    "deliverables": (self_artifact,),
                }
            )

    def test_manifest_qa_detects_identity_hash_size_mime_dimension_and_platform_failures(self) -> None:
        manifest, qa = self._build()
        path = write_comic_package_manifest(manifest, self.root / "manifest.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        cases = (
            ("project_id", "other", "project_id"),
            ("schema_version", "999", "schema_version"),
            ("generated_platforms", ["instagram"], "generated platforms"),
        )
        for key, value, message in cases:
            with self.subTest(key=key):
                changed = json.loads(json.dumps(payload))
                changed[key] = value
                path.write_text(json.dumps(changed), encoding="utf-8")
                result = check_comic_package_manifest(
                    path,
                    comic_root=self.root,
                    project_id="nura",
                    production_brief_id="brief_1",
                    render_job_id="job_1",
                    requested_platforms=["instagram", "tiktok"],
                    video_metadata={self.video: qa},
                )
                self.assertFalse(result.passed)
                self.assertTrue(any(message in error for error in result.errors), result.errors)
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.frame.write_bytes(self.frame.read_bytes() + b"tamper")
        result = check_comic_package_manifest(
            path,
            comic_root=self.root,
            project_id="nura",
            production_brief_id="brief_1",
            render_job_id="job_1",
            requested_platforms=["instagram", "tiktok"],
            video_metadata={self.video: qa},
        )
        self.assertFalse(result.passed)
        self.assertTrue(any("size mismatch" in error or "sha256 mismatch" in error for error in result.errors))

    def test_manifest_qa_rejects_missing_invalid_and_unsafe_manifest(self) -> None:
        path = self.root / "manifest.json"
        missing = check_comic_package_manifest(
            path,
            comic_root=self.root,
            project_id="nura",
            production_brief_id="brief_1",
            render_job_id="job_1",
            requested_platforms=["instagram", "tiktok"],
        )
        self.assertFalse(missing.passed)
        path.write_text("{broken", encoding="utf-8")
        invalid = check_comic_package_manifest(
            path,
            comic_root=self.root,
            project_id="nura",
            production_brief_id="brief_1",
            render_job_id="job_1",
            requested_platforms=["instagram", "tiktok"],
        )
        self.assertFalse(invalid.passed)

    def test_manifest_qa_failure_matrix(self) -> None:
        manifest, qa = self._build()
        path = write_comic_package_manifest(manifest, self.root / "manifest.json")
        baseline = json.loads(path.read_text(encoding="utf-8"))

        def checked(payload):
            path.write_text(json.dumps(payload), encoding="utf-8")
            return check_comic_package_manifest(
                path,
                comic_root=self.root,
                project_id="nura",
                production_brief_id="brief_1",
                render_job_id="job_1",
                requested_platforms=["instagram", "tiktok"],
                video_metadata={self.video: qa},
            )

        mutations = []
        wrong_mime = json.loads(json.dumps(baseline))
        wrong_mime["artifacts"]["intermediates"][0]["mime_type"] = "text/plain"
        mutations.append(("MIME", wrong_mime))
        wrong_dimensions = json.loads(json.dumps(baseline))
        wrong_dimensions["artifacts"]["deliverables"][0]["width"] = 1
        mutations.append(("image metadata", wrong_dimensions))
        wrong_video = json.loads(json.dumps(baseline))
        wrong_video["artifacts"]["deliverables"][1]["duration_sec"] = 99
        mutations.append(("video metadata", wrong_video))
        duplicate = json.loads(json.dumps(baseline))
        duplicate["artifacts"]["deliverables"].append(duplicate["artifacts"]["deliverables"][0])
        mutations.append(("duplicate", duplicate))
        unsafe = json.loads(json.dumps(baseline))
        unsafe["artifacts"]["intermediates"][0]["relative_path"] = "../scene_01.png"
        mutations.append(("Unsafe", unsafe))

        for expected, payload in mutations:
            with self.subTest(expected=expected):
                result = checked(payload)
                self.assertFalse(result.passed)
                self.assertTrue(any(expected in error for error in result.errors), result.errors)

        self.video.unlink()
        missing = checked(baseline)
        self.assertFalse(missing.passed)
        self.assertTrue(any("missing" in error for error in missing.errors), missing.errors)

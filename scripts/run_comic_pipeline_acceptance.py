from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.domain import (
    ComicOverlay,
    ComicTailAnchor,
    ContentFormat,
    ProductionBrief,
    ProductionBriefStatus,
    ProductionOutput,
    ProductionScene,
    ProductionSubtitles,
    PublishingPlatform,
    RenderJobStatus,
)
from core.services.production_pipeline import (
    FileSystemOutputFileRepository,
    FileSystemProductionBriefRepository,
    build_production_pipeline_service,
)
from core.tools.qa import check_comic_package_manifest, check_video_output

PROJECT_ID = "comic_acceptance"
SCENE_COUNT = 9
PLATFORMS = (
    PublishingPlatform.INSTAGRAM,
    PublishingPlatform.TIKTOK,
    PublishingPlatform.YOUTUBE_SHORTS,
    PublishingPlatform.VK,
)
SPEAKERS = ("nura", "woman", "shadow")
POSITIONS = (
    "top_left", "top_center", "top_right",
    "middle_left", "middle_right", "bottom_left",
    "bottom_right", "top_left", "middle_right",
)
ANCHORS = (
    (0.80, 0.80), (0.50, 0.75), (0.20, 0.80),
    (0.82, 0.50), (0.18, 0.50), (0.80, 0.20),
    (0.20, 0.20), (0.82, 0.80), (0.18, 0.20),
)
TEXTS = (
    "Нура: Выбор начинается с маленького шага.",
    "Женщина: А если путь уже рядом?",
    "Тень: Смотри внимательнее.",
    "Нура: Не обязательно видеть весь маршрут.",
    "Женщина: Достаточно увидеть следующий поворот.",
    "Тень: Страх любит оставаться безымянным.",
    "Нура: Тогда назовём его и пойдём дальше.",
    "Женщина: Я готова выбрать движение.",
    "Тень: Значит, история только начинается.",
)


def _find_default_font() -> Path | None:
    candidates = (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    )
    return next((path for path in candidates if path.is_file()), None)


def _write_project_config(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "project.yaml").write_text(
        json.dumps(
            {
                "workspace_id": "acceptance",
                "project_id": PROJECT_ID,
                "project_name": "Comic acceptance fixture",
                "project_slug": PROJECT_ID,
                "default_language": "ru",
                "status": "active",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _create_fixture_images(project_dir: Path) -> tuple[list[Path], list[str]]:
    from PIL import Image, ImageDraw

    asset_dir = project_dir / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    colors = ("#375A7F", "#7F5539", "#343A40", "#5B7F54", "#6C4E71", "#825B3C", "#3B6478", "#725D3A", "#4B4F68")
    paths: list[Path] = []
    hashes: list[str] = []
    for index, color in enumerate(colors, start=1):
        path = asset_dir / f"scene_{index:02d}_clean.png"
        image = Image.new("RGB", (270, 480), color)
        draw = ImageDraw.Draw(image)
        draw.rectangle((36, 150, 234, 402), fill="#D8C3A5")
        draw.ellipse((82, 58, 188, 164), fill="#F4D6B0")
        for point, marker in (((0, 0), "#FF0000"), ((269, 0), "#00FF00"), ((0, 479), "#0000FF"), ((269, 479), "#FFFF00")):
            draw.point(point, fill=marker)
        image.save(path, "PNG")
        paths.append(path)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return paths, hashes


def _build_brief(font: Path, source_paths: list[Path], *, font_override: str | None = None) -> ProductionBrief:
    scenes = [
        ProductionScene(
            index=index,
            image_source=f"assets/{path.name}",
            duration_sec=1.0,
            transition_duration=0.0,
            comic_overlay=ComicOverlay(
                speaker=SPEAKERS[index % len(SPEAKERS)],
                text=TEXTS[index],
                position=POSITIONS[index],
                tail_anchor=ComicTailAnchor(x=ANCHORS[index][0], y=ANCHORS[index][1]),
            ),
        )
        for index, path in enumerate(source_paths)
    ]
    return ProductionBrief(
        workspace_id="acceptance",
        project_id=PROJECT_ID,
        production_brief_id="brief_comic_acceptance",
        scenario_id="scenario_comic_acceptance",
        content_format=ContentFormat.DIALOG_MINISERIES,
        target_platforms=list(PLATFORMS),
        scenes=scenes,
        subtitles=ProductionSubtitles(enabled=False, font_path=font_override or str(font)),
        output=ProductionOutput(
            resolution_width=270,
            resolution_height=480,
            fps=24,
            generate_srt=False,
            generate_cover=False,
            generate_audio_only=False,
            generate_comic_master_video=False,
        ),
    ).transition_to(ProductionBriefStatus.VALIDATED)


def _create_contact_sheet(comic_root: Path) -> Path:
    from PIL import Image, ImageDraw

    frames = [Image.open(comic_root / f"scene_{index:02d}.png").convert("RGB") for index in range(1, SCENE_COUNT + 1)]
    width, height = frames[0].size
    sheet = Image.new("RGB", (width * 3, height * 3 + 84), "#1d1d1d")
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        x, y = (index % 3) * width, (index // 3) * height
        sheet.paste(frame, (x, y))
        draw.text((x + 8, y + 8), f"{index + 1:02d}", fill="white")
    draw.text((12, height * 3 + 28), "Technical QA contact sheet — not a production artifact", fill="white")
    output = comic_root / "acceptance_contact_sheet.png"
    sheet.save(output, "PNG")
    return output


def _run_success(workdir: Path, font: Path) -> dict[str, object]:
    projects_root = workdir / "projects"
    project_dir = projects_root / PROJECT_ID
    _write_project_config(project_dir)
    source_paths, source_hashes = _create_fixture_images(project_dir)
    service = build_production_pipeline_service(projects_root=projects_root)
    brief_repo = FileSystemProductionBriefRepository(projects_root=projects_root)
    brief = _build_brief(font, source_paths)
    brief_repo.save_brief(brief)
    job = service.create_render_job(PROJECT_ID, brief.production_brief_id)
    job = service.validate_assets(PROJECT_ID, job.render_job_id)
    if job.status != RenderJobStatus.RENDERING:
        raise RuntimeError("Acceptance fixture assets did not validate")
    job = service.execute_render(PROJECT_ID, job.render_job_id)
    if job.status != RenderJobStatus.RENDERED:
        raise RuntimeError("Acceptance RenderJob was not rendered")

    comic_root = workdir / "storage" / PROJECT_ID / "renders" / job.render_job_id / "comic"
    manifest_path = comic_root / "manifest.json"
    output_files = FileSystemOutputFileRepository(projects_root=projects_root).list_output_files_by_render_job(PROJECT_ID, job.render_job_id)
    manifest_check = check_comic_package_manifest(
        manifest_path, comic_root=comic_root, project_id=PROJECT_ID,
        production_brief_id=brief.production_brief_id, render_job_id=job.render_job_id,
        scene_count=SCENE_COUNT, requested_platforms=[platform.value for platform in PLATFORMS],
    )
    if not manifest_check.passed:
        raise RuntimeError("Acceptance manifest QA failed: " + "; ".join(manifest_check.errors))
    video_paths = {slug: comic_root / "platforms" / slug / "final_video.mp4" for slug in ("tiktok", "youtube_shorts", "vk_clips")}
    video_summary = {}
    for slug, path in video_paths.items():
        qa = check_video_output(path, expected_resolution=(270, 480), expected_fps=24, expected_video_codec="h264", expected_pixel_format="yuv420p")
        if not qa.passed:
            raise RuntimeError(f"Acceptance video QA failed for {slug}: " + "; ".join(qa.errors))
        video_summary[slug] = round(qa.duration_sec or 0.0, 2)
    current_hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths]
    if current_hashes != source_hashes:
        raise RuntimeError("Acceptance source integrity check failed")
    contact_sheet = _create_contact_sheet(comic_root)
    return {
        "render_job_id": job.render_job_id,
        "package_root": str(comic_root),
        "contact_sheet": str(contact_sheet),
        "scene_count": SCENE_COUNT,
        "instagram_slide_count": len(list((comic_root / "platforms" / "instagram").glob("[0-9][0-9].png"))),
        "video_durations_sec": video_summary,
        "output_file_count": len(output_files),
        "manifest": str(manifest_path),
    }


def _run_failure_smoke(workdir: Path, font: Path) -> dict[str, object]:
    projects_root = workdir / "failure_projects"
    project_dir = projects_root / PROJECT_ID
    _write_project_config(project_dir)
    source_paths, source_hashes = _create_fixture_images(project_dir)
    service = build_production_pipeline_service(projects_root=projects_root)
    brief_repo = FileSystemProductionBriefRepository(projects_root=projects_root)
    brief = _build_brief(font, source_paths, font_override=str(project_dir / "missing-font.ttf"))
    brief = brief.model_copy(update={"production_brief_id": "brief_comic_failure"})
    brief_repo.save_brief(brief)
    job = service.create_render_job(PROJECT_ID, brief.production_brief_id)
    job = service.validate_assets(PROJECT_ID, job.render_job_id)
    if job.status != RenderJobStatus.FAILED:
        raise RuntimeError("Missing-font failure smoke did not fail RenderJob validation")
    output_files = FileSystemOutputFileRepository(projects_root=projects_root).list_output_files_by_render_job(PROJECT_ID, job.render_job_id)
    if output_files:
        raise RuntimeError("Missing-font failure smoke registered OutputFile records")
    if [hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths] != source_hashes:
        raise RuntimeError("Missing-font failure smoke changed source assets")
    return {
        "render_job_id": job.render_job_id,
        "render_job_status": job.status.value,
        "output_file_count": len(output_files),
        "source_integrity": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the real 9-scene LOOPRA comic package acceptance.")
    parser.add_argument("--workdir", type=Path, help="Persistent acceptance work directory.")
    parser.add_argument("--font", type=Path, help="TTF/OTF font with Cyrillic glyphs.")
    parser.add_argument("--keep-output", action="store_true", help="Keep the temporary work directory after success.")
    parser.add_argument("--failure-smoke", action="store_true", help="Run the missing-font failure acceptance and exit non-zero.")
    parser.add_argument("--json", action="store_true", help="Write stable JSON to stdout.")
    args = parser.parse_args()
    font = (args.font or _find_default_font())
    if font is None or not font.is_file():
        parser.error("a usable Cyrillic TTF/OTF is required; provide --font PATH")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        parser.error("ffmpeg and ffprobe must be available on PATH")

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.workdir:
        workdir = args.workdir.resolve()
        workdir.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="loopra-comic-acceptance-")
        workdir = Path(temporary.name)
    previous_cwd = Path.cwd()
    try:
        # The existing service intentionally writes runtime artifacts relative to CWD.
        import os
        os.chdir(workdir)
        if args.failure_smoke:
            failure = _run_failure_smoke(workdir, font)
            result = {"status": "failed_as_expected", "failure": failure, "workdir": str(workdir)}
            print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else "Missing-font failure acceptance: PASSED")
            return 1
        result = _run_success(workdir, font)
        result["failure_smoke"] = _run_failure_smoke(workdir, font)
        result["status"] = "passed"
        if args.json:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print("Comic pipeline acceptance: PASSED")
            print(f"Package root: {result['package_root']}")
            print(f"Contact sheet: {result['contact_sheet']}")
        if temporary and not args.keep_output:
            temporary.cleanup()
            temporary = None
        return 0
    except Exception as exc:
        message = {"status": "failed", "message": str(exc), "workdir": str(workdir)}
        print(json.dumps(message, ensure_ascii=False) if args.json else f"ERROR: {message['message']}\nWorkdir: {workdir}", file=sys.stderr)
        return 1
    finally:
        import os
        os.chdir(previous_cwd)
        if temporary is not None and not args.keep_output:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

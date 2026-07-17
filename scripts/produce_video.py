from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.domain import ContentFormat, ProductionBrief
from core.tools.validators import validate_production_assets
from core.projects.loader import PROJECTS_ROOT, resolve_project_dir

USAGE = """\
Produce a narrative video from a Production Brief.

Usage:
  python scripts/produce_video.py --project-id <id> --brief <path> [--dry-run] [--json] [--help]

Options:
  --project-id ID    Project identifier (required)
  --brief PATH       Path to Production Brief JSON file (required)
  --format FORMAT    Content format (default: short_vertical_video)
  --dry-run          Validate assets without rendering
  --json             Output structured JSON to stdout
  --help, -h         Show this help and exit

Environment variables:
  LOOPRA_PROJECTS_ROOT         Project storage root (default: projects/)
  CONTENT_PLANT_PROJECTS_ROOT  Legacy fallback for LOOPRA_PROJECTS_ROOT

Example:
  python scripts/produce_video.py \\
    --project-id nura \\
    --brief projects/nura/data/production_briefs/brief.json
"""


def _resolve_projects_root() -> Path:
    override = (
        os.environ.get("LOOPRA_PROJECTS_ROOT")
        or os.environ.get("CONTENT_PLANT_PROJECTS_ROOT")
        or ""
    ).strip()
    return Path(override).expanduser().resolve() if override else PROJECTS_ROOT


def _error_json(message: str) -> int:
    print(json.dumps({"status": "error", "error_type": "validation_error", "message": message}, indent=2))
    return 1


def _error(message: str, json_mode: bool) -> int:
    if json_mode:
        return _error_json(message)
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    args = list(sys.argv[1:])

    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0

    valid_flags = {"--help", "-h", "--json", "--dry-run", "--project-id", "--brief", "--format"}
    unknown = [a for a in args if a.startswith("-") and a not in valid_flags]
    json_mode = "--json" in args
    dry_run = "--dry-run" in args

    if unknown:
        return _error(f"unknown option: {unknown[0]}", json_mode)

    project_id: str | None = None
    brief_path: str | None = None
    format_name: str = "short_vertical_video"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--project-id":
            i += 1
            if i >= len(args):
                return _error("--project-id requires a value", json_mode)
            project_id = args[i]
        elif arg == "--brief":
            i += 1
            if i >= len(args):
                return _error("--brief requires a value", json_mode)
            brief_path = args[i]
        elif arg == "--format":
            i += 1
            if i >= len(args):
                return _error("--format requires a value", json_mode)
            format_name = args[i]
        elif arg in ("--json", "--dry-run"):
            pass
        else:
            return _error(f"unexpected argument: {arg}", json_mode)
        i += 1

    if not project_id:
        return _error("--project-id is required", json_mode)
    if not brief_path:
        return _error("--brief is required", json_mode)

    format_map = {
        "short_vertical_video": ContentFormat.SHORT_VERTICAL_VIDEO,
        "ambient_vertical_video": ContentFormat.AMBIENT_VERTICAL_VIDEO,
    }
    content_format = format_map.get(format_name)
    if content_format is None:
        return _error(
            f"Unknown format: {format_name}. Must be one of: {', '.join(format_map)}",
            json_mode,
        )

    brief_file = Path(brief_path)
    if not brief_file.exists():
        return _error(f"Brief file not found: {brief_path}", json_mode)

    try:
        raw = json.loads(brief_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _error(f"Invalid JSON in brief file: {exc}", json_mode)

    try:
        raw.setdefault("project_id", project_id)
        brief = ProductionBrief.model_validate(raw)
    except Exception as exc:
        return _error(f"Invalid Production Brief: {exc}", json_mode)

    if brief.content_format != content_format:
        return _error(
            f"Brief content_format '{brief.content_format.value}' "
            f"does not match --format '{format_name}'",
            json_mode,
        )

    projects_root = _resolve_projects_root()
    project_dir = resolve_project_dir(project_id, projects_root)

    try:
        report = validate_production_assets(brief, project_dir)
    except Exception as exc:
        return _error(f"Asset validation error: {exc}", json_mode)

    scene_durations = [s.duration_sec for s in brief.scenes]
    total_duration = 0.0
    for i, dur in enumerate(scene_durations):
        total_duration += dur
        if i < len(scene_durations) - 1:
            total_duration -= brief.scenes[i + 1].transition_duration

    if not report.passed:
        output = {
            "status": "error",
            "error_type": "asset_validation_failed",
            "message": "Asset validation failed",
            "asset_report": {
                "passed": report.passed,
                "errors": report.errors,
                "warnings": report.warnings,
                "missing_files": report.missing_files,
                "corrupt_files": report.corrupt_files,
                "wrong_resolution": report.wrong_resolution,
            },
        }
        if json_mode:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print("Asset validation FAILED")
            for e in report.errors:
                print(f"  ERROR: {e}")
            for w in report.warnings:
                print(f"  WARNING: {w}")
            for m in report.missing_files:
                print(f"  MISSING: {m}")
        return 1

    scene_lines: list[str] = []
    for i, scene in enumerate(brief.scenes):
        nar = scene.narration_text.strip()
        scene_lines.append(
            f"  Scene {i}: \"{scene.image_source}\" ({scene.duration_sec:.1f}s)"
            + (f" — \"{nar[:60]}{'...' if len(nar) > 60 else ''}\"" if nar else "")
        )

    if dry_run:
        output = {
            "status": "success",
            "mode": "dry_run",
            "project_id": project_id,
            "brief_id": brief.production_brief_id,
            "content_format": brief.content_format.value,
            "production_variant": brief.production_variant,
            "scene_count": len(brief.scenes),
            "estimated_duration_sec": round(total_duration, 1),
            "target_resolution": f"{brief.output.resolution_width}x{brief.output.resolution_height}",
            "fps": brief.output.fps,
            "subtitles_enabled": brief.subtitles.enabled,
            "voiceover": brief.audio.voiceover_path or None,
            "music": brief.audio.music_path or None,
            "asset_report": {
                "passed": report.passed,
                "warnings": report.warnings,
                "wrong_resolution": report.wrong_resolution,
            },
        }
        if json_mode:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"DRY RUN for project '{project_id}'")
            print(f"  Brief: {brief.production_brief_id}")
            print(f"  Format: {brief.content_format.value}")
            print(f"  Variant: {brief.production_variant}")
            print(f"  Resolution: {brief.output.resolution_width}x{brief.output.resolution_height} @ {brief.output.fps}fps")
            print(f"  Scenes: {len(brief.scenes)}")
            for line in scene_lines:
                print(line)
            print(f"  Estimated duration: {total_duration:.1f}s")
            print(f"  Subtitles: {'enabled' if brief.subtitles.enabled else 'disabled'}")
            if brief.audio.voiceover_path:
                print(f"  Voiceover: {brief.audio.voiceover_path}")
            if brief.audio.music_path:
                print(f"  Music: {brief.audio.music_path}")
            print("  Asset validation: PASSED")
            print("  (dry-run — skipping render)")
        return 0

    from core.tools.video.renderer import render_narrative_video

    render_dir = project_dir / "storage" / "renders" / brief.production_brief_id
    try:
        render_result = render_narrative_video(brief, render_dir, project_dir)
    except Exception as exc:
        return _error(f"Render failed: {exc}", json_mode)

    output = {
        "status": "success",
        "project_id": project_id,
        "brief_id": brief.production_brief_id,
        "content_format": brief.content_format.value,
        "scene_count": len(brief.scenes),
        "duration_sec": round(total_duration, 1),
        "resolution": f"{brief.output.resolution_width}x{brief.output.resolution_height}",
        "fps": brief.output.fps,
        "artifacts": {
            key: str(path) for key, path in render_result.items()
        },
    }

    if json_mode:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"Render complete for project '{project_id}'")
        print(f"  Brief: {brief.production_brief_id}")
        print(f"  Scenes: {len(brief.scenes)}")
        print(f"  Duration: {total_duration:.1f}s")
        print(f"  Resolution: {brief.output.resolution_width}x{brief.output.resolution_height} @ {brief.output.fps}fps")
        for key, path in render_result.items():
            print(f"  {key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

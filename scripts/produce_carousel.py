from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.domain import ContentFormat, ProductionBrief
from core.tools.qa import check_carousel_output
from core.projects.loader import PROJECTS_ROOT, resolve_project_dir

USAGE = """\
Produce an Instagram carousel from a Production Brief.

Usage:
  python scripts/produce_carousel.py --project-id <id> --brief <path> [--dry-run] [--json] [--help]

Options:
  --project-id ID    Project identifier (required)
  --brief PATH       Path to Production Brief JSON file (required)
  --format FORMAT    Content format (default: instagram_carousel)
  --dry-run          Validate brief without rendering
  --json             Output structured JSON to stdout
  --help, -h         Show this help and exit

Environment variables:
  LOOPRA_PROJECTS_ROOT         Project storage root (default: projects/)
  CONTENT_PLANT_PROJECTS_ROOT  Legacy fallback for LOOPRA_PROJECTS_ROOT

Example:
  python scripts/produce_carousel.py \\
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
    format_name: str = "instagram_carousel"

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
        "instagram_carousel": ContentFormat.INSTAGRAM_CAROUSEL,
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

    if not brief.slides:
        return _error("ProductionBrief has no slides", json_mode)

    projects_root = _resolve_projects_root()
    project_dir = resolve_project_dir(project_id, projects_root)

    slide_count = brief.output.slide_count or len(brief.slides)
    slide_headings = [s.heading.strip()[:60] for s in brief.slides if s.heading.strip()]

    if dry_run:
        output = {
            "status": "success",
            "mode": "dry_run",
            "project_id": project_id,
            "brief_id": brief.production_brief_id,
            "content_format": brief.content_format.value,
            "production_variant": brief.production_variant,
            "slide_count": slide_count,
            "resolution": f"{brief.output.resolution_width or 1080}x{brief.output.resolution_height or 1080}",
            "slides": slide_headings if slide_headings else [f"Slide {i+1}" for i in range(slide_count)],
        }
        if json_mode:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"DRY RUN for project '{project_id}'")
            print(f"  Brief: {brief.production_brief_id}")
            print(f"  Format: {brief.content_format.value}")
            print(f"  Variant: {brief.production_variant}")
            print(f"  Slides: {slide_count}")
            print(f"  Resolution: {brief.output.resolution_width or 1080}x{brief.output.resolution_height or 1080}")
            for i, h in enumerate(slide_headings):
                print(f"    Slide {i+1}: \"{h}\"")
            print("  (dry-run — skipping render)")
        return 0

    from core.tools.carousel.renderer import render_carousel

    render_dir = Path("storage") / project_id / "renders" / brief.production_brief_id / "carousel"
    try:
        render_result = render_carousel(brief, render_dir, project_dir)
    except Exception as exc:
        return _error(f"Render failed: {exc}", json_mode)

    slide_paths = render_result.get("slides", [])

    qa_result = check_carousel_output(
        render_dir,
        expected_count=len(slide_paths),
        expected_size=(brief.output.resolution_width, brief.output.resolution_height),
    )
    qa_passed = qa_result.passed

    if not qa_passed:
        return _error("Carousel QA failed: " + "; ".join(qa_result.errors), json_mode)

    output = {
        "status": "success",
        "project_id": project_id,
        "brief_id": brief.production_brief_id,
        "content_format": brief.content_format.value,
        "slide_count": len(slide_paths),
        "resolution": f"{brief.output.resolution_width or 1080}x{brief.output.resolution_height or 1080}",
        "slides": [str(p) for p in slide_paths],
        "qa_passed": qa_passed,
        "qa_warnings": qa_result.warnings,
    }

    if json_mode:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"Render complete for project '{project_id}'")
        print(f"  Brief: {brief.production_brief_id}")
        print(f"  Slides: {len(slide_paths)}")
        print(f"  Resolution: {brief.output.resolution_width or 1080}x{brief.output.resolution_height or 1080}")
        for i, p in enumerate(slide_paths):
            heading_hint = ""
            if i < len(slide_headings):
                heading_hint = f" — \"{slide_headings[i]}\""
            print(f"  Slide {i+1}: {p}{heading_hint}")
        if qa_passed:
            print("  QA: PASSED")
        else:
            print("  QA: FAILED")
            for w in qa_result.warnings:
                print(f"    WARNING: {w}")
            for e in qa_result.errors:
                print(f"    ERROR: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

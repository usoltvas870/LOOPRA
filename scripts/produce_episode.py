from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.services.episode_package import (
    EpisodePackageValidationError,
    load_episode_package,
    stage_episode_package,
)
from core.services.production_pipeline import (
    FileSystemOutputFileRepository,
    FileSystemProductionBriefRepository,
    build_production_pipeline_service,
)
from core.domain import RenderJobStatus
from core.tools.comic import build_comic_handoff_package, verify_comic_handoff_package


USAGE = """\
Build a LOOPRA comic episode from a canonical Episode Input Package.

Usage:
  python scripts/produce_episode.py --episode <path-to-episode.json> [--validate-only] [--handoff-output <path>] [--json] [--help]
  python scripts/produce_episode.py --verify-package <path-to-final-package> [--json]

Options:
  --episode PATH       Canonical episode.json manifest (required)
  --validate-only      Validate the complete package without rendering
  --handoff-output PATH Root for output/<episode_id>/final (default: output)
  --verify-package PATH Verify an existing final handoff package without rendering
  --json               Write one machine-readable JSON result to stdout
  --help, -h           Show this help and exit

The manifest is the source of episode configuration. Internal production output
is written under storage/<project_id>/renders/; successful production also
creates output/<episode_id>/final by default.
"""


def _write(payload: dict[str, object], *, json_mode: bool, error: bool = False) -> None:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    stream = sys.stderr if error else sys.stdout
    if error:
        print(f"ERROR: {payload['message']}", file=stream)
        for issue in payload.get("errors", []):
            if isinstance(issue, dict):
                print(f"  {issue.get('path')}: {issue.get('message')}", file=stream)
        return
    print(payload.get("message", "Episode package completed"), file=stream)
    for key in ("episode_id", "project_id", "render_job_id", "package_root", "handoff_package_root"):
        if payload.get(key):
            print(f"  {key}: {payload[key]}", file=stream)


def _argument_error(message: str, json_mode: bool) -> int:
    _write(
        {"status": "error", "error_type": "argument_error", "message": message},
        json_mode=json_mode,
        error=True,
    )
    return 2


def main() -> int:
    args = list(sys.argv[1:])
    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0
    json_mode = "--json" in args
    validate_only = "--validate-only" in args
    valid_flags = {"--episode", "--validate-only", "--handoff-output", "--verify-package", "--json", "--help", "-h"}
    unknown = [item for item in args if item.startswith("-") and item not in valid_flags]
    if unknown:
        return _argument_error(f"unknown option: {unknown[0]}", json_mode)

    manifest_path: str | None = None
    handoff_output: str | None = None
    verify_package: str | None = None
    index = 0
    while index < len(args):
        argument = args[index]
        if argument == "--episode":
            index += 1
            if index >= len(args):
                return _argument_error("--episode requires a value", json_mode)
            manifest_path = args[index]
        elif argument in {"--handoff-output", "--verify-package"}:
            index += 1
            if index >= len(args):
                return _argument_error(f"{argument} requires a value", json_mode)
            if argument == "--handoff-output":
                handoff_output = args[index]
            else:
                verify_package = args[index]
        elif argument not in {"--validate-only", "--json"}:
            return _argument_error(f"unexpected argument: {argument}", json_mode)
        index += 1
    if verify_package:
        if manifest_path or validate_only or handoff_output:
            return _argument_error("--verify-package cannot be combined with production options", json_mode)
        result = verify_comic_handoff_package(Path(verify_package))
        _write(
            {
                "status": "success" if result["status"] == "passed" else "error",
                "mode": "verify_package",
                "message": "Handoff package validation: PASSED" if result["status"] == "passed" else "Handoff package validation: FAILED",
                "package_validation_status": result["status"],
                "package_root": result["package_root"],
                "errors": result["errors"],
                "warnings": result["warnings"],
            },
            json_mode=json_mode,
            error=result["status"] != "passed",
        )
        return 0 if result["status"] == "passed" else 1
    if not manifest_path:
        return _argument_error("--episode is required", json_mode)

    try:
        package = load_episode_package(Path(manifest_path))
    except EpisodePackageValidationError as exc:
        _write(
            {
                "status": "error",
                "error_type": "validation_error",
                "message": str(exc),
                "manifest": str(exc.manifest_path),
                "errors": [issue.to_dict() for issue in exc.issues],
            },
            json_mode=json_mode,
            error=True,
        )
        return 1

    initial_hashes = package.source_hashes()
    if validate_only:
        _write(
            {
                "status": "success",
                "mode": "validation_only",
                "message": "Episode package validation: PASSED",
                "manifest": str(package.manifest_path),
                "episode_id": package.brief.production_brief_id,
                "project_id": package.brief.project_id,
                "scene_count": len(package.brief.scenes),
                "target_platforms": [item.value for item in package.brief.target_platforms],
                "source_hashes": initial_hashes,
            },
            json_mode=json_mode,
        )
        return 0

    project_id = package.brief.project_id
    runtime_projects_root = (
        Path.cwd() / "storage" / project_id / "episode_runtime" / "projects"
    ).resolve()
    try:
        staged_brief = stage_episode_package(package, runtime_projects_root)
        brief_repo = FileSystemProductionBriefRepository(runtime_projects_root)
        brief_repo.save_brief(staged_brief)
        service = build_production_pipeline_service(runtime_projects_root)
        job = service.create_render_job(project_id, staged_brief.production_brief_id)
        job = service.validate_assets(project_id, job.render_job_id)
        if job.status != RenderJobStatus.RENDERING:
            report = job.input_snapshot.get("asset_report", {})
            _write(
                {
                    "status": "error",
                    "error_type": "asset_validation_failed",
                    "message": "Staged episode assets failed validation",
                    "render_job_id": job.render_job_id,
                    "asset_report": report,
                },
                json_mode=json_mode,
                error=True,
            )
            return 1
        job = service.execute_render(project_id, job.render_job_id)
        if job.status != RenderJobStatus.RENDERED:
            raise RuntimeError(f"RenderJob ended in unexpected status: {job.status.value}")
        comic_root = (
            Path.cwd() / "storage" / project_id / "renders" / job.render_job_id / "comic"
        ).resolve()
        output_files = FileSystemOutputFileRepository(
            runtime_projects_root
        ).list_output_files_by_render_job(project_id, job.render_job_id)
        final_hashes = package.source_hashes()
        if final_hashes != initial_hashes:
            raise RuntimeError("Source image integrity check failed")
        handoff_root = build_comic_handoff_package(
            staged_brief,
            job,
            comic_root,
            Path(handoff_output) if handoff_output else Path.cwd() / "output",
            source_manifest_path=package.manifest_path,
        )
        _write(
            {
                "status": "success",
                "mode": "production",
                "message": "Episode production: PASSED",
                "manifest": str(package.manifest_path),
                "episode_id": staged_brief.production_brief_id,
                "project_id": project_id,
                "render_job_id": job.render_job_id,
                "package_root": str(comic_root),
                "handoff_package_root": str(handoff_root),
                "artifact_count": len(output_files),
                "artifacts": [str(Path(output_file.path).resolve()) for output_file in output_files],
                "source_hashes": final_hashes,
            },
            json_mode=json_mode,
        )
        return 0
    except Exception as exc:
        _write(
            {
                "status": "error",
                "error_type": "production_error",
                "message": str(exc),
            },
            json_mode=json_mode,
            error=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

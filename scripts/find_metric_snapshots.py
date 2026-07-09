from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.domain import MetricSnapshot, MetricSnapshotStatus
from core.projects.loader import InvalidProjectIdError, PROJECTS_ROOT, load_project, resolve_project_dir


REQUIRED_SNAPSHOT_FIELDS = (
    "metric_snapshot_id",
    "project_id",
    "publication_id",
    "content_item_id",
    "platform",
    "status",
)

USAGE = """\
Find and list DRAFT MetricSnapshot records for a LOOPRA project.

Usage:
  python scripts/find_metric_snapshots.py [--help | -h] <project_id>

Arguments:
  project_id    Project identifier (e.g. example)

Environment variables:
  LOOPRA_PROJECTS_ROOT              Override projects root directory
  CONTENT_PLANT_PROJECTS_ROOT        Legacy fallback for LOOPRA_PROJECTS_ROOT

Example:
  python scripts/find_metric_snapshots.py example"""


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _error_json(message: str) -> int:
    print(json.dumps({"status": "error", "error_type": "validation_error", "message": message}, indent=2))
    return 1


def _resolve_projects_root() -> Path:
    override = (
        os.environ.get("LOOPRA_PROJECTS_ROOT")
        or os.environ.get("CONTENT_PLANT_PROJECTS_ROOT")
        or ""
    ).strip()
    if not override:
        return PROJECTS_ROOT
    return Path(override).expanduser().resolve()


def _resolve_project_dir(project_id: str, projects_root: Path) -> Path:
    load_project(project_id, projects_root=projects_root)
    return resolve_project_dir(project_id, projects_root)


def _list_metric_snapshot_files(project_dir: Path) -> list[Path]:
    snapshot_dir = project_dir / "data" / "metric_snapshots"
    if not snapshot_dir.exists():
        return []
    if not snapshot_dir.is_dir():
        raise ValueError(f"metric snapshot storage is not a directory: {snapshot_dir}")

    try:
        return sorted(
            file_path
            for file_path in snapshot_dir.iterdir()
            if file_path.is_file() and file_path.suffix == ".json"
        )
    except OSError as exc:
        raise OSError(f"metric snapshot storage cannot be read: {snapshot_dir}: {exc}") from exc


def _load_metric_snapshot(file_path: Path, project_id: str) -> MetricSnapshot:
    try:
        raw_text = file_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise OSError(f"metric snapshot storage cannot be read: {file_path}: {exc}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"stored snapshot JSON is not valid JSON: {file_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"stored snapshot JSON must contain an object: {file_path}")

    missing_fields = [field for field in REQUIRED_SNAPSHOT_FIELDS if field not in payload]
    if missing_fields:
        raise ValueError(
            f"stored snapshot JSON is missing required fields ({file_path.name}): {', '.join(missing_fields)}"
        )

    try:
        snapshot = MetricSnapshot.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"stored snapshot JSON is invalid ({file_path.name}): {exc}") from exc

    if snapshot.project_id != project_id:
        raise ValueError(
            f"stored snapshot project_id mismatch in {file_path.name}: "
            f"expected '{project_id}', got '{snapshot.project_id}'"
        )
    return snapshot


def _find_draft_metric_snapshots(project_id: str, projects_root: Path) -> list[MetricSnapshot]:
    project_dir = _resolve_project_dir(project_id, projects_root)
    snapshots = [
        _load_metric_snapshot(file_path, project_id)
        for file_path in _list_metric_snapshot_files(project_dir)
    ]
    drafts = [snapshot for snapshot in snapshots if snapshot.status == MetricSnapshotStatus.DRAFT]
    return sorted(drafts, key=lambda snapshot: snapshot.created_at, reverse=True)


def _format_snapshot_line(snapshot: MetricSnapshot) -> str:
    return " ".join(
        [
            f"metric_snapshot_id={snapshot.metric_snapshot_id}",
            f"publication_id={snapshot.publication_id}",
            f"content_item_id={snapshot.content_item_id}",
            f"platform={snapshot.platform.value}",
            f"status={snapshot.status.value}",
        ]
    )


def _build_json_success(project_id: str, snapshots: list[MetricSnapshot]) -> dict[str, object]:
    return {
        "status": "success",
        "project_id": project_id,
        "metric_snapshots_found": len(snapshots),
        "snapshots": [
            {
                "metric_snapshot_id": s.metric_snapshot_id,
                "publication_id": s.publication_id,
                "content_item_id": s.content_item_id,
                "platform": s.platform.value,
                "status": s.status.value,
            }
            for s in snapshots
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0

    valid_flags = {"--help", "-h", "--json"}
    flags = [a for a in args if a.startswith("-")]
    positional_args = [a for a in args if not a.startswith("-")]
    unknown_flags = [f for f in flags if f not in valid_flags]
    json_mode = "--json" in args

    if unknown_flags:
        message = f"unknown option: {unknown_flags[0]}"
        if json_mode:
            return _error_json(message)
        return _error(message)

    if len(positional_args) != 1:
        if json_mode:
            return _error_json("usage: python scripts/find_metric_snapshots.py [--json] <project_id>")
        return _error("usage: python scripts/find_metric_snapshots.py <project_id>")

    emit_error = _error_json if json_mode else _error
    project_id = positional_args[0]

    try:
        draft_snapshots = _find_draft_metric_snapshots(project_id, _resolve_projects_root())
    except (FileNotFoundError, InvalidProjectIdError, OSError, ValueError) as exc:
        return emit_error(str(exc))

    if json_mode:
        print(json.dumps(_build_json_success(project_id, draft_snapshots), indent=2))
    else:
        print(f"metric_snapshots_found={len(draft_snapshots)}")
        print(f"project_id={project_id}")
        print("snapshots:")
        for snapshot in draft_snapshots:
            print(f"- {_format_snapshot_line(snapshot)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

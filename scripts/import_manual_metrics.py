from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.projects.loader import InvalidProjectIdError, PROJECTS_ROOT
from core.services import AnalyticsValidationError, build_analytics_service


REQUIRED_TOP_LEVEL_FIELDS = (
    "project_id",
    "metric_snapshot_id",
    "metrics",
)
SUCCESS_KEY_ORDER = (
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "clicks",
    "published_url",
)


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _resolve_projects_root() -> Path:
    override = os.environ.get("CONTENT_PLANT_PROJECTS_ROOT", "").strip()
    if not override:
        return PROJECTS_ROOT
    return Path(override).expanduser().resolve()


def _load_json_file(json_path: Path) -> dict[str, Any]:
    if not json_path.exists():
        raise FileNotFoundError(f"manual metrics JSON file does not exist: {json_path}")
    if not json_path.is_file():
        raise ValueError(f"manual metrics JSON path is not a file: {json_path}")

    try:
        payload = json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"manual metrics JSON is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("manual metrics JSON must contain a JSON object")
    return payload


def _validate_payload(payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    missing_fields = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in payload]
    if missing_fields:
        raise ValueError(f"manual metrics JSON is missing required fields: {', '.join(missing_fields)}")

    project_id = payload["project_id"]
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("project_id must be a non-empty string")

    metric_snapshot_id = payload["metric_snapshot_id"]
    if not isinstance(metric_snapshot_id, str) or not metric_snapshot_id.strip():
        raise ValueError("metric_snapshot_id must be a non-empty string")

    metrics = payload["metrics"]
    if not isinstance(metrics, dict):
        raise ValueError("metrics must be an object")
    if not metrics:
        raise ValueError("metrics must not be empty")

    return project_id.strip(), metric_snapshot_id.strip(), metrics


def _build_recorded_keys(metrics: dict[str, Any]) -> str:
    return ",".join(metric_key for metric_key in SUCCESS_KEY_ORDER if metric_key in metrics)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        return _error("usage: python scripts/import_manual_metrics.py <manual_metrics_json>")

    json_path = Path(args[0]).expanduser()

    try:
        payload = _load_json_file(json_path)
        project_id, metric_snapshot_id, metrics = _validate_payload(payload)
        analytics_service = build_analytics_service(_resolve_projects_root())
        analytics_service.record_metrics(project_id, metric_snapshot_id, metrics)
    except (AnalyticsValidationError, FileNotFoundError, InvalidProjectIdError, ValueError) as exc:
        return _error(str(exc))

    print("metrics_import_status=ok")
    print(f"project_id={project_id}")
    print(f"metric_snapshot_id={metric_snapshot_id}")
    print(f"recorded_keys={_build_recorded_keys(metrics)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import sys

from _intelligence_cli import dump_success, error, parse_common, service

USAGE = """\
Activate one TrendPattern.

Usage:
  python scripts/activate_trend_pattern.py [--help | -h] [--json] <project_id> <trend_pattern_id>
"""


def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 2)
    if isinstance(parsed, int):
        return parsed

    json_mode, args = parsed
    try:
        pattern = service().activate_trend_pattern(args[0], args[1])
        return dump_success(
            {"trend_pattern": pattern.model_dump(mode="json")},
            json_mode,
            [
                f"trend_pattern_id={pattern.trend_pattern_id}",
                f"status={pattern.status.value}",
            ],
        )
    except Exception as exc:
        return error(str(exc), json_mode, type(exc).__name__)


if __name__ == "__main__":
    raise SystemExit(main())

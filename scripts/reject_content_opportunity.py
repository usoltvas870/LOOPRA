from __future__ import annotations

import sys

from _intelligence_cli import dump_success, error, parse_common, service

USAGE = """\
Reject one draft ContentOpportunity.

Usage:
  python scripts/reject_content_opportunity.py [--help | -h] [--json] <project_id> <content_opportunity_id>
"""


def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 2)
    if isinstance(parsed, int):
        return parsed

    json_mode, args = parsed
    try:
        opportunity = service().reject_content_opportunity(args[0], args[1])
        return dump_success(
            {"content_opportunity": opportunity.model_dump(mode="json")},
            json_mode,
            [
                f"content_opportunity_id={opportunity.content_opportunity_id}",
                f"status={opportunity.status.value}",
            ],
        )
    except Exception as exc:
        return error(str(exc), json_mode, type(exc).__name__)


if __name__ == "__main__":
    raise SystemExit(main())

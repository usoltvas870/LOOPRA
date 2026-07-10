from __future__ import annotations

import sys

from _intelligence_cli import dump_success, error, parse_common, service

USAGE = """\
Mark one MarketSignal as reviewed.

Usage:
  python scripts/review_market_signal.py [--help | -h] [--json] <project_id> <market_signal_id>
"""


def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 2)
    if isinstance(parsed, int):
        return parsed

    json_mode, args = parsed
    try:
        signal = service().review_market_signal(args[0], args[1])
        return dump_success(
            {"market_signal": signal.model_dump(mode="json")},
            json_mode,
            [
                f"market_signal_id={signal.market_signal_id}",
                f"status={signal.status.value}",
            ],
        )
    except Exception as exc:
        return error(str(exc), json_mode, type(exc).__name__)


if __name__ == "__main__":
    raise SystemExit(main())

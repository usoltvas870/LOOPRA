from __future__ import annotations
import sys
from _intelligence_cli import dump_success, error, load_json_arg, parse_common, service
USAGE = """\
Create one TrendPattern from manual payload and existing MarketSignal IDs.

Usage:
  python scripts/create_trend_pattern.py [--json] '<payload_json>'
"""
def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 1)
    if isinstance(parsed, int): return parsed
    json_mode, args = parsed
    try:
        payload = load_json_arg(args[0]); project_id = str(payload.pop("project_id")); ids = payload.pop("market_signal_ids")
        pattern = service().create_trend_pattern(project_id, market_signal_ids=ids, **payload)
        return dump_success({"trend_pattern": pattern.model_dump(mode="json")}, json_mode, [f"trend_pattern_id={pattern.trend_pattern_id}", f"status={pattern.status.value}"])
    except Exception as exc: return error(str(exc), json_mode, type(exc).__name__)
if __name__ == "__main__": raise SystemExit(main())

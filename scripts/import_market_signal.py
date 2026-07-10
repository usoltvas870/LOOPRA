from __future__ import annotations
import sys
from _intelligence_cli import dump_success, error, load_json_arg, parse_common, service

USAGE = """\
Import one manual MarketSignal.

Usage:
  python scripts/import_market_signal.py [--json] '<payload_json>'
"""

def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 1)
    if isinstance(parsed, int): return parsed
    json_mode, args = parsed
    try:
        payload = load_json_arg(args[0]); project_id = str(payload.pop("project_id"))
        signal = service().create_market_signal(project_id, **payload)
        return dump_success({"market_signal": signal.model_dump(mode="json")}, json_mode, [f"market_signal_id={signal.market_signal_id}", f"status={signal.status.value}"])
    except Exception as exc:
        return error(str(exc), json_mode, type(exc).__name__)
if __name__ == "__main__": raise SystemExit(main())

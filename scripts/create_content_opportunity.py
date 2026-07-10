from __future__ import annotations
import sys
from _intelligence_cli import dump_success, error, load_json_arg, parse_common, service
USAGE = """\
Create one ContentOpportunity from a TrendPattern.

Usage:
  python scripts/create_content_opportunity.py [--json] '<payload_json>'
"""
def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 1)
    if isinstance(parsed, int): return parsed
    json_mode, args = parsed
    try:
        payload = load_json_arg(args[0]); project_id = str(payload.pop("project_id"))
        opp = service().create_content_opportunity(project_id, **payload)
        return dump_success({"content_opportunity": opp.model_dump(mode="json")}, json_mode, [f"content_opportunity_id={opp.content_opportunity_id}", f"status={opp.status.value}"])
    except Exception as exc: return error(str(exc), json_mode, type(exc).__name__)
if __name__ == "__main__": raise SystemExit(main())

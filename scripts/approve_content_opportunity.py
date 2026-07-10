from __future__ import annotations
import sys
from _intelligence_cli import dump_success, error, parse_common, service
USAGE = """\
Approve one ContentOpportunity for possible Idea conversion.

Usage:
  python scripts/approve_content_opportunity.py [--json] <project_id> <content_opportunity_id>
"""
def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 2)
    if isinstance(parsed, int): return parsed
    json_mode, args = parsed
    try:
        opp = service().approve_content_opportunity(args[0], args[1])
        return dump_success({"content_opportunity": opp.model_dump(mode="json")}, json_mode, [f"content_opportunity_id={opp.content_opportunity_id}", f"status={opp.status.value}"])
    except Exception as exc: return error(str(exc), json_mode, type(exc).__name__)
if __name__ == "__main__": raise SystemExit(main())

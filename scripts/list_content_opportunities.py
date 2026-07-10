from __future__ import annotations
import sys
from _intelligence_cli import dump_success, error, parse_common, service
USAGE = """\
List ContentOpportunity records for a project.

Usage:
  python scripts/list_content_opportunities.py [--json] <project_id> [status]
"""
def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, None)
    if isinstance(parsed, int): return parsed
    json_mode, args = parsed
    if len(args) not in {1,2}: return error(f"expected 1 or 2 argument(s), got {len(args)}", json_mode)
    try:
        from core.domain import ContentOpportunityStatus
        status = ContentOpportunityStatus(args[1]) if len(args)==2 else None
        items = service().list_content_opportunities(args[0], status=status)
        return dump_success({"content_opportunities": [i.model_dump(mode="json") for i in items]}, json_mode, [f"content_opportunity_id={i.content_opportunity_id} status={i.status.value}" for i in items])
    except Exception as exc: return error(str(exc), json_mode, type(exc).__name__)
if __name__ == "__main__": raise SystemExit(main())

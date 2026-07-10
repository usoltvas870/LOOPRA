from __future__ import annotations
import sys
from _intelligence_cli import dump_success, error, parse_common, service
USAGE = """\
Convert an approved ContentOpportunity into a Foundation MVP Idea.

Usage:
  python scripts/create_idea_from_opportunity.py [--json] <project_id> <content_opportunity_id>
"""
def main() -> int:
    parsed = parse_common(sys.argv[1:], USAGE, 2)
    if isinstance(parsed, int): return parsed
    json_mode, args = parsed
    try:
        idea = service().create_idea_from_opportunity(args[0], args[1])
        return dump_success({"idea": idea.model_dump(mode="json")}, json_mode, [f"idea_id={idea.idea_id}", f"status={idea.status.value}"])
    except Exception as exc: return error(str(exc), json_mode, type(exc).__name__)
if __name__ == "__main__": raise SystemExit(main())

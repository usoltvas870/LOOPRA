"""Safe Stage 5 Content Intelligence entry point; network is opt-in."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from content_intelligence import ContentIntelligenceError, ProjectAnalysisContext, run_fake_analysis  # noqa: E402
from content_intelligence_provider import run_real_analysis  # noqa: E402


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Run Content Intelligence analysis. Default fake mode makes no network request.")
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--candidate-id", action="append", default=[])
    value.add_argument("--limit", type=int, default=5)
    value.add_argument("--project-id", required=True)
    value.add_argument("--project-context-version", default="1")
    value.add_argument("--target-audience-context")
    value.add_argument("--adaptation-field", action="append", default=[])
    value.add_argument("--acquisition-root", type=Path)
    value.add_argument("--inspection-root", type=Path)
    value.add_argument("--evidence-root", type=Path)
    value.add_argument("--output-root", type=Path, default=ROOT / "data" / "content-intelligence" / "fake")
    value.add_argument("--no-reuse", action="store_true")
    value.add_argument("--json", action="store_true")
    value.add_argument("--provider-real", action="store_true", help="Use the fixed DeepSeek Stage 5E adapter for canonical ranks 1 through 5.")
    value.add_argument("--allow-network", action="store_true", help="Required together with --provider-real to make a network request.")
    value.add_argument("--dry-run", action="store_true", help="Build and validate the real-provider payload without network.")
    value.add_argument("--reuse-only", action="store_true", help="Reuse a validated real result; fail without any provider transport on a miss.")
    value.add_argument("--project-context", type=Path, default=ROOT.parent / "projects" / "nura" / "content_intelligence_context.json")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    run_id = args.manifest.stem.removeprefix("selection_manifest_")
    try:
        if args.reuse_only and not args.provider_real:
            raise ContentIntelligenceError("--reuse-only requires --provider-real")
        if args.provider_real:
            if not args.candidate_id:
                raise ContentIntelligenceError("real provider mode requires explicit --candidate-id values")
            result = run_real_analysis(args.manifest, candidate_ids=tuple(args.candidate_id),
                acquisition_root=args.acquisition_root or ROOT / "data" / "acquisitions" / run_id,
                inspection_root=args.inspection_root or ROOT / "data" / "format-inspections" / run_id,
                intelligence_evidence_root=args.evidence_root or ROOT / "data" / "content-intelligence" / run_id / "candidates",
                output_root=args.output_root.parent / "real", context_path=args.project_context,
                allow_network=args.allow_network, dry_run=args.dry_run, reuse_only=args.reuse_only)
        else:
            result = run_fake_analysis(args.manifest, candidate_ids=tuple(args.candidate_id), limit=args.limit,
            acquisition_root=args.acquisition_root or ROOT / "data" / "acquisitions" / run_id,
            inspection_root=args.inspection_root or ROOT / "data" / "format-inspections" / run_id,
            intelligence_evidence_root=args.evidence_root or ROOT / "data" / "content-intelligence" / run_id / "candidates",
            output_root=args.output_root, project_context=ProjectAnalysisContext(args.project_id, args.project_context_version,
                args.target_audience_context, tuple(args.adaptation_field)), reuse=not args.no_reuse)
    except ContentIntelligenceError as error:
        print(json.dumps({"result": "failed", "error": str(error)}, ensure_ascii=False) if args.json else f"FAILED: {error}")
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"CONTENT INTELLIGENCE: {result.get('analysis_run_id', result['status'])}")
    return 0


if __name__ == "__main__": raise SystemExit(main())

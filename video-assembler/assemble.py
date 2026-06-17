#!/usr/bin/env python3
"""
Content Plant — Video Assembler CLI

Usage:
  python assemble.py <scenario.json>              — assemble single scenario
  python assemble.py --from-trend <trend_top.json> — generate scenarios from trend data (dry-run)
  python assemble.py --from-trend <trend_top.json> --assemble  — generate + assemble
  python assemble.py --job <job_dir>              — assemble a job directory
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.assembler import ScenarioConfig, assemble
from src.pipeline import VideoPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("assemble")


def main():
    parser = argparse.ArgumentParser(description="Content Plant — Video Assembler")
    parser.add_argument("scenario", nargs="?", help="Path to scenario JSON file")
    parser.add_argument("--from-trend", help="Path to trend_top.json for AI pipeline")
    parser.add_argument("--assemble", action="store_true", help="Actually assemble (not dry-run)")
    parser.add_argument("--job", help="Assemble from job directory")
    parser.add_argument("--top-n", type=int, default=10, help="Top N videos to process (default: 10)")

    args = parser.parse_args()

    if args.job:
        job_dir = Path(args.job)
        scenario_path = job_dir / "input" / "scenario.json"
        if not scenario_path.exists():
            logger.error(f"Scenario not found: {scenario_path}")
            sys.exit(1)
        raw = json.loads(scenario_path.read_text("utf-8"))
        cfg = ScenarioConfig.model_validate(raw)
        output = assemble(cfg, job_dir=job_dir)
        print(f"Output: {output}")
        return

    if args.from_trend:
        trend_path = Path(args.from_trend)
        if not trend_path.exists():
            logger.error(f"Trend data not found: {trend_path}")
            sys.exit(1)

        async def run_pipeline():
            pipeline = VideoPipeline(
                trend_data_path=str(trend_path),
                dry_run=not args.assemble,
                use_jobs_dir=args.assemble,
            )
            generated = await pipeline.run(top_n=args.top_n)
            print(f"\nGenerated: {len(generated)} scenarios")

            if args.assemble:
                outputs = await pipeline.assemble_all()
                print(f"Assembled: {len(outputs)} videos")
                for o in outputs:
                    print(f"  {o}")

        asyncio.run(run_pipeline())
        return

    if args.scenario:
        scenario_path = Path(args.scenario)
        if not scenario_path.exists():
            logger.error(f"Scenario not found: {scenario_path}")
            sys.exit(1)
        raw = json.loads(scenario_path.read_text("utf-8"))
        cfg = ScenarioConfig.model_validate(raw)
        output = assemble(cfg)
        print(f"Output: {output}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()

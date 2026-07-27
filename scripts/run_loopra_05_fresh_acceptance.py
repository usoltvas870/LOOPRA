"""Offline synthetic Stage 5O-B0 TOP-20 acceptance runner."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"trend-radar/src")]
from loopra_top20_acceptance_batch import (Top20AcceptanceError, initialize, collect_synthetic, create_editorial_package, finalize_editorial, generate_scripts, create_script_package, finalize_scripts, build_exports, owner_accept, verify, TARGET_COUNT)
def _decisions(name): return [{"rank":rank,"decision":name} for rank in range(1,TARGET_COUNT+1)]
def main(argv=None):
 p=argparse.ArgumentParser(description="Stage 5O-B0 offline synthetic TOP-20 acceptance.")
 p.add_argument("--runtime-root",type=Path,default=ROOT/"trend-radar/data/loopra-05-final-top20")
 p.add_argument("--offline-synthetic-acceptance",action="store_true"); p.add_argument("--initialize",action="store_true"); p.add_argument("--collect",action="store_true"); p.add_argument("--editorial-package",action="store_true"); p.add_argument("--finalize-editorial",action="store_true"); p.add_argument("--generate-scripts",action="store_true"); p.add_argument("--script-package",action="store_true"); p.add_argument("--finalize-scripts",action="store_true"); p.add_argument("--build-exports",action="store_true"); p.add_argument("--owner-accept",action="store_true"); p.add_argument("--verify",action="store_true"); p.add_argument("--json",action="store_true")
 a=p.parse_args(argv)
 try:
  if a.offline_synthetic_acceptance:
   initialize(runtime_root=a.runtime_root); collect_synthetic(runtime_root=a.runtime_root); create_editorial_package(runtime_root=a.runtime_root); finalize_editorial(runtime_root=a.runtime_root,decisions=_decisions("APPROVED_FOR_PRODUCTION_BRIEF"),human_confirmation=True); generate_scripts(runtime_root=a.runtime_root); create_script_package(runtime_root=a.runtime_root); finalize_scripts(runtime_root=a.runtime_root,decisions=_decisions("APPROVE"),human_confirmation=True); build_exports(runtime_root=a.runtime_root); owner_accept(runtime_root=a.runtime_root,decision="ACCEPTED",human_confirmation=True); result=verify(runtime_root=a.runtime_root)
  elif a.initialize: result=initialize(runtime_root=a.runtime_root)
  elif a.collect: result=collect_synthetic(runtime_root=a.runtime_root)
  elif a.editorial_package: result=create_editorial_package(runtime_root=a.runtime_root)
  elif a.finalize_editorial: result=finalize_editorial(runtime_root=a.runtime_root,decisions=_decisions("APPROVED_FOR_PRODUCTION_BRIEF"),human_confirmation=True)
  elif a.generate_scripts: result=generate_scripts(runtime_root=a.runtime_root)
  elif a.script_package: result=create_script_package(runtime_root=a.runtime_root)
  elif a.finalize_scripts: result=finalize_scripts(runtime_root=a.runtime_root,decisions=_decisions("APPROVE"),human_confirmation=True)
  elif a.build_exports: result=build_exports(runtime_root=a.runtime_root)
  elif a.owner_accept: result=owner_accept(runtime_root=a.runtime_root,decision="ACCEPTED",human_confirmation=True)
  else: result=verify(runtime_root=a.runtime_root)
 except Top20AcceptanceError as error: result={"status":"BLOCKED","reason":str(error)}
 print(json.dumps(result,ensure_ascii=False,sort_keys=True,default=str) if a.json else result["status"])
 return 0 if result["status"] not in {"BLOCKED"} else 1
if __name__=="__main__": raise SystemExit(main())

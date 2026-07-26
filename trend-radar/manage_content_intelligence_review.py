"""Safe CLI for the offline human editorial review workflow."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'src'))
from content_intelligence_review import ContentIntelligenceReviewError, create_review, finalize_review, validate_decisions
def parser():
 p=argparse.ArgumentParser(description='Create, inspect, validate or finalize offline Content Intelligence human reviews.'); s=p.add_subparsers(dest='command',required=True)
 for n in ('create','inspect'): q=s.add_parser(n); q.add_argument('--report-root',type=Path,required=True); q.add_argument('--output-root',type=Path,default=ROOT/'data'/'content-intelligence-reviews')
 q=s.add_parser('validate'); q.add_argument('--decision-file',type=Path,required=True); q.add_argument('--completed',action='store_true')
 q=s.add_parser('finalize'); q.add_argument('--decision-file',type=Path,required=True); q.add_argument('--output-root',type=Path,default=ROOT/'data'/'content-intelligence-reviews')
 return p
def main(argv=None):
 a=parser().parse_args(argv)
 try:
  if a.command=='create': r=create_review(report_root=a.report_root,output_root=a.output_root)
  elif a.command=='validate': r=validate_decisions(a.decision_file,require_completed=a.completed)
  elif a.command=='finalize': r=finalize_review(decision_path=a.decision_file,output_root=a.output_root)
  else: r={'status':'INSPECT_UNAVAILABLE','hint':'Use the generated review_form.md locally.'}
 except ContentIntelligenceReviewError as e: print(json.dumps({'status':'FAILED','error':str(e)},ensure_ascii=False)); return 2
 print(json.dumps(r,ensure_ascii=False,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())

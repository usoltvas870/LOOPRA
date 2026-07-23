#!/usr/bin/env python3
"""Deterministic local acceptance for Selected Video Format Inspection."""
from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def _run(command):
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

def _fixture(path, graph, audio=False):
    command = ["ffmpeg", "-y", "-f", "lavfi", "-i", graph]
    if audio: command += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100", "-shortest"]
    command += ["-t", "3", "-pix_fmt", "yuv420p", str(path)]
    result = _run(command)
    if result.returncode: raise RuntimeError(result.stderr)

def main(argv=None):
    parser = argparse.ArgumentParser(); parser.add_argument("--workdir", required=True, type=Path); parser.add_argument("--keep-output", action="store_true"); parser.add_argument("--json", action="store_true"); args = parser.parse_args(argv)
    root = args.workdir.resolve(); media, output = root / "media", root / "evidence"; media.mkdir(parents=True, exist_ok=True); output.mkdir(exist_ok=True)
    fixtures = [("static", "color=c=blue:s=360x640:r=24", False), ("two_states", "color=c=red:s=360x640:r=24:d=1[red];color=c=green:s=360x640:r=24:d=2[green];[red][green]concat=n=2:v=1:a=0", True), ("motion", "testsrc2=s=360x640:r=24", False)]
    results = []
    try:
        for video_id, graph, audio in fixtures:
            source = media / f"{video_id}.mp4"; _fixture(source, graph, audio)
            child = _run([sys.executable, str(ROOT / "inspect_video_format.py"), "--input", str(source), "--video-id", video_id, "--output-dir", str(output / video_id)])
            if child.returncode or child.stdout.splitlines() != ["INSPECTION_RESULT=success"]: raise RuntimeError(f"{video_id}: {child.stdout}{child.stderr}")
            inspection = json.loads((output / video_id / "inspection.json").read_text(encoding="utf-8")); results.append(inspection)
        rows = ["# Selected Video Format Comparison", "", "| video_id | duration | scenes | visual states | mostly static | audio |", "| --- | ---: | ---: | ---: | --- | --- |"]
        for item in results:
            facts, visual = item["media_facts"], item["visual_structure"]
            rows.append(f"| {item['video_id']} | {facts['duration_seconds']:.2f} | {visual['scene_count_estimate']} | {visual['unique_visual_state_count_estimate']} | {visual['mostly_static']} | {facts['audio_present']} |")
        rows += ["", "This deterministic fixture comparison validates the local pipeline only; it is not a claim about TikTok or NURA formats."]
        (output / "comparison.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
        result = {"result": "success", "videos": [item["video_id"] for item in results], "comparison": str(output / "comparison.md")}; (root / "acceptance_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False) if args.json else "INSPECTION_ACCEPTANCE_RESULT=success"); return 0
    except Exception as exc:
        print(json.dumps({"result": "failed", "reason": str(exc)}, ensure_ascii=False) if args.json else f"INSPECTION_ACCEPTANCE_RESULT=failed: {exc}"); return 2

if __name__ == "__main__": raise SystemExit(main())

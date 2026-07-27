"""Public local operator entrypoint for the Stage 5O reused NURA cycle."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "trend-radar/src")]
from loopra_content_cycle import ContentCycleError, build_cycle, register_heygen_clip, register_selected_image, technical_acceptance, validate_owner_decision

def main() -> int:
    parser = argparse.ArgumentParser(description="LOOPRA 0.5 local operator workflow; reuse-only.")
    parser.add_argument("--project", default="nura", choices=("nura",))
    parser.add_argument("--rank", type=int, default=1, choices=(1,))
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--show-export", action="store_true")
    parser.add_argument("--register-image", type=Path)
    parser.add_argument("--register-heygen-clip", type=Path)
    parser.add_argument("--selected-image-registration", type=Path)
    parser.add_argument("--apply-owner-decision", type=Path)
    parser.add_argument("--finalize", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    runtime = ROOT / "trend-radar/data/loopra-content-cycles"
    try:
        base = build_cycle(root=ROOT / "trend-radar", runtime_root=runtime)
        cycle = base["cycle"]
        if args.register_image:
            result = register_selected_image(source_path=args.register_image, cycle=cycle, runtime_root=runtime, owner_selected=True, visual_identity_confirmed=True, blur_panel_absent=True)
        elif args.register_heygen_clip:
            if not args.selected_image_registration: raise ContentCycleError("SELECTED_IMAGE_REGISTRATION_REFERENCE_REQUIRED")
            image = json.loads(args.selected_image_registration.read_text(encoding="utf-8"))
            result = register_heygen_clip(source_path=args.register_heygen_clip, cycle=cycle, image_registration=image, runtime_root=runtime, subtitle_status="OPERATOR_DEFINED", music_status="OPERATOR_DEFINED")
        elif args.apply_owner_decision:
            decision = json.loads(args.apply_owner_decision.read_text(encoding="utf-8"))
            result = {"owner_decision_status": validate_owner_decision(decision, image_registered=False, clip_registered=False)}
        elif args.finalize:
            raise ContentCycleError("FINALIZE_REQUIRES_SELECTED_IMAGE_CLIP_AND_OWNER_DECISION")
        else:
            result = technical_acceptance(root=ROOT / "trend-radar", runtime_root=runtime) if args.verify else base
    except ContentCycleError as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}, ensure_ascii=False) if args.json else f"BLOCKED: {error}")
        return 1
    if args.json:
        print(json.dumps(result.get("report", result), ensure_ascii=False, sort_keys=True))
    else:
        cycle = result.get("cycle") or result["report"]
        print("LOOPRA 0.5 — NURA Rank 1")
        print(f"Заголовок: {cycle.get('video_title', cycle.get('title'))}")
        print("Формат: TALKING_GUIDE · роликов: 1 · изображений: 1")
        print(f"Operator Export: {cycle.get('operator_export_path')}")
        print("Откройте первым: 01_CONTENT_RU.md")
        print("Selected image: PENDING · HeyGen clip: PENDING · practical acceptance: PENDING")
        print("Следующий ручной шаг: скопируйте 02_IMAGE_PROMPT.txt в ChatGPT; LOOPRA ничего не генерирует и не отправляет автоматически.")
    return 0

if __name__ == "__main__": raise SystemExit(main())

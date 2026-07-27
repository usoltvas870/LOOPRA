# LOOPRA 0.5: local operator workflow

Stage 5O records and verifies the already approved NURA Rank 1 chain. It is reuse-only: it does not call AI providers, generate images, call HeyGen, render, or publish.

Phase A is technical completion only. Run `python scripts/run_loopra_05_cycle.py --project nura --rank 1`. Open the displayed `01_CONTENT_RU.md`, copy `02_IMAGE_PROMPT.txt` to ChatGPT manually, then use the clean text manually in HeyGen. For the offline technical check run `python scripts/run_loopra_05_acceptance.py --project nura --rank 1 --verify --json`.

Phase B starts only after the owner has real manual evidence. Register it with `--register-image <SELECTED_IMAGE_PATH>`, then `--register-heygen-clip <HEYGEN_CLIP_PATH> --selected-image-registration <REGISTRATION_JSON>`, and apply the completed owner decision with `--apply-owner-decision <DECISION_JSON>`. `--finalize` rejects incomplete evidence. Phase A does not mean that LOOPRA 0.5 is accepted or frozen; final acceptance is a separate commit in this same session.

Runtime cycle records, reports, private local paths, and copied media are stored under `trend-radar/data/` and are intentionally not tracked. Before a real selected image, HeyGen clip, and explicit owner decision are registered, the honest state is `TECHNICALLY_COMPLETE_PRACTICAL_ACCEPTANCE_PENDING`; it is not LOOPRA 0.5 acceptance and no scope-freeze marker is created.

Deferred work includes automated image generation, HeyGen API use, rendering, publication, VPS operation, analytics feedback, learning memory, multi-brand operation, and an autonomous 24/7 agent.

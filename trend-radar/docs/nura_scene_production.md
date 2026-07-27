# Stage 5N: NURA Scene Production Package

Stage 5N turns the verified Stage 5L bridge and corrected Stage 5M reference
profile into a versioned, text-only Scene Production Package and a Manual
HeyGen Handoff. It is limited to Rank 1, Russian `TALKING_GUIDE`.

The package validates exact, ordered coverage of every approved spoken block;
the provider cannot add spoken text. Prompts bind the canonical visual identity
by SHA-256 as an external image-generation reference only. No image or audio
bytes, absolute paths, full editorial guide, HeyGen data, renderer data or
credentials enter the bounded provider request.

The provider response is persisted before structural validation. Valid packages
are `READY_FOR_OPERATOR_REVIEW`, never auto-approved and never execution-ready.
The handoff tells the operator to generate/select images externally, upload
them manually, and select NURA's configured voice manually in HeyGen. Stage 5N
does not call an image generator, HeyGen, renderer, TTS, FFmpeg, or media tool.

Run the deterministic acceptance:

```powershell
python trend-radar/run_nura_scene_production_acceptance.py --json
```

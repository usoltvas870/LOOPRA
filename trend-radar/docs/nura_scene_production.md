# Stage 5N: NURA Scene Production Package

Stage 5N turns the verified Stage 5L bridge and corrected Stage 5M reference
profile into a versioned, text-only Scene Production Package and a Manual
HeyGen Handoff. It is limited to Rank 1, Russian `TALKING_GUIDE`.

The first five-scene real draft is retained immutably as an operator-rejected
draft. A separate human-owner decision records `REQUEST_ALTERNATIVE_PROMPT` for
each old scene and the new package links that decision without changing its
package or raw provider-response bytes.

The corrected package has exactly three scenes: `block-1`, `block-2` plus
`block-3`, and `block-4` plus `block-5`. Each has explicit structured scene
fields, English positive/negative prompt language labels, a Russian operator
note, safe-area guidance, and a canonical NURA identity-reference instruction.
NURA is the calm direct-to-viewer guide in one continuous ivory, warm-beige
editorial setting: clean semi-realistic 2D/2.5D illustration, not photography,
anime, or a domestic burnout narrative.

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

## Canonical composition and offline reprocessing

The provider owns only a scene-specific creative delta. The trusted application
deterministically composes the final prompt from a versioned canonical NURA
identity prefix, that preserved provider delta, and a canonical talking-avatar
suffix and global negative constraints. This prevents an omission of a literal
invariant (for example, `NURA` or `vertical 9:16`) from weakening the package.
The provider is not represented as author of the composed prompt.

The initially saved real response was retained unchanged after it omitted those
literals. An omission differs from a contradiction: explicit incompatible hair,
character, photographic style, horizontal/rear/profile framing, obscured mouth,
phone at the face, or NURA burnout roleplay remains a hard failure. No new
provider call is made for offline reprocessing.

Use the immutable saved raw response without credentials or network access:

```powershell
python trend-radar/run_nura_scene_production_real_acceptance.py --offline --json
```

The command reparses the raw response, audits contradictions, preserves the
original provider prompts, writes a validation report and produces a new
`READY_FOR_OPERATOR_REVIEW` package only after final composed-prompt validation.
It never auto-generates images, transfers data to HeyGen, or marks production
execution ready.

Run the deterministic acceptance:

```powershell
python trend-radar/run_nura_scene_production_acceptance.py --json
```

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

## Human finalization

An owner `APPROVE_WITH_EDITS` decision never rewrites the review package. The
human finalizer creates a separate immutable package that retains both the
provider creative delta and the original application-composed prompt, alongside
the final human-approved positive and negative prompts, revision reasons,
reviewer identity, timestamp and hashes. Repeating the same decision reuses the
same artifacts; a conflicting decision cannot overwrite them.

Final positive prompts are ordered, deduplicated descriptions of identity,
scene direction, environment, composition, talking-avatar requirements and
safe area. Prohibitions live only in the deduplicated negative prompt, including
the specific `childish cartoon style` constraint rather than a generic cartoon
ban.

The finalized manual handoff embeds the approved subtitle source, provisional
timing state, optional music role and empty per-scene image/clip placeholders.
`READY_FOR_EXTERNAL_IMAGE_GENERATION` authorizes only manual operator work; it
does not mean that images, voice tracks, HeyGen clips, subtitle timing or video
production are ready.

Run the deterministic owner-finalization acceptance:

```powershell
python trend-radar/run_nura_scene_finalization_acceptance.py --json
```

## Simplified operator export

LOOPRA 0.5 separates internal canonical JSON artifacts from the material an
operator actually uses. Internal packages retain provenance, review and
reproducibility. The derived user-facing export requires no JSON reading and
contains only the approved Russian text, ChatGPT-ready image prompt(s), a short
reference instruction and a concise Russian README.

`visual_generation_strategy` is explicit: `ONE_IMAGE` creates one image task
for a continuous talking-guide video; `MULTI_IMAGE` creates independently usable
prompts only when distinct visuals are justified. Current Rank 1 uses
`ONE_IMAGE`: it is a 25–30 second single-speaker TALKING_GUIDE with one identity,
location, wardrobe and emotional arc, so the previous three internal scenes do
not justify three near-identical source images.

The ChatGPT-ready prompt integrates identity-reference usage, scene direction,
style, composition, talking-avatar requirements, safe area, and all negative
constraints. Separate negative-prompt, safe-area and operator-note files are not
part of the user-facing export because the owner's manual ChatGPT workflow uses
one pasted prompt.

Run the offline correction acceptance:

```powershell
python trend-radar/run_nura_operator_export_acceptance.py --json
```

### Operator-export usability correction

The first simplified prompt used percentage-based subtitle safe areas. In
manual ChatGPT generation this produced an unwanted blurred lower panel. The
current derived export leaves the older export immutable and replaces those
percentages with `NATURAL_UNCLUTTERED_IN_FOCUS`: natural breathing room around
and below NURA must remain fully rendered, sharp and coherent. Blur, fog, haze,
gradient fade, frosted/translucent overlays and lower soft-focus washes are
explicitly forbidden in the integrated prompt.

Every user export now has a separate video title contract. Current Rank 1 uses
the unchanged approved hook as `APPROVED_HOOK_FALLBACK`, with
`ACCEPTED_FOR_OPERATOR_EXPORT`; this is not represented as a separate reviewed
upstream title and is not spoken automatically. Future reviewed titles can
replace the fallback without changing Stage 5K here.

The user-facing `01_CONTENT_RU.md` distinguishes one video, its title, five
semantic script sections and their purposes, and a separately fenced exact
HeyGen speech block. Structural labels and explanations are never part of the
spoken text. The export also copies the exact canonical NURA reference bytes
into ignored runtime storage, so the owner can use the package without locating
another artifact. This correction remains fully offline and does not invoke a
provider, image generator, HeyGen or renderer.

Run the deterministic acceptance:

```powershell
python trend-radar/run_nura_scene_production_acceptance.py --json
```

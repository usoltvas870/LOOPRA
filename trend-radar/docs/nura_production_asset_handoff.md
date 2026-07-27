# Stage 5M: NURA Production Reference Handoff

Stage 5M is an offline, project-scoped boundary from a verified Stage 5L
`TALKING_GUIDE` bridge to a manual production-reference handoff. It does not
call HeyGen, an image generator, a provider, a renderer, FFmpeg, or a network
service.

The repository has no canonical NURA avatar/voice registry and no discoverable
human-approved talking-avatar or voice identity. Discovery therefore produces a
Git-ignored candidate manifest and a human selection template, never a selected
asset. Local binary assets remain outside Git; canonical records only use safe
project-relative references and SHA-256 identities.

The legacy Stage 5M profile/handoff remains immutable for provenance. The
corrected v0.2 records have new identities: the PNG is a
`VISUAL_IDENTITY_REFERENCE` for future image-generation prompts, never a
per-episode scene image or mandatory renderer input. The MP3 is an optional
`OPTIONAL_VOICE_REFERENCE`, not a generated voice track or required HeyGen
input. Both retain their content hashes and project-relative references.

LOOPRA 0.5 creates neither scene images nor voice tracks, and transfers nothing
to HeyGen. A future operator-facing package will instruct the operator to create
and select images externally, upload them manually, and select the configured
NURA voice in HeyGen. Renderer assignment remains `UNASSIGNED`, verification
remains `UNVERIFIED`, and `production_execution_ready` remains false.

Run discovery with:

`python trend-radar/run_nura_production_asset_handoff_acceptance.py --bridge <Stage-5L-bridge> --voice <candidate>`

After an owner decision, run the same offline command with `--finalize`,
`--selected-avatar` and `--selected-voice`. It copies the exact source bytes
to the ignored content-addressed `assets/nura/` store, validates byte equality,
persists the decision, and atomically creates the profile and handoff.

To build the corrected manual-workflow records from immutable legacy artifacts,
add `--correct-manual-workflow --legacy-profile <path> --legacy-handoff <path>`.

The generated `human_selection.json` requires an explicit approval reference
and `human_confirmation=true`. Cropping, scene prompts, external image
generation, human scene-image selection, manual HeyGen work, final voice-track
generation, subtitle timing, final assembly and publication are deferred to
Stage 5N or later.

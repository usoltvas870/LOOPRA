# Stage 5M: NURA Production Asset Handoff

Stage 5M is an offline, project-scoped boundary from a verified Stage 5L
`TALKING_GUIDE` bridge to a renderer-neutral handoff. It does not call HeyGen,
a provider, a renderer, FFmpeg, or a network service.

The repository has no canonical NURA avatar/voice registry and no discoverable
human-approved talking-avatar or voice identity. Discovery therefore produces a
Git-ignored candidate manifest and a human selection template, never a selected
asset. Local binary assets remain outside Git; canonical records only use safe
project-relative references and SHA-256 identities.

An approved selection creates a versioned Production Asset Profile and External
Renderer Handoff. The handoff preserves the Stage 5L bridge hash, exact approved
script, subtitle source, provisional timing and secondary music role. Renderer
assignment remains `UNASSIGNED`, verification remains `UNVERIFIED`, and
`production_execution_ready` remains false.

Run discovery with:

`python trend-radar/run_nura_production_asset_handoff_acceptance.py --bridge <Stage-5L-bridge> --voice <candidate>`

After an owner decision, run the same offline command with `--finalize`,
`--selected-avatar` and `--selected-voice`. It copies the exact source bytes
to the ignored content-addressed `assets/nura/` store, validates byte equality,
persists the decision, and atomically creates the profile and handoff.

The generated `human_selection.json` requires an explicit approval reference
and `human_confirmation=true`. Voice identity is a reusable local/external
reference; it is not a generated track. Cropping, compatibility verification,
voice generation, duration measurement, subtitle timing, adapter implementation
and renderer execution are deferred.

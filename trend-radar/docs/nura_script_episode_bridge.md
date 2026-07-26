# NURA Script-to-Production Bridge (Stage 5L)

Stage 5L introduces a versioned, deterministic **pre-episode** input artifact
for one finalized Rank 1 Russian `TALKING_GUIDE`. It does not render or call a
provider. Its authority order is: finalized Human Script Review, the linked
`HUMAN_APPROVED` Script Output, Script Input and Production Brief provenance,
then the NURA editorial identity.

The existing canonical Episode Input Package v1 is not reused: it accepts only
`dialog_miniseries`, requires image-backed comic frames and bubble dialogue,
and feeds the comic/video renderer. Inventing those frames for a spoken guide
would falsify the approved source. Stage 5L therefore selects Option C, a
separate pre-episode bridge; it does not change Episode Input Package v1 or the
production engine.

The bridge preserves the exact five approved blocks and their full-text round
trip. The same text is the subtitle source, but timestamps are explicitly
`PROVISIONAL_NO_AUDIO_MEASUREMENT`: no audio, TTS, timing analysis or subtitle
rendering occurs. It declares NURA avatar, voice asset, external renderer and
audio timing as unresolved requirements. Music is `SECONDARY_OPTIONAL`; no
track is invented.

`production_input_ready=true` means the approved script has a validated,
immutable downstream handoff. `production_execution_ready=false` honestly
means the required avatar, voice, renderer and measured timing do not yet
exist. The bridge writes atomically under ignored `trend-radar/data/`, reuses
only byte-identical content, and rejects conflicting reuse.

Run the offline acceptance:

```powershell
python trend-radar/run_nura_script_episode_bridge_acceptance.py --json
```

It reads the canonical finalized Stage 5K runtime artifacts, verifies hashes
and provenance, builds the bridge twice, and proves reuse. It makes no AI,
network, credential, provider, renderer, FFmpeg or media calls. Actual avatar
selection, voice generation, audio measurement, subtitle alignment, external
renderer/HeyGen handoff, rendering, export and publication are deferred.

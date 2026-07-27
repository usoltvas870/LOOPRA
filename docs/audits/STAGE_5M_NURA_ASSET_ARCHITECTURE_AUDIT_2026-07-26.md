# Stage 5M NURA Asset Architecture Audit

Repository audit found the Stage 5L bridge builder at
`trend-radar/src/nura_script_episode_bridge.py`. It establishes immutable
review/script provenance, exact approved text, provisional subtitle timing and
unresolved avatar/voice/renderer requirements.

No canonical project asset registry, approved talking-avatar portrait, approved
voice identity, renderer-neutral handoff contract, or provider adapter exists.
`projects/nura/project.yaml` contains only logo references. Ignored local media
includes an unapproved standalone MP3 and historical/comic output media; these
are candidates or unrelated output, not canonical voice/avatar evidence.

Stage 5M stores only runtime candidate manifests, human decisions, profiles and
handoffs under ignored `trend-radar/data/nura-production-asset-handoff/`.
Tracked code contains no absolute paths, provider IDs, credentials or binary
payloads. The contract deliberately keeps renderer assignment unassigned and
compatibility unverified.

## Semantic correction

After owner clarification, the initially successful asset handoff was
reclassified without altering its immutable runtime artifacts. The canonical
PNG is a visual identity reference for future external image-generation prompts;
it is not a per-episode scene asset or required renderer input. The canonical
MP3 is an optional voice-reference sample; it is not a final voice track or a
required HeyGen input. Corrected v0.2 profile and manual-handoff records retain
legacy hashes as provenance, have new semantic identities, and explicitly state
that LOOPRA 0.5 performs no image generation, no direct HeyGen transfer and no
renderer invocation. The next bounded gate is Stage 5N: Scene Production Package
and Manual HeyGen Handoff.

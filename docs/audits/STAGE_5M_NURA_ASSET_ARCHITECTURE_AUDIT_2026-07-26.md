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

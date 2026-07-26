# Stage 5L Script-to-Episode Input Bridge Audit

## Decision

Option C — a standalone pre-episode bridge artifact — is required. The
canonical Episode Input Package v1 is a bounded `DIALOG_MINISERIES` comic
contract: it requires `frames`, a source image, speaker, bubble text and tail
geometry for each scene, then invokes the comic production pipeline. It cannot
honestly represent a single NURA talking-avatar source with spoken blocks.

Stage 5L consequently leaves `core/services/episode_package.py`, the comic
renderer and all production execution paths unchanged. It maps only the
finalized Rank 1 `TALKING_GUIDE` to a versioned, hash-linked pre-episode bridge.
No comic frames, dialogue bubbles, measured timestamps, assets, music track or
renderer assignment are fabricated.

## Preserved boundary

The bridge validates the finalized review decision and owner confirmation,
`HUMAN_APPROVED` Script Output identity/hash, provider and Script Input links,
Production Brief hash, candidate identity and rank. It stores exact approved
spoken blocks, the exact subtitle source, provisional timing, NURA avatar and
voice requirements, secondary optional music, and explicit unresolved
execution requirements. It is atomically persisted in ignored runtime storage
and byte-identical construction is reused.

The production input is ready; execution is intentionally not ready until a
future bounded stage supplies real avatar/voice assets, audio timing and an
external renderer adapter. No provider, network, credentials, renderer,
FFmpeg, output package or publication are involved.

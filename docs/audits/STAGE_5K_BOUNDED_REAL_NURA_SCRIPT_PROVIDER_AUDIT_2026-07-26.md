# Stage 5K Bounded Real NURA Script Provider — Audit

## Baseline and boundary

- Branch: `main`; starting HEAD: `3f0226801371587b0f760f6e22cfe6ad73623c9e`.
- Stage 5J (`3f022680`) and the Script Contract foundation (`73875f8`) are
  present. Their contract, Production Brief and finalized human-review
  artifacts remain upstream and are not modified by Stage 5K.
- The worktree contained unrelated modified and untracked files before this
  block. They remain outside the Stage 5K diff.

## Decision

`trend-radar/src/content_intelligence_provider.py` already owns the canonical
DeepSeek endpoint, `DEEPSEEK_API_KEY` boundary, HTTP timeout, error taxonomy,
JSON request settings and safe response-size policy. Stage 5K exposes its
bounded `post_deepseek_request` transport helper and reuses it from the new
script-specific adapter. No parallel DeepSeek client is introduced.

The script-specific prompt is located in
`trend-radar/src/nura_real_script_provider.py` as prompt ID
`nura-script-generation`, version `1.3` for future calls; it is intentionally separate from
Content Intelligence prompt versioning. The same module creates a bounded
provider request, trusted output envelope, raw/validated artifact persistence,
hard validation and credentialless reuse. The Stage 5K adapter additionally
uses advisory provider constraint IDs/block IDs. Application-resolved evidence
copies exact block text without paraphrasing; provider spans and notes are not
authoritative. Unknown IDs remain deterministic hard failures, while a bad
optional span is visible as a warning and human-review limitation.

Attempt 3 is reprocessed offline from its immutable raw response, rather than
regenerated. Its original prompt provenance remains `1.2`. The historical
`request_hash` covered only bounded request data, so prompts `1.0`–`1.2` could
share it; future effective-request identity additionally hashes provider/model,
prompt ID/version, effective prompt messages, format, profile hash and Script
Input hash. No provider call is made by offline reprocessing.

The Stage 5K review finalization extension creates immutable, hash-linked
runtime artifacts only after an `OWNER` reviewer with explicit confirmation
chooses `APPROVED_FOR_EPISODE_BRIDGE`. It preserves the provider draft, stores
human revision reasons and a distinct human-approved Script Output, supports
stable reuse, and rejects a conflicting second finalization. The readiness bit
is only a review-gate result; no Episode Input Package is created here.

All real runtime data are written below the already ignored
`trend-radar/data/` boundary. Stage 5J schemas are preserved. The only
contract extension is deterministic provider-side validation around the
existing TALKING_GUIDE payload and the current hard-gate result.

## Scope retained

The acceptance runner uses the canonical Rank 1 Production Brief and
`TALKING_GUIDE`. It does not generate ranks 2–5, approve a human review,
construct Episode Input, call production, render media, export or publish.

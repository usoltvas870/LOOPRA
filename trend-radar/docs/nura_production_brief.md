# NURA Production Brief Contract

## Purpose and boundary

Stage 5I converts a finalized, owner-confirmed Human Editorial Review into a deterministic, candidate-scoped NURA Production Brief. The primary consumer is a future script-contract or production-orchestration layer. The contract is strictly downstream: it does not alter the review, source cards, report, canonical ranking, evidence, provider output, or ProjectAnalysisContext.

The brief is not a script. It contains no generated dialogue, voiceover, shot list, assets, music, montage plan, publishing metadata, image, or video.

## Required sources and precedence

The builder starts with `review_result.json` and `review_manifest.json` from a finalized review. It requires `COMPLETED`, `nura-owner`, `OWNER`, and `human_confirmation=true`; pending or unfinalized reviews are rejected.

For every rank, values are resolved in this order:

1. Explicit approved human revision.
2. Human-accepted source-card value, retaining its AI origin.
3. Explicit human-approved direction.
4. Typed `UNRESOLVED` or `NOT_TYPED` value.

Each field has provenance: source type, portable ref, hash, source path, reviewer and human-verification state, claim/evidence references, status, and warnings. Revisions validate their source hash, reviewer, approval, reason, known claim IDs, and known evidence refs. A stale revision blocks the candidate; it never falls back silently to the AI value.

## Schema and readiness

`NuraProductionBrief` v0.1 records the immutable manifest/radar/candidate identity, original rank, finalized review and source-card identities, human decision and eligibility, provenance-aware fields, safety and project constraints, evidence limitations, unresolved fields, readiness, warnings, errors, and deterministic hash.

`NuraProductionBriefRun` v0.1 records the five candidates in original order, brief refs/hashes, readiness counts, unresolved summary, zero AI/provider/network/script counters, and deterministic run hash.

- `READY_FOR_SCRIPT_CONTRACT`: human decision `APPROVED_FOR_PRODUCTION_BRIEF` plus `ELIGIBLE`.
- `READY_WITH_HUMAN_REVISIONS`: approved revisions were exactly applied.
- Invalid sources and stale revisions are blocked; readiness never re-ranks candidates.

Current expected unresolved values include `hook_type` and `production_complexity` (`NOT_TYPED`), plus fields that upstream has not typed. The builder does not semantically complete them.

## Runtime and reuse

Runtime is Git-ignored under `trend-radar/data/nura-production-briefs/<run-id>/`:

- `brief_run.json`
- `brief_manifest.json`
- `brief_index.md`
- `candidates/<video-id>/production_brief.json`
- `candidates/<video-id>/production_brief.md`

All artifacts use atomic writes, canonical UTF-8 JSON, portable references, bounded text, and deterministic hashes. A valid unchanged package returns `REUSED` with no metadata churn. Invalid JSON or Markdown fails reuse validation; conflicting output is never overwritten.

Markdown is Russian, makes human review, AI origin, original rank, revisions, safety, prohibited copying, and unresolved fields visible, and never includes absolute paths, raw provider responses, full OCR/transcript corpora, or scripts.

## Offline and scope guarantees

The CLI accepts only finalized-review, canonical-manifest, approved source-card root, ProjectAnalysisContext, output root, and ranks 1–5 (maximum five). `--help` performs no source reads. The builder does not read API keys, call providers, use network transport, run evidence production, or inspect ranks 6–20.

The real Stage 5I acceptance uses the finalized five-candidate NURA review and produces four `READY_WITH_HUMAN_REVISIONS` briefs and one `READY_FOR_SCRIPT_CONTRACT` brief. It performs zero AI, provider, network, or script-generation calls.

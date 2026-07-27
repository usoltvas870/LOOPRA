# LOOPRA 0.5 fresh TOP-20 acceptance — B0 contract

Stage 5O-B0 introduces the versioned `FRESH_TOP20_OPERATOR_BATCH_ACCEPTANCE`
boundary. It is a one-time NURA acceptance batch, not a TOP-20 production
mode, LOOPRA 1.0, automation, connector, publishing, HeyGen integration or
analytics/learning loop.

The new `LoopraTop20AcceptanceBatch` and its 20 immutable item records preserve
original ranks 1–20 and use content-identical atomic persistence. They aggregate
existing single-item primitives without modifying their five-item or Rank 1
contracts. Batch phases enforce editorial review, script review and owner batch
acceptance. `scope_frozen=true` is possible only after the explicit accepted
owner decision and 20 export references.

The B0 runner is deliberately offline and synthetic:

```powershell
python scripts/run_loopra_05_fresh_acceptance.py --offline-synthetic-acceptance --json
```

It writes ignored runtime metadata under `trend-radar/data/loopra-05-final-top20/`.
It never searches, reads credentials, calls a provider, creates real media,
images, HeyGen clips, renderer output or user-facing exports. The future B1 real
runner must be separately approved and must write the final operator layout
`output/LOOPRA_05_FINAL_TOP20_<batch_id>/` with 20 sources and 20 materials.

Existing five-item Content Intelligence/report/review/Production Brief flows,
single-item script/export contracts, Rank 1 content cycle and Stage 5O Phase A
remain unchanged and backward-compatible.

## B1A adapter foundation (offline only)

`LoopraTop20B1Adapter` is a separate, versioned execution envelope for a future
fresh TOP-20 run. It binds a selection manifest to twenty ordered plans and
preserves every candidate ID, video ID and original rank `1..20`. Its runtime
references are portable relative references; they are not user paths.

The B1A synthetic runner creates only deterministic fixture records for media,
acquisition, inspection, OCR, transcription and Content Intelligence. It then
builds a distinct `LoopraTop20ContentIntelligenceReport` and a pending,
non-finalized twenty-item editorial review. It never selects a winner or allows
a Production Brief before a human finalizes that review.

```powershell
python scripts/run_loopra_05_fresh_acceptance.py --b1-offline-synthetic --json
```

Rerunning reuses content-identical snapshots. An injected retryable item can be
resumed without deleting the nineteen completed items. B1A does not alter the
v1 five-item limits or its report/review contracts.

## B1B v2 real-pipeline contracts

The approval-only v2 layer is separate from every v1 five-item API. It defines
`LoopraTop20MediaAcquisitionV2`, `LoopraTop20ContentIntelligenceRequestV2`,
`LoopraTop20ContentIntelligenceCardV2`, the ordered aggregate and the owner
review package. Its offline proof is available via:

```powershell
python scripts/run_loopra_05_fresh_acceptance.py --b1-v2-offline --json
```

This proof creates no browser, network, provider call or credential read.

`run_fresh_top20_b1` is the single B1 orchestration shape. Its tests inject
collection, selection, acquisition, evidence and provider boundaries.

## B1C production dependency wiring

`build_fresh_top20_b1_production_dependencies` is the production composition
boundary for `run_fresh_top20_b1`. It adapts the canonical Trend Radar collector,
selection manifest, bounded browser-context capture, Format Inspection, OCR,
transcription and shared DeepSeek transport without changing their public v1
contracts or five-item limits.

Before `--b1-real` starts the batch it runs
`validate_fresh_top20_b1_production_readiness`. The preflight verifies callable
imports, compatible B1/v2 schemas, the project-scoped NURA source configuration,
the ignored runtime root and the owned/CDP-safe browser lifecycle boundary. A
real missing dependency is reported as
`B1_REAL_DEPENDENCY_MISSING:<dependency_name>`; a successful composition returns
`ready=true`.

```powershell
python scripts/run_loopra_05_fresh_acceptance.py --b1-real --json
```

The command delegates to the existing `run_fresh_top20_b1`; it does not contain
a second orchestration path. Collection and the acquisition browser context are
bounded and closed in `finally`. An owned browser is closed, while a CDP-attached
user Chrome is only detached through `TikTokCollector.close`. Runtime artifacts
remain under the Git-ignored B1 root. Provider credentials, cookies,
Authorization headers, absolute local paths, media bytes and base64 are excluded
from persisted request identity and metadata.

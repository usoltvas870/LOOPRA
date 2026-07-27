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
resumed without deleting the nineteen completed items. `--b1-real` is typed
blocked as `REAL_B1_NOT_ENABLED_UNTIL_ADAPTER_FOUNDATION_COMMITTED`; it must not
start a browser, search, provider call or credential lookup. B1A does not alter
the v1 five-item limits or its report/review contracts.

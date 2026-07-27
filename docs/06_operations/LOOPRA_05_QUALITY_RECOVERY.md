# LOOPRA 5O-B1E: recovery of search and evidence quality

The owner rejected batch `fresh-v2-72a2133ce76a` for retrieval, relevance and evidence-grounding quality. It remains an immutable forensic fixture and cannot generate Production Briefs, scripts or exports.

Run the offline audit only:

```powershell
python scripts/run_loopra_05_quality_recovery.py --batch fresh-v2-72a2133ce76a --audit --json
```

It performs no collection, browser, media download or provider call. Output is ignored runtime under `quality-recovery-v1.1/`, including the rejection decision, duplicate report and `quality-recovery-owner-triage/` package.

The future-run gates are versioned by `loopra_quality_recovery`: identity dedupe before ranking; media/frame/audio dedupe after acquisition; relevance hard gate (engagement cannot compensate for zero topical relevance); evidence sufficiency; source specificity; and owner review of possible template contamination. No scoring weights or canonical search configuration are changed until the owner completes all 20 labels with `human_confirmation=true`.

## Stage 5O-B1E.2 grounded preflight

The rejected v1.1 package is a superseded forensic artifact and must not be
rewritten.  Build the independent v1.2 evidence packets before any bounded
provider run:

```powershell
python scripts/run_loopra_05_quality_recovery.py --batch fresh-v2-72a2133ce76a --grounded-preflight --json
```

This creates ignored runtime JSON under `quality-recovery-v1.2/evidence-packets/`.
Each packet preserves references, full meaningful transcript segments and
deduplicated readable OCR observations.  It records unavailable visual
descriptions and missing search/ranking fields explicitly; it never guesses
them.  Rank 18 is explicitly reserved as `DUPLICATE_OF_RANK_13`, so a future
grounded provider run must reuse rank 13 rather than call the provider twice.

No provider, browser, TikTok, media-download, Production Brief, renderer, or
publication operation occurs in preflight.

After the offline tests pass, the bounded grounded run is:

```powershell
python scripts/run_loopra_05_quality_recovery.py --batch fresh-v2-72a2133ce76a --grounded-reprocess --build-actionable-package --json
```

Grounded validation resolves every provider evidence reference back to the
canonical transcript/OCR excerpt. Summaries may be semantic paraphrases; the
application-owned evidence bridge, unknown-ref checks, metrics/genericity
gates, and junk-format psychology gate remain deterministic. Rank 18 reuses
rank 13 and is excluded from contamination comparisons as a known duplicate.

An identical completed run must be verified without credentials:

```powershell
python scripts/run_loopra_05_quality_recovery.py --batch fresh-v2-72a2133ce76a --grounded-reprocess --build-actionable-package --reuse-only --json
```

# LOOPRA 5O-B1E: recovery of search and evidence quality

The owner rejected batch `fresh-v2-72a2133ce76a` for retrieval, relevance and evidence-grounding quality. It remains an immutable forensic fixture and cannot generate Production Briefs, scripts or exports.

Run the offline audit only:

```powershell
python scripts/run_loopra_05_quality_recovery.py --batch fresh-v2-72a2133ce76a --audit --json
```

It performs no collection, browser, media download or provider call. Output is ignored runtime under `quality-recovery-v1.1/`, including the rejection decision, duplicate report and `quality-recovery-owner-triage/` package.

The future-run gates are versioned by `loopra_quality_recovery`: identity dedupe before ranking; media/frame/audio dedupe after acquisition; relevance hard gate (engagement cannot compensate for zero topical relevance); evidence sufficiency; source specificity; and owner review of possible template contamination. No scoring weights or canonical search configuration are changed until the owner completes all 20 labels with `human_confirmation=true`.

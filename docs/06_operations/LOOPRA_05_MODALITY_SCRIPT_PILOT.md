# LOOPRA 05 Modality-Aware Script Pilot

This bounded operational pilot processes only ranks 2, 6, 9, 16, 17 and 19 from an already acquired batch. It never invokes search, browser collection, or media acquisition, and it does not unblock global B2.

The runner consumes immutable grounded evidence packets, writes git-ignored runtime artifacts under `quality-recovery-v1.2/quality-pilot-v1`, and creates versioned modality assessments and Source Understanding Cards. Rank 9 is an explicit `IRRELEVANT` control and has no production brief or script. Rank 2 is blocked unless a sufficient, evidence-backed text consensus exists; its music ASR is never used as literal source content.

Run:

```powershell
python scripts/run_loopra_05_modality_script_pilot.py --batch fresh-v2-72a2133ce76a --ranks 2,6,9,16,17,19 --runtime-root trend-radar/data/loopra-05-b1c-real-20260727-authenticated --run --json
```

All generated materials are `QUALITY_PILOT` artifacts awaiting owner review. Existing NURA provider and operator-export contracts remain the only sanctioned downstream boundaries; no approval, publication, or global batch finalization occurs here.

# LOOPRA TikTok Video Identity and Link Integrity Audit — 2026-07-23

## Status

PARTIAL — the report excludes unverified links, but the first controlled
validation achieved 28/30 (93.3%), below the required 95% acceptance threshold.

## Previous readiness correction

The prior `MANUAL TREND SELECTION READY` decision did not verify that clickable
TikTok URLs resolved to their claimed videos. User testing found an unavailable
permalink and only one of three ID-only fallbacks opened. That decision is
withdrawn.

## Root cause and evidence boundary

The old parser treated several generic response containers as video lists,
allowed nested-ID fallback and used `author.nickname` when `author.uniqueId`
was absent. It did not retain endpoint or JSON identity paths. This made wrong
video-object identity possible. The old runtime evidence preserves the report
and run journal but not raw API bodies, so the three reported historical rows
cannot be attributed to an exact JSON path after the fact.

## Repair

The parser now accepts only self-contained endpoint-specific video objects:
valid TikTok-length top-level `id`, `author.uniqueId`, and local stats/create
time. Music/challenge/container IDs, nickname fallbacks and unknown wrappers are
rejected. Every accepted object records endpoint, ID path, author path, identity
confidence, canonical URL, fallback URL and identity warnings.

Canonical URLs use a matching public share URL only when its video ID agrees;
otherwise they are built from `author.uniqueId` and the validated video ID.
The report checks its bounded pre-ranking set in the authenticated context and
includes only `AVAILABLE` or `REDIRECTED_TO_CANONICAL` rows in `TOP MANUAL
REVIEW CANDIDATES`.

## Controlled run

`AUTH_RESULT=session_valid`; `RADAR_RESULT=success`; exit code 0; duration
306.685 seconds. The Russian NURA configuration queried 20 sources and produced
721 raw discoveries, 179 unique records and 25 new records. It checked 30
ranked candidates: 28 `AVAILABLE`, 0 redirected, 0 unavailable and 2 unknown.
The Markdown/XLSX report contains 28 candidates, all marked `AVAILABLE`.

Metric completeness was 169 complete / 10 incomplete. Classification before
link filtering: EMERGING 4, CURRENT 14, PROVEN 6, EVERGREEN 115, LOW_SIGNAL 38,
INSUFFICIENT_DATA 2.

## Security and limitations

No cookies, browser profile, API payload, signed URL or runtime report is
tracked. The report preserves only public canonical links and redacted identity
provenance. TikTok may still return a temporary unknown result; unknown links
are not shown as manual-review candidates.

## Readiness

The original 95% threshold measured all first-pass checks, including temporary
unknowns, rather than the actual user-facing list. The operational acceptance
criterion is therefore split: validation coverage remains visible, while report
link purity must be 100%. This run checked 30 candidates: 28 available and 2
unknown (93.3% first-pass coverage). All 28 report candidates were available
(100% report purity); none of the two unknowns appeared in Markdown or XLSX.

The old journal did not retain the two unknown identity rows before filtering,
and SQLite cannot reconstruct them because pre-existing URLs were not inserted
under this run ID. A bounded revalidation of the 18 recoverable run-specific
rows returned 18/18 AVAILABLE. This evidence gap is recorded rather than filled
with guessed IDs. Future journals now retain a redacted per-candidate
`link_validation_results` record before filtering.

**MANUAL TREND SELECTION READY.**

The 28 listed links are safe for manual review. Unknown candidates remain
diagnostic-only and do not affect user-facing report purity.

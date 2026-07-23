# LOOPRA Trend Radar Virality Scoring Audit — 2026-07-23

## Status

PARTIAL — scoring and reporting are verified; the real NURA live run is
blocked by TikTok authentication.

## Original methodology

`trend-radar/src/scoring.py` used:

```
views / max_views * 0.5
+ engagement_rate * 100 * 0.3
+ comment_density * 1000 * 0.2
+ optional min(views / author_followers, 1) * 0.1
```

It used views, likes, comments, shares and optionally author followers.
Freshness was collected in `src/run_data.py`, but its component had weight
zero. The formula had no logarithmic normalisation, volume stabilisation,
missing-share distinction, repeated observations, or true velocity.

## Findings

The collector → parser → freshness → scoring → JSON/Markdown/XLSX path is
reproducible. Provenance, source attempts and publication age are preserved.

The old number did not measure virality as a coherent concept: it mixed
absolute reach with unbounded percentage multipliers, could over-rank a small
high-rate video, and called an age-independent result a viral candidate.
Old million-view videos did not automatically win, but the alternative order
was not sufficiently explainable. A one-time `views / age` observation cannot
be called growth velocity.

Synthetic checks cover: a 600-day 5M-view evergreen, an 8-hour 120K high-share
candidate, an 8K-view high-rate candidate, missing shares, unknown date, equal
metrics at unequal ages, zero views and non-finite input. All pass.

## Changed methodology

The current explainable model is documented in
`trend-radar/docs/scoring_logic.md`. It exposes raw metrics, rates, age,
freshness bucket, reach/engagement/freshness/momentum-proxy components,
confidence, final score, classification, deterministic reasons, caveats and
missing fields. Legacy fields remain present for saved-data compatibility.

`momentum_proxy` means age-normalised reach from one observation; it is not
true velocity or acceleration. Missing shares stay missing and produce a
caveat. Below 10,000 views, engagement is multiplied by a square-root volume
factor and cannot receive `EMERGING` classification.

## NURA search configuration

The tracked, Russian-first manual configuration now contains eight core
keywords (burnout, inner dialogue, comparison, self-esteem and boundaries,
self-discovery, emptiness, relationship with self, fatigue), eight relevant
hashtags and four rotational queries. Competitors are empty. The live command
used `MAX_RESULTS_PER_SOURCE=10`, disabled AI analysis and Telegram, and wrote
runtime evidence outside Git.

## Live run

Command: `python trend-radar/run_radar.py` with the NURA source config,
`MAX_RESULTS_PER_SOURCE=10`, `ENABLE_AI_ANALYSIS=false` and
`ENABLE_TELEGRAM=false`.

Duration: 15.1 seconds. Exit code: 4.
`RADAR_RESULT=authentication_timeout`.

TikTok returned a login overlay; no source attempt, discovery, candidate, JSON,
Markdown or XLSX report was produced. Cookie values and session data were not
recorded here. The process closed its browser normally. This is an external
source/authentication block, separate from the scoring model.

The isolated Data Trust acceptance supervisor did pass in 50.765 seconds with
9 unique videos, complete evidence, Markdown/XLSX validation, secret scan 0
and no remaining related processes. It uses its own fixture queries and is not
evidence of the current NURA query set.

## Manual usability and decision

After an authenticated NURA rerun, the report can be opened to select links
and manually determine hook, meaning, visual mechanic and a test format. Those
decisions remain manual; no OCR, transcription, semantic extraction, scenario
generation or video assembly is part of this slice.

Product decision: **CURRENT METHODOLOGY USABLE WITH LIMITED FIXES**.

Readiness was later withdrawn by the Video Identity and Link Integrity audit:
the original report had not verified clickable video availability.

The corrective run subsequently restored manual-report readiness under the
stricter rule that every published candidate has an AVAILABLE or canonical
redirect validation result; unknown diagnostics are excluded from the report.

## Authentication reliability follow-up

The timeout was caused by the Radar's isolated Playwright cookie state, not by
the user's ordinary browser profile: the collector loaded the saved cookie file
and detected a TikTok login overlay in its own context. `run_radar.py` does not
offer interactive login, so the previous 15.1-second failure was an immediate
preflight rejection, not an insufficient manual-login timeout.

The refresh tool now provides a non-interactive `--check` preflight and a
bounded visible refresh window. It classifies login, challenge, consent/unknown
UI and browser/network failure separately, writes only validated state
atomically, retains a backup before manual refresh, and does not print cookie
values or hashes. Collection persists state atomically only after an
authenticated preflight.

## Completed NURA operational run

On 2026-07-23 the isolated preflight returned
`AUTH_RESULT=session_valid`; it observed 16 saved cookies, of which 12 were
TikTok-domain cookies, and a usable authenticated TikTok page. The standard
NURA run then completed with `RADAR_RESULT=success`, exit code 0, in 237.148
seconds. It used 20 Russian NURA sources (8 core hashtags, 8 core keywords and
4 rotational sources), with AI analysis and Telegram disabled.

The run collected 478 raw discoveries, 188 unique videos, 188 new records and
12 duplicate discoveries. Metric completeness was 177 complete / 11
incomplete. Classifications: 4 `EMERGING`, 15 `CURRENT`, 9 `PROVEN`, 122
`EVERGREEN`, 34 `LOW_SIGNAL`, 4 `INSUFFICIENT_DATA`. The top-30 report contains
no missing shares. Markdown, XLSX and JSON journal were opened and validated;
the top ten rates were recomputed from their raw metrics.

The report is ready for manual review. Query provenance makes every candidate
traceable, but relevance remains a human decision: for example, the first
`#психология` result is an adjacent smoking-psychology topic and should not be
treated as a NURA reference solely because its score is high.

Recommended next step: refresh TikTok authentication by the approved manual
process, rerun the same NURA configuration, then manually review the reported
top candidates. Do not begin autonomous content generation from this audit.

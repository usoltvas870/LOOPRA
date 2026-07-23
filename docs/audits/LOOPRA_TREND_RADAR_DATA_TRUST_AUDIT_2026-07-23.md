# LOOPRA Trend Radar Data Trust Audit — 2026-07-23

## Status

PASS. The authenticated live acceptance completed normally on 2026-07-23.

## Implemented model

Each run records structured source attempts and a many-to-many provenance record between the run, sources, and canonical videos. `videos` remains deduplicated; JSON journals and SQLite retain overlap evidence. TikTok `createTime` is normalized to UTC when present. Freshness is emerging (≤72h), current (≤14d), recent evergreen (≤90d), historical evergreen, or unknown. Existing score weights are not changed; reports expose their breakdown and separate current candidates from evergreen references.

## Timeout and completion diagnosis

The original 64-second supervisor limit was too short for the unoptimized
three-source path and did not prove a hang. Cookie validation took about 11
seconds. The old collector then spent roughly 24 seconds on the first source,
including scrolling after API interception had already returned 30 items, plus
3–6 second inter-source sleeps. Optional detail-page enrichment can add up to
about 21 seconds per video.

The collector now skips scrolling when the intercepted API result already meets
`MAX_RESULTS_PER_SOURCE` and omits the sleep after the final source. Raw result
counts remain observable while only the requested three items are parsed into
the run. The acceptance harness uses 300 seconds because the worst normal path
can include navigation fallback and enrichment; it does not treat report
creation as completion.

## Completion semantics

Exactly one `RADAR_RESULT` is printed. `success` returns 0; `authentication_timeout` returns 4. Login overlays are not bypassed or awaited interactively.

## Live acceptance

- Evidence: `trend-radar/data/evidence/data_trust_acceptance_20260723_125407/`
- Timeout: 300 seconds; timeout flag: false.
- Wall-clock duration: 54.187 seconds.
- Application duration: 52.488 seconds.
- Collection: 51.182 seconds; browser shutdown: 0.662 seconds; export: 0.632 seconds.
- Sources: three planned and three successful API attempts.
- `hashtag/матрицасудьбы`: raw 30, parsed 3, duration 11.764 seconds.
- `hashtag/numerology`: raw 30, parsed 3, duration 10.107 seconds.
- `keyword/предназначение по дате рождения`: raw 15, parsed 3, duration 5.965 seconds.
- Unique discoveries: 9; within/cross-source duplicates: 0.
- Existing in SQLite: 7; new videos: 2.
- Freshness: emerging 1, current 2, recent evergreen 0,
  historical evergreen 6, unknown 0.
- Cross-source overlap: 0, which is valid for this sample; the provenance
  structure was populated for all nine canonical videos.
- Markdown, XLSX, JSON journal, provenance JSON, stdout, stderr, process
  metadata, sanitized configuration, and assertions were created and validated.
- Final result: `RADAR_RESULT=success`; exit code 0; termination reason
  `normal_exit`.
- Cleanup: no acceptance-related Python, Node, Playwright, Chrome, or Chromium
  process remained. Ordinary user Chrome was not targeted.
- Security scan: no cookie values, authorization headers, session identifiers,
  `msToken`, API keys, or secret environment values were found. The cookie file
  was referenced in place and not copied.

The first supervised attempt after implementation exposed a local SQLite
placeholder mismatch after successful collection/export. A focused regression
test now proves the 22-column source-attempt shape before the successful retry.

## Ranking interpretation

Final Score remains a quality-weighted score, not a freshness claim. Normalized
reach contributes 0.5, engagement 0.3, comment density 0.2, and capped viral
ratio up to 0.1. This explains why a smaller video with stronger relative
engagement can rank above a 6.7M-view video. Freshness has weight zero and is
shown separately: only emerging/current videos are current trend candidates;
older successful videos are evergreen format references.

## Limits and readiness

The radar still analyses metadata/captions rather than video content. Real TikTok access may be blocked or require a manually refreshed session; that outcome is PARTIAL, never PASS. The next gated slice, only after a successful acceptance, is Selected Video Format Inspection.

Readiness decision: **DATA TRUST SLICE ACCEPTED.**

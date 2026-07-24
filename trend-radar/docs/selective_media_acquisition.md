# Selective Local Media Acquisition

## Scope

Stage 3A accepts an already validated canonical Trend Radar selection manifest
and registers only explicitly selected, operator-provided local media files.
It does not open TikTok, use cookies, launch a browser, resolve media URLs, or
perform HTTP downloads.

## Boundary

`selection_manifest` → ordered manifest entries → local-file acquisition →
ignored run-scoped media and `acquisition_record.json`.

Candidate selection is restricted to manifest entries, preserves their manifest
order, and is capped at five candidates. The record contains technical facts:
candidate identity and rank, canonical source page, method, timestamps, media
size, SHA-256, ffprobe facts, warnings/errors, and manifest reference/hash.
It does not contain cookies, authentication headers, browser state, OCR, speech
transcription, AI analysis, or production assessment.

## Local CLI

```powershell
python acquire_media.py --selection-manifest data/runs/selection_manifest_<run>.json `
  --candidate-id <video-id> --local-file <video-id>=C:\path\to\video.mp4
```

Runtime defaults to `data/acquisitions/`, which is ignored by Git. Media is
copied through a `.part` file, finalized atomically, validated with `ffprobe`,
and hashed only after finalization. A valid run-scoped record and matching file
are reused on a later identical request.

## Browser-bound response capture (Stages 3C–3D)

Stage 3C adds a separate, bounded `authenticated_browser_response` adapter.
It accepts the same canonical selection manifest, defaults to rank 1, and can
only select an explicit video ID already contained in that manifest. It opens
the candidate's canonical page in an existing Playwright cookie-state, observes
one qualifying TikTok `video/mp4` response, and obtains that response body
through Playwright. It does not export cookies, auth headers, storage state, or
the signed media URL to a standalone HTTP client.

```powershell
python capture_browser_media.py --selection-manifest data/runs/selection_manifest_<run>.json
```

The browser capture output is `data/acquisitions/<run-id>/<video-id>/`. The
adapter writes `browser_source.mp4` via `.part` plus atomic replacement and a
redacted `acquisition_record.json`. The record has only allowlisted technical
facts: manifest identity, candidate rank, response status/type/length/range
metadata, redacted URL host/path, URL hash, captured byte count, media hash,
and ffprobe facts. A valid matching artifact is returned as `REUSED` without
starting a browser. Corrupt artifacts are not reused.

Stage 3D hardens this adapter into a bounded acquisition run. The CLI defaults
to the first five manifest entries, or accepts up to five unique
`--candidate-id` values; both paths preserve manifest rank order. It never
accepts an arbitrary TikTok or media URL. Candidates are processed sequentially
in one authenticated Playwright context, with a fresh page and response listener
for each candidate. A candidate failure is recorded and does not discard later
successes.

Each run writes an atomic UTF-8 JSON summary at
`data/acquisitions/<run-id>/browser-acquisition-*.json`. It contains portable
candidate references, concise status snapshots, hashes and ffprobe facts; it
never serializes cookie values, auth headers or signed URL queries. `COMPLETED`
means every selected candidate completed or reused; `PARTIAL` means at least one
usable artifact and a failure; `FAILED` means no usable artifact. CLI exit codes
are 0, 2 and 1 respectively.

Before browser launch, matching records, hashes and ffprobe output are checked.
Valid artifacts return `REUSED`; resume retries only unfinished candidates.
Corrupt artifacts are not reused. This is not automatic TOP-20 acquisition or a
standalone downloader; OCR, transcription, AI analysis and production adaptation
remain outside this boundary.

The real acceptance used manifest run `20260724_150816`, rank 1, video ID
`7665636437601094933`. Playwright returned the complete HTTP 200 response body:
668220 bytes matching `Content-Length`, with media SHA-256 prefix
`2fed0aba600ef748`. `ffprobe` confirmed an MP4/H.264 video stream at 1024x576,
20.176009 seconds, with optional audio present. The existing Format Inspection
also passed with 15 sampled frames, six estimated scenes, and
`mostly_static=false`. A subsequent invocation returned `REUSED` from the
validated local artifact without starting a browser.

### Stage 3D real acceptance (2026-07-24)

The bounded run used the same manifest, hash prefix `8ed5faca1422`, and ranks
1–5 only. Rank 1 was reused; ranks 3 and 5 were newly captured as valid
MP4/H.264 artifacts (565471 bytes / 6.266667 seconds and 228388 bytes /
7.633333 seconds). Ranks 2 and 4 loaded authenticated candidate pages but
produced no qualifying complete `video/mp4` response; both were recorded as
isolated failures and processing continued. The result was `PARTIAL` with three
usable artifacts. Resume reused ranks 1, 3 and 5 and retried only ranks 2 and 4.

Existing Format Inspection passed for newly captured rank 5. The unchanged
inspector failed for rank 3 at a rounded-duration frame boundary; that is a tool
limitation, not an acquisition failure. No OCR, transcription, AI analysis,
scoring, ranking or automatic TOP-20 acquisition was performed.

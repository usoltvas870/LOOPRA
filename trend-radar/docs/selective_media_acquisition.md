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

## Stage 3L — Page-context range replay integration (2026-07-24)

The browser acquisition keeps `authenticated_browser_response` as its primary
path. A separate production `authenticated_page_range_replay` adapter is used
only when that path sees an allowlisted large (8–40 MiB) HTTPS TikTok
`video/mp4` response with `Accept-Ranges: bytes` and the in-page body is
unavailable or times out. Small complete responses never enter this fallback.

The signed URL remains in the live candidate page only. Each range request uses
the page's native `fetch` with `credentials: include`; the adapter does not
construct `Cookie` or `Authorization` headers, export browser state, retain raw
headers, or serialize URL/query values. It verifies start/middle/end/repeated
start ranges before assembly, then streams 256 KiB sequential ranges through
bounded 64 KiB page-to-Python fragments. The Python side selects the `.part`
path, checks fragment ordering and exact byte totals, hashes incrementally,
cleans partial output on every failure, atomically finalizes the MP4, and
requires a valid ffprobe video stream. Audio remains optional.

`acquisition_record.json` records the method, relative local path, byte count,
SHA-256, ffprobe facts and the range chunk count. It does not include signed
URLs, cookies, credential headers, raw headers, fragments, bodies, OCR,
transcripts or AI output. Valid artifacts of either browser method pass the
same manifest/hash/path/ffprobe validation and return `REUSED` without opening
a browser.

Real acceptance used canonical manifest `20260724_150816` (hash prefix
`8ed5faca1422`) and ranks 1–5 only. Rank 2 completed through page-range replay:
35,521,949 bytes, SHA-256 prefix `c357a9b2`, H.264/AAC, 576×1024,
461.466667 seconds. Its immediate second run returned `REUSED`. Rank 4 first
reported the isolated `RANGE_FETCH_PYTHON_TIMEOUT`, then completed on resume
through the same method: 22,295,510 bytes, SHA-256 prefix `139c4a7d`, H.264/AAC,
576×1024, 639.733333 seconds. The initial five-candidate run was `PARTIAL` with
four reusable artifacts; resume retried only rank 4 and completed all five. A
following run returned 5/5 `REUSED` without browser/network work.

The existing Format Inspection tool was invoked for the long rank-2 artifact.
It produced partial runtime evidence but failed its terminal-duration frame
sample; this is separate from ffprobe acquisition validity and no inspector
algorithm was changed. Automatic TOP-20 acquisition, OCR, transcription, AI
analysis, Content Intelligence Cards and NURA adaptation remain unimplemented.

### Stage 3E response-selection hardening (2026-07-24)

For a failed manifest candidate, the adapter now records bounded page facts and
redacted observations for media-shaped responses: observation order, URL hash,
host/path without query values, query parameter names, status, MIME, declared
size, range metadata, resource type and explicit rejection codes. It never
serializes bodies, cookies, headers, storage state or signed URLs. A page's
video-element count, source kind (`blob`, `network` or `empty`) and safe player
state are recorded; the first video may be activated once only when no selected
response was observed.

The only selector change is an evidence-driven maximum complete-file size of
40 MiB. The original 8 MiB ceiling rejected the complete, allowlisted HTTP 200
`video/mp4` responses for rank 2 (35,521,949 bytes) and rank 4 (22,295,510
bytes), despite both pages having one blob-backed video player. Host validation,
HTTPS, exact HTTP 200 requirement, `video/mp4` MIME, declared length, MP4
signature, ffprobe, one-artifact policy and rejection of HTTP 206 range
responses are unchanged. The 206 `video/mp4` login-static response remains
rejected as an unsupported host/range response.

On the same bounded diagnostic run, both newly selected full MP4 responses
reported `BODY_UNAVAILABLE` when Playwright was asked for their body after the
network observation. Therefore they remain failed acquisitions: no MP4 was
written and the result remains three usable artifacts out of five. This is a
precise browser-body retrieval gap, not a reason to accept range fragments,
replay signed URLs or relax host/MIME validation.

Stage 3E therefore closes as `PASS WITH GAPS`: range capture, standalone
downloading and automatic TOP-20 acquisition are not implemented, and OCR,
transcription and AI analysis remain prohibited until at least four of the five
selected candidates have usable media.

## Stage 3I — Range consistency diagnostic

Stage 3I adds an isolated `diagnose_tiktok_ranges.py` helper; it is not wired
into browser acquisition or multi-candidate orchestration. It obtains the
already-observed media URL only in the active page's memory, issues bounded
page-context range fetches, and persists only allowlisted diagnostic fields.
It never writes signed URLs, query values, cookies, headers, HTML, or chunk
bodies.

The rank-2 diagnostic on 2026-07-24 requested `bytes=0-16383` and received
HTTP 403 with a non-video-sized 504-byte response. Consequently start/middle/
end/repeat consistency and the browser-to-Python transfer bridge are **not
proven**, and full assembly was not run. This is a current replay rejection,
not evidence that the earlier successful 206 probe is invalid or that the
signed URL has a single known failure cause.

The same page-context helper did prove controlled cancellation: a 1 ms
browser-side `AbortController` returned `RANGE_FETCH_BROWSER_TIMEOUT` before
the 12-second Python guard, and the page remained usable. When cancellation
occurred before a `ReadableStream` reader existed, evidence explicitly records
`reader_cleanup: not_started` rather than claiming a reader was cancelled.

## Stage 3J — Fresh media URL and range-session diagnostic

Stage 3J adds the separate `diagnose_tiktok_range_session.py` helper and
`range_session_diagnostics.py` module. They are diagnostic-only and do not
change browser capture, local acquisition, or multi-candidate orchestration.
The listener is installed before navigation and retains each signed URL only in
memory. The evidence contains a response generation, URL age and a short hash
prefix, never the URL, query values, cookies, headers, or a response body.

On 2026-07-24, rank 2 produced `RANGE_FETCH_FORBIDDEN` for the immediate
fresh-response default fetch (URL age approximately 5,250 ms), after reload
with a new response generation (approximately 5,516 ms), and after pausing the
player (approximately 5,625 ms).
The bounded page-native variant then returned HTTP 206 `video/mp4` for
`bytes=0-16383`, with `Content-Range: bytes 0-16383/35521949` and a 16,384-byte
body at URL age approximately 5,719 ms. That variant uses browser-native safe
semantics only: `credentials: include`, `cache: no-store`, redirects, and the
current document as referrer; it never supplies `Cookie` or `Authorization`
headers.

This proves that freshness alone, reload and the observed playing/paused state
did not resolve the 403 in this run, while one concrete safe page-context fetch
configuration did. It does not yet isolate the minimum individual option that
is required, nor prove repeatability of 206. Therefore consistency probes,
stream bridge and full MP4 assembly were **not run**. Controlled cancellation
still passed and the page remained usable. The usable count remains 3/5; the
five-candidate acquisition and OCR gates remain closed. The next bounded
decision is Stage 3K — Page-Context Range Replay Hardening.

The existing authentication helper reads the Playwright storage-state file in
Python to create the browser context. Cookie values are not printed or included
in diagnostic output, and no `Cookie` or `Authorization` header is constructed
or passed manually to the range fetch. Automatic TOP-20 acquisition, OCR,
transcription and AI analysis remain unimplemented. The separate rank-3 Format
Inspection duration-rounding gap is unchanged.

### Stage 3F targeted player-network diagnostic (2026-07-24)

The browser adapter now starts at most three bounded lifecycle tasks directly
from qualifying `response` events. Each task waits for `response.finished()`
for at most 30 seconds, then requests `response.body()` while the candidate
page and authenticated context are still open. The task is awaited before the
listener is removed and the page is closed. Diagnostics retain only redacted
lifecycle timestamps, response metadata, body status and a redacted exception
class/message; they do not retain response bodies, headers, cookies or signed
URLs.

Real rank 2 (35,521,949 bytes) and rank 4 (22,295,510 bytes) both produced a
complete, allowlisted HTTP 200 `video/mp4` response but timed out waiting for
`response.finished()` after 30 seconds. `response.body()` was therefore never
called. This rules out late page cleanup as the observed `BODY_UNAVAILABLE`
cause and classifies both responses as active player-bound streaming resources.
Neither response came from a service worker. No MP4 was saved; ranks 1, 3 and
5 remain the only reusable artifacts, so the run remains `PARTIAL` (3/5).

Context-bound replay, route interception and CDP capture were not attempted in
this stage. They require a separate Stage 3G design decision. The 40 MiB limit,
host/MIME validation, rejection of HTTP 206 ranges, manifest-only selection and
the prohibition on OCR, transcription, AI analysis and automatic TOP-20
acquisition are unchanged.

## Stage 3M — Format Inspection long-video policy (2026-07-24)

Format Inspection remains an offline consumer of an already validated local
artifact; it never changes acquisition validity, records, selection, or reuse
semantics. Its canonical duration source is `ffprobe` `format.duration`. The
old sampler rounded a uniform terminal timestamp to milliseconds, so rank 2's
`461.466667` seconds became `461.467` and rank 3's `6.266667` seconds became
`6.267`: both are outside the decodable timeline and FFmpeg emitted an empty
image. Seeking after input also made each long-video attempt decode from the
start.

The inspector now produces a deterministic, deduplicated plan that is strictly
inside the media duration, with a 50 ms terminal margin after millisecond
rounding. FFmpeg seeks before input, each frame has a 20-second subprocess
limit, and the inspection has a 180-second total limit. A failed terminal frame
is retried once at an earlier valid timestamp. Per-frame requested/effective
timestamps, retry count and classified failures are retained in `inspection.json`.
Successful frames alone feed the contact sheets and metrics. All frames gives
`COMPLETED`; at least three successful frames gives `DEGRADED`; fewer gives
`FAILED`, with unavailable metrics recorded as `null` and warnings rather than
invented values. OCR, transcription and AI analysis remain unavailable.

On the existing canonical run `20260724_150816`, all acquisition artifacts
remained unchanged and all five inspections completed: rank 1 (20.176009 s,
15/15 frames), rank 2 (461.466667 s, 16/16), rank 3 (6.266667 s, 11/11), rank
4 (639.733333 s, 16/16), and rank 5 (7.633333 s, 12/12). All have sampled-frame
evidence and an audio-stream fact. The run took 4.25, 5.406, 3.657, 5.922 and
4.406 seconds respectively; no retry or partial status was needed.

The Target closed report was not reproduced by this offline work. Code audit
confirms the current browser capture awaits every bounded body task both before
selection and in `finally`, removes the response listener, and only then closes
the page; no browser lifecycle change was justified. A five-artifact OCR input
gate is therefore open for a separately approved Stage 4A, but OCR/STT/AI and
automatic TOP-20 capture are not implemented by this stage.

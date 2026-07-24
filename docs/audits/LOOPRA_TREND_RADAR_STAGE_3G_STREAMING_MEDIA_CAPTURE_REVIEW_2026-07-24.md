# Trend Radar Stage 3G — Large Streaming Media Capture Architecture Review

## Status

PASS WITH GAPS.

Stage 3G confirms the installed Chromium/Playwright capability surface and
makes an evidence-only architecture decision.  It does not add a production
adapter, acquire a new artifact, or start Stage 3H.

## Evidence classification

- **FACT:** Stage 3F observations, the persisted redacted acquisition facts,
  and the local Playwright/Chromium capability probe described below.
- **INFERENCE:** rank 2 and rank 4 behave as active player-bound streams for
  which the standard `Response.finished()` then `Response.body()` path is
  unsuitable.
- **RECOMMENDATION:** investigate isolated range-aware replay in a separate
  Stage 3H proof.  Range replay, credential propagation, signed-URL stability,
  and end-to-end media reconstruction are not proven in Stage 3G.

## Baseline

- Branch and starting HEAD were recorded from the local repository before this
  review; the pre-existing worktree state is preserved.
- Python: 3.11.9 on Windows 10.
- Playwright: 1.60.0.
- Chromium: HeadlessChrome 148.0.7778.96 (CDP protocol 1.3).
- `ffmpeg` and `ffprobe` are available on PATH.

## Confirmed problem

For the canonical manifest run `20260724_150816`, rank 2 has a qualifying
HTTP 200 `video/mp4` response with declared length 35,521,949 bytes.  It is
HTTPS, comes from an allowlisted host, is not service-worker produced, and is
below the existing 40 MiB ceiling.  The Stage 3F lifecycle task waited 30
seconds for `Response.finished()` and received `TimeoutError`; consequently,
`Response.body()` was not called.  Rank 4 has the same observed lifecycle
class.

This removes page close, context close, listener timing, and delayed
`Response.body()` invocation as explanations for the recorded failure.  The
ordinary Playwright `Response.finished()` then `Response.body()` model is not
appropriate for these active player-bound responses.

Rank 2 also supplied two useful range facts without retaining its signed URL:
the full response advertises `Accept-Ranges: bytes`, and a later response was
HTTP 206 with `Content-Range` ending at the same 35,521,949-byte total.

## Local API capability audit

| API/mechanism | Installed support | Body before normal finish | Stream-to-disk | Session reuse | Main limitation |
| --- | --- | --- | --- | --- | --- |
| CDP `Fetch` + `IO` | Confirmed: `Fetch.enable` at `Response` stage, `takeResponseBodyAsStream`, `IO.read`, `IO.close`, `continueResponse`, `continueRequest`, and `fulfillRequest` all exist | Yes, while request is paused | Yes, chunked reads to a `.part` file are possible | Yes, inside the existing browser context | After `takeResponseBodyAsStream`, the original response cannot be continued as-is and must be cancelled or replaced; it is Chromium CDP, not a Playwright streaming API |
| Playwright `route.fetch()` | Available | No useful streaming boundary | No; it returns `APIResponse` | Browser route context | Fetch/body handling is whole-response buffering and requires route fulfil/continue lifecycle handling |
| `BrowserContext.request` | Available | No useful streaming boundary | No; `APIResponse.body()` is buffered | Context-native cookie store | Bounded at 40 MiB but still needs a replay and whole-body memory |
| Browser `fetch()` + `ReadableStream` | Web API available | Potentially | No safe native bridge to local disk | Yes, if same authenticated page can fetch | Cross-origin/CORS and host-bridge copying/back-pressure are unproven; browser cannot atomically write the local `.part` |
| Browser cache/temp files | No public supported extraction API found | N/A | Not reliably | N/A | Cache layout and temporary files are implementation details |
| Player-native download | No native path evidenced | N/A | Browser-managed only | Yes | Current player source is `blob:`; no supported download-event path was observed |

The capability probe used a fresh local Chromium page only.  It did not
navigate to TikTok, read cookie values, print headers, or serialize any URL.

## Architecture decision matrix

| Option | Suitability | Decision |
| --- | --- | --- |
| A. CDP response stream interception | Technically capable of bounded chunked capture before normal completion, exact byte counting, SHA-256, atomic write, and later ffprobe.  It can be tightly scoped to one HTTPS allowlisted response. | Rejected for the current player request: after taking the response stream, the original response cannot continue as-is and must be cancelled or replaced, so the mechanism can disrupt the player lifecycle. |
| B. `route.fetch()` / `APIResponse` | Auth-adjacent but whole-response buffered and not a streaming-to-disk design. | Rejected. |
| C. Context-bound `APIRequestContext` replay | Keeps cookie use inside Playwright and avoids manual Cookie/Authorization export, but has no public streaming response reader. | Not selected; may be a bounded replay control only. |
| D. Browser-side Fetch/ReadableStream | Could expose chunks only through an additional host bridge; CORS, copies, back-pressure, and atomic local persistence remain unresolved. | Rejected as a safe proof mechanism. |
| E. Browser cache or temporary file | No supported public extraction contract. | Rejected. |
| F. Network range-aware reconstruction | Rank 2 has positive range evidence.  A future isolated request can use a generated `Range` header, keep the observed URL in process memory only, and avoid interrupting the active player request. | Recommended next architecture hypothesis, subject to a separate Stage 3H proof. |
| G. Native player download | No download capability is evidenced for the blob-backed player. | Rejected. |

## Selected architecture

The selected next decision is **STAGE 3H — RANGE-AWARE MEDIA CAPTURE**.  This
is not a production-ready adapter and no Stage 3H implementation is included
here.

The future proof must create one isolated, manifest-bound range request in the
already authenticated Chromium context, never export cookies or manually copy
`Cookie` or `Authorization` headers, retain the signed URL only in process
memory, and use a generated `Range` header rather than a copied secret header.
It must prove which session data, if any, Chromium supplies automatically; no
such propagation or signed-URL stability is assumed here.  If it uses CDP
`Fetch` plus `IO` to stream chunks, the intercepted request must be the
isolated replay, never the player’s live response.  This isolates the response
replacement/cancellation semantic from the page/player lifecycle.

The future contract must retain the existing 40 MiB ceiling, one selected
manifest candidate, HTTPS and host allowlist enforcement, MIME validation,
`.part` cleanup, atomic finalization, SHA-256, ffprobe, bounded timeout, and a
redacted proof record.  Raw headers, signed URLs, and query values must not be
serialized.  It must reject unexpected range semantics, missing stable total
size, duplicate/overlapping chunks, incomplete reconstruction, HTML, redirects
outside the allowlist, and any response that requires exporting credentials.

## Bounded proof

No rank-2 runtime capture was run in Stage 3G.  The only locally confirmed
streaming method for a live paused response is CDP
`Fetch.takeResponseBodyAsStream`; after taking the stream, the original
response cannot continue as-is and must be cancelled or replaced.  Running it
against rank 2 could interrupt the observed player request and would not be a
safe proof of the requested non-disruptive architecture.

Therefore captured bytes, chunk count, SHA-256, ffprobe, and Format Inspection
are not applicable in this stage.  No runtime MP4 or temporary proof artifact
was created.

## Implemented contract

None.  Stage 3G creates no production adapter, does not change the collector,
authentication foundation, scoring, ranking, reports, manifest, local-file
acquisition, multi-candidate orchestration, Format Inspection, core, or comic
and production pipelines.  It does not implement automatic TOP-20 acquisition,
OCR, transcription, or AI analysis.

## Security

This review did not print or export cookies, manually copy Cookie or
Authorization headers, serialize raw request or response headers, serialize
browser storage state, retain a full signed URL or query values, serialize a
response body, or create an MP4.  The existing cookie-state files, acquisition
runtime directory, and MP4 artifacts are ignored by Git.

## Acquisition gate and limitations

- Usable candidates remain 3/5 (ranks 1, 3, and 5 reused).
- Rank 2 was not captured in this stage; rank 4 was not retested.
- The five-candidate acquisition gate is not passed.
- The OCR gate is not passed.
- The existing rank-3 Format Inspection duration-rounding gap is unchanged.
- The range reconstruction hypothesis still needs a separate, bounded proof;
  no claim is made that the acquisition layer is ready.

# LOOPRA Selected Video Format Inspection Audit — 2026-07-23

## Status

FORMAT INSPECTION SLICE ACCEPTED.

## Executive summary and acquisition decision

The bounded baseline is an explicitly selected, user-provided local MP4. The inspector is offline and independent of TikTok acquisition. It neither downloads media nor automates login, OTP, CAPTCHA, DRM bypass or browser evasion. The fallback is `trend-radar/media-inbox/`, ignored by Git.

## Capability audit

| Group | Result | Decision |
| --- | --- | --- |
| FFmpeg/ffprobe | 8.1.1 installed | metadata, frames and fixture generation |
| Pillow + NumPy | installed | contact sheets and explainable frame metrics |
| Playwright | installed and used by Radar collection | no role in local inspection |
| faster-whisper | importable, no verified local model | no automatic model download |
| OpenCV, yt-dlp, pytesseract | absent | not required |
| OCR/transcription/face detection | not validated | explicit unavailable/manual review |

## Implemented schema and pipeline

`trend-radar/inspect_video_format.py` produces a versioned `inspection.json` with identity/hash, ffprobe media facts, explainable sampled-frame scene/static metrics, audio-stream facts, evidence paths, confidence boundaries and manual-review requirements. It also creates Markdown, ffprobe JSON, scene metrics, frames, three contact sheets and `process_result.json`. Measured facts, heuristics and semantic interpretation are distinct; the last is intentionally not automated.

The handoff is filesystem-only: selected Radar record metadata supplies `--video-id` and optionally `--canonical-url`; local media supplies `--input`. No collector, Radar schema or ordinary run behaviour changes.

## Real-world acceptance sample

Five manually downloaded TikTok references were compared with one
LOOPRA-generated nine-scene NURA comic. All inputs had an MP4 `ftyp` signature,
unique SHA-256, successful ffprobe, successful full decode, and unchanged hashes
after inspection. `reference_06.mp4` was also intact but excluded from the
explicit five-reference sample.

| Sample | Bytes | SHA-256 | Preflight |
| --- | ---: | --- | --- |
| `reference_01.mp4` | 349532 | `25610330A6291B8DCAAC9410646E20B1C7EF95172F83E92A8D9BA8357E621798` | PASS |
| `reference_02.mp4` | 739183 | `B1F62FA17BC05EBF7FCE04D2A4924EE6C5FD88ABF9E95542ED38FA52D73BD89A` | PASS |
| `reference_03.mp4` | 15620185 | `8C95F3FAAD12EDAF6DD2C5555DDE98B2BFFF8679CA45A9335CF1676B7F820E3B` | PASS |
| `reference_04.mp4` | 791039 | `A35B3C3AECA385CE2FAE63AF6FC90F0B5F488A835E9D96E292B726A42A15AC76` | PASS |
| `reference_05.mp4` | 713110 | `27A9CC057ECF37D50F72CC697AE7AB7D27DE22BBF8840E4A696B28C308517679` | PASS |
| `nura_comic_01.mp4` | 18727369 | `0FB1F31104220A23E22ED38639DDE65FA5AF0241F4304D35913BCD6E0BE5C4D4` | PASS |

## Automatic results

| Sample | Duration | Scenes | Visual states | Mostly static | Static ratio | First change | Cuts/10s | Motion |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| reference 01 | 15.116s | 2 | 5 | yes | 0.714 | 4.123s | 0.662 | low |
| reference 02 | 14.048s | 2 | 2 | yes | 0.929 | 10.217s | 0.712 | low |
| reference 03 | 71.959s | 1 | 3 | no | 0.000 | 0.500s | 0.000 | high |
| reference 04 | 13.677s | 2 | 4 | no | 0.500 | 3.730s | 0.731 | medium |
| reference 05 | 10.000s | 2 | 3 | no | 0.214 | 0.500s | 1.000 | high |
| NURA comic | 41.340s | 9 | 9 | no | 0.071 | 0.500s | 1.935 | high |

TikTok medians were 14.048 seconds, 2 scenes, 3 visual states, 0.712
cuts/10 seconds, and 3.730 seconds to first visual change. Forty percent were
mostly static, twenty percent were strict one/two-state estimates, and all had
an audio stream. NURA was 27.292 seconds (+194.3%), 7 scenes (+350%), 6 visual
states (+200%), and 1.223 cuts/10 seconds (+171.8%) above the reference medians.

## Visual review and inspector correction

First-second, first-three-second, and full-video contact sheets were reviewed
for every sample. Real media exposed two bounded defects: average-colour state
clustering undercounted text/composition changes, and the original static
threshold misclassified the slowly moving background in reference 04. The
inspector now combines a DCT perceptual hash with colour distance and uses a
calibrated frame-difference threshold. Regression coverage proves continuous
motion is not reported as mostly static. The corrected NURA estimate is nine
states and reference 04 is moving/medium rather than static/low.

Manual visual review confirmed visible text in every sample. References 01,
02, 04 and 05 are short text-led formats; reference 03 is a 72-second exception
using one continuous sea background with many text beats. Only reference 02 is
strictly one/two-state after platform end-card handling. The common production
property is therefore not literal one/two-state membership: it is reuse of one
base background or clip with inexpensive text changes. Audio streams are
measured, but voice, music, spoken words and transcription remain unknown.

## Production complexity proxy

| Dimension | Simple reference format | Current NURA comic |
| --- | --- | --- |
| Base visual assets | low: one background/clip plus text cards | high: nine illustrations |
| Character generation/consistency | trivial/none | high: two recurring characters |
| Edit points | low: median two scenes | high: nine scenes/eight measured cuts |
| Dialogue bubbles | none | high: nine positioned bubbles |
| Composition and synchronization | low | high: ordered scenes, bubbles and audio timing |
| Potential failure surface | low | high: source, character, layout, render, FFmpeg and QA stages |

Exact monetary or manual-time cost is not claimed because the repository does
not provide comparable measured labour data.

## Findings and decision

Measured fact: the selected NURA comic is structurally larger than the TikTok
reference median in duration, scenes, visual states, cuts and required visual
assets. Manual observation: all references use a reusable base visual and text;
some include continuous motion or several text states, so they are not all
literal one/two-frame videos. Working hypothesis: LOOPRA can test a materially
cheaper text-led short-video class without deleting or replacing the comic
pipeline.

This sample cannot prove that simplicity caused views, that simple content is
universally better, or which hook/voice/music mechanism retained viewers. It is
a selected convenience sample without retention data, OCR or transcription.

Product decision: **LEAN SHORT VIDEO PATH JUSTIFIED.**

Readiness decision: **FORMAT INSPECTION SLICE ACCEPTED.**

## Security, runtime evidence, and next slice

Runtime media, frames, contact sheets, ffprobe JSON, manual reviews and
comparative reports remain under Git-ignored `trend-radar/media-inbox/` and
`trend-radar/data/format-inspections/`. The run used no network, cookies,
downloader, signed media URL, OCR model download or transcription model
download.

Recommended next slice: **Content Pattern Foundation**, limited to a reviewed
project-scoped schema derived from confirmed format evidence. It is not started
by this audit.

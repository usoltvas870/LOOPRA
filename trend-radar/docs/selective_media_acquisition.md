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

## Current limitation

Automatic TikTok acquisition is not implemented or confirmed. A future network
adapter requires its own bounded authenticated media-URL-resolution spike.

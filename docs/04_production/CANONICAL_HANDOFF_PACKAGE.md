# Canonical Export/Handoff Package

## Status and scope

LOOPRA 0.5 provides a user-facing, filesystem-only handoff package for a
successfully rendered `DIALOG_MINISERIES` episode. It is a derived view of an
already QA-verified `RenderJob`; it is not a renderer, a second production
pipeline, or a publishing integration.

Internal artifacts remain under `storage/<project_id>/renders/<render_job_id>/comic/`.
The portable operator-facing package is written to:

```text
output/<episode_id>/final/
```

The path is stable for an episode and deliberately does not expose a
`render_job_id` in ordinary operation.

## Contents and stable names

For the current comic contract, the package contains only the outputs actually
produced by the selected target platforms:

```text
output/<episode_id>/final/
├── instagram_carousel/
│   └── frame_01.png ... frame_NN.png    # when Instagram is selected
├── <episode_id>_tiktok.mp4              # when TikTok is selected
├── <episode_id>_youtube_shorts.mp4      # when YouTube Shorts is selected
├── <episode_id>_vk_clips.mp4            # when VK is selected
└── manifest.json
```

Instagram currently means a 1080×1350 contain-adapted carousel. LOOPRA does
not create an Instagram Reels MP4 in this bounded workflow. No master video,
cover, caption, or fictitious platform file is copied into the final package.

Episode IDs are validated by Episode Input Package v1 as lowercase ASCII
letters, digits, `_` and `-`; the handoff names therefore remain Windows-safe.
Each package replaces only its own canonical `final` directory after a fully
validated temporary build. A failed rebuild leaves the previous successful
package untouched.

## Manifest contract

`manifest.json` is the only machine-readable package contract (schema `1.0`).
It contains the episode identity and title, content format, creation time,
source episode and internal manifest SHA-256 digests, technical `render_job_id`,
requested platforms, and every copied artifact's relative path, role,
platform, MIME type, size, SHA-256, and media metadata.

Video entries include dimensions, FPS, duration, H.264 codec, pixel format,
audio presence, and audio codec. A video rendered without a supplied voiceover
or music is marked `silent_technical_track`; it is not described as ready
music. Captions are explicitly `{ "status": "manual_required" }` rather than
an empty pseudo-caption file. The manifest lists the required manual actions:
add native-platform music if desired, write a caption, select a cover if
needed, upload, schedule, and publish.

The package contains no absolute paths. Internal comic frames are render-job
intermediates and are intentionally not copied to the handoff package.

## Production and verification commands

Run from the repository root:

```powershell
python scripts/produce_episode.py --episode input/<episode_id>/episode.json --handoff-output output --json
python scripts/produce_episode.py --verify-package output/<episode_id>/final --json
```

`--handoff-output` defaults to `output`. The production JSON result reports
both the internal `package_root` and the user-facing `handoff_package_root`.
The verifier reads only the existing handoff directory: it checks schema,
paths, exact package file set, required platform roles, checksums, image
metadata, MP4 stream metadata, and a full FFmpeg decode. It exits `0` only on
PASS and does not modify the package.

Expected errors return a concise human message or structured JSON with a
non-zero exit code; they do not emit a traceback in normal operation. Examples
include missing render artifacts, checksum mismatch, extra/partial package
files, corrupt MP4, and unsupported schema version.

## Limits

LOOPRA does not add trend music, create marketing captions or hashtags,
generate covers, upload drafts, schedule or publish, call platform APIs, or
collect platform metrics. Those manual publication actions remain outside this
slice.

# Episode Input Package

## Status and scope

Episode Input Package v1 is the canonical filesystem input for the bounded
`DIALOG_MINISERIES` comic production flow. It turns one `episode.json` into the
existing canonical `ProductionBrief`, validates the complete source package,
and then uses `ProductionPipelineService` to create comic frames, Instagram
slides, platform videos, QA metadata, and the existing package manifest.

It does not implement Trend Radar, publication, Content Ledger, a database,
connectors, captions, hashtags, ZIP export, or image generation.

## Directory structure

```text
input/<episode_id>/
├── episode.json
├── assets/
│   └── optional-package-font.ttf
└── frames/ or assets/
    ├── scene_01.png
    └── ...
```

The folder names below `episode.json` are not special. Every relative image or
font path is resolved against the directory containing `episode.json`.

## Minimal manifest

```json
{
  "schema_version": 1,
  "episode_id": "episode_01",
  "title": "Внутреннее название эпизода",
  "project_id": "nura",
  "content_format": "dialog_miniseries",
  "target_platforms": ["instagram", "tiktok", "youtube_shorts", "vk"],
  "defaults": {
    "duration_sec": 3.0,
    "transition_type": "dissolve",
    "transition_duration_sec": 0.0
  },
  "font": {"path": "system:default"},
  "output": {
    "resolution_width": 1080,
    "resolution_height": 1920,
    "fps": 24
  },
  "frames": [
    {
      "frame_id": "opening",
      "image": "frames/01.png",
      "speaker": "nura",
      "text": "Нура: История начинается здесь.",
      "position": "top_left",
      "tail_anchor": {"x": 0.8, "y": 0.8}
    }
  ]
}
```

The version-controlled executable example is
`tests/fixtures/episode_package/episode.json`.

## Fields and defaults

Episode fields:

- `schema_version` is required and must be integer `1`.
- `episode_id` is required, becomes `ProductionBrief.production_brief_id`, and
  must match `^[a-z0-9][a-z0-9_-]*$`.
- `title` is optional operator metadata; default is an empty string.
- `project_id` is optional and defaults to `episode_id`. It selects the
  existing `storage/<project_id>/` boundary.
- `workspace_id` is optional and defaults to `internal`.
- `content_format` is required and v1 accepts only `dialog_miniseries`.
- `target_platforms` defaults to all four supported package targets:
  `instagram`, `tiktok`, `youtube_shorts`, and `vk`.

Defaults:

- `defaults.duration_sec`: `3.0`, must be greater than zero.
- `defaults.transition_type`: `dissolve`; supported values are `dissolve`,
  `fade`, and `wipeleft`.
- `defaults.transition_duration_sec`: `0.0`, must not be negative.

Platform videos continue to use the immutable existing platform timing and
transition presets. Manifest transitions describe the canonical base scene and
the optional master video; they do not override platform presets.

Font:

- `font.path` defaults to `system:default`.
- `system:default` deterministically checks the documented local candidates:
  Windows Arial, Windows Calibri, Linux DejaVu Sans, then macOS Arial.
- A portable self-contained package should instead provide a relative `.ttf`
  or `.otf` path inside the package.

Output:

- `resolution_width`: default `1080`, positive and even.
- `resolution_height`: default `1920`, positive and even.
- `fps`: default `24`, positive integer.
- `generate_comic_master_video`: default `false`.

Frame fields:

- `frame_id`: required stable identifier, unique in the episode.
- `image`: required package-relative `.png`, `.jpg`, or `.jpeg` file.
- `speaker`: `nura`, `woman`, or `shadow`.
- `text`: required visible text that must fit the current four-line bubble.
- `position`: `top_left`, `top_center`, `top_right`, `middle_left`,
  `middle_right`, `bottom_left`, or `bottom_right`.
- `tail_anchor`: normalized `x`/`y` coordinates from `0.0` to `1.0`. The
  renderer derives the tail side from this anchor and the bubble position;
  there is no separate `tail_direction` field.
- `duration_sec`, `transition_type`, and `transition_duration_sec` optionally
  override the episode defaults.

Frame order is the order of the `frames` array. There is no duplicate sequence
field.

## Path and validation semantics

Relative paths are resolved against the episode directory. Image and packaged
font paths must remain inside that directory; absolute image paths and `..`
traversal are rejected. Before any production render or FFmpeg invocation, the
loader checks:

- JSON syntax, schema version, required and unknown fields;
- IDs, duplicates, content type, platforms, enums, durations, transitions,
  even H.264 dimensions, and normalized anchors;
- missing paths, directories used as files, extensions, empty/corrupt images,
  and fonts;
- the actual current text wrapping, bubble bounds, and tail geometry.

Expected validation failures have no traceback. Human output identifies the
JSON path; JSON mode returns `status`, `error_type`, `manifest`, `message`, and
an `errors` array. Each error has `path`, `message`, `value`, and `allowed`.

Unknown fields are rejected in v1 so misspellings do not silently change an
episode.

## Commands

Run from the repository root.

For the complete public PowerShell setup, validation, production, verification,
platform-upload mapping and user acceptance checklist, start with
`LOCAL_WORKFLOW_QUICKSTART.md`.

Validation only:

```powershell
python scripts/produce_episode.py --episode input/<episode_id>/episode.json --validate-only
```

Machine-readable validation:

```powershell
python scripts/produce_episode.py --episode input/<episode_id>/episode.json --validate-only --json
```

Production:

```powershell
python scripts/produce_episode.py --episode input/<episode_id>/episode.json --handoff-output output --json
```

Verify the resulting user-facing package without rendering again:

```powershell
python scripts/produce_episode.py --verify-package output/<episode_id>/final --json
```

Success exits `0`. Argument errors exit `2`; validation and production failures
exit `1`.

## Runtime and output boundary

The command copies validated source assets to ignored runtime staging under
`storage/<project_id>/episode_runtime/`. It never writes to the source package.
The existing service writes the completed package under:

```text
storage/<project_id>/renders/<render_job_id>/comic/
```

The JSON result reports the exact `render_job_id`, `package_root`, artifact
paths, `handoff_package_root`, and source hashes. `render_job_id` and
`package_root` are technical traceability fields, not locations an operator must
use: hand off only `handoff_package_root` (`output/<episode_id>/final/` by
default). Existing comic output ordering, QA, rollback, and manifest semantics
are unchanged. The derived external package is documented in
`CANONICAL_HANDOFF_PACKAGE.md`.

## Current limitations

- v1 supports only `dialog_miniseries` and one bubble per frame.
- Bubble placement and tail anchors are manual; the tail side is derived.
- Platform timing and transitions are presets, not manifest-defined variants.
- `system:default` is convenient but not visually portable; package a licensed
  font for reproducible typography across machines.
- The existing RenderJob output layout is retained; the separate canonical
  handoff directory is `output/<episode_id>/final/`.

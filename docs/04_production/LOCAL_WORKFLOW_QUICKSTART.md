# LOOPRA 0.5 Local Workflow Quickstart

Status: Current public local workflow
Scope: `DIALOG_MINISERIES` episode package → verified handoff package

This is the start-here guide for creating one local comic episode. It uses the
existing public CLI only. You do not need to read LOOPRA source code, edit
Python files, know a `render_job_id`, inspect `storage/`, or run scratch
scripts.

## What this workflow produces

Starting from `input/<episode_id>/episode.json`, LOOPRA validates the package,
renders it, and writes the user-facing result to:

```text
output/<episode_id>/final/
```

The final directory contains only the platform handoff artifacts and
`manifest.json`. Internal runtime data remains under `storage/` and is not a
manual operating location.

## Prerequisites (Windows PowerShell)

Public acceptance was verified with Python 3.11.9, FFmpeg 8.1.1 and ffprobe
8.1.1 on Windows PowerShell. Use Python 3.11 for this workflow. Python, `ffmpeg`
and `ffprobe` must be available on `PATH`.

From the repository root, create an isolated environment and install the
runtime dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python --version
ffmpeg -version
ffprobe -version
```

If PowerShell blocks local activation, use the documented execution policy for
your organization, or run `.\.venv\Scripts\python.exe` in the commands below.
The production workflow needs no credentials, environment variables, network
access after dependency installation, or editable package install.

For the default font, Windows needs Arial or Calibri installed. For portable,
reproducible typography, include a licensed `.ttf` or `.otf` inside the episode
package and set its package-relative path in `episode.json`.

## First check the CLI

Run this from the repository root:

```powershell
python scripts/produce_episode.py --help
```

Exit code `0` means the CLI is available. The help lists all supported public
modes: `--episode`, `--validate-only`, `--handoff-output`, `--verify-package`
and `--json`.

## Prepare an episode package

Create this structure under the repository root:

```text
input/<episode_id>/
├── episode.json
└── assets/
    └── scene_01.png ...
```

`episode.json` is the canonical input contract. Relative image and font paths
are resolved from its directory; they cannot escape the package directory. See
[Episode Input Package](EPISODE_INPUT_PACKAGE.md) for every field and validation
rule.

For a safe first run, copy the version-controlled fixture without changing it:

```powershell
New-Item -ItemType Directory -Force input | Out-Null
Copy-Item -Recurse tests\fixtures\episode_package input\fixture_episode
```

The fixture includes Cyrillic text and all currently supported platforms. It is
an operational example, not content to publish.

## Validate before rendering

```powershell
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --validate-only
```

This checks JSON, manifest fields, assets, font availability, image integrity,
text layout and package-relative paths. It does not stage assets, invoke the
renderer, FFmpeg or ffprobe.

For an automation-friendly result, write only JSON to stdout:

```powershell
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --validate-only --json
```

You can validate that output with:

```powershell
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --validate-only --json | python -m json.tool
```

## Produce the final package

Run from the repository root so the default `output/` and `storage/` locations
are predictable:

```powershell
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --json
```

On success, the JSON result includes `episode_id`, `status`,
`handoff_package_root` and source hashes. The user-facing path is:

```text
output\fixture_episode\final\
```

To place all final packages below a different root, use a quoted path when it
contains spaces:

```powershell
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --handoff-output "D:\LOOPRA Output" --json
```

That command creates `D:\LOOPRA Output\fixture_episode\final\`. Do not use the
reported internal `package_root` as a handoff location and do not search for
files by `render_job_id`.

## Verify the existing package

Verification reads the final directory without rendering again:

```powershell
python scripts/produce_episode.py --verify-package output\fixture_episode\final --json
```

It verifies the schema, exact file set, checksums, image/video metadata and a
full FFmpeg decode of each MP4. A successful response has
`"package_validation_status": "passed"`.

## Upload mapping and manual actions

| Platform | Upload from `final/` |
|---|---|
| Instagram | `instagram_carousel/frame_01.png` through `frame_NN.png` as a carousel |
| TikTok | `<episode_id>_tiktok.mp4` |
| YouTube Shorts | `<episode_id>_youtube_shorts.mp4` |
| VK Clips | `<episode_id>_vk_clips.mp4` |

Instagram Reels MP4 is not created by this bounded workflow. Captions,
hashtags, covers and music remain manual platform actions; LOOPRA does not
publish or schedule content.

## Exit codes and expected errors

- `0` — command completed successfully.
- `1` — validation, package verification or production failure.
- `2` — invalid command-line usage.

Expected user errors are concise and do not show a traceback in normal use.
With `--json`, stdout is one JSON object. For validation errors it includes
`status`, `error_type`, `manifest`, `message` and `errors`; each error identifies
the failing JSON path. For a failed package verification, it includes
`package_root`, `errors` and `warnings`.

Typical fixes:

- Missing or invalid manifest: check the `--episode` path and the JSON path in
  the error.
- Missing font: install a supported system font or package a relative font file.
- Missing `ffmpeg` or `ffprobe`: install them and make both commands available
  on `PATH`, then start a new PowerShell window.
- Package checksum mismatch: do not upload it; rerun production or restore an
  unmodified final package, then verify it again.

## Start the next episode

Create `input/<new_episode_id>/`, place the new `episode.json`, images and any
packaged font there, then repeat validate → produce → verify. No Python source
change is needed.

Do not run `scripts/generate_test_frames.py`, `scripts/prepare_video_test.py`,
Trend Radar, or a full test suite to use this public workflow.

## User Operational Acceptance Checklist

Run these commands manually from a new PowerShell window in the repository
root, using an already installed working environment. This checklist does not
delete user files or assert that user acceptance has already occurred.

```powershell
python scripts/produce_episode.py --help
Copy-Item -Recurse tests\fixtures\episode_package input\fixture_episode
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --validate-only
python scripts/produce_episode.py --episode input\fixture_episode\episode.json --json
python scripts/produce_episode.py --verify-package output\fixture_episode\final --json
Get-ChildItem output\fixture_episode\final
```

Expected signs: each CLI command exits `0`; production reports
`handoff_package_root`; verification reports `passed`; and the final directory
contains `manifest.json`, the selected platform MP4 files and Instagram carousel
slides. If `input\fixture_episode` already exists, use a different episode ID
or replace it only after preserving your own files.

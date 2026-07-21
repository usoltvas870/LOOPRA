# Comic Production Pipeline Quickstart

## Scope

This guide runs the bounded `DIALOG_MINISERIES` package acceptance: one
ordered clean-image episode, programmatic comic overlays, Instagram slides,
TikTok, YouTube Shorts and VK Clips, and a QA-verified manifest. It does not
publish, generate captions or ZIP the package.

## Prerequisites

- Run commands from the repository root with the project's supported Python
  environment.
- Install the project's Python dependencies, including Pillow. This repository
  does not currently declare dependencies in a requirements or package
  manifest; use the established local development environment.
- Make `ffmpeg` and `ffprobe` available on `PATH`.
- Provide a readable TTF/OTF font containing Cyrillic glyphs.

Check the environment:

```powershell
python --version
ffmpeg -version
ffprobe -version
Test-Path C:\Windows\Fonts\arial.ttf
```

## Quick acceptance

On Windows, the runner auto-detects `C:\Windows\Fonts\arial.ttf` when it is
available. The command below creates an isolated technical fixture and keeps
the completed package for review:

```powershell
python scripts/run_comic_pipeline_acceptance.py --workdir .tmp/comic-acceptance --keep-output --json
```

For a different font, pass `--font <path-to-font>`. Without `--workdir`, the
runner uses a temporary directory and deletes it after a successful run unless
`--keep-output` is supplied. `--help` is side-effect-free.

To verify the real missing-font failure path (expected non-zero exit):

```powershell
python scripts/run_comic_pipeline_acceptance.py --workdir .tmp/comic-failure --keep-output --failure-smoke --json
```

The acceptance runner creates nine clean technical illustrations, uses the
actual `ProductionPipelineService` and repositories, runs real Pillow,
FFmpeg, ffprobe and manifest QA, then also checks the missing-font failure
path. It never uses network services or production mocks.

## Run your episode

Create `projects/<project_id>/` with `project.yaml` and put clean PNG images
under that project directory, for example `assets/scene_01.png`. Build a
`ProductionBrief` with:

- `content_format: "dialog_miniseries"`;
- ordered `scenes` with one `comic_overlay` each;
- `speaker`: `nura`, `woman`, or `shadow`;
- a bubble `position`, `tail_anchor` outside the bubble, `duration_sec`, and
  `image_source` relative to the project directory;
- `target_platforms`: `instagram`, `tiktok`, `youtube_shorts`, and/or `vk`;
- `subtitles.font_path` set to the TTF/OTF used to draw comic text.

The public acceptance runner is deliberately limited to its reproducible
technical fixture. To run a custom approved brief today, construct and save it
through `FileSystemProductionBriefRepository`, then call
`ProductionPipelineService.create_render_job()`, `validate_assets()`, and
`execute_render()` in that order. This preserves the existing service contract
instead of adding a second production implementation.

## Results

The package root is:

```text
storage/<project_id>/renders/<render_job_id>/comic/
├── scene_01.png ... scene_09.png
├── platforms/instagram/01.png ... 09.png
├── platforms/tiktok/final_video.mp4
├── platforms/youtube_shorts/final_video.mp4
├── platforms/vk_clips/final_video.mp4
└── manifest.json
```

The runner additionally writes `acceptance_contact_sheet.png` for manual QA.
It is not an `OutputFile` and is not included in the manifest.

## Common errors

- Missing font: set `subtitles.font_path` to an existing Cyrillic TTF/OTF.
- Source outside project root: use a project-relative image path.
- Tail anchor inside bubble: select an anchor outside the selected position.
- Text too long: shorten it so the renderer can wrap it inside the bubble.
- FFmpeg unavailable: install it and ensure both `ffmpeg` and `ffprobe` are on
  `PATH`.
- Corrupt PNG: replace the source asset with a readable image.
- Unsupported platform: use only the platforms in the current preset contract.
- Stale output: use a new workdir or remove only the intended old acceptance
  directory after inspection.

## MVP limitations

- Bubble reveal is a hard delayed reveal.
- One bubble is supported per scene; positions and anchors are manual.
- No autopublishing, ZIP, captions/hashtags, platform-specific music, UI,
  automated face detection, or automatic free-space search.

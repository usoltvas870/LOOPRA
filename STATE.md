# STATE.md

## LOOPRA Project State

## Current Identity

Project name:

LOOPRA

Category:

Autonomous Marketing Operating System

Previous working name:

Content Plant

The transition from Content Plant to LOOPRA changes the product
identity, not the validated technical foundation.

-----------------------------------------------------------------------

# Current Status

## Foundation MVP

Status:

READY + OPERATIONALLY VERIFIED

The foundation layer is operationally verified.

Validated principles:

-   project-agnostic architecture;
-   separation of foundation and project configuration;
-   filesystem-first approach;
-   controlled development process.

-----------------------------------------------------------------------

# Stage 1 Foundation Hardening

## Documentation Baseline

Commit:
ff6589b — docs: complete LOOPRA documentation baseline

Status:
COMPLETE

36 active documents across 9 layers catalogued in
docs/DOCUMENTATION_INDEX.md. All previous documentation warnings
(W1, W2, W5, W6, W7) resolved in the Final Architecture Audit
(docs/FINAL_ARCHITECTURE_AUDIT.md v1.0).

## Naming Cleanup

Commit:
3c6c0a6 — fix: make LOOPRA env vars primary

W3/W4 resolved:

W3 — CONTENT_PLANT_* env var naming migrated to LOOPRA_*.
W4 — Content Plant user-facing strings replaced with LOOPRA.

## Runtime / Configuration Naming

LOOPRA_* env vars are primary:

-   LOOPRA_SMOKE_PROJECT_ID
-   LOOPRA_SMOKE_PROJECTS_ROOT
-   LOOPRA_PROJECTS_ROOT

CONTENT_PLANT_* env vars remain supported as legacy fallback:

-   CONTENT_PLANT_SMOKE_PROJECT_ID
-   CONTENT_PLANT_SMOKE_PROJECTS_ROOT
-   CONTENT_PLANT_PROJECTS_ROOT

Resolution order:

LOOPRA_* → CONTENT_PLANT_* → default

## CLI Help Support

Commit:
4cec363 — feat: add help support to CLI scripts

Status:
COMPLETE

Summary:

-   --help/-h supported by all current Foundation MVP CLI scripts:
    smoke_loop.py, inspect_package.py, validate_package.py,
    find_metric_snapshots.py, import_manual_metrics.py.
-   smoke_loop.py --help is now safe and does not execute the lifecycle.
-   Help mode exits with code 0.
-   Help mode has no side effects.
-   Normal CLI output contract remains unchanged.

Verification:

-   tests: 120/120 OK (at time of commit)
-   smoke_loop normal mode: PASS
-   inspect_package.py: PASS
-   validate_package.py: PASS
-   working tree clean after commit

## CLI JSON Output Mode

Status:
COMPLETE

Summary:

-   --json output mode is now implemented on all 5 Foundation MVP CLI
    scripts: smoke_loop.py, inspect_package.py, validate_package.py,
    find_metric_snapshots.py, import_manual_metrics.py.
-   Human-readable output remains default and unchanged.
-   --help / -h wins over --json and remains side-effect-free.
-   JSON success output goes to stdout; stderr is empty.
-   JSON error output goes to stdout (JSON mode) or stderr with
    ERROR: prefix (human mode). Exit codes unchanged (0/1).
-   Unknown flags are rejected in both modes.
-   smoke_loop.py --json still executes the full Foundation MVP
    lifecycle and creates the same runtime artifacts as human mode.
-   Lifecycle errors in smoke_loop.py --json produce structured JSON
    errors (instead of Python tracebacks).
-   import_manual_metrics.py --json mutates through AnalyticsService,
    not direct JSON writes.
-   Env var semantics unchanged (LOOPRA_* primary, CONTENT_PLANT_*
    legacy fallback).
-   Stage 2 Slice 1 — Content Intelligence Foundation is IMPLEMENTED + VERIFIED. Full Stage 2 is NOT complete. No API/UI/DB/runtime agent/Orchestrator/connectors/autoposting/Learning Memory introduced.

Verification:

-   tests: 173/173 OK
-   all 5 scripts --json success: PASS
-   all 5 scripts --help and --json --help: PASS (side-effect-free)
-   unknown flag rejection in both modes: PASS
-   smoke_loop.py --json lifecycle artifact creation: PASS
-   import_manual_metrics.py --json mutation through service: PASS

Docs updated:

-   docs/05_platform/TOOLING_AND_CLI_SPEC.md — JSON output mode
    documented for all 5 scripts
-   docs/06_operations/OPERATIONAL_RUNBOOK.md — JSON output mode
    added to each tool section

## Operational Acceptance Run

Stage 1 Foundation Hardening Operational Acceptance: PASS

Checks:

-   tests: 109/109 OK
-   smoke_loop default mode: PASS
-   smoke_loop LOOPRA_* env mode: PASS
-   smoke_loop legacy CONTENT_PLANT_* fallback mode: PASS
-   inspect_package: PASS
-   validate_package: PASS
-   git status before run: clean
-   git status after run: clean
-   tracked files changed: none

Smoke loop default verification IDs:

project_id: example
idea_id: idea_d1ff05507da5
scenario_id: scenario_5922a10836e5
content_item_id: content_0157b7417c71
export_package_id: export_72ec3675f998
publication_id: publication_76a254518fb0
metric_snapshot_id: metric_b11f310f884f

Statuses:

scenario_status=approved
content_item_status=exported
export_package_status=ready
publication_status=published
metric_snapshot_status=draft

-----------------------------------------------------------------------

# Architecture Direction

LOOPRA is evolving toward:

Brand System

↓

Growth Loop

↓

Intelligence

↓

Production

↓

Publishing

↓

Analytics

↓

Learning Memory

↓

Improved Next Cycle

-----------------------------------------------------------------------

# Completed Foundation Capabilities

Implemented:

-   domain layer;
-   lifecycle services;
-   project configuration;
-   content item flow;
-   export package generation;
-   publication records;
-   metric snapshot foundation;
-   video production pipeline (image-to-video with subtitles).

Validated lifecycle:

Idea

↓

Scenario

↓

ContentItem

↓

ExportPackage

↓

Publication

↓

MetricSnapshot

Video Production:

ProductionBrief → RenderJob → Video Output (MP4 + SRT + ASS + Cover)

-----------------------------------------------------------------------

# Current Development Phase

Phase:

Stage 1 Foundation Hardening — small bounded improvements

Current objectives:

-   operational docs consistency checks;
-   maintain architecture boundaries;
-   no further Stage 2 slices until explicitly approved.

Completed in this phase:

-   documentation baseline finalized and committed;
-   naming cleanup: LOOPRA_* primary, Content Plant removed from runtime;
-   operational acceptance run passed;
-   CLI --help/-h support added to all 5 scripts. smoke_loop.py --help is
    now side-effect-free.
-   CLI --json output mode added to all 5 scripts (design review,
    staged implementation, full test verification, documentation).

-----------------------------------------------------------------------

# Important Boundaries

Current phase does NOT include:

-   UI development;
-   API development;
-   database implementation;
-   authentication;
-   billing;
-   SaaS infrastructure;
-   external publishing integrations;
-   autonomous agent swarm;
-   further Stage 2 slices beyond implemented Slices 1 and 2;
-   connector development;
-   autoposting.

These belong to future phases.

-----------------------------------------------------------------------

# LOOPRA Transition

The project has moved from:

Content Plant

"content production platform"

to:

LOOPRA

"autonomous marketing operating system".

The architecture remains based on the validated foundation.

-----------------------------------------------------------------------

# Development Rules

Always preserve:

-   project-agnostic core;
-   clear separation of layers;
-   documentation as source of truth;
-   incremental validated progress.

-----------------------------------------------------------------------

# Next Direction

Stage 1 Foundation Hardening can continue with small bounded
improvements only:

1.  Operational docs consistency checks.

Do not start further Stage 2 slices without explicit bounded
scope/gate approval.

-----------------------------------------------------------------------

# Final State Statement

LOOPRA is being built as an autonomous marketing operating system that
enables brands to continuously learn, create and improve through
intelligent growth loops.

-----------------------------------------------------------------------

# Stage 2 Slice 1 — Content Intelligence Foundation

Status:
IMPLEMENTED + VERIFIED

Summary:

- Manual `MarketSignal` records can be imported for a project.
- Manual `TrendPattern` records can be created from project-scoped market signals.
- Manual `ContentOpportunity` records can be created, approved, rejected, deferred, archived and converted.
- Approved opportunities can be converted into existing Foundation MVP `Idea` records through `IdeaService.create_idea()`.
- The implementation remains local/filesystem-first, deterministic, project-scoped and CLI-driven.

Boundaries preserved:

- No API, UI, database, authentication, billing or SaaS infrastructure.
- No external integrations, scraping, connectors or provider calls.
- No autoposting, scheduler, background worker or autonomous runtime agent.
- No Orchestrator Agent or Learning Memory implementation.
- NURA is used only as a project-scoped validation project.

Verification:

- domain tests: PASS
- service tests: PASS
- full test suite: 181/181 OK
- smoke_loop human mode: PASS
- smoke_loop JSON mode: PASS

-----------------------------------------------------------------------

# Stage 2 Slice 2 - Content Intelligence Hardening

Status:
IMPLEMENTED + VERIFIED

Summary:

- `ContentOpportunity` conversion now requires a non-empty `idea_id` at the domain transition boundary.
- `MarketSignal` review has an explicit deterministic service and CLI path.
- Existing trend activation and opportunity reject/defer/archive lifecycle paths have dedicated CLIs.
- Intelligence CLI scripts follow the readable Foundation CLI style and retain human/JSON/help/unknown-option contracts.
- Get/list/status-filter, missing-entity, cross-project, duplicate-conversion and lifecycle tests are explicit.

Verification:

- domain intelligence tests: 4/4 OK
- service intelligence tests: 9/9 OK
- CLI intelligence tests: 4/4 OK
- domain suite: 18/18 OK
- services suite: 172/172 OK
- full test suite: 190/190 OK
- smoke_loop human mode: PASS
- smoke_loop JSON mode: PASS

Boundaries preserved:

- This slice hardens manual deterministic Content Intelligence; full Stage 2 is not complete.
- Future slices remain gated.
- No autonomous intelligence, external integrations, scraping or connectors exist.
- No API, UI or database exists.
- No Orchestrator Agent or Learning Memory exists.
- The Foundation MVP execution chain remains unchanged.

-----------------------------------------------------------------------

# Video Production Pipeline

Status:
IMPLEMENTED

Summary:

- Core video rendering engine (`core/tools/video/renderer.py`) produces MP4 video from still images with Ken Burns effect (zoom/pan) and xfade transitions.
- Subtitle generation: SRT files generated from scene narration_text with proper timecodes.
- Subtitle burning: FFmpeg ASS filter with configurable font family, size, color and stroke; an explicit TTF/OTF path is resolved to its family and supplied to libass through its font directory.
- Audio mixing: voiceover + background music with sidechain ducking.
- Asset validation: image resolution, audio file integrity, font availability.
- QA verification: video/audio/subtitle stream checks via ffprobe.
- Domain models: ProductionBrief, ProductionScene, ProductionAudio, ProductionSubtitles, ProductionOutput.
- Production pipeline service: RenderJob creation, asset validation, render execution, output file tracking.
- CLI script: `scripts/produce_video.py` with --project-id, --brief, --format, --dry-run, --json options.
- Supported formats: short_vertical_video (1080x1920, 24fps, max 90s), ambient_vertical_video (1080x1920, 24fps, default 15s).
- Test coverage: ~51 tests across renderer, audio, QA, validators, pipeline, domain models, CLI.

Boundaries preserved:

- Video production is a tool-level capability; no autonomous agent orchestration.
- No external AI video generation APIs; rendering uses local FFmpeg.
- No autoposting or publishing integration.
- video-assembler/ remains as legacy standalone subsystem (not integrated with core pipeline).

Verification:

- focused renderer tests: 14 passed (`tests/tools/video/test_renderer.py`)
- focused model/service tests: 19 passed (`tests/domain/test_production_brief.py`, `tests/services/test_production_pipeline.py`)
- local FFmpeg subtitle smoke: PASS (two synthetic scenes, explicit Arial TTF, Cyrillic subtitles, MP4/SRT/ASS artifacts, ffprobe QA)
- CLI `--help`: PASS
- full test suite was not run in this subtitle-hardening verification

-----------------------------------------------------------------------

# Carousel Production Pipeline

Status:
IMPLEMENTED + VERIFIED

Summary:

- `ProductionBrief` with `INSTAGRAM_CAROUSEL` is rendered by the Pillow-based `render_carousel()` tool.
- The canonical production flow is `ProductionBrief` → `RenderJob` → PNG slides → carousel QA → `OutputFile` records.
- Production output is stored under `storage/<project_id>/renders/<render_job_id>/carousel/`; the standalone CLI uses the same storage layout with its brief ID.
- Slide dimensions come from `ProductionOutput`; 1080x1350 (4:5) is the verified Instagram configuration.
- QA verifies PNG existence, non-empty files, expected count and expected dimensions before the service records output artifacts.

Verification:

- carousel renderer and CLI tests: 27 passed
- production service and QA tests: 19 passed
- domain/video regression tests: 25 passed
- local carousel smoke: PASS (five 1080x1350 PNG slides, Cyrillic text, explicit QA)
- full test suite was not run in this carousel verification

Limitations:

- This slice renders text-based carousel slides only; it does not implement clean-illustration compositing, comic overlays, platform export packages or publishing.

-----------------------------------------------------------------------

# Comic Production Pipeline — Static Overlay Foundation

Status:
IMPLEMENTED + VERIFIED

Summary:

- `ProductionScene` supports an optional `ComicOverlay` with validated speaker, bubble position, text and normalized tail anchor.
- Three immutable visual themes are available: NURA, Woman and Shadow.
- `render_comic_frame()` creates one static PNG from a clean source image using Pillow; it never modifies the source image.
- Shared Pillow text layout supports Cyrillic, explicit line breaks, word wrapping, font-size reduction and explicit overflow failure without clipping.
- Focused model, text-layout and comic-renderer tests passed.
- A real, unmocked Pillow smoke render passed with an explicit Arial TTF and a Cyrillic NURA line.

Limitations:

- No integration with `ProductionPipelineService` or `RenderJob`.
- No batch episode render, video integration or Instagram comic package.
- No TikTok, YouTube or VK presets.
- No bubble animation, automatic positioning or multiple bubbles per frame.

-----------------------------------------------------------------------

# Comic Production Pipeline — Static Frame Batch

Status:
IMPLEMENTED + VERIFIED

Summary:

- The existing `DIALOG_MINISERIES` content format is the bounded comic episode type; no new enum was added.
- A comic `ProductionBrief` requires ordered `ProductionScene` entries, one `ComicOverlay` per scene and an explicit usable comic font path.
- `render_comic_frames()` renders ordered `scene_01.png`, `scene_02.png`, ... through the existing immutable `render_comic_frame()` function.
- The production flow is `ProductionBrief` → `RenderJob` → comic frame batch → PNG QA → ordered `OutputFile` records.
- Comic frames are written under `storage/<project_id>/renders/<render_job_id>/comic/`.
- QA verifies the exact ordered frame set, PNG format, non-empty files and each source-derived output size before any `OutputFile` is registered.
- Batch failures delete partial `scene_*.png` output, preserve unrelated files and set the current `RenderJob` to `FAILED`; no output records are registered before renderer and QA success.
- Sources are project-root constrained for batch rendering and remain byte-for-byte unchanged.

Verification:

- domain test: 20 passed
- comic renderer and shared text layout: 17 passed
- production service and QA: 23 passed
- carousel regression: 27 passed
- video regression: 15 passed
- real service smoke: PASS (3 scenes, `nura`/`woman`/`shadow`, 480x800 sources, Arial TTF, Cyrillic text including `ё`, em dash and Russian quotes; 3 PNG and 3 `OutputFile` records; source hashes unchanged; QA passed; no extra or temporary frames)

Limitations:

- No comic CLI, FFmpeg/video integration, Instagram comic export or platform package.
- No TikTok, YouTube or VK presets.
- No bubble animation, automatic positioning or multiple bubbles per scene.

-----------------------------------------------------------------------

# Comic Production Pipeline — Master Video Integration

Status:
IMPLEMENTED + VERIFIED

Summary:

- `DIALOG_MINISERIES` retains its static comic-frame contract; `ProductionOutput.generate_comic_master_video` explicitly and backward-compatibly requests one additional master MP4.
- The service renders and QA-checks all comic PNGs, creates a deep derived brief whose scene image sources point to those PNGs, then delegates MP4 creation to the existing `render_narrative_video()` renderer.
- The original brief, scenes, comic overlays, audio configuration and output configuration remain unchanged. The derived copy preserves scene order, duration, animation and transitions, while disabling regular subtitle burn-in to avoid duplicating bubble text.
- The master MP4 is written under `storage/<project_id>/renders/<render_job_id>/comic/video/` and is checked through the existing video QA with resolution, FPS, duration, codec and pixel-format expectations.
- The comic package follows `comic frames → comic QA → video render → video QA → OutputFile`. Frames and actual video artifacts are registered only after successful rendering and QA; a failure cleans current-job comic artifacts and leaves no newly registered output files.

Verification:

- production brief contract: 21 passed
- comic foundation and batch: 17 passed
- production service and QA: 26 passed, including a real three-scene Pillow + FFmpeg smoke at 270x480/24 FPS without voiceover or subtitle burn-in
- video regression: 15 passed
- carousel regression: 27 passed
- `python scripts/produce_video.py --help`: PASS

Limitations:

- No TikTok, YouTube Shorts or VK Clips presets.
- No comic CLI, platform package, multiple video exports, teaser, bubble timing or bubble animation.

-----------------------------------------------------------------------

# Comic Production Pipeline — Platform Video Presets

Status:
IMPLEMENTED + VERIFIED

Summary:

- The existing `ProductionBrief.target_platforms` and `PublishingPlatform` contract selects TikTok, YouTube Shorts and VK Clips outputs; no parallel platform field or content type was added.
- Three immutable presets centralize scene timing, bubble delay, supported camera motion, transition type/duration and final hold.
- One comic frame batch and the existing `render_narrative_video()` renderer are reused for every requested platform.
- Deep derived briefs expand each original scene into a clean phase and a bubble-frame phase, implementing an MVP delayed hard bubble reveal without mutating the original brief, scenes or comic overlays.
- Platform motion is expressed through renderer-supported scale/easing values. Platform transitions apply only between original story scenes; clean-to-bubble uses a zero-duration hard cut.
- Final hold is added once to the final bubble phase. Expected QA duration includes platform timing, transition overlaps and final hold.
- Requested platform videos are rendered and QA-checked before any `OutputFile` is registered. Render, QA and repository failures clean the current job's comic frames, master video and platform artifacts and leave the job `FAILED`.
- Output paths are:
  - `comic/platforms/tiktok/final_video.mp4`;
  - `comic/platforms/youtube_shorts/final_video.mp4`;
  - `comic/platforms/vk_clips/final_video.mp4`.
- `generate_comic_master_video` remains independent and can coexist with platform outputs.

Verification:

- production brief contract: 21 passed
- platform preset and derived brief tests: 7 passed
- comic foundation, batch and platform tests: 24 passed
- production service and QA: 32 passed
- video regression: 16 passed
- carousel regression: 27 passed
- real three-platform service smoke: PASS (3 original scenes, 6 derived scenes per platform, 270x480, 24 FPS, one Pillow comic batch, real FFmpeg and ffprobe, 3 PNG + 3 MP4 + 6 `OutputFile` records, source hashes unchanged, no SRT/ASS or temporary MP4)
- smoke MP4 durations: TikTok 3.81s, YouTube Shorts 5.75s, VK Clips 4.76s

Limitations:

- Bubble reveal is a hard cut; opacity/scale bubble animation is not implemented.
- No teaser scene or scene reordering.
- No platform-specific music.
- No Instagram comic export.
- No package manifest or shared publish package.
- No comic CLI or autopublishing.
- This is the bounded three-platform video preset slice, not the complete multi-platform comic package.

-----------------------------------------------------------------------

# Comic Production Pipeline — Four-Platform Package Export

Status:
IMPLEMENTED + VERIFIED

Summary:

- One `DIALOG_MINISERIES` `RenderJob` now produces one logical comic package from a single ordered comic-frame batch.
- `PublishingPlatform.INSTAGRAM` selects a static adapter over the already rendered comic PNGs. The adapter performs uniform contain from 9:16 to the immutable 1080x1350 (4:5) preset; it does not crop, stretch, redraw bubble text or mutate source/comic frames.
- Instagram background is resolved from `ProductionBrand.colors_background_dark`; an immutable neutral RGBA preset value is the project-agnostic fallback.
- TikTok, YouTube Shorts and VK Clips continue to use the existing `render_narrative_video()` renderer and their immutable video presets.
- The `RenderJob` comic directory is the package root. `comic/manifest.json` uses schema version `1.0`, safe relative paths, deterministic artifact order, MIME, byte size, SHA-256 and image/video metadata already available from QA.
- Manifest intermediates (`scene_*.png`) are distinct from deliverables (Instagram slides, platform/master media). The manifest never hashes itself and is registered last as `OutputFileType.METADATA`.
- Stable `OutputFile` order is comic frames, Instagram slides, optional master artifacts, TikTok, YouTube Shorts, VK Clips and manifest.
- Rendering, platform QA, package QA, manifest write/QA and repository failures leave the job `FAILED`, remove only known current-job artifacts and records, and preserve source images, other jobs and unrelated files.

Verification:

- production brief contract: 21 passed;
- Instagram preset/renderer: 6 passed, 3 subtests passed;
- manifest model/writer/QA: 5 passed, 12 subtests passed;
- comic foundation/platform regression: 34 passed, 9 subtests passed;
- production service and QA: 35 passed;
- video regression: 16 passed;
- ordinary carousel regression: 27 passed;
- full suite: 373 passed, 145 subtests passed;
- real four-platform service smoke: PASS (3 scenes, 270x480 sources, 1080x1350 Instagram slides, 3 comic PNG + 3 Instagram PNG + 3 MP4 + manifest, real Pillow/FFmpeg/ffprobe/manifest QA, one comic-frame batch, deterministic 10-record `OutputFile` order, unchanged sources, no SRT/ASS, temporary MP4 or unrequested outputs).
- smoke MP4 durations: TikTok 3.81s, YouTube Shorts 5.75s, VK Clips 4.76s.

Limitations:

- The package is a verified `RenderJob` directory, not a ZIP archive.
- No autopublishing, social API integration, social captions, hashtags or cover generation is added.
- No comic CLI, teaser scene, scene reordering, animated bubble reveal or platform-specific music is added.
- The final 8–10 scene MVP acceptance is recorded below.

-----------------------------------------------------------------------

# Comic Production Pipeline MVP Acceptance

Status:
READY + END-TO-END VERIFIED

Foundation chain:

- `5d00c15` static comic overlay foundation;
- `a1fb463` comic frame batch;
- `ad68ddc` comic/video renderer integration;
- `3abe8a9` comic platform presets;
- `0d3820a` four-platform comic package export.

Acceptance verification:

- A real 9-scene technical episode produces nine immutable-source comic
  frames, nine Instagram contain slides, and TikTok, YouTube Shorts and VK
  Clips MP4 outputs.
- The acceptance runner uses real Pillow, FFmpeg, ffprobe,
  `ProductionPipelineService`, filesystem repositories and manifest QA.
- The manifest has schema `1.0`; all package paths are relative and its
  artifacts are hash- and metadata-verified.
- `OutputFile` records are registered only after QA; the 9-scene four-platform
  fixture produces 22 records with the manifest last.
- The missing-font failure smoke exits non-zero, reaches `RenderJob.FAILED`,
  registers no `OutputFile`, and keeps source hashes unchanged.
- The public command is
  `python scripts/run_comic_pipeline_acceptance.py --workdir <directory> --keep-output --json`.
- Operator instructions: `docs/04_production/COMIC_PIPELINE_QUICKSTART.md`.

Known MVP limitations:

- hard delayed bubble reveal; one manually positioned bubble and tail per scene;
- no publishing, ZIP, captions/hashtags, platform-specific music, UI, face
  detection or automatic free-space search.

-----------------------------------------------------------------------

# Canonical Episode Input Package

Status:
IMPLEMENTED + END-TO-END VERIFIED

Summary:

- `episode.json` schema version `1` is the canonical filesystem input for the
  bounded `DIALOG_MINISERIES` production flow.
- The loader maps the manifest directly into the existing `ProductionBrief`,
  `ProductionScene`, and `ComicOverlay` contract; no parallel renderer or CLI
  domain model exists.
- Package-relative image and font paths are root-constrained. Strict parsing,
  enum/default checks, H.264 dimensions, image/font integrity, platform timing,
  text fit, bubble geometry, and tail geometry are validated before runtime
  staging, renderer, or FFmpeg execution.
- Validated sources are copied to ignored runtime staging. Source packages are
  never modified; production continues through the existing repositories,
  `ProductionPipelineService`, comic/image/video QA, and package manifest.
- Public command:
  `python scripts/produce_episode.py --episode input/<episode_id>/episode.json`;
  `--validate-only`, `--json`, and side-effect-free `--help` are supported.
- The version-controlled nine-frame technical fixture demonstrates all three
  speakers, Cyrillic and long text, positions/anchors, defaults, a duration
  override, four platforms, and full production.

Verification:

- targeted loader/domain/CLI/renderer tests: 66 passed;
- comic/video/service/CLI/e2e regression: 94 passed, 15 subtests passed;
- existing public comic acceptance: PASS (9 scenes, 22 output records, failure
  smoke and source integrity PASS);
- version-controlled fixture: validation-only PASS; two production runs PASS;
  22 output records per run and 21 non-manifest artifact hashes identical;
- real NURA nine-PNG package through the public episode command: PASS (22
  output records, source hashes unchanged, three MP4 files passed ffprobe,
  existing video QA, and full decode);
- full suite: 425 passed, 176 subtests passed.

Boundaries preserved:

- Existing RenderJob output and Export/Handoff Package semantics are unchanged.
- No Trend Radar, Content Ledger, publication, connector, UI, database, agent,
  image generation, or output-layout redesign is included.

-----------------------------------------------------------------------

# Intelligence / Planning to Carousel Production Vertical Slice

Status:
END-TO-END VERIFIED

The local deterministic acceptance now proves the existing canonical chain:
`MarketSignal → TrendPattern → ContentOpportunity → Idea → explicit carousel
ScenarioTextBlock input → approved Scenario → validated ProductionBrief →
RenderJob → PNG carousel QA → OutputFile`.

Verification:

- public runner:
  `python scripts/run_intelligence_to_carousel_acceptance.py --workdir .tmp/intelligence-carousel-acceptance --keep-output --json`;
- real filesystem repositories, Pillow renderer and carousel QA;
- five 1080x1350 PNG records with SHA-256 verification; and
- focused success and needs-review handoff-failure acceptance coverage.

Operator instructions:
`docs/04_production/INTELLIGENCE_TO_CAROUSEL_QUICKSTART.md`.

Limits retained:

- carousel text remains explicit planning input; no AI text generation;
- no Trend Radar connector, publishing, analytics, Learning Memory,
  orchestrator/runtime agent or general ContentCycle;
- only the Instagram carousel handoff is covered; and
- Opportunity, Idea and Scenario approvals remain explicit.

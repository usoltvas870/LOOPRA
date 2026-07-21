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

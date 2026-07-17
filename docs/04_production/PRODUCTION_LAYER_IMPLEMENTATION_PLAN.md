# PRODUCTION LAYER IMPLEMENTATION PLAN

## Version

v1.0

## Status

Planning — NURA Week 1 Production Baseline

## Purpose

This document defines the complete implementation plan for adding
minimal production capabilities to LOOPRA — specifically three content
formats for NURA's first publishing week:

1. **Narrative vertical video** (static images → MP4 with Ken Burns,
   subtitles, voiceover, music)
2. **Ambient vertical video** (single image + slow animation + text phases
   + background music)
3. **Instagram carousel** (5–7 branded slides, 4:5, PNG export)

The plan preserves the existing Foundation MVP chain:
`Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot`
and extends only the production segment between `Scenario` and `ExportPackage`.

---

# 0. Execution Model

## 0.1. Session-Based Isolation

This plan is divided into **6 sequential sessions**. Each session:

- Runs in a **separate chat** with a fresh agent context
- Is **large enough** for a lead agent to spawn sub-agents for parallel
  workstreams
- Has a **clear entry state** (what files exist before the session starts)
- Has a **clear exit state** (what files are created/modified, what tests
  pass)
- Produces a **verifiable artifact** (passing tests, working CLI, rendered
  output)
- Does **not depend on context carried over** from previous sessions —
  the agent reads the codebase fresh and verifies the current state

## 0.2. Sub-Agent Coordination

Each session is designed so the lead agent:

1. Reads the relevant source-of-truth documents and existing code
2. Decomposes the session into 3–5 parallel workstreams
3. Dispatches sub-agents for each workstream
4. Integrates results, resolves conflicts
5. Runs the full test suite
6. Verifies session acceptance criteria
7. Reports completion with changed files and test results

## 0.3. Invariants Across All Sessions

These rules must not be violated by any session:

- **No core/ modification without architectural justification.**
  Domain models, enums, and service interfaces may be extended. Existing
  behaviour must not regress.
- **No project-specific hardcoding in core/.**
  NURA-specific settings belong in `projects/nura/` and
  `docs/07_projects/nura/`.
- **No UI, no API, no database, no autoposting, no external integrations.**
- **No deletion of existing tests.** Add new tests; never remove or weaken
  existing ones.
- **Existing CLI contracts preserved.** `--help`, `--json`, unknown-flag
  rejection, exit codes, env var resolution.
- **Foundation MVP smoke loop must pass after every session.**
  `python scripts/smoke_loop.py` with the `example` project.
- **Full test suite must pass after every session.**
  `python -m pytest tests/ -v`

---

# 1. Architecture Decisions (Made Up Front)

These decisions are binding for all sessions. No session may re-litigate
them.

## 1.1. ContentFormat Enum Extension

```python
class ContentFormat(StrEnum):
    TEXT_SOCIAL_POST = "text_social_post"
    DIALOG_MINISERIES = "dialog_miniseries"
    SHORT_VERTICAL_VIDEO = "short_vertical_video"       # NEW
    AMBIENT_VERTICAL_VIDEO = "ambient_vertical_video"   # NEW
    INSTAGRAM_CAROUSEL = "instagram_carousel"           # NEW
```

## 1.2. ProductionBrief — New Domain Model

A `ProductionBrief` is a structured, machine-actionable production
instruction. It is:

- **Not a strategic entity** — it does not decide what to create
- **Immutable after approval** — like a manufacturing order
- **Stored as JSON** in `projects/{project_id}/data/production_briefs/`
- **Referenced from `Scenario.metadata`** (via `production_brief_id`)

Placement: `core/domain/models.py` (new model class)

## 1.3. RenderJob Fills the Gap

The existing `RenderJob` entity (already in `core/domain/models.py`,
line 258) is activated as the bridge between Scenario and ContentItem:

```
Scenario (approved)
    ↓
ProductionBrief (created from Scenario.metadata)
    ↓
RenderJob (queued → validating → rendering → rendered)
    ↓
OutputFile[] (one per artifact: video, audio, subtitle, cover, slide)
    ↓
ContentItem (in_production → rendered → needs_review → approved → exported)
    ↓
ExportPackage (draft → ready)
```

## 1.4. Video Assembler as Library

`video-assembler/` is adapted into `core/tools/video/` as a LOOPRA
production tool. Key changes:

- Replaces `_CONTENT_PLANT_ROOT` with `LOOPRA_PROJECTS_ROOT`
- Consumes `ProductionBrief` domain models (not standalone ScenarioConfig)
- Is called from `ProductionPipelineService`, not standalone CLI
- Outputs to `storage/{project_id}/renders/{render_job_id}/`
- Original `video-assembler/` remains intact as reference; new code lives
  in `core/tools/video/`

## 1.5. TTS Interface — Provider-Neutral

```python
# core/services/tts.py

from abc import ABC, abstractmethod
from pathlib import Path

class TTSService(ABC):
    """Provider-neutral TTS interface."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice_profile: str,
        output_path: Path,
        language: str | None = None,
    ) -> Path:
        """Synthesize text to audio file. Returns path to audio file."""
        ...


class FileTTSService(TTSService):
    """Stub: copies a pre-rendered voiceover file to the output path.
    Used when voiceover is produced externally (human or third-party TTS).
    """

    def synthesize(
        self,
        text: str,
        voice_profile: str,
        output_path: Path,
        language: str | None = None,
    ) -> Path:
        import shutil
        source = Path(voice_profile)  # voice_profile is a file path in stub mode
        if not source.exists():
            raise FileNotFoundError(f"Voiceover file not found: {source}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, output_path)
        return output_path
```

Future implementations (e.g. `ElevenLabsTTSService`, `OpenAITTSService`)
implement the same interface. The core never imports a specific provider.

## 1.6. Safe Zones — Platform-Level Constants

Safe zones for vertical video platforms are defined in `core/tools/video/`
as constants, not per-project configuration:

```python
SAFE_ZONES: dict[str, dict[str, int]] = {
    "tiktok":        {"top": 130, "bottom": 240, "left": 60, "right": 60},
    "instagram":     {"top": 120, "bottom": 200, "left": 60, "right": 60},
    "youtube_shorts": {"top": 120, "bottom": 200, "left": 60, "right": 60},
    "vk":            {"top": 100, "bottom": 180, "left": 50, "right": 50},
}
```

Individual projects may override in project config. The platform default
is used when no override exists.

## 1.7. ExportPackage Structure

```
projects/{project_id}/exports/{export_package_id}/
├── manifest.json
├── metadata.json
├── qa_report.json
├── production_snapshot.json
├── final_video.mp4              # Video formats only
├── subtitles.srt                # Video formats only
├── audio_only.mp3               # Video formats only
├── cover.png                    # Video formats only
├── carousel/                    # Carousel format only
│   ├── slide_01.png
│   ├── slide_02.png
│   └── ...
├── caption_{platform}.txt       # Per target platform
├── hashtags.txt
└── publish_notes.md
```

## 1.8. CLI Conventions

All new CLI scripts follow the established Foundation MVP contract:

```
--help / -h        Side-effect-free, exit 0
--json             Structured JSON to stdout, errors to stdout
--project-id       Required, consistent with LOOPRA_* env vars
Human-readable     Default output mode
Unknown flags      Rejected with error message
Exit codes         0 = success, 1 = error
```

---

# 2. Session Plan

## Session 0: Pre-Flight Checklist (Before Starting Any Session)

**Lead agent verifies:**

```
[ ] git status is clean
[ ] python -m pytest tests/ -v  →  190/190 OK
[ ] python scripts/smoke_loop.py → PASS
[ ] python -c "import core; print('imports OK')" → no errors
[ ] python -c "from video_assembler.src.assembler import assemble; print('assembler OK')" → no errors
[ ] pip list | grep -E "pydantic|imageio-ffmpeg|Pillow" → installed
[ ] ffmpeg -version → available on PATH
```

Do not start Session 1 until all checks pass.

---

## Session 1: Foundation Extension — Domain Models, Enums, Config

### Entry State

- All Foundation MVP entities operational
- `ContentFormat` = `TEXT_SOCIAL_POST`, `DIALOG_MINISERIES`
- `RenderJob` exists but unused
- `OutputFile` exists but unused
- No `ProductionBrief` model
- NURA project.yaml has no production configuration
- No TTS interface

### What We Build

#### Workstream 1A: ContentFormat Enum Extension
**File:** `core/domain/enums.py`
- Add `SHORT_VERTICAL_VIDEO`, `AMBIENT_VERTICAL_VIDEO`, `INSTAGRAM_CAROUSEL`

#### Workstream 1B: ProductionBrief Domain Model
**File:** `core/domain/models.py` (append)
- New class `ProductionBrief` extending `ProjectScopedModel`
- Fields: `production_brief_id`, `scenario_id`, `content_format`,
  `production_variant`, `target_platforms`, `scenes[]` (nested `ProductionScene`),
  `audio` (nested `ProductionAudio`), `subtitles` (nested `ProductionSubtitles`),
  `output` (nested `ProductionOutput`), `brand` (nested `ProductionBrand`),
  `qa` (nested `ProductionQA`), `status` (brief lifecycle: draft/validated/approved/in_progress/completed/archived)
- Nested models: `ProductionScene`, `ProductionAudio`, `ProductionSubtitles`,
  `ProductionOutput`, `ProductionBrand`, `ProductionQA`, `ProductionSlide`
- Status transitions: `PRODUCTION_BRIEF_STATUS_TRANSITIONS`
- `transition_to()` method

**File:** `core/domain/__init__.py`
- Export all new models

#### Workstream 1C: Production Brief Repository
**File:** `core/services/production_pipeline.py` (new)
- `FileSystemProductionBriefRepository(FileSystemProjectModelRepository[ProductionBrief])`
- `list_briefs()`, `load_brief()`, `save_brief()`

#### Workstream 1D: NURA Production Configuration
**File:** `projects/nura/project.yaml`
- New top-level key `production` with:
  - `formats` section for each of the 3 formats
  - `platforms` section with per-platform safe zones, aspect ratios, max durations
  - `brand_assets` paths: logo, fonts, colors
  - `templates_dir`: `projects/nura/templates/`

**File:** `projects/nura/templates/.gitkeep` (new directory)

#### Workstream 1E: TTS Interface
**File:** `core/services/tts.py` (new)
- Abstract `TTSService` (ABC)
- `FileTTSService` (stub implementation)

**File:** `core/services/__init__.py`
- Export `TTSService`, `FileTTSService`

### Sub-Agent Dispatch Strategy

| Sub-agent | Workstream | Parallel |
|---|---|---|
| Agent A | 1A: ContentFormat enums | Yes |
| Agent B | 1B: ProductionBrief model + transitions + tests | Yes |
| Agent C | 1C: ProductionBriefRepository | After 1B |
| Agent D | 1D: NURA config | Yes |
| Agent E | 1E: TTS interface | Yes |

### Acceptance Criteria

```
[ ] ContentFormat enum has all 5 values
[ ] ProductionBrief.model_validate(brief_dict) succeeds for all 3 formats
[ ] ProductionBrief.model_validate() rejects invalid briefs (missing required, wrong format)
[ ] ProductionBrief status transitions: draft→validated→approved→in_progress→completed
[ ] ProductionBriefRepository can save/load/list briefs
[ ] projects/nura/project.yaml has production section
[ ] FileTTSService copies a WAV file to target path
[ ] python -m pytest tests/domain/ -v → all pass (existing + new)
[ ] python -m pytest tests/services/ -v → all pass
[ ] python scripts/smoke_loop.py → PASS (text_social_post unchanged)
[ ] python -c "from core.domain import ProductionBrief" → no errors
[ ] python -c "from core.services.tts import FileTTSService" → no errors
```

### Output Files (Created/Modified)

```
MODIFIED: core/domain/enums.py
MODIFIED: core/domain/models.py           (+ProductionBrief +6 nested models)
MODIFIED: core/domain/__init__.py
MODIFIED: core/domain/transitions.py      (+PRODUCTION_BRIEF_STATUS_TRANSITIONS)
CREATED:  core/services/production_pipeline.py  (+FileSystemProductionBriefRepository)
CREATED:  core/services/tts.py
MODIFIED: core/services/__init__.py
MODIFIED: projects/nura/project.yaml       (+production section)
CREATED:  projects/nura/templates/.gitkeep
CREATED:  tests/domain/test_production_brief.py
CREATED:  tests/services/test_tts.py
```

---

## Session 2: Production Pipeline Service Layer

### Entry State

- `ProductionBrief` model and repository exist
- `RenderJob` and `OutputFile` models exist but are unused
- `FileTTSService` exists
- `ProductionLifecycleService` only handles text content
- NURA production config exists

### What We Build

#### Workstream 2A: ProductionPipelineService — RenderJob Orchestration
**File:** `core/services/production_pipeline.py` (extend)
- `ProductionPipelineService` class
- `create_render_job(project_id, brief_id) → RenderJob`
  - Loads brief, validates it, creates RenderJob with `input_snapshot`
  - Transition: queued → validating
- `validate_assets(project_id, render_job_id) → RenderJob`
  - Checks all referenced files exist, have correct resolutions, are readable
  - Transition: validating → rendering (or validating → failed)
- `execute_render(project_id, render_job_id) → RenderJob`
  - Dispatches to format-specific renderer (video or carousel)
  - Creates OutputFile records for each artifact
  - Transition: rendering → rendered (or rendering → failed)
- `create_content_from_render(project_id, render_job_id) → ContentItem`
  - Creates ContentItem linked to RenderJob
  - ContentItem status: in_production → rendered → needs_review
- `run_technical_qa(project_id, content_item_id) → ContentItem`
  - Extended to handle media QA (resolution, duration, audio, subtitles)

#### Workstream 2B: Asset Validator for Production Pipeline
**File:** `core/tools/validators.py` (new)
- Adapt logic from `video-assembler/src/asset_validator.py`
- `validate_image(path) → dict`  (resolution, format, file size, corruption check)
- `validate_audio(path) → dict`  (duration, bitrate, channels, corruption check)
- `validate_video(path) → dict`  (resolution, duration, codec, audio presence)
- `validate_font(path) → dict`   (file exists, format check)
- `validate_production_assets(brief, project_root) → AssetReport`

#### Workstream 2C: FileSystem Repositories for RenderJob and OutputFile
**File:** `core/services/production_pipeline.py` (extend)
- `FileSystemRenderJobRepository(FileSystemProjectModelRepository[RenderJob])`
  - Storage: `projects/{project_id}/data/render_jobs/`
- `FileSystemOutputFileRepository(FileSystemProjectModelRepository[OutputFile])`
  - Storage: `projects/{project_id}/data/output_files/`

#### Workstream 2D: QA Checker Integration
**File:** `core/tools/qa.py` (new)
- Adapt logic from `video-assembler/src/qa_checker.py`
- `QAResult` dataclass (passed, errors, warnings, video_playable, has_audio,
  duration_sec, resolution, bitrate_kbps, subtitle_count)
- `check_video_output(video_path) → QAResult`
- `check_carousel_output(carousel_dir) → QAResult`
- `format_qa_result(result, label) → str`

### Sub-Agent Dispatch Strategy

| Sub-agent | Workstream | Parallel |
|---|---|---|
| Agent A | 2A: ProductionPipelineService core | After reading 2B-2D signatures |
| Agent B | 2B: Asset validators | Yes |
| Agent C | 2C: RenderJob/OutputFile repos | Yes |
| Agent D | 2D: QA checker | Yes |

Lead agent integrates: wires validators, QA checker, and repos into
ProductionPipelineService.

### Acceptance Criteria

```
[ ] ProductionPipelineService.create_render_job() creates persistent RenderJob
[ ] ProductionPipelineService.validate_assets() detects missing files
[ ] ProductionPipelineService.validate_assets() detects wrong resolution images
[ ] ProductionPipelineService.execute_render() creates stub OutputFile (mock FFmpeg)
[ ] ProductionPipelineService.create_content_from_render() creates ContentItem
[ ] ContentItem flows: DRAFT → IN_PRODUCTION → RENDERED → NEEDS_REVIEW
[ ] FileSystemRenderJobRepository saves/loads correctly
[ ] FileSystemOutputFileRepository saves/loads correctly
[ ] validate_image() works for valid and corrupt PNGs
[ ] validate_audio() works for valid and silent WAVs
[ ] check_video_output() works for valid and corrupt MP4s
[ ] python -m pytest tests/services/ -v → all pass
[ ] python -m pytest tests/tools/ -v → all pass (new directory)
[ ] python scripts/smoke_loop.py → PASS (text flow unchanged)
```

### Output Files

```
MODIFIED: core/services/production_pipeline.py  (service + 3 repos)
CREATED:  core/tools/__init__.py
CREATED:  core/tools/validators.py
CREATED:  core/tools/qa.py
CREATED:  tests/services/test_production_pipeline.py
CREATED:  tests/tools/__init__.py
CREATED:  tests/tools/test_validators.py
CREATED:  tests/tools/test_qa.py
```

---

## Session 3: Video Assembler Integration + Narrative Video CLI

### Entry State

- `ProductionPipelineService` exists with stub render (creates OutputFile
  but doesn't actually render media)
- Asset validators and QA checkers exist
- `video-assembler/src/assembler.py` has full FFmpeg rendering logic
- No CLI for video production yet

### What We Build

#### Workstream 3A: Video Renderer Tool
**File:** `core/tools/video/__init__.py` (new)
**File:** `core/tools/video/renderer.py` (new)

- Adapted from `video-assembler/src/assembler.py`
- `render_narrative_video(brief: ProductionBrief, output_dir: Path, project_root: Path) → dict`
  - Reads brief.scenes
  - For each scene: image → apply zoom/pan via FFmpeg zoompan filter
  - Chain scenes with xfade transitions
  - Burn subtitles from manual SRT (generated from brief.scenes[].narration_text)
  - Mix audio: voiceover + music with ducking via FFmpeg sidechaincompress
  - Output: final_video.mp4 (1080x1920, H.264)
  - Returns dict with paths to all output artifacts
- `generate_srt_from_brief(brief: ProductionBrief) → str`
  - Builds SRT from scene narration text with timing from scene durations
- `build_video_filtergraph(brief, resolution, fps) → str`
  - Constructs FFmpeg filter complex for the full video

#### Workstream 3B: Audio Mixing with Ducking
**File:** `core/tools/video/audio.py` (new)

- `mix_audio_with_ducking(voiceover_path, music_path, output_path, ducking_db=12, music_volume=0.15) → Path`
  - Uses FFmpeg sidechaincompress for automatic ducking
  - Music lowers when voiceover is active, restores during silence
- `normalize_audio(input_path, output_path, target_db=-16) → Path`
  - LUFS normalization for consistent loudness

#### Workstream 3C: ProductionPipelineService — Wire Real Renderer
**File:** `core/services/production_pipeline.py` (modify `execute_render`)

- Replace stub with actual `render_narrative_video()` call
- Create OutputFile records for: final_video.mp4, subtitles.srt,
  audio_only.mp3, cover.png
- Set ContentItem.render_output_metadata

#### Workstream 3D: produce_video CLI
**File:** `scripts/produce_video.py` (new)

- CLI contract matching Foundation MVP scripts
- `--project-id` (required)
- `--brief` path to Production Brief JSON
- `--format` (short_vertical_video or ambient_vertical_video)
- `--dry-run` (validate only, no render)
- Human-readable output: scene list, estimated duration, asset status,
  render progress, output paths
- JSON output: structured result with all artifact paths
- Help: side-effect-free

### Sub-Agent Dispatch Strategy

| Sub-agent | Workstream | Parallel |
|---|---|---|
| Agent A | 3A: Video renderer core (FFmpeg filter graph) | Head start |
| Agent B | 3B: Audio mixing with ducking | Yes |
| Agent C | 3C: Wire renderer into ProductionPipelineService | After 2A |
| Agent D | 3D: produce_video CLI | After 2A |

Agent A is the critical path — FFmpeg filter graph is the most complex
piece. Lead agent should start Agent A first, then dispatch B-D in
parallel.

### Acceptance Criteria

```
[ ] render_narrative_video() produces playable MP4 1080x1920
[ ] Video has correct duration (sum of scene durations minus transition overlaps)
[ ] Zoom/pan effect visible on each scene
[ ] Scene transitions (dissolve/fade) work correctly
[ ] Subtitles appear at correct y_position, correct timing
[ ] Subtitles use specified font, color, stroke
[ ] Voiceover audio is audible
[ ] Music ducking: music lowers during voiceover, restores after
[ ] Audio_only.mp3 contains mixed audio track
[ ] Cover.png is first frame of video at 1080x1920
[ ] produce_video.py --help shows usage, no side effects
[ ] produce_video.py --json returns structured result
[ ] produce_video.py --dry-run validates assets without rendering
[ ] produce_video.py with missing image → clear error message
[ ] python scripts/produce_video.py --help → exit 0, no side effects
[ ] Full test suite passes
```

### Output Files

```
CREATED:  core/tools/video/__init__.py
CREATED:  core/tools/video/renderer.py
CREATED:  core/tools/video/audio.py
CREATED:  core/tools/video/safe_zones.py
MODIFIED: core/services/production_pipeline.py  (wire real renderer)
CREATED:  scripts/produce_video.py
CREATED:  tests/tools/video/__init__.py
CREATED:  tests/tools/video/test_renderer.py
CREATED:  tests/tools/video/test_audio.py
CREATED:  tests/scripts/test_produce_video.py
```

---

## Session 4: Carousel Renderer + Carousel CLI

### Entry State

- Video production pipeline operational
- `INSTAGRAM_CAROUSEL` content format defined
- `ProductionBrief` supports carousel slides
- NURA brand config with colors, fonts, gradients
- No carousel rendering logic yet

### What We Build

#### Workstream 4A: Carousel Slide Renderer
**File:** `core/tools/carousel/__init__.py` (new)
**File:** `core/tools/carousel/renderer.py` (new)

- `render_carousel(brief: ProductionBrief, output_dir: Path, project_root: Path) → dict`
  - For each slide in brief.slides:
    - Create blank canvas 1080x1350 with background (color/gradient/image)
    - Apply text: heading (brand font, large), subheading/body (body font)
    - Apply brand element (logo on first/last slides)
    - Apply safe zone margins
    - Export as PNG
  - Returns dict with slide paths and preview
- `render_slide_background(canvas, slide, brand_config) → Image`
  - Handles solid color, gradient, or background image
- `render_slide_text(canvas, slide, brand_config, safe_zones) → Image`
  - Pillow-based text rendering with brand fonts
  - Auto line-wrapping for long text
  - Position within safe zones

#### Workstream 4B: Brand Template Engine
**File:** `core/tools/carousel/templates.py` (new)

- `apply_brand_template(slide, brand_config, template_id) → dict`
  - Maps template_id (cover, quote, list, text_image, cta) to layout
  - Returns text positions, font sizes, colors, element placements
- `load_brand_config(project_root, project_id) → BrandConfig`
  - Reads from `projects/{project_id}/project.yaml` production section

#### Workstream 4C: Pipeline Integration
**File:** `core/services/production_pipeline.py` (modify `execute_render`)

- Add branch: if `brief.content_format == INSTAGRAM_CAROUSEL` →
  call `render_carousel()`
- Create OutputFile records for each slide PNG + preview

#### Workstream 4D: produce_carousel CLI
**File:** `scripts/produce_carousel.py` (new)

- Same CLI contract as produce_video.py
- `--project-id`, `--brief`, `--dry-run`
- Output: paths to all slide PNGs, preview grid, manifest

### Sub-Agent Dispatch Strategy

| Sub-agent | Workstream | Parallel |
|---|---|---|
| Agent A | 4A: Carousel renderer (slide-by-slide) | Head start |
| Agent B | 4B: Brand template engine + NURA brand config loading | Yes |
| Agent C | 4C: Wire carousel into pipeline | After 4A, 4B |
| Agent D | 4D: produce_carousel CLI | After 4A, 4B |

### Acceptance Criteria

```
[ ] render_carousel() produces correct number of PNGs (5-7)
[ ] All PNGs are 1080x1350 (4:5 aspect ratio)
[ ] Slide 1 (cover): heading + subheading, logo present
[ ] Slide N (cta): CTA button-style text, logo present
[ ] Text rendered with brand fonts (not system fallback)
[ ] Text respects safe zones
[ ] Background colors match brand config
[ ] No corrupt PNGs (all openable in image viewer)
[ ] produce_carousel.py --help → no side effects
[ ] produce_carousel.py --dry-run validates without rendering
[ ] produce_carousel.py --json returns structured result
[ ] Full test suite passes
```

### Output Files

```
CREATED:  core/tools/carousel/__init__.py
CREATED:  core/tools/carousel/renderer.py
CREATED:  core/tools/carousel/templates.py
MODIFIED: core/services/production_pipeline.py  (wire carousel renderer)
CREATED:  scripts/produce_carousel.py
CREATED:  tests/tools/carousel/__init__.py
CREATED:  tests/tools/carousel/test_renderer.py
CREATED:  tests/tools/carousel/test_templates.py
CREATED:  tests/scripts/test_produce_carousel.py
```

---

## Session 5: ExportPackage Expansion + Review CLI + End-to-End Integration

### Entry State

- Narrative video and carousel renderers operational
- `ContentItem` flows through statuses but ExportPackage still text-only
- `PublishingService.prepare_export()` only writes .txt files
- `validate_package.py` only checks text packages
- No human review CLI beyond smoke loop inspection

### What We Build

#### Workstream 5A: ExportPackage for Media
**File:** `core/services/publishing.py` (extend `prepare_export`)

- Detect `content_format` from ContentItem
- For video formats: copy MP4, SRT, cover, audio_only to export dir
- For carousel: copy all slide PNGs to `carousel/` subdirectory
- Generate `qa_report.json` with QA results
- Generate `production_snapshot.json` with render context
- Update `manifest.json` with all media file entries
- Update `caption_{platform}.txt` per target platform
- Generate `publish_notes.md` — manual publication checklist per platform

#### Workstream 5B: Extended Package Validation
**File:** `scripts/validate_package.py` (extend)

- Check video: MP4 exists, playable, correct resolution (1080x1920),
  duration within platform limits
- Check carousel: correct number of PNGs (5-10), all 1080x1350, no
  corrupt images
- Check subtitles: SRT exists, non-empty, valid timecodes
- Check captions: caption file exists for each target platform
- Check safe zones: verify text/subtitle positions (via metadata, not
  visual analysis)
- Check cover: cover.png exists, correct resolution

#### Workstream 5C: review_content CLI
**File:** `scripts/review_content.py` (new)

- `--project-id`, `--content-item-id`
- Without `--approve`: displays content summary, artifact paths, QA
  results, prompts for human review
- `--approve`: transitions ContentItem → approved → exported, creates
  ExportPackage
- `--reject --reason "..."`: transitions ContentItem → rejected
- `--json` mode for automation

#### Workstream 5D: End-to-End Smoke Test for Video
**File:** `tests/integration/test_video_e2e.py` (new)

- Create Idea → Scenario with ProductionBrief in metadata
- Create ProductionBrief
- Run ProductionPipelineService full flow
- Verify: ContentItem.status == NEEDS_REVIEW
- Approve → ExportPackage READY
- Validate package
- No mocking of FFmpeg (uses real test assets: 4 small color-block PNGs
  1080x1920, short silence WAV, short silence MP3)

#### Workstream 5E: End-to-End Smoke Test for Carousel
**File:** `tests/integration/test_carousel_e2e.py` (new)

- Same flow as video E2E but for carousel
- Test assets: 7 small PNG backgrounds, brand config

### Sub-Agent Dispatch Strategy

| Sub-agent | Workstream | Parallel |
|---|---|---|
| Agent A | 5A: ExportPackage expansion (most complex) | Head start |
| Agent B | 5B: validate_package extension | Yes |
| Agent C | 5C: review_content CLI | After 5A |
| Agent D | 5D: Video E2E test | After 5A, 5B |
| Agent E | 5E: Carousel E2E test | After 5A, 5B |

### Acceptance Criteria

```
[ ] prepare_export() for video: all media files copied to export dir
[ ] prepare_export() for carousel: all PNGs copied to carousel/ subdir
[ ] manifest.json lists all files with correct roles
[ ] qa_report.json present with pass/warnings/errors
[ ] validate_package.py passes for valid video package
[ ] validate_package.py fails with clear message for corrupt video
[ ] validate_package.py passes for valid carousel package
[ ] review_content.py --approve transitions to exported
[ ] review_content.py --reject transitions to rejected
[ ] E2E test: full Idea→ExportPackage flow for video (real FFmpeg)
[ ] E2E test: full Idea→ExportPackage flow for carousel
[ ] python scripts/smoke_loop.py → PASS (text unchanged)
[ ] Full test suite passes
```

### Output Files

```
MODIFIED: core/services/publishing.py          (prepare_export extended)
CREATED:  core/tools/packager.py               (build_export_media_package)
MODIFIED: scripts/validate_package.py           (media checks)
CREATED:  scripts/review_content.py
CREATED:  tests/integration/__init__.py
CREATED:  tests/integration/test_video_e2e.py
CREATED:  tests/integration/test_carousel_e2e.py
CREATED:  tests/integration/fixtures/           (test assets)
```

---

## Session 6: Ambient Video + Polish + Full Test Suite

### Entry State

- Narrative video fully operational
- Carousel fully operational
- ExportPipeline works end-to-end
- Ambient video format not yet implemented
- Audio ducking working but not tuned
- No smoke test for ambient format
- Test coverage may have gaps identified in Sessions 1-5

### What We Build

#### Workstream 6A: Ambient Video Renderer
**File:** `core/tools/video/renderer.py` (extend)

- `render_ambient_video(brief, output_dir, project_root) → dict`
  - Single image with slow zoom (e.g. 1.0 → 1.12 over 15s, cubic-in-out)
  - Two-phase text overlay: phase_1 at t=X, phase_2 at t=Y
  - Background music (no voiceover in this slice, but `voiceover_enabled`
    flag in brief prepared for future TTS)
  - Brand elements: logo, website text at defined intervals
  - Output: final_video.mp4, cover.png, audio_only.mp3

#### Workstream 6B: TTS-Ready Brief Structure
**File:** `core/domain/models.py` (ProductionBrief model already created)

- Ensure `ProductionAudio` has `voiceover_enabled: bool = False`
- Ensure `ProductionAudio` has `tts_provider: str | None = None`
- Ensure `ProductionAudio` has `tts_profile: str | None = None`
- Ensure `ProductionAudio` has `tts_text: str | None = None`
- When `voiceover_enabled=True` in the future: TTS synthesizes
  `tts_text` with `tts_provider` using `tts_profile`, saves to
  `voiceover_path`

#### Workstream 6C: Ducking Tuning and Audio Tests
**File:** `core/tools/video/audio.py` (extend)

- Parameterize ducking: threshold, attack, release, ratio
- Add `DuckingConfig` dataclass
- Test with real voiceover + music files
- Verify music level difference: during speech vs silence ≥ ducking_reduction_db

#### Workstream 6D: Ambient Video E2E Test
**File:** `tests/integration/test_ambient_e2e.py` (new)

- Full Idea→ExportPackage flow for ambient format
- 1 test image + music → 15s MP4 with text phases

#### Workstream 6E: Documentation Update
**File:** `docs/04_production/PRODUCTION_PIPELINE_SPEC.md` (update if needed)
**File:** `docs/07_projects/nura/VALIDATION_PLAN.md` (update: add media formats)
**File:** `docs/04_production/PRODUCTION_LAYER_IMPLEMENTATION_PLAN.md` (mark complete)

#### Workstream 6F: Full Test Suite Verification + Edge Cases
- All 3 formats tested with valid and edge-case inputs
- Missing asset → clear error, no crash
- Wrong resolution image → warning
- Empty narration text → valid SRT with empty cues
- Very long text → line-wrapped correctly in subtitles
- Music without voiceover → no ducking, just normalize
- Special characters in Russian text → render correctly

### Sub-Agent Dispatch Strategy

| Sub-agent | Workstream | Parallel |
|---|---|---|
| Agent A | 6A: Ambient video renderer | Head start |
| Agent B | 6B: TTS-ready brief verification | Yes |
| Agent C | 6C: Ducking tuning + audio tests | Yes |
| Agent D | 6D: Ambient E2E test | After 6A |
| Agent E | 6E: Documentation update | Yes |
| Agent F | 6F: Edge case tests + full suite run | After all |

### Acceptance Criteria

```
[ ] render_ambient_video() produces playable MP4 15-20s
[ ] Slow zoom visible throughout video
[ ] Two text phases appear and disappear at correct times
[ ] Brand logo/website visible at correct positions
[ ] Music plays at correct volume (no ducking needed if no voiceover)
[ ] ProductionAudio supports future TTS fields (voiceover_enabled, tts_provider, etc.)
[ ] Ducking test: audio analysis confirms music reduction during speech
[ ] Ambient E2E test passes
[ ] All 3 format E2E tests pass
[ ] Missing asset test: clear error, no traceback
[ ] Wrong resolution test: warning, render proceeds
[ ] Russian text renders correctly in subtitles and carousel
[ ] python -m pytest tests/ -v → ALL pass (target: 230+ tests)
[ ] python scripts/smoke_loop.py → PASS
[ ] git status clean (no unexpected artifacts)
[ ] docs updated with new production capabilities
```

### Output Files

```
MODIFIED: core/tools/video/renderer.py          (+render_ambient_video)
MODIFIED: core/tools/video/audio.py             (+DuckingConfig, tuning)
MODIFIED: core/domain/models.py                  (verify TTS fields on ProductionAudio)
MODIFIED: docs/04_production/PRODUCTION_PIPELINE_SPEC.md
MODIFIED: docs/07_projects/nura/VALIDATION_PLAN.md
MODIFIED: docs/04_production/PRODUCTION_LAYER_IMPLEMENTATION_PLAN.md
CREATED:  tests/integration/test_ambient_e2e.py
CREATED:  tests/tools/video/test_audio_ducking.py
```

---

# 3. Post-Implementation: Operator Workflow

After all 6 sessions are complete, the operator can produce NURA Week 1
content as follows:

## 3.1. Narrative Video

```bash
# 1. Prepare assets manually (one-time per video)
#    projects/nura/assets/week1/video_01/
#      scene_01_hook.png       1080x1920
#      scene_02_context.png    1080x1920
#      scene_03_value.png      1080x1920
#      scene_04_cta.png        1080x1920
#      voiceover_01.wav        pre-recorded voiceover
#      bg_music_calm.mp3       background music

# 2. Write Production Brief (manual or AI-assisted)
#    projects/nura/production/week1/video_01_brief.json

# 3. Render
python scripts/produce_video.py \
  --project-id nura \
  --brief projects/nura/production/week1/video_01_brief.json

# 4. Review
python scripts/review_content.py \
  --project-id nura \
  --content-item-id content_abc123

# 5. Approve → ExportPackage
python scripts/review_content.py \
  --project-id nura \
  --content-item-id content_abc123 \
  --approve

# 6. Validate
python scripts/validate_package.py \
  --project-id nura \
  --package-id export_def456

# 7. Publish manually using publish_notes.md
```

## 3.2. Instagram Carousel

```bash
python scripts/produce_carousel.py \
  --project-id nura \
  --brief projects/nura/production/week1/carousel_01_brief.json

# Same review → approve → validate → publish flow
```

## 3.3. Ambient Video

```bash
python scripts/produce_video.py \
  --project-id nura \
  --brief projects/nura/production/week1/ambient_01_brief.json \
  --format ambient_vertical_video

# Same review → approve → validate → publish flow
```

---

# 4. Risk Mitigation

| Risk | Mitigation |
|---|---|
| FFmpeg not available on operator machine | `imageio-ffmpeg` bundles FFmpeg; tested in video-assembler already |
| Cyrillic fonts not rendering | Fallback chain: brand font → Arial → DejaVu Sans; font validation in asset checker |
| Large images (4K+) slow FFmpeg | Asset validator warns; resize to 1080x1920 before render |
| Pillow text rendering poor quality | Use Pillow `ImageFont.truetype()` with large point size; test with Russian text |
| Session context lost between chats | Each session has entry/exit states; agent reads codebase fresh |
| Existing tests break | Smoke loop after every session; full test suite before declaring complete |
| NURA leaks into core | Code review checklist in each session explicitly checks for project-agnostic purity |

---

# 5. Dependency Graph Between Sessions

```
Session 1 (Domain + Config)
    │
    ▼
Session 2 (Service Layer)
    │
    ├──────────────────────┐
    ▼                      ▼
Session 3 (Video)    Session 4 (Carousel)
    │                      │
    └──────────┬───────────┘
               ▼
        Session 5 (Export + Integration)
               │
               ▼
        Session 6 (Ambient + Polish)
```

Sessions 3 and 4 can potentially run in parallel (different agents,
different chats) since they share no code dependencies — both depend only
on Session 2's service layer. However, the plan sequences them to allow
learning from Session 3's video patterns to inform Session 4's carousel
design.

---

# 6. Test Suite Evolution

| After Session | Expected Min Tests | New Test Files |
|---|---|---|
| 1 | 200+ | test_production_brief.py, test_tts.py |
| 2 | 215+ | test_production_pipeline.py, test_validators.py, test_qa.py |
| 3 | 230+ | test_renderer.py, test_audio.py, test_produce_video.py |
| 4 | 240+ | test_carousel_renderer.py, test_carousel_templates.py, test_produce_carousel.py |
| 5 | 255+ | test_video_e2e.py, test_carousel_e2e.py, test_review_content.py |
| 6 | 260+ | test_ambient_e2e.py, test_audio_ducking.py, edge case tests |

---

# 7. Document Status

| Field | Value |
|---|---|
| Status | Planning — Ready for Execution |
| Version | 1.0 |
| Date | 2026-07-17 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Production Layer — Implementation Plan |
| Sessions | 6 sessions, sequential execution |
| Target | NURA Week 1 content production baseline |

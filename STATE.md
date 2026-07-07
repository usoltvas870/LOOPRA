# Content Plant State

Last updated: 2026-07-07 (first real NURA content validation)

## Current Status

- Content Plant project-agnostic foundation is committed, pushed to `main`, operationally verified, and ready for the next implementation tasks.
- Working tree at the operational acceptance test checkpoint should be clean.
- Latest relevant commits:
  - (pending) Record first real NURA content validation
  - `c1654b7` Update STATE.md with NURA validation skeleton commit
  - `43178b5` Add NURA validation project skeleton
  - `7ada027` Add developer quickstart
  - `a6b9cb6` Mark foundation MVP ready
  - `718dc4b` Quarantine legacy specs from foundation MVP
  - `8be5876` Add manual metrics workflow smoke test
  - `1590159` Add draft metric snapshot finder
  - `8ec8c57` Add manual metrics import helper
  - `1fc1862` Add export package validation helper
  - `63e8143` Add export package inspection helper
  - `8b53b67` Add export package manifest
  - `2640366` Add end-to-end loop smoke script
  - `3e799ec` Enhance manual metric snapshots
  - `d2a7d7e` Enhance manual publication records

## Baseline Guarantees

- The platform foundation is project-agnostic.
- NURA is not part of the platform foundation and may only be introduced later as a validation project.
- No NURA-specific logic, assets, config, templates, prompts or packages are included in the foundation baseline.
- `graphify-out/` is generated local output, ignored by Git and must not be committed.

## Implemented Foundation

- Canonical domain layer in `core/domain`.
- Project services and project config binding.
- `IdeaService`.
- `ScenarioService`.
- `ProductionLifecycleService`.
- `PublishingService`.
- `AnalyticsService`.
- Thin `LoopOrchestrator`.
- Filesystem-based persistence.

## Current Foundation Status

- The current foundation MVP supports content loop creation from `Idea` through draft `MetricSnapshot`.
- Export package generation is implemented for the minimal `text_social_post` loop.
- Prepared export packages can be inspected through `scripts/inspect_package.py`.
- Prepared export packages can be validated through `scripts/validate_package.py`.
- Manual publication record support is implemented through `Publication`.
- Draft `MetricSnapshot` creation is implemented for the local/manual metrics path.
- Draft `MetricSnapshot` lookup is implemented through `scripts/find_metric_snapshots.py`.
- Manual metrics import is implemented through `scripts/import_manual_metrics.py`.
- End-to-end manual metrics workflow smoke coverage is implemented through `tests/services/test_manual_metrics_workflow.py`.

## Current MVP Flow

```text
Idea → Scenario → ContentItem → ExportPackage v1 → Manual Publication Record v1 → MetricSnapshot v1
```

## Export Package v1

- Current safest MVP content format is `text_social_post`.
- MVP remains export-first and manual-publication-first.
- `text_social_post ExportPackage v1` writes:
  - `title.txt`
  - `body.txt`
  - `caption_{platform}.txt`
  - `manual_publication_checklist.txt`
  - `metadata.json`
  - `manifest.json`
- Export preparation is owned by `Publishing Hub`.
- `manifest.json` is a neutral package inspection layer written by `Publishing Hub` during `prepare_export()`.
- `manifest.json` is derived only from existing package, content item and scenario data.
- `manifest.json` is intended to make prepared export packages easier to inspect manually and easier to support in future tooling, UI, CLI or API layers.
- `manifest.json` is not itself a UI, API, autoposting feature or external platform integration.
- `manifest.json` currently includes neutral fields such as:
  - `package_id`
  - `project_id`
  - `content_item_id`
  - `scenario_id`
  - `content_format`
  - `target_platform`
  - `manual_publication_only`
  - `prepared_at`
  - `status`
  - `files`
- `manifest.json.files` uses relative file names and roles only; it does not include absolute local machine paths.
- No autoposting is included in this checkpoint.

## Manual Publication Record v1

- Manual publication metadata is recorded in `Publication`.
- When manually marked as published, the record stores `published_url` and `published_at`.
- Manual publication notes preserve publication metadata for the current MVP flow.
- No external platform APIs are used.
- No autoposting is included.

## MetricSnapshot v1

- `MetricSnapshot v1` records manually provided metrics only.
- Manual metric input currently accepted in code:
  - `views`
  - `likes`
  - `comments`
  - `shares`
  - `saves`
  - `clicks`
  - `published_url`
- Stored snapshot metrics include the directly stored engagement fields plus `link_clicks`.
- Normalization behavior:
  - `clicks` is accepted as input and stored as `link_clicks`
  - `published_url` is accepted as input and updates the related `Publication.published_url`
  - `published_url` is not stored as a `MetricSnapshot.content_metrics` field
- Current implementation does not fetch external analytics.
- Current implementation does not generate insights.
- Current implementation does not generate new ideas from analytics.
- The smoke loop creates `MetricSnapshot` in `draft` / unrecorded status.

## Draft MetricSnapshot Finder Helper

- Script path: `scripts/find_metric_snapshots.py`
- Run command:

```bash
python scripts/find_metric_snapshots.py <project_id>
```

- The helper is developer-only and read-only.
- The helper lists draft / unrecorded `MetricSnapshot` records for a project.
- The helper helps find the `metric_snapshot_id` needed by `python scripts/import_manual_metrics.py <manual_metrics_json>`.
- `CONTENT_PLANT_PROJECTS_ROOT` can be used when the helper must target local/runtime project storage, for example smoke runtime data under `storage/smoke_projects/...`.
- The helper reads local project storage and filters out recorded / non-draft snapshots.
- Example local smoke usage:

```bash
python scripts/smoke_loop.py
CONTENT_PLANT_PROJECTS_ROOT=storage/smoke_projects python scripts/find_metric_snapshots.py example
```

- The helper does not write files and does not create runtime artifacts.
- The helper does not record metrics.
- The helper does not generate insights.
- The helper does not generate new ideas.
- The helper is not a product UI, not an API, not autoposting logic, not external analytics, and not a full CLI framework.

## Manual Metrics Import Helper

- Script path: `scripts/import_manual_metrics.py`
- Run command:

```bash
python scripts/import_manual_metrics.py <manual_metrics_json>
```

- The helper is developer-only and imports manually collected metrics from a local JSON file.
- The helper uses existing `AnalyticsService.record_metrics(...)`.
- The helper records metrics into an existing `MetricSnapshot`.
- Supported manual metric keys currently accepted by the helper:
  - `views`
  - `likes`
  - `comments`
  - `shares`
  - `saves`
  - `clicks`
  - `published_url`
- Current helper behavior preserves existing analytics rules:
  - `clicks` maps to stored `link_clicks`
  - `published_url` updates the related `Publication`
  - `published_url` is not written into `MetricSnapshot.content_metrics`
  - unsupported keys are rejected
  - empty metrics are rejected
- Current expected JSON shape:

```json
{
  "project_id": "example",
  "metric_snapshot_id": "metric_...",
  "metrics": {
    "views": 100,
    "likes": 12,
    "comments": 3,
    "shares": 1,
    "saves": 2,
    "clicks": 5,
    "published_url": "https://example.invalid/post/123"
  }
}
```

- `CONTENT_PLANT_PROJECTS_ROOT` can be used when the helper must target local/runtime project storage, for example smoke runtime data under `storage/smoke_projects/...`.
- The helper does not call external analytics APIs, does not generate insights, does not generate new ideas, and does not create runtime artifacts.
- The helper is not a product UI, not an API, not autoposting logic, and not a full CLI framework.

## Manual Metrics Workflow Smoke

- Test path: `tests/services/test_manual_metrics_workflow.py`
- The workflow is developer-only smoke/test coverage for the full local manual metrics path.
- The workflow uses the existing smoke and helper scripts instead of adding a new orchestration engine.
- The workflow verifies that `scripts/smoke_loop.py` creates the generic local loop and a draft `MetricSnapshot`.
- The workflow verifies that `scripts/find_metric_snapshots.py` can locate the draft `MetricSnapshot`.
- The workflow verifies that `scripts/import_manual_metrics.py` can import manual metrics from JSON.
- The workflow verifies that the imported `MetricSnapshot` becomes `recorded`.
- The workflow verifies that `views`, `likes`, `comments`, `shares`, and `saves` persist.
- The workflow verifies that `clicks` maps to stored `link_clicks`.
- The workflow verifies that `published_url` updates the related `Publication`.
- The workflow verifies that `AnalyticsService.get_insights(...)` remains `[]`.
- The workflow verifies that `AnalyticsService.generate_new_ideas_from_metrics(...)` remains `[]`.
- The workflow verifies that no new `Idea` records are created by the manual metrics workflow.
- No new user-facing script was added for this checkpoint.
- No core services changed in this checkpoint.

## Locked Architecture Decisions

- `ExportPackage` belongs to `Publishing Hub`.
- `Production Engine` owns `RenderJob`, `OutputFile`, `ContentItem`, technical QA result and render output metadata.
- `Publishing Hub` owns `ExportPackage`, platform-ready package, caption variants, publication preparation, manual publication record and `Publication` status.
- The first safest MVP content format is `text_social_post`.
- Project-specific source of truth uses a hybrid model:
  - human-readable project docs: `docs/07_projects/{project_slug}/`
  - machine-readable config: `projects/{project_id}/project.yaml`

## Smoke Script

- Script path: `scripts/smoke_loop.py`
- Run command:

```bash
python scripts/smoke_loop.py
```

- The script runs a generic project through the current MVP loop and prints the created entity ids, export directory path, generated export files and final statuses.
- Current generated export files for the smoke loop include:
  - `title.txt`
  - `body.txt`
  - `caption_{platform}.txt`
  - `manual_publication_checklist.txt`
  - `metadata.json`
  - `manifest.json`
- Runtime smoke artifacts are written under `storage/smoke_projects/...`.
- Generated smoke runtime artifacts are local-only and must not be committed.

## Package Inspection Helper

- Script path: `scripts/inspect_package.py`
- Run command:

```bash
python scripts/inspect_package.py <export_package_directory>
```

- The helper is developer-only and reads `manifest.json` from an existing export package directory.
- The helper prints a concise human-readable package summary to stdout.
- The helper validates required manifest fields needed for package inspection.
- The helper fails clearly when the export package directory is missing, `manifest.json` is missing, `manifest.json` is invalid JSON, or required manifest fields are missing.
- The helper rejects absolute paths in `manifest.json.files` entries and prints only relative file names from the manifest.
- The helper does not write files and does not create runtime artifacts.
- The helper is not a product UI, not an API, not autoposting logic, and not a full CLI framework.

## Package Validation Helper

- Script path: `scripts/validate_package.py`
- Run command:

```bash
python scripts/validate_package.py <export_package_directory>
```

- The helper is developer-only and reads `manifest.json` from an existing export package directory.
- The helper validates package completeness and internal consistency.
- The helper validates required manifest fields needed for package validation.
- The helper validates `manifest.json.files` as a list of file entries with required `name` and `role` fields.
- The helper rejects absolute paths in `manifest.json.files` entries.
- The helper verifies that every file listed in `manifest.json.files` exists on disk.
- The helper verifies that `metadata.json` exists and is valid JSON.
- The helper verifies that `manual_publication_checklist.txt` exists.
- The helper verifies that expected package content files exist:
  - `title.txt`
  - `body.txt`
  - `caption_{target_platform}.txt`
- The helper verifies that `manual_publication_only` is `true`.
- The helper verifies that the current prepared export package status is `ready`.
- The helper does not write files and does not create runtime artifacts.
- The helper is not a product UI, not an API, not autoposting logic, not external analytics, and not a full CLI framework.

## Current Dev Workflow

- Run the generic smoke loop:

```bash
python scripts/smoke_loop.py
```

- Inspect the generated export package:

```bash
python scripts/inspect_package.py <export_directory_from_smoke_output>
```

- Validate the generated export package:

```bash
python scripts/validate_package.py <export_directory_from_smoke_output>
```

- Find the created draft `MetricSnapshot` id in local smoke runtime storage:

```bash
CONTENT_PLANT_PROJECTS_ROOT=storage/smoke_projects python scripts/find_metric_snapshots.py example
```

- Import manually collected metrics into the created draft `MetricSnapshot`:

```bash
python scripts/import_manual_metrics.py <manual_metrics_json>
```

- `smoke_loop.py` creates a generic smoke export package under `storage/smoke_projects/...`.
- `smoke_loop.py` also creates a generic draft / unrecorded `MetricSnapshot`.
- `inspect_package.py` prints a human-readable package summary from `manifest.json`.
- `validate_package.py` checks whether the package is complete and ready for manual publication.
- `find_metric_snapshots.py` finds the draft `metric_snapshot_id` needed for manual metrics import.
- `import_manual_metrics.py` records manual metrics through existing `AnalyticsService` service rules.
- The current local/manual metrics workflow is covered by `tests/services/test_manual_metrics_workflow.py`.
- Generated smoke runtime artifacts are local-only and must not be committed.

## Current MVP Boundaries

- No API or UI.
- No database layer or migrations.
- No SaaS, billing, users, roles or marketplace.
- No autoposting.
- No external analytics APIs.
- No external APIs.
- No `HyperFrames`, FFmpeg flows or `video-assembler/`.
- No `Trend Radar`.
- No project-specific hardcode in platform-level code or docs.
- No NURA-specific foundation logic, assets, templates, prompts or packages.
- No generated insights or new ideas from metrics in the current foundation checkpoint.
- The minimal `text_social_post` foundation loop does not require real render.
- `RenderJob` and `OutputFile` are not mandatory for the current minimal loop unless a future task explicitly introduces them.

## Validation Snapshot

- Manual metrics workflow smoke checkpoint is committed and pushed to `main`.
- Latest relevant helper checkpoint:
  - `8be5876` Add manual metrics workflow smoke test
  - `1590159` Add draft metric snapshot finder
  - `8ec8c57` Add manual metrics import helper
  - `1fc1862` Add export package validation helper
  - `63e8143` Add export package inspection helper
- The minimal loop is runnable end-to-end through `python scripts/smoke_loop.py`.
- Prepared export packages can be inspected through `python scripts/inspect_package.py <export_package_directory>`.
- Prepared export packages can be validated through `python scripts/validate_package.py <export_package_directory>`.
- Draft `MetricSnapshot` records can be listed through `python scripts/find_metric_snapshots.py <project_id>`.
- Draft `MetricSnapshot` records can be populated through `python scripts/import_manual_metrics.py <manual_metrics_json>`.
- The full local/manual metrics workflow is covered through `python -m unittest tests.services.test_manual_metrics_workflow -v`.
- Working tree should be clean at checkpoint handoff.

## Foundation MVP Ready Checkpoint

- Foundation MVP status: READY
- Audit-lite passed after `718dc4b Quarantine legacy specs from foundation MVP`.
- Tests: `107/107 OK`.
- `python -m compileall core` and `python -m compileall scripts`: OK.
- Smoke/dev workflow: OK.
- Package inspection/validation: OK.
- Manual metrics workflow: OK.
- Project-specific leakage: clean.
- Generated/runtime artifacts: ignored.
- Legacy/spec docs: quarantined with `Legacy / future-scope note`.

Current foundation MVP loop:

```text
Idea -> Scenario -> ContentItem -> ExportPackage v1 -> Manual Publication Record v1 -> MetricSnapshot v1
```

Current developer helpers:

```bash
python scripts/smoke_loop.py
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

Current source-of-truth docs:

- `STATE.md`
- `AGENTS.md`
- `docs/00_index.md`
- `docs/PLATFORM_OVERVIEW.md`
- `docs/MVP_SCOPE.md`
- `docs/DATA_MODEL.md`
- `docs/PIPELINES_SPEC.md`
- `docs/CONTENT_FORMATS_OVERVIEW.md`
- `docs/PRODUCT_STRATEGY.md`
- `docs/WORKSPACE_AND_PROJECT_MODEL.md`
- `docs/AGENT_RULES.md`
- `docs/USER_WORKFLOWS.md`

Legacy/spec docs with `Legacy / future-scope note` are not current foundation MVP source of truth.
They must not be used to expand scope unless a future Architecture Gate explicitly reactivates them.

Boundaries remain unchanged:

- no API/UI
- no DB/migrations
- no SaaS/billing/users/roles/marketplace
- no autoposting
- no external APIs
- no external analytics APIs
- no HyperFrames/FFmpeg/video assembler
- no Trend Radar implementation
- no generated insights/new ideas from metrics
- no project-specific hardcode
- no NURA validation project yet

## Current Guidance

- Read `STATE.md` first at the start of a new Codex session.
- Keep platform work project-agnostic.
- Keep project-specific rules and assets out of the platform foundation.
- Use NURA only later as a validation project, not as a platform default.
- Project-specific logic may live only in:
  - `docs/07_projects/{project_slug}/`
  - `projects/{project_id}/project.yaml`
- Do not commit `graphify-out/`.
- Do not commit generated smoke runtime artifacts under `storage/smoke_projects/...`.
- Post-commit `graphify-out/` rebuilds must not be treated as source changes.
- Do not mix `ContentItem` status and `Publication` status.
- Do not mix Content Analytics and Product Analytics.

## Agent Operating Model

- Default mode: Fast Loop.
- Operating model:
  - `Chat defines task contract -> Codex implements -> user brings report back to Chat -> Chat reviews and chooses next step`
- CLI review is not needed for small docs, config or test tasks.
- Use CLI copilot-agent only for guarded or high-risk tasks such as:
  - domain model changes
  - storage or persistence changes
  - large diffs
  - new service layers
  - project config format changes
  - external integrations
  - API, UI, DB, render or autoposting work
  - validation-project introduction

## Operational Acceptance Test v1

- Operational Acceptance Test v1: PASS
- Foundation MVP status: READY + OPERATIONALLY VERIFIED
- Test run after: `7ada027 Add developer quickstart`
- All 14 operational steps passed.

Verified path:

- git baseline: clean working tree, latest commit `7ada027`
- full test suite: 107/107 OK
- compile checks: `core` and `scripts` OK
- `scripts/smoke_loop.py`: end-to-end loop completed
- `scripts/inspect_package.py`: content_format=text_social_post, target_platform=telegram, status=ready, manual_publication_only=true
- `scripts/validate_package.py`: validation_status=ok, ready_for_manual_publication=true
- `scripts/find_metric_snapshots.py`: draft MetricSnapshot found
- manual metrics JSON creation: OK
- `scripts/import_manual_metrics.py`: metrics_import_status=ok, recorded_keys=views,likes,comments,shares,saves,clicks,published_url
- MetricSnapshot moved from draft to recorded
- MetricSnapshot content_metrics: views=123, likes=17, comments=4, shares=2, saves=5, link_clicks=9
- MetricSnapshot raw `clicks` not stored, raw `published_url` not stored in content_metrics
- Publication.published_url updated to test URL
- generated/runtime artifacts: ignored

Scope remains unchanged:

- no API/UI
- no DB/migrations
- no SaaS/billing/users/roles/marketplace
- no autoposting
- no external APIs
- no external analytics APIs
- no render/video/HyperFrames/FFmpeg
- no Trend Radar implementation
- NURA validation skeleton created, smoke loop passed

Next recommended direction:

- NURA manual metrics import (next in validation pipeline)
- or: NURA-specific content generation
- or: next content format planning
- Do not start any of these without explicit task.

## Next Task Direction

- NURA manual metrics import (after real manual publication)
- or: next NURA text_social_post (next content pillar)
- or: next content format planning
- Do not start any of these without explicit task.

---

## NURA Validation Skeleton

Status: READY
Architecture Gate: Accepted
First NURA Smoke Loop: PASS
NURA Export Package: inspect OK, validate OK
Draft MetricSnapshot: created and found
Foundation Leakage Check: PASS (no NURA in core/scripts/tests)
Scope: `text_social_post` only, manual publication only

### Added Under This Milestone

```text
projects/nura/project.yaml                     — NURA project config (ProjectConfig schema)
docs/07_projects/nura/README.md                — NURA validation project overview
docs/07_projects/nura/POSITIONING.md           — NURA positioning and audience
docs/07_projects/nura/TONE_OF_VOICE.md         — NURA tone of voice rules
docs/07_projects/nura/CONTENT_PILLARS.md       — NURA content pillars
docs/07_projects/nura/VALIDATION_PLAN.md       — NURA validation plan and criteria
```

### Updated Foundation Files

```text
.gitignore                                      — added projects/nura/* exception for project.yaml
tests/services/test_projects.py                 — project-agnostic list_projects assertion
```

### Verified

```text
Foundation tests: 107/107 OK
NURA smoke loop: Idea -> Scenario -> ContentItem -> ExportPackage -> Publication -> MetricSnapshot
NURA export package: title.txt, body.txt, caption_telegram.txt, manual_publication_checklist.txt, metadata.json, manifest.json
NURA package inspection: OK (content_format=text_social_post, target_platform=telegram, status=ready)
NURA package validation: OK (validation_status=ok, ready_for_manual_publication=true)
NURA draft MetricSnapshot: found via find_metric_snapshots.py
NURA leakage check: no NURA references in core/, scripts/, tests/
compileall core: OK
compileall scripts: OK
```

### Boundaries Preserved

```text
No changes to core/
No changes to scripts/
No API/UI
No DB/migrations
No SaaS/billing/users/roles/marketplace
No autoposting
No external APIs
No external analytics APIs
No video/render/HyperFrames/FFmpeg
No Trend Radar
No generated insights or new ideas from metrics
No NURA hardcode in foundation
No runtime artifacts committed (storage/smoke_projects/ ignored)

## First Real NURA Text Social Post Validation

Status: PASS

First real NURA-specific `text_social_post` content was generated and validated.

Export package: `export_806ee39bdf66`  
Content format: `text_social_post`  
Target platform: `telegram`  
Manual publication readiness: `true`

### Generated IDs

```text
idea_id=idea_c191ccaf2dc5
scenario_id=scenario_6d502c10a623
content_item_id=content_629193f7ef86
export_package_id=export_806ee39bdf66
publication_id=publication_f0f6d21d7724
metric_snapshot_id=metric_fc092922555d
```

### Verification

```text
Inspect: OK (package_id=export_806ee39bdf66, content_format=text_social_post, status=ready)
Validate: OK (validation_status=ok, ready_for_manual_publication=true)
Draft MetricSnapshot: found via find_metric_snapshots.py
CTA: https://nura-ai.ru
Content quality: matches NURA tone/pillars, avoids forbidden claims (no therapy, no fortune-telling, no deterministic predictions, no fear pressure)
QA warnings: none
```

### Content Topic

```text
Почему человек снова и снова попадает в похожие отношения
```

Content pillar: Relationships and Emotional Patterns.

### Non-Goals Preserved

```text
Metrics import: not performed (no real manual publication yet)
Temporary generator: removed, not committed
Foundation core/: unchanged
Foundation tests/: unchanged
All 107 foundation tests: OK
Leakage check: PASS (no NURA in core/scripts/tests)
Runtime artifacts: not committed (storage/smoke_projects/ ignored)
```
```

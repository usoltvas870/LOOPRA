# Content Plant State

Last updated: 2026-07-07

## Current Status

- Content Plant project-agnostic foundation is committed, pushed to `main`, and ready for the next implementation tasks.
- Working tree at the manual metrics import helper checkpoint should be clean.
- Latest relevant commits:
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
- Supported stored metric keys currently implemented in code:
  - `views`
  - `likes`
  - `comments`
  - `shares`
  - `saves`
  - `clicks`
  - `published_url`
- Current implementation does not fetch external analytics.
- Current implementation does not generate insights.
- Current implementation does not generate new ideas from analytics.
- The smoke loop creates `MetricSnapshot` in `draft` / unrecorded status.

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

- Import manually collected metrics into the created draft `MetricSnapshot`:

```bash
python scripts/import_manual_metrics.py <manual_metrics_json>
```

- `smoke_loop.py` creates a generic smoke export package under `storage/smoke_projects/...`.
- `smoke_loop.py` also creates a generic draft / unrecorded `MetricSnapshot`.
- `inspect_package.py` prints a human-readable package summary from `manifest.json`.
- `validate_package.py` checks whether the package is complete and ready for manual publication.
- `import_manual_metrics.py` records manual metrics through existing `AnalyticsService` service rules.
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

- Manual metrics import helper checkpoint is committed and pushed to `main`.
- Latest relevant helper checkpoint:
  - `8ec8c57` Add manual metrics import helper
  - `1fc1862` Add export package validation helper
  - `63e8143` Add export package inspection helper
- The minimal loop is runnable end-to-end through `python scripts/smoke_loop.py`.
- Prepared export packages can be inspected through `python scripts/inspect_package.py <export_package_directory>`.
- Prepared export packages can be validated through `python scripts/validate_package.py <export_package_directory>`.
- Draft `MetricSnapshot` records can be populated through `python scripts/import_manual_metrics.py <manual_metrics_json>`.
- Working tree should be clean at checkpoint handoff.

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

## Next Task Direction

- Continue implementation on top of the committed manual metrics import helper checkpoint.
- Preserve export-first and manual-publication-first MVP boundaries.
- Keep new platform work generic enough to support multiple projects.

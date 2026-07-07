# Content Plant State

Last updated: 2026-07-07

## Current Status

- Content Plant project-agnostic foundation is committed, pushed to `main`, and ready for the next implementation tasks.
- Working tree at the smoke loop checkpoint should be clean.
- Latest relevant commits:
  - `2640366` Add end-to-end loop smoke script
  - `3e799ec` Enhance manual metric snapshots
  - `d2a7d7e` Enhance manual publication records
  - `70e46a4` Enhance text social post export package

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
- Export preparation is owned by `Publishing Hub`.
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
- Runtime smoke artifacts are written under `storage/smoke_projects/...`.
- Generated smoke runtime artifacts are local-only and must not be committed.

## Current MVP Boundaries

- No API or UI.
- No database layer or migrations.
- No SaaS, billing, users, roles or marketplace.
- No autoposting.
- No external APIs.
- No `HyperFrames`, FFmpeg flows or `video-assembler/`.
- No `Trend Radar`.
- No project-specific hardcode in platform-level code or docs.
- No NURA-specific foundation logic, assets, templates, prompts or packages.
- The minimal `text_social_post` foundation loop does not require real render.
- `RenderJob` and `OutputFile` are not mandatory for the current minimal loop unless a future task explicitly introduces them.

## Validation Snapshot

- Smoke loop checkpoint is committed and pushed to `main`.
- Working tree should be clean at checkpoint handoff.
- The minimal loop is now runnable end-to-end through `python scripts/smoke_loop.py`.

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

- Continue implementation on top of the committed smoke loop checkpoint.
- Preserve export-first and manual-publication-first MVP boundaries.
- Keep new platform work generic enough to support multiple projects.

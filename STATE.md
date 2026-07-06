# Content Plant State

Last updated: 2026-07-06

## Current Status

- Content Plant foundation baseline is committed and pushed to `main`.
- Latest baseline commits:
  - `7504449` Ignore graphify generated output
  - `fcaf743` Project-agnostic foundation services and loop skeleton
- The repository baseline is currently stable and ready for the next implementation tasks.

## Baseline Guarantees

- The platform foundation is project-agnostic.
- NURA is not part of the platform foundation and may only be used later as a validation project.
- No NURA-specific logic, assets, config, templates, prompts or packages are included in the foundation baseline.
- `graphify-out/` is generated local output, ignored by Git and must not be committed.

## Implemented Foundation

- Canonical domain layer in `core/domain`.
- Project services and project config binding.
- `IdeaService`.
- `ScenarioService`.
- Minimal production lifecycle service.
- `PublishingService`.
- `AnalyticsService` placeholder.
- Thin `LoopOrchestrator`.
- Filesystem-based persistence.
- Minimal deterministic loop:
  - `Idea`
  - `Scenario`
  - `ContentItem`
  - `ExportPackage`
  - `Publication`
  - `MetricSnapshot`

## Locked Architecture Decisions

- `ExportPackage` belongs to `Publishing Hub`.
- `Production Engine` owns `RenderJob`, `OutputFile`, `ContentItem`, technical QA result and render output metadata.
- `Publishing Hub` owns `ExportPackage`, platform-ready package, caption variants, publication preparation, manual publication record and `Publication` status.
- The first safest MVP content format is `text_social_post`.
- Project-specific source of truth uses a hybrid model:
  - human-readable project docs: `docs/07_projects/{project_slug}/`
  - machine-readable config: `projects/{project_id}/project.yaml`

## Current MVP Boundaries

- MVP is export-first.
- MVP is manual-publication-first.
- The first safest format is `text_social_post`.
- The minimal `text_social_post` foundation loop does not require real render.
- `RenderJob` and `OutputFile` are not mandatory for the current minimal foundation loop unless a future task explicitly introduces them.
- The current baseline proves the minimal loop:
  - `Idea -> Scenario -> ContentItem -> ExportPackage -> Publication -> MetricSnapshot`

## Out Of Scope For The Current Baseline

- Backend API.
- Frontend UI.
- Database layer and migrations.
- SaaS, billing, users, roles and marketplace.
- Autoposting.
- External APIs.
- `HyperFrames`, FFmpeg flows and `video-assembler/`.
- `Trend Radar`.
- Project-specific hardcode in platform-level code or docs.
- NURA-specific assets, templates, prompts or packages in foundation.

## Validation Snapshot

- `git status` was clean at baseline handoff.
- `python -m unittest` passed with 42 tests OK.
- Foundation baseline has been committed and pushed to `main`.

## Current Guidance

- Read `STATE.md` first at the start of a new Codex session.
- Keep platform work project-agnostic.
- Keep project-specific rules and assets out of the platform foundation.
- Use NURA only later as a validation project, not as a platform default.
- Project-specific logic may live only in:
  - `docs/07_projects/{project_slug}/`
  - `projects/{project_id}/project.yaml`
- Do not commit `graphify-out/`.
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

- Continue implementation on top of the committed foundation baseline.
- Preserve export-first and manual-publication-first MVP boundaries.
- Keep new platform work generic enough to support multiple projects.

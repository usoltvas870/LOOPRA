# Content Plant

## What It Is

Content Plant is a standalone multi-project platform for systematic content production, packaging, publishing and analytics.

Platform code and platform docs must stay project-agnostic. Do not hardcode any specific brand, product, URL, price, persona or project into the platform layer.

## Current Baseline

- Foundation baseline is committed and pushed to `main`.
- Current foundation is project-agnostic.
- NURA is not part of the platform foundation and may only be used later as a validation project in the project layer.
- No NURA-specific logic, assets, config, templates, prompts or packages are part of the foundation baseline.
- `graphify-out/` is generated local output, ignored by Git and must not be committed.
- The current foundation includes:
  - canonical domain layer in `core/domain`
  - project services and project config binding
  - `IdeaService`
  - `ScenarioService`
  - minimal production lifecycle service
  - `PublishingService`
  - `AnalyticsService` placeholder
  - thin `LoopOrchestrator`
  - filesystem-based persistence
  - minimal loop `Idea -> Scenario -> ContentItem -> ExportPackage -> Publication -> MetricSnapshot`

## Operating Model

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

## Read First

Before any task, read in this order:

1. `STATE.md`
2. `docs/00_index.md`
3. `docs/MVP_SCOPE.md`
4. `docs/DATA_MODEL.md`
5. `docs/PIPELINES_SPEC.md`
6. `docs/AGENT_RULES.md`
7. task-specific docs

## Current Architecture Decisions

- `ExportPackage` belongs to `Publishing Hub`.
- `Production Engine` owns `RenderJob`, `OutputFile`, `ContentItem`, technical QA result and render output metadata.
- `Publishing Hub` owns `ExportPackage`, platform-ready package, caption variants, publication preparation, manual publication record and `Publication` status.
- MVP is export-first.
- MVP is manual-publication-first.
- The first safest MVP content format is `text_social_post`.
- The minimal `text_social_post` foundation loop does not require real render.
- `RenderJob` and `OutputFile` are not mandatory for the current minimal foundation loop unless a future task explicitly introduces them.
- Project-specific source of truth uses a hybrid model:
  - human-readable project docs: `docs/07_projects/{project_slug}/`
  - machine-readable config: `projects/{project_id}/project.yaml`

## Boundaries

- Do not add API or UI work unless explicitly requested.
- Do not add database persistence layers or migrations unless explicitly requested.
- Do not add SaaS, billing, marketplace, users, roles, public onboarding, autoposting or external APIs unless explicitly requested.
- Do not touch `trend-radar/`, `hyperframes/`, FFmpeg flows, `video-assembler/` or render scripts unless explicitly requested.
- Do not add project-specific hardcode to platform-level code or docs.
- Do not add NURA-specific assets, templates, prompts or packages to the foundation layer.
- Do not treat NURA as a platform default, platform example set or platform dependency.
- Do not mix `ContentItem` status and `Publication` status.
- Do not mix Content Analytics and Product Analytics.

Project-specific logic may live only in:

- `docs/07_projects/{project_slug}/`
- `projects/{project_id}/project.yaml`

## Git Rules

- Before implementation run `git status --short`.
- If the working tree is dirty, stop and report before implementing.
- Do not use `git add .` unless explicitly requested.
- Prefer exact `git add <file>` staging.

## Testing

- Use available tests for the touched scope.
- If `pytest` is unavailable, use `unittest`.
- Known working domain test command:
  - `C:\Users\Bayzel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests.domain.test_models tests.domain.test_transitions`
- Compile check for changed Python modules, when applicable:
  - `C:\Users\Bayzel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall core`

## Reporting

- Always report in Russian.
- Keep file paths, class names, enum names, status names and technical identifiers in English.
- Include changed files, tests, risks and next task in the final report.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

`graphify-out/` is generated local output. It is a local artifact, not source code, and must not be committed.
Post-commit `graphify-out/` rebuilds must not be treated as source changes.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

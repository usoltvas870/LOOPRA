# Content Plant

## What It Is

Content Plant is a standalone multi-project platform for systematic content production, packaging, publishing and analytics.

Platform code and platform docs must stay project-agnostic. Do not hardcode any specific brand, product, URL, price, persona or project into the platform layer.

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
- The first safest MVP content format is `text_social_post`.
- Project-specific source of truth uses a hybrid model:
  - human-readable project docs: `docs/07_projects/{project_slug}/`
  - machine-readable config: `projects/{project_id}/project.yaml`

## Boundaries

- Do not add SaaS, billing, marketplace, users, roles, public onboarding, autoposting or external APIs unless explicitly requested.
- Do not touch `trend-radar/`, `hyperframes/`, FFmpeg flows, `video-assembler/` or render scripts unless explicitly requested.
- Do not add project-specific hardcode to platform-level code or docs.
- Do not mix `ContentItem` status and `Publication` status.
- Do not mix Content Analytics and Product Analytics.

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

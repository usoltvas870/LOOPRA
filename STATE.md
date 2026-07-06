# Content Plant State

Last updated: 2026-07-06

## Current Status

- Content Plant is being rebuilt as a standalone multi-project platform.
- Documentation foundation is complete or close to complete for the first implementation loop.
- The project is moving from documentation cleanup into loop engineering implementation.

## Completed

- Documentation foundation.
- Architecture cleanup before implementation.
- Task 1: canonical platform domain layer.

## Locked Architecture Decisions

- `ExportPackage` belongs to `Publishing Hub`.
- The first MVP content format is `text_social_post`.
- Project-specific source of truth uses a hybrid model:
  - human-readable project docs: `docs/07_projects/{project_slug}/`
  - machine-readable config: `projects/{project_id}/project.yaml`

## Task 1 Result

Implemented under `core/domain/`:

- `core/domain/__init__.py`
- `core/domain/enums.py`
- `core/domain/models.py`
- `core/domain/transitions.py`

Tests added:

- `tests/domain/test_models.py`
- `tests/domain/test_transitions.py`

Validation result:

- 14 `unittest` tests passed for the Task 1 domain layer.

## Current And Next Task

- First finish cleanup if the working tree still contains restored stash artifacts or non-foundation files.
- After cleanup, continue with Task 2: Workspace / Project / BrandProfile service layer and project config binding.

## Do Not Touch Unless Requested

- Trend Radar
- HyperFrames
- FFmpeg
- video-assembler
- render scripts
- SaaS / autoposting / external APIs

## Known Open Issues

- Some docs describe target folder structure while the current repository still uses physically flat files under `docs/`.
- The working tree may still contain restored stash artifacts until cleanup is fully completed and committed.
- Task 2 depends on `core/projects/loader.py` and on the `projects/{project_id}/project.yaml` convention.

## Current Guidance

- Read `STATE.md` first at the start of a new Codex session.
- Keep platform work project-agnostic.
- Do not continue Task 2 on top of a dirty working tree.

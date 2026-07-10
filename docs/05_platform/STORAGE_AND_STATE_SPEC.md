# STORAGE AND STATE SPEC

## Version

v1.0

## Status

Active — LOOPRA Platform Layer

## Purpose

This document defines the Storage and State Layer of the LOOPRA Autonomous
Marketing Operating System.

It answers the central question:

> How does LOOPRA store project configuration, domain entities, runtime
> artifacts, export packages, metric snapshots and generated outputs in the
> current filesystem MVP, and how must this model evolve into future
> DB/object-storage runtime without breaking the Foundation MVP?

STORAGE_AND_STATE_SPEC.md is the bridge between domain entities, filesystem
repositories, project configuration, runtime artifacts, export packages, metric
snapshots and future database/object storage. It describes where and how LOOPRA
stores state — not how state is mutated (services), orchestrated (runtime),
or inspected (tools).

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document defines:

- the current filesystem storage layout as it actually exists in the codebase;
- the separation between source configuration and runtime artifacts;
- where each domain entity type is persisted;
- which repositories own which storage paths;
- the structure of export packages and metric snapshots on disk;
- state ownership rules — which service owns which entity's state;
- commit and git hygiene rules;
- current filesystem limitations;
- the future storage evolution path (database, object storage, runtime state
  persistence, credential vault).

## 1.2. In Scope

- Current filesystem storage model (as implemented),
- Source vs runtime storage separation,
- Project-scoped storage paths,
- Domain entity JSON record storage,
- Export package file storage,
- Metric snapshot storage,
- Artifact lifecycle and categories,
- Repository ownership of storage paths,
- State ownership by service,
- Commit / git hygiene rules,
- Current filesystem constraints and limitations,
- Future DB / object-storage migration path (conceptual).

## 1.3. Out of Scope

- Database implementation and migrations,
- Object storage implementation,
- API endpoints,
- UI screens,
- External platform integrations,
- Credential storage implementation,
- User / team tenancy implementation,
- New storage layout changes without explicit task,
- Code changes, refactoring or test modification.

---

# 2. Role of Storage in LOOPRA

Storage persists state. Storage does not define or enforce business logic.

Storage persists:

- configuration (project identity, brand settings, channels);
- domain records (entities and their statuses);
- artifacts (export package files, manifests, metadata);
- export outputs (title, body, captions, checklists);
- metrics (draft and recorded metric snapshots);
- future: runtime execution context, job records, approval records.

Storage does not:

- decide transitions (domain layer),
- validate strategy (Intelligence Layer),
- publish content (Distribution Layer),
- analyze metrics (Analytics Layer),
- learn from results (Learning Memory),
- mutate entities without services.

**Principle:**

> Storage stores state. Services mutate state.
> Runtime coordinates state transitions.
> Tools inspect or import state through approved boundaries.
> Agents must not directly mutate storage.

---

# 3. Storage Principles

1. **Project-scoped by default.** Every storage path is bound to a specific
   `project_id`. No cross-project writes.

2. **Source config separate from runtime artifacts.** Canonical project config
   lives under `projects/`, committed to version control. Runtime-generated
   outputs live under `storage/smoke_projects/`, not committed.

3. **Services own mutations.** Only services write to entity storage via
   repositories. No direct filesystem writes to entity JSON files outside of
   repository classes.

4. **Repositories abstract persistence.** Each entity type has a dedicated
   repository that handles filesystem read/write. Business logic does not
   interact with raw file paths directly.

5. **Domain entities remain portable.** Entity JSON files are self-describing,
   human-readable and contain all fields needed to reconstruct the domain object
   via `model_validate()`.

6. **Artifacts must be inspectable.** Export packages, entity records and
   manifests are plain text (JSON, TXT) that can be read by humans and parsed by
   deterministic tools.

7. **Generated runtime outputs must not pollute source docs.** Runtime artifacts
   live under `storage/smoke_projects/`, which is excluded from version control
   (`.gitignore` line: `storage/*`).

8. **Future storage must preserve current service contracts.** When DB and object
   storage are introduced, repositories become DB-backed or object-storage-backed,
   but services retain the same method signatures and domain entity semantics.

9. **Storage paths must be deterministic where possible.** Given `project_id` and
   `entity_id`, the file path is predictable:
   `{project_dir}/data/{collection}/{entity_id}.json`.

10. **No cross-project writes in MVP.** Every repository and storage operation
    is scoped to a single `project_id`.

---

# 4. Source vs Runtime Storage

## 4.1. Source / Committed Storage

```text
projects/
    {project_id}/
        project.yaml                    — canonical project config

docs/
    07_projects/
        {project_slug}/                 — brand/project documentation

core/                                   — domain models, services, repositories
scripts/                                — CLI tools
tests/                                  — unit and service tests
```

Source files are authored configuration and specification. They are committed to
version control. The platform core (`core/`) is project-agnostic — no
project-specific values are hardcoded.

## 4.2. Runtime / Generated Storage

```text
storage/
    smoke_projects/
        {project_id}/
            project.yaml                — copy of source config
            data/
                ideas/
                    {idea_id}.json
                scenarios/
                    {scenario_id}.json
                content_items/
                    {content_item_id}.json
                export_packages/
                    {export_package_id}.json
                publications/
                    {publication_id}.json
                metric_snapshots/
                    {metric_snapshot_id}.json
            exports/
                {export_package_id}/
                    title.txt
                    body.txt
                    caption_{platform}.txt
                    manual_publication_checklist.txt
                    metadata.json
                    manifest.json
```

Runtime files are execution output — generated, local, and generally not
tracked in version control. The entire `storage/` directory is excluded by
`.gitignore` (`storage/*`), except for `storage/.gitkeep`.

## 4.3. Boundary Rule

Source config (`projects/{project_id}/project.yaml`) is the canonical
configuration. The smoke loop copies it into `storage/smoke_projects/` at
execution start. Runtime never modifies the canonical source config.

---

# 5. Project Configuration Storage

## 5.1. Canonical Project Config

**Path:** `projects/{project_id}/project.yaml`

**Purpose:** Defines the project's identity, brand context, content rules,
channels, goals and operational settings.

**Loaded by:** `FileSystemProjectRepository.load_project_config()` →
`ProjectConfig` deserialized via pydantic.

**Used by:** `ProjectService`, `BrandProfileService`, `ScenarioService`,
`LoopOrchestrator`.

**Rules:**

- `project.yaml` is source configuration. It lives in `projects/` and may be
  committed.
- Runtime copies may exist under `storage/smoke_projects/{project_id}/project.yaml`
  — these are ephemeral and regenerated by `smoke_loop.py._ensure_runtime_project()`.
- Services load config through `ProjectService.get_project()` / `FileSystemProjectRepository`.
  Direct YAML reading outside the repository is not permitted.
- Runtime must not modify canonical `project.yaml`.

## 5.2. Required Config Fields

The following fields must be present as validated by `ProjectService`:

| Field | Config path | Purpose |
|---|---|---|
| `project_id` | `id` | Project identity |
| `project_name` | `name` | Human-readable name |
| `project_slug` | `slug` | URL-safe machine identifier |
| `default_language` | `language` | Primary content language |
| `status` | `status` | draft, active, paused, archived |

Missing or empty fields raise `ProjectConfigValidationError`.

---

# 6. Project Documentation Storage

**Path:** `docs/07_projects/{project_slug}/`

**Purpose:** Contains project-specific documentation — brand positioning,
tone of voice, content pillars, validation documents.

**Rules:**

- Project-specific knowledge belongs here, not in platform core docs.
- Platform architecture documents (`docs/00_foundation/`, `docs/02_architecture/`,
  `docs/04_production/`, `docs/05_platform/`) remain project-agnostic.
- No project leakage into platform specifications.
- NURA documentation lives at `docs/07_projects/nura/`. This directory name
  matches the project's `slug` value.

---

# 7. Runtime Project Storage

## 7.1. Smoke Runtime Projects

**Path:** `storage/smoke_projects/{project_id}/`

**Created by:** `smoke_loop.py._ensure_runtime_project()` — copies the source
`project.yaml` into this directory.

**Contains:**

```text
project.yaml                    — copy of source config
data/
    ideas/                      — Idea JSON records
    scenarios/                  — Scenario JSON records
    content_items/              — ContentItem JSON records
    export_packages/            — ExportPackage JSON records
    publications/               — Publication JSON records
    metric_snapshots/           — MetricSnapshot JSON records
exports/
    {export_package_id}/        — generated export files
```

**Rules:**

- Generated by `smoke_loop.py` at execution start.
- Local-only, not committed (`.gitignore` applies).
- Safe to delete and regenerate by rerunning the smoke loop.
- Not intended for production data — this is a smoke/test runtime area.

## 7.2. Programmatic Control

When services are constructed programmatically (e.g., in tests), callers can
override the `projects_root` parameter in factory functions to point to any
directory:

```python
# Tests can use a temp directory
build_loop_orchestrator(projects_root=tmp_path)
build_publishing_service(projects_root=tmp_path)
```

This is how tests isolate storage from source directories.

---

# 8. Domain Entity Storage

## 8.1. Storage Layout

All domain entities are stored as JSON files under their project's `data/`
directory, grouped by collection (entity type):

```text
{project_dir}/
    data/
        ideas/
            {idea_id}.json
        scenarios/
            {scenario_id}.json
        content_items/
            {content_item_id}.json
        export_packages/
            {export_package_id}.json
        publications/
            {publication_id}.json
        metric_snapshots/
            {metric_snapshot_id}.json
```

`{project_dir}` is resolved by `resolve_project_dir(project_id, projects_root)`,
which returns `{projects_root}/{project_id}/`.

JSON files use `indent=2, ensure_ascii=False` for human readability.

## 8.2. Entity Storage Summary

| Entity | Collection dir | Repository class | File naming | Lifecycle owner |
|---|---|---|---|---|
| `Idea` | `data/ideas/` | `FileSystemIdeaRepository` | `{idea_id}.json` | `IdeaService` |
| `Scenario` | `data/scenarios/` | `FileSystemScenarioRepository` | `{scenario_id}.json` | `ScenarioService` |
| `ContentItem` | `data/content_items/` | `FileSystemContentItemRepository` | `{content_item_id}.json` | `ProductionLifecycleService` |
| `ExportPackage` | `data/export_packages/` | `FileSystemExportPackageRepository` | `{export_package_id}.json` | `PublishingService` |
| `Publication` | `data/publications/` | `FileSystemPublicationRepository` | `{publication_id}.json` | `PublishingService` |
| `MetricSnapshot` | `data/metric_snapshots/` | `FileSystemMetricSnapshotRepository` | `{metric_snapshot_id}.json` | `AnalyticsService` |

## 8.3. Entity ID Convention

All entity IDs are generated by `build_entity_id(prefix)` which produces
`{prefix}_{uuid4().hex[:12]}` (e.g., `idea_f80924dbb809`, `content_9e3b53760d27`).

IDs are validated against the pattern `^[a-z0-9][a-z0-9_-]*$` by repository
base classes.

---

# 9. Repository Model

## 9.1. Repository Base Class

**File:** `core/services/_storage.py:22-74`

`FileSystemProjectModelRepository[ModelT]` is the generic base class for all
entity-specific repositories.

| Method | Purpose |
|---|---|
| `list_models(project_id)` | List all JSON files in the collection directory, deserialize and return sorted by `created_at` descending |
| `load_model(project_id, entity_id, entity_name)` | Load a single entity JSON file by ID |
| `save_model(project_id, entity_id, model)` | Serialize the model to JSON and write to disk. Creates parent directories if needed |

**Storage path formula:** `{projects_root}/{project_id}/data/{collection}/{entity_id}.json`

## 9.2. Repository Inventory

### FileSystemProjectRepository

**File:** `core/services/projects.py:28-53`

| Attribute | Value |
|---|---|
| Entity type | `Project` (via `ProjectConfig` → `Project` mapping) |
| Storage path | `{PROJECTS_ROOT}/{project_id}/project.yaml` |
| Operations | `list_project_ids()`, `load_project_config(project_id)` |

### FileSystemIdeaRepository

**File:** `core/services/ideas.py:116-132`

Extends `_FileSystemProjectEntityRepository` (standalone base, not the generic
`FileSystemProjectModelRepository`).

| Attribute | Value |
|---|---|
| Entity type | `Idea` |
| Collection | `ideas` |
| Storage path | `{project_dir}/data/ideas/{idea_id}.json` |
| Operations | `list_ideas()`, `load_idea()`, `save_idea()` |

### FileSystemScenarioRepository

**File:** `core/services/ideas.py:135-156`

Extends `_FileSystemProjectEntityRepository`.

| Attribute | Value |
|---|---|
| Entity type | `Scenario` |
| Collection | `scenarios` |
| Storage path | `{project_dir}/data/scenarios/{scenario_id}.json` |
| Operations | `list_scenarios()`, `load_scenario()`, `save_scenario()` |

### FileSystemContentItemRepository

**File:** `core/services/production.py:17-28`

Extends `FileSystemProjectModelRepository[ContentItem]`.

| Attribute | Value |
|---|---|
| Entity type | `ContentItem` |
| Collection | `content_items` |
| Storage path | `{project_dir}/data/content_items/{content_item_id}.json` |
| Operations | `list_content_items()`, `load_content_item()`, `save_content_item()` |

### FileSystemExportPackageRepository

**File:** `core/services/publishing.py:28-39`

Extends `FileSystemProjectModelRepository[ExportPackage]`.

| Attribute | Value |
|---|---|
| Entity type | `ExportPackage` |
| Collection | `export_packages` |
| Storage path | `{project_dir}/data/export_packages/{export_package_id}.json` |
| Operations | `list_export_packages()`, `load_export_package()`, `save_export_package()` |

### FileSystemPublicationRepository

**File:** `core/services/publishing.py:42-53`

Extends `FileSystemProjectModelRepository[Publication]`.

| Attribute | Value |
|---|---|
| Entity type | `Publication` |
| Collection | `publications` |
| Storage path | `{project_dir}/data/publications/{publication_id}.json` |
| Operations | `list_publications()`, `load_publication()`, `save_publication()` |

### FileSystemMetricSnapshotRepository

**File:** `core/services/analytics.py:41-52`

Extends `FileSystemProjectModelRepository[MetricSnapshot]`.

| Attribute | Value |
|---|---|
| Entity type | `MetricSnapshot` |
| Collection | `metric_snapshots` |
| Storage path | `{project_dir}/data/metric_snapshots/{metric_snapshot_id}.json` |
| Operations | `list_metric_snapshots()`, `load_metric_snapshot()`, `save_metric_snapshot()` |

## 9.3. Repository Boundaries

Repositories must not:
- make business decisions;
- enforce lifecycle semantics or domain transitions;
- validate entity state transitions (that belongs to `transitions.py`);
- perform cross-project operations;
- expose raw storage mutation as a public API.

Repositories may:
- persist and load entities as JSON;
- validate entity ID format (`^[a-z0-9][a-z0-9_-]*$`);
- raise `FileNotFoundError` if entity not found;
- create parent directories during save (via `mkdir(parents=True, exist_ok=True)`).

---

# 10. Export Package Storage

## 10.1. ExportPackage Directory

**Path:** `{project_dir}/exports/{export_package_id}/`

**Created by:** `PublishingService.prepare_export()` at
`core/services/publishing.py:120-198`.

## 10.2. Export Package Files

| File | Purpose | Produced by | Consumed by |
|---|---|---|---|
| `title.txt` | The content's title/headline | `PublishingService.prepare_export()` | `inspect_package.py`, `validate_package.py`, human operator |
| `body.txt` | The full content body | `PublishingService.prepare_export()` | `inspect_package.py`, `validate_package.py`, human operator |
| `caption_{platform}.txt` | Platform-specific caption (e.g., `caption_telegram.txt`) | `PublishingService.prepare_export()` | `inspect_package.py`, `validate_package.py`, human operator |
| `manual_publication_checklist.txt` | Step-by-step manual publishing instructions | `PublishingService.prepare_export()` | `validate_package.py`, human operator |
| `metadata.json` | Export metadata: project_id, content_item_id, scenario_id, format, platform, timestamps, brand info, QA warnings | `PublishingService.prepare_export()` | `inspect_package.py`, `validate_package.py` |
| `manifest.json` | File listing with name, role, package_id, project_id, status, timestamps | `PublishingService.prepare_export()` | `inspect_package.py`, `validate_package.py` |

## 10.3. ExportPackage Entity JSON

The `ExportPackage` domain entity itself is stored separately as JSON:
`{project_dir}/data/export_packages/{export_package_id}.json`

This file contains the entity state (status, caption_variants, package_files,
timestamps) — not the export output files.

## 10.4. Rules

- ExportPackage should be inspectable — `inspect_package.py` must be able to read
  manifest and display all files.
- `validate_package.py` must pass — all required files exist and manifest is
  structurally correct.
- Distribution / manual publication uses this package as prepared.
- Future media assets (images, video) may extend the export package with
  additional file types in subdirectories.

---

# 11. Metric Snapshot Storage

## 11.1. MetricSnapshot Entity JSON

**Path:** `{project_dir}/data/metric_snapshots/{metric_snapshot_id}.json`

**Created by:** `AnalyticsService.create_metric_snapshot()` (status: `DRAFT`).

**Updated by:** `AnalyticsService.record_metrics()` (status: `DRAFT` → `RECORDED`).

**Read by:** `find_metric_snapshots.py` (direct filesystem read + domain model parse).

## 11.2. Metric Snapshot Statuses

| Status | Meaning | Mutated by |
|---|---|---|
| `DRAFT` | Snapshot created, no metrics recorded yet | `AnalyticsService.create_metric_snapshot()` |
| `RECORDED` | Metrics have been imported and validated | `AnalyticsService.record_metrics()` |

## 11.3. `published_url` Special Handling

When `published_url` is provided in manual metrics input:

1. `AnalyticsService.record_metrics()` updates the related `Publication.published_url`
   via `FileSystemPublicationRepository`.
2. The URL is NOT stored as a raw metric field inside the snapshot. It updates the
   `Publication` record that the snapshot references.

## 11.4. Manual Metric Storage

Manual metric collection has no separate storage — metrics are embedded directly
within the `MetricSnapshot` entity's `content_metrics` field
(`ContentPerformanceMetrics` model). The supported keys are:

| Input Key | Normalized Field |
|---|---|
| `views` | `content_metrics.views` |
| `likes` | `content_metrics.likes` |
| `comments` | `content_metrics.comments` |
| `shares` | `content_metrics.shares` |
| `saves` | `content_metrics.saves` |
| `clicks` | `content_metrics.link_clicks` |
| `published_url` | Updates `Publication.published_url` |

A future `RawMetricRecord` entity (conceptual) may provide separate storage for
raw platform-specific metrics before normalization.

## 11.5. Finding Snapshots

`find_metric_snapshots.py` reads the snapshot files directly from
`{project_dir}/data/metric_snapshots/*.json`, parses them with
`MetricSnapshot.model_validate()`, and filters to `DRAFT` status. It does not
use `AnalyticsService`.

---

# 12. Runtime Artifact Categories

## 12.1. Artifact Taxonomy

| Category | Examples | Current / Future | Persisted | Source / Runtime | Commit Policy |
|---|---|---|---|---|---|
| Source configuration | `project.yaml` in `projects/` | Current | Yes (filesystem) | Source | Committed |
| Domain records | `{idea_id}.json`, `{scenario_id}.json`, etc. | Current | Yes (JSON files) | Runtime (in `storage/smoke_projects/`) | Not committed (under `storage/`) |
| Export package files | `title.txt`, `body.txt`, `caption_{platform}.txt`, `metadata.json`, `manifest.json` | Current | Yes (text/JSON files) | Runtime | Not committed |
| Publication records | `{publication_id}.json` | Current | Yes (JSON) | Runtime | Not committed |
| Metric records | `{metric_snapshot_id}.json` | Current | Yes (JSON) | Runtime | Not committed |
| Validation reports | stdout from `validate_package.py` | Current | No (stdout only) | Runtime | N/A |
| Logs | stdout / stderr from scripts | Current | No (terminal output) | Runtime | N/A |
| Render outputs | Rendered video, images, carousel slides | Future | Yes (object storage) | Runtime | Not committed |
| Uploaded assets | User-provided media files | Future | Yes (object storage) | Runtime | Not committed |
| Connector responses | Platform API responses | Future | Yes (DB or file) | Runtime | Not committed |
| Runtime execution contexts | Execution state records | Future | Yes (DB) | Runtime | Not committed |
| Approval records | Human approval records | Future | Yes (DB) | Runtime | Not committed |

## 12.2. Current MVP Artifacts (Verified)

All six entity types produce JSON records. `PublishingService.prepare_export()`
produces six output files per export package. All scripts produce stdout output
only.

---

# 13. State Ownership Model

## 13.1. Principle

Every piece of mutable state is owned by exactly one service. No other
component — runtime, tool, or future agent — may mutate state without going
through the owning service.

## 13.2. State Ownership Table

| State / Entity | Owner | Storage Path | Mutated by | Read by |
|---|---|---|---|---|
| Project config | `ProjectService` | `projects/{project_id}/project.yaml` | Human (authoring), `smoke_loop.py` (copy-only) | `ProjectService`, `BrandProfileService`, `ScenarioService` |
| BrandProfile | `BrandProfileService` | Derived from config (in-memory) | Derived on read | `ScenarioService` |
| Idea | `IdeaService` | `data/ideas/{idea_id}.json` | `IdeaService` | `LoopOrchestrator`, `ScenarioService`, `smoke_loop.py` (summary read) |
| Scenario | `ScenarioService` | `data/scenarios/{scenario_id}.json` | `ScenarioService` | `LoopOrchestrator`, `ProductionLifecycleService`, `PublishingService` |
| ContentItem | `ProductionLifecycleService` | `data/content_items/{content_item_id}.json` | `ProductionLifecycleService` | `LoopOrchestrator`, `PublishingService`, `AnalyticsService` |
| ExportPackage | `PublishingService` | `data/export_packages/{export_package_id}.json` | `PublishingService` | `LoopOrchestrator`, `inspect_package.py`, `validate_package.py` |
| Export package files | `PublishingService` | `exports/{export_package_id}/*` | `PublishingService.prepare_export()` | `inspect_package.py`, `validate_package.py`, human operator |
| Publication | `PublishingService` | `data/publications/{publication_id}.json` | `PublishingService`, `AnalyticsService` (URL update only) | `LoopOrchestrator`, `AnalyticsService` |
| MetricSnapshot | `AnalyticsService` | `data/metric_snapshots/{metric_snapshot_id}.json` | `AnalyticsService` | `LoopOrchestrator`, `find_metric_snapshots.py`, `smoke_loop.py` (summary) |
| Runtime coordination | `LoopOrchestrator` | In-memory (not persisted) | `LoopOrchestrator` | `smoke_loop.py` |

## 13.3. Cross-Service Mutations

`AnalyticsService.record_metrics()` is the only operation in the current MVP
that mutates an entity owned by another service — it may update
`Publication.published_url` via `FileSystemPublicationRepository`. This is an
approved cross-service write constrained to a single field update. All other
mutations are single-owner.

---

# 14. State Transition Persistence

When a service performs a status transition, the following sequence occurs:

1. **Load entity** via repository (e.g., `self._repository.load_idea(project_id, idea_id)`).
2. **Validate preconditions** (e.g., Idea status is `RAW` before approval).
3. **Transition state** via `entity.transition_to(target_status)` — validates
   against transition rules in `core/domain/transitions.py`.
4. **Trigger timestamp updates** via domain model field defaults or
   `validated_model_copy(updated_at=utc_now())`.
5. **Save entity** via repository (e.g., `self._repository.save_idea(approved)`).
6. **Return updated entity** to caller.

**Transaction guarantees:** The current filesystem model provides no atomic
transactions. A save can succeed while a follow-up step fails. Each
`save_*()` call is a single transactional filesystem write (atomic at the
level of `Path.write_text()`). Future DB backends can provide stronger
transactional semantics.

---

# 15. Filesystem Constraints and Limitations

The current filesystem-based storage has the following limitations:

| Limitation | Impact | Future Mitigation |
|---|---|---|
| No transactions | Multi-entity operations are not atomic; partial failure possible | DB provides transactions |
| No locking | Concurrent writes from parallel processes could corrupt data | DB provides row-level locking |
| No concurrent write protection | Two scripts writing simultaneously to the same project could collide | DB / queue serializes access |
| No schema migration system | Entity model changes require manual migration of JSON files | DB migrations (Alembic or equivalent) |
| No cleanup lifecycle | Smoke artifacts accumulate indefinitely under `storage/smoke_projects/` | Artifact retention policies, TTL |
| No artifact versioning | Overwriting an export package loses the previous version | Object storage versioning, export package archiving |
| No persisted runtime execution state | Execution context is in-memory only; lost on process exit | DB-backed RuntimeExecutionContext |
| No object storage | Export files are local; no distribution, no CDN, no backup | S3-compatible object storage |
| No access control | Any process with filesystem access can read/write entity files | DB/API authentication layer |
| Direct filesystem reads by some tools | `find_metric_snapshots.py` reads entity JSON directly | Future service-backed queries |

---

# 16. Commit / Git Hygiene Rules

## 16.1. Commit Policies

| What | Commit? | Reason |
|---|---|---|
| `core/` | Yes | Platform code — project-agnostic |
| `scripts/` | Yes | Platform tools |
| `tests/` | Yes | Platform verification |
| `docs/` | Yes | Architecture and specification source of truth |
| `projects/{project_id}/project.yaml` | Yes (if intended) | Source project configuration |
| `docs/07_projects/{project_slug}/` | Yes | Project documentation |
| `storage/smoke_projects/` | **No** | Runtime artifacts — excluded by `.gitignore` |
| `storage/*` (all contents) | **No** | The entire `storage/` directory is gitignored (`storage/*`) except `.gitkeep` |
| `graphify-out/` | **No** | Generated graphify output — excluded by `.gitignore` |
| Secrets / credentials | **Never** | Security |
| `__pycache__/`, `*.pyc` | **No** | Build artifacts — excluded by `.gitignore` |

## 16.2. Actual .gitignore Entries (Relevant to Storage)

From the current `.gitignore`:

```text
# Runtime job artifacts
jobs/*/input/
jobs/*/work/
jobs/*/output/

# Local caches and reusable runtime storage
output/
storage/*

# Generated graphify output
graphify-out/

# Binary test/render artifacts
hyperframes/test-render.mp4
hyperframes/frame_*.png
```

The pattern `storage/*` excludes all runtime smoke outputs. The `storage/.gitkeep`
file is explicitly excluded from the ignore via `!storage/.gitkeep`.

---

# 17. Storage Validation

## 17.1. Validation Points

Validation is distributed across services and tools — storage itself is not the
business validator.

| Validation | Performed by | When |
|---|---|---|
| Project config required fields | `ProjectService._validate_required_fields()` | On `get_project()` |
| Project status validity | `ProjectService._parse_project_status()` | On `get_project()` |
| Entity ID format | `FileSystemProjectModelRepository._validate_entity_id()` | On every load/save |
| Domain state transitions | `core/domain/transitions.py` via `entity.transition_to()` | On every status change |
| Brand profile required fields | `BrandProfileService._validate_brand_fields()` | On `get_brand_profile()` |
| Idea input validation | `IdeaService._validate_funnel_stage()`, `_validate_source_type()`, `_validate_priority()` | On `create_idea()` |
| Scenario input validation | `ScenarioService` precondition checks | On `create_from_idea()` |
| ContentItem QA | `ProductionLifecycleService._collect_technical_qa_errors()` | On `run_technical_qa()` |
| Export package structural validation | `validate_package.py` | Post-export, manual CLI |
| Export package manifest validation | `inspect_package.py`, `validate_package.py` | Post-export, manual CLI |
| Metric key validation | `AnalyticsService._validate_metrics_payload()` | On `record_metrics()` |
| Metric value validation | `AnalyticsService._validate_metrics_payload()` | On `record_metrics()` |
| Snapshot status check | `AnalyticsService.record_metrics()` | Before recording metrics |

## 17.2. Storage Itself Is Not the Validator

The filesystem and JSON persistence layer does not perform domain validation.
It validates only:
- Entity ID format (regex).
- File existence (`FileNotFoundError` if missing).
- JSON parseability.

---

# 18. Backup / Recovery — Conceptual

## 18.1. Current MVP

- Filesystem files can be copied manually.
- Re-running `smoke_loop.py` regenerates all runtime outputs.
- No formal backup mechanism exists.
- No rollback capability.

## 18.2. Future (Conceptual)

| Capability | Approach |
|---|---|
| Database backups | Regular PostgreSQL backups (pg_dump, WAL archiving) |
| Object storage versioning | S3 versioning enabled on asset/export buckets |
| Export package retention | Configurable retention policy per workspace |
| Audit logs | Immutable append-only log of all mutations |
| Restore by project/workspace | Restore DB + object storage to a point-in-time snapshot |

Marked as future — not implemented in current MVP.

---

# 19. Future Database Storage Path (Conceptual)

When LOOPRA transitions to a database-backed persistence layer, the following
storage areas migrate from filesystem JSON to DB tables:

| Current Storage | Future DB Table(s) |
|---|---|
| `projects/{project_id}/project.yaml` | `projects`, `brand_profiles`, `channels`, `goals` |
| `data/ideas/{idea_id}.json` | `ideas` |
| `data/scenarios/{scenario_id}.json` | `scenarios`, `scenario_text_blocks`, `scenario_caption_drafts` |
| `data/content_items/{content_item_id}.json` | `content_items` |
| `data/export_packages/{export_package_id}.json` | `export_packages` |
| `data/publications/{publication_id}.json` | `publications`, `publication_attempts` |
| `data/metric_snapshots/{metric_snapshot_id}.json` | `metric_snapshots`, `content_performance_metrics`, `raw_metric_records` |
| (not yet stored) | `workspaces`, `users`, `approval_records`, `runtime_execution_contexts`, `runtime_jobs`, `learning_memory_entries` |

**Rules for DB migration:**

1. **Service contracts remain stable.** Methods signatures, return types and
   error semantics must not change when repositories become DB-backed.
2. **Repositories become DB-backed.** Replace `FileSystemXXXRepository` with
   `PostgresXXXRepository` or `SQLAlchemyXXXRepository` inheriting the same
   interface.
3. **Domain models remain portable.** Pydantic models remain the canonical
   entity representation. ORM models (if used) are separate from domain models.
4. **No direct SQL from tools or agents.** All DB access goes through
   repositories → services → runtime.
5. **Migrations require separate specification.** A dedicated DB migration spec
   must be approved before implementing any DB-backed repository.

---

# 20. Future Object Storage Path (Conceptual)

Large binary assets that do not belong in a relational database will be stored
in an object storage service (S3-compatible).

| Asset Type | Storage Location | Metadata Location |
|---|---|---|
| Export package files (title.txt, body.txt, etc.) | Object storage | `export_packages` DB record → object key reference |
| Rendered video files (mp4) | Object storage | `content_items` or `render_jobs` DB record |
| Carousel slide images (png) | Object storage | `content_items` or `assets` DB record |
| Thumbnails | Object storage | `assets` DB record |
| Subtitles (SRT) | Object storage | `export_packages` DB record |
| Audio files (voiceover, music) | Object storage | `assets` DB record |
| User-uploaded media | Object storage | `assets` DB record |
| Generated AI media | Object storage | `assets` DB record |

**Rules:**

- Metadata (entity references, file metadata, content type, timestamps) remains
  in the database — object storage stores the binary/blob files.
- Asset Library governs reusable production assets.
- ExportPackage governs distribution-ready outputs.
- Object keys should follow deterministic naming:
  `{project_id}/{collection}/{entity_id}/{filename}`.

---

# 21. Future Runtime State Persistence (Conceptual)

The current MVP does not persist runtime execution state. `LoopOrchestrator`
operates entirely in-memory.

Future runtime state persistence includes:

| Entity | Purpose |
|---|---|
| `RuntimeExecutionContext` | Captures the state of an active or completed execution |
| `RuntimeJob` | A unit of work — a single execution request spanning multiple stages |
| `RuntimeStage` | A single step within a runtime execution |
| `RuntimeError` | A structured error record from a failed execution |
| `RuntimeArtifact` | A record of a file or data entity produced during execution |
| `RuntimeToolInvocation` | A record of a tool (script) invocation during execution |
| `RuntimeApprovalGate` | A human approval checkpoint within an execution |

This enables:
- execution history and auditability;
- resume/retry of failed executions from the failed stage;
- agent-safe invocation — agents can inspect execution state before issuing
  new commands;
- observability — operators can query what is running and what failed.

Do not implement runtime state persistence in the current MVP.

---

# 22. Future Credential / Secret Storage Boundary (Conceptual)

**Current MVP:** No connector credentials. No external secrets.

**Future principles:**

- Connector credentials (platform API keys, tokens) must not live in
  `project.yaml`.
- No secrets in Git.
- No secrets in CLI args that appear in shell history.
- Use a dedicated secret manager, environment variable, or encrypted store.
- Secret values must be excluded from:
  - export packages;
  - agent prompts;
  - logs and debugging output;
  - error messages.

A separate credential storage specification must be documented before
implementing any external platform integration.

---

# 23. Storage and Multi-Project Isolation

## 23.1. Current MVP Isolation

- Every project has its own config (`projects/{project_id}/project.yaml`).
- Every project has its own entity data under `{project_dir}/data/`.
- Every project has its own export outputs under `{project_dir}/exports/`.
- No cross-project writes. Repositories validate `project_id` on every operation.
- `project_id` is validated by `validate_project_id()` from
  `core/projects/loader.py`.

## 23.2. Project Identity Boundaries

```text
projects/
    example/
        project.yaml                        — example project config
    nura/
        project.yaml                        — NURA project config

docs/07_projects/
    nura/                                   — NURA brand documentation

storage/smoke_projects/
    example/
        project.yaml                        — example runtime copy
    nura/
        project.yaml                        — NURA runtime copy
```

## 23.3. Future Isolation (Conceptual)

- Workspace-level isolation: each workspace sees only its own projects.
- Tenant-level isolation (SaaS): each tenant sees only their own workspaces.
- NURA or any project-specific data must never leak into platform core code
  or platform shared storage.

---

# 24. Storage and Future Agents

## 24.1. What Agents Must NOT Do

- Write JSON entity files directly — use service methods only.
- Edit `project.yaml` directly without an approved config workflow.
- Modify export package files directly — export is produced by
  `PublishingService.prepare_export()`.
- Delete artifacts without explicit human command or approval.
- Access cross-project storage without explicit scope.

## 24.2. What Agents May Do

- Request runtime commands (which call services).
- Request service-backed mutations (create idea, approve scenario, record metrics).
- Inspect artifacts through approved tools (`inspect_package.py`,
  `validate_package.py`, `find_metric_snapshots.py`).
- Request storage summaries (entity counts by status, export package file lists).

## 24.3. Auditability (Future)

All agent-initiated storage interactions must be auditable:
- recorded in a `RuntimeToolInvocation` or equivalent audit record;
- linked to the agent decision that triggered it;
- reviewable by a human operator.

---

# 25. Current MVP Storage Flow

Based on actual code behaviour:

```text
1. Canonical project.yaml exists at projects/{project_id}/project.yaml
       │
2. smoke_loop.py copies project.yaml to storage/smoke_projects/{project_id}/project.yaml
       │  (_ensure_runtime_project via shutil.copyfile)
       │
3. IdeaService.create_idea() → FileSystemIdeaRepository.save_idea()
       │  writes data/ideas/{idea_id}.json
       │
4. ScenarioService.create_from_idea() → FileSystemScenarioRepository.save_scenario()
       │  writes data/scenarios/{scenario_id}.json
       │  (may also update Idea JSON via FileSystemIdeaRepository)
       │
5. ProductionLifecycleService.create_content_item() →
   FileSystemContentItemRepository.save_content_item()
       │  writes data/content_items/{content_item_id}.json
       │
6. PublishingService.create_export_package() →
   FileSystemExportPackageRepository.save_export_package()
       │  writes data/export_packages/{export_package_id}.json
       │
7. PublishingService.prepare_export()
       │  writes exports/{export_package_id}/title.txt
       │  writes exports/{export_package_id}/body.txt
       │  writes exports/{export_package_id}/caption_{platform}.txt
       │  writes exports/{export_package_id}/manual_publication_checklist.txt
       │  writes exports/{export_package_id}/metadata.json
       │  writes exports/{export_package_id}/manifest.json
       │  updates ContentItem: APPROVED → EXPORTED
       │
8. inspect_package.py / validate_package.py read export package artifacts
       │  (read-only, no service calls)
       │
9. PublishingService.create_publication() →
   FileSystemPublicationRepository.save_publication()
       │  writes data/publications/{publication_id}.json
       │
10. PublishingService.publish_content() →
    FileSystemPublicationRepository.save_publication()
       │  overwrites data/publications/{publication_id}.json (PLANNED → PUBLISHED)
       │
11. AnalyticsService.create_metric_snapshot() →
    FileSystemMetricSnapshotRepository.save_metric_snapshot()
       │  writes data/metric_snapshots/{metric_snapshot_id}.json (DRAFT)
       │
12. import_manual_metrics.py → AnalyticsService.record_metrics()
       │  updates data/metric_snapshots/{metric_snapshot_id}.json (DRAFT → RECORDED)
       │  may update Publication.published_url
       │
13. find_metric_snapshots.py reads data/metric_snapshots/*.json (read-only)
       │
14. All runtime artifacts remain under storage/smoke_projects/
       │  (excluded from Git by .gitignore)
```

---

# 26. Future Storage Extension Path

Marked stages. Do not implement beyond the current stage.

| Stage | Description | Status |
|---|---|---|
| Stage 1 | Current filesystem MVP: JSON files, local directories, in-memory execution context | **Current** |
| Stage 2 | Better filesystem conventions: explicit artifact registry, cleanup tool, smoke artifact rotation | Future |
| Stage 3 | Persist RuntimeExecutionContext: execution state survives process restart | Future |
| Stage 4 | Structured artifact registry: central index of all artifacts with checksums and timestamps | Future |
| Stage 5 | DB-backed repositories: PostgreSQL replaces filesystem JSON for all entity types | Future |
| Stage 6 | Object storage for large assets: S3-compatible storage for exports, media, uploads | Future |
| Stage 7 | Workspace / tenant isolation: multi-workspace, multi-user storage separation with access control | Future |
| Stage 8 | Backup, audit, retention policies: automated backups, configurable retention, immutable audit logs | Future |
| Stage 9 | Agent-safe storage operations: audited, scoped, approval-gated agent storage access | Future |

Each stage must be validated before the next begins. The Foundation MVP must
remain operational through all stages.

---

# 27. Storage Readiness Criteria

The Storage and State architecture is ready when:

- [x] Source vs runtime storage defined — Section 4
- [x] Project config storage defined — Section 5
- [x] Project docs storage defined — Section 6
- [x] Runtime storage defined — Section 7
- [x] Entity storage folders defined — Section 8
- [x] Repository model defined — Section 9
- [x] Export package storage defined — Section 10
- [x] Metric snapshot storage defined — Section 11
- [x] State ownership defined — Section 13
- [x] Artifact categories defined — Section 12
- [x] Git hygiene rules defined — Section 16
- [x] Future DB path defined — Section 19
- [x] Future object storage path defined — Section 20
- [x] Future runtime state persistence defined — Section 21
- [x] Current MVP constraints preserved — Throughout

---

# 28. Related Documents

```text
AGENTS.md                                              — Development rules
STATE.md                                               — Current project state
docs/00_foundation/DATA_MODEL.md                       — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md            — Project configuration specification
docs/02_architecture/SYSTEM_ARCHITECTURE.md            — System architecture layers
docs/02_architecture/PIPELINES_SPEC.md                 — Foundation MVP pipeline
docs/04_production/PRODUCTION_PIPELINE_SPEC.md         — Production pipeline specification
docs/04_production/ASSET_LIBRARY_SPEC.md               — Asset library specification
docs/04_production/DISTRIBUTION_SPEC.md                — Distribution specification
docs/04_production/ANALYTICS_SPEC.md                   — Analytics specification
docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md         — Runtime orchestration specification
docs/05_platform/SERVICE_CONTRACTS_SPEC.md             — Service contracts specification
docs/05_platform/TOOLING_AND_CLI_SPEC.md               — Tooling and CLI specification
```

---

# 29. Code References

```text
core/services/_storage.py         — FileSystemProjectModelRepository base class
core/services/projects.py         — ProjectService, BrandProfileService, FileSystemProjectRepository
core/services/ideas.py            — IdeaService, ScenarioService, FileSystemIdeaRepository, FileSystemScenarioRepository
core/services/production.py       — ProductionLifecycleService, FileSystemContentItemRepository
core/services/publishing.py       — PublishingService, FileSystemExportPackageRepository, FileSystemPublicationRepository
core/services/analytics.py        — AnalyticsService, FileSystemMetricSnapshotRepository
core/services/loop.py             — LoopOrchestrator, build_loop_orchestrator
scripts/smoke_loop.py             — End-to-end smoke test (primary runtime entrypoint)
scripts/inspect_package.py        — Export package inspection tool
scripts/validate_package.py       — Export package validation tool
scripts/find_metric_snapshots.py  — Metric snapshot discovery tool
scripts/import_manual_metrics.py  — Manual metric import tool
projects/                         — Canonical project configuration directory
storage/                          — Runtime artifact storage directory
.gitignore                        — Git exclusion rules
```

---

# 30. Document Status

| Field | Value |
|---|---|
| Status | Active — LOOPRA Platform Layer |
| Version | v1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Platform Layer — Storage and State |

---

# Final Statement

The Storage and State Layer is the persistence substrate of LOOPRA. It stores
configuration, domain records, artifacts, exports and metrics — but it does not
define business logic, enforce transitions, or decide strategy.

In the current Foundation MVP, storage is filesystem-based: project-scoped JSON
records, plain-text export files, and runtime data under `storage/smoke_projects/`.
Source configuration lives in `projects/` and is committed. Runtime outputs live
under `storage/` and are not committed.

Repositories abstract persistence behind service interfaces. Services own
mutations. Runtime coordinates transitions. Tools inspect artifacts through
approved boundaries. Agents must not directly mutate storage.

Future storage evolution — database-backed repositories, object storage for
large assets, persisted runtime execution contexts — will preserve the same
service contracts, domain entity semantics and project-scoping rules defined
in the current Foundation MVP.

Storage stores state. Services mutate state. Runtime coordinates. Tools inspect.
Agents decide — but they do not touch storage directly.

---

## Current Stage 2 Slice 1 Storage

Content Intelligence Foundation records are stored locally under the owning project:

```text
projects/{project_id}/data/market_signals/{market_signal_id}.json
projects/{project_id}/data/trend_patterns/{trend_pattern_id}.json
projects/{project_id}/data/content_opportunities/{content_opportunity_id}.json
```

Runtime copies under `storage/` remain runtime artifacts and must not be committed.

# SERVICE CONTRACTS SPEC

## Version

v1.0

## Status

Active — LOOPRA Runtime Layer

## Purpose

This document defines the Service Contracts Layer of the LOOPRA Autonomous
Marketing Operating System.

It answers the central question:

> Which services exist in LOOPRA runtime, what operations do they provide,
> what inputs/outputs do they accept and return, which domain transitions do
> they perform, which errors do they raise, and which boundaries must they
> never violate?

SERVICE_CONTRACTS_SPEC.md is the bridge between the domain model, the runtime
orchestration layer, the current service code and future API/agent/worker
entrypoints.

Every contract described here for a current service is based on the actual
code in `core/services/`. No methods are invented. No current behaviour is
conjectured. Methods that do not exist are explicitly marked as future/conceptual.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document describes the service-level operations that are available to the
LOOPRA runtime, CLI tools and future agents. It defines:

- which services exist and what they are responsible for;
- which public operations each service exposes;
- what inputs each operation requires and what outputs it returns;
- what preconditions must be satisfied before an operation;
- what postconditions are guaranteed after a successful operation;
- which domain state transitions each operation performs;
- which errors each operation may raise;
- which repositories each service uses;
- how services integrate with the runtime orchestration layer.

## 1.2. In Scope

- Service responsibilities and public operation contracts.
- Input/output structures of each public service method.
- Preconditions and postconditions for every operation.
- Domain transitions performed by each operation.
- Errors raised by each operation.
- Repository usage by services.
- Factory functions and dependency wiring.
- Runtime integration (how `LoopOrchestrator` calls services).
- CLI tool usage of services.
- Future agent-to-service boundary definition.

## 1.3. Out of Scope

- API endpoints (no API exists in current MVP).
- UI screens, forms, dashboards.
- Database schemas and migrations.
- External platform integrations.
- Autoposting or automated distribution.
- Strategic decision-making (belongs to Intelligence Layer).
- New features (this is a current-state specification, not a task list).
- Code implementation changes.

---

# 2. Role of Services in LOOPRA Runtime

Services are lifecycle operators. They are the only layer that mutates domain
entities.

Services:

- validate preconditions before performing operations;
- create and update domain entities;
- enforce domain state transitions via `entity.transition_to()`;
- persist entities through repositories;
- return updated domain objects or structured results to the caller;
- expose stable contracts to runtime, CLI tools and future agents.

Services do not:

- decide strategy (which topic, which audience, which goal — Intelligence Layer);
- call external APIs in the current MVP;
- bypass domain transition rules in `core/domain/transitions.py`;
- write outside project scope;
- perform agent reasoning or decision-making;
- render media or interact with distribution platforms;
- extract or persist learning patterns (Learning Memory — future).

Principle:

> Services are the only layer that mutates domain entities.
> Runtime orchestrates services.
> Tools call services.
> Future agents call runtime/service contracts through approved entrypoints.

---

# 3. Service Contract Principles

1. **Services mutate domain entities; runtime does not.** Runtime coordinates
   service calls. Only services create, update and transition entities.

2. **Services enforce domain transitions.** Every status change passes through
   `entity.transition_to()`, which validates against the allowed transition maps
   in `core/domain/transitions.py`.

3. **Services are project-scoped.** Every operation receives `project_id` as its
   first argument. Every entity created carries `project_id`.

4. **Services validate preconditions before mutation.** Input fields are
   validated against allowed values. Required prerequisite states are checked
   before allowing the operation.

5. **Services return domain entities or structured results.** The caller
   receives the updated entity or a structured result dict, not raw storage
   handles.

6. **Services raise explicit validation errors.** All errors inherit from
   `ValueError` with descriptive messages. The caller knows exactly what failed
   and why.

7. **Repositories are implementation details behind services.** Callers never
   interact with repositories directly. Services own repository access.

8. **CLI tools and future agents must use services/runtime, not raw storage.**
   No direct filesystem mutation of entity JSON files outside of repositories.

9. **Future methods must preserve current contracts.** Existing method
   signatures, return types and error semantics must remain stable.

10. **Current MVP contracts must remain stable.** The Foundation MVP chain
    (Project → Idea → Scenario → ContentItem → ExportPackage → Publication →
    MetricSnapshot) must not be broken by future extensions.

---

# 4. Relationship to Domain Layer

The domain layer (`core/domain/`) defines:

- entities (`models.py`): `Workspace`, `Project`, `BrandProfile`, `Idea`,
  `Scenario`, `ContentItem`, `ExportPackage`, `Publication`, `MetricSnapshot`,
  `RenderJob`, `OutputFile`;
- enums/statuses (`enums.py`): `IdeaStatus`, `ScenarioStatus`,
  `ContentItemStatus`, `ExportPackageStatus`, `PublicationStatus`,
  `MetricSnapshotStatus`, etc.;
- transition rules (`transitions.py`): allowed status transitions per entity,
  enforced by `validate_status_transition()` and `entity.transition_to()`;
- validation constraints: field types, min_length, required fields, model
  validators.

Services use the domain layer to:

- instantiate entities with validated data;
- call `entity.transition_to()` to perform controlled status changes;
- validate that allowed transitions are respected;
- avoid illegal states (transition raises `InvalidStatusTransitionError`).

Domain layer has no filesystem side effects. Services own lifecycle operations.

---

# 5. Relationship to Repositories / Storage

Repositories:

- persist and load domain entities as JSON files on the local filesystem;
- scope all data by `project_id` under `{project_dir}/data/{collection}/`;
- do not make business decisions;
- do not enforce lifecycle semantics beyond basic storage constraints;
- validate entity ID patterns (regex `^[a-z0-9][a-z0-9_-]*$`).

Services:

- call repositories after validation;
- never expose raw storage mutation as a public contract;
- never allow callers to bypass repositories for entity access;
- preserve project scope in every read/write operation.

---

# 6. Relationship to Runtime Orchestration

Runtime calls services in sequence. Services execute atomic lifecycle operations.
Runtime does not mutate entities directly. `LoopOrchestrator` uses services as
its execution units.

```
Runtime command received (e.g., run_minimal_loop)
    ↓
Runtime validates project exists (ProjectService.get_project)
    ↓
Runtime calls service with validated inputs
    ↓
Service validates preconditions
    ↓
Service performs lifecycle operation (create, transition, persist)
    ↓
Service returns updated entity
    ↓
Runtime stores entity reference for next step
    ↓
... (repeat for all lifecycle steps)
    ↓
Runtime returns result with all entity IDs
```

Reference: `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md`, Sections 7, 10.

---

# 7. WorkspaceService Contract

**File:** `core/services/projects.py:56-63`

**Purpose:** Provide the single internal Workspace entity for the current MVP.

In the current Foundation MVP, a single hardcoded workspace (`internal`) serves
as the container for all projects. Multi-workspace management is a future
concept.

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `get_workspace()` | (none) | `Workspace` entity | None | Returns Workspace with `workspace_id="internal"`, `status=ACTIVE` |

**Errors:** None (always returns successfully).

**Current limitations:**
- Single hardcoded workspace — no multi-workspace support.
- No persistence — always returns the same in-memory entity.
- No workspace CRUD operations — workspaces are not mutable in MVP.

---

# 8. ProjectService Contract

**File:** `core/services/projects.py:66-113`

**Purpose:** Load and validate project configuration. Provide `Project` domain
entity to all downstream services.

**Dependencies:** `FileSystemProjectRepository`, `WorkspaceService`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `list_projects()` | (none) | `list[Project]` | None | All projects found under `PROJECTS_ROOT` are returned |
| `get_project(project_id)` | `project_id: str` | `Project` entity | Project dir and `project.yaml` exist | Returns validated Project with correct workspace scoping |

### Input Details — `get_project`

- `project_id`: string, must match a directory under `PROJECTS_ROOT` containing
  a valid `project.yaml`.

### Output Details — `get_project`

Returns a `Project` entity with:
- `project_id` — from config;
- `workspace_id` — from config or `WorkspaceService.get_workspace()` fallback;
- `name`, `slug`, `default_language`, `status` — from config.

### Required Config Fields

The following fields in `project.yaml` must be present and non-empty:
- `project_id` (id)
- `project_name` (name)
- `project_slug` (slug)
- `default_language` (language)
- `status`

### Errors

| Error | When Raised |
|---|---|
| `ProjectConfigValidationError` | Required fields are missing or empty |
| `ProjectConfigValidationError` | `status` value is not a valid `ProjectStatus` enum member |
| `FileNotFoundError` | Project directory or `project.yaml` does not exist |

### Side Effects

None. Read-only operation — no files are written.

---

# 9. BrandProfileService Contract

**File:** `core/services/projects.py:116-175`

**Purpose:** Derive a `BrandProfile` entity from raw project configuration.
Provides brand context for scenario generation and production.

**Dependencies:** `FileSystemProjectRepository`, `WorkspaceService`,
`ProjectService` (internally constructed).

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `get_brand_profile(project_id)` | `project_id: str` | `BrandProfile` entity | Project and brand config exist | Returns BrandProfile with all brand fields populated |

### Input Details — `get_brand_profile`

- `project_id`: string, must reference a valid project.

### Output Details

Returns a `BrandProfile` entity with:
- `brand_profile_id`: `f"brand_{project.project_id}"`
- `name`: from `config.brand.name`
- `positioning`: from `config.brand.positioning`
- `audience_summary`: from `config.brand.audience_summary`
- `language`: from `config.brand.language` or project `default_language`
- `brand_values`: from `config.brand.brand_values`
- `tone_of_voice`: `BrandToneOfVoice` (tone_summary, style_keywords,
  allowed_phrases, forbidden_phrases)
- `content_rules`: `BrandContentRules` (allowed_topics, forbidden_topics,
  writing_rules, claim_restrictions)
- `status`: resolved from `config.brand.status`, `config.status`, or context

### Required Brand Fields

These fields in `project.yaml` must be present and non-empty:
- `brand.name`
- `brand.positioning`
- `brand.audience_summary`

### Status Resolution

- If `config.brand.status` matches a `BrandProfileStatus` value → use it.
- If `positioning` and `audience_summary` are present → `ACTIVE`.
- Otherwise → `INCOMPLETE`.

### Errors

| Error | When Raised |
|---|---|
| `ProjectConfigValidationError` | Required brand fields are missing or empty |

### Side Effects

None. Read-only operation.

---

# 10. IdeaService Contract

**File:** `core/services/ideas.py:159-259`

**Purpose:** Manage the Idea lifecycle. Ideas are the starting point of the
content creation pipeline.

**Dependencies:** `FileSystemIdeaRepository`, `ProjectService`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `list_ideas(project_id)`, `list_ideas(project_id, status=...)` | `project_id: str`, `status: IdeaStatus | None` | `list[Idea]` | Project exists | All ideas (optionally filtered by status) returned |
| `get_idea(project_id, idea_id)` | `project_id`, `idea_id: str` | `Idea` | Project exists, idea JSON file exists | Returns loaded Idea entity |
| `create_idea(project_id, *, title, ...)` | see below | `Idea` (status=RAW) | Project exists, valid inputs | New Idea persisted with ID `idea_{uuid}` |
| `approve_idea(project_id, idea_id)` | `project_id`, `idea_id: str` | `Idea` (status=APPROVED) | Idea exists | Transition RAW → APPROVED |
| `reject_idea(project_id, idea_id)` | `project_id`, `idea_id: str` | `Idea` (status=REJECTED) | Idea exists | Transition RAW → REJECTED |
| `archive_idea(project_id, idea_id)` | `project_id`, `idea_id: str` | `Idea` (status=ARCHIVED) | Idea exists | Transition any allowed → ARCHIVED |
| `next_action_for(idea)` | `idea: Idea` | `str` (action name) | Idea entity provided | Returns suggested next action based on status |

### Input Details — `create_idea`

| Parameter | Type | Default | Constraints |
|---|---|---|---|
| `project_id` | `str` | (required) | Must reference a valid project |
| `title` | `str` | (required) | Must be non-empty |
| `description` | `str` | `""` | — |
| `topic` | `str` | `""` | — |
| `funnel_stage` | `str` | `"attention"` | One of: attention, trust, conversion, retention |
| `content_format` | `ContentFormat` | `TEXT_SOCIAL_POST` | Currently only `text_social_post` is supported |
| `source_type` | `str` | `"manual"` | One of: manual, trend, analytics_insight, content_strategy, past_content, campaign, import, agent_suggestion |
| `source_id` | `str` | `""` | — |
| `priority` | `str` | `"medium"` | One of: low, medium, high, urgent |
| `tags` | `Sequence[str] | None` | `None` | — |

### next_action_for Mapping

| IdeaStatus | Action |
|---|---|
| `RAW` | `approve_or_reject` |
| `APPROVED` | `generate_scenario` |
| `REJECTED` | `archive` |
| `SCRIPTED` | `open_scenarios` |
| `ARCHIVED` | `none` |

### Domain Transitions Performed

| Operation | From | To | Transition Rule |
|---|---|---|---|
| `approve_idea` | RAW | APPROVED | `RAW → {APPROVED, REJECTED, ARCHIVED}` |
| `reject_idea` | RAW | REJECTED | `RAW → {APPROVED, REJECTED, ARCHIVED}` |
| `archive_idea` | any allowed | ARCHIVED | e.g. `APPROVED → {SCRIPTED, ARCHIVED}`, `REJECTED → {ARCHIVED}` |

### Errors

| Error | When Raised |
|---|---|
| `IdeaBankValidationError` | Invalid `funnel_stage`, `source_type`, or `priority` |
| `InvalidStatusTransitionError` | Illegal status transition (e.g., approving an already APPROVED idea) |
| `FileNotFoundError` | Idea or project not found |

### Side Effects

- `create_idea`: writes `{project_dir}/data/ideas/{idea_id}.json`.
- `approve_idea`, `reject_idea`, `archive_idea`: overwrites the idea JSON file
  with updated status.

---

# 11. ScenarioService Contract

**File:** `core/services/ideas.py:263-619`

**Purpose:** Manage the Scenario lifecycle. Scenarios are structured content
plans created from Ideas. Run scenario-level QA checks.

**Dependencies:** `FileSystemScenarioRepository`, `FileSystemProjectRepository`,
`ProjectService`, `BrandProfileService`, `IdeaService`,
`FileSystemIdeaRepository`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `list_scenarios(project_id)`, `list_scenarios(project_id, idea_id=..., content_format=...)` | `project_id`, optional filters | `list[Scenario]` | Project exists | Filtered scenario list |
| `get_scenario(project_id, scenario_id)` | `project_id`, `scenario_id` | `Scenario` | Project exists, scenario JSON exists | Returns loaded Scenario |
| `create_manual_scenario(project_id, *, title, ...)` | see below | `Scenario` (status=DRAFT) | Project and brand profile exist | Creates manual scenario |
| `create_from_idea(project_id, idea_id, *, ...)` | see below | `Scenario` (status=NEEDS_REVIEW) | Idea is APPROVED or SCRIPTED | Scenario created with text blocks, captions, QA warnings. Idea transitions to SCRIPTED if currently APPROVED |
| `submit_for_review(project_id, scenario_id)` | `project_id`, `scenario_id` | `Scenario` (NEEDS_REVIEW) | Scenario exists | Transition DRAFT → NEEDS_REVIEW |
| `approve_scenario(project_id, scenario_id)` | `project_id`, `scenario_id` | `Scenario` (APPROVED) | Scenario exists | Transition NEEDS_REVIEW → APPROVED |
| `reject_scenario(project_id, scenario_id)` | `project_id`, `scenario_id` | `Scenario` (REJECTED) | Scenario exists | Transition NEEDS_REVIEW → REJECTED |
| `archive_scenario(project_id, scenario_id)` | `project_id`, `scenario_id` | `Scenario` (ARCHIVED) | Scenario exists | Transition any allowed → ARCHIVED |

### Input Details — `create_from_idea`

| Parameter | Type | Default | Constraints |
|---|---|---|---|
| `project_id` | `str` | (required) | Valid project |
| `idea_id` | `str` | (required) | Idea must exist and be APPROVED or SCRIPTED |
| `content_format` | `ContentFormat | None` | `None` (falls back to idea.content_format) | Must be `TEXT_SOCIAL_POST` in current MVP |
| `target_platforms` | `Sequence[PublishingPlatform | str] | None` | `None` (resolved from project config or defaults) | — |

### Key Behaviour — `create_from_idea`

1. Validates Idea status is `APPROVED` or `SCRIPTED`.
2. Validates content format is `TEXT_SOCIAL_POST` (only supported format).
3. Resolves target platforms from: explicit parameter → project config →
   defaults `[TELEGRAM, THREADS, VK]`.
4. Builds `ScenarioTextBlock` entries per platform with templated text
   (hook → explanation → insight → CTA).
5. Generates caption drafts per platform.
6. Runs `text_social_post` QA: checks body length, forbidden phrases,
   forbidden topics, conversion-stage CTA presence.
7. Creates Scenario with status `NEEDS_REVIEW`.
8. If Idea was `APPROVED`, transitions Idea to `SCRIPTED`.

### Domain Transitions Performed

| Operation | Entity | From | To | Transition Rule |
|---|---|---|---|---|
| `create_from_idea` | Idea (side effect) | APPROVED | SCRIPTED | `APPROVED → {SCRIPTED, ARCHIVED}` |
| `create_from_idea` | Scenario | — | NEEDS_REVIEW | New entity |
| `submit_for_review` | Scenario | DRAFT | NEEDS_REVIEW | `DRAFT → {NEEDS_REVIEW, ARCHIVED}` |
| `approve_scenario` | Scenario | NEEDS_REVIEW | APPROVED | `NEEDS_REVIEW → {APPROVED, REJECTED, ARCHIVED}` |
| `reject_scenario` | Scenario | NEEDS_REVIEW | REJECTED | `NEEDS_REVIEW → {APPROVED, REJECTED, ARCHIVED}` |
| `archive_scenario` | Scenario | any allowed | ARCHIVED | Various |

### Errors

| Error | When Raised |
|---|---|
| `ScenarioStudioValidationError` | Idea is not APPROVED or SCRIPTED |
| `ScenarioStudioValidationError` | Content format is not `TEXT_SOCIAL_POST` |
| `IdeaBankValidationError` | Invalid `funnel_stage` (reused from IdeaService validator) |
| `InvalidStatusTransitionError` | Illegal scenario or idea status transition |
| `FileNotFoundError` | Entity not found |

### Side Effects

- Persists `{project_dir}/data/scenarios/{scenario_id}.json`.
- On `create_from_idea`: may also update `{project_dir}/data/ideas/{idea_id}.json`
  (Idea transition to SCRIPTED).

---

# 12. ProductionLifecycleService Contract

**File:** `core/services/production.py:31-132`

**Purpose:** Manage the ContentItem production lifecycle. Create content items
from approved scenarios, run technical QA, approve content for export.

**Dependencies:** `FileSystemContentItemRepository`,
`FileSystemScenarioRepository`, `ProjectService`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `list_content_items(project_id)` | `project_id` | `list[ContentItem]` | Project exists | All content items returned |
| `get_content_item(project_id, content_item_id)` | `project_id`, `content_item_id` | `ContentItem` | Project exists, entity JSON exists | Returns loaded ContentItem |
| `create_content_item(project_id, scenario_id)` | `project_id`, `scenario_id` | `ContentItem` (status=RENDERED) | Scenario is APPROVED | ContentItem created and auto-transitioned DRAFT → IN_PRODUCTION → RENDERED |
| `run_technical_qa(project_id, content_item_id)` | `project_id`, `content_item_id` | `ContentItem` (status=NEEDS_REVIEW or QA_FAILED) | ContentItem exists | QA results recorded in render_output_metadata |
| `approve_content(project_id, content_item_id)` | `project_id`, `content_item_id` | `ContentItem` (status=APPROVED) | ContentItem exists | Transition NEEDS_REVIEW → APPROVED |

### Input Details — `create_content_item`

| Parameter | Type | Constraints |
|---|---|---|
| `project_id` | `str` | Valid project |
| `scenario_id` | `str` | Scenario must exist and be APPROVED |

### Key Behaviour — `create_content_item`

1. Loads project and scenario.
2. Validates scenario status is `APPROVED`.
3. Creates ContentItem from scenario data:
   - `title`: from scenario `title`
   - `body`: from `scenario.draft_text` or concatenated block texts
   - `content_format`: from scenario
   - `render_output_metadata`: includes source_type, source_id,
     target_platforms, content_kind, scenario_qa_warnings
4. Auto-transitions: `DRAFT → IN_PRODUCTION → RENDERED`.
5. Persists the ContentItem.

### Key Behaviour — `run_technical_qa`

1. Collects QA errors: empty title, empty body, missing brand_profile_id.
2. Records `technical_qa_errors` and `technical_qa_checked_at` in metadata.
3. If no errors → transition to `NEEDS_REVIEW`.
4. If errors found → transition to `QA_FAILED`.

### Domain Transitions Performed

| Operation | From | To | Transition Rule |
|---|---|---|---|
| `create_content_item` | DRAFT (new) | IN_PRODUCTION | `DRAFT → {IN_PRODUCTION, ARCHIVED}` |
| `create_content_item` | IN_PRODUCTION | RENDERED | `IN_PRODUCTION → {RENDERED, QA_FAILED, ARCHIVED}` |
| `run_technical_qa` | RENDERED | NEEDS_REVIEW | `RENDERED → {NEEDS_REVIEW, QA_FAILED, ARCHIVED}` |
| `run_technical_qa` | RENDERED | QA_FAILED | `RENDERED → {NEEDS_REVIEW, QA_FAILED, ARCHIVED}` |
| `approve_content` | NEEDS_REVIEW | APPROVED | `NEEDS_REVIEW → {APPROVED, REJECTED, ARCHIVED}` |

### Errors

| Error | When Raised |
|---|---|
| `ProductionLifecycleValidationError` | Scenario is not APPROVED |
| `InvalidStatusTransitionError` | Illegal content item status transition |
| `FileNotFoundError` | ContentItem or Scenario not found |

### Current Limitations

- Only `text_social_post` content format is supported.
- QA checks are limited to: empty title, empty body, missing brand_profile_id.
- No media rendering, no multi-format production.

---

# 13. PublishingService Contract

**File:** `core/services/publishing.py:56-379`

**Purpose:** Manage the publishing lifecycle. Create export packages, write
export files to disk, create publication records, record publication outcomes.

**Dependencies:** `FileSystemExportPackageRepository`,
`FileSystemPublicationRepository`, `FileSystemContentItemRepository`,
`FileSystemScenarioRepository`, `ProjectService`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `list_export_packages(project_id)` | `project_id` | `list[ExportPackage]` | Project exists | All export packages returned |
| `get_export_package(project_id, export_package_id)` | `project_id`, `export_package_id` | `ExportPackage` | Project exists, entity JSON exists | Returns loaded ExportPackage |
| `list_publications(project_id)` | `project_id` | `list[Publication]` | Project exists | All publications returned |
| `get_publication(project_id, publication_id)` | `project_id`, `publication_id` | `Publication` | Project exists, entity JSON exists | Returns loaded Publication |
| `create_export_package(project_id, content_item_id, target_platform)` | see below | `ExportPackage` (status=DRAFT) | ContentItem is APPROVED | ExportPackage created |
| `prepare_export(project_id, export_package_id)` | `project_id`, `export_package_id` | `ExportPackage` (status=READY) | ExportPackage is DRAFT; ContentItem is APPROVED or EXPORTED | Files written to disk. ContentItem transitions to EXPORTED if currently APPROVED |
| `create_publication(project_id, content_item_id, export_package_id)` | see below | `Publication` (status=PLANNED) | ExportPackage is READY; ContentItem is EXPORTED; content_item_id and export_package_id match | Publication record created |
| `publish_content(project_id, publication_id, published_url)` | `project_id`, `publication_id`, `published_url: str` | `Publication` (status=PUBLISHED) | Publication exists; `published_url` not empty | Publication recorded with URL and timestamp |
| `fail_publication(project_id, publication_id, error)` | `project_id`, `publication_id`, `error: str` | `Publication` (status=FAILED) | Publication exists | Publication marked as FAILED with error reason |

### Input Details — `create_export_package`

| Parameter | Type | Constraints |
|---|---|---|
| `project_id` | `str` | Valid project |
| `content_item_id` | `str` | ContentItem must exist and be APPROVED |
| `target_platform` | `PublishingPlatform | str` | Valid platform |

### Input Details — `prepare_export`

| Parameter | Type | Constraints |
|---|---|---|
| `project_id` | `str` | Valid project |
| `export_package_id` | `str` | ExportPackage must exist and be in DRAFT status |

### Input Details — `create_publication`

| Parameter | Type | Constraints |
|---|---|---|
| `project_id` | `str` | Valid project |
| `content_item_id` | `str` | Must match ExportPackage.content_item_id |
| `export_package_id` | `str` | Must be READY |

### Key Behaviour — `prepare_export`

Writes the following files to `{project_dir}/exports/{export_package_id}/`:

| File | Content |
|---|---|
| `title.txt` | ContentItem title |
| `body.txt` | ContentItem body |
| `caption_{platform}.txt` | Platform-specific caption (from scenario caption_drafts or export_package caption_variants) |
| `manual_publication_checklist.txt` | Human-readable checklist for manual publishing |
| `metadata.json` | Export metadata (project_id, content_item_id, scenario_id, format, platform, timestamps, brand info, funnel_stage, QA warnings) |
| `manifest.json` | File listing with name, role, package_id, project_id, status, timestamps |

### Domain Transitions Performed

| Operation | Entity | From | To | Transition Rule |
|---|---|---|---|---|
| `create_export_package` | ExportPackage | — | DRAFT | New entity |
| `prepare_export` | ExportPackage | DRAFT | READY | `DRAFT → {READY, FAILED, ARCHIVED}` |
| `prepare_export` (side effect) | ContentItem | APPROVED | EXPORTED | `APPROVED → {EXPORTED, ARCHIVED}` |
| `create_publication` | Publication | — | PLANNED | New entity |
| `publish_content` | Publication | PLANNED | PUBLISHED | `PLANNED → {PUBLISHED, FAILED, ARCHIVED}` |
| `fail_publication` | Publication | PLANNED | FAILED | `PLANNED → {PUBLISHED, FAILED, ARCHIVED}` |

### Errors

| Error | When Raised |
|---|---|
| `PublishingValidationError` | ContentItem is not APPROVED (create_export_package) |
| `PublishingValidationError` | ExportPackage is not DRAFT (prepare_export) |
| `PublishingValidationError` | ContentItem is not APPROVED or EXPORTED (prepare_export) |
| `PublishingValidationError` | ExportPackage and ContentItem IDs do not match (create_publication) |
| `PublishingValidationError` | ExportPackage is not READY (create_publication) |
| `PublishingValidationError` | ContentItem is not EXPORTED (create_publication) |
| `PublishingValidationError` | `published_url` is empty (publish_content) |
| `InvalidStatusTransitionError` | Illegal entity status transition |
| `FileNotFoundError` | Entity not found |

### Current Limitations

- Manual publication only (`publication_method = "manual"`).
- No autoposting, no external platform API calls.
- Export package output is text-only (no images, video, audio).
- Placeholder publication URL generated by `LoopOrchestrator` for smoke loop.

---

# 14. AnalyticsService Contract

**File:** `core/services/analytics.py:55-183`

**Purpose:** Manage the analytics lifecycle. Create draft metric snapshots,
record manual metrics, normalize metric keys.

**Dependencies:** `FileSystemMetricSnapshotRepository`,
`FileSystemPublicationRepository`, `FileSystemContentItemRepository`,
`ProjectService`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `list_metric_snapshots(project_id)` | `project_id` | `list[MetricSnapshot]` | Project exists | All metric snapshots returned |
| `get_metric_snapshot(project_id, metric_snapshot_id)` | `project_id`, `metric_snapshot_id` | `MetricSnapshot` | Project exists, entity JSON exists | Returns loaded MetricSnapshot |
| `create_metric_snapshot(project_id, publication_id, content_item_id)` | see below | `MetricSnapshot` (status=DRAFT) | Publication is PUBLISHED; publication and content_item match | Draft snapshot created |
| `record_metrics(project_id, metric_snapshot_id, metrics)` | see below | `MetricSnapshot` (status=RECORDED) | Snapshot is DRAFT; metrics valid | Metrics recorded, snapshot transitions to RECORDED |
| `get_insights(project_id)` | `project_id` | `list[dict[str, str]]` | — | Returns empty list (stub) |
| `generate_new_ideas_from_metrics(project_id)` | `project_id` | `list[dict[str, str]]` | — | Returns empty list (stub) |

### Input Details — `create_metric_snapshot`

| Parameter | Type | Constraints |
|---|---|---|
| `project_id` | `str` | Valid project |
| `publication_id` | `str` | Publication must exist and be PUBLISHED |
| `content_item_id` | `str` | Must match publication.content_item_id |

### Input Details — `record_metrics`

| Parameter | Type | Constraints |
|---|---|---|
| `project_id` | `str` | Valid project |
| `metric_snapshot_id` | `str` | Snapshot must exist and be DRAFT |
| `metrics` | `dict[str, Any]` | Non-empty dict with known keys |

### Supported Metric Keys

| Input Key | Normalized Field | Type | Constraints |
|---|---|---|---|
| `views` | `content_metrics.views` | `int` | `>= 0` |
| `likes` | `content_metrics.likes` | `int` | `>= 0` |
| `comments` | `content_metrics.comments` | `int` | `>= 0` |
| `shares` | `content_metrics.shares` | `int` | `>= 0` |
| `saves` | `content_metrics.saves` | `int` | `>= 0` |
| `clicks` | `content_metrics.link_clicks` | `int` | `>= 0` |
| `published_url` | Updates Publication.published_url | `str` | Non-empty |

### Key Behaviour — `record_metrics`

1. Validates all keys are in `SUPPORTED_MANUAL_METRIC_KEYS`.
2. Validates numeric fields are non-negative integers, `published_url` is a
   non-empty string.
3. If `published_url` is provided and differs from the current Publication's
   URL, updates the Publication's `published_url`.
4. Merges provided metrics into `ContentPerformanceMetrics`.
5. Transitions MetricSnapshot from `DRAFT` to `RECORDED`.
6. Updates `captured_at` timestamp.

### Domain Transitions Performed

| Operation | From | To | Transition Rule |
|---|---|---|---|
| `create_metric_snapshot` | — | DRAFT | New entity |
| `record_metrics` | DRAFT | RECORDED | `DRAFT → {RECORDED, INVALID}` |

### Errors

| Error | When Raised |
|---|---|
| `AnalyticsValidationError` | Publication is not PUBLISHED |
| `AnalyticsValidationError` | Publication and ContentItem do not match |
| `AnalyticsValidationError` | MetricSnapshot is not DRAFT |
| `AnalyticsValidationError` | `metrics` is empty or not a dict |
| `AnalyticsValidationError` | Unknown metric keys |
| `AnalyticsValidationError` | Numeric values are not non-negative integers |
| `AnalyticsValidationError` | `published_url` is empty string |
| `InvalidStatusTransitionError` | Illegal snapshot status transition |

### Stub Methods

`get_insights()` and `generate_new_ideas_from_metrics()` are stubs that return
empty lists. They exist as architectural placeholders for future Intelligence
Layer integration. They are not active in the current MVP.

### Current Limitations

- Manual metrics only (`source_type = "manual"`).
- No automated metric collection or platform API connectors.
- `get_insights` and `generate_new_ideas_from_metrics` are stubs.
- No cross-snapshot aggregation or time-series analysis.
- No benchmark comparison or goal-evaluation logic.

---

# 15. LoopOrchestrator Contract

**File:** `core/services/loop.py:20-155`

**Purpose:** Coordinate the full Foundation MVP lifecycle from Idea to
MetricSnapshot. The `LoopOrchestrator` is the primary runtime component
that binds services into a complete execution flow.

**Dependencies:** `IdeaService`, `ScenarioService`,
`ProductionLifecycleService`, `PublishingService`, `AnalyticsService`.

### Operations

| Operation | Input | Output | Preconditions | Postconditions |
|---|---|---|---|---|
| `run_minimal_loop(project_id, idea_id, target_platform=...)` | see below | `dict[str, str]` with all entity IDs | Idea exists; project exists | Full lifecycle executed. Returns dict with all entity IDs |
| `get_loop_status(project_id)` | `project_id: str` | `dict[str, object]` | Project exists | Status counts per entity type |

### Input Details — `run_minimal_loop`

| Parameter | Type | Default | Constraints |
|---|---|---|---|
| `project_id` | `str` | (required) | Valid project |
| `idea_id` | `str` | (required) | Idea must exist |
| `target_platform` | `PublishingPlatform | str | None` | `None` (resolved from scenario platforms) | Uses first scenario platform if not provided |

### Execution Flow

```
run_minimal_loop(project_id, idea_id, target_platform):
    1. get_idea → if RAW, approve_idea (RAW → APPROVED)
    2. create_from_idea → Scenario (NEEDS_REVIEW)
    3. approve_scenario → Scenario (APPROVED)
    4. create_content_item → ContentItem (RENDERED)
    5. run_technical_qa → ContentItem (NEEDS_REVIEW)
    6. approve_content → ContentItem (APPROVED)
    7. create_export_package → ExportPackage (DRAFT)
    8. prepare_export → ExportPackage (READY), ContentItem (EXPORTED)
    9. create_publication → Publication (PLANNED)
   10. publish_content → Publication (PUBLISHED)
   11. create_metric_snapshot → MetricSnapshot (DRAFT)
   Return dict with all entity IDs and "status": "completed"
```

### Result Dict

```python
{
    "project_id": str,
    "idea_id": str,
    "scenario_id": str,
    "content_item_id": str,
    "export_package_id": str,
    "publication_id": str,
    "metric_snapshot_id": str,
    "status": "completed",
}
```

### get_loop_status Output

```python
{
    "project_id": str,
    "ideas": {"raw": N, "approved": N, ...},
    "scenarios": {"draft": N, "needs_review": N, ...},
    "content_items": {"draft": N, "rendered": N, ...},
    "export_packages": {"draft": N, "ready": N, ...},
    "publications": {"planned": N, "published": N, ...},
    "metric_snapshots": {"draft": N, "recorded": N, ...},
}
```

### Errors

Any error from the underlying services propagates to the caller:
- `IdeaBankValidationError`
- `ScenarioStudioValidationError`
- `ProductionLifecycleValidationError`
- `PublishingValidationError`
- `AnalyticsValidationError`
- `InvalidStatusTransitionError`
- `FileNotFoundError`

### Failure Behaviour

If any step fails (exception raised), execution stops and the exception
propagates to the caller. The current MVP does not support mid-flow resume.
A retry means rerunning the entire loop from the beginning.

### Current Limitations

- Single platform per loop (first target platform selected).
- No step retry within a single execution — failure requires complete rerun.
- No persistent execution context — state is in-memory only.
- Not idempotent — each run creates new entities with new IDs.
- Placeholder publication URL `https://example.invalid/...` used in smoke loop.

**Important:** `LoopOrchestrator` coordinates. It does not own service logic.
Each step delegates fully to the respective service.

---

# 16. Repository Contracts

Repositories are the persistence layer behind services. They are not public
business APIs. Services own the lifecycle semantics; repositories own storage.

All current repositories are filesystem-based, storing entities as JSON files
under `{project_dir}/data/{collection}/`.

### 16.1. FileSystemProjectRepository

**File:** `core/services/projects.py:28-54`

| Attribute | Value |
|---|---|
| Entity type | `Project` (via `ProjectConfig` → `Project` conversion) |
| Storage path | `{PROJECTS_ROOT}/{project_id}/project.yaml` |
| Public operations | `list_project_ids() → list[str]` |
| | `load_project_config(project_id) → ProjectConfig` |

Scans directory entries, checks for `project.yaml`, validates project IDs.

### 16.2. FileSystemIdeaRepository

**File:** `core/services/ideas.py:116-132`

Extends `_FileSystemProjectEntityRepository`.

| Attribute | Value |
|---|---|
| Entity type | `Idea` |
| Collection | `ideas` |
| Storage path | `{project_dir}/data/ideas/{idea_id}.json` |
| Public operations | `list_ideas(project_id) → list[Idea]` |
| | `load_idea(project_id, idea_id) → Idea` |
| | `save_idea(idea) → Idea` |

### 16.3. FileSystemScenarioRepository

**File:** `core/services/ideas.py:135-156`

Extends `_FileSystemProjectEntityRepository`.

| Attribute | Value |
|---|---|
| Entity type | `Scenario` |
| Collection | `scenarios` |
| Storage path | `{project_dir}/data/scenarios/{scenario_id}.json` |
| Public operations | `list_scenarios(project_id) → list[Scenario]` |
| | `load_scenario(project_id, scenario_id) → Scenario` |
| | `save_scenario(scenario) → Scenario` |

### 16.4. FileSystemContentItemRepository

**File:** `core/services/production.py:17-28`

Extends `FileSystemProjectModelRepository[ContentItem]`.

| Attribute | Value |
|---|---|
| Entity type | `ContentItem` |
| Collection | `content_items` |
| Storage path | `{project_dir}/data/content_items/{content_item_id}.json` |
| Public operations | `list_content_items(project_id) → list[ContentItem]` |
| | `load_content_item(project_id, content_item_id) → ContentItem` |
| | `save_content_item(content_item) → ContentItem` |

### 16.5. FileSystemExportPackageRepository

**File:** `core/services/publishing.py:28-39`

Extends `FileSystemProjectModelRepository[ExportPackage]`.

| Attribute | Value |
|---|---|
| Entity type | `ExportPackage` |
| Collection | `export_packages` |
| Storage path | `{project_dir}/data/export_packages/{export_package_id}.json` |
| Public operations | `list_export_packages(project_id) → list[ExportPackage]` |
| | `load_export_package(project_id, export_package_id) → ExportPackage` |
| | `save_export_package(export_package) → ExportPackage` |

### 16.6. FileSystemPublicationRepository

**File:** `core/services/publishing.py:42-53`

Extends `FileSystemProjectModelRepository[Publication]`.

| Attribute | Value |
|---|---|
| Entity type | `Publication` |
| Collection | `publications` |
| Storage path | `{project_dir}/data/publications/{publication_id}.json` |
| Public operations | `list_publications(project_id) → list[Publication]` |
| | `load_publication(project_id, publication_id) → Publication` |
| | `save_publication(publication) → Publication` |

### 16.7. FileSystemMetricSnapshotRepository

**File:** `core/services/analytics.py:41-52`

Extends `FileSystemProjectModelRepository[MetricSnapshot]`.

| Attribute | Value |
|---|---|
| Entity type | `MetricSnapshot` |
| Collection | `metric_snapshots` |
| Storage path | `{project_dir}/data/metric_snapshots/{metric_snapshot_id}.json` |
| Public operations | `list_metric_snapshots(project_id) → list[MetricSnapshot]` |
| | `load_metric_snapshot(project_id, metric_snapshot_id) → MetricSnapshot` |
| | `save_metric_snapshot(metric_snapshot) → MetricSnapshot` |

### 16.8. FileSystemProjectModelRepository (Base Class)

**File:** `core/services/_storage.py:22-74`

Generic base class for all entity-specific repositories.

| Attribute | Value |
|---|---|
| Generic parameter | `ModelT` bound to `BaseModel` |
| Storage path | `{project_dir}/data/{collection}/{entity_id}.json` |
| Public operations | `list_models(project_id) → list[ModelT]` |
| | `load_model(project_id, entity_id, *, entity_name) → ModelT` |
| | `save_model(project_id, entity_id, model) → ModelT` |
| Validation | Entity IDs validated against `^[a-z0-9][a-z0-9_-]*$` |

### Repository Boundaries

Repositories must not:
- make business decisions;
- enforce lifecycle semantics;
- validate entity state transitions;
- perform cross-project operations;
- expose raw storage mutation as a public API.

Repositories may:
- persist and load entities as JSON;
- validate entity ID format;
- raise `FileNotFoundError` if entity not found;
- create parent directories during save.

---

# 17. Factory Functions / Dependency Wiring

Factory functions wire repositories and services together with correct
dependency injection. All factories accept an optional `projects_root: Path`
parameter to control the filesystem root for project data.

### 17.1. `build_loop_orchestrator(projects_root) → LoopOrchestrator`

**File:** `core/services/loop.py:134-155`

Dependencies wired:
- `FileSystemProjectRepository` → `ProjectService`
- `BrandProfileService`
- `FileSystemIdeaRepository` → `IdeaService`
- `FileSystemScenarioRepository` + `FileSystemProjectRepository` + `ProjectService` + `BrandProfileService` + `IdeaService` + `FileSystemIdeaRepository` → `ScenarioService`
- `build_production_lifecycle_service(projects_root)` → `ProductionLifecycleService`
- `build_publishing_service(projects_root)` → `PublishingService`
- `build_analytics_service(projects_root)` → `AnalyticsService`

Purpose: The main entry point for full lifecycle execution. Used by
`smoke_loop.py` and tests.

### 17.2. `build_production_lifecycle_service(projects_root) → ProductionLifecycleService`

**File:** `core/services/production.py:125-132`

Dependencies wired:
- `FileSystemProjectRepository` → `ProjectService`
- `FileSystemContentItemRepository`
- `FileSystemScenarioRepository`
- → `ProductionLifecycleService`

### 17.3. `build_publishing_service(projects_root) → PublishingService`

**File:** `core/services/publishing.py:369-379`

Dependencies wired:
- `FileSystemProjectRepository` → `ProjectService`
- `FileSystemExportPackageRepository`
- `FileSystemPublicationRepository`
- `FileSystemContentItemRepository`
- `FileSystemScenarioRepository`
- `projects_root` (passed directly for export directory resolution)
- → `PublishingService`

### 17.4. `build_analytics_service(projects_root) → AnalyticsService`

**File:** `core/services/analytics.py:175-183`

Dependencies wired:
- `FileSystemProjectRepository` → `ProjectService`
- `FileSystemMetricSnapshotRepository`
- `FileSystemPublicationRepository`
- `FileSystemContentItemRepository`
- → `AnalyticsService`

### Runtime Role

These factories are the canonical way to construct service instances. They
ensure correct dependency injection and replaceable storage backends. All tests
and CLI scripts use these factories (directly or through
`build_loop_orchestrator`).

---

# 18. Service Error Model

All service errors inherit from `ValueError`. Each error class identifies the
domain that raised it.

### Error Catalog

| Error Class | File | When Raised |
|---|---|---|
| `ProjectConfigValidationError` | `projects.py:24` | Missing required fields in project config; invalid status value; missing required BrandProfile fields |
| `IdeaBankValidationError` | `ideas.py:49` | Invalid `funnel_stage`, `source_type`, `priority`; invalid entity ID format |
| `ScenarioStudioValidationError` | `ideas.py:53` | Idea not APPROVED/SCRIPTED; unsupported content format |
| `ProductionLifecycleValidationError` | `production.py:13` | Scenario not APPROVED before ContentItem creation |
| `PublishingValidationError` | `publishing.py:24` | ContentItem not APPROVED; ExportPackage not DRAFT/READY; content_item_id/export_package_id mismatch; empty published_url |
| `AnalyticsValidationError` | `analytics.py:17` | Publication not PUBLISHED; invalid metric keys/values; snapshot not DRAFT; empty metrics |
| `InvalidStatusTransitionError` | `transitions.py:17` | Any illegal entity status transition (domain layer, raised by `entity.transition_to()`) |

### General Principles

| Aspect | Principle |
|---|---|
| Raise condition | Service validates preconditions first; raises before any mutation |
| Typical cause | Invalid input, wrong entity state, missing prerequisite |
| Recommended action | Read error message; fix input/state; retry operation |
| Retry allowed | Yes, for most errors (after fixing the cause). Config errors require fix first |
| Error propagation | Errors propagate to runtime caller; no silent swallowing |

### Repository-Level Errors

- `FileNotFoundError`: entity JSON file not found at expected path.
- `ValueError`: invalid entity ID format (from `_validate_entity_id`).

---

# 19. Domain Transition Mapping by Service

All transitions are enforced by `entity.transition_to()` which uses the
transition maps defined in `core/domain/transitions.py`. Services never bypass
these checks.

| Service | Operation | Entity | Required Status | Resulting Status | Transition Rule |
|---|---|---|---|---|---|
| IdeaService | `approve_idea` | Idea | RAW | APPROVED | `RAW → {APPROVED, REJECTED, ARCHIVED}` |
| IdeaService | `reject_idea` | Idea | RAW | REJECTED | `RAW → {APPROVED, REJECTED, ARCHIVED}` |
| IdeaService | `archive_idea` | Idea | any allowed | ARCHIVED | Various → ARCHIVED |
| ScenarioService | `create_from_idea` | Idea | APPROVED | SCRIPTED | `APPROVED → {SCRIPTED, ARCHIVED}` |
| ScenarioService | `create_from_idea` | Scenario | — (new) | NEEDS_REVIEW | New entity |
| ScenarioService | `submit_for_review` | Scenario | DRAFT | NEEDS_REVIEW | `DRAFT → {NEEDS_REVIEW, ARCHIVED}` |
| ScenarioService | `approve_scenario` | Scenario | NEEDS_REVIEW | APPROVED | `NEEDS_REVIEW → {APPROVED, REJECTED, ARCHIVED}` |
| ScenarioService | `reject_scenario` | Scenario | NEEDS_REVIEW | REJECTED | `NEEDS_REVIEW → {APPROVED, REJECTED, ARCHIVED}` |
| ScenarioService | `archive_scenario` | Scenario | any allowed | ARCHIVED | Various → ARCHIVED |
| ProductionLifecycleService | `create_content_item` | ContentItem | — (new) | DRAFT → IN_PRODUCTION → RENDERED | `DRAFT → IN_PRODUCTION → RENDERED` |
| ProductionLifecycleService | `run_technical_qa` | ContentItem | RENDERED | NEEDS_REVIEW or QA_FAILED | `RENDERED → {NEEDS_REVIEW, QA_FAILED, ARCHIVED}` |
| ProductionLifecycleService | `approve_content` | ContentItem | NEEDS_REVIEW | APPROVED | `NEEDS_REVIEW → {APPROVED, REJECTED, ARCHIVED}` |
| PublishingService | `create_export_package` | ExportPackage | — (new) | DRAFT | New entity |
| PublishingService | `prepare_export` | ExportPackage | DRAFT | READY | `DRAFT → {READY, FAILED, ARCHIVED}` |
| PublishingService | `prepare_export` | ContentItem | APPROVED | EXPORTED | `APPROVED → {EXPORTED, ARCHIVED}` |
| PublishingService | `create_publication` | Publication | — (new) | PLANNED | New entity |
| PublishingService | `publish_content` | Publication | PLANNED | PUBLISHED | `PLANNED → {PUBLISHED, FAILED, ARCHIVED}` |
| PublishingService | `fail_publication` | Publication | PLANNED | FAILED | `PLANNED → {PUBLISHED, FAILED, ARCHIVED}` |
| AnalyticsService | `create_metric_snapshot` | MetricSnapshot | — (new) | DRAFT | New entity |
| AnalyticsService | `record_metrics` | MetricSnapshot | DRAFT | RECORDED | `DRAFT → {RECORDED, INVALID}` |

---

# 20. Current MVP Service Flow

The full Foundation MVP lifecycle executed by `LoopOrchestrator.run_minimal_loop()`:

```
ProjectService.get_project()
    ↓ validates project exists
IdeaService.approve_idea()           [Idea RAW → APPROVED]
    ↓
ScenarioService.create_from_idea()   [Scenario new → NEEDS_REVIEW; Idea APPROVED → SCRIPTED]
    ↓
ScenarioService.approve_scenario()   [Scenario NEEDS_REVIEW → APPROVED]
    ↓
ProductionLifecycleService.create_content_item()  [ContentItem DRAFT → IN_PRODUCTION → RENDERED]
    ↓
ProductionLifecycleService.run_technical_qa()     [ContentItem RENDERED → NEEDS_REVIEW]
    ↓
ProductionLifecycleService.approve_content()      [ContentItem NEEDS_REVIEW → APPROVED]
    ↓
PublishingService.create_export_package()         [ExportPackage new → DRAFT]
    ↓
PublishingService.prepare_export()                [ExportPackage DRAFT → READY; ContentItem APPROVED → EXPORTED]
    ↓
PublishingService.create_publication()            [Publication new → PLANNED]
    ↓
PublishingService.publish_content()               [Publication PLANNED → PUBLISHED]
    ↓
AnalyticsService.create_metric_snapshot()         [MetricSnapshot new → DRAFT]
    ↓
Result: dict with all entity IDs and "status": "completed"
```

Post-loop manual workflows:
- `python scripts/inspect_package.py <dir>` — inspect export package.
- `python scripts/validate_package.py <dir>` — validate export package.
- `python scripts/find_metric_snapshots.py <project_id>` — find draft snapshots.
- `python scripts/import_manual_metrics.py <json>` — via `AnalyticsService.record_metrics()`.

Reference: `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md`, Section 7.

---

# 21. CLI Tools and Services

### smoke_loop.py → LoopOrchestrator

Uses `LoopOrchestrator.run_minimal_loop()` as the primary execution path.
Creates an Idea via `IdeaService.create_idea()` first, then orchestrates the
full loop. Also directly uses repositories for post-loop summary output.

### inspect_package.py → Filesystem / Manifest

Reads `manifest.json` from an export package directory. Does NOT use any
service directly — operates on the export artifact filesystem output.

### validate_package.py → Filesystem / Manifest

Validates `manifest.json` and checks all expected files exist on disk in the
export package directory. Does NOT use any service directly — operates on the
export artifact filesystem output.

### find_metric_snapshots.py → Filesystem / Repository-style

Directly reads `{project_dir}/data/metric_snapshots/*.json` files using
`MetricSnapshot.model_validate()`. Does NOT use `AnalyticsService` — operates
at the filesystem level with domain model parsing. Validates project via
`load_project()`.

### import_manual_metrics.py → AnalyticsService

Uses `build_analytics_service()` and calls `AnalyticsService.record_metrics()`.
Validates JSON payload structure before delegating to the service.

---

# 22. Future Agent-to-Service Boundary

In future phases, the Orchestrator Agent will issue execution requests that are
handled by the runtime layer, which in turn calls services. Services remain the
deterministic execution layer.

```
Agent
    ↓  issues runtime command
Runtime command
    ↓  validates request
Runtime validates project scope and state
    ↓
Service operation
    ↓  executes lifecycle task
Domain transition (entity.transition_to)
    ↓
Artifact / result returned to runtime
    ↓
Runtime reports back to agent
```

### What Future Agents May Request

Agents may request runtime to execute any service operation within the defined
contract. Agents do NOT call services directly — they go through runtime
entrypoints.

### What Agents Must Provide

- `project_id` — project scope for all operations.
- Explicit action — which lifecycle operation to perform.
- Context — relevant entity IDs, parameters.
- Autonomy mode — controls approval gate behaviour.
- Allowed scope — boundaries within which runtime may operate.

### What Agents Must NOT Do

- Directly mutate storage or write to entity JSON files.
- Skip services and create domain entities directly.
- Bypass domain state validation.
- Publish content without going through Distribution rules.
- Update Learning Memory without going through Analytics/Learning flow.
- Change entity statuses without calling the correct service.

---

# 23. Service Contract Stability Rules

1. **Do not break current method signatures without migration.** Existing
   method names, parameter orders and return types are stable.

2. **Add new services for new domains rather than overloading old services.**
   New content types, new production pipelines, new distribution channels —
   each deserves its own service rather than bloating existing ones.

3. **Keep `text_social_post` MVP path stable.** The current
   `Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot`
   chain must continue to work without modification.

4. **Preserve ExportPackage v1 compatibility.** The current six-file output
   (title.txt, body.txt, caption_{platform}.txt, checklist.txt, metadata.json,
   manifest.json) must remain valid and inspectable.

5. **Maintain manual publication flow.** `create_publication` →
   `publish_content` must continue to work for the manual MVP path even after
   autoposting is introduced.

6. **Maintain manual MetricSnapshot flow.** `create_metric_snapshot` →
   `record_metrics` must continue to work even after connector-based metrics
   collection is introduced.

7. **Keep repositories replaceable.** The filesystem storage layer must be
   replaceable with a database-backed layer without changing service contracts.
   Repository interfaces define the boundary.

---

# 24. Future Service Extensions (Conceptual)

The following services are architectural placeholders for future phases. None
of them are implemented in the current MVP. They are listed here to define the
service boundary map for LOOPRA evolution.

| Future Service | Purpose | Future Status |
|---|---|---|
| `ContentCycleService` | Manage full LOOPRA content cycles (MarketSignal → TrendPattern → Opportunity → Decision → Creation → Production → Distribution → Analytics → Learning → Optimization) | Future — Intelligence Layer |
| `AssetLibraryService` | Store, classify, validate and select assets for production | Future — Production Layer |
| `ProductionPipelineService` | Execute multi-stage production (Brief → Plan → Select → Generate → Assemble → QA → Export) for non-text content types | Future — Production Layer |
| `DistributionService` | Handle multi-channel distribution, connector-based publishing, scheduling, platform adaptation | Future — Distribution Layer |
| `AnalyticsEvaluationService` | Evaluate performance against goals, compute baselines, generate insights | Future — Analytics Layer |
| `LearningMemoryService` | Extract knowledge from results, persist performance patterns, retrieve relevant past experience | Future — Intelligence Layer |
| `RuntimeCommandService` | Accept, validate and dispatch runtime commands from agents, API and UI | Future — Runtime Layer |
| `ApprovalService` | Manage human approval gates, control points, autonomy mode enforcement | Future — Runtime Layer |
| `ConnectorService` | Abstract external platform API integrations (publishing, metrics, signals) | Future — Platform Layer |
| `SchedulerService` | Manage scheduled content cycles, publishing cadence, periodic jobs | Future — Runtime Layer |

These services must not be implemented without their approved specification
documents and validated Foundation MVP stability.

---

# 25. Current MVP Compatibility

The current Foundation MVP preserves:

```
Project
    ↓
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
```

No API. No UI. No DB. No external integrations. No autoposting. No background
workers. No service rewrites. No agent autonomy.

Existing tests and the smoke loop remain the source of truth for service
contract verification.

---

# 26. Service Contract Readiness Criteria

The Service Contracts specification is ready when:

- [x] All current services identified (`WorkspaceService`, `ProjectService`,
  `BrandProfileService`, `IdeaService`, `ScenarioService`,
  `ProductionLifecycleService`, `PublishingService`, `AnalyticsService`,
  `LoopOrchestrator`).
- [x] Each service responsibility defined.
- [x] Each public operation documented with method name from actual code.
- [x] Inputs/outputs documented per operation.
- [x] Preconditions/postconditions documented per operation.
- [x] Domain transitions mapped with actual enum values from `enums.py`.
- [x] Errors documented with actual exception classes from code.
- [x] Repositories documented with actual class names and storage paths.
- [x] Factory wiring documented with actual function names and dependencies.
- [x] CLI/service usage documented based on actual script code.
- [x] Future service boundaries marked as future/conceptual.
- [x] Current MVP service chain preserved and verified against actual code.

---

# 27. Related Documents

```text
AGENTS.md                                            — Development rules for AI agents
STATE.md                                             — Current project state
docs/00_foundation/DATA_MODEL.md                     — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md          — Project configuration specification
docs/02_architecture/SYSTEM_ARCHITECTURE.md          — System architecture layers
docs/02_architecture/PIPELINES_SPEC.md               — Foundation MVP pipeline
docs/03_intelligence/CONTENT_CYCLE_SPEC.md           — Content cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md            — Agent system architecture
docs/03_intelligence/LEARNING_MEMORY_SPEC.md         — Learning memory specification
docs/04_production/CONTENT_TYPES_SPEC.md             — Content type definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md       — Production pipeline specification
docs/04_production/ASSET_LIBRARY_SPEC.md             — Asset library specification
docs/04_production/DISTRIBUTION_SPEC.md              — Distribution specification
docs/04_production/ANALYTICS_SPEC.md                 — Analytics specification
docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md        — Runtime orchestration specification
```

---

# 28. Code References

```text
core/domain/models.py         — Domain entities (Workspace, Project, BrandProfile, Idea, Scenario,
                                 ContentItem, ExportPackage, Publication, MetricSnapshot, etc.)
core/domain/enums.py          — Domain status enums (IdeaStatus, ScenarioStatus, ContentItemStatus,
                                 ExportPackageStatus, PublicationStatus, MetricSnapshotStatus, etc.)
core/domain/transitions.py    — Status transition rules and validation
core/domain/__init__.py       — Domain public exports
core/services/loop.py         — LoopOrchestrator, build_loop_orchestrator
core/services/projects.py     — WorkspaceService, ProjectService, BrandProfileService,
                                 FileSystemProjectRepository
core/services/ideas.py        — IdeaService, ScenarioService, FileSystemIdeaRepository,
                                 FileSystemScenarioRepository
core/services/production.py   — ProductionLifecycleService, FileSystemContentItemRepository,
                                 build_production_lifecycle_service
core/services/publishing.py   — PublishingService, FileSystemExportPackageRepository,
                                 FileSystemPublicationRepository, build_publishing_service
core/services/analytics.py    — AnalyticsService, FileSystemMetricSnapshotRepository,
                                 build_analytics_service
core/services/_storage.py     — FileSystemProjectModelRepository (generic base)
core/services/__init__.py     — Service public exports
scripts/smoke_loop.py         — End-to-end smoke test
scripts/inspect_package.py    — Export package inspection tool
scripts/validate_package.py   — Export package validation tool
scripts/find_metric_snapshots.py  — Metric snapshot discovery tool
scripts/import_manual_metrics.py  — Manual metric import tool
tests/domain/                 — Domain model and transition tests
tests/services/               — Service lifecycle tests
```

---

# 29. Document Status

| Field | Value |
|---|---|
| Status | Active — LOOPRA Runtime Layer |
| Version | v1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Runtime Layer — Service Contracts |

---

# Final Statement

The Service Contracts Layer defines the stable, deterministic boundary between
the LOOPRA domain model and all execution entrypoints — CLI scripts, runtime
orchestration, and future agents.

Services own lifecycle operations. Services enforce domain transitions. Services
validate preconditions. Services persist through replaceable repositories.
Services raise explicit errors. Services never decide strategy.

Runtime orchestrates services in sequence. CLI tools call services for specific
actions. Future agents will request runtime commands that flow through the same
service contracts.

This specification is the contractual blueprint for every operation the LOOPRA
Foundation MVP performs — grounded in real code, verified by real tests, and
designed to remain stable through the platform's evolution.

---

## Current Stage 2 Slice 2 Hardened Service Contract

`ContentIntelligenceService` owns current Content Intelligence mutations:

- create/list/get/review `MarketSignal`;
- create/list/get/activate `TrendPattern`;
- create/list/get/approve/reject/defer/archive `ContentOpportunity`;
- convert approved `ContentOpportunity` to `Idea` through `IdeaService.create_idea()`.

List operations may filter by the entity status enum. Get/list/mutation operations remain project-scoped, and missing or cross-project identifiers are rejected by the existing project/repository boundaries. Duplicate opportunity conversion is rejected after the first conversion.

Scripts must call this service layer and must not write intelligence JSON directly. This remains a deterministic manual capability; it does not introduce autonomous decisions, external providers, scraping or connectors.

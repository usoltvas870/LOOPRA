# RUNTIME ORCHESTRATION SPEC

## Version

v1.0

## Status

Active — LOOPRA Runtime Layer

## Purpose

This document defines the Runtime Orchestration Layer — the execution
coordination layer of the LOOPRA Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA execute the already-defined architectural lifecycle
> in real runtime without breaking the Foundation MVP, without UI/API/DB
> and without premature autonomy?

RUNTIME_ORCHESTRATION_SPEC.md is the architectural blueprint for how the
system moves from specification to execution. It describes the components
that bind deterministic services, tools, scripts and future agents into a
coherent execution flow.

It does NOT describe:

- strategic content decisions (Intelligence Layer);
- content production algorithms (Production Layer);
- publication mechanics (Distribution Layer);
- metric interpretation (Analytics Layer);
- learning extraction (Learning Memory);
- UI, API, DB, authentication, billing or SaaS infrastructure.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document defines how the LOOPRA architectural layers are executed
in runtime. It establishes the execution coordination model — the set of
components, rules and flows that govern how work moves from a request
through domain entities, services, tools and scripts to a completed result.

## 1.2. In Scope

- Runtime boundaries and component roles.
- Current Foundation MVP execution flow.
- Runtime components and their responsibilities.
- Service orchestration model.
- Tool invocation model.
- State transitions during execution.
- Execution context structure.
- Artifact generation during runtime.
- Error handling during execution.
- Human approval gates in runtime.
- Future worker/agent/API entrypoint extension paths.

## 1.3. Out of Scope

- UI screens, forms, dashboards.
- API endpoint implementation.
- Database schemas and migrations.
- External platform integrations.
- Autoposting or automated distribution.
- Strategic decision-making logic (belongs to Intelligence Layer).
- Autonomous 24/7 background agent.
- Billing, authentication, users, roles, teams.
- New code implementation (this is a specification, not a task list).

---

# 2. Role of Runtime Orchestration in LOOPRA

## 2.1. Position in the Architecture

```text
Architecture Specs (SYSTEM_ARCHITECTURE.md, PIPELINES_SPEC.md, etc.)
    ↓
Domain Model (core/domain/models.py — entities, statuses, transitions)
    ↓
Services (core/services/ — lifecycle operations)
    ↓
Runtime Orchestration (LoopOrchestrator, scripts, entrypoints)
    ↓
Tools / Scripts (smoke_loop.py, inspect_package.py, validate_package.py, etc.)
    ↓
Artifacts / State (export packages, metric snapshots, JSON records)
    ↓
Future: Agent / API / UI entrypoints call runtime
```

## 2.2. Core Principle

Runtime Orchestration executes. It does not decide strategy.

```text
Intelligence Layer  →  "What content to create, why, for whom"
Runtime Layer       →  "Execute the defined workflow using the correct services"
Tools               →  "Perform the specific deterministic action"
```

Runtime Orchestration is the execution substrate of LOOPRA. It is not an
additional strategic module. It does not make marketing decisions. It
orchestrates the services and tools that carry out decisions already made
(or provided manually by the human operator in the current MVP).

## 2.3. What Runtime Orchestration Does

- Receives an execution request (from CLI, smoke loop, future agent/API).
- Loads project context and validates preconditions.
- Invokes services in the correct order.
- Enforces domain state transitions.
- Tracks execution progress and status.
- Produces inspectable artifacts.
- Handles errors with structured codes and recommended actions.
- Respects human approval gates.
- Provides entrypoints that preserve domain and service boundaries.

## 2.4. What Runtime Orchestration Does NOT Do

- Select topics or content directions (Intelligence Layer).
- Generate or assemble content (Production Pipeline services).
- Publish content to external platforms (Distribution Layer).
- Analyze or interpret metrics (Analytics Layer).
- Extract knowledge or update learning patterns (Learning Memory).
- Bypass domain validation or transition rules.
- Modify entity states without going through the correct service.
- Execute tools that belong to future phases (media rendering, autoposting).

---

# 3. Relationship to Foundation MVP

## 3.1. The Foundation MVP Chain

The Foundation MVP defines the validated entity chain:

```text
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

Reference: `docs/00_foundation/DATA_MODEL.md`, Section 3; `docs/02_architecture/PIPELINES_SPEC.md`, Section 2

## 3.2. How Runtime Executes the Chain

Runtime Orchestration does not change the chain. It provides the
execution mechanism that moves entities through their lifecycle.

```text
Runtime execution (LoopOrchestrator.run_minimal_loop):

    1. Load project config via ProjectService.
    2. Ensure Idea is approved via IdeaService.
    3. Create Scenario from Idea via ScenarioService.
    4. Approve Scenario.
    5. Create ContentItem from Scenario via ProductionLifecycleService.
    6. Run technical QA on ContentItem.
    7. Approve ContentItem.
    8. Create ExportPackage via PublishingService.
    9. Prepare Export (write files to disk).
   10. Create Publication record via PublishingService.
   11. Record publication (with published URL).
   12. Create draft MetricSnapshot via AnalyticsService.
```

Each step calls the appropriate service. Each service enforces domain
state transitions. Runtime does not skip validation or bypass services.

## 3.3. Current MVP Boundaries Preserved

The Runtime Orchestration Spec does NOT:

- Modify the `Idea`, `Scenario`, `ContentItem`, `ExportPackage`,
  `Publication` or `MetricSnapshot` entities.
- Modify domain status enums or transition rules.
- Add new required fields to any domain model.
- Change the filesystem-based storage approach.
- Require a database, API server or UI.
- Enable autoposting or external API calls.
- Activate autonomous agent decision-making.

---

# 4. Relationship to System Architecture

## 4.1. Runtime and Architectural Layers

Runtime Orchestration connects to every architectural layer defined in
SYSTEM_ARCHITECTURE.md, but only as the execution mechanism — not as a
replacement for any layer's responsibilities.

```text
Workspace / Project         →  Runtime loads project config at execution start.
Brand System                →  Runtime provides BrandSystem context to services.
Content Cycle               →  Runtime executes cycle stages via services.
Orchestrator Agent          →  Future: Agent calls runtime; runtime executes.
Intelligence Modules        →  Future: Runtime invokes modules per cycle stage.
Production Layer            →  Runtime calls ProductionLifecycleService.
Publishing / Distribution   →  Runtime calls PublishingService.
Analytics                   →  Runtime calls AnalyticsService.
Learning Memory             →  Future: Runtime triggers handoff after cycle.
```

## 4.2. Runtime Is Execution Substrate

Runtime is the layer that binds everything together in time and order. It
does not own the business logic of any architectural layer. It owns the
coordination logic — which services to call, in what sequence, under
what conditions, with what error handling.

---

# 5. Runtime Principles

1. **Deterministic by default.** Given the same inputs and project state,
   runtime produces the same outputs. No randomness in execution flow.

2. **Project-scoped execution.** Every runtime execution is bound to a
   specific `project_id`. No cross-project operations.

3. **Explicit state transitions.** Every entity state change goes through
   the domain transition rules defined in `core/domain/transitions.py`.
   Runtime does not bypass transitions.

4. **Inspectable artifacts.** Every execution produces artifacts (files,
   records, snapshots) that can be inspected after completion.

5. **No hidden background autonomy in MVP.** Runtime executes only when
   explicitly triggered. No continuous background loops, no scheduled
   jobs, no autonomous agent cycles.

6. **Human approval gates respected.** In the current MVP (copilot mode),
   the human provides inputs manually. Runtime pauses where approval is
   required.

7. **Agents call runtime; agents do not bypass runtime.** Future
   Orchestrator Agent will issue execution requests through runtime
   entrypoints — not directly mutate domain entities or skip services.

8. **Tools execute narrow tasks.** Tools (scripts) perform specific
   deterministic actions (inspect, validate, import, generate files).
   They do not make strategic decisions.

9. **Services own lifecycle changes.** Only services create or modify
   domain entities. Runtime orchestrates services. Tools are called
   by scripts or future agents — not by runtime core directly.

10. **Future extensibility without breaking MVP.** The runtime model is
    designed so that future API endpoints, UI triggers, queue workers and
    agent-controlled cycles can call the same runtime entrypoints without
    rewriting the service layer.

---

# 6. Current Runtime Components

## 6.1. Overview

The current LOOPRA Foundation MVP contains the following runtime
components. Names reflect the actual codebase.

### 6.1.1. Domain Layer (`core/domain/`)

| Component | File | Role |
|---|---|---|
| Domain models | `models.py` | Defines entities: `Workspace`, `Project`, `BrandProfile`, `Idea`, `Scenario`, `ContentItem`, `ExportPackage`, `Publication`, `MetricSnapshot`, `RenderJob`, `OutputFile`, etc. |
| Domain enums | `enums.py` | Defines statuses: `IdeaStatus`, `ScenarioStatus`, `ContentItemStatus`, `ExportPackageStatus`, `PublicationStatus`, `MetricSnapshotStatus`, etc. |
| Transition rules | `transitions.py` | Defines allowed status transitions for each entity. Enforced via `validate_status_transition()`. |

**Responsibility:** Defines what entities exist, what states they can be in,
and what transitions are legal. Domain layer has no side effects — no
filesystem writes, no external calls, no service logic.

### 6.1.2. Service Layer (`core/services/`)

| Component | File | Role |
|---|---|---|
| `ProjectService` | `projects.py` | Loads and validates project configuration. |
| `BrandProfileService` | `projects.py` | Derives `BrandProfile` from project config. |
| `IdeaService` | `ideas.py` | Creates, approves, rejects, archives ideas. |
| `ScenarioService` | `ideas.py` | Creates scenarios from ideas, approves, rejects. Runs QA checks. |
| `ProductionLifecycleService` | `production.py` | Creates content items from scenarios, runs technical QA, approves content. |
| `PublishingService` | `publishing.py` | Creates export packages, prepares exports (writes files), creates publications, records publication outcomes. |
| `AnalyticsService` | `analytics.py` | Creates metric snapshots, records manual metrics, normalizes metric keys. |

**Responsibility:** Performs lifecycle operations on domain entities.
Validates preconditions, enforces transitions, writes to storage via
repositories.

### 6.1.3. Repository / Storage Layer

| Component | File | Role |
|---|---|---|
| `FileSystemProjectRepository` | `projects.py` | Lists projects, loads project config from YAML. |
| `FileSystemIdeaRepository` | `ideas.py` | Saves/loads `Idea` entities as JSON files. |
| `FileSystemScenarioRepository` | `ideas.py` | Saves/loads `Scenario` entities as JSON files. |
| `FileSystemContentItemRepository` | `production.py` | Saves/loads `ContentItem` entities as JSON files. |
| `FileSystemExportPackageRepository` | `publishing.py` | Saves/loads `ExportPackage` entities as JSON files. |
| `FileSystemPublicationRepository` | `publishing.py` | Saves/loads `Publication` entities as JSON files. |
| `FileSystemMetricSnapshotRepository` | `analytics.py` | Saves/loads `MetricSnapshot` entities as JSON files. |
| `FileSystemProjectModelRepository` (base) | `_storage.py` | Generic JSON file persistence for domain models. |

**Responsibility:** Persists domain entities to the filesystem as JSON
files, scoped by project. No business logic. No validation beyond
entity ID pattern checks.

### 6.1.4. Runtime Orchestrator

| Component | File | Role |
|---|---|---|
| `LoopOrchestrator` | `loop.py` | Orchestrates the full Foundation MVP lifecycle from Idea to MetricSnapshot. |
| `build_loop_orchestrator()` | `loop.py` | Factory function that wires all services together. |

**Responsibility:** Coordinates services in the correct sequence for a
complete content lifecycle loop. Does not perform service logic itself.

### 6.1.5. CLI Scripts / Tools (`scripts/`)

| Script | Role |
|---|---|
| `smoke_loop.py` | End-to-end smoke test of the full Foundation MVP loop. |
| `inspect_package.py` | Reads and displays the contents of an ExportPackage directory. |
| `validate_package.py` | Validates that an ExportPackage contains all required files and correct structure. |
| `find_metric_snapshots.py` | Lists MetricSnapshot records for a project. |
| `import_manual_metrics.py` | Imports manually collected metrics into a draft MetricSnapshot. |

**Responsibility:** Provide CLI entrypoints for manual workflows. These
are tools — deterministic executors. They do not make strategic decisions.

### 6.1.6. Tests (`tests/`)

| Component | Role |
|---|---|
| `tests/domain/` | Tests for domain models, enums, transitions. |
| `tests/services/` | Tests for service lifecycle operations. |

**Responsibility:** Validate that domain rules, service logic and state
transitions behave correctly. Tests are the verification mechanism for
runtime correctness.

---

# 7. Current MVP Runtime Flow

## 7.1. Full Flow (as executed by LoopOrchestrator)

```text
ENTRYPOINT: smoke_loop.py main() or LoopOrchestrator.run_minimal_loop()
    │
    ├── STEP 1: Load Project Config
    │     Input:   project_id
    │     Service: ProjectService.get_project(project_id)
    │     Output:  Validated Project entity
    │     Failure: ProjectConfigValidationError — project not found or config invalid
    │
    ├── STEP 2: Create or Approve Idea
    │     Input:   project_id, idea title/description/topic
    │     Service: IdeaService.create_idea() or IdeaService.get_idea()
    │              IdeaService.approve_idea() if status is RAW
    │     Output:  Idea entity (status: APPROVED or SCRIPTED)
    │     State:   Idea RAW → APPROVED
    │     Failure: IdeaBankValidationError — invalid fields
    │
    ├── STEP 3: Create Scenario from Idea
    │     Input:   project_id, idea_id
    │     Service: ScenarioService.create_from_idea()
    │     Output:  Scenario entity with text blocks, caption drafts, QA warnings
    │     State:   Scenario DRAFT → NEEDS_REVIEW
    │     Failure: ScenarioStudioValidationError — Idea not approved
    │
    ├── STEP 4: Approve Scenario
    │     Input:   project_id, scenario_id
    │     Service: ScenarioService.approve_scenario()
    │     Output:  Scenario entity (status: APPROVED)
    │     State:   Scenario NEEDS_REVIEW → APPROVED
    │     Artifact: Scenario JSON stored in project data dir
    │     Failure: InvalidStatusTransitionError — wrong current status
    │
    ├── STEP 5: Create ContentItem
    │     Input:   project_id, scenario_id
    │     Service: ProductionLifecycleService.create_content_item()
    │     Output:  ContentItem entity (status: RENDERED)
    │     State:   ContentItem DRAFT → IN_PRODUCTION → RENDERED
    │     Artifact: ContentItem JSON stored
    │     Failure: ProductionLifecycleValidationError — Scenario not approved
    │
    ├── STEP 6: Run Technical QA on ContentItem
    │     Input:   project_id, content_item_id
    │     Service: ProductionLifecycleService.run_technical_qa()
    │     Output:  ContentItem with QA results (status: NEEDS_REVIEW or QA_FAILED)
    │     State:   ContentItem RENDERED → NEEDS_REVIEW
    │     Artifact: QA metadata stored in render_output_metadata
    │     Failure: QA errors detected → status QA_FAILED
    │
    ├── STEP 7: Approve ContentItem
    │     Input:   project_id, content_item_id
    │     Service: ProductionLifecycleService.approve_content()
    │     Output:  ContentItem entity (status: APPROVED)
    │     State:   ContentItem NEEDS_REVIEW → APPROVED
    │     Failure: InvalidStatusTransitionError
    │
    ├── STEP 8: Create ExportPackage
    │     Input:   project_id, content_item_id, target_platform
    │     Service: PublishingService.create_export_package()
    │     Output:  ExportPackage entity (status: DRAFT)
    │     Failure: PublishingValidationError — ContentItem not approved
    │
    ├── STEP 9: Prepare Export (write files to disk)
    │     Input:   project_id, export_package_id
    │     Service: PublishingService.prepare_export()
    │     Output:  ExportPackage entity (status: READY)
    │              Files written: title.txt, body.txt, caption_{platform}.txt,
    │              manual_publication_checklist.txt, metadata.json, manifest.json
    │     State:   ExportPackage DRAFT → READY
    │              ContentItem APPROVED → EXPORTED (side effect)
    │     Artifact: Export directory with all output files
    │     Failure: PublishingValidationError — wrong status or missing files
    │
    ├── STEP 10: Create Publication Record
    │     Input:   project_id, content_item_id, export_package_id
    │     Service: PublishingService.create_publication()
    │     Output:  Publication entity (status: PLANNED)
    │     Failure: PublishingValidationError — ExportPackage not READY
    │
    ├── STEP 11: Record Publication (simulate manual publish)
    │     Input:   project_id, publication_id, published_url
    │     Service: PublishingService.publish_content()
    │     Output:  Publication entity (status: PUBLISHED, with URL and timestamp)
    │     State:   Publication PLANNED → PUBLISHED
    │     Artifact: Publication JSON with published_at, published_url
    │     Failure: PublishingValidationError — empty URL
    │
    ├── STEP 12: Create MetricSnapshot (draft)
    │     Input:   project_id, publication_id, content_item_id
    │     Service: AnalyticsService.create_metric_snapshot()
    │     Output:  MetricSnapshot entity (status: DRAFT)
    │     Failure: AnalyticsValidationError — Publication not published
    │
    └── RESULT: dict of all entity IDs and "status": "completed"
```

## 7.2. Post-Cycle Manual Workflows

After the automated loop completes, these manual runtime actions are
available:

```text
MANUAL ACTION A: Inspect Export Package
    Tool:  python scripts/inspect_package.py <export_package_directory>
    Input: ExportPackage directory path
    Output: Human-readable display of package contents

MANUAL ACTION B: Validate Export Package
    Tool:  python scripts/validate_package.py <export_package_directory>
    Input: ExportPackage directory path
    Output: Validation report (pass/fail with details)

MANUAL ACTION C: Import Manual Metrics
    Tool:  python scripts/import_manual_metrics.py <manual_metrics_json>
    Input: JSON file with metric values (views, likes, comments, shares,
           saves, clicks, published_url)
    Service: AnalyticsService.record_metrics()
    Output: MetricSnapshot entity (status: RECORDED)
    State:  MetricSnapshot DRAFT → RECORDED

MANUAL ACTION D: Find Metric Snapshots
    Tool:  python scripts/find_metric_snapshots.py <project_id>
    Input: project_id
    Output: List of MetricSnapshot records with statuses
```

## 7.3. Step Dependencies

Each step depends on the successful completion of the previous step:

```text
Load Project   →  prerequisite for all subsequent steps
Create Idea    →  prerequisite for Scenario
Scenario       →  prerequisite for ContentItem
ContentItem    →  prerequisite for ExportPackage
ExportPackage  →  prerequisite for Publication
Publication    →  prerequisite for MetricSnapshot
```

Runtime enforces these dependencies. A failed step blocks all subsequent
steps unless the error is resolved and execution is retried.

---

# 8. Execution Context

## 8.1. Definition

The **RuntimeExecutionContext** is a conceptual entity that captures the
state of an active runtime execution. It is not a database record — it is
a logical container for execution metadata.

## 8.2. Conceptual Fields

```text
RuntimeExecutionContext:
    execution_id              — unique identifier for this execution run
    project_id                — the project scope
    workspace_id              — derived from project config
    cycle_id                  — content cycle reference (future)
    content_item_id           — the primary content item (if applicable)
    current_stage             — which runtime stage is currently active
    requested_by              — "cli", "smoke_loop", "agent" (future), "api" (future)
    autonomy_mode             — "copilot" (current MVP), "assisted" (future), "autopilot" (future)
    started_at                — execution start timestamp (UTC)
    completed_at              — execution completion timestamp (UTC)
    status                    — current runtime status (see Section 12)
    stages                    — ordered list of stage definitions
    current_stage_index       — index into the stages list
    inputs                    — input parameters provided at execution start
    outputs                   — entity IDs and artifact paths produced
    artifacts                 — list of generated artifact references
    errors                    — list of RuntimeError records
    approval_state            — state of any pending human approval
```

## 8.3. Current MVP Simplification

In the current MVP, the execution context is implicit — not stored as a
persistent entity. The `LoopOrchestrator.run_minimal_loop()` method
returns a plain `dict[str, str]` with entity IDs. The smoke loop prints
a summary to stdout.

A formal `RuntimeExecutionContext` entity is conceptual for future phases
when execution state must be persisted across restarts, inspected by
operators or queried by agents.

## 8.4. Relationship to LoopOrchestrator

The current `LoopOrchestrator` acts as an in-memory execution context:

```text
LoopOrchestrator.run_minimal_loop(project_id, idea_id, target_platform)
    │
    │  implicitly tracks: current stage position, entity references,
    │  success/failure state
    │
    └── returns dict with all entity IDs and status="completed"
```

The `get_loop_status()` method provides a project-level summary of entity
status counts — a form of runtime observability.

---

# 9. Runtime Entry Points

## 9.1. Definition

Entry points are the interfaces through which runtime execution is
triggered. They define who can start execution and what they can request.

## 9.2. Current MVP Entry Points

### 9.2.1. CLI Scripts

| Entry Point | Trigger | What It Runs |
|---|---|---|
| `python scripts/smoke_loop.py` | Manual CLI invocation | Full Foundation MVP loop |
| `python scripts/inspect_package.py <dir>` | Manual CLI invocation | Reads and displays export package |
| `python scripts/validate_package.py <dir>` | Manual CLI invocation | Validates export package |
| `python scripts/find_metric_snapshots.py <project_id>` | Manual CLI invocation | Lists metric snapshots |
| `python scripts/import_manual_metrics.py <json>` | Manual CLI invocation | Imports manual metrics |

### 9.2.2. Programmatic API (Python)

| Entry Point | Caller | What It Runs |
|---|---|---|
| `LoopOrchestrator.run_minimal_loop(project_id, idea_id)` | Tests, future agents | Full Foundation MVP loop |
| `LoopOrchestrator.get_loop_status(project_id)` | Tests, future agents | Entity status summary |

### 9.2.3. Test Suite

| Entry Point | Trigger | What It Runs |
|---|---|---|
| `pytest tests/domain/` | Manual/CI | Domain model and transition tests |
| `pytest tests/services/` | Manual/CI | Service lifecycle tests |

## 9.3. Future Entry Points (Conceptual)

| Entry Point | Trigger | Scope |
|---|---|---|
| Orchestrator Agent call | Agent decision to execute content cycle | Issues `run_content_cycle(project_id, cycle_id, autonomy_mode)` |
| API endpoint | External HTTP request | Triggers specific runtime commands |
| UI action | User button click | Initiates workflow via API |
| Scheduled job | Cron/timer | Periodic cycle execution |
| Worker queue message | Queue consumer | Async execution of individual stages |

## 9.4. Entry Point Rules

1. Every entry point must validate that the project exists and is active
   before executing.
2. No entry point may bypass domain state transitions.
3. No entry point may directly mutate storage or entity state — all
   mutations go through services.
4. Future agent entry points must provide: `project_id`, explicit action,
   context, autonomy mode.
5. Future API entry points must enforce project scoping — no cross-project
   requests.

---

# 10. Service Orchestration Model

## 10.1. How Runtime Calls Services

Runtime orchestration follows a strict service invocation pattern:

```text
Runtime command received (e.g., run_minimal_loop)
    ↓
Runtime validates project exists (ProjectService.get_project)
    ↓
Runtime calls service 1 with validated inputs
    ↓
Service validates preconditions (domain status checks)
    ↓
Service performs lifecycle operation
    ↓
Service enforces state transition (entity.transition_to)
    ↓
Service persists entity via repository
    ↓
Service returns updated entity
    ↓
Runtime stores entity reference for next step
    ↓
Runtime calls service 2 with entity references from step 1
    ↓
... (repeat for all steps)
    ↓
Runtime returns result with all entity IDs
```

## 10.2. Service Dependency Graph

```text
ProjectService         ←  standalone (loads project config)
    ↓
IdeaService            ←  depends on ProjectService (validates project)
    ↓
ScenarioService        ←  depends on ProjectService, BrandProfileService,
                           IdeaService, IdeaRepository
    ↓
ProductionLifecycleService  ←  depends on ProjectService, ScenarioRepository
    ↓
PublishingService      ←  depends on ProjectService, ContentRepository,
                           ScenarioRepository
    ↓
AnalyticsService       ←  depends on ProjectService, PublicationRepository,
                           ContentRepository
```

## 10.3. Factory Functions

Services are constructed via factory functions that wire dependencies:

```text
build_loop_orchestrator(projects_root) → LoopOrchestrator
build_production_lifecycle_service(projects_root) → ProductionLifecycleService
build_publishing_service(projects_root) → PublishingService
build_analytics_service(projects_root) → AnalyticsService
```

Each factory creates the required repositories and services, ensuring
correct dependency injection.

## 10.4. What Runtime Must NOT Do with Services

- Runtime must not call repository methods directly — only services own
  repository access.
- Runtime must not create domain entities directly — only services create
  entities.
- Runtime must not transition entity statuses — only services call
  `entity.transition_to()`.
- Runtime may read entity state for orchestration decisions (e.g., check
  if Idea is already approved before calling approve).

---

# 11. Tool Invocation Model

## 11.1. Definition

Tools are deterministic executors that perform specific actions. They
receive explicit inputs and return structured outputs. Tools do not
make strategic decisions.

## 11.2. Current Tools

| Tool | Input | Output | Deterministic |
|---|---|---|---|
| `smoke_loop.py` | project_id (env or default) | Printed summary to stdout, artifacts on disk | Yes |
| `inspect_package.py` | ExportPackage directory path | Human-readable display of package contents | Yes |
| `validate_package.py` | ExportPackage directory path | Validation report (pass/fail with errors) | Yes |
| `find_metric_snapshots.py` | project_id | List of MetricSnapshot records | Yes |
| `import_manual_metrics.py` | JSON file with metric values | Updated MetricSnapshot (DRAFT→RECORDED) | Yes |

## 11.3. Tool Invocation Rules

1. Tools receive explicit, validated inputs. No guessing. No defaults
   that change behaviour silently.
2. Tools return structured outputs: exit codes, printed reports,
   modified entities (via services).
3. Tools do NOT decide strategy:
   - `validate_package.py` says "pass" or "fail" — it does not decide
     whether a failing package should still be published.
   - `import_manual_metrics.py` imports values — it does not evaluate
     whether the metrics are good or bad.
4. Runtime (or the human operator) decides what to do with tool outputs.
5. Tool execution outcomes are observable: terminal output, exit codes,
   file artifacts.
6. Future tools (render worker, asset validator, platform connector)
   follow the same contract.

## 11.4. Future Tools (Conceptual)

| Tool | Role | Phase |
|---|---|---|
| Render worker | Renders media (video, images) from production specs | Future |
| Package validator | Extended validation with brand compliance rules | Future |
| Asset validator | Checks asset licensing, quality, brand fit | Future |
| Platform connector | Posts content to external platforms via API | Future |
| Analytics connector | Pulls metrics from platform APIs | Future |

---

# 12. Runtime State Model

## 12.1. Runtime Statuses

Runtime execution progresses through defined statuses:

```text
pending
    ↓
running
    ↓
    ├── waiting_for_input       (human input required to continue)
    │       ↓
    │   running                 (resumes after input provided)
    │
    ├── waiting_for_approval    (human approval gate)
    │       ↓
    │   running                 (resumes after approval)
    │
    ├── paused                  (explicit pause by operator or agent)
    │       ↓
    │   running                 (resumes after unpause)
    │
    ├── completed               (all stages succeeded)
    │
    ├── completed_with_warnings  (all stages completed, non-blocking issues)
    │
    ├── failed                  (a stage failed; execution stopped)
    │       ↓
    │   retry                   (operator or agent retries from failed stage)
    │
    └── cancelled               (explicit cancellation by operator or agent)
```

## 12.2. Current MVP Status Subset

In the current MVP, only these statuses are meaningful:

```text
pending    →  execution not yet started
running    →  LoopOrchestrator.run_minimal_loop() in progress
completed  →  all steps returned successfully
failed     →  an exception was raised and not caught
```

The `waiting_for_input`, `waiting_for_approval`, `paused` and
`completed_with_warnings` statuses are conceptual for future phases
where execution may span multiple sessions or require human interaction
mid-flow.

## 12.3. Transition Rules

```text
pending → running:
    Execution triggered by an entrypoint.

running → completed:
    All stages executed without errors.

running → failed:
    A stage raised an unhandled exception.

running → cancelled:
    Explicit cancellation (future — current MVP runs synchronously).

failed → running:
    Retry from the failed stage (manual rerun in current MVP).

running → waiting_for_input:
    Human input required (future — current MVP provides all inputs upfront).

running → waiting_for_approval:
    Approval gate reached (future — current MVP has no mid-flow approval gates).

completed → (terminal):
    Execution finished. No further transitions.
```

---

# 13. Lifecycle State Mapping

## 13.1. Runtime State vs Domain Entity State

Runtime states describe execution progress. Domain entity states describe
entity lifecycle. They are distinct and must not be conflated.

```text
RUNTIME STATE                        DOMAIN ENTITY STATES
─────────────                        ────────────────────
running (step 1)             →       Project loaded (validated)
running (step 2–3)           →       Idea RAW → APPROVED
running (step 4–5)           →       Scenario DRAFT → NEEDS_REVIEW → APPROVED
running (step 6–8)           →       ContentItem DRAFT → IN_PRODUCTION →
                                       RENDERED → NEEDS_REVIEW → APPROVED
running (step 9–10)          →       ExportPackage DRAFT → READY
                                       ContentItem APPROVED → EXPORTED
running (step 11–12)         →       Publication PLANNED → PUBLISHED
running (step 13)            →       MetricSnapshot DRAFT (created)
completed                    →       All entities in valid terminal states
```

## 13.2. Mapping Rules

1. Runtime state `running` maps to various domain states depending on
   which step is executing.
2. Runtime state `completed` means all domain entities reached their
   intended terminal states.
3. Runtime state `failed` means one or more domain entities are in an
   error or intermediate state.
4. A domain entity being in an error state (e.g., `QA_FAILED`) does not
   automatically mean runtime has failed — it means the runtime should
   stop and report the entity state.
5. Entity state transitions are enforced by the domain layer, not by
   runtime. Runtime calls services; services call `transition_to()`.

---

# 14. Artifact Model

## 14.1. Definition

Runtime artifacts are files, records and data produced during execution.
They are the tangible outputs that make execution inspectable.

## 14.2. Current Artifacts

| Artifact | Produced By | Location | Content |
|---|---|---|---|
| Project config copy | `smoke_loop.py._ensure_runtime_project()` | `storage/smoke_projects/{project_id}/project.yaml` | Copy of source project config |
| Idea record (JSON) | `IdeaService` via `FileSystemIdeaRepository` | `{project_dir}/data/ideas/{idea_id}.json` | Serialized Idea entity |
| Scenario record (JSON) | `ScenarioService` via `FileSystemScenarioRepository` | `{project_dir}/data/scenarios/{scenario_id}.json` | Serialized Scenario entity |
| ContentItem record (JSON) | `ProductionLifecycleService` via `FileSystemContentItemRepository` | `{project_dir}/data/content_items/{content_item_id}.json` | Serialized ContentItem entity |
| ExportPackage record (JSON) | `PublishingService` via `FileSystemExportPackageRepository` | `{project_dir}/data/export_packages/{export_package_id}.json` | Serialized ExportPackage entity |
| `title.txt` | `PublishingService.prepare_export()` | `{project_dir}/exports/{export_package_id}/title.txt` | Content title |
| `body.txt` | `PublishingService.prepare_export()` | `{project_dir}/exports/{export_package_id}/body.txt` | Content body |
| `caption_{platform}.txt` | `PublishingService.prepare_export()` | `{project_dir}/exports/{export_package_id}/caption_{platform}.txt` | Platform-specific caption |
| `manual_publication_checklist.txt` | `PublishingService.prepare_export()` | `{project_dir}/exports/{export_package_id}/manual_publication_checklist.txt` | Step-by-step manual publishing instructions |
| `metadata.json` | `PublishingService.prepare_export()` | `{project_dir}/exports/{export_package_id}/metadata.json` | Export metadata (project, content, timestamps) |
| `manifest.json` | `PublishingService.prepare_export()` | `{project_dir}/exports/{export_package_id}/manifest.json` | File listing with roles and status |
| Publication record (JSON) | `PublishingService` via `FileSystemPublicationRepository` | `{project_dir}/data/publications/{publication_id}.json` | Serialized Publication entity |
| MetricSnapshot record (JSON) | `AnalyticsService` via `FileSystemMetricSnapshotRepository` | `{project_dir}/data/metric_snapshots/{metric_snapshot_id}.json` | Serialized MetricSnapshot entity, optionally with metrics |

## 14.3. Artifact Rules

1. All artifacts are project-scoped — stored under the project's data or
   exports directory.
2. Generated runtime artifacts (under `storage/smoke_projects/`) are
   local-only and must not be committed to version control.
3. Source docs and configs (under `projects/`) are separate from runtime
   outputs.
4. Artifacts must be inspectable — JSON files are human-readable,
   export files are plain text.
5. Artifact paths are deterministic given project_id and entity_id.
6. Future artifacts (rendered video files, image files, subtitle tracks)
   follow the same project-scoped storage rules.

---

# 15. Error Handling

## 15.1. Structured Error Model

Every runtime error is described by:

```text
RuntimeError:
    error_code         — machine-readable error identifier
    stage              — which runtime stage was executing
    entity_id          — affected entity ID (if applicable)
    project_id         — project scope
    severity           — "blocking", "warning", "info"
    message            — human-readable error description
    recommended_action — what the operator should do next
    retry_allowed      — whether retrying from this stage is safe
    timestamp          — when the error occurred (UTC)
```

## 15.2. Error Catalog — Current MVP

| Error Code | Stage | Severity | Description | Recommended Action | Retry |
|---|---|---|---|---|---|
| `project_config_missing` | Load Project | blocking | `project.yaml` not found for the given project_id. | Verify project_id. Check that the project config file exists. | No (config required) |
| `invalid_project_config` | Load Project | blocking | Required fields missing in project config. | Check project.yaml against PROJECT_SETTINGS_SPEC.md. | No (fix config first) |
| `idea_creation_failed` | Create Idea | blocking | Idea validation failed (invalid funnel_stage, source_type, etc.). | Check input fields against allowed values. | Yes |
| `idea_not_approved` | Create Scenario | blocking | Idea must be in APPROVED or SCRIPTED status. | Approve the idea first. | Yes (approve first) |
| `scenario_creation_failed` | Create Scenario | blocking | Scenario creation prerequisites not met. | Ensure Idea is approved. Check content format support. | Yes |
| `unsupported_content_format` | Create Scenario | blocking | Only `text_social_post` is supported in current MVP. | Use `text_social_post` format. | Yes (change format) |
| `scenario_not_approved` | Create Content | blocking | Scenario must be in APPROVED status. | Approve the scenario. | Yes (approve first) |
| `content_generation_failed` | Create Content | blocking | ContentItem creation failed (scenario status, body empty, etc.). | Check scenario status and content. | Yes |
| `technical_qa_failed` | QA | warning/blocking | Technical QA found issues (empty title, body, missing brand_profile_id). | Review QA errors. Fix scenario content. | Yes (fix and retry) |
| `content_not_approved` | Export | blocking | ContentItem must be APPROVED before export. | Approve content item. | Yes (approve first) |
| `export_package_failed` | Export | blocking | ExportPackage creation or file writing failed. | Check filesystem permissions. Verify ContentItem status. | Yes |
| `package_validation_failed` | Validate | warning/blocking | ExportPackage is missing required files or has incorrect structure. | Compare against expected output. Rerun export. | Yes |
| `publication_record_failed` | Publish | blocking | Publication creation failed (ExportPackage not ready, ContentItem not exported). | Check entity statuses. | Yes |
| `publication_url_empty` | Publish | blocking | `published_url` must not be empty when publishing. | Provide the actual published URL. | Yes |
| `metric_snapshot_failed` | Analytics | blocking | MetricSnapshot creation failed (Publication not published). | Ensure Publication is in PUBLISHED status. | Yes |
| `metric_import_failed` | Analytics | blocking | Manual metric import failed (unknown keys, invalid values). | Check metrics JSON against supported keys and types. | Yes |
| `metric_snapshot_not_draft` | Analytics | blocking | Metrics can only be recorded into a DRAFT snapshot. | Find or create a DRAFT snapshot. | Yes (use draft) |
| `tool_execution_failed` | Tool | blocking | A script/tool exited with an error. | Read error output. Fix inputs. | Yes |
| `project_not_found` | Any | blocking | `project_id` does not reference a valid project. | Check project_id. Ensure project directory exists. | No |

## 15.3. Error Handling in Current MVP

In the current MVP, errors propagate as Python exceptions:

- `ProjectConfigValidationError` — invalid project config.
- `IdeaBankValidationError` — invalid idea inputs.
- `ScenarioStudioValidationError` — invalid scenario state or inputs.
- `ProductionLifecycleValidationError` — invalid production state.
- `PublishingValidationError` — invalid publishing state.
- `AnalyticsValidationError` — invalid analytics state.
- `InvalidStatusTransitionError` — illegal entity state transition.
- `FileNotFoundError` — entity or file not found.

Each exception includes a human-readable message. The operator reads the
error, fixes the issue and reruns the script.

In future phases, errors will be captured in a structured `RuntimeError`
record within the `RuntimeExecutionContext`.

---

# 16. Retry and Resume Model

## 16.1. Current MVP: Manual Rerun

The current MVP does not support mid-flow resume. If a step fails:

1. The operator reads the error message.
2. The operator fixes the underlying issue (e.g., approves a scenario,
   fixes project config, corrects input data).
3. The operator reruns the script from the beginning.

The smoke loop is idempotent in the sense that each rerun creates new
entities with new IDs — it does not attempt to reuse existing entities.

## 16.2. Future Retry Model (Conceptual)

```text
Resume from last successful stage:
    Runtime inspects entity states.
    Runtime identifies the first incomplete step.
    Runtime resumes execution from that step.

Retry failed tool:
    Runtime re-invokes the tool that failed.
    Previous partial outputs may be cleaned up or overwritten.

Re-run validation:
    Runtime re-runs validation without re-executing the entire pipeline.

Re-open approval gate:
    Runtime resets the approval state and re-presents for human review.
```

## 16.3. Idempotency Considerations (Future)

1. Services should not duplicate entities accidentally — if a Scenario
   already exists for a given Idea in an active state, runtime should
   detect this and ask whether to reuse or create new.
2. Artifact overwrites should be versioned or explicitly confirmed.
   Overwriting a published ExportPackage without versioning loses
   historical traceability.
3. Retry after failure should resume from the correct stage, not restart
   the entire pipeline. A MetricSnapshot failure should not require
   re-creating the Idea.

These considerations are architectural direction for future phases. The
current MVP does not implement resume, idempotency detection or artifact
versioning.

---

# 17. Human Approval and Input Gates

## 17.1. Definition

Approval gates are points in the runtime flow where execution pauses
until a human operator confirms or provides input.

## 17.2. Current MVP Gates

In the current Foundation MVP (copilot mode), human involvement is
required at these points:

| Gate | Type | How It Works |
|---|---|---|
| Idea creation | Input | Human creates the Idea manually (via script or programmatic call). |
| Manual publication | Manual action | Human copies caption from export package, pastes into platform, publishes. |
| Publication URL recording | Input | Human records the published URL and timestamp. |
| Metric entry | Input | Human collects metrics from platform, imports via `import_manual_metrics.py`. |

These are not mid-flow "pause and ask" gates — they are steps where
the human performs an action outside the system and then feeds the
result back in.

## 17.3. Future Approval Gates (Conceptual)

| Gate | Trigger | What Human Reviews |
|---|---|---|
| Production Brief approval | Before production begins | Content direction, audience, format, channels. |
| QA warnings | Non-blocking QA issues found | Whether to proceed despite warnings. |
| Content preview | Before publication | Final content draft with captions, media, branding. |
| Publication approval | Before manual or connector publishing | Final approval to publish to each channel. |
| Strategy change | Agent proposes modifying goals or priorities | Whether to accept the proposed change. |
| Autopilot boundary | Agent encounters low-confidence situation | How to handle the uncertain situation. |

## 17.4. Gate Rules

1. No content may be published without the operator's knowledge in the
   current MVP.
2. Future connector-based publishing must never bypass approval rules.
3. Approval records must be preserved for audit.
4. A rejected approval must include a reason, stored for Learning Memory.
5. Autonomy mode determines which gates are enforced:
   - Copilot: all gates active.
   - Assisted: routine gates auto-approved; strategic gates active.
   - Autopilot: only blocking errors and explicit approval rules active.

---

# 18. Autonomy Modes in Runtime

## 18.1. Mode Definitions

Runtime behaviour adapts to the project's autonomy mode (configured in
Project Settings / Brand System):

### Copilot Mode (Current MVP Default)

```text
Runtime pauses frequently.
Human confirms every significant action.
No autonomous decisions.
All publication is manual.
All metrics are manual.
```

### Assisted Mode (Future)

```text
Routine steps run without pausing.
Warnings cause pause for human review.
Strategic decisions require confirmation.
Publication may be connector-based with approval.
```

### Autopilot Mode (Future)

```text
Runtime proceeds if Project Settings allow.
Blocking issues cause pause.
Non-blocking warnings are logged, not escalated.
Emergency stop mechanism always available.
Human can reduce autonomy at any time.
```

## 18.2. Current MVP Constraint

Autopilot mode is a future concept. The current MVP operates exclusively
in copilot mode. There is no autonomous background loop. There is no
continuous 24/7 agent cycle. Runtime executes only when explicitly
triggered by a human via CLI or script.

---

# 19. Agent-to-Runtime Contract

## 19.1. Principle

In future phases, the Orchestrator Agent will issue execution requests
to the runtime layer. The agent decides what to do. Runtime executes
the decision.

## 19.2. What Agent May Request

```text
start_content_cycle       — begin a full content cycle for a project
generate_content_item     — create a single content item from a scenario
create_export_package     — prepare export for a content item
validate_package          — run validation on an export package
prepare_publication       — create publication plan and checklist
create_metric_snapshot    — create a draft metric snapshot
import_metrics            — record metrics into a snapshot
run_analytics_evaluation  — evaluate performance against goals
```

## 19.3. What Agent Must Provide

```text
project_id                — required for all requests
explicit_action           — which runtime action to execute
context                   — relevant entity IDs, channel targets, parameters
autonomy_mode             — current autonomy level for gate enforcement
allowed_scope             — boundaries within which runtime may operate
approval_requirements     — which steps require human approval
```

## 19.4. What Agent Must NOT Do

- Directly mutate storage or write to entity JSON files.
- Skip services and create domain entities directly.
- Bypass domain state validation.
- Publish content without going through Distribution rules.
- Update Learning Memory without going through Analytics/Learning flow.
- Change entity statuses without calling the correct service.
- Execute tools that are outside the current MVP scope (autoposting,
  media rendering, external API calls).

## 19.5. Contract Enforcement

The runtime layer enforces the contract by:

1. Validating that the requested action is valid for the current
   project state.
2. Checking that all required context is provided.
3. Executing only through services (never direct entity manipulation).
4. Returning structured results with entity states and artifact paths.
5. Recording all agent-initiated actions for audit.

---

# 20. Runtime and Project Scope

## 20.1. Project Scoping Rule

Every runtime execution is project-scoped. Runtime must:

1. Load project config first — validate that `project_id` exists and the
   project is active.
2. Scope all entity creation to the project — every entity carries
   `project_id`.
3. Store all artifacts under project-specific directories.
4. Never write project data to a different project's directory.
5. Never load or reference data from another project without explicit
   cross-project configuration (not supported in MVP).

## 20.2. Workspace / Project Boundaries

```text
Workspace (internal)  →  Container for projects
    │
    ├── Project A     →  own data/, exports/, ideas/, scenarios/, etc.
    ├── Project B     →  own data/, exports/, ideas/, scenarios/, etc.
    └── Project C     →  own data/, exports/, ideas/, scenarios/, etc.
```

Runtime must preserve these boundaries. No project leakage into the
platform core. No project-specific logic in the core runtime.

## 20.3. Current MVP Conformance

- `LoopOrchestrator.run_minimal_loop()` requires `project_id`.
- `ProjectService.get_project()` validates the project before any
  operation.
- All repositories scope data by `project_id`.
- Artifacts are written under `{project_dir}/data/` and
  `{project_dir}/exports/`.

---

# 21. Runtime and Storage

## 21.1. Current Storage Model

The current MVP uses local filesystem storage:

```text
storage/smoke_projects/{project_id}/
    project.yaml                          — project config (copy)
    data/
        ideas/{idea_id}.json              — Idea entities
        scenarios/{scenario_id}.json      — Scenario entities
        content_items/{content_item_id}.json  — ContentItem entities
        export_packages/{export_package_id}.json  — ExportPackage entities
        publications/{publication_id}.json — Publication entities
        metric_snapshots/{metric_snapshot_id}.json — MetricSnapshot entities
    exports/{export_package_id}/
        title.txt
        body.txt
        caption_{platform}.txt
        manual_publication_checklist.txt
        metadata.json
        manifest.json
```

## 21.2. Source vs Runtime Storage

```text
Source (committed):
    projects/{project_id}/project.yaml    — canonical project config
    docs/07_projects/{project_slug}/      — brand documentation

Runtime (not committed):
    storage/smoke_projects/{project_id}/  — smoke test runtime artifacts
```

The smoke loop copies the source config into the runtime directory.
Runtime never modifies source files.

## 21.3. Future Storage (Conceptual)

| Capability | Current | Future |
|---|---|---|
| Entity storage | JSON files on filesystem | PostgreSQL with file references |
| Export packages | Local directories | Object storage (S3-compatible) |
| Runtime state | In-memory (not persisted) | Database or state file |
| Logs | stdout | Structured logs, traces, dashboards |
| Queue | None | Redis/RabbitMQ for async execution |
| Observability | Terminal output | Execution dashboard, audit history |

Do not implement future storage models in the current MVP.

---

# 22. Runtime Observability

## 22.1. Current MVP Observability

The current MVP provides observability through:

| Mechanism | What It Shows |
|---|---|
| Terminal output (stdout) | Smoke loop summary: entity IDs, statuses, export file paths. |
| Exit codes | `0` = success, non-zero = failure. |
| File system inspection | JSON entity files can be read directly. Export directories contain human-readable artifacts. |
| `LoopOrchestrator.get_loop_status()` | Programmatic status summary per project (entity counts by status). |
| `inspect_package.py` | Human-readable display of export package contents. |
| `validate_package.py` | Validation report with pass/fail and error details. |
| `find_metric_snapshots.py` | List of metric snapshots with statuses. |

## 22.2. Future Observability (Conceptual)

| Capability | Description |
|---|---|
| Execution logs | Structured log entries with timestamps, stage, entity references. |
| Stage timings | Duration of each runtime step for performance analysis. |
| Error records | Persistent error log with codes, stages, recommendations. |
| State transition logs | Record of every entity state transition with timestamps. |
| Artifact path registry | Central record of all artifacts produced per execution. |
| Validation outcomes | Record of all validation results with pass/fail/warning counts. |
| Execution dashboard | UI view of active, completed and failed executions (future). |
| Audit trail | Complete history of agent actions and their outcomes (future). |

---

# 23. Runtime Validation

## 23.1. Pre-Execution Validation

Before runtime begins executing the lifecycle:

1. **Project exists:** `ProjectService.get_project(project_id)` succeeds.
2. **Config valid:** Required fields in `project.yaml` are present.
3. **Inputs present:** All required inputs (idea title, description, etc.)
   are provided.
4. **Project active:** Project status is `active` (not `paused` or
   `archived`).

## 23.2. During-Execution Validation

At each stage:

1. **Precondition check:** The service validates that prerequisites are
   met (e.g., Idea must be approved before Scenario creation).
2. **Input validation:** Service validates input fields against allowed
   values (e.g., valid funnel_stage, supported content_format).
3. **State transition:** Service invokes `entity.transition_to()` which
   validates the transition against allowed rules in `transitions.py`.
4. **QA checks:** Where applicable, service runs quality checks and
   records warnings or failures.

## 23.3. Post-Execution Validation

After the loop completes:

1. **Expected artifacts exist:** Export directory contains `title.txt`,
   `body.txt`, `caption_{platform}.txt`, `metadata.json`, `manifest.json`,
   `manual_publication_checklist.txt`.
2. **Package validates:** `validate_package.py` returns pass.
3. **Publication record exists:** If publication step completed,
   `Publication` entity exists with status `PUBLISHED`.
4. **Metric snapshot exists:** If analytics step completed,
   `MetricSnapshot` entity exists (status may be `DRAFT` or `RECORDED`).
5. **Loop status summary:** `get_loop_status()` returns correct counts
   for each entity type.

---

# 24. Runtime Compatibility with Production / Distribution / Analytics Specs

## 24.1. Production Pipeline Spec

Runtime executes the production steps described in
`PRODUCTION_PIPELINE_SPEC.md` through `ProductionLifecycleService`:

```text
Runtime calls create_content_item() → Brief/Plan/Generate/Assemble equivalent
Runtime calls run_technical_qa()   → QA stage equivalent
Runtime calls approve_content()    → Approval gate equivalent
```

For the current `text_social_post` MVP, the production pipeline is
collapsed into deterministic service calls. Future content types
(carousel, video) will require the full multi-stage production pipeline
as described in the spec.

## 24.2. Asset Library Spec

In the current MVP, the Asset Library is minimally active (no media
assets needed for text-only content). Runtime does not invoke asset
selection. Future runtime will call asset selection as part of
production planning.

## 24.3. Distribution Spec

Runtime executes distribution through `PublishingService`:

```text
Runtime calls create_export_package() → Distribution Intake equivalent
Runtime calls prepare_export()        → Channel Adaptation + Checklist export
Runtime calls create_publication()    → Publication Plan creation
Runtime calls publish_content()       → Manual Publication recording
```

The current MVP uses manual publication only. Future connector-based
distribution will follow the full Distribution pipeline described in
`DISTRIBUTION_SPEC.md`.

## 24.4. Analytics Spec

Runtime executes analytics through `AnalyticsService`:

```text
Runtime calls create_metric_snapshot()  → Analytics Intake equivalent
Manual tool: import_manual_metrics.py   → Metric Collection (manual mode)
        calls record_metrics()           → Normalization + Snapshot population
```

The current MVP uses manual metrics only. Future connector-based
collection will follow the full Analytics pipeline described in
`ANALYTICS_SPEC.md`.

## 24.5. Learning Memory Spec

In the current MVP, Learning Memory is not active. Runtime does not
trigger learning extraction. After cycle completion, the data is
available for future learning but no automatic handoff occurs.

In future phases, runtime will trigger a Learning Memory handoff after
analytics completion — passing the `MetricSnapshot` and production
context to the Learning Extraction process.

---

# 25. Current MVP Compatibility

## 25.1. What Stays Exactly as Is

```text
PROJECT CONFIG:         projects/{project_id}/project.yaml — unchanged.
DOMAIN MODELS:          All entities, enums, transitions — unchanged.
SERVICE INTERFACES:     All service methods — unchanged.
REPOSITORIES:           All filesystem repositories — unchanged.
ENTITY CHAIN:           Project → Idea → Scenario → ContentItem →
                        ExportPackage → Publication → MetricSnapshot — unchanged.
SMOKE LOOP:             smoke_loop.py — unchanged.
INSPECT SCRIPT:         inspect_package.py — unchanged.
VALIDATE SCRIPT:        validate_package.py — unchanged.
FIND SNAPSHOTS:         find_metric_snapshots.py — unchanged.
IMPORT METRICS:         import_manual_metrics.py — unchanged.
TESTS:                  All tests — unchanged.
```

## 25.2. What the Runtime Orchestration Spec Adds

This document adds conceptual structure around the existing code:

- Names and describes the runtime layer that is already implicitly
  present in `LoopOrchestrator`.
- Defines execution stages, state models and error handling in a
  structured way.
- Maps runtime behaviour to the broader LOOPRA architecture.
- Defines future extension paths without requiring current code changes.

## 25.3. No MVP Regression

This specification does NOT:

- Add new required steps to the current loop.
- Change the order of service calls.
- Modify any entity, enum or transition.
- Add new scripts, services or repositories.
- Require new dependencies.
- Change the filesystem layout.
- Break the smoke loop verification flow.

---

# 26. Future Runtime Extension Path

## 26.1. Stage 1 — Current CLI/Local Runtime (NOW)

```text
- LoopOrchestrator.run_minimal_loop() as the primary execution path.
- CLI scripts as entry points.
- Synchronous, single-threaded execution.
- In-memory execution context (no persisted state).
- Manual publication and manual metrics.
```

## 26.2. Stage 2 — Structured Runtime Commands

```text
- Runtime commands as first-class objects (e.g., RunContentCycle,
  GenerateContentItem, ValidateExportPackage).
- RuntimeExecutionContext persisted to filesystem for inspectability.
- Command-line interface for individual stage execution.
- Resume capability: skip completed stages, retry failed stages.
```

## 26.3. Stage 3 — Runtime Execution Context and State Logs

```text
- RuntimeExecutionContext with persisted state between runs.
- Execution log: structured records of each stage start/end/error.
- Timing data per stage.
- Error history per project.
- Artifact registry: central record of all files produced.
```

## 26.4. Stage 4 — Agent-Controlled Runtime Actions

```text
- Orchestrator Agent issues runtime commands via defined contract.
- Runtime validates agent requests against project scope.
- Autonomy mode gates enforced by runtime.
- Agent actions recorded in audit trail.
```

## 26.5. Stage 5 — API/UI Triggers

```text
- REST API endpoints that invoke runtime commands.
- UI actions that trigger runtime workflows.
- Request validation, authentication, project scoping enforced at API
  boundary.
```

## 26.6. Stage 6 — Worker/Queue-Based Execution

```text
- Runtime commands enqueued to job queue.
- Background workers execute runtime stages asynchronously.
- Long-running stages (media rendering, multi-channel export) run in
  parallel.
- Execution status queryable via API.
```

## 26.7. Stage 7 — Scheduled Cycles and Controlled Autopilot

```text
- Scheduled content cycles triggered by cron/timer.
- Runtime executes autonomously within configured boundaries.
- Autopilot mode with emergency stop.
- Human operator monitors through control points and periodic reviews.
```

## 26.8. Important Constraint

Do not implement any stage beyond Stage 1 until the current MVP is
stable, validated and the preceding stage is complete. Each stage builds
on the validated foundation of the previous one.

---

# 27. Runtime Entities (Conceptual)

## 27.1. Overview

The following entities describe the runtime domain. They are functional
concepts, not database schemas. None of these entities exist as code in
the current MVP. They are defined here to provide a shared vocabulary
for future implementation.

## 27.2. Entity Catalog

### RuntimeExecutionContext

```text
Purpose: Captures the state of an active or completed runtime execution.
Fields:  execution_id, project_id, workspace_id, cycle_id, current_stage,
         requested_by, autonomy_mode, started_at, completed_at, status,
         stages[], current_stage_index, inputs, outputs, artifacts, errors,
         approval_state
```

### RuntimeJob

```text
Purpose: A unit of runtime work — a single execution request that may
         span multiple stages.
Fields:  job_id, execution_id, project_id, job_type, status, priority,
         created_at, started_at, completed_at, requested_by, retry_count,
         max_retries
```

### RuntimeStage

```text
Purpose: A single step within a runtime execution.
Fields:  stage_id, execution_id, stage_name, stage_order, service_name,
         status, started_at, completed_at, inputs, outputs, error
```

### RuntimeStepResult

```text
Purpose: The outcome of a single runtime stage.
Fields:  result_id, stage_id, status (completed/failed/skipped), entity_ids
         produced, artifact_paths, warnings, error, duration_ms
```

### RuntimeArtifact

```text
Purpose: A record of a file or data entity produced during execution.
Fields:  artifact_id, execution_id, stage_id, artifact_type, path,
         content_type, size_bytes, checksum, created_at
```

### RuntimeError

```text
Purpose: A structured error that occurred during execution.
Fields:  error_id, execution_id, stage_id, error_code, severity, message,
         entity_id, project_id, recommended_action, retry_allowed, timestamp
```

### RuntimeApprovalGate

```text
Purpose: A point in the runtime flow where human approval is required.
Fields:  gate_id, execution_id, stage_id, gate_type, status
         (pending/approved/rejected/expired), requested_at, decided_at,
         decided_by, reason
```

### RuntimeInputRequest

```text
Purpose: A request for human input during execution.
Fields:  request_id, execution_id, stage_id, input_type, description,
         required_format, status (pending/provided/timeout), provided_value,
         requested_at, provided_at
```

### RuntimeToolInvocation

```text
Purpose: A record of a tool (script) invocation during execution.
Fields:  invocation_id, execution_id, stage_id, tool_name, tool_path,
         command, arguments, exit_code, stdout, stderr, started_at,
         completed_at, status
```

### RuntimeEvent

```text
Purpose: A significant event during execution (stage start, stage complete,
         error, warning, approval request, etc.).
Fields:  event_id, execution_id, event_type, stage_id, payload, timestamp
```

### RuntimeLogRecord

```text
Purpose: A log entry produced during execution.
Fields:  log_id, execution_id, level (debug/info/warning/error), message,
         stage_id, entity_id, timestamp
```

---

# 28. Runtime Security / Safety Boundaries

## 28.1. Project Scope Enforcement

1. Runtime must validate `project_id` at execution start.
2. All file writes must be under the project's directory.
3. Cross-project reads are not permitted in MVP.
4. Entity references must match the active project scope.

## 28.2. No Unapproved External Calls

1. Current MVP makes no external API calls.
2. Future connector-based publishing must verify that the channel is
   enabled and approved in Project Settings.
3. No external call may be made without explicit operator configuration.

## 28.3. No Autopost Without Explicit Settings

1. Future autoposting capability must require explicit enabling in
   Project Settings.
2. Connector credentials must be stored separately from project config.
3. Autopost must respect approval gates unless autopilot mode is active.

## 28.4. No Destructive Operations Without Confirmation

1. Entity archival should preserve data (no hard delete without explicit
   intent).
2. Artifact overwrite should be versioned or confirmed.
3. Project deletion (future) must require explicit confirmation.

## 28.5. No Hidden Background Work

1. Current MVP: runtime executes only when explicitly triggered.
2. Future scheduled jobs: must be visible in project configuration.
3. Future autopilot: operator must be able to see what is running and
   stop it.

## 28.6. Audit Trail for Agent Actions

1. All agent-initiated runtime actions must be logged.
2. Agent decisions must be recorded in Decision Memory.
3. Human must be able to review what the agent did and why.

---

# 29. Runtime Readiness Criteria

The Runtime Orchestration architecture is ready when:

- [x] Current MVP flow is described in full detail.
- [x] Runtime components are identified (domain, services, orchestrator,
      scripts, storage).
- [x] Service orchestration model is defined.
- [x] Tool invocation model is defined.
- [x] Execution context structure is defined.
- [x] Runtime states and transitions are defined.
- [x] Artifacts are catalogued.
- [x] Error handling model is defined with error codes and actions.
- [x] Human approval and input gates are documented.
- [x] Agent-to-runtime contract is defined for future phases.
- [x] Current MVP compatibility is explicitly preserved.
- [x] Future extension path is defined in stages.
- [x] Security and safety boundaries are articulated.
- [x] Relationship to Production, Distribution, Analytics and Learning
      Memory specs is documented.

---

# 30. Related Documents

```text
docs/00_foundation/DATA_MODEL.md                     — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md          — Project configuration specification
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md    — Workspace and project model
docs/02_architecture/SYSTEM_ARCHITECTURE.md          — System architecture layers
docs/02_architecture/PIPELINES_SPEC.md               — Foundation MVP pipeline
docs/02_architecture/BRAND_SYSTEM_SPEC.md            — Brand System specification
docs/03_intelligence/CONTENT_CYCLE_SPEC.md           — Content cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md            — Agent system architecture
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md     — Content intelligence specification
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md       — Trend intelligence specification
docs/03_intelligence/LEARNING_MEMORY_SPEC.md          — Learning memory specification
docs/04_production/CONTENT_TYPES_SPEC.md              — Content type definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md        — Production pipeline specification
docs/04_production/ASSET_LIBRARY_SPEC.md              — Asset library specification
docs/04_production/DISTRIBUTION_SPEC.md               — Distribution specification
docs/04_production/ANALYTICS_SPEC.md                  — Analytics specification
AGENTS.md                                             — Development rules for AI agents
STATE.md                                              — Current project state
```

### Code References

```text
core/domain/models.py         — Domain entities
core/domain/enums.py          — Domain status enums
core/domain/transitions.py    — Status transition rules
core/services/loop.py         — LoopOrchestrator (runtime orchestrator)
core/services/projects.py     — ProjectService, BrandProfileService
core/services/ideas.py        — IdeaService, ScenarioService
core/services/production.py   — ProductionLifecycleService
core/services/publishing.py   — PublishingService
core/services/analytics.py    — AnalyticsService
core/services/_storage.py     — FileSystemProjectModelRepository base
scripts/smoke_loop.py         — End-to-end smoke test (primary entrypoint)
scripts/inspect_package.py    — Export package inspection tool
scripts/validate_package.py   — Export package validation tool
scripts/find_metric_snapshots.py  — Metric snapshot discovery tool
scripts/import_manual_metrics.py  — Manual metric import tool
```

---

# 31. Document Status

| Field | Value |
|---|---|
| Status | Active — LOOPRA Runtime Layer |
| Version | v1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Runtime Orchestration Layer |

---

# Final Statement

The Runtime Orchestration Layer is the execution coordination substrate
of LOOPRA. It does not make strategic decisions. It does not generate
content, analyze trends or extract knowledge. It orchestrates the
services and tools that carry out the actions defined by the
architectural layers.

In the current Foundation MVP, runtime is embodied in the
`LoopOrchestrator` class and the CLI scripts — a deterministic,
project-scoped, copilot-mode execution engine that moves content from
Idea to MetricSnapshot without UI, API, database or external integrations.

In future phases, the same runtime model will accept requests from the
Orchestrator Agent, API endpoints, UI actions, scheduled jobs and worker
queues — while preserving the same service boundaries, domain rules and
execution principles defined here.

Runtime executes. Intelligence decides. Tools perform. This separation
is the foundation of LOOPRA's evolution from a deterministic production
pipeline into a self-learning autonomous marketing operating system.

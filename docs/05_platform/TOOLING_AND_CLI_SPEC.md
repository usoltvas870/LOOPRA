# TOOLING AND CLI SPEC

## Version

v1.0

## Status

Active — LOOPRA Platform Layer

## Purpose

This document defines the Tooling and CLI Layer of the LOOPRA Autonomous
Marketing Operating System.

It answers the central question:

> What deterministic CLI tools, scripts and execution helpers exist in LOOPRA,
> what tasks they perform, what inputs/outputs they accept, which services they
> call, which artifacts they read/create and which boundaries they must never
> violate?

TOOLING_AND_CLI_SPEC.md is the bridge between runtime orchestration, service
contracts, CLI scripts, validation helpers, manual operator workflows and future
agent tool calling.

It documents current MVP tools as they actually exist in the codebase. Tools
that do not exist are explicitly marked as future/conceptual.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document describes the set of deterministic execution tools —
CLI scripts, inspection helpers and import helpers — that the LOOPRA runtime,
human operator and future agents use to execute, inspect, validate and update
the system.

It serves as the specification for:

- each current CLI script contract;
- how tools relate to services and runtime orchestration;
- what artifacts tools read and write;
- what manual workflows exist;
- what tool boundaries must be preserved;
- what future tool categories the architecture supports.

## 1.2. In Scope

- Current CLI scripts: `smoke_loop.py`, `inspect_package.py`,
  `validate_package.py`, `find_metric_snapshots.py`, `import_manual_metrics.py`.
- Tool responsibilities, inputs, outputs and exit behaviour.
- Tool service usage (or absence thereof).
- Tool artifact interaction rules.
- Manual operator workflows.
- Tool error model.
- Future tool categories (marked as conceptual/future).
- Future agent tool-calling boundary (conceptual).
- Current tool limitations.

## 1.3. Out of Scope

- API endpoints (no API exists in current MVP).
- UI development.
- Database schemas and migrations.
- External platform integrations.
- Autoposting or automated distribution.
- Strategic decision-making (belongs to Intelligence Layer).
- New script implementation or modification.
- Tests (test scripts are described but their implementation is not in scope).
- Agent swarm or continuous background execution.

---

# 2. Role of Tools in LOOPRA

## 2.1. Core Principle

> **Agents decide. Tools execute.**

Tools are deterministic executors. They perform narrow, well-defined operations.
They do not make strategic decisions. They do not interpret results. They
execute and report.

## 2.2. What Tools Do

- Run defined lifecycle operations (or full loops).
- Inspect artifacts (export packages, entity records).
- Validate outputs against structural requirements.
- Import manually collected data into domain entities.
- Expose human/operator control points at the CLI.
- Provide inspectable, reproducible command-level verification.
- Can be called by future runtime/agents through approved entrypoints.

## 2.3. What Tools Do NOT Do

- Decide what content to create.
- Decide what to publish or where.
- Decide performance strategy or interpret metrics.
- Bypass services for domain entity mutations (mutating tools must call services).
- Mutate storage directly for domain entities unless read-only or service-backed.
- Invent business decisions.
- Execute cross-project operations.
- Make external network calls (current MVP).
- Run continuously in background.

## 2.4. Tool vs Service Boundary

```text
Services:   mutate domain entities, enforce transitions, persist via repositories.
            Only services create, update and transition entities.

Tools:      provide command-level execution, inspection, validation.
            Mutating tools call services. Read-only tools inspect artifacts directly.

Runtime:    orchestrates services. Tools are called by CLI or future agents,
            not by runtime core directly.

Agent:      decides strategy. May request tool execution through runtime.
            Must not bypass tools/services to mutate entities.
```

---

# 3. Tooling Principles

1. **Tools execute; they do not decide.** A tool says "pass" or "fail", not
   "this content is good enough to publish". Strategy decisions belong to
   the human operator (current MVP) or future Orchestrator Agent.

2. **Tools must be deterministic.** Given the same inputs and unchanged
   project state, a tool produces the same output. No randomness, no hidden
   state, no date-based branching that changes behaviour silently.

3. **Tools receive explicit inputs.** No hidden defaults that change behaviour
   without documentation. Every input is either a CLI argument or an
   environment variable with a documented default.

4. **Tools produce inspectable outputs.** Output is written to stdout/stderr
   in a structured-enough format for human reading and future machine parsing.
   Exit codes signal success/failure.

5. **Tools must return clear success/failure signals.** Exit code 0 = success.
   Exit code non-zero = failure. Errors are printed to stderr.

6. **Tools must respect project scope.** Every tool is bound to a specific
   `project_id` or artifact directory. No cross-project operations.

7. **Tools that mutate domain entities must use services.** Direct filesystem
   mutation of entity JSON files outside of repositories is forbidden. Use
   `AnalyticsService`, `PublishingService`, etc.

8. **Read-only tools may inspect filesystem artifacts directly.** Tools like
   `inspect_package.py` and `validate_package.py` read export package files
   without service dependencies. Tools like `find_metric_snapshots.py` read
   entity JSON files directly for listing — not for mutation.

9. **Future agent tool calls must be auditable.** Every tool invocation by an
   agent must be recorded with the requesting agent identity, exact inputs, and
   result.

10. **Future tools must not break current CLI workflows.** Existing `smoke_loop.py`
    and manual verification tools must remain operational. No silent interface
    changes. New flags and modes must be additive.

---

# 4. Relationship to Runtime Orchestration

## 4.1. Runtime Orchestrates; Tools Execute Commands

Runtime Orchestration (`LoopOrchestrator`, defined in
`docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md`) coordinates the full lifecycle
flow through service calls.

Tools provide command-level execution or inspection entrypoints:

```text
smoke_loop.py        →  triggers full runtime loop via LoopOrchestrator
inspect_package.py   →  inspects export artifacts (post-runtime)
validate_package.py  →  validates export artifacts (post-runtime)
find_metric_snapshots.py  →  lists metric records (post-runtime)
import_manual_metrics.py  →  imports metrics via AnalyticsService (post-runtime)
```

## 4.2. Current Separation

In the current MVP:

- `smoke_loop.py` is a standalone script that wires services manually (does not
  use `build_loop_orchestrator` directly — constructs all dependencies inline),
  creates an Idea, then calls `LoopOrchestrator.run_minimal_loop()`. It also
  uses repositories directly for the post-loop summary (read-only).

- The inspection/validation/metric tools operate independently on artifacts
  that were already produced by a prior runtime execution. They do not trigger
  new lifecycle transitions.

- The human operator decides when to run each tool and what to do with the
  results.

## 4.3. Future Runtime Integration

In future phases:

- Runtime may call tools as subprocesses or internal commands.
- Agents may request runtime to invoke specific tools.
- Workers may execute long-running tools (media rendering, platform connector
  calls).
- A Runtime Command Registry may map tool identifiers to execution handlers.
- Tool invocations records may be persisted in a `RuntimeExecutionContext`.

---

# 5. Relationship to Service Contracts

## 5.1. Services Are the Mutation Layer

Tools that change domain entity state must go through services. This is the
fundamental boundary:

```text
Tool → Service → Repository → JSON file on disk
```

Never:

```text
Tool → direct JSON file write  (forbidden for domain entities)
```

## 5.2. Current Tool Service Usage

| Tool | Uses Services? | Which Services | Notes |
|---|---|---|---|
| `smoke_loop.py` | Yes | `IdeaService`, `ScenarioService`, `ProductionLifecycleService`, `PublishingService`, `AnalyticsService` (through `LoopOrchestrator`) | Also reads repositories directly for smoke summary (read-only) |
| `inspect_package.py` | No | None | Reads `manifest.json` directly from export package directory |
| `validate_package.py` | No | None | Reads `manifest.json` and checks files on disk |
| `find_metric_snapshots.py` | No | None | Reads `{project_dir}/data/metric_snapshots/*.json` and parses via `MetricSnapshot.model_validate()`. Validates project via `load_project()` from `core.projects.loader`. |
| `import_manual_metrics.py` | Yes | `AnalyticsService.record_metrics()` (via `build_analytics_service()`) | Calls service to mutate MetricSnapshot from DRAFT → RECORDED |

## 5.3. Why Some Tools Bypass Services

- `inspect_package.py` and `validate_package.py` operate on export artifacts
  (plain files on disk), not on domain entities. No service is needed — the
  export package is a read-only artifact that was already produced by
  `PublishingService.prepare_export()`.

- `find_metric_snapshots.py` reads existing entity JSON files for listing
  purposes. It parses them into domain objects (`MetricSnapshot.model_validate()`)
  but does not mutate them. No service call is needed for a read-only query.

- If future tools need to list entities with dynamic filtering or cross-entity
  joins, those operations should be provided by service methods — not by tools
  bypassing the service layer.

---

# 6. Current Tool Inventory

The current Foundation MVP includes five CLI scripts. Each is a Python file
under `scripts/` that runs with `python scripts/<name>.py <args>`.

```text
scripts/
    smoke_loop.py              — end-to-end Foundation MVP lifecycle smoke test
    inspect_package.py         — read and display ExportPackage contents
    validate_package.py        — validate ExportPackage structure and required files
    find_metric_snapshots.py   — list MetricSnapshot records for a project
    import_manual_metrics.py   — import manually collected metrics into a draft snapshot
```

### Overview Table

| Tool | Purpose | Type | R/W | Uses Services? | Input | Output | Exit Codes |
|---|---|---|---|---|---|---|---|
| `smoke_loop.py` | Run full Foundation MVP lifecycle end-to-end | Lifecycle execution | Write | Yes (LoopOrchestrator + repositories for summary) | `CONTENT_PLANT_SMOKE_PROJECT_ID` env or `"example"` default | Printed summary to stdout; artifacts on disk | 0 = success; exception exit on failure |
| `inspect_package.py` | Display contents of an ExportPackage | Inspection | Read-only | No | `<export_package_directory>` CLI arg | Human-readable display of package metadata and file listing | 0 = success; 1 = error |
| `validate_package.py` | Validate ExportPackage structure | Validation | Read-only | No | `<export_package_directory>` CLI arg | Validation report (pass/fail with details) | 0 = success; 1 = error |
| `find_metric_snapshots.py` | List DRAFT MetricSnapshot records for a project | Query | Read-only | No | `<project_id>` CLI arg | Count and listing of draft snapshots | 0 = success; 1 = error |
| `import_manual_metrics.py` | Import manual metrics into a draft MetricSnapshot | Mutation | Write | Yes (`AnalyticsService.record_metrics()`) | `<manual_metrics_json>` CLI arg file path | Confirmation of import with recorded keys | 0 = success; 1 = error |

---

# 7. smoke_loop.py Contract

**File:** `scripts/smoke_loop.py:209`

## 7.1. Purpose

Run the complete Foundation MVP lifecycle from Idea to MetricSnapshot as a
deterministic smoke test. This is the primary end-to-end operational verification
of the LOOPRA runtime.

## 7.2. Invocation

```bash
python scripts/smoke_loop.py
```

No CLI arguments. Configuration via environment variables:

| Env Variable | Default | Description |
|---|---|---|
| `CONTENT_PLANT_SMOKE_PROJECT_ID` | `"example"` | Project ID to use for the smoke loop |
| `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` | `REPO_ROOT/storage/smoke_projects` | Root directory for runtime smoke project storage |

## 7.3. Inputs

1. **Project ID:** Resolved from `CONTENT_PLANT_SMOKE_PROJECT_ID` env var,
   defaulting to `"example"`.
2. **Project config:** Copied from `projects/{project_id}/project.yaml` to
   `storage/smoke_projects/{project_id}/project.yaml` at execution start.
3. **Idea parameters (hardcoded):**
   - `title = "Foundation smoke loop"`
   - `description = "Run the smallest project-agnostic Content Plant loop from idea to draft metrics."`
   - `funnel_stage = "trust"`
   - All other `IdeaService.create_idea()` parameters use defaults.

## 7.4. Execution Flow

```text
1. Resolve project_id from env or default ("example")
2. Resolve runtime projects root
3. Copy source project.yaml to runtime smoke projects directory
4. Build all services and loop orchestrator (inline, not via build_loop_orchestrator)
5. Create Idea via IdeaService.create_idea()
6. Call LoopOrchestrator.run_minimal_loop(project_id, idea.idea_id)
   → Full Foundation MVP lifecycle (see Section 7.5)
7. Build smoke summary by reading all entity repositories directly
8. Print summary to stdout
9. Return 0
```

## 7.5. Services Used

Via `LoopOrchestrator.run_minimal_loop()`:

- `IdeaService`: `approve_idea()` (if Idea is RAW)
- `ScenarioService`: `create_from_idea()`, `approve_scenario()`
- `ProductionLifecycleService`: `create_content_item()`, `run_technical_qa()`,
  `approve_content()`
- `PublishingService`: `create_export_package()`, `prepare_export()`,
  `create_publication()`, `publish_content()`
- `AnalyticsService`: `create_metric_snapshot()`

Repositories used directly (read-only, for summary):

- `FileSystemIdeaRepository.load_idea()`
- `FileSystemScenarioRepository.load_scenario()`
- `FileSystemContentItemRepository.load_content_item()`
- `FileSystemExportPackageRepository.load_export_package()`
- `FileSystemPublicationRepository.load_publication()`
- `FileSystemMetricSnapshotRepository.load_metric_snapshot()`

## 7.6. Entities Created

A complete set of new entities with new IDs on every run:

- `Idea` (status: `APPROVED` or `SCRIPTED`)
- `Scenario` (status: `APPROVED`)
- `ContentItem` (status: `APPROVED`)
- `ExportPackage` (status: `READY`)
- `Publication` (status: `PUBLISHED`)
- `MetricSnapshot` (status: `DRAFT`)

## 7.7. Artifacts Created

Under `storage/smoke_projects/{project_id}/`:

- `project.yaml` — copy of source config
- `data/ideas/{idea_id}.json`
- `data/scenarios/{scenario_id}.json`
- `data/content_items/{content_item_id}.json`
- `data/export_packages/{export_package_id}.json`
- `data/publications/{publication_id}.json`
- `data/metric_snapshots/{metric_snapshot_id}.json`
- `exports/{export_package_id}/title.txt`
- `exports/{export_package_id}/body.txt`
- `exports/{export_package_id}/caption_{platform}.txt`
- `exports/{export_package_id}/manual_publication_checklist.txt`
- `exports/{export_package_id}/metadata.json`
- `exports/{export_package_id}/manifest.json`

## 7.8. Output (stdout)

One key=value line per entity and summary field. Key fields:

```text
project_id=example
idea_id=idea_xxx
scenario_id=scenario_xxx
content_item_id=content_xxx
export_package_id=export_xxx
publication_id=publication_xxx
metric_snapshot_id=metric_xxx
export_directory=<path>
generated_export_files=title.txt,body.txt,...
idea_status=scripted
scenario_status=approved
content_item_status=approved
export_package_status=ready
publication_status=published
metric_snapshot_status=draft
```

## 7.9. Exit Behaviour

| Exit Code | Condition |
|---|---|
| 0 | Loop completed; all entities in valid terminal states |
| Exception (non-zero) | Any service error, missing project config, invalid entity state |

Errors propagate as unhandled Python exceptions. No structured error recovery.
The operator reads the traceback, fixes the issue, reruns.

## 7.10. Boundaries

- The script creates new entities with new IDs on every run. It is not
  idempotent — previous smoke artifacts accumulate in
  `storage/smoke_projects/`.
- The publication URL is a placeholder (`https://example.invalid/...`). The smoke
  loop simulates publication, it does not publish to any real platform.
- The script uses `CONTENT_PLANT_*` environment variable names (historical name;
  not yet renamed to LOOPRA).
- The script bypasses `build_loop_orchestrator()` and constructs services inline
  for direct repository access in the summary section.
- All mutations go through services. Repository access is read-only during
  summary generation.
- The script must not be relied upon for production operations — it is a smoke
  test tool.

---

# 8. inspect_package.py Contract

**File:** `scripts/inspect_package.py:115`

## 8.1. Purpose

Read and display the contents of an ExportPackage directory. Provides a
human-readable summary of the package metadata and file listing without
modifying any files.

## 8.2. Invocation

```bash
python scripts/inspect_package.py <export_package_directory>
```

## 8.3. Inputs

| Input | Source | Required | Constraints |
|---|---|---|---|
| `export_package_directory` | CLI arg 1 | Yes | Must exist and be a directory |
| `manifest.json` (read from dir) | Filesystem | Implicit | Must exist and be valid JSON |

## 8.4. Execution Flow

```text
1. Validate CLI argument count == 1
2. Check export_package_directory exists and is a directory
3. Read manifest.json from the directory
4. Validate manifest.json is valid JSON
5. Validate manifest structure:
   - Must be a JSON object
   - Must contain required fields: package_id, project_id, content_item_id,
     scenario_id, content_format, target_platform, manual_publication_only,
     status, files
   - files must be a list of objects with name and role fields
   - file names must be non-empty strings, relative, not absolute paths
6. Print summary lines to stdout
7. Return 0
```

## 8.5. Required Manifest Fields

```text
package_id
project_id
content_item_id
scenario_id
content_format
target_platform
manual_publication_only
status
files           — list of {name, role} objects
```

## 8.6. Output (stdout)

```text
package_id=export_xxx
project_id=example
content_item_id=content_xxx
scenario_id=scenario_xxx
content_format=text_social_post
target_platform=telegram
status=ready
manual_publication_only=true
files:
- title.txt [title]
- body.txt [body]
- caption_telegram.txt [caption]
- manual_publication_checklist.txt [manual_publication_checklist]
- metadata.json [metadata]
- manifest.json [manifest]
```

## 8.7. Exit Behaviour

| Exit Code | Condition |
|---|---|
| 0 | Manifest read and displayed successfully |
| 1 | Missing argument, invalid directory, missing manifest, invalid JSON, invalid structure |

Errors are printed to stderr with `ERROR: ` prefix.

## 8.8. Boundaries

- **Read-only.** This tool never modifies the export package, manifest, or any
  other file.
- **No service usage.** Operates entirely at the filesystem level on export
  artifacts.
- **Does not validate business strategy.** The tool checks manifest structure,
  not content quality or publication readiness.
- **Does not validate whether files listed in manifest actually exist on disk.**
  That is the responsibility of `validate_package.py`.

---

# 9. validate_package.py Contract

**File:** `scripts/validate_package.py:168`

## 9.1. Purpose

Validate that an ExportPackage directory contains all required files and has a
correct structure. This is a structural package validation, not a production QA
or strategy approval check.

## 9.2. Invocation

```bash
python scripts/validate_package.py <export_package_directory>
```

## 9.3. Inputs

| Input | Source | Required | Constraints |
|---|---|---|---|
| `export_package_directory` | CLI arg 1 | Yes | Must exist and be a directory |
| `manifest.json` (read from dir) | Filesystem | Implicit | Must exist and be valid JSON |

## 9.4. Manifest Validation (stricter than inspect_package.py)

In addition to the `inspect_package.py` manifest checks, `validate_package.py`
enforces:

| Check | Constraint |
|---|---|
| String fields non-empty | `package_id`, `project_id`, `content_item_id`, `scenario_id`, `content_format`, `target_platform`, `status` must be non-empty strings |
| `manual_publication_only` | Must be exactly `true` |
| `status` | Must be `"ready"` (one of: `ready`) |
| File entries | Same as inspect_package.py: must be objects with non-empty `name` and `role` strings, relative paths |

## 9.5. Package Directory Validation

| Check | Constraint |
|---|---|
| `metadata.json` | Must exist in the package directory |
| `manual_publication_checklist.txt` | Must exist in the package directory |
| `title.txt` | Must exist in the package directory |
| `body.txt` | Must exist in the package directory |
| `caption_{target_platform}.txt` | Must exist (platform-specific caption file) |
| `metadata.json` validity | Must be parseable JSON |
| All manifest-listed files | Every file in `manifest.files[].name` must exist on disk |

## 9.6. Output (stdout) — Success

```text
validation_status=ok
package_id=export_xxx
project_id=example
target_platform=telegram
files_checked=6
ready_for_manual_publication=true
```

## 9.7. Exit Behaviour

| Exit Code | Condition |
|---|---|
| 0 | All validation checks passed |
| 1 | Missing argument, invalid directory, missing manifest, invalid JSON, structural failure, missing file |

Errors printed to stderr with `ERROR: ` prefix.

## 9.8. Boundaries

- **Read-only.** Never modifies the export package.
- **No service usage.** Operates at the filesystem level.
- **Structural validation only.** Checks that files exist and manifest is correct.
  Does NOT validate: content quality, caption length relative to platform limits,
  brand compliance, production QA, strategy alignment.
- "Validation" here means "is the package structurally correct for manual
  publication" — not "is this content approved for publishing".

---

# 10. find_metric_snapshots.py Contract

**File:** `scripts/find_metric_snapshots.py:137`

## 10.1. Purpose

Find and list MetricSnapshot records in DRAFT status for a given project.
Helps the human operator locate snapshots that are ready for manual metric import.

## 10.2. Invocation

```bash
python scripts/find_metric_snapshots.py <project_id>
```

## 10.3. Inputs

| Input | Source | Required | Constraints |
|---|---|---|---|
| `project_id` | CLI arg 1 | Yes | Must reference a valid project |
| `CONTENT_PLANT_PROJECTS_ROOT` | Env var (optional) | No | Override projects root directory |

## 10.4. Execution Flow

```text
1. Validate CLI argument count == 1
2. Resolve projects root (CONTENT_PLANT_PROJECTS_ROOT env or default PROJECTS_ROOT)
3. Validate project exists via load_project(project_id)
4. Resolve project directory
5. List all *.json files in {project_dir}/data/metric_snapshots/
6. For each file:
   a. Read and parse JSON
   b. Validate required fields: metric_snapshot_id, project_id,
      publication_id, content_item_id, platform, status
   c. Parse into MetricSnapshot via MetricSnapshot.model_validate()
   d. Verify snapshot.project_id matches requested project_id
7. Filter to DRAFT status snapshots
8. Sort by created_at descending
9. Print count and listing to stdout
10. Return 0
```

## 10.5. Required Snapshot JSON Fields

```text
metric_snapshot_id
project_id
publication_id
content_item_id
platform
status
```

## 10.6. Output (stdout)

```text
metric_snapshots_found=3
project_id=example
snapshots:
- metric_snapshot_id=metric_xxx publication_id=publication_xxx content_item_id=content_xxx platform=telegram status=draft
- metric_snapshot_id=metric_yyy ...
```

## 10.7. Exit Behaviour

| Exit Code | Condition |
|---|---|
| 0 | Listing completed (even if 0 snapshots found) |
| 1 | Invalid project_id, unreadable storage, invalid JSON, missing fields, validation error |

## 10.8. Service Usage

**Does NOT use `AnalyticsService`.** This tool reads filesystem directly:

- Uses `core.projects.loader.load_project()` and `resolve_project_dir()` for
  project validation and path resolution.
- Reads raw JSON files from `{project_dir}/data/metric_snapshots/`.
- Parses into `MetricSnapshot` domain model via
  `MetricSnapshot.model_validate()`.
- No service calls, no repository abstraction — direct filesystem + domain model
  parsing.

This is a current MVP design choice. A future version may route through
`AnalyticsService.list_metric_snapshots()` if the listing needs additional
filtering, cross-entity joins or access control.

## 10.9. Boundaries

- **Read-only.** Never modifies snapshots or any files.
- **Project-scoped.** Only reads snapshots matching the given project_id.
- **DRAFT filter only.** The script hardcodes `MetricSnapshotStatus.DRAFT` as the
  target status. Other statuses are ignored.
- **Not a generic query tool.** Only finds draft snapshots. No status filter args,
  no metric value queries, no cross-snapshot aggregation.

---

# 11. import_manual_metrics.py Contract

**File:** `scripts/import_manual_metrics.py:110`

## 11.1. Purpose

Import manually collected performance metrics into a draft MetricSnapshot.
This is the current MVP's manual analytics entry point.

## 11.2. Invocation

```bash
python scripts/import_manual_metrics.py <manual_metrics_json>
```

## 11.3. Inputs — JSON File Format

The input JSON file must be a JSON object with these top-level fields:

| Field | Type | Required | Constraints |
|---|---|---|---|
| `project_id` | `string` | Yes | Non-empty; must reference a valid project |
| `metric_snapshot_id` | `string` | Yes | Non-empty; must reference an existing MetricSnapshot in DRAFT status |
| `metrics` | `object` | Yes | Non-empty object with supported metric keys |

`metrics` supports these keys:

| Key | Type | Constraints | Normalized To |
|---|---|---|---|
| `views` | `int` | `>= 0` | `content_metrics.views` |
| `likes` | `int` | `>= 0` | `content_metrics.likes` |
| `comments` | `int` | `>= 0` | `content_metrics.comments` |
| `shares` | `int` | `>= 0` | `content_metrics.shares` |
| `saves` | `int` | `>= 0` | `content_metrics.saves` |
| `clicks` | `int` | `>= 0` | `content_metrics.link_clicks` |
| `published_url` | `string` | Non-empty | Updates `Publication.published_url` |

`published_url` is special: it is not stored inside the snapshot as a metric.
Instead, it updates the related `Publication` record's `published_url` field.

## 11.4. Example Input JSON

```json
{
  "project_id": "example",
  "metric_snapshot_id": "metric_abc123",
  "metrics": {
    "views": 1250,
    "likes": 85,
    "comments": 12,
    "shares": 8,
    "saves": 34,
    "clicks": 15,
    "published_url": "https://t.me/mybrand/42"
  }
}
```

## 11.5. Execution Flow

```text
1. Validate CLI argument count == 1
2. Read and parse input JSON file
3. Validate payload structure:
   - Must be a JSON object
   - Must contain project_id, metric_snapshot_id, metrics (all non-empty)
4. Resolve projects root (CONTENT_PLANT_PROJECTS_ROOT env or default)
5. Build AnalyticsService via build_analytics_service()
6. Call AnalyticsService.record_metrics(project_id, metric_snapshot_id, metrics)
   - Validates metric keys are in SUPPORTED_MANUAL_METRIC_KEYS
   - Validates numeric values are non-negative integers
   - Validates published_url is non-empty string (if provided)
   - If published_url provided: updates Publication.published_url
   - Merges numeric metrics into ContentPerformanceMetrics
   - Transitions MetricSnapshot DRAFT → RECORDED
7. Print success summary to stdout
8. Return 0
```

## 11.6. Services Used

- `build_analytics_service()` → `AnalyticsService`
- `AnalyticsService.record_metrics()` performs:
  - Metric key validation
  - Metric value validation
  - Publication URL update (via `FileSystemPublicationRepository`)
  - Content metrics merge
  - MetricSnapshot transition DRAFT → RECORDED

## 11.7. Output (stdout) — Success

```text
metrics_import_status=ok
project_id=example
metric_snapshot_id=metric_xxx
recorded_keys=views,likes,comments,shares,saves,clicks,published_url
```

The `recorded_keys` line lists which of the standard supported keys were present
in the input. Keys are listed in fixed order: `views, likes, comments, shares,
saves, clicks, published_url`. Only keys actually present in the input appear.

## 11.8. Exit Behaviour

| Exit Code | Condition |
|---|---|
| 0 | Metrics imported; snapshot transitioned to RECORDED |
| 1 | Missing argument, file not found, invalid JSON, missing required fields, unknown metric keys, invalid values, snapshot not in DRAFT, publication not found, project not found |

## 11.9. Boundaries

- **Mutates via service.** All entity changes go through `AnalyticsService`
  which enforces domain transitions and validation.
- **No direct filesystem writes.** The tool never writes to entity JSON files
  directly.
- **No performance interpretation.** The tool imports raw numbers. It does not
  calculate engagement rates, compare to benchmarks, or evaluate whether metrics
  are "good" or "bad".
- **No cross-snapshot operations.** Only one snapshot is updated per invocation.
- **Manual source only.** `source_type` remains `"manual"` — the snapshot's
  original source type from creation.
- **No metric aggregation.** The tool does not update earlier snapshots, compute
  trends or produce aggregate analytics summaries.

---

# 12. CLI Input/Output Standards

## 12.1. Input Standards

| Aspect | Standard | Current Compliance |
|---|---|---|
| Input file paths | Explicit CLI argument. Paths expanded with `expanduser()`. | All tools comply. |
| `project_id` | Explicit CLI argument or environment variable with documented default. | `smoke_loop.py` uses env var. `find_metric_snapshots.py` uses CLI arg. Both comply. |
| JSON payloads | File path to a JSON file. Tool validates structure, types and required fields. | `import_manual_metrics.py` complies. |
| No hidden defaults | Every default is documented in the tool's help text or contract. | Partial. `smoke_loop.py` defaults to `"example"` project. Env vars are documented in code comments but not as a `--help` flag. No `--help` output exists on any current tool. |

## 12.2. Output Standards

| Aspect | Standard | Current Compliance |
|---|---|---|
| Human-readable summary | Key=value lines on stdout, structured enough for grep/awk. | All tools comply (key=value format). |
| Structured for future parsing | Consistent field naming, predictable line order. | Partial. Field order is consistent within each tool but format is not machine-optimized. |
| Clear success/failure | Success prints structured summary to stdout. Failure prints `ERROR: <message>` to stderr. | All tools comply. |
| Exit codes | 0 = success; non-zero = failure. | All tools comply. Exit code 1 used for all error types (no differentiated error codes). |
| Error messages | Descriptive message on stderr indicating what went wrong. | All tools comply. |

## 12.3. Current Limitations

- No `--help` flag or usage text beyond ad-hoc error messages.
- No `--json` output mode for machine-readable structured output.
- No `--quiet` or `--verbose` flags.
- No standardized CLI framework (tools use ad-hoc `sys.argv` parsing).
- Exit codes are not differentiated (1 for all errors — no distinction between
  invalid input, missing file, validation failure, or service error).
- Environment variable names use `CONTENT_PLANT_*` prefix (historical naming).

---

# 13. Artifact Interaction Rules

## 13.1. Artifacts Tools May Interact With

| Artifact | Path Pattern | Read-Only Tools | Write Tools |
|---|---|---|---|
| Project config | `{projects_root}/{project_id}/project.yaml` | `find_metric_snapshots.py` (validates project exists) | `smoke_loop.py` (copies to smoke runtime dir) |
| Idea record | `{project_dir}/data/ideas/{idea_id}.json` | `smoke_loop.py` (summary section) | `smoke_loop.py` (via IdeaService) |
| Scenario record | `{project_dir}/data/scenarios/{scenario_id}.json` | `smoke_loop.py` (summary section) | `smoke_loop.py` (via ScenarioService) |
| ContentItem record | `{project_dir}/data/content_items/{content_item_id}.json` | `smoke_loop.py` (summary section) | `smoke_loop.py` (via ProductionLifecycleService) |
| ExportPackage record | `{project_dir}/data/export_packages/{export_package_id}.json` | `smoke_loop.py` (summary section) | `smoke_loop.py` (via PublishingService) |
| Publication record | `{project_dir}/data/publications/{publication_id}.json` | `smoke_loop.py` (summary section) | `smoke_loop.py` (via PublishingService); `import_manual_metrics.py` (via AnalyticsService — URL update) |
| MetricSnapshot record | `{project_dir}/data/metric_snapshots/{metric_snapshot_id}.json` | `find_metric_snapshots.py` (listing); `smoke_loop.py` (summary) | `import_manual_metrics.py` (via AnalyticsService) |
| `title.txt` | `{project_dir}/exports/{export_package_id}/title.txt` | `inspect_package.py` (via manifest); `validate_package.py` (existence check) | None (created by PublishingService) |
| `body.txt` | `{project_dir}/exports/{export_package_id}/body.txt` | `inspect_package.py` (via manifest); `validate_package.py` (existence check) | None |
| `caption_{platform}.txt` | `{project_dir}/exports/{export_package_id}/caption_{platform}.txt` | `inspect_package.py` (via manifest); `validate_package.py` (existence check) | None |
| `manual_publication_checklist.txt` | `{project_dir}/exports/{export_package_id}/manual_publication_checklist.txt` | `inspect_package.py` (via manifest); `validate_package.py` (existence check) | None |
| `metadata.json` | `{project_dir}/exports/{export_package_id}/metadata.json` | `inspect_package.py` (via manifest); `validate_package.py` (parse + existence check) | None |
| `manifest.json` | `{project_dir}/exports/{export_package_id}/manifest.json` | `inspect_package.py` (read + parse); `validate_package.py` (read + validate) | None |
| Manual metrics JSON | User-provided path (any location) | — | `import_manual_metrics.py` (reads input file; does NOT modify it) |

## 13.2. Artifact Interaction Rules

1. **Read-only tools must not mutate artifacts.** `inspect_package.py` and
   `validate_package.py` never write to the export package directory or any
   entity JSON file.

2. **Mutating tools must go through services.** `smoke_loop.py` creates entities
   via `IdeaService`, `ScenarioService`, `ProductionLifecycleService`,
   `PublishingService`, `AnalyticsService`. `import_manual_metrics.py` mutates
   via `AnalyticsService.record_metrics()`.

3. **Direct filesystem read for entity listing is allowed (current MVP).**
   `find_metric_snapshots.py` reads entity JSON files directly for listing
   purposes. This is a read-only operation that does not require service
   orchestration.

4. **Artifact paths must remain project-scoped.** All entity storage, export
   files and metric data live under `{project_dir}/data/` or
   `{project_dir}/exports/`.

5. **Runtime artifacts must not be committed.** Smoke loop outputs under
   `storage/smoke_projects/` are local-only. `graphify-out/` is generated local
   output. Neither should be tracked in version control.

6. **External input files (manual metrics JSON) are read but never modified.**
   The tool reads the user's JSON, imports the data, and leaves the source file
   untouched.

---

# 14. Tool Error Model

## 14.1. Error Categories

Each tool may encounter these error categories:

| Category | Description | Example |
|---|---|---|
| Input validation | Missing or invalid CLI argument or env var | No argument provided; invalid path |
| File not found | Required file or directory does not exist | Missing `manifest.json`; no such project directory |
| Invalid format | File content does not match expected format | Invalid JSON; missing required fields; wrong types |
| Domain validation | Entity state does not allow the requested operation | Snapshot not in DRAFT; ContentItem not APPROVED |
| Service error | Service-level validation failure | Unknown metric keys; invalid metric values; empty published_url |
| Permission / OS error | Filesystem access failure | Cannot read directory; cannot write to file |

## 14.2. Error Code Table

| Error | Category | Typical Cause | Recommended Action | Retry |
|---|---|---|---|---|
| Missing CLI argument | Input validation | Tool called without required positional argument | Check usage; provide the required argument | Yes |
| Directory not found | File not found | Export package directory does not exist at given path | Verify the export directory path from smoke loop output | Yes |
| `manifest.json` not found | File not found | Export package is incomplete or wrong directory specified | Verify the path points to a valid ExportPackage directory | Yes |
| Invalid JSON in manifest | Invalid format | `manifest.json` is corrupted or hand-edited incorrectly | Rerun the smoke loop to regenerate a valid package | Yes |
| Missing required manifest fields | Invalid format | `manifest.json` structure changed or is from an older version | Rerun export with current `PublishingService.prepare_export()` | Yes |
| Required file missing from package | File not found | Export package is incomplete | Rerun `prepare_export` or the full smoke loop | Yes |
| Invalid `project_id` | Domain validation | Project does not exist or config is unreadable | Check project_id; verify `project.yaml` exists at expected path | Yes (fix project first) |
| Snapshot not in DRAFT status | Domain validation | Trying to import metrics into a non-draft snapshot | Find a DRAFT snapshot via `find_metric_snapshots.py` | Yes (use DRAFT) |
| Unknown metric keys | Service error | Input JSON contains unsupported metric field names | Use only: views, likes, comments, shares, saves, clicks, published_url | Yes (fix JSON) |
| Invalid metric value (negative) | Service error | Metric value is negative integer | Metrics must be >= 0; check input data | Yes (fix value) |
| Invalid metric value (not int) | Service error | Metric value is float, string or null | Numeric metrics must be non-negative integers | Yes (fix type) |
| `published_url` empty | Service error | `published_url` is provided but empty or whitespace-only | Provide a valid URL or omit `published_url` | Yes |
| Project config missing/invalid | Domain validation | `project.yaml` is missing required fields | Check project config against documentation | No (fix config first) |
| OS / permission error | Permission error | Filesystem access denied, read-only filesystem | Check filesystem permissions for the project directory | No (fix permissions) |

## 14.3. Current Error Propagation

- All tools catch errors, print `ERROR: <message>` to stderr, and exit with code 1.
- No structured error payloads. No error codes in machine-readable format.
- Domain-level errors from services (e.g., `AnalyticsValidationError`,
  `PublishingValidationError`) carry descriptive messages that tools relay to the
  user.

## 14.4. Future Error Model

Future tools should include:

- Differentiated exit codes (1 = input error, 2 = file not found, 3 = validation
  failure, 4 = service error, etc.).
- Optional `--json` output mode returning structured error objects:
  ```json
  {"status": "error", "error_code": "snapshot_not_draft", "message": "...", "details": {...}}
  ```
- `--quiet` mode suppressing stdout, returning only exit code.

---

# 15. Tool Exit Behaviour

## 15.1. Current Exit Code Convention

| Exit Code | Meaning | Used By |
|---|---|---|
| 0 | Success | All tools |
| 1 | Error (any type) | All tools |
| Exception (non-zero, non-1) | Unhandled exception (stack trace printed to stderr) | `smoke_loop.py` (if service error propagates uncaught) |

## 15.2. Current Limitations

- All tools use exit code 1 for every error type. No differentiation between
  "invalid input", "file not found", "domain validation failure" and "service
  error".
- `smoke_loop.py` does not catch exceptions — unhandled service errors print
  full Python tracebacks and exit with a system-dependent non-zero code.
- No tool currently supports `--help`, `--version`, `--json` or `--quiet` flags.
- Stdout format is key=value lines, which is grep-friendly but not a guaranteed
  contract for machine parsing (field order may change across versions).

## 15.3. Future Standard

```text
Exit codes (future):
    0  — success
    1  — input/usage error (wrong args, missing file)
    2  — validation failure (package invalid, manifest malformed)
    3  — domain state error (snapshot not in DRAFT, content not approved)
    4  — service/runtime error (internal error, unhandled exception)
    5  — permission/OS error

Output modes (future):
    --format human  (default, key=value lines as current)
    --format json   (structured JSON output for machine consumption)
```

---

# 16. Manual Operator Workflows

These are the complete workflows a human operator follows using the current
CLI tools. Each workflow describes the sequence of tool invocations and manual
actions.

## 16.1. Run Smoke Loop (End-to-End Verification)

**Goal:** Verify the complete Foundation MVP lifecycle works end-to-end.

```text
1. Human ensures project config exists at projects/{project_id}/project.yaml
2. Human runs:
       python scripts/smoke_loop.py
   Or with explicit project:
       CONTENT_PLANT_SMOKE_PROJECT_ID=myproject python scripts/smoke_loop.py
3. Tool copies project config to runtime storage
4. Tool creates an Idea, runs the full loop, prints entity IDs and statuses
5. Human verifies all status lines show valid terminal states
6. Human proceeds to inspect/validate the export package
```

## 16.2. Inspect Export Package

**Goal:** View the contents of a generated ExportPackage.

```text
1. Human copies the export_directory path from smoke_loop.py output
2. Human runs:
       python scripts/inspect_package.py <export_directory>
3. Tool prints package metadata and file listing
4. Human reviews package_id, target_platform, status, and all files
5. Human decides whether the package looks correct
```

## 16.3. Validate Export Package

**Goal:** Confirm the ExportPackage is structurally valid for manual publication.

```text
1. Human runs:
       python scripts/validate_package.py <export_directory>
2. Tool validates manifest structure, required files exist, metadata is valid JSON
3. If success:
   - Tool prints "validation_status=ok" and "ready_for_manual_publication=true"
   - Human can proceed to manual publication
4. If failure:
   - Tool prints "ERROR: ..." describing what is missing
   - Human must rerun the smoke loop to regenerate a valid package
```

## 16.4. Publish Manually

**Goal:** Publish the content to the target platform outside LOOPRA.

```text
1. Human opens the export package directory
2. Human opens manual_publication_checklist.txt and reads the step-by-step guide
3. Human opens the target platform (e.g., Telegram channel)
4. Human copies caption from caption_{platform}.txt
5. Human posts content on the platform
6. Human copies the resulting publication URL
7. Human records the URL for later metric import
```

Note: This workflow is manual and executed outside LOOPRA tools. The checklist
file is generated by `PublishingService.prepare_export()` as part of the
ExportPackage.

## 16.5. Record Manual Metrics

**Goal:** Import manually collected performance metrics into LOOPRA.

```text
1. Human finds a draft MetricSnapshot:
       python scripts/find_metric_snapshots.py <project_id>
2. Human identifies the target snapshot from the listing
3. Human creates a JSON file (e.g., metrics.json) with the format:
       {
         "project_id": "<project_id>",
         "metric_snapshot_id": "<snapshot_id>",
         "metrics": {
           "views": 1250,
           "likes": 85,
           "comments": 12,
           "shares": 8,
           "saves": 34,
           "clicks": 15,
           "published_url": "https://t.me/mybrand/42"
         }
       }
4. Human runs:
       python scripts/import_manual_metrics.py metrics.json
5. Tool validates input, calls AnalyticsService.record_metrics()
6. Tool prints "metrics_import_status=ok" with recorded keys
7. MetricSnapshot transitions from DRAFT to RECORDED
```

## 16.6. Find Metric Snapshots

**Goal:** Locate MetricSnapshot records ready for metric import.

```text
1. Human runs:
       python scripts/find_metric_snapshots.py <project_id>
2. Tool lists all DRAFT snapshots with IDs, publication_ids, platforms, statuses
3. Human selects the snapshot to import metrics into
4. Human proceeds to import_manual_metrics.py workflow
```

---

# 17. Tooling and Current MVP Verification

## 17.1. What Each Tool Verifies

| Tool | What It Verifies |
|---|---|
| `smoke_loop.py` | Full Foundation MVP lifecycle is operationally sound: Project → Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot. All services, repositories, transitions and artifact generation work correctly. |
| `inspect_package.py` | ExportPackage is readable. `manifest.json` has the correct structure and all expected metadata fields. |
| `validate_package.py` | ExportPackage is structurally correct: all required files exist, manifest is valid, package status is READY, prepared for manual publication. |
| `find_metric_snapshots.py` | MetricSnapshot records are discoverable. DRAFT snapshots can be located from the filesystem. |
| `import_manual_metrics.py` | Manual metric import works end-to-end: JSON parsing, validation, AnalyticsService call, DRAFT→RECORDED transition, Publication URL update. |

## 17.2. Verification Chain

```text
smoke_loop.py             —  proves the lifecycle works
    ↓
inspect_package.py        —  proves the output is readable
    ↓
validate_package.py       —  proves the output is correct
    ↓
find_metric_snapshots.py  —  proves metrics are discoverable
    ↓
import_manual_metrics.py  —  proves metrics can be recorded
```

All five tools together provide complete operational verification of the current
Foundation MVP.

---

# 18. Tooling and Tests

## 18.1. Test Files Related to Tools

Tests exist for each tool's behaviour. They are in `tests/services/`:

| Test File | Tests What |
|---|---|
| `tests/services/test_smoke_loop.py` | Smoke loop execution, entity creation, summary output |
| `tests/services/test_inspect_package.py` | `inspect_package.py` manifest reading, display, error handling |
| `tests/services/test_validate_package.py` | `validate_package.py` structural validation, error conditions |
| `tests/services/test_find_metric_snapshots.py` | `find_metric_snapshots.py` snapshot listing, filtering, error handling |
| `tests/services/test_import_manual_metrics.py` | `import_manual_metrics.py` JSON parsing, validation, service call |
| `tests/services/test_manual_metrics_workflow.py` | End-to-end manual metrics workflow integration |

Domain-level tests:

| Test File | Tests What |
|---|---|
| `tests/domain/test_models.py` | Domain entity creation, validation, field constraints |
| `tests/domain/test_transitions.py` | Status transition rules, allowed/forbidden transitions |

Service-level tests:

| Test File | Tests What |
|---|---|
| `tests/services/test_projects.py` | ProjectService, BrandProfileService, project config validation |
| `tests/services/test_ideas.py` | IdeaService, ScenarioService, idea/scenario lifecycle |
| `tests/services/test_loop_engineering.py` | LoopOrchestrator, full lifecycle orchestration |

## 18.2. Relationship Between Tools and Tests

- Tool scripts (`scripts/*.py`) are the **CLI entrypoints** for manual
  operations. They handle argument parsing, file I/O, human-readable output.
- Test files (`tests/services/test_*.py`) test the **underlying logic**, service
  contracts and domain behaviour. They call tool `main()` functions or test the
  services directly.
- Tests are the programmatic verification layer. Tools are the manual
  operational layer. Both must remain consistent.

## 18.3. Current Limitation

There are **no dedicated CLI-level integration tests** that run the actual shell
command `python scripts/smoke_loop.py` as a subprocess and assert on its exit
code and stdout. Tests call tool `main()` functions programmatically. Full CLI
invocation testing would require subprocess-based tests.

---

# 19. Future Tool Categories

These tool categories are architectural direction. They are NOT implemented in
the current Foundation MVP.

## 19.1. Asset Validation Tools

| Purpose | Validate images, videos and audio files against channel specifications and brand requirements. |
|---|---|
| Checks | Dimensions, aspect ratio, duration, file size, format, codec, bitrate, color profile, resolution. |
| Status | Future — not implemented. |

## 19.2. Media Render Tools

| Purpose | Generate visual content (images, carousel slides, video edits) from production specifications. |
|---|---|
| Status | Future — not implemented. |

## 19.3. Production QA Tools

| Purpose | Run comprehensive content quality checks beyond the current minimal technical QA: readability, brand voice consistency, grammar, SEO, localization checks. |
|---|---|
| Status | Future — not implemented. |

## 19.4. Distribution Preflight Tools

| Purpose | Validate ExportPackage against platform-specific publishing rules before manual or connector publication: character limits, aspect ratios, hashtag counts, UTM presence. |
|---|---|
| Status | Future — not implemented. |

## 19.5. Connector Publishing Tools

| Purpose | Dispatch content to external platforms via API connectors. Handle authentication, media upload, caption submission, result recording. |
|---|---|
| Status | Future — not implemented. |

## 19.6. Analytics Collection Tools

| Purpose | Pull metrics from external platform APIs on schedule. Normalize platform-specific metrics into standard categories. Create time-series MetricSnapshots. |
|---|---|
| Status | Future — not implemented. |

## 19.7. Learning Memory Inspection Tools

| Purpose | Query Learning Memory for accumulated patterns, performance trends, effective content strategies. |
|---|---|
| Status | Future — not implemented. |

## 19.8. Runtime Command Tools

| Purpose | Execute specific lifecycle stages independently (create-scenario-only, run-qa-only, prepare-export-only) without running the full loop. |
|---|---|
| Status | Future — not implemented. |

## 19.9. Approval Management Tools

| Purpose | List, approve, reject, comment on pending publication approvals. View approval history. |
|---|---|
| Status | Future — not implemented. |

## 19.10. Project Maintenance Tools

| Purpose | Validate project configuration against schema, migrate project data between storage layouts, archive old entities, clean up smoke artifacts. |
|---|---|
| Status | Future — not implemented. |

---

# 20. Future Agent Tool-Calling Boundary

## 20.1. Principle

In future phases, the Orchestrator Agent may request execution of specific tools
through the runtime layer. The agent decides what to do. The runtime invokes
the tool. The tool executes deterministically.

```text
Agent   →  "I need to validate the export package before publication."
Runtime →  invokes validate_package.py
Tool    →  validates and returns pass/fail
Runtime →  returns result to Agent
Agent   →  decides: "Package is valid. Proceed to publication."
```

## 20.2. What Agent May Request

| Requestable Action | Tool/Service |
|---|---|
| Validate export package | `validate_package.py` |
| Inspect export package | `inspect_package.py` |
| Find metric snapshots | `find_metric_snapshots.py` |
| Import metrics | `import_manual_metrics.py` |
| Run content cycle | `LoopOrchestrator.run_minimal_loop()` |
| Get loop status | `LoopOrchestrator.get_loop_status()` |

Additional actions as new tools are implemented (render worker, connector
publish, analytics collection, etc.).

## 20.3. What Agent Must Provide

For every tool invocation request, the agent must provide:

| Field | Required | Description |
|---|---|---|
| `explicit_action` | Yes | Which tool or service action to execute |
| `project_id` | Yes | Project scope for the operation |
| `entity_id` or `file_path` | Conditional | Target entity or artifact path |
| `allowed_scope` | Yes | Boundaries within which the tool may operate |
| `autonomy_mode` | Yes | Current autonomy level (affects approval gates) |
| `approval_context` | Conditional | Whether human approval was obtained before invoking |

## 20.4. What Agent Must NOT Do

- Call arbitrary shell commands beyond approved tool contracts.
- Mutate project files or entity JSON directly — only through services/tools.
- Bypass domain/service boundaries to shortcut lifecycle steps.
- Publish content without going through Distribution rules.
- Scrape or connect to external platforms unless a configured connector exists.
- Execute tools outside the current project scope.
- Skip validation and approval rules.

## 20.5. Auditing

All agent-initiated tool invocations must be recorded:

```text
AgentToolInvocation:
    invocation_id           — unique identifier
    agent_id                — which agent requested execution
    action                  — which tool/action was invoked
    project_id              — project scope
    inputs                  — exact inputs passed
    result                  — tool exit code and output summary
    requested_at            — timestamp
    completed_at            — timestamp
    autonomy_mode           — agent's autonomy level at invocation time
    approval_required       — whether human approval was required
    approval_granted        — whether approval was obtained
```

---

# 21. Tool Security / Safety Boundaries

## 21.1. Current MVP Safety Rules

1. **No destructive filesystem operations without explicit confirmation.**
   Current tools do not delete files or directories. `smoke_loop.py` creates
   files; it does not delete previous smoke artifacts.

2. **No cross-project writes.** All writes are scoped to the project directory
   identified by `project_id`. No tool writes to another project's directory.

3. **No external network calls.** None of the current tools make HTTP requests
   or connect to external services. The smoke loop generates a placeholder
   publication URL (`https://example.invalid/...`).

4. **No secrets in CLI arguments.** Current tools do not accept credentials,
   API keys or tokens as arguments or environment variables.

5. **No autoposting.** Publication is always manual. No tool publishes content
   to external platforms.

6. **No background execution.** All tools are synchronous, one-shot CLI
   commands. They run, produce output and exit.

7. **No hidden modification of source docs/config.** `smoke_loop.py` copies
   `project.yaml` to runtime storage — it does not modify the source config
   under `projects/`.

## 21.2. Future Safety Rules

1. **Connector credential isolation.** Platform API credentials must never
   appear in CLI arguments, environment variables visible to other processes,
   or log output. Use secure credential storage.

2. **Publication approval enforcement.** Connector publishing tools must check
   that publication has been approved before dispatching. The approval record
   must exist and be in `approved` status.

3. **Rate limiting for external calls.** Connector tools must respect platform
   API rate limits. Retry with backoff. Never hammer an external API.

4. **Operation confirmation for destructive actions.** Archive, delete,
   overwrite tools must prompt for confirmation (or require a `--force` flag
   explicitly passed).

5. **Tool invocation audit trail.** All tool executions — especially those
   initiated by agents — must be logged with timestamps, inputs and results.

---

# 22. Current Limitations

These are the known limitations of the current MVP tooling layer:

| Limitation | Impact | Future Direction |
|---|---|---|
| Tools are human-oriented | Output format is optimized for human reading, not machine parsing | Add `--json` output mode |
| No `--help` or `--version` flags | Operator discovers usage only from error messages or documentation | Add argparse-based CLI with standard flags |
| No standardized JSON output mode | Machine consumers must parse key=value lines | Add `--format json` |
| No common CLI framework | Each tool has ad-hoc argument parsing | Consider `argparse` or `click` |
| No persisted RuntimeExecutionContext | No way to track execution state across tool invocations | Implement execution context persistence |
| No queue/worker model | Long-running operations block the CLI | Future worker execution for media rendering, connector calls |
| No standardized exit code taxonomy | All errors use exit code 1 | Differentiate exit codes by error category |
| No integrated command registry | No way to discover available tools programmatically | Implement a tool registry with metadata |
| `CONTENT_PLANT_*` env var naming | Historical naming not yet updated to LOOPRA branding | Rename to `LOOPRA_*` in future |
| `smoke_loop.py` bypasses `build_loop_orchestrator()` | Duplicated service wiring logic | Use factory function; separate summary logic from execution |
| `find_metric_snapshots.py` bypasses `AnalyticsService` for listing | Direct filesystem access instead of service query | Add `list_by_status` to AnalyticsService and use it |
| No idempotency in smoke loop | Every run creates new entities with new IDs; artifacts accumulate | Add cleanup flag or timestamped subdirectories |
| Tools are not invocable as library functions | Must be invoked as CLI subprocesses or explicitly call `main()` | Provide clean Python API alongside CLI entrypoint |

---

# 23. Future Tooling Extension Path

Staged evolution from current scripts to full platform tooling:

```text
Stage 1 — Current scripts (PRESENT)
    Ad-hoc CLI scripts with basic key=value output.
    Human-operated. No registry. No JSON mode.
    ✅ IMPLEMENTED

Stage 2 — Standardized CLI interface
    argparse-based CLI with --help, --version, --quiet.
    Consistent argument naming across all tools.
    Documented exit codes and outputs.
    □ FUTURE

Stage 3 — Structured JSON output mode
    --format json producing machine-readable structured output.
    Structured error payloads.
    □ FUTURE

Stage 4 — Runtime command registry
    Metadata-driven tool discovery.
    Tool listing: available commands, inputs, outputs, version.
    Programmatic invocation by runtime core.
    □ FUTURE

Stage 5 — Agent-safe tool invocation
    AgentToolInvocation records for audit.
    Runtime enforces agent-provided scope and autonomy constraints.
    Agent cannot call arbitrary shell commands.
    □ FUTURE

Stage 6 — Worker-executed long-running tools
    Async execution for rendering, connector publishing, analytics collection.
    Progress reporting. Timeout handling. Cancellation.
    □ FUTURE

Stage 7 — Platform connector tools with approvals
    Connector dispatch after approval gate verification.
    Credential isolation. Rate limiting. Error retry.
    □ FUTURE

Stage 8 — Full operational dashboard / UI triggers
    UI buttons that invoke tool commands through API layer.
    Human and agent workflows converge on the same tool contracts.
    □ FUTURE
```

---

# 24. Tooling Readiness Criteria

The tooling document is aligned when:

- [x] All five current CLI scripts identified.
- [x] Each current script contract documented with purpose, inputs, outputs,
  exit behaviour, boundaries.
- [x] Service usage (or non-usage) for each tool documented.
- [x] Artifact interaction rules documented for each tool.
- [x] Tool error model documented with categories, causes, actions.
- [x] Manual operator workflows documented (6 workflows).
- [x] Current MVP verification chain described.
- [x] Relationship to tests documented.
- [x] Future tool categories explicitly marked as future/conceptual.
- [x] Future agent tool-calling boundary defined.
- [x] Tool safety/security boundaries documented.
- [x] Current limitations honestly catalogued.
- [x] Future staged extension path defined.
- [x] Foundation MVP chain preserved — no current tool contracts were invented
  or altered.

---

# 25. Related Documents

| Document | Relationship |
|---|---|
| `AGENTS.md` | Defines agent principles: agents decide, tools execute |
| `STATE.md` | Defines current project state and development phase |
| `docs/00_foundation/DATA_MODEL.md` | Defines domain entities that tools inspect and mutate |
| `docs/02_architecture/PIPELINES_SPEC.md` | Defines pipeline stages and current helper-supported workflow |
| `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` | Defines how runtime orchestrates services; tools are CLI entrypoints |
| `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` | Defines service contracts that mutating tools must use |
| `docs/04_production/DISTRIBUTION_SPEC.md` | Defines distribution layer that tools inspect and validate |
| `docs/04_production/ANALYTICS_SPEC.md` | Defines analytics layer that metric tools interact with |

---

# 26. Code References

### CLI Scripts

| Script | File |
|---|---|
| `smoke_loop.py` | `scripts/smoke_loop.py` |
| `inspect_package.py` | `scripts/inspect_package.py` |
| `validate_package.py` | `scripts/validate_package.py` |
| `find_metric_snapshots.py` | `scripts/find_metric_snapshots.py` |
| `import_manual_metrics.py` | `scripts/import_manual_metrics.py` |

### Core Services

| Service | File |
|---|---|
| `LoopOrchestrator` | `core/services/loop.py` |
| `PublishingService` | `core/services/publishing.py` |
| `AnalyticsService` | `core/services/analytics.py` |
| `IdeaService` | `core/services/ideas.py` |
| `ScenarioService` | `core/services/ideas.py` |
| `ProductionLifecycleService` | `core/services/production.py` |
| `ProjectService` | `core/services/projects.py` |
| `BrandProfileService` | `core/services/projects.py` |

### Repositories

| Repository | File |
|---|---|
| `FileSystemProjectRepository` | `core/services/projects.py` |
| `FileSystemIdeaRepository` | `core/services/ideas.py` |
| `FileSystemScenarioRepository` | `core/services/ideas.py` |
| `FileSystemContentItemRepository` | `core/services/production.py` |
| `FileSystemExportPackageRepository` | `core/services/publishing.py` |
| `FileSystemPublicationRepository` | `core/services/publishing.py` |
| `FileSystemMetricSnapshotRepository` | `core/services/analytics.py` |
| `FileSystemProjectModelRepository` (base) | `core/services/_storage.py` |

### Tests

| Test Directory | Files |
|---|---|
| `tests/domain/` | `test_models.py`, `test_transitions.py` |
| `tests/services/` | `test_smoke_loop.py`, `test_inspect_package.py`, `test_validate_package.py`, `test_find_metric_snapshots.py`, `test_import_manual_metrics.py`, `test_manual_metrics_workflow.py`, `test_ideas.py`, `test_projects.py`, `test_loop_engineering.py` |

---

# 27. Document Status

| Attribute | Value |
|---|---|
| Status | Active — LOOPRA Platform Layer |
| Version | v1.0 |
| Layer | Platform Layer — Tooling and CLI |
| Created | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |

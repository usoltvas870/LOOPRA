# OPERATIONAL RUNBOOK

## Version

v1.0

## Status

Active — LOOPRA Operations Layer

## Purpose

This document is the **practical operations guide** for the current LOOPRA
Foundation MVP. It answers the central question:

> How should an operator, developer or AI maintenance agent run, check,
> diagnose and safely maintain the current LOOPRA Foundation MVP without
> violating architectural boundaries?

This document describes what currently exists — not what is planned. It is
the bridge between platform specifications (which explain architecture) and
actual operational actions (which keep the system running).

---

# 1. Purpose and Scope

## 1.1. Purpose

The OPERATIONAL_RUNBOOK.md provides step-by-step operational procedures for:

- verifying the Foundation MVP is alive;
- running the smoke loop;
- inspecting and validating export packages;
- performing manual publication;
- finding and importing manual metrics;
- diagnosing common errors;
- maintaining git hygiene;
- preparing operational reports.

## 1.2. Who Uses This Document

| Role | How They Use It |
|------|-----------------|
| Human operator | Follow workflows to run, check and maintain the system. |
| Developer | Verify changes do not break the MVP lifecycle. |
| Codex / CLI agent | Execute documented commands with known expected outputs. |
| Future maintenance agent | Use as the canonical operational reference. |

## 1.3. In Scope

- Local MVP operation
- Running tests (domain, services, full suite)
- Executing the smoke loop
- Export package inspection and validation
- Manual publication procedure
- Finding and importing manual metrics
- Troubleshooting operational errors
- Git hygiene during operations
- Operational acceptance reporting
- Safety rules and limitations

## 1.4. Out of Scope

- Production deployment
- API / UI operations
- Database operations
- Connector operations
- SaaS operations
- User / role management
- Monitoring infrastructure
- CI / CD pipeline setup
- Autoposting or automated distribution
- External integrations

---

# 2. Operating Model

## 2.1. Current Model

LOOPRA Foundation MVP operates as a **local, copilot/manual** system:

| Property | Current Value |
|----------|--------------|
| Execution environment | Local developer workstation |
| Storage | Local filesystem (JSON files + plain text exports) |
| Trigger | Manual CLI invocation |
| Background workers | None |
| External network calls | None |
| Publication | Manual (human copies content to platform) |
| Metrics | Manual (human collects and imports numbers) |
| Autonomy mode | Copilot only |

## 2.2. Operating Principle

```
Human decides.
Scripts execute.
Services mutate state.
Tools inspect/validate.
No autoposting.
```

The system does not make content strategy decisions, publish content or
collect metrics automatically. Every external action requires a human.

---

# 3. Operational Roles

## 3.1. Human Operator

**May do:**
- Run smoke_loop.py to execute the full MVP lifecycle
- Inspect and validate export packages
- Copy content from export package and publish manually on external platforms
- Collect metrics from platforms and import via import_manual_metrics.py
- Run tests to verify system health
- Create and edit project.yaml configurations
- Manually clean up runtime artifacts

**Must not do:**
- Directly edit entity JSON files in storage/ (use services/tools instead)
- Commit runtime artifacts to version control
- Store secrets or credentials in project.yaml
- Delete source projects/ or core/ directories

## 3.2. Developer

**May do:**
- All operator actions
- Run individual test files during development
- Inspect domain entity states for debugging
- Use factory functions to construct services programmatically

**Must not do:**
- Bypass services and modify entity JSON files directly
- Add project-specific logic to core/ (project-agnostic foundation)
- Introduce API, UI, DB or external integrations without architectural approval
- Modify .gitignore without justification

## 3.3. Codex / Implementation Agent

**May do:**
- Execute documented CLI commands from this runbook
- Run tests to verify changes
- Read entity state and export package contents
- Propose configuration changes for human review

**Must not do:**
- Write entity JSON files directly (use services only)
- Modify project.yaml without explicit human approval
- Execute destructive operations without confirmation
- Invoke commands not documented in this runbook
- Assume future capabilities exist (autoposting, connectors, etc.)

## 3.4. Future Orchestrator Agent (Conceptual)

In future phases, an Orchestrator Agent will issue execution requests through
runtime entrypoints. It must:
- Route all mutations through services
- Respect approval gates
- Not bypass domain state transitions
- Operate within a single project scope
- Leave audit trail of all decisions

**Current MVP:** No agent exists. All execution is human-triggered.

---

# 4. Required Preconditions

Before operating LOOPRA Foundation MVP, ensure:

| Precondition | How to Verify |
|-------------|---------------|
| Repository cloned | `git status` returns clean or expected state |
| Python environment available | `python --version` returns Python 3.x |
| Dependencies installed | All imports in scripts and tests resolve (pydantic, etc.) |
| Project config exists | `projects/{project_id}/project.yaml` is present and valid |
| Scripts accessible | `scripts/smoke_loop.py` and other scripts are present |
| Tests available | `tests/domain/` and `tests/services/` directories exist with test files |
| No uncommitted unrelated changes | `git status --short` shows only intended files |

The project uses **`unittest`** (Python standard library). No third-party
test runner (pytest, tox) is configured or required at the repository root.
No dependency manager file (requirements.txt, pyproject.toml with deps) is
present at the root. Dependencies are assumed to be available in the Python
environment. Verify by attempting imports before operations.

---

# 5. Current Important Paths

## 5.1. Path Reference Table

| Path | Type | Purpose |
|------|------|---------|
| `projects/{project_id}/project.yaml` | Source | Canonical project configuration |
| `docs/07_projects/{project_slug}/` | Source | Project-specific brand documentation |
| `storage/smoke_projects/{project_id}/` | Runtime | Smoke loop runtime artifacts (gitignored) |
| `storage/smoke_projects/{project_id}/data/` | Runtime | Domain entity JSON records |
| `storage/smoke_projects/{project_id}/exports/` | Runtime | Generated export package files |
| `scripts/` | Source | CLI tool entrypoints |
| `tests/domain/` | Source | Domain model and transition tests |
| `tests/services/` | Source | Service, tool and lifecycle tests |
| `core/services/` | Source | Service and repository implementations |
| `core/domain/` | Source | Domain models, enums, transition rules |
| `core/projects/loader.py` | Source | Project config loading and validation |
| `docs/05_platform/` | Source | Platform layer specifications |
| `docs/06_operations/` | Source | Operations layer documentation |
| `graphify-out/` | Generated | Knowledge graph output (gitignored) |

## 5.2. Source vs Runtime Separation

```
Source (committed):           Runtime (gitignored, generated):
─────────────────────         ─────────────────────────────────
projects/                     storage/smoke_projects/
  {project_id}/                 {project_id}/
    project.yaml                  project.yaml  (copy of source)
docs/                             data/           (entity JSON)
  07_projects/                    exports/        (export files)
    {project_slug}/
scripts/
tests/
core/
```

Source paths contain authored code and configuration — committed to version
control. Runtime paths contain generated execution output — excluded from
version control by `.gitignore` (`storage/*`).

---

# 6. Environment Variables

## 6.1. Current Environment Variables

All environment variables use `LOOPRA_*` as the primary prefix.
`CONTENT_PLANT_*` names remain operational as legacy fallback for backward
compatibility. `LOOPRA_*` vars are checked first; if not set, `CONTENT_PLANT_*`
vars serve as fallback.

### LOOPRA_SMOKE_PROJECT_ID (primary)

| Property | Value |
|----------|-------|
| **Purpose** | Select which project to run the smoke loop for |
| **Default** | `"example"` |
| **Used by** | `scripts/smoke_loop.py` |
| **When to use** | When testing a non-default project via smoke loop |
| **Example** | `$env:LOOPRA_SMOKE_PROJECT_ID="nura"; python scripts/smoke_loop.py` |
| **Fallback** | If env var is empty string after stripping, falls back to `"example"` |
| **Legacy** | `CONTENT_PLANT_SMOKE_PROJECT_ID` is the legacy fallback |

### LOOPRA_SMOKE_PROJECTS_ROOT (primary)

| Property | Value |
|----------|-------|
| **Purpose** | Override the runtime directory for smoke project storage |
| **Default** | `{REPO_ROOT}/storage/smoke_projects` |
| **Used by** | `scripts/smoke_loop.py` |
| **When to use** | When you need smoke artifacts in a different location |
| **Example** | `$env:LOOPRA_SMOKE_PROJECTS_ROOT="C:\temp\smoke"; python scripts/smoke_loop.py` |
| **Legacy** | `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` is the legacy fallback |

### LOOPRA_PROJECTS_ROOT (primary)

| Property | Value |
|----------|-------|
| **Purpose** | Override the projects root for metric snapshot tools |
| **Default** | `{REPO_ROOT}/projects` |
| **Used by** | `scripts/find_metric_snapshots.py`, `scripts/import_manual_metrics.py` |
| **When to use** | When metric snapshots are under `storage/smoke_projects/` (runtime) rather than `projects/` (source). This is the normal case — smoke loop writes snapshots under `storage/smoke_projects/`, not under source `projects/`. |
| **Example** | `$env:LOOPRA_PROJECTS_ROOT="storage/smoke_projects"; python scripts/find_metric_snapshots.py example` |
| **Legacy** | `CONTENT_PLANT_PROJECTS_ROOT` is the legacy fallback |

## 6.2. Important Note on LOOPRA_PROJECTS_ROOT

The smoke loop writes all runtime artifacts (including metric snapshots) under
`storage/smoke_projects/{project_id}/`. When running `find_metric_snapshots.py`
or `import_manual_metrics.py` after a smoke loop, you must point
`LOOPRA_PROJECTS_ROOT` to `storage/smoke_projects` (or use the legacy fallback
`CONTENT_PLANT_PROJECTS_ROOT`), otherwise the tools
will look in `projects/` (source config directory) and find no metrics.

## 6.3. Environment Variables Not Present

The following are confirmed absent in the current MVP:

- `LOOPRA_*` env vars are now active as primary (see Section 6.1)
- No `.env` file at the repository root
- No `DATABASE_URL`, `SECRET_KEY`, `API_KEY`
- No `LOOPRA_ENV` or deployment mode env vars
- No log level env vars
- No feature flag env vars

---

# 7. Standard Verification Commands

## 7.1. Test Commands

LOOPRA uses **Python `unittest`** (standard library). All commands run from
the repository root.

### Run Domain Tests

```bash
python -m unittest discover -s tests/domain
```

Runs tests from:
- `tests/domain/test_models.py` — domain entity creation, field requirements
- `tests/domain/test_transitions.py` — status transition rules

**When to run:** Before and after any change affecting domain models, enums or
transition rules.

### Run Service Tests

```bash
python -m unittest discover -s tests/services
```

Runs tests from all files under `tests/services/`:
- `test_projects.py` — ProjectService, BrandProfileService
- `test_ideas.py` — IdeaService, ScenarioService
- `test_loop_engineering.py` — Production, Publishing, Analytics, LoopOrchestrator
- `test_smoke_loop.py` — Full smoke loop subprocess test
- `test_inspect_package.py` — Export package inspection
- `test_validate_package.py` — Export package validation
- `test_find_metric_snapshots.py` — Metric snapshot discovery
- `test_import_manual_metrics.py` — Manual metric import
- `test_manual_metrics_workflow.py` — End-to-end metrics workflow

**When to run:** After any change affecting services, repositories or tools.

### Run All Tests

```bash
python -m unittest discover -s tests
```

**When to run:** Before committing changes; as full operational verification.

### Run Individual Test File

```bash
python -m unittest tests.domain.test_models
python -m unittest tests.services.test_loop_engineering
python -m unittest tests.services.test_smoke_loop
```

**When to run:** During focused development on a specific area.

## 7.2. Test Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | All tests passed |
| 1 | At least one test failed or errored |

---

# 8. Full Operational Acceptance Workflow

This is the recommended complete workflow for verifying the Foundation MVP is
operationally sound.

## 8.1. Workflow Steps

```
1. CHECK GIT STATUS
   git status --short
   → Verify only intended files are modified. No unexpected changes.

2. RUN DOMAIN TESTS
   python -m unittest discover -s tests/domain
   → All domain tests must pass.

3. RUN SERVICE TESTS
   python -m unittest discover -s tests/services
   → All service tests must pass (including smoke loop test).

4. RUN ALL TESTS (optional but recommended)
   python -m unittest discover -s tests
   → Complete verification.

5. RUN SMOKE LOOP
   python scripts/smoke_loop.py
   → Captures export_directory from output.

6. INSPECT EXPORT PACKAGE
   python scripts/inspect_package.py <export_directory>
   → Verifies package is readable, manifest structure correct.

7. VALIDATE EXPORT PACKAGE
   python scripts/validate_package.py <export_directory>
   → Verifies all required files exist, package is structurally valid.

8. FIND DRAFT METRIC SNAPSHOTS
   $env:LOOPRA_PROJECTS_ROOT="storage/smoke_projects"
   python scripts/find_metric_snapshots.py example
   → Locates draft snapshots ready for metric import.

9. CREATE MANUAL METRICS JSON
   Write a metrics.json file with project_id, metric_snapshot_id, and metrics.

10. IMPORT MANUAL METRICS
    $env:LOOPRA_PROJECTS_ROOT="storage/smoke_projects"
    python scripts/import_manual_metrics.py metrics.json
    → Records metrics; snapshot transitions DRAFT → RECORDED.

11. CHECK GIT STATUS AGAIN
    git status --short
    → Verify only intended docs/code changed. No runtime artifacts appear.

12. PREPARE OPERATIONAL REPORT
    Summarize what was done, what passed, what failed, remaining risks.
```

## 8.2. Workflow Notes

- Step 5 (smoke loop) creates new entities with new IDs on every run.
  Previous smoke artifacts remain under `storage/smoke_projects/`.
- Step 8 and 10 require `LOOPRA_PROJECTS_ROOT` pointing to
  `storage/smoke_projects` (or the legacy `CONTENT_PLANT_PROJECTS_ROOT`) — otherwise tools look in source `projects/`.
- Smoke loop uses placeholder publication URL (`https://example.invalid/...`).
  This is correct — publication is simulated in the smoke loop.
- The manual metrics JSON in step 9 must reference a real `metric_snapshot_id`
  found in step 8.

---

# 9. Running the Smoke Loop

## 9.1. Purpose

The smoke loop (`scripts/smoke_loop.py`) is the primary end-to-end operational
verification of the LOOPRA runtime. It executes the complete Foundation MVP
lifecycle chain:

```
Project → Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot
```

## 9.2. Command

```bash
python scripts/smoke_loop.py
```

`--help` / `-h` on the smoke loop exits 0 and does NOT execute the lifecycle.

## 9.3. Default Behaviour

| Aspect | Value |
|--------|-------|
| Default project | `example` (from `projects/example/project.yaml`) |
| Override project | `$env:LOOPRA_SMOKE_PROJECT_ID="other_project"` |
| Runtime storage | `storage/smoke_projects/{project_id}/` |
| Override storage | `$env:LOOPRA_SMOKE_PROJECTS_ROOT="<path>"` |
| Idea title | `"Foundation smoke loop"` (hardcoded) |
| Funnel stage | `"trust"` (hardcoded) |
| Content format | `text_social_post` (default) |

## 9.4. Expected Output Fields

The smoke loop prints key=value lines to stdout. Expected fields:

```text
project_id=example
idea_id=idea_xxxxxxxxxxxx
scenario_id=scenario_xxxxxxxxxxxx
content_item_id=content_xxxxxxxxxxxx
export_package_id=export_xxxxxxxxxxxx
publication_id=publication_xxxxxxxxxxxx
metric_snapshot_id=metric_xxxxxxxxxxxx
export_directory=<full path to export package directory>
generated_export_files=title.txt,body.txt,caption_telegram.txt,manual_publication_checklist.txt,metadata.json,manifest.json
idea_status=scripted
scenario_status=approved
content_item_status=approved
export_package_status=ready
publication_status=published
metric_snapshot_status=draft
```

## 9.5. Expected Statuses

| Entity | Expected Status | Meaning |
|--------|----------------|---------|
| Idea | `scripted` | Idea was approved and a scenario was created from it |
| Scenario | `approved` | Scenario passed QA and was approved |
| ContentItem | `approved` | Content passed technical QA and was approved |
| ExportPackage | `ready` | Export files written, package ready for manual publication |
| Publication | `published` | Publication record created with placeholder URL |
| MetricSnapshot | `draft` | Draft snapshot created, ready for manual metric import |

## 9.6. Artifacts Created

Under `storage/smoke_projects/{project_id}/`:

```
project.yaml                                         — copy of source config
data/
    ideas/{idea_id}.json
    scenarios/{scenario_id}.json
    content_items/{content_item_id}.json
    export_packages/{export_package_id}.json
    publications/{publication_id}.json
    metric_snapshots/{metric_snapshot_id}.json
exports/{export_package_id}/
    title.txt
    body.txt
    caption_telegram.txt
    manual_publication_checklist.txt
    metadata.json
    manifest.json
```

## 9.7. Where export_directory Appears

The `export_directory` line in smoke loop output contains the absolute path to
the export package directory. Capture this path — it is needed for subsequent
inspect and validate steps.

## 9.8. What Failure Means

If the smoke loop fails (non-zero exit or Python traceback):

- The Foundation MVP lifecycle is broken.
- Check the error message — it will indicate which service/step failed.
- Common causes: missing project config, invalid `project_id`, missing brand
  fields, disallowed status transition attempt.
- Fix the underlying issue and rerun. Each rerun creates new entities.
- A failed smoke loop is not idempotent — previous partial entity data may
  remain in `storage/smoke_projects/`. Manual cleanup may be needed for clean
  state.

## 9.9. Important Limitations

- Smoke loop creates new entities every run. Not idempotent.
- Publication URL is placeholder (`https://example.invalid/...`). Not a real
  published URL.
- Only `text_social_post` content format. No other formats.
- Single target platform per run (first platform from scenario target_platforms,
  typically `telegram`).

## 9.10. JSON Output Mode

Use `--json` for machine-readable output:

```bash
python scripts/smoke_loop.py --json
```

JSON success output contains entity IDs, `export_directory`, `generated_export_files`
(array), and `entity_statuses` (object). All side effects are identical to human
mode — the same lifecycle executes, the same artifacts are created.

`--json --help` / `--help --json` prints human-readable USAGE, exits 0, and
does NOT create runtime artifacts. Help mode always takes priority.

---

# 10. Inspecting Export Package

## 10.1. Purpose

`inspect_package.py` reads and displays the contents of an ExportPackage
directory. It validates that `manifest.json` exists, is parseable JSON
and has the correct structure.

## 10.2. Command

```bash
python scripts/inspect_package.py <export_package_directory>
```

## 10.3. Input

| Input | Source | Required |
|-------|--------|----------|
| `export_package_directory` | CLI argument (positional) | Yes |

The directory must contain a `manifest.json` file.

## 10.4. Expected Output (Success)

```text
package_id=export_xxxxxxxxxxxx
project_id=example
content_item_id=content_xxxxxxxxxxxx
scenario_id=scenario_xxxxxxxxxxxx
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

## 10.5. Exit Behaviour

| Exit Code | Condition |
|-----------|-----------|
| 0 | Manifest read and displayed successfully |
| 1 | Missing argument, directory not found, manifest missing, invalid JSON, missing required fields, absolute file paths in manifest |

Errors are printed to stderr with `ERROR: ` prefix.

## 10.6. Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `export package directory does not exist` | Wrong path or directory deleted | Verify path from smoke loop output |
| `manifest.json not found` | Directory is not an export package | Ensure path points to the exports/{id}/ directory |
| `manifest.json is not valid JSON` | Corrupted manifest | Rerun smoke loop to regenerate |
| `manifest.json is missing required fields: ...` | Manifest structure changed | Rerun with current PublishingService |
| `must not be an absolute path` | Manifest file entry is absolute path | Rerun smoke loop — this should never happen |

## 10.7. What Inspect Does and Does Not Do

| Does | Does NOT |
|------|----------|
| Reads manifest.json | Check if files listed in manifest actually exist on disk |
| Validates manifest structure | Validate content quality |
| Displays human-readable summary | Check brand compliance |
| Returns success/failure via exit code | Modify any files |

For file-existence validation, use `validate_package.py`.

## 10.8. JSON Output Mode

Use `--json` for machine-readable output:

```bash
python scripts/inspect_package.py --json <export_package_directory>
python scripts/inspect_package.py <export_package_directory> --json
```

JSON success output includes `package_id`, `project_id`, `files` array, and other
manifest metadata. JSON errors are written to stdout with `status: "error"`.

---

# 11. Validating Export Package

## 11.1. Purpose

`validate_package.py` performs structural validation of an ExportPackage. It
verifies:
- `manifest.json` exists, is valid JSON and has correct structure
- All required files exist on disk
- All files listed in manifest exist on disk
- `metadata.json` exists and is valid JSON
- `manual_publication_only` is `true`
- Package `status` is `"ready"`

## 11.2. Command

```bash
python scripts/validate_package.py <export_package_directory>
```

## 11.3. Required Files

The following files must be present in the export package directory:

| File | Role |
|------|------|
| `title.txt` | Content title |
| `body.txt` | Content body |
| `caption_{platform}.txt` | Platform-specific caption (e.g., `caption_telegram.txt`) |
| `manual_publication_checklist.txt` | Step-by-step manual publishing guide |
| `metadata.json` | Export metadata |
| `manifest.json` | File listing with roles |

The `{platform}` in caption filename is derived from `manifest.json` field
`target_platform`.

## 11.4. Expected Output (Success)

```text
validation_status=ok
package_id=export_xxxxxxxxxxxx
project_id=example
target_platform=telegram
files_checked=6
ready_for_manual_publication=true
```

## 11.5. Exit Behaviour

| Exit Code | Condition |
|-----------|-----------|
| 0 | All validation checks passed |
| 1 | Any validation check failed |

Errors printed to stderr with `ERROR: ` prefix.

## 11.6. Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `export package directory does not exist` | Wrong path | Verify path |
| `manifest.json not found` | Not a valid export dir | Verify path points to correct directory |
| `metadata.json not found` | Package is incomplete | Rerun smoke loop |
| `manual_publication_checklist.txt not found` | Package is incomplete | Rerun smoke loop |
| `expected package file not found: caption_telegram.txt` | Missing caption file | Rerun smoke loop |
| `manifest.json field 'status' must be one of: ready` | ExportPackage not ready | Rerun prepare_export or smoke loop |
| `manifest.json field 'manual_publication_only' must be true` | Wrong publication mode | Rerun smoke loop — should never happen |
| `package file listed in manifest.json is missing on disk: ...` | Manifest-disk mismatch | Rerun smoke loop |

## 11.7. Structural vs Content Validation

```
Structural validation (validate_package.py):
    ✓ Are all required files present?
    ✓ Is manifest.json valid?
    ✓ Is metadata.json valid JSON?
    ✓ Is manual_publication_only = true?
    ✓ Is status = ready?
    ✓ Do manifest file references match disk?

Content quality (NOT checked by validate_package.py):
    ✗ Is the caption well-written?
    ✗ Does content match brand voice?
    ✗ Is the body within platform character limits?
    ✗ Are hashtags appropriate?
```

Validation here means **structural package readiness** — not content quality
or brand compliance.

## 11.8. JSON Output Mode

Use `--json` for machine-readable output:

```bash
python scripts/validate_package.py --json <export_package_directory>
python scripts/validate_package.py <export_package_directory> --json
```

JSON success output includes `validation_status`, `package_id`, `files_checked`
(number), and `ready_for_manual_publication` (boolean). JSON errors are written
to stdout with `status: "error"`.

---

# 12. Manual Publication Procedure

## 12.1. Current Reality

In the Foundation MVP, publication is **manual only**. LOOPRA prepares the
content in an export package. A human publishes it on the external platform.

## 12.2. Manual Publication Workflow

```
1. OPEN EXPORT PACKAGE
   Open the export_directory path from smoke loop output in file explorer.

2. READ CHECKLIST
   Open manual_publication_checklist.txt for step-by-step instructions.

3. READ CONTENT
   Open title.txt, body.txt and caption_{platform}.txt.

4. PUBLISH ON PLATFORM
   Open the target platform (e.g., Telegram channel).
   Copy the caption from caption_{platform}.txt.
   Paste into the platform's post editor.
   Publish the post.

5. COPY PUBLICATION URL
   After publishing, copy the resulting URL from the platform.
   (e.g., https://t.me/yourchannel/42)

6. RECORD URL FOR METRIC IMPORT
   Save the URL — it will be needed when importing metrics.
```

## 12.3. Smoke Loop vs Real Publication

| Aspect | Smoke Loop | Real Operator Workflow |
|--------|-----------|----------------------|
| Publication URL | `https://example.invalid/...` (placeholder) | Real platform URL copied by human |
| Publishing action | `PublishingService.publish_content()` records placeholder | Human publishes on external platform |
| Publication status | `PUBLISHED` (simulated) | Human marks as published via manual workflow |

The smoke loop simulates publication for testing the lifecycle chain. In real
operation, the human publishes externally, then records the real URL.

## 12.4. Current Limitations

- No autoposting — LOOPRA cannot publish to any platform automatically.
- `publish_content()` in PublishingService records publication metadata but does
  not make external API calls.
- The export package is a preparation tool, not a publishing automation tool.
- `manual_publication_checklist.txt` provides instructions for the human, not for
  an automated system.

---

# 13. Finding Metric Snapshots

## 13.1. Purpose

`find_metric_snapshots.py` discovers MetricSnapshot records in DRAFT status
that are ready for manual metric import.

## 13.2. Command

```bash
python scripts/find_metric_snapshots.py <project_id>
```

## 13.3. Environment Variable

| Env Var | Purpose |
|---------|---------|
| `LOOPRA_PROJECTS_ROOT` | Override projects root. Set to `storage/smoke_projects` if snapshots were created by smoke loop. (Legacy: `CONTENT_PLANT_PROJECTS_ROOT`) |

Default is `{REPO_ROOT}/projects` — but smoke loop writes to
`storage/smoke_projects/`. You typically need to override this.

## 13.4. Full Command with Env Var

```bash
$env:LOOPRA_PROJECTS_ROOT="storage/smoke_projects"; python scripts/find_metric_snapshots.py example
```

## 13.5. Expected Output

```text
metric_snapshots_found=1
project_id=example
snapshots:
- metric_snapshot_id=metric_xxxxxxxxxxxx publication_id=publication_xxxxxxxxxxxx content_item_id=content_xxxxxxxxxxxx platform=telegram status=draft
```

## 13.6. DRAFT-Only Behaviour

The script **only lists snapshots with `status=draft`**. Once a snapshot is
recorded (`RECORDED` status), it no longer appears in the output. This is
intentional — only DRAFT snapshots can accept metric imports.

## 13.7. Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Project config not found` | Wrong `project_id` or wrong `LOOPRA_PROJECTS_ROOT` | Verify project_id and env var |
| `metric snapshots found=0` | No DRAFT snapshots exist | Run smoke loop to create new ones |
| `metric snapshot storage is not a directory` | Corrupted storage | Check filesystem |
| `stored snapshot JSON is not valid JSON` | Corrupted snapshot file | Remove corrupted file or rerun smoke loop |

## 13.8. JSON Output Mode

Use `--json` for machine-readable output:

```bash
python scripts/find_metric_snapshots.py --json <project_id>
python scripts/find_metric_snapshots.py <project_id> --json
```

JSON output includes `metric_snapshots_found` (number) and `snapshots` (array).
Zero snapshots is still success (exit 0) with `snapshots: []`.

---

# 14. Importing Manual Metrics

## 14.1. Purpose

`import_manual_metrics.py` imports manually collected performance metrics
into a draft MetricSnapshot. This transitions the snapshot from DRAFT to
RECORDED.

## 14.2. Command

```bash
python scripts/import_manual_metrics.py <manual_metrics_json>
```

## 14.3. Environment Variable

| Env Var | Purpose |
|---------|---------|
| `LOOPRA_PROJECTS_ROOT` | Override projects root. Set to `storage/smoke_projects` if snapshot was created by smoke loop. (Legacy: `CONTENT_PLANT_PROJECTS_ROOT`) |

## 14.4. Input JSON Format

The input JSON file must contain:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | Yes | Project identifier |
| `metric_snapshot_id` | string | Yes | Snapshot ID from find_metric_snapshots.py |
| `metrics` | object | Yes | Non-empty object with supported keys |

### Supported Metric Keys

| Key | Type | Constraints | Stored As |
|-----|------|-------------|-----------|
| `views` | int | >= 0 | `content_metrics.views` |
| `likes` | int | >= 0 | `content_metrics.likes` |
| `comments` | int | >= 0 | `content_metrics.comments` |
| `shares` | int | >= 0 | `content_metrics.shares` |
| `saves` | int | >= 0 | `content_metrics.saves` |
| `clicks` | int | >= 0 | `content_metrics.link_clicks` |
| `published_url` | string | Non-empty | Updates `Publication.published_url` |

### Key Behaviours

- **`clicks` → `link_clicks` normalization:** The input key `clicks` is
  stored as `link_clicks` in the content metrics. This is automatic.
- **`published_url` is special:** It is not stored as a metric value inside
  the snapshot. Instead, it updates the related `Publication` record's
  `published_url` field. This updates the publication with the real URL from
  the external platform.
- **All numeric metrics are non-negative integers.** Floats, negative values,
  strings or null values are rejected.

## 14.5. Example Input JSON

```json
{
  "project_id": "example",
  "metric_snapshot_id": "metric_a1b2c3d4e5f6",
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

## 14.6. Full Command with Env Var

```bash
$env:LOOPRA_PROJECTS_ROOT="storage/smoke_projects"; python scripts/import_manual_metrics.py metrics.json
```

## 14.7. Expected Output (Success)

```text
metrics_import_status=ok
project_id=example
metric_snapshot_id=metric_a1b2c3d4e5f6
recorded_keys=views,likes,comments,shares,saves,clicks,published_url
```

The `recorded_keys` line shows which of the standard supported keys were
present in the input. Keys are listed in fixed order. Only keys actually
present in the input appear.

## 14.8. Post-Import State

After successful import:
- `MetricSnapshot` status transitions from `DRAFT` to `RECORDED`
- `Publication.published_url` is updated (if `published_url` was provided)
- Metric values are stored in `ContentPerformanceMetrics`
- The snapshot cannot accept another metrics import (RECORDED snapshots
  reject `record_metrics()`)

## 14.9. Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `manual metrics JSON file does not exist` | Wrong file path | Verify path to JSON file |
| `manual metrics JSON is not valid JSON` | Malformed JSON | Fix JSON syntax |
| `missing required fields: project_id` | Missing field | Add `project_id` to JSON |
| `missing required fields: metric_snapshot_id` | Missing field | Add `metric_snapshot_id` from find output |
| `missing required fields: metrics` | Missing field | Add `metrics` object |
| `metrics must not be empty` | Empty metrics object `{}` | Add at least one metric key |
| `Unknown metric keys: ...` | Unsupported key in metrics | Use only supported keys |
| `... must be an integer` | Non-integer value (float, string) | Use integer values |
| `... must be a non-negative integer` | Negative value | Use >= 0 values |
| `MetricSnapshot ... is not in DRAFT status` | Snapshot already RECORDED | Find another DRAFT snapshot or create new via smoke loop |
| `Project config not found` | Wrong project_id or env var | Verify project_id and LOOPRA_PROJECTS_ROOT |

## 14.10. BOM Handling

The script accepts UTF-8 BOM JSON files (common in PowerShell-generated
files). The `encoding="utf-8-sig"` parameter handles this automatically.

## 14.11. JSON Output Mode

Use `--json` for machine-readable output:

```bash
python scripts/import_manual_metrics.py --json <manual_metrics_json>
python scripts/import_manual_metrics.py <manual_metrics_json> --json
```

JSON success output includes `metrics_import_status`, `project_id`,
`metric_snapshot_id`, and `recorded_keys` (as a JSON array, not a
comma-separated string). Mutation behaviour is identical to human mode —
metrics go through `AnalyticsService.record_metrics()` with the same
DRAFT→RECORDED transition and `clicks`→`link_clicks` normalization.

---

# 15. Operational Troubleshooting

## 15.1. Troubleshooting Table

| Symptom | Likely Cause | Diagnostic Command | Fix | Safe Retry? |
|---------|-------------|-------------------|-----|-------------|
| `Project config not found` | Missing or wrong `project.yaml` in `projects/{project_id}/` | `ls projects/{project_id}/project.yaml` | Create or fix `project.yaml` | No — fix config first |
| `Invalid project_id` | ID contains uppercase, spaces, `..`, `/` or is empty | Check `project_id` against `^[a-z0-9][a-z0-9_-]*$` | Use valid lowercase ID | Yes |
| `project_id must not be empty` | Empty string or env var not set | Check env var value | Set valid project_id | Yes |
| Missing required project fields | Required fields missing in `project.yaml` | Compare `project.yaml` against `PROJECT_SETTINGS_SPEC.md` | Add missing fields | No |
| Missing required brand fields | `brand.name`, `brand.positioning` or `brand.audience_summary` empty | Check `project.yaml` brand section | Populate brand fields | No |
| Smoke loop fails with Python traceback | Service precondition not met | Read traceback for error class and message | Fix underlying issue; rerun smoke loop | Yes (creates new entities) |
| `export_package directory does not exist` | Wrong path or directory deleted | `ls <path>` | Verify path from smoke loop output | Yes |
| `manifest.json not found` | Wrong directory or incomplete package | `ls <export_dir>/ | Check directory contains manifest.json | Yes |
| `validate_package.py` fails | Missing required files in package | Run `inspect_package.py` first | Rerun smoke loop to regenerate package | Yes |
| `expected package file not found: caption_{platform}.txt` | Wrong platform or incomplete export | Check `target_platform` in manifest | Rerun smoke loop | Yes |
| `metadata.json is not valid JSON` | Corrupted metadata | `python -c "import json; json.load(open('<path>'))"` | Rerun smoke loop | Yes |
| `manual_publication_only must be true` | Manifest field is `false` | Check manifest in text editor | Should never happen in current MVP — rerun smoke loop | Yes |
| `status must be one of: ready` | Package not in READY state | Check manifest status field | Rerun prepare_export or smoke loop | Yes |
| `metric_snapshots_found=0` | No DRAFT snapshots or wrong `LOOPRA_PROJECTS_ROOT` | Verify env var; check `storage/smoke_projects/{project_id}/data/metric_snapshots/` | Run smoke loop to create new snapshots; set correct env var | Yes |
| `Unknown metric keys: ...` in metrics import | Unsupported key in JSON | Check keys against supported list | Remove unknown keys from JSON | Yes (fix JSON) |
| `MetricSnapshot ... is not in DRAFT status` | Snapshot already RECORDED | Run `find_metric_snapshots.py` for a DRAFT snapshot | Use a DRAFT snapshot; create new via smoke loop | Yes (use DRAFT) |
| `stored snapshot JSON is not valid JSON` | Corrupted snapshot file | Inspect file in `data/metric_snapshots/` | Remove corrupted file; rerun smoke loop | Yes (after cleanup) |
| `cannot find publication` | Publication JSON deleted or corrupted | Check `data/publications/{id}.json` | Rerun smoke loop | Yes |
| Permission / path issue | Filesystem access denied | Check file/directory permissions | Fix filesystem permissions | No |
| `Usage: python scripts/...` (missing arg) | Script invoked without required argument | Check script usage in this runbook | Provide required argument | Yes |
| Too many arguments | Extra arguments provided | Check command syntax | Remove extra arguments | Yes |

## 15.2. Error Severity Classification

| Severity | Meaning | Response |
|----------|---------|----------|
| **Blocking** | Cannot proceed without fix | Fix the underlying issue; safety check before retry |
| **Warning** | Operation may proceed but result may be suboptimal | Note the warning; proceed with caution; investigate later |
| **Info** | Expected informational message | No action needed |

---

# 16. Safe Retry Rules

## 16.1. What Is Safe to Rerun

| Operation | Safe to Rerun? | Notes |
|-----------|---------------|-------|
| Tests (any) | Yes | Read-only; no side effects between runs |
| `smoke_loop.py` | Yes | Creates new entities every run; old artifacts remain (not overwritten) |
| `inspect_package.py` | Yes | Read-only |
| `validate_package.py` | Yes | Read-only |
| `find_metric_snapshots.py` | Yes | Read-only |
| `import_manual_metrics.py` | **Conditional** | Not idempotent. Each successful run transitions DRAFT → RECORDED. Cannot record twice on the same snapshot. |

## 16.2. Rules

1. **All tests are safe to rerun.** They use temporary directories and do not
   modify source files.
2. **Smoke loop creates new entities.** Each run produces new IDs. Previous
   runs' artifacts are not affected.
3. **Inspect and validate are read-only.** No risk of repeated execution.
4. **Find metric snapshots is read-only.** Lists DRAFT snapshots without
   modifying them.
5. **Import manual metrics is NOT idempotent.** Once a snapshot transitions
   from DRAFT to RECORDED, it cannot accept another import. Do NOT run
   `import_manual_metrics.py` twice on the same snapshot.
6. **If a retry fails,** check that prerequisites are still met (entity states,
   file existence, permissions).

---

# 17. Generated Artifacts and Cleanup

## 17.1. What Is Generated

The smoke loop generates runtime artifacts under `storage/smoke_projects/`:

```
storage/smoke_projects/{project_id}/
    project.yaml                          — copy of source config
    data/
        ideas/*.json
        scenarios/*.json
        content_items/*.json
        export_packages/*.json
        publications/*.json
        metric_snapshots/*.json
    exports/{export_package_id}/
        title.txt, body.txt, caption_*.txt, ...
```

## 17.2. Accumulation

- Each smoke loop run creates new entities with new IDs.
- Old artifacts are NOT automatically cleaned up.
- Over time, `storage/smoke_projects/` will accumulate data from past runs.

## 17.3. Cleanup

| Action | Status |
|--------|--------|
| Automated cleanup tool | Not implemented (future/conceptual) |
| Manual cleanup | Allowed — `storage/` is gitignored and safe to delete |
| Partial cleanup | Can delete individual entity JSON files or entire export dirs |

**Manual cleanup command (PowerShell):**

```powershell
Remove-Item -Recurse -Force storage/smoke_projects
```

After deletion, the next smoke loop run will recreate the directory and all
artifacts.

## 17.4. What NOT to Delete

| Directory | Why |
|-----------|-----|
| `projects/{project_id}/project.yaml` | Source config — required for operation |
| `core/` | Platform code |
| `scripts/` | CLI tools |
| `tests/` | Verification suite |
| `docs/` | Architecture and operations source of truth |
| `storage/.gitkeep` | Keeps the directory in version control |

---

# 18. Git Hygiene During Operations

## 18.1. Before Operations

```bash
git status --short
```

- Verify which files are modified.
- Know what changes are expected (docs, code, configs).
- Ensure no unexpected files are staged.

## 18.2. After Operations

```bash
git status --short
```

### Expected (OK to see):
- Modified files in `docs/`, `core/`, `scripts/`, `tests/`
- Modified `projects/{project_id}/project.yaml` (if intentionally edited)
- New files in `docs/` (documentation additions)

### Unexpected (NOT OK to see):
- Files under `storage/smoke_projects/` — should be gitignored
- Files under `graphify-out/` — should be gitignored
- `.env` files — should be gitignored
- `__pycache__/` or `*.pyc` — should be gitignored
- Project-specific files leaking into core (e.g., `core/.../nura/`)

## 18.3. Commit Rules

| File Type | Commit? | Reason |
|-----------|---------|--------|
| `core/` | Yes | Platform code |
| `scripts/` | Yes | Platform tools |
| `tests/` | Yes | Verification |
| `docs/` | Yes | Architecture and operations source of truth |
| `projects/{id}/project.yaml` | Yes (if intentional) | Source configuration |
| `docs/07_projects/` | Yes | Project documentation |
| `storage/*` | **No** | Runtime artifacts — gitignored |
| `graphify-out/` | **No** | Generated output — gitignored |
| `.env` or secrets | **Never** | Security |
| `__pycache__/`, `*.pyc` | **No** | Build artifacts |

## 18.4. If Runtime Artifacts Appear in git status

This means `.gitignore` is not working correctly or the artifacts are outside
the excluded paths. Check:

1. Files are under `storage/smoke_projects/` (not under `projects/` or `core/`).
2. `.gitignore` entry `storage/*` is present.
3. Verify with `git check-ignore storage/smoke_projects/example/data`.

---

# 19. Documentation Update Rules

## 19.1. When to Update Docs

| Change Type | Docs to Update |
|-------------|---------------|
| Architecture changes | Relevant `docs/02_architecture/` specs + `STATE.md` + `AGENTS.md` |
| Code changes affecting services | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` |
| Code changes affecting runtime | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` |
| Code changes affecting tools/CLI | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` |
| Code changes affecting storage | `docs/05_platform/STORAGE_AND_STATE_SPEC.md` |
| Code changes affecting config/env | `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` |
| Code changes affecting security | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` |
| Operations procedure changes | `docs/06_operations/OPERATIONAL_RUNBOOK.md` |
| New scripts added | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` + this runbook |
| Project config changes | `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` |

## 19.2. When Tests Are Needed

- Architecture changes: tests must pass before docs are updated.
- Code changes: tests must pass after code change.
- Documentation-only changes: tests may be optional unless code/path references
  are affected.
- Runbook updates: no tests needed unless the runbook describes new testable
  behaviour.

## 19.3. Tie to AGENTS.md

Per `AGENTS.md` Section 8:
> When changing architecture: Update the relevant source-of-truth document.
> Avoid duplicate specifications, conflicting documents, outdated active
> instructions.

---

# 20. Common Operational Reports

## 20.1. Documentation Task Report Template

```text
DOCUMENTATION TASK REPORT
=========================
File created/changed: docs/06_operations/OPERATIONAL_RUNBOOK.md
Sections: [list sections]
Scope: operations documentation
Other files changed: [list or "none"]
Tests run: [list or "not run"]
Reason if not run: documentation-only change, no code affected
Architectural impact: none — documentation layer only
Remaining risks: [list or "none"]
```

## 20.2. Code Change Report Template

```text
CODE CHANGE REPORT
==================
Files changed:
  - core/services/publishing.py (added field validation)
  - tests/services/test_loop_engineering.py (added test for validation)

Tests run:
  - python -m unittest tests.services.test_loop_engineering
  - Result: all tests passed

Smoke loop status:
  - python scripts/smoke_loop.py
  - Result: all entities created, all statuses correct

Artifacts generated:
  - storage/smoke_projects/example/data/ (entity JSON files)
  - storage/smoke_projects/example/exports/ (export package files)

Git status:
  - Only intended code files modified
  - No runtime artifacts staged
```

## 20.3. Operational Acceptance Report Template

```text
OPERATIONAL ACCEPTANCE REPORT
=============================
Date: [date]
Operator: [name/role]

1. TESTS
   Domain tests:    python -m unittest discover -s tests/domain    → [PASS/FAIL]
   Service tests:   python -m unittest discover -s tests/services  → [PASS/FAIL]
   All tests:       python -m unittest discover -s tests           → [PASS/FAIL]

2. SMOKE LOOP
   Command:         python scripts/smoke_loop.py                   → [PASS/FAIL]
   Export directory: [path]
   All entity statuses: [list or "all correct"]

3. EXPORT INSPECTION
   Command:         python scripts/inspect_package.py <dir>        → [PASS/FAIL]

4. EXPORT VALIDATION
   Command:         python scripts/validate_package.py <dir>       → [PASS/FAIL]
   Files checked:   6

5. METRIC SNAPSHOTS
   Command:         python scripts/find_metric_snapshots.py example → [N found]
   DRAFT snapshots available: [count]

6. MANUAL METRICS
   Import status:   [PASS/FAIL/NOT RUN]
   Recorded keys:   [list]

7. FINAL GIT STATUS
   Command:         git status --short
   Result:          [clean / expected changes only]

FINAL STATE: [OPERATIONAL / DEGRADED / BROKEN]
```

---

# 21. Current Non-Operational Areas

The following capabilities are **not operational** in the current Foundation MVP.
Do not attempt to run, invoke or depend on them:

| Area | Status | Notes |
|------|--------|-------|
| API server | Not implemented | No HTTP endpoints exist |
| UI / Frontend | Not implemented | No web or desktop interface |
| Database / Migrations | Not implemented | Filesystem JSON only |
| External connectors | Not implemented | No platform API integrations |
| Autoposting | Not implemented | Manual publication only |
| Asset library service | Not implemented | No media asset management |
| Media rendering | Not implemented | `text_social_post` format only |
| Learning Memory runtime | Not implemented | Stub methods return empty lists |
| Scheduler / workers | Not implemented | No background jobs |
| User authentication | Not implemented | No users, roles or sessions |
| CI / CD pipeline | Not implemented | Local manual execution only |
| Production deployment | Not implemented | Development workstation only |
| Feature flags | Not implemented | Fixed MVP capability set |
| Orchestrator Agent | Not implemented | Human-only decision making |

All are marked **future/conceptual** and belong to later LOOPRA evolution phases.

---

# 22. Safety Rules During Operations

## 22.1. Golden Rules

1. **No direct entity JSON editing.** Use services via scripts to mutate domain
   entities. Emergency/manual debug edits require an explicit note and reason.
2. **No direct storage mutation outside services.** Agents and tools must route
   mutations through services. Read-only inspection of storage files is
   acceptable for debugging.
3. **No secrets in project.yaml.** Project configuration is plaintext and
   potentially committed. Never store API keys, tokens or credentials.
4. **No external API calls.** The current system has no connectors. Do not
   add HTTP calls, platform integrations or API dependencies.
5. **No autoposting.** Every publication action requires human involvement.
   Do not automate posting to external platforms.
6. **No destructive cleanup without confirmation.** Deleting runtime artifacts
   is allowed but should be intentional. Do not delete source directories.
7. **No cross-project path usage.** Every operation is scoped to one
   `project_id`. Do not access or modify another project's data.
8. **Use env vars carefully.** LOOPRA_PROJECTS_ROOT (or the legacy
   `CONTENT_PLANT_PROJECTS_ROOT`) affects which
   directory metric tools read from. Misconfiguration leads to "not found"
   errors.
9. **Do not commit runtime artifacts.** `storage/*` is gitignored. Verify
   `git status` before committing.
10. **Do not skip validation.** Package validation and test execution are the
    only guarantees of operational correctness.

## 22.2. Dangerous Actions (Never Without Confirmation)

- Deleting `projects/{project_id}/project.yaml`
- Deleting or modifying `core/` files
- Modifying `.gitignore` entries
- Direct JSON mutations on entity files
- Adding external dependencies or network calls

---

# 23. Operator Decision Checklist

Before running any operation or making any change, the operator should answer:

| Question | Why |
|----------|-----|
| **What `project_id`?** | Every operation is project-scoped. Use "example" for smoke tests. |
| **Source or runtime root?** | Source = `projects/`; Runtime = `storage/smoke_projects/`. Know which you need. |
| **Is this read-only or mutating?** | Inspect/validate/find are read-only. Smoke loop and metrics import mutate. |
| **Is publication manual or simulated?** | Smoke loop simulates with placeholder URL. Real publication is manual. |
| **Are metrics being recorded into DRAFT snapshot?** | Metrics only go into DRAFT snapshots. RECORDED snapshots cannot accept imports. |
| **Are only intended files changing?** | Check `git status` before and after. |
| **Is any future-only capability being assumed?** | No API, UI, DB, autoposting, connectors, or agents exist. |
| **Is env var LOOPRA_PROJECTS_ROOT set correctly?** | For metric tools after smoke loop, point to `storage/smoke_projects`. (Legacy `CONTENT_PLANT_PROJECTS_ROOT` also accepted.) |

---

# 24. Current Operational Limitations

These are honest acknowledgements of what the current MVP does not support:

| Limitation | Impact |
|-----------|--------|
| Local only | System runs on a single workstation; no network deployment |
| No CI | Tests must be run manually; no automated verification |
| No production deployment | All operations are development/smoke mode |
| No runtime audit log | No persisted record of who did what and when |
| No retry/resume | Failed smoke loop requires full restart from beginning |
| No cleanup tool | Smoke artifacts accumulate; manual cleanup only |
| No database | JSON files are the only persistence |
| No API / UI | CLI and Python imports are the only interfaces |
| No connectors | No external platform integration |
| No background jobs | No scheduled or triggered autonomous execution |
| No auth / users / roles | Single-user, no access control |
| No concurrent execution protection | Two simultaneous script runs could conflict |
| No artifact versioning | Overwriting is possible; no history |
| No entity relationship queries | Each entity is loaded individually |
| No metric aggregation or trends | AnalyticsService stubs only |
| Only `text_social_post` format | No carousel, video, image or multi-format support |
| Historical `CONTENT_PLANT_*` env var names | Legacy fallback names; `LOOPRA_*` is now primary (see Section 6.1) |

---

# 25. Future Operations Runbooks

These are conceptual runbooks needed for future LOOPRA evolution phases.
They are NOT to be created now — they are placeholders for the architecture
roadmap.

| Future Runbook | Purpose | Relevant Phase |
|---------------|---------|---------------|
| Deployment Runbook | Production deployment, server setup, health checks | SaaS Platform |
| Connector Operations Runbook | Platform connector management, auth, rate limiting | Production Automation |
| Incident Response Runbook | Production incident detection, triage, recovery | SaaS Platform |
| Agent Operations Runbook | Agent lifecycle management, safety boundaries, escalation | Agentic Operations |
| Backup/Restore Runbook | Data backup schedules, restore procedures, retention | SaaS Platform |
| Data Migration Runbook | Schema migrations, storage migrations, data portability | SaaS Platform |
| SaaS Operations Runbook | Multi-tenant operations, billing, user management | SaaS Platform |
| Security Operations Runbook | Secret rotation, access reviews, vulnerability response | SaaS Platform |
| Media Asset Operations Runbook | Asset library management, media processing | Production Automation |
| CI/CD Operations Runbook | Pipeline setup, test automation, quality gates | Production Automation |

**Status:** All future/conceptual. Do not implement.

---

# 26. Related Documents

## 26.1. Source of Truth Documents

| Document | Path | Relevance |
|----------|------|-----------|
| AGENTS.md | `AGENTS.md` | Development rules and boundaries |
| STATE.md | `STATE.md` | Current project state and phase |
| Data Model | `docs/00_foundation/DATA_MODEL.md` | Foundation entity chain |
| Project Settings Spec | `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` | Project configuration |
| Pipelines Spec | `docs/02_architecture/PIPELINES_SPEC.md` | Foundation MVP pipeline |
| Distribution Spec | `docs/04_production/DISTRIBUTION_SPEC.md` | Publication and export |
| Analytics Spec | `docs/04_production/ANALYTICS_SPEC.md` | Metrics and snapshots |

## 26.2. Platform Specifications

| Document | Path | Relevance |
|----------|------|-----------|
| Runtime Orchestration Spec | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` | Execution coordination |
| Service Contracts Spec | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` | Service operations |
| Tooling and CLI Spec | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` | CLI tools |
| Storage and State Spec | `docs/05_platform/STORAGE_AND_STATE_SPEC.md` | Persistence model |
| Configuration and Environment Spec | `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | Config and env vars |
| Testing and Validation Spec | `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` | Test framework and coverage |
| Security and Safety Boundaries Spec | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` | Safety rules |

---

# 27. Code References

## 27.1. Scripts (CLI Entrypoints)

| File | Purpose |
|------|---------|
| `scripts/smoke_loop.py` | End-to-end Foundation MVP lifecycle smoke test |
| `scripts/inspect_package.py` | Read and display ExportPackage contents |
| `scripts/validate_package.py` | Validate ExportPackage structure |
| `scripts/find_metric_snapshots.py` | List DRAFT MetricSnapshot records |
| `scripts/import_manual_metrics.py` | Import manual metrics into DRAFT snapshot |

All scripts support `--help` / `-h` for usage information.

| Flag | Purpose | Example |
|------|---------|---------|
| `--help` | Show usage and exit. Supported on all 5 scripts. | `python scripts/smoke_loop.py --help` |

## 27.2. Core Services

| File | Purpose |
|------|---------|
| `core/services/loop.py` | LoopOrchestrator |
| `core/services/projects.py` | ProjectService, BrandProfileService, FileSystemProjectRepository |
| `core/services/ideas.py` | IdeaService, ScenarioService, Idea and Scenario repositories |
| `core/services/production.py` | ProductionLifecycleService, ContentItem repository |
| `core/services/publishing.py` | PublishingService, ExportPackage and Publication repositories |
| `core/services/analytics.py` | AnalyticsService, MetricSnapshot repository |
| `core/services/_storage.py` | Base repository class |

## 27.3. Core Domain and Config

| File | Purpose |
|------|---------|
| `core/domain/models.py` | Domain entities |
| `core/domain/enums.py` | Status enums |
| `core/domain/transitions.py` | Status transition rules |
| `core/projects/loader.py` | Project config loading, validation, path safety |

## 27.4. Tests

| Path | Purpose |
|------|---------|
| `tests/domain/test_models.py` | Domain model tests |
| `tests/domain/test_transitions.py` | Transition rule tests |
| `tests/services/` | All service and tool tests |

## 27.5. Git

| File | Purpose |
|------|---------|
| `.gitignore` | Source/runtime artifact separation |

---

# 28. Document Status

| Field | Value |
|-------|-------|
| **Status** | Active — LOOPRA Operations Layer |
| **Version** | v1.0 |
| **Date** | 2026-07-09 |
| **Project** | LOOPRA — Autonomous Marketing Operating System |
| **Layer** | Operations Layer — Operational Runbook |

---

# Final Statement

This Operational Runbook describes how to operate the current LOOPRA
Foundation MVP — not a future SaaS platform. Every command, script,
environment variable and workflow documented here exists and has been
verified against the actual codebase.

The Foundation MVP chain — Project → Idea → Scenario → ContentItem →
ExportPackage → Publication → MetricSnapshot — is the operational backbone.
The smoke loop, inspection tools, validation tools and metric import tools
provide the operational interface.

**Human decides. Scripts execute. Services mutate state. Tools inspect and
validate. No autoposting.**

Operate within these boundaries. Do not assume future capabilities. Verify
before concluding.

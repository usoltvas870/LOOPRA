# RELEASE AND CHANGE MANAGEMENT

## Version

v1.0

## Status

Active — LOOPRA Operations Layer

## Purpose

This document defines the practical governance framework for safely managing
changes to LOOPRA documentation, code, services, runtime, tools, storage,
configuration and future architecture. It answers the central question:

> How should LOOPRA safely accept changes in documentation, code, services,
> runtime, tools, storage, config and future architecture so that the
> Foundation MVP chain is preserved and current/future capabilities are
> never mixed?

This document is the release and change discipline layer for the current
Foundation MVP and future platform evolution. It does not assume CI/CD,
production deployment or release automation — none of which exist in the
current system.

---

## 1. Purpose and Scope

### 1.1. In Scope

- Documentation changes
- Code changes (domain, services, scripts, tools)
- Test changes
- Service/runtime/tool changes
- Storage/config/security changes
- Architecture changes
- Operational acceptance definition
- Report templates and requirements
- STATE.md update rules
- AGENTS.md update rules
- Git hygiene rules
- Commit and push policy
- Rollback/revert principles
- Future CI/CD and release management path

### 1.2. Out of Scope

- Production deployment
- CI/CD implementation
- Release automation
- SaaS release process
- API/UI rollout
- Database migrations
- Connector releases
- External integration release process
- Branch strategy definition (none currently defined beyond main)
- Release tagging policy (not currently in use)
- Automated doc validation
- Secret scanning

---

## 2. Current Release Reality

### 2.1. Honest Current State

LOOPRA has **no formal production release process**. There is no production
environment, no deployment pipeline, no CI, no release tags, no automated
verification.

The current release/change process is entirely local and manual:

| Step | Actor | Action |
|------|-------|--------|
| 1 | Human | Defines the change goal. |
| 2 | ChatGPT | Prepares a scoped prompt with required reading, task bounds and forbidden actions. |
| 3 | Codex | Executes the change — creates docs, edits code, runs tests, produces report. |
| 4 | Codex | Runs required tests and the smoke loop for code/service changes. |
| 5 | Codex | Produces final report with files changed, tests run, architectural impact and risks. |
| 6 | Human | Reviews the report and decides commit/push. |
| 7 | Human | Commits and pushes if approved. |

### 2.2. What Does Not Exist

| Capability | Status |
|------------|--------|
| CI pipeline | Not implemented |
| Automated test gate | Not implemented |
| Release tagging | Not implemented |
| Deployment pipeline | Not implemented |
| Production environment | Does not exist |
| Staging environment | Does not exist |
| Automated rollback | Not implemented |
| Branch protection | Not configured |
| Code review automation | Not implemented |
| Doc consistency checks | Not automated |
| Secret scanning | Not implemented |
| Artifact scanning | Not implemented |

### 2.3. Current Verification Tools

The only verification mechanisms are:

| Tool | What It Verifies |
|------|-----------------|
| `python -m unittest discover -s tests/domain` | Domain models and transition rules |
| `python -m unittest discover -s tests/services` | Services, tools and lifecycle |
| `python -m unittest discover -s tests` | Full test suite |
| `python scripts/smoke_loop.py` | End-to-end Foundation MVP chain |
| `python scripts/inspect_package.py <dir>` | Export package readability |
| `python scripts/validate_package.py <dir>` | Export package structural validity |
| `git status --short` | File change inventory |
| `git diff --stat` | Change summary |
| `git diff -- <file>` | Detailed line-level diff |

---

## 3. Change Management Principles

All LOOPRA changes must follow these principles:

1. **Change one bounded scope at a time.** Do not mix documentation, code
   and architecture changes in one unmanageable batch.

2. **Preserve the Foundation MVP chain.** Every change must be verifiable
   against: Project → Idea → Scenario → ContentItem → ExportPackage →
   Publication → MetricSnapshot.

3. **Current behaviour must be grounded in code.** Documentation describes
   what code actually does, not what it might do later.

4. **Future capability must be marked future/conceptual.** Never describe
   a planned feature as if it already exists.

5. **Tests are mandatory for code changes.** No code change may be considered
   complete without relevant tests passing.

6. **Documentation must follow code/architecture changes.** When a change
   alters behaviour, update the relevant source-of-truth document.

7. **No forbidden scope expansion.** Do not add API, UI, DB, external
   integrations, autoposting or autonomous agents without explicit
   architectural approval.

8. **No unrelated files changed.** A change touches only files within its
   defined scope. No opportunistic cleanups, refactoring or additions.

9. **Human approves risky or structural changes.** Changes affecting domain
   models, services, runtime, storage, security or architecture require
   human review before commit.

10. **Git status must be clean or expected before completion.** No surprise
    files, no runtime artifacts, no unrelated modifications.

---

## 4. Change Types

### 4.1. Change Type Table

| Change Type | Risk Level | Tests Required | Docs Required | Approval Required |
|-------------|-----------|---------------|---------------|-------------------|
| Documentation-only change | Low | Not required (optional regression) | Source-of-truth docs if content changes materially | Human review |
| Architecture document change | Medium | Not required unless code paths referenced | Architecture doc + any downstream docs | Human + ChatGPT review |
| Foundation/domain model change | High | Full domain test suite | DATA_MODEL.md + transition docs if transitions change | Human approval required |
| Service contract change | Medium | Full service test suite + smoke loop | SERVICE_CONTRACTS_SPEC.md | Human approval required |
| Runtime orchestration change | Medium | Full service test suite + smoke loop | RUNTIME_ORCHESTRATION_SPEC.md | Human approval required |
| Tool/CLI change | Medium | Script-specific test(s) + smoke loop | TOOLING_AND_CLI_SPEC.md + OPERATIONAL_RUNBOOK.md | Human approval required |
| Storage/config change | High | Full test suite | STORAGE_AND_STATE_SPEC.md or CONFIGURATION_AND_ENVIRONMENT_SPEC.md | Human approval required |
| Security-sensitive change | High | Full test suite + manual review | SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md | Human approval required |
| Test-only change | Low | The changed tests themselves | Not required unless test philosophy changes | Human review |
| Project config change | Low | Not required unless services affected | PROJECT_SETTINGS_SPEC.md if schema changes | Human approval |
| Future feature implementation | N/A | Not allowed in current phase | N/A | Architectural approval required |
| Cleanup/refactor | Medium | Full test suite + smoke loop | Relevant spec if contracts change | Human approval |

### 4.2. Change Type Definitions

**Documentation-only change:** Creating, modifying, or deleting documentation
files under `docs/`. No code, no tests, no configuration changes.

**Architecture document change:** Modifying source-of-truth architecture
documents (LOOPRA_ARCHITECTURE.md, PIPELINES_SPEC.md, etc.).

**Foundation/domain model change:** Modifying files under `core/domain/` —
models, enums, or transition rules.

**Service contract change:** Modifying files under `core/services/` — service
behaviour, preconditions, postconditions, or errors.

**Runtime orchestration change:** Modifying `core/services/loop.py` or other
runtime coordination logic.

**Tool/CLI change:** Modifying files under `scripts/`.

**Storage/config change:** Modifying storage layout, repository logic,
configuration loading, or `.gitignore` storage rules.

**Security-sensitive change:** Any change affecting path safety, project
isolation, secret boundaries, or publication safety.

**Test-only change:** Adding, modifying, or removing test files. No production
code changes.

**Project config change:** Modifying `projects/{project_id}/project.yaml` or
project-specific documentation.

**Cleanup/refactor:** Non-functional changes to code structure, naming, or
formatting. No behaviour change.

---

## 5. Standard Change Lifecycle

### 5.1. Lifecycle Flow

```
1. IDENTIFY CHANGE GOAL
   Human defines what needs to change and why.

2. DETERMINE CHANGE TYPE
   Classify the change using the Change Type Table (Section 4).
   This determines tests, docs and approval required.

3. READ SOURCE-OF-TRUTH DOCS
   Agent reads AGENTS.md, STATE.md and all documents relevant to the
   change scope. See Section 6 for the pre-change checklist.

4. WRITE SCOPED PROMPT/TASK
   ChatGPT (or Human) writes a structured prompt with:
   - required reading
   - exact file(s) to change
   - forbidden actions
   - expected report format
   - current/future boundaries

5. EXECUTE CHANGE
   Codex performs the task within the defined scope.

6. RUN REQUIRED TESTS/CHECKS
   Tests per the Change Type Table (Section 4).
   Smoke loop for any code change affecting services or runtime.

7. REVIEW DIFF
   Verify only intended files changed:
   git status --short
   git diff --stat
   git diff -- <changed files>

8. UPDATE DOCS IF NEEDED
   Per the Documentation Update Matrix (Section 11).
   If service contracts, runtime, tools, storage, config or
   security behaviour changed, update the relevant spec.

9. UPDATE STATE.md IF MILESTONE
   Per the STATE.md Update Rules (Section 12).
   Only for major milestones, not every small change.

10. PRODUCE FINAL REPORT
    Using the template matching the change type (Section 19).
    Include: files changed, tests run, architectural impact, risks.

11. HUMAN APPROVES COMMIT/PUSH
    Human reviews the report and diff.
    Human confirms Foundation MVP chain preserved.
    Human decides to commit and push.

12. COMMIT/PUSH IF APPROVED
    Small coherent commit with descriptive message.
    Push only after human approval.
```

### 5.2. Decision Gates

| Gate | Owner | Question |
|------|-------|----------|
| Goal definition | Human | What needs to change and why? |
| Change classification | ChatGPT | What type of change is this? |
| Scope approval | ChatGPT + Human | Is this within Foundation MVP boundaries? |
| Execution boundary | Codex | Am I staying within the defined scope? |
| Tests verification | Codex | Did required tests pass? |
| Diff review | Human | Are only intended files changed? |
| Architecture verification | ChatGPT | Does the result match architecture? |
| Final approval | Human | Is this acceptable to commit and push? |

---

## 6. Pre-Change Checklist

### 6.1. Before Every Change

```
[ ] Current branch/status checked
    Command: git status --short
    → Verify no unexpected uncommitted files.

[ ] No unexpected uncommitted files
    → All files shown in git status must be expected.

[ ] Target files identified
    → Know exactly which files will be created or modified.

[ ] Forbidden areas clear
    → No change to: API, UI, DB, external integrations, autoposting.
    → No change outside defined scope.

[ ] Required docs read
    → AGENTS.md read.
    → STATE.md read.
    → All source-of-truth docs relevant to the change type read.

[ ] Test requirements known
    → Know which tests must pass: domain, services, full suite, smoke loop.
    → Know when tests may be optional (doc-only changes).

[ ] Rollback plan known (for code changes)
    → Know how to revert: git checkout -- <file> or git revert <commit>.
    → Know which tests to rerun after rollback.
```

### 6.2. Verification Command

```bash
git status --short
```

Expected output: known files only. No surprises. No runtime artifacts.

---

## 7. Documentation Change Rules

### 7.1. Documentation-Only Changes

Documentation-only changes:

- Normally do **not** require tests.
- Must **not** claim future features as current.
- Must update cross-document links and paths correctly if files are renamed
  or moved.
- Must **not** duplicate existing docs or create duplicate numbered folders.
- Must use **LOOPRA** as the active project name.
- Content Plant must be treated as historical/archive only.
- Must preserve layer boundaries — reference docs at the correct
  architectural layer.
- Must follow the style of existing documents in the same layer.

### 7.2. When Documentation Changes Require Tests

Documentation changes require tests only when:

- The doc references code paths or file locations that may have changed.
- The doc describes operational commands with specific expected output.
- The doc includes commands that must be verified.

In these cases, run the relevant smoke/inspect/validate command to confirm
accuracy before finalising the doc.

### 7.3. Documentation Change Verification

```bash
# Check no duplicate numbered folders were created
ls docs/

# Check no stale project names in active docs
grep -r "Content Plant" docs/ --include="*.md"

# Verify cross-document links resolve to existing files
ls <referenced_file_path>
```

---

## 8. Code Change Rules

### 8.1. All Code Changes

Every code change must:

- Have relevant tests pass (per the Change Type Table, Section 4).
- Potentially require the full test suite.
- Require the smoke loop if the change affects core services, runtime,
  domain models or tools.
- Require docs update if service contracts, runtime behaviour, tool
  interfaces, storage layout, config schema or security boundaries changed.
- Produce a final report with files changed, behaviour description,
  tests run, architectural impact and remaining risks.

### 8.2. Code Change Boundaries

No code change may:

- Bypass services and write domain entities directly.
- Break the Foundation MVP chain (Project → Idea → Scenario → ContentItem →
  ExportPackage → Publication → MetricSnapshot).
- Add API endpoints, UI components, database dependencies, external
  integrations or autoposting.
- Add project-specific logic into `core/`.
- Change `.gitignore` without documented justification.
- Delete source files (`core/`, `scripts/`, `tests/`, `projects/`) without
  explicit instruction.
- Change environment variable names or add new env vars without architectural
  approval.

### 8.3. Code Change Verification Commands

```bash
# Run domain tests
python -m unittest discover -s tests/domain

# Run service tests
python -m unittest discover -s tests/services

# Run full test suite (recommended for core/runtime/storage changes)
python -m unittest discover -s tests

# Run smoke loop for any service/runtime/tool change
python scripts/smoke_loop.py

# Inspect export package (capture export_directory from smoke loop output)
python scripts/inspect_package.py <export_directory>

# Validate export package
python scripts/validate_package.py <export_directory>
```

---

## 9. Test Requirements by Change Type

### 9.1. Test Requirements Matrix

| Change Type | Domain Tests | Service Tests | Full Suite | Smoke Loop | Package Validate | Metrics Workflow |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Documentation-only | — | — | — | — | — | — |
| Architecture doc change | Optional | Optional | Optional | Optional | Optional | Optional |
| Foundation/domain change | **Required** | **Required** | **Required** | **Required** | Recommended | Recommended |
| Service contract change | Recommended | **Required** | **Required** | **Required** | Recommended | Recommended |
| Runtime orchestration change | Recommended | **Required** | **Required** | **Required** | **Required** | Recommended |
| Tool/CLI change | Optional | **Required** | Recommended | **Required** | **Required** | Optional |
| Storage/config change | Recommended | **Required** | **Required** | **Required** | **Required** | Recommended |
| Security-sensitive change | **Required** | **Required** | **Required** | **Required** | **Required** | **Required** |
| Test-only change | Run changed tests | Run changed tests | Optional | Optional | Optional | Optional |
| Project config change | Optional | Optional | Optional | Recommended | Optional | Optional |
| Cleanup/refactor | **Required** | **Required** | **Required** | **Required** | Optional | Optional |

### 9.2. Test Commands Reference

```bash
# Domain tests — entity creation, required fields, transition rules
python -m unittest discover -s tests/domain

# Service tests — all service operations, tools, smoke loop, workflows
python -m unittest discover -s tests/services

# Full test suite — domain + services
python -m unittest discover -s tests

# Smoke loop — end-to-end Foundation MVP chain verification
python scripts/smoke_loop.py

# Export package inspection — readability, manifest structure
python scripts/inspect_package.py <export_directory>

# Export package validation — structural integrity, file existence
python scripts/validate_package.py <export_directory>

# Metric snapshot discovery — locate DRAFT snapshots
$env:CONTENT_PLANT_PROJECTS_ROOT="storage/smoke_projects"; python scripts/find_metric_snapshots.py example

# Manual metrics import — DRAFT → RECORDED transition
$env:CONTENT_PLANT_PROJECTS_ROOT="storage/smoke_projects"; python scripts/import_manual_metrics.py metrics.json
```

### 9.3. When Tests Are Optional

Tests may be skipped when:

- The change is documentation-only with no code path references.
- The change is a new standalone document.
- The change is a typo or formatting fix in a document.

When tests are not run, the final report must state: `NOT RUN` + the reason.

---

## 10. Operational Acceptance Gate

### 10.1. When Full Operational Acceptance Is Required

Full operational acceptance (per `OPERATIONAL_RUNBOOK.md` Section 8) is
required:

- Before marking Foundation MVP as verified after any code change.
- After domain model, service, runtime, or tool changes.
- Before declaring a major milestone complete.
- After storage, config, or security-sensitive changes.
- When preparing a release readiness report.

### 10.2. Operational Acceptance Steps (Summary)

```
1. git status --short
2. python -m unittest discover -s tests/domain
3. python -m unittest discover -s tests/services
4. python -m unittest discover -s tests (optional but recommended)
5. python scripts/smoke_loop.py
6. python scripts/inspect_package.py <export_directory>
7. python scripts/validate_package.py <export_directory>
8. $env:CONTENT_PLANT_PROJECTS_ROOT="storage/smoke_projects"; python scripts/find_metric_snapshots.py example
9. Create metrics.json and import: python scripts/import_manual_metrics.py metrics.json
10. git status --short
11. Produce Operational Acceptance Report
```

Full details and expected outputs are in `docs/06_operations/OPERATIONAL_RUNBOOK.md`
Section 8.

### 10.3. Operational Acceptance Outcome

| Outcome | Meaning | Next Action |
|---------|---------|-------------|
| **OPERATIONAL** | All tests pass, smoke loop succeeds, packages validate | Proceed to report and human approval |
| **DEGRADED** | Some non-critical tests fail, smoke loop passes | Investigate failures; decide whether to proceed |
| **BROKEN** | Smoke loop fails or critical tests fail | Stop. Fix the issue before any commit. |

---

## 11. Documentation Update Matrix

### 11.1. Which Docs to Update After a Change

| Change Area | Documents to Update |
|-------------|-------------------|
| Domain models / enums / transitions | `docs/00_foundation/DATA_MODEL.md` + `docs/02_architecture/PIPELINES_SPEC.md` |
| Services behaviour or contracts | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` |
| Runtime orchestration | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` |
| CLI tools / scripts | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` + `docs/06_operations/OPERATIONAL_RUNBOOK.md` |
| Storage layout or repository logic | `docs/05_platform/STORAGE_AND_STATE_SPEC.md` |
| Configuration model or env vars | `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` |
| Security boundaries or safety rules | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` |
| Testing philosophy or test categories | `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` |
| Operations workflows or commands | `docs/06_operations/OPERATIONAL_RUNBOOK.md` |
| Agent governance rules | `docs/06_operations/AGENT_OPERATING_MODEL.md` |
| Release/change management rules | `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` |
| Project config schema | `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` |
| Architecture layer structure | `LOOPRA_ARCHITECTURE.md` |
| Agent development rules | `AGENTS.md` |

### 11.2. When Documentation Update Is Optional

- Typo fixes in comments — no doc update.
- Formatting changes (whitespace, line breaks) — no doc update.
- Test additions that do not change behaviour — no doc update.
- Non-functional refactoring within the same interface — no doc update unless
  the contract changes.
- Internal implementation detail changes — no doc update unless behaviour
  changes.

---

## 12. STATE.md Update Rules

### 12.1. When to Update STATE.md

Update `STATE.md` after:

- A major milestone is completed (e.g., all platform specs finalised).
- Foundation MVP operational status changes (e.g., after repair of a broken
  chain).
- Foundation MVP verification changes (e.g., new capability verified).
- A new active development phase begins (e.g., moving from Foundation
  Stabilization to Content Intelligence).
- A major documentation block is completed.
- Accepted architectural direction changes materially.

### 12.2. When NOT to Update STATE.md

Do not update `STATE.md` for:

- Individual small documentation additions.
- Typo fixes or formatting changes.
- Every single doc within a planned block (update once after the block is
  complete).
- Temporary or experimental changes.
- Routine code changes or test additions.
- Individual commit-level changes.

### 12.3. Update Rules

Per `AGENTS.md` Section 8:

> When changing architecture: Update the relevant source-of-truth document.
> Avoid duplicate specifications, conflicting documents, outdated active
> instructions.

STATE.md should always accurately reflect:
- Current project identity (LOOPRA).
- Current development phase.
- Foundation MVP status.
- Completed capabilities.
- Active boundaries and constraints.

---

## 13. AGENTS.md Update Rules

### 13.1. When to Update AGENTS.md

Update `AGENTS.md` only when:

- Development rules change materially.
- Architecture evolution stages change (new phase added or reordered).
- Forbidden scope changes (new constraints added or existing ones lifted).
- Agent workflow rules change.
- Source-of-truth document list changes materially (new canonical documents
  added, old ones removed).
- Project identity or naming rules change.

### 13.2. When NOT to Update AGENTS.md

Do not update `AGENTS.md` for:

- Every individual task completion.
- Adding a new documentation file to `docs/` (the source-of-truth list is
  architecture-level, not every doc).
- Minor clarifications that do not change the rules.
- Temporary development notes.

---

## 14. Git Hygiene Rules

### 14.1. Before Any Change

```bash
git status --short
```

Verify:
- Only expected files are modified.
- No unexpected uncommitted files from prior work.
- `storage/` and `graphify-out/` are not visible (should be gitignored).

### 14.2. After Any Change

```bash
git status --short
git diff --stat
git diff -- <changed files>
```

Verify:
- Only intended files changed.
- No runtime artifacts appear (`storage/smoke_projects/`, `graphify-out/`).
- No `.env` files appear.
- No `__pycache__/` or `*.pyc` files appear.

### 14.3. What Must Never Be Committed

| Path/Pattern | Reason |
|-------------|--------|
| `storage/*` | Runtime artifacts — gitignored |
| `graphify-out/` | Generated knowledge graph — gitignored |
| `.env` | May contain secrets — gitignored |
| `__pycache__/`, `*.pyc` | Build artifacts — gitignored |
| Secrets, API keys, tokens | Security — never store in repo |
| Runtime credentials | Security — never store in repo |

### 14.4. If Runtime Artifacts Appear

If `git status --short` shows files under `storage/` or `graphify-out/`:

1. Check `.gitignore` entry `storage/*` is present and unmodified.
2. Check `.gitignore` entry `graphify-out/` is present and unmodified.
3. Verify files are under the expected gitignored paths.
4. Run `git check-ignore <file>` to confirm the file should be ignored.
5. If gitignore is intact, the file may be tracked from before the rule was
   added. Use `git rm --cached <file>` to stop tracking.

### 14.5. Runtime Artifact Cleanup

```powershell
# Safe to delete — will be regenerated by next smoke loop
Remove-Item -Recurse -Force storage/smoke_projects
```

---

## 15. Commit Policy

### 15.1. Recommended Commit Rules

1. **Small coherent commits.** One logical change per commit. Do not bundle
   unrelated documentation, code and config changes.

2. **Descriptive commit messages.** The message must describe what actually
   changed. Examples:
   - `Add RELEASE_AND_CHANGE_MANAGEMENT.md to operations layer`
   - `Fix ExportPackage status validation in PublishingService`
   - `Update SERVICE_CONTRACTS_SPEC.md after PublishingService change`

3. **Do not mix unrelated docs and code.** Separate commits for documentation
   and code changes. If a code change requires a doc update, the doc update
   may be in the same commit.

4. **Do not commit failed experiments.** Remove experimental code before
   committing. Revert unintended file changes.

5. **Do not commit runtime artifacts.** Verify `git status --short` shows
   no files under `storage/` or `graphify-out/`.

6. **Commit after tests/report when code changed.** The standard flow:
   change → test → verify diff → report → human approval → commit.

### 15.2. Commit Message Format (Recommended)

```
<Brief description of what changed and why>

Files:
  - path/to/changed_file1.md — <what changed>
  - path/to/changed_file2.py — <what changed>

Tests:
  - <test command> — <result>

Foundation MVP chain: <preserved / not affected>
```

No enforcement tooling exists for this format. It is a recommended convention.

---

## 16. Push / Remote Policy

### 16.1. Push Preconditions

Push only after:

1. **Human approval** — the human operator has reviewed the final report and
   explicitly approves.

2. **Required tests passed** — all tests required by the change type (Section 4)
   have passed.

3. **Final report accepted** — the report covers files changed, tests run,
   architectural impact and remaining risks.

4. **Git status reviewed** — only intended files appear in `git status --short`.

5. **No secrets or runtime artifacts** — verified via `git diff --stat` and
   manual review.

### 16.2. Current Branch Reality

The project currently uses the main branch directly. No branch strategy
(main/develop, feature branches, release branches) is formally defined or
enforced.

For code changes that are experimental or high-risk:
- Consider local-only changes until verified.
- Do not push until tests pass and human approval is given.
- Revert locally if the change is abandoned.

No branch protection or pull request workflow is currently configured.

### 16.3. After Push Verification

After pushing:

```bash
git status --short
```

Verify the local working tree matches the remote state. No uncommitted or
unpushed changes remain.

---

## 17. Rollback / Revert Principles

### 17.1. Documentation Changes

For documentation-only changes:

```
Option A — Revert the file change:
    git checkout -- <path/to/file>

Option B — Edit the file back to the previous state:
    Manually correct the document.
    No tests needed (doc-only change).
```

### 17.2. Code Changes

For code changes:

```
Option A — Revert the specific commit:
    git revert <commit-hash>
    Rerun relevant tests.
    Rerun smoke loop if lifecycle affected.
    Verify diff and produce rollback report.

Option B — Revert specific files from a commit:
    git checkout <commit-hash> -- <path/to/file>
    Rerun relevant tests.
    Rerun smoke loop if lifecycle affected.
    Commit the reverted state.

Option C — Manual targeted diff reversal:
    Edit the file to undo the change.
    Rerun relevant tests (per Change Type Table).
    Rerun smoke loop if core/runtime affected.
    Commit the fix.
```

### 17.3. Runtime Artifacts

Runtime artifacts under `storage/smoke_projects/` may be safely deleted at
any time:

```powershell
Remove-Item -Recurse -Force storage/smoke_projects
```

The next smoke loop run will regenerate all artifacts. No code is affected.

### 17.4. What NOT to Revert Without Care

- Do not revert `.gitignore` changes that were made to fix runtime artifact
  exposure without understanding why they were added.
- Do not revert test files without understanding what they protect.
- Do not revert `AGENTS.md` or `STATE.md` without understanding the current
  development phase and constraints.

### 17.5. Rollback Verification

After any code rollback:

```bash
python -m unittest discover -s tests/domain
python -m unittest discover -s tests/services
python scripts/smoke_loop.py
```

### 17.6. Production Rollback

No production environment exists. Production rollback procedures are
future/conceptual and belong to a future Deployment Runbook.

---

## 18. Release Readiness Checklist

### 18.1. Foundation MVP Release Readiness

Before declaring the Foundation MVP as ready for a milestone release,
verify all of the following:

```
[ ] All domain tests pass
    Command: python -m unittest discover -s tests/domain
    Expected: all tests pass (exit code 0).

[ ] All service tests pass
    Command: python -m unittest discover -s tests/services
    Expected: all tests pass (exit code 0).

[ ] Full test suite passes (optional but recommended)
    Command: python -m unittest discover -s tests
    Expected: all tests pass (exit code 0).

[ ] Smoke loop passes
    Command: python scripts/smoke_loop.py
    Expected: all entities created, correct statuses, export_directory produced.
    Statuses: Idea=scripted, Scenario=approved, ContentItem=approved,
              ExportPackage=ready, Publication=published, MetricSnapshot=draft.

[ ] Export package inspects correctly
    Command: python scripts/inspect_package.py <export_directory>
    Expected: manifest read and displayed; exit code 0.

[ ] Export package validates correctly
    Command: python scripts/validate_package.py <export_directory>
    Expected: validation_status=ok; ready_for_manual_publication=true.

[ ] Manual metrics workflow works (if applicable)
    Command: find_metric_snapshots.py → create metrics.json → import_manual_metrics.py
    Expected: metrics_import_status=ok; snapshot DRAFT → RECORDED.

[ ] All relevant docs updated
    Any spec affected by recent code changes must be current.
    Cross-document links verified.

[ ] STATE.md updated (if milestone)
    Current phase, Foundation MVP status and completed capabilities reflect reality.

[ ] AGENTS.md reviewed (if architectural rules changed)
    Development rules, source-of-truth list, forbidden scope.

[ ] Git status expected
    Command: git status --short
    Expected: only intended files modified. No runtime artifacts.

[ ] No future feature claimed as current
    All future/conceptual markers in place.
    No implementation of forbidden features.

[ ] Operational Acceptance Report produced
    Using the template in Section 19.3.

[ ] Human approval obtained
    Report reviewed. Human confirms readiness.
```

---

## 19. Change Report Templates

### 19.1. Documentation Change Report

```text
DOCUMENTATION CHANGE REPORT
===========================

File created/changed:
  docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md — created / modified

Sections:
  [List of main sections with brief description]

Change type:
  Documentation-only / Architecture document change

Scope:
  [What the document covers; confirm scope matches task]

Current/future distinction:
  - Current: [list of current-only topics]
  - Future/conceptual: [list of future-marked topics]

Project naming:
  - Active name used: LOOPRA
  - Historical name (Content Plant) used only in historical context

Foundation MVP chain referenced:
  [Yes / No — with explanation]

Other files changed:
  [List or "none"]

Tests run:
  [List of test commands and results]
  OR
  NOT RUN — documentation-only change, no code affected.
  Reason: [explanation]

Related docs referenced:
  [List of documents linked or referenced]

Cross-document links verified:
  [Yes / N/A — all linked documents exist at expected paths]
  Verification command: ls <path>

Architectural impact:
  [None / description of impact]

Remaining risks:
  [List or "none"]
```

### 19.2. Code Change Report

```text
CODE CHANGE REPORT
==================

Files changed:
  - path/to/file.py: [what changed and why]
  - path/to/test_file.py: [test additions or modifications]

Behaviour changed:
  Before: [description of behaviour before change]
  After: [description of behaviour after change]

Change type:
  [Foundation/domain change / Service contract change / Runtime change /
   Tool/CLI change / Storage/config change / Security-sensitive change /
   Cleanup/refactor]

Tests run:
  - python -m unittest tests.domain.test_models — [PASS / FAIL]
  - python -m unittest tests.services.test_<name> — [PASS / FAIL]
  - python -m unittest discover -s tests/domain — [PASS / FAIL]
  - python -m unittest discover -s tests/services — [PASS / FAIL]
  - python -m unittest discover -s tests — [PASS / FAIL] (full suite)

Smoke loop result:
  - python scripts/smoke_loop.py — [PASS / FAIL]
  - All entity statuses: [correct / incorrect — list]
  - Export directory: [path]

Export package inspection:
  - python scripts/inspect_package.py <dir> — [PASS / FAIL]

Export package validation:
  - python scripts/validate_package.py <dir> — [PASS / FAIL]
  - Files checked: [count]
  - Ready for manual publication: [true / false]

Artifacts generated:
  [List or "none — no artifacts generated"]

Git status:
  [Only intended files modified; no runtime artifacts staged]
  git status --short output: [paste]

Docs updated:
  [List of docs updated or "none — no contract/behaviour change"]

Foundation MVP chain preserved:
  [Yes — all entities progress through valid states]
  [No — describe what broke]

Current vs future distinction:
  [Confirm only current behaviour implemented; no future features added]

Architectural impact:
  [None / description]

Remaining risks:
  [List or "none"]

Rollback notes:
  [How to revert if needed, or "revert commit <hash>"]
```

### 19.3. Operational Acceptance Report

```text
OPERATIONAL ACCEPTANCE REPORT
=============================
Date: [date]
Operator: [name/role]
Change reference: [change type and brief description]

1. PRE-CHANGE GIT STATUS
   Command: git status --short
   Result: [clean / expected changes only]

2. TESTS
   Domain tests:    python -m unittest discover -s tests/domain    → [PASS/FAIL]
   Service tests:   python -m unittest discover -s tests/services  → [PASS/FAIL]
   All tests:       python -m unittest discover -s tests           → [PASS/FAIL]

3. SMOKE LOOP
   Command:         python scripts/smoke_loop.py                   → [PASS/FAIL]
   Export directory: [path]
   Entity statuses:
     Idea:            [scripted / actual]
     Scenario:        [approved / actual]
     ContentItem:      [approved / actual]
     ExportPackage:   [ready / actual]
     Publication:     [published / actual]
     MetricSnapshot:  [draft / actual]

4. EXPORT INSPECTION
   Command:         python scripts/inspect_package.py <dir>        → [PASS/FAIL]
   Package ID:      [export_xxxxxxxxxxxx]

5. EXPORT VALIDATION
   Command:         python scripts/validate_package.py <dir>       → [PASS/FAIL]
   Files checked:   [count]
   Ready:           [true / false]

6. METRIC SNAPSHOTS
   Command:         python scripts/find_metric_snapshots.py <id>   → [N found]
   DRAFT snapshots: [count]

7. MANUAL METRICS (if applicable)
   Import status:   [PASS/FAIL/NOT RUN]
   Recorded keys:   [list]

8. POST-CHANGE GIT STATUS
   Command:         git status --short
   Result:          [clean / expected changes only]
   Runtime artifacts: [none found / found — action taken]

9. DOCS UPDATED
   [List of docs updated or "none"]

10. STATE.md STATUS
    Updated:        [Yes / No]
    Reason:         [explanation]

FINAL STATE: [OPERATIONAL / DEGRADED / BROKEN]

Remaining risks:
  [List or "none"]
```

### 19.4. Release Readiness Report

```text
RELEASE READINESS REPORT
========================
Date: [date]
Milestone: [milestone name / description]
Release type: [Foundation MVP milestone / Documentation milestone / etc.]

1. FULL TEST SUITE
   python -m unittest discover -s tests → [PASS/FAIL]

2. SMOKE LOOP
   python scripts/smoke_loop.py → [PASS/FAIL]
   All entity statuses: [correct]

3. EXPORT VALIDATION
   python scripts/validate_package.py <dir> → [PASS/FAIL]

4. MANUAL METRICS WORKFLOW
   [PASS/FAIL/NOT RUN]

5. DOCS STATUS
   All affected specs updated: [Yes / No / N/A]
   Cross-document links verified: [Yes / No]
   No future features claimed current: [Confirmed]

6. STATE.md
   Updated for this milestone: [Yes / No]
   Current phase: [phase name]
   Foundation MVP status: [READY / etc.]

7. GIT STATUS
   git status --short → [clean / expected]
   No runtime artifacts: [Confirmed]

8. FORBIDDEN FEATURES CHECK
   No API added:      [Confirmed]
   No UI added:       [Confirmed]
   No DB added:       [Confirmed]
   No external calls: [Confirmed]
   No autoposting:    [Confirmed]

9. CURRENT LIMITATIONS ACKNOWLEDGED
   No CI/CD:          [Acknowledged]
   No production env: [Acknowledged]
   No release automation: [Acknowledged]

FINAL DECISION: [READY FOR RELEASE / NOT READY]

Human approval: [Name / Pending]

Remaining risks:
  [List or "none"]
```

---

## 20. Risk Classification

### 20.1. Risk Levels

| Risk Level | Change Types | Approval | Tests Required | Review Depth |
|------------|-------------|----------|---------------|--------------|
| **Low** | Documentation-only, project config, test-only | Human review | Optional | Structural check |
| **Medium** | Service contract, runtime orchestration, tool/CLI, cleanup/refactor | Human approval | Required — services + smoke loop | Full test + smoke loop + report review |
| **High** | Foundation/domain model, storage/config, security-sensitive | Human approval required | Required — full suite + smoke loop | Full test + smoke loop + manual diff review + operational acceptance |
| **Critical** | API, UI, DB, connectors, auth, autonomy, autoposting | Architectural approval required — not allowed in current phase | Future only | N/A — not implemented |

### 20.2. Risk Escalation

If a change originally classified as Medium reveals itself to have High
impact during execution (e.g., a service change unexpectedly affects domain
transitions):

1. Stop execution.
2. Reclassify to the actual risk level.
3. Expand test requirements accordingly.
4. Notify Human of the reclassification.
5. Proceed only after Human acknowledges the increased risk.

---

## 21. Forbidden Change Patterns

### 21.1. Changes That Must Never Occur Without Explicit Approval

| Forbidden Pattern | Why Forbidden | Detection |
|-------------------|---------------|-----------|
| Adding API endpoints or HTTP handlers | No API exists; adds unapproved infrastructure | grep for `http`, `flask`, `fastapi`, `route` in core/ |
| Adding UI components or templates | No UI exists; adds unapproved infrastructure | grep for `html`, `template`, `render` in core/ |
| Adding database dependencies or ORM | No DB exists; filesystem only | grep for `sql`, `database`, `orm`, `sqlalchemy` in core/ |
| Adding external HTTP calls or integrations | No connectors exist; manual publication only | grep for `requests`, `urllib`, `http` in core/ |
| Adding autoposting or automated publication | Manual publication only; no API posting | grep for `post_to`, `publish_to`, `api` in publishing.py |
| Direct JSON mutation of entity files | Bypasses services; breaks domain integrity | Check if any script writes directly to storage/smoke_projects/data/ |
| Project-specific branching in core/ | Violates project-agnostic architecture | grep for project names in core/ |
| Stale Content Plant naming in active documents | Creates identity confusion | grep -r "Content Plant" docs/ --include="*.md" |
| Duplicate numbered folders | Violates canonical path structure | ls docs/ |
| Untested service changes | Degrades verification coverage | Check report for test results |
| Claiming future capability as current | Creates false expectations | Review docs for present tense describing future features |
| Secrets or credentials in any file | Security risk | grep for `password`, `secret`, `token`, `api_key` in committed files |

### 21.2. Detection Commands

```bash
# Check for forbidden code patterns
grep -r "requests\.\|urllib\|httpx\|aiohttp" core/ --include="*.py"
grep -r "sqlalchemy\|sqlite3\|psycopg\|pymongo" core/ --include="*.py"
grep -r "flask\|fastapi\|django\|aiohttp" core/ --include="*.py"

# Check for stale naming
grep -r "Content Plant" docs/ --include="*.md"

# Check for duplicate folders
ls docs/
```

---

## 22. Current Known Limitations

These limitations are honestly acknowledged. They are not blockers for the
current phase but define the boundaries of the current release/change process.

| Limitation | Impact on Change Management |
|-----------|---------------------------|
| No CI | Tests must be run manually; no automated gate before commit. |
| No automated release | Each release is a manual human decision with no pipeline. |
| No deployment | No delivery target exists. Verification is local only. |
| No production environment | No environment to release to. |
| No migration system | Schema changes to entity models require manual test verification only. |
| No release tags policy | No formal versioning or tagging convention applied to the repo. |
| No automated doc validation | Cross-document links and naming consistency checked manually. |
| No secret scanning | Relies on human and agent discipline to avoid committing secrets. |
| No branch strategy | Main branch used directly. No isolation for risky changes. |
| No concurrent change protection | Two agents working simultaneously could create conflicts. |
| No automated rollback | All rollback is manual (git revert, manual file edits). |
| No dependency scanning | Dependencies are assumed available in the Python environment. |
| Single `text_social_post` format | Changes affecting content generation are limited to one format. |

---

## 23. Future Release Management Path

### 23.1. Staged Evolution

The following stages represent the planned evolution of release and change
management. All stages beyond Stage 1 are **future/conceptual**.

```
Stage 1 — CURRENT: Manual local change process
    Human defines task → ChatGPT prepares prompt → Codex executes →
    tests run locally → Human reviews report → Human commits and pushes.
    No CI. No deployment. No automation.

Stage 2 — STANDARDIZED PROMPTS AND REPORTS (current + near future)
    All change prompts follow AGENT_OPERATING_MODEL.md format.
    All reports follow the templates in this document.
    Pre-change checklists used consistently.

Stage 3 — REQUIRED LOCAL OPERATIONAL ACCEPTANCE (near future)
    Operational acceptance report mandatory for all Medium and High risk
    changes before commit.
    Standardised operational acceptance workflow used consistently.

Stage 4 — CI TEST GATE (future)
    Tests run automatically on push.
    Blocking gate: push rejected if tests fail.
    Smoke loop included in CI verification.

Stage 5 — DOCS CONSISTENCY CHECKS (future)
    Automated validation of cross-document links.
    Automated detection of stale naming (Content Plant).
    Automated detection of duplicate folders.

Stage 6 — ARTIFACT / SECRET SCANNING (future)
    Pre-commit hooks or CI checks for secrets.
    Pre-commit hooks for runtime artifact detection.
    Automated .gitignore compliance checking.

Stage 7 — RELEASE TAGGING (future)
    Formal versioning convention (semver or project-defined).
    Git tags applied for each release.
    Changelog generation from commit history.

Stage 8 — DEPLOYMENT PIPELINE (future)
    Automated deployment to staging/production.
    Smoke tests run post-deployment.
    Health checks and monitoring integration.

Stage 9 — ROLLBACK AUTOMATION (future)
    Automated rollback on deployment failure.
    Canary deployments or blue/green deployment patterns.
    Rollback verification integrated into CI.

Stage 10 — SAAS RELEASE PROCESS (future)
    Multi-tenant release coordination.
    Per-tenant configuration migration.
    Zero-downtime deployments.
    Release scheduling and communication.
```

### 23.2. Current Stage Only

All stages beyond Stage 1 are future/conceptual. No implementation of CI,
deployment pipelines, release tagging or automation occurs without explicit
architectural approval. The current manual change process (Stage 1) is the
only active release and change management process.

---

## 24. Related Documents

### 24.1. Source of Truth

| Document | Path | Relevance |
|----------|------|-----------|
| AGENTS.md | `AGENTS.md` | Development rules, agent principles, project identity, forbidden scope. |
| STATE.md | `STATE.md` | Current project state, phase, Foundation MVP status, boundaries. |

### 24.2. Operations Layer

| Document | Path | Relevance |
|----------|------|-----------|
| Operational Runbook | `docs/06_operations/OPERATIONAL_RUNBOOK.md` | Operational commands, verification workflows, git hygiene, safety rules. |
| Agent Operating Model | `docs/06_operations/AGENT_OPERATING_MODEL.md` | Agent roles, task lifecycle, prompt rules, report formats, testing matrix, documentation matrix. |
| Release and Change Management | `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` | This document. |

### 24.3. Platform Layer

| Document | Path | Relevance |
|----------|------|-----------|
| Runtime Orchestration Spec | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` | Execution coordination, runtime change impact. |
| Service Contracts Spec | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` | Service operations, contract change impact. |
| Tooling and CLI Spec | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` | CLI tools, tool change impact. |
| Storage and State Spec | `docs/05_platform/STORAGE_AND_STATE_SPEC.md` | Storage model, storage change impact. |
| Configuration and Environment Spec | `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | Config model, env var impact. |
| Testing and Validation Spec | `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` | Test framework, validation layers. |
| Security and Safety Boundaries Spec | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` | Security boundaries for all changes. |

### 24.4. Foundation and Architecture

| Document | Path | Relevance |
|----------|------|-----------|
| Data Model | `docs/00_foundation/DATA_MODEL.md` | Domain entities, Foundation MVP chain. |
| Pipelines Spec | `docs/02_architecture/PIPELINES_SPEC.md` | Current foundation loop, pipeline stages. |
| LOOPRA Architecture | `LOOPRA_ARCHITECTURE.md` | Overall architecture layer structure. |

---

## 25. Code References

### 25.1. Scripts

| File | Purpose |
|------|---------|
| `scripts/smoke_loop.py` | End-to-end Foundation MVP lifecycle verification. |
| `scripts/inspect_package.py` | Read and display ExportPackage contents. |
| `scripts/validate_package.py` | Validate ExportPackage structural integrity. |
| `scripts/find_metric_snapshots.py` | List DRAFT MetricSnapshot records. |
| `scripts/import_manual_metrics.py` | Import manual metrics into a DRAFT snapshot. |

### 25.2. Tests

| Path | Purpose |
|------|---------|
| `tests/domain/` | Domain model entity creation, field requirements, transition rules. |
| `tests/services/` | Service operations, tools, lifecycle, smoke loop, workflows. |

### 25.3. Core

| Path | Purpose |
|------|---------|
| `core/domain/models.py` | Domain entities — Idea, Scenario, ContentItem, ExportPackage, Publication, MetricSnapshot. |
| `core/domain/enums.py` | Status enums. |
| `core/domain/transitions.py` | Status transition rules. |
| `core/services/loop.py` | LoopOrchestrator — lifecycle execution coordination. |
| `core/services/projects.py` | ProjectService, BrandProfileService. |
| `core/services/ideas.py` | IdeaService, ScenarioService. |
| `core/services/production.py` | ProductionLifecycleService. |
| `core/services/publishing.py` | PublishingService. |
| `core/services/analytics.py` | AnalyticsService. |
| `core/services/_storage.py` | Base repository class. |
| `core/projects/loader.py` | Project config loading, validation, path safety. |

### 25.4. Repository

| File | Purpose |
|------|---------|
| `.gitignore` | Source/runtime artifact separation, exclusion rules. |

---

## 26. Document Status

| Field | Value |
|-------|-------|
| **Status** | Active — LOOPRA Operations Layer |
| **Version** | v1.0 |
| **Date** | 2026-07-09 |
| **Project** | LOOPRA — Autonomous Marketing Operating System |
| **Layer** | Operations Layer — Release and Change Management |

---

## Final Statement

The Release and Change Management document is the practical governance layer
for how LOOPRA evolves safely. It defines what changes are allowed, how they
must be verified, who approves them, and what documentation must follow.

In the current phase, every change is local, manual and human-approved. There
is no CI, no deployment pipeline, no automated release — and this document
does not pretend otherwise. It defines the discipline that keeps the Foundation
MVP chain (Project → Idea → Scenario → ContentItem → ExportPackage →
Publication → MetricSnapshot) intact through every documentation, code,
service, tool, storage, config, security and architecture change.

Future release capabilities — CI gates, deployment pipelines, release tagging,
rollback automation and SaaS release processes — are described as
future/conceptual. They will be implemented when the architecture evolves to
support them, following the same disciplined change management process defined
here.

**Test before commit. Report before approval. Human approves before push.**

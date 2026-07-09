# AGENT OPERATING MODEL

## Version

v1.0

## Status

Active — LOOPRA Operations Layer

## Purpose

This document defines the practical operating model for human + AI agents during
development, documentation, validation and future runtime evolution of LOOPRA.

It answers the central question:

> How should the Human Operator, ChatGPT architecture copilot, Codex
> implementation agent, CLI/copilot local review agent and future Orchestrator
> Agent interact during development, maintenance and operation of LOOPRA without
> violating the architectural boundaries of the Foundation MVP?

This document is the governance layer for agent-assisted development. It bridges
the current development workflow, the OPERATIONAL_RUNBOOK.md, the platform
specifications, the safety/security boundaries, and the future runtime agent
model.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

AGENT_OPERATING_MODEL.md establishes who makes decisions, who executes tasks,
how tasks are handed off between agents, how prompts are written, how reports are
formatted, how context is managed, and how safety is maintained during
agent-assisted development of LOOPRA.

## 1.2. Who Uses This Document

| Role | How They Use It |
|------|-----------------|
| Human Owner / Operator | Understand their authority, oversight duties and decision boundaries. |
| ChatGPT Architecture Copilot | Follow prompt handoff rules, maintain architectural context, review agent reports. |
| Codex Implementation Agent | Follow task scope, report format, forbidden actions and current/future distinction. |
| CLI Copilot / Local Review Agent | Follow review protocol, detect inconsistencies, produce review reports. |
| Future Agent Developer | Understand the agent-safe boundaries before implementing product agents. |

## 1.3. In Scope

- Human operator role definition.
- ChatGPT architecture copilot role definition.
- Codex implementation/documentation agent role definition.
- CLI copilot / local review agent role definition.
- Prompt handoff rules.
- Task report formats.
- Verification and review duties.
- Context management and session transition protocols.
- Future Orchestrator Agent boundary (conceptual).
- Safety rules for all agent types.
- Testing and documentation responsibilities by task type.
- Multi-agent workflow patterns.
- Direct Codex usage policy.
- Conflict resolution procedures.
- State update rules.

## 1.4. Out of Scope

- Runtime agent implementation.
- Agent framework design or implementation.
- Autonomous background execution.
- Scheduler or worker implementation.
- API or UI development.
- Multi-agent product runtime.
- External agent marketplace.
- Specific AI model selection or provider comparison.
- Prompt engineering for product intelligence (belongs to Intelligence Layer).

---

# 2. Current Agent Reality

## 2.1. Honest Current State

The current LOOPRA Foundation MVP has **no internal autonomous agent**.

The product runtime is deterministic: services execute, tools inspect, scripts
run the smoke loop. No background agent is running. No autonomous decision is
being made by the system.

The Foundation MVP operates in copilot mode:
- Human creates ideas.
- Services execute the lifecycle.
- Human publishes externally.
- Human collects and imports metrics manually.

## 2.2. Agents Are Workflow Participants — Not Product Runtime

Current agents are **external participants in the development workflow**:

| Agent Role | Reality |
|------------|---------|
| Human Owner / Operator | Provides goals, approves architecture, decides direction. |
| ChatGPT Architecture Copilot | Preserves architectural context, prepares Codex prompts, reviews reports, detects contradictions. |
| Codex Implementation Agent | Executes concrete repo tasks — creates docs, edits code, runs tests, reports changes. |
| CLI Copilot / Local Review Agent | Optional inspector — reviews Codex output, runs grep/tests, verifies paths, checks git status. |

None of these agents exist inside the product runtime. They operate on the
repository as external tools, similar to how a developer uses an IDE.

## 2.3. Future Orchestrator Agent

The future Orchestrator Agent is a **product capability** — not a development
tool. It will manage content cycles, coordinate intelligence modules, and issue
execution requests through the runtime layer. It is described in
`docs/03_intelligence/AGENT_SYSTEM_SPEC.md`.

**Current status:** Not implemented. All references to Orchestrator Agent
operations within the product are future/conceptual.

---

# 3. Core Operating Principle

## 3.1. The Principle

```
Agents decide.
Tools execute.
```

This principle applies at two levels:

### Development Workflow Level (Current)

| Decision Layer | Who Owns It |
|---------------|-------------|
| Strategic/architectural decisions | Human + ChatGPT |
| Implementation decisions within task bounds | Codex (must respect docs) |
| Deterministic execution | Scripts and tools |
| Runtime lifecycle execution | Services and tools |
| Final approval | Human |

### Product Runtime Level (Future/Conceptual)

| Decision Layer | Who Owns It |
|---------------|-------------|
| Strategic direction and brand boundaries | Human |
| Operational cycle management and content decisions | Orchestrator Agent |
| Analytical capability | Intelligence Modules |
| Deterministic execution | Production Tools |
| Knowledge retention | Learning Memory |

## 3.2. Clarification

- **Strategic decisions** (architecture direction, naming, scope boundaries) are
  owned by Human and ChatGPT working together.
- **Implementation decisions** (how to structure a specific doc, what code to
  write within defined scope) may be proposed by Codex but must respect
  architecture docs.
- **Deterministic execution** (running tests, smoke loop, validation scripts)
  belongs to tools and scripts — not agents.
- **Final approval** always rests with the Human.

## 3.3. The Boundary

```
Development agents are NOT product runtime agents.
ChatGPT/Codex workflow does NOT equal Orchestrator Agent operation.
ChatGPT/Codex edit code and docs. They do not operate the product.
```

---

# 4. Roles and Responsibilities

## 4.1. Role Table

| Role | Current or Future | Responsibilities | May Do | Must Not Do |
|------|-------------------|-----------------|--------|-------------|
| Human Owner / Operator | Current | Final product direction, architecture approval, task priority, naming/brand decisions, merge/push approval, manual publication actions, autonomy escalation decisions. | Provide context, review reports, confirm risky actions, decide new session start. | Bypass architecture docs, delegate strategic decisions fully, commit runtime artifacts. |
| ChatGPT Architecture Copilot | Current | Preserve architectural context, prepare Codex prompts, review agent reports, detect contradictions, keep current/future separation, choose next task, prevent scope creep, maintain LOOPRA naming consistency. | Write structured prompts, review docs, detect stale names, maintain session context. | Claim repo changes without agent report, invent current code behaviour, approve unsafe shortcuts, replace tests when code changes. |
| Codex Implementation / Documentation Agent | Current | Execute concrete repo tasks: create docs, edit code (when tasked), inspect files, run tests, report changes. | Create/update docs, edit code per task, inspect repo, run test suites. | Implement forbidden features, change unrelated files, bypass architecture docs, merge current/future, commit secrets, delete source files silently. |
| CLI Copilot / Local Review Agent | Current (optional) | Inspect repo state, review Codex output, run grep/tests, verify paths, check git status, detect inconsistencies, produce review reports. | Audit file changes, verify doc completeness, cross-check paths. | Silently change code/docs unless tasked, create parallel architecture, override Human/ChatGPT direction. |
| Runtime Tools / Scripts | Current | Deterministic execution: smoke loop, inspection, validation, metric snapshots, metric imports. | Execute documented commands, return structured output, produce artifacts. | Make strategic decisions, interpret results, bypass services, mutate storage directly. |
| Future Orchestrator Agent | Future (conceptual) | Plan content cycles, request tools, call runtime commands, coordinate intelligence modules, ask for human approval, learn from analytics. | Invoke services through runtime entrypoints, query intelligence modules, propose content decisions. | Bypass services, write storage directly, publish without approval, access secrets, escalate autonomy, operate continuously without cycle checkpoints. |
| Future Intelligence Modules | Future (conceptual) | Trend analysis, content opportunity generation, performance analytics, learning memory management. | Analyze patterns, generate structured recommendations. | Make autonomous decisions without Orchestrator, call tools directly, bypass Orchestrator. |
| Future Production Tools | Future (conceptual) | Media rendering, multi-format content generation, platform-specific adaptation. | Execute deterministic production actions. | Make strategic decisions, select content directions, interpret performance. |

## 4.2. Role Interaction Model

```
Human
  │  Strategic authority, final approval
  ↓
ChatGPT
  │  Architecture continuity, prompt crafting, report review
  ↓
Codex
  │  Task execution within scope, report back
  ↓
CLI Copilot (optional)
  │  Review, inspection, verification
  ↓
Tools / Scripts
  │  Deterministic execution, tests, validation
```

Future product runtime (conceptual):

```
Human
  │  Strategic governance
  ↓
Orchestrator Agent
  │  Operational authority within boundaries
  ↓
Intelligence Modules → Production Tools → Learning Memory
```

---

# 5. Human Owner / Operator

## 5.1. Ownership

The Human owns:

- Final product direction.
- Architecture approval.
- Task priority and sequencing.
- Naming and brand decisions.
- Merge/push approval (when version control is involved).
- Publication and manual external actions.
- Autonomy escalation decisions.

## 5.2. Responsibilities

The Human should:

- Provide clear context and goals to ChatGPT.
- Review agent reports for correctness and architectural alignment.
- Confirm risky or destructive actions before execution.
- Decide when to start a new session due to context window limitations.
- Verify that Foundation MVP chain is preserved after changes.
- Ensure that no forbidden features (API, UI, DB, external integrations,
  autoposting) are introduced without explicit architectural approval.

## 5.3. Boundaries

The Human must not:

- Rely on agents to make strategic architectural decisions without review.
- Skip review of agent reports and assume correctness.
- Allow direct Codex usage to bypass architecture docs for critical tasks.
- Commit runtime artifacts to version control.
- Store secrets or credentials in the repository.

---

# 6. ChatGPT Architecture Copilot

## 6.1. Current Role

ChatGPT acts as the architecture continuity layer. It maintains the "big picture"
across sessions and ensures that individual Codex tasks do not diverge from the
architectural direction.

## 6.2. Responsibilities

ChatGPT is responsible for:

- **Preserving architectural context** — loading and maintaining awareness of
  all active architecture documents, STATE.md, and AGENTS.md.
- **Preparing Codex prompts** — writing structured, scoped prompts that include
  required reading, exact tasks, forbidden actions and report format.
- **Reviewing agent reports** — verifying that Codex output matches the requested
  scope, does not introduce forbidden features and respects current/future
  boundaries.
- **Detecting contradictions** — flagging when agent reports conflict with
  architecture docs, when docs conflict with code, or when STATE.md is stale.
- **Maintaining current/future separation** — ensuring no future capability is
  claimed as current, and no current capability is incorrectly described.
- **Choosing next tasks** — deciding which document, code change or validation
  step should follow based on architecture priorities.
- **Preventing scope creep** — rejecting agent proposals that exceed the
  Foundation MVP scope.
- **Maintaining naming consistency** — ensuring LOOPRA is used as the active
  project name; Content Plant is treated as historical only.

## 6.3. Boundaries

ChatGPT must not:

- Claim repo changes were made without receiving a Codex agent report.
- Invent current code behaviour without inspecting the actual codebase.
- Approve unsafe shortcuts (skipping tests, bypassing services, editing entity
  JSON directly).
- Replace test execution with assumptions when code changes are involved.
- Produce implementation without first reading the relevant architecture docs.

## 6.4. Working with Context

ChatGPT should:

- Summarize completed work regularly to prevent context window overflow.
- Preserve a list of created documents and their status.
- When the context window becomes heavy, create a transition prompt for the next
  session (see Section 15).
- Reference docs by path, not by full copy, to conserve context space.

---

# 7. Codex Implementation / Documentation Agent

## 7.1. Current Role

Codex is the execution agent. It performs concrete repository tasks: creating
documentation, editing code, running tests, inspecting files and reporting
results.

## 7.2. Capabilities

Codex may:

- Create new documentation files within defined scope.
- Edit existing code when explicitly tasked.
- Inspect repository structure, files and code.
- Run test suites to verify changes.
- Report exact files changed and test results.

## 7.3. Requirements

Codex must:

- **Read required docs before starting** — AGENTS.md, STATE.md and any docs
  specified in the task prompt.
- **Follow prompt scope exactly** — do not expand beyond the requested task.
- **Not implement forbidden features** — no API, UI, DB, external integrations,
  autoposting, scheduler, agents, connectors.
- **Not change unrelated files** — only files specified in the task prompt or
  directly required by the change.
- **Report exact files changed** — path and nature of change.
- **Report tests run or not run** — with justification if not run.
- **Distinguish current vs future** — mark any future concept as
  "future/conceptual".
- **Preserve Foundation MVP chain** — Project → Idea → Scenario → ContentItem →
  ExportPackage → Publication → MetricSnapshot must remain valid.

## 7.4. Boundaries

Codex must not:

- Write code or docs beyond the task scope.
- Implement future capabilities without explicit permission.
- Bypass architecture documents.
- Change project structure (move files, rename directories) without approval.
- Commit secrets or credentials.
- Alter `.gitignore` without documented reason.
- Delete source files (in `core/`, `scripts/`, `tests/`, `projects/`) without
  explicit instruction.
- Create duplicate numbered folders.
- Change architecture names (Content Plant, LOOPRA) without approval.
- Claim orchestration or strategy decisions that belong to ChatGPT or Human.

---

# 8. CLI Copilot / Local Review Agent

## 8.1. Current Role

The CLI copilot is an optional review layer. It can inspect the repository after
Codex execution to verify correctness, detect inconsistencies and produce review
reports.

## 8.2. Capabilities

The CLI copilot may:

- Inspect repository state (`git status`, file listing, path verification).
- Review Codex output for structural correctness.
- Run `grep` to detect stale names (Content Plant in active docs).
- Run tests to verify changes.
- Verify paths against the project structure.
- Check git status for unexpected changes or runtime artifacts.
- Detect inconsistencies between docs and code.
- Produce structured review reports.

## 8.3. Boundaries

The CLI copilot must not:

- Silently change code or docs unless explicitly tasked.
- Create parallel architecture or alternative specifications.
- Override Human or ChatGPT direction.
- Commit changes without Human approval.
- Delete files without explicit instruction.

## 8.4. Review Report Format

```
CLI COPILOT REVIEW REPORT
=========================
Repository: LOOPRA
Review scope: [what was reviewed]
Files inspected: [list]
Issues found:
  - [issue description] — [file:line] — [severity]
Tests run: [list or "not run"]
Git status: [clean / expected changes / unexpected changes]
Recommendation: [proceed / fix issues first / escalate]
```

---

# 9. Runtime Tools / Scripts as Deterministic Executors

## 9.1. Definition

Tools and scripts are deterministic executors — not agents. They perform narrow,
well-defined operations. They do not make strategic decisions.

## 9.2. Current Tool Inventory

| Tool | Type | Purpose |
|------|------|---------|
| `smoke_loop.py` | Lifecycle execution | End-to-end Foundation MVP verification. |
| `inspect_package.py` | Read-only inspection | Reads and displays ExportPackage contents. |
| `validate_package.py` | Read-only validation | Validates ExportPackage structural integrity. |
| `find_metric_snapshots.py` | Read-only query | Lists DRAFT MetricSnapshot records. |
| `import_manual_metrics.py` | Service-backed mutation | Imports manual metrics into DRAFT snapshot. |

## 9.3. Agent vs Tool Boundary

```
Agent:      Decides what, why and when.
Tool:       Determines how (the deterministic execution).

Agent decision:  "Verify the Foundation MVP lifecycle is operational."
Tool execution:  python scripts/smoke_loop.py
                 → produces entities, artifacts, status output

Agent decision:  "Validate the export package structure."
Tool execution:  python scripts/validate_package.py <dir>
                 → produces validation_status=ok or ERROR
```

## 9.4. Relationship to Agent Operating Model

When agents (ChatGPT, Codex) need operational verification, they invoke tools:

- Codex runs tests: `python -m unittest discover -s tests`
- Codex runs smoke loop: `python scripts/smoke_loop.py`
- Codex validates package: `python scripts/validate_package.py <dir>`

Tools provide the deterministic ground truth that agents rely on for reporting.

Reference: `docs/05_platform/TOOLING_AND_CLI_SPEC.md`, `docs/06_operations/OPERATIONAL_RUNBOOK.md`.

---

# 10. Future Orchestrator Agent Boundary

## 10.1. Current Status

The Orchestrator Agent is **not implemented**. It is a future product capability
described in `docs/03_intelligence/AGENT_SYSTEM_SPEC.md`.

All references to the Orchestrator Agent operating within the product runtime
are future/conceptual.

## 10.2. Future Role

When implemented, the Orchestrator Agent will:

- Plan and manage content cycles.
- Query Intelligence Modules for analysis.
- Request tool execution through runtime entrypoints.
- Coordinate multiple cycles across channels and content pillars.
- Ask for human approval at defined control points.
- Learn from Analytics Intelligence and update Learning Memory.

## 10.3. Future Boundaries

The future Orchestrator Agent must not:

- Bypass services and mutate domain entities directly.
- Write storage directly without going through repositories.
- Publish content externally without approval gate (unless in approved
  autopilot mode with explicit configuration).
- Access secrets or credentials directly.
- Escalate its own autonomy level — only the Human can change autonomy mode.
- Operate continuously without defined cycles and checkpoints.
- Access data from a different project.
- Operate in autopilot mode without confidence checks and safety boundaries.

## 10.4. Development Agents vs Product Agents

```
DEVELOPMENT AGENTS (current):
    ChatGPT — helps design architecture, writes prompts, reviews output.
    Codex — executes repo tasks, creates docs, edits code.
    CLI Copilot — inspects and reviews.

PRODUCT AGENT (future, conceptual):
    Orchestrator Agent — manages content cycles, coordinates intelligence
    modules, calls runtime tools.
```

These are separate categories. Development agents are external workflow
participants. The Orchestrator Agent is an internal product component.

---

# 11. Task Lifecycle

## 11.1. Standard Task Flow

```
1. HUMAN STATES GOAL
   Human describes what they want to achieve.
   Example: "Create the Agent Operating Model document."

2. CHATGPT CLARIFIES ARCHITECTURE AND WRITES TASK PROMPT
   ChatGPT reads relevant architecture docs.
   ChatGPT writes a structured prompt for Codex.
   Prompt includes: project name, required reading, exact task, forbidden
   actions, report format, current/future boundaries.

3. CODEX EXECUTES WITHIN REPO
   Codex reads the specified source documents.
   Codex performs the task (creates doc, edits code, runs tests).
   Codex does not exceed scope.

4. CODEX RETURNS FINAL REPORT
   Codex reports: files changed, tests run, architectural impact,
   current/future distinction maintained, Foundation MVP preserved.

5. CHATGPT REVIEWS REPORT AGAINST ARCHITECTURE
   ChatGPT verifies: correct file paths, no forbidden changes, no current/
   future mix, Foundation MVP chain preserved, docs consistent.

6. HUMAN DECIDES NEXT ACTION
   Human reviews the result.
   Human approves, requests fixes, or decides next task.

7. TESTS / RUNBOOK USED IF NEEDED
   If code changed: tests run, smoke loop verified.
   If docs changed: structural review, consistency check.

8. DOCUMENTATION / STATE UPDATED IF NEEDED
   STATE.md updated for major milestones.
   AGENTS.md consulted for architectural impact.
```

## 11.2. Decision Points

| Gate | Owner | Question |
|------|-------|----------|
| Task definition | Human + ChatGPT | What exactly needs to be done? |
| Scope approval | ChatGPT | Does this task fit Foundation MVP scope? |
| Execution | Codex | How do I implement this within the given boundaries? |
| Verification | Codex | Did tests pass? Is the output correct? |
| Architecture review | ChatGPT | Does the result match the architecture? |
| Final approval | Human | Is this acceptable to proceed? |

## 11.3. Iteration

If a task fails review:
1. ChatGPT identifies the issue.
2. ChatGPT writes a correction prompt for Codex.
3. Codex fixes the issue.
4. Report and review cycle repeats.

---

# 12. Prompt Handoff Rules

## 12.1. Purpose

Prompts are the handoff mechanism between ChatGPT (architecture layer) and
Codex (execution layer). A well-structured prompt prevents scope creep, ensures
required reading and produces verifiable output.

## 12.2. Prompt Structure

### Required Sections

Every Codex task prompt must include:

```
PROJECT: LOOPRA

REQUIRED READING:
  - path/to/doc1.md
  - path/to/doc2.md

TASK:
  [Exact description of what to create or change.]

SCOPE:
  - File(s) to create/change: [exact paths]
  - Format: [Markdown, Python, YAML, etc.]

FORBIDDEN:
  - Do not implement: API, UI, DB, external integrations, autoposting.
  - Do not modify: [list of files not to touch].
  - Do not claim: future capabilities as current.
  - Do not: [other constraints].

REQUIRED DISTINCTIONS:
  - Mark future/conceptual capabilities explicitly.
  - Distinguish current development workflow from future product runtime.
  - Preserve Foundation MVP chain.

EXPECTED REPORT:
  - Files created/changed.
  - Tests run (or reason if not run).
  - Architectural impact.
  - Current vs future distinction verified.
  - Foundation MVP chain preserved.
  - Remaining risks.
```

### Example Documentation Task Prompt

```
PROJECT: LOOPRA

REQUIRED READING:
  - AGENTS.md
  - STATE.md
  - docs/06_operations/OPERATIONAL_RUNBOOK.md
  - docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md

TASK:
  Create docs/06_operations/AGENT_OPERATING_MODEL.md describing the
  operating model for human + AI agents during LOOPRA development.

SCOPE:
  File to create: docs/06_operations/AGENT_OPERATING_MODEL.md
  Format: Markdown

FORBIDDEN:
  - Do not claim that Orchestrator Agent is already implemented.
  - Do not mix ChatGPT/Codex workflow with product runtime.
  - Do not add API, UI, DB, or any implementation code.
  - Do not change any files other than the target document.

REQUIRED DISTINCTIONS:
  - Mark all future/conceptual product agent capabilities explicitly.
  - Distinguish development agents from product runtime agents.

EXPECTED REPORT:
  [Standard report format — see Section 13]
```

### Example Code Task Prompt

```
PROJECT: LOOPRA

REQUIRED READING:
  - core/services/publishing.py
  - docs/05_platform/SERVICE_CONTRACTS_SPEC.md
  - tests/services/test_loop_engineering.py

TASK:
  Add validation for [specific field] in PublishingService.publish_content().

SCOPE:
  - File to edit: core/services/publishing.py (publish_content method)
  - File to edit: tests/services/test_loop_engineering.py (add test)

FORBIDDEN:
  - Do not change any other service.
  - Do not modify ExportPackage or Publication entity models.
  - Do not add API or external integrations.

REQUIRED DISTINCTIONS:
  - Current behaviour: manual publication only.
  - Future: connector-based publishing (do not implement).

EXPECTED REPORT:
  [Standard report format — see Section 13]
```

## 12.3. Prompt Quality Rules

1. **Specific enough to execute.** The agent must know exactly which file to
   create or change.
2. **Not so broad that the agent invents features.** Scope must be bounded.
3. **Include required reading.** Prevent the agent from operating on stale
   assumptions.
4. **State forbidden actions explicitly.** "Do not implement API/UI/DB" should
   be in every task prompt.
5. **Require report format.** The agent must know what constitutes an
   acceptable completion report.
6. **Include current vs future boundary.** Especially important for
   documentation tasks where future concepts may be adjacent to current scope.

---

# 13. Report Format Rules

## 13.1. Purpose

Agent reports are the verification mechanism. ChatGPT and the Human rely on
them to know what changed, what was tested and whether the architecture was
respected.

## 13.2. Documentation Task Report Format

```
DOCUMENTATION TASK REPORT
=========================

File created/changed:
  docs/06_operations/AGENT_OPERATING_MODEL.md — created

Section structure:
  [List of main sections with brief description]

Scope:
  [What the document covers; confirm scope matches task prompt]

Current/future distinction:
  - Current roles documented: Human, ChatGPT, Codex, CLI copilot, tools
  - Future roles marked conceptual: Orchestrator Agent, Intelligence Modules,
    Production Tools (product runtime variants)

Foundation MVP chain preserved:
  [Yes / No — with explanation]

Current vs future language rules applied:
  - Current: [list of current-only topics]
  - Future/conceptual: [list of future-marked topics]

Other files changed:
  [List or "none"]

Tests run:
  [List of test commands run and results]
  OR
  NOT RUN — documentation-only change, no code affected.

Related docs referenced:
  [List of documents linked or referenced]

Architectural impact:
  [None / description of impact]

Remaining risks:
  [List or "none"]
```

## 13.3. Code Change Report Format

```
CODE CHANGE REPORT
==================

Files changed:
  - core/services/publishing.py: [what changed]
  - tests/services/test_loop_engineering.py: [what changed]

Behaviour changed:
  [Description of behaviour before and after]

Tests run:
  - python -m unittest tests.services.test_loop_engineering — PASS
  - python -m unittest tests.domain.test_models — PASS (regression check)

Smoke loop result (if applicable):
  - python scripts/smoke_loop.py — PASS
  - All entity statuses correct

Artifacts generated:
  [List or "none — no artifacts generated"]

Git status:
  [Only intended files modified; no runtime artifacts staged]

Foundation MVP chain preserved:
  [Yes — all entities progress through valid states]

Architectural impact:
  [None / description]

Current vs future distinction:
  [Confirm only current behaviour implemented]

Remaining risks:
  [List or "none"]

Rollback notes:
  [How to revert if needed, or "revert commit"]
```

## 13.4. Report Verification Checklist

ChatGPT or CLI copilot verifies:

- [ ] File paths correct — no duplicate numbered folders.
- [ ] No stale project names (Content Plant in active docs).
- [ ] Current/future distinction maintained.
- [ ] Foundation MVP chain preserved.
- [ ] No forbidden files changed.
- [ ] Tests justified (run or explained why not).
- [ ] Doc links consistent and valid.
- [ ] No implementation beyond task scope.

---

# 14. Context Management

## 14.1. The Finite Context Window

ChatGPT and Codex sessions have finite context windows. Without active
management, context quality degrades: earlier information is lost,
contradictions are missed, and architecture drift occurs.

## 14.2. Context Management Rules

1. **Summarize completed work regularly.** After each major document or code
   block is completed, produce a concise summary.
2. **Preserve document inventory.** Maintain a list of created documents, their
   versions and statuses.
3. **Keep current status visible.** The latest STATE.md status and active phase
   should be readily available.
4. **When context gets heavy, create a transition prompt.** See Section 15.
5. **Reference documents by path, not by full content.** Do not re-paste entire
   specification documents into every prompt. Reference
   `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` — do not copy all 1200 lines.
6. **Include only essential architecture principles** in transition prompts —
   not the full text of every spec.

## 14.3. Signs of Context Window Problems

- ChatGPT repeats questions already answered.
- Architecture boundaries are forgotten between sessions.
- Current/future confusion appears.
- Tasks exceed scope without detection.
- Document contradictions are not caught.

When these signs appear, it is time to start a new session with a transition
prompt.

## 14.4. Context Preservation Checklist

Before starting a new task, verify that ChatGPT has access to:

- [ ] Current project name (LOOPRA).
- [ ] Current phase (Foundation Stabilization and Architecture Alignment).
- [ ] Completed document inventory.
- [ ] Active constraints (no API, UI, DB, etc.).
- [ ] Next task definition.

---

# 15. Session Transition Protocol

## 15.1. When to Transition

Start a new session when:

- The context window becomes large and early context may be lost.
- A major documentation block is completed (e.g., all 05_platform specs done).
- Moving from architecture to implementation phase.
- Repeated contradictions appear that context refresh would resolve.
- A new development phase begins.

## 15.2. Transition Prompt Template

```
SESSION TRANSITION — LOOPRA

PROJECT: LOOPRA (Autonomous Marketing Operating System)
Historical name: Content Plant (archive only).

CURRENT STATUS:
  Phase: [current phase from STATE.md]
  Foundation MVP: READY + OPERATIONALLY VERIFIED
  Foundation MVP chain: Project → Idea → Scenario → ContentItem →
    ExportPackage → Publication → MetricSnapshot

COMPLETED DOCUMENTS:
  [List of created/updated docs with versions]

ACTIVE CONSTRAINTS:
  - No API, UI, DB, external integrations, autoposting.
  - Manual publication only. Manual metrics only.
  - text_social_post content format only.
  - Filesystem-only storage. No database.
  - Development agents are external workflow participants.
  - Orchestrator Agent is future/conceptual — not implemented.

CURRENT ENVIRONMENT:
  - Env vars: LOOPRA_* primary, CONTENT_PLANT_* legacy fallback (W3 resolved).
  - Tests: Python unittest, run from repo root.
  - Scripts: scripts/smoke_loop.py, scripts/inspect_package.py, etc.

NEXT TASK:
  [Description of next task]

FILES TO LOAD:
  - AGENTS.md
  - STATE.md
  - [List of docs needed for next task]

FORBIDDEN ACTIONS:
  - Do not implement API, UI, DB, external integrations.
  - Do not claim future capabilities as current.
  - Do not bypass architecture docs.

EXPECTED REPORT FORMAT:
  [Standard report format — see AGENT_OPERATING_MODEL.md Section 13]
```

## 15.3. What to Carry Forward

Always include in a transition prompt:

- Project identity (LOOPRA, not Content Plant).
- Current phase and Foundation MVP status.
- Active constraints and forbidden actions.
- Completed document inventory.
- Essential architecture principles from AGENTS.md.
- Next task and its scope.

## 15.4. What to Leave Behind

Do not carry forward:

- Full text of completed specifications (reference by path).
- Intermediate debugging details.
- Speculative implementation ideas.
- Historical discussions that were resolved.

---

# 16. Review and Verification Protocol

## 16.1. After Agent Report

When Codex submits a final report, the reviewer (ChatGPT or CLI copilot or
Human) checks:

### Structural Checks

- [ ] Correct file path — no duplicate numbered folders.
- [ ] Files exist at the reported paths.
- [ ] No unexpected files changed (`git status --short`).
- [ ] No duplicate folder numbering created.

### Content Checks

- [ ] No stale project names (Content Plant where LOOPRA should be used).
- [ ] Current/future distinction maintained throughout.
- [ ] Foundation MVP chain referenced correctly.
- [ ] Doc links valid and consistent.
- [ ] No forbidden features described as current.

### Quality Checks

- [ ] Prompt scope fully addressed.
- [ ] Report format followed.
- [ ] Tests justified (run or explained).
- [ ] Architectural impact assessed.
- [ ] Remaining risks identified.

## 16.2. Verification Tools

Use these commands to verify:

```bash
# Check git status for unexpected changes
git status --short

# Search for stale project names in docs
grep -r "Content Plant" docs/ --include="*.md"

# Verify file exists at reported path
ls <reported_file_path>

# Check for duplicate numbered folders
ls docs/
```

## 16.3. Escalation Criteria

Escalate to Human when:

- Codex report contradicts architecture docs.
- Forbidden files were changed without explanation.
- Current and future are conflated in the output.
- Foundation MVP chain appears broken.
- Test justification is absent for a code change.
- Security boundary may have been violated.

---

# 17. Scope Control Rules

## 17.1. Foundation MVP Scope

The current scope is defined in AGENTS.md Section 5 and STATE.md:

**Allowed:**
- Domain models.
- Services.
- Project configuration.
- Validation.
- Documentation.
- CLI scripts and tools.

**Forbidden (unless explicitly tasked in a later phase):**
- API.
- UI.
- Database.
- Authentication.
- Billing.
- SaaS infrastructure.
- External integrations.
- Autonomous agent systems (product runtime).
- Autoposting.
- Scheduler / workers.
- Media rendering (beyond text_social_post).
- External API calls.

## 17.2. Agent Scope Enforcement

Agents must enforce these boundaries at three levels:

| Level | Enforcement |
|-------|------------|
| Prompt level | ChatGPT writes prompts that explicitly forbid out-of-scope features. |
| Execution level | Codex must not implement forbidden features, even if it seems useful. |
| Review level | ChatGPT and CLI copilot verify no forbidden features were added. |

## 17.3. Scope Creep Detection

Signs of scope creep:

- Agent proposes adding a feature not in the task prompt.
- Agent adds "helpful" extras (error handling for non-existent scenarios,
  configuration for future platforms, etc.).
- Agent writes code for future capabilities "so it's ready."
- Agent restructures code beyond the required change.

Response: Reject the change. Return a corrected prompt with tighter scope.

---

# 18. Current vs Future Language Rules

## 18.1. Why This Matters

Conflating current and future creates false expectations, leads to
implementation of unsupported features and degrades architecture integrity.

## 18.2. Language Rules

### Current Language (Use for Implemented Features)

| Category | Current Terms | Evidence |
|----------|--------------|----------|
| Storage | filesystem JSON files | `core/services/_storage.py` |
| Execution | CLI scripts + Python imports | `scripts/` directory |
| Publication | manual only | `PublishingService.publish_content()` uses placeholder URL |
| Metrics | manual collection + import | `import_manual_metrics.py` |
| Autonomy | copilot mode only | No autonomous agent code exists |
| Content format | text_social_post only | `content_format` enum constraint |
| Env vars | LOOPRA_* primary, CONTENT_PLANT_* fallback | `smoke_loop.py` env var usage |
| Test framework | unittest (standard library) | `tests/` directory |

### Future/Conceptual Language (Marked Explicitly)

| Category | Current Status | Where Described |
|----------|---------------|-----------------|
| Orchestrator Agent | Not implemented | AGENT_SYSTEM_SPEC.md |
| Intelligence Modules | Not implemented | AGENT_SYSTEM_SPEC.md |
| Learning Memory runtime | Stub methods only | `AnalyticsService.get_insights()` returns `[]` |
| Autopilot mode | Not implemented | AGENT_SYSTEM_SPEC.md |
| Database storage | Not implemented | STORAGE_AND_STATE_SPEC.md (future section) |
| Object storage | Not implemented | STORAGE_AND_STATE_SPEC.md (future section) |
| Connector publishing | Not implemented | TOOLING_AND_CLI_SPEC.md (future section) |
| Media rendering | Not implemented | TOOLING_AND_CLI_SPEC.md (future section) |
| API endpoints | Not implemented | RUNTIME_ORCHESTRATION_SPEC.md (future section) |
| UI | Not implemented | Not described in any active spec |
| LOOPRA_* env vars | Not implemented | CONFIGURATION_AND_ENVIRONMENT_SPEC.md (future section) |
| Multi-tenancy / SaaS | Not implemented | Various future sections |

## 18.3. Enforcement

Every document must:

- Use present tense for current features.
- Use future tense or "future/conceptual" marker for planned features.
- Include a "Current MVP Constraint" or "Future/Conceptual" note wherever
  future features are mentioned.

---

# 19. Safety Rules for Agents

## 19.1. Development Agent Safety Rules

All development agents (ChatGPT, Codex, CLI copilot) must follow these safety
rules:

### Storage Safety

- [ ] Never directly edit entity JSON files in `storage/smoke_projects/`.
- [ ] Never bypass services and write domain entities directly.
- [ ] All mutations go through services → repositories → JSON files.

### Repository Safety

- [ ] Never delete source files in `core/`, `scripts/`, `tests/`, `projects/`.
- [ ] Never alter `.gitignore` without documented reason and approval.
- [ ] Never change project structure (rename directories, move files) silently.
- [ ] Never create duplicate numbered folders (e.g., two `docs/06_operations/`).

### Secret Safety

- [ ] Never commit secrets, credentials, API keys or tokens.
- [ ] Never store secrets in `project.yaml` or documentation.
- [ ] Never create `.env` files with real credentials.

### Naming Safety

- [ ] Never use Content Plant as the active project name in new documents.
- [ ] Content Plant is historical/archive only.
- [ ] Use LOOPRA for all current documentation, file content and prompts.

### Architecture Safety

- [ ] Never implement future features without explicit task.
- [ ] Never bypass architecture documents.
- [ ] Never claim future capabilities as current.
- [ ] Never introduce project-specific logic into `core/`.

### Git Safety

- [ ] Never commit runtime artifacts (`storage/smoke_projects/`, `graphify-out/`).
- [ ] Never force-push or rewrite history without explicit approval.
- [ ] Always check `git status` before and after changes.

## 19.2. Dangerous Actions — Require Explicit Human Confirmation

| Action | Why Dangerous |
|--------|--------------|
| Deleting `projects/{project_id}/project.yaml` | Destroys project configuration. |
| Deleting or modifying `core/` domain files | Breaks Foundation MVP. |
| Modifying `.gitignore` entries | May expose runtime artifacts to version control. |
| Direct JSON mutations on entity files | Bypasses service validation and state transitions. |
| Adding external dependencies or network calls | Expands MVP scope without approval. |
| Deleting test files | Removes verification coverage. |

## 19.3. Reference

These rules align with `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md`
and `docs/06_operations/OPERATIONAL_RUNBOOK.md` Section 22.

---

# 20. Testing Responsibility by Task Type

## 20.1. Testing Matrix

| Task Type | Tests Required | Report Expectation |
|-----------|---------------|-------------------|
| Documentation-only change | Not required (optional regression check) | "NOT RUN — documentation-only change, no code affected." |
| Code change — domain models | `python -m unittest discover -s tests/domain` | Full domain test pass/fail result. |
| Code change — services | `python -m unittest discover -s tests/services` | Full service test pass/fail result. |
| Code change — any core/ | `python -m unittest discover -s tests` + `python scripts/smoke_loop.py` | Full test suite + smoke loop pass/fail. |
| Service contract change | `python -m unittest discover -s tests/services` + `python scripts/smoke_loop.py` | Service tests + end-to-end verification. |
| Script change | `python -m unittest discover -s tests/services/test_<script>.py` + `python scripts/smoke_loop.py` | Script-specific tests + full smoke loop. |
| Storage/config change | `python -m unittest discover -s tests` | Full test suite. |
| Security-sensitive change | Full test suite + manual review of git status + grep for secrets | Full verification + security confirmation. |
| New file creation (non-code) | Not required | "NOT RUN — new file, no existing code affected." |
| File rename or move | `python -m unittest discover -s tests` | Verify imports and paths still resolve. |

## 20.2. Smokeloop as Acceptance Test

The smoke loop is the ultimate acceptance test for any code change:

```bash
python scripts/smoke_loop.py
```

Expected: all entities created, all statuses correct, export_directory produced.

The smoke loop proves the Foundation MVP chain (Project → Idea → Scenario →
ContentItem → ExportPackage → Publication → MetricSnapshot) is intact.

## 20.3. When NOT to Run Tests

Tests may be skipped when:

- The change is documentation-only and does not reference code paths.
- The change is a new standalone document with no code dependencies.
- The change is a formatting or typo fix in a doc.

In all cases, the report must state: "NOT RUN" + the reason.

## 20.4. Reference

Testing rules align with:
- `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md`
- `docs/06_operations/OPERATIONAL_RUNBOOK.md` Sections 7, 8

---

# 21. Documentation Responsibility by Task Type

## 21.1. Documentation Update Matrix

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
| Agent governance changes | `docs/06_operations/AGENT_OPERATING_MODEL.md` |
| New scripts added | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` + `OPERATIONAL_RUNBOOK.md` |
| Project config changes | `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` |

## 21.2. When Documentation Update Is Optional

- Typo fixes in comments — no doc update needed.
- Formatting changes (no content change) — no doc update needed.
- Test additions that don't change behaviour — no doc update needed.
- Non-functional refactoring within same interface — verify but no doc update
  needed unless contract changes.

## 21.3. Reference

These rules align with OPERATIONAL_RUNBOOK.md Section 19 and AGENTS.md
Section 8.

---

# 22. Multi-Agent Workflow Patterns

## 22.1. Pattern A — Simple Codex Execution

```
Human → ChatGPT prompt → Codex → report → ChatGPT review
```

**Use when:** Standard documentation or small code change. Architecture is
well-understood. Task scope is clear.

**ChatGPT duties:** Write prompt, review report, maintain architecture context.

**Codex duties:** Execute task, report results, stay within scope.

## 22.2. Pattern B — Codex + CLI Copilot Review

```
Human → ChatGPT prompt → Codex → CLI reviewer → report → ChatGPT
```

**Use when:** Code change is significant. Multiple files affected. Risk of
introducing inconsistencies.

**CLI copilot duties:** Inspect repo state after Codex execution, verify file
paths, check git status, run grep for stale names, produce review report.

**ChatGPT duties:** Write prompt, review both Codex report and CLI copilot
report.

## 22.3. Pattern C — Direct Human-to-Codex Task

```
Human → Codex → [optional review]
```

**Use when:** Small, well-bounded task. Human has clear understanding of
architecture. Quick fix needed.

**Tradeoffs:**
- Faster for small tasks.
- ChatGPT loses context unless report is returned.
- Risky for architecture-sensitive work.

**Rules:**
- Direct Codex tasks should still include scope and forbidden actions.
- After completion, paste the final report into the architecture chat for
  ChatGPT context.
- Architecture-critical tasks should go through ChatGPT prompt (Pattern A or B).

## 22.4. Pattern D — Future Runtime Agent (Conceptual)

```
Orchestrator Agent → Runtime entrypoint → Services → Tools → Result →
  Intelligence Modules → Learning Memory → Next cycle
```

**Use when:** Orchestrator Agent is implemented. Content cycles are autonomous.

**Current status:** Not implemented. Conceptual only.

## 22.5. Selecting the Right Pattern

| Situation | Recommended Pattern |
|-----------|-------------------|
| New architecture document | Pattern A |
| Code change in core services | Pattern B |
| Quick typo fix | Pattern C |
| Architecture refactoring | Pattern A (with Human deep review) |
| Multi-file implementation | Pattern B |
| Exploratory research | Pattern C (then report back to ChatGPT) |

---

# 23. Direct Codex Usage Policy

## 23.1. When Direct Usage Is Appropriate

Direct Codex usage (Human → Codex without ChatGPT intermediary) is acceptable
for:

- Small, well-bounded tasks (typo fix in a doc, adding a comment, running a
  grep search).
- Operational commands (running tests, smoke loop, inspecting a package).
- Quick investigation (checking a specific file, verifying a path).
- Tasks where the Human has current architectural context and can write an
  adequate prompt.

## 23.2. When Direct Usage Is Risky

Direct Codex usage is risky for:

- Creating new architecture documents.
- Changing core services or domain models.
- Implementing new features.
- Renaming or restructuring the project.
- Tasks that touch multiple architectural layers.
- Any change that could affect the Foundation MVP chain.

## 23.3. Rules for Direct Codex Tasks

1. **Include scope and forbidden actions** in the prompt, even for small tasks.
2. **State the project name** (LOOPRA) and current phase.
3. **Reference relevant docs** if the task touches existing architecture.
4. **After completion, share the final report** with the architecture chat
   (ChatGPT) to maintain context continuity.
5. **If the task grows in complexity**, stop and route through ChatGPT for
   proper architecture review.

## 23.4. Mandatory ChatGPT Involvement

The following task types must go through ChatGPT prompt:

- Creating new docs in `docs/` (except trivial fixes).
- Changing any file in `core/`.
- Changing `scripts/` logic.
- Adding or modifying tests that change test philosophy.
- Any change affecting the Foundation MVP chain.
- Tasks that require current/future distinction judgment.

---

# 24. Conflict Resolution

## 24.1. Conflict Types and Responses

| Conflict | Detection | Response |
|----------|----------|----------|
| Codex report contradicts docs | Reviewer compares report claims to architecture specs | Stop. Compare against source-of-truth docs. Flag discrepancy. Create correction task. |
| Docs contradict code | Reviewer or agent inspects both | Stop. Identify which is correct (code is ground truth for current behaviour; docs for architecture intent). Update the incorrect one. |
| STATE.md contradicts current files | Reviewer notices mismatch | Stop. Update STATE.md to reflect reality. Verify against actual repo state. |
| Two docs define same thing differently | Cross-reference during review | Stop. Determine which definition is authoritative based on document layer. Update the other. |
| Folder numbering conflict appears | Path inspection | Stop. Rename and update all references. One canonical path per topic. |
| Agent implemented beyond scope | Report shows files changed outside task | Stop. Revert or flag the extra changes. Create corrected prompt. |

## 24.2. Resolution Process

```
1. STOP — Do not continue. Do not build on inconsistency.
2. IDENTIFY source of truth:
   - Code behaviour → actual codebase
   - Architecture intent → architecture docs (LOOPRA_ARCHITECTURE.md,
     AGENTS.md)
   - Project state → STATE.md
3. INSPECT the discrepancy. Determine which side is correct.
4. CREATE a cleanup task. Scope it to fix the specific issue only.
5. UPDATE the incorrect source (doc or code) to match the correct one.
6. VERIFY consistency is restored before proceeding.
```

## 24.3. Prevention

- Always read architecture docs before starting a task.
- Cross-reference related documents when making changes.
- Report any inconsistency found during task execution.
- Do not assume one source is correct without verification.

---

# 25. State Update Rules

## 25.1. When to Update STATE.md

Update STATE.md after:

- Meaningful architecture milestone (e.g., all platform specs completed).
- Foundation status changes (e.g., new capability verified).
- Operational acceptance of a major change.
- Major documentation block completion.
- Major implementation phase begins or completes.

## 25.2. When NOT to Update STATE.md

Do not update STATE.md for:

- Individual small documentation additions.
- Typo fixes or formatting changes.
- Every single doc within a planned block (update once after the block is
  complete).
- Temporary experimental changes.

## 25.3. Update Rules

Per AGENTS.md Section 8:
> When changing architecture: Update the relevant source-of-truth document.
> Avoid duplicate specifications, conflicting documents, outdated active
> instructions.

STATE.md should accurately reflect:
- Current project identity (LOOPRA).
- Current phase.
- Foundation MVP status.
- Completed capabilities.
- Active boundaries and constraints.

---

# 26. Agent Operating Model and Security

## 26.1. Security Boundary Alignment

The Agent Operating Model aligns with `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md`
in the following areas:

| Security Boundary | Agent Rule |
|------------------|------------|
| No direct storage mutation | Agents must route mutations through services. Read-only inspection of storage files is acceptable for debugging. |
| No secrets in repository | Agents must never commit secrets, credentials or tokens. |
| No hidden autonomy | Future agents must not escalate their own autonomy level. Autonomy mode is set by Human. |
| Project isolation | Agents must not access data across project boundaries. |
| Approval gates | Future Orchestrator Agent must respect human approval gates defined by autonomy mode. |
| Publication safety | Agents must not publish content externally without approval (except in configured autopilot mode — future). |
| Config integrity | Agents must not store secrets in project.yaml or environment config files. |
| Path safety | Agents must not write outside project-scoped directories. |
| .gitignore hygiene | Agents must not alter .gitignore without justification. Agents must verify no runtime artifacts appear in git status. |

## 26.2. Future Agent Security

When the Orchestrator Agent is implemented, it must:

- Operate within defined autonomy boundaries.
- Route all mutations through services.
- Not access secrets or credentials directly.
- Leave an audit trail of all decisions.
- Respect emergency stop and autonomy reduction by Human.
- Not publish without approval (or explicit autopilot configuration).

---

# 27. Agent Operating Model and Operations

## 27.1. Operational Runbook Alignment

The Agent Operating Model aligns with `docs/06_operations/OPERATIONAL_RUNBOOK.md`
in the following areas:

| Operational Concern | Agent Rule |
|--------------------|------------|
| Running tests | Agents use `python -m unittest discover -s tests` — exactly as documented in the runbook. |
| Running smoke loop | Agents use `python scripts/smoke_loop.py` and report entity statuses. |
| Inspecting packages | Agents use `python scripts/inspect_package.py <dir>` for read-only verification. |
| Validating packages | Agents use `python scripts/validate_package.py <dir>` for structural verification. |
| Finding metric snapshots | Agents use `python scripts/find_metric_snapshots.py <project_id>` with correct env var. |
| Importing metrics | Agents use `python scripts/import_manual_metrics.py <json>` via AnalyticsService. |
| Checking git status | Agents use `git status --short` before and after changes. |
| Report format | Agent reports follow the templates in OPERATIONAL_RUNBOOK.md Section 20. |

## 27.2. When Agents Invoke Operations

Agents invoke operational commands:

1. **After code changes** — to verify the Foundation MVP is intact.
2. **Before reporting completion** — to confirm no regressions.
3. **During review** — to verify that reported entity states are accurate.
4. **For smoke verification** — when any core service or domain model changes.

Agents must not invoke operational commands for strategic decisions — only
for verification and execution.

---

# 28. Future Evolution

## 28.1. Staged Evolution of Agent Operating Model

```
Stage 1 — CURRENT: Human + ChatGPT + Codex Workflow
    Manual prompts, manual reviews, context carried by Human and ChatGPT.
    Codex executes deterministic repo tasks.
    CLI copilot available for optional review.

Stage 2 — STANDARDIZED PROMPTS AND REPORTS (current + near future)
    All prompts follow AGENT_OPERATING_MODEL.md format.
    All reports follow standard templates.
    Context transition protocols used between sessions.

Stage 3 — CLI COPILOT REVIEW PROTOCOL (near future)
    CLI copilot review becomes standard for code changes.
    Review reports cover structural, naming and scope checks.
    Integrated into the Codex → review → report flow.

Stage 4 — RUNTIME COMMAND REGISTRY (future)
    All operational commands registered in a central registry.
    Agents invoke commands through registry, not ad-hoc.
    Command contracts defined (inputs, outputs, exit codes, errors).

Stage 5 — AGENT-SAFE TOOL INVOCATION (future)
    Tools have defined safe invocation boundaries.
    Agents cannot invoke destructive operations without approval gate.
    Tool outcomes audited and recorded.

Stage 6 — PRODUCT ORCHESTRATOR AGENT (future)
    Orchestrator Agent implemented as product capability.
    Manages content cycles, coordinates intelligence modules.
    Operates within autonomy boundaries set by Human.
    Uses runtime entrypoints defined in RUNTIME_ORCHESTRATION_SPEC.md.

Stage 7 — MULTI-AGENT CONTENT CYCLE OPERATION (future)
    Orchestrator + Intelligence Modules operate together.
    Content cycles run with autonomous decision-making.
    Learning Memory accumulates operational experience.
    Human provides strategic governance and boundary setting.

Stage 8 — SAAS AGENT OPERATIONS (future)
    Multi-tenant agent operations with audit and security.
    Per-project autonomy configurations.
    Agent marketplace (if applicable).
    Full audit trail and compliance capabilities.
```

## 28.2. Current Stage Only

All stages beyond Stage 1 are future/conceptual. No implementation occurs
without explicit architectural approval. The current Agent Operating Model
governs Stage 1 with preparation for Stage 2 (standardized prompts and reports).

---

# 29. Readiness Criteria

The AGENT_OPERATING_MODEL.md document is considered ready when all of the
following are satisfied:

- [ ] Current agent reality documented (development agents are external
  workflow participants; no product runtime agents exist).
- [ ] All roles described with responsibilities, capabilities and boundaries
  (Human, ChatGPT, Codex, CLI copilot, Tools, Future Orchestrator).
- [ ] Task lifecycle defined (goal → prompt → execute → report → review →
  decide → verify → update).
- [ ] Prompt handoff rules defined with required sections and template format.
- [ ] Report format defined for documentation and code change tasks.
- [ ] Context management rules defined (summarize, inventory, transition).
- [ ] Session transition protocol defined with template.
- [ ] Review and verification protocol defined with checklist.
- [ ] Direct Codex usage policy defined (when allowed, when risky, mandatory
  ChatGPT involvement).
- [ ] Current vs future language rules defined with specific examples.
- [ ] Safety boundaries for agents defined (storage, repo, secrets, naming,
  architecture, git).
- [ ] Testing responsibilities by task type defined with matrix.
- [ ] Documentation responsibilities by task type defined with matrix.
- [ ] Multi-agent workflow patterns defined (A, B, C, D).
- [ ] Conflict resolution procedures defined.
- [ ] State update rules defined.
- [ ] Security alignment documented.
- [ ] Operational runbook alignment documented.
- [ ] Future evolution staged and marked conceptual.
- [ ] Foundation MVP preserved — no claim of implemented runtime agents.

---

# 30. Related Documents

## 30.1. Source of Truth Documents

| Document | Path | Relevance |
|----------|------|-----------|
| AGENTS.md | `AGENTS.md` | Development rules, agent principles, project identity. |
| STATE.md | `STATE.md` | Current project state, phase, boundaries. |

## 30.2. Intelligence Layer

| Document | Path | Relevance |
|----------|------|-----------|
| Agent System Spec | `docs/03_intelligence/AGENT_SYSTEM_SPEC.md` | Future Orchestrator Agent architecture. |
| Content Cycle Spec | `docs/03_intelligence/CONTENT_CYCLE_SPEC.md` | Future content cycle model. |

## 30.3. Platform Layer

| Document | Path | Relevance |
|----------|------|-----------|
| Runtime Orchestration Spec | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` | Execution coordination, agent-to-runtime contract. |
| Service Contracts Spec | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` | Service operations, agent-safe boundaries. |
| Tooling and CLI Spec | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` | CLI tools, agent tool-calling boundary. |
| Storage and State Spec | `docs/05_platform/STORAGE_AND_STATE_SPEC.md` | Storage model, artifact separation. |
| Configuration and Environment Spec | `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | Config model, env vars. |
| Testing and Validation Spec | `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` | Test framework, validation layers. |
| Security and Safety Boundaries Spec | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` | Security boundaries for all agents. |

## 30.4. Operations Layer

| Document | Path | Relevance |
|----------|------|-----------|
| Operational Runbook | `docs/06_operations/OPERATIONAL_RUNBOOK.md` | Operational commands, verification workflows. |
| Agent Operating Model | `docs/06_operations/AGENT_OPERATING_MODEL.md` | This document. |

---

# 31. Code References

## 31.1. Scripts

| File | Purpose |
|------|---------|
| `scripts/smoke_loop.py` | End-to-end Foundation MVP lifecycle verification. |
| `scripts/inspect_package.py` | Read and display ExportPackage contents. |
| `scripts/validate_package.py` | Validate ExportPackage structural integrity. |
| `scripts/find_metric_snapshots.py` | List DRAFT MetricSnapshot records. |
| `scripts/import_manual_metrics.py` | Import manual metrics into draft snapshot. |

## 31.2. Tests

| Path | Purpose |
|------|---------|
| `tests/domain/` | Domain model and transition tests. |
| `tests/services/` | Service, tool and lifecycle tests. |

## 31.3. Core Services

| Path | Purpose |
|------|---------|
| `core/services/loop.py` | LoopOrchestrator — lifecycle execution. |
| `core/services/projects.py` | ProjectService, BrandProfileService. |
| `core/services/ideas.py` | IdeaService, ScenarioService. |
| `core/services/production.py` | ProductionLifecycleService. |
| `core/services/publishing.py` | PublishingService. |
| `core/services/analytics.py` | AnalyticsService. |
| `core/services/_storage.py` | Base repository class. |

## 31.4. Core Domain

| Path | Purpose |
|------|---------|
| `core/domain/models.py` | Domain entities. |
| `core/domain/enums.py` | Status enums. |
| `core/domain/transitions.py` | Status transition rules. |

## 31.5. Configuration

| Path | Purpose |
|------|---------|
| `core/projects/loader.py` | Project config loading, validation, path safety. |

## 31.6. Repository

| File | Purpose |
|------|---------|
| `.gitignore` | Source/runtime artifact separation. |

---

# 32. Document Status

| Field | Value |
|-------|-------|
| **Status** | Active — LOOPRA Operations Layer |
| **Version** | v1.0 |
| **Date** | 2026-07-09 |
| **Project** | LOOPRA — Autonomous Marketing Operating System |
| **Layer** | Operations Layer — Agent Operating Model |

---

# Final Statement

The Agent Operating Model is not a product specification. It is a governance
framework for how humans and AI agents collaborate to build LOOPRA.

In the current phase, development agents — ChatGPT, Codex and CLI copilot —
are external workflow participants. They operate on the repository under
human direction and architecture-defined boundaries. They are not product
runtime components.

The future Orchestrator Agent will be a product capability — an internal
component that manages content cycles, coordinates intelligence modules and
issues execution requests through the runtime layer. It is described in
`AGENT_SYSTEM_SPEC.md` and is marked as future/conceptual throughout this
document.

Until the Orchestrator Agent is implemented, every strategic decision is made
by the Human. Every task is scoped by ChatGPT. Every execution is performed
by Codex. Every result is verified against architecture documents.

**Agents decide. Tools execute. Humans approve.**

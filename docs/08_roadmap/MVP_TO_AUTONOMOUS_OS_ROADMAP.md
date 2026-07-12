# MVP TO AUTONOMOUS OS ROADMAP

## Version

v1.0

## Status

Active -- LOOPRA Roadmap Layer

## Purpose

This document defines the staged evolution path from the current LOOPRA Foundation MVP to a full Autonomous Marketing Operating System. It establishes stage boundaries, entry/exit criteria, dependencies, validation gates and risk controls -- without prescribing implementation details, UI/API/DB specifics, sprint planning or code tasks.

It answers the central question:

> How does LOOPRA evolve from today's deterministic foundation into an
> autonomous, self-learning marketing operating system without breaking
> validated execution primitives, without premature infrastructure
> build-out and without losing current Foundation MVP integrity?

---

# 1. Purpose and Scope

## 1.1. In Scope

- Current baseline (Foundation MVP verified state).
- Roadmap stages from Stage 0 through Stage 10.
- Stage entry criteria, exit criteria and dependencies.
- Validation gates per stage.
- Risk controls and mitigation strategies.
- Current/future separation at every stage boundary.
- Dependency map across capabilities.
- NURA validation project positioning.
- Stage transition rules.

## 1.2. Out of Scope

- Implementation details, code tasks, sprint planning.
- UI/API/DB implementation specifics.
- Connector-specific implementation specifications.
- Commercial pricing, billing models.
- Deployment infrastructure details.
- External integration API contracts.
- Specific AI model/provider selection.
- Team structure or hiring plans.

---

# 2. Current Baseline -- Foundation MVP

## 2.1. Status

**READY + OPERATIONALLY VERIFIED**

The Foundation MVP is the validated deterministic execution baseline of LOOPRA. It provides reliable content lifecycle primitives that future stages will wrap with intelligence, autonomy and continuous learning.

## 2.2. Verified Capabilities

| Capability | Scope |
|---|---|
| Domain entities | Project, Idea, Scenario, ContentItem, ExportPackage, Publication, MetricSnapshot |
| Lifecycle services | ProjectService, IdeaService, ScenarioService, ProductionService, PublishingService, AnalyticsService |
| Filesystem repositories | JSON-record persistence, project-scoped storage |
| Smoke loop | `python scripts/smoke_loop.py` -- full lifecycle verification |
| Export package | Inspection and validation via `inspect_package.py`, `validate_package.py` |
| Manual publication | Human publishes externally; system records Publication outcome |
| Manual metrics | `find_metric_snapshots.py`, `import_manual_metrics.py` |
| Content types | `text_social_post` only |
| Testing | Domain tests, service tests, runtime loop tests |
| Operational docs | Runbook, agent operating model, release/change management |

## 2.3. Foundation MVP Chain

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

This chain is the canonical execution backbone. Future stages do not replace it -- they wrap it with intelligence, automation and learning.

## 2.4. Current Constraints (by Design)

- No API.
- No UI.
- No database.
- No external integrations.
- No autoposting.
- No internal autonomous runtime agent.
- Manual publication only.
- Manual metrics only.
- `text_social_post` only.
- Local filesystem storage.
- Deterministic services/tools only.
- Copilot mode only.

## 2.5. Validated Principles

- Project-agnostic architecture.
- Strict separation of foundation and project configuration.
- Filesystem-first approach.
- Controlled development process.
- Documentation as source of truth.
- Foundation First development philosophy.

---

# 3. North Star

## 3.1. End Goal

LOOPRA as a fully operational **Autonomous Marketing Operating System**:

```text
Workspace
    ↓
Brand System
    ↓
Content Cycle
    ↓
Orchestrator Agent
    ↓
Intelligence Modules (Trend, Content, Analytics)
    ↓
Production Tools
    ↓
Distribution (Manual + Connector)
    ↓
Analytics (Manual + Automated)
    ↓
Learning Memory
    ↓
Next Cycle (improved)
```

## 3.2. Core Characteristics

- **Cycle-based**, not hidden 24/7 continuous background thinking.
- **Human-governed autonomy** -- human sets direction, rules and boundaries; the system operates within them.
- **Agents decide. Tools execute.** -- Orchestrator Agent coordinates; deterministic tools remain the execution core.
- **Continuous self-improvement** -- each completed cycle feeds the next with structured learning.
- **Project isolation** -- no cross-project data leakage; each brand operates in its own scoped environment.
- **Progressive autonomy** -- copilot → assisted → autopilot modes, always with emergency stop.

## 3.3. What the North Star Is NOT

- NOT a 24/7 agent swarm with uncontrolled decision-making.
- NOT a black-box AI that replaces the marketer.
- NOT a content generator tool.
- NOT a social media scheduler.
- NOT a SaaS dashboard with analytics widgets.

It is a **self-learning marketing operating system** where the human is the strategic operator, not the content creator.

---

# 4. Evolution Principles

1. **Foundation First.** Validate the current layer before building the next. No future features before current validation.

2. **Deterministic Core Before Autonomy.** Services, tools and repositories must be stable, tested and contract-documented before agents are introduced.

3. **Services Before API.** Service contracts (`SERVICE_CONTRACTS_SPEC.md`) define behaviour. External API wraps existing services -- it does not create new logic paths.

4. **Tools Before Agents.** Deterministic CLI tools and scripts must exist and be verified before an agent is allowed to invoke them.

5. **Manual Before Automated.** Every automated capability must have a working manual path first. The manual path validates correctness; automation adds speed and scale.

6. **Observability Before Autonomy.** Logs, error handling, audit trails and operational runbooks must exist before the system makes autonomous decisions.

7. **Approval Before External Action.** No content is published externally without human approval (or explicitly configured autopilot permission). No connector dispatches without an approval gate.

8. **Learning Memory After Analytics.** Analytics must produce reliable MetricSnapshots before Learning Memory attempts to extract patterns from them.

9. **Project Isolation Before Multi-Tenant SaaS.** Multi-project workspace operations must be clean, validated and leak-free before adding user accounts, billing and public onboarding.

10. **Security Boundary Before Connector.** Secrets management, credential boundaries and audit trails must be defined before any connector touches an external platform API.

---

# 5. Roadmap Overview

| Stage | Name | Goal | Status |
|---|---|---|---|
| 0 | Foundation MVP Complete | Validated deterministic content lifecycle | **Current** |
| 1 | Foundation Hardening | Stabilize, document, align | Next |
| 2 | Content Intelligence | Intelligence-supported idea generation | Future |
| 3 | Production Automation | Expand content types and production pipeline | Future |
| 4 | Runtime Command Layer | Structured runtime command contracts | Future |
| 5 | Learning Memory | Persist analytics learning into future cycles | Future |
| 6 | Orchestrator Agent | Introduce bounded product Orchestrator Agent | Future |
| 7 | Assisted Distribution and Connectors | Controlled connector-based publishing | Future |
| 8 | Analytics Automation | Automated metric collection with manual fallback | Future |
| 9 | Workspace / Multi-Project Platform | Operationalized multi-project workspace | Future |
| 10 | SaaS Platform | Public platform with API, UI, DB, auth | Future |

---

# 6. Stage 0 -- Foundation MVP Complete

## 6.1. Status: Current

## 6.2. What Exists

| Layer | Implemented |
|---|---|
| Domain | Project, Idea, Scenario, ContentItem, ExportPackage, Publication, MetricSnapshot entities with status enums and transition rules |
| Services | ProjectService, IdeaService, ScenarioService, ProductionService, PublishingService, AnalyticsService -- full lifecycle operations |
| Repositories | Filesystem JSON-record persistence, project-scoped storage |
| Runtime | `LoopOrchestrator` class, smoke loop script |
| Tools | `smoke_loop.py`, `inspect_package.py`, `validate_package.py`, `find_metric_snapshots.py`, `import_manual_metrics.py` |
| Export | `ExportPackage v1` -- `title.txt`, `body.txt`, `caption_{platform}.txt`, `manual_publication_checklist.txt`, `metadata.json`, `manifest.json` |
| Publication | Manual publication records with URL, timestamp, platform |
| Metrics | Draft `MetricSnapshot`, manual import, `clicks` → `link_clicks` normalization |
| Configuration | `project.yaml`, `ProjectConfig`, brand settings, channel settings |
| Tests | Domain tests (`tests/domain/`), service tests (`tests/services/`), runtime loop tests |
| Documentation | Full spec layer: foundation, product, architecture, intelligence, production, platform, operations |

## 6.3. Exit Criteria (Met)

- All domain and service tests pass.
- Smoke loop (`smoke_loop.py`) completes successfully.
- Export package inspection and validation succeed.
- Manual metrics import path works.
- Foundation MVP marked READY + OPERATIONALLY VERIFIED in `STATE.md`.
- No Content Plant active naming remains in docs, code, or config.
- Documentation index (`DOCUMENTATION_INDEX.md`) references active specification set.

---

# 7. Stage 1 -- Foundation Hardening

## 7.1. Goal

Stabilize the current foundation before adding complexity. Ensure documentation, code, tests and operational procedures are clean, consistent and aligned.

## 7.2. Status: Future (Next Priority)

## 7.3. Key Capabilities

| Capability | Description |
|---|---|
| Service cleanup | Remove dead code paths, ensure all public methods are contract-documented |
| CLI output consistency | Standardize output format across all scripts |
| Optional JSON output mode | Machine-parseable output for future agent consumption |
| Docs index completeness | All active specs listed in `DOCUMENTATION_INDEX.md` with correct statuses |
| Doc/code consistency | Verify spec claims match actual code behaviour |
| Terminology alignment | No remaining Content Plant naming in any active document |
| Operational acceptance | Run full operational acceptance from `OPERATIONAL_RUNBOOK.md` |
| STATE.md update | Reflect hardening completion |

## 7.4. Dependencies

- Stage 0 complete.

## 7.5. Boundaries

- **No API/UI/DB.** Hardening addresses existing capabilities only.
- **No new domain entities.**
- **No external integrations.**
- **No agent logic.**

## 7.6. Exit Criteria

- `DOCUMENTATION_INDEX.md` references all active docs with correct statuses.
- All domain and service tests pass.
- Smoke loop passes.
- No stale Content Plant active naming anywhere.
- No duplicated or conflicting specs.
- Operational runbook verified (all procedures produce expected results).
- CLI output consistent across all tools.
- `STATE.md` updated to reflect Stage 1 completion.

---

# 8. Stage 2 -- Content Intelligence

## 8.1. Goal

Move beyond manually provided ideas into intelligence-supported idea generation. Allow LOOPRA to propose content opportunities based on structured inputs -- without autoposting, external scraping or autonomous execution.

## 8.2. Status: Future

## 8.3. Key Capabilities

| Capability | Description |
|---|---|
| Trend input records | Structured `MarketSignal` and `TrendPattern` records for manual/scoped input |
| Opportunity model | `ContentOpportunity` entity linking trend + brand context + goal |
| Idea scoring | Basic relevance scoring against Brand System, goals and Learning Memory (if available) |
| Content pillar mapping | Map opportunities to defined content pillars from Brand System |
| NURA validation | Use NURA project to validate intelligence-driven idea creation |

## 8.4. Dependencies

- Stage 1 complete (Foundation Hardening).
- `AGENT_SYSTEM_SPEC.md` -- Orchestrator Agent and Intelligence Module design.
- `CONTENT_CYCLE_SPEC.md` -- Stages 1-4 (Market Signal → Strategic Decision).
- `DATA_MODEL.md` -- Future entities: `MarketSignal`, `TrendPattern`, `ContentInsight`.
- `BRAND_SYSTEM_SPEC.md` -- Brand identity and content strategy for mapping.

## 8.5. Boundaries

- Intelligence **proposes**; human **approves**.
- No external scraping or API-based trend detection unless separately approved.
- No autonomous idea-to-execution pipeline.
- Current services (`IdeaService`, `ScenarioService`) remain unchanged in their contracts.
- No autoposting.

## 8.6. Exit Criteria

- `Idea` creation can be driven by structured `ContentOpportunity` input (not only manual).
- `ContentOpportunity` model exists with scoring, pillar mapping and brand alignment.
- Tests cover opportunity creation, scoring and brand alignment validation.
- NURA validation project demonstrates intelligence-driven idea flow.
- `STATE.md` updated.

---

# 9. Stage 3 -- Production Automation

## 9.1. Goal

Expand from `text_social_post` to richer content types and a structured production pipeline with quality assurance.

## 9.2. Status: Future

## 9.3. Key Capabilities

| Capability | Description |
|---|---|
| ProductionBrief | Formal operational instruction bridging Intelligence and Production |
| ProductionPlan | Structured execution roadmap for each content type |
| Content type routing | Route production to correct variant (carousel, short video, text post) |
| Asset Library integration | Brand assets, templates, media assets for production |
| QA model | Brand compliance, format validation, technical checks, content quality |
| New content types | At least one beyond `text_social_post` (e.g., `carousel` or `short_vertical_video`) |

## 9.4. Dependencies

- Stage 2 complete (Content Intelligence).
- `CONTENT_TYPES_SPEC.md` -- Content type structures and parameters.
- `PRODUCTION_PIPELINE_SPEC.md` -- Production Brief, Plan, QA, Assembly stages.
- `ASSET_LIBRARY_SPEC.md` -- Asset taxonomy, validation, selection model.

## 9.5. Boundaries

- Deterministic production tools only -- no autonomous production decisions.
- No autoposting.
- No external rendering dependency (AI image/video generation API) unless separately approved.
- ProductionPipeline does not make strategic decisions -- it executes what Intelligence defines.

## 9.6. Exit Criteria

- At least one new content type supported beyond `text_social_post`.
- `ExportPackage` validation updated for new content types.
- QA checks run as part of production flow.
- Tests cover new content type production, QA and export.
- `STATE.md` updated.

---

# 10. Stage 4 -- Runtime Command Layer

## 10.1. Goal

Convert CLI/service execution into explicit, structured runtime command contracts. Establish the foundation for future agent tool-calling without changing current behaviour.

## 10.2. Status: Future

## 10.3. Key Capabilities

| Capability | Description |
|---|---|
| RuntimeCommand model | Typed command definitions with inputs, outputs, preconditions, postconditions |
| Command registry | Central registry of all executable commands |
| Structured I/O | JSON input/output for every command |
| Resumable stage concept | Runtime stages with ability to pause, inspect and resume |
| Approval request concept | Structured approval request/response model before mutating operations |
| Command audit trail | Log of every command execution with timestamp, inputs, outputs, outcome |

## 10.4. Dependencies

- Stage 1 complete (Foundation Hardening). Stage 2-3 not required but beneficial.
- `RUNTIME_ORCHESTRATION_SPEC.md` -- Execution coordination model.
- `TOOLING_AND_CLI_SPEC.md` -- Current CLI tool contracts.
- `RELEASE_AND_CHANGE_MANAGEMENT.md` -- Change discipline for runtime.

## 10.5. Boundaries

- Commands wrap existing services and tools -- no new business logic.
- No agent autonomy yet.
- No background workers or schedulers.
- No external API calls.

## 10.6. Exit Criteria

- All current CLI tools mapped to `RuntimeCommand` definitions.
- Command registry operational with structured I/O.
- Tests cover command execution, error handling and audit trail.
- `STATE.md` updated.

---

# 11. Stage 5 -- Learning Memory

## 11.1. Goal

Persist structured learning from analytics back into future content cycles. Enable the system to remember what worked and what did not.

## 11.2. Status: Future

## 11.3. Key Capabilities

| Capability | Description |
|---|---|
| LearningMemoryRecord | Structured entity storing performance observations |
| Performance observations | Format effectiveness, hook performance, topic resonance, timing insights, CTA behaviour |
| Pattern extraction | Identify repeatable success/failure patterns across cycles |
| Content recommendations | Suggest format, tone, timing based on past performance |
| Confidence scoring | Score recommendations based on evidence strength and pattern similarity |
| Knowledge organization | By content pillar, audience segment, channel, format, goal, time period |

## 11.4. Dependencies

- Stage 3 complete (Production Automation) -- content types must exist for pattern extraction.
- Analytics layer producing reliable `MetricSnapshot` records.
- `AGENT_SYSTEM_SPEC.md` -- Learning Memory Module design.
- `CONTENT_CYCLE_SPEC.md` -- Stages 9-10 (Learning Memory Update, Optimization).
- `ANALYTICS_SPEC.md` -- Learning Memory Handoff payload.
- `DATA_MODEL.md` -- `LearningMemoryEntry` entity.

## 11.5. Boundaries

- Learning Memory **advises**; Orchestrator Agent (Stage 6) **uses** advice.
- Learning Memory does NOT override Brand System.
- Learning Memory optimizes WITHIN brand boundaries, not beyond them.
- No autonomous decision-making from Learning Memory alone.
- Project-scoped -- no cross-project knowledge sharing.

## 11.6. Exit Criteria

- `AnalyticsSummary` can produce `LearningMemoryRecord` entries.
- Future cycles can read structured learning context.
- Pattern extraction works for at least one content type and one goal.
- Confidence scoring attached to all recommendations.
- Tests cover record creation, retrieval, pattern extraction and boundary enforcement.
- `STATE.md` updated.

---

# 12. Stage 6 -- Orchestrator Agent

## 12.1. Goal

Introduce the product runtime Orchestrator Agent -- a bounded, tool-invoking coordinator that manages content cycles within defined safety boundaries.

## 12.2. Status: Future

## 12.3. Key Capabilities

| Capability | Description |
|---|---|
| Cycle planning | Read Brand System, Project Settings, Learning Memory; plan cycle stages |
| Tool request generation | Generate structured tool invocation requests from decisions |
| State reading | Read current entity states, cycle progress, pending approvals |
| Approval gate requests | Request human approval for decisions that require it per autonomy mode |
| Content cycle coordination | Manage progression through cycle stages: Signal → Idea → Scenario → Production → Distribution → Analytics → Learning |
| Decision recording | `AgentDecision` records with context, reasoning, confidence, expected vs actual outcome |
| Confidence-based escalation | Escalate low-confidence decisions to human operator |

## 12.4. Dependencies

- Stage 4 complete (Runtime Command Layer) -- commands must exist for agent to invoke.
- Stage 5 complete (Learning Memory) -- agent needs learning context for decisions.
- `AGENT_SYSTEM_SPEC.md` -- Full Orchestrator Agent design.
- `SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` -- Agent safety boundaries.
- `AGENT_OPERATING_MODEL.md` -- Agent governance and interaction rules.

## 12.5. Boundaries

- **No direct storage writes.** Agent invokes services; services write.
- **No arbitrary shell.** Agent invokes registered commands only.
- **No external publishing without approval.** Distribution commands require approval gates.
- **No autonomy escalation.** Agent cannot increase its own autonomy level.
- **No cross-project action.** Agent is project-scoped.
- Copilot mode only unless explicitly configured otherwise.

## 12.6. Exit Criteria

- Orchestrator can run a bounded content cycle in copilot mode (every decision requires human approval).
- Complete audit trail exists for every agent decision.
- Agent safety tests pass: cannot bypass restrictions, cannot escalate autonomy, cannot write outside project scope.
- Agent operates within defined confidence boundaries.
- `STATE.md` updated.

---

# 13. Stage 7 -- Assisted Distribution and Connectors

## 13.1. Goal

Introduce controlled connector-based publishing. LOOPRA can publish to external platforms through configured connectors -- with mandatory approval gates, preflight checks and safety boundaries.

## 13.2. Status: Future

## 13.3. Key Capabilities

| Capability | Description |
|---|---|
| Connector config | Platform connector configuration per channel in Project Settings |
| Secret manager boundary | Credentials stored separately from project config; never leaked to logs, prompts or exports |
| Publication preflight | Pre-publish checks: channel enabled, content adapted, QA passed, approval obtained |
| Connector dry-run | Validate connector config and authentication without publishing |
| Approval gate | Mandatory human approval before connector dispatch (copilot/assisted modes) |
| Publication attempt records | Each connector dispatch logged as `PublicationAttempt` with result, error, retry |
| Emergency stop | Human can halt any connector dispatch at any time |

## 13.4. Dependencies

- Stage 6 complete (Orchestrator Agent) -- agent coordinates distribution decisions.
- `DISTRIBUTION_SPEC.md` -- Connector mode definition, preflight, approval gates.
- `SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` -- Connector safety boundaries.
- `CONFIGURATION_AND_ENVIRONMENT_SPEC.md` -- Secrets boundary, env var policy.
- Secret manager or credential boundary implemented.

## 13.5. Boundaries

- **No connector before secrets spec.** Credential management must be defined first.
- **No autoposting without approval rules.** Connector only dispatches after explicit approval (copilot/assisted) or configured autopilot permission.
- **Emergency stop required.** Every connector action must be interruptible.
- **No connector that bypasses QA.** Content must pass Production QA and Distribution preflight before connector dispatch.
- One connector first; validate the model before adding more.

## 13.6. Exit Criteria

- At least one platform connector works in assisted/manual-approved mode.
- Publication preflight checks pass/fail correctly.
- Connector dry-run works without side effects.
- Failure handling tested: auth failure, API error, rate limit, timeout.
- No secret leakage in logs, exports, agent prompts or audit trails.
- Emergency stop verified.
- `STATE.md` updated.

---

# 14. Stage 8 -- Analytics Automation

## 14.1. Goal

Automate metric collection while preserving manual fallback. Connectors pull performance data from platforms; normalization produces reliable MetricSnapshots.

## 14.2. Status: Future

## 14.3. Key Capabilities

| Capability | Description |
|---|---|
| Connector metric pull | Platform connector retrieves post metrics via platform API |
| RawMetricRecord | Separate entity for platform-specific raw metric data |
| Normalization | Platform-specific metrics → standardized categories (reach, engagement, attention, conversion, negative, operational) |
| Freshness tracking | Metric collection timestamps, collection window start/end |
| Provenance | Source type recorded (manual, connector, import, hybrid) with confidence |
| Analytics summaries | Automated `AnalyticsSummary` generation with performance evaluation against goals |
| Manual fallback | Manual metric entry remains available alongside connector collection |

## 14.4. Dependencies

- Stage 7 complete (Assisted Distribution and Connectors) -- connector infrastructure exists.
- `ANALYTICS_SPEC.md` -- Connector mode, normalization, MetricSnapshot, derived metrics.
- `LEARNING_MEMORY_SPEC.md` -- Handoff payload from Analytics to Learning Memory.

## 14.5. Boundaries

- **Metrics connector is read-only.** Never publishes, never modifies platform data.
- **Credentials scoped.** Metrics-only API access; no publish permissions on analytics credentials.
- **Manual import remains available.** Connector automation is additive, not replacement.
- **Normalization preserves raw data.** Platform-specific values are not discarded.

## 14.6. Exit Criteria

- At least one platform metric connector works (mock or live safe mode).
- `MetricSnapshot` can be populated from connector data.
- Normalization correctly maps platform-specific metrics to standard categories.
- Tests cover normalization, connector error handling, freshness tracking.
- Manual import path still works alongside connector collection.
- `STATE.md` updated.

---

# 15. Stage 9 -- Workspace / Multi-Project Platform

## 15.1. Goal

Turn the project-scoped MVP into a workspace-based platform. Multiple projects operate in clean isolation under one workspace with shared services.

## 15.2. Status: Future

## 15.3. Key Capabilities

| Capability | Description |
|---|---|
| Workspace model operationalized | `Workspace` entity active with multiple `Project` references |
| Multi-project management | Create, list, switch, archive projects within a workspace |
| Workspace-level settings | Global defaults across projects (optional override per project) |
| Project isolation | No cross-project data access, storage leakage or entity reference crossing |
| Shared Asset Library | Assets scoped per project; templates may be workspace-level (project-neutral) |
| Workspace analytics | Cross-project performance view (aggregation without data mixing) |

## 15.4. Dependencies

- Stages 0-8 complete or sufficiently stable.
- `PROJECT_SETTINGS_SPEC.md` -- Workspace and project model.
- `WORKSPACE_AND_PROJECT_MODEL.md` -- Workspace architecture.
- `STORAGE_AND_STATE_SPEC.md` -- Project-scoped storage model.

## 15.5. Boundaries

- **No SaaS auth until Stage 10.** Workspace operates in local/admin mode.
- **No user roles or permissions.**
- **No billing or subscription tiers.**
- **No public onboarding.**

## 15.6. Exit Criteria

- Multiple projects managed cleanly within one workspace.
- No cross-project data leakage (verified by tests).
- Workspace-level operations tested: create project, switch context, list projects, archive.
- Cross-project analytics view works without data mixing.
- `STATE.md` updated.

---

# 16. Stage 10 -- SaaS Platform

## 16.1. Goal

Deploy LOOPRA as a public platform. API, UI, database, authentication, multi-tenancy, billing and production infrastructure.

## 16.2. Status: Future (Distant)

## 16.3. Key Capabilities

| Capability | Description |
|---|---|
| API | REST or GraphQL API wrapping service contracts |
| UI | Workflow-first interface, not decorative dashboard |
| Database | PostgreSQL with migration path |
| Authentication | User accounts, sessions, password/SSO |
| Roles and permissions | Owner, admin, editor, viewer per workspace/project |
| Billing | Subscription tiers, plan limits, payment integration |
| Deployment pipeline | CI/CD, staging environment, production deployment |
| Monitoring | Application logs, metrics dashboard, alerts, trace IDs |
| Tenant isolation | Multi-tenant storage separation, database isolation |
| Backup/restore | Regular automated backup, disaster recovery |
| Onboarding | Public registration, workspace creation wizard |

## 16.4. Dependencies

- Stage 9 complete (Workspace / Multi-Project Platform).
- All previous stages validated.
- Architecture proven in local mode before SaaS deployment.
- `SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` -- Auth, tenancy, access control.
- `CONFIGURATION_AND_ENVIRONMENT_SPEC.md` -- Deployment configuration.

## 16.5. Boundaries

- **Only after local architecture is proven.** Do not deploy SaaS before the system works correctly in local/admin mode.
- **Production security required.** Auth, encryption, secret management, audit logging must be implemented.
- **CI/CD required.** No manual production deployments.
- **Backup/restore required.** No production data without recovery path.

## 16.6. Exit Criteria

- Production-ready platform checklist completed.
- All services accessible via API.
- UI operational with workflow-first design.
- Multi-tenant isolation verified.
- Billing system functional.
- Backup/restore tested.
- Monitoring and alerting active.
- Security review passed.

---

# 17. Dependency Map

| Capability | Requires | Must Not Start Before |
|---|---|---|
| Content Intelligence (Stage 2) | Foundation Hardening (Stage 1) | Intelligence specs defined; Brand System spec stable |
| Production Automation (Stage 3) | Content Intelligence (Stage 2) | Content type specs + QA model defined |
| Runtime Command Layer (Stage 4) | Foundation Hardening (Stage 1) | Service contracts stable; CLI tools mapped |
| Learning Memory (Stage 5) | Production Automation (Stage 3) | Analytics producing reliable MetricSnapshots |
| Orchestrator Agent (Stage 6) | Runtime Commands (Stage 4) + Learning Memory (Stage 5) | Command registry exists; learning records available |
| Connectors (Stage 7) | Orchestrator Agent (Stage 6) | Secrets spec defined; approval gates operational |
| Analytics Automation (Stage 8) | Connectors (Stage 7) | Connector infrastructure exists; read-only API access |
| Multi-Project Platform (Stage 9) | Stages 0-8 stable | Workspace model tested with 2+ projects |
| SaaS Platform (Stage 10) | Multi-Project Platform (Stage 9) | Architecture proven locally; security baseline defined |

## 17.1. Cross-Cutting Dependency Rules

- **Connectors require secret manager.** No connector before credential boundary is defined.
- **Agent autonomy requires audit + approval gates.** No autonomous decisions without complete audit trail and human override capability.
- **SaaS requires DB + auth + security.** No public deployment without authentication, authorization and encryption.
- **Learning Memory requires analytics summaries.** No pattern extraction from unreliable or incomplete data.
- **Production automation requires content type spec + QA.** No new content types without defined structure and quality checks.
- **Autoposting requires approval rules + emergency stop.** No connector dispatch without human control points.

---

# 18. Validation Gates by Stage

| Gate | Stage 0 | Stage 1 | Stage 2-3 | Stage 4-5 | Stage 6-8 | Stage 9-10 |
|---|---|---|---|---|---|---|
| Domain tests pass | Yes | Yes | Yes | Yes | Yes | Yes |
| Service tests pass | Yes | Yes | Yes | Yes | Yes | Yes |
| Smoke loop passes | Yes | Yes | Yes | Yes | Yes | Yes |
| Docs index complete | -- | Yes | Yes | Yes | Yes | Yes |
| Operational acceptance | Yes | Yes | Yes | Yes | Yes | Yes |
| No stale naming | Yes | Yes | Yes | Yes | Yes | Yes |
| No duplicated specs | Yes | Yes | Yes | Yes | Yes | Yes |
| Runbook verified | Yes | Yes | Yes | Yes | Yes | Yes |
| Security review | -- | -- | -- | Yes (Stage 6+) | Yes | Yes |
| Agent safety tests | -- | -- | -- | -- | Yes | Yes |
| Connector safety tests | -- | -- | -- | -- | Yes (Stage 7+) | Yes |
| Project isolation tests | Yes | Yes | Yes | Yes | Yes | Yes |
| Multi-project tests | -- | -- | -- | -- | -- | Yes |
| STATE.md updated | Yes | Yes | Yes | Yes | Yes | Yes |

---

# 19. Risk Map

| Risk | Severity | Mitigation |
|---|---|---|
| **Overbuilding UI/API too early** | High | No UI/API until Stage 10. Service contracts define behaviour; UI/API wrap services later. |
| **Adding agents before tools** | High | Stage 4 (Runtime Commands) required before Stage 6 (Orchestrator Agent). Agents only invoke registered, tested commands. |
| **Adding connectors before secrets** | Critical | No connector dispatch until secrets boundary is defined and implemented. Stage 7 explicit dependency. |
| **Autoposting before approval gates** | Critical | No connector publishing without mandatory approval (copilot/assisted) or explicit autopilot configuration with emergency stop. |
| **Database before service contracts stabilize** | Medium | Filesystem repositories allow fast iteration. DB migration is deferred until service contracts are stable and verified. |
| **Project-specific logic leaking into core** | High | All platform docs forbid project-specific hardcoding. NURA validation project rules enforced (Section 21). |
| **Current/future confusion** | High | Every stage explicitly marks current vs future. No document claims future capability as current. `STATE.md` is the canonical current-state source. |
| **Learning Memory overriding Brand System** | Medium | Learning Memory optimizes within brand boundaries. BRAND_SYSTEM_SPEC.md rules are inviolable. Tests verify boundary enforcement. |
| **Agent autonomy escalation** | Critical | Orchestrator Agent cannot increase its own autonomy level. Human-only control. Tested in agent safety suite. |
| **Cross-project data leakage** | High | Every entity carries `project_id`. Services validate scope. Storage paths are project-scoped. Multi-project tests verify isolation. |
| **SaaS deployment before local validation** | High | Stage 10 only after all prior stages validated in local mode. Production security baseline must exist. |

---

# 20. What Must NOT Be Built Yet

The following capabilities are explicitly excluded from current and near-term stages. They may only be introduced when their prerequisite stage begins:

| Capability | Earliest Stage | Prerequisite |
|---|---|---|
| API | Stage 10 | Service contracts stable (Stage 4+); architecture proven locally |
| UI | Stage 10 | API operational; workflow-first design defined |
| Database | Stage 10 | Filesystem repos sufficient until multi-tenancy required |
| SaaS authentication | Stage 10 | Multi-project platform operational (Stage 9) |
| Billing | Stage 10 | SaaS platform with user accounts |
| Platform connectors | Stage 7 | Secrets boundary; approval gates; emergency stop |
| Autoposting | Stage 7 | Connectors + approval rules + emergency stop |
| Scheduler / background workers | Stage 4 (conceptual) / Stage 6 (active) | Command registry; agent coordination |
| Marketplace | Stage 10 | SaaS platform with multi-tenancy |
| Internal autonomous agent | Stage 6 | Command registry + Learning Memory + safety boundaries |
| 24/7 continuous thinking agent | Never (by design) | LOOPRA is cycle-based, not continuous background inference |
| External analytics APIs | Stage 8 | Connector infrastructure; read-only credentials |
| AI image/video generation | Stage 3 (optional, separately approved) | External rendering dependency requires explicit approval |
| Multi-user teams | Stage 10 | Auth + roles + permissions |

---

# 21. NURA as Validation Project

## 21.1. Role

NURA serves as the **validation project** for LOOPRA. It provides a real-world project context to test and validate LOOPRA capabilities without polluting the platform core.

## 21.2. Allowed

- Project configuration under `projects/nura/` and `docs/07_projects/nura/`.
- Validation plans and test scenarios using NURA brand context.
- Content tests that exercise the LOOPRA lifecycle with NURA as the project.
- NURA-specific Brand System, content pillars, channels and goals in project-scoped files.

## 21.3. Not Allowed

- Hardcoded NURA brand references in core platform code.
- NURA-only service logic or branching in core services.
- NURA-specific assumptions in platform-level specification documents.
- NURA brand elements leaking into generic platform docs (except as examples explicitly marked as NURA-specific).
- NURA configuration treated as platform default.

## 21.4. Validation Scope by Stage

| Stage | NURA Validation |
|---|---|
| Stage 0 (Current) | Smoke loop with NURA project context |
| Stage 2 (Content Intelligence) | Intelligence-driven idea creation for NURA content pillars |
| Stage 3 (Production Automation) | Multi-format content production using NURA brand context |
| Stage 6 (Orchestrator Agent) | Bounded content cycle for NURA in copilot mode |
| Stage 7 (Assisted Distribution) | Connector-based publishing for NURA channels |
| Stage 8 (Analytics Automation) | Automated metric collection for NURA publications |

---

# 22. Stage Transition Rules

Before moving from one stage to the next, all of the following must be satisfied:

1. **Current stage exit criteria met.** All gates defined for the current stage pass.
2. **Tests pass.** Full test suite (domain, services, relevant stage-specific tests) green.
3. **Smoke loop passes.** `smoke_loop.py` completes without errors.
4. **Docs updated.** All affected specification documents reflect current state.
5. **STATE.md updated.** Current phase, completed stage and next direction recorded.
6. **Human approval.** Stage transition explicitly approved by the human operator.
7. **No unresolved architectural contradictions.** No conflicting specs, no duplicated capability claims, no current/future mixing.
8. **Dependencies verified.** All prerequisite stages confirmed complete and stable.

---

# 23. Roadmap Tracking Model

## 23.1. Current Tracking (Manual)

| Artifact | Purpose |
|---|---|
| `STATE.md` | Canonical current state -- phase, completed capabilities, active boundaries |
| `docs/08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md` | This document -- stage definitions, criteria, dependencies |
| `RELEASE_AND_CHANGE_MANAGEMENT.md` | How changes are proposed, executed, verified and committed |
| `AGENT_OPERATING_MODEL.md` | How human + AI agents interact during development |
| `OPERATIONAL_RUNBOOK.md` | How to operate and verify the current system |

No Jira/Linear/issue tracker is assumed. Current tracking is document-driven.

## 23.2. Future Tracking (Stage 4+)

- Roadmap board (visual stage overview with current progress).
- Milestone tags on commits or PRs.
- Release notes per stage completion.
- Automated doc consistency checks (conceptual, not yet implemented).

---

# 24. Related Documents

## 24.1. Governance

- `AGENTS.md` -- Development rules for AI coding agents.
- `STATE.md` -- Current project state and phase.

## 24.2. Foundation Layer

- `docs/00_foundation/DATA_MODEL.md` -- Foundation data model and entity chain.
- `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` -- Project configuration specification.
- `docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md` -- Workspace and project model.
- `docs/02_architecture/PLATFORM_OVERVIEW.md` -- Platform overview.
- `docs/00_foundation/MVP_SCOPE.md` -- Foundation MVP scope.

## 24.3. Product Layer

- `docs/01_product/USER_WORKFLOWS.md` -- User interaction model and workflows.
- `docs/01_product/LOOPRA_BRAND_POSITIONING.md` -- LOOPRA product identity.

## 24.4. Architecture Layer

- `docs/02_architecture/SYSTEM_ARCHITECTURE.md` -- System architecture layers.
- `docs/02_architecture/LOOPRA_ARCHITECTURE.md` -- Core architecture direction.
- `docs/02_architecture/BRAND_SYSTEM_SPEC.md` -- Brand System specification.
- `docs/02_architecture/PIPELINES_SPEC.md` -- Content lifecycle pipeline stages.

## 24.5. Intelligence Layer

- `docs/03_intelligence/AGENT_SYSTEM_SPEC.md` -- Orchestrator Agent and Intelligence Module design.
- `docs/03_intelligence/CONTENT_CYCLE_SPEC.md` -- Full content cycle specification.

## 24.6. Production Layer

- `docs/04_production/CONTENT_TYPES_SPEC.md` -- Content type definitions and production model.
- `docs/04_production/PRODUCTION_PIPELINE_SPEC.md` -- Production pipeline and QA.
- `docs/04_production/ASSET_LIBRARY_SPEC.md` -- Asset library and selection model.
- `docs/04_production/DISTRIBUTION_SPEC.md` -- Distribution and publication boundary.
- `docs/04_production/ANALYTICS_SPEC.md` -- Analytics layer and metric model.
- `docs/04_production/CONTENT_TYPES_SPEC.md` -- Current format portfolio.

## 24.7. Platform Layer

- `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` -- Runtime execution coordination.
- `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` -- Service operation contracts.
- `docs/05_platform/TOOLING_AND_CLI_SPEC.md` -- CLI tools and execution helpers.
- `docs/05_platform/STORAGE_AND_STATE_SPEC.md` -- Storage model and state persistence.
- `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` -- Configuration hierarchy.
- `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` -- Testing and validation model.
- `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` -- Security and safety boundaries.

## 24.8. Operations Layer

- `docs/06_operations/OPERATIONAL_RUNBOOK.md` -- Practical operations guide.
- `docs/06_operations/AGENT_OPERATING_MODEL.md` -- Human + AI agent operating model.
- `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` -- Change governance and release discipline.

## 24.9. Projects

- `docs/07_projects/nura/` -- NURA validation project configuration.

---

# 25. Document Status

| Field | Value |
|---|---|
| Status | Active -- LOOPRA Roadmap Layer |
| Version | v1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA -- Autonomous Marketing Operating System |
| Layer | Roadmap Layer -- MVP to Autonomous OS Roadmap |

---

## Stage 2 Progress Update

Stage 2 has begun with two bounded, implemented slices: Slice 1 (Content Intelligence Foundation) and Slice 2 (Content Intelligence Hardening). Implemented scope is limited to manual, deterministic, filesystem-first records, explicit review and lifecycle paths, and approved opportunity-to-Idea conversion.

Not yet implemented:

- external trend collection;
- autonomous Content Intelligence;
- Orchestrator Agent runtime;
- Learning Memory;
- API/UI/database/platform automation.

Further Stage 2 slices remain gated. The current priority remains Stage 1 Foundation Hardening through small bounded improvements such as operational documentation consistency checks.

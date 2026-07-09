# DOCUMENTATION INDEX

## Version

v1.0

## Status

Active — LOOPRA Documentation Layer

## Purpose

This document is the single navigational index for all active LOOPRA documentation. It answers:

1. Which documents exist?
2. Which layer does each document belong to?
3. What is the status of each document?
4. What is each document responsible for?
5. Which documents are source of truth?
6. Which documents relate to the current MVP?
7. Which documents describe future/conceptual evolution?
8. Which documents should be read before different types of tasks?

---

## 1. Purpose and Scope

### 1.1. Purpose

The DOCUMENTATION_INDEX.md serves as the entry point for navigating the LOOPRA documentation landscape. It maps every active document to its layer, status, purpose, and relationship to the current Foundation MVP or future architecture.

### 1.2. Who Uses This Index

- AI coding agents working on LOOPRA;
- developers onboarding to the project;
- architects verifying design consistency;
- operators maintaining the Foundation MVP;
- project maintainers tracking documentation health.

### 1.3. What Is Included

- All active documents under `docs/00_foundation/` through `docs/08_roadmap/`;
- The root-level `AGENTS.md` and `STATE.md`;
- Archived/legacy documents in `docs/archive/`;


### 1.4. What Is Not Included

- Source code files;
- Runtime artifacts under `storage/`;
- Project configuration under `projects/`;
- Future documents that do not yet exist on disk.

---

## 2. Documentation Principles

1. **Docs are source of truth.** When architecture changes, documentation must be updated. Code behaviour is ground truth for the current implementation.
2. **Current vs future separation.** Every document must be clearly classifiable as describing the current MVP (implemented and verified) or future/conceptual evolution (specified but not implemented).
3. **LOOPRA is the active project name.** Content Plant is a historical name only. Active documents must use LOOPRA. Historical references to Content Plant belong in `docs/archive/` or transition documents.
4. **Project-specific docs stay in `docs/07_projects/`.** Project configuration and brand-specific documentation must not leak into platform-level docs.
5. **Platform docs stay project-agnostic.** No hardcoded brands, customer-specific workflows, or project-specific prompts in core/platform documentation.
6. **Code behaviour is ground truth for current implementation.** Specs that describe implemented functionality must match the actual code. Specs that describe future functionality must be marked as future/conceptual.

---

## 3. Layer Overview

| Layer Folder | Purpose | Status |
|---|---|---|
| `00_foundation/` | Foundation models, MVP scope, developer quickstart | Active — Current MVP |
| `01_product/` | Product identity, brand positioning, transition plan, user workflows | Active — Product Strategy |
| `02_architecture/` | System architecture, brand system, pipelines, platform overview | Active — Architecture Baseline |
| `03_intelligence/` | Agent system, content cycle, content intelligence, trend intelligence, learning memory | Active — Future / Conceptual Blueprint |
| `04_production/` | Production pipeline, content types, asset library, distribution, analytics | Active — Current + Future Mixed |
| `05_platform/` | Runtime orchestration, service contracts, tooling/CLI, storage/state, configuration, testing, security | Active — Current MVP Platform Specs |
| `06_operations/` | Operational runbook, agent operating model, release and change management | Active — Operations Governance |
| `07_projects/` | Project-specific documentation (NURA validation project) | Active — Project-Scoped |
| `08_roadmap/` | MVP-to-Autonomous-OS evolution roadmap | Active — Future Planning |
| `archive/` | Historical Content Plant era documents | Archived — Reference Only |

---

## 4. Foundation Layer Documents

### `docs/00_foundation/`

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `MVP_SCOPE.md` | Active | Defines the current minimal Foundation MVP: scope, boundaries, constraints, and what is excluded | Current | Primary source of truth for MVP boundaries |
| `DATA_MODEL.md` | Active | Describes the core data model: entities (Project, Idea, Scenario, ContentItem, ExportPackage, Publication, MetricSnapshot), relationships, ownership boundaries | Current | Primary source of truth for domain entities and relationships |
| `WORKSPACE_AND_PROJECT_MODEL.md` | Active | Defines multi-project architecture: Workspace, Project, Brand Profile, storage separation, platform vs project boundaries | Current | Primary source of truth for workspace/project model |
| `PROJECT_SETTINGS_SPEC.md` | Active (v2.0) | Defines Project Settings — the structured configuration LOOPRA requires to operate autonomous marketing cycles for a specific project | Current | Primary source of truth for project configuration schema |
| `DEVELOPER_QUICKSTART.md` | Active (v1.0) | Developer onboarding: project setup, tests, smoke loop, package inspection, manual metrics workflow | Current | Primary source of truth for developer setup and workflow |

---

## 5. Product Layer Documents

### `docs/01_product/`

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `LOOPRA_BRAND_POSITIONING.md` | Active (v1.0) | Brand identity, mission, positioning as Autonomous Marketing OS | Current | Primary source of truth for LOOPRA brand identity |
| `LOOPRA_TRANSITION_PLAN.md` | Active (v1.0) | Transition from Content Plant to LOOPRA: decisions, scope, migration rules, naming conventions | Current | Primary source of truth for the LOOPRA rebrand and transition |
| `USER_WORKFLOWS.md` | Active (v1.0) | Defines how a user interacts with LOOPRA — setup, daily operation, human-AI collaboration, autonomy governance | Conceptual (describes future product interaction model, not current CLI-only MVP) | Primary source of truth for user interaction model and product workflows |

---

## 6. Architecture Layer Documents

### `docs/02_architecture/`

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `LOOPRA_ARCHITECTURE.md` | Active (v1.0) | Core architectural direction: product vision, growth loop concept, architectural layers, module ownership | Current + Future | Primary source of truth for LOOPRA architecture direction |
| `BRAND_SYSTEM_SPEC.md` | Active (v2.0) | Brand System as the fundamental operational knowledge layer: identity, audience, communication rules, content strategy, business goals | Current + Future (spec exists; full runtime integration is future) | Primary source of truth for Brand System architecture |
| `PIPELINES_SPEC.md` | Active | Documents the current helper-supported local/manual pipeline for the Foundation MVP: Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot | Current | Primary source of truth for current pipeline stages |
| `PLATFORM_OVERVIEW.md` | Active | Top-level platform description: what LOOPRA is, foundation loop, MVP boundaries, module ownership, platform vs project layer | Current | Primary source of truth for platform-level overview |
| `SYSTEM_ARCHITECTURE.md` | Active (v2.0) | System architecture: architectural layers, component interactions, Workspace, Brand System, Content Cycle, Orchestrator Agent, current MVP scope and future direction | Current + Future | Primary source of truth for system architecture |

---

## 7. Intelligence Layer Documents

### `docs/03_intelligence/`

All documents in this layer are **Active specifications** but describe **Future/Conceptual** capabilities. No runtime agent or autonomous intelligence system is implemented in the current Foundation MVP.

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `AGENT_SYSTEM_SPEC.md` | Active (v1.0) | Functional architecture of the LOOPRA Agent System: Orchestrator Agent, Intelligence Modules, agent-tool interaction, decision-making layer | Future (no runtime agent in current MVP) | Source of truth for future agent system design |
| `CONTENT_CYCLE_SPEC.md` | Active (v1.0) | The LOOPRA Content Cycle — primary operational model: stages, component responsibilities, inputs/outputs, transitions, learning feedback | Future (no autonomous cycle in current MVP) | Source of truth for future content cycle design |
| `CONTENT_INTELLIGENCE_SPEC.md` | Active (v1.0) | Content Intelligence Module: strategic content selection, trend-to-content transformation, format selection, opportunity analysis | Future (no content intelligence in current MVP) | Source of truth for future content intelligence design |
| `LEARNING_MEMORY_SPEC.md` | Active (v1.0) | Learning Memory: accumulated operational experience, feedback loops, improvement tracking, knowledge accumulation across cycles | Future (no learning memory in current MVP) | Source of truth for future learning memory design |
| `TREND_INTELLIGENCE_SPEC.md` | Active (v1.0) | Trend Intelligence Module: market signal capture, signal processing, trend detection, opportunity generation | Future (no trend intelligence in current MVP) | Source of truth for future trend intelligence design |

---

## 8. Production Layer Documents

### `docs/04_production/`

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `ANALYTICS_SPEC.md` | Active (v1.0) | Analytics Layer: MetricSnapshot model, performance interpretation, analytics handoff to Learning Memory | Current (manual MetricSnapshot exists) + Future (automated analytics, connectors) | Source of truth for analytics architecture |
| `ASSET_LIBRARY_SPEC.md` | Active (v1.0) | Asset Library: storage, classification, validation, selection, and reuse of assets for content production | Future (no asset library in current MVP) | Source of truth for future asset library design |
| `CONTENT_TYPES_SPEC.md` | Active (v1.0) | Production content types: supported formats (`text_social_post` is current), structural components, production parameters | Current (text_social_post) + Future (other format types) | Source of truth for content type specifications |
| `DISTRIBUTION_SPEC.md` | Active (v1.0) | Distribution/Publishing boundary: ExportPackage transformation, channel mapping, publication records | Current (manual publication) + Future (automated channel delivery) | Source of truth for distribution architecture |
| `PRODUCTION_PIPELINE_SPEC.md` | Active (v1.0) | Production Pipeline: from Content Decision/Scenario to verified Export Package ready for distribution | Future (full pipeline; only basic Scenario→ContentItem→ExportPackage flow exists in MVP) | Source of truth for future production pipeline design |

---

## 9. Platform Layer Documents

### `docs/05_platform/`

All documents in this layer describe the current Foundation MVP platform. Each bridges the specification with actual code behaviour.

| Document | Status | Purpose | Current or Future | Source-of-Truth Area | Related Code/Runtime Area |
|---|---|---|---|---|---|
| `RUNTIME_ORCHESTRATION_SPEC.md` | Active (v1.0) | Runtime Orchestration Layer: execution coordination binding services, tools, scripts into coherent execution flow | Current | How the platform executes the architecture lifecycle | `core/services/`, CLI scripts, runtime orchestration |
| `SERVICE_CONTRACTS_SPEC.md` | Active (v1.0) | Service Contracts: every service operation, input/output, domain transitions, error handling, current vs future methods | Current | What services expose and how they behave | `core/services/` (all service implementations) |
| `TOOLING_AND_CLI_SPEC.md` | Active (v1.0) | Tooling and CLI Layer: deterministic CLI tools, scripts, execution helpers, manual operator workflows | Current | How CLI tools work and what they do | CLI scripts, validation helpers, manual operator workflows |
| `STORAGE_AND_STATE_SPEC.md` | Active (v1.0) | Storage and State Layer: filesystem repositories, project configuration storage, runtime artifacts, export packages, metric snapshots | Current | Where and how LOOPRA stores state | `storage/`, filesystem repositories, project config |
| `CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | Active (v1.0) | Configuration and Environment: project settings, runtime config, environment variables, modes (local/dev/test/smoke), future secrets | Current | How configuration and environment variables are handled | `project.yaml`, `ProjectConfig`, environment, runtime roots |
| `TESTING_AND_VALIDATION_SPEC.md` | Active (v1.0) | Testing and Validation: domain tests, service tests, smoke loop, export package validation, manual metrics workflow, operational acceptance | Current | How testing and validation are performed | `tests/`, domain tests, service tests, smoke loop, validation helpers |
| `SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` | Active (v1.0) | Security and Safety Boundaries: project isolation, path safety, storage mutation boundaries, service/tool invocation boundaries, human approval gates | Current | What safety boundaries protect the system | All runtime code, tools, services, config, storage |

---

## 10. Operations Layer Documents

### `docs/06_operations/`

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `OPERATIONAL_RUNBOOK.md` | Active (v1.0) | Practical operations guide: how to run, check, diagnose, and maintain the current Foundation MVP | Current | Primary source of truth for operational procedures |
| `AGENT_OPERATING_MODEL.md` | Active (v1.0) | Governance layer for human + AI agent collaboration during development, documentation, validation, and future runtime | Current (development governance) + Future (runtime agent model) | Primary source of truth for agent collaboration model |
| `RELEASE_AND_CHANGE_MANAGEMENT.md` | Active (v1.0) | Governance framework for safely managing changes to documentation, code, services, runtime, tools, storage, and config | Current | Primary source of truth for change management discipline |

---

## 11. Project-Specific Documents

### `docs/07_projects/`

Project-specific documentation is allowed in this directory only. Platform-level truth must remain project-agnostic.

**NURA** is the active validation project for LOOPRA.

Project docs must not redefine platform architecture. Project-specific context must not leak into core docs or code.

### `docs/07_projects/nura/`

| Document | Status | Purpose |
|---|---|---|
| `README.md` | Active | Navigation and scope for the NURA project |
| `POSITIONING.md` | Active | Product definition, target audience, value proposition for NURA |
| `TONE_OF_VOICE.md` | Active | Brand voice rules, communication style, and examples for NURA |
| `CONTENT_PILLARS.md` | Active | Content themes, topic boundaries, and content strategy for NURA |
| `VALIDATION_PLAN.md` | Active | Validation goals, success criteria, and test scenarios for NURA as LOOPRA validation project |

---

## 12. Roadmap Layer Documents

### `docs/08_roadmap/`

| Document | Status | Purpose | Current or Future | Source-of-Truth Role |
|---|---|---|---|---|
| `MVP_TO_AUTONOMOUS_OS_ROADMAP.md` | Active (v1.0) | Staged evolution path from current Foundation MVP to full Autonomous Marketing Operating System: Stage 0 through Stage 10, entry/exit criteria, dependencies, validation gates | Future planning based on current baseline | Primary source of truth for LOOPRA evolution roadmap |

---

## 13. Source-of-Truth Map

| Question | Source-of-Truth Document(s) |
|---|---|
| What is the current MVP scope? | `docs/00_foundation/MVP_SCOPE.md`, `STATE.md` |
| What is the current MVP chain? | `docs/00_foundation/DATA_MODEL.md`, `docs/02_architecture/PIPELINES_SPEC.md`, `STATE.md` |
| What is the data model? | `docs/00_foundation/DATA_MODEL.md` |
| How do projects and workspaces work? | `docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md` |
| How are project settings configured? | `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` |
| How do I set up development? | `docs/00_foundation/DEVELOPER_QUICKSTART.md` |
| What is LOOPRA? | `docs/01_product/LOOPRA_BRAND_POSITIONING.md`, `docs/02_architecture/PLATFORM_OVERVIEW.md` |
| How did the transition happen? | `docs/01_product/LOOPRA_TRANSITION_PLAN.md` |
| How do users interact with LOOPRA? | `docs/01_product/USER_WORKFLOWS.md` |
| What is the architecture? | `docs/02_architecture/LOOPRA_ARCHITECTURE.md`, `docs/02_architecture/SYSTEM_ARCHITECTURE.md` |
| What is the Brand System? | `docs/02_architecture/BRAND_SYSTEM_SPEC.md` |
| What pipeline stages exist? | `docs/02_architecture/PIPELINES_SPEC.md` |
| How does the agent system work? | `docs/03_intelligence/AGENT_SYSTEM_SPEC.md` (future) |
| How does the content cycle work? | `docs/03_intelligence/CONTENT_CYCLE_SPEC.md` (future) |
| How does content intelligence work? | `docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md` (future) |
| How does learning memory work? | `docs/03_intelligence/LEARNING_MEMORY_SPEC.md` (future) |
| How does trend intelligence work? | `docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md` (future) |
| What content types are supported? | `docs/04_production/CONTENT_TYPES_SPEC.md` |
| How does distribution work? | `docs/04_production/DISTRIBUTION_SPEC.md` |
| How does analytics work? | `docs/04_production/ANALYTICS_SPEC.md` |
| How does the production pipeline work? | `docs/04_production/PRODUCTION_PIPELINE_SPEC.md` (future) |
| How does the asset library work? | `docs/04_production/ASSET_LIBRARY_SPEC.md` (future) |
| How does runtime execute? | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` |
| What do services expose? | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` |
| How do CLI tools work? | `docs/05_platform/TOOLING_AND_CLI_SPEC.md` |
| Where is state stored? | `docs/05_platform/STORAGE_AND_STATE_SPEC.md` |
| How are env vars/config handled? | `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` |
| How is testing done? | `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` |
| What are safety boundaries? | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` |
| How to operate the MVP? | `docs/06_operations/OPERATIONAL_RUNBOOK.md` |
| How should agents collaborate? | `docs/06_operations/AGENT_OPERATING_MODEL.md` |
| How to manage changes? | `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` |
| What is the roadmap? | `docs/08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md` |
| What is the current project state? | `STATE.md` |
| What are the agent development rules? | `AGENTS.md` |


---

## 14. Reading Paths by Task Type

| Task Type | Must Read | Optional Read |
|---|---|---|
| **Documentation task** | `AGENTS.md`, `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` | `docs/00_foundation/MVP_SCOPE.md`, `STATE.md` |
| **Service code change** | `docs/00_foundation/DATA_MODEL.md`, `docs/05_platform/SERVICE_CONTRACTS_SPEC.md`, `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` | `docs/02_architecture/PIPELINES_SPEC.md`, `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` |
| **Runtime/tooling change** | `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md`, `docs/05_platform/TOOLING_AND_CLI_SPEC.md` | `docs/05_platform/SERVICE_CONTRACTS_SPEC.md`, `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` |
| **Storage/config change** | `docs/05_platform/STORAGE_AND_STATE_SPEC.md`, `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | `docs/00_foundation/PROJECT_SETTINGS_SPEC.md`, `docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md` |
| **Security-sensitive change** | `docs/05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md`, `docs/06_operations/AGENT_OPERATING_MODEL.md` | `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` |
| **Operations task** | `docs/06_operations/OPERATIONAL_RUNBOOK.md`, `docs/06_operations/AGENT_OPERATING_MODEL.md` | `docs/00_foundation/DEVELOPER_QUICKSTART.md`, `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` |
| **Roadmap/planning task** | `docs/08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md`, `STATE.md`, `docs/02_architecture/LOOPRA_ARCHITECTURE.md` | `docs/02_architecture/SYSTEM_ARCHITECTURE.md` |
| **Project-specific NURA task** | `docs/07_projects/nura/README.md`, `docs/07_projects/nura/VALIDATION_PLAN.md` | `docs/07_projects/nura/POSITIONING.md`, `docs/07_projects/nura/CONTENT_PILLARS.md` |
| **Future agent/intelligence task** | `docs/03_intelligence/AGENT_SYSTEM_SPEC.md`, `docs/03_intelligence/CONTENT_CYCLE_SPEC.md`, `docs/08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md` | `docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md`, `docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md`, `docs/03_intelligence/LEARNING_MEMORY_SPEC.md` |
| **New developer onboarding** | `AGENTS.md`, `STATE.md`, `docs/00_foundation/DEVELOPER_QUICKSTART.md`, `docs/00_foundation/MVP_SCOPE.md` | `docs/02_architecture/PLATFORM_OVERVIEW.md`, `docs/02_architecture/PIPELINES_SPEC.md` |
| **Architecture decision** | `AGENTS.md`, `docs/02_architecture/LOOPRA_ARCHITECTURE.md`, `docs/02_architecture/SYSTEM_ARCHITECTURE.md`, `STATE.md` | `docs/01_product/LOOPRA_BRAND_POSITIONING.md`, `docs/08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md` |

---

## 15. Current vs Future Document Map

| Document | Current MVP | Future/Conceptual | Notes |
|---|---|---|---|
| `00_foundation/MVP_SCOPE.md` | Yes | — | Defines current baseline only |
| `00_foundation/DATA_MODEL.md` | Yes | — | Current entities only |
| `00_foundation/WORKSPACE_AND_PROJECT_MODEL.md` | Yes | Has future extensions | Core model is current; future SaaS multi-tenancy is described conceptually |
| `00_foundation/PROJECT_SETTINGS_SPEC.md` | Yes | — | Current project.yaml schema |
| `00_foundation/DEVELOPER_QUICKSTART.md` | Yes | — | Current developer workflow only |
| `01_product/LOOPRA_BRAND_POSITIONING.md` | Yes | — | Current brand identity |
| `01_product/LOOPRA_TRANSITION_PLAN.md` | Yes | — | Completed transition documentation |
| `01_product/USER_WORKFLOWS.md` | — | Yes | Describes future product interaction model; not reflected in current CLI-only MVP |
| `02_architecture/LOOPRA_ARCHITECTURE.md` | Yes (current layers) | Yes (future vision) | Mixes current and future architecture direction |
| `02_architecture/BRAND_SYSTEM_SPEC.md` | Partial | Yes | Spec exists; full runtime integration with agents is future |
| `02_architecture/PIPELINES_SPEC.md` | Yes | — | Current manual pipeline only |
| `02_architecture/PLATFORM_OVERVIEW.md` | Yes | — | Current platform description |
| `02_architecture/SYSTEM_ARCHITECTURE.md` | Yes (current scope) | Yes (future layers) | Mixes current MVP boundaries with future architecture |
| `03_intelligence/AGENT_SYSTEM_SPEC.md` | — | Yes | No runtime agent in current MVP |
| `03_intelligence/CONTENT_CYCLE_SPEC.md` | — | Yes | No autonomous cycle in current MVP |
| `03_intelligence/CONTENT_INTELLIGENCE_SPEC.md` | — | Yes | No content intelligence in current MVP |
| `03_intelligence/LEARNING_MEMORY_SPEC.md` | — | Yes | No learning memory in current MVP |
| `03_intelligence/TREND_INTELLIGENCE_SPEC.md` | — | Yes | No trend intelligence in current MVP |
| `04_production/ANALYTICS_SPEC.md` | Partial (manual MetricSnapshot) | Yes (automated analytics) | Manual metrics exist; full analytics pipeline is future |
| `04_production/ASSET_LIBRARY_SPEC.md` | — | Yes | No asset library in current MVP |
| `04_production/CONTENT_TYPES_SPEC.md` | Partial (text_social_post) | Yes (other formats) | text_social_post is current; all other formats are future |
| `04_production/DISTRIBUTION_SPEC.md` | Partial (manual publication) | Yes (automated channel delivery) | Manual publication exists; automated distribution is future |
| `04_production/PRODUCTION_PIPELINE_SPEC.md` | — | Yes | Full production pipeline is future; only basic flow exists in MVP |
| `05_platform/RUNTIME_ORCHESTRATION_SPEC.md` | Yes | — | Describes current runtime execution |
| `05_platform/SERVICE_CONTRACTS_SPEC.md` | Yes | — | Based on actual `core/services/` code |
| `05_platform/TOOLING_AND_CLI_SPEC.md` | Yes | — | Based on actual CLI scripts |
| `05_platform/STORAGE_AND_STATE_SPEC.md` | Yes | — | Describes current filesystem storage |
| `05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | Yes | — | Describes current config handling |
| `05_platform/TESTING_AND_VALIDATION_SPEC.md` | Yes | — | Describes current test suite |
| `05_platform/SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md` | Yes | — | Describes current safety boundaries |
| `06_operations/OPERATIONAL_RUNBOOK.md` | Yes | — | Describes current operational procedures |
| `06_operations/AGENT_OPERATING_MODEL.md` | Yes (development) | Yes (runtime) | Current development governance + future runtime agent model |
| `06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` | Yes | — | Describes current change management |
| `07_projects/nura/*` | Yes | — | Current validation project |
| `08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md` | — | Yes | Describes future evolution stages |

---

## 16. Deprecated / Archived / Legacy Documents

### `docs/archive/content-plant-era/`

Contains historical documents from the Content Plant era. These documents are **archived for reference only** and do not define current LOOPRA architecture, scope, or decisions.

| Entry | Type | Description |
|---|---|---|
| `00_governance/` | Directory | Historical governance documents |
| `01_product/` | Directory | Historical product documentation |
| `02_architecture/` | Directory | Historical architecture documents (includes original `SYSTEM_ARCHITECTURE.md`, `BRAND_SYSTEM_SPEC.md`, and others pending LOOPRA adaptation) |
| `03_content/` | Directory | Historical content documentation |
| `04_production/` | Directory | Historical production documentation |
| `05_platform/` | Directory | Historical platform documentation |
| `06_misc/` | Directory | Miscellaneous historical documents |
| `DOCUMENT_AUDIT.md` | File | Audit of archived documents requiring LOOPRA adaptation |


---

## 17. Naming and Path Rules

1. **Active project name:** LOOPRA. All active documents must use LOOPRA as the product identity.
2. **Historical name:** Content Plant. This name belongs only in `docs/archive/` and `docs/01_product/LOOPRA_TRANSITION_PLAN.md`.
3. **`docs/05_runtime/` must not exist.** Runtime documentation lives under `docs/05_platform/`. The correct path is `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md`.
4. **Platform docs live under `docs/05_platform/`.** This includes runtime, services, tools, storage, configuration, testing, and security.
5. **Operations docs live under `docs/06_operations/`.** This includes runbook, agent model, and change management.
6. **Roadmap docs live under `docs/08_roadmap/`.** This includes evolution planning.
7. **Project-specific docs live under `docs/07_projects/{project_slug}/`.** Only project-level truth belongs here. Platform-level truth must remain in numbered directories.
8. **Foundation docs live under `docs/00_foundation/`.** MVP scope, data model, developer setup.
9. **Product docs live under `docs/01_product/`.** Brand, positioning, transition, workflows.
10. **Architecture docs live under `docs/02_architecture/`.** System design, pipelines, platform overview.
11. **Intelligence docs live under `docs/03_intelligence/`.** Agent system, content cycle, intelligence modules.
12. **Production docs live under `docs/04_production/`.** Pipeline, content types, distribution, analytics, assets.

---

## 18. Documentation Maintenance Rules

### 18.1. When to Update Docs

- When architecture changes → update the relevant source-of-truth document in `docs/02_architecture/`.
- When domain model changes → update `docs/00_foundation/DATA_MODEL.md`.
- When MVP scope changes → update `docs/00_foundation/MVP_SCOPE.md` and `STATE.md`.
- When a new platform spec is created → add to `docs/05_platform/` and update this index.
- When project configuration schema changes → update `docs/00_foundation/PROJECT_SETTINGS_SPEC.md`.
- When operational procedures change → update `docs/06_operations/OPERATIONAL_RUNBOOK.md`.

### 18.2. When to Update STATE.md

- When the current development phase changes.
- When the Foundation MVP status changes (READY, IN_PROGRESS, etc.).
- When new capabilities are validated and added to the completed list.
- When boundaries or constraints change.

### 18.3. When to Update AGENTS.md

- When development rules change.
- When architecture source-of-truth documents change.
- When the current development scope expands or contracts.
- When agent principles are refined.

### 18.4. When to Update DOCUMENTATION_INDEX.md

- When a new document is added to any active layer.
- When a document is archived or removed.
- When a document's status changes (e.g., from future to current).
- When a document's source-of-truth role changes.
- When a new reading path is needed.

### 18.5. How to Avoid Duplicate Specs

- Before creating a new document, check if the topic is already covered in an existing source-of-truth document.
- If information belongs in an existing document, extend that document rather than creating a new one.
- Use the source-of-truth map (Section 13) to verify coverage before creating new docs.

### 18.6. How to Avoid Stale References

- When moving or renaming a document, search for references to the old path across all active docs.
- When changing a document's role, update all documents that reference it as a source of truth.
- When archiving a document, remove references to it from active docs unless the reference is explicitly marked as historical.

These rules are governed by `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md`, which defines the full change management discipline.

---

## 19. Documentation Health Checklist

- [x] All active docs listed in this index
- [x] All listed paths exist on disk
- [x] No references to `docs/05_runtime/` (verified — this path does not exist; runtime docs are at `docs/05_platform/`)
- [x] No stale active Content Plant naming (historical mentions are isolated to archive, transition plan, and update-required docs)
- [x] Source-of-truth map complete (Section 13)
- [x] Current vs future separation clear (Section 15)
- [x] Project docs isolated in `docs/07_projects/nura/`
- [x] Roadmap marked as future where appropriate
- [x] Archive docs listed separately and marked as reference-only
- [x] Platform layer docs (Section 9) all present and accounted for
- [x] Operations layer docs (Section 10) all present and accounted for
- [x] Naming and path rules documented (Section 17)
- [x] Maintenance rules documented (Section 18)

---

## 20. Related Documents

- `AGENTS.md` — Development rules for AI coding agents working on LOOPRA
- `STATE.md` — Current project state, Foundation MVP status, development phase
- `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` — Governance framework for managing changes
- `docs/06_operations/AGENT_OPERATING_MODEL.md` — Human + AI agent collaboration model
- `docs/06_operations/OPERATIONAL_RUNBOOK.md` — Practical operations guide
- `docs/08_roadmap/MVP_TO_AUTONOMOUS_OS_ROADMAP.md` — Staged evolution path


---

## 21. Document Status

**Status:** Active — LOOPRA Documentation Layer

**Version:** v1.0

**Layer:** Documentation Index

**Created:** 2026-07-09

**Maintained by:** AI coding agents under `AGENTS.md` rules and `docs/06_operations/RELEASE_AND_CHANGE_MANAGEMENT.md` governance.

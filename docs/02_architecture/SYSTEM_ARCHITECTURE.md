# System Architecture

## Version

v2.0

## Status

Active — LOOPRA Architecture Source of Truth

## Purpose

This document defines the system architecture of LOOPRA — the
Autonomous Marketing Operating System.

It describes:

- the architectural layers of the system;
- how components interact across autonomous marketing cycles;
- how Workspace, Brand System, Content Cycle, Orchestrator Agent,
  Intelligence Modules, Production, Publishing, Analytics and Learning
  Memory form a unified operating system;
- the current Foundation MVP scope and its boundaries;
- future architecture direction without premature implementation.

This document is platform-level and must remain brand-agnostic.

---

## 1. System Overview

LOOPRA is an Autonomous Marketing Operating System.

It is not a content production tool.

LOOPRA is a system that continuously operates marketing growth cycles.

The primary value is not creating individual content items.

The value is creating a self-learning marketing process that improves
over time.

Core operating principle:

```text
Brand System
    ↓
Content Cycle
    ↓
Orchestrator Agent
    ↓
Intelligence Modules
    ↓
Production Layer
    ↓
Publishing
    ↓
Analytics
    ↓
Learning Memory
    ↓
Next Cycle
```

Each cycle feeds the next through structured learning.

---

## 2. High-Level Architecture

```text
Workspace
    ↓
Brand System
    ↓
Content Cycle
    ↓
Orchestrator Agent
    ↓
Intelligence Modules
    ↓
Production Layer
    ↓
Publishing
    ↓
Analytics
    ↓
Learning Memory
    ↓
Next Cycle (improved)
```

The system does not restart each cycle.

It accumulates context, experience and patterns.

---

## 3. Workspace Layer

Workspace is the top-level container for the user's operational
environment.

A Workspace contains:

- brands;
- projects;
- settings;
- channels;
- goals;
- autonomy level configuration.

Reference: `WORKSPACE_AND_PROJECT_MODEL.md`

In the current Foundation MVP, a single internal workspace is
sufficient.

Future SaaS phases will support multiple workspaces per user.

---

## 4. Brand System Layer

Brand System is the primary context source for all LOOPRA processes.

It defines:

- identity — who the brand is;
- audience — who the brand speaks to;
- positioning — how the brand is perceived;
- communication rules — how the brand talks;
- strategy — what content the brand creates and why;
- restrictions — what the brand must never do;
- goals — what the brand aims to achieve.

Reference: `BRAND_SYSTEM_SPEC.md`

Brand System is project-scoped.

The Orchestrator Agent reads Brand System at the start of every
content cycle and applies it to all subsequent decisions.

Brand System answers: "Who is this brand?"

It is stable and changes only when the brand itself evolves.

---

## 5. Content Cycle Layer

Content Cycle is the primary operational unit of LOOPRA.

A full content cycle proceeds through stages:

```text
Signal
    ↓
Idea
    ↓
Scenario
    ↓
Production
    ↓
Distribution
    ↓
Analytics
    ↓
Learning
    ↓
Optimization
```

Each stage is a distinct phase within the cycle.

The Orchestrator Agent manages the progression between stages.

Multiple cycles may operate in parallel for different content pillars,
channels or experiments.

Content Cycle is the core working object that LOOPRA orchestrates.

---

## 6. Orchestrator Agent Layer

The Orchestrator Agent is the decision-making layer of LOOPRA.

It is responsible for:

- managing content cycles;
- selecting next actions;
- coordinating tools and services;
- reading and applying Brand System context;
- evaluating results and deciding on optimization.

The Orchestrator Agent does not replace deterministic infrastructure.

Principle:

> Agents decide.
>
> Tools execute.

The agent operates within boundaries defined by:

- Brand System restrictions;
- Autonomy Settings;
- Human control points.

In the current Foundation MVP, the agent layer is a defined
architecture position — not an active autonomous system.

Future phases will implement orchestration gradually:
manual → assisted → autonomous.

---

## 7. Intelligence Modules

Intelligence Modules provide analysis and insight capabilities to
inform the Orchestrator Agent's decisions.

### 7.1. Trend Intelligence

Analyzes:

- market movements;
- emerging trends;
- audience signals;
- competitor activity.

### 7.2. Content Intelligence

Analyzes:

- successful content patterns;
- format performance;
- topic effectiveness;
- engagement patterns.

### 7.3. Analytics Intelligence

Analyzes:

- performance results;
- deviations from expected outcomes;
- hypotheses for improvement;
- optimization opportunities.

### 7.4. Learning Memory

Stores:

- successful decisions and their context;
- failed experiments and why they failed;
- accumulated operational knowledge;
- repeatable patterns.

Intelligence Modules are future architecture layers.

Current Foundation MVP does not implement them as active components.

---

## 8. Production Layer

Production is responsible for executing content creation decisions.

It produces:

- text content;
- images;
- video;
- other formats.

Production receives inputs from:

- Content Cycle stage definition;
- Brand System context;
- Orchestrator Agent decisions.

Production does not make strategic decisions.

It executes what the Orchestrator Agent and Content Cycle define.

In the current Foundation MVP, Production covers:

- Scenario creation;
- Content Item generation;
- Export Package assembly.

---

## 9. Publishing Layer

Publishing is responsible for content delivery.

It handles:

- publication preparation;
- channel-specific formatting;
- publication status tracking;
- schedule management.

Current Foundation MVP mode is export-first with manual publishing.

Publication records store:

- published URL;
- published timestamp;
- target platform;
- content linkage.

Autoposting is a future extension.

---

## 10. Analytics Layer

Analytics collects and aggregates performance data.

It captures:

- views;
- engagement;
- conversions;
- feedback signals.

In the current Foundation MVP, Analytics operates through:

- manual metric entry;
- MetricSnapshot records;
- basic aggregation by project and platform.

Analytics serves as the input layer for Learning Memory.

Collected data flows into:

```text
Analytics → Learning Memory → Cycle Optimization
```

---

## 11. Learning Memory

Learning Memory is the long-term memory of the LOOPRA system.

It is responsible for:

- preserving operational experience across cycles;
- identifying repeatable successful patterns;
- documenting failed experiments to avoid repetition;
- improving subsequent cycles with accumulated knowledge.

Relationship between Brand System and Learning Memory:

```text
Brand System:      "Who we are"
                       ↓
                  Guides decisions
                       ↓
Learning Memory:   "What works"
                       ↓
                  Refines execution
                       ↓
                  Improved next cycle
```

Brand System is stable.

Learning Memory evolves continuously.

Learning Memory does not override Brand System — it optimizes
execution within brand boundaries.

In the current Foundation MVP, Learning Memory is a defined
architecture layer for future implementation.

---

## 12. Autonomy Model

LOOPRA supports progressive autonomy levels.

### 12.1. Copilot

User controls most decisions.

LOOPRA suggests and assists.

Every action requires approval.

### 12.2. Assisted

LOOPRA proposes decisions and executes approved actions.

Periodic human checkpoints are required.

### 12.3. Autopilot

LOOPRA operates autonomously within defined rules.

Human retains emergency stop capability.

### 12.4. Control Points

All autonomy levels include:

- approval gates;
- review periods;
- checkpoints;
- emergency stop mechanism.

Current Foundation MVP operates in copilot mode by default.

Full autonomy enforcement is a future capability.

---

## 13. Data Model

The fundamental data flow in LOOPRA follows the content cycle.

Current Foundation MVP entity chain:

```text
Project context
    → Idea
    → Scenario
    → ContentItem
    → ExportPackage
    → Publication
    → MetricSnapshot
```

Reference: `DATA_MODEL.md`

All entities are project-scoped.

Platform-level entities remain generic structures without
project-specific values.

---

## 14. Storage Separation

Project-scoped storage structure:

```text
storage/
    projects/
        {project_slug}/
            assets/
            renders/
            exports/
            analytics/
```

Platform rules:

- project files must not be stored in shared directories without
  project separation;
- export packages and runtime artifacts are project-scoped;
- generated/runtime artifacts are local and not committed.

Reference: `WORKSPACE_AND_PROJECT_MODEL.md`

---

## 15. Project Scoping

Every project-level entity must carry `project_id`.

Required for:

- Brand System configuration;
- Ideas;
- Scenarios;
- Content Items;
- Export Packages;
- Publications;
- Metric Snapshots.

Platform-level entities exist without `project_id`:

- Content format definitions;
- Shared lifecycle rules;
- Platform reference dictionaries.

Project-specific configuration lives in:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/
```

Platform core must never contain project-specific hardcoded logic.

---

## 16. Lifecycle Statuses

Status management is owned by the relevant architectural layer.

### 16.1. Content Item Statuses

```text
draft
needs_review
approved
rejected
changes_requested
exported
scheduled
published
analyzed
archived
failed
```

### 16.2. Publication Statuses

```text
draft
ready
scheduled
published
failed
cancelled
archived
```

### 16.3. Metric Snapshot Statuses

```text
draft
imported
validated
needs_review
approved
archived
```

Status transitions must respect current state validation.

Do not mix Content Item status with Publication status.

Do not mix analytics state with publication state.

---

## 17. Snapshots and Reproducibility

LOOPRA should preserve snapshots for important operations.

Snapshot types:

- Content generation input snapshot (idea, brand context, format specs);
- Export package snapshot (content version, captions, settings);
- Publication context snapshot (platform, URL, UTM parameters).

Snapshots enable:

- debugging;
- re-generation;
- cross-cycle comparison;
- learning pattern extraction.

Current MVP may store simplified snapshots as structured records.

---

## 18. Error Handling

Errors should be structured and actionable.

Every pipeline error should include:

- entity type and identifier;
- project context;
- error code and message;
- severity;
- recommended action.

Errors that block progression should surface to the operator.

---

## 19. Current Foundation MVP Boundary

### 19.1. Implemented

Current validated capabilities:

- project model;
- lifecycle services;
- content item flow (Idea → Scenario → ContentItem);
- export package generation;
- publication records;
- metric snapshot foundation.

Validated lifecycle:

```text
Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot
```

### 19.2. Not Implemented

Not in current Foundation MVP scope:

- UI;
- API;
- database;
- authentication;
- billing;
- SaaS infrastructure;
- external integrations;
- autonomous agents.

These capabilities belong to future architecture phases and must not
be implemented without explicit scope change.

### 19.3. Future Architecture Evolution

LOOPRA evolves through validated stages:

```text
Foundation MVP
    ↓
Content Intelligence
    ↓
Production Automation
    ↓
Agentic Operations
    ↓
Marketing Operating System
    ↓
SaaS Platform
```

Each stage must be validated before the next begins.

---

## 20. Technology Guidance

This section provides directional guidance, not strict requirements.

### 20.1. Frontend

Possible direction:

```text
React / Next.js
TypeScript
Tailwind / component library
Workflow-first UI
```

Key requirement: UI must be workflow-first, not a decorative dashboard.

### 20.2. Backend

Possible direction:

```text
Python + FastAPI
or Node.js / TypeScript
```

Important: modularity, project scope, clean data model.

### 20.3. Database

Recommended:

```text
PostgreSQL
```

Early local development may use SQLite with migration path.

### 20.4. Storage

Foundation MVP:

```text
local filesystem
```

Future:

```text
S3-compatible object storage
CDN for previews
```

### 20.5. Queue and Workers

Possible direction:

```text
Redis + RQ / Celery / BullMQ
```

Simple job runner is acceptable for early stages.

---

## 21. Deployment Model

Foundation MVP may run as a local or private internal application.

Local-first setup:

```text
single machine
local database
local storage
local worker
manual backups
```

Private server setup:

```text
single VPS
PostgreSQL
object storage or mounted volume
background worker
reverse proxy
basic auth or private access
```

Public SaaS deployment is future scope.

---

## 22. Observability

Minimum observability for Foundation MVP:

```text
application logs
worker logs
job status history
error records
last updated timestamps
```

Future additions:

```text
structured logs
metrics dashboard
alerts
trace IDs
audit log
```

---

## 23. Backup and Data Safety

Minimum protection:

```text
regular database backup
regular storage backup
exportable project folder
archive-first approach before hard delete
```

Recommended pattern:

```text
archive first
hard delete only when explicitly required
```

---

## 24. Future SaaS Readiness

Architecture must allow future SaaS expansion without implementing it
prematurely.

Future additions may include:

- user accounts and authentication;
- workspace memberships;
- roles and permissions;
- billing and subscriptions;
- plan limits;
- public onboarding;
- template marketplace;
- API keys;
- multi-tenant storage separation.

Current MVP preserves clean boundaries:

```text
workspace_id
project_id
project-scoped storage
project-scoped settings
platform-level templates
no project-specific hardcode
```

---

## 25. Architecture Principles

LOOPRA architecture follows these principles:

1. Project-agnostic foundation — core contains no brand-specific logic.
2. Progressive evolution — each layer validated before the next.
3. Human-controlled autonomy — agents decide, humans retain control.
4. Continuous learning — each cycle feeds the next.
5. Clear boundaries — layers have defined responsibilities.
6. Documentation as source of truth — architecture docs drive implementation.
7. Foundation first — no future features before current validation.

---

## 26. Out of Scope for Foundation MVP

Do not implement without explicit scope change:

```text
public SaaS registration
billing
plans and limits
teams
roles and permissions
marketplace
public onboarding
white-label accounts
complex integrations layer
mandatory autoposting
built-in AI image/video generation APIs
advanced recommendation engine
autonomous agent execution
```

---

## 27. Related Documents

This document should be read together with:

```text
docs/02_architecture/LOOPRA_ARCHITECTURE.md       — Core architecture direction
docs/02_architecture/BRAND_SYSTEM_SPEC.md         — Brand System specification
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md — Workspace and project model
docs/00_foundation/DATA_MODEL.md                  — Current data model baseline
docs/01_product/LOOPRA_BRAND_POSITIONING.md       — LOOPRA product identity
AGENTS.md                                          — Development rules for agents
STATE.md                                           — Current project state
```

---

## 28. Future Detailed Specifications

This section defines the roadmap for future LOOPRA specification
documents. These documents do not yet exist. They are listed here as
architectural direction only.

No future module should be implemented without its approved
specification document.

### 28.1. Intelligence Layer Specifications

Future documents under `docs/03_intelligence/`:

- `TREND_INTELLIGENCE_SPEC.md` — market signal analysis and trend detection
- `CONTENT_INTELLIGENCE_SPEC.md` — pattern recognition and content insight generation
- `AGENT_SYSTEM_SPEC.md` — Orchestrator Agent design, decision model and execution
- `LEARNING_MEMORY_SPEC.md` — long-term memory, pattern retention and retrieval

### 28.2. Production Specifications

Future documents under `docs/04_production/`:

- `CONTENT_OPERATING_SYSTEM_SPEC.md` — autonomous content cycle execution
- `CONTENT_TYPES_SPEC.md` — supported content formats and their properties
- `PRODUCTION_PIPELINE_SPEC.md` — content production workflow and quality gates
- `QA_SYSTEM_SPEC.md` — automated quality assurance rules and checks

### 28.3. Platform Specifications

Future documents under `docs/05_platform/`:

- `PUBLISHING_SYSTEM_SPEC.md` — multi-platform publishing and scheduling
- `ANALYTICS_SYSTEM_SPEC.md` — metrics collection, aggregation and analysis
- `INTEGRATIONS_SPEC.md` — external service and platform integrations

### 28.4. Specification Governance

Architecture documents define system boundaries.

Detailed specifications define implementation behaviour.

No future module should be implemented without its approved
specification document.

---

## Final Statement

LOOPRA is an Autonomous Marketing Operating System.

It transforms marketing from disconnected content tasks into a
continuous self-learning cycle.

The architecture layers — Workspace, Brand System, Content Cycle,
Orchestrator Agent, Intelligence Modules, Production, Publishing,
Analytics and Learning Memory — form a unified operating system
designed for continuous marketing growth.

The system grows through validated capabilities, not premature
feature expansion.

Build LOOPRA as an evolving autonomous marketing platform.

Optimize for a clean architecture that can grow.

# USER WORKFLOWS

## Version

v1.0

## Status

Active — LOOPRA Product Specification

## Purpose

This document defines how a user interacts with LOOPRA — the
Autonomous Marketing Operating System — from initial setup through daily
operation.

It answers the question:

> How does a human manage an autonomous marketing system?

This document describes the product interaction model, business
processes, human-AI collaboration patterns and autonomy governance.

It is NOT a UI specification.

---

# 1. Purpose and Scope

USER_WORKFLOWS.md defines the complete user journey with LOOPRA: from
first workspace creation, through brand and channel configuration, to
autonomous cycle monitoring and learning feedback.

The document is a product-level specification of user interaction. It
does not define screens, components, API contracts or database schemas.

It answers:

- What does the user do to set up LOOPRA?
- How does the user configure a brand for autonomous operation?
- How does LOOPRA operate once configured?
- How does the user control and monitor autonomous cycles?
- How does the human remain in control while letting LOOPRA execute?

---

# 2. LOOPRA User Model

## 2.1. The New Role

In LOOPRA, the user is not an operator of content generation tasks.

The user is an **operator of an autonomous marketing system**.

The user does not:

- create content ideas manually;
- write scenarios;
- manage individual content items;
- publish content item by item.

The user:

- sets strategic direction;
- configures brand context;
- defines goals and constraints;
- selects autonomy level;
- reviews results and adjusts rules.

## 2.2. Core Principle

> Human sets direction.
>
> LOOPRA executes and learns.

The human provides context, goals, boundaries and brand knowledge.

LOOPRA operates continuous marketing cycles within those boundaries,
improving with every cycle.

## 2.3. Interaction Model

```text
Human
    ↓
Goals / Rules / Context
    ↓
Orchestrator Agent
    ↓
Tools and Intelligence Modules
    ↓
Results
    ↓
Learning Memory
    ↓
Improved Next Cycle
```

The human does not participate in the inner loop of content creation.

The human sets the conditions under which the inner loop operates.

## 2.4. User Archetypes

### Solo Founder

One person managing one or several brands. Single workspace, personal
operation.

### Marketer

One professional responsible for marketing operations. May manage
multiple brands or channels.

### Agency

Multiple users managing multiple client brands. Multiple projects under
one agency workspace.

### Enterprise

Multiple brands, multiple team members, role-based permissions and
operational governance (future scope).

---

# 3. Workspace Creation Workflow

## 3.1. Overview

The user's first interaction with LOOPRA is creating a Workspace — the
top-level operational container.

```text
User creates Workspace
    ↓
Creates Projects
    ↓
Invites team members (future scope)
    ↓
Configures workspace-level settings
```

## 3.2. Workspace Types

### Individual Marketer

One user, one workspace, one or multiple brands.

```text
Workspace: My Brand
    ├── Project: Brand A
    └── Project: Personal Content
```

### Agency

One workspace with multiple client projects, each having its own Brand
System.

```text
Workspace: Agency
    ├── Project: Client A
    ├── Project: Client B
    └── Project: Client C
```

### Enterprise

One workspace with multiple brands, multiple team members and
permission structures (future scope).

```text
Workspace: Enterprise
    ├── Project: Brand X
    ├── Project: Brand Y
    ├── Project: Internal Communications
    └── Teams and Permissions (future)
```

## 3.3. Current Foundation MVP

In the current Foundation MVP, a single internal Workspace is
sufficient. Multiple projects are supported within it.

Reference: `WORKSPACE_AND_PROJECT_MODEL.md`

---

# 4. Project Creation Workflow

## 4.1. Overview

After creating a Workspace, the user creates a Project — the
operational unit that represents a brand, product or client.

## 4.2. What the User Defines

The user provides:

- project name;
- description;
- industry context;
- primary language;
- primary URL or web property.

## 4.3. Structural Model

```text
Workspace
    ↓
Project
    ↓
Brand System
    ↓
Content Cycles
```

The Project connects to a Brand System, which provides the full brand
context for autonomous operation.

The Project itself stores operational settings: channels, goals, export
preferences and constraints.

Reference: `PROJECT_SETTINGS_SPEC.md`

## 4.4. Project Scope

Each Project has its own:

- Brand System;
- content cycles;
- channels;
- goals;
- analytics history;
- export packages;
- publication records;
- metric snapshots.

Projects are fully isolated. Data from one project never leaks into
another.

---

# 5. Brand System Setup Workflow

## 5.1. Overview

After creating a Project, the user configures the Brand System — the
structured knowledge layer that LOOPRA uses to make autonomous
marketing decisions.

The Brand System answers the question:

> Who is this brand, who does it speak to, and how does it communicate?

Reference: `BRAND_SYSTEM_SPEC.md`

## 5.2. What the User Configures

### Brand Identity

The user defines:

- brand name;
- positioning — how the brand should be perceived;
- mission — the brand's purpose;
- values — core principles that guide the brand;
- differentiation — what makes this brand unique.

### Audience Intelligence

The user defines:

- target audience description;
- audience segments with distinct characteristics;
- pain points and frustrations;
- motivations and desires;
- content format preferences.

### Communication System

The user defines:

- tone of voice — style, emotional range;
- allowed and forbidden formulations;
- content principles — topics to cover and avoid;
- key meanings to amplify consistently.

### Content Strategy

The user defines:

- content pillars — thematic categories (e.g. education,
  storytelling, product, community);
- preferred content formats;
- publishing goals and target frequency.

### Business Goals

The user defines:

- goal type (awareness, engagement, traffic, leads, sales, retention);
- priority level;
- target description;
- key metrics for tracking.

### Restrictions and Safety

The user defines:

- forbidden topics — what must never appear;
- forbidden claims — promises that must never be made;
- legal and compliance rules;
- industry-specific disclaimers.

## 5.3. How LOOPRA Uses the Brand System

Once configured, the Brand System becomes the permanent source of truth
for all LOOPRA operations.

The Orchestrator Agent reads the Brand System at the start of every
content cycle and applies it to all decisions:

- which topics to pursue;
- which formats to use;
- which audience segments to target;
- which tone to apply;
- which restrictions to enforce.

The Brand System is stable. It changes only when the brand itself
evolves.

---

# 6. Channel Configuration Workflow

## 6.1. Overview

The user selects which distribution channels LOOPRA operates for the
project.

## 6.2. Supported Channels

- Telegram
- Instagram
- TikTok
- YouTube Shorts
- LinkedIn
- Threads
- VK
- X
- Facebook
- Pinterest

Additional channel types (blog, email, podcast) are future scope.

## 6.3. What the User Configures Per Channel

For each enabled channel:

- account reference (handle, URL);
- enabled content formats;
- publishing rules (length limits, aspect ratios);
- caption rules;
- hashtag strategy;
- CTA constraints;
- preferred publishing days and times.

## 6.4. Validation

At least one channel must be enabled for LOOPRA to operate content
cycles.

---

# 7. Content Strategy Configuration

## 7.1. Content Types

The user selects which content types LOOPRA generates:

- text social posts;
- carousels;
- short video reels;
- educational carousels;
- images.

Additional content types belong to future phases.

## 7.2. Content Pillars

The user defines thematic pillars that organize all content:

```text
education      — knowledge sharing and expertise demonstration
storytelling   — narrative content that builds connection
product        — product and offer presentation
community      — audience engagement and interaction
```

Each pillar specifies:

- suitable formats;
- content objectives;
- priority within the strategy.

## 7.3. Publishing Frequency

The user defines:

- target publishing cadence (e.g. 3 posts per week);
- preferred publishing days;
- preferred publishing times per channel.

---

# 8. Autonomy Mode Selection

## 8.1. Overview

One of the most critical user decisions: how much independent action
LOOPRA is permitted.

Three autonomy modes exist. The user selects one per project.

## 8.2. Copilot Mode

**Principle:** LOOPRA suggests, human decides.

LOOPRA:

- analyzes market signals;
- proposes content opportunities;
- generates content drafts;
- recommends optimizations.

The user:

- reviews every proposal;
- approves or rejects content;
- makes all final decisions.

Every action requires human approval.

**Current Foundation MVP operates in copilot mode by default.**

## 8.3. Assisted Mode

**Principle:** LOOPRA operates with periodic human checkpoints.

LOOPRA:

- autonomously executes routine processes;
- proposes strategic decisions;
- waits for confirmation at important stages.

The user:

- reviews at defined checkpoints;
- approves critical decisions;
- adjusts rules based on results.

Checkpoint examples:

- after idea selection;
- before final content publication;
- after weekly analytics review.

## 8.4. Autopilot Mode

**Principle:** LOOPRA operates autonomously within defined rules.

LOOPRA:

- launches content cycles independently;
- creates and publishes content;
- analyzes performance results;
- optimizes subsequent cycles.

But always with:

- control points;
- operational limits;
- emergency stop;
- periodic review checkpoints.

The user:

- monitors rather than operates;
- intervenes only at boundaries;
- adjusts rules to improve performance;
- escalates to assisted or copilot mode when needed.

## 8.5. Emergency Controls

In all autonomy modes, the user retains:

- **Emergency Stop** — immediately pause all active cycles;
- **Reduce Autonomy** — drop from autopilot to assisted or copilot;
- **Change Rules** — modify restrictions, forbidden topics or goals
  that affect running cycles.

---

# 9. First Content Cycle Workflow

## 9.1. Overview

Once the Project and Brand System are configured, the user starts the
first content cycle.

This is the moment where the difference between LOOPRA and a content
generator becomes visible.

A content generator asks:

> "What topic should I create content about today?"

LOOPRA already knows:

- the brand identity;
- the audience;
- the communication rules;
- the content strategy;
- the business goals;
- the channel constraints.

It operates from context, not from per-task instructions.

## 9.2. What Happens When a Cycle Starts

```text
User starts cycle
    ↓
LOOPRA reads Brand System
    ↓
LOOPRA reads Project Settings
    ↓
LOOPRA analyzes available signals
    ↓
LOOPRA identifies content opportunities
    ↓
LOOPRA selects best opportunity based on strategy
    ↓
LOOPRA generates content aligned with brand voice
    ↓
LOOPRA runs quality validation
    ↓
LOOPRA prepares publication package
    ↓
LOOPRA collects results after publication
```

The cycle is self-contained. The user does not provide per-item
instructions.

In copilot mode, the user retains approval gates at key stages.

## 9.3. Key Distinction

```text
Traditional tool:
    User provides topic → Tool creates content → User publishes

LOOPRA:
    User sets context once → LOOPRA discovers opportunities
    → LOOPRA creates content → LOOPRA learns from results
    → Cycle improves
```

The user's role shifts from content creator to system operator.

---

# 10. Daily User Workflow

## 10.1. Opening LOOPRA

When a user opens LOOPRA daily, they see the current state of the
autonomous system:

- active content cycles with progress;
- generated content ready for review (in copilot/assisted modes);
- content pending approval;
- recent publications with performance data;
- system recommendations and insights;
- learning memory findings — what improved since last cycle.

## 10.2. User Actions

The daily user workflow consists of:

### Review and Approve

- review generated content;
- approve or request changes;
- confirm publication decisions.

### Adjust Rules

- update goals if business priorities shift;
- modify restrictions if new boundaries are needed;
- change channel configuration;
- adjust autonomy level.

### Launch Experiments

- test new content formats;
- explore new audience segments;
- try new content pillars;
- adjust publishing frequency.

### Monitor Performance

- review analytics summaries;
- compare performance across cycles;
- identify trends and patterns;
- note learning memory insights.

## 10.3. What the User Does NOT Do Daily

The user does not:

- manually create content ideas;
- write content from scratch;
- manage individual content item statuses;
- manually track metrics per post;
- decide what to publish each day.

These are LOOPRA's responsibilities.

---

# 11. Autopilot Monitoring Workflow

## 11.1. Overview

When the user selects autopilot mode, LOOPRA operates continuously
without per-cycle human involvement.

The user's role becomes monitoring and governance.

## 11.2. LOOPRA's Autonomous Operation

In autopilot mode, LOOPRA continuously:

- analyzes market signals and audience data;
- identifies content opportunities;
- generates content;
- publishes according to schedule;
- collects performance metrics;
- feeds data into Learning Memory;
- optimizes the next cycle.

## 11.3. Control Points

Even in autopilot, structured control points ensure human governance:

### Weekly Review

LOOPRA prepares a weekly summary:

- content published;
- performance metrics;
- learning insights;
- recommended adjustments.

The user reviews and confirms or adjusts.

### Content Approval (Optional)

The user may configure that certain content types or channels require
approval even in autopilot mode.

### Performance Review

The user periodically reviews:

- whether goals are being met;
- whether content quality is maintained;
- whether brand voice is consistent;
- whether restrictions are respected.

## 11.4. Emergency Controls

When needed, the user can:

- **Stop Cycle** — pause current content cycles immediately;
- **Change Mode** — switch from autopilot to assisted or copilot;
- **Change Rules** — update restrictions, goals or strategy;
- **Review Decision** — inspect any autonomous decision the system made.

## 11.5. Escalation Policy

LOOPRA escalates to human attention when:

- performance drops below defined thresholds;
- a restriction might be triggered;
- a decision falls outside confidence boundaries;
- an unexpected market shift is detected.

---

# 12. Human and AI Collaboration Model

## 12.1. Fundamental Principle

> LOOPRA does not replace the marketer.
>
> LOOPRA transforms the marketer into an operator of an autonomous
> marketing system.

The human provides what AI cannot:

- strategic vision;
- brand intuition;
- ethical boundaries;
- creative direction;
- business context.

LOOPRA provides what humans cannot sustain:

- continuous market monitoring;
- consistent content production;
- systematic performance analysis;
- persistent learning accumulation;
- scalable multi-channel operation.

## 12.2. Responsibility Division

### Human Responsibilities

- define strategy and goals;
- configure brand identity;
- set boundaries and restrictions;
- make final approval decisions;
- adjust rules based on business context;
- handle exceptions and edge cases.

### Orchestrator Agent Responsibilities

- coordinate all system components;
- manage content cycles;
- select actions based on strategy;
- evaluate cycle results;
- decide on optimizations;
- escalate when uncertain.

### Tools and Services Responsibilities

- execute deterministic operations;
- generate content formats;
- prepare export packages;
- collect metrics;
- apply validation rules.

## 12.3. Collaboration Pattern

```text
Human defines:           Strategy, Brand, Goals, Rules
    ↓
Orchestrator decides:    What to do, When to do it, How to optimize
    ↓
Tools execute:           Content generation, Publishing, Analytics
    ↓
Learning Memory stores:  What worked, What didn't, Why
    ↓
Human reviews:           Results, Insights, Recommendations
    ↓
Human adjusts:           Strategy, Rules, Goals
    ↓
Next cycle begins with improved context
```

The system improves with every cycle, but the human remains the
ultimate authority.

---

# 13. Agency Workflow

## 13.1. Overview

An agency uses a single Workspace to manage multiple client brands.

```text
Agency Workspace
    ├── Client A
    │   ├── Project: Client A
    │   ├── Brand System: Client A brand
    │   ├── Content Cycles: Client A cycles
    │   └── Analytics: Client A data
    │
    ├── Client B
    │   ├── Project: Client B
    │   ├── Brand System: Client B brand
    │   ├── Content Cycles: Client B cycles
    │   └── Analytics: Client B data
    │
    └── Client C
        └── ...
```

## 13.2. Per-Client Isolation

Each client has:

- a separate Project;
- a separate Brand System;
- independent content cycles;
- independent analytics history;
- independent learning memory.

No client data is shared or leaked across projects.

## 13.3. Agency Operations

An agency user:

- switches between client projects;
- configures each client's Brand System independently;
- sets per-client autonomy modes;
- reviews per-client performance;
- applies agency-wide best practices across clients while keeping
  brand-specific configurations separate.

Multi-user agency teams with role-based permissions are future scope.

---

# 14. Learning Interaction

## 14.1. How the User Influences Learning

The user does not directly train LOOPRA's models.

The user influences system learning through operational actions:

- **Changing goals** — signals new priorities to the system;
- **Adjusting rules** — refines creative boundaries;
- **Approval decisions** — teaches what content directions are valued;
- **Feedback on content** — indicates quality and brand alignment;
- **Switching strategies** — redirects the system toward new
  opportunities.

## 14.2. How LOOPRA Learns

LOOPRA improves through its Learning Memory:

- records which content formats perform best for which goals;
- identifies successful patterns across cycles;
- documents failed experiments and why they failed;
- accumulates audience response patterns;
- refines content decisions cycle after cycle.

## 14.3. Separation of Concerns

```text
Brand System (stable)
    "Who we are"
        ↓
    Guides decisions
        ↓
Learning Memory (evolving)
    "What works best"
        ↓
    Refines execution
        ↓
Improved next cycle
```

Learning Memory does not override Brand System.
It optimizes execution within brand boundaries.

---

# 15. Appendix A — Current Foundation MVP Internal Workflow

**Important:** This appendix describes the current technical pipeline
of the Foundation MVP. It represents the internal execution mechanism
that LOOPRA uses today. It does not describe the full user experience
of the future autonomous system.

The user workflows described in sections 3 through 14 above are the
product model toward which LOOPRA is evolving. This appendix documents
the current implementation baseline.

## A.1. Current Foundation Pipeline

The current Foundation MVP executes this pipeline:

```text
Idea
    ↓
Scenario
    ↓
ContentItem
    ↓
ExportPackage
    ↓
Manual Publication
    ↓
MetricSnapshot
```

## A.2. How the Pipeline Works Today

In the current Foundation MVP:

1. An **Idea** is created as a starting point for content.
2. A **Scenario** is created from the Idea — a content plan.
3. A **ContentItem** is produced from the Scenario.
4. An **ExportPackage** is assembled — a filesystem package ready for
   inspection.
5. The user publishes manually outside LOOPRA using the export package.
6. A **Publication** record stores the manual publication outcome.
7. A **MetricSnapshot** stores manually collected performance metrics.

## A.3. Current Pipeline Limitations

The current Foundation MVP is:

- export-first (not autopublishing);
- manual-publication-first;
- manual-metrics-first;
- local filesystem-based;
- developer-helper-driven.

These limitations are by design. The Foundation MVP validates the
operational content lifecycle before expanding toward autonomous
operation.

## A.4. Relationship to LOOPRA Product Vision

The Foundation MVP pipeline (`Idea → Scenario → ContentItem →
ExportPackage → Publication → MetricSnapshot`) is the technical
baseline that will evolve into the full LOOPRA operating cycle
(`Discover → Decide → Produce → Distribute → Measure → Learn →
Improve`).

The transition from the current Foundation MVP to the autonomous
marketing operating system happens through validated stages:

```text
Foundation MVP (current)
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

The current Foundation MVP provides reliable execution primitives.

Future layers add intelligence, autonomy and continuous learning.

---

# Related Documents

```text
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md  — Workspace and Project architecture
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration specification
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline stages
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |

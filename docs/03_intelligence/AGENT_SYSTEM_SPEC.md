# AGENT SYSTEM SPEC

## Version

v1.0

## Status

Active — LOOPRA Intelligence Layer

## Purpose

This document defines the functional architecture of the LOOPRA Agent
System — the intelligent decision-making layer of the Autonomous
Marketing Operating System.

It answers the central question:

> How does LOOPRA make decisions, manage cycles and use AI components
> for continuous improvement of marketing results?

AGENT_SYSTEM_SPEC.md is the architectural blueprint for the
intelligence that transforms LOOPRA from a deterministic production
layer into a self-learning marketing operating system.

It describes:

- the role of the Orchestrator Agent;
- the responsibilities of Intelligence Modules;
- the interaction between agents and tools;
- the decision-making model;
- autonomy governance and human control.

It does NOT describe:

- specific LLM providers (OpenAI, Anthropic, Gemini or any other);
- API contracts and implementation details;
- prompt engineering or agent prompts;
- database schemas or storage implementation;
- code-level implementation.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

AGENT_SYSTEM_SPEC.md defines the functional architecture of AI
components within LOOPRA.

It establishes:

- how the system makes marketing decisions;
- how components interact to form an intelligent operating loop;
- what boundaries govern autonomous behaviour;
- how human control is preserved at every level;
- how the agent system relates to the current Foundation MVP.

## 1.2. Scope

This document covers:

- the Orchestrator Agent — the central coordinating intelligence;
- Intelligence Modules — specialized analytical capabilities;
- the decision model — how decisions are formed and recorded;
- the confidence and escalation model — when the system acts vs asks;
- the human approval model — autonomy modes and control points;
- the agent memory model — what the system remembers and why;
- the agent relationship with the Content Cycle;
- safety boundaries — what agents cannot do.

## 1.3. Out of Scope

This document does not cover:

- specific AI model selection or provider comparison;
- API contracts between system components;
- database schemas for agent state or memory;
- prompt templates or agent instruction formats;
- implementation code for any agent component.

---

# 2. LOOPRA Agent System Overview

## 2.1. The Core Model

LOOPRA is not a collection of independent autonomous agents.

LOOPRA Agent System follows an Orchestrator Architecture:

```text
Human Operator
    ↓
Orchestrator Agent
    ↓
Specialized Intelligence Modules
    ↓
Execution Tools
    ↓
Analytics
    ↓
Learning Memory
    ↓
Improved Decisions
```

## 2.2. The Orchestrator Role

The Orchestrator Agent is the managing layer of LOOPRA
intelligence.

It does not execute all actions itself.

It:

- analyzes context from multiple sources;
- selects the next operational step;
- invokes the appropriate tools;
- evaluates outcomes;
- launches the next cycle.

## 2.3. Why Orchestration, Not Swarm

A multi-agent swarm model introduces:

- competing objectives between agents;
- chaotic decision chains;
- lack of accountability;
- unpredictable behaviour.

LOOPRA uses a single Orchestrator Agent that coordinates
specialized modules.

Each module provides analytical capability.

The Orchestrator integrates their outputs into coherent
decisions.

## 2.4. System Hierarchy

```text
Human
  │  Strategic authority
  │  Sets direction, goals, boundaries
  ↓
Orchestrator Agent
  │  Operational authority
  │  Manages cycles, makes decisions, coordinates
  ↓
Intelligence Modules
  │  Analytical capability
  │  Trend analysis, content insight, performance analytics
  ↓
Production Tools
  │  Execution capability
  │  Content generation, publishing, metrics collection
  ↓
Learning Memory
  │  Knowledge retention
  │  Pattern storage, experience accumulation, retrieval
```

---

# 3. Core Design Principles

## 3.1. Orchestration Over Agent Swarm

LOOPRA does NOT use:

- multiple competing agents with independent goals;
- agent swarm where agents negotiate or compete;
- chaotic agent networks without central coordination;
- decentralized decision-making without accountability.

LOOPRA uses:

- one Orchestrator Agent as the central coordinator;
- specialized Intelligence Modules as analytical capabilities;
- deterministic Execution Tools for production actions.

The Orchestrator integrates module outputs into coherent
operational decisions. Modules provide information. The
Orchestrator decides.

## 3.2. Agents Decide. Tools Execute

This is the foundational principle of the LOOPRA Agent System.

**Agent:**

- thinks;
- plans;
- makes decisions;
- evaluates context;
- selects actions.

**Tool:**

- performs a defined action;
- transforms inputs into outputs;
- returns a result;
- does not make strategic choices.

**Example:**

```text
Agent decision:
"Create an educational video for audience segment X based on
detected trend Y."

Tool execution:
"Generate video package with specified parameters."
```

The agent determines what, why and when.

The tool determines how (the deterministic execution).

## 3.3. Human Remains Strategic Authority

The human is the operator of an autonomous marketing system, not
a replaced decision-maker.

The human retains control over:

- **Business Goals** — what the brand aims to achieve;
- **Brand System** — who the brand is and how it communicates;
- **Restrictions** — what must never appear in content;
- **Autonomy Level** — how much independent authority the system
  has;
- **Critical Decisions** — approvals for significant actions;
- **Emergency Control** — stop, pause or reduce autonomy at any
  time.

LOOPRA operates within human-defined boundaries. It may suggest
changing those boundaries but never overrides them.

---

# 4. Orchestrator Agent

## 4.1. Definition

The Orchestrator Agent is the central coordinator of LOOPRA.

It is the single decision-making intelligence that manages
all operational activity.

The Orchestrator Agent does not replace deterministic
infrastructure. It orchestrates it.

## 4.2. Core Responsibilities

### Context Management

The Orchestrator Agent loads and maintains operational context:

- Workspace configuration;
- Project settings;
- Brand System (identity, audience, tone, strategy,
  restrictions);
- Business goals and priorities;
- Channel configuration;
- Learning Memory (past outcomes, patterns, experiments);
- Current cycle state and progress.

This context is loaded at the start of every content cycle and
updated as the cycle progresses.

### Cycle Management

The Orchestrator Agent manages progression through the Content
Cycle stages:

```text
Signal → Insight → Decision → Creation → Production →
Distribution → Analysis → Learning → Optimization
```

The Orchestrator:
- initiates each stage;
- monitors completion;
- evaluates stage outputs;
- decides whether to progress, repeat or halt;
- manages parallel cycles for different content pillars or
  channels.

Reference: `CONTENT_CYCLE_SPEC.md`

### Decision Making

The Orchestrator Agent answers operational questions:

- Which market signal is worth acting on?
- Which content opportunity to pursue?
- What content to create?
- Which format best serves the goal?
- Which channel is optimal for this content?
- When is human input required?
- What action comes next in the cycle?

Each decision is recorded as a Decision Record for audit and
learning.

### Tool Coordination

The Orchestrator Agent selects and coordinates tools.

It does not execute tools directly. It composes tool chains.

Example:

```text
Orchestrator decision: "Create educational carousel for LinkedIn"

    ↓ invokes

Content Intelligence Module → analyzes patterns, suggests format

    ↓ invokes

Production Tool → generates carousel content

    ↓ invokes

QA Tool → validates brand voice, restrictions, format compliance

    ↓ invokes

Export Tool → assembles platform-ready export package
```

The Orchestrator defines the sequence, provides context
parameters and evaluates results at each step.

## 4.3. Operational Boundaries

The Orchestrator Agent operates within:

- **Brand System boundaries** — cannot violate brand identity or
  communication rules;
- **Restriction boundaries** — cannot generate forbidden topics
  or claims;
- **Goal boundaries** — must serve defined business goals;
- **Autonomy boundaries** — scope of independent action defined
  by the selected mode;
- **Confidence boundaries** — must escalate when below
  confidence threshold.

## 4.4. Orchestrator State

At any point, the Orchestrator maintains:

- active content cycles and their current stages;
- pending decisions;
- queued tool executions;
- recent outcomes awaiting evaluation;
- learning observations to be stored.

## 4.5. Relationship to Other Components

```text
Orchestrator Agent
    │
    ├── reads from → Brand System (stable context)
    ├── reads from → Project Settings (operational parameters)
    ├── queries → Intelligence Modules (analysis and insight)
    ├── invokes → Production Tools (execution)
    ├── writes to → Learning Memory (accumulated knowledge)
    ├── records → Decision Records (audit trail)
    └── escalates to → Human Operator (when needed)
```

---

# 5. Intelligence Modules

## 5.1. Definition

Intelligence Modules are specialized analytical capabilities
within LOOPRA.

They are NOT independent agents.

They do not make autonomous decisions.

They provide structured analysis, insight and recommendations
that the Orchestrator Agent integrates into its decisions.

Each module has a defined input, processing responsibility and
output.

## 5.2. Module Principles

- Single responsibility — each module answers one category of
  questions;
- No independent action — modules analyze, Orchestrator decides;
- Stateless analysis — modules process current inputs against
  stored knowledge;
- Structured output — modules return typed entities the
  Orchestrator can reason about.

---

## 5.3. Trend Intelligence Module

### Responsibility

Analyze the external environment to find signals and patterns
that create marketing opportunities.

### Capabilities

- market signal monitoring;
- trend detection and pattern recognition;
- competitor activity analysis;
- audience behaviour shift identification;
- platform change detection;
- relevance filtering against Brand System and goals.

### Input

- external environment data (social trends, platform signals,
  competitor activity);
- audience behaviour data;
- internal performance history.

### Output

- `MarketSignal` — a structured observation of external change;
- `TrendPattern` — an identified pattern of content behaviour;
- opportunity assessments with relevance scoring.

### Relationship to Orchestrator

The Orchestrator queries Trend Intelligence to answer:

"What is happening in the market that is relevant to this
brand?"

### Future Specification

`TREND_INTELLIGENCE_SPEC.md` will define the detailed analysis
model, signal processing and pattern detection logic.

---

## 5.4. Content Intelligence Module

### Responsibility

Determine which content has strategic potential given the
intersection of brand context and market intelligence.

### Capabilities

- successful content pattern analysis;
- format effectiveness evaluation;
- topic and theme identification;
- Content Opportunity generation;
- content recommendation formulation;
- learning-informed content selection.

### Input

- Brand System (identity, audience, tone, strategy);
- Trend Patterns from Trend Intelligence;
- Learning Memory (past content performance);
- audience content preferences;
- channel constraints.

### Output

- Content Opportunity — a structured recommendation including
  topic, format, channel, audience segment, content pillar and
  expected impact.

### Relationship to Orchestrator

The Orchestrator queries Content Intelligence to answer:

"Given who we are and what is happening in the market, what
content should we create?"

### Future Specification

`CONTENT_INTELLIGENCE_SPEC.md` will define the opportunity
formation model, content recommendation logic and format
selection criteria.

---

## 5.5. Analytics Intelligence Module

### Responsibility

Transform performance data into understanding — analyze results
and form hypotheses about what worked and why.

### Capabilities

- performance outcome analysis;
- root cause identification for successes and failures;
- hypothesis formation about content effectiveness;
- deviation detection from expected outcomes;
- optimization opportunity identification.

### Input

- performance data (MetricSnapshot records);
- comparison against goals and KPIs;
- past performance history;
- content and channel context.

### Output

- insights — structured conclusions about content performance;
- hypotheses — testable explanations for observed outcomes;
- optimization recommendations.

### Relationship to Orchestrator

The Orchestrator queries Analytics Intelligence to answer:

"What happened, why did it happen and what should we do
differently?"

---

## 5.6. Learning Memory Module

### Responsibility

Store, organize and retrieve operational experience across
cycles to improve future decisions.

### Capabilities

- persistent storage of successful and failed patterns;
- retrieval of similar past situations;
- knowledge organization by category (pillar, audience,
  channel, format, goal);
- confidence scoring based on past evidence;
- pattern reinforcement and decay over time.

### Input

- performance outcomes and insights;
- Decision Records and their results;
- experiment outcomes;
- human feedback and approvals.

### Output

- relevant past knowledge for current decisions;
- confidence estimates based on historical evidence;
- recommended patterns for new situations;
- warnings about previously failed approaches.

### Critical Constraint

Learning Memory does NOT change Brand Identity.

```text
Brand System:     "We communicate with professional, trustworthy
                  expertise"
Learning Memory:  "Humorous content generates higher engagement"
Decision:         Do NOT switch to humor if it contradicts brand
                  tone

Learning Memory optimizes WITHIN brand boundaries, not beyond
them.
```

### Relationship to Orchestrator

The Orchestrator queries Learning Memory to answer:

"What does past experience tell us about this situation?"

### Future Specification

`LEARNING_MEMORY_SPEC.md` will define the knowledge model,
storage structure, retrieval mechanisms and pattern maintenance
logic.

---

## 5.7. Module Interaction Model

Intelligence Modules do not call each other directly.

The Orchestrator Agent is the only component that:

- queries modules;
- receives module outputs;
- integrates multiple module insights;
- makes decisions based on combined intelligence.

```text
                    Orchestrator Agent
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ↓              ↓              ↓
    Trend          Content         Analytics
  Intelligence   Intelligence    Intelligence
          │              │              │
          └──────────────┼──────────────┘
                         │
                         ↓
                  Learning Memory
```

This ensures coherent decision-making without module conflicts.

---

# 6. Agent Decision Model

## 6.1. Decision Flow

Every operational decision in LOOPRA follows a structured flow:

```text
Input:
    Context         — Brand System, Project Settings, current state
    + Goal          — what the brand aims to achieve
    + Rules         — restrictions, constraints, boundaries
    + Memory        — past experience, patterns, outcomes
    + Signals       — current market and performance data
        ↓
    Reasoning       — Orchestrator processes inputs
        ↓
    Decision        — selected action with rationale
        ↓
    Action          — tool invocation or escalation
        ↓
    Result          — outcome captured
        ↓
    Learning        — decision + result stored in Learning Memory
```

## 6.2. Decision Record

Every significant Orchestrator decision is stored as a Decision
Record containing:

| Field | Description |
|---|---|
| Context | What was the situation when the decision was made? |
| Decision | What action was chosen? |
| Reasoning | Why was this action chosen over alternatives? |
| Confidence | How certain was the system about this decision? |
| Expected Outcome | What result was predicted? |
| Actual Result | What actually happened? (filled after execution) |
| Timestamp | When was the decision made? |
| Cycle Reference | Which content cycle does this belong to? |

Reference: `DATA_MODEL.md`, Section 4.5 — `AgentDecision`

## 6.3. Decision Categories

Orchestrator decisions fall into categories:

| Category | Example |
|---|---|
| Signal Selection | "Trend Y is relevant and worth acting on" |
| Opportunity Selection | "Opportunity Z has highest potential for goal X" |
| Content Creation | "Create educational carousel for this topic" |
| Format Selection | "Video performs better than static for this goal" |
| Channel Selection | "This content fits LinkedIn over Instagram" |
| Experiment Design | "Test format X against format Y for this segment" |
| Cycle Progression | "Advance cycle from Creation to Production" |
| Optimization | "Increase carousel share based on recent performance" |
| Escalation | "This decision requires human review" |

---

# 7. Confidence and Escalation Model

## 7.1. Confidence Levels

LOOPRA must understand its own confidence in each decision.

Three confidence levels:

### High Confidence

- strong supporting evidence from Learning Memory;
- clear alignment with Brand System and goals;
- well-understood pattern with consistent past results;
- no restriction concerns.

**Behaviour:** action executed automatically.

### Medium Confidence

- some supporting evidence but not definitive;
- pattern recognized but not strongly validated;
- minor uncertainty about audience response;
- standard execution path.

**Behaviour:** action executed, flagged for human review.

### Low Confidence

- insufficient evidence;
- new or unfamiliar situation;
- potential restriction proximity;
- significant deviation from past patterns;
- high-impact decision.

**Behaviour:** escalated to human operator.

## 7.2. Factors Influencing Confidence

Confidence is derived from:

- **Evidence Strength** — how many past cycles support this
  decision;
- **Pattern Similarity** — how closely current situation matches
  known patterns;
- **Brand Alignment** — how well the decision fits Brand System;
- **Risk Level** — potential negative impact of a wrong decision;
- **Goal Criticality** — how important this decision is to
  business goals.

## 7.3. Escalation Triggers

The Orchestrator escalates to human attention when:

- confidence falls below the autonomy threshold;
- a restriction boundary is approached;
- performance drops below defined thresholds;
- an unexpected market shift is detected;
- the decision is outside standard operational patterns;
- Learning Memory contains warnings about similar past
  situations;
- the selected autonomy mode requires checkpoint approval.

## 7.4. Autonomy vs Confidence

Autonomy mode determines the confidence threshold for automatic
action:

```text
Copilot mode:   every decision requires human approval regardless
                of confidence

Assisted mode:  high-confidence decisions proceed automatically;
                medium/low require review

Autopilot mode: high and medium-confidence decisions proceed;
                only low confidence escalates
```

All modes retain emergency stop and human override capability.

---

# 8. Human Approval Model

## 8.1. Autonomy Modes

LOOPRA supports three progressive autonomy levels.

The human selects one per project.

### Copilot Mode

**Principle:** LOOPRA suggests. Human decides.

- LOOPRA analyzes signals and proposes opportunities;
- every decision requires human approval;
- content drafts are presented for review;
- the human makes all final decisions.

**Current Foundation MVP default.**

### Assisted Mode

**Principle:** LOOPRA operates with periodic human checkpoints.

- routine actions execute autonomously;
- strategic decisions await confirmation;
- defined checkpoints require human review;
- examples: after opportunity selection, before publication,
  after weekly analytics.

### Autopilot Mode

**Principle:** LOOPRA operates autonomously within defined rules.

- content cycles launch and execute independently;
- decisions are made within confidence boundaries;
- performance is continuously analyzed;
- optimization applied automatically.

But always with:
- control points;
- operational limits;
- emergency stop;
- periodic review checkpoints.

Reference: `USER_WORKFLOWS.md`, Section 8

## 8.2. Universal Human Controls

Regardless of autonomy mode, the human always retains:

- **Emergency Stop** — immediately pause all active cycles;
- **Reduce Autonomy** — drop from Autopilot to Assisted or
  Copilot;
- **Change Rules** — modify restrictions, forbidden topics or
  goals that affect running cycles;
- **Review Decision** — inspect any autonomous decision the
  system made;
- **Audit Trail** — complete history of all agent decisions and
  tool executions.

## 8.3. Control Points

Structured control points ensure human governance even in
autopilot:

- **Weekly Review** — summary of content published, performance
  metrics, learning insights, recommendations;
- **Content Approval Gates** — configurable per content type or
  channel;
- **Performance Review** — periodic verification of goal
  achievement, quality maintenance, brand consistency;
- **Boundary Check** — verification that restrictions remain
  respected.

---

# 9. Agent Interaction with Content Cycle

## 9.1. Cycle Stage Participation

The Agent System interacts with the LOOPRA Content Cycle at
every stage.

Reference: `CONTENT_CYCLE_SPEC.md`

### Stages 1-3: Intelligence Modules Provide Understanding

```text
Stage 1 — Market Signal Discovery
    Trend Intelligence monitors and detects signals.

Stage 2 — Trend Understanding
    Trend Intelligence transforms signals into patterns.

Stage 3 — Content Opportunity Creation
    Content Intelligence combines trends, Brand System, audience
    and Learning Memory to form structured opportunities.
```

During these stages, the Orchestrator queries modules and
aggregates their outputs.

### Stage 4: Orchestrator Makes Decisions

```text
Stage 4 — Strategic Decision
    The Orchestrator Agent evaluates opportunities against goals,
    strategy, constraints and Learning Memory.
    
    It makes the decision: create, defer, experiment, decline or
    escalate.
    
    Each decision is recorded as a Decision Record.
```

### Stages 5-7: Tools Execute

```text
Stage 5 — Content Creation
    Production Tools generate scenarios and content items based
    on the Orchestrator's decision.

Stage 6 — Production
    Production Tools assemble finished content into export
    packages with quality validation.

Stage 7 — Distribution
    Distribution Tools prepare and deliver content to target
    channels.
```

The Orchestrator coordinates tool chains but does not execute
them directly.

### Stages 8-10: Analytics and Learning Improve Future Decisions

```text
Stage 8 — Performance Analysis
    Analytics Intelligence processes performance data and
    generates insights.

Stage 9 — Learning Memory Update
    Learning Memory stores new knowledge — what worked, what did
    not, why.

Stage 10 — Optimization
    The Orchestrator applies accumulated learning to improve the
    next cycle's parameters.
```

## 9.2. Cycle Orchestration Flow

```text
Cycle Start
    ↓
Orchestrator loads Brand System + Project Settings + Learning Memory
    ↓
Orchestrator queries Trend Intelligence → Market Signals
    ↓
Orchestrator queries Trend Intelligence → Trend Patterns
    ↓
Orchestrator queries Content Intelligence → Content Opportunities
    ↓
Orchestrator makes Strategic Decision (with human approval if needed)
    ↓
Orchestrator invokes Production Tools → Content Creation + Production
    ↓
Orchestrator invokes Distribution Tools → Publication
    ↓
Orchestrator queries Analytics Intelligence → Performance Insights
    ↓
Orchestrator writes to Learning Memory → New Knowledge
    ↓
Orchestrator applies Optimization → Improved Next Cycle
```

---

# 10. Agent Memory Model

## 10.1. Three Memory Types

The LOOPRA Agent System maintains three distinct memory types
with different purposes, lifetimes and behaviours.

### Context Memory

**What it stores:**

The current operational context for the active project:

- Brand System (identity, audience, tone, strategy, restrictions);
- Project Settings (goals, channels, content types, constraints);
- current cycle state and progress;
- active decisions and pending actions.

**Lifetime:** loaded at cycle start, updated during cycle, relates
to current operation.

**Purpose:** answers "What is the current situation?"

### Operational Memory

**What it stores:**

Knowledge about what works and what does not:

- successful content patterns and their characteristics;
- failed experiments and the reasons they failed;
- audience response patterns across segments;
- format effectiveness by channel and goal;
- timing and frequency insights;
- accumulated statistical evidence for decisions.

**Lifetime:** persistent across cycles, evolves continuously.

**Purpose:** answers "What works best in practice?"

This is Learning Memory as defined in the Intelligence Module
layer.

### Decision Memory

**What it stores:**

Records of why the system made each decision:

- Decision Records with context, reasoning, confidence;
- expected vs actual outcomes;
- decision chains — how earlier decisions led to later ones;
- escalation decisions and their resolutions.

**Lifetime:** permanent audit trail, used for learning.

**Purpose:** answers "Why did the system choose this action?"

## 10.2. Memory Interaction

```text
Context Memory
    │  "What is the current situation?"
    ↓
Decision Making
    │  uses Context + Operational Memory
    ↓
Decision Memory
    │  "Why did we decide this?"
    ↓
Result captured
    ↓
Operational Memory updated
    │  "What did we learn?"
    ↓
Next cycle begins with improved memory
```

## 10.3. Memory Separation

- Context Memory and Operational Memory (Learning Memory) are
  project-scoped — each project has its own.
- Decision Memory provides an audit trail per project.
- No memory is shared across projects.

---

# 11. Agent Safety and Boundaries

## 11.1. Inviolable Constraints

Agents within LOOPRA CANNOT:

- **change Brand Identity** — the Brand System is set by the
  human and is read-only for agents;
- **violate restrictions** — forbidden topics, claims and
  compliance rules are absolute boundaries;
- **ignore business goals** — all content must serve defined
  goals;
- **bypass human controls** — emergency stop, autonomy reduction
  and rule changes are always available;
- **escalate autonomy** — agents cannot increase their own
  autonomy level; only the human can;
- **share data across projects** — project isolation is absolute.

## 11.2. Operational Guardrails

- **Content validation** — all generated content is checked
  against restrictions before publication;
- **Goal alignment** — every content decision is verified against
  active goals;
- **Brand voice check** — content is validated for tone and voice
  consistency;
- **Frequency limits** — publishing cadence respects defined
  parameters;
- **Channel constraints** — content is adapted to channel
  requirements.

## 11.3. Failure Behaviour

When the agent system encounters uncertainty:

- the Orchestrator does not guess;
- low-confidence decisions are escalated;
- content that might violate restrictions is blocked;
- cycles can be paused for human review;
- errors are recorded with context for debugging.

---

# 12. Current Foundation MVP Relationship

## 12.1. The Critical Distinction

The current Foundation MVP does NOT contain a full agent system.

The Foundation MVP is:

```text
Human
    ↓
Manual Input (Idea creation)
    ↓
Deterministic Pipeline (Scenario → ContentItem → ExportPackage →
Publication → MetricSnapshot)
```

It is a validated execution baseline with manual inputs and
deterministic processing.

## 12.2. Future Architecture

The Agent System wraps around the Foundation MVP as the
intelligence layer:

```text
Human
    ↓
Orchestrator Agent
    ↓
Intelligence Modules
    ↓
Deterministic Tools (Foundation MVP pipeline)
    ↓
Analytics + Learning Memory
    ↓
Next Cycle
```

The Foundation MVP pipeline (Idea → Scenario → ContentItem →
ExportPackage → Publication → MetricSnapshot) becomes the
execution layer for the Agent System.

## 12.3. What Changes

```text
Current Foundation MVP:
    Human creates Idea → Pipeline executes → Manual publication →
    Manual metrics

Future Agent System:
    Orchestrator discovers opportunities → Intelligence Modules
    inform decisions → Pipeline executes → Automated or
    checkpointed publication → Automated metrics → Learning
    Memory improves next cycle
```

## 12.4. What Stays

The Foundation MVP execution primitives remain the production
backbone:

- `Idea` — the creative concept (source becomes Intelligence
  Layer, not manual);
- `Scenario` — the content plan;
- `ContentItem` — the produced content unit;
- `ExportPackage` — the prepared distribution package;
- `Publication` — the publication record;
- `MetricSnapshot` — the performance data record.

These entities are not replaced. They become tools invoked by the
Orchestrator Agent.

## 12.5. Evolution Path

```text
Foundation MVP (current)
    Deterministic pipeline
    Manual inputs
    Copilot mode only
        ↓
Content Intelligence (next)
    Signal analysis begins
    Pattern recognition
    Opportunity generation
        ↓
Agentic Operations
    Orchestrator Agent active
    Decision automation
    Learning Memory operational
        ↓
Marketing Operating System
    Full autonomous cycles
    Continuous self-improvement
```

The Agent System specification defines the architecture for the
future. It is not implemented in the current Foundation MVP.

---

# 13. Future Agent Evolution

## 13.1. Stage 1 — Orchestrator as Assistant

The Orchestrator Agent operates in advisory mode:

- analyzes signals and proposes opportunities;
- recommends content decisions;
- suggests optimizations;
- all decisions require human approval;
- copilot mode only.

The Orchestrator learns from human choices — observing which
proposals are accepted and which are rejected.

## 13.2. Stage 2 — Limited Autonomous Decisions

The Orchestrator gains authority for routine decisions:

- standard content creation within well-understood patterns;
- channel selection based on historical performance;
- format selection within brand preferences;
- assisted mode active;
- strategic decisions remain human-approved.

Confidence model begins to determine when autonomy is appropriate.

## 13.3. Stage 3 — Autonomous Content Cycles

The Orchestrator manages complete cycles independently:

- signal discovery through to optimization;
- Learning Memory drives continuous improvement;
- autopilot mode for routine operations;
- human oversight through control points and reviews;
- escalation only for exceptions and edge cases.

## 13.4. Stage 4 — Full Marketing Operating System

The Orchestrator operates as a true autonomous marketing system:

- multi-cycle parallel operation across channels and pillars;
- continuous optimization without manual intervention;
- autonomous experiment design and execution;
- proactive opportunity discovery;
- human role shifts to strategic governance and direction
  setting.

---

# 14. Related Documents

## 14.1. Core Architecture

```text
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
```

## 14.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
docs/00_foundation/MVP_SCOPE.md                     — Foundation MVP scope
```

## 14.3. Product Layer

```text
docs/01_product/LOOPRA_BRAND_POSITIONING.md         — LOOPRA product identity
docs/01_product/USER_WORKFLOWS.md                   — User interaction model
```

## 14.4. Intelligence Layer

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Content Cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — This document
```

## 14.5. Future Documents

```text
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — Trend detection specification
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content insight specification
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory specification
docs/04_production/CONTENT_TYPES_SPEC.md            — Content format definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — Production workflow specification
docs/04_production/CONTENT_OPERATING_SYSTEM_SPEC.md — Autonomous cycle execution
```

## 14.6. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# 15. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Intelligence Layer — Agent System Specification |

---

# Final Statement

The LOOPRA Agent System is not a collection of independent AI
agents.

It is a structured intelligence layer built on three principles:

1. **Orchestration** — one Orchestrator Agent coordinates
   specialized modules.
2. **Separation** — Agents decide. Tools execute.
3. **Human Authority** — the human sets direction, rules and
   boundaries; the system operates within them.

The Orchestrator Agent transforms market signals, brand context
and performance data into marketing decisions.

Intelligence Modules provide analytical depth.

Production Tools execute deterministic actions.

Learning Memory accumulates experience.

Together they form a continuous intelligent operating cycle that
improves with every iteration.

This specification is the architectural blueprint for building the
intelligence that transforms LOOPRA from a deterministic
production pipeline into a self-learning autonomous marketing
operating system.

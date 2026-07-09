# CONTENT CYCLE SPEC

## Version

v1.0

## Status

Active — LOOPRA Intelligence Layer

## Purpose

This document defines the LOOPRA Content Cycle — the primary operational
model of the Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA transform market signals into content, results and
> improved next cycles?

CONTENT_CYCLE_SPEC.md is the functional bridge between Business Vision
and Future Intelligence Implementation.

It describes:

- the stages of the LOOPRA content cycle;
- component responsibilities at each stage;
- inputs, outputs and transitions between stages;
- how Learning Memory accumulates operational experience;
- how each cycle improves upon the previous one;
- the relationship between the future LOOPRA Cycle and the current
  Foundation MVP.

It does NOT describe:

- UI, API or database implementation;
- specific AI providers, model selection or agent prompts;
- code-level implementation details.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

CONTENT_CYCLE_SPEC.md defines the continuous marketing cycle model that
LOOPRA operates.

It serves as the functional specification for how LOOPRA moves from
market awareness to content production to performance measurement to
continuous learning — forming a self-improving loop.

## 1.2. Scope

This document covers:

- the full LOOPRA operating cycle from Signal to Next Cycle;
- the participants in the cycle and their responsibilities;
- each stage's purpose, inputs, outputs and transitions;
- the impact of autonomy modes on cycle execution;
- cycle lifecycle states;
- the relationship between the future LOOPRA Cycle and the current
  Foundation MVP.

## 1.3. Out of Scope

This document does not cover:

- UI components, API contracts, database schemas;
- implementation details of AI models, prompts or providers;
- specific content format specifications (see future
  `CONTENT_TYPES_SPEC.md`);
- detailed agent decision algorithms (see future
  `AGENT_SYSTEM_SPEC.md`);
- external platform integration mechanics (see future
  `INTEGRATIONS_SPEC.md`).

---

# 2. LOOPRA Content Cycle Overview

## 2.1. The Core Cycle

LOOPRA does not create individual pieces of content.

LOOPRA manages a continuous cycle:

```text
Market Signals
    ↓
Trend Understanding
    ↓
Content Opportunities
    ↓
Strategic Decisions
    ↓
Content Creation
    ↓
Production
    ↓
Distribution
    ↓
Performance Analysis
    ↓
Learning Memory
    ↓
Optimization
    ↓
Next Cycle
```

## 2.2. The Fundamental Principle

Each completed cycle feeds the next cycle with knowledge:

- what worked — reinforced in future decisions;
- what did not work — avoided in future decisions;
- new patterns discovered — tested in future experiments;
- audience signals decoded — applied to future content.

The system does not restart each cycle.

It accumulates context, experience and patterns that compound over time.

## 2.3. Cycle vs Content Item

A common misunderstanding is that LOOPRA creates content items.

LOOPRA operates cycles.

A cycle may produce one or many content items across multiple channels.

The cycle is the operational unit.

Content items are outputs within a cycle.

## 2.4. Relationship to Brand System

The Brand System provides stable context for every cycle:

- who the brand is;
- who it speaks to;
- how it communicates;
- what it must never do;
- what goals it pursues.

Reference: `BRAND_SYSTEM_SPEC.md`

The Content Cycle reads Brand System at cycle start and applies it
consistently throughout.

Brand System is stable. Learning Memory evolves.

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

---

# 3. Cycle Participants

## 3.1. Participant Overview

Five types of participants interact within the LOOPRA Content Cycle:

```text
Human Operator
    ↓  sets direction, approves, adjusts
Orchestrator Agent
    ↓  manages cycles, coordinates, decides
Intelligence Modules
    ↓  analyzes, discovers, recommends
Production Tools
    ↓  executes, generates, assembles
Learning Memory
    ↓  accumulates, retrieves, informs
```

## 3.2. Human Operator

The human is the operator of an autonomous marketing system, not a
content creator.

Responsibilities:

- define business goals and strategic direction;
- configure Brand System (identity, audience, tone, strategy,
  restrictions);
- select autonomy mode (Copilot, Assisted, Autopilot);
- approve or reject decisions at control points;
- provide feedback on outcomes;
- adjust rules based on business context changes;
- handle exceptions and edge cases.

The human provides what AI cannot:

- strategic vision;
- brand intuition;
- ethical boundaries;
- creative direction;
- business context.

Reference: `USER_WORKFLOWS.md`

## 3.3. Orchestrator Agent

The Orchestrator Agent is the central decision-making component of the
LOOPRA Content Cycle.

Responsibilities:

- manage content cycle progression between stages;
- coordinate tools, services and intelligence modules;
- make operational decisions within defined boundaries;
- launch content creation and distribution actions;
- evaluate cycle results;
- decide on optimizations for the next cycle;
- escalate uncertain situations to the human operator.

Principle:

> Agents decide. Tools execute.

The Orchestrator Agent does not replace deterministic production
systems. It orchestrates them.

Reference: `LOOPRA_ARCHITECTURE.md`, Section 6

## 3.4. Intelligence Modules

Intelligence Modules provide the analysis and insight layer that
informs the Orchestrator Agent's decisions.

### Trend Intelligence

Finds market signals, detects emerging patterns, tracks competitor
activity, identifies audience behaviour shifts.

### Content Intelligence

Identifies which content directions have potential: successful
formats, effective topics, engagement patterns, audience content
preferences.

### Analytics Intelligence

Analyzes performance results: what worked, what did not, why,
deviations from expected outcomes, hypotheses for improvement.

Reference: `SYSTEM_ARCHITECTURE.md`, Section 7

## 3.5. Production Tools

Production Tools execute deterministic content creation.

They receive instructions from the Orchestrator Agent and produce:

- scenarios and content plans;
- text content (posts, articles);
- visual content (images, carousels);
- video content (scripts, renders);
- export and publication packages.

Production Tools do not make strategic decisions.

They execute what the Orchestrator Agent defines.

## 3.6. Learning Memory

Learning Memory is the long-term operational memory of LOOPRA.

It stores:

- successful decisions and their context;
- failed experiments and why they failed;
- accumulated operational knowledge;
- repeatable patterns;
- audience response patterns.

Learning Memory does NOT change Brand Identity.

It changes the system's understanding of effectiveness.

Learning Memory evolves continuously. It optimizes execution within
brand boundaries.

Reference: `DATA_MODEL.md`, Section 4.6

---

# 4. Stage 1 — Market Signal Discovery

## 4.1. Purpose

Find meaningful changes in the external environment that may create
marketing opportunities.

## 4.2. Signal Sources

LOOPRA monitors multiple signal sources:

| Source | Examples |
|---|---|
| Social Trends | Emerging topics, viral formats, cultural shifts |
| Audience Behaviour | New consumption patterns, platform migration, engagement shifts |
| Competitor Activity | New content directions, format adoption, strategy changes |
| Platform Signals | Algorithm updates, new features, format support changes |
| Internal Performance Data | Past cycle results, audience feedback patterns, metric anomalies |

## 4.3. Signal Categories

Signals may be:

- **Emerging** — new pattern detected, too early to confirm;
- **Growing** — pattern strengthening, potential opportunity;
- **Mature** — established trend, worth acting on;
- **Declining** — fading trend, avoid investing.

## 4.4. Inputs and Outputs

```text
Input:     External environment (market, audience, competitors, platforms)
              ↓
Stage:     Market Signal Discovery
              ↓
Output:    MarketSignal
              ↓
Next:      Trend Intelligence → Stage 2
```

A `MarketSignal` is a structured observation of external change.

Reference: `DATA_MODEL.md`, Section 4.1

---

# 5. Stage 2 — Trend Understanding

## 5.1. Purpose

Transform raw market signals into understandable patterns that can
inform content decisions.

## 5.2. Process

```text
Signal
    ↓
Pattern Detection — group related signals, identify common themes
    ↓
Trend Pattern — structured understanding of what is happening
    ↓
Opportunity Assessment — evaluate relevance and potential
    ↓
Output: TrendPattern
```

## 5.3. Pattern Types

Trend Intelligence identifies pattern types:

| Pattern Type | Example |
|---|---|
| Hook Pattern | "Question-based hooks generate 3x more engagement" |
| Topic Pattern | "Sustainability content is growing in this audience segment" |
| Format Pattern | "Short educational videos outperform static carousels" |
| Timing Pattern | "Tuesday morning posts receive higher initial reach" |
| Audience Pattern | "This demographic is moving from Platform A to Platform B" |

## 5.4. Relevance Filtering

Not every trend is relevant.

Trend Intelligence filters by:

- alignment with Brand System identity and strategy;
- applicability to defined audience segments;
- feasibility within current production capabilities;
- compatibility with channel constraints;
- relationship to defined business goals.

## 5.5. Inputs and Outputs

```text
Input:     MarketSignal (from Stage 1)
              ↓
Stage:     Trend Understanding
              ↓
Output:    TrendPattern
              ↓
Next:      Content Intelligence → Stage 3
```

A `TrendPattern` is a structured description of an identified content
pattern.

Reference: `DATA_MODEL.md`, Section 4.2

---

# 6. Stage 3 — Content Opportunity Creation

## 6.1. Purpose

Determine which content has strategic potential given the intersection
of brand context and market intelligence.

## 6.2. Opportunity Formation

Content Opportunities are formed by combining:

```text
Trend          — what is happening in the market
    +
Brand System   — who we are and how we communicate
    +
Audience       — who we speak to and what they need
    +
Goals          — what we aim to achieve
    +
Previous Learning — what has worked before
    =
Content Opportunity
```

## 6.3. Opportunity Example

```text
Trend Pattern:
"Short educational videos are growing in reach and engagement
among professional audiences."

    +

Brand System:
"We are recognized experts in our domain. Our tone is
professional, educational and trustworthy."

    +

Audience:
"Professionals seeking practical knowledge to advance their
careers."

    +

Goals:
"Engagement and authority building."

    +

Learning:
"Video content under 60 seconds with text overlays performed
well in the previous cycle."

    =

Content Opportunity:
"Create a series of short educational videos (under 60 seconds)
demonstrating professional expertise through practical tips,
with text overlays for accessibility."
```

## 6.4. Opportunity Components

Each Content Opportunity includes:

- **Topic** — what to create content about;
- **Format** — which content format is suitable;
- **Channel** — which distribution channel is optimal;
- **Audience Segment** — which audience subset is targeted;
- **Content Pillar** — which strategic pillar this serves;
- **Expected Impact** — predicted effectiveness based on past data.

## 6.5. Inputs and Outputs

```text
Input:     TrendPattern (from Stage 2)
           Brand System context
           Learning Memory
              ↓
Stage:     Content Opportunity Creation
              ↓
Output:    Content Opportunity
              ↓
Next:      Orchestrator Agent → Stage 4
```

---

# 7. Stage 4 — Strategic Decision

## 7.1. Purpose

The Orchestrator Agent evaluates content opportunities and decides
which actions to take.

## 7.2. Decision Factors

The Orchestrator Agent considers:

| Factor | Question Answered |
|---|---|
| Business Goals | Does this opportunity serve active goals? |
| Strategy Alignment | Does this fit the defined content strategy? |
| Resource Constraints | Can the system produce this now? |
| Channel Fit | Is this suitable for available channels? |
| Learning Memory | What does past experience indicate? |
| Brand Restrictions | Does this violate any rules? |
| Autonomy Mode | How much independent authority is permitted? |
| Priority | How important is this relative to other opportunities? |

## 7.3. Decision Types

Possible Orchestrator decisions:

- **Create** — approve the opportunity, proceed to creation;
- **Defer** — save the opportunity for a later cycle;
- **Experiment** — test the opportunity at small scale;
- **Decline** — reject the opportunity with reasoning stored in
  Learning Memory;
- **Escalate** — request human input (in Copilot/Assisted modes).

## 7.4. Decision Record

Every strategic decision is recorded as an `AgentDecision`.

This enables:

- auditing of system choices;
- learning from decision outcomes;
- transparency for the human operator;
- pattern analysis of successful decision chains.

Reference: `DATA_MODEL.md`, Section 4.5

## 7.5. Inputs and Outputs

```text
Input:     Content Opportunity (from Stage 3)
           Brand System context
           Learning Memory
           Autonomy Settings
              ↓
Stage:     Strategic Decision
              ↓
Output:    Content Decision (create / defer / experiment / decline)
              ↓
Next:      Content Creation → Stage 5  (if "create" or "experiment")
```

---

# 8. Stage 5 — Content Creation

## 8.1. Purpose

Transform a Content Decision into a structured content plan ready for
production.

## 8.2. Creation Flow

```text
Content Decision
    ↓
Idea — the creative concept, scoped to the project
    ↓
Scenario — the content plan with structure, tone, objectives
    ↓
ContentItem — the produced content unit, ready for export
```

## 8.3. Relationship to Foundation MVP

This stage preserves the Foundation MVP pipeline as the execution
baseline:

```text
Idea → Scenario → ContentItem
```

In the future LOOPRA Cycle, the source of the Idea becomes the
Intelligence Layer (Stages 1–4), not manual human definition.

The execution pipeline itself remains the same validated foundation.

## 8.4. Content Creation Context

Content Creation uses:

- the Content Decision from Stage 4;
- Brand System for tone, voice, restrictions;
- channel parameters for format adaptation;
- Learning Memory for effective patterns.

## 8.5. Inputs and Outputs

```text
Input:     Content Decision (from Stage 4)
           Brand System context
           Channel specifications
              ↓
Stage:     Content Creation
              ↓
Output:    ContentItem (produced content unit)
              ↓
Next:      Production → Stage 6
```

Reference: `PIPELINES_SPEC.md`

---

# 9. Stage 6 — Production

## 9.1. Purpose

Transform content plans into finished, distribution-ready outputs.

## 9.2. Production by Content Type

Production handles format-specific creation:

### Text

- social post;
- article;
- caption generation.

### Visual

- image creation;
- carousel assembly;
- branded graphics.

### Video

- script generation;
- voiceover;
- visuals and motion;
- subtitles;
- branding overlay;
- final render.

Specific content format definitions will be documented in the future
`CONTENT_TYPES_SPEC.md`.

## 9.3. Quality Assurance

Production includes quality checks:

- brand voice consistency;
- restriction compliance;
- format specification adherence;
- channel requirements satisfaction;
- technical validity (length, aspect ratio, formatting).

## 9.4. Export Package

Production assembles `ExportPackage` — structured output ready for
distribution:

```text
ExportPackage
    ├── content files (text, image, video)
    ├── captions and descriptions
    ├── metadata (timestamps, versions, references)
    └── publication instructions
```

Reference: `PIPELINES_SPEC.md`, Section 6

## 9.5. Inputs and Outputs

```text
Input:     ContentItem (from Stage 5)
           Format specifications
           Channel parameters
              ↓
Stage:     Production
              ↓
Output:    ExportPackage (ready for distribution)
              ↓
Next:      Distribution → Stage 7
```

---

# 10. Stage 7 — Distribution

## 10.1. Purpose

Deliver finished content to target channels.

## 10.2. Distribution Activities

Distribution includes:

- **Publication Preparation** — final formatting, channel-specific
  adaptation;
- **Channel Adaptation** — caption formatting, hashtag application,
  platform constraints;
- **Scheduling** — publication timing according to configured
  preferences (future scope);
- **Publishing Workflow** — content delivery to target platforms;
- **Publication Recording** — storing publication outcome data
  (URL, timestamp, platform).

## 10.3. Current Foundation MVP State

In the current Foundation MVP:

- distribution is export-first;
- publishing is manual (outside the system);
- `Publication` records store manual publication outcomes.

Autoposting and automated distribution are future capabilities.

Reference: `MVP_SCOPE.md`, Section 5

## 10.4. Inputs and Outputs

```text
Input:     ExportPackage (from Stage 6)
           Channel configuration
           Schedule preferences (future)
              ↓
Stage:     Distribution
              ↓
Output:    Publication record
              ↓
Next:      Performance Analysis → Stage 8
```

---

# 11. Stage 8 — Performance Analysis

## 11.1. Purpose

Collect and analyze the results of distributed content to understand
what happened and why.

## 11.2. Data Collection

After publication, LOOPRA collects:

| Metric Category | Examples |
|---|---|
| Reach | Views, impressions, unique viewers |
| Engagement | Likes, comments, saves, shares |
| Retention | Watch time, completion rate, return visits |
| Conversions | Link clicks, form submissions, purchases |
| Audience Feedback | Comments sentiment, direct messages, shares |

## 11.3. Current Foundation MVP State

In the current Foundation MVP:

- metrics are collected manually;
- `MetricSnapshot` records store performance data;
- manual import helpers exist for metric entry.

Automated analytics collection is a future capability.

Reference: `MVP_SCOPE.md`, Section 7

## 11.4. From Data to Insight

Raw metrics alone are not valuable.

Performance Analysis transforms data into understanding:

```text
Performance Data
    ↓
Comparison to Goals — did we achieve what we aimed for?
    ↓
Pattern Recognition — what patterns emerge across content?
    ↓
Hypothesis Formation — why did certain content perform as it did?
    ↓
Insight Generation — what should we do differently?
```

## 11.5. Inputs and Outputs

```text
Input:     Publication record (from Stage 7)
           MetricSnapshot data
           Goals and KPIs
              ↓
Stage:     Performance Analysis
              ↓
Output:    Performance Data + Insights
              ↓
Next:      Learning Memory → Stage 9
```

---

# 12. Stage 9 — Learning Memory Update

## 12.1. Purpose

Transform performance analysis into persistent operational knowledge
that improves future cycles.

This is the most critical stage in the LOOPRA Content Cycle.

Without Learning Memory, LOOPRA would repeat the same decisions
regardless of outcomes.

With Learning Memory, each cycle becomes smarter than the previous one.

## 12.2. The Learning Process

```text
Analytics Data (from Stage 8)
    ↓
Analysis — what patterns emerge from the results?
    ↓
Abstraction — what general principles can be extracted?
    ↓
Storage — recording in Learning Memory
    ↓
Retrieval — applying knowledge to future cycles
```

## 12.3. What Learning Memory Stores

| Category | Examples |
|---|---|
| Format Effectiveness | "Carousels with 5-7 slides have 40% higher completion" |
| Hook Performance | "Question hooks outperform statement hooks for this audience" |
| Topic Resonance | "Audience engages more with practical tips than theory" |
| Timing Insights | "Weekday morning posts have 2x engagement vs weekend" |
| CTA Behaviour | "Soft CTAs generate more conversions than aggressive CTAs" |
| Audience Responses | "This segment responds negatively to sales language" |
| Format-Audience Fit | "Video works for awareness, carousel works for education" |
| Failed Experiments | "X format did not work because of Y — avoid in future" |

## 12.4. Learning Memory Constraints

Learning Memory operates within critical boundaries:

```text
Learning Memory MUST NOT override Brand Identity.

Brand System:     "We provide professional, trustworthy expertise"
Learning Memory:  "Humorous content gets more engagement"
Decision:         Do NOT switch to humor if it contradicts brand tone.

Learning Memory optimizes WITHIN brand boundaries, not beyond them.
```

## 12.5. Knowledge Categories

Learning Memory organizes knowledge by:

- **Content Pillar** — what works for education vs. storytelling;
- **Audience Segment** — what resonates with each group;
- **Channel** — what performs on Instagram vs. LinkedIn;
- **Format** — effectiveness per content type;
- **Goal** — which patterns serve which business goals;
- **Time Period** — seasonal and temporal patterns.

## 12.6. Inputs and Outputs

```text
Input:     Performance Data + Insights (from Stage 8)
           Past Learning Memory
              ↓
Stage:     Learning Memory Update
              ↓
Output:    LearningMemoryEntry — accumulated operational knowledge
              ↓
Next:      Optimization → Stage 10
```

Reference: `DATA_MODEL.md`, Section 4.6

---

# 13. Stage 10 — Optimization

## 13.1. Purpose

Apply accumulated learning to improve the next content cycle.

## 13.2. What Optimization Changes

Based on Learning Memory, LOOPRA adjusts:

| Area | Example Change |
|---|---|
| Recommendations | "Increase carousel format share based on recent performance" |
| Priorities | "Shift from awareness to engagement goal for this segment" |
| Content Patterns | "Use educational hooks more frequently in this pillar" |
| Experiments | "Test short-form video for the community pillar" |
| Channel Mix | "Increase LinkedIn frequency, reduce X frequency" |
| Timing | "Adjust publishing schedule based on time-of-day performance" |
| Format Selection | "Prefer video for awareness content, carousel for educational" |

## 13.3. Optimization Actions

Each optimization is recorded as an `OptimizationAction`.

Reference: `DATA_MODEL.md`, Section 4.7

Examples:

- "Increase usage of educational carousel format based on previous
  cycle performance."
- "Adjust CTA strategy: move from direct CTA to soft CTA for this
  audience segment."
- "Test video content in the storytelling pillar — carousel performed
  well, video may extend reach."

## 13.4. The Continuous Loop

```text
Optimization
    ↓
Applies to Next Cycle
    ↓
Next Cycle starts with improved context
    ↓
Produces new results
    ↓
New results feed Learning Memory
    ↓
Learning Memory drives further Optimization
    ↓
Cycle after cycle, the system improves.
```

## 13.5. Inputs and Outputs

```text
Input:     LearningMemoryEntry (from Stage 9)
           Brand System context
           Goals
              ↓
Stage:     Optimization
              ↓
Output:    OptimizationAction → applied to Next Cycle
              ↓
Next:      Cycle returns to Stage 1 with improved parameters
```

---

# 14. Autonomy Modes Impact

## 14.1. Overview

The autonomy mode selected for a project determines how much
independent authority the Orchestrator Agent has at each cycle stage.

Three modes exist. The human selects one per project.

Reference: `USER_WORKFLOWS.md`, Section 8

## 14.2. Copilot Mode

**Principle:** LOOPRA suggests, human decides.

Impact on the cycle:

| Stage | Behaviour |
|---|---|
| Signal Discovery | LOOPRA detects and presents signals to the user |
| Trend Understanding | LOOPRA analyzes and recommends patterns |
| Opportunity Creation | LOOPRA proposes opportunities for review |
| Strategic Decision | User makes all decisions; LOOPRA assists |
| Content Creation | LOOPRA generates drafts; user approves each |
| Production | LOOPRA produces; user reviews |
| Distribution | LOOPRA prepares; user manually publishes |
| Performance Analysis | LOOPRA collects data; user interprets |
| Learning Memory | User validates learning entries |
| Optimization | LOOPRA recommends; user decides |

Every action requires human approval.

Current Foundation MVP operates in copilot mode by default.

## 14.3. Assisted Mode

**Principle:** LOOPRA operates with periodic human checkpoints.

Impact on the cycle:

| Stage | Behaviour |
|---|---|
| Signal Discovery | LOOPRA autonomously monitors; presents summaries |
| Trend Understanding | LOOPRA analyzes autonomously |
| Opportunity Creation | LOOPRA creates opportunities; presents for review |
| Strategic Decision | LOOPRA decides routine cases; escalates significant ones |
| Content Creation | LOOPRA creates independently within confidence bounds |
| Production | LOOPRA produces autonomously |
| Distribution | LOOPRA publishes; user reviews at checkpoints |
| Performance Analysis | LOOPRA analyzes; presents insights weekly |
| Learning Memory | LOOPRA updates autonomously; user validates periodically |
| Optimization | LOOPRA optimizes within rules; flags significant changes |

Checkpoint examples:

- after idea selection;
- before final content publication;
- after weekly analytics review.

## 14.4. Autopilot Mode

**Principle:** LOOPRA operates autonomously within defined rules.

Impact on the cycle:

| Stage | Behaviour |
|---|---|
| Signal Discovery | LOOPRA continuously monitors all sources |
| Trend Understanding | LOOPRA autonomously identifies and analyzes |
| Opportunity Creation | LOOPRA creates and selects opportunities |
| Strategic Decision | LOOPRA makes all routine decisions autonomously |
| Content Creation | LOOPRA generates content independently |
| Production | LOOPRA produces independently |
| Distribution | LOOPRA publishes autonomously on schedule |
| Performance Analysis | LOOPRA continuously analyzes performance |
| Learning Memory | LOOPRA continuously updates knowledge |
| Optimization | LOOPRA continuously optimizes the next cycle |

But always with:

- control points;
- operational limits;
- emergency stop;
- periodic review checkpoints.

## 14.5. Emergency Controls Across All Modes

Regardless of autonomy mode, the human always retains:

- **Emergency Stop** — immediately pause all active cycles;
- **Reduce Autonomy** — drop from Autopilot to Assisted or Copilot;
- **Change Rules** — modify restrictions, forbidden topics or goals;
- **Review Decision** — inspect any autonomous decision the system made.

---

# 15. Cycle States

## 15.1. Cycle Lifecycle

A Content Cycle progresses through defined states:

```text
Draft            — cycle created, not yet launched
    ↓
Planning         — LOOPRA is analyzing signals and creating opportunities
    ↓
Deciding         — Orchestrator Agent is evaluating what to create
    ↓
Production       — content is being created and assembled
    ↓
Published        — content has been distributed to target channels
    ↓
Measured         — performance data has been collected
    ↓
Learning Updated — Learning Memory has been updated with new knowledge
    ↓
Optimized        — optimization actions have been applied
    ↓
Completed        — cycle is complete; next cycle may begin
```

## 15.2. State Descriptions

| State | Description |
|---|---|
| Draft | Cycle is configured but has not started executing |
| Planning | Stage 1–3: signal discovery, trend understanding, opportunity creation |
| Deciding | Stage 4: strategic decisions being made |
| Production | Stage 5–6: content creation and production |
| Published | Stage 7: content has been distributed |
| Measured | Stage 8: performance data collected and analyzed |
| Learning Updated | Stage 9: new knowledge stored in Learning Memory |
| Optimized | Stage 10: optimization actions prepared for next cycle |
| Completed | Cycle is finished; next cycle may start with improved context |

## 15.3. Parallel Cycles

Multiple cycles may operate in parallel for different:

- content pillars;
- distribution channels;
- experiments;
- audience segments.

Each cycle maintains its own state independently.

---

# 16. Foundation MVP Relationship

## 16.1. The Critical Distinction

The current Foundation MVP is the reliable execution baseline.

The future LOOPRA Content Cycle is the autonomous marketing operating
model that wraps around and extends it.

## 16.2. Current Foundation MVP Pipeline

```text
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

This pipeline is the validated technical core. It represents the
deterministic content lifecycle.

Reference: `PIPELINES_SPEC.md`, `MVP_SCOPE.md`

## 16.3. Future LOOPRA Content Cycle Relationship

```text
Future LOOPRA Content Cycle:

Market Signals          (Stage 1)
    ↓
Trend Understanding     (Stage 2)     ← Intelligence Layer provides
    ↓                                      the source of Ideas
Content Opportunities   (Stage 3)
    ↓
Strategic Decision      (Stage 4)     ← Orchestrator Agent replaces
    ↓                                      manual Idea creation
Content Creation        (Stage 5)     ← Foundation MVP pipeline
    ↓                                      executes within the cycle
Production              (Stage 6)     ← Idea → Scenario → ContentItem
    ↓
Distribution            (Stage 7)     ← ExportPackage → Publication
    ↓
Performance Analysis    (Stage 8)     ← MetricSnapshot
    ↓
Learning Memory         (Stage 9)     ← New layer: captures learning
    ↓                                      that the current MVP does
Optimization            (Stage 10)    ← not automatically generate
    ↓
Next Cycle                           ← Returns to Stage 1 with
                                         improved context
```

## 16.4. What Changes and What Stays

```text
What stays from Foundation MVP:

    Idea → Scenario → ContentItem → ExportPackage → Publication →
    MetricSnapshot

    These execution primitives remain the production backbone.

What the Intelligence Layer adds:

    Signal discovery, trend understanding, opportunity creation,
    strategic decisions, learning accumulation, cycle optimization.

    These transform the deterministic pipeline into an intelligent
    operating cycle.
```

## 16.5. Evolution Path

```text
Foundation MVP (current)
    Deterministic pipeline
    Manual inputs, manual metrics
    Export-first, local filesystem
    Copilot mode only
        ↓
Content Intelligence (next)
    Automatic signal analysis
    Pattern recognition
    Opportunity generation
        ↓
Production Automation
    Automated production execution
    Quality gates
    Batch content generation
        ↓
Agentic Operations
    Orchestrator Agent active
    Autonomous decision making
    Learning Memory operational
        ↓
Marketing Operating System
    Full autonomous cycles
    Continuous self-improvement
    Multi-channel operation
        ↓
SaaS Platform
    Public availability
    Multi-tenant
    Billing, teams, marketplace
```

Reference: `LOOPRA_ARCHITECTURE.md`, Section 2

---

# 17. Future Design Implications

## 17.1. What CONTENT_CYCLE_SPEC.md Enables

This specification is the functional blueprint for designing:

- **Orchestrator Agent** — understanding which decisions it must make at
  each stage;
- **Intelligence Modules** — understanding what analysis each module
  must provide;
- **Learning Memory** — understanding what knowledge must be stored and
  retrieved;
- **Cycle Management** — understanding how cycles progress through
  states;
- **Autonomy System** — understanding how autonomy modes affect each
  stage.

## 17.2. Future Detailed Specifications

The following specifications will define the implementation details of
each intelligence component:

```text
docs/03_intelligence/
    AGENT_SYSTEM_SPEC.md          — Orchestrator Agent design and decision model
    TREND_INTELLIGENCE_SPEC.md    — Market signal analysis and trend detection
    CONTENT_INTELLIGENCE_SPEC.md  — Pattern recognition and content insight
    LEARNING_MEMORY_SPEC.md       — Long-term memory, knowledge storage, retrieval

docs/04_production/
    CONTENT_TYPES_SPEC.md         — Supported content formats and properties
    PRODUCTION_PIPELINE_SPEC.md   — Content production workflow and quality gates
    CONTENT_OPERATING_SYSTEM_SPEC.md — Autonomous content cycle execution
```

## 17.3. Implementation Prerequisites

No intelligence component should be implemented without:

1. Its approved specification document.
2. Validated Foundation MVP stability.
3. Clear boundaries between Foundation and Intelligence layers.
4. Defined interaction contracts between modules.

---

# 18. Related Documents

## 18.1. Core Architecture

```text
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
```

## 18.2. Foundation Layer

```text
docs/00_foundation/MVP_SCOPE.md                     — Foundation MVP scope
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
```

## 18.3. Product Layer

```text
docs/01_product/LOOPRA_BRAND_POSITIONING.md         — LOOPRA product identity
docs/01_product/USER_WORKFLOWS.md                   — User interaction model
```

## 18.4. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

## 18.5. Future Documents

```text
docs/03_intelligence/AGENT_SYSTEM_SPEC.md            — Orchestrator Agent design
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md      — Trend detection specification
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md    — Content insight specification
docs/03_intelligence/LEARNING_MEMORY_SPEC.md         — Learning Memory specification
docs/04_production/CONTENT_TYPES_SPEC.md             — Content format definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md       — Production workflow specification
docs/04_production/CONTENT_OPERATING_SYSTEM_SPEC.md  — Autonomous cycle execution
```

---

# 19. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Intelligence Layer — Functional Specification |

---

# Final Statement

The LOOPRA Content Cycle is not a content generation pipeline.

It is a continuous autonomous marketing operating cycle that transforms
market signals into content, results and improved future performance.

Each cycle feeds the next. The system compounds knowledge. Marketing
does not restart every day — it continuously improves.

This specification is the functional blueprint for building the
Intelligence Layer that transforms LOOPRA from a deterministic
production tool into a self-learning marketing operating system.

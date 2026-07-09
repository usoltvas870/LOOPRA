# LEARNING MEMORY SPEC

## Version

v1.0

## Status

Active — LOOPRA Intelligence Layer

## Purpose

This document defines the functional architecture of Learning Memory —
the accumulated operational experience layer of the LOOPRA Autonomous
Marketing Operating System.

It answers the central question:

> How does LOOPRA transform every content cycle into accumulated
> experience and use that experience to improve future marketing
> decisions?

LEARNING_MEMORY_SPEC.md is the functional specification for the
mechanism that closes the LOOPRA Growth Loop — turning results into
knowledge, knowledge into better decisions, and better decisions into
improved results.

It describes:

- what knowledge LOOPRA accumulates across cycles;
- how experience is extracted from results;
- how knowledge is organized into actionable memory;
- how memory informs Intelligence Modules and the Orchestrator Agent;
- the boundaries that prevent learning from overriding strategy;
- the relationship between Learning Memory and the Foundation MVP.

It does NOT describe:

- specific database schemas or storage engines;
- vector databases or embedding implementations;
- specific AI models, providers or prompts;
- API contracts or code-level implementation;
- UI components or visualization.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

LEARNING_MEMORY_SPEC.md defines the functional architecture of the
LOOPRA memory system — the persistent knowledge layer that accumulates
marketing experience across cycles.

It serves as the specification for:

- what types of knowledge LOOPRA stores;
- how experience forms from cycle results;
- how results are transformed into actionable knowledge;
- how knowledge is retrieved and applied by Intelligence Modules and
  the Orchestrator Agent;
- what boundaries govern the influence of learning on strategy.

## 1.2. Scope

This document covers:

- the role of Learning Memory in the LOOPRA Content Cycle;
- the four types of memory — Context, Operational, Decision,
  Experimental;
- the learning entity model — how knowledge is structured;
- the learning extraction process — how results become knowledge;
- categories of knowledge LOOPRA accumulates;
- interaction with Intelligence Modules and the Orchestrator Agent;
- the confidence model for knowledge reliability;
- the memory lifecycle from creation to expiration;
- critical boundaries — what Learning Memory cannot change;
- relationship to the current Foundation MVP.

## 1.3. Out of Scope

This document does not cover:

- database design, schema definitions or storage implementation;
- vector databases, embeddings or similarity search implementation;
- specific AI providers, model selection or prompt engineering;
- API contracts between system components;
- UI components for memory visualization or knowledge dashboards;
- Trend Intelligence detection algorithms;
- Content Intelligence recommendation logic;
- Orchestrator Agent decision algorithms.

---

# 2. Role of Learning Memory in LOOPRA

## 2.1. Position in the Content Cycle

Learning Memory operates at Stages 9 and 10 of the LOOPRA Content
Cycle, and also informs Stages 1–4 of the next cycle:

```text
Creation
    ↓
Distribution
    ↓
Analytics
    ↓
Learning Memory (Stage 9)    ← Knowledge formation
    ↓
Optimization (Stage 10)       ← Knowledge application
    ↓
Next Cycle (Stages 1–4)       ← Knowledge-informed decisions
```

Learning Memory is the mechanism that closes the Growth Loop.

Reference: `CONTENT_CYCLE_SPEC.md`, Sections 12 and 13

## 2.2. Position in the System Architecture

Within the LOOPRA system:

```text
Analytics (MetricSnapshot, performance data)
    ↓
Learning Memory
    ↓
    "What works, why it works, and when it works."
    ↓
Orchestrator Agent (informed decisions)
    ↓
Improved Content Cycles
```

Reference: `SYSTEM_ARCHITECTURE.md`, Section 11

## 2.3. What Learning Memory Answers

Learning Memory answers the operational question:

> "What works, why it works, and when it works."

It provides the Orchestrator Agent and Intelligence Modules with:

- what has succeeded in the past;
- what has failed and why;
- which patterns are reliable;
- which assumptions are validated;
- which experiments produced useful knowledge.

## 2.4. What Learning Memory Is Not

Learning Memory is not:

- a simple history log of past actions;
- a database of all system events;
- a replacement for Brand System;
- a decision-making authority;
- a strategy-setting mechanism.

Learning Memory is accumulated operational experience that informs
future execution within strategic boundaries.

---

# 3. Core Principle: Learning From Experience

## 3.1. The Fundamental Difference

A conventional content system operates linearly:

```text
Input → Generation → Output
```

Each cycle starts fresh. The system does not remember what happened
before.

LOOPRA operates cyclically with memory:

```text
Input
    ↓
Decision
    ↓
Action
    ↓
Result
    ↓
Learning (knowledge extracted from result)
    ↓
Improved Decision (applied to next cycle)
```

Each cycle builds on the accumulated experience of all previous cycles.

## 3.2. The Core Value Proposition

The fundamental value of LOOPRA is not content generation.

The fundamental value is:

> Every content cycle makes the next content cycle better.

This compounding improvement is only possible through Learning Memory.

Without Learning Memory, LOOPRA would repeat the same decisions
regardless of outcome. It would be a production tool, not a marketing
operating system.

With Learning Memory, LOOPRA becomes a self-improving system.

## 3.3. Experience, Not Just Data

Learning Memory does not store raw metrics.

It stores extracted experience:

```text
Raw metric:        "Post received 1,200 impressions and 85 saves."
                       ↓  Analytics Intelligence analysis
Extracted experience: "Carousel format generated 2x higher save rate
                       compared to single-image posts for the educational
                       pillar with the professional audience."
                       ↓  Learning Memory storage
Knowledge:          "Educational carousels with practical tips are a
                    reliable format for engagement and saves among
                    professional audiences."
                       ↓  Future application
                    System recommends carousel format when goal is
                    engagement and audience is professional.
```

Raw data is perishable. Extracted knowledge compounds.

---

# 4. Learning Memory Architecture Overview

## 4.1. The Learning Pipeline

```text
Content Cycle Results (MetricSnapshot)
        ↓
Analytics Intelligence (analysis, pattern detection, hypothesis formation)
        ↓
Learning Extraction (transforming analysis into structured knowledge)
        ↓
Knowledge Formation (creating and updating learning entities)
        ↓
Learning Memory (persistent storage of accumulated experience)
        ↓
Future Decisions (retrieval and application by Orchestrator Agent)
```

## 4.2. Core Components

Learning Memory consists of:

- **Knowledge Storage** — persistent storage of learning entities
  organized by category (pillar, audience, channel, format, goal);
- **Pattern Repository** — structured storage of repeatable success
  and failure patterns;
- **Confidence Model** — assessment of knowledge reliability based on
  evidence strength and recency;
- **Retrieval Interface** — mechanisms for the Orchestrator Agent and
  Intelligence Modules to query accumulated knowledge;
- **Lifecycle Management** — processes for creation, validation,
  strengthening, revision and expiration of knowledge.

## 4.3. Knowledge Organization

Learning Memory organizes knowledge by:

- **Content Pillar** — what works for education vs. storytelling vs.
  social proof;
- **Audience Segment** — what resonates with each segment;
- **Channel** — what performs on which platform;
- **Format** — effectiveness per content type;
- **Business Goal** — which patterns serve which goals;
- **Time Period** — seasonal and temporal patterns;
- **Topic and Theme** — which subjects resonate.

This multidimensional organization enables precise retrieval:
instead of "what works," the system retrieves "what works for
audience X on channel Y toward goal Z."

## 4.4. Memory Scope

Learning Memory is project-scoped — each project accumulates its own
experience.

Knowledge from one project is not shared with another project.

This preserves brand-specific learning and prevents pattern
contamination across different brand contexts.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 10.3

---

# 5. Types of Memory

## 5.1. Overview

Learning Memory is organized into four distinct types, each serving a
different purpose in the learning pipeline.

| Memory Type | Question Answered | Lifetime | Primary User |
|---|---|---|---|
| Context Memory | "What is the current situation?" | Duration of active cycle | Orchestrator Agent |
| Operational Memory | "What works in practice?" | Persistent, evolves continuously | Intelligence Modules, Orchestrator Agent |
| Decision Memory | "Why did we choose this action?" | Permanent audit trail | Human Operator, Orchestrator Agent |
| Experimental Memory | "What did we learn from testing?" | Persistent, evolves with new experiments | Content Intelligence, Orchestrator Agent |

These four types form a complete learning system:
Context provides understanding of the present. Operational Memory
provides knowledge of what works. Decision Memory provides rationale
for past choices. Experimental Memory provides validated discoveries.

---

## 5.2. Context Memory

### 5.2.1. Purpose

Context Memory stores the current operational context — everything the
system needs to understand the present situation before making
decisions.

It answers: "What is the current situation?"

### 5.2.2. What It Stores

| Category | Examples |
|---|---|
| Workspace | Active workspace configuration, global settings |
| Project | Project identity, configuration, status |
| Brand System | Identity, audience, communication rules, strategy, restrictions, goals |
| Channels | Enabled channels, channel configurations, constraints |
| Current Content Cycle | Active cycle state, progress, pending actions, queued decisions |
| Active Decisions | Decisions being evaluated, awaiting execution or awaiting approval |

### 5.2.3. Lifetime

Loaded at the start of each content cycle.

Updated continuously as the cycle progresses through stages.

Reloaded at the start of the next cycle with updated knowledge.

### 5.2.4. Primary Users

The Orchestrator Agent loads Context Memory to understand the operating
environment before making any decisions.

Intelligence Modules receive relevant portions of Context Memory as
input to their analysis.

### 5.2.5. Relationship to Other Memory Types

Context Memory is the entry point. It provides the "now" that
Operational Memory enriches with "what works," Decision Memory enriches
with "why we chose before," and Experimental Memory enriches with
"what we discovered."

---

## 5.3. Operational Memory

### 5.3.1. Purpose

Operational Memory stores accumulated knowledge about what works and
what does not work in marketing practice.

It answers: "What works in practice?"

This is the core of Learning Memory — the persistent, evolving
knowledge of marketing effectiveness.

### 5.3.2. What It Stores

Operational Memory stores knowledge in the form of repeatable
patterns, validated by evidence from completed cycles.

| Category | Example Knowledge |
|---|---|
| Format Effectiveness | "Carousels with 5–7 slides have 40% higher save rate than 3-slide carousels for the professional audience." |
| Topic Resonance | "Practical AI application content generates 2x more comments than theoretical AI discussion." |
| Hook Performance | "Question-based hooks generate 3x more engagement than statement hooks for the beginner audience." |
| CTA Behaviour | "Soft CTAs ('Learn more', 'Try this') generate more link clicks than direct CTAs ('Buy now', 'Sign up') for the awareness goal." |
| Audience-Format Fit | "Short video works for awareness and discovery. Carousel works for education and saves. Text works for authority and discussion." |
| Channel Effectiveness | "LinkedIn carousel format generates higher professional engagement. Instagram Reels generate higher discovery reach." |
| Timing Patterns | "Tuesday and Thursday morning posts receive 2x initial reach compared to weekend posts." |
| Goal-Format Mapping | "For awareness: short video > carousel > image > text. For lead generation: carousel > text > short video > image." |
| Successful Combinations | "Educational carousel + professional audience + awareness goal = consistent high performance across 8 cycles." |
| Topic Fatigue | "Audience engagement with topic X has decreased over the last 3 cycles. Topic may be approaching saturation." |

### 5.3.3. Key Examples

**Example — Format-Audience-Goal Combination:**

```text
Performance Pattern:
    "For the entrepreneur audience segment, short educational videos
     under 60 seconds with practical demonstrations consistently
     outperform static educational posts for awareness goals.

     Evidence: 12 cycles over 16 weeks.
     Average engagement delta: +140%.
     Confidence: high."
```

**Example — Audience Behaviour:**

```text
Audience Learning:
    "The professional audience segment saves educational content 3x more
     often than they like or comment. They prefer revisitable, reference-
     style content. CTA effectiveness is highest in the final slide,
     not the caption.

     Evidence: 8 cycles across multiple content pillars.
     Confidence: high."
```

### 5.3.4. Lifetime

Operational Memory is persistent and evolves continuously.

New cycles add evidence. Existing knowledge is strengthened or
weakened based on new results. Knowledge that is consistently
contradicted by new evidence is revised. Patterns that are no longer
relevant are expired.

### 5.3.5. Primary Users

Content Intelligence queries Operational Memory to inform format
recommendations, topic selection and angle choices.

Trend Intelligence queries Operational Memory to calibrate relevance
assessment — past performance data informs the evaluation of new
trends.

The Orchestrator Agent queries Operational Memory before making
strategic decisions — "what does past experience tell us about this
situation?"

---

## 5.4. Decision Memory

### 5.4.1. Purpose

Decision Memory stores records of why the system made each decision
and what resulted from those decisions.

It answers: "Why did the system choose this action?"

### 5.4.2. What It Stores

Each Decision Record captures:

| Field | Description |
|---|---|
| Context | What was the situation when the decision was made? |
| Decision | What action was chosen? |
| Reasoning | Why was this action chosen over alternatives? |
| Alternatives | What other options were considered but not selected? |
| Confidence | How certain was the system about this decision? |
| Expected Outcome | What result was predicted? |
| Actual Result | What actually happened? (filled after cycle completion) |
| Outcome Gap | Difference between expected and actual result |
| Timestamp | When was the decision made? |
| Cycle Reference | Which content cycle does this decision belong to? |

Reference: `DATA_MODEL.md`, Section 4.5 — `AgentDecision`

### 5.4.3. How Decision Memory Enables Learning

Decision Memory enables:

- **Causal Understanding** — connecting decisions to outcomes:
  "We chose format X because of reason Y. The result was Z. The gap
  between expected and actual was W."

- **Pattern Detection in Decisions** — identifying which types of
  decisions consistently produce good outcomes and which do not:
  "Decisions based on trend evidence alone (without Learning Memory
  confirmation) have a 40% lower success rate than decisions that
  combine trend evidence with Learning Memory validation."

- **Confidence Calibration** — comparing predicted confidence against
  actual outcomes to improve the confidence model:
  "The system predicted high confidence in 30 decisions. 24 produced
  the expected outcome. The confidence model is calibrated at 80%
  accuracy."

- **Audit Trail** — the human operator can review why each decision
  was made and what resulted.

### 5.4.4. Example

```text
Decision Record:

    context: "Cycle 14. Trend detected: growing interest in AI
              automation among small business owners. Audience:
              entrepreneurs. Goal: awareness."
    decision: "Create educational carousel demonstrating 3 practical
              AI automation workflows."
    reasoning: "Carousel format has 40% higher save rate for this
                audience. Educational angle aligns with awareness
                goal. Topic directly addresses audience pain point
                identified in Trend Pattern."
    alternatives:
        - "Short video (higher reach potential but less educational
          depth)"
        - "Text post (lower production cost but lower engagement
          for this audience)"
    confidence: high
    expected_outcome: "High save rate. Moderate comment engagement.
                       Low link clicks (awareness stage)."
    actual_result: "1,800 impressions. 95 saves. 12 comments.
                    5 link clicks."
    outcome_gap: "Aligned with expectations. Save rate slightly
                 above projection. Comment rate slightly below."
```

### 5.4.5. Lifetime

Decision Memory is a permanent audit trail.

Decisions are not deleted. They accumulate as the system's operational
history.

Decision Records form the raw material for Operational Memory
extraction — patterns in decisions become patterns in knowledge.

### 5.4.6. Primary Users

The Orchestrator Agent references Decision Memory to evaluate similar
past situations before making new decisions.

The human operator reviews Decision Memory for transparency and
strategic oversight.

Analytics Intelligence mines Decision Memory to identify decision
patterns that correlate with success or failure.

---

## 5.5. Experimental Memory

### 5.5.1. Purpose

Experimental Memory stores the results of controlled content
experiments — systematic tests of hypotheses about what might work.

It answers: "What did we learn from testing?"

### 5.5.2. The Role of Experiments

Not all knowledge comes from routine cycles.

Experiments are deliberate tests of assumptions:

- "Is format X actually better than format Y for this audience?"
- "Does angle A generate more engagement than angle B for this topic?"
- "Will this new content type work for our brand?"

Experiments transform assumptions into verified knowledge.

Reference: `CONTENT_INTELLIGENCE_SPEC.md`, Section 16

### 5.5.3. What Experimental Memory Stores

Each experiment record captures:

| Field | Description |
|---|---|
| Hypothesis | What was the belief being tested? |
| Motivation | Why was this experiment conducted? |
| Conditions | What was the test environment? (audience, channel, timing) |
| Variant A | Description of the control content |
| Variant B | Description of the test content |
| Method | How was the experiment conducted? (A/B test, sequential test) |
| Metrics | What was measured? |
| Result | What actually happened? |
| Conclusion | What does the result mean? |
| Confidence | How reliable is this conclusion? |
| Action | What should change based on this learning? |

Reference: `DATA_MODEL.md`, Section 4.4 — `Experiment`

### 5.5.4. Example

```text
Experiment Record:

    hypothesis: "Short educational videos (60 seconds) will generate
                higher completion rate than longer educational videos
                (3 minutes) for the entrepreneur audience on the
                expertise pillar."
    motivation: "Learning Memory shows video format is effective for
                 this audience, but optimal length is unknown."
    conditions:
        audience: entrepreneurs
        channel: Instagram
        goal: awareness
        pillar: expertise
    variant_a: "12 AI Tools in 3 Minutes" (long-form educational video)
    variant_b: "3 AI Tools in 60 Seconds" (short-form educational video)
    result:
        variant_a: completion_rate: 22%, saves: 14
        variant_b: completion_rate: 68%, saves: 31
    conclusion: "Short-form educational video (60 seconds) significantly
                 outperforms long-form (3 minutes) for this audience on
                 this channel.
                 Completion rate difference: +46 percentage points.
                 Save rate difference: +121%."
    confidence: high
    action: "Default to short-form video (60 seconds) for entrepreneur
            audience on Instagram. Reserve long-form for YouTube or
            LinkedIn where audience expects longer content."
```

### 5.5.5. From Experiment to Operational Knowledge

A confirmed experiment graduates into Operational Memory:

```text
Experiment Hypothesis → Test → Result → Conclusion
    ↓
    If conclusion is confident and clear:
    ↓
New or updated Performance Pattern in Operational Memory
    ↓
Applied to future content recommendations
```

Failed experiments are equally valuable — they prevent the system from
repeating the same test and document what does not work.

### 5.5.6. Lifetime

Experimental Memory is persistent. Experiment records are never
deleted — they form the evidence base for Operational Memory patterns.

When an experiment's conclusion is integrated into Operational Memory,
the experiment record becomes supporting evidence for the pattern.

### 5.5.7. Primary Users

Content Intelligence uses Experimental Memory to validate format
recommendations and identify untested assumptions that should become
experiments.

The Orchestrator Agent uses Experimental Memory to decide when to
launch an experiment vs. execute a known pattern.

---

# 6. Learning Entity Model

## 6.1. Overview

Learning Memory is composed of conceptual entities that structure
accumulated experience into actionable knowledge.

These are functional entities — they describe what knowledge looks like,
not how it is stored in a database.

## 6.2. Learning Record

### 6.2.1. Definition

A **Learning Record** is the atomic unit of experience in LOOPRA.

Each completed content action — whether a routine post, a strategic
campaign or a deliberate experiment — produces a Learning Record that
captures what happened and what it means.

### 6.2.2. Structure

| Field | Description |
|---|---|
| `context` | What was the situation? (audience, channel, goal, pillar, cycle) |
| `action` | What was done? (format, topic, angle, message, CTA) |
| `result` | What happened? (metrics, audience response, goal achievement) |
| `interpretation` | What does the result mean? (success, failure, partial, inconclusive) |
| `confidence` | How reliable is this interpretation? |
| `applicability` | When should this knowledge be applied? (audience, channel, goal, format constraints) |

### 6.2.3. Example

```text
Learning Record:

    context:
        audience: professional_marketers
        channel: linkedin
        goal: engagement
        pillar: expertise
        cycle: 17
    action:
        format: carousel (7 slides)
        topic: "Content Strategy Frameworks for 2026"
        angle: educational
        message: "Three proven frameworks with implementation steps"
        cta: "Save for later reference"
    result:
        impressions: 3,200
        saves: 142
        comments: 28
        shares: 15
        link_clicks: 8
    interpretation: "Educational carousel with practical frameworks
                    generated strong save behaviour. Audience values
                    reference-style content they can revisit. CTA
                    'Save for later' aligned with audience behaviour."
    confidence: high
    applicability:
        audiences: [professional_marketers, content_strategists]
        channels: [linkedin]
        goals: [engagement, authority_building]
        formats: [carousel, educational_carousel]
        pillars: [expertise, education]
```

## 6.3. Performance Pattern

### 6.3.1. Definition

A **Performance Pattern** is a validated, repeatable description of
what produces consistent results under specific conditions.

It is formed when multiple Learning Records show the same outcome for
similar actions in similar contexts.

A single success is an observation. A Performance Pattern is a
confirmed, reusable structure.

### 6.3.2. Structure

| Field | Description |
|---|---|
| `pattern` | Description of the repeatable success structure |
| `audience` | Which audience segments this pattern applies to |
| `goal` | Which business goals this pattern supports |
| `format` | Which content formats this pattern involves |
| `channel` | Which distribution channels this pattern is validated for |
| `pillar` | Which content pillars this pattern belongs to |
| `evidence` | Summary of supporting Learning Records (count, recency, consistency) |
| `confidence` | How reliable is this pattern? |
| `conditions` | Under what conditions does this pattern hold? |
| `exceptions` | When might this pattern not apply? |

### 6.3.3. Example

```text
Performance Pattern:

    pattern: "Educational carousels with practical, step-by-step
              frameworks generate 3x higher save rate than theoretical
              or opinion-based carousels for professional audiences
              on LinkedIn.

              Optimal structure: hook slide → problem slide →
              3–4 solution slides → implementation steps slide →
              summary slide → CTA slide.

              CTA 'Save for later' outperforms 'Comment below' for
              this format on this channel."
    audience: [professional_marketers, content_strategists, business_owners]
    goal: [engagement, authority_building, lead_generation]
    format: [carousel]
    channel: [linkedin]
    pillar: [expertise, education]
    evidence:
        supporting_learning_records: 14
        consistency: "12 of 14 records showed above-average save rate.
                     2 records with theoretical approach showed average
                     save rate."
        recency: "Last confirmed in cycle 22 (current cycle - 1)."
        time_span: "Pattern stable across 18 weeks and 14 cycles."
    confidence: high
    conditions: "Pattern holds for professional audiences. Untested for
                consumer audiences. Pattern holds for educational and
                practical topics. Weaker for opinion and storytelling
                topics."
    exceptions: "Pattern may not apply to awareness-stage audiences who
                are not yet seeking detailed frameworks."
```

### 6.3.4. Pattern Evolution

Performance Patterns are not static.

They evolve as new evidence accumulates:

```text
Initial Observation:
    1–2 similar Learning Records → Low-confidence pattern candidate.

Emerging Pattern:
    3–5 consistent Learning Records → Medium-confidence pattern.

Established Pattern:
    6+ consistent Learning Records over extended period → High-confidence
    pattern.

Mature Pattern:
    12+ consistent Learning Records, stable across multiple cycles,
    confirmed across multiple related contexts → Very-high-confidence
    pattern.
```

## 6.4. Failed Pattern

### 6.4.1. Definition

A **Failed Pattern** documents what does NOT work.

It is as important as a Performance Pattern — preventing the system
from repeating mistakes is as valuable as repeating successes.

### 6.4.2. Why Failed Patterns Are Critical

Most marketing systems optimize for what works but ignore what fails.
This leads to repeated mistakes.

LOOPRA treats failed patterns as first-class knowledge entities
because avoiding failure compounds over time just as pursuing success
does.

### 6.4.3. Structure

| Field | Description |
|---|---|
| `pattern` | Description of what consistently fails |
| `failure_type` | Category of failure (engagement, reach, conversion, retention, brand fit) |
| `likely_cause` | Why this pattern fails (identified through analysis) |
| `audience` | Which audience segments this applies to |
| `goal` | Which goals this pattern fails to serve |
| `format` | Which formats are involved |
| `channel` | Which channels this failure was observed on |
| `evidence` | Number of failed attempts and consistency |
| `confidence` | How certain are we that this is a reliable failure? |
| `recommendation` | What should be used instead? |

### 6.4.4. Example

```text
Failed Pattern:

    pattern: "Long-form text posts (over 1,500 characters) consistently
              underperform on Instagram for the beginner audience segment
              regardless of topic or goal.

              Average engagement: 70% below account average.
              Average reach: 55% below account average.
              Save rate: near zero."
    failure_type: engagement_and_reach
    likely_cause: "Instagram audience for this segment prefers visual
                   and short-form content. Long text posts violate
                   platform consumption patterns for this demographic."
    audience: [beginners, career_changers]
    goal: [awareness, engagement]
    format: [text_post]
    channel: [instagram]
    evidence:
        failed_attempts: 8
        consistency: "8 of 8 long text posts on Instagram underperformed
                     significantly across 12 weeks and multiple topics."
        recovery_attempts: "2 posts with the same topic reformatted as
                           carousels performed at or above average."
    confidence: high
    recommendation: "For Instagram + beginner audience, replace long
                    text posts with carousels or short videos.
                    Use text posts only on LinkedIn and Telegram where
                    this audience expects longer written content."
```

### 6.4.5. Failed Pattern Application

When the Orchestrator Agent or Content Intelligence formulates a
content direction, Learning Memory checks:

```text
Proposed: "Long text post about AI tools for beginners on Instagram."

Learning Memory check:
    → Failed Pattern found: "Long text posts consistently fail for
      beginner audience on Instagram."
    → Recommendation: "Use carousel or short video instead."
    → Confidence in this failure pattern: high.

Orchestrator Action:
    → Adjusts format to carousel.
    → Records the failed pattern check in Decision Record.
    → Avoids a predicted failure.
```

This is the defensive value of Learning Memory — it prevents known
failures before they happen.

## 6.5. Learning Hypothesis

### 6.5.1. Definition

A **Learning Hypothesis** is an unverified belief about what might work.

It represents the boundary between what the system assumes and what
the system knows.

### 6.5.2. Purpose

Not all marketing knowledge is verified through cycles.

Hypotheses capture assumptions that need to be tested:

- "We believe format X will outperform format Y for audience Z."
- "We believe angle A will generate more engagement than angle B."
- "We believe channel C is more effective than channel D for goal W."

Hypotheses that are tested become experimental knowledge.

Hypotheses that are confirmed graduate into Operational Memory.

Hypotheses that are disproven become Failed Patterns.

### 6.5.3. Structure

| Field | Description |
|---|---|
| `hypothesis` | The belief being proposed |
| `status` | untested, testing, confirmed, disproven |
| `proposed_by` | Source (Orchestrator Agent, Content Intelligence, Human Operator) |
| `proposed_date` | When the hypothesis was formed |
| `test_design` | How the hypothesis would be tested |
| `test_result` | What happened when tested |
| `conclusion` | What the test means |

### 6.5.4. Hypothesis Lifecycle

```text
untested → testing → confirmed   → Performance Pattern in Operational Memory
                    → disproven  → Failed Pattern or archived knowledge
```

---

# 7. Learning Extraction Process

## 7.1. Overview

Learning Extraction is the process that transforms raw performance
results into structured knowledge.

It is the bridge between "what happened" and "what it means."

## 7.2. The Extraction Pipeline

```text
MetricSnapshot
    (raw performance data from a completed content action)
        ↓
Analytics Intelligence
    (analysis of results: what happened, comparison to goals and
     expectations, identification of patterns and anomalies)
        ↓
Pattern Detection
    (correlation of the current result with past similar results:
     does this confirm, contradict or extend existing knowledge?)
        ↓
Knowledge Interpretation
    (formation of meaning: what does this result tell us about what
     works, for whom, under what conditions?)
        ↓
Learning Record Formation
    (structured capture of the experience: context, action, result,
     interpretation, confidence, applicability)
        ↓
Memory Update
    (integration into Learning Memory:
     - new Learning Record stored
     - Performance Patterns updated (strengthened, weakened or created)
     - Failed Patterns updated
     - Confidence scores recalculated
     - Knowledge organized into retrieval categories)
```

## 7.3. From Single Result to Generalized Knowledge

A single Learning Record is a data point.

Knowledge emerges when multiple Learning Records form a pattern:

```text
Learning Record 1:   Carousel + professional audience + education
                     → high save rate.
Learning Record 2:   Carousel + professional audience + education
                     → high save rate.
Learning Record 3:   Carousel + professional audience + education
                     → high save rate.
...
Learning Record 12:  Carousel + professional audience + education
                     → high save rate.

Pattern Detection identifies the common thread:
    "Educational carousels for professional audiences consistently
     produce above-average save rates."

Knowledge Formation generalizes:
    Performance Pattern:
        "Educational carousel format is optimal for engagement and
         saves when targeting professional audiences with educational
         content."

Confidence increases with each confirming record.
```

## 7.4. What Triggers Learning Extraction

Learning extraction is triggered by:

- **Cycle Completion** — when a content cycle reaches the Measured
  state and performance data is available;
- **Manual Input** — when a human operator provides feedback or
  analysis;
- **Anomaly Detection** — when performance significantly deviates from
  expectations, triggering deeper analysis;
- **Experiment Completion** — when a controlled experiment produces
  comparative results.

## 7.5. Learning Extraction Rules

Not every result produces knowledge.

Learning extraction follows rules:

- **Single occurrence** → creates a Learning Record but does not form
  a Performance Pattern. Too early to generalize.

- **2–3 similar occurrences** → candidate for pattern. Low confidence.
  Flagged for monitoring.

- **4–6 similar occurrences** → emerging pattern. Medium confidence.
  Used for recommendations with caution.

- **7+ similar occurrences with consistency over time** → established
  pattern. High confidence. Used as primary input for content
  recommendations.

- **Contradictory result** → challenges existing pattern. Confidence
  reduced. Pattern may be revised, narrowed with conditions or
  eventually expired.

## 7.6. Analytics Intelligence Role

Learning Extraction depends on Analytics Intelligence.

Analytics Intelligence provides:

- **Result Analysis** — what happened: reach, engagement, retention,
  conversion, compared to goals and expectations;
- **Root Cause Analysis** — why it happened: format, topic, angle,
  timing, audience, channel, external factors;
- **Pattern Correlation** — how this result relates to past results:
  consistent with established patterns, contradictory or novel;
- **Hypothesis Formation** — if the result is unexpected: why might
  this have happened? What should be tested?

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.5

Learning Extraction consumes Analytics Intelligence outputs and
transforms them into persistent memory.

---

# 8. What LOOPRA Learns

## 8.1. Overview

LOOPRA accumulates knowledge across multiple dimensions of marketing
effectiveness.

Each dimension forms a category of knowledge that can be queried and
applied independently or in combination.

## 8.2. Audience Learning

### 8.2.1. What Is Learned

Knowledge about how the audience behaves, what it values and how it
responds.

| Knowledge Category | Example |
|---|---|
| Content Preferences | "The professional audience engages more with practical examples than theoretical explanations." |
| Consumption Patterns | "The beginner audience prefers short-form video for discovery and carousel for detailed learning." |
| Pain Point Resonance | "Content about time management triggers 2x more saves than content about cost management." |
| Attention Span | "The entrepreneur audience completes videos under 60 seconds at 3x the rate of videos over 2 minutes." |
| Engagement Behaviour | "This audience saves educational content but comments on opinion content. Likes are evenly distributed." |
| CTA Responsiveness | "The professional audience responds to soft CTAs ('Learn more', 'Save for later'). Direct CTAs ('Buy now') decrease engagement." |
| Topic Interests | "AI tools, automation and productivity are top-interest topics. General business advice shows declining engagement." |
| Platform Behaviour | "This audience is migrating from X to LinkedIn and Threads for professional content consumption." |

### 8.2.2. How Audience Learning Is Applied

Audience Learning informs:

- Content Intelligence audience targeting;
- format recommendations per audience segment;
- angle selection based on audience awareness level;
- CTA strategy per audience segment;
- channel selection based on audience presence.

## 8.3. Content Learning

### 8.3.1. What Is Learned

Knowledge about what content structures, approaches and messages
produce results.

| Knowledge Category | Example |
|---|---|
| Format Effectiveness | "Carousel format generates highest save rate. Short video generates highest reach. Text posts generate most comments." |
| Structure Patterns | "Content with a clear structure (hook → problem → solution → evidence → CTA) outperforms unstructured content by 60% in completion rate." |
| Hook Effectiveness | "Question hooks generate 3x more engagement than statement hooks. Statistic hooks generate highest save rate." |
| Narrative Approaches | "Storytelling angle with personal experience generates more comments. Educational angle generates more saves." |
| Message Framing | "Value-first messaging ('How to achieve X') outperforms feature-first messaging ('We offer Y') for awareness goals." |
| Visual Patterns | "Carousels with text overlays on branded backgrounds generate higher completion than image-only slides." |
| Optimal Length | "Text posts between 800–1,200 characters generate highest engagement for this audience on LinkedIn." |
| Topic Depth | "Step-by-step practical content outperforms overview content. Audience wants actionable, not aspirational." |

### 8.3.2. How Content Learning Is Applied

Content Learning informs:

- Content Intelligence format and structure recommendations;
- content creation parameters (length, structure, hook type);
- angle selection per goal and audience;
- message framing per goal;
- production quality guidelines.

## 8.4. Channel Learning

### 8.4.1. What Is Learned

Knowledge about which platforms are effective for what purpose with
which content.

| Knowledge Category | Example |
|---|---|
| Platform Effectiveness | "LinkedIn is most effective for professional authority building. Instagram is most effective for brand discovery." |
| Content-Platform Fit | "Educational carousels perform best on LinkedIn. Short educational videos perform best on Instagram. Text posts perform best on Telegram." |
| Audience Presence | "80% of the professional audience segment is active on LinkedIn. 40% is active on Instagram. 15% is active on X." |
| Channel Reach Patterns | "Instagram generates highest initial reach. LinkedIn generates highest sustained engagement over 7 days." |
| Format-Channel Compatibility | "Video works across all channels. Carousel is strong on LinkedIn and Instagram. Text is strong on LinkedIn and Telegram." |
| Channel Goal Alignment | "LinkedIn → authority and lead generation. Instagram → awareness and community. Telegram → retention and deep engagement." |

### 8.4.2. How Channel Learning Is Applied

Channel Learning informs:

- channel selection per content opportunity;
- cross-channel content adaptation strategies;
- channel investment prioritization;
- format-to-channel mapping.

## 8.5. Timing Learning

### 8.5.1. What Is Learned

Knowledge about when content performs best.

| Knowledge Category | Example |
|---|---|
| Day-of-Week Patterns | "Tuesday and Thursday posts generate highest initial reach. Monday posts generate lowest." |
| Time-of-Day Patterns | "Morning posts (8–10 AM) generate highest engagement from the professional audience. Evening posts generate highest from the beginner audience." |
| Publishing Frequency | "3 posts per week on LinkedIn maintains engagement without fatigue. 5+ posts per week shows diminishing returns." |
| Content Sequencing | "Educational content followed by engagement content (discussion, question) generates 40% higher engagement on the second post." |
| Seasonal Patterns | "Educational content demand increases in January and September. Engagement content demand is stable year-round." |
| Platform-Specific Timing | "LinkedIn: Tuesday–Thursday mornings. Instagram: Tuesday–Friday evenings. Telegram: any day, evening." |

### 8.5.2. How Timing Learning Is Applied

Timing Learning informs:

- publishing schedule recommendations;
- cycle timing and cadence;
- content sequencing within cycles;
- seasonal content planning.

## 8.6. Goal Learning

### 8.6.1. What Is Learned

Knowledge about which content types, formats and approaches best
serve each business goal.

| Knowledge Category | Example |
|---|---|
| Awareness Content | "Short video and carousel are most effective for reaching new audiences. Educational and entertaining angles generate highest discovery." |
| Engagement Content | "Question-based text posts and storytelling carousels generate highest comment and share rates. Opinion angles spark discussion." |
| Lead Generation Content | "Educational carousels with practical frameworks generate highest link clicks. Problem/solution angles create urgency. Soft CTAs outperform hard CTAs." |
| Sales Content | "Case study format with data-driven proof generates highest conversion. Comparison angles aid decision-making. Social proof increases trust." |
| Retention Content | "Behind-the-scenes and community content generates highest loyalty signals. Advanced educational content keeps existing audience engaged." |
| Authority Content | "Original research, data-backed insights and opinion pieces generate highest perception of expertise. Depth over breadth." |

### 8.6.2. How Goal Learning Is Applied

Goal Learning informs:

- goal-based content selection;
- format-to-goal mapping;
- angle-to-goal mapping;
- CTA strategy per goal;
- success metric definition per goal.

---

# 9. Learning Memory and Intelligence Modules

## 9.1. Overview

Learning Memory is not an isolated component.

It interacts with all three Intelligence Modules — providing them with
accumulated experience and receiving new knowledge from their
analysis.

## 9.2. Interaction Model

```text
                    Learning Memory
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ↓             ↓             ↓
    Trend             Content         Analytics
  Intelligence      Intelligence    Intelligence
            │             │             │
            └─────────────┼─────────────┘
                          │
                          ↓
                   Orchestrator Agent
```

Intelligence Modules query Learning Memory. Learning Memory does not
query Intelligence Modules.

Intelligence Modules produce new knowledge that is written into
Learning Memory through the Learning Extraction process.

## 9.3. Trend Intelligence and Learning Memory

### 9.3.1. How Trend Intelligence Uses Learning Memory

Trend Intelligence queries Learning Memory to:

- **Strengthen Evidence** — when a detected trend aligns with past
  performance data, confidence in the trend's relevance increases:
  ```text
  External Trend: "Short educational videos gaining engagement."
  Learning Memory: "Short videos performed 2.5x better than static
                    posts for this audience in the last 6 cycles."
  Result: Higher confidence. The trend is validated by internal
          experience, not just external observation.
  ```

- **Recognize Patterns** — classify new signals against established
  knowledge:
  ```text
  New Signal: "Carousel format engagement is increasing."
  Learning Memory: "Carousel format has been the top-performing
                    educational format for 14 cycles."
  Result: Signal is recognized as reinforcement of an established
          pattern, not a new discovery.
  ```

- **Calibrate Relevance** — adjust trend relevance scoring based on
  past experience with similar trends:
  ```text
  Trend: "Topic X is gaining attention."
  Learning Memory: "Content about Topic X performed well in cycle 8
                    but poorly in cycle 15. The difference was the
                    angle, not the topic."
  Result: Relevance scoring accounts for nuance — the topic is relevant
          but angle selection within it is critical.
  ```

- **Identify Warnings** — flag trends that resemble past failures:
  ```text
  Trend: "Format Y is popular among competitors."
  Learning Memory: "Format Y was tested in cycle 10 and failed for
                    this audience."
  Result: Trend flagged with warning. Orchestrator alerted to past
          failure before deciding to pursue.
  ```

### 9.3.2. What Trend Intelligence Writes to Learning Memory

After the Orchestrator acts on a trend and performance data is
collected, the outcome feeds back into Learning Memory:

```text
Trend Prediction: "Format X will resonate with audience Y."
    ↓
Content Created based on this prediction.
    ↓
Result analyzed.
    ↓
Learning Memory updated:
    - Trend prediction accuracy recorded.
    - If prediction was correct → evidence for future similar trends
      strengthened.
    - If prediction was incorrect → understanding of why it was wrong
      stored. Future similar trends evaluated with caution.
```

Reference: `TREND_INTELLIGENCE_SPEC.md`, Section 12

## 9.4. Content Intelligence and Learning Memory

### 9.4.1. How Content Intelligence Uses Learning Memory

Content Intelligence is the primary consumer of Operational Memory.

It queries Learning Memory to:

- **Select Formats** — which format has the highest probability of
  success for this audience, goal and topic:
  ```text
  Question: "Which format should we recommend for educational content
            targeting professional audience with engagement goal?"
  Learning Memory: "Educational carousel format has 40% higher save
                    rate than text posts for this audience-goal
                    combination. Confidence: high."
  Content Intelligence: Recommends carousel as primary format.
  ```

- **Choose Angles** — which angle generates the desired response:
  ```text
  Question: "Which angle works best for awareness + beginner audience?"
  Learning Memory: "Educational angle generates highest reach and saves
                    for beginners. Storytelling angle generates highest
                    comments. Opinion angle underperforms for beginners."
  Content Intelligence: Recommends educational angle for awareness goal.
  ```

- **Select Topics** — which topics within a trend have the highest
  resonance:
  ```text
  Question: "Within the AI trend, which subtopics resonate with the
            entrepreneur audience?"
  Learning Memory: "Practical AI tool demonstrations consistently
                    outperform abstract AI discussion. Productivity
                    use cases generate more saves than creative use cases."
  Content Intelligence: Prioritizes practical demonstrations of
                        productivity AI tools.
  ```

- **Form Confidence Scores** — how confident should we be in this
  recommendation:
  ```text
  Content Opportunity: "Educational video about AI tools."
  Learning Memory query: Has this format + topic + audience + goal
                         combination worked before?
  
  Result: 12 supporting records, 2 neutral, 0 contradictory → high
          confidence.
  
  Alternatively: 1 supporting record, no pattern established → low
                confidence.
  ```

- **Avoid Failed Approaches** — check if the proposed direction
  resembles a known failure:
  ```text
  Proposed: "Text post about AI tools for beginners on Instagram."
  Learning Memory: "Failed Pattern — long text posts consistently
                    fail for beginners on Instagram. Confidence: high."
  Content Intelligence: Adjusts recommendation to carousel or short
                        video. Records the failed pattern avoidance.
  ```

### 9.4.2. What Content Intelligence Writes to Learning Memory

Content Intelligence contributes to Learning Memory through its
recommendation outcomes:

- when a Content Opportunity is pursued and succeeds → evidence for
  similar future opportunities strengthened;
- when a Content Opportunity is pursued and fails → understanding of
  why it failed stored, future similar opportunities flagged;
- when a Content Opportunity is declined → the reason for declination
  is recorded.

The gap between Content Intelligence's prediction (confidence, expected
outcome) and actual result is a learning signal that calibrates future
recommendations.

Reference: `CONTENT_INTELLIGENCE_SPEC.md`, Section 13

## 9.5. Analytics Intelligence and Learning Memory

### 9.5.1. The Creator-Consumer Relationship

Analytics Intelligence has a bidirectional relationship with Learning
Memory:

- **Creator role** — Analytics Intelligence analyzes results and
  produces insights that become new Learning Records;
- **Consumer role** — Analytics Intelligence queries Learning Memory
  to contextualize current results against past performance.

### 9.5.2. Analytics Intelligence as Knowledge Creator

Analytics Intelligence drives the Learning Extraction process:

```text
MetricSnapshot → Analytics Intelligence → Learning Records → Learning Memory
```

It transforms raw performance data into structured knowledge:

- identifying which results confirm established patterns;
- detecting which results contradict expectations;
- discovering new patterns not previously recognized;
- forming hypotheses about anomalous results.

### 9.5.3. Analytics Intelligence as Knowledge Consumer

Analytics Intelligence queries Learning Memory to:

- compare current results against historical baselines;
- identify whether a result is within expected range or anomalous;
- find past similar situations to aid root cause analysis;
- retrieve past hypotheses that may explain current outcomes.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.5

---

# 10. Learning Memory and Orchestrator Agent

## 10.1. The Decision-Informing Role

Learning Memory does not make decisions.

The Orchestrator Agent makes decisions.

Learning Memory provides the accumulated experience that makes those
decisions informed rather than arbitrary.

## 10.2. How the Orchestrator Uses Learning Memory

The Orchestrator Agent queries Learning Memory to:

### 10.2.1. Increase Decision Confidence

Without Learning Memory:

```text
Orchestrator: "Should we create a video?"
Answer: Uncertain. No basis for prediction.
Confidence: Low.
```

With Learning Memory:

```text
Orchestrator queries Learning Memory:
    "Has video format worked for this audience, goal and topic?"
Learning Memory:
    "Video format has produced +40% engagement compared to static
     posts for the professional audience on awareness goals across
     the last 12 cycles. Confidence in this pattern: high."
Orchestrator: "Create a video. The decision is supported by strong,
              consistent evidence."
Confidence: High.
```

### 10.2.2. Select Between Alternatives

When multiple content directions are possible, Learning Memory provides
comparative evidence:

```text
Orchestrator evaluates two Content Opportunities:

Opportunity A: "Carousel about AI tools for professional audience."
    Learning Memory: "12 positive records. High confidence."

Opportunity B: "Video about AI tools for professional audience."
    Learning Memory: "4 positive records. Medium confidence.
                    Untested for this specific subtopic."

Orchestrator selects A with higher confidence, or selects B as an
experiment with controlled scope.
```

### 10.2.3. Assess Risk

Learning Memory provides risk signals:

```text
Orchestrator considers: "Provocative opinion post about industry trends."

Learning Memory query:
    - "Has opinion angle worked for this audience?"
      → Yes, but only with data-backed opinions. Pure opinion without
        evidence underperformed in 3 of 4 attempts.
    - "Are there any warnings about this approach?"
      → One past opinion post generated negative comments. Audience
        prefers constructive, solution-oriented content.

Risk Assessment: Medium risk. If format is adjusted to data-backed
opinion with constructive framing, risk decreases to low.
```

### 10.2.4. Decide Whether to Experiment

Learning Memory identifies knowledge gaps that experiments can fill:

```text
Orchestrator: "We have no data on how this audience responds to
              storytelling video format."

Learning Memory:
    - Performance Pattern exists for educational video with this
      audience. High confidence.
    - Performance Pattern exists for storytelling carousel with this
      audience. Medium confidence.
    - No data exists for storytelling video with this audience.

Orchestrator Decision: "Launch an experiment. Produce one storytelling
                       video. Compare results against educational video
                       baseline. Fill the knowledge gap."
```

### 10.2.5. Escalate Appropriately

When Learning Memory provides insufficient or contradictory evidence,
the Orchestrator escalates to the human operator:

```text
Orchestrator: "Should we pursue this opportunity?"
Learning Memory:
    - 2 positive records from 6 months ago. Recent data is absent.
    - Audience may have shifted since those records were created.
    - Confidence: low.

Orchestrator: "Escalate to human. The system lacks sufficient recent
              evidence to make this decision confidently."
```

## 10.3. The Decision Record Loop

Every Orchestrator decision produces a Decision Record that feeds
back into Learning Memory:

```text
Orchestrator queries Learning Memory
    ↓
Orchestrator makes decision (informed by memory)
    ↓
Action executed
    ↓
Result obtained
    ↓
Decision Record created (context + decision + reasoning + expected outcome)
    ↓
Decision Record updated with actual outcome
    ↓
Learning Record extracted from Decision Record + result
    ↓
Learning Memory updated
    ↓
Next Orchestrator decision benefits from this new knowledge
```

## 10.4. Autonomy Mode and Memory Access

The Orchestrator's autonomy mode affects how it uses Learning Memory:

```text
Copilot mode:
    Orchestrator queries Learning Memory.
    Presents findings to human with recommendation.
    Human decides.
    → Learning Memory informs, but does not execute.

Assisted mode:
    Orchestrator queries Learning Memory.
    Makes routine decisions autonomously when confidence is high and
    pattern evidence is strong.
    Escalates when evidence is weak.
    → Learning Memory enables autonomous routine decisions.

Autopilot mode:
    Orchestrator queries Learning Memory.
    Makes autonomous decisions within confidence boundaries.
    Human monitors through control points.
    → Learning Memory is the primary decision support system.
```

Reference: `AGENT_SYSTEM_SPEC.md`, Section 8

---

# 11. Confidence and Knowledge Reliability

## 11.1. Not All Knowledge Is Equal

Learning Memory must distinguish between reliable knowledge and
uncertain observations.

Confidence is the measure of how much the system should trust a
particular piece of knowledge.

## 11.2. Confidence Factors

Confidence in stored knowledge depends on:

### 11.2.1. Evidence Quantity

How many Learning Records support this knowledge?

```text
1 supporting record     →  very low confidence
2–3 supporting records  →  low confidence
4–6 supporting records  →  medium confidence
7–12 supporting records →  high confidence
13+ supporting records  →  very high confidence
```

### 11.2.2. Evidence Recency

When was the most recent supporting evidence?

```text
Last confirmed in the current or previous cycle   →  recency: high
Last confirmed 3–5 cycles ago                     →  recency: medium
Last confirmed 6+ cycles ago                      →  recency: low
                                                      (may be stale)
```

### 11.2.3. Evidence Consistency

How consistently does the evidence support the pattern?

```text
90–100% of records support the pattern    →  consistency: high
70–89% of records support the pattern     →  consistency: medium
50–69% of records support the pattern     →  consistency: low
                                              (pattern may not be reliable)
Below 50%                                 →  pattern is not established;
                                              knowledge is unreliable
```

### 11.2.4. Evidence Quality

How reliable is the data underlying the knowledge?

```text
Data collected from automated analytics   →  quality: high
Data collected from manual input          →  quality: medium (human error possible)
Data from a single, unverified source     →  quality: low
```

### 11.2.5. Contradictory Evidence

Is there evidence that contradicts this knowledge?

```text
No contradictory records                  →  confidence preserved
1–2 contradictory records                 →  confidence slightly reduced
3+ contradictory records                  →  confidence significantly reduced;
                                              knowledge may need revision
Contradictory records outweigh supporting  →  knowledge is unreliable;
                                              pattern should be revised or
                                              expired
```

## 11.3. Confidence Levels

| Confidence | Meaning | Implication for Use |
|---|---|---|
| Very High | Supported by extensive, consistent, recent evidence with no contradictions | Primary decision input. Act with high autonomy. |
| High | Supported by substantial, consistent evidence | Strong decision input. Minimal caution needed. |
| Medium | Supported by moderate evidence or evidence with minor inconsistencies | Use with caution. Consider as one of several inputs. |
| Low | Supported by limited evidence or evidence with significant age | Use as a suggestion, not a basis for major decisions. Flag for more data collection. |
| Very Low | Supported by minimal or largely contradicted evidence | Do not use for decisions. Knowledge is informational only. Needs significant additional evidence. |

## 11.4. Confidence Example

```text
Performance Pattern: "Educational carousels outperform text posts
                      for professional audiences."

Evidence:
    Quantity:    14 supporting Learning Records
    Recency:     Last confirmed in cycle 22 (most recent cycle)
    Consistency: 13 of 14 records show above-average performance.
                 1 record showed average (not below-average).
    Quality:     All 14 records from automated analytics collection.
    Contradictions: None.

Confidence: Very High.

Orchestrator can rely on this pattern as a primary decision input.
```

```text
Performance Pattern: "Video format may be effective for the beginner
                      audience on the community pillar."

Evidence:
    Quantity:    2 supporting Learning Records
    Recency:     Last confirmed in cycle 15 (7 cycles ago)
    Consistency: 2 of 2 records showed above-average performance.
    Quality:     Both records from manual analytics input.
    Contradictions: None (but insufficient data).

Confidence: Very Low.

Orchestrator should not rely on this. The knowledge gap should be
flagged for an experiment.
```

## 11.5. Confidence Over Time

Confidence is not static.

It evolves with new evidence:

- **Strengthening** — each new confirming Learning Record increases
  confidence.
- **Weakening** — each new contradictory record decreases confidence.
- **Decay** — knowledge that is not reconfirmed for an extended period
  loses confidence. Yesterday's successful pattern may not hold today.
- **Revision** — when confidence drops below a threshold, the knowledge
  is flagged for revision — the pattern's conditions may need narrowing
  or the pattern may need to be expired.

---

# 12. Memory Lifecycle

## 12.1. Overview

Knowledge in Learning Memory is not permanent.

It passes through a defined lifecycle from creation to potential
expiration.

## 12.2. Lifecycle Stages

```text
Creation
    ↓
Validation
    ↓
Strengthening
    ↓
Active Usage
    ↓
Revision (if evidence weakens)
    ↓
Expiration (if evidence is consistently contradicted or knowledge
           becomes irrelevant)
```

## 12.3. Stage Descriptions

### Creation

A new knowledge entity is created when:

- a Learning Record is extracted from a completed cycle;
- a Performance Pattern is detected from multiple Learning Records;
- a Failed Pattern is identified from repeated failures;
- an Experiment produces a conclusion;
- a Learning Hypothesis is formulated.

At creation, confidence is typically low — the knowledge has not yet
been validated by repeated evidence.

### Validation

Knowledge is validated when:

- additional cycles produce confirming evidence;
- the pattern holds across different topics within the same category;
- the pattern holds across different time periods;
- the pattern is confirmed by Analytics Intelligence analysis.

Validation moves knowledge from low confidence to medium confidence.

### Strengthening

Knowledge is strengthened when:

- multiple additional cycles consistently confirm the pattern;
- the pattern holds across a wide range of conditions;
- the pattern is used successfully by the Orchestrator Agent;
- the pattern demonstrates predictive power — content created based on
  it achieves expected outcomes.

Strengthening moves knowledge from medium confidence to high or very
high confidence.

### Active Usage

Knowledge in active usage is:

- regularly queried by Intelligence Modules;
- used by the Orchestrator Agent as decision input;
- applied to content recommendations;
- referenced in decision records.

Active knowledge is the operational backbone of LOOPRA decision-making.

### Revision

Knowledge is revised when:

- contradictory evidence begins to appear;
- the pattern's effectiveness declines over multiple cycles;
- the pattern no longer holds for certain conditions (audience,
  channel, topic);
- the pattern's conditions need narrowing (e.g., "this pattern works
  for audience X but not audience Y").

Revision may involve:

- narrowing conditions (specifying when the pattern applies and when
  it does not);
- lowering confidence (reflecting reduced reliability);
- merging with related patterns (identifying a broader principle);
- splitting into separate patterns (identifying distinct conditions).

### Expiration

Knowledge is expired when:

- contradictory evidence consistently outweighs supporting evidence;
- the pattern has not been confirmed for an extended period and
  conditions have changed;
- the audience, platform or market has shifted so significantly that
  past patterns are no longer relevant;
- the pattern was based on a temporary condition that no longer exists.

Expired knowledge is not deleted. It is archived with an expiration
reason and remains available for historical reference.

Expired knowledge may be reactivated if conditions change and new
evidence supports it.

## 12.4. Lifecycle Triggers

| Trigger | Action |
|---|---|
| New confirming Learning Record | Strengthen confidence. Extend evidence base. |
| New contradictory Learning Record | Reduce confidence. Flag for revision if pattern weakens. |
| Extended period without reconfirmation | Begin confidence decay. Flag for monitoring. |
| Significant market or platform change | Review all knowledge related to the affected area. |
| Orchestrator or human feedback | Immediate revision — human feedback overrides automated confidence. |
| Experiment disproves a hypothesis | Move hypothesis to disproven. If the hypothesis was the basis for a pattern, revise the pattern. |

## 12.5. Knowledge Maintenance

Learning Memory is not a write-once, read-forever store.

It requires active maintenance:

- **Periodic Review** — patterns should be reviewed for continued
  relevance;
- **Confidence Recalculation** — confidence scores should be
  recalculated as new evidence arrives and old evidence ages;
- **Inconsistency Detection** — when two patterns contradict each
  other, the contradiction must be flagged and resolved;
- **Redundancy Detection** — when multiple patterns describe
  essentially the same knowledge, they should be merged.

---

# 13. Learning Does Not Override Strategy

## 13.1. The Critical Boundary

Learning Memory accumulates what works.

But "what works" is not the only consideration in marketing.

Brand strategy imposes constraints that learning cannot override.

## 13.2. What Learning Memory Cannot Change

Learning Memory CANNOT:

### 13.2.1. Change Brand Identity

```text
Brand Identity: "We communicate with professional, trustworthy expertise."

Learning Memory: "Humorous, casual content generates 3x more engagement
                 for competitor brands."

Decision: Humorous content is NOT recommended. It contradicts the brand's
          identity. The engagement gain does not justify the brand
          positioning loss.

Learning Memory optimizes WITHIN the brand identity, not beyond it.
```

### 13.2.2. Change Brand Values

```text
Brand Values: "Transparency and honesty."

Learning Memory: "Clickbait hooks increase initial reach by 40%."

Decision: Clickbait hooks are NOT used. They violate the brand's
          commitment to transparency regardless of reach gains.
```

### 13.2.3. Violate Restrictions

```text
Brand Restriction: "Do not make income claims."

Learning Memory: "Posts with specific income figures generate high
                 engagement."

Decision: Content with income claims is BLOCKED regardless of potential
          engagement. Restrictions are absolute.
```

### 13.2.4. Change Business Goals

```text
Active Goal: "Lead generation for the B2B service."

Learning Memory: "Entertainment content generates the highest reach
                 and follower growth."

Decision: Entertainment content is deprioritized. It serves follower
          growth, not lead generation. Goals determine what content
          is created. Learning determines how effectively it is created.
```

### 13.2.5. Select Strategy Instead of the Human

```text
Learning Memory: "Short-form video is the highest-performing format
                 across all metrics."

Human Strategy: "We are investing in long-form thought leadership to
                differentiate from competitors who all use short video."

Decision: The system respects the human's strategic choice. It optimizes
          long-form content creation based on what works within that
          format — not by recommending a strategy change.
```

## 13.3. The Relationship: Strategy Sets Boundaries, Learning Optimizes Within Them

```text
Strategy Layer (Human + Brand System):
    "We create professional, trustworthy, educational content for
     business owners. We prioritize lead generation over reach."
        ↓
    This sets the boundaries within which learning operates.
        ↓
Learning Memory:
    "Within these boundaries, educational carousels with step-by-step
     frameworks generate the most leads. Question-based hooks in the
     first slide increase completion. Soft CTAs outperform direct CTAs."
        ↓
    This optimizes execution within the strategic boundaries.
        ↓
Content Created:
    Educational carousel with step-by-step framework, question hook,
    soft CTA — aligned with strategy, optimized by learning.
```

## 13.4. The Brand System — Learning Memory Separation

```text
Brand System:      "Who we are"
                       ↓
                   Stable identity
                   Values, tone, restrictions, goals
                   Changed only by human strategic decision
                       ↓
                   Guides all decisions
                       ↓
Learning Memory:   "What works"
                       ↓
                   Evolving operational knowledge
                   Patterns, evidence, experiments
                   Continuously updated from cycle results
                       ↓
                   Refines execution WITHIN brand boundaries
                       ↓
                   Improved next cycle
```

Reference: `SYSTEM_ARCHITECTURE.md`, Section 11
Reference: `BRAND_SYSTEM_SPEC.md`
Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.6

## 13.5. The Provocative Content Example

The clearest illustration of this boundary:

```text
Scenario:
    A brand with a professional, trustworthy, educational identity
    published one provocative, controversial post as a test.

    Result: 5x normal engagement. 10x normal reach. Viral sharing.

Learning Memory analysis:
    "Provocative, polarizing content generates massive engagement and
     reach. This is the highest-performing single post in brand history."

Learning Memory decision:
    Does NOT recommend provocative content.

Reason:
    Brand System restriction: "We communicate with professional,
    constructive, educational tone. We do not engage in controversy
    or polarization."

    Learning Memory cannot override this restriction.

    The engagement gain is real — but the brand cost of violating
    identity is higher than the engagement benefit.

    This result is stored as a data point but does NOT become a
    Performance Pattern for future use.

    It may be stored as a warning: "Provocative content violates
    brand identity. High engagement does not justify brand erosion."
```

This example demonstrates that Learning Memory is not a simple
optimization engine that maximizes metrics. It is a knowledge layer
that operates within strategic constraints.

---

# 14. Foundation MVP Relationship

## 14.1. Current State

The Foundation MVP does NOT contain Learning Memory as an active
component.

In the current Foundation MVP:

```text
Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot
```

The system creates content, publishes it and records metrics.

But it does not:

- extract knowledge from results;
- identify patterns across cycles;
- accumulate experience for future decisions;
- prevent repeated mistakes;
- validate hypotheses through experiments.

`MetricSnapshot` exists as the data collection foundation.

Learning Memory is the intelligence layer that transforms that data
into actionable knowledge.

## 14.2. The Foundation Role

The Foundation MVP provides the essential prerequisite for Learning
Memory:

**Reliable, structured performance data.**

Without `MetricSnapshot`, there is nothing to learn from.

The Foundation MVP establishes the data collection pipeline that
Learning Memory will consume.

## 14.3. Future Activation

When Learning Memory is activated:

```text
Current Foundation MVP:
    MetricSnapshot → stored as record. No further processing.

Future with Learning Memory:
    MetricSnapshot → Analytics Intelligence → Learning Extraction
    → Learning Memory → Orchestrator Agent → Improved decisions.
```

The Foundation MVP entities are not replaced. They are extended with:

- analytics processing (Automated analysis of MetricSnapshot data);
- learning extraction (Transformation of analysis into knowledge);
- memory storage (Persistent, organized knowledge);
- memory retrieval (Query interface for Intelligence Modules and
  Orchestrator).

## 14.4. What Stays

The Foundation MVP pipeline remains the production backbone:

- `Idea` — creative concept (source becomes intelligence-driven);
- `Scenario` — content plan;
- `ContentItem` — produced content;
- `ExportPackage` — distribution package;
- `Publication` — publication record;
- `MetricSnapshot` — performance data.

Learning Memory wraps AROUND this pipeline:

- Before: provides knowledge to inform Idea creation.
- After: extracts knowledge from MetricSnapshot results.

The pipeline itself is unchanged. The intelligence around it evolves.

## 14.5. Evolution Path

```text
Foundation MVP (current)
    Deterministic pipeline
    Manual metrics collection
    No knowledge extraction
    No pattern recognition
        ↓
Content Intelligence (next)
    Automated performance analysis
    Basic pattern detection
    Learning Records created
        ↓
Agentic Operations
    Orchestrator Agent active
    Learning Memory operational
    Knowledge applied to decisions
    Confidence model active
        ↓
Marketing Operating System
    Full autonomous learning cycle
    Continuous knowledge accumulation
    Self-improving marketing system
```

Reference: `LOOPRA_ARCHITECTURE.md`, Section 2

---

# 15. Future Implementation Considerations

## 15.1. Overview

This section describes conceptual directions for Learning Memory
implementation. It does not specify implementation details,
technologies or timelines.

These directions represent the architectural vision for how Learning
Memory capabilities may evolve.

## 15.2. Semantic Memory

Beyond structured pattern storage, Learning Memory may develop
semantic understanding:

- recognizing that "educational carousel with practical frameworks"
  and "step-by-step guide in multi-slide format" describe the same
  underlying pattern;
- connecting knowledge across categories — understanding that an
  audience preference for "practical, actionable content" explains
  both format preference (carousels that can be saved) and angle
  preference (step-by-step over theoretical);
- building conceptual maps of marketing effectiveness that transcend
  individual patterns.

## 15.3. Knowledge Graph

Learning Memory may organize knowledge as a connected graph rather
than isolated entries:

```text
Audience Node: "Professional Marketers"
    ↓ prefers format
Format Node: "Educational Carousel"
    ↓ effective for goal
Goal Node: "Lead Generation"
    ↓ best on channel
Channel Node: "LinkedIn"
    ↓ optimal timing
Timing Node: "Tuesday–Thursday, 8–10 AM"
```

This enables traversal queries:

- "What content should we create for professional marketers on
  LinkedIn?" → traverse from audience to channel, find overlapping
  formats, goals and patterns.

- "Why did our last carousel underperform?" → traverse from format to
  audience, check if the audience was correct; traverse from format to
  goal, check if the goal aligned; traverse from format to pattern,
  check if conditions were met.

## 15.4. Similarity Search

When the Orchestrator faces a new situation, Learning Memory can:

- find the most similar past situations based on audience, goal,
  channel and topic similarity;
- retrieve what worked in those situations;
- provide confidence based on how similar the current situation is to
  past situations.

Similarity search enables the Orchestrator to reason:

```text
"This is a new combination: storytelling video for the professional
 audience on Instagram. We have no direct experience.

 But similar situations exist:
    - Storytelling video for professional audience on LinkedIn
      (medium confidence)
    - Educational video for professional audience on Instagram
      (high confidence)
    - Storytelling carousel for professional audience on Instagram
      (medium confidence)

 Based on the closest matches, the predicted outcome is X with
 medium-low confidence."
```

## 15.5. Pattern Discovery

Beyond recognizing predefined pattern types, Learning Memory may
discover novel patterns:

- identifying correlations that were not previously hypothesized:
  "Content published on the same day as a major industry event
   generates 60% higher engagement regardless of topic."

- surfacing unexpected insights:
  "The save-to-like ratio for educational content is 4:1. For
   entertainment content it is 1:3. The audience treats educational
   content as reference material and entertainment content as
   consumable."

- detecting audience evolution:
  "Over the last 20 cycles, the audience has shifted from preferring
   text-based educational content to video-based educational content."

## 15.6. Predictive Analytics

Based on accumulated knowledge, Learning Memory may predict future
outcomes:

- **Performance Prediction** — before content is created, predict its
  likely performance based on similar past content;
- **Trend Projection** — predict whether a current trend will grow,
  peak or decline based on historical trend patterns;
- **Audience Forecasting** — predict how audience preferences may
  evolve based on past preference shifts;
- **Risk Assessment** — predict the probability of failure for an
  untested content direction based on similarity to past failures.

Predictions are not guarantees. They are probabilistic inputs to
decision-making, calibrated by the confidence model.

## 15.7. Automated Learning Extraction

Learning extraction may move from triggered (cycle completion) to
continuous:

- real-time pattern detection as data arrives;
- automatic hypothesis formation when anomalies are detected;
- proactive knowledge gap identification — recognizing what the
  system does not know and recommending experiments to fill the gap;
- continuous confidence recalibration as new evidence arrives.

## 15.8. Implementation Constraints

Regardless of implementation approach, Learning Memory must respect:

- **Project Scoping** — knowledge is project-scoped, never shared
  across projects;
- **Brand System Boundaries** — learning does not override strategy,
  identity or restrictions;
- **Orchestrator Authority** — Learning Memory informs decisions but
  does not make them;
- **Foundation MVP Preservation** — the Idea → Scenario → ContentItem
  pipeline remains intact;
- **Module Boundaries** — Learning Memory is an Intelligence Module,
  not an agent or a decision-making authority.

---

# 16. Related Documents

## 16.1. Core Intelligence Documents

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Content Cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Agent System specification
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — Trend Intelligence specification
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content Intelligence specification
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — This document
```

## 16.2. Architecture Layer

```text
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
```

## 16.3. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
docs/00_foundation/MVP_SCOPE.md                     — Foundation MVP scope
```

## 16.4. Product Layer

```text
docs/01_product/LOOPRA_BRAND_POSITIONING.md         — LOOPRA product identity
docs/01_product/USER_WORKFLOWS.md                   — User interaction model
```

## 16.5. Future Documents

```text
docs/04_production/CONTENT_TYPES_SPEC.md            — Content format definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — Production workflow specification
docs/04_production/CONTENT_OPERATING_SYSTEM_SPEC.md — Autonomous cycle execution
```

## 16.6. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# 17. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Intelligence Layer — Learning Memory Specification |

---

# Final Statement

Learning Memory is the mechanism that transforms LOOPRA from an
automated marketing production tool into a self-learning marketing
operating system.

Without Learning Memory:

```text
Create content → Publish → Record metrics → Repeat.
The system does the same thing every cycle regardless of results.
```

With Learning Memory:

```text
Create content → Publish → Measure results → Extract knowledge →
Store patterns → Apply learning → Create better content.
Each cycle is smarter than the previous one.
```

Learning Memory answers the essential question:

> "What works, why it works, and when it works."

It stores four types of memory:

- **Context Memory** — the current situation;
- **Operational Memory** — what works in practice;
- **Decision Memory** — why decisions were made;
- **Experimental Memory** — what was discovered through testing.

It accumulates knowledge across five dimensions:

- **Audience Learning** — how the audience behaves;
- **Content Learning** — what content structures produce results;
- **Channel Learning** — which platforms are effective for what;
- **Timing Learning** — when content performs best;
- **Goal Learning** — what best serves each business objective.

It operates within critical boundaries:

- Learning Memory does NOT replace Brand System — strategy sets the
  boundaries, learning optimizes within them;
- Learning Memory does NOT make decisions — the Orchestrator Agent
  decides; Learning Memory informs;
- Learning Memory does NOT override restrictions — brand safety rules
  are absolute regardless of what "works."

Learning Memory is the layer that closes the LOOPRA Growth Loop:

```text
Intelligence → Decision → Action → Result → Learning → Better Intelligence
     ↑                                                          │
     └──────────────────────────────────────────────────────────┘
                         Continuous improvement
```

Each cycle feeds the next.

Knowledge compounds.

Marketing does not restart every day — it continuously improves.

This is the architectural foundation of the self-learning autonomous
marketing operating system.

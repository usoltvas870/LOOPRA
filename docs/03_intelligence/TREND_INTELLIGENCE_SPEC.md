# TREND INTELLIGENCE SPEC

## Version

v1.0

## Status

Active — LOOPRA Intelligence Layer

## Purpose

This document defines the functional architecture of the Trend
Intelligence Module — the first Intelligence Module of the LOOPRA
Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA detect market changes, understand significant trends
> and transform them into content opportunities for a specific brand?

TREND_INTELLIGENCE_SPEC.md is the functional specification for the
module that enables LOOPRA to sense and interpret the external
environment before making any content decisions.

It describes:

- sources of market signals;
- signal processing and normalization;
- trend detection and pattern recognition;
- trend relevance evaluation for specific brands;
- structured knowledge delivery to the Orchestrator Agent.

It does NOT describe:

- specific APIs, platforms or data providers;
- scraping implementation or data collection code;
- database schemas or storage implementation;
- AI model providers, prompts or model selection;
- code-level implementation details.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

TREND_INTELLIGENCE_SPEC.md defines the functional model of external
environment analysis within LOOPRA.

It serves as the specification for how LOOPRA:

- collects signals from the external world;
- processes and classifies those signals;
- detects meaningful trends and patterns;
- evaluates relevance for a specific brand;
- delivers structured knowledge to the Orchestrator Agent.

## 1.2. Scope

This document covers:

- external signal sources and their categories;
- the MarketSignal entity and its structure;
- the signal processing pipeline from raw observation to trend candidate;
- trend detection criteria and validation;
- the TrendPattern entity and its structure;
- brand-specific relevance scoring;
- relationship with Brand System, Orchestrator Agent and Learning Memory;
- trend lifecycle from detection to learning feedback;
- relationship to the current Foundation MVP.

## 1.3. Out of Scope

This document does not cover:

- specific API integrations or data provider selection;
- scraping implementation, crawlers or data collection infrastructure;
- database schemas, storage engines or indexing strategies;
- AI model configuration, prompts or provider evaluation;
- UI components for signal visualization or trend dashboards;
- Content Intelligence logic (see future `CONTENT_INTELLIGENCE_SPEC.md`);
- Orchestrator Agent decision algorithms (see `AGENT_SYSTEM_SPEC.md`).

---

# 2. Role of Trend Intelligence in LOOPRA

## 2.1. Position in the Content Cycle

Trend Intelligence operates at the beginning of the LOOPRA Content
Cycle:

```text
Market Signal Discovery (Stage 1)
    ↓
Trend Understanding (Stage 2)
    ↓
Content Opportunity Creation (Stage 3)
```

Trend Intelligence is responsible for Stages 1 and 2 of the Content
Cycle.

Reference: `CONTENT_CYCLE_SPEC.md`, Sections 4 and 5

## 2.2. Position in the System Architecture

Within the LOOPRA system:

```text
External World
    ↓
Trend Intelligence
    ↓
Structured Knowledge (MarketSignals, TrendPatterns, opportunities)
    ↓
Orchestrator Agent
    ↓
Decision
```

Trend Intelligence is an Intelligence Module — a specialized analytical
capability. It does not make autonomous decisions. It provides
structured knowledge that the Orchestrator Agent integrates into its
decision-making process.

Reference: `SYSTEM_ARCHITECTURE.md`, Section 7.1
Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.3

## 2.3. What Trend Intelligence Does

Trend Intelligence:

- collects signals from external sources;
- analyzes changes in market behaviour, audience preferences and
  competitor activity;
- detects emerging patterns that may create marketing opportunities;
- evaluates relevance of detected trends for a specific brand;
- provides structured knowledge (MarketSignals, TrendPatterns, opportunity
  assessments) to the Orchestrator Agent.

## 2.4. What Trend Intelligence Does NOT Do

Trend Intelligence does NOT:

- create content;
- make strategic decisions about what content to produce;
- select which opportunities to pursue;
- publish content or interact with distribution channels;
- override Brand System rules or brand identity.

These responsibilities belong to the Orchestrator Agent, Production
Tools and the Human Operator respectively.

## 2.5. Intelligence Module Role

As an Intelligence Module within the LOOPRA Agent System, Trend
Intelligence follows the module principles:

- **Single responsibility** — answers one category of questions:
  "What is happening in the market that is relevant to this brand?"
- **No independent action** — Trend Intelligence analyzes; the
  Orchestrator decides.
- **Stateless analysis** — processes current inputs against stored
  knowledge (Learning Memory).
- **Structured output** — returns typed entities the Orchestrator can
  reason about.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.2

---

# 3. Core Principles

## 3.1. Signal First, Not Content First

LOOPRA does not begin with the question:

> "What content should we create?"

LOOPRA begins with the question:

> "What is happening in the world and why is it important?"

Trend Intelligence embodies this principle. Before any content idea
exists, Trend Intelligence establishes the external context — what is
changing, what audiences care about, what competitors are doing, what
platforms are enabling.

Content decisions are downstream from market understanding.

## 3.2. Trends Are Context Dependent

A trend is not universally relevant.

The same market change can be:

- critically important for one brand;
- completely irrelevant for another brand;
- counterproductive for a third brand.

Example:

```text
Trend: "AI productivity tools are gaining rapid adoption among
entrepreneurs."

Brand A — Technology audience for entrepreneurs:
    Alignment with brand positioning: high
    Relevance to defined audience: high
    Compatibility with content strategy: high
    → High relevance — significant opportunity.

Brand B — Luxury fashion for high-net-worth individuals:
    Alignment with brand positioning: low
    Relevance to defined audience: low
    Compatibility with content strategy: low
    → Low relevance — not a priority.
```

Trend Intelligence does not simply report popular trends. It evaluates
trends through the lens of a specific brand's identity, audience, goals
and strategy.

This evaluation is performed using the Brand System as the source of
truth.

Reference: `BRAND_SYSTEM_SPEC.md`

## 3.3. Signal Is Not Trend

Trend Intelligence distinguishes three levels of market observation:

```text
Signal:
    A single observation of change.
    "One creator posted a short educational video and received high
    engagement."

Trend:
    A confirmed shift in behaviour supported by multiple signals over
    time.
    "Short educational videos are consistently outperforming long-form
    educational content among professional audiences."

Pattern:
    A repeatable structure of success extracted from multiple trends
    and validated through performance data.
    "Content under 60 seconds with a strong hook in the first 3 seconds,
    educational value and clear takeaway outperforms longer formats
    across platforms."
```

- A **Signal** is a data point. It may or may not represent a
  meaningful change.
- A **Trend** is a validated behavioural shift backed by persistence,
  growth and adoption.
- A **Pattern** is an abstracted, repeatable structure that can be
  applied to future content decisions.

Trend Intelligence works to move from Signal → Trend → Pattern,
providing increasingly structured and actionable knowledge.

---

# 4. External Signal Sources

## 4.1. Overview

Trend Intelligence monitors the external environment through multiple
signal source categories.

This section defines the conceptual categories of signal sources. It
does not specify concrete platforms, APIs or data providers.

## 4.2. Social Signals

Social signals capture changes in public conversation, content
consumption and engagement patterns.

Examples of what Social Signals detect:

- emerging topics gaining traction in audience conversations;
- viral content formats spreading across platforms;
- engagement pattern shifts — what types of content receive more
  interaction;
- audience discussion themes — what people are talking about, asking
  about, concerned about;
- cultural moments and conversations that brands may engage with;
- sentiment shifts toward topics, brands or industries.

## 4.3. Search Signals

Search signals capture changes in what people are actively looking for.

Examples of what Search Signals detect:

- rising search interests — topics with growing query volume;
- keyword phrase changes — how people describe their needs is evolving;
- demand shifts — new problems, needs or desires emerging;
- seasonal patterns — predictable interest cycles;
- question trends — what people are asking about a topic or industry.

## 4.4. Competitor Signals

Competitor signals capture observable changes in competitor behaviour
and audience response.

Examples of what Competitor Signals detect:

- content strategy shifts — new topics, formats or tones competitors
  are adopting;
- format adoption — which content types competitors are investing in;
- audience response — how competitor audiences react to specific
  content approaches;
- publishing pattern changes — frequency, timing, channel mix
  adjustments;
- positioning evolution — how competitors are repositioning themselves.

## 4.5. Platform Signals

Platform signals capture changes in the distribution environment.

Examples of what Platform Signals detect:

- algorithm changes that affect content visibility and reach;
- new content formats introduced by platforms;
- feature changes that create new distribution opportunities;
- policy updates that affect content strategy;
- platform growth or decline trends affecting audience presence.

## 4.6. Internal Performance Signals

Internal signals capture patterns within the brand's own performance
data.

Examples of what Internal Performance Signals detect:

- content format performance trends across cycles;
- audience engagement patterns with specific content types;
- channel effectiveness shifts;
- metric anomalies — unexpected changes in reach, engagement or
  conversion;
- content topic resonance patterns over time.

Internal signals connect Trend Intelligence to Learning Memory —
past performance data informs the evaluation of new external signals.

## 4.7. Signal Source Categories Summary

| Source | Detects | Purpose |
|---|---|---|
| Social Signals | Conversation changes, format virality, engagement shifts | Understand audience interests and content consumption |
| Search Signals | Query trends, demand shifts, seasonal patterns | Understand what people actively seek |
| Competitor Signals | Strategy changes, format adoption, audience response | Understand competitive landscape movement |
| Platform Signals | Algorithm updates, new formats, policy changes | Understand distribution environment evolution |
| Internal Signals | Own performance patterns, metric anomalies, content resonance | Ground external observations in own data |

---

# 5. MarketSignal Entity

## 5.1. Definition

A `MarketSignal` is a structured observation of a change in the
external environment.

It represents a single data point — one piece of evidence that
something has changed.

A MarketSignal is NOT a confirmed trend. It is a raw observation that
requires further analysis and validation.

Reference: `DATA_MODEL.md`, Section 4.1

## 5.2. Purpose

MarketSignal serves as the atomic unit of external observation in
LOOPRA.

It:

- captures a detected change in structured form;
- preserves source and context of the observation;
- carries initial assessment of potential relevance;
- enables aggregation and pattern detection across multiple signals.

## 5.3. Entity Structure

| Field | Description |
|---|---|
| `source` | Category of signal source (social, search, competitor, platform, internal) |
| `timestamp` | When the signal was detected |
| `category` | Type of change observed (topic, format, audience, platform, competitor) |
| `description` | Human-readable description of the observed change |
| `detected_change` | What specifically changed compared to previous state |
| `initial_relevance` | Preliminary relevance assessment (high, medium, low, unknown) |
| `confidence` | Confidence in the signal's validity (high, medium, low) |

## 5.4. Signal Categories

| Category | Description | Example |
|---|---|---|
| topic | A subject gaining or losing attention | "Interest in no-code tools is growing among small business owners" |
| format | A content format showing changed performance | "Carousel posts on LinkedIn are receiving more engagement than text posts" |
| audience | A shift in audience behaviour or preferences | "Professional audience segment is migrating from X to Threads" |
| platform | A change in platform capabilities or algorithms | "Platform X introduced a new short-video format with increased organic reach" |
| competitor | An observable change in competitor activity | "Three competitors in the market launched daily educational content series" |
| sentiment | A shift in audience sentiment toward a topic | "Audience sentiment toward AI-generated content is becoming more skeptical" |

## 5.5. Confidence Levels

| Confidence | Meaning | Implication |
|---|---|---|
| High | Signal is well-supported by multiple observations | Strong candidate for trend analysis |
| Medium | Signal is plausible but not strongly verified | Requires additional monitoring |
| Low | Signal is a single observation or weakly supported | Archive for later re-evaluation |

## 5.6. Example

```text
MarketSignal:

    source: social
    timestamp: 2026-07-08T10:00:00Z
    category: format
    description: "Short educational videos about AI tool usage are
                  generating 3x higher engagement than long-form
                  educational posts among entrepreneur audiences."
    detected_change: "Engagement ratio for short-form educational
                      video vs long-form text shifted from 2:1 to
                      3:1 in the last 4 weeks."
    initial_relevance: medium
    confidence: high
```

## 5.7. Relationship to Other Entities

```text
MarketSignal
    ↓  feeds into
Trend Intelligence analysis pipeline
    ↓  produces
TrendPattern (when multiple signals confirm a trend)
    ↓  feeds into
Content Intelligence (opportunity creation)
```

---

# 6. Signal Processing Pipeline

## 6.1. Overview

Raw signals from the external environment must be processed before they
can inform decisions.

Trend Intelligence applies a structured pipeline:

```text
Raw Signal
    ↓
Collection
    ↓
Normalization
    ↓
Classification
    ↓
Relevance Evaluation
    ↓
Trend Candidate
```

Each stage transforms the signal toward a more structured and actionable
form.

## 6.2. Collection

Raw observations are collected from signal sources.

At this stage:

- observations are unprocessed;
- duplicates may exist;
- noise is present;
- source and timestamp are captured.

Collection does not filter for relevance. It captures what is
observable.

## 6.3. Normalization

Raw signals are transformed into a consistent structure.

Normalization includes:

- extracting the core observation from source-specific formats;
- standardizing terminology across different sources;
- removing duplicates and near-duplicates;
- enriching with metadata (timestamp normalization, source tagging);
- converting unstructured descriptions into structured `detected_change`
  fields.

After normalization, signals are comparable across different sources.

## 6.4. Classification

Each normalized signal is classified by:

- **Signal category** — topic, format, audience, platform, competitor,
  sentiment;
- **Change type** — emerging, growing, stable, declining;
- **Scope** — industry-wide, platform-specific, audience-segment-specific,
  competitor-specific;
- **Urgency** — immediate action needed, monitor, observe, historical
  reference.

Classification enables subsequent grouping and pattern detection.

## 6.5. Relevance Evaluation

Each classified signal receives a preliminary relevance assessment.

At this stage, relevance is evaluated against:

- the brand's industry and domain;
- the brand's defined audience segments;
- the brand's content strategy pillars;
- the brand's active business goals.

This is a preliminary filter — detailed relevance scoring occurs at the
trend level.

Signals clearly outside the brand's domain are deprioritized but not
discarded. A signal that is irrelevant today may become relevant if
conditions change.

## 6.6. Trend Candidate

After processing, each signal becomes a `Trend Candidate` — a signal
ready for trend detection analysis.

Trend candidates carry:

- the normalized, classified signal;
- metadata about processing decisions;
- initial relevance assessment;
- confidence level.

Candidates are grouped by similarity for trend detection.

---

# 7. Trend Detection

## 7.1. Overview

A single signal is not a trend.

Trend detection is the process of determining whether observed changes
represent a meaningful, sustained shift in market behaviour.

Trend Intelligence evaluates signals against five factors to determine
whether they constitute a trend.

## 7.2. Detection Factors

### Persistence

Does the change repeat over time?

A single observation may be an anomaly. Multiple observations over an
extended period suggest a trend.

Persistence is evaluated by:

- frequency of signal recurrence;
- consistency of the pattern over time;
- absence of contradictory signals.

### Growth

Is interest in the change increasing?

A trend should show growing attention, not a stable level of interest.

Growth is evaluated by:

- rising signal frequency over time;
- increasing volume of related observations;
- expanding audience engagement with the topic or format.

### Adoption

Are more actors engaging with this change?

A trend is adopted when it spreads beyond early observers to broader
participation.

Adoption is evaluated by:

- increasing number of content creators using the format or topic;
- expanding platform support for the content type;
- growing audience familiarity and expectation.

### Engagement

Does the change provoke audience response?

A trend that does not generate engagement is not useful for marketing.

Engagement is evaluated by:

- audience interaction rates with related content;
- comment volume, sharing behaviour and saves;
- discussion depth and quality around the topic.

### Relevance

Does this change matter for this specific brand?

This is the critical filter. A trend may be persistent, growing,
widely adopted and highly engaging — and still be wrong for a
particular brand.

Relevance is evaluated against the Brand System (see Section 10).

## 7.3. Trend Confirmation

A signal becomes a confirmed trend when it meets threshold criteria
across multiple factors:

```text
Persistence:  signal appears consistently over defined time window
    + 
Growth:       signal frequency or volume is increasing
    +
Adoption:     adoption is expanding beyond isolated cases
    +
Engagement:   audience response is measurable and sustained
    +
Relevance:    change is relevant to the brand's domain and audience
    =
Trend:        confirmed understanding of a market shift
```

A confirmed trend is documented as a `TrendPattern`.

## 7.4. Signal Lifecycle Classification

As signals move toward trend confirmation, they pass through lifecycle
stages:

| Stage | Description | Action |
|---|---|---|
| Emerging | New signal detected, too early to confirm | Monitor closely |
| Growing | Signal strengthening across multiple sources | Prioritize for analysis |
| Mature | Established trend, well-supported by evidence | Evaluate for opportunities |
| Declining | Trend fading, interest decreasing | Deprioritize; avoid investment |
| Archived | Trend no longer relevant | Preserve for historical reference |

---

# 8. TrendPattern Entity

## 8.1. Definition

A `TrendPattern` is a structured description of an identified content
or market pattern.

It represents the output of trend detection — a confirmed,
understandable pattern that can inform content decisions.

A TrendPattern abstracts from individual signals to describe the
underlying behavioural structure.

Reference: `DATA_MODEL.md`, Section 4.2

## 8.2. Purpose

TrendPattern serves as the knowledge unit that Trend Intelligence
delivers to the Orchestrator Agent.

It:

- describes what pattern has been detected;
- provides evidence supporting the pattern;
- identifies which audience segments are affected;
- indicates which content formats are relevant;
- carries a confidence level for decision-making.

## 8.3. Entity Structure

| Field | Description |
|---|---|
| `pattern_type` | Category of the pattern (content, audience, format, timing, hook, topic) |
| `description` | Human-readable description of the identified pattern |
| `evidence` | Summary of supporting signals and data |
| `affected_audience` | Which audience segments this pattern applies to |
| `related_formats` | Which content formats are involved in this pattern |
| `confidence` | System confidence in the pattern's validity |

## 8.4. Pattern Types

| Pattern Type | Description | Example |
|---|---|---|
| Content Pattern | A repeatable content structure that drives results | "Short educational videos with strong hooks in the first 3 seconds outperform long explanations" |
| Audience Pattern | A repeatable audience behaviour or preference | "Professional audiences engage more with practical examples than theoretical content" |
| Format Pattern | A content format showing consistent performance characteristics | "Carousel format increases saves and revisit rate compared to single-image posts" |
| Timing Pattern | A temporal pattern in content performance | "Content published on Tuesday and Thursday mornings receives higher initial reach" |
| Hook Pattern | A specific opening technique that drives engagement | "Question-based hooks generate 2x more comment engagement than statement hooks" |
| Topic Pattern | A thematic area showing sustained audience interest | "Practical AI application content consistently outperforms abstract AI discussion" |
| Channel Pattern | A platform-specific content behaviour | "LinkedIn audience engages more with professional storytelling than promotional content" |

## 8.5. Confidence Levels

| Confidence | Meaning | Implication for Orchestrator |
|---|---|---|
| High | Pattern is well-supported by multiple signals and past performance data | Strong basis for content decisions |
| Medium | Pattern is supported but not extensively validated | Use with caution; consider as experiment |
| Low | Pattern is newly detected with limited evidence | Monitor; do not base major decisions on this pattern |

## 8.6. Pattern Evidence

Each TrendPattern carries evidence — a summary of the signals and data
that support it.

Evidence may include:

- number and recency of supporting signals;
- signal source diversity (multiple independent sources strengthen
  confidence);
- alignment with past Learning Memory entries;
- consistency over time;
- absence of contradictory observations.

## 8.7. Example

```text
TrendPattern:

    pattern_type: content
    description: "Short educational videos (under 60 seconds) with
                  practical AI tool demonstrations are generating
                  engagement rates 2.5x higher than static educational
                  posts among entrepreneur and marketer audiences."
    evidence: "Detected through 47 social signals over 8 weeks, confirmed
               by competitor adoption across 5 accounts in the market,
               supported by internal performance data showing similar
               pattern in the last 2 content cycles."
    affected_audience: ["entrepreneurs", "marketers", "small business owners"]
    related_formats: ["short_video_reel", "educational_carousel"]
    confidence: high
```

## 8.8. Relationship to Other Entities

```text
MarketSignal (multiple, confirmed)
    ↓  analyzed by Trend Intelligence
TrendPattern
    ↓  delivered to
Content Intelligence
    ↓  combined with Brand System and Learning Memory
Content Opportunity
    ↓  evaluated by
Orchestrator Agent
```

---

# 9. Trend Relevance Scoring

## 9.1. Overview

Trend Intelligence does not simply identify popular trends.

Its critical function is answering:

> "How important is this trend for THIS specific brand?"

Relevance scoring evaluates every detected trend through the lens of a
specific brand's identity, audience, goals and strategy.

The output is a Relevance Score that the Orchestrator Agent uses to
prioritize opportunities.

## 9.2. Scoring Factors

### Brand Alignment

How well does this trend align with the brand's positioning, values
and communication style?

```text
High alignment:   trend naturally fits the brand's identity and voice
Medium alignment: trend is not contradictory but requires adaptation
Low alignment:    trend conflicts with brand positioning or tone
```

Brand alignment is evaluated against the Brand System:
`BRAND_SYSTEM_SPEC.md`

### Audience Relevance

How relevant is this trend to the brand's defined audience segments?

```text
High relevance:   trend directly involves or interests defined segments
Medium relevance: trend partially overlaps with audience interests
Low relevance:    trend is unrelated to audience interests or needs
```

### Goal Relevance

How well does this trend support the brand's active marketing goals?

```text
High relevance:   trend directly supports a high-priority goal
Medium relevance: trend supports a medium or low-priority goal
Low relevance:    trend does not contribute to any active goal
```

Goal alignment is evaluated against Project Settings:
`PROJECT_SETTINGS_SPEC.md`

### Evidence Strength

How strong is the evidence supporting this trend?

```text
High strength:    multiple independent sources, consistent over time,
                  supported by internal data
Medium strength:  several sources, moderate consistency, limited
                  internal validation
Low strength:     few sources, inconsistent, no internal validation
```

### Timing

Is now the right moment to act on this trend?

```text
Optimal:          trend is growing, early adoption advantage exists
Acceptable:       trend is mature, still valuable to participate
Late:             trend is declining, limited remaining value
Premature:        trend is too early, audience not yet engaged
```

## 9.3. Relevance Score Calculation

The Relevance Score is a composite evaluation:

```text
Relevance Score
    =
Brand Alignment      × weight
Audience Relevance   × weight
Goal Relevance       × weight
Evidence Strength    × weight
Timing               × weight
```

Weights are configurable per project and may be adjusted based on
business priorities.

The Orchestrator Agent receives the Relevance Score alongside the
TrendPattern and uses it to prioritize which opportunities to pursue.

## 9.4. Relevance Score Ranges

| Score Range | Meaning | Recommended Action |
|---|---|---|
| High | Trend is strongly relevant to this brand | Prioritize for Content Opportunity creation |
| Medium | Trend has partial relevance | Consider as secondary opportunity or experiment |
| Low | Trend has minimal relevance | Monitor but do not prioritize |
| None | Trend is irrelevant or counterproductive | Archive; do not pursue |

## 9.5. Example Relevance Evaluation

```text
Trend: "Short educational videos with practical AI demonstrations"

Brand: Technology education platform for entrepreneurs

    Brand Alignment:  high    (educational, practical, technology-focused)
    Audience Relevance: high  (entrepreneurs actively seek practical AI knowledge)
    Goal Relevance:   high   (supports engagement and authority-building goals)
    Evidence Strength: high  (47 signals, 8 weeks, competitor + internal validation)
    Timing:           optimal (trend is growing, early adoption advantage)

    Relevance Score: HIGH → Create Content Opportunity immediately.

---

Same trend. Different brand:

Brand: Luxury fashion house

    Brand Alignment:  low     (technology focus conflicts with fashion identity)
    Audience Relevance: low   (luxury consumers not primary AI tool audience)
    Goal Relevance:   low    (does not support awareness or desire goals)
    Evidence Strength: high  (trend is real, just not relevant)
    Timing:           optimal (but irrelevant)

    Relevance Score: LOW → Archive; do not pursue.
```

The trend is real in both cases. The difference is brand context.

---

# 10. Relationship with Brand System

## 10.1. The Brand System as Context Filter

Trend Intelligence does not evaluate trends in isolation.

Every analysis is performed through the lens of the Brand System —
the structured knowledge layer that defines who the brand is and how
it communicates.

The Brand System provides the context for answering:

- does this trend align with who we are?
- does this trend matter to our audience?
- does this trend fit our communication style?
- does this trend violate any restrictions?

Reference: `BRAND_SYSTEM_SPEC.md`

## 10.2. Brand System Elements Used

Trend Intelligence reads from the Brand System:

| Brand System Element | How Trend Intelligence Uses It |
|---|---|
| Brand Identity | Evaluates whether a trend aligns with brand positioning, mission and values |
| Audience Intelligence | Evaluates whether a trend involves defined audience segments and their pain points |
| Communication System | Evaluates whether the brand's tone of voice is compatible with the trend |
| Content Strategy | Evaluates whether the trend fits defined content pillars and format preferences |
| Business Goals | Evaluates whether the trend supports active marketing goals |
| Restrictions and Safety | Identifies trends that must not be pursued due to forbidden topics, claims or compliance rules |

## 10.3. What Trend Intelligence Communicates

Trend Intelligence does not say:

> "This trend is popular. Use it."

Trend Intelligence says:

> "This trend is relevant to your brand because [alignment with
> positioning], your audience is [affected segment], and it supports
> your goal of [relevant goal]. Confidence: [high/medium/low].
> Evidence: [summary]."

This structured communication enables the Orchestrator Agent to make
informed decisions rather than following popularity.

## 10.4. Restriction Compliance

Trend Intelligence actively filters out trends that conflict with
brand restrictions.

If a trend involves:

- forbidden topics;
- prohibited claims;
- restricted content categories;
- legal or compliance risks.

Trend Intelligence marks it as `restricted` regardless of its
popularity or potential engagement value.

Brand restrictions are absolute boundaries. No trend overrides them.

---

# 11. Relationship with Orchestrator Agent

## 11.1. Provider-Consumer Relationship

Trend Intelligence is a provider. The Orchestrator Agent is the
consumer.

Trend Intelligence provides:

- **MarketSignals** — structured observations of external change;
- **TrendPatterns** — confirmed, explained market patterns;
- **Relevance Scores** — brand-specific importance assessments;
- **Opportunity Assessments** — preliminary evaluations of content
  potential.

The Orchestrator Agent consumes these outputs to answer:

> "What is happening in the market that is relevant to this brand?"

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.3

## 11.2. Decision Boundary

The critical separation:

```text
Trend Intelligence answers:   "What is happening and why it matters."
                               ↓
                              Knowledge
                               ↓
Orchestrator Agent answers:   "What should we do about it."
                               ↓
                              Decision
```

Trend Intelligence does not decide:

- whether to act on a trend;
- which opportunity to pursue;
- what content to create;
- how to allocate resources;
- when to publish.

These are Orchestrator Agent decisions.

Trend Intelligence ensures the Orchestrator's decisions are informed
by structured external knowledge, not guesswork.

## 11.3. Query Model

The Orchestrator Agent queries Trend Intelligence with:

- a specific brand context (Brand System reference);
- a time scope (recent signals, historical trends);
- a focus area (specific industry, platform, audience segment);
- a priority level (urgent analysis vs. routine monitoring).

Trend Intelligence returns:

- relevant MarketSignals;
- confirmed TrendPatterns;
- relevance-scored opportunity assessments;
- confidence levels for each finding.

## 11.4. Escalation

Trend Intelligence may escalate to the Orchestrator when:

- a high-relevance, high-confidence trend is detected that represents
  a significant opportunity;
- a market shift is detected that may require strategy adjustment;
- a trend is detected that approaches restriction boundaries;
- a previously stable pattern shows unexpected change.

The Orchestrator decides whether to escalate further to the Human
Operator based on autonomy mode and decision significance.

---

# 12. Relationship with Learning Memory

## 12.1. Learning from Past Signals

Trend Intelligence uses Learning Memory to ground external observations
in the brand's own experience.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.6

## 12.2. How Learning Memory Enhances Trend Intelligence

### Evidence Strengthening

When a detected trend aligns with past performance data:

```text
Trend: "Educational carousel content is gaining engagement."

Learning Memory: "Carousel format produced 40% higher save rate in
                  the last 2 cycles for this audience segment."

Result: Higher confidence in the trend's relevance. Evidence is
        strengthened by internal validation.
```

### Pattern Recognition

Learning Memory provides historical patterns that help classify new
signals:

```text
New Signal: "Short-form video engagement is increasing."

Learning Memory: "Video content under 60 seconds has consistently
                  outperformed longer video for this audience over
                  6 cycles."

Result: The signal is recognized as part of an established pattern
        rather than a new, unverified observation.
```

### Confidence Adjustment

Past outcomes affect confidence:

```text
Trend: "Topic X is gaining attention."

Learning Memory check: Has content about Topic X performed well
                       for this brand in the past?

    Yes, with strong evidence    → Confidence increased
    Yes, with moderate evidence  → Confidence unchanged
    No past data                 → Confidence slightly reduced
    Past attempts failed         → Confidence significantly reduced;
                                   trend flagged with warning
```

### Relevance Calibration

Learning Memory helps calibrate relevance:

```text
Trend: "Audience segment Y is engaging with format Z."

Learning Memory: "This audience segment responded well to format Z
                  in cycle 3 but poorly in cycle 5. The difference
                  was the topic, not the format."

Result: Relevance scoring accounts for the nuance — the format is
        relevant but topic selection within it is critical.
```

## 12.3. Learning Memory Boundaries

Learning Memory enhances Trend Intelligence but does not override it:

- Learning Memory provides past context; Trend Intelligence provides
  current observation.
- If Learning Memory suggests a trend is low-relevance but current
  signals indicate a shift, Trend Intelligence reports both — the
  new signals and the historical context.
- Learning Memory does not prevent Trend Intelligence from detecting
  new patterns that contradict past experience.

---

# 13. Trend Lifecycle

## 13.1. Overview

A trend passes through a defined lifecycle within LOOPRA — from first
detection through to performance feedback that improves future
detection.

## 13.2. Lifecycle Stages

```text
Stage 1 — Detection
    Signal is observed and processed through the Signal Processing Pipeline.
    Output: MarketSignal (classified, preliminary relevance assessment).

Stage 2 — Validation
    Signal is evaluated against detection factors (persistence, growth,
    adoption, engagement, relevance).
    Related signals are grouped.
    Output: confirmed or rejected as a trend.

Stage 3 — Pattern Formation
    Validated trends are abstracted into structured patterns.
    Output: TrendPattern with description, evidence, affected audience,
    related formats and confidence.

Stage 4 — Opportunity
    TrendPattern is evaluated for brand-specific relevance.
    Relevance Score is calculated.
    Output: opportunity assessment delivered to Orchestrator Agent.

Stage 5 — Performance Feedback
    If the Orchestrator acts on the trend and content is produced,
    performance data is collected.
    The relationship between the trend prediction and actual performance
    is analyzed.

Stage 6 — Learning Update
    Outcome is stored in Learning Memory.
    Trend Intelligence's detection accuracy and relevance assessment are
    calibrated based on results.
    Future similar signals are evaluated with improved context.
```

## 13.3. Closed Loop

The trend lifecycle forms a closed learning loop:

```text
Detection → Validation → Pattern → Opportunity → Feedback → Learning
    ↑                                                          │
    └──────────────────────────────────────────────────────────┘
                    Improved next detection
```

Each completed cycle improves Trend Intelligence's ability to:

- detect meaningful signals faster;
- filter noise more effectively;
- assess relevance more accurately;
- predict opportunity potential with greater confidence.

---

# 14. Foundation MVP Relationship

## 14.1. Current State

The Foundation MVP does NOT contain Trend Intelligence.

In the current Foundation MVP:

```text
Human creates Idea
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

Content ideas originate from human input. There is no automated
market signal analysis, trend detection or opportunity discovery.

Reference: `MVP_SCOPE.md`

## 14.2. Future Integration

When Trend Intelligence is activated:

```text
Current:                          Future:

Human creates Idea                MarketSignal
                                       ↓
                                  Trend Intelligence
                                       ↓
                                  Content Opportunity
                                       ↓
                                  Orchestrator Agent Decision
                                       ↓
                                  Idea (source: intelligence,
                                        not manual input)
                                       ↓
                                  Scenario → ContentItem → ...
```

The Foundation MVP pipeline (Idea → Scenario → ContentItem →
ExportPackage → Publication → MetricSnapshot) remains the execution
backbone.

What changes is the **source of the Idea**. Instead of human manual
definition, Ideas emerge from Trend Intelligence analysis, evaluated
by the Orchestrator Agent and shaped by Brand System context.

## 14.3. What Stays

The Foundation MVP entities persist as the reliable production
layer:

- `Idea` — the creative concept (source evolves from manual to
  intelligence-driven);
- `Scenario` — the content plan;
- `ContentItem` — the produced content unit;
- `ExportPackage` — the prepared distribution package;
- `Publication` — the publication record;
- `MetricSnapshot` — the performance data record.

Trend Intelligence adds the layer **before** Idea creation. It does not
replace the Foundation MVP pipeline.

## 14.4. Evolution Path

```text
Foundation MVP (current)
    Manual Idea creation
    Deterministic pipeline
    No trend analysis
        ↓
Content Intelligence (next phase)
    Trend Intelligence activated
    Automatic signal analysis
    Pattern detection
    Opportunity generation
    Source of Ideas becomes partially automated
        ↓
Agentic Operations
    Full Orchestrator integration
    Autonomous opportunity discovery
    Learning Memory feedback loop
        ↓
Marketing Operating System
    Continuous autonomous trend detection
    Self-improving market intelligence
```

Reference: `LOOPRA_ARCHITECTURE.md`, Section 2

---

# 15. Future Implementation Considerations

## 15.1. Overview

This section describes conceptual directions for Trend Intelligence
implementation. It does not specify implementation details,
technologies or timelines.

These directions represent the architectural vision for how Trend
Intelligence capabilities may evolve.

## 15.2. Multi-Source Data Collection

Future Trend Intelligence will collect signals from diverse sources
simultaneously:

- social media platforms — conversation monitoring, engagement pattern
  tracking;
- search engines — query trend analysis, demand shift detection;
- competitor channels — content strategy observation, format adoption
  tracking;
- industry publications and news — market movement detection;
- internal performance data — pattern extraction from own content
  results.

Collection will be continuous, not periodic. The system will maintain
a live understanding of the market environment.

## 15.3. Semantic Analysis

Beyond keyword and volume tracking, Trend Intelligence will perform
semantic analysis:

- understanding the meaning behind surface-level trends;
- identifying relationships between seemingly unrelated topics;
- detecting narrative shifts — how the story around a topic is
  changing;
- recognizing emerging audience needs before they are explicitly
  expressed.

## 15.4. Trend Forecasting

Based on historical patterns and current signals, Trend Intelligence
will project trend trajectories:

- which emerging signals are likely to become significant trends;
- when a mature trend is likely to peak and decline;
- which audience segments will adopt a trend next;
- timing recommendations for content publication relative to trend
  lifecycle.

## 15.5. Audience Clustering

Trend Intelligence will segment audiences based on trend response
patterns:

- identifying which audience segments are early adopters of specific
  trends;
- detecting which segments respond to which content formats and topics;
- mapping audience migration patterns across platforms and interests;
- enabling precise targeting of content opportunities to responsive
  segments.

## 15.6. Competitive Intelligence

Trend Intelligence will build structured competitive understanding:

- tracking competitor content strategy evolution over time;
- identifying competitor strengths and content gaps;
- detecting when competitors are responding to the same market signals;
- discovering uncontested content spaces — topics and formats that
  competitors are not addressing but audiences want.

## 15.7. Automated Opportunity Discovery

The ultimate capability: from signal to opportunity without manual
intervention.

```text
MarketSignal detected
    ↓  automatic processing
Trend confirmed
    ↓  automatic relevance evaluation
Brand-specific opportunity identified
    ↓  automatic delivery
Orchestrator Agent receives structured opportunity with evidence
and confidence
```

The human and Orchestrator retain decision authority. Trend
Intelligence automates the discovery process but does not automate the
decision to act.

## 15.8. Continuous Learning Calibration

Trend Intelligence will calibrate its detection and evaluation models
based on outcomes:

- comparing predicted opportunity potential with actual content
  performance;
- adjusting relevance scoring weights based on what proved valuable;
- improving signal-to-noise ratio by learning which signals matter;
- building brand-specific intelligence that improves with every cycle.

---

# 16. Related Documents

## 16.1. Core Architecture

```text
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
```

## 16.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
docs/00_foundation/MVP_SCOPE.md                     — Foundation MVP scope
```

## 16.3. Product Layer

```text
docs/01_product/LOOPRA_BRAND_POSITIONING.md         — LOOPRA product identity
docs/01_product/USER_WORKFLOWS.md                   — User interaction model
```

## 16.4. Intelligence Layer

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Content Cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Agent System specification
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — This document
```

## 16.5. Future Documents

```text
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content insight specification
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory specification
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
| Layer | Intelligence Layer — Trend Intelligence Specification |

---

# Final Statement

Trend Intelligence is the sensory system of LOOPRA.

Before any content idea exists, before any production begins, before
any strategic decision is made — Trend Intelligence establishes what
is happening in the world and why it matters for this specific brand.

It transforms the external environment from noise into structured
knowledge:

```text
Raw signals
    ↓
MarketSignals — structured observations of change
    ↓
TrendPatterns — confirmed behavioural patterns
    ↓
Relevance Scores — brand-specific importance assessments
    ↓
Orchestrator Agent receives knowledge to inform decisions
```

Trend Intelligence does not create content. It does not make
strategic decisions. It does not replace human judgment.

It provides the market understanding that makes intelligent content
decisions possible.

Without Trend Intelligence, LOOPRA would create content based on
guesswork. With Trend Intelligence, LOOPRA creates content based on
verified market understanding — filtered through brand context,
grounded in evidence and continuously improved through learning.

This is the foundation of autonomous marketing intelligence.

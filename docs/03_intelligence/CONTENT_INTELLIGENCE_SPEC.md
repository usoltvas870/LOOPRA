# CONTENT INTELLIGENCE SPEC

## Version

v1.0

## Status

Active — LOOPRA Intelligence Layer

## Purpose

This document defines the functional architecture of the Content
Intelligence Module — the strategic content selection and planning layer
of the LOOPRA Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA transform market understanding, brand context and
> accumulated experience into concrete content decisions?

CONTENT_INTELLIGENCE_SPEC.md is the functional specification for the
module that bridges Trend Intelligence (market understanding) with the
Orchestrator Agent (strategic decisions) and ultimately Content Creation.

It describes:

- analysis of content opportunities;
- connection between trends and brand;
- format selection logic;
- formation of content ideas;
- creation of strategic recommendations.

It does NOT describe:

- text generation;
- image generation;
- video generation;
- rendering;
- publishing;
- specific AI models or prompts;
- API contracts or database schemas.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

CONTENT_INTELLIGENCE_SPEC.md defines the functional model of intelligent
content selection and planning within LOOPRA.

It serves as the specification for how LOOPRA:

- analyzes content opportunities from market signals and trend patterns;
- evaluates opportunities through the lens of Brand System;
- selects appropriate content formats for specific goals and audiences;
- forms structured content ideas ready for strategic decision;
- creates recommendations with confidence scoring and evidence.

## 1.2. Scope

This document covers:

- the role of Content Intelligence in the LOOPRA Content Cycle;
- the Content Opportunity entity and its structure;
- the Content Opportunity generation pipeline from trend to recommendation;
- audience-centric content planning principles;
- goal-based content selection logic;
- content format recommendation criteria;
- content angle selection logic;
- relationship with Orchestrator Agent, Trend Intelligence and Learning Memory;
- relationship with the Foundation MVP pipeline.

## 1.3. Out of Scope

This document does not cover:

- content generation, rendering or production;
- specific AI model selection, prompts or providers;
- API contracts between system components;
- database schemas for opportunity or recommendation storage;
- publishing, distribution or channel mechanics;
- UI components for opportunity visualization.

---

# 2. Role of Content Intelligence in LOOPRA

## 2.1. Position in the Content Cycle

Content Intelligence operates at Stage 3 of the LOOPRA Content Cycle:

```text
Market Signal Discovery (Stage 1)
    ↓
Trend Understanding (Stage 2)
    ↓
Content Opportunity Creation (Stage 3)  ← Content Intelligence
    ↓
Strategic Decision (Stage 4)
    ↓
Content Creation (Stage 5)
```

Reference: `CONTENT_CYCLE_SPEC.md`, Sections 4–6

## 2.2. Position in the System Architecture

Within the LOOPRA system:

```text
Trend Intelligence
    ↓
    "What is happening in the market?"
    ↓
Content Intelligence
    ↓
    "What content should we create because of it?"
    ↓
Content Opportunity
    ↓
Orchestrator Agent
    ↓
    "Which opportunities should we pursue?"
    ↓
Decision
```

Reference: `SYSTEM_ARCHITECTURE.md`, Section 7

## 2.3. The Critical Transition

Content Intelligence is responsible for the transition from:

> "We understand the market."

to:

> "We know which content makes sense to create."

Trend Intelligence answers: "What is happening?"

Content Intelligence answers: "What should we create because of it?"

## 2.4. What Content Intelligence Does

Content Intelligence:

- receives TrendPatterns from Trend Intelligence;
- combines trend data with Brand System context;
- analyzes audience segments against trend relevance;
- matches content possibilities to business goals;
- recommends content formats based on strategy and evidence;
- selects content angles aligned with brand positioning;
- forms structured Content Opportunities with confidence scoring;
- incorporates Learning Memory to strengthen recommendations.

## 2.5. What Content Intelligence Does NOT Do

Content Intelligence does NOT:

- produce content (text, images, video);
- render or assemble content assets;
- publish or distribute content;
- make strategic decisions about which opportunities to pursue;
- replace the Orchestrator Agent;
- replace the Production Layer;
- override Brand System restrictions or identity.

These responsibilities belong respectively to Production Tools, Publishing,
the Orchestrator Agent and the Human Operator.

## 2.6. Intelligence Module Role

As an Intelligence Module within the LOOPRA Agent System, Content
Intelligence follows the module principles:

- **Single responsibility** — answers the question: "What content has
  strategic potential given who we are and what is happening?"
- **No independent action** — Content Intelligence analyzes and recommends;
  the Orchestrator decides.
- **Structured output** — returns typed entities (Content Opportunities)
  the Orchestrator can reason about.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.2

---

# 3. Core Principles

## 3.1. Context Before Creation

LOOPRA does not begin with content generation.

Content Intelligence does not ask:

> "What should we write about?"

Content Intelligence first analyzes:

- **Brand System** — who the brand is, how it communicates, what it stands for;
- **Audience** — who the content is for, what they need, how they consume;
- **Goals** — why content is being created, what it should achieve;
- **Trends** — what is happening in the market that creates opportunity;
- **Learning Memory** — what has worked before and what has not.

Only after this contextual analysis does Content Intelligence form
recommendations about what content has strategic potential.

Content creation begins with understanding. Understanding begins with
context.

Reference: `BRAND_SYSTEM_SPEC.md`

## 3.2. Content Is a Strategic Decision

Content is not simply a format choice or a topic selection.

Every content unit must have a defined strategic purpose:

- **Goal** — what business objective does this content serve?
- **Audience** — which segment is this content for?
- **Message** — what key takeaway should the audience receive?
- **Expected Outcome** — what result should this content produce?

Content Intelligence does not create content for its own sake. Every
recommendation is grounded in strategic intent.

A content piece without purpose is noise. Content Intelligence exists
to ensure every recommendation has strategic foundation.

## 3.3. One Trend Can Create Multiple Content Directions

A single market trend does not produce a single content idea.

The same trend can manifest in multiple content directions, each serving
a different goal, audience or strategic intent.

Example:

```text
Trend:
"Growing interest in AI productivity among entrepreneurs."

Brand:
AI education platform for business owners.

Possible Directions:

Education:
    "5 AI tools every entrepreneur should know in 2026"
    Goal: awareness, authority
    Audience: beginners
    Format: carousel

Storytelling:
    "How one founder replaced 20 hours of manual work with AI workflows"
    Goal: engagement, emotional connection
    Audience: sceptics considering adoption
    Format: short video

Comparison:
    "Manual workflow vs AI-assisted workflow: side by side comparison"
    Goal: lead generation, demonstration
    Audience: evaluators comparing options
    Format: carousel or short video

Opinion:
    "Why most entrepreneurs use AI wrong — and what to do instead"
    Goal: thought leadership, differentiation
    Audience: experienced users seeking advanced insight
    Format: text post

Case Study:
    "From zero to automated: 30-day AI integration journey"
    Goal: conversion, trust building
    Audience: prospects near decision
    Format: video series or multi-post carousel
```

The direction chosen depends on brand strategy, active goals, target
audience segment and current priorities.

Content Intelligence evaluates all possible directions and recommends
the most strategically valuable path.

---

# 4. Content Intelligence Inputs

## 4.1. Overview

Content Intelligence does not generate recommendations from a blank slate.

It synthesizes multiple structured inputs to form coherent, strategic
content opportunities.

## 4.2. Brand Context

From the Brand System, Content Intelligence receives:

| Input | Source | How Used |
|---|---|---|
| Brand positioning | Brand Identity | Determines what messages align with brand perception |
| Brand values | Brand Identity | Filters content directions that fit brand principles |
| Audience segments | Audience Intelligence | Identifies who the content targets and what they need |
| Audience pain points | Audience Intelligence | Surfaces problems content should address |
| Tone of voice | Communication System | Guides how messages should be expressed |
| Allowed and forbidden formulations | Communication System | Filters what can and cannot be said |
| Content pillars | Content Strategy | Organizes content opportunities by strategic theme |
| Preferred formats | Content Strategy | Constrains format recommendations to brand preferences |
| Publishing goals | Content Strategy | Aligns recommendations with publishing capacity |
| Restrictions | Safety Rules | Eliminates directions that violate brand boundaries |

Reference: `BRAND_SYSTEM_SPEC.md`

## 4.3. Market Understanding

From Trend Intelligence, Content Intelligence receives:

| Input | Source | How Used |
|---|---|---|
| MarketSignals | Trend Intelligence | Raw observations of external change |
| TrendPatterns | Trend Intelligence | Confirmed patterns of market behaviour |
| Relevance scores | Trend Intelligence | Brand-specific importance of each trend |
| Affected audiences | TrendPattern | Which audience segments a trend involves |
| Related formats | TrendPattern | Which content formats a trend connects to |
| Confidence levels | TrendPattern | How well-supported each pattern is |

Reference: `TREND_INTELLIGENCE_SPEC.md`

## 4.4. Business Context

From Project Settings, Content Intelligence receives:

| Input | Source | How Used |
|---|---|---|
| Active goals | Project Settings | Determines what content should achieve |
| Goal priorities | Project Settings | Prioritizes content that serves high-priority goals |
| Enabled channels | Project Settings | Constrains format recommendations by channel availability |
| Content type configuration | Project Settings | Defines which content types can be recommended |

Reference: `PROJECT_SETTINGS_SPEC.md`

## 4.5. Historical Experience

From Learning Memory, Content Intelligence receives:

| Input | Source | How Used |
|---|---|---|
| Successful format patterns | Learning Memory | Increases confidence in format recommendations with proven results |
| Failed experiments | Learning Memory | Decreases or eliminates recommendations that proved ineffective |
| Audience response patterns | Learning Memory | Calibrates audience targeting based on past engagement |
| Goal-format effectiveness | Learning Memory | Maps which formats reliably serve which goals |
| Topic resonance history | Learning Memory | Indicates which themes have historically performed well |

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.6 — Learning Memory Module

## 4.6. Input Integration

Content Intelligence integrates these four input categories into a
unified analysis:

```text
Brand Context       →  "Who we are and who we speak to"
    +
Market Understanding →  "What is happening and why it matters"
    +
Business Context    →  "What we need to achieve"
    +
Historical Experience →  "What we know works"
    =
Content Opportunity
```

No single input dominates. The value of Content Intelligence is in the
synthesis — understanding the intersection of brand, market, goals
and experience.

---

# 5. Content Opportunity Entity

## 5.1. Definition

A **Content Opportunity** is a structured, intelligence-backed description
of a potentially successful content direction.

It is the primary output entity of Content Intelligence and the primary
input entity for the Orchestrator Agent's strategic decisions.

A Content Opportunity is NOT a content brief, a content draft or a
production instruction. It is a strategic recommendation grounded in
brand context, market understanding and historical evidence.

## 5.2. Purpose

Content Opportunity serves as:

- a bridge between market understanding and content creation;
- a structured decision input for the Orchestrator Agent;
- a record of why a particular content direction was considered;
- a learnable entity — outcomes can be traced back to the opportunity
  that generated them.

## 5.3. Entity Structure

| Field | Description |
|---|---|
| `related_trend` | Reference to the TrendPattern that inspired this opportunity |
| `audience_segment` | Which audience segment this content targets |
| `business_goal` | Which marketing goal this content serves |
| `content_objective` | What this specific content piece should achieve |
| `key_message` | The core message or takeaway for the audience |
| `recommended_formats` | Content formats that best deliver this message |
| `recommended_channels` | Distribution channels most suitable for this content |
| `content_pillar` | Strategic pillar this opportunity belongs to |
| `expected_outcome` | Predicted result based on evidence and past patterns |
| `confidence_score` | How certain Content Intelligence is about this opportunity |
| `evidence` | Summary of data and reasoning supporting the recommendation |

## 5.4. Confidence Scoring

Confidence is derived from the strength and alignment of inputs:

| Confidence Level | Conditions |
|---|---|
| **High** | Strong trend evidence + clear brand alignment + supported by Learning Memory + serves high-priority goal |
| **Medium** | Moderate trend evidence or partial brand alignment or limited Learning Memory support |
| **Low** | Weak trend evidence or uncertain brand alignment or no historical validation |

Confidence influences how the Orchestrator Agent treats the opportunity
and whether it requires human review.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 7 — Confidence and Escalation

## 5.5. Example

```text
Content Opportunity:

    related_trend: TrendPattern — "Growing interest in AI automation
                   among small business owners."

    audience_segment: small_business_owners — founders with 1-10
                      employees seeking operational efficiency.

    business_goal: awareness — increase visibility among entrepreneur
                   audience.

    content_objective: educate — introduce AI automation as a practical,
                       accessible solution for small business owners.

    key_message: "AI automation is not only for enterprises. Small
                 businesses can adopt practical AI tools today to save
                 time and focus on growth."

    recommended_formats:
        - short_video_reel (primary — reach, discovery, emotional)
        - carousel (secondary — saves, structured explanation)

    recommended_channels:
        - instagram (primary — visual, discovery)
        - linkedin (secondary — professional context)

    content_pillar: expertise — demonstrating knowledge and practical
                    guidance.

    expected_outcome: increased reach among entrepreneur audience;
                      engagement through saved/revisited content;
                      authority positioning in the AI-for-business space.

    confidence_score: high

    evidence: trend supported by 47 signals over 8 weeks; brand
              positioning as practical AI educators aligns perfectly;
              Learning Memory indicates short-form educational video
              outperforms static posts 2.5x for this audience.
```

## 5.6. Relationship to Other Entities

```text
MarketSignal (multiple, confirmed)
    ↓
TrendPattern (from Trend Intelligence)
    ↓
    + Brand System
    + Project Settings
    + Learning Memory
    ↓
Content Opportunity (from Content Intelligence)
    ↓
    evaluated by Orchestrator Agent
    ↓
Content Decision (create / defer / experiment / decline)
    ↓
Idea (creative concept, Foundation MVP pipeline entry point)
```

---

# 6. Content Opportunity Generation Pipeline

## 6.1. Overview

Content Intelligence transforms a TrendPattern into a Content Opportunity
through a structured multi-stage pipeline.

Each stage applies a specific analytical lens, progressively building
the opportunity from market observation to strategic recommendation.

## 6.2. Pipeline Stages

```text
TrendPattern
    ↓
Stage 1 — Brand Alignment
    ↓
Stage 2 — Audience Analysis
    ↓
Stage 3 — Goal Matching
    ↓
Stage 4 — Content Direction Formation
    ↓
Stage 5 — Evidence and Confidence
    ↓
Content Opportunity
```

## 6.3. Stage 1 — Brand Alignment

**Purpose:** Determine whether the trend is compatible with the brand's
identity, values and communication style.

**Questions Answered:**
- Does this trend align with our brand positioning?
- Does it fit our brand values?
- Is our tone of voice appropriate for this topic?
- Does this trend touch any restricted topics or forbidden claims?

**Process:**
- Trend is compared against Brand Identity, Communication System and
  Restrictions.
- Trends that conflict with brand restrictions are eliminated regardless
  of popularity.
- Trends that strongly align with brand positioning receive higher
  relevance weight.

**Output:** Brand-compatible trend with alignment score.

## 6.4. Stage 2 — Audience Analysis

**Purpose:** Determine which audience segments the trend affects and how
they would receive content on this topic.

**Questions Answered:**
- Which of our defined audience segments does this trend involve?
- What pain points of this audience does the trend address?
- What motivations does this trend connect to?
- What is the audience's awareness level for this topic?
- How does this audience prefer to consume content?

**Process:**
- Trend is cross-referenced with Audience Intelligence from Brand System.
- Each potentially relevant audience segment is evaluated.
- Audience readiness level is assessed (unaware → problem-aware →
  solution-aware → product-aware).

**Output:** Prioritized audience segments with consumption preferences.

## 6.5. Stage 3 — Goal Matching

**Purpose:** Determine which business goals the potential content would
serve and with what priority.

**Questions Answered:**
- Which active marketing goals does this content direction support?
- What is the priority of those goals?
- What content objectives would serve these goals?
- How would success be measured?

**Process:**
- Content possibilities are mapped to active goals from Project Settings.
- Goals with higher priority receive stronger recommendation weight.
- Content objective type is selected (educate, inspire, entertain,
  convert, retain) based on the goal.

**Output:** Goal-matched content direction with prioritized objectives.

## 6.6. Stage 4 — Content Direction Formation

**Purpose:** Form the concrete content direction — topic, format, channel,
angle and message.

**Questions Answered:**
- What specific topic within this trend has the most potential?
- Which content format best serves the goal and audience?
- Which channel is most appropriate?
- What angle should the content take?
- What is the core message?

**Process:**
- Topic is selected from the intersection of trend, brand expertise and
  audience interest.
- Format is selected based on goal-audience-format fit (see Section 9).
- Channel is selected based on audience presence and format compatibility.
- Angle is selected based on goal and audience awareness level (see
  Section 10).
- Key message is formulated from brand voice, goal and audience need.

**Output:** Concrete content direction with format, channel, angle and
message.

## 6.7. Stage 5 — Evidence and Confidence

**Purpose:** Ground the recommendation in evidence and assign a
confidence score.

**Questions Answered:**
- What evidence supports this recommendation?
- What does Learning Memory say about similar content?
- How confident are we that this content will achieve its objective?

**Process:**
- Trend evidence is summarized (number of signals, duration, sources).
- Learning Memory is queried for similar past content (format, topic,
  audience, goal).
- Past successes increase confidence; past failures decrease it.
- Overall confidence score is assigned.

**Output:** Evidence summary and confidence score attached to the
Content Opportunity.

## 6.8. Pipeline Integration

```text
TrendPattern → Brand Alignment → Audience Analysis → Goal Matching
→ Content Direction → Evidence & Confidence → Content Opportunity
```

Each stage enriches the opportunity. If any stage identifies a blocker
(incompatible brand alignment, no relevant audience, no matching goal),
the opportunity is deprioritized or eliminated.

The pipeline does not produce opportunities that do not pass all stages.
Content Intelligence does not recommend content that is incompatible
with the brand, irrelevant to the audience or disconnected from goals.

---

# 7. Audience-Centric Content Planning

## 7.1. The Central Question

Content Intelligence always answers the question:

> "Who is this content for?"

Before asking what to create or how to create it, Content Intelligence
establishes who the audience is and what they need.

## 7.2. Audience Analysis Dimensions

For each potential content direction, Content Intelligence analyzes the
target audience along these dimensions:

### Audience Segment
- Which defined audience segment does this content target?
- Is this a primary or secondary segment for the brand?
- What is the size and strategic importance of this segment?

### Pain Points
- What frustrations or problems does this audience experience?
- Which of these problems can this content address?
- How urgent is this problem for the audience?

### Motivations
- What drives this audience to take action?
- What outcomes do they desire?
- What values do they hold?

### Awareness Level
- Is the audience unaware of the problem?
- Are they problem-aware but not solution-aware?
- Are they solution-aware but not product-aware?
- Are they product-aware and evaluating options?

Awareness level fundamentally changes the content approach.

### Preferred Formats
- How does this segment prefer to consume information?
- Which platforms do they use?
- When and how do they engage with content?

## 7.3. One Topic, Different Audiences

The same topic serves different audiences differently:

```text
Topic: "AI tools for business"

For Beginner audience (unaware or problem-aware):
    Content objective: awareness, education
    Key message: "AI tools exist and can help your business."
    Angle: educational — "What is AI automation and why it matters."
    Format: short video (discovery), carousel (explanation)
    Tone: simple, encouraging, non-technical

For Intermediate audience (solution-aware):
    Content objective: consideration, engagement
    Key message: "Here is how to evaluate and choose AI tools."
    Angle: comparison — "Top 5 AI tools for small business compared."
    Format: carousel (structured comparison), text post (detailed analysis)
    Tone: practical, analytical, specific

For Advanced audience (product-aware):
    Content objective: conversion, retention
    Key message: "Advanced techniques to maximize AI tool value."
    Angle: deep expertise — "Building multi-step AI workflows."
    Format: video series (demonstration), case study (proof)
    Tone: expert, detailed, actionable
```

Content Intelligence evaluates which audience segment and awareness
level is most strategically valuable given current brand priorities.

## 7.4. Audience-Pillar Mapping

Audience segments map to content pillars:

```text
Audience: Beginners
    → Pillar: education — introducing concepts, building awareness
    → Pillar: community — welcoming, inclusive content

Audience: Intermediate users
    → Pillar: expertise — deepening knowledge, practical application
    → Pillar: storytelling — case studies, transformations

Audience: Advanced users
    → Pillar: expertise — advanced techniques, thought leadership
    → Pillar: product — demonstrating sophisticated use cases
```

Content Intelligence ensures that recommended opportunities serve
the right audience through the right pillar.

---

# 8. Goal-Based Content Selection

## 8.1. Goals Drive Content Decisions

Content Intelligence does not recommend content in a vacuum.

Every Content Opportunity is evaluated against the brand's active
business goals. Content that does not serve an active goal is
deprioritized regardless of trend popularity or audience size.

## 8.2. Goal-to-Content Mapping

Different business goals require fundamentally different content
approaches:

### Awareness

```text
Goal: Reach new audiences. Increase visibility.

Content approach:
    - Educational content that introduces concepts
    - Reach-optimized formats (short video, carousel)
    - Broad topics that attract new audience segments
    - Discovery-focused angles (overview, introduction, beginner guides)
    - High-volume, consistent publishing

Content objective: Educate and introduce.
CTA approach: Soft or none. Focus on providing value first.
```

### Engagement

```text
Goal: Deepen audience interaction and loyalty.

Content approach:
    - Conversation-starting content
    - Interactive formats that invite response
    - Storytelling and personal connection angles
    - Content that builds community around shared interests
    - Response-driven topics (questions, opinions, shared experiences)

Content objective: Connect and involve.
CTA approach: Ask questions. Invite comments. Start discussions.
```

### Lead Generation

```text
Goal: Generate qualified interest and inquiries.

Content approach:
    - Problem-solving content that demonstrates value
    - Educational carousels with clear, actionable value
    - Case studies and proof content that builds trust
    - Direct CTA inviting the next step
    - Value-first content with logical CTA progression

Content objective: Demonstrate value and convert interest.
CTA approach: Direct but value-anchored. "Learn more", "Try this".
```

### Sales

```text
Goal: Drive conversions and revenue.

Content approach:
    - Product and offer presentation
    - Comparison content (before/after, with/without)
    - Social proof and testimonials
    - Limited-time or exclusive content
    - Direct conversion-oriented messaging

Content objective: Convert intent into action.
CTA approach: Direct. "Buy now", "Get started", "Join today".
```

### Retention

```text
Goal: Maintain existing customer relationships.

Content approach:
    - Relationship-building content
    - Advanced usage tips and techniques
    - Community and belonging content
    - Exclusive content for existing customers
    - Soft, appreciative communication

Content objective: Reinforce value and belonging.
CTA approach: Soft. "Stay connected", "Share your experience".
```

## 8.3. Goal Priority Weighting

Goals have priorities (high, medium, low) defined in Project Settings.

Content Intelligence weights opportunities accordingly:

```text
High-priority goal    →  opportunities serving this goal receive
                         stronger recommendation weight.

Medium-priority goal  →  opportunities serving this goal are considered
                         but do not override high-priority opportunities.

Low-priority goal     →  opportunities serving this goal are
                         deprioritized unless no higher-priority
                         opportunities are available.
```

Goals are defined in Project Settings. Priorities are stable but may be
adjusted by the human operator as business context evolves.

Reference: `PROJECT_SETTINGS_SPEC.md`, Section 4

## 8.4. Goals vs Content Objectives

Content Intelligence distinguishes between two levels of purpose:

```text
Marketing Goals (business level):
    "Why does the brand create content?"
    Defined in Project Settings.
    Stable and long-term.
    Examples: awareness, engagement, lead generation, sales, retention.

Content Objectives (tactical level):
    "What should this specific content piece achieve?"
    Defined per Content Opportunity.
    Changes per cycle and per content item.
    Examples: educate, inspire, entertain, demonstrate, convert, retain.
```

Marketing goals provide strategic direction.

Content objectives provide tactical focus per opportunity.

---

# 9. Content Format Recommendation

## 9.1. Content Intelligence Does Not Create Formats

Content Intelligence does NOT:
- generate content in any format;
- render visual assets;
- produce video;
- write text;
- assemble content items.

Content Intelligence recommends which format the Production Layer
should create and why.

The Production Layer executes the format decision.

## 9.2. Format Selection Criteria

For each Content Opportunity, Content Intelligence evaluates formats
against multiple criteria:

### Goal Fit
Which format best serves the content's objective?

| Format | Effective For |
|---|---|
| Short video | Reach, discovery, emotional impact, demonstration |
| Carousel | Education, structured explanation, saves, revisit |
| Text post | Authority, thought leadership, depth, discussion |
| Image | Visual attention, quick communication, brand presence |
| Educational carousel | Deep education, step-by-step explanation, value demonstration |
| Case study / story | Trust building, proof, emotional connection |

### Audience Fit
Which format does the target audience prefer?

Content Intelligence references audience communication preferences
defined in Brand System Audience Intelligence.

### Channel Fit
Which format works on the target channel?

Content Intelligence references channel configuration from Project
Settings to verify format compatibility.

### Performance Evidence
Which format has historically performed well for similar content?

Content Intelligence queries Learning Memory:
- Has this format worked for this audience before?
- Has this format worked for this goal before?
- Has this format worked for this content pillar before?

### Brand Preferences
Which format does the brand prefer?

Content Intelligence references preferred formats from the Brand System
Content Strategy layer.

## 9.3. Format Recommendation Logic

```text
Format Recommendation:

    Goal → "What are we trying to achieve?"
        +
    Audience → "How does this segment consume content?"
        +
    Channel → "What works on this platform?"
        +
    Evidence → "What has worked before?"
        +
    Brand → "What does the brand prefer?"
        =
    Recommended Format with ranking and reasoning.
```

## 9.4. Primary and Secondary Formats

Content Intelligence may recommend multiple formats for a single
opportunity, distinguishing between:

- **Primary format** — the main recommended format with the highest
  predicted effectiveness.
- **Secondary formats** — alternative formats that also fit the
  opportunity with supporting rationale.

The Orchestrator Agent may select the primary format or choose a
secondary format based on resource availability, experiment design
or other operational factors.

## 9.5. Format Examples

### Short Video

```text
Recommended when:
    - Goal is awareness, reach or emotional connection
    - Audience prefers visual, fast-consumption content
    - Channel supports video (Instagram, TikTok, YouTube Shorts)
    - Evidence supports video for this goal and audience
    - Content angle benefits from demonstration or visual storytelling
```

### Carousel

```text
Recommended when:
    - Goal is education, lead generation or saves
    - Audience values structured, revisitable content
    - Channel supports multi-slide posts (Instagram, LinkedIn)
    - Evidence supports carousel for this content type
    - Content has multiple steps, points or comparisons to present
```

### Text Post

```text
Recommended when:
    - Goal is authority, thought leadership or discussion
    - Audience prefers reading and engaging with ideas
    - Channel supports long-form text (Telegram, LinkedIn, Threads)
    - Evidence supports text for this goal and audience
    - Content angle benefits from depth and nuance
```

### Image

```text
Recommended when:
    - Goal is visual attention or brand presence
    - Audience engages with visual-first content
    - Channel supports image posts
    - Content message is simple and visually communicable
    - Supplemental to other content types
```

### Educational Carousel

```text
Recommended when:
    - Goal is deep education or lead generation
    - Audience seeks practical, actionable learning
    - Channel supports carousel format
    - Content has clear step-by-step structure
    - Evidence supports educational format for this goal and audience
```

---

# 10. Content Angle Selection

## 10.1. Definition

A content angle is the specific perspective, framing or approach through
which a topic is presented.

The same topic can be addressed through multiple angles, each serving a
different strategic purpose.

Content Intelligence selects the most strategically appropriate angle
for each Content Opportunity.

## 10.2. Angle Types

### Educational Angle

```text
Approach:    "How it works" — explain, teach, demonstrate.
Purpose:     Build awareness, establish authority, educate audience.
Best for:    Awareness and lead generation goals.
             Audiences at problem-aware or solution-aware stages.
Example:     "How AI automation can save 10 hours per week."
```

### Storytelling Angle

```text
Approach:    "Someone's experience" — narrative, personal, emotional.
Purpose:     Build connection, engagement, trust and relatability.
Best for:    Engagement and retention goals.
             Audiences at any awareness level.
Example:     "How a small business owner transformed operations with AI."
```

### Problem/Solution Angle

```text
Approach:    "Why current approach fails and what to do instead."
Purpose:     Generate leads, demonstrate value, create urgency.
Best for:    Lead generation and sales goals.
             Audiences at solution-aware or product-aware stages.
Example:     "Manual reporting wastes 5 hours a week. Here is the fix."
```

### Opinion Angle

```text
Approach:    "Why the market is changing" — perspective, analysis, stance.
Purpose:     Establish thought leadership, differentiate brand, spark
             discussion.
Best for:    Authority building and engagement goals.
             Audiences at solution-aware or product-aware stages.
Example:     "Why most AI adoption advice is wrong for small business."
```

### Comparison Angle

```text
Approach:    "Old vs new" or "Option A vs Option B."
Purpose:     Aid evaluation, demonstrate superiority, reduce uncertainty.
Best for:    Lead generation and sales goals.
             Audiences at product-aware stage comparing options.
Example:     "Manual workflow vs AI workflow — side by side comparison."
```

### Case Study Angle

```text
Approach:    "Real example with results" — evidence, data, proof.
Purpose:     Build trust, provide social proof, convert sceptics.
Best for:    Sales and conversion goals.
             Audiences near decision.
Example:     "How Company X increased output by 40% with AI workflows."
```

### Behind the Scenes Angle

```text
Approach:    "How we do things" — process, transparency, authenticity.
Purpose:     Build connection, humanize brand, deepen trust.
Best for:    Engagement and retention goals.
             Existing audience and community.
Example:     "How we research, test and select AI tools for our content."
```

## 10.3. Angle Selection Factors

Content Intelligence selects the angle based on:

| Factor | Question Answered |
|---|---|
| Business Goal | Which angle best serves the active marketing goal? |
| Audience Awareness Level | How prepared is the audience for this angle? |
| Brand Tone of Voice | Which angle is compatible with how the brand communicates? |
| Content Pillar | Which angle fits the strategic content pillar? |
| Learning Memory | Which angles have performed well for similar content? |

## 10.4. Angle-Audience Compatibility

```text
Unaware audience:
    → Educational angle (introduce the problem and concept)
    → Storytelling angle (create emotional connection to the topic)

Problem-aware audience:
    → Educational angle (explain the solution space)
    → Problem/Solution angle (contrast current state with alternative)

Solution-aware audience:
    → Comparison angle (help evaluate options)
    → Opinion angle (provide perspective on choices)

Product-aware audience:
    → Case Study angle (provide proof and social validation)
    → Comparison angle (differentiate from alternatives)
```

Content Intelligence applies the angle that matches the audience's
readiness to receive the message, not the angle that is most convenient
to produce.

---

# 11. Relationship with Orchestrator Agent

## 11.1. Provider-Consumer Relationship

Content Intelligence is a provider. The Orchestrator Agent is the
consumer.

Content Intelligence provides:

- **Content Opportunities** — structured, evidence-backed content
  directions;
- **Confidence Scores** — how certain Content Intelligence is about each
  recommendation;
- **Reasoning** — why each recommendation was made, with evidence.

The Orchestrator Agent consumes these outputs to answer:

> "Given what Content Intelligence has identified, which opportunities
> should we pursue?"

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.4

## 11.2. Decision Boundary

The critical separation:

```text
Content Intelligence answers:
    "What content should we create, for whom, in what format,
     with what message and with what expected outcome?"
                    ↓
            Recommendation (with evidence and confidence)
                    ↓
Orchestrator Agent answers:
    "Which of these opportunities will we pursue, in what order,
     with what resources, at what time, and should we escalate
     to the human operator?"
                    ↓
            Decision
```

Content Intelligence does NOT decide:

- whether to act on an opportunity;
- which opportunity to prioritize;
- when to start a content cycle;
- whether to request additional data;
- whether to escalate to human review.

These are Orchestrator Agent decisions.

Content Intelligence ensures the Orchestrator's decisions are informed
by structured, evidence-backed content recommendations rather than
guesswork.

## 11.3. What the Orchestrator May Request

The Orchestrator Agent may:

- **Select** a Content Opportunity and launch a content cycle.
- **Defer** a Content Opportunity to a later cycle.
- **Experiment** — launch a small-scale test of an opportunity before
  full commitment.
- **Decline** a Content Opportunity with reasoning stored in Learning
  Memory.
- **Request Refinement** — ask Content Intelligence for additional
  analysis, alternative formats or different angles.
- **Escalate** to the human operator for strategic direction.

Reference: `CONTENT_CYCLE_SPEC.md`, Section 7 — Strategic Decision

## 11.4. Autonomy Mode Impact

The autonomy mode affects how Content Intelligence recommendations
flow through the Orchestrator:

```text
Copilot mode:
    Content Intelligence recommends → Orchestrator presents to human
    → Human decides.

Assisted mode:
    Content Intelligence recommends → Orchestrator decides routine
    cases autonomously → Human reviews at checkpoints.

Autopilot mode:
    Content Intelligence recommends → Orchestrator decides autonomously
    within confidence boundaries → Human monitors through control points.
```

Reference: `AGENT_SYSTEM_SPEC.md`, Section 8 — Human Approval Model

---

# 12. Relationship with Trend Intelligence

## 12.1. Upstream-Downstream Relationship

Trend Intelligence and Content Intelligence form a sequential
intelligence chain:

```text
Trend Intelligence      →  Content Intelligence

"What is happening?"    →  "What should we create because of it?"

MarketSignals           →  Content input analysis
TrendPatterns           →  Content direction formation
Relevance Scores        →  Opportunity prioritization
Affected Audiences      →  Audience targeting
Related Formats         →  Format recommendation
```

Trend Intelligence provides the market understanding. Content
Intelligence transforms that understanding into actionable content
recommendations.

## 12.2. The Transition Point

The transition from Trend Intelligence to Content Intelligence is the
critical handoff in the LOOPRA intelligence pipeline:

```text
TrendPattern:
    "Short educational videos about AI tool usage are generating
     2.5x higher engagement than static educational posts among
     entrepreneur and marketer audiences."
         ↓  handed to Content Intelligence
         ↓  combined with Brand System, Goals, Learning Memory
         ↓
Content Opportunity:
    "Create a series of short educational videos (under 60 seconds)
     demonstrating practical AI tips for small business owners,
     targeting awareness and engagement goals through the expertise
     pillar."
```

Trend Intelligence says: "This is happening."

Content Intelligence says: "Here is what we should create because of it,
for this audience, with this goal, in this format, with this message."

## 12.3. Dependency Direction

```text
Trend Intelligence → Content Intelligence → Orchestrator Agent

Content Intelligence depends on Trend Intelligence.
Content Intelligence does NOT drive Trend Intelligence.

Trend Intelligence does not need to know what content will be created.
Content Intelligence must know what trends exist to form opportunities.
```

This one-directional dependency maintains clean module boundaries.

## 12.4. Multiple Opportunities Per Trend

A single TrendPattern can generate multiple Content Opportunities.

Content Intelligence explores all viable content directions from a given
trend and presents the most strategically valuable ones to the
Orchestrator Agent.

The Orchestrator may select one, several or none of the opportunities
associated with a trend.

---

# 13. Relationship with Learning Memory

## 13.1. Learning from Experience

Learning Memory is the persistent operational knowledge of LOOPRA.

Content Intelligence uses Learning Memory to ground its recommendations
in proven experience rather than theoretical assumptions.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 5.6 — Learning Memory Module

## 13.2. How Learning Memory Enhances Content Intelligence

### Confidence Adjustment

Past content outcomes directly affect confidence:

```text
Content Opportunity:
    "Educational carousel about AI tools for small business owners."

Learning Memory query:
    Has educational carousel format worked for small business audience?
    Has AI/technology topic worked for this audience?
    Has awareness goal been served by carousel format before?

    Result: carousel format has 40% higher save rate for this audience.
            AI topic performed well in the last 2 cycles.
            Awareness goal met or exceeded in 3 of last 4 carousel cycles.
            → Confidence: HIGH.
```

Conversely:

```text
Content Opportunity:
    "Text post about AI tools for small business owners."

Learning Memory query:
    Has text format worked for this audience with this topic?

    Result: text posts on AI topic generated low engagement in 3 cycles.
            Audience prefers visual format for technical topics.
            → Confidence: LOW. Format recommendation adjusted.
```

### Format Effectiveness

Learning Memory provides evidence about which formats work:

- which formats drive saves vs likes vs shares vs clicks;
- which formats perform best for which audience segments;
- which formats are most effective for which business goals;
- which format-audience-goal combinations have the strongest track record.

This evidence directly informs Content Intelligence's format
recommendations.

### Topic Resonance

Learning Memory provides evidence about which topics resonate:

- which themes generate sustained engagement;
- which topics drive audience growth vs retention;
- which topics connect to conversions;
- which topics have declining audience interest.

This evidence helps Content Intelligence select topics within a trend
that have the highest probability of success.

### Failed Experiments

Learning Memory documents what did not work:

```text
Content Intelligence queries Learning Memory:

    "Has similar content been attempted before?"

    If yes and it failed:
        → Content Intelligence marks the opportunity with a warning.
        → Confidence is reduced.
        → The Orchestrator sees the warning and may decline or redesign.

    If yes and it succeeded:
        → Confidence is increased.
        → The opportunity is prioritized.
```

Content Intelligence does not blindly repeat failed approaches.

### Pattern Recognition

Learning Memory provides patterns that Content Intelligence applies to
new situations:

```text
Pattern from Learning Memory:
    "Content with personal stories in the first 3 slides of a carousel
     generates higher completion rates for this audience."

Content Intelligence applies this pattern:
    → Recommends storytelling angle for carousel format.
    → Recommends leading with a personal story in the first slides.
```

## 13.3. Learning Memory Boundaries

Learning Memory enhances Content Intelligence but operates within
constraints:

- Learning Memory does NOT override Brand System — a format that
  generates high engagement but conflicts with brand tone is not
  recommended.
- Learning Memory does NOT override goals — a topic that generates high
  engagement but serves a low-priority goal is correctly deprioritized.
- Learning Memory provides patterns, not mandates — Content Intelligence
  may recommend an approach that contradicts past patterns if current
  evidence indicates a shift.

Content Intelligence uses Learning Memory to inform, not to constrain.

---

# 14. Relationship with Foundation MVP

## 14.1. Current State

The Foundation MVP does NOT contain Content Intelligence.

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

Content ideas originate from human input. There is no automated content
opportunity analysis, format recommendation or confidence scoring.

Reference: `MVP_SCOPE.md`

## 14.2. The Foundation Pipeline Is Preserved

Content Intelligence does NOT replace the Foundation MVP pipeline.

The Foundation MVP pipeline (`Idea → Scenario → ContentItem →
ExportPackage → Publication → MetricSnapshot`) remains the execution
backbone of LOOPRA production.

What changes is the **source of the Idea**.

```text
Current Foundation MVP:
    Human → Idea → Scenario → ContentItem → ...

Future with Content Intelligence:
    Trend Intelligence → Content Intelligence → Content Opportunity
    → Orchestrator Decision → Idea → Scenario → ContentItem → ...
```

The Idea entity persists. The Scenario entity persists. The ContentItem
entity persists. The Foundation MVP pipeline continues to execute
reliably.

Content Intelligence adds the intelligence layer that determines what
Idea should be created, for whom, with what goal, in what format — before
the Foundation MVP pipeline begins execution.

## 14.3. What Changes and What Stays

```text
What stays from Foundation MVP:

    Idea → Scenario → ContentItem → ExportPackage → Publication →
    MetricSnapshot

    These execution primitives remain the validated production backbone.

What Content Intelligence adds:

    Before the pipeline begins:
        - Content Opportunity formation from trends and brand context
        - Audience targeting and analysis
        - Format recommendation grounded in evidence
        - Angle selection aligned with goals
        - Confidence scoring based on Learning Memory

    After the pipeline completes:
        - Outcome data feeds back into Learning Memory
        - Future Content Opportunities benefit from accumulated experience
```

## 14.4. Evolution Path

```text
Foundation MVP (current)
    Manual Idea creation
    Deterministic pipeline
    No content intelligence
        ↓
Content Intelligence (next)
    Automated opportunity analysis
    Format and angle recommendation
    Confidence scoring from Learning Memory
    Source of Ideas begins to shift from manual to intelligence-driven
        ↓
Agentic Operations
    Full Orchestrator integration
    Autonomous opportunity selection
    Learning Memory feedback loop active
        ↓
Marketing Operating System
    Continuous autonomous content planning
    Self-improving content recommendations
```

Reference: `LOOPRA_ARCHITECTURE.md`, Section 2

---

# 15. Content Decision Model

## 15.1. Recommendation, Not Decision

Content Intelligence creates **recommendations**.

The Orchestrator Agent makes **decisions**.

This separation is fundamental to the LOOPRA architecture.

## 15.2. What the Orchestrator Evaluates

When the Orchestrator Agent receives a Content Opportunity, it evaluates:

| Factor | Question |
|---|---|
| **Opportunity strength** | How well-formed and supported is this recommendation? |
| **Confidence** | How certain is Content Intelligence about this opportunity? |
| **Goal alignment** | Does this serve active, high-priority goals? |
| **Autonomy mode** | Can I decide independently or must I escalate? |
| **Restrictions** | Does this opportunity respect all brand boundaries? |
| **Resources** | Do we have the production capacity to execute this? |
| **Timing** | Is now the right moment to pursue this? |
| **Portfolio fit** | How does this fit with other active content cycles? |

## 15.3. Possible Orchestrator Decisions

Based on evaluation, the Orchestrator may:

```text
Create:
    Approve the opportunity. Launch content creation cycle.
    The Content Opportunity becomes an Idea in the Foundation MVP pipeline.

Defer:
    Save the opportunity for a later cycle. Conditions may be more
    favourable in the future.

Experiment:
    Launch a small-scale test. Produce one content item and evaluate
    results before committing to a series.

Decline:
    Reject the opportunity. Record reasoning in Learning Memory for
    future reference.

Escalate:
    Request human input. The opportunity requires strategic judgment
    beyond the current autonomy level.
```

Reference: `CONTENT_CYCLE_SPEC.md`, Section 7.3 — Decision Types
Reference: `AGENT_SYSTEM_SPEC.md`, Section 6 — Agent Decision Model

## 15.4. Decision Record

Every Orchestrator decision about a Content Opportunity is recorded.

This enables:
- auditing — why was an opportunity pursued or declined;
- learning — which types of opportunities produce the best outcomes;
- transparency — the human operator can review all decisions;
- pattern analysis — which decision patterns lead to success.

Reference: `DATA_MODEL.md`, Section 4.5 — `AgentDecision`

---

# 16. Content Experimentation

## 16.1. Conceptual Overview

Content experimentation is a future capability in which LOOPRA
systematically tests content hypotheses to improve recommendations.

## 16.2. Experiment Cycle

```text
Hypothesis:
    "We believe that format X will outperform format Y for audience Z
     on goal W."

Content Experiment:
    Produce content in both formats. Distribute under controlled
    conditions.

Result:
    Measure actual performance of each format. Compare against hypothesis.

Learning Update:
    Record outcome in Learning Memory. Adjust future Content Intelligence
    recommendations based on results.
```

## 16.3. Experiment Types

| Experiment Type | Tests |
|---|---|
| Format experiment | Which format performs best for a given goal and audience? |
| Angle experiment | Which angle generates the most engagement for a topic? |
| Topic experiment | Which subtopic within a trend resonates most? |
| Channel experiment | Which channel yields the best response for this content? |
| Timing experiment | Which publishing time maximizes reach and engagement? |
| CTA experiment | Which call-to-action converts best for this audience? |

## 16.4. How Experiments Improve Content Intelligence

Experiment results feed into Learning Memory and strengthen Content
Intelligence:

```text
Before experiment:
    Content Intelligence recommends format based on general heuristics.
    Confidence: medium.

After experiment:
    Content Intelligence recommends format based on actual performance
    data for this specific brand, audience and goal.
    Confidence: high.
```

Systematic experimentation transforms assumptions into verified
knowledge.

Content Intelligence uses verified knowledge to make increasingly
accurate recommendations.

## 16.5. Current Scope

Content experimentation is a future capability.

It is described here as an architectural direction that Content
Intelligence will support.

Current Foundation MVP does not include automated experimentation.

---

# 17. Future Implementation Considerations

## 17.1. Overview

This section describes conceptual directions for Content Intelligence
implementation. It does not specify implementation details, technologies
or timelines.

These directions represent the architectural vision for how Content
Intelligence capabilities may evolve.

## 17.2. Semantic Content Analysis

Beyond format and topic matching, Content Intelligence will develop
deeper semantic understanding:

- analyzing why certain content structures work for certain audiences;
- identifying the underlying communication patterns that drive
  engagement;
- understanding narrative structures that resonate with specific
  segments;
- detecting emotional triggers and their effectiveness by audience.

## 17.3. Audience Modeling

Content Intelligence will build detailed models of audience behaviour:

- predictive models of audience content preferences;
- segment-level response patterns to different content types;
- awareness-level progression tracking — how audiences move through
  awareness stages;
- cross-channel audience behaviour mapping.

## 17.4. Content Scoring

Content Intelligence will develop predictive scoring of content
potential:

- pre-production scoring — how likely is this opportunity to succeed
  before anything is created;
- format-goal-audience fit scoring — quantitative assessment of the
  three-way match;
- competitive content space analysis — identifying under-served
  content areas with high audience demand;
- predicted performance estimation based on historical patterns.

## 17.5. Automated Content Planning

Content Intelligence will move from single-opportunity recommendation
to strategic content planning:

- multi-cycle content plans aligned with campaign objectives;
- content sequencing — which content pieces should follow which to
  guide audience progression;
- pillar balance optimization — ensuring strategic content pillars
  receive appropriate coverage;
- channel mix optimization across cycles.

## 17.6. Multi-Channel Adaptation

Content Intelligence will recommend how a single content idea can
be adapted across channels:

```text
Core Content Direction:
    "AI tools for small business owners."

Channel Adaptations:
    Instagram → short video reel (visual demonstration)
    LinkedIn → carousel (professional, detailed explanation)
    Telegram → text post (depth, community discussion)
    TikTok → short video (trend-aligned, entertaining angle)
```

One content direction, multiple channel-specific executions, each
optimized for the platform and its audience.

## 17.7. Implementation Constraints

Content Intelligence implementation must respect:

- module boundaries — Content Intelligence remains an Intelligence
  Module, not an agent;
- decision separation — Content Intelligence recommends, Orchestrator
  decides;
- production separation — Content Intelligence does not produce content;
- brand boundaries — Content Intelligence respects Brand System
  restrictions at all times;
- Foundation MVP preservation — the Idea → Scenario → ContentItem
  pipeline remains intact.

---

# 18. Related Documents

## 18.1. Core Documents

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Content Cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Agent System specification
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — Trend Intelligence specification
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
```

## 18.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
docs/00_foundation/MVP_SCOPE.md                     — Foundation MVP scope
```

## 18.3. Architecture Layer

```text
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
```

## 18.4. Product Layer

```text
docs/01_product/LOOPRA_BRAND_POSITIONING.md         — LOOPRA product identity
docs/01_product/USER_WORKFLOWS.md                   — User interaction model
```

## 18.5. Future Documents

```text
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory specification
docs/04_production/CONTENT_TYPES_SPEC.md            — Content format definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — Production workflow specification
docs/04_production/CONTENT_OPERATING_SYSTEM_SPEC.md — Autonomous cycle execution
```

## 18.6. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# 19. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Intelligence Layer — Content Intelligence Specification |

---

# Final Statement

Content Intelligence is the strategic content selection layer of LOOPRA.

It does not produce content.

It does not render content.

It does not publish content.

Content Intelligence determines:

- which content has strategic potential;
- for which audience;
- toward which goal;
- in which format;
- with which message;
- with what probability of success.

It transforms the market understanding provided by Trend Intelligence
into structured, evidence-backed content recommendations.

It provides the Orchestrator Agent with the intelligence needed to make
informed strategic decisions about what content to create.

```text
Trend Intelligence       →  "What is happening in the market?"

Content Intelligence     →  "What content should we create
                             because of it?"

Orchestrator Agent       →  "Which of these opportunities will
                             we pursue?"

Production Layer         →  "We will create this content now."
```

Content Intelligence bridges market understanding and content creation.

Without it, LOOPRA would create content based on guesswork.

With it, LOOPRA creates content based on verified market understanding,
filtered through brand context, aligned with business goals, informed by
accumulated experience and continuously improved through learning.

This is the intelligence that transforms LOOPRA from a deterministic
production pipeline into a self-learning autonomous marketing operating
system.

---

## Current Implementation — Stage 2 Slice 1

The current implemented Content Intelligence capability is a deterministic, manual foundation:

```text
MarketSignal -> TrendPattern -> ContentOpportunity -> optional Idea
```

Implemented behaviour:

- project-scoped `ContentOpportunity` records;
- approval/rejection/defer/archive lifecycle;
- approved-opportunity conversion to a Foundation MVP `Idea`;
- CLI support with human-readable and `--json` output modes.

Current boundaries:

- Content Intelligence recommends; it does not autonomously decide.
- It does not generate final content.
- It does not publish.
- It does not call external APIs or scrape platforms.
- Full Content Intelligence, Orchestrator Agent and Learning Memory remain future scope.

# Brand System Spec

## Status

Active — LOOPRA Architecture Layer

## Version

v2.0

## Purpose

This document defines the Brand System as the fundamental operational
knowledge layer of LOOPRA — the Autonomous Marketing Operating System.

The Brand System is not a set of content generation parameters.
It is the structured knowledge about a brand that LOOPRA uses to make
autonomous marketing decisions across continuous growth cycles.

---

## 1. Brand System Definition

**Brand System** is a structured description of a brand that includes:

- identity;
- audience;
- communication rules;
- content strategy;
- business goals;
- safety constraints.

LOOPRA uses the Brand System as the primary context source for all
subsequent processes:

```
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

Production

    ↓

Analytics

    ↓

Learning Memory
```

The Brand System is the foundation layer.
Without it, LOOPRA cannot make informed marketing decisions.

### 1.1. What Brand System Answers

The Brand System provides answers to the questions LOOPRA needs to
operate autonomously:

- Who is the brand?
- Who is the brand speaking to?
- How does the brand communicate?
- What content strategy does the brand follow?
- What are the business goals?
- What are the boundaries and restrictions?
- What level of autonomy is permitted?

### 1.2. What Brand System Is Not

The Brand System is not:

- a logo guide;
- a design style guide;
- a classic marketing brandbook;
- a collection of visual assets;
- hardcoded platform rules.

It is an operational model of the brand designed for AI-driven
marketing decisions.

---

## 2. Brand System Position in LOOPRA Architecture

The Brand System is a project-scoped layer within a Workspace.

```
Workspace

    ├── Brand System
    │     ├── Brand Identity
    │     ├── Audience Intelligence
    │     ├── Communication System
    │     ├── Content Strategy
    │     ├── Business Goals
    │     ├── Restrictions and Safety Rules
    │     └── Autonomy Settings
    │
    ├── Projects
    ├── Content Cycles
    ├── Assets
    └── Analytics History
```

### 2.1. Platform vs Project Scope

Platform-level remains generic structure definition.
Project-specific truth lives in Brand System configuration.

Principle:

> No brand-specific rules should be hardcoded into the LOOPRA platform core.

Project-specific Brand System configuration belongs in:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/
```

---

## 3. Brand Identity Layer

The Brand Identity Layer defines who the brand is.

### 3.1. Fields

| Field | Description |
|---|---|
| `brand_name` | Brand name as used in content and references |
| `positioning` | How the brand should be perceived by the audience |
| `mission` | Brand mission statement |
| `values` | Core values that guide brand decisions |
| `personality` | Brand personality traits |
| `differentiation` | What makes this brand different from alternatives |
| `language` | Primary language for content generation |

### 3.2. Minimal Structure

```json
{
  "brand_identity": {
    "brand_name": "Example Brand",
    "positioning": "Clear and practical content brand.",
    "mission": "Help teams create consistently.",
    "values": [
      "clarity",
      "reliability",
      "growth"
    ],
    "personality": "calm guide",
    "differentiation": "Continuous improvement model.",
    "language": "ru"
  }
}
```

### 3.3. Usage

The Orchestrator Agent uses Brand Identity to:
- understand what the brand represents;
- maintain consistent brand voice across cycles;
- evaluate whether content ideas align with brand values;
- protect brand integrity during autonomous decisions.

---

## 4. Audience Intelligence Layer

The Audience Intelligence Layer defines who the brand speaks to.

### 4.1. Fields

| Field | Description |
|---|---|
| `target_audience` | Primary audience description |
| `audience_segments` | Audience segments with distinct characteristics |
| `pain_points` | Key problems and frustrations the audience experiences |
| `motivations` | What drives the audience to act |
| `desired_outcomes` | What the audience wants to achieve |
| `communication_preferences` | How the audience prefers to receive information |

### 4.2. Minimal Structure

```json
{
  "audience_intelligence": {
    "target_audience": "Teams and creators who need repeatable content workflows.",
    "audience_segments": [
      {
        "segment": "solo_founders",
        "description": "Independent founders building audience.",
        "pain_points": ["time scarcity", "inconsistent publishing"],
        "motivations": ["growth", "efficiency"],
        "desired_outcomes": ["consistent visibility", "audience trust"]
      },
      {
        "segment": "marketers",
        "description": "Marketing professionals managing multiple channels.",
        "pain_points": ["fragmented tools", "slow production"],
        "motivations": ["performance", "scale"],
        "desired_outcomes": ["faster execution", "data-driven decisions"]
      }
    ],
    "communication_preferences": ["text posts", "short video", "educational content"]
  }
}
```

### 4.3. Usage

LOOPRA uses Audience Intelligence to:
- select relevant topics for each segment;
- adapt tone and format to audience preferences;
- identify which pain points to address in content;
- align content objectives with audience motivations;
- avoid content that does not match audience needs.

---

## 5. Communication System

The Communication System defines how the brand talks.

### 5.1. Tone of Voice

The Tone of Voice layer defines the brand's communication style.

#### Fields

| Field | Description |
|---|---|
| `style` | Tone characteristics (e.g. calm, confident, warm) |
| `emotional_range` | Permitted emotional spectrum |
| `allowed_formulations` | Phrases and patterns that are encouraged |
| `forbidden_formulations` | Phrases and patterns that are prohibited |

#### Minimal Structure

```json
{
  "tone_of_voice": {
    "style": ["calm", "confident", "practical"],
    "emotional_range": ["neutral", "supportive", "inspiring"],
    "allowed_formulations": [
      "speak simply and directly",
      "use practical examples",
      "acknowledge real challenges"
    ],
    "forbidden_formulations": [
      "fear-based urgency",
      "unrealistic guarantees",
      "aggressive pressure language"
    ]
  }
}
```

### 5.2. Content Principles

Content principles define what the brand talks about and how.

#### Fields

| Field | Description |
|---|---|
| `topics_to_cover` | Themes and subjects the brand actively addresses |
| `topics_to_avoid` | Themes the brand stays away from |
| `meanings_to_amplify` | Key messages and values to reinforce repeatedly |

#### Minimal Structure

```json
{
  "content_principles": {
    "topics_to_cover": [
      "practical workflows",
      "continuous improvement",
      "real examples",
      "actionable strategies"
    ],
    "topics_to_avoid": [
      "get-rich-quick claims",
      "unverified statistics",
      "negative competitor references"
    ],
    "meanings_to_amplify": [
      "consistency over perfection",
      "systems over hacks",
      "continuous growth"
    ]
  }
}
```

### 5.3. Usage

The Orchestrator Agent applies the Communication System to:
- generate content in the correct tone;
- filter out inappropriate messages;
- maintain brand voice consistency;
- adapt communication style per platform and audience segment.

---

## 6. Content Strategy Layer

The Content Strategy Layer defines what content the brand creates
and why.

### 6.1. Fields

| Field | Description |
|---|---|
| `content_pillars` | Thematic pillars that organize all content |
| `preferred_formats` | Content formats the brand uses |
| `channels` | Distribution channels |
| `publishing_goals` | Publishing frequency and volume targets |
| `content_objectives` | What each content piece should achieve |

### 6.2. Minimal Structure

```json
{
  "content_strategy": {
    "content_pillars": [
      {
        "pillar": "relationships",
        "description": "Building audience trust and connection.",
        "formats": ["text_posts", "short_video", "carousel"],
        "objectives": ["engagement", "trust"]
      },
      {
        "pillar": "expertise",
        "description": "Demonstrating knowledge and authority.",
        "formats": ["educational_carousel", "long_form_text"],
        "objectives": ["authority", "leads"]
      },
      {
        "pillar": "offers",
        "description": "Presenting products and services.",
        "formats": ["announcement", "demo_video"],
        "objectives": ["sales", "conversion"]
      }
    ],
    "channels": ["telegram", "threads", "vk"],
    "publishing_goals": {
      "target_frequency": "3 posts per week",
      "preferred_days": ["mon", "wed", "fri"]
    }
  }
}
```

### 6.3. Usage

LOOPRA uses Content Strategy to:
- select which pillar to activate in each cycle;
- choose appropriate formats for the selected pillar;
- prioritize content objectives;
- plan publishing schedules;
- evaluate content performance against pillar goals.

---

## 7. Business Goals Layer

The Business Goals Layer defines why the brand creates content.

### 7.1. Fields

| Field | Description |
|---|---|
| `brand_goals` | High-level business goals the brand pursues |

### 7.2. Goal Types

```text
awareness     — reach new audiences, increase visibility
engagement    — deepen audience interaction and loyalty
leads         — generate qualified interest
sales         — drive conversions and revenue
retention     — maintain existing customer relationships
```

### 7.3. Minimal Structure

```json
{
  "business_goals": {
    "brand_goals": [
      {
        "goal": "awareness",
        "priority": "high",
        "target": "grow audience by 30% in 3 months"
      },
      {
        "goal": "engagement",
        "priority": "medium",
        "target": "increase average interaction rate"
      },
      {
        "goal": "leads",
        "priority": "medium",
        "target": "generate qualified inquiries"
      }
    ]
  }
}
```

### 7.4. Usage

LOOPRA must understand not only **what** to create but **why**.
Business goals drive:
- content pillar selection;
- format choice;
- CTA activation;
- priority allocation across cycles;
- performance evaluation criteria.

---

## 8. Restrictions and Safety Rules

The Restrictions layer defines what the brand must never do.

### 8.1. Fields

| Field | Description |
|---|---|
| `forbidden_topics` | Topics that must never appear in content |
| `forbidden_claims` | Claims that must never be made |
| `legal_limitations` | Legal and regulatory constraints |
| `compliance_rules` | Compliance requirements for the brand's industry |

### 8.2. Minimal Structure

```json
{
  "restrictions": {
    "forbidden_topics": [
      "religious claims",
      "political positions",
      "unverified medical advice",
      "personal attacks"
    ],
    "forbidden_claims": [
      "guaranteed results",
      "magic solutions",
      "get rich without effort"
    ],
    "legal_limitations": [
      "no financial advice without disclaimer",
      "no health claims without evidence"
    ],
    "compliance_rules": [
      "include disclaimer when discussing sensitive topics",
      "cite sources for data claims"
    ]
  }
}
```

### 8.3. Usage

All content generated by LOOPRA must pass through restriction
validation. The Orchestrator Agent applies these rules during:
- idea selection;
- scenario generation;
- content creation;
- final review before publication.

Restrictions are non-negotiable hard constraints.

---

## 9. Autonomy Settings

The Autonomy Settings define the level of autonomous operation
LOOPRA is permitted to execute for a brand.

### 9.1. Autonomy Modes

| Mode | Description |
|---|---|
| `copilot` | LOOPRA suggests; human decides and approves everything |
| `assisted` | LOOPRA operates with periodic human checkpoints |
| `autopilot` | LOOPRA operates autonomously with emergency stop |

### 9.2. Control Points

| Field | Description |
|---|---|
| `autonomy_mode` | Current autonomy level |
| `approval_requirements` | Which steps require human approval |
| `review_frequency` | How often human review is triggered |
| `human_checkpoints` | Specific checkpoints where human must confirm |

### 9.3. Minimal Structure

```json
{
  "autonomy_settings": {
    "autonomy_mode": "copilot",
    "approval_requirements": [
      "content_ideas",
      "final_content_before_publication"
    ],
    "review_frequency": "every_cycle",
    "human_checkpoints": [
      "after_idea_selection",
      "before_publication"
    ]
  }
}
```

### 9.4. Usage

Autonomy Settings act as operational guardrails.
As LOOPRA evolves toward autonomous cycles, these settings control:
- how much the Orchestrator Agent can decide independently;
- when human review is required;
- what must never be automated for a given brand.

**Note:** This layer is defined for future scope.
Current Foundation MVP operates in `copilot` mode by default.

---

## 10. Brand System and Orchestrator Agent

The Orchestrator Agent uses the Brand System as its primary decision
context.

### 10.1. How The Agent Uses Brand System

```
Agent receives Brand System context:

    → Who is the brand?
    → Who is the audience?
    → What are the goals?
    → What are the restrictions?
    → What autonomy level is permitted?

Agent then decides:

    → What topics to pursue?
    → What formats to use?
    → What scenarios to create?
    → What experiments to run?
    → When to request human review?
```

### 10.2. Agent Principles

The Orchestrator Agent:
- reads Brand System at the start of each cycle;
- applies brand rules to every decision;
- does not modify Brand System on its own;
- escalates to human when uncertain.

Principle:

> Brand System defines the boundaries.
> Orchestrator Agent operates within them.

---

## 11. Brand System and Learning Memory

Brand System and Learning Memory serve different roles in LOOPRA.

### 11.1. Separation of Concerns

| Layer | Role | Stability |
|---|---|---|
| **Brand System** | Who the brand is | Stable |
| **Learning Memory** | What works best | Evolving |

### 11.2. Definition

**Brand System** answers:
> "Who is this brand?"

It changes rarely — only when the brand itself changes.

**Learning Memory** answers:
> "What performs best for this brand?"

It changes continuously — with every cycle and every metric.

### 11.3. Interaction

```
Brand System (stable)
        ↓
    Guides decisions
        ↓
Learning Memory (evolving)
        ↓
    Refines decisions over time
        ↓
    Improved next cycle
```

Learning Memory does not override Brand System.
It optimizes execution within brand boundaries.

---

## 12. Brand System and Content Cycles

The Brand System provides context for every content cycle.

```
Content Cycle:

    Brand System
        ↓
    Market Signals
        ↓
    Idea Selection → (filtered by brand identity and restrictions)
        ↓
    Scenario Generation → (guided by tone and audience)
        ↓
    Content Creation → (bounded by safety rules)
        ↓
    Publication → (aligned with business goals)
        ↓
    Analytics → (measured against objectives)
        ↓
    Learning Memory → (stores what worked)
```

Each cycle starts from the Brand System.
Each cycle feeds back into Learning Memory.

---

## 13. Brand System Configuration Storage

### 13.1. Project-Level Storage

Brand System configuration belongs to the project level:

```text
docs/07_projects/{project_slug}/
    POSITIONING.md        — brand identity and positioning
    TONE_OF_VOICE.md      — communication rules
    CONTENT_PILLARS.md    — content strategy and themes
    BRAND_SYSTEM.yaml     — structured configuration (future)

projects/{project_id}/
    project.yaml          — project-level settings
```

### 13.2. Platform-Level

Platform-level only defines the generic Brand System structure.
It never contains specific brand values.

---

## 14. Brand System Versioning

In future phases, Brand System should support versioning.

Reason:
- brands evolve;
- positioning may update;
- tone of voice may refine;
- content strategy may shift;
- it must be possible to know which version was active when specific
  content was created.

### 14.1. Version Fields

```json
{
  "brand_system_version": "1.0",
  "updated_at": "2026-07-08T00:00:00Z"
}
```

Content items may reference:

```json
{
  "brand_system_version_used": "1.0"
}
```

### 14.2. MVP Scope

Current Foundation MVP does not require full versioning.
One active Brand System per project is sufficient.
Version tracking can be added in later phases.

---

## 15. What Is In Current Foundation MVP

In the current Foundation MVP, Brand System includes:

- one Brand System configuration per project;
- brand identity fields (name, positioning, mission);
- audience description;
- tone of voice definition;
- content principles and pillars;
- business goals;
- restriction lists (forbidden topics, claims);
- basic content strategy parameters.

---

## 16. What Is Not In Current Foundation MVP

Not included in current Foundation MVP:

- multiple Brand System profiles per project;
- complex versioning;
- brand approval workflow;
- automatic brand extraction from website;
- AI brand audit;
- marketplace brand templates;
- team permissions for brand modifications;
- public onboarding for external users;
- full Autonomy Settings enforcement (copilot mode is the default).

These capabilities belong to future phases.

---

## 17. Common Mistakes to Avoid

### 17.1. Hardcoding Brand Rules in Platform

```text
BAD:  template always uses specific brand colors and specific CTA
GOOD: template loads brand configuration from Brand System
```

### 17.2. Single Global Tone of Voice

```text
BAD:  all generated content uses the same voice
GOOD: each project applies its own Brand System tone
```

### 17.3. Platform-Level CTA Library

```text
BAD:  all projects use one hardcoded CTA set
GOOD: each project has its own CTA configuration in Brand System
```

### 17.4. Missing Restrictions Layer

```text
BAD:  content generation without safety constraints
GOOD: Brand System restrictions are applied at every content step
```

### 17.5. Confusing Brand System with Brandbook

```text
BAD:  Brand System contains logo placement guides, font sizes,
      color hex values, motion style descriptions
GOOD: Brand System describes operational brand knowledge for
      AI-driven marketing decisions
```

---

## 18. Readiness Criteria

Brand System MVP is considered ready when:

- each project has a defined Brand System;
- brand identity fields are complete;
- audience intelligence layer is populated;
- tone of voice and content principles are defined;
- restrictions are documented;
- Orchestrator Agent can read and apply Brand System context;
- no brand-specific rules are hardcoded in platform code;
- content cycles operate within brand boundaries;
- Learning Memory feeds back without overriding Brand System.

---

## 19. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 2.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |

---

## 20. Related Documents

- `LOOPRA_ARCHITECTURE.md` — Core architectural source of truth
- `LOOPRA_BRAND_POSITIONING.md` — LOOPRA product brand identity
- `WORKSPACE_AND_PROJECT_MODEL.md` — Workspace and project architecture
- `PIPELINES_SPEC.md` — Content lifecycle pipeline stages
- `DOCUMENTATION_INDEX.md` — Documentation navigation

Project-level Brand System examples:

```text
docs/07_projects/nura/
    POSITIONING.md
    TONE_OF_VOICE.md
    CONTENT_PILLARS.md
```

# PRODUCTION PIPELINE SPEC

## Version

v1.0

## Status

Active — LOOPRA Production Layer

## Purpose

This document defines the Production Pipeline — the manufacturing
conveyor of the LOOPRA Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA transform a Content Decision / Scenario into a
> complete, verified Export Package ready for Distribution?

PRODUCTION_PIPELINE_SPEC.md is the architectural blueprint for the
layer that bridges strategic content decisions with concrete,
deliverable content packages.

It describes:

- the full production pipeline from Scenario to Distribution Ready;
- each production stage's inputs, outputs and transitions;
- the Production Brief as the operational execution contract;
- the variant-based production model for different content types;
- the asset selection and generation mechanics;
- the assembly process for multi-component content types;
- the mandatory Quality Assurance stage and its outcomes;
- the Export Package as the final production deliverable;
- the relationship between Production Pipeline and Foundation MVP;
- the interfaces with Intelligence Layer, Asset Library and Distribution Layer.

It does NOT describe:

- strategic decisions about what content to create;
- market/trend analysis or opportunity discovery;
- distribution, publishing or autoposting mechanics;
- analytics interpretation or performance analysis;
- learning algorithms or knowledge extraction;
- UI components, API contracts or database schemas;
- specific AI model providers, prompts or code-level implementation.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

PRODUCTION_PIPELINE_SPEC.md defines the production execution model of
LOOPRA — the deterministic manufacturing layer that receives strategic
decisions and produces finished, verified content packages.

It serves as the specification for:

- the stages of production from Scenario to Export Package;
- the inputs required at each stage;
- the outputs produced at each stage;
- the Production Brief as the operational contract between intelligence
  and execution;
- the variant-based production model for different content types;
- the asset system interaction within the production flow;
- the generation and assembly mechanics;
- the mandatory Quality Assurance stage;
- the Export Package structure;
- the interfaces with Intelligence Layer, Asset Library and Distribution Layer;
- the operational boundaries that preserve Foundation MVP integrity.

## 1.2. Scope

This document covers:

- the position of the Production Pipeline in the LOOPRA architecture;
- the relationship between Foundation MVP entities and future production entities;
- the complete pipeline stage diagram;
- upstream inputs from the Intelligence Layer;
- the Production Brief as a functional production instruction;
- Production Planning for different content types;
- Asset Selection and Asset Requirement mechanics;
- Content Generation by content type category;
- Assembly of multi-component content;
- Quality Assurance with all check categories and outcomes;
- Export Package structure and compatibility;
- Distribution Ready state definition;
- per-content-type production paths;
- conceptual production entities;
- production states and transitions;
- error handling model;
- human review and autonomy mode integration;
- Learning Memory production context snapshot;
- Asset Library interface role;
- Distribution Layer handoff boundary;
- Foundation MVP compatibility.

## 1.3. Out of Scope

This document does not cover:

- strategic content opportunity analysis (see `CONTENT_INTELLIGENCE_SPEC.md`);
- market trend detection (see `TREND_INTELLIGENCE_SPEC.md`);
- Orchestrator Agent decision-making (see `AGENT_SYSTEM_SPEC.md`);
- content cycle stage management (see `CONTENT_CYCLE_SPEC.md`);
- distribution, publishing or scheduling mechanics;
- analytics data collection or performance interpretation;
- learning memory extraction algorithms (see `LEARNING_MEMORY_SPEC.md`);
- detailed Asset Library storage structure (see future `ASSET_LIBRARY_SPEC.md`);
- UI, API, database, authentication or billing;
- external publishing platform integrations;
- autoposting or automated distribution.

---

# 2. Role of Production Pipeline in LOOPRA

## 2.1. Position in the LOOPRA Architecture

The Production Pipeline occupies a defined position in the LOOPRA
system architecture between Intelligence (strategic decisions) and
Distribution (content delivery):

```text
Intelligence Layer
    │  "What to create, why, for whom, in what format"
    │  Content Opportunity → Content Decision → Idea → Scenario
    ↓
Production Layer
    │  "How to manufacture the selected content"
    │  Production Pipeline: Plan → Select → Generate → Assemble → QA → Export
    ↓
Distribution Layer
    │  "How to deliver the finished package"
    │  Publication preparation, scheduling, channel delivery
    ↓
Analytics Layer
    │  "What happened after publication"
    │  Metric collection, performance analysis
    ↓
Learning Memory
    │  "What the system should remember"
    │  Knowledge extraction, pattern retention, next-cycle improvement
```

Reference: `SYSTEM_ARCHITECTURE.md`, Sections 8–11

## 2.2. The Production Pipeline Does NOT Make Strategic Decisions

The Production Pipeline operates under a strict principle:

> Production executes. Intelligence decides.

The Production Pipeline:

- receives a Content Decision and Scenario from the Intelligence Layer;
- translates them into a Production Brief;
- plans production steps based on the content type and channel requirements;
- selects, requests or generates required assets;
- assembles content components into a complete output;
- runs mandatory Quality Assurance checks;
- produces a verified Export Package;
- marks the package as Distribution Ready.

The Production Pipeline does NOT:

- decide whether content should be created;
- select which topic to address;
- choose which audience to target;
- determine the business goal behind the content;
- modify the strategic direction of a Scenario;
- change the content type selection made by Intelligence;
- override Brand System constraints or restrictions;
- initiate content cycles independently.

## 2.3. Production Receives, Production Executes, Production Delivers

```text
From Intelligence:  Content Decision + Scenario
                        ↓
Production Pipeline:  Brief → Plan → Select → Generate → Assemble → QA → Export
                        ↓
To Distribution:     ExportPackage (Distribution Ready)
```

Production is the deterministic bridge between strategic decision
and deliverable output. It does not question the decision. It executes
it to the highest quality standard within defined constraints.

---

# 3. Relationship to Foundation MVP

## 3.1. The Foundation MVP Preserved

The Foundation MVP defines a validated, operational entity chain:

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

Reference: `DATA_MODEL.md`, Section 3; `PIPELINES_SPEC.md`, Section 2

This chain is the reliable execution backbone of LOOPRA. The Production
Pipeline specification does not replace it — it elaborates on the
production portion.

## 3.2. What the Production Pipeline Detalizes

The Production Pipeline provides an expanded, detailed view of the
section between Scenario and ExportPackage:

```text
Foundation MVP:
    Scenario → ContentItem → ExportPackage

Production Pipeline (detailed):
    Scenario
        ↓
    Production Brief
        ↓
    Production Plan
        ↓
    Asset Requirements
        ↓
    Asset Selection
        ↓
    Content Generation
        ↓
    Assembly
        ↓
    Quality Assurance
        ↓
    Export Package
```

The Foundation MVP entities (`ContentItem`, `ExportPackage`) remain in
place as the production backbone. The Production Pipeline Specification
explains what happens between and within these entities without
changing their identity or role.

## 3.3. Upstream Context in the Full Architecture

In the full future LOOPRA architecture, the Production Pipeline
receives enriched upstream context that the current Foundation MVP
does not yet provide:

```text
Content Opportunity      (from Content Intelligence)
    ↓
Content Decision         (from Orchestrator Agent)
    ↓
Idea                     (creative concept, Foundation MVP bridge)
    ↓
Scenario                 (content plan, Foundation MVP bridge)
    ↓
Production Pipeline      ← **THIS DOCUMENT**
    ↓
ExportPackage            (distribution-ready package)
```

In the current Foundation MVP, the Idea is created manually by the
human operator. In the future, the Idea originates from the
Intelligence Layer. The Production Pipeline is agnostic to the
source of the Scenario — it executes identically regardless of
whether the Scenario was created by a human or by the Orchestrator
Agent.

## 3.4. What Does NOT Change

The Production Pipeline Specification does NOT:

- modify the `ContentItem` entity or its statuses;
- modify the `ExportPackage` entity or its structure (it extends conceptually);
- modify the `Publication` entity;
- modify the `MetricSnapshot` entity;
- change the existing Foundation MVP lifecycle;
- require new database schemas or migrations.

It adds conceptual depth to the production process that will guide
future implementation, without requiring changes to the validated
current baseline.

---

# 4. Production Pipeline Overview

## 4.1. The Full Pipeline Diagram

```text
                    FROM INTELLIGENCE LAYER
                           │
              Content Decision from Orchestrator
                           │
                    ┌──────┴──────┐
                    │     Idea    │  (Foundation MVP)
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   Scenario  │  (Foundation MVP)
                    └──────┬──────┘
                           │
         ╔═════════════════╧═════════════════╗
         ║       PRODUCTION PIPELINE         ║
         ║                                  ║
         ║  ┌───────────────────────┐       ║
         ║  │   Production Brief    │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │   Production Plan     │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │   Asset Requirements  │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │   Asset Selection     │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │  Content Generation   │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │      Assembly         │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │  Quality Assurance    │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ║  ┌───────────┴───────────┐       ║
         ║  │   Export Package      │       ║
         ║  └───────────┬───────────┘       ║
         ║              │                   ║
         ╚══════════════╧═══════════════════╝
                        │
               Distribution Ready
                        │
                    TO DISTRIBUTION LAYER
```

## 4.2. Stage-by-Stage Transition Explanation

### Stage Transition 1: Scenario → Production Brief

**What happens:** The Scenario (content plan with tone, objectives,
structure) is transformed into a Production Brief — a machine-actionable
production instruction that specifies exactly what to produce, in what
format, for which channels, with what parameters.

**Who owns it:** Production Pipeline consumes Scenario, produces Brief.

### Stage Transition 2: Production Brief → Production Plan

**What happens:** The Production Brief is decomposed into a structured
Production Plan that defines: which production variant applies, what
layers are needed, what steps the pipeline must execute, what assets
are required, what outputs are expected.

**Who owns it:** Production Planning stage.

### Stage Transition 3: Production Plan → Asset Requirements

**What happens:** The Production Plan identifies which assets are needed.
For each required asset, the pipeline checks availability in the Asset
Library. Available assets proceed to selection. Missing assets generate
Asset Requirements.

**Who owns it:** Asset Selection stage.

### Stage Transition 4: Asset Requirements → Asset Selection

**What happens:** Available assets are selected based on brand fit,
quality, licensing, and content type requirements. Missing assets that
can be generated are routed to Generation. Missing assets that cannot
be generated are flagged for human attention.

**Who owns it:** Asset Selection stage.

### Stage Transition 5: Asset Selection → Content Generation

**What happens:** For content components that require generation (text
body, headlines, captions, image prompts, scripts, voiceover, subtitles),
the pipeline invokes generation tools. Each tool produces a specific
component type based on the Production Brief parameters.

**Who owns it:** Generation stage.

### Stage Transition 6: Content Generation → Assembly

**What happens:** Generated components and selected assets are assembled
into a complete content output. Assembly follows the content type
structure — slides for carousels, scenes for videos, sections for text.
The result is a coherent, complete content unit.

**Who owns it:** Assembly stage.

### Stage Transition 7: Assembly → Quality Assurance

**What happens:** The assembled content passes through mandatory QA.
Brand voice, content structure, format specifications, channel
requirements, technical validity and compliance are checked. QA produces
a verdict: passed, warnings, changes_required or failed.

**Who owns it:** QA stage.

### Stage Transition 8: Quality Assurance → Export Package

**What happens:** Content that passes QA (or passes with acceptable
warnings) is packaged into an Export Package. The package includes
content files, captions, metadata, QA report, manifest and
channel-specific folders.

**Who owns it:** Export stage.

### Stage Transition 9: Export Package → Distribution Ready

**What happens:** The completed Export Package is marked as Distribution
Ready. The Production Pipeline's responsibility ends here. The package
is handed to the Distribution Layer for publication.

**Who owns it:** Production Pipeline boundary → Distribution Layer handoff.

---

# 5. Production Inputs

## 5.1. Overview

The Production Pipeline does not begin from a blank slate. It receives
a rich set of inputs from upstream layers and configuration sources.

## 5.2. Input Categories

### 5.2.1. Project Context

| Input | Source | Production Use |
|---|---|---|
| `project_id` | Project Configuration | Scoping all production entities |
| `workspace_id` | Workspace Configuration | Context reference |
| `project_name` | Project Configuration | Output naming, metadata |
| `default_language` | Project Settings | Content generation language |
| `primary_url` | Project Configuration | UTM links, brand references |

### 5.2.2. Brand System Snapshot

| Input | Source | Production Use |
|---|---|---|
| Brand Identity (name, positioning, values) | Brand System | Tone enforcement, QA checks |
| Audience Intelligence (segments, pain points) | Brand System | Content-to-audience alignment |
| Communication System (tone of voice, allowed/forbidden formulations) | Brand System | Content generation parameters, QA checks |
| Content Strategy (pillars, preferred formats) | Brand System | Format alignment validation |
| Restrictions (forbidden topics, claims, legal) | Brand System | Absolute QA boundaries |
| Brand Visual Identity (logo, fonts, colors) | Brand System | Brand layer assembly |

Reference: `BRAND_SYSTEM_SPEC.md`

### 5.2.3. Project Settings

| Input | Source | Production Use |
|---|---|---|
| Goals and priorities | Project Settings | Goal alignment validation |
| Channel configuration | Project Settings | Platform-specific output formatting |
| Content type configuration | Project Settings | Enabled type validation |
| UTM configuration | Project Settings | Link generation for export |
| Export settings | Project Settings | Output path and naming |

Reference: `PROJECT_SETTINGS_SPEC.md`

### 5.2.4. Content Decision and Scenario

| Input | Source | Production Use |
|---|---|---|
| Content Decision (create/defer/experiment) | Orchestrator Agent | Trigger to begin production |
| Idea (creative concept) | Foundation MVP / Intelligence | Thematic direction |
| Scenario (content plan) | Foundation MVP / Intelligence | Production execution blueprint |
| Content type selection | Content Intelligence → Scenario | Determines production variant |
| Content objective | Scenario | Guides generation parameters |
| Key message | Scenario | Core message for content text |
| Target audience segment | Scenario | Audience-specific adaptation |
| Recommended channels | Scenario | Output format targets |

### 5.2.5. Content Type Definition

| Input | Source | Production Use |
|---|---|---|
| Content type structure | `CONTENT_TYPES_SPEC.md` | Template for assembly |
| Required layers and components | Content type spec | Generation step list |
| Production variants | Content type spec | Variant selection in Planning |
| Channel constraints | Content type spec | Output format validation |
| Quality rules | Content type spec | QA checklist per type |

Reference: `CONTENT_TYPES_SPEC.md`

### 5.2.6. Channel Requirements

| Input | Source | Production Use |
|---|---|---|
| Platform character limits | Channel config | Text truncation and adaptation |
| Aspect ratio requirements | Channel config | Visual output dimensions |
| Duration constraints | Channel config | Video length enforcement |
| Caption formatting rules | Channel config | Caption styling per platform |
| Hashtag rules | Channel config | Hashtag generation per platform |
| CTA constraints | Channel config | CTA formatting per platform |

### 5.2.7. Asset Library Context

| Input | Source | Production Use |
|---|---|---|
| Available brand assets | Asset Library | Brand layer assembly |
| Available media assets | Asset Library | Visual/video production |
| Available audio assets | Asset Library | Video audio layer |
| Available templates | Asset Library | Slide/overlay templates |
| Asset licensing status | Asset Library | Usage permission checks |
| Asset quality metadata | Asset Library | Quality suitability assessment |

### 5.2.8. Learning Memory Recommendations

| Input | Source | Production Use |
|---|---|---|
| Format effectiveness patterns | Learning Memory | Production variant selection |
| Structure patterns (e.g. "5-7 slides optimal") | Learning Memory | Assembly parameter tuning |
| Hook type recommendations | Learning Memory | Hook selection in text generation |
| CTA performance patterns | Learning Memory | CTA selection per goal and audience |
| Duration optimization patterns | Learning Memory | Video length tuning |
| Failed approach warnings | Learning Memory | Avoiding known production mistakes |

Reference: `LEARNING_MEMORY_SPEC.md`

**Important:** Learning Memory recommendations have already been
processed by the Intelligence Layer before reaching Production.
The Production Pipeline receives these as input parameters, not
as queries it must resolve. Production does NOT retrieve Learning
Memory data itself — it consumes the parameters already embedded
in the Scenario and Production Brief.

### 5.2.9. Human Constraints or Approvals

| Input | Source | Production Use |
|---|---|---|
| Autonomy mode (copilot/assisted/autopilot) | Brand System / Project Settings | Determines approval gates |
| Specific production constraints | Human operator | Override production parameters |
| Manual asset uploads | Human operator | User-provided raw material |
| Production brief approval | Human operator (copilot mode) | Gate before production begins |
| QA override decisions | Human operator | Override QA failure with approval |

---

# 6. Production Brief

## 6.1. Definition

The **Production Brief** is the formal operational instruction that
the Production Pipeline receives. It transforms the Scenario — a
creative content plan — into a precise, machine-actionable
production specification.

The Production Brief is NOT a strategic recommendation. It is a
production instruction. It says "produce this" with exact parameters,
not "consider producing something like this."

## 6.2. Role as Bridge

The Production Brief is the critical bridge between the Intelligence
Layer and the Production Layer:

```text
Intelligence Layer Output:
    "Create an educational carousel about AI tools for entrepreneurs.
     Target awareness goal. Professional tone. LinkedIn and Instagram."

        ↓  translated into

Production Brief:
    content_type: carousel
    production_variant: educational_carousel
    slide_count: 7
    slides: [hook, problem, solution_1, solution_2, solution_3, evidence, cta]
    channels: [linkedin, instagram]
    tone: professional, educational, practical
    audience: entrepreneurs
    goal: awareness
    ...
```

The Production Brief allows the Intelligence Layer to express
strategic intent without needing to know production mechanics.
It allows the Production Layer to execute without needing to
interpret strategic intent.

## 6.3. Production Brief Structure

### 6.3.1. Required Fields

| Field | Description |
|---|---|
| `project_id` | Project scope identifier |
| `content_item_id` | Reference to the ContentItem being produced (Foundation MVP bridge) |
| `content_type` | Content type identifier (e.g. `carousel`, `short_vertical_video`, `text_social_post`) |
| `production_variant` | Specific production approach within the content type (e.g. `educational_carousel`, `stock_footage_video`) |
| `target_channels` | List of distribution channels this content is for |
| `business_goal` | Primary marketing goal (awareness, engagement, leads, sales, retention) |
| `audience_segment` | Target audience segment from Brand System |
| `content_objective` | What this content piece should achieve tactically (educate, inspire, demonstrate, convert) |
| `key_message` | The core message or takeaway for the audience |
| `content_angle` | The framing approach (educational, storytelling, opinion, comparison, case_study) |

### 6.3.2. Tone and Brand Constraints

| Field | Description |
|---|---|
| `tone_of_voice` | Tone parameters (professional, casual, inspirational, authoritative) |
| `brand_restrictions` | Applicable forbidden topics, claims, formulations |
| `allowed_formulations` | Encouraged phrasings and patterns |
| `brand_elements_required` | Logo, colors, fonts, watermark requirements |

### 6.3.3. Production Parameters

| Field | Description |
|---|---|
| `required_assets` | List of assets needed (logos, fonts, templates, media) |
| `required_output_formats` | File formats for export (mp4, png, txt) |
| `duration` | Target duration for video (seconds) |
| `slide_count` | Target slide count for carousel |
| `text_length` | Target text length range (characters) |
| `aspect_ratio` | Required aspect ratio (9:16, 1:1, 4:5, 16:9) |
| `resolution` | Target resolution (e.g. 1080x1920) |

### 6.3.4. QA Requirements

| Field | Description |
|---|---|
| `brand_qa_required` | Whether brand voice check is mandatory |
| `format_qa_required` | Whether format specification check is mandatory |
| `channel_qa_required` | Whether channel constraint check is mandatory |
| `technical_qa_required` | Whether technical validation is mandatory |
| `compliance_qa_required` | Whether compliance and legal check is mandatory |
| `qa_strictness` | Whether warnings block progression or only flag |

### 6.3.5. Export Requirements

| Field | Description |
|---|---|
| `include_captions` | Generate per-channel caption files |
| `include_metadata` | Include metadata.json in export |
| `include_manifest` | Include manifest.json in export |
| `include_qa_report` | Include QA report in export |
| `include_thumbnails` | Generate and include thumbnail images |
| `include_subtitles` | Include subtitle files (SRT) for video |
| `include_utm_links` | Generate UTM-tagged links for CTAs |
| `channel_specific_folders` | Organize export by channel |

## 6.4. Production Brief Example — Carousel

```text
Production Brief:

    project_id: "project_001"
    content_item_id: "content_042"
    content_type: "carousel"
    production_variant: "educational_carousel"
    target_channels: ["linkedin", "instagram"]

    business_goal: "awareness"
    audience_segment: "entrepreneurs"
    content_objective: "educate"
    key_message: "AI automation tools can save 10+ hours per week for
                  small business owners without technical expertise."
    content_angle: "educational"

    tone_of_voice: ["professional", "practical", "encouraging"]
    brand_restrictions: ["no income guarantees", "no competitor mentions"]

    required_assets: ["brand_logo_light", "brand_font", "slide_template_v2"]
    required_output_formats: ["png"]
    slide_count: 7
    aspect_ratio: "1:1"
    resolution: "1080x1080"

    brand_qa_required: true
    format_qa_required: true
    channel_qa_required: true
    technical_qa_required: true
    compliance_qa_required: true
    qa_strictness: "standard"

    include_captions: true
    include_metadata: true
    include_manifest: true
    include_qa_report: true
    include_thumbnails: false
    include_subtitles: false
    include_utm_links: false
    channel_specific_folders: true
```

## 6.5. Production Brief Lifecycle

The Production Brief has its own lifecycle:

```text
created      — Brief is formed from Scenario
    ↓
validated    — Brief fields checked for completeness and consistency
    ↓
approved     — Human approval obtained (copilot/assisted modes) or
               auto-approved (autopilot mode)
    ↓
in_progress  — Production Pipeline is executing the Brief
    ↓
completed    — Export Package produced from this Brief
    ↓
archived     — Brief stored as production context snapshot for Learning Memory
```

The Production Brief, once approved, is an immutable operational
contract for the duration of that production run. It is not modified
during production. If changes are needed, the Brief is revised and
re-approved.

---

# 7. Production Planning Stage

## 7.1. Purpose

Production Planning is the first execution stage of the Production
Pipeline. It translates the Production Brief into a detailed, actionable
Production Plan that defines exactly how the content will be manufactured.

Production Planning answers:

- Which production variant applies to this content?
- What layers must be assembled?
- What specific generation steps are needed?
- What assets are required and in what sequence?
- What assembly steps must be performed?
- What QA checks apply?
- What output files will be produced?

## 7.2. Planning Inputs

- Approved Production Brief;
- Content Type specification (from `CONTENT_TYPES_SPEC.md`);
- Brand System snapshot (for brand layer parameters);
- Channel configuration (for platform-specific requirements);
- Learning Memory parameters embedded in the Brief.

## 7.3. Planning Outputs

The **Production Plan** is a structured execution roadmap containing:

### 7.3.1. Production Variant Selection

The content type defines multiple possible production variants. The
Production Brief selects the variant. Planning confirms fit and resolves
any conflicts.

| Content Type | Possible Variants | Selection Factor |
|---|---|---|
| Short Video | stock_footage, ai_visuals, user_uploaded, avatar, screen_recording | Visual layer approach defined in Brief |
| Carousel | educational, storytelling, list_tips, comparison | Content angle defined in Brief |
| Text Post | social_post, article, thread, newsletter | Text content type defined in Brief |

### 7.3.2. Required Layers

For each content type, Planning identifies which layers are active:

**Text Content:**
```text
Layers:
    ├── text_structure    (always active)
    ├── caption_variants  (per channel)
    ├── cta_variants      (per goal and channel)
    └── metadata          (always active)
```

**Visual Content (Carousel):**
```text
Layers:
    ├── slide_structure   (always active)
    ├── visual_layer      (backgrounds, images, graphics)
    ├── text_overlay      (headlines, body text per slide)
    ├── brand_layer       (logos, colors, fonts)
    └── metadata          (always active)
```

**Video Content:**
```text
Layers:
    ├── script            (text foundation)
    ├── visual_layer      (scenes, footage, AI visuals, avatar)
    ├── audio_layer       (voiceover, music, ambient)
    ├── subtitle_layer    (text overlay, synchronized)
    ├── brand_layer       (logo, colors, watermark)
    ├── thumbnail         (cover image)
    └── metadata          (always active)
```

### 7.3.3. Asset Requirements

Planning identifies every asset needed for the production, organized
by category:

| Asset Category | Examples |
|---|---|
| Brand Assets | Logo variants, font files, color palette, slide templates |
| Media Assets | Stock footage clips, stock images, AI-generated visuals |
| Audio Assets | Voice profiles, music tracks, ambient sounds |
| Template Assets | Slide templates, thumbnail templates, overlay templates |
| Generated Assets | Text components, image prompts, script text, voiceover audio |
| User Assets | Uploaded raw footage, provided images, voice recordings |

Each asset is marked as:
- **available** — exists in Asset Library and can be selected;
- **generatable** — can be produced during the Generation stage;
- **required_external** — must be provided by the user or an external source.

### 7.3.4. Generation Steps

Planning defines the generation sequence:

```text
For Text Content:
    Step 1: Generate title / headline
    Step 2: Generate body text
    Step 3: Generate per-channel captions
    Step 4: Generate CTA variants per channel
    Step 5: Generate metadata

For Carousel:
    Step 1: Generate slide text (hook, body slides, CTA)
    Step 2: Generate or select slide visuals
    Step 3: Apply brand layer to slides
    Step 4: Generate caption per channel
    Step 5: Generate metadata

For Video:
    Step 1: Generate script (narration text)
    Step 2: Generate scene definitions
    Step 3: Generate or select visual layer (per scene)
    Step 4: Generate voiceover audio
    Step 5: Generate subtitles (from script → timed text)
    Step 6: Select and apply music
    Step 7: Generate thumbnail
    Step 8: Generate caption per channel
    Step 9: Generate metadata
```

### 7.3.5. Assembly Steps

Planning defines the assembly sequence for multi-component types:

```text
For Carousel:
    Step 1: Assemble slide 1 (hook slide)
    Step 2: Assemble slides 2–N (content slides)
    Step 3: Assemble final slide (CTA slide)
    Step 4: Apply brand consistency across all slides
    Step 5: Render final slide images

For Video:
    Step 1: Synchronize visual layer with audio timeline
    Step 2: Overlay subtitle text with timecodes
    Step 3: Apply brand layer (logo, watermark, colors)
    Step 4: Mix audio (voiceover + music + ambient)
    Step 5: Render final video
    Step 6: Render thumbnail
    Step 7: Export subtitle file (SRT)
```

### 7.3.6. QA Checks

Planning defines which QA checks apply based on content type:

| QA Category | Text | Carousel | Video |
|---|---|---|---|
| Brand QA | Yes | Yes | Yes |
| Content QA | Yes | Yes | Yes |
| Format QA | Yes | Yes | Yes |
| Channel QA | Yes | Yes | Yes |
| Technical QA | Yes | Yes | Yes |
| Compliance QA | Yes | Yes | Yes |

### 7.3.7. Expected Output Files

Planning defines the expected output manifest:

```text
For Text Social Post:
    title.txt
    body.txt
    caption_{platform}.txt        (one per target channel)
    manual_publication_checklist.txt
    metadata.json
    manifest.json

For Carousel:
    slide_01.png through slide_N.png
    caption_{platform}.txt        (one per target channel)
    metadata.json
    manifest.json
    qa_report.json

For Video:
    final_video.mp4
    thumbnail.png
    subtitles.srt
    caption_{platform}.txt        (one per target channel)
    metadata.json
    manifest.json
    qa_report.json
```

## 7.4. Planning Adapts Per Content Type

### 7.4.1. Text Content Planning

Focuses on:
- text structure (opening line → main message → bridge → CTA);
- platform caption variants (length, tone, hashtag adaptation);
- CTA variants per goal and channel.

### 7.4.2. Visual (Carousel) Content Planning

Focuses on:
- slide structure (hook slide → content slides → CTA slide);
- slide count (5–7 recommended based on Learning Memory data);
- visual layout per slide (background, text overlay, brand elements);
- visual style (brand template, illustration, photo-background, text-only).

### 7.4.3. Video Content Planning

Focuses on:
- script structure (hook → problem → value → conclusion → CTA);
- scene count and duration per scene;
- visual layer variant (stock, AI, avatar, user-uploaded, screen recording);
- audio profile selection (voice type, music genre, pacing);
- subtitle styling (font, size, color, position, timing);
- brand layer positioning (logo, watermark, website display).

---

# 8. Asset Selection Stage

## 8.1. Purpose

Asset Selection is the stage where the Production Pipeline resolves
all asset requirements identified during Planning. It examines the
Asset Library, selects appropriate assets, and generates requirements
for assets that are missing.

Asset Selection answers:

- Which available assets best match the production requirements?
- Which assets are missing and need to be generated?
- Which assets must be requested from the user?
- Are selected assets compatible with Brand System constraints?
- Are selected assets licensed for the intended use?

## 8.2. The Principle

Asset Selection must not be chaotic. It must be structured, traceable
and brand-aware.

Every asset selection decision is guided by:

1. **Brand System** — does this asset align with the brand's identity, tone and visual standards?
2. **Content Type Requirements** — does this asset meet the technical parameters (resolution, format, duration)?
3. **Channel Requirements** — is this asset compatible with the target platform?
4. **Licensing Status** — is this asset properly licensed for the intended use?
5. **Quality** — does this asset meet the quality threshold?
6. **Reusability** — can this asset be reused across multiple content items?
7. **Project Scope** — does this asset belong to the correct project?

## 8.3. Asset Types

### 8.3.1. Brand Assets

These are defined in the Brand System and are always available:

| Asset | Selection Rule |
|---|---|
| Logo (primary, secondary, light, dark) | Select variant appropriate for content background |
| Fonts (display, body) | Use brand typeface; fallback to system fonts only if brand font unavailable |
| Color palette (primary, secondary, accent, background) | Apply per brand guide |
| Slide/animation templates | Select by content type variant |
| Watermark | Apply if project configuration requires |

### 8.3.2. Media Assets

These are stored in the Asset Library:

| Asset | Selection Rule |
|---|---|
| Stock footage | Match by topic, mood, pacing, resolution, licensing tier |
| Stock images | Match by topic, style, resolution, licensing tier |
| User-uploaded footage | Select by upload date, quality assessment, scene match |
| User-uploaded images | Select by upload date, quality, composition |

### 8.3.3. Audio Assets

| Asset | Selection Rule |
|---|---|
| AI voice profiles | Select by gender, tone, pace, language match to Brief |
| Music tracks | Select by genre, mood, duration, licensing tier |
| Ambient sounds | Select by scene atmosphere match |
| User-uploaded voice | Select by upload date, quality assessment |

### 8.3.4. Template Assets

| Asset | Selection Rule |
|---|---|
| Slide templates | Select by content type variant, aspect ratio, brand match |
| Thumbnail templates | Select by content type, channel requirements |
| Overlay templates | Select by visual layer variant |
| Caption templates | Select by platform |

### 8.3.5. User Uploaded Assets

These are provided by the human operator:

| Asset | Selection Rule |
|---|---|
| Raw video footage | Quality assessed; selection based on scene match |
| Raw images | Quality assessed; selection based on composition |
| Voice recordings | Quality assessed; noise reduction applied |

### 8.3.6. Generated Assets

These do not exist yet and will be created during the Generation stage:

| Asset | Selection Rule |
|---|---|
| AI-generated imagery | Prompt defined in Generation stage; output becomes a new Asset Library entry |
| AI-generated motion | Prompt defined in Generation; output becomes a new Asset Library entry |
| Text components | Generated during Text Generation stage |
| Script text | Generated during Video Script Generation |

## 8.4. Selection Process

```text
Production Plan Asset Requirements
                │
                ▼
    ┌───────────────────────┐
    │  Check Asset Library  │
    └───────────┬───────────┘
                │
        ┌───────┴───────┐
        │ Asset exists? │
        └───┬───────┬───┘
            │       │
     YES    │       │    NO
            │       │
            ▼       ▼
    ┌───────────┐ ┌───────────────────┐
    │ Select by │ │ Can be generated? │
    │ criteria  │ └────────┬──────────┘
    └─────┬─────┘          │
          │         ┌──────┴──────┐
          │    YES  │             │  NO
          │         ▼             ▼
          │  ┌────────────┐ ┌──────────────┐
          │  │ Create     │ │ Create       │
          │  │ Generation │ │ Asset        │
          │  │ Task       │ │ Requirement  │
          │  └─────┬──────┘ │ (human/external)
          │        │        └──────────────┘
          │        │
          ▼        ▼
    ┌───────────────────────┐
    │   SelectedAsset set   │
    │   + Generation tasks  │
    │   + Asset Requirements│
    └───────────────────────┘
```

## 8.5. Missing Asset Behaviour

When an asset is missing and cannot be generated:

### 8.5.1. Asset Requirement

An **Asset Requirement** is created with:

| Field | Description |
|---|---|
| `asset_type` | Category (brand, media, audio, template) |
| `asset_description` | What is needed and why |
| `required_resolution` | Minimum quality spec |
| `required_format` | File format |
| `required_duration` | Length (for video/audio) |
| `licensing_required` | Rights needed |
| `used_in_content_item` | Which content item requires it |
| `used_in_layer` | Which production layer needs it |
| `blocking` | Whether production can proceed without it |

### 8.5.2. Behaviour by Severity

```text
Blocking asset missing:
    → Production pauses.
    → Asset Requirement generated.
    → Human operator notified.
    → Production resumes when asset is provided.

Non-blocking asset missing:
    → Production continues with fallback or placeholder.
    → Warning logged in QA report.
    → Asset Requirement generated for future fulfillment.
```

## 8.6. Asset Selection Record

Every asset selection is recorded for traceability:

| Field | Description |
|---|---|
| `asset_id` | Reference to the selected asset |
| `selected_for_content_item` | Which content item uses it |
| `selected_for_layer` | Which production layer (visual, audio, brand, etc.) |
| `selection_reason` | Why this asset was chosen |
| `alternatives_considered` | Other assets that were evaluated |
| `selection_timestamp` | When the asset was selected |
| `licensing_status` | Current licensing state |
| `quality_assessment` | Quality check result |

---

# 9. Generation Stage

## 9.1. Purpose

Generation is the stage where content components that do not already
exist are created. It transforms the Production Brief parameters into
concrete text, visual specifications, audio, and other components.

Generation answers:

- What text content should be produced (headlines, body, captions, CTAs)?
- What visual specifications should guide image/video generation?
- What script should drive video narration?
- What audio should be synthesized (voiceover)?

## 9.2. The Principle

> Generation performs a production task defined by the Brief. It does
> not alter the strategic goal.

Generation is a tool execution phase. The Production Brief defines what
to generate. Generation produces the defined output. It does not
reinterpret goals, change target audiences, or modify the content angle.

If generation encounters a conflict (e.g., the requested tone conflicts
with brand restrictions), it escalates — it does not silently adjust
the Brief.

## 9.3. Generation by Content Type Category

### 9.3.1. Text Content Generation

**Components produced:**

| Component | Description |
|---|---|
| Title / Headline | Attention-capturing opening text |
| Body text | Main message content, structured per Brief |
| Bridge text | Transition between main message and CTA |
| CTA variants | Call-to-action text per channel and goal |
| Caption variants | Per-platform caption with appropriate length, tone, hashtags |
| Hashtags | Platform-specific hashtag sets |
| Metadata | Title, description, content context for metadata.json |

**Generation parameters** (from Production Brief or Brand System):

- tone of voice;
- character length constraints per platform;
- target audience segment;
- content objective (educate, inspire, entertain, convert);
- key message;
- CTA strategy per goal;
- brand restrictions (forbidden claims, formulations);
- hashtag strategy per channel.

**Structure for Text Social Post:**

```text
Generated output:
    Opening line (hook)
        ↓
    Main message (body, 2–4 paragraphs)
        ↓
    Bridge (transition to CTA)
        ↓
    CTA (channel-appropriate call to action)
        ↓
    Hashtags (channel-appropriate count and selection)
```

For each target channel, a platform-adapted caption variant is generated.

### 9.3.2. Visual (Carousel) Content Generation

**Components produced:**

| Component | Description |
|---|---|
| Slide text per slide | Headline and body text for each slide |
| Image prompts / specs | Specifications for AI-generated or selected images per slide |
| Slide layout definitions | Layout structure for each slide |
| Caption variants | Per-platform caption text |
| Hashtags | Platform-specific hashtag sets |
| Slide metadata | Slide-by-slide structure description |

**Slide text generation:**

```text
Slide 1 (Hook):
    Visual: bold, simple, high-contrast
    Text: short headline (3–7 words)
    Purpose: capture attention, frame topic

Slides 2–6 (Value Delivery):
    Visual: consistent style, varied layout
    Text: one concept per slide, 2–3 short lines
    Purpose: deliver core content in digestible chunks

Slide 7 (CTA):
    Visual: brand-consistent, high-visibility
    Text: clear instruction (Save, Follow, Comment, Link in bio)
    Purpose: drive specific audience action
```

**Image prompt generation:**

For each slide that requires a visual, Generation produces an image
prompt or visual specification that describes:

- subject matter relevant to slide content;
- visual style (photographic, illustration, abstract);
- brand colors and tone;
- composition guidelines;
- resolution and aspect ratio.

These prompts are consumed by the Assembly stage which invokes
actual image generation or selection tools.

### 9.3.3. Video Content Generation

**Components produced:**

| Component | Description |
|---|---|
| Script text | Full narration script with timing cues |
| Scene definitions | Per-scene visual description and duration |
| Visual specifications | Per-scene footage/AI visual requirements |
| Image/video prompts | Specifications for AI-generated or selected visuals per scene |
| Voiceover text | Narration text formatted for voice synthesis |
| Subtitle text | Script broken into timed subtitle phrases |
| Thumbnail specification | Cover image composition description |
| Caption variants | Per-platform caption text |
| Hashtags | Platform-specific hashtag sets |

**Script generation structure:**

```text
Hook (0–3 seconds):
    "Are you spending 10+ hours on manual tasks every week?"
    Purpose: capture attention in first 3 seconds.

Problem / Context (3–15 seconds):
    "Most small business owners waste time on repetitive tasks
     that AI can handle in minutes."
    Purpose: establish relevance and frame the topic.

Value Delivery (15–60 seconds):
    "Here are 3 AI tools that can automate your weekly workflow:
     1. [Tool name] — [what it does]
     2. [Tool name] — [what it does]
     3. [Tool name] — [what it does]"
    Purpose: deliver the core content in clear, digestible beats.

Conclusion / Recap (60–75 seconds):
    "These three tools can save you 10+ hours every week.
     The key is starting with one and building from there."
    Purpose: summarize and reinforce the main message.

CTA (75–90 seconds):
    "Save this video for later. Follow for more practical AI tips.
     Link in bio for the full tool comparison."
    Purpose: drive specific audience action.
```

**Voiceover generation parameters:**

- Voice profile (gender, age, tone from Brand System or Brief);
- Pace (words per minute);
- Emphasis markers (words to stress);
- Pause markers (beat points between sections);
- Language (from Project Settings).

**Subtitle generation:**

Subtitles are generated by breaking the script into timed phrases:

```text
Script: "Here are 3 AI tools that can automate your weekly workflow."

Subtitles:
    [00:15.0 → 00:17.5] "Here are 3 AI tools"
    [00:17.5 → 00:19.0] "that can automate"
    [00:19.0 → 00:21.0] "your weekly workflow."
```

Per-phrase parameters:
- text content;
- start timecode;
- end timecode;
- emphasis words (in brand accent color);
- positioning (bottom third default).

## 9.4. Generation Quality Rules

Generation must respect:

1. **Brand Restrictions** — generated text must pass restriction filter
   before proceeding to Assembly;
2. **Tone Consistency** — generated content must match the defined tone
   of voice;
3. **Goal Alignment** — generated content must serve the specified
   business goal;
4. **Audience Appropriateness** — generated content must be suitable for
   the target audience segment;
5. **Platform Compatibility** — generated content must respect channel
   constraints (length, format).

If generation produces content that violates any of these rules, the
content is flagged and either auto-corrected (if the violation is
minor) or escalated for human review.

## 9.5. Generation and Learning Memory

Generation produces a **generation context record** that captures:

- which generation method was used (text prompt, AI model, template);
- which parameters were applied;
- which brand context was active;
- which content type and variant were selected.

This record is included in the Production Snapshot for future
Learning Memory correlation — enabling the system to understand
which generation approaches produce the best-performing content.

---

# 10. Assembly Stage

## 10.1. Purpose

Assembly is the stage where generated components and selected assets
are combined into a complete, coherent content output.

Assembly answers:

- How do the components fit together into the final content unit?
- Is the structure complete and coherent?
- Are all layers present and correctly positioned?
- Is the brand layer consistently applied?
- Is the output ready for QA?

## 10.2. The Principle

> Assembly should be deterministic and tool-driven where possible.

Assembly follows a defined structure per content type. It is not a
creative stage. It is a construction stage — components are placed
according to the content type specification and the Production Plan.

## 10.3. Assembly by Content Type

### 10.3.1. Text Content Assembly

```text
Assembly Steps:
    Step 1: Combine title + body + bridge into complete text
    Step 2: Insert CTA at the defined position
    Step 3: Format for target platform (paragraph breaks, emoji, mentions)
    Step 4: Attach per-channel caption variant
    Step 5: Attach hashtags per channel
    Step 6: Generate metadata (title, description, timestamps, version)
```

**Assembled output structure:**

```text
ContentItem (text_social_post):
    ├── title
    ├── body
    ├── captions:
    │   ├── telegram
    │   ├── linkedin
    │   └── instagram
    ├── hashtags:
    │   ├── telegram (0-5)
    │   ├── linkedin (3-5)
    │   └── instagram (5-15)
    └── metadata
```

### 10.3.2. Carousel Assembly

```text
Assembly Steps:
    Step 1: Load slide template or layout definition
    Step 2: For each slide:
        2a: Apply background (brand color, image or gradient)
        2b: Place text overlay (headline + optional body)
        2c: Place visual element (icon, illustration, photo, diagram)
        2d: Place brand element (logo on first and last slides)
    Step 3: Verify slide-to-slide consistency (colors, fonts, spacing)
    Step 4: Verify slide count matches Production Plan
    Step 5: Render each slide as final image file
    Step 6: Generate caption per channel
    Step 7: Generate metadata
```

**Assembled output structure:**

```text
ContentItem (carousel):
    ├── slides:
    │   ├── slide_01.png (hook)
    │   ├── slide_02.png (content)
    │   ├── slide_03.png (content)
    │   ├── slide_04.png (content)
    │   ├── slide_05.png (content)
    │   ├── slide_06.png (content)
    │   └── slide_07.png (CTA)
    ├── captions:
    │   ├── linkedin
    │   └── instagram
    ├── hashtags:
    │   ├── linkedin (3-5)
    │   └── instagram (5-15)
    └── metadata
```

### 10.3.3. Video Assembly

```text
Assembly Steps:
    Step 1: Load visual layer per scene:
        1a: Stock footage clips → sequenced per scene timeline
        1b: AI visuals → rendered per scene specification
        1c: Avatar presenter → positioned per scene layout
        1d: User footage → trimmed and placed per scene
    Step 2: Load audio layer:
        2a: Voiceover → synchronized to scene timeline
        2b: Music → mixed under voiceover with ducking
        2c: Ambient → blended at low level
    Step 3: Apply subtitle layer:
        3a: Place subtitle text per timecode
        3b: Style with brand font, color, background
        3c: Add emphasis styling to key words
    Step 4: Apply brand layer:
        4a: Logo → positioned (corner), sized, opacity set
        4b: Website/handle → displayed at defined intervals
        4c: Watermark → applied if configured
        4d: Colors → applied to text backgrounds, transitions
    Step 5: Mix audio:
        5a: Normalize voiceover level
        5b: Set music-to-voice ratio
        5c: Apply fade in/out at start/end of CTA
    Step 6: Render final video file
    Step 7: Extract thumbnail frame
    Step 8: Export subtitle file (SRT)
    Step 9: Generate caption per channel
    Step 10: Generate metadata
```

**Assembled output structure:**

```text
ContentItem (short_vertical_video):
    ├── final_video.mp4
    ├── thumbnail.png
    ├── subtitles.srt
    ├── captions:
    │   ├── tiktok
    │   ├── instagram
    │   └── youtube_shorts
    ├── hashtags:
    │   ├── tiktok
    │   ├── instagram
    │   └── youtube_shorts
    └── metadata
```

## 10.4. Assembly Validation

During assembly, the pipeline performs structural validation:

- All required layers are present;
- Component counts match the Production Plan (slides, scenes);
- Asset references are resolved (no broken links to missing assets);
- Brand layer is consistently applied across all elements;
- Output structure matches the content type specification.

Assembly validation failures block progression to QA. The pipeline
does not QA structurally incomplete content.

---

# 11. Quality Assurance Stage

## 11.1. Purpose

Quality Assurance is a mandatory stage in the Production Pipeline.
Every content item, regardless of type, must pass QA before it can
be exported as Distribution Ready.

QA answers:

- Does this content meet the Brand System standards?
- Does this content fulfill the Scenario goals?
- Does this content match the content type specification?
- Does this content satisfy channel requirements?
- Is this content technically valid?
- Is this content compliant with legal and brand restrictions?

## 11.2. QA is Mandatory

No content may proceed to Export Package without passing QA.

QA is not optional. QA is not a suggestion. QA is a hard gate in the
Production Pipeline.

## 11.3. QA Check Categories

### 11.3.1. Brand QA

Verifies that the content aligns with the Brand System.

| Check | Rule |
|---|---|
| Tone of voice | Content tone matches brand-defined tone (professional, casual, inspirational etc.) |
| Forbidden topics | Content contains none of the forbidden topics defined in Brand System Restrictions |
| Forbidden claims | Content makes none of the forbidden claims |
| Forbidden formulations | Content uses none of the prohibited phrasings |
| Brand consistency | Brand name, positioning and values are correctly represented |
| Allowed formulations | Content aligns with encouraged phrasings and patterns |

Reference: `BRAND_SYSTEM_SPEC.md`, Sections 5 and 8

### 11.3.2. Content QA

Verifies that the content fulfills the strategic intent.

| Check | Rule |
|---|---|
| Scenario alignment | Content structure and message match the Scenario |
| Message clarity | Key message is clearly communicated and not lost |
| Structure completeness | All structural components are present (hook, body, CTA, etc.) |
| CTA correctness | CTA matches the defined goal and audience strategy |
| Audience appropriateness | Content is suitable for the target audience segment |
| Goal alignment | Content serves the defined business goal |

### 11.3.3. Format QA

Verifies that the content matches the content type specification.

| Check | Rule |
|---|---|
| Content type requirements | All required components for the content type are present |
| Length | Text is within defined character range |
| Slide count | Carousel slide count is within specified range |
| Duration | Video length is within min/max bounds |
| Aspect ratio | Visual dimensions match the specification (9:16, 1:1, 4:5) |
| Resolution | Output meets the minimum resolution requirement |
| File format | Output files use the specified format (mp4, png, txt) |

Reference: `CONTENT_TYPES_SPEC.md`, Sections 4–8

### 11.3.4. Channel QA

Verifies that the content satisfies platform requirements.

| Check | Rule |
|---|---|
| Platform constraints | Content respects character limits, duration limits, file size limits |
| Caption length | Platform captions are within maximum character count |
| Hashtag rules | Hashtag count and style follow platform conventions |
| Media requirements | Visual/video content meets platform aspect ratio and resolution requirements |
| CTA constraints | CTA format matches platform capabilities (link in bio vs direct link) |
| Platform tone | Content tone is appropriate for the platform's culture |

Reference: `PROJECT_SETTINGS_SPEC.md`, Section 5

### 11.3.5. Technical QA

Verifies the technical integrity of the output.

| Check | Rule |
|---|---|
| Files exist | All expected output files are present and not empty |
| Metadata valid | metadata.json is present, well-formed and contains required fields |
| Manifest valid | manifest.json accurately lists all package files |
| Render available | Video files are complete and playable |
| No missing assets | All asset references in assembled content are resolved |
| File integrity | Files are not corrupted, have expected sizes, open correctly |
| Encoding | Video is correctly encoded (codec, bitrate); images are valid |

### 11.3.6. Compliance QA

Verifies legal and regulatory compliance.

| Check | Rule |
|---|---|
| Legal disclaimers | Required disclaimers are present (financial, health, legal advice) |
| Sensitive claim rules | No unverified claims about results, income, health or performance |
| Source / license status | Assets used have valid licensing for the intended use |
| Privacy compliance | Content does not expose personal data |
| Platform terms of service | Content does not violate platform content policies |
| Age restrictions | Content is appropriately marked if targeting restricted demographics |

## 11.4. QA Outcomes

### 11.4.1. Passed

```text
All checks passed. No issues found.

Action: Content proceeds directly to Export Package stage.
```

### 11.4.2. Passed with Warnings

```text
All mandatory checks passed. Non-blocking issues identified.

Examples:
    - Slide count is 8 (recommended range is 5–7) but content is complete.
    - Audio levels are slightly above recommended but within acceptable range.
    - One hashtag is suboptimal for the platform.

Action: Content proceeds to Export Package. Warnings are included in the
QA report and the Production Snapshot for Learning Memory.

Future cycles should review whether warnings correlate with lower
performance.
```

### 11.4.3. Changes Required

```text
One or more checks failed, but issues are auto-fixable or can be 
addressed without strategic re-evaluation.

Examples:
    - Body text exceeds platform character limit by 50 characters → auto-truncate.
    - Brand logo missing from final slide → auto-add.
    - Audio levels require normalization → auto-adjust.
    - Video duration is 95 seconds, platform max is 90 → auto-trim to 90.

If auto-fix is possible:
    → Auto-fix applied.
    → Re-run relevant QA checks.
    → If checks now pass, proceed with auto-fix record in QA report.

If manual fix is required:
    → Content held.
    → Human operator notified with specific change requests.
    → After changes applied, re-run QA.
    → If checks pass, proceed.
```

### 11.4.4. Failed

```text
One or more mandatory checks failed. Issues cannot be auto-fixed or
require significant rework.

Examples:
    - Content contains a forbidden claim.
    - Key message is absent from the content.
    - Video render is corrupted or unusable.
    - Brand restrictions are violated.
    - Required legal disclaimer is missing and cannot be auto-inserted.

Action:
    → Content is BLOCKED.
    → Cannot proceed to Export Package.
    → Full QA report generated with failure details.
    → Human operator notified.
    → Production may restart from Production Brief revision or
      Generation re-run.
```

## 11.5. QA Report Structure

Every QA run produces a structured QA report:

```json
{
  "qa_run_id": "qa_2026_07_08_001",
  "content_item_id": "content_042",
  "qa_timestamp": "2026-07-08T14:30:00Z",
  "qa_outcome": "passed",
  "checks": {
    "brand_qa": {
      "result": "passed",
      "checks_performed": 6,
      "issues_found": 0
    },
    "content_qa": {
      "result": "passed",
      "checks_performed": 6,
      "issues_found": 0
    },
    "format_qa": {
      "result": "passed_with_warnings",
      "checks_performed": 6,
      "issues_found": 1,
      "warnings": [
        {
          "check": "slide_count",
          "expected": "5–7",
          "actual": 8,
          "severity": "low",
          "message": "Slide count exceeds recommended range."
        }
      ]
    },
    "channel_qa": {
      "result": "passed",
      "checks_performed": 6,
      "issues_found": 0
    },
    "technical_qa": {
      "result": "passed",
      "checks_performed": 6,
      "issues_found": 0
    },
    "compliance_qa": {
      "result": "passed",
      "checks_performed": 4,
      "issues_found": 0
    }
  },
  "auto_fixes_applied": [],
  "requires_human_review": false,
  "human_review_required_for": []
}
```

## 11.6. QA and Pipeline Flow

```text
Assembly Complete
        │
        ▼
   ┌─────────┐
   │   QA    │
   └────┬────┘
        │
   ┌────┴────────────────────┐
   │                         │
   ▼                         ▼
Passed /                Changes Required /
Passed with Warnings    Failed
   │                         │
   ▼                         ▼
Export Package          ┌──────────────┐
                        │ Auto-fixable?│
                        └──┬───────┬───┘
                      YES  │       │  NO
                           ▼       ▼
                      Auto-fix   Human Review
                           │       │
                           ▼       ▼
                      Re-run QA  Revise or Reject
```

---

# 12. Export Package Stage

## 12.1. Purpose

The Export Package is the final production deliverable — a complete,
self-contained, verified package of content files and metadata ready
for handoff to the Distribution Layer.

The Export Package answers:

- What content was produced?
- In what formats?
- For which channels?
- With what quality results?
- How should it be published?

## 12.2. Export Package is the Production Boundary

The Production Pipeline's last action is assembling the Export Package.
Once the package is assembled and verified, Production's responsibility
ends. The package is handed to Distribution.

Production does not publish. Production does not schedule. Production
does not track post-publication performance. Production delivers a
complete, verified package.

## 12.3. Current Foundation MVP Export Package

The current Foundation MVP defines `ExportPackage v1` for
`text_social_post`:

```text
ExportPackage v1:
    ├── title.txt
    ├── body.txt
    ├── caption_{platform}.txt
    ├── manual_publication_checklist.txt
    ├── metadata.json
    └── manifest.json
```

Reference: `PIPELINES_SPEC.md`, Section 6

This structure is the validated baseline. The Production Pipeline
Specification extends it conceptually for future content types without
breaking the current structure.

## 12.4. Future Extended Export Package Structure

Future content types will produce richer Export Packages. The
extended structure is designed as a superset of the current MVP:

```text
ExportPackage (extended):
    │
    ├── content/
    │   ├── text/                          (text content files)
    │   │   ├── title.txt
    │   │   └── body.txt
    │   │
    │   ├── media/                         (visual and audio files)
    │   │   ├── images/
    │   │   │   ├── slide_01.png
    │   │   │   ├── slide_02.png
    │   │   │   └── thumbnail.png
    │   │   ├── video/
    │   │   │   └── final_video.mp4
    │   │   └── audio/
    │   │       └── voiceover.mp3
    │   │
    │   └── subtitles/
    │       └── subtitles.srt
    │
    ├── channels/                          (per-channel content)
    │   ├── linkedin/
    │   │   ├── caption_linkedin.txt
    │   │   └── hashtags_linkedin.txt
    │   ├── instagram/
    │   │   ├── caption_instagram.txt
    │   │   └── hashtags_instagram.txt
    │   └── tiktok/
    │       ├── caption_tiktok.txt
    │       └── hashtags_tiktok.txt
    │
    ├── qa/
    │   └── qa_report.json                 (QA results)
    │
    ├── production/
    │   └── production_snapshot.json        (production context for Learning Memory)
    │
    ├── links/
    │   └── utm_links.json                 (UTM-tagged URLs if applicable)
    │
    ├── publication/
    │   ├── publication_checklist.txt       (manual publication guide)
    │   └── channel_schedule.json           (suggested publication timing)
    │
    ├── metadata.json                       (content, brand, version metadata)
    └── manifest.json                       (complete file listing with checksums)
```

## 12.5. Current MVP Compatibility

The current `text_social_post` Export Package maps cleanly into this
future structure:

```text
Current MVP output              →  Future structure location
─────────────────────────────────────────────────────────────
title.txt                       →  content/text/title.txt
body.txt                        →  content/text/body.txt
caption_{platform}.txt          →  channels/{platform}/caption_{platform}.txt
manual_publication_checklist.txt → publication/publication_checklist.txt
metadata.json                   →  metadata.json (root)
manifest.json                   →  manifest.json (root)
```

This mapping ensures that the current Foundation MVP output is a
valid subset of the future Export Package — nothing breaks, the
current structure is simply nested within the extended structure.

## 12.6. Metadata Content

The `metadata.json` file contains:

```json
{
  "content_item_id": "content_042",
  "project_id": "project_001",
  "content_type": "carousel",
  "production_variant": "educational_carousel",
  "content_title": "3 AI Tools to Save 10 Hours Per Week",
  "content_description": "Educational carousel about AI automation tools for entrepreneurs.",
  "target_audience": "entrepreneurs",
  "business_goal": "awareness",
  "content_objective": "educate",
  "content_angle": "educational",
  "target_channels": ["linkedin", "instagram"],
  "brand_system_version_used": "1.0",
  "project_settings_version": "1.0",
  "language": "en",
  "created_at": "2026-07-08T14:00:00Z",
  "exported_at": "2026-07-08T14:30:00Z",
  "production_brief_id": "brief_042",
  "production_plan_id": "plan_042",
  "qa_run_id": "qa_2026_07_08_001",
  "qa_outcome": "passed",
  "version": "1.0"
}
```

## 12.7. Manifest Content

The `manifest.json` file contains a complete inventory:

```json
{
  "package_id": "export_content_042_v1",
  "content_item_id": "content_042",
  "exported_at": "2026-07-08T14:30:00Z",
  "file_count": 14,
  "total_size_bytes": 45200000,
  "files": [
    {
      "path": "content/text/title.txt",
      "size_bytes": 156,
      "checksum_sha256": "abc123...",
      "format": "text/plain"
    },
    {
      "path": "channels/linkedin/caption_linkedin.txt",
      "size_bytes": 894,
      "checksum_sha256": "def456...",
      "format": "text/plain"
    },
    {
      "path": "content/media/images/slide_01.png",
      "size_bytes": 245000,
      "checksum_sha256": "ghi789...",
      "format": "image/png",
      "dimensions": "1080x1080"
    }
  ],
  "qa_report_included": true,
  "production_snapshot_included": true
}
```

---

# 13. Distribution Ready State

## 13.1. Definition

**Distribution Ready** is the state of an Export Package that has
passed all required quality gates and is complete for handoff to the
Distribution Layer.

## 13.2. Distribution Ready Criteria

An Export Package is Distribution Ready when:

1. **Package is assembled** — all files defined in the Production Plan
   are present and accounted for in the manifest.

2. **Required files exist** — content files, captions, media, metadata
   and manifest are present, non-empty and valid.

3. **QA is passed or passed with acceptable warnings** — the QA report
   shows passed or passed_with_warnings outcome. Changes_required and
   failed outcomes block Distribution Ready status.

4. **Channel-specific requirements are met** — each target channel has
   its required files (caption, hashtag, appropriate media format).

5. **Package is internally consistent** — manifest.json lists all files
   accurately; metadata.json references correct entity IDs; file checksums
   match; no stale or orphaned files.

## 13.3. Distribution Ready Does NOT Mean Published

```text
Distribution Ready:
    "The package is complete, verified and ready to be published."

Published:
    "The content has been delivered to the target platform and is live."

These are different states. Distribution Ready is the Production
Pipeline's final state. Published is the Distribution Layer's state.
```

## 13.4. Handoff to Distribution Layer

When the Export Package reaches Distribution Ready:

1. The Production Pipeline creates a Production Snapshot (see Section 20).
2. The Production Pipeline marks the ContentItem as `exported` (respecting
   existing Foundation MVP statuses).
3. The Distribution Layer receives the Export Package path and metadata.
4. The Distribution Layer begins its workflow: publication preparation,
   scheduling, channel delivery.
5. Production Pipeline responsibility ends.

Reference: `SYSTEM_ARCHITECTURE.md`, Section 9; `PIPELINES_SPEC.md`, Section 5.4

---

# 14. Production Pipeline by Content Type

## 14.1. Overview

This section describes the specific production path for each content
type defined in `CONTENT_TYPES_SPEC.md`. It does not duplicate the
content type definitions themselves — it describes the production
execution path.

## 14.2. Production Path Diagrams

### 14.2.1. Text Social Post (Current Foundation MVP)

```text
Scenario
    ↓
Production Brief     → content_type: text_social_post
    ↓
Production Plan      → text structure, channel caption plan
    ↓
Asset Requirements   → brand logo (optional), brand fonts (future)
    ↓
Asset Selection      → minimal (text-only current MVP)
    ↓
Generation           → title, body, bridge, CTA, captions, hashtags
    ↓
Assembly             → combine text components, format per channel
    ↓
QA                   → brand, content, format, channel, technical, compliance
    ↓
Export Package       → title.txt, body.txt, caption_{platform}.txt,
                       manual_publication_checklist.txt,
                       metadata.json, manifest.json
    ↓
Distribution Ready
```

### 14.2.2. Long-Form Article

```text
Scenario
    ↓
Production Brief     → content_type: long_form_article
    ↓
Production Plan      → headline, introduction, sections, conclusion, CTA
    ↓
Asset Requirements   → brand logo, featured image (optional)
    ↓
Asset Selection      → brand assets, featured image from library
    ↓
Generation           → headline, intro, 3–5 body sections, conclusion, CTA
    ↓
Assembly             → structure article, apply formatting, metadata
    ↓
QA                   → brand, content, format, channel, technical, compliance
    ↓
Export Package       → article.md or article.txt, metadata.json, manifest.json
    ↓
Distribution Ready
```

### 14.2.3. Carousel

```text
Scenario
    ↓
Production Brief     → content_type: carousel, variant: educational/...
    ↓
Production Plan      → slide structure, count, visual style
    ↓
Asset Requirements   → brand logos, fonts, slide template, images
    ↓
Asset Selection      → brand assets, template, images (library or generate)
    ↓
Generation           → slide text per slide, image prompts, captions, hashtags
    ↓
Assembly             → construct slides, apply brand layer, render PNGs
    ↓
QA                   → brand, content, format, channel, technical, compliance
    ↓
Export Package       → slide_01.png → slide_N.png, captions, metadata, manifest
    ↓
Distribution Ready
```

### 14.2.4. Infographic

```text
Scenario
    ↓
Production Brief     → content_type: infographic
    ↓
Production Plan      → visual structure, data points, sections
    ↓
Asset Requirements   → brand assets, icons, charts, data visuals
    ↓
Asset Selection      → brand assets, icons from library, generate charts
    ↓
Generation           → text sections, data visualizations, layout text
    ↓
Assembly             → compose infographic layout, render final image
    ↓
QA                   → brand, content, format, channel, technical, compliance
    ↓
Export Package       → infographic.png, metadata.json, manifest.json
    ↓
Distribution Ready
```

### 14.2.5. Short Vertical Video

```text
Scenario
    ↓
Production Brief     → content_type: short_vertical_video
                       variant: stock_footage / ai_visuals / avatar / etc.
    ↓
Production Plan      → script structure, scenes, layers
    ↓
Asset Requirements   → brand assets, stock footage / AI prompts, music, voice profile
    ↓
Asset Selection      → brand assets, media from library, audio from library
    ↓
Generation           → script, scene specs, visual prompts, voiceover, subtitles
    ↓
Assembly             → timeline: visual + audio + subtitles + brand layer
    ↓                   → render final video, thumbnail, SRT
    ↓
QA                   → brand, content, format, channel, technical, compliance
    ↓
Export Package       → final_video.mp4, thumbnail.png, subtitles.srt,
                       captions, metadata, manifest
    ↓
Distribution Ready
```

### 14.2.6. Educational Video

```text
Production path identical to Short Vertical Video with these differences:
    - duration typically 2–10 minutes (vs 15–90 seconds);
    - aspect ratio may be 16:9 (vs 9:16 vertical);
    - structure: introduction → chapter 1 → chapter 2 → ... → summary → CTA;
    - visual variant: often screen recording or avatar presenter;
    - target channels: YouTube, LinkedIn (vs TikTok, Instagram Reels).
```

### 14.2.7. Product Video

```text
Production path identical to Short Vertical Video with these differences:
    - structure: problem → product reveal → features → benefits → social proof → CTA;
    - visual variant: often screen recording + stock footage or user uploaded;
    - CTA intensity: higher (direct purchase or trial);
    - brand layer: more prominent product branding;
    - goal: sales or lead generation (vs awareness).
```

### 14.2.8. Avatar Video

```text
Production path identical to Short Vertical Video with these differences:
    - visual variant: explicitly avatar_presenter;
    - avatar appearance, background, style configured per project;
    - script adapted for on-camera delivery (eye contact cues, gesture notes);
    - avatar assets managed in Asset Library as reusable presenter profiles.
```

### 14.2.9. User Uploaded Footage Video

```text
Scenario
    ↓
Production Brief     → content_type: short_vertical_video
                       variant: user_uploaded_footage
    ↓
Production Plan      → script structure based on footage analysis
    ↓
Asset Requirements   → user footage (provided), brand assets, music, voice
    ↓
Asset Selection      → user footage quality assessment, brand + audio from library
    ↓
Footage Analysis     → scene detection, pacing, key moments
    ↓
Generation           → script (adapted to footage), voiceover, subtitles
    ↓
Enhancement          → color correction, audio normalization, noise reduction
    ↓
Assembly             → timeline with user footage + voiceover + subtitles + brand
    ↓                   → render final video, thumbnail, SRT
    ↓
QA                   → brand, content, format, channel, technical, compliance
    ↓
Export Package       → final_video.mp4, thumbnail.png, subtitles.srt,
                       captions, metadata, manifest
    ↓
Distribution Ready
```

---

# 15. Production Entities

## 15.1. Overview

The Production Pipeline operates on conceptual entities that structure
the production workflow. These are functional entities — they describe
the production domain, not database schemas.

These entities are architectural concepts for future implementation.
They do not replace existing Foundation MVP entities.

## 15.2. Entity Catalog

### 15.2.1. ProductionBrief

**Definition:** The formal production instruction derived from a
Scenario. Translates strategic intent into machine-actionable
production parameters.

**Lifecycle:** created → validated → approved → in_progress → completed → archived

**Key fields:** project_id, content_item_id, content_type, production_variant,
target_channels, business_goal, audience_segment, content_objective,
key_message, content_angle, tone_of_voice, brand_restrictions,
required_assets, required_output_formats, qa_requirements, export_requirements

### 15.2.2. ProductionPlan

**Definition:** The structured execution roadmap produced by the
Production Planning stage. Decomposes the Production Brief into
concrete steps.

**Lifecycle:** created → in_progress → completed

**Key fields:** production_variant, required_layers, asset_requirements,
generation_steps, assembly_steps, qa_checklist, expected_output_files

### 15.2.3. AssetRequirement

**Definition:** A specification for an asset needed by production that
is not currently available in the Asset Library.

**Lifecycle:** open → fulfilled → cancelled

**Key fields:** asset_type, asset_description, required_resolution,
required_format, required_duration, licensing_required,
used_in_content_item, used_in_layer, blocking (bool)

### 15.2.4. SelectedAsset

**Definition:** An asset from the Asset Library that has been selected
for use in the current production run.

**Key fields:** asset_id, selected_for_content_item, selected_for_layer,
selection_reason, alternatives_considered, selection_timestamp,
licensing_status, quality_assessment

### 15.2.5. GeneratedComponent

**Definition:** A content component produced by the Generation stage —
text, image prompt, script, voiceover audio, subtitle text.

**Key fields:** component_type, content_item_id, generation_method,
generation_parameters_used, generated_output, generation_timestamp

### 15.2.6. AssemblyPlan

**Definition:** The step-by-step assembly sequence for the content type,
produced by Production Planning and executed by the Assembly stage.

**Key fields:** content_type, assembly_steps (ordered list),
required_components, output_structure

### 15.2.7. RenderJob

**Definition:** A video or image rendering task — future/broader
production entity. Converts assembled components into final media files.

**Status:** Not required for current `text_social_post` MVP. Reserved for
future visual and video content type production.

**Key fields:** render_type (video, image), input_components, output_format,
resolution, duration, render_status, output_file_path

### 15.2.8. OutputFile

**Definition:** A file produced by the Production Pipeline and included
in the Export Package.

**Status:** Exists in current MVP as the files in `ExportPackage v1`.
Future content types extend the set of possible OutputFiles.

**Key fields:** file_path, file_format, file_size, checksum,
associated_layer, associated_channel

### 15.2.9. QAResult

**Definition:** The structured result of a Quality Assurance run.

**Key fields:** qa_run_id, content_item_id, qa_timestamp, qa_outcome,
checks (per category), auto_fixes_applied, requires_human_review

### 15.2.10. ExportPackage

**Definition:** The complete, verified content bundle ready for
Distribution — existing Foundation MVP entity extended conceptually.

**Status:** Implemented in Foundation MVP as `ExportPackage v1`.
Extended structure described in Section 12.4 for future content types.

### 15.2.11. ProductionSnapshot

**Definition:** A capture of the complete production context — all
decisions, parameters, assets and outcomes — stored alongside the
Export Package for future Learning Memory correlation.

**Key fields:** content_item_id, production_brief_snapshot,
production_plan_snapshot, assets_used, generation_methods_used,
assembly_structure, qa_report, export_metadata, version_snapshot

## 15.3. Entity Relationships

```text
ProductionBrief (1) ──────────→ (1) ContentItem (Foundation MVP)
        │
        │ 1:1
        ▼
ProductionPlan (1) ──────────→ (N) AssetRequirement
        │                              │
        │                              │ fulfilled by
        │                              ▼
        │                       (N) SelectedAsset
        │
        │ defines
        ▼
(N) GeneratedComponent ────→ used in ──→ AssemblyPlan (1)
                                              │
                                              │ produces
                                              ▼
                                      (N) OutputFile
                                              │
                                              │ included in
                                              ▼
                                      ExportPackage (1)
                                              │
                                              │ validated by
                                              ▼
                                         QAResult (1)
                                              │
                                              │ captured in
                                              ▼
                                    ProductionSnapshot (1)
```

---

# 16. Production States and Transitions

## 16.1. Purpose

Production states describe the lifecycle of a content item as it
progresses through the Production Pipeline. These are conceptual
states for the production domain — they do not conflict with existing
ContentItem, Publication or MetricSnapshot statuses.

## 16.2. Production-Scoped States

These states describe the production process only. They are distinct
from ContentItem lifecycle statuses defined in the Foundation MVP.

```text
draft
    │  Production Brief created but not yet validated
    ↓
planned
    │  Production Plan created, assets identified
    ↓
assets_required
    │  Missing assets identified, requirements generated
    │  Production may be paused if blocking assets are missing
    ↓
assets_ready
    │  All required assets available or generated
    ↓
generating
    │  Text, visual specs, scripts, voiceover being produced
    ↓
generated
    │  All content components produced
    ↓
assembling
    │  Components being combined into complete content
    ↓
assembled
    │  Content structurally complete, ready for QA
    ↓
qa_pending
    │  Content queued for Quality Assurance
    ↓
qa_passed
    │  All QA checks passed (or passed with acceptable warnings)
    ↓
changes_required
    │  QA found issues requiring revision before export
    │  → may return to generating or assembling
    ↓
failed
    │  QA found blocking issues; content cannot proceed
    │  → requires human intervention or Production Brief revision
    ↓
exported
    │  Export Package assembled and verified
    ↓
distribution_ready
    │  Package complete and ready for Distribution Layer handoff
```

## 16.3. State Transition Rules

```text
draft → planned:
    Trigger: Production Brief validated and approved.

planned → assets_required:
    Trigger: Production Plan identifies asset needs.

assets_required → assets_ready:
    Trigger: All asset requirements fulfilled (selected, generated
            or externally provided).

planned → assets_ready:
    Trigger: No assets required (e.g. text-only content).

assets_ready → generating:
    Trigger: All assets available; begin generation.

generating → generated:
    Trigger: All generation steps completed successfully.

generated → assembling:
    Trigger: All components ready; begin assembly.

assembling → assembled:
    Trigger: Assembly completed; structure validated.

assembled → qa_pending:
    Trigger: Content handed to QA stage.

qa_pending → qa_passed:
    Trigger: QA outcome is passed or passed_with_warnings.

qa_pending → changes_required:
    Trigger: QA outcome is changes_required.

qa_pending → failed:
    Trigger: QA outcome is failed.

changes_required → generating / assembling:
    Trigger: Required changes applied; re-enter appropriate stage.

qa_passed → exported:
    Trigger: QA passed; Export Package assembled.

exported → distribution_ready:
    Trigger: Package integrity verified; manifest validated.

failed → draft:
    Trigger: Production Brief revised; restart production.
```

## 16.4. Relationship to ContentItem Statuses

The Foundation MVP defines ContentItem statuses (see `SYSTEM_ARCHITECTURE.md`,
Section 16.1):

```text
draft, needs_review, approved, rejected, changes_requested,
exported, scheduled, published, analyzed, archived, failed
```

Production states operate within the production portion of the
ContentItem lifecycle. They do not duplicate or conflict with
ContentItem statuses:

```text
ContentItem status: draft
    │  Production may begin (Production Brief created)
    │  Production state: draft → planned → assets_required → ...

ContentItem status: exported
    │  Production complete; ExportPackage assembled
    │  Production state: exported → distribution_ready
```

Production states provide internal granularity within the ContentItem
lifecycle — they describe what is happening inside production while
the ContentItem transitions from `draft` to `exported`.

---

# 17. Error Handling

## 17.1. The Principle

Every production error must be structured, actionable and traceable.

An error is not a log line. An error includes context, severity and
a recommended action. Errors that block progression must surface to
the operator with clear resolution guidance.

## 17.2. Error Structure

Every production error includes:

| Field | Description |
|---|---|
| `error_code` | Unique error identifier |
| `project_id` | Project context |
| `related_entity` | Entity type and ID involved (ContentItem, Asset, etc.) |
| `stage` | Which production stage encountered the error |
| `severity` | blocking, warning, info |
| `message` | Human-readable error description |
| `details` | Technical details (stack trace, invalid values, expected vs actual) |
| `recommended_action` | What the operator or system should do to resolve |

## 17.3. Production Error Catalog

### 17.3.1. missing_asset

```text
Code: PROD_ERR_MISSING_ASSET
Stage: Asset Selection
Severity: blocking or warning (depending on asset criticality)
Related Entity: AssetRequirement

Message: "Required asset '{asset_type}' is not available in the Asset
          Library and cannot be auto-generated."

Recommended Action:
    - If blocking: "Upload the required asset or adjust the Production
      Brief to use available alternatives."
    - If non-blocking: "Production will proceed with a placeholder.
      Upload the asset when available for improved quality."
```

### 17.3.2. invalid_brand_context

```text
Code: PROD_ERR_INVALID_BRAND_CONTEXT
Stage: Production Brief validation, Generation, QA
Severity: blocking
Related Entity: ProductionBrief, ContentItem

Message: "Brand System context is incomplete or missing required
          fields: {missing_fields}."

Recommended Action:
    "Complete the Brand System configuration for this project before
     proceeding with production."
```

### 17.3.3. unsupported_content_type

```text
Code: PROD_ERR_UNSUPPORTED_CONTENT_TYPE
Stage: Production Planning
Severity: blocking
Related Entity: ProductionBrief

Message: "Content type '{content_type}' is not enabled for this project
          or not supported by the current production capabilities."

Recommended Action:
    "Enable the content type in Project Settings or select a supported
     content type."
```

### 17.3.4. unsupported_channel_format

```text
Code: PROD_ERR_UNSUPPORTED_CHANNEL_FORMAT
Stage: Production Planning, Channel QA
Severity: blocking
Related Entity: ProductionBrief

Message: "Channel '{platform}' does not support content format
          '{content_type}'."

Recommended Action:
    "Remove the unsupported channel from the Production Brief or select
     a compatible content format."
```

### 17.3.5. generation_failed

```text
Code: PROD_ERR_GENERATION_FAILED
Stage: Generation
Severity: blocking
Related Entity: GeneratedComponent

Message: "Generation of '{component_type}' failed. Reason: {reason}."

Recommended Action:
    "Review generation parameters. Retry generation or adjust the
     Production Brief if the component specification is unachievable."
```

### 17.3.6. render_failed

```text
Code: PROD_ERR_RENDER_FAILED
Stage: Assembly (render phase)
Severity: blocking
Related Entity: RenderJob

Message: "Render of '{output_type}' failed. Reason: {reason}.
          Render job ID: {render_job_id}."

Recommended Action:
    "Check input asset integrity, available disk space, and render
     parameters. Retry render or reduce output complexity."
```

### 17.3.7. qa_failed

```text
Code: PROD_ERR_QA_FAILED
Stage: QA
Severity: blocking
Related Entity: QAResult, ContentItem

Message: "Quality Assurance failed with outcome '{qa_outcome}'.
          {count} checks failed: {failed_checks_summary}."

Recommended Action:
    "Review the QA report. Address failed checks. For auto-fixable
     issues, trigger auto-fix. For manual issues, revise content
     and re-submit for QA."
```

### 17.3.8. export_failed

```text
Code: PROD_ERR_EXPORT_FAILED
Stage: Export Package
Severity: blocking
Related Entity: ExportPackage

Message: "Export Package assembly failed. Reason: {reason}."

Recommended Action:
    "Check output path permissions, available storage, and file
     integrity. Ensure all files listed in the manifest exist."
```

### 17.3.9. manifest_invalid

```text
Code: PROD_ERR_MANIFEST_INVALID
Stage: Export Package (validation)
Severity: blocking
Related Entity: ExportPackage

Message: "Manifest validation failed. {discrepancy_count}
          discrepancies found between manifest listing and actual files."

Recommended Action:
    "Regenerate the manifest or verify that all expected output files
     were produced. Missing files may indicate an incomplete assembly
     or generation stage."
```

## 17.4. Error Recovery

```text
Blocking error:
    → Production stage pauses.
    → Error recorded with full context.
    → Operator notified if human intervention required.
    → Production resumes from the failed stage after resolution.

Warning error:
    → Production continues.
    → Warning recorded in QA report and Production Snapshot.
    → Operator informed for awareness.

Info error:
    → Production continues.
    → Recorded for diagnostics and future Learning Memory analysis.
```

---

# 18. Human Review and Autonomy

## 18.1. Autonomy Modes in Production

The Production Pipeline operates under the same autonomy modes defined
for the overall LOOPRA system. The mode determines when human review
is required during production.

Reference: `AGENT_SYSTEM_SPEC.md`, Section 8; `BRAND_SYSTEM_SPEC.md`, Section 9

### 18.1.1. Copilot Mode

```text
Production Behaviour:
    - Production Brief requires human approval before production begins.
    - Each major production stage may require checkpoint confirmation.
    - Final Export Package requires human review before Distribution Ready.
    - QA warnings are presented for human decision.

Control Points:
    - After Production Brief creation → human approves.
    - After Generation → human reviews generated components.
    - After QA → human reviews QA report and decides on warnings.
    - Before Distribution Ready → human gives final approval.

Current Foundation MVP operates in copilot mode by default.
```

### 18.1.2. Assisted Mode

```text
Production Behaviour:
    - Production Brief auto-approved for routine content types with
      high confidence patterns.
    - Production stages execute autonomously within defined parameters.
    - Human review triggered at checkpoints:
      - after Production Brief for new/unfamiliar content types;
      - after QA if warnings exceed threshold;
      - after QA if changes_required or failed.
    - Export Packages for routine content bypass human review and
      proceed directly to Distribution Ready.

Checkpoint Triggers:
    - Content type is being used for the first time.
    - Content type variant is experimental.
    - QA warnings exceed defined threshold.
    - QA outcome is changes_required or failed.
    - Autonomy mode requires periodic review (e.g. weekly).
```

### 18.1.3. Autopilot Mode

```text
Production Behaviour:
    - Production Brief auto-approved for all content types.
    - All production stages execute autonomously.
    - QA auto-resolves warnings where auto-fix is available.
    - Only blocking failures (qa_failed, generation_failed) escalate
      to human review.
    - Low-confidence QA outcomes escalate.
    - Proximity to brand restrictions escalates.

Escalation Triggers:
    - QA outcome is failed and auto-fix is unavailable.
    - Generation produces content near a brand restriction boundary.
    - Production encounters a previously unseen error pattern.
    - Learning Memory indicates low confidence for this content type
      and variant combination.
    - Human has configured periodic review checkpoints.

Emergency Controls:
    - Human retains emergency stop at all times.
    - Human can reduce autonomy mode instantly.
    - Human can review any autonomous production decision.
    - Human can override any QA decision.
```

## 18.2. What Production Tools Must Never Do

Regardless of autonomy mode:

- Production tools must NOT modify the Production Brief without explicit
  approval or a new Brief revision;
- Production tools must NOT change the strategic goal, target audience or
  key message defined by Intelligence;
- Production tools must NOT skip QA;
- Production tools must NOT override failed QA without human authorization;
- Production tools must NOT publish content (that is Distribution Layer);
- Production tools must NOT initiate a new content cycle (that is the
  Orchestrator Agent).

## 18.3. Human Review Points Summary

| Stage | Copilot | Assisted | Autopilot |
|---|---|---|---|
| Production Brief | Human approves | Auto; human for new types | Auto |
| Asset Requirements | Human fulfills missing | Auto for available; human for missing | Auto; escalate blocking |
| Generation | Human reviews output | Auto; review if QA warns | Auto |
| Assembly | Human reviews structure | Auto | Auto |
| QA (passed) | Human reviews report | Auto | Auto |
| QA (warnings) | Human decides | Auto unless threshold exceeded | Auto if auto-fixable; escalate otherwise |
| QA (changes_required) | Human fixes | Human reviews; auto-fix if possible | Auto-fix; escalate if not auto-fixable |
| QA (failed) | Human fixes and re-runs | Human fixes and re-runs | Escalate to human |
| Export Package | Human approves | Auto for routine | Auto |
| Distribution Ready | Human gives final approval | Auto for routine | Auto |

---

# 19. Relationship with Learning Memory

## 19.1. Production Pipeline as Knowledge Provider

The Production Pipeline provides structured context to Learning Memory
beyond just the final content output. Learning Memory needs to understand
not only **what** was produced, but **how** it was produced — because
production decisions correlate with content performance.

## 19.2. The Production Snapshot

The **Production Snapshot** is a structured capture of the complete
production context, included in the Export Package and passed to
Learning Memory after the content cycle completes.

The Production Snapshot enables Learning Memory to answer:

- Which production variants produce the best-performing content?
- Which asset combinations correlate with higher engagement?
- Which generation methods produce more effective text?
- Which assembly structures drive higher completion rates?
- Which QA warnings correlate with poor performance?

## 19.3. Production Snapshot Content

```json
{
  "snapshot_id": "prod_snapshot_content_042",
  "content_item_id": "content_042",
  "snapshot_timestamp": "2026-07-08T14:30:00Z",

  "content_context": {
    "content_type": "carousel",
    "production_variant": "educational_carousel",
    "target_audience": "entrepreneurs",
    "business_goal": "awareness",
    "content_objective": "educate",
    "content_angle": "educational",
    "key_message": "AI tools can save 10+ hours per week..."
  },

  "production_context": {
    "production_brief_id": "brief_042",
    "production_plan_id": "plan_042",
    "planning_decisions": {
      "slide_count_selected": 7,
      "visual_style_selected": "brand_template_v2",
      "tone_parameters": ["professional", "practical", "encouraging"]
    }
  },

  "asset_context": {
    "assets_used": [
      {
        "asset_id": "brand_logo_light_v1",
        "asset_type": "brand_logo",
        "used_in_layer": "brand_layer"
      },
      {
        "asset_id": "slide_template_v2",
        "asset_type": "template",
        "used_in_layer": "visual_layer"
      }
    ],
    "assets_generated": [
      {
        "component_type": "slide_text",
        "generation_method": "text_generation",
        "generation_parameters": {
          "tone": "professional",
          "length": "short"
        }
      }
    ],
    "missing_assets_flagged": []
  },

  "generation_context": {
    "text_generation_method": "ai_text",
    "visual_generation_method": "template_based",
    "generation_parameters": {
      "language": "en",
      "tone_of_voice": "professional_practical",
      "target_audience_segment": "entrepreneurs"
    }
  },

  "assembly_context": {
    "assembly_structure": "educational_carousel_7_slides",
    "slide_structure": [
      "hook", "problem", "solution_1", "solution_2",
      "solution_3", "evidence", "cta"
    ],
    "brand_layer_applied": true,
    "visual_consistency_verified": true
  },

  "qa_context": {
    "qa_outcome": "passed_with_warnings",
    "warnings": [
      {
        "category": "format_qa",
        "check": "slide_count",
        "expected": "5–7",
        "actual": 7,
        "severity": "low"
      }
    ],
    "auto_fixes_applied": [],
    "human_review_conducted": false
  },

  "export_context": {
    "files_count": 14,
    "total_size_bytes": 45200000,
    "channels_exported": ["linkedin", "instagram"],
    "format_version": "1.0"
  }
}
```

## 19.4. What Learning Memory Can Extract from Production Snapshots

| Production Data | Learning Memory Use |
|---|---|
| Content type + variant | Which production variants perform best per goal and audience |
| Assets used (brand logo version, template version) | Which asset combinations correlate with better performance |
| Generation method | Which generation approaches produce more engaging text/visuals |
| Slide count / structure | Optimal structural patterns per content type |
| Assembly structure | Which structural patterns drive higher completion rates |
| QA warnings | Which warning types correlate with underperformance |
| Export metadata | Production version tracking for cross-cycle comparison |

## 19.5. Production Pipeline Does Not Query Learning Memory

The Production Pipeline receives Learning Memory recommendations as
parameters embedded in the Production Brief — already processed by
the Intelligence Layer.

Production does NOT independently query Learning Memory. This
maintains clean boundaries:

```text
Learning Memory → Intelligence Layer → Production Brief → Production Pipeline
                                          (parameters embedded)

NOT:
Learning Memory → Production Pipeline (direct query)
```

---

# 20. Relationship with Future Asset Library

## 20.1. Interface Role

The Asset Library is a future Production Layer subsystem that stores,
classifies, validates and provides assets. It will be defined in detail
in a separate document:

```
docs/04_production/ASSET_LIBRARY_SPEC.md
```

This section defines the interface role between the Production Pipeline
and the Asset Library — what the pipeline expects and what the library
provides.

## 20.2. Production Pipeline ↔ Asset Library Interface

```text
Production Pipeline                          Asset Library
─────────────────                          ─────────────
Asset Selection stage
        │
        ├── "List available assets         →  Returns asset catalog
        │    of type X matching            ←  filtered by type,
        │    parameters Y, Z"                 quality, license
        │
        ├── "Select asset A for            →  Locks asset for use
        │    content item C, layer L"      ←  Returns SelectedAsset
        │
        ├── "Store generated asset G       →  Adds to library
        │    from content item C"          ←  Returns asset_id
        │
        ├── "Check asset A license         →  Returns licensing status
        │    validity for use U"           ←  and restrictions
        │
        └── "Report missing asset          →  Creates AssetRequirement
             type X for content C"         ←  Returns requirement_id
```

## 20.3. Asset Library Responsibilities

The Asset Library is responsible for:

1. **Storage** — persistent, project-scoped storage of all asset files.
2. **Classification** — assets organized by type, project, quality tier,
   licensing status.
3. **Validation** — asset integrity checks (file exists, format valid,
   resolution meets spec).
4. **Search and Retrieval** — queryable by type, quality, license,
   content match.
5. **Provision** — delivering asset files to the Production Pipeline
   when selected.
6. **Lifecycle Management** — tracking asset usage, archiving unused
   assets, version management.

## 20.4. Production Pipeline Does NOT Own Asset Storage

The Production Pipeline does not store assets. It does not manage
asset metadata or licensing. It selects and consumes assets through
the Asset Library interface.

The Production Pipeline may generate new assets (AI imagery, audio)
which it hands to the Asset Library for storage and future reuse.

---

# 21. Relationship with Distribution Layer

## 21.1. The Handoff Boundary

The Production Pipeline ends at Distribution Ready. The Distribution
Layer begins at Distribution Ready.

This is a hard architectural boundary:

```text
PRODUCTION PIPELINE                    DISTRIBUTION LAYER
───────────────────                    ──────────────────

Prepares Export Package                Receives Export Package
Runs QA                                Previews content
Generates metadata                     Validates package for publication
Creates manifest                       Formats for platform
Marks Distribution Ready               Schedules publication
                                       Publishes to channels
                                       Records Publication entity
                                       Initiates Analytics collection

HANDOFF: ExportPackage                 HANDOFF: ExportPackage
         + metadata.json                        + metadata.json
         + manifest.json                        + manifest.json
         + QA report                            + QA report
```

## 21.2. What Production Does NOT Do

- Production does NOT publish content to any platform.
- Production does NOT schedule publication times.
- Production does NOT create Publication records.
- Production does NOT interact with platform APIs.
- Production does NOT track publication status.
- Production does NOT collect post-publication metrics.

These are Distribution Layer responsibilities.

## 21.3. What Production Provides to Distribution

Production provides:

- A complete, verified Export Package;
- Content files in platform-appropriate formats;
- Per-channel caption files;
- Hashtag sets per channel;
- Publication checklist for manual publishing (current MVP mode);
- Full metadata for the content item;
- QA report confirming content quality;
- UTM-tagged links if configured;
- Suggested schedule parameters (derived from Learning Memory, embedded in Brief).

Distribution uses these inputs to execute publication without needing
to understand how the content was produced.

## 21.4. Publication Checklist (Current MVP)

For the current manual publication mode, Production includes a
`publication_checklist.txt` that guides the human operator:

```text
Manual Publication Checklist
─────────────────────────────
Content Item: content_042
Content Type: text_social_post
Channels: telegram, linkedin

Telegram:
    [ ] Open caption_telegram.txt
    [ ] Copy text to Telegram channel
    [ ] Add hashtags from hashtags_telegram.txt (optional)
    [ ] Publish
    [ ] Copy published post URL
    [ ] Record URL in metrics system

LinkedIn:
    [ ] Open caption_linkedin.txt
    [ ] Copy text to LinkedIn post
    [ ] Add hashtags from hashtags_linkedin.txt (3-5)
    [ ] Publish
    [ ] Copy published post URL
    [ ] Record URL in metrics system
```

---

# 22. Current MVP Compatibility

## 22.1. The Preserved Baseline

The Foundation MVP defines the validated execution baseline:

```text
Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot
```

The Production Pipeline Specification does not replace this chain.
It elaborates the production portion without changing the entities
or their relationships.

## 22.2. Current MVP Mapping

| Foundation MVP | Production Pipeline Equivalent |
|---|---|
| `Idea` | Input from Intelligence Layer (future) or human (current) |
| `Scenario` | Input to Production Brief creation |
| `ContentItem` | Central entity linking all production stages |
| `ExportPackage` | Final production deliverable; extended conceptually for future types |
| `Publication` | Distribution Layer responsibility; unchanged |
| `MetricSnapshot` | Analytics Layer responsibility; unchanged |

## 22.3. Current Implemented Content Type

The Foundation MVP currently implements:

**Content Type:** `text_social_post`

**Production Path (current MVP):**
```text
Idea → Scenario → ContentItem → ExportPackage v1
```

The current export produces:
```text
title.txt
body.txt
caption_{platform}.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

This output is inspection-friendly, validation-friendly, and
manual-publication-ready.

## 22.4. Future Extension Path

The Production Pipeline Specification describes how the same
pipeline architecture extends to visual and video content types
without modifying the Foundation MVP baseline:

```text
Current:    text_social_post → ExportPackage v1

Future:     text_social_post → ExportPackage v1 (unchanged)
            carousel         → ExportPackage (extended)
            short_vertical_video → ExportPackage (extended)
            long_form_article → ExportPackage (extended)
            ...
```

The pipeline stages (Brief → Plan → Select → Generate → Assemble →
QA → Export) apply identically. Only the content type parameters
and output structure differ.

## 22.5. What Must NOT Break

When future content types are implemented:

- The `text_social_post` production path must continue to work as-is.
- The `ExportPackage v1` structure must remain valid.
- The `ContentItem` entity and its statuses must not change.
- The `smoke_loop.py` verification path must continue to pass.
- `inspect_package.py` and `validate_package.py` must remain functional.

---

# 23. Readiness Criteria

## 23.1. Production Pipeline Architectural Readiness

The Production Pipeline is considered architecturally defined when:

### Input and Output Boundaries
- Production inputs are defined (Project, Brand System, Scenario, Content Type, Channel config, Asset Library).
- Production outputs are defined (Export Package with content, captions, metadata, QA report, manifest).
- The handoff from Intelligence Layer and to Distribution Layer is clearly specified.

### Pipeline Stages
- Production Brief stage is defined as the bridge between Scenario and production execution.
- Production Planning stage is defined with variant, layer, step and QA identification.
- Asset Selection stage is defined with selection criteria and missing asset behaviour.
- Generation stage is defined by content type category (text, visual, video).
- Assembly stage is defined as deterministic component combination.
- QA stage is defined as mandatory with six check categories and four outcomes.
- Export Package stage is defined with structure compatible with current MVP.
- Distribution Ready state is defined as the final Production handoff.

### Layer Separation
- Production responsibility is separated from Intelligence (Production does not decide what to create).
- Production responsibility is separated from Distribution (Production does not publish).
- Production responsibility is separated from Analytics (Production does not measure results).
- Production responsibility is separated from Learning Memory (Production provides data, does not extract patterns).

### Content Type Integration
- Each content type from `CONTENT_TYPES_SPEC.md` has a defined production path.
- Variant-based production model is described for visual and video types.
- Channel adaptation is integrated into the production flow.

### Asset System Interface
- Asset categories are defined (brand, media, audio, template, user, generated).
- Asset Selection criteria are defined.
- Missing asset handling (Asset Requirement) is defined.
- Asset Library interface role is defined (detailed spec deferred to `ASSET_LIBRARY_SPEC.md`).

### Quality Assurance
- All six QA categories are defined (brand, content, format, channel, technical, compliance).
- QA outcomes are defined (passed, passed_with_warnings, changes_required, failed).
- Failed/changes_required content is blocked from Distribution Ready.
- QA report structure is defined.

### Export Package
- Export Package structure is compatible with current Foundation MVP.
- Extended structure for future content types is defined as a superset.
- Current `text_social_post` output maps cleanly into the extended structure.

### Learning Memory Integration
- Production Snapshot captures production context for Learning Memory.
- Production pipeline provides context without querying Learning Memory directly.

### Foundation MVP Preservation
- The Foundation MVP entity chain (Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot) is preserved.
- Current `text_social_post` export path continues to work unchanged.
- Existing verification helpers remain functional.
- No existing statuses or entities are modified.

---

# 24. Related Documents

## 24.1. Architecture Layer

```text
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers and boundaries
docs/02_architecture/PIPELINES_SPEC.md              — Current Foundation MVP pipeline
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System configuration and rules
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
```

## 24.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration specification
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
```

## 24.3. Intelligence Layer

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Full content cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Orchestrator Agent and Intelligence Module design
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content opportunity analysis and format recommendation
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory architecture and knowledge model
```

## 24.4. Production Layer

```text
docs/04_production/CONTENT_TYPES_SPEC.md            — Content type definitions, structure and assets
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — This document
docs/04_production/ASSET_LIBRARY_SPEC.md            — Asset Library specification (future)
```

## 24.5. Project Governance

```text
AGENTS.md                                            — Development rules for agents
STATE.md                                             — Current project state
```

---

# 25. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Production Layer — Production Pipeline Specification |

---

# Final Statement

The LOOPRA Production Pipeline is the deterministic manufacturing layer
of the Autonomous Marketing Operating System.

It does not decide what to create. It executes creation decisions with
precision, quality and traceability.

The pipeline transforms a strategic Scenario into a verified,
channel-ready Export Package through eight stages:

```text
Brief → Plan → Select → Generate → Assemble → QA → Export → Distribution Ready
```

Each stage has defined inputs and outputs. Each stage has defined
responsibility boundaries. Each stage can be validated independently.

The Production Pipeline operates on a simple principle:

> Production executes. Intelligence decides.

The Production Brief is the immutable contract between strategic
intent and manufacturing execution. Once approved, production follows
the Brief to completion — no reinterpretation, no strategic deviation.

Quality Assurance is mandatory. No content reaches Distribution Ready
without passing QA. Failed content is blocked, not silently released.

The Export Package is the final production deliverable — a complete,
self-contained bundle of content files, metadata, QA results and
publication instructions. It is the Production Pipeline's last act.

The pipeline preserves the Foundation MVP. The current `text_social_post`
path continues to work unchanged. Future content types extend the
pipeline without breaking the validated baseline.

The Production Pipeline provides rich context to Learning Memory
through Production Snapshots — enabling the system to correlate
production decisions with content performance across cycles.

Build LOOPRA as an evolving autonomous marketing platform.

Optimize for a clean architecture that can grow.

The Production Pipeline is the execution layer — precise, reliable,
measurable — that transforms strategic intelligence into marketing
reality.

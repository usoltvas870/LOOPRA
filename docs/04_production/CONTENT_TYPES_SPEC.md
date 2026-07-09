# CONTENT TYPES SPEC

## Version

v1.0

## Status

Active — LOOPRA Production Layer

## Purpose

This document defines the production content types of the LOOPRA
Autonomous Marketing Operating System.

It answers the central question:

> Which products does the LOOPRA Content Production System produce?

CONTENT_TYPES_SPEC.md is the production specification for content
types — executable formats the Production Layer assembles from
intelligence-driven recommendations.

It describes:

- which content formats LOOPRA supports;
- what structural components define each type;
- what parameters control production;
- what assets are consumed;
- what production variants exist.

It does NOT describe:

- content strategy or opportunity selection;
- idea generation or topic identification;
- UI components or API contracts;
- specific AI providers, models or prompts;
- code-level implementation details.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

CONTENT_TYPES_SPEC.md defines the production types LOOPRA can
create — the concrete, renderable content formats the Production
Layer assembles.

This document serves as the specification for:

- the catalogue of supported production content types;
- the structural model common to all types;
- the parameters and variants that govern production;
- the asset system that supplies production inputs;
- the adaptation model for multi-channel output;
- the quality rules that validate production output;
- the relationship with the Intelligence Layer and Learning Memory.

## 1.2. Scope

This document covers:

- LOOPRA Content Production Model;
- content type taxonomy (text, visual, video, interactive);
- universal content model;
- video content specification (structure, layers, components);
- short vertical video specification;
- carousel specification;
- text content specification;
- asset system;
- user uploaded content workflow;
- channel adaptation model;
- production quality rules;
- relationship with Production Pipeline and Foundation MVP;
- relationship with Learning Memory;
- future content types.

## 1.3. Out of Scope

This document does not cover:

- content opportunity analysis (see `CONTENT_INTELLIGENCE_SPEC.md`);
- market trend detection (see `TREND_INTELLIGENCE_SPEC.md`);
- strategic decision making (see `AGENT_SYSTEM_SPEC.md`);
- content cycle management (see `CONTENT_CYCLE_SPEC.md`);
- publishing and distribution mechanics;
- UI or API implementation;
- specific AI model selection or prompt engineering.

---

# 2. LOOPRA Content Production Model

## 2.1. The Production Chain

Content production in LOOPRA follows a layered model:

```text
Content Intelligence
    "What should we create?"
        ↓
Content Type Selection
    "Which production format fits?"
        ↓
Production Pipeline
    "How do we create it?"
        ↓
Export Package
    Ready for distribution.
```

## 2.2. Intelligence Precedes Production

Content Intelligence determines what content has strategic
potential — audience, goal, angle, format recommendation.

Content Type Selection maps the intelligence recommendation to a
concrete production format the Production Layer can execute.

The Production Pipeline assembles the output using the selected
type's structure, parameters and assets.

Reference: `CONTENT_INTELLIGENCE_SPEC.md`, Section 9

## 2.3. Foundation MVP Alignment

The Foundation MVP pipeline remains the execution backbone:

```text
Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot
```

Content Types define what a `ContentItem` can be. The pipeline
executes identically regardless of content type — the type
determines the structure, parameters and assets required.

Reference: `PIPELINES_SPEC.md`, `DATA_MODEL.md`

---

# 3. Content Type Taxonomy

## 3.1. Overview

LOOPRA classifies content types into three active categories and
one future category:

| Category | Current Status | Examples |
|---|---|---|
| Text Content | Active (Foundation MVP) | social post, article, thread, newsletter |
| Visual Content | Production Specification | single image, carousel, infographic |
| Video Content | Production Specification | short vertical video, educational video, storytelling video |
| Interactive Content | Future | quizzes, calculators, interactive experiences |

## 3.2. Text Content

Text content is the current Foundation MVP baseline.

Formats:

- **Social Post** — short-form text for social platforms (Telegram,
  Threads, LinkedIn, VK);
- **Long-Form Article** — extended text for blogs, LinkedIn articles,
  owned media;
- **Thread** — multi-post text sequence for platforms supporting
  threaded content (Threads, X, LinkedIn);
- **Newsletter** — email or digest text for owned distribution.

Current implemented format: `text_social_post`.

Reference: `CONTENT_TYPES_SPEC.md`, Section 5

## 3.3. Visual Content

Visual content combines imagery with messaging and branding.

Formats:

- **Single Image** — standalone branded visual with caption;
- **Carousel** — multi-slide visual sequence (Instagram, LinkedIn);
- **Infographic** — data-driven visual explanation.

## 3.4. Video Content

Video content is the most complex production format in LOOPRA.

Formats:

- **Short Vertical Video** — mobile-first, 9:16, 15–90 seconds
  (TikTok, Instagram Reels, YouTube Shorts);
- **Educational Video** — explanatory, instructional, longer format
  (YouTube, LinkedIn);
- **Storytelling Video** — narrative-driven content with emotional arc;
- **Product Video** — demonstration with feature focus and CTA;
- **Avatar Video** — AI-presenter-driven content;
- **Stock Footage Video** — assembled from licensed stock media.

## 3.5. Interactive Content

Future category. Reserved for:

- quizzes;
- calculators;
- interactive experiences;
- polls and assessments.

---

# 4. Universal Content Model

## 4.1. Definition

Every content type in LOOPRA conforms to a universal content model — a
common structure that all production types share and extend.

## 4.2. Content Type Object

Each content type defines:

### Identity

| Field | Description |
|---|---|
| `content_type_id` | Stable platform-level identifier (e.g. `short_vertical_video`) |
| `name` | Human-readable type name |
| `category` | Taxonomy category (text, visual, video, interactive) |

### Purpose

| Field | Description |
|---|---|
| `business_goals` | Which marketing goals this type serves (awareness, engagement, lead generation, sales, retention) |
| `audience` | Which audience segments this type is suitable for |
| `recommended_usage` | When and why to use this type |

### Structure

| Field | Description |
|---|---|
| `sections` | Text content: opening, body, CTA blocks |
| `slides` | Visual content: individual slide definitions |
| `scenes` | Video content: timed visual-audio segments |
| `frames` | Sub-components within scenes or slides |

### Assets

| Field | Description |
|---|---|
| `images` | Static visuals: photos, illustrations, AI-generated |
| `videos` | Motion media: stock footage, user uploads, generated |
| `audio` | Sound: voiceover, music, ambient, effects |
| `logos` | Brand identity elements |
| `fonts` | Typography assets |
| `brand_elements` | Colors, overlays, watermarks, templates |

### Production Parameters

| Field | Description |
|---|---|
| `duration` | Video length constraints (min/max seconds) |
| `aspect_ratio` | Visual dimensions (9:16, 16:9, 1:1, 4:5) |
| `resolution` | Output quality specification |
| `platform_requirements` | Platform-specific constraints (file size, codec, format) |

### Optimization

| Field | Description |
|---|---|
| `expected_metrics` | Which metrics this type typically drives (reach, saves, comments, link clicks) |
| `learning_feedback` | How performance data for this type feeds into Learning Memory |

## 4.3. Platform-Level Neutrality

Content types are platform-level definitions. They describe universal
structure and parameters — not project-specific configurations.

Project-specific variations (brand tone, voice, CTA text, preferred
fonts) are applied through Brand System and Project Settings, not
embedded in the content type definition.

Reference: `CONTENT_TYPES_SPEC.md`, Section 2

---

# 5. Video Content Specification

## 5.1. Video Production Architecture

Video is the most structurally complex content type in LOOPRA.

The video production architecture follows an input-process-output model:

```text
Input
    ├── Idea (strategic direction)
    ├── Scenario (content plan)
    └── Script (text foundation)

        ↓

Production
    ├── Visual Layer (scenes, footage, graphics)
    ├── Audio Layer (voiceover, music, sound)
    ├── Subtitle Layer (text overlay)
    └── Brand Layer (logo, colors, watermark)

        ↓

Output
    └── Final Video Package (rendered, export-ready)
```

## 5.2. Video Input

### 5.2.1. Idea

The Idea originates from the Intelligence Layer (Content Opportunity
→ Orchestrator Decision) or from human input in Foundation MVP mode.

The Idea provides:
- topic and theme;
- target audience;
- business goal;
- key message.

### 5.2.2. Scenario

The Scenario translates the Idea into a structured video plan:

- scene sequence and timing;
- visual direction per scene;
- audio direction per scene;
- subtitle placement and timing;
- brand element positions.

### 5.2.3. Script

The Script provides the text foundation for the video:

- spoken narration text;
- on-screen text cues;
- subtitle text with timecodes;
- CTA text and placement.

## 5.3. Video Production Layers

### 5.3.1. Visual Layer

The visual layer is the primary visual content of the video.

Production variants:

1. **Stock Footage** — licensed stock video clips assembled to match
   the script. Suitable for brands without original footage.
2. **AI Generated Visuals** — AI-generated imagery or animation,
   either as static visual backgrounds or motion sequences.
3. **User Uploaded Footage** — original video provided by the brand
   or client. LOOPRA processes, edits and enhances.
4. **Avatar Presenter** — AI-generated presenter delivering the
   script on screen. Provides a consistent on-camera presence
   without human recording.
5. **Screen Recording** — capture of software, product or process
   demonstration. Suitable for educational and product videos.

A single video may combine multiple visual variants — for example:
avatar presenter for narration paired with screen recording for
demonstration.

### 5.3.2. Audio Layer

The audio layer provides the sonic content of the video.

Components:

| Component | Description |
|---|---|
| **AI Voice** | Synthesized narration from text script. Multiple voice profiles, languages and tones available. |
| **Human Voice** | Original voice recording provided by the brand or a hired voice. LOOPRA processes from user upload. |
| **Music** | Background music track. Sourced from licensed libraries. Matched to video tone and pacing. |
| **Ambient Sound** | Environmental audio for atmosphere. Sourced from libraries or AI-generated. |

Audio mixing rules:

- voiceover level dominates music by defined ratio;
- music fades at CTA delivery;
- ambient sound supports, does not distract;
- audio levels normalized to platform standards.

### 5.3.3. Subtitle Layer

LOOPRA generates and renders subtitles automatically.

Subtitle specification:

| Parameter | Description |
|---|---|
| **Generation** | Automatic from script text or AI transcription of audio |
| **Styling** | Font, size, color, background opacity — defined by Brand System |
| **Positioning** | Bottom-center default; configurable per platform |
| **Timing** | Synchronized with audio by word or phrase |
| **Brand Rules** | Font family from brand typography. Color from brand palette. No default system fonts. |

Subtitle display modes:

- **Always On** — subtitles visible throughout the video (default
  for short vertical video);
- **Selective** — subtitles appear for key phrases or emphasis;
- **Captioned** — full captions for accessibility compliance.

### 5.3.4. Brand Layer

The brand layer overlays brand identity elements onto the video.

Components:

| Element | Description |
|---|---|
| **Logo Placement** | Position (corner, centered), size, opacity. Defined per platform and video type. |
| **Website / Handle** | Display URL or social handle at defined intervals |
| **Colors** | Brand palette applied to overlays, text backgrounds, transition effects |
| **Typography** | Brand fonts for all on-screen text |
| **Watermark** | Semi-transparent brand mark for content protection. Configurable — some brands require, others do not. |

Brand layer rules are defined in Brand System and applied
consistently across all videos for a project.

Reference: `BRAND_SYSTEM_SPEC.md`

## 5.4. Video Output

The Final Video Package includes:

- rendered video file (platform-appropriate format and resolution);
- separate audio track (for repurposing);
- subtitle file (SRT or embedded);
- metadata (duration, resolution, codec, creation context);
- thumbnail image (auto-generated or specified).

---

# 6. Short Vertical Video

## 6.1. Overview

Short vertical video is the primary video format for mobile-first
social platforms.

### Platform Targets

| Platform | Format | Max Duration |
|---|---|---|
| TikTok | 9:16 vertical | up to 10 minutes (15–90 seconds recommended) |
| Instagram Reels | 9:16 vertical | up to 90 seconds |
| YouTube Shorts | 9:16 vertical | up to 60 seconds |

### Core Parameters

| Parameter | Value |
|---|---|
| Aspect Ratio | 9:16 |
| Resolution | 1080×1920 (minimum) |
| Duration | 15–90 seconds |
| Orientation | Vertical, mobile-first |

## 6.2. Script Structure

Short vertical video follows a proven structural model:

```text
Hook (0–3 seconds)
    Capture attention immediately.
    Question, bold statement, visual surprise or pattern interrupt.
        ↓
Problem / Context (3–15 seconds)
    Establish what the video is about.
    Define the problem or frame the topic.
        ↓
Value Delivery (15–60 seconds)
    The core content. Tips, insights, demonstration or story.
    Multiple short beats with visual changes to maintain attention.
        ↓
Conclusion / Recap (60–75 seconds)
    Summarize the key takeaway.
    Reinforce the main message.
        ↓
CTA (75–90 seconds)
    Call to action. Follow, save, comment, link in bio or visit website.
```

## 6.3. Visual Layer Variants

### 6.3.1. Stock Footage Variant

Production approach:
- script is matched to relevant stock clips;
- clips are sequenced with transitions;
- text overlays reinforce key points;
- brand layer applied.

Best for: brands without original footage, volume content production,
topical content that does not require original visuals.

### 6.3.2. AI Generated Visuals Variant

Production approach:
- AI generates images or short motion clips per scene;
- visuals are stylistically consistent;
- animation applied to static visuals for motion;
- brand layer and text overlays applied.

Best for: conceptual content, abstract topics, brands that want
distinctive visual style without stock libraries.

### 6.3.3. User Uploaded Footage Variant

Production approach:
- user uploads raw video footage;
- LOOPRA analyzes content — scene detection, pacing, key moments;
- script is generated or adapted to match footage;
- subtitles, branding, music and transitions are applied;
- final render with LOOPRA production quality.

Best for: personal brands, client content, repurposing existing
video assets.

### 6.3.4. Avatar Presenter Variant

Production approach:
- AI avatar delivers the script on screen;
- avatar appearance, background and style are configurable;
- visual layer may include supporting graphics alongside avatar;
- applicable across all video content goals.

Best for: consistent presenter presence, volume content production,
brands without on-camera talent.

### 6.3.5. Screen Recording Variant

Production approach:
- screen capture of software, product or process;
- narration overlaid;
- highlights and zooms applied for emphasis;
- subtitles and branding applied.

Best for: educational content, product demonstrations, tutorials.

## 6.4. Audio Layer Specification

| Component | Production Options |
|---|---|
| **AI Voice** | Multiple profiles (gender, age, tone). Language support. Adjustable pace and emphasis. |
| **Human Voice** | Uploaded recording. LOOPRA processes for clarity, normalization, noise reduction. |
| **Music** | Licensed background track. Genre matched to video tone (energetic, calm, inspirational, professional). Volume ducking under voiceover. |
| **Ambient** | Optional environmental sound layer for immersion. |

## 6.5. Subtitle Specification

| Attribute | Specification |
|---|---|
| Generation | Automatic from script. Synchronized to audio timeline. |
| Font | From Brand System typography. No default system fonts. |
| Size | Platform-appropriate. Legible on mobile screen. |
| Color | White text with dark background or outline. Brand accent for emphasis words. |
| Position | Bottom third of frame. Adjustable to avoid visual conflicts. |
| Duration | Per word or short phrase (2–6 words at a time). Rapid display for fast-paced sections. |
| Emphasis | Key words in brand accent color or bold weight. |

## 6.6. Brand Layer Specification

| Element | Default Position | Notes |
|---|---|---|
| Logo | Top-right or bottom-right corner | Semi-transparent. Small (5–8% of frame width). |
| Website / Handle | Bottom of frame, intermittent | Displayed for 3–5 seconds at intervals. Not continuous. |
| Watermark | Center, low opacity | Optional. Configurable per project. |

---

# 7. Carousel Specification

## 7.1. Overview

Carousel is a multi-slide visual content format for platforms
supporting swipeable post sequences.

### Platform Targets

- Instagram (up to 10 slides)
- LinkedIn (up to 20 slides, document format)

## 7.2. Structure

```text
Slide 1 — Hook
    Capture attention. Frame the topic.
    Visual: bold, simple, high-contrast.
    Text: short headline (3–7 words).

Slides 2–(N-1) — Value Delivery
    Core content broken into digestible slides.
    Each slide: one idea, one visual, minimal text.
    Visual: consistent style, varied layout to maintain interest.
    Text: short bullet points or single sentences.

Slide N — CTA
    Direct call to action.
    Visual: brand-consistent, high-visibility.
    Text: clear instruction (Save, Follow, Comment, Link in bio).
```

## 7.3. Parameters

| Parameter | Specification |
|---|---|
| Number of Slides | 3–10 (5–7 recommended based on completion data) |
| Visual Style | Brand template, illustration, photo-background, or text-only |
| Text Density | Low. One concept per slide. Maximum 2–3 short lines. |
| Brand Elements | Logo on first and last slides. Brand colors throughout. Consistent typography. |

## 7.4. Production Variants

| Variant | Description |
|---|---|
| Educational Carousel | Step-by-step explanation. Structured knowledge delivery. Best for saves and authority. |
| Storytelling Carousel | Narrative arc across slides. Personal, emotional. Best for engagement and connection. |
| List / Tips Carousel | Numbered list format. "5 Ways to X", "3 Mistakes to Avoid". Best for saves and reach. |
| Comparison Carousel | Side-by-side comparison. Before/After, With/Without. Best for lead generation. |

## 7.5. Visual Construction

Each slide comprises:

- background (brand color, image or gradient);
- text overlay (headline and optional body);
- visual element (icon, illustration, photo or diagram);
- brand element (logo on first and last slides).

---

# 8. Text Content Specification

## 8.1. Overview

Text content is the current Foundation MVP baseline and the most
fundamental production type in LOOPRA.

Currently implemented format: `text_social_post`.

## 8.2. Text Content Types

### 8.2.1. Social Post

Short-form text for social platforms.

Parameters:
- length: 100–2,200 characters (platform-dependent);
- tone: defined by Brand System voice settings;
- structure: opening line → main message → bridge → CTA;
- platform adaptation: per-platform caption variants.

### 8.2.2. Long-Form Article

Extended text for blogs, LinkedIn articles, owned media.

Parameters:
- length: 800–3,000 words;
- structure: headline → introduction → body sections → conclusion → CTA;
- tone: authoritative, educational or narrative based on goal.

### 8.2.3. Thread

Multi-post text sequence.

Parameters:
- posts: 3–12 connected posts;
- structure: hook post → development posts → conclusion post;
- platform: Threads, X, LinkedIn.

### 8.2.4. Newsletter

Email or digest text.

Parameters:
- length: 300–1,500 words;
- structure: subject → greeting → main content → CTA → footer;
- tone: personal, direct, value-first.

## 8.3. Content Angles for Text

| Angle | Description | Best For |
|---|---|---|
| **Educational** | Teaching, explaining, instructing | Authority building, lead generation |
| **Storytelling** | Narrative, personal experience, case study | Engagement, connection, trust |
| **Opinion** | Perspective, stance, analysis | Thought leadership, differentiation |
| **Promotional** | Product, offer, feature | Sales, conversion |
| **Community** | Conversation starter, question, engagement prompt | Engagement, retention |

Reference: `CONTENT_INTELLIGENCE_SPEC.md`, Section 10

## 8.4. Platform Adaptation for Text

| Platform | Format | Character Limit | Style Adaptation |
|---|---|---|---|
| LinkedIn | Professional post | 3,000 | Professional tone, structured, value-first |
| Telegram | Channel post | 4,096 | Direct, personal, community-oriented |
| Threads | Thread post | 500 | Conversational, punchy, thread-friendly |
| X (Twitter) | Tweet / thread | 280 / thread | Concise, hook-driven, shareable |
| Instagram | Caption | 2,200 | Visual-first context, emoji-friendly |

## 8.5. Foundation MVP Text Structure

The current `text_social_post` format produces:

```text
Opening line
→ main message
→ optional bridge
→ CTA
```

Output files in export package:

- `title.txt`
- `body.txt`
- `caption_{platform}.txt`
- `manual_publication_checklist.txt`
- `metadata.json`
- `manifest.json`

Reference: `CONTENT_TYPES_SPEC.md`, Section 5

---

# 9. Asset System

## 9.1. Overview

LOOPRA consumes and manages assets across all content types. Assets
are the raw materials the Production Layer assembles into finished
content.

## 9.2. Brand Assets

Brand assets provide visual and tonal identity to all content.

| Asset | Description | Source |
|---|---|---|
| Logo | Primary and secondary logo variants. Light and dark background versions. | Brand System configuration |
| Fonts | Typeface files for on-screen text, subtitles, slide overlays | Brand System typography |
| Colors | Brand palette — primary, secondary, accent, background | Brand System identity |
| Templates | Reusable slide, thumbnail and overlay templates | Brand System / Project Settings |

## 9.3. Media Assets

Media assets provide visual and motion content.

| Asset | Description | Source |
|---|---|---|
| Stock Videos | Licensed stock footage clips | Stock library integration (future) |
| Stock Images | Licensed stock photography and illustrations | Stock library or bundled library |
| User Uploads | Original video, images or audio provided by the brand | User upload workflow |
| AI Generated Assets | AI-created imagery, animation or motion | AI generation tools (future) |

## 9.4. Audio Assets

Audio assets provide sonic content for video production.

| Asset | Description | Source |
|---|---|---|
| AI Voices | Synthesized narration profiles | AI voice generation (future) |
| Human Voice Recordings | Uploaded original voice audio | User upload workflow |
| Music Tracks | Licensed background music | Music library integration (future) |
| Sound Effects | Ambient and emphasis sounds | Library or AI generation (future) |

## 9.5. Asset Lifecycle

Assets move through defined states:

```text
Available — asset exists and is ready for production use
    ↓
In Use — asset is actively referenced by a content item in production
    ↓
Archived — asset is no longer used but retained for reference
```

Assets are project-scoped. Assets from one project are not shared
with another project.

---

# 10. User Uploaded Content

## 10.1. Principle

LOOPRA must support user-provided content as a first-class production
input.

Brands and clients bring their own:
- raw video footage;
- images and photography;
- voice recordings;
- existing content assets.

LOOPRA's value is not only in generating new content from scratch,
but in enhancing, adapting and professionalizing user-provided
material.

## 10.2. User Upload Workflow

```text
User Uploads Raw Content
    (video, image, audio, existing content)
        ↓
LOOPRA Analyzes Content
    - scene detection (video)
    - content classification (image)
    - audio quality assessment
    - metadata extraction
        ↓
LOOPRA Enhances Content
    - color correction (video, image)
    - audio normalization and noise reduction
    - subtitle generation (video)
    - transcription (audio → text)
        ↓
LOOPRA Applies Production Layers
    - subtitles added (video)
    - branding applied (video, image)
    - music mixed (video)
    - voiceover overlaid (video)
    - captions generated (image)
        ↓
LOOPRA Creates Platform Versions
    - platform-specific aspect ratios
    - platform-specific durations
    - platform-specific caption text
        ↓
LOOPRA Prepares Publishing Package
    - final render
    - metadata
    - publication checklist
    - export package assembled
```

## 10.3. User Upload Scenarios

### 10.3.1. Raw Video Enhancement

User provides raw video footage. LOOPRA:
- analyzes footage content and quality;
- adds subtitles from audio transcription;
- applies brand logo, colors and watermark;
- mixes background music;
- trims to optimal platform duration;
- creates multiple platform versions.

### 10.3.2. Image Branding

User provides images. LOOPRA:
- applies brand templates and overlays;
- generates caption text;
- resizes for platform requirements;
- prepares carousel from image sequence.

### 10.3.3. Voice Recording Integration

User provides voice recording. LOOPRA:
- normalizes and cleans audio;
- synchronizes with video timeline;
- generates subtitles from the recording;
- provides as audio layer for video production.

### 10.3.4. Content Repurposing

User provides existing content (article, post, presentation).
LOOPRA:
- extracts key messages;
- adapts to new format (article → carousel, article → video);
- applies brand standards;
- creates derivative content items.

## 10.4. User Upload Quality Handling

LOOPRA does not reject low-quality uploads. It processes them and
reports quality concerns:

- low resolution warning;
- poor audio quality warning;
- insufficient duration warning;
- aspect ratio mismatch warning.

The human operator decides whether to proceed with available
material or request improved uploads.

---

# 11. Content Adaptation Across Channels

## 11.1. Principle

One content direction can produce multiple platform-specific outputs.

A single `ContentItem` can generate:

```text
Base Content
    ↓
LinkedIn version — professional tone, longer text, document-friendly
    ↓
Instagram version — visual-first, shorter text, hashtag-optimized
    ↓
TikTok version — vertical video, fast-paced, trend-aligned
    ↓
Telegram version — direct, community-oriented, longer retention
    ↓
X (Twitter) version — concise, thread-friendly, share-optimized
```

## 11.2. What Adapts

| Element | Adaptation Rule |
|---|---|
| **Length** | Platform character/time limits applied. Long content truncated or summarized. |
| **Format** | Video aspect ratio adjusted. Image dimensions adapted. Text structure modified. |
| **Tone** | Professional for LinkedIn. Casual for TikTok. Direct for Telegram. |
| **CTA** | Platform-appropriate: "Link in bio" (Instagram), "Comment below" (LinkedIn), direct link (Telegram). |
| **Hashtags** | Platform-specific. None for LinkedIn (minimal). Relevant tags for Instagram and TikTok. |
| **Style** | Emoji density adjusted. Hashtag count varied. Mention format adapted. |

## 11.3. Adaptation Model

Adaptation is not a separate content item. It is a variant of the
same content item with platform-specific parameters.

The base content is created once. Platform adaptations are derived
from the base with override parameters.

```text
ContentItem (base)
    ├── adaptation: linkedin
    ├── adaptation: instagram
    ├── adaptation: tiktok
    └── adaptation: telegram
```

Each adaptation is independently exportable as part of the
`ExportPackage`.

---

# 12. Production Quality Rules

## 12.1. Quality Pipeline

Every content item passes through quality validation before export:

```text
Brand Compliance Check
    - Brand voice consistency
    - Restriction compliance
    - Forbidden topic screening
    - Logo and branding presence
        ↓
Technical Validation
    - Duration within limits
    - Resolution meets specification
    - Aspect ratio correct
    - File format appropriate
    - Audio levels normalized
        ↓
Platform Validation
    - Platform-specific constraints satisfied
    - Character limits respected
    - Format compatibility confirmed
    - Required metadata present
        ↓
Quality Check
    - Content completeness
    - Structural integrity
    - Asset references resolved
    - Export package completeness
```

## 12.2. Quality Check Outcomes

| Outcome | Action |
|---|---|
| **Pass** | Content proceeds to export |
| **Pass with Warnings** | Content proceeds; warnings logged for operator review |
| **Fail — Auto-Fixable** | System applies correction automatically (e.g., audio normalization, resolution adjustment) |
| **Fail — Requires Review** | Content held; operator notified for manual decision |

## 12.3. Mandatory Checks

Content must not be exported if:

- brand restrictions are violated;
- content references missing assets;
- resolution or duration falls below minimum thresholds;
- required metadata is absent.

---

# 13. Relationship With Production Pipeline

## 13.1. Pipeline Chain

Content Types integrate into the Foundation MVP pipeline:

```text
Content Type
    (defines structure, parameters, assets)
        ↓
Scenario
    (applies content type to the creative plan)
        ↓
Production Job
    (executes content assembly per type specification)
        ↓
ContentItem
    (the produced content unit)
        ↓
Output File
    (rendered media file)
        ↓
ExportPackage
    (bundle ready for distribution)
```

## 13.2. Foundation MVP Preservation

The Foundation MVP pipeline (`Idea → Scenario → ContentItem →
ExportPackage → Publication → MetricSnapshot`) is preserved.

Content Types extend this pipeline — they define what a
`ContentItem` can be, not how the pipeline operates. The pipeline
executes identically regardless of content type.

## 13.3. Current State

In the current Foundation MVP:

- only `text_social_post` is implemented;
- the pipeline produces text-only export packages;
- other content types are production specifications for future
  implementation.

---

# 14. Relationship With Learning Memory

## 14.1. Content Types as Learning Objects

Every content type becomes an object of learning for LOOPRA.

As content is produced and published, Learning Memory accumulates
knowledge per content type:

```text
Content Type Performance Data
    ↓
Learning Memory Analysis
    ↓
Knowledge Extraction:
    - Which formats work for which goals?
    - Which durations produce best completion rates?
    - Which structural patterns generate highest engagement?
    - Which visual variants perform best for which audiences?
    - Which CTA placements drive most conversions?
    ↓
Future Content Intelligence
    (informed by accumulated type-specific knowledge)
```

## 14.2. What LOOPRA Learns Per Content Type

| Knowledge Category | Example |
|---|---|
| Format-Goal Effectiveness | "Short vertical video performs 3x better than carousel for awareness goal with this audience" |
| Duration Optimization | "45–60 second videos produce highest completion rate; 90-second videos show 40% drop-off" |
| Structural Patterns | "Videos with hook in first 2 seconds retain 50% more viewers than videos with hook at 5 seconds" |
| Visual Variant Performance | "Stock footage outperforms AI-generated visuals for educational content; AI visuals outperform stock for storytelling" |
| Audio Preferences | "Female AI voice generates 20% higher completion than male AI voice for this audience" |
| CTA Effectiveness | "CTA placed at 75–85 seconds generates highest action rate; CTA at 15 seconds underperforms" |

## 14.3. Learning Memory Boundaries

Learning Memory optimizes content type parameters within brand
boundaries:

- Learning Memory may recommend shorter duration, not different
  brand voice;
- Learning Memory may recommend different visual variant, not
  different logo placement policy;
- Learning Memory may recommend adjusted CTA timing, not different
  CTA text that violates brand tone.

Reference: `LEARNING_MEMORY_SPEC.md`, Section 8

---

# 15. Future Content Types

## 15.1. Reserved Types

The following content types are recognized as future production
targets. They are not part of the current Foundation MVP but are
architecturally reserved.

| Content Type | Category | Description |
|---|---|---|
| Podcast | Audio | Long-form audio content with chapters, shownotes and platform distribution |
| Webinar | Video | Live or recorded presentation format with slides, Q&A and registration flow |
| Interactive Tools | Interactive | Quizzes, calculators, assessments with personalized results |
| AI Avatars | Video | Persistent AI presenter characters with brand-defined appearance and personality |
| Personalized Content | Multi-format | Content dynamically adapted to individual audience member preferences and behaviour |
| Autonomous Campaigns | Multi-format | Multi-type, multi-channel content sequences managed autonomously by the Orchestrator Agent |

## 15.2. Evolution Path

Future content types follow the LOOPRA evolution path:

```text
Foundation MVP (current)
    text_social_post only
        ↓
Content Intelligence
    content type recommendations driven by market and brand analysis
        ↓
Production Automation
    multi-type production with quality gates
        ↓
Agentic Operations
    autonomous type selection and multi-format campaign execution
        ↓
Marketing Operating System
    full portfolio of content types operating in continuous cycles
```

---

# 16. Related Documents

## 16.1. Intelligence Layer

```text
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md  — Content opportunity analysis and format recommendation
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Full content cycle specification
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory architecture and knowledge model
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Orchestrator Agent and Intelligence Module design
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — Market signal analysis and trend detection
```

## 16.2. Architecture Layer

```text
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers and boundaries
docs/02_architecture/PIPELINES_SPEC.md              — Production pipeline specification
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System configuration and rules
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
```

## 16.3. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration specification
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
```

## 16.4. Production Layer

```text
docs/04_production/CONTENT_TYPES_SPEC.md      — Current format portfolio and Foundation MVP baseline
```

---

# 17. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Production Layer — Content Type Specification |

---

# Final Statement

LOOPRA Content Types define the production formats the system can
create — from the current Foundation MVP's `text_social_post` to the
full portfolio of video, visual and interactive formats.

Each type follows a universal content model: identity, purpose,
structure, assets, parameters and optimization — all governed by the
Brand System and improved through Learning Memory.

Content Types are production definitions, not strategic
recommendations. Content Intelligence determines what to create.
Content Types define how to produce it. Learning Memory refines it
cycle after cycle.

This specification is the production blueprint for every content
format LOOPRA produces — present and future.

# ASSET LIBRARY SPEC

## Version

v1.0

## Status

Active — LOOPRA Production Layer

## Purpose

This document defines the Asset Library — the production subsystem that
stores, classifies, validates, selects, and provides assets for the
LOOPRA Production Pipeline.

It answers the central question:

> How does LOOPRA store, classify, validate, select, use and reuse
> assets for content production?

ASSET_LIBRARY_SPEC.md is the architectural blueprint for the asset
subsystem within the Production Layer. It describes the complete asset
model — from intake and classification through validation, selection,
usage and reuse — without prescribing implementation details.

It describes:

- the role of Asset Library in the LOOPRA Production Layer;
- the asset taxonomy and universal asset model;
- asset source types, lifecycle and validation;
- the asset selection model for Production Pipeline;
- handling of missing assets and generated assets;
- user uploaded asset workflow;
- asset versioning, derivatives and reuse;
- the relationship between Asset Library, Production Pipeline,
  ExportPackage and Learning Memory;
- conceptual storage model and project scoping;
- asset permissions and rights boundaries.

It does NOT describe:

- UI asset manager or media browser;
- public media marketplace;
- external stock integrations;
- copyright/legal automation beyond status tracking;
- publishing/distribution;
- analytics interpretation;
- learning algorithms;
- database schema;
- code implementation.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

ASSET_LIBRARY_SPEC.md defines the Asset Library as a production
subsystem within the LOOPRA Production Layer.

It serves as the specification for:

- the asset taxonomy — what categories of assets LOOPRA manages;
- the universal asset model — what metadata defines every asset;
- asset source types — where assets originate;
- asset lifecycle — how assets move from intake to archive;
- asset validation — how assets are verified for production use;
- asset selection — how Production Pipeline selects assets;
- missing asset handling — how requirements are generated;
- user uploaded assets — how user-provided media enters the system;
- generated assets — how AI-generated content returns to the library;
- asset versioning and derivatives — how assets evolve;
- asset usage tracking — how asset use is recorded;
- asset storage and scoping — how assets are organized;
- asset rights and permissions — how licensing is tracked;
- relationship with Production Pipeline, ExportPackage and Learning Memory.

## 1.2. Scope

This document covers:

- the position of Asset Library in the LOOPRA system architecture;
- the complete asset taxonomy with 7 categories;
- the universal asset model with identity, source, file, usage, brand,
  quality, rights and lifecycle fields;
- 8 asset source types with metadata and production-readiness rules;
- 14+ asset lifecycle statuses;
- 4 validation categories (technical, brand, quality, rights)
  with 5 possible outcomes;
- the asset selection model with scoring factors;
- 12 conceptual entities that define the asset domain;
- asset requirement and missing asset resolution paths;
- user uploaded asset workflow from upload to production-ready;
- generated asset workflow from requirement to reuse;
- asset versioning and derivatives model;
- asset usage tracking for traceability and learning;
- conceptual storage model with project scoping;
- asset rights and permissions tracking;
- asset collections for reusable production contexts;
- asset-specific error handling;
- current Foundation MVP compatibility;
- readiness criteria for architectural definition.

## 1.3. Out of Scope

This document does not cover:

- UI components for asset browsing or management;
- public media marketplace or stock integrations beyond conceptual reference;
- copyright/legal automation beyond status tracking and flagging;
- publishing or distribution mechanics (Distribution Layer);
- analytics interpretation or performance analysis (Analytics Layer);
- learning algorithms or knowledge extraction (Learning Memory);
- database schema, migrations or storage engine selection;
- code-level implementation of any component.

---

# 2. Role of Asset Library in LOOPRA

## 2.1. Position in the LOOPRA Architecture

The Asset Library is a subsystem of the Production Layer. It occupies a
defined position between the Brand System, Production Pipeline and
ultimately the ExportPackage:

```text
Brand System
    │  "Who the brand is and how it should look/sound"
    │  Brand identity, visual standards, logo, colors, typography, tone
    ↓
Project Settings
    │  "What channels, goals and content types are active"
    │  Channel requirements, format constraints
    ↓
Content Decision / Scenario
    │  "What content to create, for whom, why"
    │  From Intelligence Layer / Orchestrator Agent
    ↓
Production Pipeline
    │  "How to manufacture the selected content"
    │  Brief → Plan → Select → Generate → Assemble → QA → Export
    ↓
Asset Library
    │  "Which assets are available, suitable and licensed"
    │  Provide SelectedAsset / AssetRequirement / GeneratedAssetRecord
    ↓
Assembly
    │  "Combine assets into complete content"
    ↓
QA
    │  "Verify content quality and compliance"
    ↓
ExportPackage
    │  "Distribution-ready content package"
```

## 2.2. The Core Principle

The Asset Library operates under a strict principle:

> Asset Library provides. Production Pipeline consumes. Intelligence
> decides.

The Asset Library:

- stores and organizes assets by project, category, type and metadata;
- validates assets for technical integrity, brand compatibility, quality
  and rights;
- responds to asset queries from the Production Pipeline;
- returns selected assets, generates requirements for missing assets;
- records asset usage for traceability and Learning Memory;
- stores generated assets for future reuse;
- tracks asset lifecycle, versioning and derivatives.

The Asset Library does NOT:

- decide which content to create;
- decide which channels to target;
- decide which audience to address;
- modify the Production Brief;
- assemble content or create ExportPackages;
- analyze content performance;
- determine brand identity or visual standards.

## 2.3. Asset Library Is a Production Subsystem

The Asset Library is not a standalone product, a digital asset management
(DAM) system, or a media marketplace. It is a production subsystem of
LOOPRA, designed to serve the Production Pipeline.

Its scope is bounded by production needs. It does not become a
general-purpose media library. It exists to answer one question reliably:

> "Which assets should production use for this content item?"

---

# 3. Relationship to Production Pipeline

## 3.1. Interface Definition

The Production Pipeline and Asset Library have a defined provider-consumer
relationship. The Asset Library is called during the Asset Selection stage
of the Production Pipeline.

Reference: `PRODUCTION_PIPELINE_SPEC.md`, Section 8

## 3.2. What the Production Pipeline Requests

The Production Pipeline queries the Asset Library with structured
parameters:

| Query Parameter | Purpose |
|---|---|
| `project_id` | Scope assets to the correct project |
| `asset_category` | Filter by category (brand, media, audio, template, etc.) |
| `asset_type` | Filter by specific type within category |
| `content_type` | Filter by content type compatibility |
| `target_channels` | Filter by channel requirements (aspect ratio, resolution, duration) |
| `required_resolution` | Minimum resolution requirement |
| `required_format` | Required file format |
| `required_duration` | Required duration (video, audio) |
| `required_aspect_ratio` | Required aspect ratio (9:16, 1:1, 4:5, 16:9) |
| `quality_threshold` | Minimum quality score |
| `license_status` | Required license status (owned, licensed, generated) |
| `license_type` | Required license type for intended use |
| `brand_fit_required` | Whether brand fit validation is mandatory |
| `reuse_preferred` | Whether to prefer previously used assets |
| `blocking_only` | Whether to report only blocking missing assets |

## 3.3. What the Asset Library Returns

The Asset Library responds with structured results:

| Return Type | Purpose |
|---|---|
| **SelectedAsset** | An available asset that matches the production requirements |
| **AssetRequirement** | A specification for a missing or invalid asset |
| **AssetValidationResult** | The outcome of asset validation checks |
| **AssetUsageRecord** | A record of an asset being used in production |
| **GeneratedAssetRecord** | A record of a newly generated asset entering the library |
| **MissingAssetReport** | A summary of all missing assets for a production run |

## 3.4. Asset Categories Referenced by Production Pipeline

The Production Pipeline already defines six asset categories that the
Asset Library must support:

```text
Brand Assets          — logos, fonts, colors, templates
Media Assets          — images, footage, illustrations
Audio Assets          — voice, music, ambient, effects
Template Assets       — slide, thumbnail, overlay templates
User Uploaded Assets  — raw video, images, voice recordings
Generated Assets      — AI-generated visuals, voiceover, subtitles
```

Reference: `PRODUCTION_PIPELINE_SPEC.md`, Section 7.3.3

The Asset Library specification elaborates these into a complete taxonomy
with a seventh category: Reference Assets.

## 3.5. Production Pipeline Stages Using Asset Library

```text
Production Brief
    │  Defines what assets are conceptually needed
    ↓
Production Plan
    │  Identifies specific asset requirements per layer
    ↓
Asset Requirements  ───→  Asset Library queried for each requirement
    ↓
Asset Selection     ───→  Asset Library returns SelectedAsset or
    │                     generates AssetRequirement for missing assets
    ↓
Generation          ───→  Generated assets returned to Asset Library
    │                     as GeneratedAssetRecord
    ↓
Assembly            ───→  Selected assets consumed for content assembly
    ↓
QA                  ───→  Asset Library provides validation status,
    │                     license status, quality metadata for QA checks
    ↓
Export              ───→  Asset usage records written for Production Snapshot
```

---

# 4. Relationship to Brand System

## 4.1. Brand System Defines Standards

The Brand System defines the visual and tonal identity that assets must
align with:

| Brand System Element | What It Defines for Assets |
|---|---|
| Brand Identity | Logo versions, brand name usage, positioning context |
| Visual Identity | Color palette (primary, secondary, accent, background), typography (display and body fonts), visual motifs |
| Communication System | Tone of voice, allowed and forbidden formulations, brand personality |
| Content Strategy | Preferred formats, content pillars, publishing goals |
| Restrictions | Forbidden visual language, restricted claims, compliance rules |

Reference: `BRAND_SYSTEM_SPEC.md`

## 4.2. Brand System Answers, Asset Library Provides

```text
Brand System answers:
    "Who is the brand and how should it look and sound?"

Asset Library answers:
    "Which specific logo file, template, voice profile, color palette
     and font file are available and suitable for this production run?"
```

The Brand System defines the standards. The Asset Library stores,
validates and provides the concrete files that meet those standards.

## 4.3. Brand Assets in the Asset Library

Brand assets are the most tightly coupled to the Brand System:

| Brand System Definition | Asset Library Entity |
|---|---|
| Logo identity (primary, secondary, light, dark) | Logo PNG/SVG files with variants |
| Typography (display font, body font) | Font files (TTF/OTF/WOFF) |
| Color palette (primary, secondary, accent) | Color values, swatch files, CSS variables |
| Visual motifs and overlays | Overlay PNG/SVG, watermark files |
| Brand templates | Slide templates, thumbnail templates, intro/outro elements |

The Asset Library stores the actual files and their metadata. The Brand
System stores the rules for how those files should be used. Together they
enable production to apply brand identity consistently.

## 4.4. Brand Fit Validation

Every asset can carry brand fit metadata:

```text
brand_system_id          — which Brand System version this asset aligns with
brand_system_version     — the specific version used during validation
visual_style_tags        — descriptive tags (minimal, bold, warm, technical)
tone_tags                — descriptive tags (professional, casual, inspirational)
brand_fit_score          — 0.0–1.0 score of brand alignment
brand_fit_notes          — human-readable assessment notes
```

Assets with low brand_fit_score or mismatched brand_system_version are
flagged during selection and may be blocked from production use.

---

# 5. Relationship to Foundation MVP

## 5.1. The Foundation MVP Chain Preserved

The Foundation MVP defines a validated entity chain:

```text
Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot
```

Reference: `DATA_MODEL.md`, Section 3

The Asset Library does NOT modify this chain. It adds a new dimension
— asset tracking — within the production portion between Scenario and
ExportPackage, without changing any existing entity.

## 5.2. Current MVP and Asset Library

In the current Foundation MVP (text_social_post only):

- Asset Library is conceptually defined but minimally active;
- text-only content requires few assets (brand fonts optionally);
- the existing smoke loop, inspect_package.py and validate_package.py
  remain unaffected;
- the Asset Library spec is forward-compatible — it does not require
  changes to current working code.

## 5.3. When Asset Library Becomes Active

The Asset Library becomes a required production subsystem when LOOPRA
expands beyond text:

```text
text_social_post      →  Asset Library: minimal (fonts optional)
carousel              →  Asset Library: required (slide templates, logos, images)
short_vertical_video  →  Asset Library: required (footage, voice, music, brand layers)
educational_video     →  Asset Library: required (screen recordings, voice, templates)
```

The Asset Library spec is designed so that text-only content works with
the same model — it simply selects zero or few assets.

## 5.4. What Does NOT Change

- `ContentItem` entity and statuses remain unchanged;
- `ExportPackage` entity and structure remain unchanged;
- `Publication` entity remains unchanged;
- `MetricSnapshot` entity remains unchanged;
- Existing Foundation MVP lifecycle is preserved;
- No current code, tests or smoke scripts require modification.

---

# 6. Asset Library Core Principles

## 6.1. Principles

1. **Project-scoped by default.** Every asset belongs to a project.
   Platform-level shared templates are the only exception and must remain
   project-neutral.

2. **No project-specific hardcoding in platform core.** Asset categories,
   types and models are generic. Project-specific assets live in
   project-scoped storage.

3. **Assets must be traceable.** Every asset has a known source, creation
   context, and usage history. No orphan assets.

4. **Assets must have source/status metadata.** Every asset carries
   source_type, license_status, quality_status and lifecycle status.

5. **Assets must be validated before production use.** No asset enters
   production without passing validation or being marked with explicit
   warnings.

6. **Asset selection must be deterministic where possible.** Given the same
   query parameters, the Asset Library should return the same assets.
   Random selection is not a production strategy.

7. **Generated assets become reusable assets.** Every AI-generated image,
   voiceover, video clip or template output enters the Asset Library as a
   managed asset for future reuse.

8. **Missing assets must create explicit requirements.** No silent failure.
   Every missing or invalid asset generates a structured AssetRequirement.

9. **Asset use must be captured for Learning Memory.** Every asset used in
   production is recorded with context — which content item, which layer,
   which channel — enabling future performance correlation.

10. **Licensing/source uncertainty must block or warn depending on
    severity.** Unknown license status blocks production for critical
    assets. Expired licenses block. Uncertain sources trigger review.

---

# 7. Asset Taxonomy

## 7.1. Overview

LOOPRA classifies assets into 7 categories. Each category groups assets
by their role in content production.

| # | Category | Role in Production | Examples |
|---|---|---|---|
| 1 | Brand Assets | Visual and tonal identity | Logos, fonts, colors, overlays, watermarks |
| 2 | Media Assets | Visual and motion content | Images, footage, illustrations, b-roll |
| 3 | Audio Assets | Sonic content | Voice profiles, music, ambient, sound effects |
| 4 | Template Assets | Reusable production structures | Slide layouts, video templates, thumbnail templates |
| 5 | User Uploaded Assets | Original user-provided material | Raw footage, product screenshots, voice recordings |
| 6 | Generated Assets | AI-produced content | Generated images, voiceover, subtitles, thumbnails |
| 7 | Reference Assets | Guidance and inspiration | Moodboards, style references, competitor examples |

## 7.2. Brand Assets

Brand assets provide visual and tonal identity to all content. They are
the most stable asset category — changing only when the brand itself
evolves.

| Asset Subtype | Description | Typical Formats |
|---|---|---|
| Logos | Primary, secondary and variant logos | PNG, SVG, EPS |
| Logo Variants | Light background, dark background, monochrome, icon-only | PNG, SVG |
| Fonts | Display and body typefaces | TTF, OTF, WOFF2 |
| Color Palettes | Primary, secondary, accent, background color definitions | JSON, CSS, ASE |
| Visual Motifs | Repeating visual elements, patterns, graphic devices | PNG, SVG |
| Watermarks | Semi-transparent brand marks for content protection | PNG |
| Brand Overlays | Standard graphic overlays for video and images | PNG, PSD |
| Lower Thirds | Name/title overlays for video | PNG, PSD, template |
| Intro/Outro Elements | Opening and closing brand sequences for video | MP4, MOV, template |

Brand assets are defined by the Brand System and loaded into the Asset
Library during project setup or brand update. They rarely change and have
the highest reuse priority.

## 7.3. Media Assets

Media assets provide visual and motion content — the primary visual layer
for image and video content types.

| Asset Subtype | Description | Typical Formats |
|---|---|---|
| Images | Static photographs, graphics, compositions | PNG, JPG, WEBP |
| Photos | Photographic images (stock, original, product) | JPG, RAW, TIFF |
| Illustrations | Drawn or designed graphics | PNG, SVG, AI |
| Stock Footage | Licensed video clips from stock libraries | MP4, MOV |
| User Footage | Original video provided by the brand/user | MP4, MOV |
| Background Videos | Ambient motion backgrounds for text overlay | MP4 |
| B-Roll | Supplementary footage for context and transitions | MP4 |
| Screen Recordings | Captured software or product demonstrations | MP4, GIF |

Media assets are the most numerous category. They require the most
metadata: resolution, duration, aspect ratio, color profile, codec.

## 7.4. Audio Assets

Audio assets provide sonic content — the audio layer for video production.

| Asset Subtype | Description | Typical Formats |
|---|---|---|
| Voice Profiles | Defined AI voice characteristics (gender, age, tone, pace) | Configuration + samples |
| Voice Recordings | Human or AI-generated voice audio files | MP3, WAV, FLAC |
| Music Tracks | Background music for videos | MP3, WAV |
| Ambient Sounds | Environmental atmosphere audio | MP3, WAV |
| Sound Effects | Emphasis sounds, transitions, UI sounds | MP3, WAV |
| Audio Logos / Sonic Branding | Short brand audio signature | MP3, WAV |

Audio assets require duration, bitrate, sample rate, channel count
metadata. Voice profiles are hybrid — they combine configuration
(which AI voice to use) with sample or reference audio files.

## 7.5. Template Assets

Template assets are reusable production structures. They define how
content is laid out, not what the content says.

| Asset Subtype | Description | Typical Formats |
|---|---|---|
| Carousel Templates | Slide layout templates with brand styling | PSD, FIGMA, JSON, PNG |
| Slide Layouts | Individual slide composition templates | PSD, FIGMA, JSON |
| Video Templates | Video production project files with layers | Project file + assets |
| Subtitle Styles | Font, size, color, position, animation presets | JSON, CSS |
| Thumbnail Templates | Cover image composition templates | PSD, PNG, JSON |
| Export Templates | Output format, naming, and structure presets | JSON, YAML |
| Publication Checklist Templates | Per-platform publication step lists | JSON, MD |

Template assets define structure. They contain placeholder positions for
text, images and brand elements. The Production Pipeline fills these
placeholders with generated content and selected media.

## 7.6. User Uploaded Assets

User uploaded assets are original media provided by the brand operator.
They are NOT automatically production-ready — they must pass validation.

| Asset Subtype | Description |
|---|---|
| Raw Videos | Unedited video footage from the user |
| Raw Images | Original photographs, screenshots, graphics |
| Product Screenshots | Screen captures of products or software |
| Product Recordings | Screen recordings of product usage |
| Human Voice Recordings | Original voice audio from the brand team |
| Brand Files | Fonts, logos, templates provided by the user |
| Campaign-Specific Materials | Assets created for a specific campaign or season |

User uploaded assets have source_type `user_upload`. They require
validation before production use. Their metadata is extracted during
intake.

## 7.7. Generated Assets

Generated assets are AI-produced content. They are created during the
Generation stage of the Production Pipeline and returned to the Asset
Library as reusable assets.

| Asset Subtype | Description |
|---|---|
| AI-Generated Images | Images produced by generative AI from text prompts |
| AI-Generated Video Clips | Short motion clips generated by AI |
| Generated Voiceover | AI-synthesized narration audio |
| Generated Subtitles | Timed text subtitle tracks |
| Generated Thumbnails | Auto-generated cover images for video content |
| Generated Carousel Slides | Rendered slide images from templates and generation |
| Generated Prompt Outputs | Any output from an AI generation prompt |
| Generated Derivatives | AI-modified versions of uploaded media (color-corrected, cropped, etc.) |

Generated assets have source_type `ai_generated`. They carry generation
context — which model/tool, what prompt, what parameters. This context is
critical for reproducibility and Learning Memory correlation.

## 7.8. Reference Assets

Reference assets guide production decisions but are not typically used as
direct output content.

| Asset Subtype | Description |
|---|---|
| Moodboards | Collections of visual references defining a desired aesthetic |
| Style References | Reference images or videos demonstrating a visual style |
| Competitor References | Examples of competitor content for analysis |
| Visual Examples | Specific visual approaches to emulate or avoid |
| Previous High-Performing Content | Content items that performed well and serve as models |

Reference assets inform the creative direction. They are not rendered
into output. They help answer: "What style should this content follow?"

---

# 8. Universal Asset Model

## 8.1. Definition

Every asset in LOOPRA conforms to a universal asset model — a common
set of fields that describe identity, source, file properties, usage
constraints, brand alignment, quality, rights and lifecycle.

This model applies to all 7 asset categories. Category-specific fields
extend this base model.

## 8.2. Identity Fields

| Field | Type | Description |
|---|---|---|
| `asset_id` | string | Unique asset identifier |
| `project_id` | string | Owning project reference |
| `workspace_id` | string | Owning workspace reference |
| `asset_type` | string | Specific type within category (e.g. logo, stock_footage, voice_profile) |
| `asset_category` | string | Top-level category (brand, media, audio, template, user_uploaded, generated, reference) |
| `name` | string | Human-readable asset name |
| `description` | string | Short description of the asset and its intended use |
| `tags` | list[string] | Searchable tags for retrieval |
| `created_at` | timestamp | When the asset entered the library |
| `updated_at` | timestamp | Last modification timestamp |

## 8.3. Source Fields

| Field | Type | Description |
|---|---|---|
| `source_type` | string | Origin of the asset (see Section 9) |
| `uploaded_by` | string | Who uploaded (user_id or system reference) |
| `generated_by` | string | Tool or model that generated the asset |
| `generation_context` | object | Prompt, parameters, model version used |
| `original_filename` | string | Filename at intake |
| `source_url` | string | Original URL if sourced from external reference |
| `source_reference` | string | Human-readable source description |
| `source_confidence` | string | high, medium, low, unknown — certainty about origin |

## 8.4. File Metadata Fields

| Field | Type | Description |
|---|---|---|
| `file_path` | string | Relative path within project storage |
| `file_format` | string | File extension / container format (MP4, PNG, MP3, TTF) |
| `mime_type` | string | MIME type (image/png, video/mp4, audio/mpeg) |
| `size_bytes` | integer | File size in bytes |
| `checksum` | string | SHA-256 hash for integrity verification |
| `dimensions` | string | Width x Height (e.g. 1920x1080) for images and video |
| `duration` | float | Duration in seconds for video and audio |
| `bitrate` | integer | Bitrate in kbps for video and audio |
| `frame_rate` | float | Frames per second for video |
| `color_profile` | string | Color space (sRGB, Display P3, Rec.709) |

## 8.5. Usage Fields

| Field | Type | Description |
|---|---|---|
| `allowed_content_types` | list[string] | Content types this asset can be used for |
| `allowed_channels` | list[string] | Channels this asset is compatible with |
| `allowed_layers` | list[string] | Production layers this asset belongs in (visual, audio, brand, subtitle) |
| `preferred_use` | string | Recommended primary use case |
| `restricted_use` | list[string] | Specific uses where this asset is forbidden |
| `reuse_priority` | string | high, medium, low — how aggressively to reuse |
| `reuse_count` | integer | How many times this asset has been used |
| `last_used_at` | timestamp | Most recent usage timestamp |
| `fatigue_risk` | string | high, medium, low — risk of overuse causing visual fatigue |
| `preferred_content_types` | list[string] | Content types where this asset performs best |
| `deprecated_after` | integer | Suggested reuse limit before deprecation |

## 8.6. Brand Fit Fields

| Field | Type | Description |
|---|---|---|
| `brand_system_id` | string | Which Brand System this asset belongs to |
| `brand_system_version` | string | Brand System version at time of validation |
| `visual_style_tags` | list[string] | Style descriptors (minimal, bold, warm, technical, elegant) |
| `tone_tags` | list[string] | Tone descriptors (professional, casual, inspirational, authoritative) |
| `brand_fit_score` | float | 0.0–1.0 alignment score |
| `brand_fit_notes` | string | Human-readable assessment |

## 8.7. Quality Fields

| Field | Type | Description |
|---|---|---|
| `quality_status` | string | valid, valid_with_warnings, needs_review, invalid |
| `quality_score` | float | 0.0–1.0 overall quality score |
| `resolution_ok` | boolean | Whether resolution meets minimum threshold |
| `audio_quality_ok` | boolean | Whether audio is clear and undistorted |
| `technical_validity` | boolean | Whether file is readable and not corrupted |
| `human_review_status` | string | not_reviewed, pending, approved, rejected |

## 8.8. Rights and Source Status Fields

| Field | Type | Description |
|---|---|---|
| `license_status` | string | unknown, owned, user_provided, licensed, generated, restricted, expired, blocked |
| `license_type` | string | Type of license (royalty_free, rights_managed, creative_commons, custom, internal_only) |
| `usage_rights` | list[string] | Permitted use contexts (internal_only, organic_social, paid_ads, website, email, all_channels) |
| `attribution_required` | boolean | Whether attribution must be displayed |
| `expiration_date` | date | License expiration date if time-limited |
| `restricted_platforms` | list[string] | Platforms where this asset must NOT be used |
| `rights_notes` | string | Human-readable rights information |

## 8.9. Lifecycle Fields

| Field | Type | Description |
|---|---|---|
| `status` | string | Current lifecycle status (see Section 10) |
| `version` | integer | Asset version number |
| `parent_asset_id` | string | Reference to the original asset if this is a derivative |
| `derivative_of` | string | Reference to the source asset |
| `derivative_type` | string | Type of derivative (crop, resize, compress, color_correct, brand, translate, platform_adapt) |
| `transformation_applied` | string | Description of what transformation created this derivative |
| `created_for_content_item` | string | Content item that prompted this derivative's creation |
| `reusable` | boolean | Whether the derivative can be reused independently |
| `archived_at` | timestamp | When the asset was archived |

---

# 9. Asset Source Types

## 9.1. Overview

Every asset has a `source_type` that defines its origin, the metadata it
requires, the risks associated with it and whether it can be used in
production automatically.

## 9.2. Source Type Catalog

### 9.2.1. brand_system

```text
Definition:
    Asset defined by and loaded from the Brand System configuration.
    These are the brand's own identity assets.

Examples:
    Logos, fonts, color palettes, brand overlays, watermarks.

Required metadata:
    brand_system_id, brand_system_version, brand_fit_score.

Risks:
    Minimal. These are owner-controlled brand assets.

Auto-production-use:
    Yes, when brand_fit_score is high and brand_system_version matches
    the active version.
```

### 9.2.2. user_upload

```text
Definition:
    Asset provided directly by the brand operator — original media,
    footage, images, recordings.

Examples:
    Raw video footage, product screenshots, voice recordings, campaign
    materials.

Required metadata:
    uploaded_by, original_filename, upload timestamp.
    Must pass validation before production use.

Risks:
    Unknown quality. Potential licensing ambiguity if the uploader is not
    the rights holder. Unknown source confidence.

Auto-production-use:
    No. User uploaded assets MUST pass technical, quality and rights
    validation before being marked available. Assets that fail validation
    are marked needs_review or blocked.
```

### 9.2.3. ai_generated

```text
Definition:
    Asset produced by an AI generation tool during content production.

Examples:
    AI-generated images, video clips, voiceover audio, subtitles.

Required metadata:
    generated_by (tool/model reference), generation_context (prompt,
    parameters, model version), parent_content_item_id, parent_brief_id.

Risks:
    AI-generated content may have usage right uncertainties depending on
    the generation platform's terms. Quality may vary.

Auto-production-use:
    Yes, after passing technical and quality validation. Generated assets
    are owned by the project by default. Rights depend on the generation
    platform's terms — must be captured in license_status.
```

### 9.2.4. stock_library

```text
Definition:
    Asset sourced from a licensed stock media library.

Examples:
    Stock photos, stock video clips, licensed music tracks.

Required metadata:
    license_type, license_status, usage_rights, attribution_required,
    expiration_date, restricted_platforms.

Risks:
    License expiration. Platform restrictions. Attribution requirements.
    The same asset may be used by competitors.

Auto-production-use:
    Yes, when license_status is licensed, expiration_date is in the
    future and usage_rights cover the intended use. Expired or restricted
    assets are blocked.
```

### 9.2.5. internal_template

```text
Definition:
    Asset that is a LOOPRA platform template — reusable structure,
    not project-specific.

Examples:
    Default carousel layouts, thumbnail templates, subtitle style presets.

Required metadata:
    Template version, compatible content types, compatible channels.

Risks:
    Minimal. These are platform-provided, generic assets.

Auto-production-use:
    Yes, when compatible with the content type and channel.
```

### 9.2.6. external_reference

```text
Definition:
    Asset used as a reference only — not for direct output.

Examples:
    Moodboards, competitor examples, style references, inspiration images.

Required metadata:
    source_url or source_reference. Must be clearly marked as reference-only.

Risks:
    Must never be accidentally used as production output. Copyright of
    referenced material belongs to original owner.

Auto-production-use:
    No — NEVER used as direct output asset. Reference only.
```

### 9.2.7. previous_export

```text
Definition:
    An asset extracted from a previous ExportPackage or production output
    that has been returned to the library for reuse.

Examples:
    A thumbnail that performed well, a rendered slide that can be reused,
    a generated image that proved effective.

Required metadata:
    origin_content_item_id, origin_export_package_id, performance_context
    (if available from Learning Memory).

Risks:
    May become visually stale. Must not create circular reuse cycles.

Auto-production-use:
    Yes, when quality_status is still valid and fatigue_risk is below
    threshold.
```

### 9.2.8. manual_import

```text
Definition:
    Asset manually imported into the library by the operator through
    an import mechanism.

Examples:
    Fonts, templates, media files imported through a structured import
    process.

Required metadata:
    imported_by, import_timestamp, source_reference.

Risks:
    Similar to user_upload — must pass validation.

Auto-production-use:
    After validation. Same rules as user_upload.
```

## 9.3. Source Type and Production Readiness Summary

| Source Type | Auto-Use in Production | Requires Validation | Blocking Risks |
|---|---|---|---|
| brand_system | Yes (if version matches) | Minimal | Brand version mismatch |
| user_upload | No (requires validation) | Full validation required | Unknown quality, rights ambiguity |
| ai_generated | Yes (after validation) | Technical + quality | Tool terms restrictions |
| stock_library | Yes (if license valid) | Rights check | License expiration, platform restrictions |
| internal_template | Yes | Compatibility check | None |
| external_reference | Never (reference only) | N/A | Accidental production use |
| previous_export | Yes (if still valid) | Quality check | Visual fatigue |
| manual_import | After validation | Full validation | Same as user_upload |

---

# 10. Asset Status and Lifecycle

## 10.1. Conceptual Lifecycle

```text
uploaded / created
    │  Asset enters the library
    ↓
pending_validation
    │  Asset queued for automated checks
    ↓
┌───────────────────────────────┐
│  Validation (Section 11)      │
│  Technical / Brand / Quality  │
│  / Rights / Production Fit    │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
    validated       needs_review / rejected / blocked
        │                │
        ▼                ▼
    available       Human review or resolution required
        │
        ▼
    selected
        │  Asset chosen for a production run
        ▼
    in_use
        │  Asset actively used in production
        ▼
    used
        │  Asset usage recorded; returns to available for reuse
        ▼
    available (reuse loop)
        │
        ▼
    deprecated
        │  Asset marked for phase-out (fatigue, brand update, quality)
        ▼
    archived
        │  Asset no longer available for new production; retained for history
```

## 10.2. Lifecycle Statuses

| Status | Description |
|---|---|
| `uploaded` | Asset has been received but not yet processed |
| `created` | Asset has been generated or derived but not yet validated |
| `pending_validation` | Asset is queued for automated validation checks |
| `validated` | Asset has passed all applicable validation checks |
| `available` | Asset is validated and ready for production selection |
| `needs_review` | Asset requires human review before production use |
| `rejected` | Asset failed validation and is not usable in current state |
| `blocked` | Asset cannot be used due to license, rights or compliance issues |
| `generated_pending_review` | AI-generated asset awaiting human approval |
| `selected` | Asset has been chosen for a specific production run |
| `in_use` | Asset is actively being used in a production process |
| `used` | Asset has been used in production; record created |
| `deprecated` | Asset is marked for phase-out; still available but not recommended |
| `archived` | Asset is no longer available for new production; retained for history |
| `duplicate_candidate` | Asset appears to be a duplicate of an existing asset |
| `expired_license` | Asset license has expired; blocked from production use |
| `missing_file` | Asset record exists but the referenced file is not found |

## 10.3. Status Transition Rules

```text
uploaded/created → pending_validation:
    Trigger: Asset intake complete.

pending_validation → validated:
    Trigger: All applicable validation checks passed.

pending_validation → needs_review:
    Trigger: Validation found issues requiring human judgment.

pending_validation → rejected:
    Trigger: Validation found blocking issues that cannot be auto-resolved.

pending_validation → blocked:
    Trigger: License or rights issues prevent use.

validated → available:
    Trigger: Asset is ready for production.

available → selected:
    Trigger: Production Pipeline selects this asset for a run.

selected → in_use:
    Trigger: Asset consumption begins.

in_use → used → available:
    Trigger: Production complete; usage recorded; asset returns to pool.

available → deprecated:
    Trigger: Fatigue, brand update, or quality decline.

deprecated → archived:
    Trigger: Explicit archival or automatic after deprecation period.

any → missing_file:
    Trigger: Referenced file is not found at expected path.

any → archived:
    Trigger: Manual archival or automatic archival policy.
```

---

# 11. Asset Validation

## 11.1. Overview

Every asset must be validated before it can be used in production. The
Asset Library performs validation during intake (for user uploaded and
manually imported assets) and during generation (for AI-generated assets).

Validation is not optional. An asset that has not been validated cannot
be selected for production.

## 11.2. Validation Categories

### 11.2.1. Technical Validation

Verifies that the asset file is technically valid and usable.

| Check | Rule |
|---|---|
| File exists | The referenced file is present at file_path |
| File readable | The file can be opened and read without errors |
| Correct format | The file format matches the expected format for its type |
| Checksum generated | A SHA-256 checksum is computed and stored |
| Resolution meets minimum | Image/video resolution meets or exceeds the minimum threshold |
| Duration valid | Video/audio duration is within acceptable bounds and not zero |
| Audio not corrupted | Audio file is playable and has valid signal |
| Video playable | Video file decodes and renders correctly |
| File size reasonable | File size is non-zero and within expected range for type |

### 11.2.2. Brand Validation

Verifies that the asset aligns with the Brand System standards.

| Check | Rule |
|---|---|
| Brand visual style match | Asset's visual style is consistent with brand identity |
| Allowed by Brand System | Asset type and usage are permitted by Brand System rules |
| No forbidden visual rules | Asset does not violate explicitly forbidden visual language |
| Correct logo/font/color usage | If the asset contains brand elements, they are correctly applied |
| Brand version match | Asset was validated against the current Brand System version |

### 11.2.3. Quality Validation

Verifies that the asset meets quality thresholds for production output.

| Check | Rule |
|---|---|
| Image sharpness | Image is not blurry; sufficient detail for intended resolution |
| Video clarity | Video is free of compression artifacts, blockiness, or excessive noise |
| Audio clarity | Audio is free of distortion, clipping, excessive noise, or dropouts |
| No visible artifacts | Image/video is free of unintended visual artifacts |
| No unauthorized watermarks | Asset does not contain third-party watermarks (brand watermark is allowed) |
| Composition quality | Image/video composition is professionally acceptable |
| Safe crop areas | Important content is within safe areas for target aspect ratios |

### 11.2.4. Rights Validation

Verifies that the asset can be legally used for the intended purpose.

| Check | Rule |
|---|---|
| License known | license_status is not unknown for non-brand assets |
| Rights sufficient | usage_rights cover the intended use context |
| Attribution captured | If attribution_required is true, attribution text is stored |
| Expiration date known | If license is time-limited, expiration_date is recorded |
| Expiration not passed | expiration_date is in the future |
| Platform restrictions respected | restricted_platforms does not include target channels |

### 11.2.5. Production Fit Validation

Verifies that the asset is technically compatible with the intended
production use.

| Check | Rule |
|---|---|
| Content type compatible | Asset type is allowed for the target content type |
| Channel compatible | Asset format, resolution, duration match channel requirements |
| Aspect ratio compatible | Asset dimensions match or can be adapted to the target aspect ratio |
| Resolution compatible | Asset resolution meets channel minimum requirements |
| Layer compatible | Asset can be placed in the required production layer |

## 11.3. Validation Outcomes

| Outcome | Meaning | Production Can Use? |
|---|---|---|
| `valid` | All checks passed | Yes, without restriction |
| `valid_with_warnings` | All blocking checks passed; minor issues noted | Yes, warnings included in QA report |
| `needs_review` | One or more checks require human judgment | No, until reviewed |
| `invalid` | One or more checks failed; asset not usable as-is | No |
| `blocked` | License, rights or compliance issues prevent use | No, permanently for this use |

## 11.4. Validation Triggers

Validation runs:

- on asset intake (upload, import, generation);
- on brand system update (re-validate brand fit for all assets);
- on license expiration check (scheduled);
- on selection request (on-demand validation before returning asset);
- on file integrity check (scheduled checksum verification).

---

# 12. Asset Selection Model

## 12.1. Purpose

The Asset Selection model defines how the Asset Library evaluates and
ranks available assets when the Production Pipeline requests assets for
a production run.

## 12.2. Selection Inputs

The Production Pipeline provides:

```text
Project context:
    project_id, workspace_id

Content context:
    content_type, production_variant, target_channels

Layer requirements:
    required_layer (visual, audio, brand, subtitle)

Technical requirements:
    required_format, required_resolution, required_duration,
    required_aspect_ratio

Brand constraints:
    brand_system_id, brand_system_version, required_brand_fit_score

License requirements:
    required_license_status, required_usage_rights

Quality requirements:
    quality_threshold (minimum quality_score)

Strategy preferences:
    reuse_preferred (prefer assets with successful reuse history)
```

## 12.3. Selection Scoring Factors

Assets are scored against these dimensions:

| Factor | Weight | How Scored |
|---|---|---|
| **Project match** | Required | Must match project_id. Disqualifying if wrong. |
| **Brand fit** | High | brand_fit_score × brand version match |
| **Technical fit** | High | Resolution, format, duration, aspect ratio match |
| **Channel fit** | High | Compatibility with target channel requirements |
| **Content type fit** | Medium | Asset's allowed_content_types includes target |
| **Quality score** | Medium | quality_score relative to threshold |
| **License safety** | High | License valid, not expiring soon, covers intended use |
| **Recency** | Low | Prefer newer assets over older (for freshness) |
| **Reuse effectiveness** | Medium | If reuse_preferred: assets with past successful use score higher |
| **Fatigue risk** | Medium | Penalize assets with high reuse_count relative to fatigue threshold |

## 12.4. Selection Rules

```text
Rule 1 — Project scope:
    Asset MUST belong to the requesting project_id.
    Exception: internal_template assets may be platform-level.

Rule 2 — Blocking exclusions:
    Assets with status blocked, rejected, expired_license, missing_file
    are NEVER returned.

Rule 3 — Needs review assets:
    Assets with status needs_review or generated_pending_review are
    returned only if explicitly requested and flagged with warning.

Rule 4 — Quality threshold:
    Assets with quality_score below the requested threshold are
    excluded unless no alternatives exist. If excluded, an
    AssetRequirement is generated.

Rule 5 — License safety:
    Assets with license_status unknown are excluded for production
    unless the operator has explicitly allowed them.

Rule 6 — Brand fit:
    Assets with brand_fit_score below the configured minimum are
    excluded.

Rule 7 — Deterministic tie-breaking:
    When multiple assets score identically, the asset with the highest
    version and most recent updated_at is selected. This ensures
    deterministic selection.
```

## 12.5. Selection Response

The Asset Library returns:

```text
For each asset query:
    ├── SelectedAsset          (if one or more suitable assets found)
    │     ├── asset_id
    │     ├── selection_reason
    │     ├── selection_score
    │     ├── alternatives_considered
    │     └── validation_status at selection time
    │
    └── AssetRequirement       (if no suitable asset found)
          ├── requirement_id
          ├── asset_category
          ├── asset_type
          ├── blocking (bool)
          ├── reason
          └── recommended_resolution_path
```

---

# 13. SelectedAsset

## 13.1. Definition

A **SelectedAsset** records the choice of a specific asset for a specific
production run. It captures the context of the selection — why this asset
was chosen, what alternatives were considered, what its status was at the
time of selection.

## 13.2. Entity Structure

```text
SelectedAsset:

    selected_asset_id        — unique identifier for this selection record
    asset_id                 — reference to the Asset entity
    project_id               — project scope
    content_item_id          — the ContentItem this asset is used for
    production_brief_id      — the Production Brief that defined the need
    production_plan_id       — the Production Plan that identified this asset

    selected_for_layer       — which production layer (visual, audio, brand, subtitle)
    selected_for_content_type — which content type this is for
    selected_for_channel     — which target channel (or "all" if multi-channel)

    selection_reason         — human-readable reason for selection
    selection_score          — composite score that led to this choice
    alternatives_considered  — list of asset_ids that were evaluated

    selected_at              — timestamp of selection
    selected_by              — system or human identifier

    license_status_at_selection   — snapshot of license_status at selection time
    quality_status_at_selection   — snapshot of quality_status at selection time
```

## 13.3. SelectedAsset and Production Snapshot

The SelectedAsset records are included in the Production Snapshot passed
to Learning Memory. This enables future analysis of which asset
combinations correlate with content performance.

---

# 14. Asset Requirement / Missing Asset Handling

## 14.1. Definition

An **AssetRequirement** is created when the Asset Library cannot provide
a suitable asset for a production need. It describes what is needed,
why it is needed, how critical it is and how it might be resolved.

## 14.2. When AssetRequirements Are Created

| Scenario | Severity |
|---|---|
| Asset type does not exist in the library | blocking or warning |
| Asset exists but quality_score is below threshold | blocking or warning |
| Asset exists but license is expired or blocked | blocking |
| Asset exists but does not match channel requirements (resolution, aspect ratio) | blocking or warning |
| Asset exists but brand_fit_score is too low | warning |
| Asset exists but is in needs_review status | blocking (until reviewed) |
| New generated asset is required (does not exist yet) | Generation task |

## 14.3. Entity Structure

```text
AssetRequirement:

    requirement_id           — unique identifier
    project_id               — project scope
    content_item_id          — the ContentItem that needs this asset
    production_brief_id      — the Production Brief that defines the need

    asset_category           — which category (brand, media, audio, etc.)
    asset_type               — specific type within category
    required_layer           — which production layer needs it
    required_format          — required file format
    required_resolution      — minimum resolution
    required_duration        — required duration (video/audio)
    required_aspect_ratio    — required aspect ratio
    required_style           — required visual or audio style descriptors
    required_license         — required license type for intended use

    blocking                 — boolean. Whether production can proceed without this asset
    priority                 — high, medium, low
    reason                   — why this requirement exists
    recommended_resolution_path — suggested approach to resolve
    status                   — open, in_progress, fulfilled, cancelled
```

## 14.4. Resolution Paths

| Resolution Path | Description |
|---|---|
| `user_upload_required` | Operator must upload the needed asset |
| `generate_asset` | Asset should be created during the Generation stage |
| `select_alternative` | A different but acceptable asset exists if requirements are relaxed |
| `relax_requirement_with_approval` | Lower quality/resolution thresholds with operator approval |
| `revise_production_brief` | The Brief should be updated to avoid needing this asset |
| `skip_optional_asset` | Asset is non-blocking; production can proceed without it |

## 14.5. Blocking vs Non-Blocking

```text
Blocking asset missing:
    → Production pauses at Asset Selection stage.
    → AssetRequirement created with blocking: true.
    → Operator notified (copilot/assisted) or escalated (autopilot).
    → Production resumes when requirement is fulfilled.

Non-blocking asset missing:
    → Production continues with fallback or omission.
    → AssetRequirement created with blocking: false.
    → Warning logged in Production Snapshot.
    → QA stage notes the missing asset.
```

---

# 15. User Uploaded Asset Workflow

## 15.1. Overview

User uploaded assets enter the Asset Library through a structured intake
process. They are not automatically production-ready. Every uploaded
asset passes through validation before becoming available.

## 15.2. Upload Workflow

```text
Upload
    │  User provides raw media file
    ↓
Intake
    │  File received and stored in project-scoped upload area
    │  Asset record created with status: uploaded
    ↓
Metadata Extraction
    │  Technical metadata extracted: format, resolution, duration,
    │  size, checksum computed
    │  Original filename preserved
    │  Upload timestamp and uploader recorded
    ↓
Technical Validation
    │  File readable, format valid, not corrupted, checksum verified
    │  Outcome: valid → proceed; invalid → rejected or needs_review
    ↓
Brand Validation
    │  Visual/audio style assessed against Brand System
    │  Logo/watermark/color usage checked if applicable
    │  Outcome: brand_fit_score assigned
    ↓
Quality Validation
    │  Resolution adequacy, clarity, artifacts checked
    │  Audio quality, noise levels, clarity checked
    │  Outcome: quality_score assigned
    ↓
Rights Validation
    │  Source and licensing information collected from uploader
    │  Attribution requirements captured
    │  Expiration dates recorded if applicable
    │  Outcome: license_status set
    ↓
Classification
    │  Asset assigned to correct category and type
    │  Tags extracted or assigned
    │  allowed_content_types, allowed_channels set
    │  reuse_priority set based on type and quality
    ↓
Status Update
    │  All validations passed → status: available
    │  Some warnings → status: available (quality_status: valid_with_warnings)
    │  Human review needed → status: needs_review
    │  Blocking issues → status: rejected or blocked
    ↓
Available for Production
    │  Asset is now selectable by the Production Pipeline
    │  Included in asset search results
    │  Ready for usage tracking
```

## 15.3. Upload Cases

| Upload Case | Typical Use | Validation Focus |
|---|---|---|
| Raw video footage | Video production (visual layer) | Resolution, duration, clarity, codec |
| Product screenshots | Carousel, image posts | Resolution, composition, brand fit |
| Brand logos | Brand layer overlay | Format (PNG/SVG with transparency), correct version |
| Fonts | Typography in all content | Format (TTF/OTF), license, rendering test |
| Image references | Carousel backgrounds, thumbnails | Resolution, quality, source rights |
| Voice recordings | Video audio layer | Clarity, noise level, duration, format |
| Campaign materials | Seasonal content production | Campaign-specific metadata, expiration date |

## 15.4. Rules for User Uploads

- User uploaded does NOT mean production-ready. Validation is mandatory.
- Uploader must confirm they have rights to the material (attestation, not legal proof).
- Unknown or uncertain license_status → blocked or needs_review.
- Original filename and upload timestamp are always preserved.
- Duplicate detection runs on upload (same checksum → duplicate_candidate).

---

# 16. Generated Asset Workflow

## 16.1. Overview

Generated assets are created during the Generation stage of the
Production Pipeline. They enter the Asset Library through a structured
process that captures generation context, validates the output and marks
it for reuse where appropriate.

## 16.2. Generation-to-Library Workflow

```text
Production Requirement
    │  AssetRequirement with resolution_path: generate_asset
    │  Generated as part of Production Pipeline Generation stage
    ↓
Generation Task
    │  AI tool invoked with prompt, parameters, context
    │  generation_context captured (model, prompt, version, parameters)
    ↓
Generated Output
    │  Asset file produced by the generation tool
    │  Asset record created with status: created
    │  source_type: ai_generated
    │  generated_by, generation_context stored
    ↓
Technical Validation
    │  Same checks as any other asset
    │  File integrity, format, resolution, duration verified
    ↓
Brand / Quality Validation
    │  Brand fit assessed (does the AI output match brand style?)
    │  Quality assessed (is the AI output usable for production?)
    │  Outcome: quality_score, brand_fit_score assigned
    ↓
Human Review (if required)
    │  Autonomy mode determines if human review is needed
    │  Copilot: always reviewed
    │  Assisted: reviewed for new/unfamiliar content types
    │  Autopilot: auto-approved if quality and brand scores pass
    │  Status: available or generated_pending_review
    ↓
Store in Asset Library
    │  Asset saved to project-scoped generated/ storage
    │  Metadata stored with full generation context
    │  Linked to parent asset if derived from uploaded media
    ↓
Use in Current Production
    │  Asset immediately available for the current production run
    │  SelectedAsset record created
    ↓
Available for Future Reuse
    │  Asset remains in library after production completes
    │  Can be selected for future production runs
    │  Reuse subject to fatigue_risk and quality decay
```

## 16.3. Generated Asset Types

| Generated Type | Generation Context Captured | Reuse Considerations |
|---|---|---|
| AI-generated image | Prompt, model, style parameters, seed | Visual fatigue if overused; style consistency with brand |
| AI-generated video clip | Prompt, model, duration, motion parameters | Motion style consistency; file size for reuse |
| Generated voiceover | Voice profile, script text, pace, emphasis | Voice consistency within project; avoid monotony |
| Generated subtitles | Script text, timing data, style parameters | Reusable only if associated media is also reused |
| Generated thumbnail | Template, image assets used, text overlay | Visual fatigue risk; thumbnail variety is important |
| Generated carousel slide | Template, text content, image assets | Slide-specific; low standalone reuse value |
| Generated derivative from uploaded media | Source asset, transformation applied | Transformed asset is independent; source attribution preserved |

## 16.4. Generation Context Fields

Every generated asset carries:

```text
generation_context:
    model_or_tool         — which AI system produced this
    model_version         — version identifier if available
    prompt_or_spec        — the input prompt or specification
    parameters            — generation parameters (temperature, style, seed)
    parent_brief_id       — the Production Brief that initiated generation
    parent_content_item_id — the ContentItem this was generated for
    generation_timestamp  — when generation occurred
```

This context enables:
- Reproducibility — the same parameters can be reused;
- Debugging — if quality is poor, context reveals the input;
- Learning Memory — understanding which generation approaches produce
  assets that correlate with higher content performance.

---

# 17. Asset Versioning and Derivatives

## 17.1. Overview

Assets evolve. An original uploaded video may be trimmed, color-corrected
and rendered in multiple aspect ratios. An original logo may have light
and dark variants. A template may be updated with new brand colors.

The Asset Library tracks this evolution through versioning and derivative
relationships.

## 17.2. Original vs Derivative

```text
Original Asset:
    The first version of an asset ingested into the library.
    parent_asset_id: null
    derivative_of: null
    version: 1

Derivative Asset:
    A modified version of an existing asset.
    parent_asset_id: reference to the original
    derivative_of: reference to the immediate source asset
    version: auto-incremented or explicit
```

## 17.3. Derivative Types

| Derivative Type | Description | Example |
|---|---|---|
| `crop` | Cropped to different dimensions | 16:9 video cropped to 1:1 |
| `resize` | Resized to different resolution | 4K image resized to 1080p |
| `compress` | Compressed for file size or platform requirements | High-bitrate video compressed for social |
| `color_correct` | Color grading or correction applied | Raw footage color-graded to brand palette |
| `branded` | Brand elements applied (logo, overlay, watermark) | Clean video with brand logo added |
| `translate` | Text or subtitles translated to another language | Voiceover in language A, derivative in language B |
| `localize` | Culturally adapted version | US-market image adapted for EU market |
| `platform_adapt` | Adapted for specific platform requirements | 16:9 video rendered as 9:16 for TikTok |
| `trim` | Trimmed to different duration | 3-minute video trimmed to 60 seconds |
| `format_convert` | Converted to different file format | PNG logo converted to SVG or vice versa |
| `audio_normalize` | Audio levels normalized or enhanced | Raw voice recording with noise reduction |

## 17.4. Derivative Chain Example

```text
uploaded_video_raw (version 1, original)
    │
    ├── trimmed_clip (version 1, derivative_of: uploaded_video_raw)
    │     derivative_type: trim
    │
    ├── color_corrected_clip (version 1, derivative_of: uploaded_video_raw)
    │     derivative_type: color_correct
    │     │
    │     └── branded_vertical_video (version 1, derivative_of: color_corrected_clip)
    │           derivative_type: platform_adapt + branded
    │
    └── compressed_preview (version 1, derivative_of: uploaded_video_raw)
          derivative_type: compress
```

## 17.5. Derivative Rules

- A derivative is a fully independent asset with its own asset_id, file,
  metadata and lifecycle.
- Derivatives inherit brand_fit_score and license_status from the parent
  unless explicitly overridden (e.g., a branded derivative may have
  higher brand_fit_score).
- Derivatives carry derivative_type and transformation_applied for
  traceability.
- Derivatives marked reusable: true can be independently selected for
  future production runs.
- Derivatives marked reusable: false are scoped to the specific content
  item that required them and are archived after that production run
  unless explicitly promoted.

---

# 18. Asset Usage Tracking

## 18.1. Definition

Every time an asset is used in production, an **AssetUsageRecord** is
created. This record captures when, where, how and in what context the
asset was used.

## 18.2. Entity Structure

```text
AssetUsageRecord:

    usage_id                — unique identifier for this usage event
    asset_id                — reference to the Asset used
    content_item_id         — the ContentItem that consumed this asset
    export_package_id       — the ExportPackage that includes this asset
    production_brief_id     — the Production Brief that defined the need

    used_in_layer           — which production layer (visual, audio, brand, subtitle)
    used_in_channel         — which channel the content was produced for
    used_at                 — timestamp of usage

    usage_type              — direct, derivative_source, reference_only
    version_used            — asset version at time of use

    license_status_at_use   — snapshot of license_status at time of use
    quality_status_at_use   — snapshot of quality_status at time of use
```

## 18.3. Purpose of Usage Tracking

| Purpose | How Usage Records Enable It |
|---|---|
| **Traceability** | Know exactly which assets are in which export packages |
| **Debugging** | If a published content item has an issue (wrong logo, low-quality image), trace back to the specific asset version used |
| **License audit** | Prove that licensed assets were used within their valid period and scope |
| **Learning Memory** | Correlate asset combinations with content performance to identify which assets produce better results |
| **Reuse analytics** | Track reuse_count, last_used_at and fatigue_risk per asset |
| **Performance correlation** | Discover which visual styles, voice profiles, templates correlate with higher engagement |

## 18.4. Usage Tracking in Production Snapshot

AssetUsageRecords are included in the Production Snapshot alongside other
production context. This allows Learning Memory to associate specific
assets with content performance outcomes after the content cycle completes.

---

# 19. Asset Library and ExportPackage

## 19.1. Asset Inclusion in ExportPackage

ExportPackages may include assets in several ways:

| Inclusion Mode | Description |
|---|---|
| **Copied media files** | The actual asset file is copied into the ExportPackage (e.g., rendered slide PNGs, final video MP4) |
| **Rendered derivatives** | Asset derivatives created specifically for this export (e.g., platform-adapted versions) |
| **Asset context references** | metadata.json and manifest.json reference asset_ids and versions used |
| **Asset usage report** | A summary of all assets consumed in this production run |
| **Generated subtitles and captions** | Text assets produced from the audio/script assets |

## 19.2. Self-Contained Export

The ExportPackage should be self-contained enough for distribution. This
means:

- Final rendered output files (video, images, text) are included directly.
- Source asset files are included only if needed for distribution (e.g.,
  a brand logo file for the publisher's reference).
- The Asset Library remains the source of truth for reusable, non-exported
  assets.
- The ExportPackage does not replace the Asset Library — it is a
  distribution snapshot, not the master asset repository.

## 19.3. Asset Manifest in ExportPackage

The ExportPackage manifest includes an asset usage section:

```json
{
  "package_id": "export_content_042_v1",
  "assets_used": [
    {
      "asset_id": "brand_logo_light_v1",
      "asset_category": "brand",
      "asset_type": "logo",
      "version_used": 1,
      "used_in_layer": "brand_layer",
      "included_in_package": true,
      "package_path": "content/media/images/brand_logo.png"
    },
    {
      "asset_id": "ai_voice_profile_01",
      "asset_category": "audio",
      "asset_type": "voice_profile",
      "version_used": 1,
      "used_in_layer": "audio_layer",
      "included_in_package": false,
      "output_rendered_as": "content/media/audio/voiceover.mp3"
    }
  ]
}
```

## 19.4. Asset Library After Export

After the ExportPackage is assembled:

- The Asset Library updates usage records for all selected assets.
- Generated assets are stored in the library for future reuse.
- Asset lifecycle states transition from `in_use` to `used` and back to
  `available`.
- Deprecated or single-use assets may be archived per policy.

---

# 20. Asset Library and Learning Memory

## 20.1. Asset Library Does Not Learn

The Asset Library does NOT analyze performance. It does NOT determine
which assets are "better" based on content results. It stores and
provides asset metadata. Learning Memory does the analysis.

## 20.2. Data Passed to Learning Memory via Production Snapshot

The Asset Library contributes the following data to the Production
Snapshot, which Learning Memory later consumes:

| Asset Data | Learning Memory Question Answered |
|---|---|
| assets_used (list of asset_ids) | Which assets were in this content? |
| asset_category per asset | Which categories of assets perform best? |
| asset_type per asset | Which specific asset types correlate with success? |
| template version used | Which template versions produce better results? |
| visual_style_tags | Which visual styles resonate with the audience? |
| audio_style_tags / voice_profile | Which voice profiles retain attention? |
| source_type (generated vs uploaded vs stock) | Which source types produce better-performing content? |
| quality_status_at_use | Did assets with quality warnings produce worse results? |
| license_status_at_use | (context only; not a performance factor) |
| reuse_count at time of use | Does asset reuse correlate with performance changes? |
| asset combination (which assets used together) | Which visual + audio + template combinations work best? |

## 20.3. Future Learning Memory Insights About Assets

Over time, Learning Memory could identify:

```text
Visual style insights:
    "Minimal visual style with bold typography generates higher
     engagement for the professional audience than photo-heavy
     carousels."

Template effectiveness:
    "Template v2 produces 30% higher save rates than template v1
     for educational carousels on LinkedIn."

Voice profile performance:
    "Female voice profile A retains viewers 20% longer than male
     voice profile B for awareness-goal videos."

Source type impact:
    "User uploaded footage generates higher engagement than stock
     footage for storytelling content."

Quality warnings correlation:
    "Content with asset quality warnings in QA had 15% lower
     average engagement than content with clean QA."

Asset fatigue detection:
    "Logo variant X used in 18 consecutive posts shows declining
     novelty. Consider rotating with variant Y."

Generated vs uploaded:
    "AI-generated thumbnail images underperform custom-designed
     thumbnails by 12% in click-through rate."
```

## 20.4. Clean Boundary

```text
Asset Library:     "Here is what was used and its metadata."
Learning Memory:   "Here is what that means for future decisions."

Asset Library provides data.
Learning Memory extracts knowledge.
Orchestrator Agent applies that knowledge to future cycles.
```

---

# 21. Asset Library and QA

## 21.1. QA Uses Asset Library Data

During the Quality Assurance stage of the Production Pipeline, QA checks
query the Asset Library for asset-specific verification:

| QA Check | Asset Library Data Used |
|---|---|
| Brand logo presence | Is the correct brand logo asset selected and applied? |
| Logo version check | Is the selected logo the current approved version? |
| Font usage | Are the selected fonts from the Brand System? |
| Asset license validity | Is the license_status of all used assets valid? |
| Source traceability | Do all assets have known source_type? |
| Quality of media assets | Do selected media assets meet quality thresholds? |
| Missing assets | Are there any unresolved AssetRequirements? |
| Expired licenses | Do any selected assets have expired or expiring licenses? |
| Low-quality media | Are any selected assets flagged with quality warnings? |
| Wrong aspect ratio | Do media assets match the channel aspect ratio requirements? |
| Wrong logo version | Is the correct logo variant used (light logo on dark background, etc.)? |
| Unsafe source | Do any assets have source_confidence: low or unknown? |

## 21.2. QA Outcome Impact on Assets

If QA identifies an asset-related issue:

```text
QA Passed:
    → Assets confirmed suitable. Usage records finalized.

QA Passed with Warnings:
    → Warnings about assets included in QA report.
    → Example: "Logo version v1 used; v2 is available."
    → Asset usage records include the warning.

QA Changes Required:
    → If asset is the issue (wrong logo, expired license):
      → Asset selection is re-run.
      → Replacement asset is selected.
      → QA re-run with new asset.

QA Failed:
    → If asset issue is blocking (missing, invalid license):
      → AssetRequirement escalated.
      → Production may halt until resolved.
```

---

# 22. Asset Storage and Project Scoping

## 22.1. Conceptual Storage Model

Assets are project-scoped. The conceptual storage structure:

```text
storage/
projects/
  {project_slug}/
    assets/
      brand/
        logos/            — logo files (PNG, SVG)
        fonts/            — typeface files (TTF, OTF, WOFF2)
        colors/           — color palette definitions
        overlays/         — brand graphic overlays
        watermarks/       — watermark files
        intro_outro/      — video intro/outro elements
      media/
        images/           — photos, illustrations, graphics
        footage/          — video clips, stock footage
        broll/            — supplementary video
        screenshots/      — screen captures
        recordings/       — screen recordings
      audio/
        voice/            — voice recordings, voice profiles
        music/            — background music tracks
        ambient/          — ambient sound files
        effects/          — sound effects
        voiceover/        — generated voiceover files
      templates/
        carousel/         — carousel slide templates
        video/            — video project templates
        thumbnail/        — thumbnail templates
        subtitle/         — subtitle style presets
        export/           — export configuration templates
      uploads/
        raw_video/        — user uploaded raw video
        raw_images/       — user uploaded raw images
        raw_audio/        — user uploaded raw audio
        campaign/         — campaign-specific uploaded materials
      generated/
        images/           — AI-generated images
        video/            — AI-generated video clips
        voiceover/        — synthesized voiceover
        subtitles/        — generated subtitle files
        thumbnails/       — auto-generated thumbnails
        slides/           — generated carousel slides
        derivatives/      — generated derivatives of uploaded media
      references/
        moodboards/       — visual reference collections
        style_refs/       — style reference images
        competitor/       — competitor content references
        examples/         — high-performing content examples
        inspiration/      — general inspiration references
    exports/
      {content_id}/       — ExportPackages
    renders/              — temporary render outputs
```

## 22.2. Platform-Level vs Project-Level

```text
Platform-level (shared):
    Internal templates (default carousel layouts, thumbnail presets,
    subtitle styles). These are platform-provided, project-neutral
    assets. No project-specific content.

Project-level (scoped):
    All brand assets, media, audio, user uploads, generated assets,
    reference assets. Each project's assets are isolated.
```

## 22.3. Storage Rules

1. **Project-scoped by default.** Every asset file lives under its
   project's storage path.

2. **Shared platform templates must remain project-neutral.** No brand
   colors, no specific logos, no project-specific values.

3. **Project-specific assets must not leak into platform core.** No
   project asset paths in platform configuration.

4. **Generated/runtime artifacts must not be committed as source.**
   storage/ is for runtime artifacts only.

5. **Local MVP can use filesystem.** Future SaaS may use object storage
   (S3-compatible). The conceptual model abstracts the storage backend.

6. **Asset metadata may be stored alongside files** (e.g., asset.json
   sidecar files) or in a database (future). The Asset Library spec
   does not prescribe the storage engine.

---

# 23. Asset Permissions and Rights Boundaries

## 23.1. Conceptual Rights Model

The Asset Library tracks rights status — it does NOT enforce legal
compliance. It is a tracking model, not a legal engine. It flags risks.
It does not provide legal guarantees.

## 23.2. License Statuses

| License Status | Description | Production Use |
|---|---|---|
| `unknown` | License status has not been determined | Block or require review |
| `owned` | Asset is owned by the brand/project | Allowed |
| `user_provided` | Provided by user with attestation of rights | Allowed after validation |
| `licensed` | Licensed from a third party (stock, music library) | Allowed within license terms |
| `generated` | Created by AI; rights determined by platform terms | Allowed with terms documented |
| `restricted` | Limited use — specific channels, duration or geography | Allowed only within restrictions |
| `expired` | License period has ended | Blocked |
| `blocked` | Rights issue prevents any use | Blocked permanently |

## 23.3. Usage Rights

```text
internal_only      — internal use only; not for public distribution
organic_social     — organic (unpaid) social media posts
paid_ads           — paid advertising and promotion
website            — owned website and web properties
email              — email marketing
all_channels       — no channel restrictions
restricted_channels — only specific listed channels allowed
```

## 23.4. Rights Rules

```text
Rule 1 — Unknown license blocks or requires review:
    Assets with license_status: unknown must not be used in production
    without explicit operator approval.

Rule 2 — Expired license blocks production:
    Assets with license_status: expired are blocked from selection.

Rule 3 — Restricted platforms must be respected:
    An asset with restricted_platforms: ["tiktok"] must not be selected
    for content targeting TikTok.

Rule 4 — Attribution requirement must be captured:
    If attribution_required is true, the attribution text is stored and
    must be included in the content output.

Rule 5 — Rights status at time of use must be stored:
    AssetUsageRecord captures license_status_at_use to enable audit
    of whether assets were used within their rights window.

Rule 6 — AI-generated assets carry platform terms:
    The license_status for generated assets depends on the generation
    platform's terms of service. This must be documented per platform.
```

---

# 24. Asset Search and Retrieval

## 24.1. Conceptual Retrieval Model

The Asset Library supports structured queries for assets. This is a
conceptual retrieval model — the implementation (database query,
search index, metadata scan) is not prescribed.

## 24.2. Query Parameters

Assets can be queried by any combination of:

```text
Identity:
    project_id, asset_category, asset_type

Technical:
    file_format, mime_type, resolution_min, resolution_max,
    duration_min, duration_max, aspect_ratio

Content compatibility:
    allowed_content_types (includes target), allowed_channels (includes target)

Quality:
    quality_status, quality_score_min

Rights:
    license_status, usage_rights (includes target), expiration_after (date)

Brand:
    brand_fit_score_min, visual_style_tags, tone_tags

Usage:
    reuse_count_max, last_used_before, fatigue_risk_max

Lifecycle:
    status (must be available or validated), created_after, version_min

Tags:
    tags (contains any/all)
```

## 24.3. Return Format

Queries return:

```text
AssetSearchResult:
    assets              — list of matching assets, ranked by selection score
    total_matches       — total count of matching assets
    validation_summary  — count by validation outcome
    warnings            — any caveats about the result set
    alternatives        — near-matches that failed one or two criteria
```

Each returned asset includes:
- Core identity and file metadata;
- Current validation status;
- Quality and brand fit scores;
- License status summary;
- Reuse count and fatigue risk.

## 24.4. Ranking

Results are ranked by the selection scoring model (Section 12). The
highest-scoring asset is the recommended selection. The Production
Pipeline may select it or choose an alternative with explicit reason.

---

# 25. Asset Reuse Strategy

## 25.1. Purpose

Asset reuse is the practice of using the same asset across multiple
content items. It provides brand consistency and production efficiency.
But it carries the risk of visual fatigue — audiences becoming
desensitized to repeated visual elements.

## 25.2. Reusable Assets

Assets with high reuse value:

```text
Logos                        — reused in every content item; low fatigue risk
Fonts                        — reused universally; no fatigue risk
Voice profiles               — reused for voice consistency; moderate fatigue risk
Music themes                 — reused for sonic branding; moderate fatigue risk
Branded overlays             — reused across content; low fatigue risk
Slide templates              — reused for consistent visual structure; moderate risk
Thumbnail templates          — reused for recognizable format; moderate risk
Video intro/outro            — reused for brand identity; low fatigue risk
High-performing generated visuals — reuse if still effective; high fatigue risk
```

## 25.3. Reuse vs Fatigue Balance

```text
Too much reuse:
    → Visual monotony. Audience disengages because everything looks
      the same.

Too little reuse:
    → Brand inconsistency. Audience does not recognize the brand
      across content. Production efficiency is lost.

The balance is maintained through:
    - reuse_priority field (high, medium, low);
    - reuse_count tracking;
    - fatigue_risk assessment;
    - Learning Memory correlation (does higher reuse correlate with
      declining engagement?).
```

## 25.4. Reuse Metadata Fields

| Field | Purpose |
|---|---|
| `reuse_priority` | How aggressively to reuse this asset (high for logos, low for campaign-specific images) |
| `reuse_count` | Times this asset has been used in production |
| `last_used_at` | Timestamp of most recent use |
| `fatigue_risk` | Assessment of audience fatigue risk (high, medium, low) |
| `preferred_content_types` | Content types where this asset works best |
| `deprecated_after` | Suggested maximum reuse count before deprecation |

## 25.5. Reuse Rules

```text
Rule 1 — Always reuse brand identity assets:
    Logos, fonts, colors, watermarks are reused by default.

Rule 2 — Rotate media assets:
    Stock footage clips, background images, music tracks should be
    rotated. Reuse the same clip across too many videos → fatigue.

Rule 3 — Reuse templates with version updates:
    Templates can be reused broadly. Version updates keep them fresh.

Rule 4 — Limit generated asset reuse:
    AI-generated images and thumbnails have higher fatigue risk.
    Monitor reuse_count and rotate when nearing deprecated_after.

Rule 5 — Learning Memory informs reuse decisions:
    When Learning Memory matures, it can detect fatigue signals
    (declining engagement when same visual assets are used repeatedly)
    and recommend rotation.
```

---

# 26. Asset Library Entities

## 26.1. Overview

The Asset Library domain is composed of conceptual entities. These are
functional definitions — they describe the asset domain. They are not
database schemas.

## 26.2. Entity Catalog

### 26.2.1. Asset

The central entity. Represents any managed file or resource in the
library. Contains all universal model fields (Section 8).

### 26.2.2. AssetMetadata

Structured metadata attached to an asset — category-specific fields
beyond the universal model. For example, a video asset has scene_count
and codec; a font asset has font_family and font_weight.

### 26.2.3. AssetValidationResult

The outcome of a validation run on an asset. Contains:
- validation_id, asset_id, validation_timestamp;
- per-category results (technical, brand, quality, rights, production_fit);
- overall outcome (valid, valid_with_warnings, needs_review, invalid, blocked);
- per-check details (check name, passed/failed, message);
- recommendations for resolution.

### 26.2.4. AssetRequirement

A specification for a needed but unavailable asset (Section 14).

### 26.2.5. SelectedAsset

A record of an asset chosen for a production run (Section 13).

### 26.2.6. GeneratedAssetRecord

A record of an AI-generated asset entering the library. Extends Asset
with mandatory generation_context. Contains:
- generation_task_id, generation_method, generation_prompt;
- parameters, model_version, generation_timestamp;
- parent_asset_id if derived from an existing asset.

### 26.2.7. UserUploadedAssetRecord

A record of a user-provided asset entering the library. Extends Asset
with upload-specific metadata. Contains:
- uploaded_by, upload_timestamp, original_filename;
- upload_ip_address (optional, for audit);
- rights_attestation (user's confirmation of rights).

### 26.2.8. AssetUsageRecord

A record of an asset being consumed in production (Section 18).

### 26.2.9. AssetDerivative

Represents the relationship between an original asset and its derivatives.
Contains:
- original_asset_id, derivative_asset_id;
- derivative_type, transformation_applied;
- created_for_content_item;
- reusable flag.

### 26.2.10. AssetCollection

A named grouping of assets for a reusable production context (Section 27).

### 26.2.11. AssetSearchResult

The result of an asset query (Section 24).

### 26.2.12. AssetLicenseRecord

A snapshot of an asset's license information at a point in time. Used for
audit trail — to prove an asset was licensed when it was used.

## 26.3. Entity Relationship Diagram

```text
Asset (1) ──────────────── (N) AssetMetadata
   │
   ├── (N) AssetValidationResult
   │
   ├── (N) SelectedAsset
   │
   ├── (N) AssetUsageRecord
   │
   ├── (N) AssetDerivative (as original)
   │
   ├── (1) AssetDerivative (as derivative)
   │
   ├── (1) GeneratedAssetRecord (if source_type: ai_generated)
   │
   ├── (1) UserUploadedAssetRecord (if source_type: user_upload)
   │
   └── (N) AssetLicenseRecord

AssetRequirement ──────── fulfilled by ──────── (1) Asset (optional)

AssetCollection ──────── contains ──────── (N) Asset

AssetSearchResult ──────── references ──────── (N) Asset
```

---

# 27. Asset Collections

## 27.1. Definition

An **AssetCollection** is a named grouping of assets that form a reusable
production context. Collections simplify asset selection by allowing the
Production Pipeline to request a pre-grouped set of assets rather than
selecting individual assets one by one.

## 27.2. Purpose

Collections are for assets that are consistently used together. Instead
of selecting "logo + font + color palette + slide template + music track"
individually for every production run, the pipeline selects a
"brand identity kit" collection that contains all of them.

## 27.3. Entity Structure

```text
AssetCollection:

    collection_id           — unique identifier
    project_id              — project scope
    name                    — human-readable collection name
    purpose                 — description of when this collection is used
    asset_ids               — list of asset references in this collection
    allowed_content_types   — content types this collection is compatible with
    allowed_channels        — channels this collection is valid for
    status                  — active, deprecated, archived
    created_at              — creation timestamp
    updated_at              — last modification timestamp
```

## 27.4. Collection Examples

| Collection | Typical Contents | Used For |
|---|---|---|
| Brand Identity Kit | Logo variants, fonts, color palette, watermark, brand overlays | All content types |
| Carousel Template Pack | Slide templates, font styles, color presets, brand overlays | Carousel content |
| Video Overlay Pack | Logo overlays, lower thirds, intro/outro, subtitle style, watermark | Video content |
| Campaign Assets | Campaign-specific logos, images, music, templates | Time-limited campaigns |
| Product Launch Kit | Product screenshots, demo footage, feature graphics, CTA templates | Product launch content |
| Seasonal Visual Set | Seasonal color palette, themed overlays, seasonal music | Seasonal/holiday content |
| Voice and Audio Kit | Voice profile, music theme, sound effects, audio logo | Video content audio layer |
| Educational Template Set | Educational slide layouts, diagram templates, icon set | Educational carousels and videos |

## 27.5. Collection Rules

- Collections are project-scoped.
- An asset can belong to multiple collections.
- Collections can be deprecated (brand update) or archived (campaign ended).
- When a collection is selected, all its assets are evaluated for
  current validity (license, quality, brand fit).
- If an asset in a collection is invalid, the collection can still be
  used with a warning — the invalid asset is flagged and an
  AssetRequirement is generated for a replacement.

---

# 28. Error Handling

## 28.1. Error Structure

Asset-specific errors follow the same structured error model used
throughout LOOPRA (see `PRODUCTION_PIPELINE_SPEC.md`, Section 17):

```text
error_code      — unique error identifier
project_id      — project context
asset_id        — asset reference if applicable
content_item_id — content item reference if applicable
severity        — blocking, warning, info
message         — human-readable description
details         — technical details
recommended_action — resolution guidance
```

## 28.2. Asset Error Catalog

### asset_missing

```text
Code: ASSET_ERR_MISSING
Severity: blocking or warning
Message: "Asset '{asset_id}' is not found in the Asset Library."
Details: Asset record may exist but file is missing, or asset was never created.
Recommended Action: "Upload the missing asset file or create a new
    AssetRequirement for generation. If the asset is no longer needed,
    update the Production Plan."
```

### asset_invalid_format

```text
Code: ASSET_ERR_INVALID_FORMAT
Severity: blocking
Message: "Asset '{asset_id}' format '{actual_format}' does not match
    required format '{required_format}'."
Recommended Action: "Convert the asset to the required format or select
    a different asset. A format conversion derivative may be generated."
```

### asset_corrupted

```text
Code: ASSET_ERR_CORRUPTED
Severity: blocking
Message: "Asset '{asset_id}' file is corrupted or unreadable."
Details: Checksum mismatch, decode failure, or zero-byte file.
Recommended Action: "Re-upload or re-generate the asset. The current
    file cannot be used in production."
```

### asset_license_unknown

```text
Code: ASSET_ERR_LICENSE_UNKNOWN
Severity: warning or blocking (configurable)
Message: "Asset '{asset_id}' has unknown license status."
Recommended Action: "Determine and record the license status before
    using this asset in production. Set license_status to owned,
    licensed or generated as appropriate."
```

### asset_license_expired

```text
Code: ASSET_ERR_LICENSE_EXPIRED
Severity: blocking
Message: "Asset '{asset_id}' license expired on '{expiration_date}'."
Recommended Action: "Renew the license or replace the asset with an
    alternative that has valid licensing."
```

### asset_not_allowed_for_channel

```text
Code: ASSET_ERR_CHANNEL_RESTRICTED
Severity: blocking
Message: "Asset '{asset_id}' is restricted from use on platform
    '{platform}'."
Recommended Action: "Select an alternative asset without platform
    restrictions, or verify whether the restriction can be lifted."
```

### asset_quality_below_threshold

```text
Code: ASSET_ERR_QUALITY_LOW
Severity: warning (non-blocking) or blocking (if strict QA)
Message: "Asset '{asset_id}' quality_score ({score}) is below the
    required threshold ({threshold})."
Recommended Action: "Use a higher-quality alternative if available.
    If this is the only available asset, proceed with warning logged
    in QA report."
```

### asset_brand_mismatch

```text
Code: ASSET_ERR_BRAND_MISMATCH
Severity: warning or blocking
Message: "Asset '{asset_id}' brand_fit_score ({score}) is below the
    minimum ({minimum}). The asset may not align with brand identity."
Recommended Action: "Review the asset against Brand System standards.
    Use an alternative if available. If the asset is approved for use,
    override the warning with operator authorization."
```

### asset_scope_violation

```text
Code: ASSET_ERR_SCOPE_VIOLATION
Severity: blocking
Message: "Asset '{asset_id}' belongs to project '{asset_project_id}'
    and cannot be used by project '{requesting_project_id}'."
Recommended Action: "Select an asset from the correct project or import
    the asset into the requesting project if cross-project use is
    authorized."
```

### asset_generation_failed

```text
Code: ASSET_ERR_GENERATION_FAILED
Severity: blocking
Message: "Generation of asset type '{asset_type}' failed.
    Reason: {reason}."
Recommended Action: "Review generation parameters. Retry with adjusted
    prompt or parameters. If generation consistently fails, create a
    user upload AssetRequirement as fallback."
```

### asset_duplicate_detected

```text
Code: ASSET_ERR_DUPLICATE
Severity: info or warning
Message: "Uploaded asset appears to be a duplicate of existing asset
    '{existing_asset_id}' (matching checksum)."
Recommended Action: "The asset already exists in the library. The
    duplicate upload has been flagged. Use the existing asset or
    explicitly create a new version."
```

---

# 29. Current MVP Compatibility

## 29.1. Current State

The current Foundation MVP (text_social_post) does not require a full
Asset Library. Text-only content uses minimal assets — fonts optionally,
and brand identity conceptually but not as managed asset files.

## 29.2. Forward Compatibility

The Asset Library spec is designed to be compatible with the current MVP:

- The universal asset model applies to text content as much as video —
  it simply selects zero or few assets.
- The existing `inspect_package.py` and `validate_package.py` scripts
  remain unaffected — they validate ExportPackage structure, not asset
  metadata.
- The existing smoke loop (Idea → Scenario → ContentItem → ExportPackage
  → Publication → MetricSnapshot) is unchanged.
- No current code, tests or scripts require modification for this spec
  to be valid.

## 29.3. Minimum Future-Compatible MVP Support

When the Asset Library is minimally implemented (beyond spec), the
following is sufficient for Foundation MVP compatibility:

```text
- Project-scoped asset folder (storage/projects/{project_slug}/assets/)
- Metadata file for brand assets (logos, fonts, colors)
- Basic file validation (exists, readable, format check)
- Simple AssetRequirement creation for missing media
- Record of assets used in ExportPackage (in metadata.json)
- The existing export path remains functional
```

## 29.4. When Full Asset Library Activates

The full Asset Library becomes necessary when content types beyond text
are implemented:

| Content Type | Asset Library Requirements |
|---|---|
| carousel | Slide templates, brand logos, image assets, font files |
| short_vertical_video | Footage, voice profiles, music, brand overlays, subtitle styles |
| educational_video | Screen recordings, voice profiles, templates, brand layers |
| infographic | Icons, brand colors, fonts, illustration assets |

---

# 30. Readiness Criteria

## 30.1. Architectural Definition Complete

The Asset Library is considered architecturally defined when:

- [x] Asset taxonomy defined (7 categories — Section 7)
- [x] Universal asset model defined (Section 8)
- [x] Asset source types defined (8 types — Section 9)
- [x] Asset lifecycle defined (17 statuses — Section 10)
- [x] Validation model defined (4 categories, 5 outcomes — Section 11)
- [x] Selection model defined (scoring factors, rules — Section 12)
- [x] SelectedAsset entity defined (Section 13)
- [x] Missing asset handling defined (AssetRequirement, resolution paths — Section 14)
- [x] User uploaded workflow defined (Section 15)
- [x] Generated asset workflow defined (Section 16)
- [x] Versioning and derivatives defined (Section 17)
- [x] Usage tracking defined (Section 18)
- [x] Relationship with ExportPackage defined (Section 19)
- [x] Relationship with Learning Memory defined (Section 20)
- [x] Relationship with QA defined (Section 21)
- [x] Storage and scoping rules defined (Section 22)
- [x] Rights and permissions model defined (Section 23)
- [x] Search and retrieval model defined (Section 24)
- [x] Reuse strategy defined (Section 25)
- [x] Conceptual entities defined (12 entities — Section 26)
- [x] Asset collections defined (Section 27)
- [x] Error handling defined (11 error codes — Section 28)
- [x] Foundation MVP compatibility preserved (Section 29)
- [x] Relationship with Production Pipeline defined (Section 3)
- [x] Relationship with Brand System defined (Section 4)

---

# 31. Related Documents

## 31.1. Core Architecture

```text
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
```

## 31.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
```

## 31.3. Intelligence Layer

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Content cycle specification
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Orchestrator Agent design
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content opportunity analysis
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory architecture
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — Trend detection specification
```

## 31.4. Production Layer

```text
docs/04_production/CONTENT_TYPES_SPEC.md            — Content type definitions and asset system overview
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — Production pipeline stages and asset selection stage
docs/04_production/ASSET_LIBRARY_SPEC.md            — This document
```

## 31.5. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# 32. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Production Layer — Asset Library Specification |

---

# Final Statement

The Asset Library is the production subsystem that answers the question
every content production run must resolve:

> "Which assets should production use for this content item?"

It does not decide what content to create. It does not determine brand
identity. It does not analyze performance. It stores, classifies,
validates, selects, tracks and provides assets — the raw materials of
content production.

The Asset Library serves the Production Pipeline. It provides
deterministic, traceable, brand-aware asset selection. It captures asset
usage for future learning. It stores generated assets for reuse. It flags
missing assets, invalid licenses, quality problems and brand mismatches
before they reach the audience.

Together with the Production Pipeline, Content Types and QA system, the
Asset Library forms the complete Production Layer — the manufacturing
capability of the LOOPRA Autonomous Marketing Operating System.

Build the Asset Library as a reliable production subsystem, not a
general-purpose media platform. Optimize for determinism, traceability
and brand safety. Let Learning Memory discover which assets work best.
Let the Orchestrator Agent decide what to create.

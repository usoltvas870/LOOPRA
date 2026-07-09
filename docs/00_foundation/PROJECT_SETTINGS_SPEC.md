# Project Settings Spec

## Status

Active — LOOPRA Foundation Layer

## Version

v2.0

## Purpose

This document defines Project Settings — the structured configuration
that LOOPRA requires to operate autonomous marketing cycles for a
specific project.

Project Settings answer the question:

> What must LOOPRA know about a project to work independently?

This document is platform-level. Project-specific values belong in
project configuration files.

---

# 1. Project Settings Overview

## 1.1. Definition

**Project Settings** — structured project configuration that defines:

- project identity;
- workspace membership;
- connection to Brand System;
- marketing goals;
- distribution channels;
- content type preferences;
- operational constraints;
- autonomy mode.

## 1.2. Configuration Hierarchy

Project Settings connect the layers of the LOOPRA operating model:

```text
User
    ↓
Workspace
    ↓
Project
    ↓
Brand System
    ↓
Content Cycles
    ↓
Agents
```

## 1.3. Role

Project Settings form the operational context that LOOPRA loads before
starting any marketing cycle.

Without Project Settings, LOOPRA cannot understand:

- why content is being created;
- for whom;
- through which channels;
- toward which goals.

## 1.4. Where Project Settings Are Used

Project Settings inform:

- Chief Content Agent (Orchestrator);
- content cycle management;
- scenario generation;
- content production;
- export package formation;
- publication context;
- metric evaluation;
- learning memory feedback.

---

# 2. Workspace Configuration

## 2.1. Definition

`Workspace` — the top-level container that holds projects, users and
global configuration.

## 2.2. Fields

| Field | Description |
|---|---|
| `workspace_id` | Unique workspace identifier |
| `name` | Human-readable workspace name |
| `type` | Workspace type (internal, agency, enterprise) |
| `status` | active, inactive |
| `projects` | Project references within the workspace |
| `users` | User references (future scope) |
| `permissions` | Role-based access rules (future scope) |
| `global_settings` | Workspace-level defaults |

## 2.3. Minimal Structure

```json
{
  "workspace_id": "ws_001",
  "name": "Agency Workspace",
  "type": "agency",
  "status": "active",
  "projects": ["project_client_a", "project_client_b", "project_client_c"]
}
```

## 2.4. Multi-Project Capability

A single Workspace can contain multiple projects.

Examples:

```text
Agency Workspace:
    - Client A
    - Client B
    - Client C

Business Workspace:
    - Brand X
    - Brand Y
    - Internal Content

Creator Workspace:
    - Personal Brand
```

## 2.5. Current Foundation MVP Scope

In the current Foundation MVP:

- one internal Workspace is sufficient;
- multiple projects are supported within the workspace;
- users, permissions, teams, billing are future scope.

---

# 3. Project Configuration

## 3.1. Definition

`Project` — a distinct operational unit within a Workspace. Each Project
represents a brand, product, content direction or client.

## 3.2. Identity

### Fields

| Field | Description |
|---|---|
| `project_id` | Unique project identifier |
| `workspace_id` | Parent workspace reference |
| `slug` | URL-safe machine identifier, stable after creation |
| `project_name` | Human-readable project name |
| `description` | Short project description |
| `industry` | Industry context for content targeting |
| `default_language` | Primary content language |
| `status` | draft, active, paused, archived |
| `primary_url` | Primary web property URL |
| `created_at` | Creation timestamp |
| `updated_at` | Last modification timestamp |

### Slug Requirements

```text
lowercase
latin characters only
no spaces
unique within workspace
stable after creation unless intentional migration
```

Valid examples:

```text
example_project
client_brand
education_app
```

Slug is used in:

- filesystem paths;
- export package names;
- analytics grouping;
- storage isolation;
- internal references.

### Status Values

```text
draft     — project created, not ready for production
active    — project in operational use
paused    — project temporarily suspended, data preserved
archived  — project inactive, kept for history
```

### Minimal Structure

```json
{
  "project_id": "project_001",
  "workspace_id": "ws_001",
  "slug": "example_project",
  "project_name": "Example Project",
  "description": "Short project description.",
  "industry": "technology",
  "default_language": "ru",
  "status": "active",
  "primary_url": "https://example.com",
  "created_at": "2026-07-08T00:00:00Z",
  "updated_at": "2026-07-08T00:00:00Z"
}
```

## 3.3. Brand Connection

### Principle

Project does not store brand identity internally.

Brand identity lives in the **Brand System** — a separate project-scoped
layer that defines positioning, audience, tone, content strategy and
restrictions.

### Relationship

```text
Project
    ↓
Brand System
    ├── Brand Identity
    ├── Audience Intelligence
    ├── Communication System
    ├── Content Strategy
    ├── Business Goals
    ├── Restrictions and Safety
    └── Autonomy Settings
```

### Connection Fields

| Field | Description |
|---|---|
| `brand_system_id` | Reference to Brand System configuration |
| `brand_system_version` | Active Brand System version (future scope) |

### Why Separate

```text
Project Configuration   = what LOOPRA needs to operate the project
Brand System            = who the brand is and how it communicates

BAD:   Brand identity embedded inside project settings
GOOD:  Project references Brand System; Brand System is project-scoped
```

### Minimal Structure

```json
{
  "project_id": "project_001",
  "brand_system_id": "brand_example",
  "brand_system_version": "1.0"
}
```

Full Brand System structure is defined in `BRAND_SYSTEM_SPEC.md`.

---

# 4. Goals Configuration

## 4.1. Definition

Marketing Goals define **why** LOOPRA creates content for a project.

LOOPRA must understand not just:

> "create content"

but:

> "why create content".

## 4.2. Goal Types

```text
awareness     — reach new audiences, increase visibility
engagement    — deepen audience interaction and loyalty
traffic       — drive visits to web properties
leads         — generate qualified interest and inquiries
sales         — drive conversions and revenue
retention     — maintain existing customer relationships
```

## 4.3. Goal Structure

Each goal can specify:

| Field | Description |
|---|---|
| `goal` | Goal type identifier |
| `priority` | high, medium, low |
| `target` | Qualitative or quantitative target description |
| `metrics` | Key metrics that track this goal |
| `active` | Whether the goal is currently active |

## 4.4. Minimal Structure

```json
{
  "goals": [
    {
      "goal": "awareness",
      "priority": "high",
      "target": "Grow audience by 30% in 3 months.",
      "metrics": ["reach", "impressions", "new_followers"],
      "active": true
    },
    {
      "goal": "engagement",
      "priority": "medium",
      "target": "Increase average interaction rate.",
      "metrics": ["likes", "comments", "saves", "shares"],
      "active": true
    },
    {
      "goal": "leads",
      "priority": "medium",
      "target": "Generate qualified inquiries.",
      "metrics": ["link_clicks", "form_submissions"],
      "active": true
    }
  ]
}
```

## 4.5. How Goals Drive LOOPRA

Marketing goals influence:

| Goal | Effect on LOOPRA Behaviour |
|---|---|
| awareness | Prioritize reach-focused formats, activate discovery topics |
| engagement | Prioritize interactive formats, select conversation topics |
| traffic | Activate link-driving formats and CTA |
| leads | Select lead-generation content pillars, activate direct CTA |
| sales | Select conversion content, apply direct CTA intensity |
| retention | Select loyalty content, apply soft CTA |

Goals connect to Content Strategy pillars defined in the Brand System.

## 4.6. Goals vs Content Objectives

```text
Marketing Goals      = why the brand creates content (business level)
Content Objectives   = what each specific content piece should achieve (tactical level)

Goals are stable and long-term.
Content objectives change per cycle and per content item.
```

Marketing goals are defined in Project Settings.
Content objectives are defined in the Brand System Content Strategy layer.

---

# 5. Channel Configuration

## 5.1. Definition

Channel Configuration defines which distribution platforms LOOPRA
operates for the project and how content is published on each platform.

## 5.2. Supported Channel Types

### Social Channels

```text
telegram
instagram
tiktok
youtube_shorts
linkedin
threads
vk
x
facebook
pinterest
```

### Other Channel Types (future scope)

```text
blog
email
podcast
```

## 5.3. Channel Structure

For each channel:

| Field | Description |
|---|---|
| `platform` | Platform identifier from supported list |
| `enabled` | Whether the channel is active for this project |
| `account_reference` | Platform account identifier or URL |
| `content_formats` | Content types appropriate for this channel |
| `publishing_rules` | Channel-specific publishing constraints |
| `caption_rules` | Caption formatting rules |
| `hashtag_rules` | Hashtag strategy for this channel |
| `cta_rules` | CTA constraints for this channel |
| `schedule_preferences` | Preferred publishing days and times |

## 5.4. Minimal Structure

```yaml
channels:
  - platform: telegram
    enabled: true
    account_reference: "@example_channel"
    content_formats:
      - text_social_post
      - educational_carousel
    publishing_rules:
      max_length: 4096
      supports_formatting: true
    caption_rules: "Long-form reflective posts allowed."
    hashtag_rules: "0-5 hashtags per post."
    cta_rules: "Soft CTA at end of post."
    schedule_preferences:
      days: [mon, wed, fri]
      time: "10:00 MSK"

  - platform: instagram
    enabled: true
    account_reference: "@example_account"
    content_formats:
      - carousel
      - short_video_reel
    publishing_rules:
      max_caption_length: 2200
      aspect_ratio: ["1:1", "4:5", "9:16"]
    caption_rules: "Short caption, soft CTA. Emojis allowed."
    hashtag_rules: "5-15 hashtags."
    cta_rules: "CTA in first comment or caption end."
    schedule_preferences:
      days: [tue, thu, sat]
      time: "12:00 MSK"

  - platform: tiktok
    enabled: false

  - platform: linkedin
    enabled: true
    account_reference: "https://linkedin.com/company/example"
    content_formats:
      - text_social_post
      - carousel
    publishing_rules:
      max_length: 3000
    caption_rules: "Professional tone. Storytelling format."
    hashtag_rules: "3-5 hashtags."
    cta_rules: "Soft professional CTA."
```

## 5.5. Validation Rule

At least one channel must be `enabled: true` for LOOPRA to operate
content cycles.

## 5.6. How Channels Drive LOOPRA

Channel configuration determines:

- which content formats are generated;
- how export packages are assembled per platform;
- which caption and hashtag rules are applied;
- how publication records reference platform data;
- which metrics are relevant for performance evaluation.

---

# 6. Content Type Configuration

## 6.1. Definition

Content Type Configuration defines which content types LOOPRA can
generate for a project.

## 6.2. Supported Content Types

In current Foundation MVP:

```text
text_social_post    — single text post for social platforms
carousel             — multi-slide visual post
short_video_reel     — short-form vertical video
educational_carousel — multi-slide educational format
```

Additional content types belong to future phases.

## 6.3. Structure

| Field | Description |
|---|---|
| `content_type` | Type identifier |
| `enabled` | Whether this type is active |
| `platforms` | Which channels support this type |
| `default_format` | Default output format specification |

## 6.4. Minimal Structure

```json
{
  "content_types": [
    {
      "content_type": "text_social_post",
      "enabled": true,
      "platforms": ["telegram", "linkedin"]
    },
    {
      "content_type": "carousel",
      "enabled": true,
      "platforms": ["instagram", "linkedin"]
    }
  ]
}
```

---

# 7. Operational Constraints

## 7.1. Definition

Operational Constraints define boundaries within which LOOPRA must
operate.

## 7.2. Content Rules

Rules that apply at the project level:

| Field | Description |
|---|---|
| `allowed_topics` | Topics LOOPRA may address |
| `forbidden_topics` | Topics LOOPRA must never address |
| `claim_restrictions` | Claims LOOPRA must not make |
| `legal_disclaimers` | Required disclaimers for content |

### Minimal Structure

```json
{
  "content_rules": {
    "forbidden_topics": [
      "religious claims",
      "political positions",
      "unverified medical advice"
    ],
    "claim_restrictions": [
      "Do not promise guaranteed results",
      "Do not make financial return guarantees"
    ],
    "legal_disclaimers": [
      "Include disclaimer when discussing financial topics"
    ]
  }
}
```

Content rules are also defined in the Brand System Restrictions layer.
Project-level rules supplement Brand System rules.

## 7.3. Autonomy Mode

Defines how much independent action LOOPRA is permitted.

Current Foundation MVP operates in `copilot` mode.

Future modes:

```text
copilot   — LOOPRA suggests, human decides
assisted  — LOOPRA operates with checkpoint reviews
autopilot — LOOPRA operates autonomously with emergency stop
```

Autonomy Settings are fully defined in the Brand System
(`BRAND_SYSTEM_SPEC.md`, Section 9).

---

# 8. Export and Publication Settings

## 8.1. Definition

Export Settings define how LOOPRA prepares content for manual
publication.

## 8.2. Fields

| Field | Description |
|---|---|
| `default_export_path` | Filesystem path for export output |
| `file_naming_pattern` | Template for export file naming |
| `include_metadata` | Whether to include metadata JSON |
| `include_captions` | Whether to include caption text files |
| `include_utm_links` | Whether to generate UTM-tagged links |

## 8.3. UTM Configuration

```json
{
  "utm": {
    "defaults": {
      "utm_source": "{platform}",
      "utm_medium": "organic",
      "utm_campaign": "{project_slug}_{content_series}",
      "utm_content": "{content_id}"
    }
  }
}
```

Each export package references UTM configuration to produce
platform-ready links.

## 8.4. Export Package Structure

```text
exports/
  {project_slug}/
    {content_id}/
      content.{format}
      caption.txt
      metadata.json
```

---

# 9. Analytics Settings

## 9.1. Definition

Analytics Settings define which metrics LOOPRA tracks and evaluates.

## 9.2. Fields

| Field | Description |
|---|---|
| `primary_metrics` | Core performance indicators |
| `secondary_metrics` | Supplementary metrics |
| `conversion_events` | Events that mark a conversion |
| `manual_metrics_enabled` | Whether manual metric import is active |

## 9.3. Minimal Structure

```json
{
  "analytics": {
    "primary_metrics": ["views", "link_clicks", "conversions"],
    "secondary_metrics": ["likes", "comments", "saves", "shares"],
    "conversion_events": ["lead", "purchase"],
    "manual_metrics_enabled": true
  }
}
```

## 9.4. Metrics and Goals

Metrics tracked must align with defined Marketing Goals.

```text
Goal: awareness    → primary metrics: reach, impressions, new_followers
Goal: engagement   → primary metrics: likes, comments, saves, shares
Goal: traffic      → primary metrics: link_clicks
Goal: leads        → primary metrics: form_submissions, link_clicks
Goal: sales        → primary metrics: purchases, conversion_rate
Goal: retention    → primary metrics: return_visits, engagement_rate
```

---

# 10. Storage and Scoping

## 10.1. Project-Scoped Storage

All project settings, assets and outputs must remain project-scoped.

```text
storage/
  projects/
    {project_slug}/
      assets/
      renders/
      exports/
      analytics/
```

## 10.2. Configuration Files

Project-specific configuration lives in:

```text
projects/{project_id}/
    project.yaml        — project settings

docs/07_projects/{project_slug}/
    POSITIONING.md      — brand identity
    TONE_OF_VOICE.md    — communication rules
    CONTENT_PILLARS.md   — content strategy
    BRAND_SYSTEM.yaml   — structured brand system (future)
```

## 10.3. Platform vs Project Separation

```text
Platform-level:
    generic structure definitions
    format specifications
    lifecycle rules

Project-level:
    specific values
    brand configuration
    channel settings
    goal definitions
```

Platform code must never contain project-specific values.

---

# 11. Validation Rules

## 11.1. Workspace Validation

- `workspace_id` not empty;
- `name` not empty;
- `type` from allowed list;
- `status` from allowed list.

## 11.2. Project Identity Validation

- `project_name` not empty;
- `slug` unique within workspace, lowercase, alphanumeric with underscores/hyphens;
- `default_language` specified;
- `status` from allowed list;
- `primary_url` valid URL format.

## 11.3. Goals Validation

- At least one goal defined;
- Each goal has `priority` from allowed list;
- Active goals have `metrics` populated.

## 11.4. Channels Validation

- At least one channel `enabled: true`;
- `platform` value from supported list;
- Channel-specific rules are consistent with platform capabilities.

## 11.5. Brand Connection Validation

- `brand_system_id` references an existing Brand System;
- Brand System completeness checked at cycle start.

## 11.6. Content Rules Validation

- `forbidden_topics` and `claim_restrictions` exist (may be empty);
- No contradictions between project-level rules and Brand System rules.

---

# 12. Completeness Requirements

LOOPRA requires the following minimum configuration before operating
content cycles:

```text
project_name        — defined
slug                — defined and unique
default_language    — defined
primary_url         — defined
brand_system_id     — references existing Brand System
goals               — at least one active goal
channels            — at least one enabled channel
content_types       — at least one enabled type
```

If required fields are missing, LOOPRA must signal incomplete
configuration rather than operating with default assumptions.

---

# 13. Security and Secrets

Project Settings must not store secrets in plain text.

If future phases introduce API keys or tokens:

- store separately from project configuration;
- mask in any UI;
- exclude from export packages;
- exclude from agent prompts;
- exclude from logs and debugging output.

Current Foundation MVP does not require external API keys.

---

# 14. Versioning

## 14.1. Settings Versioning

In future phases, Project Settings should support versioning.

Reason:

- goals may change over time;
- channels may be added or removed;
- content types may evolve;
- analytics must understand which settings were active when content
  was created.

## 14.2. Content Item Reference

Each content item should reference the settings version used:

```json
{
  "content_id": "content_001",
  "project_id": "project_001",
  "settings_version": "1.0"
}
```

Current Foundation MVP stores only active settings without full
version history.

---

# 15. Current Foundation MVP Scope

## 15.1. Included

- Workspace definition (single internal workspace);
- Project identity and basic fields;
- Brand System connection;
- Marketing goals definition;
- Channel configuration;
- Content type configuration;
- Content rules and operational constraints;
- Export settings and UTM configuration;
- Analytics settings;
- Validation rules;
- Completeness requirements.

## 15.2. Not Included

- UI screens and forms;
- API endpoints;
- Database storage;
- Authentication and authorization;
- Team management and permissions;
- Billing and subscription;
- Advanced versioning UI;
- External API key management;
- Marketplace templates;
- Client access mode;
- Multi-language localization management;
- Automatic brand audit.

These capabilities belong to future LOOPRA evolution phases.

---

# 16. Common Mistakes to Avoid

## 16.1. Hardcoding Project Rules

```text
BAD:  template always uses specific brand colors and CTA
GOOD: template loads configuration from Project Settings and Brand System
```

## 16.2. Single Global Defaults

```text
BAD:  all projects share the same channel list, goals and CTA
GOOD: each project defines its own channels, goals, and Brand System
```

## 16.3. Mixing Project Settings with Brand System

```text
BAD:  brand identity, tone of voice and visual style stored in project settings
GOOD: project settings reference Brand System; Brand System owns brand identity
```

## 16.4. Platform-Level CTA Library

```text
BAD:  all projects use one hardcoded CTA set
GOOD: each project has its own CTA configuration in Brand System
```

## 16.5. Leaking Project Values into Platform

```text
BAD:  platform documents reference specific brand goals, channels or rules
GOOD: platform documents define structure only; projects define values
```

---

# 17. Related Documents

```text
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md  — Workspace and Project architecture
docs/00_foundation/DATA_MODEL.md                    — Foundation data model
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture
AGENTS.md                                           — Development rules
STATE.md                                            — Project state
```

---

# 18. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 2.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |

---

# 19. Change History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-07-04 | Initial draft (Content Plant era) |
| 2.0 | 2026-07-08 | Full rewrite for LOOPRA: added Workspace, Goals, Channels; separated Brand System; aligned with current architecture |

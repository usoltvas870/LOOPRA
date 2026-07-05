# Data Model

## 1. Назначение документа

Этот документ описывает базовую модель данных платформы **Content Plant**.

Он фиксирует:

- ключевые сущности платформы;
- связи между Workspace, Project, Brand Profile, Idea, Scenario, Asset, Production, Review, Publication и Metrics;
- какие поля обязательны для MVP;
- какие статусы использовать;
- какие данные являются project-scoped;
- какие данные являются platform-level;
- какие сущности можно отложить на future / SaaS layer.

Документ является платформенным и не привязан к конкретному проекту, бренду или нише.

---

## 2. Главный принцип модели данных

Главный принцип:

> Все данные, которые относятся к конкретному проекту, должны иметь `project_id`.

Это защищает платформу от смешивания данных между проектами и позволяет Content Plant работать как мультипроектная система.

Project-scoped сущности:

```text
Brand Profile
Idea
Scenario
Scene
Asset
Asset Slot
Render Job
Content Item
Export Package
Publication
Metric Snapshot
CTA
Topic
Hook
Campaign
```

Platform-level сущности:

```text
Workspace
Content Format
Production Template
Platform Dictionary
System Settings
Global Integration Definition
```

В MVP может использоваться один внутренний Workspace, но `workspace_id` желательно хранить в ключевых сущностях, чтобы не ломать архитектуру при будущем SaaS-расширении.

---

## 3. Базовая схема связей

```text
Workspace
  └── Project
        ├── Brand Profile
        ├── Project Settings
        ├── CTA Library
        ├── Topics
        ├── Ideas
        │     └── Scenarios
        │           ├── Scenes / Blocks
        │           ├── Visual Prompts
        │           ├── Asset Slots
        │           └── Render Jobs
        │                 └── Content Items
        │                       ├── Output Files
        │                       ├── Export Packages
        │                       ├── Review Decisions
        │                       └── Publications
        │                             └── Metric Snapshots
        └── Analytics Views
```

Упрощённый production loop:

```text
Idea
→ Scenario
→ Asset Slot
→ Asset
→ Render Job
→ Content Item
→ Review Decision
→ Export Package
→ Publication
→ Metric Snapshot
```

---

## 4. Naming conventions

### 4.1. IDs

Рекомендуемый формат ID:

```text
workspace_001
project_001
brand_001
idea_001
scenario_001
scene_001
asset_001
render_001
content_001
export_001
publication_001
metric_001
```

Для MVP допустимы UUID, short IDs или database-generated IDs, если они стабильны.

### 4.2. Slugs

Slug используется для путей, URL, экспорта и UTM.

Требования:

```text
lowercase
latin letters
numbers
hyphens or underscores
no spaces
stable after creation
unique within workspace
```

Примеры:

```text
example_project
client_brand
content_lab
```

---

## 5. Workspace

### 5.1. Назначение

`Workspace` — верхний контейнер, внутри которого находятся проекты.

На MVP может быть один внутренний workspace.

### 5.2. MVP fields

```json
{
  "workspace_id": "workspace_001",
  "name": "Internal Workspace",
  "slug": "internal",
  "type": "internal",
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 5.3. Required fields MVP

```text
workspace_id
name
slug
status
created_at
updated_at
```

### 5.4. Workspace statuses

```text
active
paused
archived
```

### 5.5. MVP notes

В MVP не нужны:

- teams;
- roles;
- billing;
- external user onboarding;
- workspace invitations.

Но `workspace_id` желательно хранить заранее в Project, Brand Profile, Asset, Render Job, Publication и Metrics.

---

## 6. Project

### 6.1. Назначение

`Project` — отдельный бренд, продукт, медиа-направление или клиентский контентный поток внутри Workspace.

Project является ключевой сущностью MVP.

### 6.2. MVP fields

```json
{
  "project_id": "project_001",
  "workspace_id": "workspace_001",
  "project_name": "Example Project",
  "project_slug": "example_project",
  "description": "Short project description.",
  "default_language": "ru",
  "primary_url": "https://example.com",
  "target_platforms": ["instagram", "tiktok", "telegram"],
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 6.3. Required fields MVP

```text
project_id
workspace_id
project_name
project_slug
default_language
status
created_at
updated_at
```

### 6.4. Project statuses

```text
draft
active
paused
archived
```

### 6.5. Rules

- `project_slug` must be unique within workspace.
- All project-specific data must reference `project_id`.
- Project data must not be mixed across modules without explicit project selection.
- Project may have one primary Brand Profile in MVP.

---

## 7. Brand Profile

### 7.1. Назначение

`Brand Profile` — project-scoped configuration that defines how Content Plant should generate, render, review and publish content for a specific project.

Brand Profile is not a platform-level brand. It belongs to Project.

### 7.2. MVP fields

```json
{
  "brand_profile_id": "brand_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "brand_name": "Example Brand",
  "brand_description": "Short brand description.",
  "positioning": "How the brand should be perceived.",
  "audience_summary": "Primary audience summary.",
  "language": "ru",
  "tone_of_voice": {
    "tone_summary": "Clear, warm and practical.",
    "style_keywords": ["clear", "calm", "helpful"],
    "allowed_phrases": [],
    "forbidden_phrases": [],
    "writing_rules": [],
    "claim_restrictions": []
  },
  "visual_identity": {
    "visual_style_summary": "Clean and consistent visual style.",
    "colors": {},
    "fonts": {},
    "logo_asset_id": "",
    "motion_style": {},
    "forbidden_visuals": []
  },
  "content_rules": {
    "allowed_topics": [],
    "forbidden_topics": [],
    "required_disclaimers": [],
    "moderation_notes": []
  },
  "links": {
    "primary_url": "https://example.com",
    "profile_urls": {}
  },
  "platform_settings": {},
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 7.3. Required fields MVP

```text
brand_profile_id
project_id
brand_name
positioning
audience_summary
language
status
created_at
updated_at
```

### 7.4. Brand Profile statuses

```text
draft
incomplete
active
archived
```

### 7.5. Rules

- Scenario Studio must load Brand Profile before generation.
- Production Engine must load Brand Profile before rendering.
- QA must use Brand Profile for tone, claim, CTA and visual checks.
- Publishing Hub must use Brand Profile for links, CTA, captions and platform rules.
- Brand Profile examples must stay generic in platform docs.

---

## 8. Project Settings

### 8.1. Назначение

`Project Settings` — configuration layer for project-level behavior.

In MVP, Project Settings may be stored as fields on Project, Brand Profile or a separate linked object.

### 8.2. Recommended fields

```json
{
  "project_settings_id": "settings_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "timezone": "Europe/London",
  "default_language": "ru",
  "default_platforms": ["telegram", "vk"],
  "export_settings": {},
  "analytics_settings": {},
  "render_defaults": {},
  "created_at": "",
  "updated_at": ""
}
```

### 8.3. MVP notes

A separate `Project Settings` table is optional for MVP. It can be introduced when settings become too large to keep inside Project / Brand Profile.

---

## 9. Platform

### 9.1. Назначение

`Platform` is a stable dictionary of supported publishing channels.

### 9.2. Recommended values MVP

```text
tiktok
instagram
youtube_shorts
telegram
vk
threads
pinterest
```

### 9.3. Future values

```text
linkedin
x
facebook
blog
email
website
```

### 9.4. Platform dictionary entity

```json
{
  "platform_id": "platform_instagram",
  "code": "instagram",
  "name": "Instagram",
  "content_capabilities": ["vertical_video", "carousel", "image", "caption"],
  "supports_direct_links": false,
  "supports_autoposting": "future",
  "status": "active"
}
```

### 9.5. Rules

- Platform dictionary is platform-level.
- Project-specific platform behavior lives in Brand Profile / Project Settings.
- Publishing credentials and account details are not required in MVP.

---

## 10. Content Format

### 10.1. Назначение

`Content Format` describes a universal structure for a type of content.

It is platform-level and must not be project-specific.

### 10.2. MVP / near-MVP content type IDs

```text
dialog_miniseries
text_social_post
atmospheric_video
dialog_carousel
explainer_carousel
pinterest_pin
```

### 10.3. Content Format entity

```json
{
  "content_format_id": "format_dialog_miniseries",
  "content_type": "dialog_miniseries",
  "name": "Dialog Miniseries",
  "default_output_type": "vertical_video",
  "supported_output_types": ["vertical_video"],
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 10.4. Rules

- Do not create project-specific content type IDs.
- Project-specific naming belongs to Project Content Strategy or Brand Profile.
- Format-specific fields should be defined in separate `FORMAT_*.md` documents.

---

## 11. CTA

### 11.1. Назначение

`CTA` is a project-scoped call-to-action object used by Scenario Studio, QA and Publishing Hub.

### 11.2. MVP fields

```json
{
  "cta_id": "cta_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "label": "Learn more",
  "intent": "website_click",
  "intensity": "soft",
  "target": "website",
  "url": "https://example.com",
  "platforms": ["telegram", "vk", "instagram"],
  "funnel_stages": ["trust", "conversion"],
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 11.3. CTA intent values

```text
engagement
profile_visit
website_click
lead
conversion
subscription
retention
download
booking
purchase
```

### 11.4. CTA intensity values

```text
none
soft
medium
direct
```

### 11.5. CTA statuses

```text
draft
active
paused
archived
```

### 11.6. Rules

- CTA must be project-scoped.
- Templates must not hardcode CTA text.
- Scenario Studio may suggest CTA, but Review / QA should validate it against project rules.

---

## 12. Topic

### 12.1. Назначение

`Topic` is a project-scoped thematic label used for ideas, scenarios, publications and analytics.

### 12.2. MVP fields

```json
{
  "topic_id": "topic_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "name": "Example Topic",
  "slug": "example_topic",
  "description": "Short topic description.",
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 12.3. Topic statuses

```text
active
paused
archived
```

### 12.4. MVP notes

Topics can be simple free-text fields in early MVP. A separate Topic table becomes useful when analytics by topic is needed.

---

## 13. Hook

### 13.1. Назначение

`Hook` stores reusable opening lines, patterns or tested attention triggers.

Hooks can come from Trend Radar, successful content or manual input.

### 13.2. MVP fields

```json
{
  "hook_id": "hook_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "text": "Opening hook text.",
  "source_type": "manual",
  "source_id": "",
  "topic_id": "topic_001",
  "funnel_stage": "attention",
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 13.3. Source types

```text
manual
trend
idea
scenario
content_item
analytics
```

### 13.4. MVP notes

Hook can be delayed until Trend Radar / Analytics is implemented. For MVP, hook may be stored directly inside Idea or Scenario.

---

## 14. Idea

### 14.1. Назначение

`Idea` is an early content concept that can become one or more scenarios.

### 14.2. MVP fields

```json
{
  "idea_id": "idea_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "title": "Idea title",
  "description": "Short idea description.",
  "topic": "example_topic",
  "topic_id": "topic_001",
  "funnel_stage": "attention",
  "suggested_content_type": "dialog_miniseries",
  "source_type": "manual",
  "source_id": "",
  "status": "raw",
  "created_at": "",
  "updated_at": ""
}
```

### 14.3. Required fields MVP

```text
idea_id
project_id
title
status
created_at
updated_at
```

### 14.4. Idea statuses

```text
raw
approved
scripted
waiting_assets
in_production
ready
scheduled
published
analyzed
archived
```

### 14.5. Rules

- Idea belongs to one project.
- One Idea may generate multiple Scenarios.
- Idea can be created manually, from Trend Radar, from analytics or from content strategy.
- Idea should preserve `source_type` and `source_id` when possible.

---

## 15. Scenario

### 15.1. Назначение

`Scenario` is a structured production-ready or draft content plan for a specific content format.

Scenario belongs to Project and uses Brand Profile.

### 15.2. MVP fields

```json
{
  "scenario_id": "scenario_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "idea_id": "idea_001",
  "content_type": "dialog_miniseries",
  "title": "Example Scenario",
  "topic_id": "topic_001",
  "funnel_stage": "attention",
  "target_platforms": ["instagram", "tiktok"],
  "brand_profile_id": "brand_001",
  "cta_id": "cta_001",
  "status": "draft",
  "metadata": {},
  "created_at": "",
  "updated_at": ""
}
```

### 15.3. Required fields MVP

```text
scenario_id
project_id
content_type
title
status
created_at
updated_at
```

### 15.4. Scenario statuses

```text
draft
needs_review
approved
needs_assets
ready_to_render
in_production
rendered
rejected
archived
```

### 15.5. Rules

- Scenario must not be generic copy only. It should be structured for a content format.
- Scenario must reference `content_type`.
- Scenario should reference `idea_id` when generated from an Idea.
- Scenario should reference `brand_profile_id` or store brand profile version in render snapshot.
- Scenario can have scenes or text blocks depending on format.

---

## 16. Scene

### 16.1. Назначение

`Scene` is a structured part of scenario for visual or timeline-based formats.

Used by formats such as:

```text
dialog_miniseries
atmospheric_video
dialog_carousel
explainer_carousel
```

### 16.2. MVP fields

```json
{
  "scene_id": "scene_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "order": 1,
  "role": "hook",
  "duration_sec": 3,
  "speaker": "character_1",
  "text": "Scene text.",
  "overlay_text": "Overlay text.",
  "visual_description": "Short visual description.",
  "visual_prompt": "Prompt for external visual generation.",
  "asset_id": "asset_001",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 16.3. Scene roles

```text
hook
problem
context
mirror
insight
reframe
proof
example
cta
closing
```

### 16.4. Scene statuses

```text
draft
needs_asset
asset_linked
ready
rejected
archived
```

### 16.5. Rules

- Scene belongs to Scenario and Project.
- Scene order must be unique within Scenario.
- Scene may have an asset directly, but preferred MVP model is via Asset Slot.
- Overlay length rules belong to format spec and QA.

---

## 17. Text Block

### 17.1. Назначение

`Text Block` is used for non-scene text formats such as `text_social_post`.

### 17.2. MVP fields

```json
{
  "block_id": "block_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "order": 1,
  "role": "opening",
  "platform": "telegram",
  "text": "Block text.",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 17.3. Text block roles

```text
opening
main_thought
explanation
example
product_bridge
cta
hashtags
closing
```

### 17.4. MVP notes

Text blocks can be stored inside Scenario JSON in early MVP. A separate table becomes useful when collaborative editing, versions or analytics by block are needed.

---

## 18. Visual Prompt

### 18.1. Назначение

`Visual Prompt` stores prompts used for external image/video generation or asset creation.

### 18.2. MVP fields

```json
{
  "visual_prompt_id": "prompt_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "scene_id": "scene_001",
  "prompt_text": "Visual generation prompt.",
  "negative_prompt": "Elements to avoid.",
  "target_aspect_ratio": "9:16",
  "source_type": "scenario_studio",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 18.3. Visual prompt statuses

```text
draft
ready
used
archived
```

### 18.4. MVP notes

Visual prompts may be stored directly on Scene in MVP. A separate entity is recommended once prompt history and prompt-to-asset linkage matter.

---

## 19. Asset

### 19.1. Назначение

`Asset` is a project-scoped file used as input for production.

### 19.2. MVP fields

```json
{
  "asset_id": "asset_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "type": "image",
  "filename": "scene_001.png",
  "file_path": "storage/projects/example_project/assets/images/scene_001.png",
  "mime_type": "image/png",
  "size_bytes": 123456,
  "width": 1080,
  "height": 1920,
  "duration_sec": null,
  "aspect_ratio": "9:16",
  "tags": [],
  "source_type": "manual_upload",
  "source_id": "",
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 19.3. Asset types

```text
image
video
audio
logo
background
character
template_asset
document
other
```

### 19.4. Asset statuses

```text
uploading
active
linked
needs_review
rejected
archived
deleted
failed
```

### 19.5. Rules

- Asset must have `project_id`.
- Asset from one project must not be linked to another project's scenario.
- File paths must include project separation.
- Asset can be reused across scenarios within the same project.

---

## 20. Asset Slot

### 20.1. Назначение

`Asset Slot` defines what kind of asset is required for a scene, slide, template or content output.

### 20.2. MVP fields

```json
{
  "asset_slot_id": "slot_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "scene_id": "scene_001",
  "slot_name": "scene_1_visual",
  "required_type": "image",
  "required_aspect_ratio": "9:16",
  "required_duration_sec": null,
  "asset_id": null,
  "required": true,
  "status": "empty",
  "created_at": "",
  "updated_at": ""
}
```

### 20.3. Asset slot statuses

```text
empty
linked
invalid
approved
rejected
optional
```

### 20.4. Rules

- Asset Slot must belong to Project.
- Linked Asset must belong to the same Project.
- Required empty slots block rendering.
- Invalid slots should produce actionable QA messages.

---

## 21. Production Template

### 21.1. Назначение

`Production Template` is a platform-level rendering template that accepts project data, Brand Profile, Scenario and Assets.

### 21.2. MVP fields

```json
{
  "template_id": "template_dialog_miniseries_v1",
  "content_type": "dialog_miniseries",
  "output_type": "vertical_video",
  "version": "1.0",
  "supported_aspect_ratios": ["9:16"],
  "required_slots": [],
  "default_duration_sec": 15,
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

### 21.3. Template statuses

```text
draft
active
deprecated
archived
```

### 21.4. Rules

- Template must not hardcode project-specific colors, CTA, characters or texts.
- Template must apply Brand Profile values at render time.
- Template version should be stored in Render Job snapshot.

---

## 22. Render Job

### 22.1. Назначение

`Render Job` represents a production task that creates output files from Scenario, Assets, Brand Profile and Template.

### 22.2. MVP fields

```json
{
  "render_job_id": "render_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "content_type": "dialog_miniseries",
  "template_id": "template_dialog_miniseries_v1",
  "status": "queued",
  "progress": 0,
  "input_snapshot": {},
  "output_files": [],
  "error": null,
  "created_at": "",
  "started_at": "",
  "finished_at": ""
}
```

### 22.3. Render statuses

```text
queued
validating
rendering
postprocessing
rendered
failed
cancelled
archived
```

### 22.4. Required input snapshot fields MVP

```text
scenario snapshot
asset mapping snapshot
brand profile version
template version
cta
output spec
```

### 22.5. Rules

- Render Job must preserve input snapshot for reproducibility.
- Render Job must not start if required validation blockers exist.
- Render Job creates output files and usually creates or updates Content Item.
- Render Job must belong to Project.

---

## 23. Output File

### 23.1. Назначение

`Output File` is a generated file created by Production Engine.

It is not the same as Asset.

### 23.2. MVP fields

```json
{
  "file_id": "file_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "render_job_id": "render_001",
  "content_id": "content_001",
  "type": "video",
  "path": "storage/projects/example_project/renders/content_001/video.mp4",
  "mime_type": "video/mp4",
  "size_bytes": 1234567,
  "width": 1080,
  "height": 1920,
  "duration_sec": 15,
  "created_at": ""
}
```

### 23.3. Output file types

```text
video
image
audio
caption
metadata
cover
text
zip
other
```

### 23.4. Rules

- Output File is generated by the system.
- Asset is an input file; Output File is a production result.
- Output File should be linked to Content Item when applicable.

---

## 24. Content Item

### 24.1. Назначение

`Content Item` is a produced unit of content that can be reviewed, exported, scheduled, published and analyzed.

### 24.2. MVP fields

```json
{
  "content_id": "content_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "render_job_id": "render_001",
  "content_type": "dialog_miniseries",
  "output_type": "vertical_video",
  "title": "Content title",
  "status": "needs_review",
  "files": [],
  "caption": "",
  "metadata": {},
  "created_at": "",
  "updated_at": ""
}
```

### 24.3. Content Item statuses

```text
rendered
needs_review
approved
rejected
changes_requested
exported
scheduled
published
analyzed
archived
failed
```

### 24.4. Rules

- Content Item should default to `needs_review` after successful render.
- Content Item should not become `approved` without human review in MVP.
- A single Content Item may have multiple Publications.
- Content Item status should not replace Publication status.

---

## 25. Review Decision

### 25.1. Назначение

`Review Decision` stores human review decisions for content items.

### 25.2. MVP fields

```json
{
  "review_id": "review_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "decision": "approved",
  "notes": "",
  "reviewer": "internal_user",
  "created_at": ""
}
```

### 25.3. Review decisions

```text
approved
rejected
changes_requested
```

### 25.4. Rules

- Human Review is mandatory before Publishing Hub treats content as ready-to-publish.
- Review Decision should preserve notes.
- MVP may use a simple reviewer value if there is no full user model.

---

## 26. QA Check

### 26.1. Назначение

`QA Check` stores automated or manual quality checks for scenarios, assets, content items, export packages and publications.

### 26.2. MVP fields

```json
{
  "check_id": "check_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "entity_type": "scenario",
  "entity_id": "scenario_001",
  "check_type": "forbidden_phrase",
  "severity": "warning",
  "status": "failed",
  "message": "Text contains a forbidden phrase.",
  "field": "scenes[2].overlay_text",
  "recommendation": "Edit the overlay text or regenerate this scene.",
  "created_at": ""
}
```

### 26.3. Severity levels

```text
info
warning
error
blocker
```

### 26.4. QA result statuses

```text
passed
failed
skipped
not_applicable
```

### 26.5. Entity types

```text
idea
scenario
scene
asset
asset_slot
render_job
content_item
export_package
publication
metric_snapshot
```

---

## 27. Export Package

### 27.1. Назначение

`Export Package` is a platform-ready or channel-ready set of files prepared for publication.

### 27.2. MVP fields

```json
{
  "export_package_id": "export_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "package_path": "storage/projects/example_project/exports/content_001/",
  "files": [],
  "target_platforms": ["instagram", "tiktok"],
  "status": "ready",
  "created_at": "",
  "updated_at": ""
}
```

### 27.3. Export package statuses

```text
creating
ready
incomplete
failed
archived
```

### 27.4. Rules

- Export Package must belong to Project and Content Item.
- Export Package is owned by Publishing Hub.
- Production Engine may create base output files, technical QA result and render output metadata, but must not own the final Export Package.
- Export Package should include metadata.
- Export Package can be created only after content is approved, unless explicitly marked as draft export.
- Publishing Hub uses Export Package for scheduling and publication flows.

---

## 28. Caption Variant

### 28.1. Назначение

`Caption Variant` stores platform-specific publication text for a Content Item.

### 28.2. MVP fields

```json
{
  "caption_id": "caption_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "platform": "instagram",
  "text": "Caption text.",
  "hashtags": [],
  "cta_id": "cta_001",
  "utm_url": "https://example.com?utm_source=instagram&utm_medium=organic&utm_campaign=example_project_campaign&utm_content=content_001",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 28.3. Caption statuses

```text
draft
ready
approved
archived
```

### 28.4. Rules

- Captions should be platform-specific.
- Caption Variant should be linked to Content Item.
- UTM URL should be generated using project settings.
- Caption must respect Brand Profile tone and platform settings.

---

## 29. Publication

### 29.1. Назначение

`Publication` is a record of publishing one Content Item on one specific platform.

A single Content Item may have multiple Publications.

### 29.2. MVP fields

```json
{
  "publication_id": "publication_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "platform": "instagram",
  "status": "draft",
  "scheduled_at": "",
  "published_at": "",
  "published_url": "",
  "caption_id": "caption_001",
  "export_package_id": "export_001",
  "utm_url": "",
  "notes": "",
  "created_at": "",
  "updated_at": ""
}
```

### 29.3. Publication statuses

```text
draft
ready
scheduled
published
failed
cancelled
archived
```

### 29.4. Rules

- Publication belongs to one platform.
- Publication status is separate from Content Item status.
- Manual publishing is supported in MVP.
- Autoposting can be added later without changing core publication model.
- Published URL should be stored when available.

---

## 30. Metric Snapshot

### 30.1. Назначение

`Metric Snapshot` stores performance data for a Publication at a specific time.

### 30.2. MVP fields

```json
{
  "metric_snapshot_id": "metric_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "publication_id": "publication_001",
  "content_id": "content_001",
  "platform": "instagram",
  "captured_at": "",
  "source_type": "manual",
  "views": 0,
  "likes": 0,
  "comments": 0,
  "saves": 0,
  "shares": 0,
  "profile_visits": 0,
  "link_clicks": 0,
  "registrations": 0,
  "purchases": 0,
  "revenue": 0,
  "currency": "",
  "raw_data": {},
  "created_at": ""
}
```

### 30.3. Source types

```text
manual
csv_import
platform_api
analytics_api
estimated
```

### 30.4. Rules

- Metric Snapshot belongs to Publication and Project.
- Metrics can be manually entered in MVP.
- CSV import can be added after manual input.
- Multiple snapshots may exist for one Publication.
- Analytics should use snapshots rather than overwriting historical values.

---

## 31. Campaign

### 31.1. Назначение

`Campaign` groups ideas, scenarios, content items and publications around a common marketing goal.

### 31.2. MVP fields

```json
{
  "campaign_id": "campaign_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "name": "Example Campaign",
  "slug": "example_campaign",
  "description": "Short campaign description.",
  "start_date": "",
  "end_date": "",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 31.3. Campaign statuses

```text
draft
active
paused
completed
archived
```

### 31.4. MVP notes

Campaign can be optional in early MVP. UTM generation can use default project campaign if campaign entity does not exist yet.

---

## 32. Trend

### 32.1. Назначение

`Trend` stores external or internal market signal that may generate ideas.

Trend Radar may be implemented after core MVP, but data model should reserve a place for it.

### 32.2. MVP / future fields

```json
{
  "trend_id": "trend_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "platform": "tiktok",
  "url": "",
  "title": "Trend title",
  "caption": "",
  "transcript": "",
  "views": 0,
  "likes": 0,
  "comments": 0,
  "shares": 0,
  "hook_text": "",
  "topic_id": "topic_001",
  "emotional_trigger": "",
  "structure_notes": "",
  "adaptation_notes": "",
  "status": "captured",
  "created_at": "",
  "updated_at": ""
}
```

### 32.3. Trend statuses

```text
captured
analyzed
idea_created
ignored
archived
```

### 32.4. MVP notes

Trend Radar is not required for the first production loop. If implemented, start with manual link / CSV import.

---

## 33. Experiment

### 33.1. Назначение

`Experiment` groups content variants that test a hypothesis.

### 33.2. Future fields

```json
{
  "experiment_id": "experiment_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "name": "Hook test",
  "hypothesis": "Short hypothesis.",
  "variant_ids": ["content_001", "content_002"],
  "primary_metric": "link_clicks",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

### 33.3. MVP notes

Experiment can be delayed until Analytics & Optimization is stable.

---

## 34. Batch

### 34.1. Назначение

`Batch` groups generation, production or publication tasks.

### 34.2. Future fields

```json
{
  "batch_id": "batch_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "batch_type": "render",
  "name": "Batch name",
  "entity_ids": [],
  "status": "queued",
  "created_at": "",
  "updated_at": ""
}
```

### 34.3. Batch types

```text
idea_generation
scenario_generation
asset_import
render
export
publication
metrics_import
```

### 34.4. MVP notes

Batch rendering is should-have, not mandatory for the first MVP loop.

---

## 35. Entity ownership matrix

| Entity | workspace_id | project_id | MVP required | Notes |
|---|---:|---:|---:|---|
| Workspace | self | no | yes | One internal workspace allowed |
| Project | yes | self | yes | Core MVP entity |
| Brand Profile | yes | yes | yes | One primary profile per project |
| Project Settings | yes | yes | optional | Can be embedded early |
| Platform Dictionary | no | no | yes | Platform-level reference |
| Content Format | no | no | yes | Platform-level reference |
| CTA | yes | yes | yes | Project-scoped |
| Topic | yes | yes | optional | Can start as free text |
| Hook | yes | yes | optional | Useful for analytics / Trend Radar |
| Idea | yes | yes | yes | Core pipeline entity |
| Scenario | yes | yes | yes | Core pipeline entity |
| Scene | yes | yes | yes for scene formats | Linked to Scenario |
| Text Block | yes | yes | optional | Can be embedded in Scenario |
| Visual Prompt | yes | yes | optional | Can be embedded in Scene |
| Asset | yes | yes | yes | Core production input |
| Asset Slot | yes | yes | yes for video/carousel | Blocks render if required empty |
| Production Template | no | no | yes | Platform-level, versioned |
| Render Job | yes | yes | yes | Core production task |
| Output File | yes | yes | yes | Generated output |
| Content Item | yes | yes | yes | Review / publishing unit |
| QA Check | yes | yes | yes | Can be simple in MVP |
| Review Decision | yes | yes | yes | Human review record |
| Export Package | yes | yes | yes | Export-first MVP |
| Caption Variant | yes | yes | yes | Platform-specific text |
| Publication | yes | yes | yes | Manual publishing supported |
| Metric Snapshot | yes | yes | yes | Manual metrics supported |
| Campaign | yes | yes | optional | Useful for UTM |
| Trend | yes | yes | later | Trend Radar MVP |
| Experiment | yes | yes | later | Optimization layer |
| Batch | yes | yes | later | Batch operations |

---

## 36. Canonical lifecycle overview

### 36.1. Idea lifecycle

```text
raw
→ approved
→ scripted
→ waiting_assets
→ in_production
→ ready
→ scheduled
→ published
→ analyzed
→ archived
```

### 36.2. Scenario lifecycle

```text
draft
→ needs_review
→ approved
→ needs_assets
→ ready_to_render
→ in_production
→ rendered
```

Alternative exits:

```text
rejected
archived
```

### 36.3. Asset lifecycle

```text
uploading
→ active
→ linked
```

Alternative states:

```text
needs_review
rejected
archived
deleted
failed
```

### 36.4. Render lifecycle

```text
queued
→ validating
→ rendering
→ postprocessing
→ rendered
```

Alternative states:

```text
failed
cancelled
archived
```

### 36.5. Content Item lifecycle

```text
rendered
→ needs_review
→ approved
→ exported
→ scheduled
→ published
→ analyzed
```

Alternative states:

```text
rejected
changes_requested
archived
failed
```

### 36.6. Publication lifecycle

```text
draft
→ ready
→ scheduled
→ published
```

Alternative states:

```text
failed
cancelled
archived
```

---

## 37. Minimal MVP database tables

The minimum useful MVP can start with these tables / collections:

```text
workspaces
projects
brand_profiles
ctas
ideas
scenarios
scenes
assets
asset_slots
production_templates
render_jobs
output_files
content_items
qa_checks
review_decisions
export_packages
caption_variants
publications
metric_snapshots
```

Can be delayed:

```text
project_settings
topics
hooks
visual_prompts
text_blocks
campaigns
trends
experiments
batches
```

---

## 38. File path conventions

Recommended project-scoped storage:

```text
storage/
  projects/
    {project_slug}/
      assets/
        images/
        videos/
        audio/
        logos/
        backgrounds/
        characters/
        documents/
        template_assets/
      renders/
        {content_id}/
      exports/
        {content_id}/
      imports/
      analytics/
```

Example:

```text
storage/projects/example_project/assets/images/scene_001.png
storage/projects/example_project/renders/content_001/video.mp4
storage/projects/example_project/exports/content_001/metadata.json
```

Rules:

- no shared global asset folder for project-specific files;
- output files and source assets should be separated;
- export packages should be reproducible from metadata when possible;
- file paths should not depend on project display name.

---

## 39. Metadata principles

Each production output should preserve metadata sufficient for review, publishing and analytics.

Minimum content metadata:

```json
{
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "scenario_id": "scenario_001",
  "render_job_id": "render_001",
  "content_type": "dialog_miniseries",
  "output_type": "vertical_video",
  "target_platforms": ["instagram", "tiktok"],
  "cta_id": "cta_001",
  "created_at": ""
}
```

Minimum publication metadata:

```json
{
  "project_id": "project_001",
  "content_id": "content_001",
  "publication_id": "publication_001",
  "platform": "instagram",
  "scheduled_at": "",
  "published_at": "",
  "published_url": "",
  "utm_url": "",
  "status": "draft"
}
```

---

## 40. Versioning principles

MVP should preserve enough versioning to debug outputs.

Important snapshot fields:

```text
scenario snapshot
brand profile version
template version
asset mapping snapshot
cta snapshot
output spec
```

Versioning can be simple in MVP:

- store `input_snapshot` on Render Job;
- store `brand_profile_version` if Brand Profile supports versions;
- store `template_version` on Render Job;
- store generated metadata with each output.

Full version history can be added later.

---

## 41. MVP implementation notes

### 41.1. Start simple

The first implementation does not need a perfect normalized database.

Acceptable MVP shortcuts:

- scenes stored as JSON inside Scenario;
- visual prompts stored on scenes;
- text blocks stored inside Scenario or Content Item;
- Project Settings embedded in Project / Brand Profile;
- Topic stored as free text;
- one internal user without full auth model;
- manual metrics input before API integrations.

### 41.2. Do not break core principles

Even with shortcuts, do not violate:

- project separation;
- Brand Profile separation;
- export-first publishing;
- human review before publishing;
- no project-specific hardcode in platform templates;
- metadata preservation.

---

## 42. Not in MVP

The following data areas should not be implemented unless explicitly approved:

```text
billing accounts
subscription plans
external user accounts
teams
roles and permissions
marketplace entities
public onboarding funnels
template marketplace purchases
complex attribution graph
full AI optimization engine
```

They can be considered in future SaaS documents, but they are outside MVP data model.

---

## 43. Open questions

Before implementation, clarify:

1. Should Scenario store scenes as JSON first, or should Scene be a separate table from day one?
2. Should Project Settings be a separate table or embedded inside Project / Brand Profile for MVP?
3. Should Content Item be created immediately after render starts, or only after render succeeds?
4. Should Metrics allow multiple snapshots per publication from day one?
5. What storage backend is used in MVP: local filesystem or S3-compatible storage?

Recommended MVP defaults:

```text
Scene: separate table if web UI editing is planned early; JSON if speed matters more.
Project Settings: embedded first, separate later.
Content Item: create after successful render.
Export Package: Publishing Hub creates platform-ready package from approved Content Item.
Metric Snapshot: allow multiple snapshots from day one.
Storage: local filesystem first, S3-compatible later.
```

---

## 44. Summary

The Content Plant data model should support a simple but complete production loop:

```text
Workspace
→ Project
→ Brand Profile
→ Idea
→ Scenario
→ Asset Slots
→ Assets
→ Render Job
→ Content Item
→ QA
→ Review
→ Export Package
→ Publication
→ Metric Snapshot
```

The MVP data model must remain practical, but it should not sacrifice the main architectural promise of Content Plant:

> One platform, multiple projects, reusable formats, project-specific brand profiles, export-first publishing and measurable content loops.

# Scenario Studio Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает модуль **Scenario Studio** в платформе **Content Plant**.

Он фиксирует:

- зачем нужен Scenario Studio;
- какие сценарии он создаёт;
- какие входные данные использует;
- как работает генерация сценариев;
- как сценарии связаны с форматами, Brand Profile, CTA и ассетами;
- какие статусы и действия нужны;
- какие данные сохраняются;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Scenario Studio

Scenario Studio превращает идею в структурированный сценарий для конкретного контентного формата.

Базовая цепочка:

```text
Idea
→ Content Type
→ Brand Profile
→ Scenario Draft
→ Scenes / Blocks
→ Visual Prompts
→ Captions
→ Review
→ Production-ready Scenario
```

Scenario Studio — это не просто текстовый генератор.  
Это рабочий модуль, который переводит сырой смысл в производственную форму.

---

## 3. Основной принцип

Scenario Studio должен быть format-aware и project-aware.

Это значит:

```text
Universal Content Format
+ Project Settings
+ Brand Profile
+ CTA Library
+ Idea
= Scenario
```

Сценарий не должен быть generic-текстом.  
Он должен быть готовым производственным объектом, который дальше можно отправить в Asset Library, Production Engine, Text Social Posts или Publishing Hub.

---

## 4. Где находится Scenario Studio в pipeline

Scenario Studio находится после Idea Bank и до Asset Library / Production Engine.

```text
Idea Bank
→ Scenario Studio
→ Visual Prompt Builder
→ Asset Library
→ Production Engine
→ Review
→ Export / Publishing
```

Также Scenario Studio может создавать текстовые посты и captions без полноценного video production.

---

## 5. Основные сценарии пользователя

Пользователь должен уметь:

1. Создать сценарий из идеи.
2. Создать сценарий вручную.
3. Выбрать content type.
4. Сгенерировать draft.
5. Отредактировать сцены.
6. Сгенерировать visual prompts.
7. Добавить или выбрать CTA.
8. Сгенерировать captions.
9. Отправить сценарий в assets / production.
10. Создать repurpose bundle из сценария.

---

## 6. Поддерживаемые content types MVP

Scenario Studio должен поддерживать минимум:

```text
dialog_miniseries
text_social_post
```

Should-have:

```text
atmospheric_video
dialog_carousel
explainer_carousel
```

Could-have:

```text
pinterest_pin
```

---

## 7. Scenario entity

Scenario — это структурированный объект, связанный с проектом и форматом.

Минимальные поля:

```text
scenario_id
project_id
idea_id
content_type
title
funnel_stage
target_platforms
status
scenes
cta_id
created_at
updated_at
```

Пример:

```json
{
  "scenario_id": "scenario_001",
  "project_id": "project_001",
  "idea_id": "idea_001",
  "content_type": "dialog_miniseries",
  "title": "Example Scenario",
  "funnel_stage": "attention",
  "target_platforms": ["tiktok", "instagram"],
  "status": "draft",
  "scenes": [],
  "cta_id": "cta_001",
  "created_at": "",
  "updated_at": ""
}
```

---

## 8. Scenario statuses

Рекомендуемые статусы:

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

### 8.1. draft

Сценарий создан, но не утверждён.

### 8.2. needs_review

Сценарий ожидает проверки человеком.

### 8.3. approved

Сценарий утверждён.

### 8.4. needs_assets

Для сценария нужны ассеты.

### 8.5. ready_to_render

Все обязательные ассеты привязаны, можно запускать production.

### 8.6. in_production

Сценарий используется в render job.

### 8.7. rendered

По сценарию создан output.

### 8.8. rejected

Сценарий отклонён.

### 8.9. archived

Сценарий скрыт из активной работы.

---

## 9. Входные данные для генерации

Scenario Studio должен использовать:

- Idea;
- Project Settings;
- Brand Profile;
- Content Format Spec;
- CTA Library;
- target platforms;
- funnel stage;
- optional trend reference;
- optional source content;
- optional user notes.

---

## 10. Idea input

Минимальная идея:

```json
{
  "idea_id": "idea_001",
  "project_id": "project_001",
  "title": "Idea title",
  "description": "Short idea description",
  "topic": "topic",
  "funnel_stage": "attention",
  "suggested_content_type": "dialog_miniseries"
}
```

Scenario Studio должен уметь работать даже с короткой идеей, но чем богаче input, тем лучше результат.

---

## 11. Brand Profile input

Scenario Studio должен использовать из Brand Profile:

```text
positioning
audience_summary
tone_of_voice
allowed_phrases
forbidden_phrases
content_rules
CTA Library
visual_style_summary
target_platforms
primary_url
```

Если Brand Profile неполный, Scenario Studio должен показывать warning.

---

## 12. Format Spec input

Каждый content type должен иметь spec.

Format Spec задаёт:

- структуру сценария;
- количество сцен или блоков;
- роли сцен;
- ограничения по длине;
- тип текста;
- требования к visual prompts;
- требования к captions;
- export expectations.

Пример:

```text
dialog_miniseries:
  Hook
  Problem
  Mirror
  Reframe
  CTA
```

---

## 13. Scenario generation flow

Базовый flow:

```text
1. Select idea
2. Select content type
3. Select target platforms
4. Load project settings
5. Load Brand Profile
6. Load format spec
7. Select CTA or CTA intensity
8. Generate draft
9. Run text QA
10. Show draft to user
11. User approves or edits
```

---

## 14. Generation modes

Scenario Studio может поддерживать режимы:

```text
generate_new
regenerate_full
regenerate_scene
rewrite_for_platform
shorten
expand
change_tone
create_variation
```

MVP:

```text
generate_new
regenerate_full
regenerate_scene
```

---

## 15. Scene model

Для форматов со сценами используется Scene object.

Поля:

```text
scene_id
order
role
duration_sec
speaker
text
overlay_text
visual_description
visual_prompt
asset_id
status
```

Пример:

```json
{
  "scene_id": "scene_001",
  "order": 1,
  "role": "hook",
  "duration_sec": 3,
  "speaker": "character_a",
  "text": "Opening line",
  "overlay_text": "Short overlay",
  "visual_description": "Short visual description",
  "visual_prompt": "",
  "asset_id": null,
  "status": "draft"
}
```

---

## 16. Scene roles

Рекомендуемые универсальные роли:

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

Конкретный формат может использовать свою комбинацию.

---

## 17. Text blocks model

Для текстовых форматов без сцен можно использовать blocks.

Поля:

```text
block_id
order
role
text
platform
status
```

Роли:

```text
opening
main_thought
explanation
example
product_bridge
cta
hashtags
```

---

## 18. Scenario editor UI

Scenario editor должен показывать:

```text
Scenario metadata
Scenes / blocks
Visual prompts
CTA
Captions
QA warnings
Actions
```

Основные действия:

- edit title;
- edit scene text;
- edit overlay;
- edit prompt;
- regenerate scene;
- approve scenario;
- reject scenario;
- send to asset mapping.

---

## 19. Metadata panel

Metadata panel должен показывать:

- project;
- idea;
- content type;
- funnel stage;
- target platforms;
- CTA;
- status;
- created date;
- updated date;
- author/source, if available.

---

## 20. Visual prompts

Scenario Studio должен уметь генерировать visual prompts для сцен или слайдов.

Prompt должен учитывать:

- scene role;
- scene text;
- visual description;
- format requirements;
- Brand Profile visual identity;
- forbidden visuals;
- target aspect ratio;
- safe zones.

---

## 21. Visual prompt actions

Для каждого prompt:

```text
copy
edit
regenerate
mark as used
attach asset
```

В MVP достаточно:

```text
copy
edit
regenerate
```

---

## 22. Captions

Scenario Studio может генерировать captions для платформ.

Caption должен учитывать:

- platform;
- content type;
- funnel stage;
- CTA;
- hashtags;
- link / UTM;
- project tone.

Caption output:

```text
caption_tiktok.txt
caption_instagram.txt
caption_youtube_shorts.txt
caption_telegram.txt
```

Для MVP достаточно caption draft внутри scenario или export package.

---

## 23. CTA selection

Scenario Studio должен позволять:

- выбрать CTA из CTA Library;
- выбрать CTA intensity;
- сгенерировать текстовый CTA;
- отключить CTA;
- указать platform-specific CTA.

CTA должен быть project-scoped.

---

## 24. Repurpose from scenario

Один сценарий может порождать несколько content items.

Пример:

```text
scenario
→ vertical video
→ caption
→ text post
→ carousel
→ pin
```

MVP minimum:

```text
scenario
→ dialog_miniseries video
→ caption
→ text social posts
```

Scenario Studio должен хранить source linkage, чтобы repurpose не терял происхождение.

---

## 25. Scenario variations

Scenario Studio должен поддерживать варианты.

Variation может отличаться:

- hook;
- platform;
- length;
- CTA intensity;
- tone;
- visual direction;
- audience segment.

MVP может поддерживать simple duplicate:

```text
Duplicate scenario
→ edit variation
```

---

## 26. QA checks

Scenario Studio должен запускать basic QA.

Проверки:

- project_id exists;
- content_type valid;
- required scenes exist;
- scene text not empty;
- overlay length acceptable;
- forbidden phrases absent;
- CTA valid;
- target platform valid;
- tone roughly matches Brand Profile;
- no unsupported claims;
- scenario has next action.

---

## 27. QA warnings

Warnings должны быть видны в editor.

Примеры:

```text
Scene 2 overlay is too long for vertical video.
CTA is missing.
Brand Profile has no forbidden phrases list.
Scenario uses a phrase from forbidden list.
No target platform selected.
```

Warnings не всегда блокируют approve.  
Critical errors должны блокировать production.

---

## 28. Required data by format

### 28.1. dialog_miniseries

Required:

- title;
- 3–6 scenes;
- hook scene;
- CTA or closing;
- visual prompt per scene;
- target platform.

### 28.2. text_social_post

Required:

- platform;
- post subtype;
- body;
- CTA optional;
- metadata.

### 28.3. atmospheric_video

Required:

- short text sequence;
- visual direction;
- duration;
- music/mood notes;
- CTA optional.

### 28.4. carousel

Required:

- slides;
- cover;
- closing / CTA;
- visual direction.

---

## 29. Scenario actions

Available actions:

```text
Generate
Regenerate
Save Draft
Approve
Reject
Duplicate
Archive
Generate Visual Prompts
Generate Captions
Generate Text Posts
Send to Assets
Send to Production
```

MVP actions:

```text
Generate
Regenerate
Save Draft
Approve
Generate Visual Prompts
Generate Captions
Send to Assets
```

---

## 30. Scenario list filters

Scenario list should support filters:

```text
status
content_type
funnel_stage
platform
topic
date
needs_assets
ready_to_render
```

MVP:

```text
status
content_type
date
```

---

## 31. Scenario source linkage

Scenario can be created from:

```text
idea
trend
existing content
manual input
analytics recommendation
```

MVP source types:

```text
idea
manual
```

The scenario must preserve:

```text
source_type
source_id
```

---

## 32. Manual scenario creation

User can create scenario manually.

Flow:

```text
1. Click New Scenario
2. Select project
3. Select content type
4. Enter title
5. Add scenes or blocks
6. Save draft
```

Manual scenarios still need project_id and content_type.

---

## 33. Prompt templates

Scenario Studio should use prompt templates from platform and project layers.

Prompt structure:

```text
System rules
Platform format spec
Project Brand Profile
Input idea
Generation task
Output schema
```

Prompt templates must not hardcode a specific project.

---

## 34. Output schema enforcement

Generated output should follow schema.

Example for scene-based scenario:

```json
{
  "title": "",
  "content_type": "",
  "funnel_stage": "",
  "target_platforms": [],
  "scenes": [
    {
      "role": "",
      "duration_sec": 0,
      "speaker": "",
      "text": "",
      "overlay_text": "",
      "visual_description": "",
      "visual_prompt": ""
    }
  ],
  "cta_id": "",
  "caption_draft": ""
}
```

If output is invalid, Scenario Studio should ask for regeneration or show schema error.

---

## 35. Integration with Asset Library

After approval, Scenario Studio should identify required assets.

Example:

```text
Scene 1 needs image or video
Scene 2 needs image or video
Scene 3 needs image or video
```

It should send required asset slots to Asset Library.

---

## 36. Asset slot model

```json
{
  "asset_slot_id": "slot_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "scene_id": "scene_001",
  "required_type": "image",
  "aspect_ratio": "9:16",
  "status": "empty"
}
```

---

## 37. Integration with Production Engine

Production Engine can render only when:

- scenario status is approved or ready_to_render;
- required assets are linked;
- content_type has production template;
- project settings are complete enough;
- output format is selected.

Scenario Studio should expose readiness state.

---

## 38. Readiness state

Readiness can be:

```text
not_ready
needs_review
needs_assets
ready_to_render
```

Readiness reason should be visible.

Example:

```text
Not ready: Scene 3 has no visual prompt.
```

---

## 39. Integration with Text Social Posts

Scenario Studio can generate text posts from scenario.

Output:

```text
telegram.txt
threads.txt
vk.txt
metadata.json
```

This is especially useful for repurpose bundles.

---

## 40. Integration with Publishing Hub

Scenario Studio itself does not publish.

It provides:

- scenario;
- caption drafts;
- CTA;
- metadata;
- content package inputs.

Publishing Hub handles:

- schedule;
- platform-specific package;
- published URL;
- status;
- metrics linkage.

---

## 41. Data model: Scenario

Recommended fields:

```json
{
  "scenario_id": "scenario_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "source_type": "idea",
  "source_id": "idea_001",
  "content_type": "dialog_miniseries",
  "title": "Scenario title",
  "topic": "topic",
  "funnel_stage": "attention",
  "target_platforms": ["instagram", "tiktok"],
  "status": "draft",
  "scenes": [],
  "blocks": [],
  "cta_id": null,
  "caption_drafts": [],
  "qa_warnings": [],
  "created_at": "",
  "updated_at": ""
}
```

---

## 42. Data model: Caption Draft

```json
{
  "caption_id": "caption_001",
  "scenario_id": "scenario_001",
  "project_id": "project_001",
  "platform": "instagram",
  "text": "",
  "cta_id": "cta_001",
  "hashtags": [],
  "utm": "",
  "status": "draft"
}
```

---

## 43. API endpoints MVP

Recommended endpoints:

```text
GET /api/projects/:project_id/scenarios
POST /api/projects/:project_id/scenarios
GET /api/scenarios/:scenario_id
PATCH /api/scenarios/:scenario_id
POST /api/scenarios/:scenario_id/generate
POST /api/scenarios/:scenario_id/regenerate
POST /api/scenarios/:scenario_id/generate-prompts
POST /api/scenarios/:scenario_id/generate-captions
POST /api/scenarios/:scenario_id/approve
POST /api/scenarios/:scenario_id/archive
```

MVP can simplify if local-first or file-based.

---

## 44. UI requirements

Scenario Studio UI should include:

- scenario list;
- scenario detail/editor;
- scene/block editor;
- visual prompt panel;
- CTA selector;
- caption panel;
- QA panel;
- actions panel.

---

## 45. Empty states

If no scenarios exist:

```text
No scenarios yet.
Create one from an idea or start manually.

[Open Idea Bank]
[New Scenario]
```

If Brand Profile incomplete:

```text
Brand Profile is incomplete.
Generated scenarios may be generic.

[Open Project Settings]
```

---

## 46. Error states

Examples:

```text
Cannot generate scenario: content type is missing.
Cannot approve scenario: required scenes are empty.
Cannot send to production: assets are missing.
```

Error message should include next action.

---

## 47. MVP scope

MVP includes:

- scenario list;
- create scenario from idea;
- manual scenario creation;
- support for `dialog_miniseries`;
- support for `text_social_post`;
- scene/block editor;
- generate visual prompts;
- generate captions;
- CTA selector;
- basic QA;
- statuses;
- source linkage;
- asset slots;
- readiness state.

---

## 48. Not in MVP

MVP does not include:

- complex collaborative editing;
- comments and mentions;
- version history UI;
- advanced A/B variations;
- full trend-to-scenario automation;
- multi-agent debate;
- paid ads scripts;
- auto-publishing;
- complete language localization system;
- full prompt marketplace.

---

## 49. Definition of Done

Scenario Studio считается готовым для MVP, если пользователь может пройти путь:

```text
Open idea
→ Choose content type
→ Generate scenario
→ Edit scenes
→ Generate visual prompts
→ Select CTA
→ Generate caption
→ Approve scenario
→ Send to assets / production
```

Сценарий должен быть structured data, а не просто текст в поле.

---

## 50. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/02_platform_architecture/DATA_MODEL.md
docs/03_modules/ASSET_LIBRARY_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md
docs/04_content_formats/FORMAT_DIALOG_MINISERIES.md
docs/04_content_formats/FORMAT_TEXT_SOCIAL_POSTS.md
docs/05_product_design/USER_WORKFLOWS.md
docs/05_product_design/WEB_UI_SPEC.md
docs/05_product_design/PROJECT_SETTINGS_SPEC.md
```

---

## 51. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 52. Следующие документы

После этого документа необходимо создать:

1. `docs/03_modules/ASSET_LIBRARY_SPEC.md`
2. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
3. `docs/03_modules/QA_AND_REVIEW.md`
4. `docs/02_platform_architecture/DATA_MODEL.md`
5. `docs/02_platform_architecture/PIPELINES_SPEC.md`

# Project Settings Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает экран и модель **Project Settings** в платформе **Content Plant**.

Он фиксирует:

- какие настройки есть у проекта;
- какие поля обязательны для MVP;
- как Project Settings связаны с Brand Profile, CTA, ссылками, платформами, экспортом и аналитикой;
- как настройки используются в генерации, production, review и analytics;
- какие проверки нужны;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному бренду или проекту.

---

## 2. Роль Project Settings

Project Settings — это центр управления конкретным проектом.

Если Project — это отдельный бренд, продукт или контентное направление, то Project Settings отвечает за то, чтобы вся система понимала:

```text
что это за проект
как он говорит
как он выглядит
куда ведёт трафик
какие платформы используются
какие CTA доступны
какие ограничения нельзя нарушать
как экспортировать контент
как считать результаты
```

---

## 3. Главный принцип

Project Settings должны отделять проектный слой от платформенного.

Правильно:

```text
Universal format + Project Settings + Brand Profile = project-specific content
```

Неправильно:

```text
Hardcoded project rules inside templates, prompts or render scripts
```

Вся проектная специфика должна жить в настройках проекта, Brand Profile и связанных project-level документах, а не в ядре платформы.

---

## 4. Где используется Project Settings

Project Settings используются в:

- Dashboard;
- Idea Bank;
- Scenario Studio;
- Visual Prompt Builder;
- Asset Library;
- Production Engine;
- Review / QA;
- Publishing Hub;
- Export Packages;
- Analytics;
- Agent tasks.

---

## 5. Основные разделы Project Settings

Рекомендуемая структура:

```text
Basics
Brand Profile
Audience
Tone of Voice
Visual Identity
CTA Library
Links and UTM
Platforms
Content Rules
Export Settings
Analytics Settings
Integrations
Advanced
```

Для MVP часть разделов можно объединить на одной странице.

---

## 6. Basics

### 6.1. Назначение

Basics описывает базовую идентичность проекта.

### 6.2. Поля MVP

```text
project_name
project_slug
description
default_language
primary_url
status
created_at
updated_at
```

### 6.3. Пример

```json
{
  "project_id": "project_001",
  "project_name": "Example Project",
  "project_slug": "example_project",
  "description": "Short description of the project.",
  "default_language": "ru",
  "primary_url": "https://example.com",
  "status": "active"
}
```

---

## 7. Project slug

`project_slug` используется для:

- URL;
- folder paths;
- export package names;
- UTM;
- internal identifiers;
- analytics grouping.

Правила:

```text
lowercase
latin letters
numbers
underscores or hyphens
no spaces
unique within workspace
```

Примеры:

```text
example_project
brand_alpha
client_001
```

---

## 8. Project status

Возможные статусы:

```text
draft
active
paused
archived
```

### 8.1. Draft

Проект создан, но не готов к production.

### 8.2. Active

Проект используется в работе.

### 8.3. Paused

Проект временно остановлен, но данные сохранены.

### 8.4. Archived

Проект не используется, но доступен для истории.

---

## 9. Brand Profile

Brand Profile — ключевой блок Project Settings.

Он отвечает за:

- позиционирование;
- аудиторию;
- tone of voice;
- визуальный стиль;
- CTA;
- ограничения.

В MVP Brand Profile можно хранить как вложенную структуру внутри project settings или как отдельную связанную сущность.

Важно: все генераторы должны загружать Brand Profile перед созданием контента.

---

## 10. Audience

Audience описывает целевую аудиторию проекта.

Поля MVP:

```text
audience_summary
primary_segments
audience_pains
audience_desires
audience_language
audience_objections
```

Пример:

```json
{
  "audience_summary": "People interested in improving a specific area of their life or work.",
  "primary_segments": ["segment_1", "segment_2"],
  "audience_pains": ["pain_1", "pain_2"],
  "audience_desires": ["desire_1", "desire_2"],
  "audience_objections": ["objection_1"]
}
```

---

## 11. Tone of Voice

Tone of Voice описывает, как проект должен говорить.

Поля MVP:

```text
tone_summary
style_keywords
allowed_phrases
forbidden_phrases
writing_rules
claim_restrictions
```

Пример:

```json
{
  "tone_summary": "Clear, warm and practical.",
  "style_keywords": ["clear", "calm", "helpful"],
  "allowed_phrases": [],
  "forbidden_phrases": [],
  "writing_rules": [
    "Use short paragraphs",
    "Avoid aggressive sales pressure"
  ]
}
```

---

## 12. Visual Identity

Visual Identity описывает, как проект должен выглядеть в generated content.

Поля MVP:

```text
visual_style_summary
colors
fonts
logo
image_style
motion_style
forbidden_visuals
safe_zones
```

Пример:

```json
{
  "visual_style_summary": "Clean, modern, warm and minimal.",
  "colors": {
    "background": "#F5F5F5",
    "surface": "#FFFFFF",
    "text": "#111111",
    "accent": "#AA8855"
  },
  "fonts": {
    "primary": "Inter",
    "secondary": "Georgia"
  },
  "motion_style": {
    "transitions": ["fade", "slow_zoom"],
    "avoid": ["fast_flashing", "hard_glitch"]
  }
}
```

---

## 13. CTA Library

CTA Library хранит доступные призывы к действию проекта.

Минимальные поля CTA:

```text
cta_id
label
intent
intensity
target
url
platforms
funnel_stage
status
```

Пример:

```json
{
  "cta_id": "cta_001",
  "label": "Learn more",
  "intent": "website_click",
  "intensity": "soft",
  "target": "website",
  "url": "https://example.com",
  "platforms": ["telegram", "vk", "instagram"],
  "funnel_stage": ["trust", "conversion"],
  "status": "active"
}
```

CTA должны быть project-scoped.

---

## 14. CTA intent

Рекомендуемые intent values:

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

Проект может использовать только часть из них.

---

## 15. CTA intensity

Рекомендуемые значения:

```text
none
soft
medium
direct
```

CTA intensity используется генераторами и QA.

Пример:

- attention content: none / soft;
- trust content: soft / medium;
- conversion content: medium / direct;
- retention content: soft / medium.

---

## 16. Links and UTM

Links and UTM отвечает за ссылки проекта.

Поля MVP:

```text
primary_url
landing_url
telegram_url
profile_urls
utm_defaults
utm_campaigns
```

Пример UTM:

```text
utm_source={platform}
utm_medium=organic
utm_campaign={project_slug}_{campaign}
utm_content={content_id}
```

Каждый export package должен иметь возможность получить готовую ссылку с UTM.

---

## 17. Platform Settings

Platform Settings описывает, какие каналы используются проектом.

Поддерживаемые значения:

```text
tiktok
instagram
youtube_shorts
telegram
vk
threads
pinterest
linkedin
x
facebook
blog
email
```

Для каждой платформы можно хранить:

```text
enabled
profile_url
default_content_types
caption_rules
hashtag_rules
cta_rules
posting_notes
```

---

## 18. Пример Platform Settings

```json
{
  "platforms": {
    "telegram": {
      "enabled": true,
      "profile_url": "",
      "default_content_types": ["text_social_post"],
      "caption_rules": "Longer reflective posts are allowed.",
      "hashtag_rules": "0-5 hashtags."
    },
    "instagram": {
      "enabled": true,
      "profile_url": "",
      "default_content_types": ["dialog_miniseries", "carousel"],
      "caption_rules": "Short caption with soft CTA."
    }
  }
}
```

---

## 19. Content Rules

Content Rules задают ограничения проекта.

Поля MVP:

```text
allowed_topics
forbidden_topics
claim_restrictions
legal_disclaimers
sensitive_topics
moderation_notes
```

Пример:

```json
{
  "forbidden_topics": ["topic_1", "topic_2"],
  "claim_restrictions": [
    "Do not promise guaranteed results",
    "Do not make medical claims"
  ],
  "legal_disclaimers": []
}
```

Content Rules должны использоваться в QA.

---

## 20. Export Settings

Export Settings описывает, как формировать output packages.

Поля MVP:

```text
default_export_path
file_naming_pattern
include_metadata
include_captions
include_cover
include_utm_links
```

Пример naming pattern:

```text
{project_slug}_{content_type}_{content_id}_{platform}
```

Пример package:

```text
exports/
  {project_slug}/
    {content_id}/
      video.mp4
      caption.txt
      metadata.json
```

---

## 21. Analytics Settings

Analytics Settings описывает, какие метрики важны проекту.

Поля MVP:

```text
primary_metrics
secondary_metrics
conversion_events
revenue_tracking_enabled
manual_metrics_enabled
csv_import_enabled
```

Пример:

```json
{
  "primary_metrics": ["views", "link_clicks", "purchases"],
  "secondary_metrics": ["likes", "comments", "saves", "shares"],
  "conversion_events": ["lead", "purchase"],
  "manual_metrics_enabled": true,
  "csv_import_enabled": true
}
```

---

## 22. Integrations

Integrations в MVP могут быть минимальными.

Возможные интеграции:

```text
file storage
video renderer
social platforms
analytics import
image generation tools
video generation tools
```

В MVP достаточно хранить placeholders и export-first подход.

Не нужно строить сложный интеграционный слой до готовности production loop.

---

## 23. Advanced

Advanced settings могут включать:

- custom metadata fields;
- default language fallback;
- timezone;
- archive policy;
- render defaults;
- experimental flags.

Для MVP Advanced можно не делать отдельным экраном.

---

## 24. Project Settings UI

Рекомендуемый UI:

```text
Tabs or sections:
  Basics
  Brand
  CTA
  Links
  Platforms
  Rules
  Export
  Analytics
```

Для MVP допустим один scrollable screen с секциями.

Важно: интерфейс должен показывать completeness.

---

## 25. Completeness Score

Project Settings может иметь completeness score.

Минимальные обязательные поля:

```text
project_name
project_slug
default_language
primary_url
audience_summary
tone_summary
visual_style_summary
target_platforms
```

Если часть полей отсутствует, Dashboard должен показывать warning.

---

## 26. Validation Rules

### 26.1. Basics

- project_name не пустой;
- project_slug уникальный;
- default_language указан;
- status корректный.

### 26.2. Links

- URL валиден;
- UTM template содержит допустимые placeholders;
- links не дублируются.

### 26.3. CTA

- cta_id уникальный внутри проекта;
- label не пустой;
- intent корректный;
- target корректный;
- active CTA не должен ссылаться на пустой URL, если target = website.

### 26.4. Platforms

- хотя бы одна платформа enabled;
- platform value из allowed list.

### 26.5. Brand Profile

- tone summary заполнен;
- visual summary заполнен;
- forbidden phrases могут быть пустыми, но поле должно существовать.

---

## 27. Project Settings API

Рекомендуемые endpoints MVP:

```text
GET /api/projects/:project_id/settings
PATCH /api/projects/:project_id/settings
GET /api/projects/:project_id/brand-profile
PATCH /api/projects/:project_id/brand-profile
GET /api/projects/:project_id/cta
POST /api/projects/:project_id/cta
PATCH /api/projects/:project_id/cta/:cta_id
DELETE /api/projects/:project_id/cta/:cta_id
```

Можно упростить до одного settings endpoint на раннем MVP.

---

## 28. Project Settings Data Model

Пример агрегированной структуры:

```json
{
  "project_id": "project_001",
  "basics": {},
  "brand_profile": {},
  "cta_library": [],
  "links": {},
  "platforms": {},
  "content_rules": {},
  "export_settings": {},
  "analytics_settings": {},
  "updated_at": ""
}
```

---

## 29. Use in Scenario Studio

Scenario Studio должен получать из Project Settings:

- audience;
- tone of voice;
- content rules;
- CTA library;
- target platforms;
- default language.

Без этих данных сценарии будут generic, а не project-specific.

---

## 30. Use in Visual Prompt Builder

Visual Prompt Builder должен получать:

- visual style summary;
- colors;
- image style;
- forbidden visuals;
- character rules, if any;
- motion style;
- platform aspect ratio.

---

## 31. Use in Production Engine

Production Engine должен получать:

- colors;
- fonts;
- logo;
- safe zones;
- CTA;
- export settings;
- platform output format;
- motion defaults.

Production Engine не должен иметь проектные стили, зашитые в код.

---

## 32. Use in Publishing Hub

Publishing Hub должен получать:

- platform settings;
- profile URLs;
- caption rules;
- hashtag rules;
- CTA rules;
- UTM defaults;
- schedule preferences.

---

## 33. Use in Analytics

Analytics должен получать:

- primary metrics;
- conversion events;
- revenue tracking settings;
- UTM rules;
- platform list.

Это позволяет сравнивать контент по meaningful metrics, а не только по просмотрам.

---

## 34. Use in QA

QA должен проверять:

- forbidden phrases;
- forbidden topics;
- claim restrictions;
- CTA validity;
- platform length rules;
- links and UTM;
- missing metadata;
- Brand Profile completeness.

---

## 35. Versioning

В будущем Project Settings должны поддерживать versioning.

Причина:

- Brand Profile может меняться;
- CTA могут меняться;
- визуальный стиль может меняться;
- analytics нужно понимать, с какими настройками был создан контент.

MVP может хранить только current settings, но metadata content item должен сохранять applied settings snapshot или version id.

---

## 36. Settings snapshot in metadata

Каждый content item желательно связывать с версией настроек.

Пример:

```json
{
  "content_id": "content_001",
  "project_id": "project_001",
  "brand_profile_version": "v1",
  "cta_id": "cta_001",
  "settings_snapshot_id": "settings_snapshot_001"
}
```

Для MVP можно начать с `brand_profile_version`.

---

## 37. Import / Export settings

В будущем полезно экспортировать проектные настройки.

Форматы:

```text
project_settings.json
brand_profile.json
cta_library.json
```

В MVP это необязательно, но структура должна быть JSON-friendly.

---

## 38. Security and secrets

Project Settings не должны хранить секреты в plain text.

Если появятся API keys или tokens:

- хранить отдельно;
- маскировать в UI;
- не попадать в export package;
- не попадать в prompts;
- не попадать в logs.

В MVP лучше вообще не хранить внешние API keys, если можно работать export-first.

---

## 39. MVP scope

В MVP входит:

- Basics;
- Brand Profile basic;
- Audience;
- Tone of Voice;
- Visual Identity basic;
- CTA Library basic;
- Links and UTM;
- Platform Settings basic;
- Content Rules basic;
- Export Settings basic;
- Analytics Settings basic;
- validation;
- completeness warning;
- Project Settings UI;
- Project Settings API or config storage.

---

## 40. Не входит в MVP

В MVP не входит:

- team settings;
- permissions;
- billing;
- project templates marketplace;
- complex integrations UI;
- API keys management;
- advanced versioning UI;
- brand audit;
- automatic style checking;
- multi-language localization management;
- client access mode.

---

## 41. Definition of Done

Project Settings считается готовым для MVP, если пользователь может:

```text
create project
→ define basic identity
→ fill audience
→ set tone
→ set visual style
→ add CTA
→ add primary URL
→ enable platforms
→ define content restrictions
→ save settings
→ use these settings in scenario generation, visual prompts, production and export
```

Без этого Content Plant превращается в generic генератор, а не мультипроектную систему.

---

## 42. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/02_platform_architecture/DATA_MODEL.md
docs/03_modules/SCENARIO_STUDIO_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/05_product_design/WEB_UI_SPEC.md
docs/05_product_design/DASHBOARD_SPEC.md
```

---

## 43. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 44. Следующие документы

После этого документа необходимо создать:

1. `docs/03_modules/SCENARIO_STUDIO_SPEC.md`
2. `docs/03_modules/ASSET_LIBRARY_SPEC.md`
3. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
4. `docs/02_platform_architecture/DATA_MODEL.md`
5. `docs/02_platform_architecture/PIPELINES_SPEC.md`

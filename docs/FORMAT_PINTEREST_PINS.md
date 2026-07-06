# Format: Pinterest Pins

## 1. Назначение документа

Этот документ описывает универсальный формат **Pinterest Pins** для платформы **Content Plant**.

Он фиксирует:

- что такое `pinterest_pin`;
- для каких задач используется формат;
- какие входные данные нужны;
- какие типы pin outputs поддерживаются;
- как формируются title, description, keywords и destination URL;
- какие визуальные требования нужны для вертикальных карточек;
- как формат связан с Brand Profile, Asset Library, Production Engine, Publishing Hub и Analytics;
- какие QA-проверки обязательны;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту, бренду или нише.

---

## 2. Краткое определение

**Pinterest Pin** — это вертикальная визуальная карточка или короткий media item, который упаковывает одну идею, тезис, quote, mini-guide, checklist или product/context bridge в evergreen-формат для Pinterest и похожих визуально-поисковых каналов.

Базовая формула:

```text
Idea / Scenario / Content Item / Analytics Insight
+ Brand Profile
+ Pin Template
+ Visual Asset / Background
+ Title
+ Description
+ Keywords
+ Destination URL
= Pinterest Pin Package
```

Формат должен помогать превращать уже созданные смыслы в долгоживущий контент, который может работать дольше, чем короткий ролик в ленте.

---

## 3. Главный принцип формата

`pinterest_pin` должен быть **evergreen-first**.

Это значит:

- pin должен быть понятен без контекста предыдущих публикаций;
- одна карточка должна передавать одну идею;
- title и description должны быть пригодны для поиска;
- визуал должен быть чистым, читаемым и consistent with Brand Profile;
- destination URL должен быть project-scoped и tracking-ready;
- формат не должен зависеть от конкретного бренда или продукта.

Неправильно:

```text
Hardcoded project product card
```

Правильно:

```text
Universal pin format
+ Project Brand Profile
+ Project links
+ Project CTA
= project-specific pin
```

---

## 4. Роль в content portfolio

Pinterest Pins нужны для:

- evergreen traffic;
- repurpose лучших идей;
- поискового хвоста;
- упаковки цитат и тезисов;
- mini-guides;
- сохранений;
- визуальной библиотеки проекта;
- мягкого перехода на сайт, блог, лендинг, продукт или подборку;
- повторного использования контента, который уже показал результат в других каналах.

Формат особенно полезен, когда контент может жить дольше 24–72 часов и не зависит от сиюминутного тренда.

---

## 5. Supported platforms

Основная платформа:

```text
pinterest
```

Потенциальное переиспользование:

```text
instagram
vk
blog
website
email
```

Для MVP `pinterest_pin` может быть export-ready пакетом без обязательного автопостинга.

---

## 6. Pin subtypes

Формат должен поддерживать несколько подтипов.

### 6.1. Quote Pin

Короткая мысль или цитата.

Структура:

```text
short text
+ subtle brand mark
+ destination URL metadata
```

Используется для:

- узнавания;
- сохранений;
- визуальной библиотеки;
- мягкого brand awareness.

---

### 6.2. Tip Pin

Один полезный совет.

Структура:

```text
problem / context
→ tip
→ soft next step
```

Используется для:

- practical content;
- educational snippets;
- expert positioning.

---

### 6.3. Mini Guide Pin

Мини-гайд на одной карточке.

Структура:

```text
title
→ 3–5 short points
→ closing / CTA
```

Используется для:

- saves;
- educational content;
- product-aware traffic.

---

### 6.4. Checklist Pin

Чеклист.

Структура:

```text
title
→ checklist items
→ destination / CTA
```

Используется для:

- high-save content;
- preparation tasks;
- comparison or decision support.

---

### 6.5. Carousel Repurpose Pin

Карточка, созданная из carousel или explainer content.

Структура:

```text
carousel key idea
→ condensed visual card
→ destination URL
```

Используется для:

- recycling strong carousel ideas;
- Pinterest traffic from existing social content.

---

### 6.6. Video Pin

Короткий вертикальный video pin.

Структура:

```text
background motion
+ short text sequence
+ title / description metadata
```

На MVP может быть should-have, если Production Engine уже поддерживает vertical video rendering.

---

## 7. Recommended output specs

### 7.1. Static pin MVP

Рекомендуемый размер:

```text
1000x1500 px
aspect ratio 2:3
format PNG or JPG
```

Допустимые размеры:

```text
1080x1620 px
1080x1920 px
1000x1500 px
```

MVP default:

```text
1000x1500 px
PNG
```

---

### 7.2. Video pin should-have

```text
aspect ratio: 9:16 or 2:3
resolution: 1080x1920 or 1000x1500 equivalent
format: MP4
duration: 6–15 seconds
```

Video Pin не обязателен для MVP, если static pin pipeline ещё не стабилен.

---

## 8. Required inputs

Минимальные входные данные:

```text
project_id
content_type = pinterest_pin
pin_subtype
title
main_text or points
Brand Profile
template_id
destination_url or destination_url_source
platform = pinterest
```

Желательные данные:

```text
source_type
source_id
topic
keywords
funnel_stage
cta_id
background_asset_id
visual_prompt
board_name
campaign_id
utm_campaign
```

---

## 9. Source types

`pinterest_pin` может создаваться из разных источников:

```text
idea
scenario
content_item
text_social_post
explainer_carousel
dialog_carousel
atmospheric_video
trend
analytics_insight
manual_note
```

Пример:

```json
{
  "source_type": "content_item",
  "source_id": "content_001",
  "project_id": "project_example",
  "content_type": "pinterest_pin"
}
```

---

## 10. Pinterest Pin entity

Минимальная структура:

```json
{
  "pin_id": "pin_001",
  "workspace_id": "workspace_001",
  "project_id": "project_example",
  "content_type": "pinterest_pin",
  "pin_subtype": "mini_guide_pin",
  "title": "Example Pin Title",
  "main_text": "",
  "points": [],
  "description": "",
  "keywords": [],
  "destination_url": "https://example.com",
  "cta_id": "cta_001",
  "template_id": "template_pin_2x3_v1",
  "background_asset_id": "asset_001",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

---

## 11. Required fields MVP

Для MVP обязательны:

```text
pin_id
project_id
content_type
pin_subtype
title
status
created_at
updated_at
```

Для production-ready pin также нужны:

```text
template_id
output_spec
destination_url or no_link mode
description
```

Если используется визуальный asset:

```text
background_asset_id
```

Если pin генерируется полностью шаблоном, background может быть template-controlled.

---

## 12. Pin statuses

Рекомендуемые статусы:

```text
draft
needs_review
approved
in_production
rendered
exported
scheduled
published
analyzed
rejected
archived
failed
```

### draft

Pin создан, но не готов к production.

### needs_review

Pin требует проверки текста, визуала или metadata.

### approved

Pin утверждён для production или export.

### in_production

Production Engine создаёт output file.

### rendered

Файл создан.

### exported

Export package готов.

### scheduled

Создана Publication со статусом scheduled.

### published

Pin опубликован.

### analyzed

По публикации есть metric snapshots.

---

## 13. Funnel stages

Формат поддерживает funnel stage:

```text
attention
trust
conversion
retention
```

### attention

Цель:

- привлечь внимание;
- получить сохранение;
- познакомить с темой.

Подтипы:

```text
quote_pin
tip_pin
```

### trust

Цель:

- объяснить подход;
- дать пользу;
- усилить доверие.

Подтипы:

```text
mini_guide_pin
checklist_pin
```

### conversion

Цель:

- привести к destination URL;
- объяснить следующий шаг;
- связать контент с оффером проекта.

Подтипы:

```text
mini_guide_pin
checklist_pin
product_bridge_pin
```

### retention

Цель:

- поддерживать контакт;
- возвращать пользователя к теме;
- усиливать повторное взаимодействие.

---

## 14. Title rules

Pin title должен быть:

- коротким;
- понятным без контекста;
- searchable;
- связанным с темой;
- readable on image;
- consistent with Brand Profile.

Рекомендации:

```text
30–80 characters
```

Избегать:

```text
clickbait without value
unclear abstract title
too many words
all-caps shouting
project-specific hardcode in template
```

---

## 15. Description rules

Description используется для публикации и поиска.

Рекомендуемая структура:

```text
1. Short context.
2. What the pin helps with.
3. Soft CTA or destination explanation.
4. Keywords naturally included.
```

Рекомендуемая длина MVP:

```text
150–500 characters
```

Description должен учитывать:

- Brand Profile tone;
- platform rules;
- CTA intensity;
- destination URL;
- keywords;
- forbidden phrases.

---

## 16. Keywords

Keywords помогают классифицировать и искать pins.

Keyword sources:

```text
Idea topic
Content Format
Project topics
Manual input
Trend Radar
Analytics insights
```

MVP keywords могут быть free text.

Будущее улучшение:

```text
controlled keyword taxonomy
keyword performance tracking
Pinterest trend integration
```

---

## 17. Destination URL

Pin может вести на project destination URL.

Источники URL:

```text
Project primary_url
CTA url
Campaign landing URL
Content-specific URL
Manual URL
```

Если URL используется, Publishing Hub должен сформировать UTM.

Базовый шаблон:

```text
utm_source=pinterest
utm_medium=organic
utm_campaign={project_slug}_{campaign}
utm_content={pin_id}
```

Пример нейтрального URL:

```text
https://example.com?utm_source=pinterest&utm_medium=organic&utm_campaign=example_project_evergreen&utm_content=pin_001
```

---

## 18. CTA rules

CTA optional.

CTA должен браться из Project CTA Library.

CTA может быть:

- visual CTA on pin;
- description CTA;
- destination URL only;
- no explicit CTA.

Рекомендуемые CTA intensity:

```text
attention: none / soft
trust: soft
conversion: soft / medium
retention: none / soft
```

Нельзя зашивать CTA в template.

---

## 19. Visual structure

Static pin должен иметь чистую визуальную иерархию.

Рекомендуемые зоны:

```text
top: title / hook
middle: main idea or visual
bottom: short CTA / subtle brand mark
```

Варианты layout:

```text
title_only
quote_card
image_plus_text
checklist
mini_guide
split_panel
```

Template должен определять layout, а Brand Profile — цвета, шрифты, logo, visual style.

---

## 20. Text density rules

Pin не должен превращаться в лист мелкого текста.

Рекомендации:

```text
Quote Pin: 1–2 short lines
Tip Pin: title + 1 tip
Mini Guide Pin: title + 3–5 short points
Checklist Pin: title + 3–6 checklist items
```

Если текста больше, лучше создать carousel или text post, а pin использовать как entry point.

---

## 21. Typography rules

Typography берётся из Brand Profile:

```text
primary font
secondary font
fallback font
font weights
text colors
accent colors
```

MVP требования:

- title readable on mobile;
- sufficient contrast;
- no tiny body text;
- safe margins;
- consistent hierarchy.

Если конкретный font недоступен, Production Engine использует fallback.

---

## 22. Visual assets

Pin может использовать:

```text
background image
illustration
photo
texture
brand pattern
template background
product image
icon
logo
```

Asset должен быть project-scoped.

Asset compatibility checks:

- asset belongs to project;
- type supported;
- file exists;
- aspect ratio compatible or crop allowed;
- status active/approved/linked;
- not archived/deleted/rejected.

---

## 23. Visual prompt rules

Если pin требует external visual generation, Scenario Studio или Visual Prompt Builder может создать prompt.

Prompt должен учитывать:

- pin subtype;
- title;
- main idea;
- Brand Profile visual style;
- forbidden visuals;
- aspect ratio;
- empty space for text;
- composition rules.

Prompt не должен содержать project-specific hardcode, если эти данные не пришли из active Brand Profile.

---

## 24. Template rules

Pin Template задаёт:

- output size;
- layout;
- text slots;
- image slots;
- logo slot;
- background behavior;
- typography slots;
- CTA slot;
- export rules.

Template не должен содержать:

```text
project name
project product name
project price
project URL
hardcoded CTA
hardcoded brand colors
hardcoded character
```

Правильно:

```text
Template slot: title
Template slot: background
Template slot: cta
Template reads Brand Profile
```

---

## 25. Output files

MVP static pin output:

```text
exports/
  {project_slug}/
    {content_id}/
      pin.png
      title.txt
      description.txt
      keywords.txt
      metadata.json
```

Optional:

```text
cover.png
source_prompt.txt
utm_url.txt
```

Video pin output:

```text
exports/
  {project_slug}/
    {content_id}/
      pin_video.mp4
      title.txt
      description.txt
      keywords.txt
      metadata.json
```

---

## 26. Metadata

`metadata.json` должен включать:

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "content_type": "pinterest_pin",
  "pin_subtype": "mini_guide_pin",
  "title": "Example Pin Title",
  "description": "",
  "keywords": [],
  "destination_url": "https://example.com",
  "utm_url": "",
  "template_id": "template_pin_2x3_v1",
  "asset_ids": [],
  "created_at": ""
}
```

---

## 27. Caption / publication package

Для Pinterest package должен включать:

```text
title
description
keywords / tags
destination URL
board suggestion
notes
```

Publication package может быть manual export-first:

```text
Download pin image
Copy title
Copy description
Copy destination URL
Publish manually
Paste published URL back to Content Plant
```

---

## 28. Production pipeline

Базовый pipeline:

```text
Idea / Scenario / Content Item
→ Generate Pin Draft
→ Select Pin Subtype
→ Generate Title / Description / Keywords
→ Select Template
→ Select or create visual asset
→ Render Pin
→ Output QA
→ Human Review
→ Export Package
→ Publishing Hub
```

MVP может поддерживать:

```text
manual create pin draft
select template
render static image
export package
manual publishing
manual metrics
```

---

## 29. Repurpose logic

Pinterest Pins хорошо работают как repurpose layer.

### From Text Social Post

```text
Text post key idea
→ quote / tip pin
```

### From Explainer Carousel

```text
Slide summary
→ mini guide pin
```

### From Dialog Carousel

```text
best dialogue line
→ quote pin
```

### From Atmospheric Video

```text
best text line
→ quote pin
```

### From Analytics

```text
high-performing topic
→ pin series
```

---

## 30. Batch production

`pinterest_pin` должен поддерживать batch production.

Примеры batch:

```text
Create 10 quote pins from approved text posts
Create 5 checklist pins from explainer topics
Create 20 pins from top-performing content items
```

Batch не должен обходить QA and Review.

MVP batch может быть ограничен:

```text
generate drafts
render static images
send to review
```

---

## 31. QA checks

MVP QA checks:

- project_id exists;
- content_type is `pinterest_pin`;
- title exists;
- description exists, if publishing package required;
- template exists;
- output size valid;
- image file exists after render;
- text readable;
- text does not overflow;
- Brand Profile exists;
- forbidden phrases absent;
- forbidden topics absent;
- CTA valid, if used;
- destination URL valid, if used;
- UTM generated, if URL used;
- metadata exists.

Blockers:

```text
missing project_id
missing template
missing output file
invalid destination URL when URL is required
missing metadata
asset belongs to another project
```

Warnings:

```text
title too long
description too short
text density too high
no keywords
no destination URL
low contrast
```

---

## 32. Review rules

Human Review должен проверить:

- смысл pin;
- читаемость;
- визуальное качество;
- соответствие Brand Profile;
- корректность title;
- корректность description;
- CTA;
- destination URL;
- нет ли визуального мусора;
- пригодность для публикации.

Review actions:

```text
Approve
Reject
Request changes
Edit title
Edit description
Replace asset
Rerender
Export
Schedule
```

MVP actions:

```text
Approve
Reject
Edit title
Edit description
Rerender
Export
```

---

## 33. Publishing rules

Publishing Hub должен поддерживать Pinterest publication record.

Publication fields:

```text
publication_id
project_id
content_id
platform = pinterest
board
status
scheduled_at
published_at
published_url
destination_url
utm_url
notes
```

MVP может быть manual:

```text
Export package
→ User publishes manually
→ User pastes published URL
→ User adds metrics later
```

Autoposting через API можно добавить позже.

---

## 34. Metrics

Для Pinterest полезны метрики:

```text
impressions
saves
outbound_clicks
pin_clicks
closeups
engagements
engagement_rate
profile_visits
conversions
revenue
```

MVP может использовать ручной ввод:

```text
impressions
saves
outbound_clicks
published_url
```

Metric Snapshot связывается с Publication.

---

## 35. Analytics usage

Analytics должен позволять анализировать:

- какие pin subtypes работают лучше;
- какие topics дают saves;
- какие keywords дают outbound clicks;
- какие templates дают лучший CTR;
- какие destination URLs конвертируют лучше;
- какие pins стоит масштабировать в series.

Пример recommendation:

```text
Mini guide pins with checklist structure have higher saves than quote pins. Create more pins from similar topics.
```

---

## 36. Platform adaptation

Pinterest-specific adaptation:

- title должен быть searchable;
- description должен содержать естественные keywords;
- image должен быть readable in feed;
- destination URL должен быть relevant;
- board suggestion полезен для manual publishing;
- UTM обязателен для tracking, если используется ссылка.

Для reuse в других каналах:

```text
Instagram: use as single image post or story
VK: use as image post with longer caption
Blog / website: use as visual card
Email: use as visual snippet
```

---

## 37. MVP scope

В MVP входит:

- создать pin draft вручную или из Idea / Content Item;
- выбрать subtype;
- сгенерировать title / description / keywords;
- выбрать template;
- использовать template background или uploaded asset;
- render static pin image;
- создать export package;
- human review;
- manual publishing support;
- manual metrics support.

В MVP не входит обязательно:

- Pinterest API autoposting;
- автоматический сбор всех Pinterest metrics;
- встроенная генерация изображений через API;
- сложная keyword research system;
- board optimization engine;
- массовая SEO-оптимизация через external APIs.

---

## 38. Acceptance criteria MVP

Формат считается реализованным, если:

1. Пользователь может создать `pinterest_pin` внутри активного Project.
2. Pin имеет `project_id` и не смешивается с другими проектами.
3. Можно выбрать subtype.
4. Можно задать title, description, keywords и destination URL.
5. Можно выбрать template.
6. Production Engine создаёт static image output.
7. Создаётся metadata.json.
8. QA проверяет основные ошибки.
9. Human Review может approve/reject pin.
10. Export Package содержит image, title, description, keywords и metadata.
11. Publishing Hub может создать Publication для platform = pinterest.
12. Метрики можно добавить вручную после публикации.

---

## 39. Anti-patterns

Запрещено:

- делать `pinterest_pin` только под один проект;
- hardcode project name, price, URL or CTA in template;
- использовать global assets без project separation;
- публиковать без review;
- хранить metrics внутри pin как source of truth;
- считать saves единственным показателем успеха;
- создавать перегруженные карточки с мелким текстом;
- смешивать pin draft и publication record.

---

## 40. Open questions

Вопросы для будущих итераций:

1. Нужно ли делать Pinterest API integration в MVP 2?
2. Нужен ли отдельный Board entity?
3. Нужна ли keyword taxonomy на уровне проекта?
4. Нужно ли поддерживать rich pins?
5. Нужно ли импортировать Pinterest analytics через CSV?
6. Нужно ли создавать pin series автоматически из top content?
7. Нужно ли делать A/B templates для pins?

---

## 41. Связанные документы

Этот документ связан с:

- `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
- `docs/02_platform_architecture/DATA_MODEL.md`
- `docs/02_platform_architecture/PIPELINES_SPEC.md`
- `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`
- `docs/03_modules/SCENARIO_STUDIO_SPEC.md`
- `docs/03_modules/ASSET_LIBRARY_SPEC.md`
- `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
- `docs/03_modules/QA_AND_REVIEW.md`
- `docs/03_modules/PUBLISHING_HUB_SPEC.md`
- `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`

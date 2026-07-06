# Trend Radar Spec

## 1. Назначение документа

Этот документ описывает модуль **Trend Radar** в платформе **Content Plant**.

Он фиксирует:

- зачем нужен Trend Radar;
- какие источники трендов поддерживаются;
- как тренды попадают в систему;
- как хранить trend references;
- как анализировать хук, тему, структуру и эмоциональный триггер;
- как превращать trend reference в Idea;
- как Trend Radar связан с Idea Bank, Scenario Studio, Analytics и Project Settings;
- какие ограничения входят в MVP;
- что не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Trend Radar

Trend Radar — это модуль рыночного наблюдения и отбора сигналов.

Он нужен, чтобы Content Plant не производил контент в вакууме, а опирался на:

- тренды;
- удачные hooks;
- повторяющиеся структуры;
- платформенные паттерны;
- темы, которые уже получают внимание;
- конкурирующие публикации;
- собственные лучшие материалы;
- ручные наблюдения пользователя.

Главная цепочка:

```text
External Signal / Internal Performance
→ Trend Reference
→ Trend Analysis
→ Adaptation Idea
→ Idea Bank
→ Scenario Studio
```

Trend Radar не должен быть просто списком ссылок.  
Он должен превращать наблюдения в производственные входные данные для контентного конвейера.

---

## 3. Основной принцип

Trend Radar должен быть **source-flexible** и **MVP-safe**.

Это значит:

- не строить MVP вокруг одного нестабильного API;
- поддерживать manual import;
- поддерживать CSV import;
- хранить источник и context;
- анализировать тренд через LLM или rule-based parsing;
- позволять пользователю подтверждать адаптацию;
- не использовать сомнительные scraping-подходы как обязательную часть MVP.

Правильный подход:

```text
Manual / CSV / API source
→ normalized Trend Reference
→ analysis
→ idea candidate
```

Неправильный подход:

```text
One fragile scraper
→ hidden dependency
→ broken pipeline
```

---

## 4. Место Trend Radar в платформе

Trend Radar находится до Idea Bank.

```text
Trend Radar
→ Idea Bank
→ Scenario Studio
→ Asset Library
→ Production Engine
→ Review
→ Publishing Hub
→ Analytics
```

Также Trend Radar получает обратную связь из Analytics:

```text
Published Content
→ Metrics
→ Analytics Insight
→ Trend Radar / Idea Bank
```

---

## 5. Основные задачи Trend Radar

Trend Radar должен позволять:

- добавить trend reference вручную;
- импортировать batch трендов из CSV;
- хранить ссылку, платформу и metadata;
- добавить заметки пользователя;
- сохранить screenshot или preview, если доступно;
- добавить transcript или caption;
- запустить trend analysis;
- выделить hook;
- определить topic;
- определить emotional trigger;
- определить content structure;
- определить visual pattern;
- определить CTA pattern;
- оценить adaptation potential;
- создать Idea из trend analysis;
- связать тренд с созданными сценариями и публикациями;
- показать, какие тренды уже использованы.

---

## 6. Что Trend Radar не должен делать в MVP

В MVP Trend Radar не должен требовать:

- полного автоматического сканирования всех соцсетей;
- обязательного API конкретной социальной платформы;
- обхода ограничений платформ;
- нестабильного scraping как core dependency;
- автоматического скачивания чужого контента без явной необходимости;
- сложного AI optimizer;
- автоматического копирования чужого формата без адаптации;
- публикации без human review.

Trend Radar помогает анализировать и адаптировать, а не клонировать контент.

---

## 7. Supported sources MVP

MVP sources:

```text
manual_link
manual_note
csv_import
own_publication
analytics_insight
```

### 7.1. manual_link

Пользователь вручную добавляет ссылку на публикацию.

### 7.2. manual_note

Пользователь добавляет наблюдение без ссылки.

### 7.3. csv_import

Пользователь импортирует таблицу трендов.

### 7.4. own_publication

Сигнал создаётся из собственного опубликованного контента.

### 7.5. analytics_insight

Сигнал создаётся из аналитического вывода.

---

## 8. Future sources

Future sources:

```text
youtube_api
pinterest_api
social_platform_api
approved_scraper
browser_extension
rss_feed
competitor_monitoring
trend_report_import
```

Эти источники не должны блокировать MVP.

---

## 9. Trend Reference entity

Trend Reference — это нормализованная запись о внешнем или внутреннем сигнале.

Минимальная структура:

```json
{
  "trend_id": "trend_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "source_type": "manual_link",
  "source_platform": "short_video_platform",
  "source_url": "https://example.com/trend",
  "title": "Example trend title",
  "caption": "",
  "transcript": "",
  "user_notes": "",
  "status": "new",
  "created_at": "",
  "updated_at": ""
}
```

---

## 10. Обязательные поля MVP

Для MVP обязательны:

```text
trend_id
project_id
source_type
source_platform
status
created_at
updated_at
```

Желательные поля:

```text
source_url
title
caption
transcript
user_notes
metrics_snapshot
screenshot_asset_id
analysis_id
idea_id
```

---

## 11. Project scope

Trend Reference должен быть project-scoped.

Правило:

```text
trend.project_id must exist
```

Даже если тренд кажется универсальным, его анализ и адаптация выполняются под конкретный Project и Brand Profile.

Если один и тот же trend reference нужен для нескольких проектов, MVP может создать отдельные project-scoped copies.

---

## 12. Source platform values

Рекомендуемые значения:

```text
short_video_platform
photo_social_platform
video_platform
visual_search_platform
messaging_channel
community_platform
website
manual
other
```

MVP может поддерживать любое значение как text field, но для фильтров лучше использовать controlled list.

---

## 13. Trend statuses

Рекомендуемые статусы:

```text
new
needs_context
ready_for_analysis
analyzing
analyzed
idea_created
dismissed
archived
failed
```

### 13.1. new

Trend reference добавлен, но ещё не обработан.

### 13.2. needs_context

Не хватает caption, transcript, notes или platform data.

### 13.3. ready_for_analysis

Данных достаточно для анализа.

### 13.4. analyzing

Идёт анализ.

### 13.5. analyzed

Trend analysis создан.

### 13.6. idea_created

На основе тренда создана Idea.

### 13.7. dismissed

Пользователь решил не использовать тренд.

### 13.8. archived

Trend reference скрыт из активной работы.

### 13.9. failed

Ошибка импорта или анализа.

---

## 14. Trend metrics snapshot

Для внешнего тренда можно хранить наблюдаемые метрики.

```json
{
  "views": 100000,
  "likes": 12000,
  "comments": 800,
  "shares": 300,
  "saves": 0,
  "collected_at": ""
}
```

Важно:

- внешние метрики могут быть неполными;
- внешние метрики могут быть вручную введены пользователем;
- точность не гарантируется;
- Trend Radar должен хранить source and timestamp.

---

## 15. CSV import

CSV import должен позволять массово загрузить trend references.

Минимальные колонки:

```text
source_platform
source_url
title
caption
transcript
views
likes
comments
shares
user_notes
```

Допустимо импортировать частично заполненные строки.

Если не хватает данных, status может быть:

```text
needs_context
```

---

## 16. CSV import flow

```text
1. User opens Trend Radar.
2. Clicks Import CSV.
3. Uploads CSV file.
4. System maps columns.
5. System validates rows.
6. System creates Trend References.
7. Invalid rows are reported.
8. User reviews imported trends.
9. User selects trends for analysis.
```

---

## 17. Manual link flow

```text
1. User opens Trend Radar.
2. Clicks Add Trend.
3. Pastes URL.
4. Selects or confirms platform.
5. Adds notes, caption or transcript if needed.
6. Saves trend reference.
7. System marks trend as new or ready_for_analysis.
```

MVP may not fetch platform metadata automatically.

---

## 18. Manual note flow

```text
1. User adds a note.
2. Selects source_platform = manual.
3. Adds topic, hook, observation or screenshot.
4. Saves.
5. Trend Radar can analyze it like any other signal.
```

This is useful when the user saw a pattern but does not have a stable URL.

---

## 19. Trend Analysis entity

Trend Analysis — это результат анализа trend reference.

```json
{
  "analysis_id": "trend_analysis_001",
  "trend_id": "trend_001",
  "project_id": "project_001",
  "hook": "",
  "topic": "",
  "emotional_trigger": "",
  "content_structure": "",
  "visual_pattern": "",
  "cta_pattern": "",
  "platform_pattern": "",
  "adaptation_notes": "",
  "adaptation_potential": "medium",
  "recommended_content_types": ["dialog_miniseries", "text_social_post"],
  "risk_notes": [],
  "created_at": ""
}
```

---

## 20. Analysis dimensions

Trend Radar должен анализировать следующие измерения.

### 20.1. Hook

Что останавливает внимание.

Примеры типов:

```text
question
confession
contrarian_statement
promise
pattern_recognition
pain_mirror
curiosity_gap
```

### 20.2. Topic

О чём публикация.

Topic должен быть project-scoped или выбираемым из topic taxonomy.

### 20.3. Emotional trigger

Какая эмоция запускает внимание.

Примеры:

```text
recognition
curiosity
relief
fear
hope
anger
surprise
belonging
desire
```

### 20.4. Content structure

Как устроен материал.

Примеры:

```text
pain_to_reframe
problem_solution
before_after
myth_truth
list
dialogue
story_turn
question_answer
```

### 20.5. Visual pattern

Как визуально сделан материал.

Примеры:

```text
talking_head
text_on_background
carousel_explainer
screen_recording
dialog_scene
aesthetic_broll
meme_format
```

### 20.6. CTA pattern

Какой следующий шаг предлагается.

Примеры:

```text
no_cta
comment_prompt
profile_visit
link_in_profile
direct_link
save_for_later
follow_for_more
```

### 20.7. Adaptation potential

Насколько тренд подходит активному проекту.

Values:

```text
low
medium
high
unknown
```

---

## 21. Brand Profile usage

Trend Radar должен загружать Brand Profile выбранного Project при анализе.

Brand Profile используется для:

- оценки соответствия теме;
- выявления forbidden topics;
- выбора tone adaptation;
- выбора recommended content types;
- выбора CTA boundaries;
- формирования adaptation notes.

Trend Radar не должен выдавать идею, которая нарушает Content Rules проекта.

---

## 22. Recommended content types

Trend Analysis может рекомендовать один или несколько content types:

```text
dialog_miniseries
atmospheric_video
dialog_carousel
explainer_carousel
text_social_post
pinterest_pin
```

Рекомендация должна быть объяснима:

```text
This trend works as a dialogue because it contains a clear tension between two points of view.
```

---

## 23. Trend to Idea flow

```text
1. User opens analyzed trend.
2. Reviews hook, topic, emotional trigger and adaptation notes.
3. Selects recommended content type or chooses another.
4. Clicks Create Idea.
5. System creates Idea with source_type = trend.
6. Idea stores trend_id as source_id.
7. Idea appears in Idea Bank.
```

Created Idea should include:

```text
project_id
source_type = trend
source_id = trend_id
title
description
topic
funnel_stage
suggested_content_type
priority
status
```

Default Idea status:

```text
raw
```

or

```text
approved
```

depending on Project Settings.

---

## 24. Trend to Scenario shortcut

MVP should prefer:

```text
Trend → Idea → Scenario
```

Future may allow:

```text
Trend → Scenario
```

But the Idea step is useful because it keeps the pipeline auditable.

---

## 25. Trend Radar UI

MVP UI sections:

```text
Trend List
Add Trend
CSV Import
Trend Detail
Analysis Panel
Create Idea action
```

---

## 26. Trend List

Trend List should show:

- title;
- source platform;
- status;
- hook;
- topic;
- adaptation potential;
- recommended content types;
- created_at;
- linked idea;
- actions.

Filters:

```text
source_platform
status
topic
adaptation_potential
recommended_content_type
date
```

---

## 27. Trend Detail

Trend Detail should show:

```text
Source URL
Platform
Caption
Transcript
User notes
Metrics snapshot
Screenshot / preview
Analysis
Linked Ideas
Linked Scenarios
Linked Content Items
```

Actions:

```text
Edit
Analyze
Create Idea
Dismiss
Archive
```

---

## 28. Analysis Panel

Analysis Panel should show:

```text
Hook
Topic
Emotional trigger
Content structure
Visual pattern
CTA pattern
Adaptation notes
Recommended content types
Risks
```

If Brand Profile is incomplete, show warning:

```text
Brand Profile is incomplete. Trend adaptation may be generic.
```

---

## 29. Trend QA

Trend Radar should perform basic checks.

MVP checks:

- project_id exists;
- source_type valid;
- source_platform exists;
- at least one of URL, caption, transcript or notes exists;
- forbidden topic warning;
- duplicate URL warning;
- incomplete analysis warning;
- unsupported platform warning.

---

## 30. Duplicate detection

Trend Radar should warn if the same URL already exists in the same project.

MVP rule:

```text
project_id + source_url must be unique when source_url exists
```

Manual notes may duplicate because they can represent different observations.

---

## 31. Integration with Idea Bank

Idea Bank receives ideas from Trend Radar.

Trend-created Idea should store:

```text
source_type = trend
source_id = trend_id
```

This allows Analytics to later answer:

```text
Which trend sources created successful content?
```

---

## 32. Integration with Scenario Studio

Scenario Studio may use Trend Analysis as input.

Useful fields:

- hook;
- topic;
- emotional_trigger;
- content_structure;
- visual_pattern;
- adaptation_notes;
- recommended_content_types.

Scenario Studio should not copy the trend.  
It should create project-specific adaptation.

---

## 33. Integration with Asset Library

Trend Radar may store screenshots or reference files as assets.

If stored, they should use:

```text
asset.type = document or image
asset.source_type = trend_reference
asset.source_id = trend_id
```

Reference assets should not be confused with production-ready assets.

---

## 34. Integration with Analytics

Analytics can create internal signals for Trend Radar.

Examples:

```text
A topic is rising in project performance.
A hook pattern repeatedly performs well.
A content type has high conversion rate.
A platform shows increasing saves.
```

This allows internal trends, not only external trends.

---

## 35. Integration with Publishing Hub

Publishing Hub is not directly controlled by Trend Radar.

But trend lineage should be preserved:

```text
Trend → Idea → Scenario → Content Item → Publication → Metric Snapshot
```

This makes it possible to compare trend-inspired content against manually created content.

---

## 36. LLM analysis prompt requirements

Trend analysis prompt should include:

```text
Project context
Brand Profile summary
Content Rules
Trend caption / transcript / notes
Observed metrics
Requested output schema
```

Prompt must ask for structured output.

The LLM must not be treated as source of truth for platform metrics.  
It only analyzes provided context.

---

## 37. LLM output schema

Recommended structured output:

```json
{
  "hook": "",
  "topic": "",
  "emotional_trigger": "",
  "content_structure": "",
  "visual_pattern": "",
  "cta_pattern": "",
  "adaptation_potential": "medium",
  "recommended_content_types": [],
  "adaptation_notes": "",
  "risk_notes": []
}
```

If confidence is low, output should include:

```text
adaptation_potential = unknown
```

and a clear reason.

---

## 38. Trend scoring MVP

MVP can use simple scoring.

Suggested fields:

```text
attention_score
fit_score
production_effort_score
risk_score
priority_score
```

The score should be explainable and editable.

Example:

```text
priority_score = attention_score + fit_score - production_effort_score - risk_score
```

This formula can change later.

---

## 39. Trend tags

Tags can include:

```text
hook_type
topic
emotion
visual_pattern
platform
format
funnel_stage
campaign
```

MVP tags can be free text.

---

## 40. Trend lifecycle

Recommended lifecycle:

```text
new
→ ready_for_analysis
→ analyzing
→ analyzed
→ idea_created
→ archived
```

Alternative ending:

```text
analyzed
→ dismissed
```

Failure path:

```text
analyzing
→ failed
→ ready_for_analysis
```

---

## 41. Permissions

MVP does not need complex permissions.

Future SaaS roles may include:

- owner;
- strategist;
- editor;
- analyst;
- viewer.

Do not implement role complexity in MVP.

---

## 42. API principles

Trend Radar APIs should be project-scoped.

Examples:

```text
GET /api/projects/:project_id/trends
POST /api/projects/:project_id/trends
GET /api/projects/:project_id/trends/:trend_id
POST /api/projects/:project_id/trends/:trend_id/analyze
POST /api/projects/:project_id/trends/:trend_id/create-idea
POST /api/projects/:project_id/trends/import-csv
```

Avoid global trend endpoints in MVP unless explicitly filtered by project.

---

## 43. MVP scope

Trend Radar MVP includes:

- manual trend creation;
- manual link input;
- manual note input;
- CSV import;
- trend list;
- trend detail;
- LLM-based analysis from provided text;
- structured Trend Analysis;
- create Idea from analyzed trend;
- duplicate URL warning;
- project-scoped storage;
- basic status lifecycle.

---

## 44. Not in MVP

Not in MVP:

- full automatic social listening;
- mandatory social platform API;
- large-scale scraping;
- automated downloading of external videos;
- automatic competitor monitoring;
- auto-publishing based on trend;
- autonomous content strategy changes;
- complex ML scoring;
- external SaaS user permissions.

---

## 45. Acceptance criteria

Trend Radar MVP is ready when:

1. User can create a trend manually.
2. User can import trends from CSV.
3. Trend references are project-scoped.
4. Trend list supports basic filters.
5. User can open Trend Detail.
6. User can add caption, transcript or notes.
7. User can run analysis.
8. Analysis returns hook, topic, emotional trigger, structure, visual pattern, CTA pattern and adaptation notes.
9. User can create Idea from analyzed trend.
10. Created Idea links back to trend_id.
11. Duplicate URL warning works inside a project.
12. No project-specific rules are hardcoded in Trend Radar.
13. The module works without external social APIs.

---

## 46. Anti-patterns

Avoid:

- using Trend Radar as a hidden scraper;
- treating external metrics as exact truth without source/timestamp;
- copying competitor content without adaptation;
- creating scenarios directly without preserving lineage;
- hardcoding one platform as required;
- hardcoding one brand, product, CTA or audience;
- blocking MVP because platform APIs are unavailable;
- allowing trend-inspired content to skip Review.

---

## 47. Open questions

Open questions for later:

1. Should Trend Radar support browser extension capture?
2. Should screenshots be stored automatically or manually uploaded?
3. Should trend scoring be rule-based or LLM-assisted?
4. Should one trend be shareable across multiple projects?
5. Should the system support competitor profiles?
6. Should platform APIs be prioritized by value or by technical simplicity?
7. Should Trend Radar store original media files or only references and metadata?
8. How should legal/compliance rules differ by platform and country?

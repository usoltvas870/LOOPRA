# Idea Bank Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает модуль **Idea Bank** в платформе **Content Plant**.

Он фиксирует:

- зачем нужен Idea Bank;
- какие идеи хранит платформа;
- как идеи связаны с Project, Brand Profile, Trend Radar, Scenario Studio, Production, Publishing и Analytics;
- какие поля, статусы и действия нужны для MVP;
- как идеи превращаются в сценарии и production tasks;
- как сохранять source linkage и performance feedback;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Idea Bank

Idea Bank — это управляемый запас смыслов, тем и гипотез для производства контента.

Он нужен, чтобы Content Plant не работал как одноразовый генератор, а накапливал и развивал контентные идеи.

Базовая цепочка:

```text
Trend / User Note / Analytics Insight / Content Strategy
→ Idea
→ Scenario
→ Production
→ Publication
→ Metrics
→ Idea Feedback
```

Idea Bank отвечает за первый рабочий слой content pipeline: что именно стоит превратить в контент.

---

## 3. Основной принцип

Idea Bank должен быть **project-scoped** и **pipeline-aware**.

Это значит:

```text
Every idea belongs to a Project.
Every idea has status.
Every idea has next action.
Every idea can be traced back to source.
Every idea can be linked to produced content and metrics.
```

Неправильно:

```text
Global list of random notes without project_id, source, status or next action.
```

Правильно:

```text
Project-specific idea with topic, source, funnel stage, suggested format, status and links to scenarios/content.
```

---

## 4. Место в pipeline

Idea Bank находится после источников идей и перед Scenario Studio.

```text
Trend Radar
Manual Notes
Content Strategy
Analytics Insights
Past Content
→ Idea Bank
→ Scenario Studio
→ Asset Library
→ Production Engine
→ QA / Review
→ Publishing Hub
→ Analytics
```

Idea Bank не должен сам рендерить контент. Его задача — хранить, сортировать, приоритизировать и передавать идеи в Scenario Studio.

---

## 5. Источники идей

Idea может быть создана из разных источников:

```text
manual
trend
analytics_insight
content_strategy
past_content
campaign
import
agent_suggestion
```

### 5.1. manual

Пользователь вручную добавляет идею.

### 5.2. trend

Идея создана из Trend Radar: ссылка, CSV-строка, трендовая карточка или рыночный паттерн.

### 5.3. analytics_insight

Идея создана из результатов прошлых публикаций.

Пример:

```text
Posts about comparison topics have high save rate. Create more comparison content.
```

### 5.4. content_strategy

Идея создана из project content strategy или planned content pillars.

### 5.5. past_content

Идея создана как variation, repurpose или scale candidate на основе существующего Content Item.

### 5.6. campaign

Идея принадлежит конкретной кампании.

### 5.7. import

Идея импортирована из CSV, markdown, spreadsheet или внешнего planning document.

### 5.8. agent_suggestion

Идея предложена агентом на основе текущих данных проекта.

---

## 6. Основные задачи Idea Bank

Idea Bank должен позволять:

- создать идею вручную;
- импортировать идеи;
- сохранить source linkage;
- присвоить project_id;
- задать тему, funnel stage и suggested content type;
- присвоить приоритет;
- утвердить или отклонить идею;
- отправить идею в Scenario Studio;
- видеть связанные сценарии;
- видеть связанные Content Items;
- видеть publication / metrics summary;
- создавать variations;
- масштабировать успешные идеи;
- архивировать устаревшие идеи.

---

## 7. Idea entity

Минимальная структура:

```json
{
  "idea_id": "idea_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "title": "Example idea title",
  "description": "Short explanation of the idea.",
  "topic": "example_topic",
  "funnel_stage": "attention",
  "suggested_content_type": "dialog_miniseries",
  "source_type": "manual",
  "source_id": "",
  "priority": "medium",
  "status": "raw",
  "tags": [],
  "created_at": "",
  "updated_at": ""
}
```

---

## 8. Обязательные поля MVP

Для MVP обязательны:

```text
idea_id
project_id
title
description
funnel_stage
suggested_content_type
status
source_type
created_at
updated_at
```

Желательные поля:

```text
workspace_id
topic
priority
tags
source_id
campaign_id
owner_notes
score
```

---

## 9. Idea statuses

Рекомендуемые статусы:

```text
raw
approved
rejected
scripted
needs_assets
in_production
ready
scheduled
published
analyzed
scale_candidate
archived
```

### 9.1. raw

Идея создана, но ещё не утверждена.

### 9.2. approved

Идея готова к генерации сценария.

### 9.3. rejected

Идея отклонена и не должна идти дальше по pipeline.

### 9.4. scripted

По идее создан минимум один Scenario.

### 9.5. needs_assets

Связанный Scenario требует визуальные или аудио ассеты.

### 9.6. in_production

Связанный Scenario или Content Item находится в production.

### 9.7. ready

По идее есть approved / ready content, который можно экспортировать или планировать.

### 9.8. scheduled

Один или несколько связанных content items запланированы к публикации.

### 9.9. published

Связанный content опубликован минимум на одной платформе.

### 9.10. analyzed

По опубликованному контенту есть метрики или performance summary.

### 9.11. scale_candidate

Идея показала хороший результат и может быть расширена, повторена или repurposed.

### 9.12. archived

Идея скрыта из активной работы, но сохранена в истории.

---

## 10. Funnel stage

Idea должна поддерживать stage воронки:

```text
attention
trust
conversion
retention
```

### attention

Идея направлена на охват, узнавание и первичное внимание.

### trust

Идея объясняет подход, укрепляет доверие или раскрывает ценность.

### conversion

Идея ведёт к конкретному действию, офферу, заявке, покупке или регистрации.

### retention

Идея поддерживает текущую аудиторию, возвращает к продукту или усиливает привычку.

---

## 11. Suggested content type

Idea может иметь recommended format:

```text
dialog_miniseries
atmospheric_video
dialog_carousel
explainer_carousel
text_social_post
pinterest_pin
```

Для MVP must-have:

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

Если suggested content type не выбран, Scenario Studio может предложить вариант на основе темы, funnel stage и Project Settings.

---

## 12. Topic and tags

Topic — основная смысловая категория идеи.

Tags — дополнительные признаки.

Примеры tag categories:

```text
emotion
pain
objection
format
platform
campaign
audience_segment
product_area
content_pillar
```

В MVP tags могут быть free text.

В будущем можно добавить controlled taxonomy.

---

## 13. Priority

Рекомендуемые значения:

```text
low
medium
high
urgent
```

Priority может задаваться вручную или рассчитываться по score.

Пример факторов:

- trend relevance;
- funnel gap;
- campaign priority;
- past performance of similar ideas;
- production effort;
- platform fit.

MVP может использовать ручной priority.

---

## 14. Idea score

Idea score — необязательная оценка перспективности.

Пример структуры:

```json
{
  "score": 78,
  "score_factors": {
    "trend_fit": 80,
    "brand_fit": 90,
    "production_effort": 60,
    "conversion_potential": 70
  }
}
```

Для MVP score может быть отложен.

Если score используется, он не должен автоматически заменять человеческое решение.

---

## 15. Source linkage

Idea должна хранить связь с источником.

Пример для trend:

```json
{
  "source_type": "trend",
  "source_id": "trend_001"
}
```

Пример для analytics insight:

```json
{
  "source_type": "analytics_insight",
  "source_id": "insight_001"
}
```

Пример для past content:

```json
{
  "source_type": "past_content",
  "source_id": "content_001"
}
```

Зачем это нужно:

- понимать происхождение идеи;
- сравнивать источники идей;
- улучшать Trend Radar;
- строить analytics loop;
- видеть, какие тренды превращаются в результат.

---

## 16. Связь с Project

Каждая идея должна принадлежать проекту.

```text
idea.project_id must exist
```

Idea Bank должен по умолчанию показывать идеи активного Project.

Нельзя смешивать идеи разных проектов без явного Workspace-level view.

---

## 17. Связь с Brand Profile

Idea не обязана хранить Brand Profile snapshot, но Scenario Studio при генерации сценария должна загружать актуальный Brand Profile проекта.

Важно:

```text
Idea = raw or structured content hypothesis.
Brand Profile = rules for turning idea into project-specific content.
```

Если Brand Profile неполный, Idea Bank может показывать warning:

```text
Project Brand Profile is incomplete. Generated scenarios may be inconsistent.
```

---

## 18. Связь со Scenario Studio

Главное действие Idea Bank:

```text
Generate Scenario
```

Flow:

```text
Idea approved
→ user clicks Generate Scenario
→ Scenario Studio loads Idea
→ Scenario Studio loads Brand Profile
→ Scenario Studio loads Content Format Spec
→ Scenario draft is created
→ Idea status becomes scripted
```

Одна Idea может породить несколько Scenarios.

Пример:

```text
Idea
→ dialog_miniseries scenario
→ text_social_post scenario
→ carousel scenario
```

---

## 19. Idea to Scenario relation

Связь:

```text
Idea 1 → Scenario many
```

Scenario должен хранить:

```text
idea_id
project_id
content_type
```

Idea Detail должен показывать связанные scenarios.

Минимальный related scenarios item:

```json
{
  "scenario_id": "scenario_001",
  "content_type": "dialog_miniseries",
  "status": "ready_to_render",
  "created_at": ""
}
```

---

## 20. Связь с Content Items

Через Scenario идея должна быть связана с produced content.

Связь:

```text
Idea
→ Scenario
→ Render Job
→ Content Item
```

Idea Detail может показывать:

- generated content count;
- approved content count;
- published content count;
- best performing publication;
- latest metrics snapshot.

---

## 21. Связь с Publications

Idea не публикуется напрямую.

Публикуются Content Items, которые произошли из идеи.

Для summary Idea Bank может показывать publication state:

```text
not_published
scheduled
partially_published
published
```

Это derived state, а не отдельный source of truth.

Source of truth:

```text
Publication records in Publishing Hub
```

---

## 22. Связь с Metrics

Idea может получать aggregated metrics через связанные Publications.

Пример derived summary:

```json
{
  "idea_id": "idea_001",
  "published_count": 3,
  "total_views": 42000,
  "total_clicks": 230,
  "total_conversions": 12,
  "total_revenue": 0,
  "best_platform": "instagram",
  "best_content_type": "dialog_miniseries"
}
```

Idea Bank не должен хранить manual metrics как источник истины. Метрики живут в Metric Snapshot.

---

## 23. Idea lifecycle

Canonical lifecycle:

```text
raw
→ approved
→ scripted
→ needs_assets
→ in_production
→ ready
→ scheduled
→ published
→ analyzed
→ scale_candidate / archived
```

Не каждая идея обязана пройти все статусы.

Например text-only idea может идти так:

```text
raw
→ approved
→ scripted
→ ready
→ scheduled
→ published
→ analyzed
```

Rejected path:

```text
raw
→ rejected
→ archived
```

---

## 24. Status ownership

Idea status может обновляться разными модулями, но ownership должен быть понятным.

| Status change | Owner |
|---|---|
| raw → approved | User / Idea Bank |
| raw → rejected | User / Idea Bank |
| approved → scripted | Scenario Studio |
| scripted → needs_assets | Scenario Studio / Asset Slots |
| needs_assets → in_production | Production Engine |
| in_production → ready | Production / Review / Export state |
| ready → scheduled | Publishing Hub |
| scheduled → published | Publishing Hub |
| published → analyzed | Analytics |
| analyzed → scale_candidate | Analytics / User |
| any → archived | User |

Idea status can also be derived from linked entities. If there is conflict, linked entity source of truth wins.

---

## 25. Idea list UI

Idea Bank list должен показывать:

- title;
- topic;
- funnel stage;
- suggested content type;
- source type;
- priority;
- status;
- linked scenarios count;
- linked content count;
- latest performance summary, if available;
- created_at;
- next action.

MVP fields:

```text
title
funnel_stage
suggested_content_type
source_type
status
created_at
next_action
```

---

## 26. Filters

Idea Bank должен поддерживать фильтры:

```text
status
funnel_stage
content_type
source_type
topic
tag
priority
date range
campaign
```

MVP filters:

```text
status
funnel_stage
content_type
source_type
```

---

## 27. Search

MVP search:

```text
search by title
search by description
```

Should-have:

```text
search by topic
tag
source note
linked scenario title
```

Future:

```text
semantic search
similar ideas
duplicate detection
```

---

## 28. Idea Detail screen

Idea Detail должен показывать:

```text
Idea metadata
Description
Source
Topic / tags
Funnel stage
Suggested content type
Priority
Status
Owner notes
Related scenarios
Related content items
Publication summary
Metrics summary
Actions
```

MVP actions:

```text
Edit
Approve
Reject
Generate Scenario
Duplicate
Archive
```

Should-have actions:

```text
Create variation
Generate text posts
Generate carousel scenario
Mark as scale candidate
```

---

## 29. Quick create flow

Flow:

```text
1. User opens Idea Bank.
2. Clicks New Idea.
3. Enters title.
4. Adds description.
5. Selects funnel stage.
6. Selects suggested content type, optional.
7. Adds topic/tags, optional.
8. Saves idea.
9. Idea appears as raw or approved depending on setting.
```

MVP can default new idea status to:

```text
raw
```

Project Settings may later allow default status:

```text
raw or approved
```

---

## 30. Manual idea import

MVP should allow simple import from CSV or pasted text later, but it is not required for the first vertical slice.

Recommended CSV fields:

```text
title
description
topic
funnel_stage
suggested_content_type
source_type
tags
priority
```

Imported ideas default to:

```text
raw
```

Import should validate:

- project_id exists;
- title exists;
- funnel_stage valid, if provided;
- content_type valid, if provided;
- status valid, if provided.

---

## 31. Trend to Idea flow

Trend Radar can create Idea.

Flow:

```text
1. User adds or imports trend.
2. Trend Radar analyzes hook, topic, structure and trigger.
3. User clicks Create Idea.
4. Idea Bank receives title, description, topic, suggested format and source link.
5. Idea status = raw or approved.
6. User can generate scenario.
```

Minimum fields from trend:

```text
source_type = trend
source_id
title
description
topic
suggested_content_type
funnel_stage
```

---

## 32. Analytics to Idea flow

Analytics can suggest new ideas based on performance.

Flow:

```text
1. Analytics identifies strong or weak pattern.
2. System creates recommendation.
3. User accepts recommendation as Idea.
4. Idea source_type = analytics_insight.
5. Idea can become variation, scale candidate or new topic.
```

MVP may not automate this fully.

MVP minimum:

```text
User can manually create idea from analytics observation.
```

---

## 33. Repurpose idea flow

A successful Content Item can create new ideas.

Examples:

```text
video → text_social_post
video → carousel
text post → atmospheric_video
best hook → new dialog_miniseries variation
```

Flow:

```text
1. User opens Content Item or Analytics result.
2. Clicks Create Repurpose Idea.
3. Selects target content type.
4. Idea is created with source_type = past_content.
5. Scenario Studio generates target format.
```

---

## 34. Variations

Idea variations are useful for testing hooks, angles, platforms and funnel stages.

Variation relation:

```text
parent_idea_id
variation_type
```

Variation types:

```text
hook
angle
platform
format
funnel_stage
audience_segment
cta_intensity
```

MVP can support simple duplicate:

```text
Duplicate idea → edit fields manually
```

---

## 35. Duplicate detection

Duplicate detection is not required for MVP.

Should-have:

- same title warning;
- similar topic warning;
- same trend source warning.

Future:

- semantic similarity;
- cluster ideas by topic;
- merge duplicates.

---

## 36. Idea QA

Idea QA should be light.

MVP checks:

- project_id exists;
- title not empty;
- funnel_stage valid;
- suggested content type valid, if present;
- source_type valid;
- status valid.

Should-have checks:

- description too vague;
- duplicate title;
- missing topic;
- missing next action;
- conflicts with project content rules.

Idea QA should usually produce warnings, not blockers, except for missing project_id or title.

---

## 37. Next action logic

Idea Bank should show next action based on status.

Examples:

| Status | Next action |
|---|---|
| raw | Approve or reject |
| approved | Generate scenario |
| scripted | Open scenario |
| needs_assets | Upload or link assets |
| in_production | Open render job |
| ready | Review / export / schedule |
| scheduled | Open publication |
| published | Add metrics |
| analyzed | Create variation / scale / archive |
| scale_candidate | Create variations |

Next action should link to the relevant module.

---

## 38. Dashboard integration

Dashboard should aggregate Idea Bank state.

Useful counters:

```text
raw ideas
approved ideas waiting for scenario
ideas with scenarios waiting for assets
scale candidates
ideas without next action
```

Dashboard should not store idea data separately.

Source of truth:

```text
Idea Bank + linked entities
```

---

## 39. Permissions

MVP does not require complex permissions.

Future roles may include:

```text
owner
editor
strategist
reviewer
viewer
```

Idea Bank should be designed so permissions can be added later, but no role system is required in MVP.

---

## 40. API principles

Suggested project-scoped endpoints:

```text
GET /api/projects/:project_id/ideas
POST /api/projects/:project_id/ideas
GET /api/projects/:project_id/ideas/:idea_id
PATCH /api/projects/:project_id/ideas/:idea_id
POST /api/projects/:project_id/ideas/:idea_id/approve
POST /api/projects/:project_id/ideas/:idea_id/reject
POST /api/projects/:project_id/ideas/:idea_id/archive
POST /api/projects/:project_id/ideas/:idea_id/generate-scenario
```

Avoid global idea endpoints in MVP unless explicitly filtered by project.

---

## 41. File storage

Idea itself usually does not require files.

If imported files are used, they should be stored under project scope:

```text
storage/projects/{project_slug}/imports/ideas/
```

Idea attachments, if added later, should become Assets or Documents with project_id.

---

## 42. MVP scope

MVP must include:

- create idea manually;
- edit idea;
- list ideas by active project;
- filter by status;
- approve idea;
- reject idea;
- archive idea;
- generate scenario from approved idea;
- show linked scenarios;
- preserve project_id;
- preserve source_type.

MVP may include:

- tags;
- topic;
- priority;
- simple CSV import;
- simple performance summary.

MVP does not require:

- semantic duplicate detection;
- advanced scoring;
- automatic trend scraping;
- automatic optimization agent;
- complex permissions;
- public SaaS collaboration features.

---

## 43. Acceptance criteria

Idea Bank can be considered MVP-ready when:

1. User can create an idea inside active Project.
2. Idea cannot be created without project_id.
3. User can approve / reject / archive idea.
4. User can generate Scenario from approved idea.
5. Scenario stores idea_id and project_id.
6. Idea list shows status and next action.
7. Idea Detail shows related scenarios.
8. Data from one project is not mixed with another project.
9. Dashboard can show idea counters.
10. No project-specific rules are hardcoded in Idea Bank.

---

## 44. Out of scope

Do not include in MVP:

- public idea submission portal;
- external user collaboration;
- marketplace of ideas;
- paid idea packs;
- complex AI scoring;
- autonomous daily content strategy without human approval;
- mandatory autopublishing;
- automatic scraping from restricted platforms.

---

## 45. Open questions

Questions to decide later:

1. Should new manual ideas default to `raw` or `approved`?
2. Should Idea Bank use Kanban view in MVP or list view first?
3. Should `topic` be free text or controlled taxonomy?
4. Should `scale_candidate` be a status, a tag or a recommendation type?
5. Should idea score be shown before Analytics module is ready?
6. Should one Idea support multiple funnel stages, or only one primary stage?

Recommended MVP answers:

```text
manual idea default: raw
first UI: list view
initial topic: free text
scale_candidate: status for now
idea score: later
funnel stage: one primary stage
```

# Dashboard Spec

## 1. Назначение документа

Этот документ описывает главный рабочий экран платформы **Content Plant**: **Dashboard**.

Он фиксирует:

- какую задачу решает Dashboard;
- какие блоки должны быть на экране;
- какие данные отображаются;
- какие действия доступны пользователю;
- как Dashboard связан с проектами, статусами, production pipeline и аналитикой;
- что входит в MVP;
- что не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Dashboard

Dashboard — это операционная панель контентного производства.

Он должен отвечать на три вопроса:

```text
1. Что сейчас происходит?
2. Что требует моего внимания?
3. Что делать дальше?
```

Dashboard не должен быть декоративным экраном с красивыми, но бесполезными карточками.  
Он должен помогать пользователю каждый день управлять контентным заводом.

---

## 3. Основной принцип

Dashboard должен строиться вокруг активного проекта.

Если пользователь выбрал проект, Dashboard показывает:

- идеи этого проекта;
- сценарии этого проекта;
- ассеты этого проекта;
- render jobs этого проекта;
- review queue этого проекта;
- публикации этого проекта;
- метрики этого проекта.

Если в будущем появится режим Workspace Dashboard, он должен быть отдельным переключателем.

---

## 4. Главный пользовательский сценарий

Пользователь открывает Dashboard и видит:

```text
Active project
→ summary of pipeline
→ blockers
→ next actions
→ upcoming publications
→ recent results
```

После этого пользователь может:

- создать идею;
- продолжить сценарий;
- загрузить ассеты;
- запустить render;
- проверить готовый материал;
- экспортировать контент;
- отметить публикацию;
- добавить метрики;
- открыть аналитику.

---

## 5. Структура Dashboard MVP

Рекомендуемая структура экрана:

```text
Header
Project Health Summary
Pipeline Overview
Next Actions
Blockers
Review Queue
Upcoming Publications
Recent Metrics
Quick Create
```

Для MVP это может быть один экран с карточками и таблицами.

---

## 6. Header

Header Dashboard должен показывать:

- активный проект;
- период данных;
- быстрые действия;
- статус последних фоновых процессов.

Минимальные элементы:

```text
Project Switcher
Date range selector
Create button
Refresh / Last updated
```

Пример:

```text
Project: Current Project
Period: Last 7 days
Last updated: 12:40
```

---

## 7. Date Range Selector

Для MVP нужны варианты:

```text
Today
Last 7 days
Last 30 days
Custom
```

По умолчанию:

```text
Last 7 days
```

Date range влияет на:

- recent metrics;
- published content;
- performance summary;
- top content;
- weak content.

Date range не должен скрывать текущие operational tasks: идеи, сценарии, review и blockers показываются независимо от периода, если они актуальны.

---

## 8. Project Health Summary

Project Health Summary — верхний блок состояния проекта.

Он должен кратко показывать:

```text
Ideas waiting
Scenarios in progress
Assets missing
Content waiting for review
Scheduled publications
Published this period
```

Пример карточек:

| Metric | Meaning |
|---|---|
| Ideas waiting | Идеи, которые ещё не превращены в сценарии |
| Scenarios need assets | Сценарии, где не хватает ассетов |
| Review queue | Материалы, ожидающие проверки |
| Scheduled | Запланированные публикации |
| Published | Опубликовано за выбранный период |
| Revenue / conversions | Если метрики доступны |

---

## 9. Pipeline Overview

Pipeline Overview показывает, где находится контент.

Статусная воронка:

```text
Ideas
→ Scenarios
→ Assets
→ Production
→ Review
→ Approved
→ Scheduled
→ Published
→ Analyzed
```

MVP может отображать это как horizontal pipeline cards.

Пример:

| Stage | Count | Click action |
|---|---:|---|
| Ideas | 12 | Open Idea Bank |
| Scenarios | 8 | Open Scenario Studio |
| Needs Assets | 4 | Open Asset Mapping |
| Rendering | 2 | Open Production |
| Needs Review | 5 | Open Review |
| Scheduled | 7 | Open Calendar |
| Published | 21 | Open Analytics |

---

## 10. Next Actions

Next Actions — самый важный блок Dashboard.

Он должен показывать конкретные действия, а не абстрактные показатели.

Примеры actions:

```text
Generate scenario for 3 approved ideas
Upload assets for 4 scenarios
Review 5 rendered items
Add metrics for 6 published posts
Retry 1 failed render
Schedule 3 approved items
```

Каждое действие должно вести в нужный модуль.

Структура action item:

```json
{
  "action_id": "action_001",
  "project_id": "project_001",
  "type": "review_content",
  "title": "Review 5 rendered items",
  "target_module": "review",
  "priority": "high",
  "count": 5
}
```

---

## 11. Prioritization of Next Actions

Порядок действий:

1. Critical blockers.
2. Failed production jobs.
3. Content waiting for review.
4. Scenarios waiting for assets.
5. Approved ideas waiting for scenario.
6. Scheduled publications due soon.
7. Metrics missing for published content.
8. Optimization suggestions.

MVP может использовать простую фиксированную сортировку.

---

## 12. Blockers

Blockers — отдельный блок проблем, мешающих движению контента.

Типовые blockers:

- Brand Profile incomplete;
- missing required assets;
- render failed;
- CTA missing;
- export package incomplete;
- publication has no caption;
- published URL missing;
- metrics missing;
- unsupported asset format.

Blocker должен включать:

```text
problem
affected item
recommended action
link to fix
```

Пример:

```text
Scenario “Product Hook 01” cannot be rendered because Scene 3 has no linked asset.
[Open asset mapping]
```

---

## 13. Review Queue Preview

Dashboard должен показывать краткий preview очереди review.

Минимальные поля:

- thumbnail or icon;
- title;
- content type;
- platform;
- created date;
- QA status;
- action.

Пример:

| Item | Type | Status | Action |
|---|---|---|---|
| Hook Series 01 | video | needs_review | Open |
| Carousel 03 | carousel | needs_review | Open |
| Telegram Post 12 | text | needs_review | Open |

Кнопка:

```text
Open Review Queue
```

---

## 14. Upcoming Publications

Блок upcoming publications показывает ближайшие публикации.

Поля:

- date/time;
- platform;
- content title;
- content type;
- status;
- action.

Статусы:

```text
draft
scheduled
published
failed
cancelled
```

MVP может показывать ближайшие 5–10 публикаций.

---

## 15. Recent Metrics

Recent Metrics показывает результат выбранного периода.

Минимальные метрики:

```text
views
likes
comments
saves
shares
link_clicks
purchases
revenue
```

Если часть метрик недоступна, интерфейс должен показывать `not available`, а не ломаться.

---

## 16. Top Content

Dashboard может показывать лучшие материалы за выбранный период.

Сортировки MVP:

```text
by views
by saves
by clicks
by purchases
by revenue
```

Для MVP достаточно одной таблицы Top Content с выбранной метрикой.

Поля:

- title;
- content type;
- platform;
- published date;
- views;
- clicks;
- purchases;
- revenue.

---

## 17. Weak Content

Weak Content — материалы, которые требуют внимания.

Признаки:

- low retention;
- low engagement;
- no clicks;
- no metrics after publication;
- high effort with weak result.

В MVP этот блок можно отложить или сделать простым:

```text
Published items with no metrics
Published items with zero link clicks
```

---

## 18. Quick Create

Dashboard должен позволять быстро создавать основные сущности.

Кнопка Create может открывать меню:

```text
New Idea
New Scenario
Upload Asset
New Text Post
New Publication
```

В MVP достаточно:

```text
New Idea
Upload Asset
```

Остальные действия могут быть доступны из соответствующих модулей.

---

## 19. Empty State

Если проект новый, Dashboard должен объяснять первый шаг.

Пример:

```text
This project has no content yet.

Start by creating your first idea, then turn it into a scenario and production package.

[Create Idea]
[Open Brand Profile]
```

Если Brand Profile не заполнен:

```text
Brand Profile is incomplete.
Content generation may be inconsistent until you fill the core brand settings.

[Complete Brand Profile]
```

---

## 20. Dashboard states

Dashboard должен поддерживать состояния:

```text
new_project
active_project
project_with_blockers
project_in_production
project_waiting_review
project_with_recent_metrics
```

Визуально это может быть один экран с разными состояниями блоков.

---

## 21. Data sources

Dashboard использует данные из:

- Projects;
- Brand Profile;
- Idea Bank;
- Scenario Studio;
- Asset Library;
- Production Engine;
- Review module;
- Calendar / Publications;
- Analytics;
- QA module.

Dashboard не должен быть самостоятельным источником истины.  
Он только агрегирует данные из модулей.

---

## 22. Data model: Dashboard Summary

Пример агрегированной структуры:

```json
{
  "project_id": "project_001",
  "date_range": {
    "from": "2026-07-01",
    "to": "2026-07-07"
  },
  "pipeline": {
    "ideas": 12,
    "scenarios": 8,
    "needs_assets": 4,
    "rendering": 2,
    "needs_review": 5,
    "approved": 3,
    "scheduled": 7,
    "published": 21
  },
  "blockers": [],
  "next_actions": [],
  "recent_metrics": {
    "views": 0,
    "clicks": 0,
    "purchases": 0,
    "revenue": 0
  }
}
```

---

## 23. Refresh behavior

Для MVP достаточно ручного refresh.

Показывать:

```text
Last updated: timestamp
```

В будущем можно добавить:

- polling;
- websocket updates;
- background job progress;
- notifications.

---

## 24. Permissions

В MVP permissions не требуются.

Но в будущей SaaS-версии Dashboard может показывать разные действия для ролей:

- owner;
- admin;
- editor;
- reviewer;
- analyst;
- viewer.

Не реализовывать в MVP без отдельного решения.

---

## 25. Dashboard and Project Switcher

При переключении проекта Dashboard должен:

1. сбросить project-scoped данные;
2. загрузить summary нового проекта;
3. показать его pipeline;
4. показать его blockers;
5. показать его metrics;
6. не смешивать данные разных проектов.

Если данные ещё грузятся, показывать loading state.

---

## 26. Loading State

Loading state должен быть понятным.

Пример:

```text
Loading project dashboard...
```

Для отдельных блоков можно использовать skeleton placeholders.

Не показывать старые данные одного проекта как будто они относятся к новому.

---

## 27. Error State

Если Dashboard не может загрузиться:

```text
Dashboard could not be loaded.
Try again or open modules directly.
[Retry]
[Open Idea Bank]
```

Если не загрузился отдельный блок, остальные блоки должны работать.

---

## 28. UI layout recommendation

Рекомендуемая компоновка:

```text
Row 1:
  Header / Project context

Row 2:
  Project Health Summary cards

Row 3:
  Pipeline Overview

Row 4:
  Left: Next Actions
  Right: Blockers

Row 5:
  Left: Review Queue
  Right: Upcoming Publications

Row 6:
  Recent Metrics / Top Content
```

MVP может быть проще, но логика приоритета должна сохраняться.

---

## 29. Dashboard widgets

MVP widgets:

```text
ProjectHealthCards
PipelineOverview
NextActionsList
BlockersList
ReviewQueuePreview
UpcomingPublications
RecentMetricsCards
TopContentTable
QuickCreatePanel
```

---

## 30. Widget: ProjectHealthCards

Показывает короткие числа.

Поля:

```text
ideas_waiting
scenarios_in_progress
needs_assets
needs_review
scheduled
published_this_period
```

Клик по карточке ведёт в соответствующий модуль.

---

## 31. Widget: PipelineOverview

Показывает воронку статусов.

Требования:

- counts by stage;
- click to filtered list;
- highlight problematic stages;
- show empty stages as 0.

---

## 32. Widget: NextActionsList

Показывает список задач.

Поля:

- title;
- priority;
- count;
- target module;
- action button.

Priority:

```text
critical
high
medium
low
```

---

## 33. Widget: BlockersList

Показывает ошибки и препятствия.

Поля:

- blocker type;
- message;
- affected entity;
- recommended fix;
- link.

Если blockers нет:

```text
No blockers. Production pipeline is clear.
```

---

## 34. Widget: ReviewQueuePreview

Показывает первые материалы, ожидающие review.

Ограничение MVP:

```text
max 5 items
```

Кнопка:

```text
Open Review
```

---

## 35. Widget: UpcomingPublications

Показывает ближайшие публикации.

Ограничение MVP:

```text
max 10 items
```

Сортировка:

```text
scheduled_at ascending
```

---

## 36. Widget: RecentMetricsCards

Показывает метрики за период.

Поля MVP:

```text
views
engagements
clicks
purchases
revenue
```

Если purchases/revenue не подключены, можно показать только доступные метрики.

---

## 37. Widget: TopContentTable

Показывает лучшие материалы за период.

Поля:

- title;
- content type;
- platform;
- views;
- clicks;
- purchases;
- revenue.

MVP может скрывать пустые колонки.

---

## 38. Widget: QuickCreatePanel

Действия:

```text
Create Idea
Upload Asset
Open Brand Profile
Open Scenario Studio
```

В новом проекте первым действием должен быть Brand Profile или Create Idea в зависимости от completeness.

---

## 39. Brand Profile completeness

Dashboard должен показывать, если Brand Profile неполный.

Минимальные обязательные поля:

```text
brand_name
positioning
audience_summary
tone_of_voice
primary_url
target_platforms
```

Если этих полей нет, показывать warning.

---

## 40. Metrics completeness

Dashboard должен показывать публикации без метрик.

Пример:

```text
6 published items have no metrics yet.
[Add metrics]
```

Это важно, потому что без метрик optimization loop не работает.

---

## 41. Suggested MVP implementation

Для первого MVP можно реализовать Dashboard на основе server-side summary endpoint.

Пример endpoint:

```text
GET /api/projects/:project_id/dashboard
```

Ответ:

```json
{
  "summary": {},
  "pipeline": {},
  "next_actions": [],
  "blockers": [],
  "review_items": [],
  "upcoming_publications": [],
  "recent_metrics": {},
  "top_content": []
}
```

---

## 42. Frontend requirements

Frontend должен:

- загружать summary по active project;
- показывать loading state;
- показывать partial error states;
- давать переходы в модули;
- поддерживать empty states;
- не смешивать project data;
- обновляться по refresh.

---

## 43. Backend requirements

Backend должен:

- агрегировать counts by status;
- находить blockers;
- формировать next actions;
- отдавать review queue preview;
- отдавать upcoming publications;
- отдавать recent metrics;
- отдавать top content;
- учитывать date range.

---

## 44. MVP scope

В MVP входит:

- Dashboard page;
- active project context;
- health cards;
- pipeline overview;
- next actions;
- blockers;
- review preview;
- upcoming publications list;
- recent metrics cards;
- top content table;
- empty states;
- basic dashboard API.

---

## 45. Не входит в MVP

В MVP не входит:

- complex analytics;
- AI recommendations;
- drag-and-drop dashboard builder;
- custom widgets;
- real-time websocket updates;
- team workload;
- notifications center;
- cross-project executive dashboard;
- paid ads metrics;
- advanced attribution.

---

## 46. Definition of Done

Dashboard считается готовым для MVP, если пользователь может открыть активный проект и сразу понять:

- сколько идей ждут сценария;
- сколько сценариев ждут ассетов;
- сколько материалов ждут review;
- какие есть blockers;
- какие действия нужно сделать следующими;
- что запланировано;
- какие материалы опубликованы;
- какие базовые результаты получены за период.

Dashboard должен сокращать хаос, а не добавлять ещё один слой шума.

---

## 47. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/DATA_MODEL.md
docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md
docs/03_modules/QA_AND_REVIEW.md
docs/05_product_design/USER_WORKFLOWS.md
docs/05_product_design/WEB_UI_SPEC.md
```

---

## 48. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 49. Следующие документы

После этого документа необходимо создать:

1. `docs/05_product_design/PROJECT_SETTINGS_SPEC.md`
2. `docs/03_modules/SCENARIO_STUDIO_SPEC.md`
3. `docs/03_modules/ASSET_LIBRARY_SPEC.md`
4. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
5. `docs/02_platform_architecture/DATA_MODEL.md`

# Web UI Spec

## 1. Назначение документа

Этот документ описывает веб-интерфейс платформы **Content Plant**.

Он фиксирует:

- структуру интерфейса;
- основные разделы приложения;
- навигационную модель;
- ключевые экраны MVP;
- роли Project Switcher и Brand Profile;
- статусы контента в интерфейсе;
- минимальные требования к UX;
- что входит и не входит в MVP.

Документ описывает платформенный интерфейс Content Plant и не привязан к конкретному бренду или проекту.

---

## 2. Главная задача интерфейса

Интерфейс Content Plant должен помогать пользователю управлять контентным производством от идеи до результата.

Главный рабочий путь:

```text
Project
→ Brand Profile
→ Idea
→ Scenario
→ Assets
→ Production
→ Review
→ Export / Schedule
→ Metrics
```

Интерфейс не должен быть просто набором красивых экранов.  
Он должен быть пультом управления контентным заводом.

---

## 3. UX-принципы

### 3.1. Project-first

Почти все действия происходят внутри активного проекта.

Пользователь должен всегда понимать:

- какой проект сейчас активен;
- какие данные относятся к этому проекту;
- где переключить проект;
- какие настройки бренда применяются.

---

### 3.2. Workflow-first

Интерфейс должен вести пользователя по процессу, а не заставлять искать следующий шаг.

Пример:

```text
Idea created
→ suggested action: Generate Scenario

Scenario approved
→ suggested action: Upload Assets

Assets ready
→ suggested action: Render

Render complete
→ suggested action: Review
```

---

### 3.3. Status clarity

У каждой сущности должен быть понятный статус.

Пользователь должен быстро видеть:

- что ждёт сценария;
- что ждёт ассетов;
- что сейчас в production;
- что ждёт review;
- что готово к публикации;
- что уже опубликовано;
- что требует анализа.

---

### 3.4. Human-in-the-loop

На MVP пользователь остаётся в контуре решений.

Интерфейс должен поддерживать:

- approve;
- reject;
- edit;
- regenerate;
- replace asset;
- rerender;
- export;
- schedule;
- add metrics.

---

### 3.5. No SaaS overload in MVP

MVP-интерфейс не должен содержать лишние SaaS-функции:

- billing;
- тарифы;
- команды;
- роли;
- marketplace;
- публичный onboarding;
- сложную систему permissions.

---

## 4. Основная навигация

Рекомендуемая структура sidebar navigation:

```text
Dashboard
Projects
Idea Bank
Scenario Studio
Asset Library
Production
Review
Calendar
Analytics
Settings
```

В будущем можно добавить:

```text
Trend Radar
Publishing Hub
Templates
Reports
Integrations
```

---

## 5. Project Switcher

Project Switcher — обязательный элемент интерфейса.

Он должен быть виден в верхней части приложения или sidebar.

Функции:

- показать активный проект;
- переключить проект;
- открыть настройки проекта;
- создать новый проект.

После переключения проекта меняются:

- идеи;
- сценарии;
- ассеты;
- production jobs;
- review queue;
- публикации;
- аналитика;
- CTA;
- Brand Profile.

---

## 6. Global Header

Верхняя панель может содержать:

```text
Project Switcher
Search
Create button
Notifications / Queue status
User menu
```

Для MVP user menu может быть минимальным или отсутствовать.

---

## 7. Dashboard

Dashboard — главный рабочий экран.

Он должен отвечать на вопрос:

> Что сейчас происходит в контентном производстве и что нужно сделать следующим?

MVP-блоки Dashboard:

```text
Active Project
Production Pipeline Summary
Ideas Waiting for Scenario
Scenarios Waiting for Assets
Content Waiting for Review
Approved Content
Scheduled Publications
Recent Metrics
Next Recommended Actions
```

Dashboard не должен быть декоративной витриной.  
Он должен быть операционной панелью.

---

## 8. Projects Screen

Экран Projects показывает список проектов.

Минимальные элементы:

- project name;
- project slug;
- status;
- default language;
- target platforms;
- last updated;
- quick actions.

Действия:

- create project;
- open project;
- edit settings;
- archive project.

MVP не требует сложных прав доступа и команд.

---

## 9. Project Settings

Project Settings содержит настройки выбранного проекта.

Разделы:

```text
Basics
Brand Profile
CTA Library
Links
Platforms
Export Settings
Analytics Settings
```

Для MVP можно реализовать все настройки на одной странице с секциями.

---

## 10. Brand Profile UI

Brand Profile должен редактироваться через понятную форму.

Минимальные секции:

```text
Brand Basics
Audience
Tone of Voice
Visual Identity
CTA
Links
Restrictions
Platform Settings
```

Поля MVP:

- brand name;
- positioning;
- audience summary;
- tone description;
- allowed phrases;
- forbidden phrases;
- colors;
- fonts;
- logo;
- CTA list;
- primary URL;
- forbidden topics;
- target platforms.

---

## 11. Idea Bank

Idea Bank — список идей проекта.

Цель:

- хранить темы;
- быстро переводить идеи в сценарии;
- видеть статус каждой идеи.

Элементы списка:

- title;
- topic;
- funnel stage;
- suggested content type;
- status;
- created date;
- source;
- next action.

Фильтры:

- status;
- content type;
- funnel stage;
- topic;
- date.

Действия:

- create idea;
- edit idea;
- approve idea;
- generate scenario;
- archive idea.

---

## 12. Idea Detail

Экран идеи должен показывать:

- title;
- description;
- topic;
- funnel stage;
- suggested format;
- source;
- notes;
- generated scenarios;
- related content items;
- metrics if available.

Главная кнопка:

```text
Generate Scenario
```

---

## 13. Scenario Studio

Scenario Studio — экран создания и редактирования сценариев.

Основные зоны:

```text
Scenario settings
Scenes editor
Visual prompts
Captions
CTA
Status / actions
```

MVP-функции:

- generate scenario;
- edit scene text;
- edit overlay text;
- generate visual prompts;
- regenerate selected scene;
- approve scenario;
- send to assets;
- generate text posts.

---

## 14. Scenario List

Список сценариев должен показывать:

- title;
- content type;
- project;
- status;
- scene count;
- assets status;
- last updated;
- next action.

Статусы:

```text
draft
approved
needs_assets
ready_to_render
in_production
rendered
archived
```

---

## 15. Scenario Detail

Scenario Detail должен показывать:

```text
Scenario metadata
Scenes
Dialogue / text overlays
Visual prompts
Required assets
CTA
Caption drafts
Related render jobs
```

Для каждой сцены:

- order;
- role;
- duration;
- speaker;
- text;
- visual prompt;
- linked asset;
- status.

---

## 16. Visual Prompt Panel

Для каждой сцены должен быть блок prompt.

Функции:

- copy prompt;
- regenerate prompt;
- edit prompt;
- mark as used;
- attach generated asset.

Prompt должен быть собран из:

- scene description;
- format rules;
- Brand Profile;
- visual restrictions;
- platform requirements.

---

## 17. Asset Library

Asset Library хранит проектные ассеты.

Типы ассетов:

```text
image
video
audio
logo
background
character
template_asset
```

Элементы списка:

- preview;
- filename;
- type;
- tags;
- linked scenario;
- linked scene;
- status;
- created date.

Фильтры:

- type;
- tag;
- linked / unlinked;
- status;
- date.

Действия:

- upload;
- tag;
- link to scene;
- preview;
- delete / archive.

---

## 18. Asset Upload Flow

Минимальный upload flow:

```text
1. Select files
2. Choose asset type
3. Add tags
4. Link to scenario or scene, optional
5. Upload
6. Validate
7. Save to project storage
```

Validation:

- file type supported;
- file size acceptable;
- project_id attached;
- image/video resolution detected;
- aspect ratio warning if needed.

---

## 19. Scene Asset Mapping UI

Для сценариев с визуальными сценами нужен mapping-экран.

Формат:

```text
Scene 1 | prompt | selected asset | preview
Scene 2 | prompt | selected asset | preview
Scene 3 | prompt | selected asset | preview
```

Действия:

- choose asset;
- upload new asset;
- replace asset;
- preview;
- mark ready.

Когда все обязательные сцены имеют ассеты, сценарий может перейти в `ready_to_render`.

---

## 20. Production Screen

Production показывает render jobs и production queue.

Элементы:

- job id;
- project;
- content type;
- scenario;
- template;
- status;
- created date;
- progress;
- output link;
- error, if any.

Статусы:

```text
queued
rendering
rendered
failed
cancelled
```

Действия:

- start render;
- cancel;
- retry;
- open output;
- send to review.

---

## 21. Render Setup

Перед запуском рендера пользователь должен видеть:

- scenario;
- content type;
- template;
- assets status;
- Brand Profile applied;
- output format;
- duration;
- platform target;
- CTA;
- audio settings.

Кнопка:

```text
Render
```

Если не хватает данных, кнопка должна быть disabled с объяснением.

---

## 22. Review Queue

Review Queue показывает материалы, ожидающие проверки.

Элементы:

- preview thumbnail;
- title;
- content type;
- platform;
- status;
- created date;
- issue flags;
- next action.

Действия:

- open review;
- approve;
- reject;
- request changes.

---

## 23. Review Detail

Review Detail должен показывать:

- video / carousel / text preview;
- metadata;
- caption;
- CTA;
- QA checklist;
- notes;
- action buttons.

Actions:

```text
Approve
Reject
Edit text
Replace asset
Regenerate caption
Rerender
Export
Schedule
```

---

## 24. Export Packages

Экран или блок Export должен показывать готовые пакеты.

Для видео:

```text
video.mp4
caption.txt
metadata.json
cover.png / cover.txt
```

Для текстовых постов:

```text
telegram.txt
threads.txt
vk.txt
metadata.json
```

Действия:

- download package;
- copy caption;
- open folder;
- mark as exported;
- schedule publication.

---

## 25. Calendar

Calendar в MVP может быть простым списком публикаций.

Поля:

- publication date;
- platform;
- project;
- content title;
- content type;
- status;
- export package;
- published URL;
- notes.

View modes:

```text
list
week
month
```

Для MVP достаточно list view.

---

## 26. Publication Detail

Publication Detail показывает:

- content item;
- platform;
- caption;
- scheduled time;
- export package;
- published URL;
- status;
- metrics snapshots.

Действия:

- mark as published;
- add published URL;
- add metrics;
- reschedule;
- cancel.

---

## 27. Analytics

Analytics должен отвечать:

> Что работает, а что нет?

MVP-секции:

```text
Overview
By Content Type
By Platform
By Topic
By CTA
Top Content
Weak Content
Manual Metrics Input
CSV Import
```

Минимальные метрики:

- views;
- likes;
- comments;
- saves;
- shares;
- profile visits;
- link clicks;
- registrations;
- purchases;
- revenue.

---

## 28. Analytics UI

Базовый dashboard:

```text
Period selector
Project selector
Metric cards
Content type table
Platform table
Top content list
CTA performance table
```

Графики могут быть простыми.  
Главное — помочь принимать решения.

---

## 29. Settings

Global Settings в MVP минимальны.

Возможные разделы:

```text
Storage
Render Defaults
Integrations
Export Defaults
System
```

Не включать billing, team settings и roles в MVP.

---

## 30. Create Button

Глобальная кнопка Create может открывать меню:

```text
New Project
New Idea
New Scenario
Upload Asset
New Text Post
New Publication
```

Список действий должен зависеть от активного проекта.

---

## 31. Search

Search в MVP может быть простым.

Искать по:

- ideas;
- scenarios;
- assets;
- content items;
- publications.

Результаты должны быть scoped to active project by default.

---

## 32. Notifications and warnings

Интерфейс должен показывать предупреждения:

- Brand Profile incomplete;
- missing assets;
- unsupported file format;
- render failed;
- CTA missing;
- forbidden phrase detected;
- no metadata;
- export package incomplete.

Предупреждения должны быть полезными, а не шумными.

---

## 33. Empty states

Каждый пустой экран должен объяснять следующий шаг.

Пример:

```text
No ideas yet.
Create your first idea to start the content pipeline.
[Create Idea]
```

Плохой empty state:

```text
No data.
```

---

## 34. MVP UI pages

Минимальный список страниц MVP:

```text
/dashboard
/projects
/projects/:project_id/settings
/ideas
/ideas/:idea_id
/scenarios
/scenarios/:scenario_id
/assets
/production
/review
/review/:content_id
/calendar
/analytics
/settings
```

---

## 35. URL principles

URL должен быть понятным и platform-level.

Допустимо:

```text
/projects/:project_id/scenarios/:scenario_id
```

или проще для MVP:

```text
/scenarios/:scenario_id
```

если active project хранится в state.

Важно: проектный контекст должен быть однозначным.

---

## 36. MVP layout

Рекомендуемая структура:

```text
Sidebar
Header
Main content area
Right detail panel, optional
```

Для сложных экранов можно использовать right panel для:

- metadata;
- status;
- actions;
- QA;
- notes.

---

## 37. Responsive requirements

MVP может быть desktop-first, потому что это рабочий инструмент.

Но интерфейс не должен ломаться на планшете и ноутбуке.

Mobile-first не обязателен для Content Plant MVP, в отличие от пользовательских продуктов.

Минимум:

- корректная работа на 1366×768;
- комфортная работа на 1440×900;
- адаптация на 1920×1080;
- без критичных переполнений.

---

## 38. Visual style of Content Plant UI

Content Plant UI должен быть:

- нейтральным;
- рабочим;
- чистым;
- не завязанным на стиль конкретного проекта;
- достаточно спокойным для ежедневной работы.

Важно:

> Интерфейс платформы не должен наследовать визуальный стиль активного бренда полностью.

Brand Profile влияет на preview и production, но не должен перекрашивать весь интерфейс приложения.

---

## 39. Brand preview

В интерфейсе можно показывать Brand Preview.

Пример:

```text
Brand colors
Fonts
CTA style
Sample card
Sample caption
```

Это помогает понять, как настройки будут применяться в контенте.

---

## 40. Status badges

Использовать status badges для:

- ideas;
- scenarios;
- assets;
- render jobs;
- content items;
- publications.

Пример:

```text
draft
needs_assets
ready_to_render
rendering
needs_review
approved
published
failed
```

---

## 41. Tables and cards

Для списков лучше использовать таблицы с быстрыми действиями.

Для визуального контента использовать cards.

Пример:

- Idea Bank: table;
- Asset Library: grid/cards;
- Review Queue: cards;
- Analytics: tables + simple charts;
- Production: table.

---

## 42. Permissions in MVP

В MVP permissions не требуются.

Но архитектурно UI не должен предполагать, что проект всегда будет однопользовательским.

В будущем могут появиться:

- owner;
- admin;
- editor;
- reviewer;
- viewer.

Не реализовывать в MVP без отдельного решения.

---

## 43. Error states

Ошибки должны быть понятными.

Пример:

```text
Render failed because Scene 3 has no linked asset.
```

Плохо:

```text
Error 500.
```

Для каждой ошибки желательно показывать:

- что случилось;
- где проблема;
- что сделать дальше.

---

## 44. Loading states

Для долгих процессов показывать статус:

- uploading;
- generating;
- rendering;
- exporting;
- importing metrics.

Пользователь должен понимать, что система работает, а не зависла.

---

## 45. Confirmation actions

Требовать подтверждение для:

- delete project;
- archive project;
- delete asset;
- cancel render;
- overwrite export package;
- bulk changes.

Для MVP можно использовать archive вместо hard delete.

---

## 46. Что входит в MVP UI

В MVP UI входит:

- Project Switcher;
- Projects;
- Project Settings;
- Brand Profile form;
- Idea Bank;
- Scenario Studio basic;
- Visual Prompt panel;
- Asset Library;
- Scene Asset Mapping;
- Production queue;
- Review queue;
- Export package access;
- Calendar list;
- Analytics basic;
- Manual metrics input.

---

## 47. Что не входит в MVP UI

В MVP UI не входит:

- billing;
- pricing pages;
- team management;
- role management;
- client onboarding;
- marketplace;
- public template gallery;
- Canva-like editor;
- advanced timeline editor;
- full social media inbox;
- complex automation builder.

---

## 48. Definition of Done for UI MVP

UI MVP считается готовым, если пользователь может пройти путь:

```text
Create Project
→ Fill Brand Profile
→ Create Idea
→ Generate Scenario
→ Copy Visual Prompts
→ Upload Assets
→ Link Assets to Scenes
→ Render
→ Review
→ Export
→ Schedule / Mark Published
→ Add Metrics
```

без обращения к файловой структуре вручную и без смешивания данных разных проектов.

---

## 49. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md
docs/05_product_design/USER_WORKFLOWS.md
docs/06_agents/AGENT_RULES.md
```

---

## 50. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 51. Следующие документы

После этого документа необходимо создать:

1. `docs/05_product_design/DASHBOARD_SPEC.md`
2. `docs/05_product_design/PROJECT_SETTINGS_SPEC.md`
3. `docs/03_modules/SCENARIO_STUDIO_SPEC.md`
4. `docs/03_modules/ASSET_LIBRARY_SPEC.md`
5. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`

# MVP Scope

## 1. Назначение документа

Этот документ фиксирует границы MVP платформы **Content Plant**.

Он нужен, чтобы:

- определить, что именно входит в первую рабочую версию;
- отделить обязательные функции от будущих;
- защитить проект от преждевременного усложнения;
- не превратить MVP во внешний SaaS раньше времени;
- задать критерии готовности первой версии;
- дать агентам и разработчикам чёткие рамки работы.

Документ является источником истины для определения объёма MVP.

---

## 2. Краткое определение MVP

MVP Content Plant — это внутренняя мультипроектная платформа, которая позволяет создавать проекты, задавать для них бренд-профили, генерировать сценарии, принимать ассеты, собирать контентные материалы и готовить публикационные пакеты.

MVP не является публичным SaaS.

Главная задача MVP:

> Проверить, может ли Content Plant реально ускорить и систематизировать производство контента для нескольких внутренних проектов без привязки к одному бренду.

---

## 3. Главный принцип MVP

Главный принцип:

> MVP должен быть мультипроектным внутри, но не должен сразу становиться публичным SaaS.

Это означает:

- в системе можно создать несколько проектов;
- каждый проект имеет собственный Brand Profile;
- ассеты, сценарии, публикации и аналитика разделяются по проектам;
- первый validation project может использоваться для проверки платформы, но не должен становиться платформенной зависимостью;
- внешняя регистрация пользователей, тарифы, биллинг и команды не входят в MVP.

---

## 4. Почему MVP должен быть мультипроектным

Мультипроектность нужна уже на первом этапе, даже если фактически первым активным будет один validation project.

Причины:

1. Нельзя зашивать Content Plant под один конкретный проект.
2. Владелец планирует использовать платформу для нескольких проектов.
3. В будущем Content Plant может стать самостоятельным продуктом.
4. Универсальные форматы должны работать для разных брендов.
5. Brand Profile должен быть проверен как механизм кастомизации.

На MVP мультипроектность может быть простой:

```text
Workspace: internal
  Project: demo_project
  Project: internal_product
  Project: client_brand
```

Не требуется сложная система пользователей, ролей и доступов.

---

## 5. MVP как вертикальный срез

MVP должен быть построен как рабочий вертикальный срез, а не как набор незавершённых экранов.

Первый полезный вертикальный срез:

```text
Project
→ Brand Profile
→ Idea
→ Scenario / Draft
→ QA
→ Review
→ Export Package
→ Manual Publication
→ Metric Snapshot
→ Insight
→ New Idea
```

Этот цикл должен работать для первого validation project, но архитектурно не должен быть зашит под него.

---

## 6. Основной сценарий MVP

Базовый рабочий сценарий:

1. Пользователь выбирает проект.
2. Пользователь видит Brand Profile проекта.
3. Пользователь создаёт или выбирает идею.
4. Система генерирует `Scenario` или text draft.
5. Система проводит базовый QA для текста, CTA и project rules.
6. Пользователь review-ит и утверждает материал.
7. `Publishing Hub` создаёт `Export Package`.
8. Пользователь публикует материал вручную.
9. В системе создаётся `Publication` record.
10. Метрики заносятся вручную или импортируются.
11. Система сохраняет `Metric Snapshot`.
12. Система формирует `Insight`.
13. На основе `Insight` создаётся следующая `Idea`.

---

## 7. Что входит в MVP

### 7.1. Project Layer

MVP должен поддерживать:

- создание проекта;
- выбор активного проекта;
- хранение проектных настроек;
- базовый Project Profile;
- базовый Brand Profile;
- разделение данных по проектам.

Минимальные поля проекта:

- project_id;
- project_slug;
- project_name;
- description;
- status;
- default_language;
- target_platforms;
- primary_url;
- created_at;
- updated_at.

---

### 7.2. Brand Profile

MVP должен поддерживать базовый Brand Profile.

Brand Profile должен включать:

- название бренда;
- описание;
- целевую аудиторию;
- позиционирование;
- tone of voice;
- основные цвета;
- шрифты или типографические предпочтения;
- визуальные правила;
- запрещённые элементы;
- CTA;
- ссылки;
- продукты или офферы;
- платформы публикации.

В MVP Brand Profile может храниться в базе, JSON или конфигурационном файле.  
Главное: брендовые правила не должны быть зашиты в код.

---

### 7.3. Idea Bank

MVP должен поддерживать базовый банк идей.

Функции:

- создать идею вручную;
- сохранить тему;
- указать проект;
- указать формат;
- указать статус;
- указать воронку: attention / trust / conversion;
- отправить идею в генерацию сценария.

Статусы идей:

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

---

### 7.4. Scenario Studio Basic

MVP должен поддерживать генерацию сценариев.

Для сценария нужно хранить:

- project_id;
- content_type;
- title;
- topic;
- hook;
- scenes;
- dialogue lines;
- text overlays;
- visual prompts;
- CTA;
- captions;
- status.

Scenario Studio должен учитывать Brand Profile выбранного проекта.

На MVP допускается ручной запуск генерации.

---

### 7.5. Visual Prompts

MVP должен генерировать prompts для внешней генерации изображений или видео.

Это важно, потому что на первом этапе пользователь сам создаёт визуальные ассеты в других нейросетевых инструментах.

Prompt должен описывать:

- сцену;
- персонажей;
- настроение;
- композицию;
- стиль;
- формат;
- ограничения;
- связь с брендом.

Prompts должны учитывать Brand Profile активного проекта, но сам механизм должен быть универсальным.

---

### 7.6. Asset Upload

MVP должен поддерживать загрузку ассетов.

Типы ассетов:

- image;
- video;
- audio;
- logo;
- background;
- character;
- template asset.

Для каждого ассета нужно хранить:

- asset_id;
- project_id;
- type;
- filename;
- file_path;
- tags;
- status;
- linked_scenario_id;
- linked_scene_id;
- created_at.

MVP должен позволять привязать ассет к сцене сценария.

---

### 7.7. Первый safest MVP format: `text_social_post`

Для первого implementation loop MVP должен в первую очередь поддерживать формат **`text_social_post`**.

Причины:

- он быстрее всего проверяет `Project -> Brand Profile -> Idea -> Scenario / Draft -> QA -> Review -> Export Package -> Manual Publication -> Metric Snapshot -> Insight`;
- он не зависит от FFmpeg/HyperFrames/video assets для первого loop;
- он позволяет проверить project scoping, Brand Profile, review flow, export-first и manual publication;
- video formats должны подключаться после стабилизации core loop.

Минимальные требования:

- platform-specific text variants;
- project-aware CTA;
- export-ready `.txt` bundle;
- metadata file;
- QA and review before export;
- manual publication support через `Publishing Hub`.

---

### 7.8. Export Package

MVP должен создавать публикационный пакет.

`Export Package` belongs to `Publishing Hub`.

`Production Engine` не должен владеть финальным `Export Package`; он может передавать только base outputs, technical QA result и render output metadata.

Минимальный пакет:

```text
content_item/
  video.mp4
  caption.txt
  metadata.json
  cover.txt или cover.png
```

Для каруселей:

```text
carousel_item/
  slides/
    slide_01.png
    slide_02.png
    slide_03.png
  caption.txt
  metadata.json
```

metadata.json должен включать:

- project_id;
- content_id;
- content_type;
- platform;
- title;
- hook;
- CTA;
- UTM;
- created_at;
- render_status.

---

### 7.9. Basic Review

MVP должен включать простой review flow.

Статусы:

```text
draft
needs_assets
ready_to_render
rendering
rendered
needs_review
approved
rejected
scheduled
published
```

Минимальные действия:

- preview;
- approve;
- reject;
- regenerate text;
- replace asset;
- export.

---

### 7.10. Text Social Posts

MVP должен поддерживать генерацию текстовых постов на основе сценария или идеи.

Каналы:

- Telegram;
- Threads;
- VK.

На MVP не обязательно сразу публиковать автоматически.  
Достаточно генерировать export-ready тексты.

Для каждого поста:

- title;
- body;
- CTA;
- link;
- hashtags, если нужны;
- platform;
- project_id;
- source_scenario_id.

---

### 7.11. Basic Calendar

MVP должен иметь базовый календарь или список публикаций.

Минимальные функции:

- дата публикации;
- платформа;
- проект;
- content item;
- статус;
- ссылка на export package;
- заметки.

Автопостинг не обязателен для MVP.

---

### 7.12. Basic Analytics

MVP должен позволять заносить метрики вручную или импортировать CSV.

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

На первом этапе достаточно таблицы и простого dashboard.

---

### 7.13. Documentation Foundation

MVP включает обязательную документационную базу:

- `00_index.md`;
- `PLATFORM_OVERVIEW.md`;
- `PRODUCT_STRATEGY.md`;
- `MVP_SCOPE.md`;
- `WORKSPACE_AND_PROJECT_MODEL.md`;
- `BRAND_SYSTEM_SPEC.md`;
- `AGENT_RULES.md`.

Новые модули должны добавляться только после описания в документации.

---

## 8. Что желательно, но не обязательно в MVP

Следующие функции могут быть добавлены после базового вертикального среза.

### 8.1. Atmospheric Text Video

Сборка атмосферных видео с текстом поверх загруженного видео или изображения.

### 8.2. Dialog Carousel

Генерация каруселей из сценария Dialog Miniseries.

### 8.3. Explainer Carousel

Объясняющие карусели на основе темы и Brand Profile.

### 8.4. Pinterest Pins

Генерация вертикальных карточек для Pinterest.

### 8.5. Trend Radar MVP

Ручной импорт ссылок или CSV с трендами.

Система анализирует:

- хук;
- тему;
- структуру;
- эмоциональный триггер;
- потенциальную адаптацию под проект.

### 8.6. Batch Rendering

Возможность собрать несколько материалов одним запуском.

### 8.7. Telegram / VK Autoposting

Автоматическая публикация в каналы, где API доступен и стабилен.

### 8.8. Weekly Report

Простой недельный offer:

- что опубликовано;
- какие форматы сработали;
- какие темы повторить;
- что остановить.

---

## 9. Что не входит в MVP

В MVP не входят функции публичного SaaS.

### 9.1. Пользователи и доступы

Не входит:

- публичная регистрация;
- личные кабинеты внешних пользователей;
- команды;
- роли;
- permissions;
- приглашения участников.

На MVP может быть один внутренний пользователь.

---

### 9.2. Биллинг

Не входит:

- тарифы;
- подписки;
- оплата;
- invoices;
- ограничения по тарифам;
- trial-периоды.

---

### 9.3. SaaS onboarding

Не входит:

- публичный onboarding;
- wizard для новых клиентов;
- шаблоны под разные ниши для внешних пользователей;
- customer success flow.

---

### 9.4. Marketplace

Не входит:

- marketplace шаблонов;
- marketplace промтов;
- marketplace production formats;
- сторонние авторы шаблонов.

---

### 9.5. Полный автопостинг во все соцсети

Не входит:

- обязательный автопостинг в TikTok;
- обязательный автопостинг в Instagram;
- сложные интеграции с нестабильными API;
- автоматический сбор всех метрик из всех платформ.

MVP должен поддерживать export packages.  
Автопостинг подключается постепенно.

---

### 9.6. Полная генерация изображений и видео через API

Не входит:

- генерация изображений через API;
- анимация изображений через API;
- генерация музыки через API;
- автоматический подбор трендовой музыки.

На MVP пользователь генерирует визуалы во внешних инструментах и загружает их в Content Plant.

---

### 9.7. Сложный AI Strategy Optimizer

Не входит:

- автоматическое перераспределение бюджета;
- сложные прогнозы;
- ML-модели;
- полностью автономное принятие решений.

На MVP достаточно простых правил и offerов.

---

## 10. Приоритизация MVP

### 10.1. Must-have

Без этих функций MVP не считается полезным:

- project switcher;
- project profile;
- brand profile;
- idea creation;
- scenario generation;
- text social post generation;
- export package;
- basic review;
- basic metrics input;
- documentation base.

---

### 10.2. Should-have

Желательно добавить в первой или второй итерации:

- dialog miniseries render;
- visual prompts;
- asset upload;
- carousel generation;
- atmospheric text video;
- content calendar;
- Trend Radar manual import;
- batch render;
- basic QA checks;
- weekly report.

---

### 10.3. Could-have

Можно добавить, если не ломает сроки:

- Telegram autoposting;
- VK autoposting;
- Pinterest package generation;
- template variants;
- reusable music library;
- simple dashboard charts.

---

### 10.4. Won't-have for MVP

Не делать в MVP:

- SaaS accounts;
- billing;
- teams;
- roles;
- marketplace;
- public landing for Content Plant;
- full social media API integrations;
- AI image/video generation APIs;
- complex attribution model;
- advanced optimizer.

---

## 11. Минимальные экраны MVP

MVP должен включать следующие экраны.

### 11.1. Projects

Функции:

- список проектов;
- создать проект;
- выбрать активный проект;
- открыть настройки проекта.

### 11.2. Project Settings

Функции:

- Project Profile;
- Brand Profile;
- CTA;
- links;
- target platforms.

### 11.3. Idea Bank

Функции:

- список идей;
- создать идею;
- фильтр по проекту;
- статус;
- отправить в сценарий.

### 11.4. Scenario Studio

Функции:

- создать сценарий;
- посмотреть сцены;
- посмотреть реплики;
- посмотреть visual prompts;
- сгенерировать captions;
- отправить в production.

### 11.5. Asset Library

Функции:

- загрузка ассетов;
- список ассетов;
- теги;
- связь со сценами.

### 11.6. Production

Функции:

- список render jobs;
- запуск рендера;
- статус;
- preview;
- export.

### 11.7. Review

Функции:

- просмотр готового материала;
- approve;
- reject;
- заметки.

### 11.8. Calendar / Publications

Функции:

- список публикаций;
- дата;
- платформа;
- статус;
- export package.

### 11.9. Analytics

Функции:

- ручной ввод метрик;
- импорт CSV;
- базовые таблицы;
- простые выводы.

---

## 12. Минимальные сущности MVP

На уровне данных MVP должен поддерживать:

- Workspace;
- Project;
- BrandProfile;
- Idea;
- Scenario;
- Scene;
- Asset;
- RenderJob;
- ContentItem;
- Publication;
- MetricSnapshot;
- CTA;
- Platform.

Детальная модель должна быть описана в `DATA_MODEL.md`.

---

## 13. Первый production line

Первым production line должен стать:

```text
text_social_post
```

Причины:

- это самый безопасный способ проверить core platform loop;
- он не зависит от video assets и render stack;
- он позволяет рано проверить `Export Package`, `Publication`, `Metric Snapshot` и `Insight`;
- после стабилизации этого loop можно подключать `dialog_miniseries` и другие video formats.

Минимальный pipeline:

```text
Idea
→ Scenario / Draft
→ QA
→ Review
→ Export Package
→ Manual Publication
→ Metric Snapshot
→ Insight
```

---

## 14. Validation project boundary

A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`.

Для MVP это означает:

- платформа может проверяться на одном реальном проекте;
- проектные офферы, цены, CTA, персонажи, URL, визуальные правила и готовые тексты не должны попадать в платформенные спецификации;
- все универсальные механики должны работать через Project, Brand Profile, Content Format и Production Template;
- результат проверки должен подтверждать универсальность платформенного pipeline.

---

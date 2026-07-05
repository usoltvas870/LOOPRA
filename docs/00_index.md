# Content Plant Documentation Index

## 1. Назначение документа

Этот документ является центральной картой документации проекта **Content Plant**.

Его задача — описать:

- какие документы существуют в проекте;
- зачем нужен каждый документ;
- в каком порядке их читать;
- какие документы являются источниками истины;
- как агентам и разработчикам работать с документацией;
- как поддерживать документацию в актуальном состоянии.

Content Plant проектируется как **мультипроектная контентная платформа**. A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`. Архитектура и документация должны сразу учитывать возможность подключения разных внутренних проектов и внешних клиентских брендов.

---

## 2. Ключевая идея Content Plant

**Content Plant** — это платформа для системного производства, публикации и оптимизации контента для разных проектов и брендов.

Платформа должна помогать:

- анализировать тренды и рынок;
- превращать тренды и идеи в сценарии;
- генерировать тексты, диалоги, CTA и промты для визуалов;
- принимать изображения, видео, музыку и другие ассеты;
- собирать ролики, карусели, посты и Pinterest-карточки;
- готовить публикационные пакеты для разных социальных сетей;
- публиковать контент там, где это технически возможно;
- собирать аналитику;
- улучшать контентную стратегию на основе данных.

Content Plant не должен быть жёстко завязан на конкретный проект. Любой первый validation project должен оставаться проектным слоем, а не ядром платформы.

---

## 3. Принцип разделения документации

Документация делится на несколько уровней:

### 3.1. Platform Core

Документы, описывающие саму платформу Content Plant: продукт, цели, MVP, SaaS-потенциал.

### 3.2. Platform Architecture

Документы, описывающие техническую и продуктовую архитектуру: workspace/project, бренд-система, модель данных, пайплайны, интеграции.

### 3.3. Platform Modules

Документы по отдельным функциональным модулям: Trend Radar, Scenario Studio, Asset Library, Production Engine, Publishing Hub, Analytics, QA and Review.

### 3.4. Content Format Specs

Документы, описывающие универсальные форматы контента: мини-сериалы, атмосферные видео, карусели, текстовые посты, Pinterest Pins.

### 3.5. Product Design

Документы по пользовательским сценариям и веб-интерфейсу.

### 3.6. Agents

Документы, регулирующие работу агентов и разработчиков.

### 3.7. Project Profiles

Документы конкретных проектов внутри Content Plant: внутренние продукты, экспериментальные направления и клиентские бренды.

---

## 4. Рекомендуемая структура папок

```text
docs/
  00_index.md

  01_platform/
    PLATFORM_OVERVIEW.md
    PRODUCT_STRATEGY.md
    MVP_SCOPE.md
    SAAS_VISION.md
    DEVELOPMENT_ROADMAP.md

  02_platform_architecture/
    SYSTEM_ARCHITECTURE.md
    DATA_MODEL.md
    WORKSPACE_AND_PROJECT_MODEL.md
    BRAND_SYSTEM_SPEC.md
    PIPELINES_SPEC.md
    INTEGRATIONS_SPEC.md

  03_modules/
    TREND_RADAR_SPEC.md
    SCENARIO_STUDIO_SPEC.md
    ASSET_LIBRARY_SPEC.md
    PRODUCTION_ENGINE_SPEC.md
    PUBLISHING_HUB_SPEC.md
    ANALYTICS_AND_OPTIMIZATION.md
    QA_AND_REVIEW.md

  04_content_formats/
    CONTENT_FORMATS_OVERVIEW.md
    FORMAT_DIALOG_MINISERIES.md
    FORMAT_ATMOSPHERIC_VIDEO.md
    FORMAT_DIALOG_CAROUSEL.md
    FORMAT_EXPLAINER_CAROUSEL.md
    FORMAT_TEXT_SOCIAL_POSTS.md
    FORMAT_PINTEREST_PINS.md

  05_product_design/
    USER_WORKFLOWS.md
    WEB_UI_SPEC.md
    DASHBOARD_SPEC.md
    PROJECT_SETTINGS_SPEC.md

  06_agents/
    AGENT_RULES.md
    TASK_PROMPT_TEMPLATES.md

  07_projects/
    {project_slug}/
      PROJECT_PROFILE.md
      CONTENT_STRATEGY.md
      VISUAL_GUIDELINES.md
      TONE_OF_VOICE.md
      CTA_LIBRARY.md
      PROMPT_LIBRARY.md
      CONTENT_PLAN_30D.md

  CHANGELOG.md
```

---

## 5. Документы первой очереди

1. `docs/00_index.md` — карта документации, порядок чтения, источники истины, правила обновления.
2. `docs/01_platform/PLATFORM_OVERVIEW.md` — что такое Content Plant как отдельная мультипроектная платформа.
3. `docs/01_platform/PRODUCT_STRATEGY.md` — стратегия развития: внутренний инструмент сейчас, потенциальный SaaS позже.
4. `docs/01_platform/MVP_SCOPE.md` — границы MVP.
5. `docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md` — модель workspace, project и Brand Profile.
6. `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md` — универсальная бренд-система.
7. `docs/06_agents/AGENT_RULES.md` — правила работы агентов.

---

## 6. Документы второй очереди

1. `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
2. `docs/04_content_formats/FORMAT_DIALOG_MINISERIES.md`
3. `docs/04_content_formats/FORMAT_ATMOSPHERIC_VIDEO.md`
4. `docs/04_content_formats/FORMAT_DIALOG_CAROUSEL.md`
5. `docs/04_content_formats/FORMAT_TEXT_SOCIAL_POSTS.md`
6. `docs/05_product_design/USER_WORKFLOWS.md`
7. `docs/05_product_design/WEB_UI_SPEC.md`

---

## 7. Документы третьей очереди

1. `docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md`
2. `docs/02_platform_architecture/DATA_MODEL.md`
3. `docs/02_platform_architecture/PIPELINES_SPEC.md`
4. `docs/03_modules/TREND_RADAR_SPEC.md`
5. `docs/03_modules/SCENARIO_STUDIO_SPEC.md`
6. `docs/03_modules/ASSET_LIBRARY_SPEC.md`
7. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
8. `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`
9. `docs/03_modules/QA_AND_REVIEW.md`

---

## 8. Проектные документы

Проектные документы находятся внутри:

```text
docs/07_projects/{project_slug}/
```

Каждый проект должен иметь собственный набор документов.

### `{project_slug}`

Каждый проект может иметь собственный набор документов:

- `PROJECT_PROFILE.md`
- `CONTENT_STRATEGY.md`
- `VISUAL_GUIDELINES.md`
- `TONE_OF_VOICE.md`
- `CTA_LIBRARY.md`
- `PROMPT_LIBRARY.md`
- `CONTENT_PLAN_30D.md`

Проектные параметры, офферы, цены, ссылки, tone of voice, визуальные правила и CTA должны храниться только здесь, а не в платформенных документах.

---

## 9. Источники истины

### Для платформенных решений

1. `PLATFORM_OVERVIEW.md`
2. `PRODUCT_STRATEGY.md`
3. `MVP_SCOPE.md`
4. `WORKSPACE_AND_PROJECT_MODEL.md`
5. `SYSTEM_ARCHITECTURE.md`
6. `DATA_MODEL.md`

### Для брендовых решений

1. `BRAND_SYSTEM_SPEC.md`
2. `docs/07_projects/{project_slug}/PROJECT_PROFILE.md`
3. `docs/07_projects/{project_slug}/VISUAL_GUIDELINES.md`
4. `docs/07_projects/{project_slug}/TONE_OF_VOICE.md`
5. `docs/07_projects/{project_slug}/CTA_LIBRARY.md`
6. `projects/{project_id}/project.yaml`

### Для контентных решений

1. `CONTENT_FORMATS_OVERVIEW.md`
2. соответствующий `FORMAT_*.md`
3. `docs/07_projects/{project_slug}/CONTENT_STRATEGY.md`
4. `docs/07_projects/{project_slug}/PROMPT_LIBRARY.md`
5. `projects/{project_id}/project.yaml`

---

## 10. Правила для агентов

### 10.1. Hybrid project-specific source of truth

Для project-specific source of truth используется **hybrid model**:

- `docs/07_projects/{project_slug}/` хранит project-level documentation:
  - strategy;
  - brand rules;
  - content rules;
  - tone;
  - positioning;
- `projects/{project_id}/project.yaml` хранит machine-readable settings for code.

Platform-level code и platform-level docs не должны содержать project-specific hardcode.

Перед началом любой задачи агент обязан:

1. Прочитать `docs/00_index.md`.
2. Прочитать `docs/01_platform/MVP_SCOPE.md`.
3. Прочитать `docs/06_agents/AGENT_RULES.md`.
4. Прочитать документы, относящиеся к конкретной задаче.
5. Проверить, не противоречит ли задача существующей документации.
6. Если задача требует изменения архитектуры, сначала предложить обновление документации.
7. После выполнения задачи обновить `CHANGELOG.md`.

Агент не должен:

- зашивать платформу только под конкретный проект;
- добавлять SaaS-функции в MVP без явного решения;
- менять модель данных без обновления `DATA_MODEL.md`;
- добавлять новый формат без обновления `CONTENT_FORMATS_OVERVIEW.md` и соответствующего `FORMAT_*.md`;
- менять брендовые правила проекта без обновления проектных документов;
- смешивать ассеты, сценарии и аналитику разных проектов.

---

## 11. Базовый принцип мультипроектности

Content Plant должен поддерживать несколько проектов.

Каждый проект имеет собственные:

- Brand Profile;
- Content Strategy;
- Visual Guidelines;
- Tone of Voice;
- CTA Library;
- Prompt Library;
- Asset Library;
- Scenarios;
- Publications;
- Analytics.

Общие для платформы:

- production engine;
- content formats;
- trend radar;
- scenario studio;
- publishing hub;
- analytics engine;
- QA engine.

---

## 12. MVP principles

MVP должен быть достаточно универсальным, чтобы поддерживать несколько внутренних проектов, но не должен становиться полноценным SaaS.

### В MVP допускается

- несколько проектов;
- переключение между проектами;
- проектные настройки;
- Brand Profile;
- отдельные ассеты по проектам;
- отдельные сценарии по проектам;
- отдельные публикационные пакеты;
- базовая аналитика по проектам.

### В MVP не входит

- публичная регистрация пользователей;
- тарифы;
- биллинг;
- команды;
- роли доступа;
- клиентский onboarding;
- маркетплейс шаблонов;
- публичный лендинг Content Plant;
- полноценная SaaS-инфраструктура.

---

## 13. First validation project

A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`.

Платформенные документы не должны содержать project-specific цены, URL, CTA, персонажей, офферы, тексты, визуальные правила или product logic.

---

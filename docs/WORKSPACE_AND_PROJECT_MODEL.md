# Workspace and Project Model

## 1. Назначение документа

Этот документ описывает модель мультипроектности платформы **Content Plant**.

Он фиксирует:

- что такое Workspace;
- что такое Project;
- что такое Brand Profile;
- как разделяются данные между проектами;
- какие сущности принадлежат проекту;
- какие сущности являются общими для платформы;
- что входит в MVP;
- что откладывается до SaaS-версии.

Документ является источником истины для проектирования мультипроектной архитектуры.

---

## 2. Главная идея модели

Content Plant должен проектироваться как платформа, которая может обслуживать несколько проектов и брендов.

A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`. Архитектура не должна быть зашита под конкретный проект.

Базовая модель:

```text
Workspace
  └── Project
        ├── Brand Profile
        ├── Content Strategy
        ├── Asset Library
        ├── Ideas
        ├── Scenarios
        ├── Content Items
        ├── Publications
        └── Analytics
```

В MVP Workspace может быть один внутренний, но Project должен быть полноценной сущностью уже на первом этапе.

---

## 3. Почему нужна такая модель

Модель Workspace / Project нужна по нескольким причинам.

### 3.1. Чтобы не зашить систему под один проект

Content Plant должен быть пригоден для разных направлений:

- Astra Insight;
- будущие продукты владельца;
- экспериментальные контентные проекты;
- клиентские бренды;
- потенциальные SaaS-пользователи.

Если проектная модель не заложена сразу, позже придётся переделывать данные, интерфейс, ассеты, шаблоны и аналитику.

### 3.2. Чтобы переиспользовать форматы

Один и тот же формат должен работать для разных проектов.

Например:

```text
Dialog Miniseries
```

может быть:

- диалоговый мини-сериал для одного проекта;
- “Диалог ученика и наставника” для образовательного проекта;
- “Диалог клиента и консультанта” для e-commerce;
- “Диалог предпринимателя и эксперта” для B2B.

Формат остаётся общим, но поведение и стиль задаются проектом.

### 3.3. Чтобы хранить разные бренды отдельно

У разных проектов будут разные:

- цвета;
- шрифты;
- визуальные правила;
- персонажи;
- tone of voice;
- CTA;
- продукты;
- платформы;
- ссылки;
- аналитика.

Их нельзя смешивать.

---

## 4. Workspace

**Workspace** — это верхний контейнер, внутри которого находятся проекты.

На MVP Workspace может быть один:

```text
Workspace: internal
```

В будущем SaaS-версии Workspace может соответствовать:

- отдельному пользователю;
- компании;
- агентству;
- команде;
- клиентскому аккаунту.

---

## 5. Workspace в MVP

На этапе MVP не требуется сложная модель Workspace.

Достаточно одного внутреннего workspace:

```json
{
  "workspace_id": "internal",
  "name": "Internal Workspace",
  "type": "internal",
  "status": "active"
}
```

В MVP не нужны:

- публичная регистрация;
- несколько владельцев workspace;
- команды;
- роли;
- permissions;
- тарифы;
- биллинг.

Но архитектура должна позволять добавить эти функции позже.

---

## 6. Project

**Project** — это отдельный бренд, продукт или контентное направление внутри Workspace.

Project является ключевой сущностью MVP.

Каждый Project должен иметь собственные:

- настройки;
- Brand Profile;
- ассеты;
- идеи;
- сценарии;
- публикации;
- аналитику;
- платформы;
- UTM-настройки.

Примеры проектов:

```text
example_project
astra
future_product
client_brand
```

---

## 7. Project в MVP

На MVP Project должен поддерживать минимальную, но полноценную модель.

Минимальные поля:

```json
{
  "project_id": "project_example",
  "workspace_id": "internal",
  "slug": "example_project",
  "name": "Demo Project",
  "description": "Short description of the project.",
  "status": "active",
  "default_language": "ru",
  "primary_url": "https://example.com",
  "target_platforms": ["tiktok", "instagram", "youtube_shorts", "telegram", "vk", "pinterest"],
  "created_at": "2026-07-04T00:00:00Z",
  "updated_at": "2026-07-04T00:00:00Z"
}
```

---

## 8. Project slug

Каждый проект должен иметь стабильный `slug`.

Требования:

- lowercase;
- латиница;
- без пробелов;
- короткий;
- не менять после создания без миграции.

Примеры:

```text
example_project
astra
content_plant_demo
client_brand
```

Slug используется в:

- путях файлов;
- id;
- export packages;
- UTM;
- analytics;
- routing;
- папках ассетов.

Пример пути:

```text
storage/projects/{project_slug}/assets/
storage/projects/{project_slug}/renders/
storage/projects/{project_slug}/exports/
```

---

## 9. Brand Profile

**Brand Profile** — это проектная конфигурация, которая задаёт, как Content Plant должен создавать контент для конкретного проекта.

Brand Profile отвечает за кастомизацию универсальных форматов.

Он должен включать:

- бренд;
- аудиторию;
- позиционирование;
- tone of voice;
- визуальные правила;
- цвета;
- шрифты;
- CTA;
- запреты;
- продуктовые офферы;
- ссылки;
- платформенные настройки.

Brand Profile не является глобальным.  
Он принадлежит конкретному Project.

---

## 10. Минимальная структура Brand Profile

Для MVP достаточно такой структуры:

```json
{
  "brand_profile_id": "brand_example",
  "project_id": "project_example",
  "brand_name": "Example Brand",
  "positioning": "Soft AI self-understanding tool.",
  "audience": "Women interested in self-understanding, relationships, inner patterns and symbolic tools.",
  "tone_of_voice": {
    "style": "soft, warm, clear, non-judgmental",
    "avoid": ["hard predictions", "fear-based claims", "medical or therapeutic promises"]
  },
  "visual_style": {
    "description": "light premium, warm, calm, modern",
    "colors": {
      "background": "#EFEEE9",
      "text": "#1A1A1A",
      "accent_gold": "#C2A476",
      "accent_terracotta": "#B8743F",
      "accent_green": "#6B8068"
    },
    "fonts": {
      "primary": "Manrope",
      "secondary": "Playfair Display"
    }
  },
  "cta": [
    "Open the next step",
    "Open the primary offer",
    "Learn more"
  ],
  "links": {
    "primary": "https://example.com"
  }
}
```

Это пример для конкретного проекта.  
Общая структура Brand Profile описывается в `BRAND_SYSTEM_SPEC.md`.

---

## 11. Project Profile

**Project Profile** шире, чем Brand Profile.

Project Profile описывает сам проект как продукт или бизнес-направление.

Он должен включать:

- название;
- описание;
- продуктовую модель;
- аудиторию;
- офферы;
- цены;
- воронку;
- платформы;
- статус;
- ключевые цели.

Пример для конкретного проекта:

```json
{
  "project_name": "Example Brand",
  "business_model": {
    "primary_offer": {
      "name": "Primary Offer",
      "price": "{price}",
      "currency": "RUB"
    },
    "recurring_offer": {
      "name": "Recurring Offer",
      "price": "{recurring_price}",
      "currency": "RUB",
      "period": "month"
    }
  },
  "funnel": {
    "traffic": ["tiktok", "instagram", "youtube_shorts", "pinterest"],
    "main_entry": "website",
    "secondary_entry": "telegram",
    "conversion": "purchase"
  }
}
```

---

## 12. Разница между Project Profile и Brand Profile

| Сущность | Отвечает на вопрос | Пример |
|---|---|---|
| Project Profile | Что это за проект и как он монетизируется? | Demo Project продаёт primary offer и может иметь recurring offer |
| Brand Profile | Как этот проект должен звучать и выглядеть? | Светлый премиальный стиль, мягкий тон, брендовый персонаж |
| Content Strategy | Какой контент производить? | Мини-сериалы, атмосферные видео, карусели |
| Format Spec | Как устроен универсальный формат? | Dialog Miniseries: 3–5 сцен, 9:16, реплики, CTA |

---

## 13. Project-level entities

Следующие сущности должны быть привязаны к Project.

### 13.1. Ideas

Идеи не должны быть глобальными.

Каждая идея принадлежит проекту:

```json
{
  "idea_id": "idea_001",
  "project_id": "project_example",
  "title": "Example content idea",
  "status": "approved"
}
```

---

### 13.2. Scenarios

Сценарий создаётся под конкретный проект и учитывает его Brand Profile.

```json
{
  "scenario_id": "scenario_001",
  "project_id": "project_example",
  "content_type": "dialog_miniseries",
  "title": "Example content idea"
}
```

---

### 13.3. Assets

Ассеты принадлежат проекту.

```json
{
  "asset_id": "asset_001",
  "project_id": "project_example",
  "type": "image",
  "file_path": "storage/projects/{project_slug}/assets/image_001.png"
}
```

Ассеты разных проектов не должны смешиваться.

---

### 13.4. Content Items

Content Item — это готовая или почти готовая единица контента.

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "content_type": "dialog_miniseries",
  "status": "ready"
}
```

---

### 13.5. Publications

Publication — это размещение content item на конкретной платформе.

```json
{
  "publication_id": "pub_001",
  "project_id": "project_example",
  "content_id": "content_001",
  "platform": "instagram",
  "status": "scheduled"
}
```

---

### 13.6. Metrics

Метрики привязаны к публикации и проекту.

```json
{
  "metric_id": "metric_001",
  "project_id": "project_example",
  "publication_id": "pub_001",
  "views": 12000,
  "clicks": 84,
  "purchases": 3
}
```

---

## 14. Platform-level entities

Некоторые сущности являются общими для платформы.

### 14.1. Content Formats

Форматы контента универсальны.

Примеры:

- dialog_miniseries;
- atmospheric_video;
- dialog_carousel;
- explainer_carousel;
- text_social_post;
- pinterest_pin.

Они не должны быть зашиты под конкретный проект.

---

### 14.2. Production Templates

Production templates могут быть общими, но должны принимать проектные настройки.

Пример:

```text
template_dialog_miniseries_light
```

может использоваться разными проектами, если поддерживает:

- цвета из Brand Profile;
- шрифты из Brand Profile;
- логотип проекта;
- CTA проекта;
- tone of voice на уровне сценария.

---

### 14.3. Modules

Общие модули платформы:

- Trend Radar;
- Scenario Studio;
- Asset Library;
- Production Engine;
- Publishing Hub;
- Analytics;
- QA.

Эти модули должны работать с любым Project.

---

## 15. Разделение данных

Главное правило:

> Все данные, которые относятся к конкретному проекту, должны иметь `project_id`.

Это относится к:

- идеям;
- сценариям;
- сценам;
- ассетам;
- готовому контенту;
- публикациям;
- метрикам;
- CTA;
- prompt templates project-level;
- platform settings.

Без `project_id` допускаются только глобальные справочники и универсальные шаблоны.

---

## 16. Структура хранения файлов

Рекомендуемая структура:

```text
storage/
  workspaces/
    internal/
      projects/
        example_project/
          assets/
            images/
            videos/
            audio/
            logos/
          scenarios/
          renders/
          exports/
          analytics/
        astra/
          assets/
          scenarios/
          renders/
          exports/
          analytics/
```

Для MVP допускается упрощённая структура:

```text
storage/
  projects/
    example_project/
      assets/
      renders/
      exports/
    astra/
      assets/
      renders/
      exports/
```

Главное: не хранить все ассеты в одной общей куче без project separation.

---

## 17. Project Settings

Каждый проект должен иметь настройки.

Минимальные настройки:

- project name;
- project slug;
- language;
- primary URL;
- active platforms;
- default CTA;
- default UTM campaign;
- timezone;
- brand profile;
- export settings.

Пример:

```json
{
  "project_id": "project_example",
  "settings": {
    "language": "ru",
    "timezone": "Europe/Moscow",
    "primary_url": "https://example.com",
    "active_platforms": ["tiktok", "instagram", "youtube_shorts", "telegram", "vk", "pinterest"],
    "default_utm_campaign": "example_campaign"
  }
}
```

---

## 18. Platform Accounts

Platform Accounts описывают аккаунты социальных сетей.

В MVP можно хранить просто настройки и ссылки.

Пример:

```json
{
  "platform_account_id": "pa_example_instagram",
  "project_id": "project_example",
  "platform": "instagram",
  "handle": "example.brand",
  "profile_url": "https://instagram.com/example.brand",
  "posting_mode": "manual_export"
}
```

Типы posting mode:

```text
manual_export
semi_auto
auto_api
disabled
```

На MVP большинство платформ могут быть в режиме `manual_export`.

---

## 19. UTM Model

Каждый проект должен иметь собственную UTM-логику.

Базовый формат:

```text
utm_source={platform}
utm_medium=organic
utm_campaign={project_slug}_{content_series}
utm_content={content_id}
```

Пример для конкретного проекта:

```text
utm_source=tiktok
utm_medium=organic
utm_campaign=dialog_miniseries_s01
utm_content=content_001
```

UTM должен связывать публикации с аналитикой сайта и продажами.

---

## 20. Project switcher

В интерфейсе должен быть Project Switcher.

Задачи:

- показывать активный проект;
- позволять переключаться между проектами;
- не смешивать данные разных проектов;
- применять Brand Profile активного проекта ко всем действиям.

Пример:

```text
Active project: Demo Project
Switch project: Astra Insight / Future Project
```

После переключения проекта должны меняться:

- идеи;
- сценарии;
- ассеты;
- публикации;
- аналитика;
- настройки бренда.

---

## 21. Создание нового проекта

На MVP процесс может быть простым.

Минимальный flow:

1. Пользователь нажимает “Create Project”.
2. Вводит название.
3. Вводит slug.
4. Выбирает язык.
5. Указывает основной сайт.
6. Выбирает платформы.
7. Заполняет базовый Brand Profile.
8. Сохраняет проект.

После этого можно:

- создавать идеи;
- генерировать сценарии;
- загружать ассеты;
- собирать контент.

---

## 22. Project templates

В MVP project templates не обязательны, но архитектурно возможны.

Будущие шаблоны:

- personal brand;
- AI product;
- e-commerce;
- expert / coach;
- education;
- media;
- local business.

Шаблон может предзаполнять:

- content formats;
- default platforms;
- CTA examples;
- prompt templates;
- analytics goals.

Но в MVP достаточно ручного создания проекта.

---

## 23. Project-level Prompt Library

У каждого проекта может быть своя библиотека промтов.

Пример:

```text
docs/07_projects/{project_slug}/PROMPT_LIBRARY.md
```

или в базе:

```json
{
  "prompt_template_id": "prompt_dialog_miniseries",
  "project_id": "project_example",
  "format": "dialog_miniseries",
  "template": "..."
}
```

Scenario Studio должен использовать:

1. универсальный prompt template формата;
2. Brand Profile проекта;
3. проектную Prompt Library, если она есть.

---

## 24. Project-level CTA Library

CTA должны быть проектными.

Пример для конкретного проекта:

- “Open the next step”
- “Open the primary offer”
- “Learn more”
- “Primary offer — {price}”

Для другого проекта CTA будут другими.

CTA не должны быть глобально зашиты в шаблон.

---

## 25. Project-level Analytics

Аналитика должна быть доступна:

- по проекту;
- по платформе;
- по формату;
- по теме;
- по CTA;
- по публикации.

Нельзя смешивать метрики разных проектов.

Пример offerа:

```text
Project: Example Project
Format: Dialog Miniseries
Period: last 7 days

Views: 84,000
Clicks: 412
Purchases: 19
Revenue: 16,910 RUB
```

---

## 26. MVP vs Future SaaS

### 26.1. MVP

В MVP:

- один workspace;
- несколько внутренних projects;
- один внутренний пользователь;
- простая проектная модель;
- базовый Brand Profile;
- manual export;
- ручной или CSV импорт метрик.

### 26.2. Future SaaS

В SaaS-версии:

- много workspaces;
- много пользователей;
- команды;
- роли;
- права доступа;
- тарифы;
- биллинг;
- onboarding;
- приглашения;
- лимиты;
- project templates.

Важно: SaaS-функции не должны реализовываться в MVP, но модель не должна блокировать их появление.

---

## 27. Минимальные требования к базе данных

Все проектные таблицы должны содержать:

```text
project_id
created_at
updated_at
status
```

Для SaaS-готовности желательно также предусмотреть:

```text
workspace_id
created_by
updated_by
```

Даже если `created_by` пока не используется.

---

## 28. Ошибки, которых нужно избегать

### 28.1. Глобальная папка ассетов без проектов

Плохо:

```text
assets/
  image_001.png
  image_002.png
```

Хорошо:

```text
projects/{project_slug}/assets/image_001.png
projects/astra/assets/image_001.png
```

---

### 28.2. Глобальные CTA без проекта

Плохо:

```json
{
  "cta": "Open the next step"
}
```

Хорошо:

```json
{
  "project_id": "project_example",
  "cta": "Open the next step"
}
```

---

### 28.3. Хардкод конкретного бренда в production template

Плохо:

```text
render_dialog_miniseries_video()
```

Хорошо:

```text
render_dialog_miniseries(project_id, scenario_id, template_id)
```

---

### 28.4. Общая аналитика без project_id

Плохо:

```json
{
  "views": 10000,
  "clicks": 100
}
```

Хорошо:

```json
{
  "project_id": "project_example",
  "content_id": "content_001",
  "views": 10000,
  "clicks": 100
}
```

---

## 29. Критерии готовности Project Model MVP

Project Model считается готовой, если:

- можно создать проект;
- можно выбрать активный проект;
- у проекта есть slug;
- у проекта есть Brand Profile;
- идеи привязаны к проекту;
- сценарии привязаны к проекту;
- ассеты привязаны к проекту;
- рендеры привязаны к проекту;
- публикации привязаны к проекту;
- метрики привязаны к проекту;
- переключение проекта меняет видимые данные;
- в коде нет жёсткой привязки к конкретному бренду.

---

## 30. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant  
Первый validation project: задаётся отдельно в docs/07_projects/{project_slug}/

---

## 31. Следующие документы

После этого документа необходимо создать:

1. `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`
2. `docs/06_agents/AGENT_RULES.md`
3. `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
4. `docs/05_product_design/PROJECT_SETTINGS_SPEC.md`

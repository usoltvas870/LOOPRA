# Workspace and Project Model

## 1. Назначение документа

Этот документ описывает модель мультипроектности платформы **LOOPRA**.

Он фиксирует:

- что такое `Workspace`;
- что такое `Project`;
- что такое `Brand Profile`;
- как разделяются platform-level и project-level сущности;
- как должен выглядеть project-scoped storage;
- какие правила обязательны уже в current foundation MVP.

Документ является platform-level и должен оставаться project-agnostic.

---

## 2. Главная идея модели

LOOPRA должен проектироваться как платформа, которая может обслуживать несколько проектов без смешивания данных и без project-specific hardcode.

Главный принцип:

> Всё, что относится к конкретному проекту, должно быть project-scoped и отделено от platform-level foundation.

Это включает:

- content entities;
- brand rules;
- CTA;
- prompts;
- publications;
- metrics;
- runtime assets.

---

## 3. Core Structure

Базовая модель:

```text
Workspace
  └── Project
        ├── Brand Profile
        ├── Ideas
        ├── Scenarios
        ├── Content Items
        ├── Export Packages
        ├── Publications
        └── Metric Snapshots
```

В current foundation MVP `Workspace` может быть один внутренний, но `Project` уже должен быть полноценной сущностью.

---

## 4. Why The Model Is Required

Эта модель нужна, чтобы:

1. не зашить систему под один проект;
2. отделить project-specific docs и config от platform baseline;
3. повторно использовать shared workflows;
4. сохранять project-specific assets и metrics без смешивания;
5. упростить future validation на разных проектах.

Нейтральные project examples:

- `example_project`
- `education_project`
- `wellness_app`
- `client_brand`

---

## 5. Workspace

`Workspace` — верхний контейнер для проектов.

### 5.1. MVP shape

В текущем MVP допустим один internal workspace:

```json
{
  "workspace_id": "internal",
  "name": "Internal Workspace",
  "type": "internal",
  "status": "active"
}
```

### 5.2. Current constraint

Current foundation MVP не требует:

- public registration;
- multiple owners;
- teams;
- roles;
- billing;
- workspace invitations.

---

## 6. Project

`Project` — это отдельный бренд, продукт, контентное направление или validation target внутри workspace.

Каждый `Project` должен иметь собственные:

- settings;
- `Brand Profile`;
- ideas;
- scenarios;
- content items;
- export packages;
- publications;
- metric snapshots.

### 6.1. Neutral examples

```text
example_project
education_project
wellness_app
client_brand
```

### 6.2. Minimal fields

```json
{
  "project_id": "project_example",
  "workspace_id": "internal",
  "slug": "example_project",
  "name": "Example Project",
  "description": "Short project description.",
  "status": "active",
  "default_language": "ru",
  "primary_url": "https://example.com",
  "target_platforms": ["telegram", "threads", "vk"],
  "created_at": "2026-07-07T00:00:00Z",
  "updated_at": "2026-07-07T00:00:00Z"
}
```

---

## 7. Project Slug

Каждый проект должен иметь стабильный `slug`.

Требования:

- lowercase;
- latin characters;
- no spaces;
- stable after creation unless migration is intentional;
- unique within workspace.

Примеры:

```text
example_project
education_project
client_brand
```

`slug` используется в:

- filesystem paths;
- export paths;
- project runtime storage;
- analytics grouping;
- stable references.

---

## 8. Brand Profile

`Brand Profile` — project-scoped configuration, которая определяет, как платформа должна формировать контент для конкретного проекта.

Он задаёт:

- brand name;
- positioning;
- audience summary;
- tone of voice;
- visual constraints;
- CTA;
- links;
- allowed/forbidden topics;
- platform preferences.

### 8.1. Neutral example

```json
{
  "brand_profile_id": "brand_example",
  "project_id": "project_example",
  "brand_name": "Example Brand",
  "positioning": "Clear and practical content brand.",
  "audience": "Teams and creators who need repeatable content workflows.",
  "tone_of_voice": {
    "style": "clear, calm, helpful",
    "avoid": ["fear-based claims", "hard guarantees"]
  },
  "visual_style": {
    "description": "clean, modern, readable"
  },
  "cta": [
    "Learn more",
    "Open the next step"
  ],
  "links": {
    "primary": "https://example.com"
  }
}
```

Общая структура `Brand Profile` должна быть универсальной, а конкретное содержимое — project-scoped.

---

## 9. Project Profile vs Brand Profile

`Project Profile` отвечает на вопрос:

```text
What is this project and how does it operate?
```

`Brand Profile` отвечает на вопрос:

```text
How should this project sound and appear in content?
```

Project-level truth хранится в:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/project.yaml
```

---

## 10. Project-Level Entities

Следующие сущности должны быть project-scoped:

- `Idea`
- `Scenario`
- `ContentItem`
- `ExportPackage`
- `Publication`
- `MetricSnapshot`
- CTA
- project prompts
- project assets

Нормативное правило:

> Если сущность относится к конкретному проекту, она должна иметь `project_id`.

---

## 11. Platform-Level Entities

Platform-level остаются только общие abstractions:

- `Workspace`
- content format definitions
- shared lifecycle rules
- platform dictionaries
- generic package validation rules

Platform-level сущности не должны включать project-specific values.

---

## 12. Storage Separation

Рекомендуемая project-scoped storage structure:

```text
storage/
  projects/
    {project_slug}/
      assets/
      renders/
      exports/
      analytics/
```

Для runtime smoke data допустим отдельный локальный путь:

```text
storage/smoke_projects/{project_slug}/...
```

Главное правило:

> Нельзя хранить project-specific assets и runtime outputs в общей куче без project separation.

---

## 13. Export And Runtime Artifacts

`ExportPackage` и runtime artifacts должны оставаться project-scoped.

В current foundation это особенно важно для:

- `ExportPackage v1`
- manual publication record workflow
- local smoke runtime artifacts
- manual metrics workflow helpers

Generated/runtime artifacts:

- локальные;
- не являются foundation source files;
- не должны коммититься.

---

## 14. Project Settings

Минимальные project settings могут включать:

- project name;
- slug;
- language;
- primary URL;
- active platforms;
- timezone;
- default CTA;
- export settings.

Нейтральный пример:

```json
{
  "project_id": "project_example",
  "settings": {
    "language": "ru",
    "timezone": "Europe/Moscow",
    "primary_url": "https://example.com",
    "active_platforms": ["telegram", "threads", "vk"],
    "default_utm_campaign": "example_campaign"
  }
}
```

---

## 15. Project Switcher

Если later появляется интерфейс, `Project Switcher` должен:

- показывать активный проект;
- разделять данные по проектам;
- применять `Brand Profile` активного проекта;
- не смешивать идеи, публикации и метрики разных проектов.

Нейтральный пример:

```text
Active project: Example Project
Switch project: Education Project / Client Brand
```

Но current foundation MVP не требует UI-реализации этого слоя.

---

## 16. UTM And Publication Context

Каждый проект может иметь свою UTM-логику и publication context, но это должно оставаться project-scoped.

Нейтральный пример:

```text
utm_source={platform}
utm_medium=organic
utm_campaign={project_slug}_{content_series}
utm_content={content_id}
```

Это правило совместимо с export-first/manual-publication-first foundation.

---

## 17. Validation Project Boundary

Validation project может существовать, но он должен подключаться поверх этой модели, а не менять её основу.

То есть:

- platform model generic;
- project docs specific;
- project config specific;
- validation real-world;
- foundation baseline neutral.

---

## 18. Common Mistakes To Avoid

### 18.1. Shared asset pile without project separation

Плохо:

```text
assets/
  image_001.png
  image_002.png
```

Хорошо:

```text
storage/projects/{project_slug}/assets/image_001.png
```

### 18.2. Global CTA without project scope

Плохо:

```json
{
  "cta": "Learn more"
}
```

Хорошо:

```json
{
  "project_id": "project_example",
  "cta": "Learn more"
}
```

### 18.3. Foundation docs carrying project assumptions

Плохо:

```text
platform docs define a specific brand persona or project content style
```

Хорошо:

```text
platform docs define generic structure; project docs define project specifics
```

---

## 19. Readiness Criteria For Current Model

Current project model считается согласованным, если:

- проект можно идентифицировать через `project_id` и `slug`;
- project data не смешиваются;
- `Brand Profile` остаётся project-scoped;
- export packages и manual publication records project-scoped;
- metric snapshots project-scoped;
- platform docs не зашиты под конкретный проект.

---

## 20. Статус документа

Статус: Draft  
Версия: 0.2  
Дата обновления: 2026-07-08  
Проект: LOOPRA  
Validation boundary: project-specific validation lives outside platform baseline

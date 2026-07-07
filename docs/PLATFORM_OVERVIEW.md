# Platform Overview

## 1. Назначение документа

Этот документ описывает платформу **Content Plant** на верхнем уровне.

Он фиксирует:

- что такое Content Plant;
- какую проблему решает платформа;
- почему она должна оставаться мультипроектной и project-agnostic;
- какой foundation MVP зафиксирован сейчас;
- какие границы нельзя нарушать;
- как соотносятся platform layer и project layer.

Документ является одним из основных platform-level источников истины.

---

## 2. Что такое Content Plant

**Content Plant** — это standalone мультипроектная платформа для системного производства, упаковки, ручной публикации и базовой аналитики контента.

Платформа должна помогать превращать:

```text
Idea
→ Scenario
→ ContentItem
→ ExportPackage
→ Manual Publication Record
→ MetricSnapshot
```

в управляемый и воспроизводимый контентный цикл.

Content Plant не должен быть зашит под один бренд, один продукт, одну нишу или один набор примеров. Все project-specific правила должны жить только в project layer.

---

## 3. Основная проблема

Даже у небольших команд и внутренних продуктов контентный цикл часто остаётся фрагментированным:

- идеи хранятся отдельно;
- сценарии и тексты создаются вручную без общей структуры;
- публикационные материалы собираются несистемно;
- публикации фиксируются вручную;
- метрики теряются или не связываются с исходным контентом.

Content Plant нужен как нейтральный foundation, который задаёт единый контур:

```text
project-scoped content production
without project-specific hardcode
and without early SaaS complexity
```

---

## 4. Project-Agnostic Principle

Главный platform-level принцип:

> Foundation должен быть универсальным, а project-specific поведение должно подключаться через `Project`, `Brand Profile`, project docs и project config.

Это означает:

- platform docs не должны содержать active brand assumptions;
- platform code не должен содержать project-specific templates, CTA, prompts или packages;
- примеры должны быть нейтральными;
- validation project может существовать, но не должен определять foundation baseline.

Разрешённые места для project-specific source of truth:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/project.yaml
```

---

## 5. Current Foundation MVP

Текущий foundation MVP intentionally narrow.

### 5.1. Current implemented loop

```text
Idea
→ Scenario
→ ContentItem
→ ExportPackage v1
→ Manual Publication Record v1
→ MetricSnapshot v1
```

### 5.2. Current safest content format

Текущий safest foundation format:

```text
text_social_post
```

Этот формат выбран как минимальный и безопасный foundation loop, потому что не требует реального render pipeline.

### 5.3. Current workflow shape

Foundation сейчас является:

- export-first;
- manual-publication-first;
- local/filesystem-first;
- manual-metrics-first.

### 5.4. Current dev helpers

Текущий локальный workflow опирается на:

```bash
python scripts/smoke_loop.py
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

---

## 6. Current Platform Modules

В текущем foundation baseline зафиксированы:

- canonical domain layer;
- project services and project config binding;
- `IdeaService`;
- `ScenarioService`;
- `ProductionLifecycleService`;
- `PublishingService`;
- `AnalyticsService`;
- thin `LoopOrchestrator`;
- filesystem-based persistence.

Platform-level ownership:

- `Production Engine` owns `ContentItem` and related production lifecycle concerns;
- `Publishing Hub` owns `ExportPackage`, publication preparation and `Publication`;
- analytics foundation currently records manual metrics into `MetricSnapshot`.

---

## 7. Platform Layer vs Project Layer

### 7.1. Platform layer

Platform layer описывает:

- universal entities;
- neutral workflows;
- shared lifecycle rules;
- generic content formats;
- export/validation mechanics;
- project isolation rules.

### 7.2. Project layer

Project layer описывает:

- positioning;
- offers;
- pricing;
- CTA;
- prompts;
- visual rules;
- tone of voice;
- project-specific examples;
- asset libraries and project-specific strategy.

### 7.3. Neutral examples

Допустимые нейтральные project examples:

- `example_project`
- `wellness_app`
- `education_project`
- `content_brand`
- `client_brand`

---

## 8. Validation Project Boundary

Платформа может позже проверяться на одном или нескольких validation projects, но это не меняет foundation baseline.

Правильный подход:

```text
Platform foundation
→ generic project model
→ project-specific docs/config
→ validation on a concrete project
```

Неправильный подход:

```text
concrete project rules
→ copied into platform docs
→ treated as foundation requirement
```

---

## 9. MVP Boundaries

В текущий foundation MVP не входят:

- API;
- UI;
- database layer или migrations;
- SaaS, billing, users, roles или marketplace;
- autoposting;
- external APIs;
- external analytics APIs;
- `HyperFrames`, FFmpeg flows или `video-assembler/`;
- `Trend Radar`;
- generated insights;
- generated new ideas from metrics;
- project-specific hardcode в platform-level docs или code.

Также важно:

- не смешивать `ContentItem` status и `Publication` status;
- не смешивать Content Analytics и Product Analytics;
- не коммитить generated runtime artifacts и `graphify-out/`.

---

## 10. Long-Term Direction

После стабилизации foundation loop платформа может расширяться:

- дополнительными content formats;
- richer review and QA flows;
- project-level templates;
- broader analytics summaries;
- later SaaS-oriented layers.

Но такие расширения не должны переписывать текущий foundation baseline задним числом.

---

## 11. Main Risks

Главные риски для платформы:

1. Зашить foundation под один конкретный проект.
2. Расширить MVP раньше, чем стабилизирован минимальный loop.
3. Смешать platform docs и project docs.
4. Подменить export-first/manual workflow premature integrations.
5. Трактовать generated/runtime artifacts как source changes.

---

## 12. Success Criteria For Current Foundation

Текущий foundation можно считать platform-ready, когда:

- loop `Idea -> Scenario -> ContentItem -> ExportPackage v1 -> Manual Publication Record v1 -> MetricSnapshot v1` согласован в docs и code;
- платформа остаётся project-agnostic;
- `text_social_post` остаётся минимальным безопасным foundation format;
- export package можно создать, проверить и валидировать локально;
- manual metrics path работает без внешних API;
- project-specific examples не протекают в platform baseline.

---

## 13. Статус документа

Статус: Draft  
Версия: 0.2  
Дата обновления: 2026-07-07  
Проект: Content Plant  
Validation project boundary: project-specific validation lives outside platform baseline

# Product Strategy

## 1. Назначение документа

Этот документ описывает product strategy платформы **Content Plant**.

Он фиксирует:

- зачем создаётся платформа;
- какую ценность должен дать foundation MVP;
- почему мультипроектность важна с первого этапа;
- где проходит граница между foundation, validation и future SaaS;
- какие product principles нельзя нарушать.

Документ должен оставаться platform-level и project-agnostic.

---

## 2. Краткая стратегия

**Content Plant** строится как internal-first, export-first, multi-project foundation для системного контентного цикла.

Текущая стратегия:

1. Сначала стабилизировать нейтральный foundation loop.
2. Не зашивать platform layer под один проект.
3. Проверять foundation на project-specific данных только через project layer.
4. Расширять platform surface только после того, как минимальный loop воспроизводим и проверяем.

---

## 3. Основная стратегическая гипотеза

Главная гипотеза:

> Для небольших команд и внутренних продуктов наибольшую ценность даёт не разрозненный набор AI-функций, а управляемый loop от идеи до публикации и ручно-собранных метрик.

Content Plant должен уменьшать ручной хаос в таких задачах:

- хранение идей;
- подготовка сценариев;
- формирование publication-ready package;
- фиксация ручной публикации;
- связка публикации с метриками.

---

## 4. Почему продукт нужен

Во многих командах контентный процесс распадается на отдельные несвязанные шаги:

- идея существует отдельно от сценария;
- сценарий отдельно от готового package;
- публикация отдельно от source content;
- метрики отдельно от publication record;
- lessons learned не сохраняются в общей системе.

Product strategy Content Plant состоит в том, чтобы собрать эти шаги в единый и нейтральный operational loop.

---

## 5. Two Horizons Strategy

### 5.1. Horizon 1: Foundation MVP

Current priority — не широкий SaaS, а практичный foundation MVP.

Текущий scope:

```text
Idea
→ Scenario
→ ContentItem
→ ExportPackage v1
→ Manual Publication Record v1
→ MetricSnapshot v1
```

Current characteristics:

- manual-publication-first;
- export-first;
- no API/UI dependency;
- no external analytics APIs;
- no autoposting;
- no generated insights/new ideas from metrics.

### 5.2. Horizon 2: Validation Through Project Layer

После стабилизации foundation платформа может проверяться на одном или нескольких validation projects.

Ключевое ограничение:

> Validation project проверяет foundation, но не становится foundation baseline.

### 5.3. Horizon 3: Possible SaaS Expansion

Только после доказанной полезности foundation можно рассматривать:

- broader onboarding;
- multi-user workspace logic;
- richer project templates;
- public product layers;
- future external integrations.

Но такие решения не должны просачиваться в current MVP requirements.

---

## 6. Role Of A Validation Project

Validation project useful only as a proving ground.

Он может:

- дать реальные сценарии использования;
- выявить missing abstractions;
- проверить reproducibility export workflow;
- показать, какие project settings должны жить в project layer.

Он не должен:

- задавать platform naming;
- определять platform content types;
- становиться обязательным example set;
- переносить свои CTA, prompts, offers или visual assumptions в platform docs.

---

## 7. Multi-Project Strategy

Мультипроектность нужна не как early SaaS feature, а как защита foundation architecture.

Она нужна, чтобы:

- не смешивать project data;
- не зашивать brand rules в shared templates;
- повторно использовать formats и workflows;
- облегчить future validation на разных project profiles.

Нейтральные project examples:

- `example_project`
- `wellness_app`
- `education_project`
- `client_brand`

---

## 8. Product Positioning

На текущем этапе позиционирование такое:

> Content Plant — это operational foundation для мультипроектного контентного цикла, а не публичный SaaS и не autoposting tool.

Важно не позиционировать систему как:

- universal social autoposter;
- AI media generator by default;
- public marketplace product в текущем MVP;
- dashboard-first систему без production loop.

---

## 9. Brand Profile As Strategy Boundary

`Brand Profile` — ключевой product mechanism для универсальности платформы.

Именно через него project layer должен определять:

- tone of voice;
- CTA;
- links;
- visual constraints;
- allowed/forbidden topics;
- platform preferences.

Это позволяет одному platform workflow работать для разных проектов без hardcode.

---

## 10. Current MVP Strategy

Текущий MVP intentionally narrow and disciplined.

### 10.1. Current safest format

```text
text_social_post
```

### 10.2. Why this format first

- quickest to validate end-to-end loop;
- не требует real render stack;
- совместим с manual publication;
- позволяет проверить package inspection/validation;
- позволяет проверить manual metric import path.

### 10.3. What current MVP proves

Current MVP должен доказать, что foundation умеет:

- хранить project-scoped ideas;
- превращать их в `Scenario`;
- выпускать `ContentItem`;
- готовить `ExportPackage v1`;
- хранить `Publication` как manual publication record;
- записывать `MetricSnapshot` вручную;
- оставаться project-agnostic.

---

## 11. What Is Explicitly Out Of Scope

В current foundation MVP не входят:

- API;
- UI;
- database migrations;
- billing;
- users/roles/teams;
- marketplace;
- autoposting;
- external APIs;
- external analytics APIs;
- `Trend Radar`;
- FFmpeg flows, `HyperFrames`, `video-assembler/`;
- generated insights;
- generated new ideas from metrics.

---

## 12. Strategic Risks

### 12.1. Brand Lock-In

Риск:

```text
project-specific examples become platform requirements
```

Решение:

- neutral platform docs;
- project-specific docs only in `docs/07_projects/{project_slug}/`;
- machine-readable project-specific config only in `projects/{project_id}/project.yaml`.

### 12.2. Premature Scope Expansion

Риск:

```text
foundation loop expands before minimal path is stable
```

Решение:

- keep current loop narrow;
- protect export-first/manual-publication-first flow;
- treat future features as future, not as hidden MVP requirements.

### 12.3. Documentation Drift

Риск:

```text
platform docs describe a broader or different MVP than code/state
```

Решение:

- keep docs aligned with current foundation baseline;
- explicitly distinguish current implementation from future direction.

---

## 13. Product Principles

1. `Project-agnostic foundation first`
2. `Project-specific behavior lives in project layer`
3. `Export first, autopost later`
4. `Manual publication before external integrations`
5. `Manual metrics before analytics automation`
6. `Vertical slice before feature breadth`
7. `Documentation must match the real foundation baseline`

---

## 14. Foundation Success Criteria

Текущий foundation strategy считается успешной, если:

- minimal loop works end-to-end locally;
- platform stays reusable across projects;
- docs no longer depend on project-specific assumptions;
- export package and manual metrics workflow are first-class;
- future expansion remains possible without rewriting the baseline.

---

## 15. Next Strategic Step

После docs cleanup логичный следующий шаг — подтвердить, что foundation MVP снова проходит final audit как project-agnostic baseline.

---

## 16. Статус документа

Статус: Draft  
Версия: 0.2  
Дата обновления: 2026-07-07  
Проект: Content Plant  
Current strategic baseline: project-agnostic foundation MVP

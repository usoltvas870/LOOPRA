# QA and Review Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает модуль **QA and Review** в платформе **Content Plant**.

Он фиксирует:

- зачем нужен QA and Review;
- какие проверки выполняются до и после production;
- как устроена очередь review;
- какие статусы используются;
- какие действия доступны пользователю;
- как QA связан с Brand Profile, Scenario Studio, Asset Library, Production Engine, Publishing Hub и Analytics;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль QA and Review

QA and Review — это контрольная башня перед публикацией.

Модуль должен помогать не выпускать контент, который:

- нарушает правила проекта;
- содержит запрещённые формулировки;
- имеет технические ошибки;
- не соответствует формату;
- потерял metadata;
- не имеет CTA, если он нужен;
- не готов к публикации.

Главная формула:

```text
Generated / Rendered Content
→ Automated QA
→ Human Review
→ Approved Content
→ Export / Publishing
```

---

## 3. Основной принцип

QA не должен быть “полицейским”, который блокирует всё подряд.

QA должен:

- находить проблемы;
- объяснять, где именно ошибка;
- предлагать следующий шаг;
- различать warning и blocker;
- оставлять финальное решение человеку там, где это безопасно.

---

## 4. Где QA находится в pipeline

QA используется на нескольких этапах:

```text
Idea
→ Scenario QA
→ Asset QA
→ Pre-render QA
→ Render Output QA
→ Human Review
→ Publishing QA
→ Analytics QA
```

В MVP важно закрыть минимум:

```text
Scenario QA
Pre-render QA
Output QA
Human Review
Export QA
```

---

## 5. Виды QA

### 5.1. Scenario QA

Проверка сценария до production.

### 5.2. Asset QA

Проверка ассетов и их соответствия слотам.

### 5.3. Pre-render QA

Проверка готовности к render.

### 5.4. Output QA

Проверка готового файла после render.

### 5.5. Publishing QA

Проверка пакета перед публикацией.

### 5.6. Analytics QA

Проверка наличия метрик после публикации.

---

## 6. Severity levels

Каждая проверка должна иметь severity.

```text
info
warning
error
blocker
```

### 6.1. info

Информационное сообщение.

Пример:

```text
This content has no CTA. This may be acceptable for attention-stage content.
```

### 6.2. warning

Проблема, но пользователь может продолжить.

Пример:

```text
Caption is longer than recommended for this platform.
```

### 6.3. error

Ошибка, которую желательно исправить.

Пример:

```text
Required metadata is missing.
```

### 6.4. blocker

Критичная ошибка, production или publishing невозможны.

Пример:

```text
Required scene asset is missing.
```

---

## 7. QA Check entity

Структура проверки:

```json
{
  "check_id": "check_001",
  "project_id": "project_001",
  "entity_type": "scenario",
  "entity_id": "scenario_001",
  "check_type": "forbidden_phrase",
  "severity": "warning",
  "status": "failed",
  "message": "Text contains a forbidden phrase.",
  "field": "scenes[2].overlay_text",
  "recommendation": "Edit the overlay text or regenerate this scene.",
  "created_at": ""
}
```

---

## 8. QA result statuses

```text
passed
failed
skipped
not_applicable
```

### 8.1. passed

Проверка пройдена.

### 8.2. failed

Проверка не пройдена.

### 8.3. skipped

Проверка пропущена.

### 8.4. not_applicable

Проверка не применима к этому типу контента.

---

## 9. Scenario QA

Scenario QA проверяет сценарий до production.

Проверки MVP:

- project_id exists;
- content_type valid;
- required scenes or blocks exist;
- scene text not empty;
- overlay text not empty, if required;
- text length within format guidelines;
- forbidden phrases absent;
- forbidden topics absent;
- CTA valid, if selected;
- target platform selected;
- funnel stage selected;
- visual prompts exist, if required;
- status allows next action.

---

## 10. Scenario QA examples

### Missing scene

```json
{
  "severity": "blocker",
  "message": "Scenario requires at least 3 scenes for this format.",
  "recommendation": "Add scenes or regenerate the scenario."
}
```

### Overlay too long

```json
{
  "severity": "warning",
  "message": "Scene 2 overlay text is longer than recommended.",
  "recommendation": "Shorten overlay text for better readability."
}
```

### Forbidden phrase

```json
{
  "severity": "error",
  "message": "Scenario contains a phrase from the forbidden list.",
  "recommendation": "Rewrite this sentence according to the project tone rules."
}
```

---

## 11. Asset QA

Asset QA проверяет загруженные файлы и их соответствие требованиям.

Проверки MVP:

- file exists;
- file type supported;
- mime type valid;
- file size within limit;
- asset belongs to project;
- asset status active or linked;
- aspect ratio compatible;
- duration compatible for video/audio;
- required asset slot filled.

---

## 12. Asset QA examples

### Wrong project

```json
{
  "severity": "blocker",
  "message": "Asset belongs to another project.",
  "recommendation": "Choose an asset from the active project or upload a new one."
}
```

### Wrong aspect ratio

```json
{
  "severity": "warning",
  "message": "Asset aspect ratio differs from target output.",
  "recommendation": "Crop, replace or allow template to fit the asset."
}
```

---

## 13. Pre-render QA

Pre-render QA выполняется перед запуском Production Engine.

Проверки MVP:

- scenario status is approved or ready_to_render;
- all required asset slots linked;
- template exists;
- template supports content type;
- Brand Profile exists;
- output spec valid;
- CTA active, if required;
- export settings available.

Если есть blockers, render button должен быть disabled.

---

## 14. Output QA

Output QA проверяет результат после render.

Проверки MVP:

- output file exists;
- output file size > 0;
- metadata.json exists;
- content_id exists;
- render_job_id exists;
- project_id exists;
- video resolution matches output spec;
- duration detected;
- caption exists, if required;
- content status set to needs_review.

---

## 15. Output QA examples

### Missing metadata

```json
{
  "severity": "blocker",
  "message": "metadata.json is missing.",
  "recommendation": "Regenerate export metadata or rerender the content."
}
```

### Wrong resolution

```json
{
  "severity": "error",
  "message": "Rendered video resolution does not match output spec.",
  "recommendation": "Check production template and rerender."
}
```

---

## 16. Publishing QA

Publishing QA проверяет готовность к публикации.

Проверки:

- content status approved;
- export package exists;
- platform selected;
- caption available;
- CTA valid;
- UTM link generated, if link exists;
- scheduled_at valid, if scheduled;
- published URL empty before publish;
- metadata complete.

MVP может выполнять Publishing QA внутри Publishing Hub.

---

## 17. Analytics QA

Analytics QA помогает не терять feedback loop.

Проверки:

- published content has published URL;
- metrics added after publication;
- metrics snapshot not empty;
- required metrics exist;
- revenue fields valid, if revenue tracking enabled.

Dashboard может показывать:

```text
6 published items have no metrics yet.
```

---

## 18. Brand QA

Brand QA проверяет соответствие проектным правилам.

Источники правил:

- Brand Profile;
- Project Settings;
- Tone of Voice;
- Content Rules;
- CTA Library;
- Platform Settings.

Проверки:

- forbidden phrases;
- forbidden topics;
- claim restrictions;
- CTA intensity;
- tone warnings;
- visual restrictions, partially manual in MVP.

---

## 19. Format QA

Format QA проверяет правила контентного формата.

Примеры:

### dialog_miniseries

- has hook;
- scene count within range;
- CTA or closing exists;
- overlay length acceptable;
- scene duration valid;
- visual prompt per scene exists.

### text_social_post

- body exists;
- platform selected;
- length within recommendation;
- CTA valid, if used;
- hashtags within recommendation.

### carousel

- cover exists;
- slide count within range;
- one main idea per slide;
- CTA slide optional or required by funnel stage.

---

## 20. Platform QA

Platform QA проверяет адаптацию под площадку.

Примеры:

- vertical video 9:16 for short-video platforms;
- caption length recommendation;
- hashtag count;
- link policy;
- safe zone warnings;
- text readability.

MVP может использовать только базовые checks.

---

## 21. Human Review

Human Review — обязательный этап перед публикацией.

Человек проверяет:

- смысл;
- визуальное качество;
- соответствие бренду;
- CTA;
- отсутствие странностей генерации;
- техническую готовность;
- пригодность для публикации.

Автоматический QA не заменяет человека в MVP.

---

## 22. Review Queue

Review Queue показывает материалы со статусом:

```text
needs_review
```

Элементы очереди:

- title;
- content type;
- project;
- platform;
- thumbnail / preview;
- QA status;
- created_at;
- action.

Фильтры:

```text
content_type
platform
qa_status
date
project
```

В MVP project filter может быть скрыт, если активен Project Switcher.

---

## 23. Review Detail

Review Detail должен показывать:

```text
Preview
Metadata
Caption
CTA
QA checks
Files
Notes
Actions
```

Actions:

```text
Approve
Reject
Request changes
Edit caption
Replace asset
Rerender
Export
Schedule
```

MVP actions:

```text
Approve
Reject
Edit caption
Rerender
Export
```

---

## 24. Review statuses

Для Content Item:

```text
needs_review
approved
rejected
changes_requested
```

### 24.1. needs_review

Материал ожидает проверки.

### 24.2. approved

Материал одобрен.

### 24.3. rejected

Материал отклонён.

### 24.4. changes_requested

Нужно изменить сценарий, ассеты, caption или render.

---

## 25. Review decision entity

```json
{
  "review_id": "review_001",
  "content_id": "content_001",
  "project_id": "project_001",
  "decision": "approved",
  "notes": "",
  "created_at": "",
  "reviewer": "internal_user"
}
```

MVP может не иметь полноценной user model, но decision metadata желательно сохранять.

---

## 26. Approve flow

```text
1. User opens content item in Review.
2. Checks preview and QA.
3. Clicks Approve.
4. System sets content status = approved.
5. Content becomes available for Export / Schedule.
```

Если есть blockers, Approve должен быть disabled или требовать explicit override, если это не критично.

---

## 27. Reject flow

```text
1. User opens content item.
2. Clicks Reject.
3. Adds note.
4. System sets content status = rejected.
5. User can archive or create variation / rerender.
```

---

## 28. Request changes flow

```text
1. User identifies issue.
2. Chooses request changes.
3. Selects issue type.
4. Adds note.
5. System routes user to Scenario, Asset Library or Production.
```

Issue types:

```text
scenario_text
visual_asset
caption
cta
technical_render
metadata
```

---

## 29. Rerender from Review

Review can trigger rerender.

Flow:

```text
Review output
→ request rerender
→ create new render job
→ preserve previous output
→ new content version needs_review
```

Rerender should not overwrite previous approved output unless user explicitly confirms.

---

## 30. QA override

В MVP можно не делать override.

Если делать, override должен требовать note.

Пример:

```json
{
  "check_id": "check_001",
  "override": true,
  "override_reason": "Accepted because this warning is not relevant for this platform.",
  "created_at": ""
}
```

Blockers лучше не override в MVP.

---

## 31. QA report

Каждый content item может иметь QA report.

```json
{
  "content_id": "content_001",
  "qa_status": "warning",
  "checks": [],
  "summary": {
    "passed": 12,
    "warnings": 2,
    "errors": 0,
    "blockers": 0
  }
}
```

---

## 32. QA summary statuses

```text
passed
warning
error
blocked
not_run
```

### passed

Все обязательные проверки пройдены.

### warning

Есть warnings, но нет errors/blockers.

### error

Есть ошибки, желательно исправить.

### blocked

Есть blockers, нельзя продолжать.

### not_run

QA ещё не запускался.

---

## 33. QA UI

QA panel должен показывать:

- summary;
- список checks;
- severity;
- status;
- affected field;
- recommendation;
- action link.

Пример:

```text
Warning: Caption is longer than recommended.
Action: Edit caption.
```

---

## 34. Automated vs manual checks

Automated checks:

- required fields;
- file exists;
- file type;
- metadata;
- text length;
- forbidden phrases;
- status;
- CTA;
- UTM.

Manual checks:

- visual quality;
- tone nuance;
- emotional accuracy;
- brand fit;
- whether generated image looks strange;
- whether CTA feels appropriate.

---

## 35. Text QA

Text QA checks:

- body not empty;
- overlay not empty;
- forbidden phrases absent;
- length within format limits;
- no unsupported claims;
- CTA not aggressive if content stage is attention;
- language matches project default;
- paragraphs readable.

MVP can implement forbidden phrases + length + empty checks.

---

## 36. Visual QA

Visual QA checks in MVP are mostly manual.

Automated visual checks could include:

- image exists;
- resolution;
- aspect ratio;
- video duration;
- file format.

Future visual checks:

- logo visibility;
- text contrast;
- safe zone detection;
- watermark detection;
- face distortion check;
- low quality image detection.

---

## 37. Metadata QA

Metadata QA is essential.

Checks:

- content_id exists;
- project_id exists;
- scenario_id exists, if applicable;
- content_type exists;
- output_type exists;
- cta_id exists, if used;
- target_platforms exist;
- created_at exists;
- file paths valid.

---

## 38. Export QA

Export QA checks:

- package folder exists;
- required files exist;
- metadata.json exists;
- caption files exist;
- output file exists;
- UTM links generated;
- filenames follow naming conventions.

---

## 39. Review notes

Review notes help improve iteration.

Note fields:

```text
note_id
content_id
project_id
note_type
text
created_at
resolved
```

Note types:

```text
text
visual
audio
cta
technical
metadata
platform
```

MVP can use a single notes textarea.

---

## 40. Integration with Dashboard

Dashboard should show:

- content waiting for review;
- blockers;
- failed QA count;
- published items missing metrics;
- next actions.

Example:

```text
5 items waiting for review
2 render jobs blocked by missing assets
6 published items missing metrics
```

---

## 41. Integration with Scenario Studio

Scenario Studio should show QA warnings before approval.

Example:

```text
Scene 2 overlay is too long.
CTA is missing.
Forbidden phrase detected.
```

Scenario cannot be sent to production if critical checks fail.

---

## 42. Integration with Asset Library

Asset Library should show asset QA status.

Examples:

```text
wrong_aspect_ratio
too_short
unsupported_type
belongs_to_another_project
```

Scene Asset Mapping should show blockers before render.

---

## 43. Integration with Production Engine

Production Engine runs:

```text
pre-render QA
→ render
→ output QA
→ create content item
→ send to Review
```

If pre-render QA fails with blocker, render job should not start.

---

## 44. Integration with Publishing Hub

Publishing Hub should run Publishing QA before scheduling or publishing.

If content is not approved, schedule should be blocked.

---

## 45. Integration with Analytics

QA data can later be analyzed.

Possible insights:

- which templates often fail;
- which formats often have long text;
- which asset types create render errors;
- which content gets rejected most often;
- whether QA warnings correlate with lower performance.

Not needed in MVP, but metadata should allow it.

---

## 46. API endpoints MVP

Recommended endpoints:

```text
POST /api/qa/run
GET /api/qa/reports/:entity_type/:entity_id
GET /api/projects/:project_id/review
GET /api/content-items/:content_id/review
POST /api/content-items/:content_id/approve
POST /api/content-items/:content_id/reject
POST /api/content-items/:content_id/request-changes
POST /api/content-items/:content_id/rerender
```

Local MVP can implement QA as scripts and JSON reports first.

---

## 47. Data model: QA Report

```json
{
  "qa_report_id": "qa_001",
  "project_id": "project_001",
  "entity_type": "content_item",
  "entity_id": "content_001",
  "qa_status": "warning",
  "checks": [],
  "created_at": ""
}
```

---

## 48. Data model: Review

```json
{
  "review_id": "review_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "status": "approved",
  "notes": "",
  "created_at": "",
  "updated_at": ""
}
```

---

## 49. MVP scope

В MVP входит:

- Scenario QA basic;
- Asset QA basic;
- Pre-render QA;
- Output QA;
- Review Queue;
- Review Detail;
- Approve;
- Reject;
- Request changes, simple;
- QA report;
- QA summary;
- Export QA basic;
- Dashboard blockers integration.

---

## 50. Не входит в MVP

В MVP не входит:

- advanced AI moderation;
- semantic tone classifier;
- automatic visual quality scoring;
- automatic safe zone detection;
- OCR-based text contrast checks;
- team review workflow;
- comments and mentions;
- role-based approvals;
- multi-step legal approval;
- advanced QA analytics;
- auto-fix for all issues.

---

## 51. Definition of Done

QA and Review считается готовым для MVP, если пользователь может:

```text
Generate scenario
→ See QA warnings
→ Link assets
→ Run pre-render QA
→ Render content
→ Run output QA
→ Open content in Review
→ Approve or reject
→ Export only approved content
```

и система не позволяет случайно отправить в публикацию content item без базовой проверки и human review.

---

## 52. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/02_platform_architecture/DATA_MODEL.md
docs/03_modules/SCENARIO_STUDIO_SPEC.md
docs/03_modules/ASSET_LIBRARY_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/PUBLISHING_HUB_SPEC.md
docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md
docs/05_product_design/DASHBOARD_SPEC.md
```

---

## 53. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 54. Следующие документы

После этого документа необходимо создать:

1. `docs/03_modules/PUBLISHING_HUB_SPEC.md`
2. `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`
3. `docs/02_platform_architecture/DATA_MODEL.md`
4. `docs/02_platform_architecture/PIPELINES_SPEC.md`
5. `docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md`

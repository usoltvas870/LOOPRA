# Production Engine Spec

## 1. Назначение документа

Этот документ описывает модуль **Production Engine** в платформе **Content Plant**.

Он фиксирует:

- какую роль выполняет Production Engine;
- какие входные данные нужны для сборки контента;
- какие output formats поддерживаются;
- как работают render jobs;
- как Production Engine связан со сценариями, ассетами, Brand Profile, QA, Review и Export;
- какие статусы, проверки и metadata нужны;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Production Engine

Production Engine превращает подготовленные данные в готовые content outputs.

Базовая цепочка:

```text
Scenario
+ Brand Profile
+ Assets
+ Production Template
+ Output Spec
= Rendered Content
```

Production Engine должен собирать:

- вертикальные видео;
- текстовые посты;
- карусели;
- base text outputs;
- metadata.

В MVP основной фокус — собрать первый устойчивый production loop, а не сделать универсальный редактор всего на свете.

---

## 3. Основной принцип

Production Engine должен быть template-driven и project-aware.

Правильно:

```text
Universal template
+ project settings
+ scenario data
+ assets
= project-specific output
```

Неправильно:

```text
Hardcoded project-specific renderer
```

Production Engine не должен знать, “какой это бренд” через код.  
Он должен получать настройки через Project Settings и Brand Profile.

---

## 4. Место в pipeline

Production Engine находится после Scenario Studio и Asset Library.

```text
Idea
→ Scenario Studio
→ Asset Library
→ Production Engine
→ QA
→ Review
→ Export Package
→ Publishing Hub
→ Analytics
```

---

## 5. Основные задачи Production Engine

Production Engine должен:

- принимать approved scenario;
- проверять наличие обязательных ассетов;
- загружать Brand Profile;
- выбирать template;
- применять визуальные и текстовые настройки проекта;
- собирать output;
- сохранять результат;
- создавать metadata;
- передавать результат в Review;
- фиксировать ошибки.

---

## 6. Supported output types

MVP output types:

```text
vertical_video
text_bundle
```

Should-have:

```text
carousel_images
atmospheric_video
caption_bundle
```

Future:

```text
pinterest_pin
blog_post
email_snippet
multi-platform_package
```

---

## 7. Supported content types MVP

Production Engine должен поддерживать:

```text
text_social_post
dialog_miniseries
```

For the first implementation loop the safest MVP format is `text_social_post`. Video formats should connect after the core platform loop is stable.

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

---

## 8. Production Template

Production Template — это универсальный шаблон сборки.

Template задаёт:

- layout;
- scene structure;
- typography slots;
- visual slots;
- timing;
- transitions;
- safe zones;
- output size;
- required assets;
- export rules.

Template не должен содержать проектные тексты, цвета и CTA как hardcode.

---

## 9. Template entity

Минимальная структура:

```json
{
  "template_id": "template_dialog_miniseries_v1",
  "content_type": "dialog_miniseries",
  "output_type": "vertical_video",
  "version": "1.0",
  "supported_aspect_ratios": ["9:16"],
  "required_slots": [],
  "default_duration_sec": 15,
  "status": "active"
}
```

---

## 10. Template slots

Template может иметь slots:

```text
background
scene_asset
overlay_text
speaker_label
cta
logo
music
voiceover
caption
```

Пример:

```json
{
  "slot_id": "scene_1_visual",
  "slot_type": "image_or_video",
  "required": true,
  "aspect_ratio": "9:16"
}
```

---

## 11. Входные данные Render Job

Render Job должен получать:

```text
project_id
scenario_id
content_type
template_id
asset_mappings
brand_profile_version
target_platforms
output_spec
cta_id
```

Пример:

```json
{
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "content_type": "dialog_miniseries",
  "template_id": "template_dialog_miniseries_v1",
  "target_platforms": ["instagram", "tiktok"],
  "output_spec": {
    "aspect_ratio": "9:16",
    "width": 1080,
    "height": 1920,
    "duration_sec": 15,
    "format": "mp4"
  }
}
```

---

## 12. Output Spec

Output Spec задаёт технический формат результата.

Для vertical video MVP:

```json
{
  "output_type": "vertical_video",
  "width": 1080,
  "height": 1920,
  "aspect_ratio": "9:16",
  "duration_sec": 15,
  "format": "mp4",
  "fps": 30
}
```

Для text bundle:

```json
{
  "output_type": "text_bundle",
  "platforms": ["telegram", "threads", "vk"],
  "format": "txt"
}
```

---

## 13. Render Job entity

```json
{
  "render_job_id": "render_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "content_type": "dialog_miniseries",
  "template_id": "template_dialog_miniseries_v1",
  "status": "queued",
  "progress": 0,
  "input_snapshot": {},
  "output_files": [],
  "error": null,
  "created_at": "",
  "started_at": "",
  "finished_at": ""
}
```

---

## 14. Render statuses

Рекомендуемые статусы:

```text
queued
validating
rendering
postprocessing
rendered
failed
cancelled
archived
```

### 14.1. queued

Render job создан, но ещё не начат.

### 14.2. validating

Проверяются входные данные.

### 14.3. rendering

Идёт сборка output.

### 14.4. postprocessing

Идёт финальная обработка: export, metadata, thumbnails.

### 14.5. rendered

Output создан успешно.

### 14.6. failed

Render завершился ошибкой.

### 14.7. cancelled

Job отменён пользователем.

### 14.8. archived

Job скрыт из активной очереди.

---

## 15. Pre-render validation

Перед запуском Production Engine должен проверить:

- project_id exists;
- scenario exists;
- scenario belongs to project;
- scenario status allows rendering;
- template supports content_type;
- required assets are linked;
- assets belong to project;
- files exist;
- Brand Profile exists;
- CTA valid, if required;
- output spec valid.

Если validation не пройдена, render job не должен начинать сборку.

---

## 16. Common validation errors

Примеры:

```text
Scenario is not approved.
Scene 3 has no linked asset.
Asset belongs to another project.
Template does not support selected content type.
Brand Profile is incomplete.
Output format is not supported.
CTA is missing or inactive.
```

Каждая ошибка должна иметь actionable message.

---

## 17. Input Snapshot

Render Job должен сохранять snapshot входных данных.

Зачем:

- воспроизводимость;
- debugging;
- versioning;
- analytics;
- понимание, какие настройки применялись.

Snapshot может включать:

```text
scenario snapshot
asset mapping snapshot
brand profile version
template version
cta
output spec
```

MVP может хранить simplified snapshot.

---

## 18. Vertical Video Rendering

Для `vertical_video` Production Engine должен:

- собрать сцены по порядку;
- применить duration;
- добавить visual assets;
- добавить overlay text;
- применить transitions;
- добавить logo, if configured;
- добавить CTA screen, if configured;
- добавить audio, if provided;
- экспортировать mp4;
- создать metadata.

---

## 19. Scene composition

Каждая сцена может включать:

```text
background asset
main visual
overlay text
speaker label
decorative elements
transition
duration
safe zone rules
```

Scene composition должна быть template-controlled.

---

## 20. Text overlays

Overlay text должен:

- быть читаемым;
- не выходить за safe zones;
- не закрывать важные части изображения;
- соответствовать Brand Profile typography;
- соответствовать platform limits.

Production Engine должен получать overlay text из Scenario Studio.

---

## 21. Safe zones

Для vertical video MVP:

```text
top margin: 160 px
bottom margin: 260 px
left margin: 80 px
right margin: 80 px
```

Safe zones могут быть overridden by template или platform settings.

---

## 22. Transitions

MVP transitions:

```text
fade
crossfade
cut
slow_zoom
```

Avoid in default templates:

```text
fast_flashing
hard_glitch
chaotic_shake
jerky_typing
```

Template должен задавать transitions, а Brand Profile может ограничивать motion style.

---

## 23. Audio handling

Audio может включать:

- background music;
- voiceover;
- sound effects.

MVP audio support:

```text
optional background audio
optional mute
```

Should-have:

```text
voiceover track
audio fade in/out
volume normalization
```

---

## 24. Text Bundle Rendering

Для `text_social_post` Production Engine может создавать text bundle.

Output:

```text
telegram.txt
threads.txt
vk.txt
metadata.json
```

Text bundle может быть создан Scenario Studio, но Production Engine отвечает за base output generation и metadata.

Final `Export Package` for these files belongs to `Publishing Hub`.

---

## 25. Carousel Rendering

Should-have output:

```text
slide_01.png
slide_02.png
slide_03.png
...
caption.txt
metadata.json
```

Carousel rendering должен использовать:

- slide text;
- layout template;
- Brand Profile;
- CTA;
- export settings.

MVP может отложить carousel rendering, если video loop важнее.

---

## 26. Handoff to Export Package

После successful render Production Engine должен передать base outputs в `Publishing Hub`.

Canonical decision:

- Production Engine does not own the final `Export Package`.
- Production Engine owns `RenderJob`, `OutputFile`, `ContentItem`, technical QA result and render output metadata.
- Publishing Hub creates the final `Export Package`, platform-ready package, caption variants, publication preparation and publication records.

---

## 27. Output files entity

```json
{
  "file_id": "file_001",
  "render_job_id": "render_001",
  "project_id": "project_001",
  "type": "video",
  "path": "exports/project/content/video.mp4",
  "mime_type": "video/mp4",
  "size_bytes": 1234567,
  "created_at": ""
}
```

---

## 28. Content Item creation

После успешного render создаётся Content Item.

Content Item — это готовая единица контента, которую можно review, export, schedule, publish и analyze.

Минимальные поля:

```text
content_id
project_id
scenario_id
render_job_id
content_type
output_type
status
files
caption
metadata
created_at
updated_at
```

---

## 29. Content Item statuses

```text
rendered
needs_review
approved
rejected
exported
scheduled
published
analyzed
archived
failed
```

После render по умолчанию:

```text
needs_review
```

---

## 30. Integration with Review

Production Engine не должен автоматически считать контент approved.

После render:

```text
rendered output
→ content item
→ needs_review
→ Review module
```

Review module решает:

- approve;
- reject;
- request changes;
- rerender.

---

## 31. Rerender flow

Rerender может понадобиться, если:

- изменился сценарий;
- заменён ассет;
- изменился CTA;
- изменился caption;
- render failed;
- review отклонил output.

Flow:

```text
Open content item
→ request rerender
→ create new render job
→ preserve previous output
→ mark new output needs_review
```

---

## 32. Versioning of outputs

В будущем нужно хранить versions.

MVP может использовать simple naming:

```text
content_001_v1
content_001_v2
```

Не перезаписывать output без необходимости.

---

## 33. Template versioning

Каждый output должен знать:

```text
template_id
template_version
brand_profile_version
```

Это важно для отладки и аналитики.

---

## 34. Production Queue UI

Production screen должен показывать:

- job id;
- title;
- content type;
- template;
- status;
- progress;
- created date;
- error;
- actions.

Actions:

```text
open
retry
cancel
archive
send to review
```

MVP:

```text
open
retry
cancel
```

---

## 35. Render Setup UI

Перед запуском render показывать:

```text
Scenario
Content type
Template
Required assets status
Brand Profile applied
CTA
Output spec
Estimated duration
```

Если что-то не готово, render button disabled.

---

## 36. Progress

MVP может использовать coarse progress:

```text
queued: 0%
validating: 10%
rendering: 50%
postprocessing: 90%
rendered: 100%
```

Не нужно делать точный progress, если renderer этого не поддерживает.

---

## 37. Error handling

Render error должен сохранять:

```text
error_code
error_message
failed_step
created_at
```

Пример:

```json
{
  "error_code": "MISSING_ASSET",
  "error_message": "Scene 3 has no linked asset.",
  "failed_step": "validation"
}
```

---

## 38. Renderer implementation options

Production Engine может быть реализован через:

- local renderer;
- HTML-to-video;
- ffmpeg pipeline;
- external video API;
- hybrid approach;
- manual export package first.

MVP должен выбирать самый быстрый путь к стабильному output.

---

## 39. Local-first recommendation

Для внутреннего MVP предпочтительно:

```text
local templates
local asset storage
local or server-side render
manual publishing
```

Это снижает зависимость от unstable social APIs.

---

## 40. External AI generation

Production Engine не обязан генерировать images/videos через API в MVP.

В MVP внешний процесс может быть таким:

```text
Scenario Studio generates visual prompts
→ User generates assets externally
→ User uploads assets
→ Production Engine assembles content
```

Это быстрее и надёжнее для первого вертикального среза.

---

## 41. Integration with Publishing Hub

Production Engine отдаёт Publishing Hub:

- content item;
- output files;
- base text outputs, if available;
- metadata;
- CTA;
- technical QA result.

Publishing Hub отвечает за schedule / publish / published URL.

---

## 42. Integration with Analytics

Production Engine должен сохранять metadata, чтобы Analytics мог связывать:

```text
content_type
template_id
scenario_id
topic
CTA
platform
publication
metrics
```

Без metadata optimization loop не работает.

---

## 43. Metadata file

Каждый output package должен иметь `metadata.json`.

Пример:

```json
{
  "content_id": "content_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "render_job_id": "render_001",
  "content_type": "dialog_miniseries",
  "output_type": "vertical_video",
  "template_id": "template_dialog_miniseries_v1",
  "template_version": "1.0",
  "brand_profile_version": "v1",
  "cta_id": "cta_001",
  "target_platforms": ["instagram", "tiktok"],
  "files": ["video.mp4", "caption.txt"],
  "created_at": ""
}
```

---

## 44. QA integration

Перед Review Production Engine должен передать content item в QA.

QA checks могут включать:

- output file exists;
- file size > 0;
- duration within range;
- resolution correct;
- metadata exists;
- caption exists;
- CTA valid;
- forbidden text absent;
- safe zone warnings, optional.

---

## 45. MVP QA after render

MVP checks:

```text
video file exists
metadata.json exists
caption.txt exists if required
resolution correct
duration detected
content item created
status = needs_review
```

---

## 46. API endpoints MVP

Recommended endpoints:

```text
POST /api/projects/:project_id/render-jobs
GET /api/projects/:project_id/render-jobs
GET /api/render-jobs/:render_job_id
POST /api/render-jobs/:render_job_id/cancel
POST /api/render-jobs/:render_job_id/retry
GET /api/content-items/:content_id
GET /api/projects/:project_id/content-items
```

Local MVP can use CLI commands and JSON files first, but module boundaries should stay clear.

---

## 47. Data model: Content Item

```json
{
  "content_id": "content_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "render_job_id": "render_001",
  "content_type": "dialog_miniseries",
  "output_type": "vertical_video",
  "status": "needs_review",
  "files": [],
  "caption_drafts": [],
  "metadata": {},
  "created_at": "",
  "updated_at": ""
}
```

---

## 48. Storage structure

Recommended:

```text
storage/
  projects/
    {project_slug}/
      production/
        render_jobs/
        content_items/
      exports/
        {content_id}/
```

Example:

```text
storage/projects/example_project/exports/content_001/video.mp4
```

---

## 49. MVP scope

В MVP входит:

- render job model;
- production queue;
- pre-render validation;
- support for text bundle output for `text_social_post`;
- support for dialog_miniseries vertical video after the core text loop is stable;
- template-driven rendering;
- project settings applied;
- asset mappings;
- output files;
- metadata.json;
- content item creation;
- status needs_review;
- retry failed render;
- basic error handling.

---

## 50. Не входит в MVP

В MVP не входит:

- full video editor;
- drag-and-drop timeline;
- advanced animation editor;
- automatic AI image/video generation;
- complex audio mixing;
- subtitles auto-sync;
- real-time collaborative editing;
- cloud render autoscaling;
- multi-language dubbing;
- paid ads creatives generator;
- dynamic personalization;
- public template marketplace.

---

## 51. Definition of Done

Production Engine считается готовым для MVP, если пользователь может:

```text
Approve scenario or text draft
→ Start render or text bundle build
→ Get output files
→ Get metadata
→ See content item in Review
→ Retry if failed
```

и всё это происходит project-scoped, template-driven и без hardcoded project rules.

---

## 52. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/02_platform_architecture/DATA_MODEL.md
docs/02_platform_architecture/PIPELINES_SPEC.md
docs/03_modules/SCENARIO_STUDIO_SPEC.md
docs/03_modules/ASSET_LIBRARY_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/03_modules/PUBLISHING_HUB_SPEC.md
docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md
docs/05_product_design/WEB_UI_SPEC.md
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

1. `docs/03_modules/QA_AND_REVIEW.md`
2. `docs/03_modules/PUBLISHING_HUB_SPEC.md`
3. `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`
4. `docs/02_platform_architecture/DATA_MODEL.md`
5. `docs/02_platform_architecture/PIPELINES_SPEC.md`

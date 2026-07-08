# Asset Library Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает модуль **Asset Library** в платформе **Content Plant**.

Он фиксирует:

- какие ассеты хранит платформа;
- как ассеты связаны с проектами, сценариями, сценами и production;
- какие типы файлов поддерживаются;
- как работает загрузка, валидация, теги и привязка ассетов;
- какие статусы и metadata нужны;
- как Asset Library используется в Production Engine;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Asset Library

Asset Library — это проектная библиотека визуальных, аудио и брендовых материалов.

Она нужна, чтобы Content Plant мог работать не только с текстом, но и с реальными production inputs:

```text
images
videos
audio
logos
backgrounds
characters
generated assets
template assets
```

Asset Library связывает внешний мир генерации и съёмки с внутренним pipeline Content Plant.

---

## 3. Основной принцип

Каждый ассет должен быть привязан к проекту.

Главное правило:

```text
asset.project_id must exist
```

Ассет одного проекта не должен случайно использоваться в другом проекте.

В будущем можно добавить shared assets на уровне workspace, но в MVP все ассеты project-scoped.

---

## 4. Где Asset Library находится в pipeline

Asset Library находится между Scenario Studio и Production Engine.

```text
Scenario Studio
→ Visual Prompts
→ External generation / manual asset creation
→ Asset Library
→ Scene Asset Mapping
→ Production Engine
```

Также Asset Library используется напрямую в:

- Review;
- Export;
- Brand Profile;
- Project Settings;
- Publishing Hub.

---

## 5. Основные задачи Asset Library

Asset Library должна позволять:

- загрузить файл;
- определить тип ассета;
- сохранить metadata;
- добавить теги;
- связать ассет со сценарием;
- связать ассет со сценой;
- проверить формат;
- показать preview;
- заменить ассет;
- архивировать ассет;
- передать ассет в Production Engine.

---

## 6. Типы ассетов

Поддерживаемые asset types:

```text
image
video
audio
logo
background
character
template_asset
document
other
```

### 6.1. image

Используется для:

- сцен;
- каруселей;
- обложек;
- pins;
- thumbnails;
- backgrounds.

### 6.2. video

Используется для:

- вертикальных роликов;
- b-roll;
- atmospheric video;
- animated backgrounds;
- talking head clips.

### 6.3. audio

Используется для:

- music;
- voiceover;
- sound effects.

### 6.4. logo

Используется для:

- брендирования;
- watermarks;
- covers;
- export packages.

### 6.5. background

Используется как повторяемый фон для шаблонов.

### 6.6. character

Используется для персонажей, аватаров, говорящих голов или visual identity.

### 6.7. template_asset

Используется для production templates:

- frames;
- overlays;
- masks;
- decorative elements;
- reusable scene parts.

### 6.8. document

Используется для референсов, брифов, исходных текстов или guideline-файлов.

---

## 7. Поддерживаемые форматы файлов MVP

### 7.1. Images

```text
png
jpg
jpeg
webp
```

### 7.2. Videos

```text
mp4
mov
webm
```

### 7.3. Audio

```text
mp3
wav
m4a
aac
```

### 7.4. Documents

```text
txt
md
json
csv
pdf
```

PDF можно хранить как asset reference, но не обязательно парсить в MVP.

---

## 8. Asset entity

Минимальная структура asset:

```json
{
  "asset_id": "asset_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "type": "image",
  "filename": "scene_001.png",
  "file_path": "storage/projects/project_001/assets/images/scene_001.png",
  "mime_type": "image/png",
  "size_bytes": 123456,
  "width": 1080,
  "height": 1920,
  "duration_sec": null,
  "aspect_ratio": "9:16",
  "tags": [],
  "status": "active",
  "created_at": "",
  "updated_at": ""
}
```

---

## 9. Обязательные поля MVP

Для MVP обязательны:

```text
asset_id
project_id
type
filename
file_path
mime_type
size_bytes
status
created_at
updated_at
```

Желательные поля:

```text
width
height
duration_sec
aspect_ratio
tags
source_type
source_id
linked_scenario_id
linked_scene_id
```

---

## 10. Asset statuses

Рекомендуемые статусы:

```text
uploading
active
linked
needs_review
rejected
archived
deleted
failed
```

### 10.1. uploading

Файл загружается.

### 10.2. active

Файл доступен для использования.

### 10.3. linked

Файл привязан к сцене, сценарию или content item.

### 10.4. needs_review

Ассет требует проверки.

### 10.5. rejected

Ассет не подходит.

### 10.6. archived

Ассет скрыт из активной работы, но сохранён.

### 10.7. deleted

Ассет удалён или помечен как удалённый.

### 10.8. failed

Ошибка загрузки или обработки.

---

## 11. Asset sources

Ассет может прийти из разных источников:

```text
manual_upload
external_ai_generation
stock
camera
screen_recording
template
brand_upload
import
```

MVP source types:

```text
manual_upload
external_ai_generation
brand_upload
```

---

## 12. Source linkage

Если ассет был создан по visual prompt, нужно хранить связь.

```json
{
  "asset_id": "asset_001",
  "source_type": "visual_prompt",
  "source_id": "prompt_001",
  "scenario_id": "scenario_001",
  "scene_id": "scene_001"
}
```

Это позволит понимать:

- какой prompt использовался;
- для какой сцены ассет создавался;
- можно ли заменить ассет;
- какие visuals работают лучше.

---

## 13. Связь с project_id

Все asset queries должны быть scoped by project.

Примеры:

```text
GET /api/projects/:project_id/assets
POST /api/projects/:project_id/assets
```

Не использовать глобальный список ассетов без project filter в MVP.

---

## 14. Asset folder structure

Рекомендуемая структура хранения:

```text
storage/
  projects/
    {project_slug}/
      assets/
        images/
        videos/
        audio/
        logos/
        backgrounds/
        characters/
        documents/
        template_assets/
```

Пример:

```text
storage/projects/example_project/assets/images/scene_001.png
```

---

## 15. Naming conventions

Рекомендуемый pattern:

```text
{project_slug}_{asset_type}_{date}_{short_id}.{ext}
```

Пример:

```text
example_project_image_20260704_a1b2.png
```

Для scene-linked assets:

```text
{project_slug}_{scenario_id}_{scene_id}_{asset_type}.{ext}
```

---

## 16. Upload flow

Базовый flow:

```text
1. User opens Asset Library
2. Click Upload
3. Select files
4. Choose asset type
5. Add tags, optional
6. Link to scenario or scene, optional
7. Upload
8. Validate
9. Save metadata
10. Show in Asset Library
```

---

## 17. Upload validation

Validation MVP:

- file extension supported;
- file size within limit;
- mime type detected;
- project_id exists;
- file saved successfully;
- metadata created.

Optional validation:

- image dimensions;
- video duration;
- aspect ratio;
- audio duration;
- corruption check.

---

## 18. Recommended file size limits MVP

Начальные лимиты:

```text
image: 25 MB
video: 500 MB
audio: 100 MB
document: 25 MB
```

Эти лимиты можно менять в System Settings.

---

## 19. Preview generation

Asset Library должна показывать preview.

Для MVP:

- image preview: original or resized thumbnail;
- video preview: thumbnail or first frame;
- audio preview: file name + duration;
- logo preview: image;
- document preview: icon + filename.

Не обязательно генерировать sophisticated thumbnails в первой версии.

---

## 20. Asset metadata extraction

При загрузке желательно извлекать:

### Images

```text
width
height
aspect_ratio
color mode
```

### Videos

```text
width
height
aspect_ratio
duration_sec
fps
codec, optional
```

### Audio

```text
duration_sec
codec, optional
```

### Documents

```text
page_count, optional
encoding, optional
```

---

## 21. Tags

Tags помогают искать и фильтровать ассеты.

Примеры tag categories:

```text
topic
style
scene
character
platform
campaign
source
status
```

MVP tags могут быть free text.

В будущем можно добавить controlled taxonomy.

---

## 22. Search and filters

Asset Library должна поддерживать:

```text
search by filename
filter by type
filter by tag
filter by linked status
filter by scenario
filter by date
filter by status
```

MVP:

```text
type
status
search by filename
```

---

## 23. Asset detail screen

Asset Detail должен показывать:

- preview;
- filename;
- type;
- metadata;
- tags;
- source;
- linked scenario;
- linked scene;
- usage history;
- actions.

Actions:

```text
download
copy path
edit metadata
add tags
link to scene
replace
archive
delete
```

MVP actions:

```text
preview
edit metadata
link to scene
archive
```

---

## 24. Scene Asset Mapping

Scene Asset Mapping связывает asset slots со сценами сценария.

Пример UI:

```text
Scene 1
Prompt: ...
Required: image 9:16
Selected asset: none
[Upload] [Choose from library]

Scene 2
Prompt: ...
Required: video 9:16
Selected asset: asset_002.mp4
[Replace]
```

---

## 25. Asset slot model

Asset slot создаётся Scenario Studio или Production Engine.

```json
{
  "asset_slot_id": "slot_001",
  "project_id": "project_001",
  "scenario_id": "scenario_001",
  "scene_id": "scene_001",
  "required_type": "image",
  "required_aspect_ratio": "9:16",
  "required_duration_sec": null,
  "asset_id": null,
  "status": "empty"
}
```

---

## 26. Asset slot statuses

```text
empty
linked
invalid
approved
rejected
optional
```

### empty

Нет ассета.

### linked

Ассет привязан.

### invalid

Ассет не соответствует требованиям.

### approved

Ассет проверен и подходит.

### rejected

Ассет отклонён.

### optional

Слот необязательный.

---

## 27. Asset compatibility checks

При привязке ассета к слоту проверять:

- project_id совпадает;
- тип подходит;
- aspect ratio подходит или допустим crop;
- duration подходит, если video/audio;
- file exists;
- status не archived/deleted/rejected.

Пример ошибки:

```text
This asset cannot be linked because it belongs to another project.
```

---

## 28. Replace asset flow

Замена ассета:

```text
1. Open linked asset
2. Click Replace
3. Choose new file or library asset
4. Validate compatibility
5. Update asset slot
6. Mark scenario readiness again
```

Важно: старая связь должна сохраняться в usage history или activity log, если возможно.

---

## 29. Usage tracking

Asset usage показывает, где используется ассет.

Пример:

```json
{
  "asset_id": "asset_001",
  "used_in": [
    {
      "entity_type": "scenario_scene",
      "entity_id": "scene_001"
    },
    {
      "entity_type": "content_item",
      "entity_id": "content_001"
    }
  ]
}
```

MVP может показывать только linked scenario / scene.

---

## 30. Brand assets

Некоторые ассеты являются брендовыми:

```text
logo
brand mark
font files reference
backgrounds
characters
color cards
```

Brand assets могут быть связаны с Brand Profile.

Важно: не раздавать пользователю font files из среды выполнения.  
В документации можно хранить названия шрифтов и ссылки на источники, но не распространять файлы шрифтов.

---

## 31. Template assets

Template assets используются Production Engine.

Примеры:

- frame overlays;
- subtle texture;
- masks;
- placeholder backgrounds;
- reusable lower thirds;
- end screens.

Template assets могут быть:

```text
platform-level
project-level
```

MVP может поддерживать только project-level или bundled platform templates.

---

## 32. Audio assets

Audio assets могут быть:

- background music;
- voiceover;
- sound effect.

Metadata:

```text
duration_sec
usage_rights
mood
tempo, optional
```

MVP не обязан управлять лицензиями глубоко, но поле `usage_rights` желательно.

---

## 33. Usage rights

Для ассетов желательно хранить:

```text
usage_rights
source_url
license_notes
created_by
```

MVP может оставить это optional, но в будущем важно для коммерческого использования.

Пример:

```json
{
  "usage_rights": "owned",
  "source_url": "",
  "license_notes": "Generated externally by user."
}
```

---

## 34. Asset quality flags

Можно использовать quality flags:

```text
low_resolution
wrong_aspect_ratio
too_short
too_long
needs_crop
watermark_detected
unclear_text
```

MVP:

```text
wrong_aspect_ratio
too_short
too_long
```

---

## 35. Integration with Scenario Studio

Scenario Studio создаёт:

- visual prompts;
- asset slots;
- required asset list.

Asset Library принимает:

- uploads;
- links;
- replacements.

После заполнения слотов Scenario Studio может перейти в:

```text
ready_to_render
```

---

## 36. Integration with Production Engine

Production Engine получает:

- scenario;
- asset slots;
- linked assets;
- project settings;
- template;
- output spec.

Production Engine не должен искать файлы вручную.  
Он должен получать structured asset references.

---

## 37. Integration with Review

Review может отправить ассет обратно на замену.

Пример flow:

```text
Review rendered content
→ scene visual is bad
→ replace scene asset
→ rerender
```

Asset Library должна поддержать замену без потери связи со сценой.

---

## 38. Integration with Publishing Hub

Publishing Hub использует final output assets:

- video.mp4;
- carousel images;
- cover image;
- caption files;
- metadata.json.

Эти output files могут быть отдельным типом content output, не обязательно raw asset.

В MVP можно хранить их в export packages.

---

## 39. Raw assets vs output assets

Важно различать:

```text
raw asset
production output
export package
```

Raw asset:

```text
input image, video, audio, logo
```

Production output:

```text
rendered video, generated carousel slides
```

Export package:

```text
files prepared for publication
```

Asset Library хранит raw and reusable assets.  
Outputs можно хранить в Production / Export modules.

---

## 40. API endpoints MVP

Рекомендуемые endpoints:

```text
GET /api/projects/:project_id/assets
POST /api/projects/:project_id/assets
GET /api/assets/:asset_id
PATCH /api/assets/:asset_id
POST /api/assets/:asset_id/archive
DELETE /api/assets/:asset_id
GET /api/scenarios/:scenario_id/asset-slots
PATCH /api/asset-slots/:asset_slot_id
POST /api/asset-slots/:asset_slot_id/link
POST /api/asset-slots/:asset_slot_id/unlink
```

Для локального MVP можно заменить API файловой структурой и JSON metadata.

---

## 41. UI requirements

Asset Library UI должен включать:

- asset grid/list;
- upload button;
- filters;
- asset detail;
- scene mapping view;
- preview;
- tags;
- link status;
- archive action.

---

## 42. Grid vs table

Рекомендуется:

- grid для image/video;
- table для documents/audio;
- toggle view later.

MVP может использовать единый grid/list.

---

## 43. Empty states

Если ассетов нет:

```text
No assets yet.
Upload images, videos, audio or logos to use them in production.

[Upload Assets]
```

Если сценарий ждёт ассеты:

```text
This scenario needs assets before rendering.
Upload or choose assets for each required scene.

[Open Asset Mapping]
```

---

## 44. Error states

Примеры:

```text
Upload failed: unsupported file type.
This asset cannot be linked because it belongs to another project.
This video is shorter than required.
File not found in storage.
```

Каждая ошибка должна иметь next action, если возможно.

---

## 45. MVP scope

В MVP входит:

- project-scoped Asset Library;
- upload images/videos/audio/logos/documents;
- metadata storage;
- basic validation;
- preview;
- tags basic;
- filters basic;
- asset detail;
- asset slots;
- link asset to scene;
- replace asset;
- archive asset;
- compatibility checks;
- integration with Scenario Studio and Production Engine.

---

## 46. Не входит в MVP

В MVP не входит:

- advanced DAM;
- AI image generation inside platform;
- automatic background removal;
- advanced video trimming;
- color correction;
- licensing marketplace;
- shared workspace asset library;
- role-based asset permissions;
- duplicate detection;
- face recognition;
- full OCR;
- automatic quality scoring.

---

## 47. Definition of Done

Asset Library считается готовой для MVP, если пользователь может:

```text
Upload asset
→ See preview
→ Add metadata/tags
→ Link asset to scenario scene
→ Validate compatibility
→ Replace asset if needed
→ Send scenario to production
```

без ручного редактирования JSON и без поиска файлов в папках.

---

## 48. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/DATA_MODEL.md
docs/03_modules/SCENARIO_STUDIO_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/05_product_design/USER_WORKFLOWS.md
docs/05_product_design/WEB_UI_SPEC.md
docs/05_product_design/PROJECT_SETTINGS_SPEC.md
```

---

## 49. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 50. Следующие документы

После этого документа необходимо создать:

1. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
2. `docs/03_modules/QA_AND_REVIEW.md`
3. `docs/03_modules/PUBLISHING_HUB_SPEC.md`
4. `docs/02_platform_architecture/DATA_MODEL.md`
5. `docs/02_platform_architecture/PIPELINES_SPEC.md`

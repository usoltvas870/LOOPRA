# Publishing Hub Spec

## 1. Назначение документа

Этот документ описывает модуль **Publishing Hub** в платформе **Content Plant**.

Он фиксирует:

- зачем нужен Publishing Hub;
- как готовый контент превращается в публикацию;
- как работает календарь публикаций;
- как формируются export packages;
- какие статусы используются;
- как хранить platform-specific captions, links, UTM и published URLs;
- как Publishing Hub связан с Production Engine, Review, QA и Analytics;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Publishing Hub

Publishing Hub управляет последним участком контентного конвейера:

```text
Approved Content
→ Export Package
→ Schedule
→ Manual / Semi-automatic Publishing
→ Published URL
→ Metrics
```

Главная задача модуля — не “автоматически постить всё во все соцсети”, а сделать публикационный процесс управляемым, прозрачным и измеримым.

---

## 3. Основной принцип

Publishing Hub должен быть **export-first**.

Canonical ownership decision:

- `Export Package` belongs to `Publishing Hub`.
- `Production Engine` may hand off base outputs and metadata, but must not own the final `Export Package`.

Это значит:

- сначала платформа должна стабильно готовить файлы и тексты для публикации;
- автопостинг можно добавлять позже;
- пользователь должен иметь возможность вручную опубликовать материал и вернуть ссылку в систему;
- analytics loop должен работать даже без API социальных сетей.

Такой подход снижает зависимость от ограничений платформ, нестабильных API и ручных особенностей публикации.

---

## 4. Место в pipeline

Publishing Hub находится после QA and Review.

```text
Production Engine
→ QA
→ Review
→ Approved Content
→ Publishing Hub
→ Publication
→ Metrics
→ Analytics
```

Контент не должен попадать в Publishing Hub как ready-to-publish, если он не прошёл human review.

---

## 5. Основные задачи Publishing Hub

Publishing Hub должен позволять:

- видеть approved content;
- создавать export package;
- готовить platform-specific caption;
- добавлять UTM links;
- планировать публикацию;
- отмечать ручную публикацию;
- хранить published URL;
- связывать публикацию с content item;
- передавать публикацию в Analytics;
- показывать публикации без метрик.

---

## 6. Основные сущности

Publishing Hub работает с сущностями:

```text
Content Item
Export Package
Publication
Caption Variant
Platform
UTM Link
Metric Snapshot
```

---

## 7. Publication entity

Publication — это запись о размещении content item на конкретной платформе.

```json
{
  "publication_id": "publication_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "platform": "instagram",
  "status": "draft",
  "scheduled_at": "",
  "published_at": "",
  "published_url": "",
  "caption_id": "caption_001",
  "export_package_id": "export_001",
  "utm_url": "",
  "notes": "",
  "created_at": "",
  "updated_at": ""
}
```

---

## 8. Publication statuses

Рекомендуемые статусы:

```text
draft
ready
scheduled
published
failed
cancelled
archived
```

### draft

Публикация создана, но ещё не готова.

### ready

Есть платформа, caption и export package.

### scheduled

Публикация запланирована.

### published

Публикация размещена, желательно с published URL.

### failed

Публикация не удалась или отмечена как проблемная.

### cancelled

Публикация отменена.

### archived

Публикация скрыта из активной работы.

---

## 9. Export Package

Export Package — набор файлов, подготовленных для публикации.

`Export Package` is a Publishing Hub entity, not a Production Engine entity.

Пример для video:

```text
exports/
  {project_slug}/
    {content_id}/
      video.mp4
      caption_instagram.txt
      caption_tiktok.txt
      caption_youtube_shorts.txt
      metadata.json
      cover.txt
```

Пример для text bundle:

```text
exports/
  {project_slug}/
    {content_id}/
      telegram.txt
      threads.txt
      vk.txt
      metadata.json
```

Пример для carousel:

```text
exports/
  {project_slug}/
    {content_id}/
      slide_01.png
      slide_02.png
      slide_03.png
      caption.txt
      metadata.json
```

---

## 10. Export Package entity

```json
{
  "export_package_id": "export_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "package_path": "exports/project_001/content_001/",
  "files": [],
  "status": "ready",
  "created_at": "",
  "updated_at": ""
}
```

Статусы export package:

```text
creating
ready
incomplete
failed
archived
```

---

## 11. Caption Variant

Caption Variant — версия текста публикации для конкретной платформы.

```json
{
  "caption_id": "caption_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_id": "content_001",
  "platform": "instagram",
  "text": "",
  "hashtags": [],
  "cta_id": "cta_001",
  "utm_url": "",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

Caption statuses:

```text
draft
ready
approved
archived
```

---

## 12. Platform-specific adaptation

Один content item может иметь разные captions для разных платформ.

Пример:

```text
Instagram: короткий caption + soft CTA
TikTok: короткий caption + link in profile note
YouTube Shorts: короткое описание + ссылка
Telegram: длиннее и глубже
VK: средний пост + ссылка
Threads: короткий текст без тяжёлого CTA
Pinterest: evergreen description
```

Правила берутся из Project Settings → Platform Settings.

---

## 13. Supported platforms

MVP может поддерживать значения:

```text
tiktok
instagram
youtube_shorts
telegram
vk
threads
pinterest
```

Future:

```text
linkedin
x
facebook
blog
email
website
```

---

## 14. Manual publishing flow

Главный MVP-сценарий:

```text
1. User opens approved content item.
2. Creates export package.
3. Chooses target platform.
4. Copies caption or downloads package.
5. Publishes manually on platform.
6. Returns to Content Plant.
7. Marks publication as published.
8. Adds published URL.
9. Later adds metrics.
```

Это базовый путь без зависимости от API социальных сетей.

---

## 15. Schedule flow

Scheduling в MVP может быть внутренним календарём без фактического автопостинга.

```text
1. User chooses approved content.
2. Selects platform.
3. Selects date/time.
4. Selects caption variant.
5. Saves publication as scheduled.
6. System shows it in Calendar.
7. User publishes manually at planned time.
8. User marks as published.
```

---

## 16. Autoposting future flow

В будущем:

```text
Approved Content
→ Schedule
→ Platform API
→ Auto publish
→ Store published URL
→ Import metrics
```

Но это не должно блокировать MVP.

---

## 17. Calendar

Calendar показывает публикации.

MVP view:

```text
list view
```

Should-have:

```text
week view
month view
```

Поля списка:

- scheduled_at;
- platform;
- content title;
- content type;
- status;
- caption status;
- export package status;
- published URL;
- actions.

Фильтры:

```text
platform
status
content_type
date range
project
```

---

## 18. Publication Detail

Publication Detail должен показывать:

```text
Content preview
Platform
Caption
Hashtags
CTA
UTM URL
Export files
Scheduled time
Published URL
Status
Metrics status
Notes
```

Actions:

```text
Copy caption
Download package
Mark as published
Add published URL
Add metrics
Reschedule
Cancel
Archive
```

---

## 19. UTM generation

Publishing Hub должен формировать UTM-ссылки по правилам проекта.

Базовый шаблон:

```text
utm_source={platform}
utm_medium=organic
utm_campaign={project_slug}_{campaign}
utm_content={content_id}
```

Пример:

```text
https://example.com?utm_source=telegram&utm_medium=organic&utm_campaign=example_project_launch&utm_content=content_001
```

UTM должен сохраняться в caption variant, publication и metadata.

---

## 20. Link rules

Publishing Hub должен учитывать, что платформы по-разному работают со ссылками.

Примеры:

- TikTok / Instagram: ссылка обычно в профиле;
- Telegram / VK: можно использовать прямую ссылку;
- YouTube Shorts: ссылка может быть в описании;
- Pinterest: ссылка может быть outbound link;
- Threads: ссылка может быть возможна, но CTA должен быть мягким.

Platform Settings должны описывать эти правила.

---

## 21. Export QA

Перед публикацией нужно проверить:

- content item approved;
- export package ready;
- caption exists;
- platform selected;
- CTA valid, if used;
- UTM generated, if URL used;
- required files exist;
- metadata exists.

Если content item не approved, Publishing Hub не должен разрешать schedule/publish.

---

## 22. Publication metadata

Каждая публикация должна сохранять:

```text
project_id
content_id
platform
scheduled_at
published_at
published_url
caption_id
utm_url
status
```

Это необходимо для Analytics.

---

## 23. Publishing notes

Для ручной публикации полезно хранить notes.

Примеры:

```text
Use trending audio manually.
Upload as Reel, not Story.
Pin first comment with link.
Post at 19:00 local time.
```

MVP может иметь одно поле `notes`.

---

## 24. Platform checklist

Для каждой платформы можно показывать чеклист.

Пример для video:

```text
Download video
Copy caption
Add music manually, if needed
Check cover
Publish
Paste published URL
Mark as published
```

В MVP checklist может быть текстовым.

---

## 25. Published URL

После публикации пользователь должен добавить published URL.

Зачем:

- открыть публикацию;
- связать метрики;
- проверять performance;
- хранить историю;
- использовать в отчётах.

Если URL отсутствует, Dashboard может показывать warning:

```text
3 published items have no URL.
```

---

## 26. Metrics handoff

После status = published публикация должна появиться в списке:

```text
Needs metrics
```

или Dashboard warning:

```text
Published items missing metrics
```

Analytics позже использует publication_id и content_id.

---

## 27. Reuse content on multiple platforms

Один content item может иметь несколько publications.

Пример:

```text
content_001
→ publication_instagram
→ publication_tiktok
→ publication_youtube_shorts
→ publication_vk
```

Каждая publication имеет свой platform, caption, URL и metrics.

---

## 28. Cross-post package

Для одного content item можно создать cross-post package:

```text
video.mp4
caption_instagram.txt
caption_tiktok.txt
caption_youtube_shorts.txt
caption_vk.txt
metadata.json
```

MVP может создавать несколько caption files, но не обязан создавать отдельную папку на каждую платформу.

---

## 29. Publication creation from approved content

Flow:

```text
1. Open approved content item.
2. Click Create Publication.
3. Select platform.
4. Select or generate caption variant.
5. Generate UTM link.
6. Save as draft or scheduled.
```

---

## 30. Publication creation from Calendar

Flow:

```text
1. Open Calendar.
2. Click New Publication.
3. Select approved content item.
4. Select platform.
5. Select date/time.
6. Save.
```

---

## 31. Bulk scheduling

Bulk scheduling может быть полезен, но не обязателен.

Future flow:

```text
Select multiple approved items
→ assign platforms
→ distribute across dates
→ create scheduled publications
```

Не включать в MVP без необходимости.

---

## 32. Integration with Project Settings

Publishing Hub использует:

- target platforms;
- profile URLs;
- platform rules;
- CTA Library;
- UTM defaults;
- export settings;
- timezone;
- primary URL.

---

## 33. Integration with Production Engine

Production Engine отдаёт:

- content item;
- files;
- base text outputs or caption drafts;
- metadata;
- technical QA result.

Publishing Hub создаёт:

- export package;
- publication records;
- scheduling records;
- platform variants.

---

## 34. Integration with QA and Review

Publishing Hub должен принимать только:

```text
content.status = approved
```

Если QA status = blocked, публикация запрещена.

Если QA status = warning, можно показать предупреждение.

---

## 35. Integration with Dashboard

Dashboard должен показывать:

- scheduled publications;
- draft publications;
- publications due today;
- published items without URL;
- published items without metrics.

---

## 36. Integration with Analytics

Analytics использует:

- publication_id;
- content_id;
- platform;
- published_at;
- published_url;
- UTM;
- metrics snapshots;
- revenue.

Без Publication entity analytics не сможет корректно сравнивать платформы.

---

## 37. API endpoints MVP

Recommended endpoints:

```text
GET /api/projects/:project_id/publications
POST /api/projects/:project_id/publications
GET /api/publications/:publication_id
PATCH /api/publications/:publication_id
POST /api/publications/:publication_id/mark-published
POST /api/publications/:publication_id/cancel
GET /api/projects/:project_id/export-packages
POST /api/content-items/:content_id/export-package
GET /api/export-packages/:export_package_id
POST /api/content-items/:content_id/caption-variants
PATCH /api/caption-variants/:caption_id
```

Local MVP can use file-based packages first.

---

## 38. UI requirements

Publishing Hub UI должен включать:

- approved content list;
- export package view;
- publication calendar/list;
- publication detail;
- caption editor;
- UTM preview;
- manual publishing checklist;
- published URL input;
- quick metrics action.

---

## 39. Empty states

Если нет approved content:

```text
No approved content yet.
Approve content in Review before creating publications.

[Open Review]
```

Если нет публикаций:

```text
No publications scheduled.
Create a publication from approved content.

[Create Publication]
```

---

## 40. Error states

Примеры:

```text
Cannot create publication: content item is not approved.
Cannot create export package: metadata is missing.
Cannot schedule publication: platform is not selected.
Cannot mark as published: published URL is missing.
```

Published URL can be optional if platform URL is not available, but system should warn.

---

## 41. MVP scope

В MVP входит:

- approved content list;
- create export package;
- platform-specific captions;
- UTM generation;
- create publication;
- calendar/list view;
- schedule record;
- manual publish workflow;
- mark as published;
- published URL field;
- handoff to metrics;
- Publishing QA basic.

---

## 42. Не входит в MVP

В MVP не входит:

- full autoposting;
- OAuth connections to all platforms;
- social inbox;
- comment management;
- trend audio integration;
- paid campaign publishing;
- approval chains by role;
- bulk scheduling;
- AI best-time-to-post;
- automatic metric import from every platform;
- content recycling automation.

---

## 43. Definition of Done

Publishing Hub считается готовым для MVP, если пользователь может:

```text
Open approved content
→ Create export package
→ Choose platform
→ Prepare caption with CTA/UTM
→ Schedule publication
→ Publish manually
→ Mark as published
→ Add published URL
→ Send to metrics/analytics
```

и вся эта цепочка сохраняет project_id, content_id, platform и metadata.

---

## 44. Связанные документы

```text
docs/00_index.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/DATA_MODEL.md
docs/02_platform_architecture/PIPELINES_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md
docs/05_product_design/DASHBOARD_SPEC.md
docs/05_product_design/WEB_UI_SPEC.md
docs/05_product_design/PROJECT_SETTINGS_SPEC.md
```

---

## 45. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant

---

## 46. Следующие документы

После этого документа необходимо создать:

1. `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`
2. `docs/02_platform_architecture/DATA_MODEL.md`
3. `docs/02_platform_architecture/PIPELINES_SPEC.md`
4. `docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md`
5. `docs/02_platform_architecture/INTEGRATIONS_SPEC.md`

# Integrations Spec

## 1. Назначение документа

Этот документ описывает интеграционный слой платформы **Content Plant**.

Он фиксирует:

- какие внешние сервисы и API могут использоваться платформой;
- какие интеграции входят и не входят в MVP;
- как интеграции связаны с Project, Brand Profile, Asset Library, Production Engine, Publishing Hub и Analytics;
- как хранить настройки интеграций;
- как работать с нестабильными или ограниченными API социальных платформ;
- как проектировать систему так, чтобы она оставалась export-first и не зависела от одного внешнего поставщика;
- какие требования к безопасности, логированию, ошибкам и retry нужны для MVP и следующих версий.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль интеграционного слоя

Integrations Layer соединяет Content Plant с внешним миром.

Он может отвечать за:

```text
LLM providers
File storage
Render tools
Image / video generation tools
Social publishing APIs
Analytics imports
Website / conversion tracking
CSV imports
Webhook events
Notification channels
```

Но интеграционный слой не должен становиться ядром продукта.

Главное ядро Content Plant:

```text
Project
→ Brand Profile
→ Idea
→ Scenario
→ Asset
→ Production
→ Review
→ Publication
→ Metrics
```

Интеграции помогают этому циклу, но не должны ломать его, если один внешний сервис недоступен.

---

## 3. Главный принцип

Content Plant должен быть **integration-tolerant**, а не **integration-dependent**.

Это значит:

- основной workflow должен работать без обязательного автопостинга;
- external generation через API не должна быть обязательной для MVP;
- social APIs могут подключаться постепенно;
- ручной импорт и export packages должны оставаться базовым fallback;
- каждая интеграция должна иметь явные статусы, ошибки и ограничения;
- project-specific credentials не должны быть смешаны между проектами.

Базовое правило MVP:

```text
Manual / CSV / Export-first flow first.
API automation later.
```

---

## 4. Категории интеграций

Content Plant может иметь следующие категории интеграций.

```text
storage
llm_provider
render_engine
image_generation
video_generation
audio_generation
publishing_platform
analytics_import
website_events
csv_import
notification
identity
payment
```

Для MVP приоритетны:

```text
storage
llm_provider
render_engine
csv_import
manual_publishing
manual_metrics
```

Autoposting, paid SaaS integrations, billing and multi-user identity are future layers.

---

## 5. MVP integrations scope

### 5.1. Входит в MVP

MVP должен поддерживать:

- local file storage или S3-compatible storage;
- LLM provider для генерации сценариев, captions, prompts и анализа текстов;
- render engine для сборки видео / изображений / export packages;
- manual upload assets;
- manual export packages;
- manual publication marking;
- manual metrics input;
- CSV metrics import;
- CSV / manual trend import;
- project-scoped integration settings placeholders.

### 5.2. Не входит в MVP

В MVP не обязательно реализовывать:

- полный автопостинг во все соцсети;
- встроенную генерацию изображений через API;
- встроенную генерацию видео через API;
- автоматический импорт всех метрик из соцсетей;
- сложную OAuth-инфраструктуру для внешних пользователей;
- billing provider;
- public SaaS identity;
- marketplace integrations;
- full CRM / email marketing automation.

---

## 6. Integration entity

Integration — это конфигурация подключения к внешнему сервису.

Минимальная структура:

```json
{
  "integration_id": "integration_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "type": "publishing_platform",
  "provider": "instagram",
  "status": "disabled",
  "mode": "manual_export",
  "credentials_ref": null,
  "settings": {},
  "last_checked_at": "",
  "created_at": "",
  "updated_at": ""
}
```

### 6.1. Scope

Integrations могут быть:

```text
workspace-scoped
project-scoped
system-scoped
```

MVP recommendation:

```text
project-scoped for publishing and analytics
system-scoped for local render engine
workspace-scoped for shared storage, if needed
```

---

## 7. Integration statuses

Рекомендуемые статусы:

```text
disabled
configured
active
limited
error
expired
revoked
archived
```

### disabled

Интеграция не используется.

### configured

Настройки добавлены, но подключение ещё не проверено или не активно.

### active

Интеграция работает.

### limited

Интеграция работает частично или имеет ограничения.

### error

Последняя операция завершилась ошибкой.

### expired

Credentials истекли.

### revoked

Доступ был отозван пользователем или платформой.

### archived

Интеграция скрыта из активного списка.

---

## 8. Integration modes

Поддерживаемые режимы:

```text
manual_export
csv_import
semi_auto
auto_api
webhook
internal
```

### manual_export

Платформа готовит файлы и тексты, пользователь публикует вручную.

### csv_import

Платформа принимает CSV с данными.

### semi_auto

Платформа автоматизирует часть workflow, но требует ручного шага.

### auto_api

Платформа выполняет действие через API.

### webhook

Внешний сервис отправляет события в Content Plant.

### internal

Интеграция является внутренним системным компонентом, например local render engine.

---

## 9. Credentials handling

Credentials нельзя хранить в открытом виде внутри обычных JSON-полей.

Рекомендуемый подход:

```text
credentials_ref → secure storage / environment variable / secrets manager
```

В MVP допустимо:

- использовать environment variables для system-level providers;
- хранить project settings без секретов;
- вручную задавать API keys только в protected config;
- не строить сложный multi-user OAuth, если нет внешних пользователей.

Нельзя:

- писать tokens в markdown-документацию;
- сохранять tokens в export packages;
- смешивать credentials разных проектов;
- логировать секреты в plain text.

---

## 10. Storage integrations

Storage используется для:

- uploaded assets;
- generated outputs;
- export packages;
- thumbnails;
- documents;
- CSV imports;
- logs, if needed.

### 10.1. MVP storage

MVP может использовать local storage:

```text
storage/
  projects/
    {project_slug}/
      assets/
      renders/
      exports/
      thumbnails/
      imports/
      analytics/
```

### 10.2. Future storage

В будущем можно использовать:

```text
S3-compatible storage
cloud object storage
CDN
backup storage
archive storage
```

### 10.3. Storage rules

- все project-level files должны быть separated by project;
- file paths должны быть stored in database;
- external URLs should not replace internal file references;
- export packages должны быть reproducible;
- deleted files не должны ломать database state without warning.

---

## 11. LLM provider integration

LLM provider используется для:

- idea expansion;
- trend analysis;
- scenario generation;
- scene generation;
- visual prompt generation;
- caption generation;
- text social posts;
- QA suggestions;
- analytics summaries;
- optimization recommendations.

### 11.1. LLM request entity

Минимальная структура:

```json
{
  "llm_request_id": "llm_request_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "module": "scenario_studio",
  "task_type": "generate_scenario",
  "provider": "provider_name",
  "model": "model_name",
  "input_snapshot": {},
  "output_snapshot": {},
  "status": "completed",
  "error": null,
  "created_at": "",
  "finished_at": ""
}
```

### 11.2. LLM status values

```text
queued
running
completed
failed
cancelled
```

### 11.3. LLM rules

- LLM output must be reviewed or QA checked before production;
- prompt templates should be versioned;
- Brand Profile must be loaded for project-specific generation;
- project-specific data must come from Project Settings / Brand Profile, not hardcoded prompts;
- input and output snapshots should be stored for debugging, at least in simplified form;
- sensitive credentials must not be included in prompts.

---

## 12. Render engine integration

Render engine creates production outputs.

It may use:

```text
FFmpeg
HTML-to-video renderer
browser-based renderer
image composition engine
video composition service
custom templates
```

### 12.1. Render engine responsibilities

Render engine should:

- receive Render Job input snapshot;
- load Production Template;
- load project Brand Profile;
- load asset mappings;
- create output files;
- create technical metadata;
- report progress and errors;
- store outputs in project-scoped storage.

### 12.2. Render engine integration mode

MVP recommendation:

```text
internal render worker
```

Future:

```text
external render service
cloud render queue
third-party video generation provider
```

### 12.3. Render integration rules

- render workers must not hardcode project-specific colors, text, CTA or logo;
- templates must receive project settings as data;
- output files must be linked to Render Job and Content Item;
- failed renders must preserve error message;
- retry should create a new attempt or update attempt count.

---

## 13. Image generation integrations

Image generation through API is not required for MVP.

MVP flow:

```text
Scenario Studio generates visual prompts
→ User copies prompt to external tool
→ User generates image manually
→ User uploads asset to Asset Library
```

Future flow:

```text
Scenario Studio
→ Image generation provider API
→ Generated Asset
→ Asset Library
→ Production
```

### 13.1. Future generated asset metadata

If image API is added, store:

```text
provider
model
prompt
negative_prompt
seed, if available
source_scenario_id
source_scene_id
generation_status
cost, optional
```

### 13.2. Rules

- generated images become Assets after save;
- each generated asset must have project_id;
- generated assets require QA or review before production;
- provider-specific fields should not pollute core Asset model too much.

---

## 14. Video generation integrations

Video generation through API is not required for MVP.

MVP flow:

```text
User creates or sources video externally
→ uploads video asset
→ Production Engine uses it as background / scene asset
```

Future:

```text
Scenario / Visual Prompt
→ Video generation provider
→ Asset Library
→ Production Engine
```

Rules are similar to image generation:

- project_id required;
- source prompt should be stored;
- generated video must be reviewed;
- provider limits and cost must be tracked if integrated.

---

## 15. Audio integrations

Audio may include:

```text
background music
voiceover
sound effects
platform-native music added manually
```

MVP:

- optional uploaded audio;
- optional mute;
- audio file stored as Asset;
- no required audio generation API.

Future:

- TTS providers;
- music generation providers;
- sound effect libraries;
- platform-native music notes in Publishing Hub.

Rules:

- audio licensing metadata should be stored if known;
- platform-native music may be added manually after export;
- export package can include publishing notes like “add trending audio manually”.

---

## 16. Publishing platform integrations

Publishing integrations connect Content Plant with platforms where content is distributed.

Supported platform IDs should align with Project Settings and Publishing Hub:

```text
tiktok
instagram
youtube_shorts
telegram
vk
threads
pinterest
linkedin
x
facebook
blog
email
website
```

MVP priority:

```text
manual_export for all platforms
optional API integrations later
```

### 16.1. Manual publishing

Manual publishing is the default MVP workflow:

```text
Approved Content
→ Export Package
→ User downloads / copies caption
→ User publishes manually
→ User pastes published URL
→ User adds metrics later
```

This is stable and platform-independent.

### 16.2. Semi-automatic publishing

Semi-auto publishing can include:

- prepared captions;
- platform checklist;
- UTM links;
- reminders;
- publication notes;
- copied hashtags;
- exported media variants.

### 16.3. Auto API publishing

Auto publishing can be added per platform only when:

- API is stable enough;
- terms allow it;
- credentials are configured;
- error handling exists;
- manual fallback still works.

---

## 17. Platform integration capability matrix

Content Plant should store capabilities per platform.

Example structure:

```json
{
  "platform": "example_platform",
  "manual_export": true,
  "auto_publish": false,
  "metrics_import": false,
  "supports_links": true,
  "supports_scheduling": false,
  "supports_video": true,
  "supports_carousel": true,
  "supports_text": true,
  "notes": "Manual publishing recommended in MVP."
}
```

This matrix should be configurable and updated as integrations evolve.

---

## 18. Publishing job entity

If autoposting or semi-auto publishing is added, use Publishing Job.

```json
{
  "publishing_job_id": "publishing_job_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "publication_id": "publication_001",
  "integration_id": "integration_001",
  "status": "queued",
  "attempt_count": 0,
  "request_snapshot": {},
  "response_snapshot": {},
  "error": null,
  "created_at": "",
  "started_at": "",
  "finished_at": ""
}
```

Statuses:

```text
queued
validating
uploading
processing
published
failed
cancelled
requires_manual_action
```

---

## 19. Analytics import integrations

Analytics can be imported from:

```text
manual input
CSV upload
platform APIs
website events
internal tracking
UTM reports
```

MVP:

```text
manual input
CSV upload
```

Future:

```text
platform API import
website event tracking
webhooks
analytics connectors
```

### 19.1. Metrics import entity

```json
{
  "metrics_import_id": "metrics_import_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "source_type": "csv",
  "source_file_id": "file_001",
  "status": "completed",
  "rows_total": 100,
  "rows_imported": 95,
  "rows_failed": 5,
  "error_report_path": "",
  "created_at": ""
}
```

### 19.2. Import statuses

```text
uploaded
validating
mapping
importing
completed
completed_with_errors
failed
cancelled
```

### 19.3. Metrics import rules

- imports must be project-scoped;
- metrics must link to Publication when possible;
- unmatched rows should be reported, not silently ignored;
- raw imported file should be stored or traceable;
- imported values create Metric Snapshots.

---

## 20. CSV import

CSV import is important for MVP because it avoids dependency on platform APIs.

Supported CSV use cases:

```text
trend import
metrics import
publication import, optional
content inventory import, optional
```

### 20.1. Metrics CSV recommended columns

```text
platform
published_url
publication_id
content_id
date
views
likes
comments
saves
shares
profile_visits
link_clicks
registrations
purchases
revenue
currency
notes
```

MVP can support partial columns and show warnings for missing mappings.

### 20.2. Trend CSV recommended columns

```text
platform
url
title
caption
transcript
views
likes
comments
shares
published_at
author
notes
```

---

## 21. Website event integrations

Website events can connect content performance to business outcomes.

Future events:

```text
page_view
lead
registration
checkout_start
purchase
subscription_start
subscription_cancel
form_submit
```

MVP can rely on manual or CSV metrics.

Future architecture should support:

- UTM parameters;
- content_id attribution;
- campaign attribution;
- event timestamp;
- revenue;
- anonymous visitor id, if allowed;
- privacy and consent requirements.

---

## 22. UTM integration

UTM generation is shared between Project Settings, Publishing Hub and Analytics.

Default template:

```text
utm_source={platform}
utm_medium=organic
utm_campaign={project_slug}_{campaign}
utm_content={content_id}
```

Rules:

- UTM should be generated before publication;
- UTM should be stored in Caption Variant and Publication;
- UTM should be included in export metadata;
- Analytics should use UTM to connect traffic and conversion data when available.

---

## 23. Notification integrations

Notifications are not required for MVP, but can be useful later.

Potential channels:

```text
email
telegram
slack
discord
in-app notifications
```

Use cases:

- render finished;
- render failed;
- publication due;
- metrics missing;
- integration token expired;
- weekly report ready.

MVP can start with in-app warnings and Dashboard alerts.

---

## 24. Identity integrations

MVP does not require public identity integrations.

MVP can assume:

```text
single internal user
local admin access
no public registration
```

Future identity integrations may include:

- OAuth login;
- email/password;
- SSO;
- workspace invitations;
- role-based permissions.

These are SaaS-layer features and should not block MVP.

---

## 25. Payment integrations

Payment integrations are out of MVP scope.

Future SaaS may require:

- billing provider;
- plans;
- subscription status;
- invoices;
- usage limits;
- payment webhooks.

These should be documented in SaaS Vision or Billing Spec later, not implemented in the MVP production loop.

---

## 26. Integration error model

All integration errors should be actionable.

Minimum error fields:

```json
{
  "error_code": "provider_rate_limited",
  "message": "Provider rate limit was reached.",
  "severity": "warning",
  "provider": "provider_name",
  "recommendation": "Retry later or use manual export.",
  "raw_error_ref": "log_001"
}
```

Severity values:

```text
info
warning
error
blocker
```

Rules:

- user-facing messages should be understandable;
- raw provider errors should not expose credentials;
- fallback action should be shown when possible;
- error should be linked to job or integration entity.

---

## 27. Retry and fallback

Integration jobs should support retry where safe.

Retry strategy examples:

```text
manual retry
automatic retry with delay
retry after token refresh
fallback to manual export
mark as failed and continue pipeline
```

MVP requirements:

- failed render or import jobs should be visible;
- failed publishing integration should not destroy export package;
- manual fallback should remain available;
- retry count should be tracked for automated jobs.

---

## 28. Rate limits and quotas

External APIs can have rate limits.

Content Plant should store or document:

```text
provider
operation
limit_type
limit_value
reset_window
last_rate_limit_error
```

MVP can keep this lightweight.

Future automation should respect:

- API rate limits;
- daily quotas;
- upload limits;
- file size limits;
- platform-specific restrictions.

---

## 29. Integration logs

Integration logs help debugging.

Minimum fields:

```json
{
  "integration_log_id": "log_001",
  "integration_id": "integration_001",
  "project_id": "project_001",
  "operation": "metrics_import",
  "status": "failed",
  "message": "CSV row mapping failed.",
  "created_at": ""
}
```

Rules:

- do not log secrets;
- keep request/response snapshots only when safe;
- link logs to jobs;
- logs can be truncated or archived.

---

## 30. Integration settings UI

Project Settings should include Integrations section.

MVP UI can show:

```text
Provider
Type
Mode
Status
Last checked
Actions
Notes
```

Actions:

```text
Enable
Disable
Test connection
Open settings
View logs
```

MVP may use placeholders for future integrations.

Important: Do not show complex SaaS OAuth flows until external users are supported.

---

## 31. Publishing platform notes

Because social platform APIs can change and have access restrictions, Content Plant should treat platform support as capability-based, not promise-based.

Recommended wording in UI and docs:

```text
This platform supports export package in MVP.
Autoposting may be added later if API access and platform rules allow it.
```

Avoid designing MVP around mandatory autoposting.

---

## 32. Module integration map

### 32.1. Trend Radar

Uses:

- manual link input;
- CSV import;
- optional external APIs later;
- LLM provider for analysis.

### 32.2. Scenario Studio

Uses:

- LLM provider;
- Brand Profile;
- Content Format Specs;
- Project Settings.

### 32.3. Asset Library

Uses:

- local / object storage;
- metadata extraction;
- optional external generation tools later.

### 32.4. Production Engine

Uses:

- render engine;
- storage;
- templates;
- Brand Profile;
- optional audio/video tools later.

### 32.5. Publishing Hub

Uses:

- export packages;
- platform settings;
- UTM generation;
- manual / semi-auto / auto publishing integrations.

### 32.6. Analytics

Uses:

- manual metrics;
- CSV import;
- platform API metrics later;
- website events later.

---

## 33. Integration acceptance criteria MVP

MVP integration layer is ready when:

- project-scoped integration settings can be stored;
- local storage works with project separation;
- LLM provider can be called through a service layer;
- render engine can be called through a job interface;
- CSV import works for metrics or has a clear interface;
- manual export remains available for all target platforms;
- integration errors are visible and actionable;
- failed integrations do not block unrelated pipeline steps;
- no project-specific credentials or settings are hardcoded into platform modules.

---

## 34. Anti-patterns

Avoid:

- making one social platform API mandatory for MVP;
- storing API tokens in markdown or plain logs;
- hardcoding provider-specific logic in core entities;
- mixing project credentials;
- using global asset folders for project files;
- assuming every platform supports links, scheduling or metrics;
- treating missing API automation as a blocker for publishing;
- building public SaaS billing before internal MVP loop works;
- hiding integration failures from the user.

---

## 35. Open questions

Questions to resolve during implementation:

1. Which LLM provider is used first in MVP?
2. Will render engine be fully internal or partly external?
3. Should CSV import support custom column mapping in MVP or fixed templates only?
4. Which platforms are enabled as manual export targets at launch?
5. Which platform gets first autoposting experiment after MVP?
6. How long should integration logs be stored?
7. Should website event tracking be implemented before or after first analytics loop?
8. Should project-level integration settings support multiple accounts per platform later?

---

## 36. Summary

Integrations in Content Plant should extend the production system without making it fragile.

The MVP should prove the full content loop with stable primitives:

```text
Manual input
→ LLM-assisted generation
→ Project-scoped assets
→ Internal render
→ Export package
→ Manual publishing
→ Manual / CSV metrics
→ Analytics insight
```

API automation can be added platform by platform after the export-first workflow is reliable.

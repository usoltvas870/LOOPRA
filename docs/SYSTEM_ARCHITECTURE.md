# System Architecture

## 1. Назначение документа

Этот документ описывает техническую архитектуру платформы **Content Plant**.

Он фиксирует:

- из каких основных компонентов состоит система;
- как frontend, backend, database, storage, workers и render layer взаимодействуют между собой;
- как архитектура поддерживает Workspace, Project и Brand Profile;
- как данные проходят через pipeline от идеи до метрик;
- какие технические границы входят в MVP;
- какие интеграции и SaaS-функции откладываются на будущие этапы;
- какие принципы должны соблюдать агенты и разработчики при реализации.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главный архитектурный принцип

Content Plant должен проектироваться как **modular project-aware platform**.

Это означает:

```text
Universal platform modules
+ Project Settings
+ Brand Profile
+ Content Format Specs
+ Production Templates
= Project-specific content output
```

Архитектура не должна содержать project-specific hardcode.

Правильно:

```text
project_id → load Brand Profile → apply format rules → render output
```

Неправильно:

```text
brand-specific script → hardcoded colors → hardcoded CTA → one-project renderer
```

A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`.

---

## 3. Архитектурные цели MVP

MVP архитектура должна позволить:

1. Создавать и переключать Projects внутри одного Workspace.
2. Хранить Brand Profile отдельно для каждого Project.
3. Создавать Ideas и Scenarios.
4. Генерировать Visual Prompts для внешней генерации ассетов.
5. Загружать Assets и связывать их со Scenario / Scene.
6. Запускать Production Jobs.
7. Создавать Content Items и Output Files.
8. Проводить QA and Human Review.
9. Формировать Export Packages.
10. Вести Publications и Calendar.
11. Вносить Metrics вручную или через CSV.
12. Показывать Dashboard как агрегированное состояние pipeline.

MVP не должен требовать:

- публичной регистрации пользователей;
- billing;
- tariff plans;
- teams and permissions;
- marketplace;
- обязательного autoposting;
- встроенной генерации изображений и видео через API;
- сложного AI optimizer.

---

## 4. High-level architecture

Базовая схема системы:

```text
Web UI
  ↓
Backend API
  ↓
Application Services
  ↓
Database
  ↓
File Storage
  ↓
Worker Queue
  ↓
Production / Render Workers
  ↓
Output Storage
  ↓
Publishing / Metrics / Analytics
```

Логическая схема модулей:

```text
Projects / Settings
  ↓
Brand System
  ↓
Idea Bank
  ↓
Scenario Studio
  ↓
Asset Library
  ↓
Production Engine
  ↓
QA and Review
  ↓
Publishing Hub
  ↓
Analytics
  ↓
Dashboard
```

Dashboard не является источником истины. Он только читает агрегированное состояние из других модулей.

---

## 5. Основные компоненты системы

### 5.1. Web UI

Web UI — интерфейс оператора Content Plant.

Основные разделы MVP:

```text
Dashboard
Projects
Project Settings
Idea Bank
Scenario Studio
Asset Library
Production
Review
Publishing / Calendar
Analytics
```

Web UI должен:

- всегда показывать active Project;
- не смешивать данные разных Projects;
- показывать next actions;
- показывать status и blockers;
- позволять запускать основные pipeline-действия;
- открывать preview для assets, scenarios, content items и publications.

---

### 5.2. Backend API

Backend API — центральный слой приложения.

Он отвечает за:

- project-scoped CRUD operations;
- запуск генерации и production jobs;
- валидацию статусов;
- доступ к Brand Profile;
- работу с файлами;
- создание export packages;
- ручной ввод metrics;
- подготовку данных для Dashboard.

API должен быть project-aware.

Пример правильного routing pattern:

```text
/api/projects/{project_id}/ideas
/api/projects/{project_id}/scenarios
/api/projects/{project_id}/assets
/api/projects/{project_id}/render-jobs
/api/projects/{project_id}/content-items
/api/projects/{project_id}/publications
/api/projects/{project_id}/metrics
```

Глобальные endpoints допустимы только для platform-level справочников:

```text
/api/content-formats
/api/production-templates
/api/platforms
```

---

### 5.3. Application Services

Application Services — слой бизнес-логики.

Рекомендуемые сервисы:

```text
ProjectService
BrandProfileService
IdeaService
ScenarioService
AssetService
ProductionService
QAService
ReviewService
ExportService
PublishingService
MetricsService
DashboardService
```

Каждый service должен работать через `workspace_id` и / или `project_id`, если сущность относится к проекту.

---

### 5.4. Database

Database хранит структурированные сущности.

Основные группы таблиц:

```text
Workspace / Project
Brand Profile / Project Settings
Idea / Topic / Hook / Trend
Scenario / Scene / Text Block / Visual Prompt
Asset / Asset Slot
Production Template / Render Job / Output File
Content Item
QA Check / Review Decision
Export Package / Caption Variant
Publication
Metric Snapshot
Campaign / Experiment / Batch
```

Единая модель данных описывается в `DATA_MODEL.md`.

---

### 5.5. File Storage

File Storage хранит binary files и generated outputs.

В MVP допустимо локальное хранилище.

Рекомендуемая структура:

```text
storage/
  workspaces/
    {workspace_id}/
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
          renders/
            {content_id}/
          exports/
            {content_id}/
          thumbnails/
          imports/
          metrics/
```

В будущем локальное хранилище можно заменить или дополнить S3-compatible storage.

Важно: project files не должны лежать в общей папке без project separation.

---

### 5.6. Worker Queue

Worker Queue используется для долгих задач.

Типы background jobs:

```text
scenario_generation
visual_prompt_generation
asset_metadata_extraction
pre_render_validation
render_job
postprocessing
export_package_creation
thumbnail_generation
qa_checks
metrics_import
analytics_aggregation
```

Для MVP можно начать с простого job runner, но архитектура должна позволять вынести задачи в отдельные workers.

---

### 5.7. Production / Render Workers

Render Workers выполняют сборку output.

Они получают:

```text
render_job_id
project_id
scenario_id
template_id
asset_mappings
brand_profile_snapshot
output_spec
```

И создают:

```text
output files
render metadata
content item
qa input
```

Render Worker не должен сам решать project-specific правила. Он должен получать их через Brand Profile snapshot, Template config и Output Spec.

---

### 5.8. LLM Integration Layer

LLM Integration Layer используется для генерации и анализа текста.

Основные задачи:

```text
idea expansion
trend analysis
scenario generation
hook generation
visual prompt generation
caption generation
text social post generation
optimization suggestions
```

LLM prompts должны строиться из:

```text
Project Settings
Brand Profile
Content Format Spec
Scenario / Idea input
CTA Library
Content Rules
Platform Settings
```

Prompt templates не должны содержать project-specific hardcode.

---

### 5.9. Publishing Integration Layer

Publishing Integration Layer отвечает за подготовку публикаций и будущие интеграции с платформами.

MVP режим:

```text
export-first
manual publishing
manual published URL input
manual metrics / CSV import
```

Future режим:

```text
semi-automatic posting
autoposting through stable APIs
metrics import through APIs
platform account management
```

Autoposting не должен блокировать MVP.

---

### 5.10. Analytics Layer

Analytics Layer агрегирует Metric Snapshots и связывает их с Content Items, Publications, Ideas, Scenarios, Formats, Topics, Hooks and CTAs.

MVP Analytics должен поддерживать:

```text
manual metric entry
CSV metric import
basic aggregation by project
basic aggregation by platform
basic aggregation by content_type
top content
weak content
missing metrics warnings
```

Advanced optimization может быть добавлена позже.

---

## 6. Recommended MVP technology shape

Этот раздел не является жёстким требованием, но задаёт целевую форму реализации.

### 6.1. Frontend

Возможные варианты:

```text
React / Next.js
TypeScript
Tailwind / component library
tables, forms, kanban, calendar, preview panels
```

Ключевое требование — UI должен быть workflow-first, а не decorative dashboard.

### 6.2. Backend

Возможные варианты:

```text
Python + FastAPI
or Node.js / TypeScript backend
```

Важно не конкретное имя фреймворка, а соблюдение модульности, project scope и чистой data model.

### 6.3. Database

Рекомендуемый вариант:

```text
PostgreSQL
```

Для раннего MVP допустим SQLite, если проект находится в локальной разработке, но data model должна быть совместима с последующей миграцией.

### 6.4. Queue / Workers

Возможные варианты:

```text
Redis + RQ / Celery / BullMQ / custom worker
```

Для первой версии можно использовать простую очередь задач, если render jobs не блокируют Web UI.

### 6.5. Rendering

Возможные подходы:

```text
FFmpeg
MoviePy
Remotion
HTML-to-video
custom template renderer
```

Production Templates должны быть data-driven и принимать Brand Profile values.

### 6.6. Storage

MVP:

```text
local filesystem
```

Future:

```text
S3-compatible object storage
CDN for previews
backup storage
```

---

## 7. Module boundaries

### 7.1. Projects and Settings

Отвечает за:

- Workspace;
- Project;
- Project Settings;
- Brand Profile;
- CTA Library;
- Platform Settings;
- Export Settings;
- Analytics Settings.

Не отвечает за:

- генерацию сценариев;
- рендер;
- публикацию;
- аналитику метрик.

---

### 7.2. Idea Bank

Отвечает за:

- создание ideas;
- хранение topics, hooks, notes;
- статусы идей;
- передачу идеи в Scenario Studio.

Не отвечает за:

- генерацию production-ready сценариев;
- рендер;
- публикацию.

---

### 7.3. Scenario Studio

Отвечает за:

- generation / editing сценариев;
- scenes / blocks;
- visual prompts;
- captions draft;
- CTA selection;
- scenario QA input.

Не отвечает за:

- хранение binary assets;
- rendering output;
- final publication.

---

### 7.4. Asset Library

Отвечает за:

- upload;
- metadata extraction;
- preview;
- tags;
- asset slots;
- scene asset mapping.

Не отвечает за:

- генерацию изображений через API в MVP;
- финальный render;
- публикацию.

---

### 7.5. Production Engine

Отвечает за:

- render jobs;
- template application;
- output files;
- content item creation;
- base render metadata;
- postprocessing.

Не отвечает за:

- human approval;
- final platform-specific publishing;
- long-term metrics analysis.

---

### 7.6. QA and Review

Отвечает за:

- automated checks;
- severity;
- human decision;
- approve / reject / request changes;
- handoff to export.

Не отвечает за:

- render implementation;
- actual posting;
- analytics aggregation.

---

### 7.7. Publishing Hub

Отвечает за:

- export packages;
- caption variants;
- publication records;
- schedule list / calendar;
- published URLs;
- UTM links;
- metrics handoff.

Не отвечает за:

- source scenario generation;
- render implementation;
- strategic optimization.

---

### 7.8. Analytics

Отвечает за:

- Metric Snapshots;
- aggregation;
- reports;
- top / weak content;
- missing data warnings;
- optimization suggestions.

Не отвечает за:

- editing scenarios;
- rendering;
- publishing files.

---

## 8. Data flow overview

### 8.1. From Idea to Scenario

```text
Idea
→ Scenario generation request
→ Load Project Settings
→ Load Brand Profile
→ Load Content Format Spec
→ Generate Scenario
→ Save Scenario
→ Scenario QA
```

Created / updated entities:

```text
Idea
Scenario
Scene / Text Block
Visual Prompt
QA Check
```

---

### 8.2. From Scenario to Assets

```text
Scenario approved
→ Generate / confirm Visual Prompts
→ Create Asset Slots
→ User creates assets externally
→ Upload Assets
→ Link Assets to Slots
→ Asset QA
→ Scenario ready_to_render
```

Created / updated entities:

```text
Visual Prompt
Asset Slot
Asset
QA Check
Scenario status
```

---

### 8.3. From Assets to Content Item

```text
Scenario ready_to_render
→ Create Render Job
→ Pre-render QA
→ Render Worker
→ Output Files
→ Content Item
→ Output QA
→ needs_review
```

Created / updated entities:

```text
Render Job
Output File
Content Item
QA Check
```

---

### 8.4. From Review to Export

```text
Content Item needs_review
→ Human Review
→ Approve
→ Create Export Package
→ Caption Variants
→ ready for Publishing Hub
```

Created / updated entities:

```text
Review Decision
Content Item status
Export Package
Caption Variant
```

---

### 8.5. From Export to Publication

```text
Export Package ready
→ Create Publication
→ Schedule or manual publish
→ Add published URL
→ Publication status published
→ Metrics required
```

Created / updated entities:

```text
Publication
UTM Link
Metric Snapshot placeholder
```

---

### 8.6. From Publication to Analytics

```text
Publication published
→ Manual metrics or CSV import
→ Metric Snapshot
→ Aggregation
→ Dashboard update
→ Optimization suggestions
```

Created / updated entities:

```text
Metric Snapshot
Analytics summary
Dashboard summary
Experiment / recommendation, future
```

---

## 9. Status ownership

### 9.1. Idea statuses

Owned by Idea Bank.

```text
raw
approved
scripted
waiting_assets
in_production
ready
scheduled
published
analyzed
archived
```

### 9.2. Scenario statuses

Owned by Scenario Studio.

```text
draft
needs_review
approved
needs_assets
ready_to_render
in_production
rendered
rejected
archived
```

### 9.3. Render Job statuses

Owned by Production Engine.

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

### 9.4. Content Item statuses

Owned by Production / Review / Publishing lifecycle.

```text
rendered
needs_review
approved
rejected
changes_requested
exported
scheduled
published
analyzed
archived
failed
```

### 9.5. Publication statuses

Owned by Publishing Hub.

```text
draft
ready
scheduled
published
failed
cancelled
archived
```

### 9.6. Metric Snapshot statuses

Owned by Analytics.

```text
draft
imported
validated
needs_review
approved
archived
```

---

## 10. Project scoping rules

Every project-level entity must have `project_id`.

Required for:

```text
Brand Profile
Project Settings
CTA
Ideas
Trends, if project-adapted
Scenarios
Scenes
Visual Prompts
Asset Slots
Assets
Render Jobs
Output Files
Content Items
QA Checks
Review Decisions
Export Packages
Caption Variants
Publications
Metric Snapshots
Campaigns
Experiments
Batches
```

Platform-level entities may exist without `project_id`:

```text
Content Format Specs
Production Templates
Platform registry
Global system settings
Documentation references
```

If a template has project-specific overrides, the override must be stored in project-level settings, not in the platform template itself.

---

## 11. Snapshots and reproducibility

Content Plant should keep snapshots for important operations.

### 11.1. Scenario generation snapshot

May include:

```text
input idea
brand profile version
format spec version
prompt template version
CTA selection
LLM model metadata, if available
```

### 11.2. Render job snapshot

May include:

```text
scenario snapshot
asset mapping snapshot
brand profile snapshot
template version
output spec
CTA
platform targets
```

### 11.3. Export package snapshot

May include:

```text
content item version
caption variants
UTM settings
platform settings
export files
created_at
```

Snapshots are important for debugging, rerendering, analytics and comparing content performance.

MVP can store simplified snapshots as JSON.

---

## 12. File handling rules

### 12.1. Uploads

On upload, system should:

1. attach `project_id`;
2. detect file type;
3. validate extension and mime type;
4. store file in project-scoped path;
5. extract metadata if possible;
6. create Asset record;
7. generate preview if applicable.

### 12.2. Renders

On render, system should:

1. create Render Job;
2. write output files to project-scoped render folder;
3. create Output File records;
4. create Content Item;
5. run Output QA;
6. set Content Item to `needs_review`.

### 12.3. Exports

On export, system should:

1. verify Content Item is approved;
2. create Export Package;
3. create platform-specific captions;
4. include metadata;
5. include UTM links where needed;
6. save files in project-scoped export folder.

---

## 13. Error handling principles

Errors should be structured and actionable.

Every pipeline error should include:

```text
entity_type
entity_id
project_id
error_code
message
severity
recommended_action
created_at
```

Examples:

```text
Scenario cannot be rendered because required asset slot is empty.
Asset cannot be linked because it belongs to another project.
Export package cannot be created because content item is not approved.
Publication cannot be marked as published without target platform.
Metrics cannot be validated because publication_id is missing.
```

Errors that block next steps should be surfaced in Dashboard Blockers.

---

## 14. Security and permissions MVP

MVP may have one internal operator.

Therefore MVP does not require:

```text
public auth
team roles
complex permissions
billing entitlements
organization management
```

However, architecture should not prevent future user accounts and workspaces.

Future SaaS layer may add:

```text
User
Workspace membership
Roles
Permissions
Billing account
Plan limits
Audit log
```

Do not implement these until MVP scope explicitly changes.

---

## 15. Integration strategy

MVP integrations should follow a cautious approach.

### 15.1. Generation tools

MVP should assume external generation for images and videos.

Flow:

```text
Content Plant creates prompt
User generates asset externally
User uploads asset
Content Plant stores and uses asset
```

Built-in image/video generation APIs are future scope.

### 15.2. Social platforms

MVP should be export-first.

Flow:

```text
Export package
→ manual publishing
→ published URL added manually
→ metrics added manually or by CSV
```

Autoposting can be added platform by platform later.

### 15.3. Analytics import

MVP should support:

```text
manual input
CSV import
```

API-based metrics import is future scope.

---

## 16. Dashboard architecture

Dashboard should aggregate data from modules.

Inputs:

```text
Project
Ideas
Scenarios
Assets
Render Jobs
Content Items
QA Checks
Review Queue
Export Packages
Publications
Metric Snapshots
```

Dashboard should produce:

```text
Project Health Summary
Pipeline Overview
Next Actions
Blockers
Review Queue Preview
Upcoming Publications
Recent Metrics
Missing Metrics Warnings
```

Dashboard should not create its own business state.

If Dashboard shows a blocker, the source must be traceable to the original entity and QA Check or validation error.

---

## 17. API design principles

API should follow these principles:

1. Project-scoped routes for project data.
2. Platform-level routes only for global references.
3. Explicit status transitions.
4. No silent cross-project access.
5. Actions should validate current status before mutation.
6. Long-running actions should create jobs.
7. Every generated output should have traceable input snapshot.
8. Errors should be actionable.

Example action routes:

```text
POST /api/projects/{project_id}/ideas/{idea_id}/generate-scenario
POST /api/projects/{project_id}/scenarios/{scenario_id}/generate-prompts
POST /api/projects/{project_id}/scenarios/{scenario_id}/create-asset-slots
POST /api/projects/{project_id}/render-jobs
POST /api/projects/{project_id}/content-items/{content_id}/approve
POST /api/projects/{project_id}/content-items/{content_id}/create-export-package
POST /api/projects/{project_id}/publications/{publication_id}/mark-published
POST /api/projects/{project_id}/metrics/import-csv
```

---

## 18. MVP deployment model

MVP may run as a local or private internal application.

Possible setup:

```text
Web app
Backend API
Database
Local/S3-compatible storage
Worker process
Render engine
```

For local-first MVP:

```text
single machine
local database
local storage
local render worker
manual backups
```

For private server MVP:

```text
single VPS
PostgreSQL
object storage or mounted volume
background worker
reverse proxy
basic auth or private access
```

Public SaaS deployment is future scope.

---

## 19. Observability MVP

Even internal MVP should have basic observability.

Minimum:

```text
application logs
worker logs
render job logs
error records
last updated timestamps
job status history
```

Useful later:

```text
structured logs
metrics dashboard
alerts
trace IDs
audit log
```

Render failures must be visible in Production and Dashboard.

---

## 20. Backup and data safety

MVP should protect project data and generated assets.

Minimum:

```text
regular database backup
regular storage backup
exportable project folder
safe archive behavior instead of hard delete
```

Delete behavior should be conservative.

Recommended pattern:

```text
archive first
hard delete later only when explicitly needed
```

---

## 21. Future SaaS readiness

Architecture should allow future SaaS expansion, but not implement it prematurely.

Future additions may include:

```text
User accounts
Workspace memberships
Roles and permissions
Billing and subscriptions
Plan limits
Public onboarding
Template marketplace
External brand onboarding
API keys
Multi-tenant storage separation
```

Current MVP should only preserve clean boundaries:

```text
workspace_id
project_id
project-scoped storage
project-scoped settings
platform-level templates
no project-specific hardcode
```

---

## 22. MVP architecture checklist

Before implementation, verify:

- [ ] Project entity exists.
- [ ] Workspace can be represented, even if single internal workspace.
- [ ] Brand Profile is project-scoped.
- [ ] Every project-level entity has `project_id`.
- [ ] Assets are stored in project-scoped folders.
- [ ] Scenarios load Brand Profile before generation.
- [ ] Render Jobs save input snapshots.
- [ ] Production Templates are not project-hardcoded.
- [ ] Content Items go to human review before publishing.
- [ ] Export Packages are created only after approval.
- [ ] Publications have their own status separate from Content Item status.
- [ ] Metrics link to Publication and Project.
- [ ] Dashboard aggregates state and does not own business logic.
- [ ] Autoposting is optional / future.
- [ ] Built-in image/video generation API is optional / future.

---

## 23. Out of scope for MVP

Do not implement in MVP without explicit scope change:

```text
public SaaS registration
billing
plans and limits
teams
roles and permissions
marketplace
public onboarding
white-label accounts
complex integrations layer
mandatory autoposting
automatic scraping of every social platform
built-in AI image/video generation APIs
advanced recommendation engine
```

---

## 24. Related documents

This document should be read together with:

```text
docs/01_platform/PLATFORM_OVERVIEW.md
docs/01_platform/PRODUCT_STRATEGY.md
docs/01_platform/MVP_SCOPE.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/02_platform_architecture/DATA_MODEL.md
docs/02_platform_architecture/PIPELINES_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/PUBLISHING_HUB_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/05_product_design/WEB_UI_SPEC.md
docs/06_agents/AGENT_RULES.md
```

---

## 25. Краткий итог

System Architecture Content Plant должна быть:

```text
project-aware
modular
export-first
human-in-the-loop
template-driven
storage-separated
MVP-focused
future-SaaS-ready, but not SaaS-heavy
```

Главная цель архитектуры — дать платформе пройти полный рабочий цикл от идеи до метрик без project-specific hardcode и без преждевременного усложнения.

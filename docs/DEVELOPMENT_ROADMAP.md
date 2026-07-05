# Development Roadmap

## 1. Назначение документа

Этот документ описывает дорожную карту разработки платформы **Content Plant**.

Он фиксирует:

- в каком порядке развивать платформу;
- что входит в первый рабочий MVP;
- какие этапы должны быть завершены до начала production use;
- какие зависимости есть между модулями;
- какие критерии готовности использовать;
- какие функции откладываются на future iterations;
- как не превратить MVP в преждевременный SaaS.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главный принцип roadmap

Content Plant должен развиваться как **вертикальный рабочий срез**, а не как коллекция недостроенных экранов.

Правильный подход:

```text
One project
→ Brand Profile
→ Idea
→ Scenario
→ Assets
→ Production
→ Review
→ Export
→ Publication
→ Metrics
```

Неправильный подход:

```text
Many screens
+ no working pipeline
+ no clear status flow
+ no measurable output
```

Первый MVP должен доказать, что платформа может провести хотя бы один content item от идеи до метрик.

---

## 3. Roadmap horizons

Разработка делится на несколько горизонтов.

```text
Foundation
→ MVP Vertical Slice
→ Multi-format Production
→ Analytics Loop
→ Automation Expansion
→ SaaS Readiness
```

### 3.1. Foundation

Цель: создать документационную, архитектурную и модельную базу.

### 3.2. MVP Vertical Slice

Цель: собрать первый полный production loop для одного или нескольких внутренних проектов.

### 3.3. Multi-format Production

Цель: расширить производство на несколько универсальных форматов.

### 3.4. Analytics Loop

Цель: связать публикации с метриками и решениями.

### 3.5. Automation Expansion

Цель: постепенно автоматизировать публикацию, импорт метрик и batch operations.

### 3.6. SaaS Readiness

Цель: подготовить архитектуру к внешним пользователям, но не раньше доказанной внутренней пользы.

---

## 4. Roadmap rules

### 4.1. Documentation-first

Крупные изменения сначала фиксируются в документации.

Нельзя добавлять:

- новую сущность без `DATA_MODEL.md`;
- новый pipeline без `PIPELINES_SPEC.md`;
- новый формат без `FORMAT_*.md`;
- новый модуль без module spec;
- новую интеграцию без `INTEGRATIONS_SPEC.md`.

---

### 4.2. Project-aware by default

Все project-level данные должны быть scoped by `project_id`.

Это относится к:

- ideas;
- scenarios;
- assets;
- render jobs;
- content items;
- publications;
- metrics;
- CTA;
- settings;
- platform accounts.

---

### 4.3. Human review before publication

На MVP автоматическая генерация не должна обходить human review.

Контент может попасть в Publishing Hub только после статуса:

```text
approved
```

---

### 4.4. Export-first

MVP не должен зависеть от автопостинга.

Сначала:

```text
Export package
→ Manual publishing
→ Published URL
→ Manual / CSV metrics
```

Потом:

```text
Platform API publishing
→ Automatic URL capture
→ Automatic metrics import
```

---

### 4.5. Avoid premature SaaS

В MVP не входят:

- public signup;
- billing;
- pricing plans;
- multi-user teams;
- permissions;
- marketplace;
- external onboarding;
- public template store.

Архитектурно эти функции можно учитывать, но не реализовывать в первом рабочем цикле.

---

## 5. Phase 0 — Documentation Foundation

### 5.1. Цель

Создать согласованную документационную базу, чтобы разработка не шла вслепую.

### 5.2. Required documents

Foundation считается закрытым, когда готовы и согласованы:

```text
00_index.md
PLATFORM_OVERVIEW.md
PRODUCT_STRATEGY.md
MVP_SCOPE.md
WORKSPACE_AND_PROJECT_MODEL.md
BRAND_SYSTEM_SPEC.md
AGENT_RULES.md
CONTENT_FORMATS_OVERVIEW.md
USER_WORKFLOWS.md
WEB_UI_SPEC.md
DATA_MODEL.md
PIPELINES_SPEC.md
SYSTEM_ARCHITECTURE.md
```

### 5.3. Acceptance criteria

- Platform documents do not contain project-specific hardcode.
- MVP boundaries are clear.
- Project / Workspace / Brand Profile model is defined.
- Core entities are defined.
- Core pipelines are defined.
- Agent rules are clear.

### 5.4. Output

Documentation baseline that can be used by development agents.

---

## 6. Phase 1 — Core Data and Project Layer

### 6.1. Цель

Создать базовую project-aware систему.

### 6.2. Scope

Входит:

- database schema for core entities;
- Workspace model, even if single internal workspace;
- Project CRUD;
- Project Switcher;
- Project Settings;
- Brand Profile storage;
- CTA Library storage;
- Platform Settings storage;
- project-scoped file paths.

Не входит:

- public user registration;
- teams;
- billing;
- permissions beyond a simple internal user assumption.

### 6.3. Core entities

Minimum:

```text
Workspace
Project
Brand Profile
Project Settings
CTA
Platform Settings
Content Format registry
```

### 6.4. Acceptance criteria

- User can create a project.
- User can switch active project.
- Project has basic settings.
- Project has a Brand Profile.
- All project-level data is saved with `project_id`.
- No module reads or writes project data globally without project scope.

---

## 7. Phase 2 — Idea Bank and Scenario Studio MVP

### 7.1. Цель

Создать первый слой смыслового производства: idea → scenario.

### 7.2. Scope

Входит:

- Idea Bank list;
- Idea detail;
- manual idea creation;
- idea status lifecycle;
- generate scenario from idea;
- scenario list;
- scenario detail;
- scene editor;
- text block editor;
- visual prompt generation;
- caption draft generation;
- basic scenario QA;
- approve scenario.

### 7.3. Core entities

```text
Idea
Scenario
Scene
Text Block
Visual Prompt
Caption Draft
QA Check
```

### 7.4. MVP content types

Minimum:

```text
text_social_post
dialog_miniseries
```

Should-have after vertical slice:

```text
atmospheric_video
dialog_carousel
explainer_carousel
pinterest_pin
```

### 7.5. Acceptance criteria

- User can create an idea manually.
- User can generate a structured scenario from an idea.
- Scenario uses active project's Brand Profile.
- Scenario has scenes or text blocks depending on content type.
- User can generate visual prompts.
- User can approve scenario.
- Scenario can move to asset mapping or text output.

---

## 8. Phase 3 — Asset Library and Asset Mapping

### 8.1. Цель

Позволить пользователю загружать production inputs и связывать их со сценариями.

### 8.2. Scope

Входит:

- asset upload;
- asset metadata extraction;
- asset preview;
- asset type selection;
- asset status lifecycle;
- asset filters;
- link asset to scenario scene;
- asset slot model;
- compatibility checks;
- replace asset flow;
- archive asset flow.

### 8.3. Core entities

```text
Asset
Asset Slot
Asset Mapping
```

### 8.4. Supported asset types MVP

```text
image
video
audio
logo
background
character
template_asset
document
```

### 8.5. Acceptance criteria

- User can upload files into the active project.
- Assets are stored under project-scoped storage path.
- User can link asset to scene or slot.
- System blocks linking assets from another project.
- Scenario can become `ready_to_render` when required slots are filled.

---

## 9. Phase 4 — Production Engine Vertical Video MVP

### 9.1. Цель

Собрать первый working production loop for vertical video.

### 9.2. Scope

Входит:

- render setup screen;
- template selection;
- pre-render validation;
- render job creation;
- worker queue;
- vertical video rendering;
- text overlays;
- basic motion;
- optional audio;
- output file creation;
- metadata creation;
- content item creation;
- output QA.

### 9.3. First supported video formats

Minimum:

```text
dialog_miniseries
```

Next:

```text
atmospheric_video
```

### 9.4. Core entities

```text
Production Template
Render Job
Output File
Content Item
QA Check
```

### 9.5. Acceptance criteria

- User can select approved scenario.
- System validates assets and template.
- Render Job is created.
- Worker creates video output.
- Metadata is saved.
- Content Item is created with status `needs_review`.
- Render failures are visible and actionable.

---

## 10. Phase 5 — Review and QA MVP

### 10.1. Цель

Добавить human-in-the-loop контроль перед export and publishing.

### 10.2. Scope

Входит:

- Review Queue;
- Review Detail;
- preview content;
- show metadata;
- show QA checks;
- approve;
- reject;
- request changes;
- edit caption;
- trigger rerender;
- review notes.

### 10.3. Core entities

```text
Review Decision
QA Check
Content Item
```

### 10.4. Acceptance criteria

- Rendered content appears in Review Queue.
- User can approve or reject content.
- Approved content becomes available for export.
- Rejected content does not appear as ready to publish.
- QA blockers are visible before approval.

---

## 11. Phase 6 — Export and Publishing Hub MVP

### 11.1. Цель

Сделать контент пригодным для ручной или полуавтоматической публикации.

### 11.2. Scope

Входит:

- create export package;
- platform-specific captions;
- UTM generation;
- package download;
- copy caption;
- internal schedule list;
- publication entity;
- mark as published;
- add published URL;
- notes;
- missing URL warnings.

### 11.3. Core entities

```text
Export Package
Caption Variant
Publication
UTM Link
```

### 11.4. Supported platforms MVP

```text
tiktok
instagram
youtube_shorts
telegram
vk
threads
pinterest
```

These platforms may be supported as export targets before any API posting integration exists.

### 11.5. Acceptance criteria

- Approved Content Item can create export package.
- Export package contains required files.
- User can create Publication for a platform.
- User can schedule publication internally.
- User can mark publication as published.
- User can add published URL.
- Published publication becomes eligible for metrics.

---

## 12. Phase 7 — Text Social Posts MVP

### 12.1. Цель

Создать быстрый text-output pipeline for text-first platforms.

This is the safest first implementation loop and should be stabilized before `dialog_miniseries` and other video formats become mandatory for MVP delivery.

### 12.2. Scope

Входит:

- generate text posts from idea;
- generate text posts from scenario;
- platform-specific versions;
- edit text;
- approve text content;
- export text bundle;
- schedule text publication;
- manual metrics.

### 12.3. Supported platforms MVP

```text
telegram
threads
vk
```

### 12.4. Core entities

```text
Scenario
Text Block
Content Item
Caption Variant
Export Package
Publication
```

### 12.5. Acceptance criteria

- User can generate text social posts for enabled platforms.
- Texts follow Brand Profile.
- Text outputs can be reviewed.
- Text bundle can be exported.
- Text publications can be scheduled and marked as published.

---

## 13. Phase 8 — Basic Analytics MVP

### 13.1. Цель

Закрыть первую feedback loop: публикация → метрики → выводы.

### 13.2. Scope

Входит:

- manual metrics input;
- CSV import;
- metric snapshots;
- top content table;
- weak content table;
- performance by platform;
- performance by content type;
- performance by topic;
- performance by CTA;
- simple derived metrics;
- missing metrics warnings;
- create idea from analytics insight.

### 13.3. Core entities

```text
Metric Snapshot
Analytics Summary
Performance Insight
Optimization Recommendation
Idea
```

### 13.4. Acceptance criteria

- User can add metrics to published publication.
- System can store multiple snapshots per publication.
- Dashboard shows recent performance.
- Analytics can identify top and weak content.
- User can create a new idea from an insight.

---

## 14. Phase 9 — Multi-format Expansion

### 14.1. Цель

Расширить production beyond the first vertical video pipeline.

### 14.2. Formats

Add production support for:

```text
atmospheric_video
dialog_carousel
explainer_carousel
pinterest_pin
```

### 14.3. Scope

For each format:

- generation support in Scenario Studio;
- asset requirements;
- template;
- production pipeline;
- QA checks;
- export package;
- publishing adaptation;
- analytics grouping.

### 14.4. Acceptance criteria

- Each format has a working end-to-end path.
- Each format uses Brand Profile and Project Settings.
- Each format can be reviewed, exported, published and measured.
- No format contains project-specific hardcode.

---

## 15. Phase 10 — Trend Radar MVP

### 15.1. Цель

Создать controlled intake for market signals and trend references.

### 15.2. Scope

Входит:

- manual trend link input;
- CSV import;
- trend card;
- source platform;
- hook analysis;
- topic extraction;
- structure extraction;
- emotional trigger;
- visual pattern notes;
- adaptation idea;
- send to Idea Bank.

### 15.3. Does not include in MVP

- full platform scraping;
- unstable unofficial APIs;
- full automatic social monitoring;
- legal-risk data collection.

### 15.4. Acceptance criteria

- User can add trend manually.
- User can import trends via CSV.
- System can analyze trend into structured fields.
- User can create Idea from trend.
- Trend remains linked to Idea and later content.

---

## 16. Phase 11 — Automation Expansion

### 16.1. Цель

Reduce manual work after the core loop is proven.

### 16.2. Candidate automations

- batch scenario generation;
- batch render;
- automatic text post scheduling;
- CSV metric import mapping;
- platform API publishing where stable;
- platform API metrics import where stable;
- weekly report generation;
- recurring optimization suggestions.

### 16.3. Rule

Automation can be added only when the manual workflow is already working and documented.

---

## 17. Phase 12 — SaaS Readiness

### 17.1. Цель

Prepare for external users after internal validation.

### 17.2. Candidate areas

- user accounts;
- teams;
- roles;
- permissions;
- billing;
- plans;
- onboarding;
- workspace invitations;
- template marketplace;
- public project templates;
- integration setup wizard.

### 17.3. Rule

SaaS readiness is not SaaS implementation.

MVP may keep architecture compatible with future SaaS, but should not build unused SaaS features early.

---

## 18. Suggested implementation order

Recommended order:

```text
1. Core project layer
2. Brand Profile / Project Settings
3. Idea Bank
4. Scenario Studio basic
5. Text Social Posts
6. QA and Review
7. Export Package
8. Publishing Hub manual flow
9. Manual metrics
10. Dashboard summary
11. Asset Library basic
12. Asset mapping
13. Production Engine for dialog_miniseries
14. Atmospheric Video
15. Carousels
16. Pinterest Pins
17. Trend Radar MVP
18. Analytics recommendations
19. Batch production
20. API integrations
```

This order prioritizes a working loop over feature breadth.

---

## 19. MVP 1.0 definition of done

MVP 1.0 is done when Content Plant can support this full flow:

```text
Create Project
→ Fill Brand Profile
→ Create Idea
→ Generate Scenario
→ Generate Visual Prompts
→ Upload Assets
→ Link Assets
→ Render Video
→ Review
→ Approve
→ Export Package
→ Create Publication
→ Mark Published
→ Add Metrics
→ See Performance Summary
→ Create New Idea from Insight
```

### 19.1. Required outputs

- at least one vertical video output;
- at least one text social post bundle;
- at least one export package;
- at least one publication record;
- at least one metrics snapshot;
- at least one dashboard summary.

### 19.2. Required controls

- project separation;
- brand profile application;
- human review;
- export-first publishing;
- manual metrics input;
- basic QA.

---

## 20. Out of scope for MVP 1.0

Not included:

- public SaaS registration;
- billing;
- teams;
- permissions;
- template marketplace;
- full TikTok / Instagram autoposting;
- full automated trend scraping;
- built-in AI image generation;
- built-in AI video generation;
- complex attribution engine;
- autonomous optimization without user approval;
- multi-tenant production scaling.

---

## 21. Risk management

### 21.1. Risk: platform becomes project-specific

Mitigation:

- use Brand Profile;
- avoid hardcoded project values;
- require project_id on project data;
- keep project docs separate.

### 21.2. Risk: too many formats before one works

Mitigation:

- finish one full vertical slice first;
- add formats after export and analytics work.

### 21.3. Risk: API dependencies slow MVP

Mitigation:

- export-first;
- manual metrics;
- CSV import;
- API integrations later.

### 21.4. Risk: UI becomes a dashboard museum

Mitigation:

- every dashboard block must lead to an action;
- prioritize Next Actions over decorative charts.

### 21.5. Risk: generated content quality is low

Mitigation:

- keep human review;
- keep scenario editing;
- support asset replacement;
- support rerender;
- capture weak content signals.

---

## 22. Roadmap update rules

This roadmap should be updated when:

- MVP scope changes;
- a new module becomes priority;
- a new content format is added;
- API integration becomes required;
- internal validation results change priorities;
- SaaS direction becomes active.

Every roadmap update should include:

```text
reason
changed phase
new priority
impact on MVP
related documents
```

---

## 23. Open questions

To resolve later:

1. Which render technology will be used first for vertical videos?
2. Should file storage start local-only or S3-compatible from the beginning?
3. Which text platform should be automated first after export flow is stable?
4. What is the minimum dashboard needed before Analytics module is complete?
5. Should batch production be introduced before or after Trend Radar MVP?
6. How many projects should be used for internal validation before considering SaaS readiness?

# Pipelines Spec

## 1. Назначение документа

Этот документ описывает основные производственные пайплайны платформы **Content Plant**.

Он фиксирует:

- как контент проходит путь от идеи до публикации и метрик;
- какие сущности участвуют в каждом пайплайне;
- какие статусы используются;
- какие шаги выполняются автоматически;
- какие шаги остаются за человеком в MVP;
- где используются QA, Review, Production Engine, Publishing Hub и Analytics;
- какие ошибки и blockers должны обрабатываться;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главный принцип пайплайнов

Content Plant должен работать как связанный контентный конвейер, а не как набор отдельных генераторов.

Базовая логика:

```text
Idea
→ Scenario
→ Assets
→ Production
→ QA
→ Review
→ Export
→ Publication
→ Metrics
→ Optimization
```

Каждый этап должен:

- иметь понятный вход;
- создавать или обновлять конкретные сущности;
- менять статус сущностей;
- показывать следующий шаг;
- не терять project scope;
- сохранять metadata для аналитики и воспроизводимости.

---

## 3. Source of truth

Пайплайны используют сущности, описанные в:

```text
docs/02_platform_architecture/DATA_MODEL.md
```

Этот документ описывает **движение сущностей**, а не их полную структуру.

Если есть конфликт:

1. `MVP_SCOPE.md` определяет, входит ли функция в MVP.
2. `DATA_MODEL.md` определяет поля и связи сущностей.
3. `PIPELINES_SPEC.md` определяет порядок переходов.
4. Module specs определяют детали конкретного модуля.

---

## 4. Global pipeline overview

Главный полный цикл:

```text
Project selected
→ Brand Profile loaded
→ Idea created or imported
→ Scenario generated
→ Visual prompts generated
→ Asset slots created
→ Assets uploaded and linked
→ Render job created
→ Output files created
→ Content item created
→ Automated QA
→ Human review
→ Export package created
→ Publication scheduled or exported
→ Publication marked as published
→ Metrics added or imported
→ Analytics summary updated
→ New ideas or optimization recommendations created
```

На MVP этот цикл может быть частично ручным, но все ключевые связи должны сохраняться.

---

## 5. Pipeline stages

Канонические стадии:

```text
project_setup
idea
scenario
asset_preparation
production
qa
review
export
publication
metrics
optimization
```

Эти стадии могут использоваться в Dashboard, filters, logs и analytics grouping.

---

## 6. Project setup pipeline

### 6.1. Цель

Создать рабочий проект, у которого есть настройки, Brand Profile и минимальная готовность к генерации контента.

### 6.2. Flow

```text
Create Project
→ Fill Project Settings
→ Create / edit Brand Profile
→ Configure platforms
→ Add CTA Library
→ Add links and UTM defaults
→ Mark project active
```

### 6.3. Input

```text
project_name
project_slug
default_language
primary_url
target_platforms
```

### 6.4. Output

Создаются или обновляются:

```text
Project
Project Settings
Brand Profile
Platform Settings
CTA Library
```

### 6.5. MVP manual steps

В MVP пользователь вручную заполняет:

- project basics;
- audience summary;
- tone of voice;
- visual identity;
- CTA;
- platform settings;
- links.

### 6.6. Completion condition

Проект готов к production, если:

- Project status = `active`;
- Brand Profile has required MVP fields;
- at least one target platform is enabled;
- at least one content format is supported;
- generation can access project settings.

---

## 7. Idea creation pipeline

### 7.1. Цель

Создать или импортировать идею, которую можно превратить в сценарий.

### 7.2. Flow

```text
Create / import idea
→ Assign project_id
→ Add topic and funnel stage
→ Select suggested content type
→ Save as raw or approved
→ Send to Scenario Studio
```

### 7.3. Input sources

Идея может прийти из:

```text
manual_input
trend_radar
analytics_recommendation
content_strategy
repurpose_request
csv_import
```

### 7.4. Created / updated entities

```text
Idea
Topic, optional
Hook, optional
Trend linkage, optional
```

### 7.5. Idea statuses

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

### 7.6. Status transitions

```text
raw → approved
approved → scripted
scripted → waiting_assets
waiting_assets → in_production
in_production → ready
ready → scheduled
scheduled → published
published → analyzed
any active status → archived
```

### 7.7. Blockers

Идея не может перейти в сценарий, если:

- missing `project_id`;
- missing title or description;
- unsupported suggested content type;
- project is archived or paused;
- Brand Profile is critically incomplete.

---

## 8. Trend to Idea pipeline

### 8.1. Цель

Преобразовать рыночный сигнал или тренд в пригодную идею.

### 8.2. Flow MVP

```text
User adds trend link or CSV row
→ Trend record created
→ User adds notes or available metrics
→ System analyzes hook, topic and structure
→ System suggests adaptation
→ User approves adaptation
→ Idea created
```

### 8.3. Input

```text
platform
url
caption
transcript, optional
metrics, optional
notes
```

### 8.4. Output

```text
Trend
Idea
Hook, optional
Topic, optional
```

### 8.5. Automation level MVP

MVP supports:

- manual link input;
- CSV import;
- LLM-assisted trend interpretation;
- manual approval before idea creation.

MVP does not require:

- continuous scraping;
- full automatic market scanning;
- unsupported platform APIs;
- automatic copying of third-party content.

---

## 9. Idea to Scenario pipeline

### 9.1. Цель

Преобразовать идею в структурированный сценарий для выбранного content type.

### 9.2. Flow

```text
Open approved idea
→ Select content type
→ Load Brand Profile
→ Load Format Spec
→ Select target platforms
→ Select funnel stage
→ Select CTA or CTA intensity
→ Generate scenario draft
→ Run Scenario QA
→ User edits or approves
→ Scenario status updated
```

### 9.3. Input

```text
Idea
Project Settings
Brand Profile
Content Format Spec
CTA Library
Target Platforms
Funnel Stage
User Notes, optional
```

### 9.4. Output

```text
Scenario
Scenes or Text Blocks
Visual Prompts, optional
Caption Drafts, optional
CTA linkage
QA Checks
```

### 9.5. Scenario statuses

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

### 9.6. Recommended transitions

```text
draft → needs_review
needs_review → approved
approved → needs_assets
needs_assets → ready_to_render
ready_to_render → in_production
in_production → rendered
needs_review → rejected
any active status → archived
```

### 9.7. MVP human decisions

Human review is required before:

- sending scenario to production;
- using generated text as final content;
- publishing output.

In MVP, scenario approval can be lightweight but should be explicit.

---

## 10. Scenario to Visual Prompts pipeline

### 10.1. Цель

Создать visual prompts для внешней генерации изображений или видео.

### 10.2. Flow

```text
Scenario approved or drafted
→ For each scene / slide requiring visual
→ Load Brand Profile visual settings
→ Load format visual rules
→ Generate visual prompt
→ User copies prompt to external tool
→ User generates asset externally
→ User uploads asset to Asset Library
```

### 10.3. Created entities

```text
Visual Prompt
Asset Slot
```

### 10.4. Prompt status values

```text
draft
ready
copied
used
archived
```

### 10.5. MVP boundary

MVP generates prompts but does not require built-in image or video generation through API.

---

## 11. Scenario to Asset Slots pipeline

### 11.1. Цель

Определить, какие ассеты нужны для production.

### 11.2. Flow

```text
Scenario approved
→ Format rules checked
→ Required asset slots created
→ Slots shown in scenario detail or asset mapping UI
→ User uploads or selects assets
→ Assets linked to slots
→ Compatibility checks run
→ Scenario becomes ready_to_render
```

### 11.3. Asset Slot statuses

```text
empty
linked
invalid
approved
rejected
optional
```

### 11.4. Compatibility checks

При привязке asset к slot нужно проверить:

- asset has same `project_id`;
- asset file exists;
- asset type matches required type;
- aspect ratio is compatible or can be adapted;
- duration is compatible, if video/audio;
- asset status is not archived/deleted/rejected.

### 11.5. Completion condition

Scenario can become `ready_to_render` when all required asset slots are:

```text
linked or approved
```

Optional slots may remain empty.

---

## 12. Asset upload pipeline

### 12.1. Цель

Загрузить и зарегистрировать файлы, которые будут использоваться в production.

### 12.2. Flow

```text
User selects project
→ Opens Asset Library or scenario asset mapping
→ Uploads files
→ Selects asset type
→ Adds tags, optional
→ Links to scenario / scene, optional
→ System validates files
→ Metadata extracted
→ Asset saved
→ Asset available for project
```

### 12.3. Created entities

```text
Asset
QA Check, optional
Asset Slot linkage, optional
```

### 12.4. Asset statuses

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

### 12.5. Blockers

Upload or linking should fail if:

- file type unsupported;
- file cannot be saved;
- project_id missing;
- asset belongs to another project;
- asset is deleted or failed.

---

## 13. Production pipeline: vertical video

### 13.1. Цель

Собрать вертикальное видео из сценария, ассетов, Brand Profile и production template.

### 13.2. Flow

```text
Scenario ready_to_render
→ User opens render setup
→ System loads Production Template
→ System loads Brand Profile
→ System loads linked assets
→ Pre-render QA runs
→ Render Job created
→ Worker renders output
→ Output files saved
→ Metadata created
→ Content Item created
→ Output QA runs
→ Content Item status = needs_review
```

### 13.3. Input

```text
Scenario
Scenes
Asset mappings
Brand Profile
Production Template
Output Spec
CTA
Target Platforms
```

### 13.4. Output

```text
Render Job
Output Files
Content Item
QA Checks
Metadata
```

### 13.5. Render Job statuses

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

### 13.6. Content Item default status

After successful render:

```text
needs_review
```

Production Engine must not mark generated content as approved automatically.

### 13.7. MVP rendering rules

MVP should support:

- 9:16 vertical output;
- scene order;
- image/video backgrounds;
- overlay text;
- basic transitions;
- optional logo placement;
- optional audio;
- metadata output.

MVP does not require:

- complex timeline editor;
- automatic image generation;
- automatic motion generation through external video APIs;
- advanced multi-user approval.

---

## 14. Production pipeline: text social posts

### 14.1. Цель

Создать export-ready текстовые посты из идеи, сценария или content item.

### 14.2. Flow

```text
User selects source idea / scenario / content item
→ Selects target platforms
→ System loads Brand Profile and platform rules
→ Text posts generated
→ QA checks length, CTA and forbidden phrases
→ User reviews or edits
→ Text bundle created
→ Export package or publication draft created
```

### 14.3. Input

```text
source_type
source_id
project_id
platforms
Brand Profile
CTA Library
Platform Settings
```

### 14.4. Output

```text
Text Blocks or Text Post records
Caption Variants
Export Package, optional
Publication Drafts, optional
```

### 14.5. MVP target platforms

MVP may support text output for:

```text
telegram
threads
vk
```

The list can be extended through Platform Settings.

---

## 15. Production pipeline: carousel

### 15.1. Цель

Собрать карусель из сценария, text blocks, slides and assets.

### 15.2. MVP status

Carousel production is should-have unless explicitly moved into MVP implementation plan.

### 15.3. Flow

```text
Scenario or idea selected
→ Carousel format selected
→ Slide structure generated
→ Brand Profile loaded
→ Assets or template backgrounds linked
→ Slide QA runs
→ Images rendered
→ Export package created
→ Review required
```

### 15.4. Output

```text
slide_01.png
slide_02.png
...
caption.txt
metadata.json
```

---

## 16. QA pipeline

### 16.1. Цель

Проверять контент на разных этапах и не выпускать критически сломанные материалы.

### 16.2. QA stages

```text
Scenario QA
Asset QA
Pre-render QA
Output QA
Publishing QA
Analytics QA
```

### 16.3. Flow

```text
Entity created or updated
→ Relevant QA checks selected
→ Checks executed
→ QA results saved
→ Blockers update next available actions
→ User sees warnings or errors
```

### 16.4. QA severity levels

```text
info
warning
error
blocker
```

### 16.5. Blocker behavior

If severity = `blocker`, the system should disable the next destructive or irreversible action.

Examples:

- missing required asset blocks render;
- missing output file blocks review approval;
- unapproved content blocks schedule/publish;
- missing platform blocks publication creation.

---

## 17. Review pipeline

### 17.1. Цель

Дать человеку финальный контроль перед export and publication.

### 17.2. Flow

```text
Content Item status = needs_review
→ User opens Review Queue
→ User checks preview, caption, QA and metadata
→ User approves, rejects, or requests changes
→ System records Review Decision
→ Content Item status updated
```

### 17.3. Review decisions

```text
approved
rejected
changes_requested
```

### 17.4. Content Item status transitions

```text
needs_review → approved
needs_review → rejected
needs_review → changes_requested
changes_requested → needs_review, after rerender or edit
approved → exported
approved → archived
```

### 17.5. MVP review actions

```text
Approve
Reject
Edit caption
Replace asset
Rerender
Export
```

### 17.6. Human review rule

Content must not enter Publishing Hub as ready-to-publish unless it has been approved by a human or explicitly marked with an approved override policy.

For MVP, explicit human approval is required.

---

## 18. Export package pipeline

### 18.1. Цель

Подготовить platform-ready files and metadata for publication.

### 18.2. Boundary decision

Production Engine creates base output files.

Publishing Hub creates platform-ready export packages.

Canonical separation:

```text
Production Engine:
  render output + base metadata
  technical QA result

Publishing Hub:
  platform captions + package structure + UTM + publishing checklist
```

### 18.3. Flow

```text
Content Item approved
→ User selects export action
→ Target platforms selected
→ Caption variants created or loaded
→ UTM links generated, if needed
→ Files copied or referenced into export package
→ metadata.json created
→ Export Package status = ready
```

### 18.4. Export Package statuses

```text
creating
ready
incomplete
failed
archived
```

### 18.5. Output examples

Video package:

```text
exports/{project_slug}/{content_id}/
  video.mp4
  caption_{platform}.txt
  metadata.json
  cover.txt or cover.png
```

Text package:

```text
exports/{project_slug}/{content_id}/
  telegram.txt
  threads.txt
  vk.txt
  metadata.json
```

Carousel package:

```text
exports/{project_slug}/{content_id}/
  slides/
    slide_01.png
    slide_02.png
  caption.txt
  metadata.json
```

---

## 19. Publishing pipeline: manual / export-first

### 19.1. Цель

Позволить пользователю опубликовать контент вручную, не теряя связи с системой.

### 19.2. Flow MVP

```text
Approved Content Item
→ Export Package ready
→ Publication draft created
→ User downloads package or copies caption
→ User publishes manually on platform
→ User returns to Content Plant
→ Marks Publication as published
→ Adds published URL
→ Metrics task created
```

### 19.3. Publication statuses

```text
draft
ready
scheduled
published
failed
cancelled
archived
```

### 19.4. Required before ready

Publication can become `ready` only if:

- content item is approved;
- target platform is selected;
- export package is ready;
- caption exists;
- UTM exists if link is used;
- required files exist.

### 19.5. MVP boundary

MVP does not require full autoposting.

Manual and semi-automatic publishing are acceptable if:

- export package is reliable;
- publication record exists;
- published URL can be stored;
- metrics can be linked later.

---

## 20. Publishing pipeline: scheduling

### 20.1. Цель

Планировать публикации во внутреннем календаре, даже если actual posting remains manual.

### 20.2. Flow

```text
User selects approved content
→ Selects platform
→ Selects date/time
→ Selects caption variant
→ Creates scheduled publication
→ Calendar displays item
→ User publishes at planned time
→ User marks as published
```

### 20.3. Schedule rules

- Scheduling does not imply autoposting in MVP.
- Scheduled publication must stay project-scoped.
- Calendar must not mix projects unless workspace-level view is explicitly enabled.

---

## 21. Metrics pipeline

### 21.1. Цель

Связать опубликованный контент с результатами.

### 21.2. Flow MVP

```text
Publication status = published
→ System marks item as needs metrics
→ User enters metrics manually or imports CSV
→ Metric Snapshot created
→ Dashboard updates recent metrics
→ Analytics groups performance by platform, format, topic, CTA and campaign
```

### 21.3. Input methods MVP

```text
manual_input
csv_import
```

Future:

```text
platform_api_import
website_event_tracking
conversion_api
```

### 21.4. Metric Snapshot fields

Minimum:

```text
publication_id
project_id
platform
captured_at
views
likes
comments
shares
saves
profile_visits
link_clicks
conversions
revenue
```

Fields may be null if unavailable.

### 21.5. Analytics QA

Analytics QA should warn when:

- published item has no published URL;
- published item has no metrics after configured time;
- required metrics are missing;
- revenue fields are invalid;
- publication cannot be linked to content item.

---

## 22. Optimization pipeline

### 22.1. Цель

Использовать результаты публикаций для следующего цикла контента.

### 22.2. MVP boundary

MVP does not require complex AI optimizer.

MVP may support simple rules and dashboard insights.

### 22.3. Flow

```text
Metric Snapshots collected
→ Analytics summary updated
→ Top and weak content identified
→ User reviews insights
→ New ideas or experiment suggestions created
```

### 22.4. Example recommendation types

```text
repeat_topic
create_variation
scale_format
reduce_format
change_cta
change_platform
rerun_hook
archive_pattern
```

### 22.5. Human control

Recommendations should not automatically change production plans in MVP.

The user approves what enters Idea Bank or next production batch.

---

## 23. Repurpose pipeline

### 23.1. Цель

Переиспользовать один смысл в нескольких форматах.

### 23.2. Flow

```text
Source Idea / Scenario / Content Item selected
→ Target formats selected
→ Brand Profile loaded
→ Format specs loaded
→ New scenario, text post, carousel or pin generated
→ Source linkage saved
→ QA and review required
```

### 23.3. Source linkage

Repurposed content should store:

```text
source_type
source_id
source_content_id, if applicable
parent_scenario_id, if applicable
```

### 23.4. MVP minimum

Minimum repurpose flow:

```text
Scenario
→ vertical video
→ caption
→ text social posts
```

Should-have:

```text
Scenario
→ carousel
→ pin
```

---

## 24. Batch production pipeline

### 24.1. Цель

Создавать несколько content items в одном controlled run.

### 24.2. MVP status

Batch production is should-have, not required for first working vertical slice.

### 24.3. Flow

```text
User selects multiple approved scenarios
→ System checks readiness
→ Batch record created
→ Render jobs queued
→ Results grouped
→ QA and review queue updated
→ Export packages created after approval
```

### 24.4. Batch statuses

```text
draft
queued
running
partially_completed
completed
failed
cancelled
archived
```

---

## 25. Error handling principles

### 25.1. Errors must be actionable

Bad:

```text
Render failed.
```

Good:

```text
Render failed because Scene 3 has no linked asset. Upload or link an asset and retry.
```

### 25.2. Error fields

Each blocking failure should store:

```text
entity_type
entity_id
stage
severity
message
recommendation
created_at
```

This can be represented as QA Check, job error, or system notification depending on context.

### 25.3. Retry rules

Retry should be possible for:

- failed render job;
- failed export package creation;
- failed metrics import;
- failed publication API call, future.

Retry should not duplicate content items unless explicitly configured.

---

## 26. Status ownership

Different statuses belong to different entities.

| Entity | Owns statuses for |
|---|---|
| Idea | editorial readiness of idea |
| Scenario | scenario preparation and asset readiness |
| Asset Slot | whether required asset is linked and valid |
| Render Job | technical render progress |
| Content Item | readiness of generated output |
| Export Package | package creation and completeness |
| Publication | platform-specific publishing state |
| Metric Snapshot | collected performance data |
| QA Check | result of a specific validation |
| Review Decision | human decision history |

Avoid using one global status for the whole pipeline.

---

## 27. Canonical MVP vertical slice

The first useful MVP slice should be:

```text
Project active
→ Brand Profile complete enough
→ Idea created
→ Scenario / Draft generated
→ Text social post draft generated
→ QA checks completed
→ Human approves
→ Export package ready
→ Publication manually published
→ Metrics manually added
→ Insight created
→ New Idea linked
```

This vertical slice proves the platform can move one content item through the full loop without depending on video rendering, autoposting or external media APIs.

---

## 28. What is not required in MVP pipelines

MVP pipelines should not require:

- public user registration;
- billing;
- roles and permissions;
- marketplace;
- full autoposting to every platform;
- automatic image or video generation through API;
- complex multi-touch revenue attribution;
- fully autonomous strategy optimizer;
- advanced workflow automations for teams.

These can be added later if the internal production loop works.

---

## 29. Dashboard implications

Dashboard should derive operational blocks from pipeline state.

Examples:

```text
Ideas waiting for scenarios
Scenarios waiting for assets
Assets invalid
Render jobs failed
Content waiting for review
Approved content waiting for export
Scheduled publications due soon
Published items missing metrics
Top content this period
Weak content this period
```

Dashboard should not create separate truth. It aggregates pipeline state from source entities.

---

## 30. Pipeline logging

For debugging and future analytics, major transitions should be logged.

Minimum event fields:

```json
{
  "event_id": "event_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "entity_type": "scenario",
  "entity_id": "scenario_001",
  "event_type": "status_changed",
  "from_status": "needs_assets",
  "to_status": "ready_to_render",
  "created_at": ""
}
```

MVP may store simplified logs, but the architecture should not lose state transition history completely.

---

## 31. Open decisions

The following decisions should be finalized during implementation planning:

1. Whether Scenario approval is mandatory before visual prompts or only before production.
2. Whether Content Item can have multiple output variants under one content_id or each platform variant becomes separate content item.
3. How detailed pipeline logging should be in the first implementation.
4. Whether carousel production is included in first MVP slice or second iteration.
5. Whether text social posts are stored as Content Items or as Publication drafts before approval.

---

## 32. MVP acceptance criteria

Pipeline implementation can be considered minimally ready when:

- user can create a project;
- user can define a Brand Profile;
- user can create an idea;
- user can generate or create a scenario;
- scenario can create required asset slots;
- user can upload and link assets;
- system can run a render job;
- render output becomes a content item;
- content item can be reviewed;
- approved content can produce an export package;
- publication can be scheduled or marked as manually published;
- published URL can be saved;
- manual metrics can be added;
- Dashboard can show where content is stuck.

---

## 33. Final principle

The pipeline should make the next action obvious.

At any moment, Content Plant should be able to answer:

```text
What is this item?
Which project does it belong to?
Where is it in the pipeline?
What blocks it?
What can the user do next?
What happened after publication?
What should be repeated or changed?
```

If the system can answer these questions consistently, the content production loop is working.

# Analytics and Optimization Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает модуль **Analytics and Optimization** в платформе **Content Plant**.

Он фиксирует:

- зачем нужен модуль аналитики;
- какие метрики собирает платформа;
- как метрики связываются с публикациями, контентом, идеями и проектами;
- как работает ручной ввод метрик и CSV-import;
- какие отчёты нужны в MVP;
- как система помогает принимать решения по форматам, темам, hooks, CTA и платформам;
- какие оптимизационные выводы можно делать в MVP;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Главная роль Analytics and Optimization

Analytics and Optimization закрывает feedback loop Content Plant.

Без аналитики платформа остаётся производственной машиной.  
С аналитикой она становится системой обучения.

Базовая петля:

```text
Publication
→ Metric Snapshot
→ Performance Summary
→ Insight
→ Optimization Recommendation
→ New Idea / Scenario / Format Decision
```

Главная задача модуля — помогать пользователю понимать:

- какой контент работает;
- какой контент не работает;
- какие форматы стоит масштабировать;
- какие темы стоит повторить;
- какие hooks дают внимание;
- какие CTA дают клики и конверсии;
- какие платформы дают полезный результат;
- какие материалы требуют повторной проверки или прекращения.

---

## 3. Основной принцип

Analytics должен быть **publication-based** и **project-scoped**.

Правильно:

```text
Project
→ Content Item
→ Publication
→ Metric Snapshot
→ Analytics Summary
```

Неправильно:

```text
Global metrics table without project_id or publication_id
```

Метрики не должны жить отдельно от публикаций.  
Каждый показатель должен быть связан минимум с:

```text
project_id
publication_id
platform
snapshot_at
```

Желательно также связывать метрики с:

```text
content_id
content_type
idea_id
scenario_id
campaign_id
cta_id
```

---

## 4. Место в pipeline

Analytics находится после publication.

```text
Idea
→ Scenario
→ Asset
→ Production
→ Review
→ Publishing
→ Metrics
→ Optimization
→ New Ideas
```

В MVP метрики могут добавляться вручную или импортироваться через CSV.

Autopull через API социальных платформ не обязателен для MVP.

---

## 5. Основные задачи модуля

Analytics and Optimization должен позволять:

- видеть список опубликованных материалов без метрик;
- вручную вводить метрики;
- импортировать метрики из CSV;
- хранить metric snapshots;
- показывать performance по публикациям;
- сравнивать результаты по платформам;
- сравнивать результаты по content type;
- сравнивать результаты по topic;
- сравнивать результаты по CTA;
- находить top content;
- находить weak content;
- формировать простые рекомендации;
- отправлять успешные идеи обратно в Idea Bank;
- показывать базовые выводы на Dashboard.

---

## 6. Основные сущности

Модуль использует сущности:

```text
Project
Content Item
Publication
Metric Snapshot
Analytics Summary
Performance Insight
Optimization Recommendation
Idea
Scenario
CTA
Campaign
Experiment
```

Источник истины для сырых метрик:

```text
Metric Snapshot
```

Источник истины для публикаций:

```text
Publication
```

Analytics Summary и Recommendations являются производными данными.

---

## 7. Metric Snapshot

**Metric Snapshot** — это набор метрик публикации в конкретный момент времени.

Одна публикация может иметь несколько snapshots:

```text
24h snapshot
72h snapshot
7d snapshot
30d snapshot
manual correction snapshot
```

Минимальная структура:

```json
{
  "metric_snapshot_id": "metric_snapshot_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "publication_id": "publication_001",
  "content_id": "content_001",
  "platform": "instagram",
  "snapshot_at": "2026-07-05T12:00:00Z",
  "source_type": "manual",
  "views": 0,
  "likes": 0,
  "comments": 0,
  "saves": 0,
  "shares": 0,
  "profile_visits": 0,
  "link_clicks": 0,
  "registrations": 0,
  "purchases": 0,
  "revenue": 0,
  "currency": "",
  "notes": "",
  "created_at": "",
  "updated_at": ""
}
```

---

## 8. Обязательные поля MVP

Для MVP обязательны:

```text
metric_snapshot_id
project_id
publication_id
platform
snapshot_at
source_type
created_at
updated_at
```

Минимальные метрики MVP:

```text
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
```

Допустимо, что часть метрик пустая или недоступна.

Интерфейс должен показывать `not available`, а не подставлять ноль там, где данных нет.

---

## 9. Source types

Метрики могут приходить из разных источников.

Рекомендуемые значения:

```text
manual
csv_import
platform_api
internal_event
estimated
```

### manual

Пользователь вручную ввёл показатели.

### csv_import

Метрики загружены из CSV.

### platform_api

Метрики получены через официальную интеграцию.

Не обязательно для MVP.

### internal_event

Метрика пришла из внутреннего сайта, приложения, CRM или event tracking.

### estimated

Оценочная метрика.

В MVP лучше избегать estimated как основного источника истины.

---

## 10. Metric categories

Метрики делятся на несколько категорий.

### 10.1. Reach metrics

```text
views
impressions
reach
```

Показывают охват.

### 10.2. Engagement metrics

```text
likes
comments
saves
shares
reactions
```

Показывают взаимодействие.

### 10.3. Attention quality metrics

```text
watch_time
average_view_duration
completion_rate
retention_rate
```

Для MVP можно не вводить эти метрики вручную, если они недоступны.

### 10.4. Traffic metrics

```text
profile_visits
link_clicks
landing_visits
```

Показывают переход от платформы к следующему шагу.

### 10.5. Conversion metrics

```text
registrations
leads
purchases
subscription_events
revenue
```

Показывают бизнес-результат.

---

## 11. Platform-specific metrics

Разные платформы дают разные метрики.

Analytics должен поддерживать неполные данные.

Пример:

```text
A short-video platform may provide views, likes, comments, shares.
A text platform may provide views, reactions, replies, link clicks.
A pin platform may provide impressions, saves, outbound clicks.
```

Нельзя требовать одинаковый набор метрик для всех платформ.

Для нормализации можно использовать общие группы:

```text
reach
engagement
traffic
conversion
revenue
```

---

## 12. Derived metrics

Analytics может считать производные показатели.

MVP derived metrics:

```text
engagement_rate
save_rate
share_rate
click_rate
conversion_rate
revenue_per_publication
revenue_per_1000_views
```

Примеры формул:

```text
engagement_rate = (likes + comments + saves + shares) / views
click_rate = link_clicks / views
conversion_rate = purchases / link_clicks
revenue_per_1000_views = revenue / views * 1000
```

Если denominator равен нулю или отсутствует, показатель должен быть `not available`.

---

## 13. Analytics Summary

**Analytics Summary** — агрегированное представление результатов.

Может строиться по:

```text
project
platform
content_type
topic
hook
cta
campaign
period
```

Пример структуры:

```json
{
  "summary_id": "summary_001",
  "project_id": "project_001",
  "period_start": "2026-07-01",
  "period_end": "2026-07-07",
  "group_by": "content_type",
  "items": [
    {
      "key": "dialog_miniseries",
      "publications": 12,
      "views": 120000,
      "link_clicks": 840,
      "purchases": 24,
      "revenue": 0
    }
  ],
  "created_at": ""
}
```

MVP может считать summaries on demand, без отдельного постоянного хранения.

---

## 14. Performance Insight

**Performance Insight** — текстовый или структурированный вывод о данных.

Пример:

```json
{
  "insight_id": "insight_001",
  "project_id": "project_001",
  "period_start": "2026-07-01",
  "period_end": "2026-07-07",
  "insight_type": "format_performance",
  "severity": "info",
  "message": "Text social posts generated fewer views but higher click rate than vertical videos.",
  "related_entity_type": "content_type",
  "related_entity_id": "text_social_post",
  "created_at": ""
}
```

MVP может генерировать insights rule-based, без сложного AI optimizer.

---

## 15. Optimization Recommendation

**Optimization Recommendation** — предлагаемое действие.

Пример:

```json
{
  "recommendation_id": "recommendation_001",
  "project_id": "project_001",
  "period_start": "2026-07-01",
  "period_end": "2026-07-07",
  "type": "scale_topic",
  "priority": "medium",
  "message": "Create more content around this topic because it produced above-average clicks.",
  "target_entity_type": "topic",
  "target_entity_id": "topic_001",
  "suggested_action": "create_ideas",
  "status": "new",
  "created_at": ""
}
```

Recommendation не должна автоматически менять production plan в MVP.  
Пользователь должен подтверждать действия.

---

## 16. Recommendation types

Рекомендуемые типы:

```text
scale_content
scale_topic
scale_hook
scale_content_type
reduce_content_type
revise_cta
revise_topic
repurpose_content
create_variation
collect_missing_metrics
stop_format
```

### scale_content

Повторить или адаптировать успешный content item.

### scale_topic

Создать больше идей по успешной теме.

### scale_hook

Использовать успешный hook pattern в новых сценариях.

### reduce_content_type

Уменьшить долю формата, если он стабильно слабый.

### collect_missing_metrics

Заполнить отсутствующие метрики.

---

## 17. Recommendation statuses

```text
new
accepted
dismissed
converted_to_idea
converted_to_experiment
archived
```

### new

Рекомендация создана и ждёт решения.

### accepted

Пользователь согласился с рекомендацией.

### dismissed

Пользователь отклонил рекомендацию.

### converted_to_idea

Рекомендация превращена в Idea.

### converted_to_experiment

Рекомендация превращена в Experiment.

### archived

Рекомендация скрыта из активной работы.

---

## 18. Manual metrics flow

Главный MVP-сценарий:

```text
1. User opens Analytics or Dashboard warning.
2. System shows published publications without metrics.
3. User opens publication metrics form.
4. User enters available metrics.
5. System validates values.
6. System creates Metric Snapshot.
7. Dashboard and Analytics summaries update.
```

Минимальная форма:

```text
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
notes
snapshot_at
```

---

## 19. CSV import flow

CSV-import нужен, чтобы не вводить метрики по одной публикации.

Flow:

```text
1. User opens CSV Import.
2. Uploads CSV file.
3. System detects columns.
4. User maps columns to metric fields.
5. System matches rows to publications by published_url, publication_id, content_id or platform + date.
6. System previews import.
7. User confirms.
8. System creates Metric Snapshots.
9. System reports imported, skipped and failed rows.
```

---

## 20. CSV fields MVP

Рекомендуемые поля:

```text
publication_id
content_id
published_url
platform
snapshot_at
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

Matching priority:

```text
publication_id
published_url
content_id + platform
platform + published_at + title
```

Если match неоднозначный, строка должна попасть в `needs_manual_match`.

---

## 21. CSV import statuses

```text
uploaded
mapping_required
ready_to_import
importing
imported
partial_failed
failed
archived
```

MVP может хранить import job как lightweight record.

---

## 22. Validation rules

Analytics должен проверять:

- project_id exists;
- publication exists;
- publication belongs to project;
- platform matches publication platform, if provided;
- metric values are non-negative;
- revenue is non-negative;
- snapshot_at is valid;
- source_type is valid;
- duplicate snapshot warning, if same publication and same snapshot_at already exists.

Blockers:

```text
missing publication
wrong project
invalid metric value
invalid date
```

Warnings:

```text
no published URL
zero views
all metrics empty
possible duplicate snapshot
```

---

## 23. Missing metrics logic

Dashboard и Analytics должны показывать материалы без метрик.

Правило:

```text
Publication status = published
AND no Metric Snapshot exists
→ Needs metrics
```

Дополнительно:

```text
Publication status = published
AND published_at older than configured threshold
AND no Metric Snapshot exists
→ Metrics overdue
```

MVP threshold:

```text
72 hours after published_at
```

Project Settings может позволять менять threshold позже.

---

## 24. Top Content

Top Content показывает лучшие материалы за период.

Сортировки MVP:

```text
views
saves
shares
link_clicks
purchases
revenue
click_rate
engagement_rate
```

Поля таблицы:

```text
title
content_type
platform
topic
published_at
views
engagement_rate
link_clicks
purchases
revenue
actions
```

Actions:

```text
open publication
open content item
create variation
repurpose
create idea from content
```

---

## 25. Weak Content

Weak Content показывает материалы, которые требуют внимания.

Признаки:

```text
very low views
low engagement_rate
zero link_clicks
zero conversions
missing metrics
high effort with weak result
```

MVP может использовать простые thresholds.

Пример:

```text
Views below project median by 50%
AND engagement_rate below project median
```

Не нужно считать слабым контент без достаточного периода наблюдения.

---

## 26. Performance by Content Type

Analytics должен показывать performance по `content_type`.

Минимальные groupings:

```text
dialog_miniseries
text_social_post
atmospheric_video
dialog_carousel
explainer_carousel
pinterest_pin
```

Поля:

```text
publications
views
engagement
link_clicks
purchases
revenue
average_click_rate
average_engagement_rate
```

Важно: формат с меньшими views может быть сильнее по clicks или purchases.  
Analytics не должен считать вирусность единственной целью.

---

## 27. Performance by Platform

Analytics должен показывать performance по платформам.

Поля:

```text
platform
publications
views
engagement
profile_visits
link_clicks
purchases
revenue
```

Цель:

- понять, где контент получает охват;
- где получает клики;
- где получает конверсии;
- где стоит продолжать ручную публикацию;
- где нужен другой формат.

---

## 28. Performance by Topic

Topic analysis показывает, какие темы работают.

Источник topic:

```text
Idea.topic
Scenario.topic
Content Item.metadata.topic
```

MVP может использовать topic как free text или tag.

Поля:

```text
topic
content_count
publications
views
saves
shares
link_clicks
purchases
revenue
```

Actions:

```text
create more ideas
create variation
mark as scale candidate
archive weak topic
```

---

## 29. Performance by Hook

Hook analysis помогает понять, какие opening patterns дают результат.

Источник hook:

```text
Idea.hook_text
Scenario.hook
Content Item.metadata.hook
```

MVP может хранить hook как text field.

В будущем можно добавить hook pattern classification.

Поля:

```text
hook_text
content_count
views
engagement_rate
click_rate
purchases
```

---

## 30. Performance by CTA

CTA analysis показывает, какие призывы к действию работают.

Источник CTA:

```text
CTA entity
Scenario.cta_id
Caption Variant.cta_id
Publication.caption_id
```

Поля:

```text
cta_id
label
intent
intensity
publications
link_clicks
registrations
purchases
revenue
click_rate
conversion_rate
```

Важно: CTA нужно оценивать не только по кликам, но и по downstream conversion, если данные доступны.

---

## 31. Campaign analysis

Campaign используется для группировки публикаций.

Примеры campaign types:

```text
launch
weekly_theme
seasonal
format_test
platform_test
cta_test
```

MVP может поддерживать campaign_id опционально.

Campaign analysis полезен для недельных и месячных отчётов.

---

## 32. Experiment analysis

Experiment помогает сравнивать варианты.

Примеры:

```text
same idea, different hook
same scenario, different CTA
same content item, different platform
same format, different visual style
```

MVP может не иметь полноценного statistical testing.

Достаточно хранить:

```text
experiment_id
hypothesis
variant_a
variant_b
metric_goal
result_notes
```

---

## 33. Optimization loop

Главный optimization flow:

```text
1. Metrics are added to publications.
2. Analytics groups performance by platform, format, topic, hook and CTA.
3. System identifies top and weak patterns.
4. System creates insights.
5. System creates recommendations.
6. User accepts, dismisses or converts recommendations.
7. Accepted recommendations create new ideas, variations or experiments.
```

В MVP recommendations могут быть rule-based.

---

## 34. Rule-based recommendations MVP

MVP-правила могут быть простыми.

### 34.1. Scale content

```text
If content item is in top 10% by link_clicks or purchases
→ recommend repurpose / create variation.
```

### 34.2. Scale topic

```text
If topic has above-average click_rate across at least 3 publications
→ recommend more ideas for this topic.
```

### 34.3. Revise CTA

```text
If content gets good engagement but weak link_clicks
→ recommend testing a different CTA.
```

### 34.4. Collect metrics

```text
If publication is published and has no metrics after threshold
→ recommend adding metrics.
```

### 34.5. Reduce format

```text
If content_type underperforms across reach, engagement and clicks over enough publications
→ recommend reducing its share temporarily.
```

---

## 35. Create Idea from Analytics

Analytics должен уметь создавать Idea на основе успешного результата.

Flow:

```text
1. User opens top content or recommendation.
2. Clicks Create Idea.
3. System creates idea with source_type = analytics_insight.
4. Idea links back to source publication/content item.
5. User edits or approves idea.
```

Idea fields prefilled:

```text
title
description
topic
suggested_content_type
source_type
source_id
priority
```

---

## 36. Repurpose from Analytics

Если публикация успешна, пользователь может создать repurpose tasks.

Examples:

```text
vertical video → text social posts
vertical video → carousel
text post → video scenario
carousel → pin
```

Flow:

```text
1. User opens successful content item.
2. Clicks Repurpose.
3. Selects target content types.
4. System creates ideas or scenarios.
5. New items keep source linkage.
```

---

## 37. Weekly report

Weekly Report — should-have, но полезен рано.

MVP можно сделать как simple generated summary.

Sections:

```text
Published this week
Metrics completeness
Top content
Weak content
Best content types
Best platforms
Best topics
Best CTA
Recommended actions
```

Report не должен быть длинным ради красоты.  
Он должен отвечать:

```text
What worked?
What did not work?
What should be produced next?
```

---

## 38. Dashboard integration

Dashboard должен показывать:

```text
Published this period
Publications missing metrics
Top content this period
Weak content warnings
Best content type
Best platform by clicks
Revenue / conversions, if available
Next actions from recommendations
```

Dashboard не хранит analytics data как source of truth.  
Он получает агрегированные данные из Analytics.

---

## 39. Publishing Hub integration

Publishing Hub передаёт в Analytics:

```text
publication_id
content_id
project_id
platform
published_at
published_url
utm_url
caption_id
status
```

После `status = published` публикация должна попасть в список:

```text
Needs metrics
```

Если `published_url` отсутствует, Analytics может принять manual metrics, но должен показывать warning.

---

## 40. UTM and attribution

Analytics должен учитывать UTM.

Базовые поля:

```text
utm_source
utm_medium
utm_campaign
utm_content
```

Рекомендуемая связь:

```text
utm_content = content_id or publication_id
```

Если сайт или внутренний продукт может передавать conversion events, они должны связываться с publication через UTM.

В MVP допускается ручной ввод:

```text
registrations
purchases
revenue
```

без полной автоматической attribution.

---

## 41. Data completeness

Analytics должен показывать полноту данных.

Примеры warnings:

```text
12 published items have no metrics.
5 published items have no published URL.
3 metric snapshots have no link_clicks value.
Revenue tracking is enabled but revenue is missing for 8 purchases.
```

Completeness score может быть should-have.

MVP достаточно warnings.

---

## 42. Analytics UI

Рекомендуемые экраны:

```text
Analytics Overview
Top Content
Weak Content
By Platform
By Content Type
By Topic
By CTA
Metric Input
CSV Import
Recommendations
```

MVP может объединить это в один экран с секциями.

---

## 43. Analytics Overview

Overview показывает:

```text
Date range selector
Project summary
Published count
Views
Engagement
Link clicks
Conversions
Revenue
Top content
Needs metrics
Recommendations
```

Date range options:

```text
Today
Last 7 days
Last 30 days
Custom
```

Default:

```text
Last 7 days
```

---

## 44. Metric Input UI

Metric Input должен быть быстрым.

Fields:

```text
publication
platform
snapshot_at
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
notes
```

Helpful UI:

```text
copy previous snapshot
mark metric as unavailable
save and next
```

---

## 45. CSV Import UI

CSV Import UI должен показывать:

```text
upload area
column mapping
preview rows
matched publications
unmatched rows
validation errors
confirm import
import summary
```

Import summary:

```text
rows imported
rows skipped
rows failed
rows needing manual match
```

---

## 46. Recommendation UI

Recommendations list fields:

```text
type
priority
message
related entity
suggested action
status
created_at
```

Actions:

```text
accept
dismiss
create idea
create variation
create experiment
archive
```

---

## 47. Permissions

Permissions не входят в MVP.

Future SaaS may introduce roles:

```text
owner
admin
editor
analyst
viewer
```

MVP can assume one internal user.

---

## 48. API principles

Analytics API should be project-scoped.

Examples:

```text
GET /api/projects/:project_id/analytics/overview
GET /api/projects/:project_id/analytics/top-content
GET /api/projects/:project_id/analytics/by-platform
POST /api/projects/:project_id/metric-snapshots
POST /api/projects/:project_id/metric-imports
GET /api/projects/:project_id/recommendations
POST /api/projects/:project_id/recommendations/:id/accept
```

Do not expose global analytics without project scoping in MVP.

---

## 49. MVP scope

Analytics MVP includes:

- manual metric input;
- CSV import basic flow;
- metric snapshots;
- top content table;
- weak content warnings;
- by-platform summary;
- by-content-type summary;
- by-topic summary;
- by-CTA summary, if CTA data exists;
- missing metrics warning;
- simple rule-based recommendations;
- create idea from insight;
- dashboard integration.

---

## 50. Not in MVP

Не входит в MVP:

- full automatic metrics import from all platforms;
- full cross-platform attribution;
- billing analytics;
- multi-user permissions;
- complex statistical experiments;
- advanced AI strategy optimizer;
- automatic production plan changes without approval;
- external SaaS reporting for clients;
- marketplace analytics.

---

## 51. Acceptance criteria

Модуль можно считать готовым для MVP, если:

1. Published publications can be listed as missing metrics.
2. User can manually add metric snapshot.
3. User can import metrics from CSV with basic mapping.
4. Metric snapshots are linked to publication and project.
5. Analytics Overview shows period summary.
6. Top Content table works.
7. Weak Content warnings work.
8. By Platform summary works.
9. By Content Type summary works.
10. Dashboard shows missing metrics and recent results.
11. Successful content can be converted into new Idea.
12. No analytics data leaks across projects.

---

## 52. Open questions

Questions to clarify later:

- Which metrics should be required per platform?
- Should snapshots use fixed windows such as 24h, 72h, 7d?
- Should revenue be tracked manually, imported from website events, or both?
- How should Content Plant attribute conversions if several publications use the same landing URL?
- Should recommendations be stored permanently or generated on demand?
- Should weekly reports be saved as documents or generated views?
- What is the minimum data volume before a format can be called weak?

---

## 53. Summary

Analytics and Optimization is the learning loop of Content Plant.

It should not only answer:

```text
How many views did this get?
```

It should answer:

```text
What should we produce next?
What should we stop producing?
What should be repeated, repurposed or tested again?
```

For MVP, the module should stay simple:

```text
manual / CSV metrics
→ metric snapshots
→ summaries
→ warnings
→ basic recommendations
→ new ideas
```

This is enough to make Content Plant a feedback-driven production system instead of a one-way content generator.

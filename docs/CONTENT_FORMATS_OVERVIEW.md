# Content Formats Overview

## 1. Назначение документа

Этот документ описывает platform-level content formats для **Content Plant**.

Он фиксирует:

- какие форматы считаются универсальными;
- как formats отделяются от project-specific правил;
- какой формат реализован в текущем foundation MVP;
- какие форматы могут появиться позже без нарушения project-agnostic baseline.

Документ должен оставаться platform-level и не должен включать project-specific brand assumptions.

---

## 2. Главный принцип

Главный принцип:

> Format описывает универсальную структуру контента, а не конкретный бренд, персонажа, продукт, нишу или оффер.

Project-specific вариации должны задаваться через:

- `project_id`;
- `Brand Profile`;
- project `Content Strategy`;
- project CTA;
- project prompts;
- project config.

Платформенный слой не должен создавать `content_type`, названия шаблонов или metadata schema под конкретный проект.

---

## 3. Current Foundation Status

Текущий foundation MVP реализует только один safest production format:

```text
text_social_post
```

Текущий minimal foundation loop:

```text
Idea
→ Scenario
→ ContentItem
→ ExportPackage v1
→ Manual Publication Record v1
→ MetricSnapshot v1
```

Почему именно `text_social_post`:

- он не требует real render pipeline;
- он совместим с export-first/manual-publication-first подходом;
- он позволяет проверить project scoping, package generation и manual metrics path;
- он является самым безопасным foundation entry point.

---

## 4. Platform-Level Format Portfolio

Платформа может поддерживать семейство универсальных форматов:

1. `text_social_post`
2. `short_video_brief`
3. `carousel_post`
4. `newsletter_snippet`
5. `image_prompt`
6. `dialog_miniseries`
7. `atmospheric_video`
8. `explainer_carousel`
9. `pinterest_pin`

Но наличие формата в platform docs не означает, что он уже входит в текущий foundation MVP.

---

## 5. Current Must-Have Format: `text_social_post`

### 5.1. Назначение

`text_social_post` — это export-ready текстовый контент для text-first каналов и ручной публикации.

Он подходит для:

- Telegram;
- Threads;
- VK;
- внутренних или будущих text-first каналов;
- быстрых content iterations;
- manual publication workflows.

### 5.2. Универсальная структура

```text
Opening line
→ main message
→ optional bridge
→ CTA
```

### 5.3. Входные данные

- `project_id`
- `Brand Profile`
- source `Idea` or `Scenario`
- target platform
- funnel stage
- CTA
- optional link

### 5.4. Выходные данные

В текущем foundation export package writes:

```text
title.txt
body.txt
caption_{platform}.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

### 5.5. MVP статус

```text
must-have
current safest implemented foundation format
```

---

## 6. Future Candidate Format: `short_video_brief`

### 6.1. Назначение

`short_video_brief` описывает короткий video-first сценарный формат для будущего production expansion.

### 6.2. Универсальная структура

```text
Hook
→ 2-4 short beats
→ closing line
→ CTA
```

### 6.3. Примеры neutral positioning

- `wellness_app`: reflective short-form message
- `education_project`: concept explanation
- `content_brand`: audience insight clip

### 6.4. Статус

```text
future / not required for current foundation MVP
```

---

## 7. Future Candidate Format: `carousel_post`

### 7.1. Назначение

`carousel_post` — это последовательность слайдов для объяснения темы, разбора идеи или структурированного CTA path.

### 7.2. Универсальная структура

```text
Cover
→ context
→ explanation
→ example
→ CTA
```

### 7.3. Neutral examples

- `education_project`: step-by-step explanation
- `client_brand`: product selection guide
- `content_brand`: insight-to-action carousel

### 7.4. Статус

```text
future / not implemented in current foundation MVP
```

---

## 8. Future Candidate Format: `newsletter_snippet`

### 8.1. Назначение

`newsletter_snippet` — короткий reusable текстовый блок для email, digest или owned-media distribution.

### 8.2. Универсальная структура

```text
Subject idea
→ short message
→ key takeaway
→ CTA
```

### 8.3. Статус

```text
future / project-agnostic candidate
```

---

## 9. Future Candidate Format: `image_prompt`

### 9.1. Назначение

`image_prompt` — это structured prompt output для внешней генерации или ручного создания visual assets.

### 9.2. Универсальная структура

```text
scene
style
composition
brand constraints
technical notes
```

### 9.3. Статус

```text
future / not required for current foundation MVP
```

---

## 10. Optional Extended Format Families

Если платформа later расширяется, она может поддерживать:

- `dialog_miniseries`
- `atmospheric_video`
- `explainer_carousel`
- `pinterest_pin`

Эти форматы должны оставаться platform-level abstractions и не должны наследовать project-specific names, characters или themes.

---

## 11. Content Type IDs

Platform-level `content_type` identifiers должны быть стабильными и нейтральными.

Допустимо:

```text
text_social_post
short_video_brief
carousel_post
newsletter_snippet
image_prompt
dialog_miniseries
atmospheric_video
explainer_carousel
pinterest_pin
```

Недопустимо:

```text
project_specific_dialog
brand_private_format
custom_offer_post
```

---

## 12. Common Input Model

Нейтральная platform-level input model:

```json
{
  "content_type": "text_social_post",
  "project_id": "project_example",
  "brand_profile_id": "brand_example",
  "title": "",
  "topic": "",
  "funnel_stage": "attention",
  "target_platforms": [],
  "source_idea_id": "",
  "source_scenario_id": "",
  "cta_id": "",
  "status": "draft"
}
```

Дополнительные поля зависят от формата, но базовая модель должна оставаться project-agnostic.

---

## 13. Funnel Stage Compatibility

Форматы могут работать на разных стадиях воронки:

- `attention`
- `trust`
- `conversion`
- `retention`

Пример neutral mapping:

- `text_social_post`: `trust`, `conversion`, `retention`
- `carousel_post`: `trust`, `conversion`
- `short_video_brief`: `attention`, `trust`

---

## 14. Platform Adaptation

Один content item может иметь несколько platform adaptations:

```text
base content
→ caption per platform
→ checklist per platform
→ metadata
```

В текущем foundation MVP это реализовано прежде всего как `caption_{platform}.txt` внутри export package.

---

## 15. Repurpose Logic

Один смысл может переиспользоваться в нескольких format outputs.

Нейтральный пример:

```text
Idea: "Why teams lose content consistency"

Outputs:
  text_social_post
  carousel_post
  newsletter_snippet
```

Но current foundation MVP не требует repurpose engine для готовности baseline.

---

## 16. Metadata Requirements

Каждый output должен иметь metadata, достаточную для публикации и audit trail.

Нейтральный пример:

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "content_type": "text_social_post",
  "title": "Example post title",
  "topic": "content_consistency",
  "funnel_stage": "trust",
  "platform": "telegram",
  "cta_id": "cta_learn_more",
  "status": "ready",
  "created_at": ""
}
```

В текущем foundation package metadata должна оставаться neutral и не включать absolute local paths.

---

## 17. QA Requirements For Formats

Минимальные общие проверки:

- указан `project_id`
- применён `Brand Profile`
- `CTA` принадлежит проекту
- статус валиден
- export package complete enough for manual publication
- metadata present

Для текущего `text_social_post` foundation loop особенно важны:

- `title.txt`
- `body.txt`
- `caption_{platform}.txt`
- `manual_publication_checklist.txt`
- `metadata.json`
- `manifest.json`

---

## 18. Priority In Current Foundation

### 18.1. Current foundation priority

```text
text_social_post
```

### 18.2. Later expansion priorities

Possible later priorities:

```text
carousel_post
short_video_brief
image_prompt
newsletter_snippet
```

### 18.3. Important constraint

Later format additions must not rewrite the current foundation baseline retroactively.

---

## 19. What Must Not Happen

Нельзя:

- делать project-specific `content_type`;
- зашивать format examples под конкретный бренд;
- смешивать project strategy с format definition;
- трактовать future render formats как уже реализованный foundation baseline;
- добавлять external API assumptions в current format foundation.

---

## 20. Foundation Readiness Criteria

Current content formats foundation считается согласованным, если:

- current implemented format clearly identified as `text_social_post`;
- future formats описаны как neutral candidates, а не как active foundation requirements;
- `content_type` naming остаётся generic;
- format docs не содержат project-specific leakage;
- export-first/manual-publication-first workflow остаётся неизменным.

---

## 21. Статус документа

Статус: Draft  
Версия: 0.2  
Дата обновления: 2026-07-07  
Проект: Content Plant  
Current foundation format: `text_social_post`

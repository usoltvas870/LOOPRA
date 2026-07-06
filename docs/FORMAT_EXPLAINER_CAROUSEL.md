# Format: Explainer Carousel

## 1. Назначение документа

Этот документ описывает универсальный формат **Explainer Carousel** для платформы **Content Plant**.

Он фиксирует:

- что такое `explainer_carousel`;
- для каких задач используется формат;
- какие входные данные нужны;
- как строится структура объясняющей карусели;
- какие слайды и блоки обязательны;
- как формат использует Brand Profile;
- какие ассеты и шаблоны нужны;
- какие файлы должны быть на выходе;
- какие QA-проверки обязательны;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту, бренду, продукту или нише.

---

## 2. Краткое определение

**Explainer Carousel** — это серия слайдов, которая простым языком объясняет тему, продукт, механику, ошибку, подход, процесс или концепцию.

Формат должен превращать сложный смысл в понятную последовательность:

```text
Question / Hook
→ Context
→ Explanation
→ Example
→ Why it matters
→ Product / idea bridge
→ CTA or closing
```

Explainer Carousel не должен быть рекламной презентацией по умолчанию. Он должен помогать аудитории понять идею и только после этого, если уместно, вести к следующему действию.

---

## 3. Главный принцип формата

Главный принцип:

> Explainer Carousel объясняет один смысл за один проход.

Формат не должен пытаться рассказать всё сразу.

Правильно:

```text
One carousel = one question / one concept / one misconception / one decision point.
```

Неправильно:

```text
One carousel = full product manual + brand story + offer + FAQ + all objections.
```

Brand Profile задаёт тон, визуальный стиль, CTA, ограничения и product bridge. Сам формат задаёт только универсальную структуру объяснения.

---

## 4. Для чего нужен формат

`explainer_carousel` подходит для задач:

- объяснить сложную тему простыми словами;
- показать, как работает продукт или подход;
- снять типичное возражение;
- разобрать ошибку аудитории;
- дать mini-guide;
- показать пошаговый процесс;
- повысить доверие;
- подготовить пользователя к переходу на сайт, канал, продукт или консультацию;
- repurpose из сценария, тренда, статьи, FAQ или аналитического insight.

---

## 5. Supported platforms

MVP platforms:

```text
instagram
vk
telegram
pinterest
```

Should-have:

```text
linkedin
threads
website
```

Future:

```text
x
facebook
blog
email
```

Платформа влияет на:

- размер слайдов;
- длину текста;
- CTA;
- caption;
- hashtag rules;
- link policy;
- export package.

---

## 6. Output sizes

Recommended sizes:

```text
instagram_feed: 1080x1350
instagram_square: 1080x1080
vk_feed: 1080x1350
telegram_image: 1080x1350
pinterest_pin: 1000x1500 or 1080x1920
```

MVP default:

```text
1080x1350
```

Specific size должен задаваться через:

- Production Template;
- Platform Settings;
- Output Spec.

---

## 7. Recommended slide count

Recommended:

```text
5–8 slides
```

MVP default:

```text
6 slides
```

Allowed range:

```text
3–10 slides
```

Если объяснение не помещается в 10 слайдов, лучше разделить его на серию каруселей.

---

## 8. Basic structure

Базовая структура:

```text
Slide 1: Cover / Question / Hook
Slide 2: Context / Problem
Slide 3: Explanation point 1
Slide 4: Explanation point 2 or Example
Slide 5: Why it matters / Reframe
Slide 6: CTA / Closing / Next step
```

Расширенная структура:

```text
Cover
→ Misconception
→ Simple explanation
→ Example
→ Step-by-step breakdown
→ Practical takeaway
→ Product / idea bridge
→ CTA
```

---

## 9. Slide roles

Рекомендуемые роли слайдов:

```text
cover
question
problem
misconception
context
explanation
step
example
comparison
proof
checklist
reframe
product_bridge
cta
closing
```

### 9.1. cover

Первый слайд. Должен остановить внимание и ясно показать тему.

### 9.2. misconception

Используется, когда нужно снять ошибочное представление.

### 9.3. explanation

Основной смысловой слайд.

### 9.4. example

Показывает применение идеи на простой ситуации.

### 9.5. comparison

Сравнивает два подхода, варианта или состояния.

### 9.6. checklist

Дает практический список действий или признаков.

### 9.7. product_bridge

Мягко связывает объяснение с продуктом, сервисом, консультацией, материалом или следующим шагом.

### 9.8. cta

Предлагает действие. CTA должен браться из Project CTA Library.

### 9.9. closing

Закрывает мысль без прямого CTA, если CTA не нужен.

---

## 10. Explainer Carousel entity

Минимальная структура:

```json
{
  "carousel_id": "carousel_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_type": "explainer_carousel",
  "source_type": "idea",
  "source_id": "idea_001",
  "title": "Example explainer title",
  "topic": "example_topic",
  "funnel_stage": "trust",
  "target_platforms": ["instagram", "vk"],
  "slides": [],
  "cta_id": "cta_001",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

---

## 11. Slide model

Каждый слайд должен быть структурированным объектом.

```json
{
  "slide_id": "slide_001",
  "order": 1,
  "role": "cover",
  "headline": "Short slide headline",
  "body": "Short supporting text.",
  "visual_description": "Simple visual direction.",
  "visual_prompt": "",
  "asset_id": null,
  "layout_variant": "cover_centered",
  "notes": ""
}
```

Обязательные поля MVP:

```text
slide_id
order
role
headline or body
status
```

Желательные поля:

```text
visual_description
visual_prompt
asset_id
layout_variant
speaker_note
```

---

## 12. Source types

Explainer Carousel может создаваться из:

```text
idea
scenario
trend
content_item
faq
manual_note
analytics_insight
source_document
```

MVP source types:

```text
idea
scenario
manual_note
analytics_insight
```

---

## 13. Funnel stage

Explainer Carousel должен поддерживать funnel stage.

```text
attention
trust
conversion
retention
```

### 13.1. attention

Фокус: простой хук, узнавание, первый интерес.

### 13.2. trust

Фокус: объяснение подхода, снятие непонимания, экспертность.

### 13.3. conversion

Фокус: объяснение ценности продукта, процесса, оффера или следующего действия.

### 13.4. retention

Фокус: обучение существующей аудитории, повторное использование, привычка, поддержка.

---

## 14. Text rules

Текст должен быть коротким и читаемым.

Рекомендации MVP:

```text
cover headline: 30–70 characters
slide headline: 20–80 characters
slide body: 80–220 characters
max text blocks per slide: 2
```

Правила:

- одна главная мысль на слайд;
- короткие предложения;
- без перегруза терминами;
- не использовать мелкий текст;
- не превращать карусель в статью;
- не обещать результат, если это запрещено Content Rules;
- CTA должен соответствовать funnel stage.

---

## 15. Explanation patterns

Scenario Studio может использовать разные структуры объяснения.

### 15.1. Question → Answer

```text
Question
→ Short answer
→ Explanation
→ Example
→ Next step
```

### 15.2. Myth → Reality

```text
Common belief
→ Why it is incomplete
→ Better explanation
→ Example
→ Takeaway
```

### 15.3. Problem → Framework

```text
Problem
→ Why it happens
→ Framework
→ How to use it
→ CTA
```

### 15.4. Step-by-step

```text
Goal
→ Step 1
→ Step 2
→ Step 3
→ Result
→ CTA
```

### 15.5. Before / After

```text
Before state
→ Hidden cause
→ New perspective
→ After state
→ Next step
```

---

## 16. Visual assets

Explainer Carousel может использовать:

```text
backgrounds
icons
illustrations
screenshots
diagrams
simple charts
product visuals
brand elements
template elements
```

MVP может работать с:

```text
background
logo
simple decorative elements
uploaded images
```

Не обязательно строить сложный infographic editor в первой версии.

---

## 17. Asset requirements

Для изображений:

```text
png
jpg
jpeg
webp
```

Recommended:

```text
same aspect ratio as output template
high resolution
readable contrast
safe area respected
```

Если asset не подходит:

- show warning;
- allow crop / fit if template supports it;
- block export only for critical mismatch.

---

## 18. Visual prompt rules

Если слайду нужен visual prompt, он должен учитывать:

- slide role;
- headline;
- body;
- topic;
- Brand Profile visual identity;
- forbidden visuals;
- target aspect ratio;
- safe zones;
- whether text will be placed on top.

Prompt не должен содержать project-specific hardcode вне Brand Profile.

---

## 19. Layout rules

Layout должен быть controlled by template.

Типовые layout variants:

```text
cover_centered
headline_top_body_middle
split_text_visual
comparison_two_columns
checklist
numbered_steps
quote_style
cta_card
closing_card
```

MVP layouts:

```text
cover_centered
headline_body
split_text_visual
checklist
cta_card
```

---

## 20. Typography

Typography берётся из Brand Profile.

Template может задавать:

- hierarchy;
- font sizes;
- spacing;
- max line width;
- slide-safe margins.

Brand Profile задаёт:

- primary font;
- secondary font;
- fallback font;
- text colors;
- emphasis style.

Если конкретный шрифт недоступен, должен использоваться fallback.

---

## 21. Color and brand application

Explainer Carousel должен использовать:

- colors from Brand Profile;
- logo if configured;
- brand-safe backgrounds;
- consistent visual style;
- template-defined contrast rules.

Нельзя зашивать в template цвета, офферы, тексты, цены или персонажей конкретного проекта.

---

## 22. CTA rules

CTA optional.

CTA должен браться из:

```text
Project CTA Library
```

CTA может быть:

- slide CTA;
- caption CTA;
- link CTA;
- closing line;
- save/share CTA;
- no CTA.

CTA intensity зависит от funnel stage:

```text
attention: none / soft
trust: soft / medium
conversion: medium / direct
retention: soft / medium
```

---

## 23. Caption generation

Для каждой платформы может быть отдельный caption.

Caption должен учитывать:

- platform;
- carousel title;
- topic;
- funnel stage;
- CTA;
- hashtags;
- link policy;
- Brand Profile tone of voice.

MVP output:

```text
caption.txt
```

Should-have:

```text
caption_instagram.txt
caption_vk.txt
caption_telegram.txt
caption_pinterest.txt
```

---

## 24. Output files

Export package для Explainer Carousel:

```text
exports/
  {project_slug}/
    {content_id}/
      slides/
        slide_01.png
        slide_02.png
        slide_03.png
        slide_04.png
        slide_05.png
        slide_06.png
      caption.txt
      metadata.json
      cover.png
```

If platform-specific export is enabled:

```text
exports/
  {project_slug}/
    {content_id}/
      instagram/
        slides/
        caption.txt
        metadata.json
      vk/
        slides/
        caption.txt
        metadata.json
```

---

## 25. Metadata

`metadata.json` should include:

```json
{
  "content_id": "content_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "content_type": "explainer_carousel",
  "source_type": "idea",
  "source_id": "idea_001",
  "title": "Example explainer title",
  "topic": "example_topic",
  "funnel_stage": "trust",
  "target_platforms": ["instagram"],
  "slide_count": 6,
  "template_id": "template_explainer_carousel_v1",
  "brand_profile_version": "1.0",
  "cta_id": "cta_001",
  "created_at": ""
}
```

---

## 26. Production pipeline

Basic pipeline:

```text
Idea / Scenario / Manual Note
→ Select explainer_carousel
→ Generate outline
→ Generate slides
→ Generate visual prompts or choose template visuals
→ Link assets if needed
→ Run QA
→ Render slides
→ Create Content Item
→ Human Review
→ Export Package
→ Publishing Hub
→ Metrics
```

---

## 27. Repurpose logic

Explainer Carousel может быть создан из:

- successful text post;
- successful video;
- FAQ answer;
- trend analysis;
- analytics insight;
- long-form source document;
- product explanation;
- scenario.

Также Explainer Carousel может порождать:

```text
text_social_post
atmospheric_video
pinterest_pin
caption_bundle
short video script
```

---

## 28. QA checks

Required QA checks MVP:

- project_id exists;
- content_type = explainer_carousel;
- slide count within allowed range;
- cover slide exists;
- each slide has headline or body;
- text length within recommendation;
- CTA valid, if used;
- Brand Profile exists;
- forbidden phrases absent;
- forbidden topics absent;
- output size valid;
- export files created;
- metadata exists.

Should-have QA:

- contrast check;
- safe-zone check;
- repeated slide text warning;
- too much text warning;
- unsupported claims check;
- visual consistency warning.

---

## 29. Review rules

Human Review должен проверить:

- понятна ли логика объяснения;
- не слишком ли много текста;
- не перепутан ли порядок слайдов;
- не нарушены ли правила бренда;
- корректен ли CTA;
- читаются ли слайды на мобильном;
- нет ли unsupported claims;
- готов ли материал к публикации.

После approve создаётся platform-ready export package.

---

## 30. Template rules

Production Template должен задавать:

- output size;
- layout variants;
- typography scale;
- safe zones;
- spacing;
- logo placement rules;
- slide numbering rules;
- CTA slide layout;
- export rules.

Template не должен содержать:

- project-specific product names;
- project-specific prices;
- project-specific CTA;
- hardcoded URLs;
- hardcoded character names;
- niche-specific claims.

---

## 31. Batch production

Explainer Carousel хорошо подходит для batch production.

Batch input:

```text
list of ideas / questions / FAQ items / topics
```

Batch output:

```text
multiple draft carousels
```

MVP может поддерживать batch generation как should-have, но каждый generated carousel должен проходить review.

---

## 32. Platform adaptation

### Instagram

- shorter text per slide;
- strong cover;
- save/share friendly;
- caption with soft CTA.

### VK

- can support slightly longer captions;
- carousel may include more explanation;
- direct links are possible.

### Telegram

- carousel can be posted with longer supporting text;
- caption can expand the idea;
- useful for deeper explanation.

### Pinterest

- more evergreen title;
- keyword-oriented description;
- output size may differ;
- destination URL important.

---

## 33. MVP scope

MVP includes:

- create explainer carousel from idea or manual note;
- generate 5–8 slide draft;
- edit slide text;
- apply Brand Profile style;
- render PNG slides;
- generate caption;
- create metadata.json;
- create export package;
- human review;
- manual publishing support.

MVP does not include:

- complex infographic editor;
- full design system builder;
- automatic chart generation from arbitrary data;
- mandatory autoposting;
- built-in image generation API;
- advanced A/B testing automation;
- public SaaS template marketplace.

---

## 34. Acceptance criteria

Format implementation is acceptable when:

- user can create `explainer_carousel` for active project;
- generated carousel has valid slide structure;
- Brand Profile is applied;
- no project-specific data is hardcoded in template;
- output slides are rendered as image files;
- caption and metadata are created;
- QA checks run;
- Content Item enters `needs_review`;
- approved content can be exported;
- publication can later receive metrics.

---

## 35. Open questions

Questions to decide later:

1. Should MVP support both 1080x1350 and 1080x1920 for carousels?
2. Should slide numbering be enabled by default?
3. Should cover slide be required for all platforms?
4. Should carousel generation support source documents in MVP?
5. Should diagrams be treated as assets or generated layout blocks?
6. Should carousel templates be shared across projects or copied per project?
7. Which platform should define default carousel size if multiple target platforms are selected?

---

## 36. Summary

`explainer_carousel` is a universal format for explaining one idea clearly through a sequence of slides.

Its role in Content Plant is to convert ideas, trends, FAQs, scenarios and analytics insights into structured educational or trust-building content.

The format is platform-level. Project-specific voice, visuals, offers, CTA and restrictions must come from Brand Profile and Project Settings.

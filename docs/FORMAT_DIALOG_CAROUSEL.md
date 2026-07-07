# Format: Dialog Carousel

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает универсальный формат **Dialog Carousel** для платформы **Content Plant**.

Он фиксирует:

- что такое `dialog_carousel`;
- для каких задач используется формат;
- как формат связан с Dialog Miniseries и другими форматами;
- какие входные данные нужны;
- какая структура у карусели;
- какие ассеты и текстовые блоки требуются;
- какие output files должны создаваться;
- какие QA-проверки обязательны;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту или бренду.

---

## 2. Краткое определение

**Dialog Carousel** — это серия слайдов, построенная на диалоге двух персонажей, двух точек зрения, пользователя и эксперта, клиента и консультанта, ученика и наставника или другого проектного сочетания ролей.

Формат превращает короткую смысловую сцену в визуальную карусель, которую можно листать, сохранять, пересылать и переиспользовать.

Базовая формула:

```text
Dialog structure
+ Slide sequence
+ Brand Profile
+ Visual assets
+ CTA
= Carousel package
```

---

## 3. Главный принцип формата

`dialog_carousel` должен быть универсальным.

Формат описывает:

- структуру слайдов;
- роли слайдов;
- правила текста;
- требования к визуалам;
- правила CTA;
- output package;
- QA.

Проектный слой описывает:

- кто именно говорит;
- как звучит диалог;
- какой визуальный стиль использовать;
- какие темы разрешены;
- какие CTA доступны;
- какие платформы целевые.

Нельзя зашивать в формат конкретного персонажа, продукт, цену, ссылку, брендовый цвет или готовую проектную фразу.

---

## 4. Для чего нужен Dialog Carousel

Формат подходит для:

- repurpose из `dialog_miniseries`;
- объяснения сложной мысли через короткий диалог;
- создания сохраняемого контента;
- прогрева аудитории;
- визуального storytelling;
- образовательных микро-сцен;
- консультационных сценариев;
- сравнений двух точек зрения;
- мягкой конверсии через CTA-слайд.

Карусель особенно полезна там, где один короткий ролик нужно превратить в более спокойный, развернутый и сохраняемый формат.

---

## 5. Роль в content portfolio

`dialog_carousel` находится между video content и text social posts.

```text
Dialog Miniseries → Dialog Carousel → Text Social Posts
```

Один сценарий может породить:

- vertical video;
- carousel slides;
- caption;
- Telegram post;
- Threads post;
- VK post;
- Pinterest pin.

`dialog_carousel` должен поддерживать source linkage, чтобы было понятно, из какой Idea, Scenario или Content Item он создан.

---

## 6. Supported platforms

MVP target platforms:

```text
instagram
vk
telegram
pinterest
```

Should-have:

```text
linkedin
facebook
website
```

Формат может использоваться и как export-only package, если автоматическая публикация не поддерживается.

---

## 7. Output sizes

Рекомендуемые размеры:

### Square / feed

```text
1080x1080
1:1
```

### Portrait / feed

```text
1080x1350
4:5
```

### Vertical / story-like

```text
1080x1920
9:16
```

MVP default:

```text
1080x1350
4:5
```

Для Pinterest может использоваться:

```text
1000x1500
2:3
```

Output size должен задаваться через template или platform settings.

---

## 8. Recommended slide count

Рекомендуемый диапазон:

```text
5–8 slides
```

MVP minimum:

```text
4 slides
```

MVP maximum:

```text
10 slides
```

Слишком длинные карусели требуют отдельного QA-warning.

---

## 9. Basic structure

Рекомендуемая структура:

```text
Slide 1: Cover / Hook
Slide 2: First voice / Problem
Slide 3: Second voice / Response
Slide 4: Mirror / Recognition
Slide 5: Reframe / Insight
Slide 6: Practical meaning / Example
Slide 7: Closing / CTA
```

Минимальная структура:

```text
Cover
→ Dialogue turn
→ Insight
→ CTA / Closing
```

---

## 10. Slide roles

Универсальные роли слайдов:

```text
cover
hook
problem
character_line
guide_line
contrast
mirror
insight
example
explanation
product_bridge
cta
closing
```

Конкретный формат может использовать часть ролей.

---

## 11. Carousel entity

Carousel может быть отдельным Content Item или output type от Scenario.

Минимальная структура:

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "source_scenario_id": "scenario_001",
  "content_type": "dialog_carousel",
  "output_type": "carousel_images",
  "title": "Example carousel title",
  "target_platforms": ["instagram", "vk"],
  "funnel_stage": "trust",
  "slides": [],
  "caption": "",
  "cta_id": "cta_001",
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

---

## 12. Slide model

Каждый слайд должен быть структурированным объектом.

```json
{
  "slide_id": "slide_001",
  "order": 1,
  "role": "cover",
  "speaker": "",
  "headline": "",
  "body": "",
  "dialogue_text": "",
  "visual_prompt": "",
  "asset_id": "asset_001",
  "layout_variant": "default",
  "cta_id": "",
  "notes": "",
  "status": "draft"
}
```

Обязательные поля MVP:

```text
slide_id
order
role
headline or body or dialogue_text
status
```

Желательные поля:

```text
speaker
visual_prompt
asset_id
layout_variant
cta_id
notes
```

---

## 13. Text rules

Carousel text должен быть коротким и легко читаемым.

Рекомендации:

- одна главная мысль на слайд;
- короткие строки;
- не превращать слайд в статью;
- важный текст держать в safe zone;
- избегать мелкого кегля;
- не перегружать CTA;
- оставлять визуальный воздух.

MVP limits:

```text
cover headline: 20–80 characters
slide body: 40–220 characters
max lines per slide: 6
cta text: 20–120 characters
```

Эти ограничения могут быть overridden by format settings.

---

## 14. Dialogue rules

Диалог должен быть понятен без озвучки.

Рекомендации:

```text
Speaker label optional
Short turn per slide
No long monologues
Clear emotional or logical progression
```

Пример универсальной структуры:

```text
Person: I keep choosing the same pattern.
Guide: Maybe the question is not why you repeat it, but what it protects.
```

Это пример структуры, а не готовый проектный текст.

---

## 15. Visual assets

Carousel может использовать:

```text
image
background
character
logo
texture
template_asset
```

MVP допускает два режима:

### 15.1. Asset-per-slide

Каждый слайд использует отдельный visual asset.

```text
slide_01 → asset_001
slide_02 → asset_002
slide_03 → asset_003
```

### 15.2. Shared visual system

Карусель использует общий фон, иллюстрации, декоративные элементы или layout template.

```text
same background + changing text blocks
```

---

## 16. Asset requirements

Для слайдов MVP:

```text
png
jpg
jpeg
webp
```

Рекомендуемое качество:

```text
width >= target output width
height >= target output height
```

Если ассет не соответствует размеру:

- crop;
- fit with background;
- warn user;
- or block export, depending on template rules.

---

## 17. Visual prompt rules

Если ассеты нужно создать во внешнем AI-инструменте, Scenario Studio может генерировать visual prompts для каждого слайда.

Prompt должен учитывать:

- slide role;
- text meaning;
- speaker role;
- desired composition;
- Brand Profile visual identity;
- forbidden visuals;
- output aspect ratio;
- safe zones for text.

Visual Prompt не должен содержать project-specific hardcode, если он создаётся на уровне универсального формата.

---

## 18. Layout rules

Template должен управлять:

- text placement;
- image placement;
- speaker labels;
- slide numbering;
- CTA placement;
- logo placement;
- margins;
- safe zones;
- typography hierarchy.

Brand Profile должен управлять:

- colors;
- fonts;
- logo;
- visual mood;
- forbidden elements;
- tone of written text.

---

## 19. Typography

Typography берётся из Brand Profile.

Минимальные уровни:

```text
cover_title
slide_headline
slide_body
speaker_label
cta_text
footer_note
```

Template должен иметь fallback fonts, если проектные шрифты недоступны.

---

## 20. Brand marks

Logo или brand mark optional.

Правила:

- не зашивать logo в template;
- брать logo из Brand Profile / Asset Library;
- позволять отключать logo для отдельных платформ;
- соблюдать safe zones;
- не мешать чтению текста.

---

## 21. CTA rules

CTA optional и должен браться из Project CTA Library.

CTA может быть:

```text
engagement
profile_visit
website_click
lead
conversion
subscription
retention
booking
purchase
```

CTA slide может быть:

- финальным слайдом;
- soft closing line;
- product bridge;
- platform-specific instruction;
- omitted for attention-stage content.

Нельзя зашивать готовый CTA в формат.

---

## 22. Caption generation

Для carousel должен создаваться caption.

Caption должен учитывать:

- platform;
- content type;
- funnel stage;
- CTA;
- hashtags;
- link policy;
- UTM;
- project tone.

Output examples:

```text
caption_instagram.txt
caption_vk.txt
caption_telegram.txt
caption_pinterest.txt
```

MVP может поддерживать один `caption.txt` и metadata с platform variants.

---

## 23. Hashtags

Hashtags optional.

Hashtag rules должны быть platform-specific и project-specific.

MVP recommendation:

```text
0–10 hashtags
```

Если platform settings указывают меньший лимит, использовать его.

---

## 24. Output files

Carousel export package должен включать:

```text
exports/
  {project_slug}/
    {content_id}/
      slides/
        slide_01.png
        slide_02.png
        slide_03.png
      caption.txt
      metadata.json
```

Optional:

```text
cover.png
caption_instagram.txt
caption_vk.txt
caption_telegram.txt
caption_pinterest.txt
slides.zip
```

---

## 25. Metadata

`metadata.json` должен включать:

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "content_type": "dialog_carousel",
  "output_type": "carousel_images",
  "source_scenario_id": "scenario_001",
  "target_platforms": ["instagram", "vk"],
  "slide_count": 7,
  "cta_id": "cta_001",
  "template_id": "template_dialog_carousel_v1",
  "brand_profile_version": "1.0",
  "created_at": ""
}
```

---

## 26. Production pipeline

Basic pipeline:

```text
Idea / Scenario
→ Dialog Carousel Draft
→ Slides / Text Blocks
→ Visual Prompts
→ Asset Mapping
→ Render Slides
→ Output QA
→ Human Review
→ Export Package
→ Publishing Hub
→ Metrics
```

---

## 27. Repurpose from Dialog Miniseries

`dialog_carousel` может создаваться из `dialog_miniseries`.

Mapping example:

```text
Video hook → Cover slide
Scene 1 dialogue → Slide 2
Scene 2 dialogue → Slide 3
Scene 3 insight → Slide 4
CTA scene → CTA slide
```

Repurpose должен сохранять source linkage:

```text
source_content_id
source_scenario_id
source_idea_id
```

---

## 28. Repurpose to Text Social Posts

Carousel может стать источником для текстовых постов:

```text
Carousel → Telegram post
Carousel → Threads post
Carousel → VK post
Carousel → Pinterest description
```

Text outputs должны использовать `FORMAT_TEXT_SOCIAL_POSTS.md`.

---

## 29. QA checks

MVP QA checks:

- project_id exists;
- content_type = dialog_carousel;
- slide count within limits;
- required slide roles exist;
- each slide has readable text;
- text length within limits;
- no empty required slide;
- visual assets exist, if required by template;
- asset belongs to project;
- output files exist;
- metadata exists;
- caption exists, if required;
- CTA valid, if used;
- Brand Profile exists;
- forbidden phrases absent;
- forbidden topics absent;
- export package complete.

---

## 30. Review rules

Human review проверяет:

- смысловую последовательность;
- читаемость;
- визуальное качество;
- соответствие Brand Profile;
- корректность CTA;
- отсутствие project-rule violations;
- пригодность для публикации.

После render Content Item получает статус:

```text
needs_review
```

После approve:

```text
approved
```

Только approved carousel может идти в Publishing Hub как ready-to-publish.

---

## 31. Common QA warnings

Примеры warnings:

```text
Slide 3 text is too long.
Carousel has no CTA. This may be acceptable for attention-stage content.
Slide 5 uses an asset with different aspect ratio.
Caption is missing hashtags, but platform settings recommend them.
```

Примеры blockers:

```text
Required cover slide is missing.
Slide 2 has no text.
Required asset belongs to another project.
metadata.json is missing.
```

---

## 32. Template rules

Production Template должен задавать:

- output size;
- slide layout;
- text slots;
- visual slots;
- required slide roles;
- optional slide roles;
- safe zones;
- logo placement;
- export rules.

Template не должен задавать:

- конкретный бренд;
- конкретный продукт;
- цену;
- project-specific CTA;
- project-specific character.

---

## 33. Batch production

`dialog_carousel` подходит для batch production.

Batch input:

```text
approved scenarios
or approved ideas
or top-performing content items
```

Batch output:

```text
multiple carousel packages
review queue items
publishing candidates
```

Batch production не должна обходить human review.

---

## 34. Platform adaptation

Одна карусель может иметь разные platform variants.

Examples:

```text
Instagram: 1080x1350, short caption, carousel post
VK: 1080x1350 or 1080x1080, longer caption allowed
Telegram: image sequence + text post
Pinterest: 2:3 pin-like adaptation or selected key slide
```

Platform adaptation должна управляться Platform Settings.

---

## 35. MVP scope

В MVP входит:

- создание carousel draft из scenario;
- ручное редактирование slides;
- генерация visual prompts;
- загрузка/привязка assets;
- render slides to PNG;
- создание caption;
- создание metadata;
- export package;
- QA checks;
- human review.

В MVP не входит:

- сложный drag-and-drop design editor;
- marketplace carousel templates;
- встроенная генерация изображений через API;
- автоматический постинг во все платформы;
- advanced A/B design optimizer;
- многоуровневые approval roles.

---

## 36. Acceptance criteria MVP

Формат считается готовым для MVP, если пользователь может:

1. выбрать project;
2. создать или выбрать scenario;
3. создать dialog carousel draft;
4. увидеть slides;
5. отредактировать текст слайдов;
6. сгенерировать visual prompts;
7. привязать assets;
8. отрендерить PNG-слайды;
9. получить caption и metadata;
10. отправить carousel в Review;
11. approve / reject;
12. создать export package;
13. передать approved carousel в Publishing Hub.

---

## 37. Open questions

Вопросы для будущего решения:

1. Делать ли `dialog_carousel` самостоятельным content type или всегда repurpose от scenario?
2. Нужен ли встроенный slide editor в MVP или достаточно template-driven render?
3. Какие output sizes должны быть default для разных платформ?
4. Нужно ли поддерживать animated carousel / video carousel later?
5. Как хранить design variants: как template versions или как content variations?
6. Нужно ли автоматическое split длинного сценария на slide sequence?
7. Как оценивать carousel performance: saves, shares, clicks, completion, swipe depth?

---

## 38. Summary

`dialog_carousel` — универсальный формат для превращения диалога, сценария или идеи в сохраняемую визуальную последовательность.

Ключевой принцип:

```text
Format defines structure.
Brand Profile defines voice and visual identity.
Project Settings define platforms, CTA and rules.
```

Формат должен усиливать production loop, поддерживать repurpose и не содержать project-specific hardcode.

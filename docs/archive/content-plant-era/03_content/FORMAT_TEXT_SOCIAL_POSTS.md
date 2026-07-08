# Format: Text Social Posts

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает универсальный формат **Text Social Posts** для платформы **Content Plant**.

Он фиксирует:

- что такое `text_social_post`;
- для каких платформ и задач используется формат;
- как текстовые посты связаны с видео, каруселями и сценариями;
- какие входные данные нужны;
- какая структура у постов;
- как посты адаптируются под разные платформы;
- какие файлы и данные должны быть на выходе;
- какие QA-проверки обязательны;
- что входит в MVP.

Документ является источником истины для реализации формата `text_social_post`.

---

## 2. Краткое определение

**Text Social Posts** — это текстовые публикации, адаптированные под социальные платформы, где текст может работать как самостоятельная единица контента или как repurpose из видео, сценария, карусели или идеи.

`text_social_post` is the first safest MVP format for the first implementation loop.

Причина:

- он позволяет проверить core platform loop без зависимости от FFmpeg, HyperFrames и video assets;
- он быстрее всего проверяет `Project`, `Brand Profile`, `Idea`, `Scenario / Draft`, `QA`, `Review`, `Export Package`, `Manual Publication`, `Metric Snapshot` и `Insight`.

Основные платформы MVP:

```text
Telegram
Threads
VK
```

В будущем формат может быть расширен на:

```text
LinkedIn
X / Twitter
Facebook
email snippets
blog micro-posts
```

---

## 3. Главный принцип формата

Главный принцип:

> Один смысл должен превращаться не только в видео или карусель, но и в набор текстовых публикаций под разные площадки.

Например, из одной идеи:

```text
"Example content idea"
```

Content Plant может создать:

- короткий Threads-пост;
- более глубокий Telegram-пост;
- VK-пост с мягким CTA;
- цитату для повторного использования;
- caption для видео;
- мини-ветку.

Текстовый формат усиливает контентный конвейер и помогает не терять смыслы после генерации сценария.

---

## 4. Для чего нужен формат

`text_social_post` нужен для:

- регулярной коммуникации с аудиторией;
- прогрева;
- объяснения продукта;
- репостинга смыслов из видео;
- поддержки Telegram/VK/Threads;
- тестирования тем без сложного производства;
- удержания аудитории;
- мягкой конверсии;
- расширения одного сценария в несколько касаний.

Текстовые посты особенно важны для проектов, где аудитории нужно не только увидеть короткое видео, но и глубже понять тон, доверие и смысл продукта.

---

## 5. Универсальность формата

Формат не должен быть зашит под конкретный проект.

Для e-commerce:

```text
полезный экспертный пост
советы по выбору продукта
CTA к подборке или товару
```

Для education:

```text
мини-урок
объяснение ошибки
CTA к уроку или курсу
```

Для B2B:

```text
короткий разбор проблемы
деловая интонация
CTA к аудиту или кейсу
```

Формат задаёт структуру.  
Brand Profile задаёт голос, стиль, CTA и ограничения.

---

## 6. Основные типы текстовых постов

Формат `text_social_post` должен поддерживать несколько подтипов.

### 6.1. Reflection Post

Рефлексивный пост.

Используется для:

- эмоционального прогрева;
- узнавания;
- доверия;
- мягкой связи с продуктом.

Структура:

```text
opening line
→ reflection
→ insight
→ soft CTA
```

### 6.2. Explainer Post

Объясняющий пост.

Используется для:

- простого объяснения продукта;
- ответа на вопросы;
- снятия возражений;
- обучения.

Структура:

```text
question
→ simple explanation
→ example
→ why it matters
→ CTA
```

### 6.3. Story Post

Мини-история.

Используется для:

- вовлечения;
- эмоционального storytelling;
- демонстрации ситуации аудитории.

Структура:

```text
situation
→ tension
→ turn
→ meaning
→ CTA
```

### 6.4. Dialogue Post

Текстовый диалог.

Используется как repurpose из `dialog_miniseries`.

Структура:

```text
Person:
...

Guide:
...

Person:
...

Guide:
...

CTA
```

### 6.5. Thread Post

Короткая ветка.

Используется для Threads или X-like платформ.

Структура:

```text
1. hook
2. point
3. point
4. point
5. CTA or closing line
```

### 6.6. Caption Post

Caption для видео или карусели.

Используется вместе с готовым media item.

Структура:

```text
short hook
→ context
→ CTA
→ hashtags
```

---

## 7. Платформы MVP

### 7.1. Telegram

Особенности:

- можно писать глубже;
- допустимы длинные абзацы, но лучше короткие;
- CTA может быть мягким;
- можно использовать ссылку;
- можно вести серийную коммуникацию;
- можно прогревать к покупке.

Рекомендуемая длина:

```text
700–1800 characters
```

---

### 7.2. Threads

Особенности:

- короткий формат;
- сильная первая строка;
- можно делать микро-мысли;
- хорошо работают короткие наблюдения;
- CTA должен быть лёгким или отсутствовать в части постов.

Рекомендуемая длина:

```text
150–700 characters
```

---

### 7.3. VK

Особенности:

- можно использовать более развёрнутую структуру;
- допустимы списки;
- можно ставить ссылку;
- подходит для объясняющих и прогревающих постов.

Рекомендуемая длина:

```text
800–2500 characters
```

---

## 8. Входные данные

Формат может создаваться из разных источников.

### 8.1. From Idea

```json
{
  "source_type": "idea",
  "idea_id": "idea_001",
  "project_id": "project_example"
}
```

### 8.2. From Scenario

```json
{
  "source_type": "scenario",
  "scenario_id": "scenario_001",
  "project_id": "project_example"
}
```

### 8.3. From Content Item

```json
{
  "source_type": "content_item",
  "content_id": "content_001",
  "project_id": "project_example"
}
```

### 8.4. From Trend

```json
{
  "source_type": "trend",
  "trend_id": "trend_001",
  "project_id": "project_example"
}
```

---

## 9. Общая структура данных

```json
{
  "post_id": "post_001",
  "project_id": "project_example",
  "content_type": "text_social_post",
  "post_subtype": "reflection_post",
  "source_type": "scenario",
  "source_id": "scenario_001",
  "platform": "telegram",
  "title": "Example content idea",
  "body": "",
  "cta_id": "cta_primary_offer",
  "links": [],
  "hashtags": [],
  "status": "draft",
  "created_at": "",
  "updated_at": ""
}
```

---

## 10. Обязательные поля MVP

Для MVP обязательны:

```text
post_id
project_id
content_type
post_subtype
platform
body
status
created_at
updated_at
```

Желательные поля:

```text
source_type
source_id
cta_id
funnel_stage
topic
utm
hashtags
```

---

## 11. Funnel stage

Текстовые посты должны поддерживать stage воронки:

```text
attention
trust
conversion
retention
```

### 11.1. Attention

Цель:

- поймать внимание;
- вызвать узнавание;
- получить реакцию.

Пример:

```text
Иногда проблема не в продукте.
Проблема в том, что пользователь ещё не увидел связь с собственной задачей.
```

### 11.2. Trust

Цель:

- объяснить;
- раскрыть подход;
- дать ощущение глубины.

Пример:

```text
Хороший project-specific framework не обещает результат.
Он помогает пользователю яснее увидеть проблему и следующий шаг.
```

### 11.3. Conversion

Цель:

- привести к действию;
- объяснить продукт;
- снять возражение.

Пример:

```text
Primary offer помогает пользователю перейти от интереса к понятному следующему действию.
```

### 11.4. Retention

Цель:

- поддерживать контакт;
- возвращать человека к продукту;
- формировать привычку.

Пример:

```text
Сегодня попробуй заметить, где ты соглашаешься быстрее, чем успеваешь понять, чего хочешь.
```

---

## 12. Platform adaptation

Один и тот же смысл должен адаптироваться под платформы.

Пример:

### Telegram

```text
Длиннее, теплее, глубже.
Можно раскрыть мысль через 3–5 коротких абзацев.
```

### Threads

```text
Коротко, точно, с сильной первой строкой.
Можно без явного CTA.
```

### VK

```text
Можно добавить объяснение, список, ссылку и явный CTA.
```

---

## 13. Tone of Voice

Все посты должны использовать Brand Profile.

Text generator должен учитывать:

- tone_of_voice;
- forbidden_phrases;
- allowed_phrases;
- audience pains;
- product offers;
- CTA library;
- content rules.

Нельзя использовать один общий голос для всех проектов.

---

## 14. CTA rules

CTA должен быть проектным.

CTA берётся из:

```text
Project CTA Library
```

или Brand Profile.

Типы CTA:

```text
engagement
profile_visit
website_click
lead
conversion
subscription
retention
```

Пример структуры:

```json
{
  "cta_id": "cta_primary_offer",
  "intent": "conversion",
  "text": "Open the primary offer",
  "target": "website",
  "url": "https://example.com"
}
```

---

## 15. CTA intensity

Текстовые посты должны поддерживать разную силу CTA.

### 15.1. No CTA

Используется для охвата и доверия.

```text
Без ссылки и прямого призыва.
```

### 15.2. Soft CTA

Мягкий переход.

```text
Если хочешь, можно начать с даты рождения и посмотреть свою project-specific framework.
```

### 15.3. Direct CTA

Прямой призыв.

```text
Primary offer is available on the project page.
```

### 15.4. Product CTA

Конкретная продажа.

```text
Primary offer — {price}.
```

CTA intensity должен зависеть от funnel_stage и платформы.

---

## 16. Links and UTM

Если в посте есть ссылка, она должна поддерживать UTM.

Базовый шаблон:

```text
utm_source={platform}
utm_medium=organic
utm_campaign={project_slug}_{campaign}
utm_content={post_id}
```

Пример:

```text
https://example.com?utm_source=telegram&utm_medium=organic&utm_campaign=example_project_reflections&utm_content=post_001
```

UTM нужен, чтобы связать посты с кликами, регистрациями и продажами.

---

## 17. Hashtags

Hashtags optional.

Для Telegram хэштеги можно использовать ограниченно.  
Для Threads часто лучше без хэштегов или с минимальным количеством.  
Для VK можно использовать несколько тематических хэштегов.

Рекомендация MVP:

```text
0–5 hashtags
```

Хэштеги должны быть platform-specific и project-specific.

---

## 18. Output package

Для одиночного поста:

```text
text_social_post_{post_id}/
  post.txt
  metadata.json
```

Для platform bundle:

```text
text_social_post_{source_id}/
  telegram.txt
  threads.txt
  vk.txt
  metadata.json
```

Для MVP предпочтителен второй вариант, если пост создаётся из одной идеи для нескольких платформ.

---

## 19. Metadata

`metadata.json` должен включать:

```json
{
  "post_id": "post_001",
  "project_id": "project_example",
  "content_type": "text_social_post",
  "post_subtype": "reflection_post",
  "platform": "telegram",
  "source_type": "scenario",
  "source_id": "scenario_001",
  "topic": "inner_fatigue",
  "funnel_stage": "trust",
  "cta_id": "cta_primary_offer",
  "utm": "",
  "status": "ready",
  "created_at": ""
}
```

---

## 20. Generation pipeline

Базовый pipeline:

```text
Idea / Scenario / Content Item
→ Select platform
→ Select post subtype
→ Load Project
→ Load Brand Profile
→ Load CTA Library
→ Generate draft
→ QA
→ Review
→ Export
→ Schedule / Publish
→ Metrics
```

---

## 21. Repurpose from Dialog Miniseries

`dialog_miniseries` должен уметь порождать текстовые посты.

Пример:

```text
Dialog Miniseries:
"Example content idea"

Repurpose:
- Telegram reflection post
- Threads micro-post
- VK explainer post
- caption for video
```

Это позволяет одному сценарию работать на нескольких платформах.

---

## 22. Recommended post bundles

Для MVP можно генерировать bundle:

```text
1 Telegram post
1 Threads post
1 VK post
1 caption
```

Из одного источника:

```text
source_idea
source_scenario
source_content_item
```

---

## 23. Структура Telegram post

Рекомендуемая структура:

```text
Opening line

Short emotional reflection.

Insight or reframe.

Optional product bridge.

Soft CTA.
```

Пример skeleton:

```text
[opening]

[reflection]

[insight]

[CTA]
```

---

## 24. Структура Threads post

Вариант 1: короткая мысль

```text
[strong first line]

[second line that deepens meaning]
```

Вариант 2: мини-thread

```text
1/ [hook]
2/ [point]
3/ [point]
4/ [closing]
```

Для MVP можно генерировать один короткий пост, не полноценную ветку.

---

## 25. Структура VK post

Рекомендуемая структура:

```text
Hook

Explanation

Example or mini-list

Product bridge

CTA
```

VK может быть более объясняющим, чем Threads и Telegram.

---

## 26. Text length limits

Рекомендации:

| Platform | Recommended length |
|---|---:|
| Telegram | 700–1800 characters |
| Threads | 150–700 characters |
| VK | 800–2500 characters |
| Caption | 150–600 characters |

Это не жёсткие технические ограничения, а guideline для генерации.

---

## 27. QA checks

Обязательные QA-проверки:

### 27.1. Data QA

- project_id указан;
- content_type = text_social_post;
- platform указан;
- body не пустой;
- status корректный.

### 27.2. Brand QA

- применён Tone of Voice;
- нет запрещённых фраз;
- нет запрещённых тем;
- CTA принадлежит проекту;
- язык соответствует проекту.

### 27.3. Content QA

- первая строка достаточно сильная;
- текст не перегружен;
- абзацы читаемые;
- нет чрезмерного давления;
- нет ложных обещаний;
- нет противоречия продукту.

### 27.4. Platform QA

- длина подходит платформе;
- hashtags подходят платформе;
- ссылка корректна;
- UTM сформирован, если есть ссылка.

---

## 28. Review flow

MVP review flow:

```text
draft
→ needs_review
→ approved / rejected
→ scheduled / exported
→ published
```

Действия пользователя:

- approve;
- edit;
- regenerate;
- reject;
- export;
- schedule.

---

## 29. Statuses

Рекомендуемые статусы:

```text
draft
needs_review
approved
rejected
scheduled
published
analyzed
archived
```

---

## 30. MVP scope

В MVP входит:

- генерация Telegram post;
- генерация Threads post;
- генерация VK post;
- генерация caption;
- использование Brand Profile;
- использование CTA Library;
- export `.txt`;
- metadata.json;
- basic QA;
- review status.

---

## 31. Не входит в MVP

В MVP не входит:

- автопостинг во все текстовые платформы;
- сложный редактор текста;
- A/B testing headlines на уровне интерфейса;
- автоматический подбор хэштегов через внешние API;
- генерация длинных статей;
- email marketing;
- сложная контентная CRM.

---

## 32. Project-specific implementation

A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`.

Project-specific source of truth uses a hybrid model:

- project docs live in `docs/07_projects/{project_slug}/`;
- machine-readable settings for code live in `projects/{project_id}/project.yaml`.

Project-specific implementation may define:

- tone of voice;
- topics and content angles;
- CTA rules;
- offer wording;
- links and UTM campaigns;
- platform-specific restrictions;
- examples of approved posts.

These rules must not become global format defaults.

---

## 33. Example output

Ниже пример нейтрального output для `text_social_post`. Это демонстрация структуры, а не правило для конкретного проекта.

```text
Platform: Telegram
Subtype: explainer_post
Funnel stage: trust

Иногда пользователь не покупает не потому, что продукт ему не нужен.

Он просто ещё не понял, как именно продукт связан с его задачей.

Хороший контент помогает пройти этот мост: от узнавания проблемы к ясному следующему шагу.

CTA: Learn more on the project page.
```

---

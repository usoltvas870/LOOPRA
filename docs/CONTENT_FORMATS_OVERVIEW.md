# Content Formats Overview

## 1. Назначение документа

Этот документ описывает универсальные контентные форматы платформы **Content Plant**.

Он фиксирует:

- какие типы контента должна производить платформа;
- почему форматы должны быть универсальными, а не зашитыми под один проект;
- как форматы адаптируются через Brand Profile;
- какие форматы входят в MVP и ближайшие итерации;
- какие входные и выходные данные нужны для каждого формата;
- как форматы связаны с производственными пайплайнами, публикациями и аналитикой.

Документ является источником истины для общего списка контентных форматов.

---

## 2. Главный принцип

Content Plant должен работать не как генератор одного вида роликов, а как **портфель производственных форматов**.

Главный принцип:

> Формат является универсальным. Конкретный проект делает его уникальным через Brand Profile, Content Strategy, Visual Guidelines и CTA Library.

Например:

```text
Universal format: Dialog Miniseries
```

Для NURA это:

```text
Диалоги с NURA: NURA + человек, мягкое самопонимание, светлый премиальный стиль.
```

Для e-commerce это может быть:

```text
Консультант + покупатель, выбор товара, коммерческий стиль.
```

Для образовательного проекта:

```text
Наставник + ученик, объяснение сложной темы, чистый educational style.
```

---

## 3. Зачем нужны универсальные форматы

Универсальные форматы нужны, чтобы:

- не создавать новый production engine под каждый проект;
- быстро запускать новые бренды;
- переиспользовать шаблоны;
- тестировать одинаковые механики в разных нишах;
- разделить platform logic и project-specific logic;
- подготовить основу для будущего SaaS.

Формат отвечает на вопрос:

> Как устроена единица контента?

Brand Profile отвечает на вопрос:

> Как эта единица контента должна звучать и выглядеть для конкретного проекта?

---

## 4. Базовый список форматов

На первом этапе Content Plant должен поддерживать 6 ключевых форматов.

1. `dialog_miniseries`
2. `atmospheric_video`
3. `dialog_carousel`
4. `explainer_carousel`
5. `text_social_post`
6. `pinterest_pin`

Эти форматы формируют ядро платформы.

---

## 5. Формат 1: Dialog Miniseries

### 5.1. Назначение

`dialog_miniseries` — короткое вертикальное видео, построенное на диалоге двух персонажей или двух точек зрения.

Формат подходит для:

- эмоционального storytelling;
- узнавания аудитории;
- объяснения сложных тем через сцену;
- мягкого прогрева;
- серийного контента;
- брендового персонажа.

### 5.2. Пример для NURA

```text
NURA + второй персонаж
короткий диалог о внутреннем состоянии
3–5 сцен
реплики появляются поверх изображений
финальная мягкая фраза + CTA
```

### 5.3. Универсальная структура

```text
Hook
→ Character line
→ Guide / expert / second voice line
→ Emotional turn
→ Resolution
→ CTA
```

### 5.4. Входные данные

- project_id;
- Brand Profile;
- idea;
- topic;
- characters;
- scenes;
- dialogue lines;
- visual prompts;
- uploaded images or videos;
- CTA;
- music or audio mood.

### 5.5. Выходные данные

```text
video.mp4
caption.txt
metadata.json
cover.png или cover.txt
```

### 5.6. MVP статус

Это **первый приоритетный production format** для MVP.

---

## 6. Формат 2: Atmospheric Video

### 6.1. Назначение

`atmospheric_video` — короткое вертикальное видео с атмосферным фоном и появляющимся текстом.

Формат подходит для:

- эмоциональных фраз;
- цитат;
- смысловых сообщений;
- быстрых тестов хуков;
- массового производства;
- TikTok / Reels / Shorts;
- мягких CTA.

### 6.2. Пример для NURA

```text
Спокойный AI/stock-video background
текст о внутреннем состоянии
мягкая музыка
финальная строка: "Понять себя глубже"
```

### 6.3. Универсальная структура

```text
Opening line / hook
→ 2–4 смысловых текстовых экрана
→ финальная мысль
→ мягкий CTA
```

### 6.4. Входные данные

- project_id;
- Brand Profile;
- background video or image;
- text lines;
- CTA;
- music;
- duration;
- platform.

### 6.5. Выходные данные

```text
video.mp4
caption.txt
metadata.json
```

### 6.6. MVP статус

Should-have после первого рабочего Dialog Miniseries pipeline.

---

## 7. Формат 3: Dialog Carousel

### 7.1. Назначение

`dialog_carousel` — карусель, построенная на диалоге двух персонажей или двух точек зрения.

Формат подходит для:

- Instagram;
- Pinterest;
- VK;
- прогрева;
- сохранений;
- объяснения через сцену;
- repurpose из Dialog Miniseries.

### 7.2. Пример для NURA

```text
Слайд 1: хук
Слайд 2: реплика героини
Слайд 3: ответ NURA
Слайд 4: эмоциональный разворот
Слайд 5: короткое объяснение
Слайд 6: CTA
```

### 7.3. Универсальная структура

```text
Cover
→ Dialogue slide
→ Dialogue slide
→ Insight slide
→ Explanation slide
→ CTA slide
```

### 7.4. Входные данные

- project_id;
- Brand Profile;
- scenario;
- dialogue lines;
- images or illustrations;
- CTA;
- slide count;
- platform.

### 7.5. Выходные данные

```text
slides/
  slide_01.png
  slide_02.png
  slide_03.png
caption.txt
metadata.json
```

### 7.6. MVP статус

Should-have.  
Желательно делать как repurpose из `dialog_miniseries`.

---

## 8. Формат 4: Explainer Carousel

### 8.1. Назначение

`explainer_carousel` — объясняющая карусель, которая раскрывает тему, продукт, механику или концепцию.

Формат подходит для:

- прогрева;
- объяснения продукта;
- обучения;
- повышения доверия;
- разбора частых вопросов;
- снижения возражений.

### 8.2. Пример для NURA

```text
Что такое Матрица судьбы без мистики?
Почему дата рождения может быть зеркалом сценариев?
Что внутри полного отчёта?
Чем отчёт отличается от гадания?
```

### 8.3. Универсальная структура

```text
Cover question
→ Simple explanation
→ Example
→ Why it matters
→ Product bridge
→ CTA
```

### 8.4. Входные данные

- project_id;
- Brand Profile;
- topic;
- explanation points;
- examples;
- product bridge;
- CTA;
- slide count.

### 8.5. Выходные данные

```text
slides/
caption.txt
metadata.json
```

### 8.6. MVP статус

Should-have / second iteration.

---

## 9. Формат 5: Text Social Posts

### 9.1. Назначение

`text_social_post` — текстовый пост, адаптированный под Telegram, Threads, VK или другую текстовую платформу.

Формат подходит для:

- прогрева;
- ежедневной коммуникации;
- повторного использования сценариев;
- коротких мыслей;
- deeper reflections;
- CTA к сайту или продукту.

### 9.2. Пример для NURA

```text
Telegram:
мягкий текст от лица NURA
размышление о внутреннем состоянии
мягкий мостик к отчёту

Threads:
короткая фраза или мини-диалог

VK:
чуть более развёрнутый пост + ссылка
```

### 9.3. Универсальная структура

```text
Opening line
→ main reflection
→ insight
→ optional product bridge
→ CTA
```

### 9.4. Входные данные

- project_id;
- Brand Profile;
- source idea or scenario;
- platform;
- length;
- CTA;
- link.

### 9.5. Выходные данные

```text
post.txt
metadata.json
```

или запись в календаре публикаций.

### 9.6. MVP статус

Must-have как простой export-ready формат.

---

## 10. Формат 6: Pinterest Pin

### 10.1. Назначение

`pinterest_pin` — вертикальная карточка или короткий pin для Pinterest.

Формат подходит для:

- evergreen-контента;
- цитат;
- mini-guides;
- визуальной библиотеки;
- поискового трафика;
- повторного использования лучших фраз и каруселей.

### 10.2. Пример для NURA

```text
вертикальная карточка
краткая фраза о самопонимании
мягкий фирменный стиль
ссылка на сайт
```

### 10.3. Универсальная структура

```text
Title
→ visual background
→ short text
→ subtle brand mark
→ destination URL
```

### 10.4. Входные данные

- project_id;
- Brand Profile;
- title;
- short text;
- image or background;
- keywords;
- destination URL;
- board.

### 10.5. Выходные данные

```text
pin.png
title.txt
description.txt
metadata.json
```

### 10.6. MVP статус

Could-have / second iteration.

---

## 11. Content type IDs

Для кода и базы данных использовать следующие стабильные `content_type`:

```text
dialog_miniseries
atmospheric_video
dialog_carousel
explainer_carousel
text_social_post
pinterest_pin
```

Не использовать project-specific названия как content_type.

Неправильно:

```text
nura_dialog
nura_tarot_video
```

Правильно:

```text
dialog_miniseries
```

Проектная специфика должна задаваться через:

- project_id;
- Brand Profile;
- format settings;
- project Content Strategy.

---

## 12. Общая модель входных данных формата

Каждый формат должен поддерживать общий набор полей:

```json
{
  "content_type": "dialog_miniseries",
  "project_id": "project_nura",
  "brand_profile_id": "brand_nura",
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

Дополнительные поля зависят от формата.

---

## 13. Funnel stage

Каждый content item должен иметь stage воронки.

Возможные значения:

```text
attention
trust
conversion
retention
```

### 13.1. Attention

Задача:

- остановить внимание;
- вызвать узнавание;
- получить охват.

Типичные форматы:

- dialog_miniseries;
- atmospheric_video;
- pinterest_pin.

### 13.2. Trust

Задача:

- объяснить продукт;
- вызвать доверие;
- показать глубину.

Типичные форматы:

- dialog_carousel;
- explainer_carousel;
- text_social_post.

### 13.3. Conversion

Задача:

- привести к действию;
- перейти на сайт;
- купить;
- подписаться.

Типичные форматы:

- explainer_carousel;
- text_social_post;
- atmospheric_video with CTA.

### 13.4. Retention

Задача:

- удерживать аудиторию;
- поддерживать связь;
- прогревать повторно.

Типичные форматы:

- text_social_post;
- recurring series;
- Telegram posts.

---

## 14. Platform adaptation

Один content item может иметь несколько platform versions.

Пример:

```text
Base content: dialog_miniseries_001

Platform versions:
  tiktok
  instagram_reels
  youtube_shorts
  pinterest_video
```

Различаться могут:

- caption;
- CTA;
- hashtags;
- duration;
- title;
- metadata;
- cover;
- safe zones.

На MVP можно начинать с одного base export и platform-specific captions.

---

## 15. Repurpose logic

Content Plant должен уметь превращать одну идею в несколько форматов.

Пример:

```text
Idea: "Я устала быть сильной"

Outputs:
  dialog_miniseries
  dialog_carousel
  text_social_post for Telegram
  short Threads post
  pinterest_pin
```

Это ключевая ценность платформы.

Один смысл должен становиться контентным пакетом, а не одной единицей контента.

---

## 16. Content package

Content package — набор материалов, созданных из одной идеи или сценария.

Пример:

```text
package_001/
  video_dialog/
  carousel/
  telegram_post/
  threads_post/
  pinterest_pin/
  metadata.json
```

На MVP можно ограничиться одним форматом + текстовыми версиями.

---

## 17. Metadata requirements

Каждый выходной материал должен иметь metadata.

Минимальные поля:

```json
{
  "content_id": "content_001",
  "project_id": "project_nura",
  "content_type": "dialog_miniseries",
  "title": "Я устала быть сильной",
  "topic": "inner_fatigue",
  "funnel_stage": "attention",
  "platform": "instagram_reels",
  "cta_id": "cta_full_report",
  "utm": "",
  "status": "ready",
  "created_at": ""
}
```

Metadata нужна для:

- поиска;
- публикаций;
- аналитики;
- повторного использования;
- attribution.

---

## 18. QA requirements for all formats

Каждый формат должен проходить базовую проверку.

Общие QA-пункты:

- project_id указан;
- Brand Profile применён;
- CTA принадлежит проекту;
- нет запрещённых фраз;
- нет запрещённых тем;
- текст читаемый;
- export package содержит нужные файлы;
- metadata.json создан;
- статус корректный.

Для видео дополнительно:

- формат 9:16;
- длительность в допустимых пределах;
- safe zones соблюдены;
- текст не слишком мелкий;
- файл экспортирован корректно.

Для каруселей:

- все слайды созданы;
- порядок слайдов правильный;
- CTA-слайд есть, если требуется;
- размеры слайдов корректны.

---

## 19. MVP priority

### 19.1. First priority

```text
dialog_miniseries
text_social_post
```

Причина:

- dialog_miniseries демонстрирует главную производственную ценность;
- text_social_post легко автоматизировать и использовать для Telegram/Threads/VK.

### 19.2. Second priority

```text
dialog_carousel
atmospheric_video
```

Причина:

- хорошо переиспользуют сценарии и ассеты;
- подходят для NURA и других проектов.

### 19.3. Third priority

```text
explainer_carousel
pinterest_pin
```

Причина:

- важны для прогрева и evergreen-трафика;
- могут быть добавлены после первого production loop.

---

## 20. Нельзя делать в MVP

В рамках форматов не нужно делать:

- уникальный renderer под каждый проект;
- полностью автономную генерацию изображений через API;
- сложный template marketplace;
- editor уровня Canva;
- тяжёлый timeline video editor;
- автоподбор трендовой музыки;
- автопубликацию во все платформы как обязательную часть.

MVP должен сначала уметь стабильно производить контент по заданным форматам.

---

## 21. Связь с Brand Profile

Каждый формат должен брать из Brand Profile:

- цвета;
- шрифты;
- tone of voice;
- CTA;
- визуальные правила;
- запрещённые темы;
- ссылки;
- продуктовые офферы.

Если формат работает без Brand Profile, это ошибка архитектуры.

---

## 22. Связь с Project Profile

Project Profile даёт бизнес-контекст:

- что продаём;
- кому продаём;
- цена;
- основной сайт;
- каналы;
- воронка.

Форматы используют Project Profile через:

- CTA;
- product bridge;
- conversion content;
- UTM;
- analytics goals.

---

## 23. Связь с Analytics

Аналитика должна группировать результаты по:

- project_id;
- content_type;
- platform;
- topic;
- funnel_stage;
- CTA;
- campaign;
- date.

Это позволит понимать:

- какие форматы дают охват;
- какие форматы дают клики;
- какие форматы дают покупки;
- какие темы повторять;
- какие CTA работают.

---

## 24. Критерии готовности Content Formats MVP

Content Formats MVP считается готовым, если:

- существует общий список форматов;
- content_type ids стабильны;
- есть спецификация `dialog_miniseries`;
- есть базовая генерация `text_social_post`;
- каждый content item имеет project_id;
- каждый content item имеет content_type;
- format templates не зашиты под NURA;
- Brand Profile применяется к генерации и production;
- export package содержит metadata.

---

## 25. Документы по форматам

Для каждого формата должен быть отдельный документ:

```text
docs/04_content_formats/FORMAT_DIALOG_MINISERIES.md
docs/04_content_formats/FORMAT_ATMOSPHERIC_VIDEO.md
docs/04_content_formats/FORMAT_DIALOG_CAROUSEL.md
docs/04_content_formats/FORMAT_EXPLAINER_CAROUSEL.md
docs/04_content_formats/FORMAT_TEXT_SOCIAL_POSTS.md
docs/04_content_formats/FORMAT_PINTEREST_PINS.md
```

Каждый документ должен описывать:

- назначение;
- структуру;
- входные данные;
- выходные данные;
- правила рендера;
- правила текста;
- QA;
- platform adaptation;
- примеры;
- MVP scope.

---

## 26. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant  
Первый прикладной проект: NURA

---

## 27. Следующие документы

После этого документа необходимо создать:

1. `docs/04_content_formats/FORMAT_DIALOG_MINISERIES.md`
2. `docs/04_content_formats/FORMAT_TEXT_SOCIAL_POSTS.md`
3. `docs/05_product_design/USER_WORKFLOWS.md`
4. `docs/07_projects/nura/PROJECT_PROFILE.md`

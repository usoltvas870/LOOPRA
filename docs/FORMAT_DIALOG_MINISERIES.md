# Format: Dialog Miniseries

## 1. Назначение документа

Этот документ описывает универсальный формат **Dialog Miniseries** для платформы **Content Plant**.

Он фиксирует:

- что такое Dialog Miniseries;
- для каких задач используется формат;
- как формат работает для разных проектов;
- какие входные данные нужны;
- какая структура у сценария;
- какие ассеты требуются;
- как должен работать production pipeline;
- какие файлы должны быть на выходе;
- какие QA-проверки обязательны;
- что входит в MVP.

Документ является источником истины для реализации формата `dialog_miniseries`.

---

## 2. Краткое определение

**Dialog Miniseries** — это короткое вертикальное видео, построенное на диалоге двух персонажей, двух точек зрения или человека и смыслового проводника бренда.

Формат должен работать как мини-сцена:

```text
человек сталкивается с внутренним вопросом
→ второй голос помогает увидеть смысл
→ появляется эмоциональный разворот
→ зритель узнаёт себя
→ мягкий CTA ведёт дальше
```

На уровне платформы формат остаётся универсальным:

```text
dialog_miniseries
```

---

## 3. Главный принцип формата

Главный принцип:

> Dialog Miniseries не должен быть зашит под конкретный проект. Project-specific реализация должна задаваться через Project Profile и Brand Profile.

Платформенный формат описывает структуру:

- сцены;
- диалог;
- визуалы;
- ритм;
- CTA;
- export package;
- QA.

Проектный слой описывает:

- кто персонажи;
- как они говорят;
- как выглядит сцена;
- какие цвета и шрифты использовать;
- какой CTA показывать;
- какие темы разрешены;
- какие темы запрещены.

---

## 4. Для чего нужен формат

Dialog Miniseries подходит для задач:

- привлечь внимание;
- вызвать узнавание;
- быстро раскрыть эмоциональную проблему;
- показать голос бренда;
- создать серийный контент;
- прогреть аудиторию;
- объяснить сложную мысль через короткую сцену;
- подготовить зрителя к переходу на сайт, в канал или к продукту.

Формат особенно полезен там, где важны:

- эмоция;
- диалог;
- мягкая драматургия;
- персонаж бренда;
- повторяемость;
- storytelling.

---

## 5. Примеры применения в разных проектах

### 5.2. E-commerce

```text
Персонаж 1: покупатель
Персонаж 2: консультант
Тема: выбор товара, сомнения, сравнение, польза
Тон: экспертный, простой, помогающий
CTA: посмотреть товар / открыть подборку
```

### 5.3. Education

```text
Персонаж 1: ученик
Персонаж 2: наставник
Тема: сложная тема, ошибка, объяснение
Тон: ясный, поддерживающий, образовательный
CTA: пройти урок / скачать материал
```

### 5.4. B2B

```text
Персонаж 1: предприниматель
Персонаж 2: эксперт
Тема: бизнес-проблема, операционная ошибка, рост
Тон: точный, деловой, спокойный
CTA: запросить аудит / прочитать кейс
```

---

## 6. Базовая структура видео

Рекомендуемая структура:

```text
Scene 1: Hook
Scene 2: Problem / tension
Scene 3: Mirror / recognition
Scene 4: Reframe / insight
Scene 5: CTA / continuation
```

Для MVP допускается 3–5 сцен.

Минимальная структура:

```text
Hook
→ Dialogue turn
→ Insight
→ CTA
```

---

## 7. Рекомендуемая длительность

Для коротких вертикальных платформ:

```text
12–25 seconds
```

Рекомендуемый MVP default:

```text
15 seconds
```

Возможные варианты:

| Тип | Длительность | Когда использовать |
|---|---:|---|
| Short | 8–12 sec | быстрый hook, тест темы |
| Standard | 15–20 sec | основной формат |
| Extended | 25–35 sec | более глубокий диалог |

На MVP приоритет: 15–20 секунд.

---

## 8. Формат видео

Базовые требования:

```text
Aspect ratio: 9:16
Resolution: 1080×1920
Format: MP4
Codec: H.264
FPS: 24 / 25 / 30
Audio: optional
```

Для MVP:

```text
1080×1920
MP4
15 sec default
```

---

## 9. Структура сценария

Сценарий должен храниться структурированно.

Пример:

```json
{
  "scenario_id": "scenario_001",
  "project_id": "project_example",
  "content_type": "dialog_miniseries",
  "title": "Example Dialog",
  "topic": "example_topic",
  "funnel_stage": "attention",
  "hook": "What is the real problem?",
  "characters": ["person", "guide"],
  "scenes": [
    {
      "scene_id": "scene_01",
      "role": "hook",
      "duration_sec": 3,
      "speaker": "person",
      "dialogue": "I keep running into the same problem.",
      "overlay_text": "This keeps happening.",
      "visual_prompt": "...",
      "asset_id": ""
    }
  ],
  "cta": {
    "cta_id": "cta_primary_offer",
    "text": "Open the next step"
  },
  "caption": "",
  "status": "draft"
}
```

---

## 10. Scene model

Каждая сцена должна иметь:

```json
{
  "scene_id": "scene_01",
  "order": 1,
  "role": "hook",
  "duration_sec": 3,
  "speaker": "character_1",
  "dialogue": "",
  "overlay_text": "",
  "visual_prompt": "",
  "asset_id": "",
  "transition": "fade",
  "motion": "slow_zoom",
  "notes": ""
}
```

Обязательные поля MVP:

- scene_id;
- order;
- duration_sec;
- dialogue или overlay_text;
- visual_prompt;
- asset_id после загрузки ассета.

---

## 11. Scene roles

Рекомендуемые роли сцен:

```text
hook
problem
mirror
insight
cta
```

### 11.1. Hook

Задача:

- остановить внимание;
- дать узнавание;
- открыть эмоциональную тему.

Пример:

```text
"What keeps repeating here?"
```

### 11.2. Problem

Задача:

- раскрыть напряжение;
- показать внутренний конфликт.

Пример:

```text
"Я всё понимаю, но всё равно снова выбираю не себя."
```

### 11.3. Mirror

Задача:

- дать зрителю ощущение “это про меня”;
- назвать паттерн.

Пример:

```text
"Иногда ты держишься не потому, что хочешь, а потому что привыкла."
```

### 11.4. Insight

Задача:

- дать мягкий смысловой разворот;
- показать новое объяснение.

Пример:

```text
"Сила не обязана быть одиночеством."
```

### 11.5. CTA

Задача:

- предложить следующий шаг;
- не давить;
- связать видео с продуктом или каналом.

Пример:

```text
"Open the next step."
```

---

## 12. Персонажи

Формат поддерживает 2 основных персонажа.

Варианты:

```text
person + guide
customer + consultant
student + mentor
founder + expert
self + inner voice
```

Персонажи должны задаваться через Brand Profile или Scenario.

Нельзя делать конкретного брендового персонажа обязательным на уровне платформенного формата.

---

## 13. Dialogue rules

Диалог должен быть коротким.

Рекомендации:

- 1 мысль на сцену;
- короткие фразы;
- без длинных абзацев;
- не перегружать экран;
- не объяснять всё сразу;
- оставить воздух;
- CTA должен быть мягким и понятным.

Ограничения для MVP:

```text
max 80 characters per overlay line
max 2 lines per scene
max 5 scenes
```

Допускается менять ограничения после тестов читаемости.

---

## 14. Текстовые оверлеи

Текст должен быть:

- крупным;
- читаемым на мобильном;
- контрастным;
- в safe zone;
- не слишком длинным;
- связанным с репликой.

Рекомендуемое расположение:

```text
upper-middle или center-lower
не закрывать лицо персонажа
не попадать под UI платформ
```

Нужно учитывать safe zones для TikTok/Reels/Shorts.

---

## 15. Visual prompts

Для каждой сцены должен генерироваться visual prompt.

Prompt должен состоять из:

- описания сцены;
- персонажей;
- эмоции;
- композиции;
- visual style из Brand Profile;
- запретов из Brand Profile;
- технического формата.

Пример структуры:

```text
Scene:
...

Characters:
...

Mood:
...

Composition:
...

Brand visual style:
...

Avoid:
...

Format:
vertical 9:16
```

---

## 16. Ассеты

Для MVP пользователь генерирует изображения или видео во внешних инструментах и загружает их в Content Plant.

Поддерживаемые ассеты:

```text
image
video
audio
logo
background
```

Для `dialog_miniseries` обязательны:

- минимум 1 asset на сцену или 1 общий background;
- logo optional;
- music optional.

Рекомендуется:

```text
1 scene = 1 image/video asset
```

---

## 17. Asset requirements

Для изображений:

```text
aspect ratio: 9:16 preferred
resolution: 1080×1920 preferred
format: PNG/JPG/WebP
```

Для видео:

```text
aspect ratio: 9:16 preferred
resolution: 1080×1920 preferred
format: MP4/MOV
duration: equal or longer than scene duration
```

Если ассет не 9:16, production engine должен:

- crop;
- fit with background;
- warn user;
- or reject, depending on settings.

Для MVP достаточно warning + crop/fit.

---

## 18. Motion rules

MVP motion должен быть простым и аккуратным.

Разрешено:

```text
fade
crossfade
slow_zoom
slow_pan
gentle_parallax
```

Запрещено по умолчанию:

```text
jerky typing
fast flashes
aggressive shake
hard glitch
chaotic transitions
```

Motion style может уточняться через Brand Profile.

---

## 19. Transition rules

Рекомендуемые переходы:

```text
fade
crossfade
soft cut
```

Default motion style не должен быть глобальным правилом формата. Проект может задать нужный motion style через Brand Profile.

---

## 20. Audio

Audio optional для MVP.

Возможные варианты:

- no audio;
- background music;
- voiceover;
- sound design;
- platform-native music added manually after export.

MVP baseline:

```text
background music optional
voiceover not required
```

Важно: если пользователь планирует добавлять трендовую музыку внутри TikTok/Instagram, export package может быть без музыки или с quiet placeholder.

---

## 21. CTA

CTA должен браться из Project CTA Library.

В сценарии хранится:

```json
{
  "cta_id": "cta_primary_offer",
  "text": "Open the primary offer",
  "target": "website"
}
```

Нельзя зашивать CTA в формат.

CTA может быть:

- текстом на последней сцене;
- caption CTA;
- link CTA;
- soft brand line.

---

## 22. Caption

Для каждого видео должен генерироваться caption.

Caption должен учитывать:

- project_id;
- Brand Profile;
- platform;
- CTA;
- UTM;
- tone of voice.

Пример структуры caption:

```text
Hook sentence.

Short reflection.

CTA with link or instruction.

#hashtags
```

На MVP допустимо хранить несколько caption versions:

```text
caption_tiktok.txt
caption_instagram.txt
caption_youtube_shorts.txt
```

или один `caption.txt`.

---

## 23. Hashtags

Hashtags optional.

Если используются, они должны быть:

- platform-specific;
- project-specific;
- не слишком многочисленные;
- не противоречить positioning;
- не содержать запрещённых тем.

Для MVP можно генерировать 3–8 hashtags.

---

## 24. Export package

Минимальный export package:

```text
dialog_miniseries_{content_id}/
  video.mp4
  caption.txt
  metadata.json
  cover.txt
```

Расширенный вариант:

```text
dialog_miniseries_{content_id}/
  video.mp4
  cover.png
  captions/
    caption_tiktok.txt
    caption_instagram.txt
    caption_youtube_shorts.txt
  metadata.json
  source/
    scenario.json
    prompts.json
```

Для MVP достаточно минимального пакета.

---

## 25. Metadata

`metadata.json` должен включать:

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "content_type": "dialog_miniseries",
  "title": "",
  "topic": "",
  "funnel_stage": "attention",
  "platforms": ["tiktok", "instagram_reels", "youtube_shorts"],
  "cta_id": "",
  "scenario_id": "",
  "asset_ids": [],
  "duration_sec": 15,
  "resolution": "1080x1920",
  "status": "ready",
  "created_at": ""
}
```

---

## 26. Production pipeline

Основной pipeline:

```text
Idea
→ Scenario
→ Scenes
→ Visual Prompts
→ Asset Upload
→ Asset-to-Scene Mapping
→ Render Job
→ Preview
→ Review
→ Export Package
→ Publication
→ Metrics
```

---

## 27. Render job

Render job должен хранить:

```json
{
  "render_job_id": "render_001",
  "project_id": "project_example",
  "scenario_id": "scenario_001",
  "content_type": "dialog_miniseries",
  "template_id": "dialog_miniseries_default",
  "status": "queued",
  "output_path": "",
  "error": "",
  "created_at": "",
  "updated_at": ""
}
```

Статусы:

```text
queued
rendering
rendered
failed
cancelled
```

---

## 28. Content statuses

Рекомендуемые статусы:

```text
draft
needs_assets
ready_to_render
rendering
rendered
needs_review
approved
rejected
scheduled
published
analyzed
archived
failed
```

---

## 29. Review flow

MVP review flow:

1. Видео создано.
2. Статус: `needs_review`.
3. Пользователь смотрит preview.
4. Пользователь выбирает:
   - approve;
   - reject;
   - replace asset;
   - edit text;
   - regenerate caption.
5. После approve создаётся export package.
6. Статус: `approved` или `ready`.

---

## 30. QA checks

Обязательные QA checks:

### 30.1. Data QA

- project_id указан;
- content_type = dialog_miniseries;
- scenario_id указан;
- scenes существуют;
- у каждой сцены есть order;
- CTA принадлежит проекту;
- Brand Profile найден.

### 30.2. Asset QA

- ассеты существуют;
- ассеты принадлежат тому же project_id;
- каждая сцена имеет asset_id или допустимый fallback;
- формат файлов поддерживается.

### 30.3. Text QA

- текст не слишком длинный;
- текст не содержит forbidden phrases;
- CTA корректен;
- нет запрещённых обещаний;
- язык соответствует project default language.

### 30.4. Video QA

- видео экспортировано;
- формат 9:16;
- длительность в допустимом диапазоне;
- resolution корректный;
- файл не пустой;
- текст читаем;
- safe zones соблюдены.

---

## 31. Safe zones

Текст не должен попадать в зоны интерфейса платформ.

Рекомендуемое правило:

```text
top margin: 160 px
bottom margin: 260 px
left/right margin: 80 px
```

Для разных платформ safe zones могут отличаться.

На MVP можно использовать conservative safe zone.

---

## 32. Templates

MVP template:

```text
dialog_miniseries_default
```

Параметры template:

- vertical canvas;
- background media;
- text overlay;
- transition;
- optional logo;
- optional CTA screen;
- Brand Profile colors;
- Brand Profile fonts.

Template не должен быть `dialog_miniseries_template`, если его можно использовать для других проектов.

Можно иметь project preset:

```text
dialog_miniseries_default + active project Brand Profile
```

---

## 33. Platform versions

Base video может использоваться для:

```text
tiktok
instagram_reels
youtube_shorts
```

На MVP допустимо:

- один MP4;
- разные captions;
- один metadata file.

В будущем:

- platform-specific safe zones;
- platform-specific cover;
- platform-specific duration;
- platform-specific CTA.

---

## 34. Repurpose

Из `dialog_miniseries` можно создавать:

- `dialog_carousel`;
- `text_social_post`;
- `pinterest_pin`;
- quote cards;
- Telegram post;
- Threads post.

Это важная часть будущей ценности формата.

На MVP желательно генерировать хотя бы:

```text
video + caption + text_social_post
```

---

## 35. Project-specific implementation

A first validation project may be used to test the platform, but project-specific rules must live in `docs/07_projects/{project_slug}/`.

Project-specific implementation may define:

- characters;
- relationship between speakers;
- tone of dialogue;
- allowed and forbidden topics;
- visual direction;
- CTA rules;
- example scenarios;
- prompt examples.

These rules must not become global format defaults.

---

## 36. MVP scope

В MVP входит:

- создание сценария `dialog_miniseries`;
- 3–5 сцен;
- visual prompts для сцен;
- загрузка ассетов;
- привязка ассетов к сценам;
- простой рендер MP4 9:16;
- текстовые overlays;
- soft transitions;
- caption;
- metadata;
- export package;
- basic review;
- basic QA.

---

## 37. Не входит в MVP

В MVP не входит:

- сложный timeline editor;
- ручное редактирование каждой анимации в UI;
- автоматическая генерация изображений через API;
- автоматическая генерация видео через API;
- lip-sync avatars;
- сложная voiceover-система;
- multi-language dubbing;
- автоподбор трендовой музыки;
- platform-native posting во все соцсети.

---

## 38. Критерии готовности формата

Формат `dialog_miniseries` считается готовым для MVP, если:

- можно создать сценарий с 3–5 сценами;
- каждая сцена имеет prompt;
- можно загрузить ассеты;
- можно связать ассеты со сценами;
- можно запустить render job;
- получен MP4 1080×1920;
- создан caption.txt;
- создан metadata.json;
- есть preview/review;
- можно approve/reject;
- export package создан;
- в renderer нет hardcode конкретного бренда;
- Brand Profile применяется к тексту и визуальному оформлению.

---

## 39. Пример минимального сценария

```json
{
  "project_id": "project_example",
  "content_type": "dialog_miniseries",
  "title": "Example Dialog",
  "funnel_stage": "attention",
  "scenes": [
    {
      "order": 1,
      "role": "hook",
      "duration_sec": 3,
      "speaker": "person",
      "overlay_text": "This keeps happening.",
      "visual_prompt": "..."
    },
    {
      "order": 2,
      "role": "mirror",
      "duration_sec": 4,
      "speaker": "guide",
      "overlay_text": "Look at the pattern before choosing the next step.",
      "visual_prompt": "..."
    },
    {
      "order": 3,
      "role": "insight",
      "duration_sec": 4,
      "speaker": "guide",
      "overlay_text": "A clearer frame can change the next action.",
      "visual_prompt": "..."
    },
    {
      "order": 4,
      "role": "cta",
      "duration_sec": 4,
      "speaker": "guide",
      "overlay_text": "Open the next step.",
      "visual_prompt": "..."
    }
  ],
  "cta_id": "cta_primary_offer"
}
```

Это пример для конкретного проекта, а не правило платформы.

---

## 40. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant  
Первый validation project: задаётся отдельно в docs/07_projects/{project_slug}/

---

## 41. Следующие документы

После этого документа необходимо создать:

1. `docs/04_content_formats/FORMAT_TEXT_SOCIAL_POSTS.md`
2. `docs/05_product_design/USER_WORKFLOWS.md`
3. `docs/07_projects/{project_slug}/PROJECT_PROFILE.md`
4. `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`

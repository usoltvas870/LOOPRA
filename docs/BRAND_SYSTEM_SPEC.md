# Brand System Spec

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ описывает универсальную бренд-систему платформы **Content Plant**.

Он фиксирует:

- что такое Brand Profile;
- какие параметры бренда должны храниться в системе;
- как брендовые настройки применяются к сценариям, визуалам, рендерам, публикациям и аналитике;
- как универсальные форматы адаптируются под разные проекты;
- какие данные являются платформенными, а какие проектными;
- какие требования входят в MVP;
- что нужно предусмотреть для будущего SaaS.

Документ не описывает конкретный бренд.  
Project-specific правила должны храниться отдельно:

```text
docs/07_projects/{project_slug}/
```

---

## 2. Главная идея Brand System

Content Plant должен производить контент для разных проектов и брендов.

Чтобы один и тот же production engine мог работать с разными проектами, все брендовые настройки должны быть вынесены в **Brand Profile**.

Brand Profile — это набор данных, который отвечает на вопросы:

- кто говорит;
- кому говорит;
- как говорит;
- как выглядит;
- какие продукты продвигает;
- какие CTA использует;
- какие темы допустимы;
- какие темы запрещены;
- какие визуальные правила обязательны.

Главный принцип:

> Никакие брендовые правила не должны быть жёстко зашиты в код платформы.

---

## 3. Что такое Brand Profile

**Brand Profile** — это проектная конфигурация, которая позволяет Content Plant адаптировать универсальные форматы под конкретный бренд.

Brand Profile принадлежит конкретному Project.

Пример:

```text
Project: Example Project
Brand Profile: Example Brand settings

Project: Client Brand
Brand Profile: Client Brand settings
```

У каждого проекта может быть один основной Brand Profile на MVP.

В будущем проект может поддерживать несколько Brand Profiles, например:

- основной бренд;
- бренд под конкретную кампанию;
- seasonal campaign;
- sub-brand;
- white-label style.

---

## 4. Роль Brand Profile в системе

Brand Profile используется в ключевых модулях платформы.

### 4.1. Scenario Studio

Использует Brand Profile для:

- выбора tone of voice;
- генерации реплик;
- генерации CTA;
- учёта запрещённых тем;
- выбора эмоциональной интонации;
- адаптации сценария под проект.

### 4.2. Visual Prompt Generation

Использует Brand Profile для:

- описания визуального стиля;
- выбора цветовой палитры;
- описания персонажей;
- запрета нежелательных визуальных элементов;
- создания consistent prompts для внешних генераторов изображений.

### 4.3. Production Engine

Использует Brand Profile для:

- цветов;
- шрифтов;
- логотипов;
- композиций;
- safe zones;
- финальных экранов;
- оформления CTA;
- выбора визуальных шаблонов.

### 4.4. Publishing Hub

Использует Brand Profile для:

- ссылок;
- UTM;
- platform-specific captions;
- CTA;
- хэштегов;
- tone adaptation по платформам.

### 4.5. QA and Review

Использует Brand Profile для проверки:

- соответствия стилю;
- соответствия tone of voice;
- отсутствия запрещённых тем;
- корректности CTA;
- брендовой целостности.

### 4.6. Analytics

Использует Brand Profile и Project данные для анализа:

- эффективности CTA;
- эффективности визуальных стилей;
- эффективности контентных направлений;
- продаж по проекту.

---

## 5. Минимальная структура Brand Profile

Для MVP Brand Profile должен включать следующие блоки:

```json
{
  "brand_profile_id": "brand_example",
  "project_id": "project_example",
  "brand_name": "Example Brand",
  "brand_description": "",
  "positioning": "",
  "target_audience": "",
  "tone_of_voice": {},
  "visual_identity": {},
  "content_rules": {},
  "cta_library": [],
  "product_offers": [],
  "links": {},
  "platform_settings": {},
  "forbidden_topics": [],
  "created_at": "",
  "updated_at": ""
}
```

---

## 6. Brand Identity

Блок Brand Identity описывает базовые сведения о бренде.

Поля:

```json
{
  "brand_name": "Example Brand",
  "brand_description": "Short description of the brand.",
  "positioning": "How the brand should be perceived.",
  "mission": "Optional mission statement.",
  "audience_summary": "Short audience description.",
  "brand_archetype": "Optional archetype or role.",
  "language": "ru"
}
```

Для MVP обязательны:

- brand_name;
- positioning;
- audience_summary;
- language.

---

## 7. Target Audience

Блок Target Audience описывает аудиторию проекта.

Поля:

```json
{
  "primary_audience": "Main audience description.",
  "secondary_audience": "Optional secondary audience.",
  "pains": [],
  "desires": [],
  "objections": [],
  "awareness_level": "problem_aware",
  "buying_motivation": []
}
```

Пример использования:

- Scenario Studio пишет сценарии, которые попадают в боли аудитории;
- CTA учитывают мотивацию покупки;
- QA проверяет, что текст не уходит в неподходящий тон.

---

## 8. Tone of Voice

Tone of Voice описывает, как бренд говорит.

Минимальная структура:

```json
{
  "style": ["soft", "clear", "warm"],
  "personality": "calm guide",
  "voice_rules": [
    "speak simply",
    "avoid pressure",
    "avoid fear-based claims"
  ],
  "allowed_phrases": [],
  "forbidden_phrases": [],
  "examples_good": [],
  "examples_bad": []
}
```

Tone of Voice должен использоваться во всех текстовых генерациях.

### 8.1. Поля Tone of Voice

| Поле | Назначение |
|---|---|
| `style` | краткие характеристики тона |
| `personality` | роль голоса бренда |
| `voice_rules` | правила коммуникации |
| `allowed_phrases` | фразы, которые можно использовать |
| `forbidden_phrases` | фразы, которых нужно избегать |
| `examples_good` | хорошие примеры текста |
| `examples_bad` | плохие примеры текста |

---

## 9. Visual Identity

Visual Identity описывает визуальную систему бренда.

Минимальная структура:

```json
{
  "visual_style_description": "",
  "colors": {
    "background": "",
    "text": "",
    "primary_accent": "",
    "secondary_accent": "",
    "muted_accent": ""
  },
  "fonts": {
    "primary": "",
    "secondary": "",
    "fallback": ""
  },
  "logo": {
    "file_path": "",
    "usage_rules": ""
  },
  "composition_rules": [],
  "image_style": "",
  "motion_style": "",
  "forbidden_visuals": []
}
```

---

## 10. Colors

Цвета должны храниться как данные Brand Profile.

Пример:

```json
{
  "colors": {
    "background": "#EFEEE9",
    "surface": "#FFFFFF",
    "text": "#1A1A1A",
    "muted_text": "#5A5752",
    "primary_accent": "#C2A476",
    "secondary_accent": "#B8743F",
    "tertiary_accent": "#6B8068"
  }
}
```

Для MVP достаточно:

- background;
- surface;
- text;
- muted_text;
- primary_accent;
- secondary_accent.

Production templates должны брать цвета из Brand Profile, а не из хардкода.

---

## 11. Typography

Шрифты должны храниться в Brand Profile.

Пример:

```json
{
  "fonts": {
    "primary": "Manrope",
    "secondary": "Playfair Display",
    "fallback": "Arial"
  }
}
```

Если конкретный шрифт недоступен в production engine, должен использоваться fallback.

В MVP важно:

- не хардкодить один шрифт для всех проектов;
- позволить проекту задавать primary и secondary font;
- иметь безопасный fallback.

---

## 12. Logo and Brand Assets

Brand Profile должен ссылаться на логотипы и брендовые ассеты.

Пример:

```json
{
  "logo": {
    "main": "storage/projects/{project_slug}/assets/logos/logo_main.png",
    "icon": "storage/projects/{project_slug}/assets/logos/icon.png",
    "monochrome": "storage/projects/{project_slug}/assets/logos/logo_mono.png",
    "usage_rules": "Use small and unobtrusive logo placement."
  }
}
```

Логотипы являются project-level assets.

Нельзя хранить логотипы всех проектов в одной глобальной папке без project separation.

---

## 13. Characters

Некоторые проекты используют персонажей.

Brand Profile должен уметь описывать персонажей.

Пример:

```json
{
  "characters": [
    {
      "character_id": "guide",
      "name": "Guide",
      "role": "Project guide",
      "description": "Reusable project character defined by Brand Profile.",
      "visual_rules": [],
      "voice_rules": [],
      "forbidden_changes": []
    },
    {
      "character_id": "viewer_avatar",
      "name": "Second character",
      "role": "Audience reflection",
      "description": "A person who represents the viewer's inner state."
    }
  ]
}
```

Для MVP characters могут храниться как часть Brand Profile или как отдельные project-level entities.

---

## 14. Product Offers

Brand Profile или Project Profile должен содержать продуктовые офферы.

Пример для конкретного проекта:

```json
{
  "product_offers": [
    {
      "offer_id": "primary_offer",
      "name": "Primary offer",
      "price": "{price}",
      "currency": "RUB",
      "cta": "Open the primary offer",
      "url": "https://example.com"
    },
    {
      "offer_id": "recurring_offer",
      "name": "Recurring Offer",
      "price": "{recurring_price}",
      "currency": "RUB",
      "period": "month",
      "cta": "Open subscription"
    }
  ]
}
```

Офферы должны быть проектными.

Нельзя зашивать цену или продукт в универсальные форматы.

---

## 15. CTA Library

CTA Library должна храниться на уровне проекта.

Структура CTA:

```json
{
  "cta_id": "cta_primary_offer",
  "project_id": "project_example",
  "label": "Open the primary offer",
  "intent": "conversion",
  "target": "website",
  "url": "https://example.com",
  "utm_template": "utm_source={platform}&utm_medium=organic&utm_campaign={campaign}&utm_content={content_id}"
}
```

Типы CTA:

```text
attention
engagement
profile_visit
website_click
lead
conversion
subscription
retention
```

Scenario Studio и Publishing Hub должны выбирать CTA по intent и platform.

---

## 16. Links

Brand Profile должен хранить ссылки проекта.

Пример:

```json
{
  "links": {
    "website": "https://example.com",
    "telegram_bot": "",
    "telegram_channel": "",
    "instagram": "",
    "tiktok": "",
    "youtube": "",
    "vk": "",
    "pinterest": ""
  }
}
```

На MVP ссылки могут быть неполными.

---

## 17. Platform Settings

Для каждого проекта нужны настройки платформ.

Пример:

```json
{
  "platform_settings": {
    "instagram": {
      "enabled": true,
      "handle": "example.brand",
      "posting_mode": "manual_export",
      "default_format": "reels"
    },
    "tiktok": {
      "enabled": true,
      "posting_mode": "manual_export",
      "default_format": "vertical_video"
    },
    "telegram": {
      "enabled": true,
      "posting_mode": "manual_export"
    }
  }
}
```

`posting_mode` может быть:

```text
manual_export
semi_auto
auto_api
disabled
```

---

## 18. Content Rules

Content Rules задают, что бренд может и не может говорить.

Пример:

```json
{
  "content_rules": {
    "allowed_topics": [],
    "restricted_topics": [],
    "forbidden_topics": [],
    "required_disclaimers": [],
    "claims_policy": [],
    "emotional_boundaries": []
  }
}
```

Для проектов в чувствительных нишах это особенно важно.

Например, для чувствительных ниш важно не обещать:

- гарантированный результат;
- недоказуемый эффект;
- фатальные утверждения;
- манипуляции страхом;
- claims, которые нарушают правила проекта или платформы публикации.

Эти правила должны жить в проектном Brand Profile.

---

## 19. Forbidden Visuals

Brand Profile должен поддерживать список запрещённых визуальных элементов.

Пример:

```json
{
  "forbidden_visuals": [
    "horror style",
    "dark occult symbols",
    "blood",
    "fear-based imagery",
    "cheap mystic cliches"
  ]
}
```

Production Engine и Visual Prompt Generation должны учитывать этот список.

---

## 20. Motion Style

Motion Style описывает анимационную подачу.

Пример:

```json
{
  "motion_style": {
    "pace": "slow",
    "transitions": ["fade", "soft zoom"],
    "avoid": ["jerky typing", "fast flashing", "aggressive cuts"]
  }
}
```

Это важно для видеоформатов.

---

## 21. Brand Profile and Universal Formats

Универсальный формат не должен знать конкретный бренд.

Пример:

```text
Format: Dialog Miniseries
```

Общие параметры формата:

- 3–5 сцен;
- 9:16;
- персонажи;
- диалог;
- текстовые оверлеи;
- CTA;
- export package.

Brand Profile подставляет:

- персонажей;
- tone of voice;
- цвета;
- шрифты;
- визуальный стиль;
- CTA;
- запреты;
- ссылки.

---

## 22. Пример применения Brand Profile

### 22.1. Один формат

```text
Dialog Miniseries
```

### 22.2. Demo Project

Параметры:

- персонаж: project guide;
- второй персонаж: audience representative;
- тон: задаётся Brand Profile;
- стиль: задаётся Visual Identity;
- CTA: выбирается из project CTA Library.

### 22.3. E-commerce project

Параметры:

- персонаж: consultant;
- второй персонаж: customer;
- тон: expert and helpful;
- стиль: commercial and clean;
- CTA: product page or category page.

### 22.4. Итог

Production Engine использует один формат, но разные Brand Profiles.

---

## 23. Brand Profile в генерации сценариев

Scenario Studio должен получать:

1. выбранный Project;
2. Brand Profile;
3. Content Format;
4. Idea или Trend;
5. цель контента.

На основе этого он генерирует сценарий.

Пример логики:

```text
Input:
  project = Demo Project
  format = dialog_miniseries
  idea = "Example content idea"
  funnel_stage = attention

Scenario Studio:
  reads Brand Profile
  applies project tone
  applies forbidden claims
  selects soft CTA
  generates scenes and dialogue
```

---

## 24. Brand Profile в visual prompts

Visual prompts должны собираться из:

- описания сцены;
- персонажей;
- visual style;
- colors;
- composition rules;
- forbidden visuals;
- platform requirements.

Пример структуры prompt:

```text
Scene description:
  ...

Brand style:
  ...

Characters:
  ...

Composition:
  ...

Avoid:
  ...
```

Промт не должен каждый раз придумывать стиль заново.  
Он должен использовать Brand Profile как источник истины.

---

## 25. Brand Profile в Production Engine

Production Engine должен использовать Brand Profile для:

- выбора цветов;
- выбора шрифтов;
- оформления текста;
- логотипа;
- финального экрана;
- CTA;
- визуального стиля template.

Пример:

```text
render_dialog_miniseries(
  project_id="project_example",
  scenario_id="scenario_001",
  template_id="dialog_miniseries_default"
)
```

Renderer должен загрузить Brand Profile проекта и применить настройки.

---

## 26. Brand Profile в QA

QA должен проверять:

- есть ли запрещённые слова;
- нет ли запрещённых обещаний;
- соответствует ли CTA проекту;
- не использован ли чужой брендовый стиль;
- корректны ли цвета;
- есть ли логотип, если он нужен;
- не нарушены ли visual constraints.

Пример QA-ошибки:

```text
Content item uses a CTA that is not present in project CTA Library.
```

---

## 27. Brand Profile в аналитике

Analytics может использовать Brand Profile для анализа:

- какой CTA лучше работает;
- какие визуальные стили дают удержание;
- какие content pillars дают клики;
- какие product offers конвертируют;
- какие platform settings требуют изменений.

В MVP достаточно связать метрики с project_id, content_type и CTA.

---

## 28. Brand Profile versioning

В будущем Brand Profile должен иметь версионирование.

Причина:

- бренд может меняться;
- цвета могут обновляться;
- CTA могут меняться;
- tone of voice может уточняться;
- нужно понимать, по какой версии был создан конкретный контент.

Для MVP можно упростить, но желательно предусмотреть поле:

```json
{
  "brand_profile_version": "0.1"
}
```

ContentItem может хранить:

```json
{
  "brand_profile_version_used": "0.1"
}
```

---

## 29. Default Brand Profile

Если проект только создан, система может предложить минимальный default Brand Profile.

Поля:

- brand_name;
- language;
- primary color;
- tone;
- target platforms;
- primary URL.

Но качественный контент требует ручного заполнения бренд-профиля.

---

## 30. Brand Profile onboarding

В MVP onboarding может быть простой формой.

Минимальные шаги:

1. Название бренда.
2. Описание проекта.
3. Целевая аудитория.
4. Tone of voice.
5. Цвета.
6. Основной сайт.
7. CTA.
8. Запрещённые темы.
9. Платформы публикации.

В SaaS-версии onboarding может стать полноценным мастером настройки.

---

## 31. Что входит в MVP

В MVP входит:

- один Brand Profile на проект;
- базовые поля бренда;
- цвета;
- шрифты;
- tone of voice;
- CTA;
- ссылки;
- запреты;
- визуальное описание;
- использование Brand Profile в сценариях;
- использование Brand Profile в рендерах;
- project-level хранение brand assets.

---

## 32. Что не входит в MVP

В MVP не входит:

- несколько Brand Profiles на один проект;
- сложное версионирование;
- brand approval workflow;
- автоматическое извлечение бренда с сайта;
- AI brand audit;
- marketplace brand templates;
- team permissions для изменения бренда;
- публичный onboarding для внешних пользователей.

Эти функции могут быть добавлены позже.

---

## 33. Минимальные требования к интерфейсу Brand Profile

В интерфейсе проекта должен быть раздел:

```text
Project Settings → Brand Profile
```

Минимальные вкладки:

- Basics;
- Audience;
- Tone of Voice;
- Visual Identity;
- CTA;
- Links;
- Restrictions;
- Platforms.

На MVP можно сделать всё на одной странице, если это ускоряет разработку.

---

## 34. Минимальные требования к данным

Каждый Brand Profile должен иметь:

```text
brand_profile_id
project_id
brand_name
positioning
audience_summary
tone_of_voice
visual_identity
cta_library
links
content_rules
created_at
updated_at
```

Все поля, которые содержат сложную структуру, могут храниться как JSON на MVP.

---

## 35. Ошибки, которых нужно избегать

### 35.1. Хардкод бренда в шаблоне

Плохо:

```text
template always uses hardcoded brand colors and hardcoded CTA
```

Хорошо:

```text
template loads colors and CTA from Brand Profile
```

---

### 35.2. Один глобальный Tone of Voice

Плохо:

```text
All generated content uses the same voice.
```

Хорошо:

```text
Scenario Studio applies project tone_of_voice.
```

---

### 35.3. Глобальная CTA-библиотека

Плохо:

```text
All projects use one hardcoded CTA
```

Хорошо:

```text
Each project has its own CTA Library.
```

---

### 35.4. Визуальный стиль в prompt без Brand Profile

Плохо:

```text
Prompt manually repeats style every time.
```

Хорошо:

```text
Prompt builder composes scene prompt + Brand Profile visual style.
```

---

## 36. Критерии готовности Brand System MVP

Brand System MVP считается готовой, если:

- у каждого проекта есть Brand Profile;
- Brand Profile можно редактировать;
- Scenario Studio использует Brand Profile;
- Visual Prompt Generation использует Brand Profile;
- Production Engine использует цвета, шрифты и CTA из Brand Profile;
- ассеты бренда привязаны к проекту;
- CTA хранятся на уровне проекта;
- в коде нет жёсткой привязки к конкретному бренду;
- универсальный формат можно применить минимум к двум проектам с разными brand settings.

---

## 37. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant  
Первый validation project: задаётся отдельно в docs/07_projects/{project_slug}/

---

## 38. Следующие документы

После этого документа необходимо создать:

1. `docs/06_agents/AGENT_RULES.md`
2. `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
3. `docs/05_product_design/PROJECT_SETTINGS_SPEC.md`
4. `docs/07_projects/{project_slug}/PROJECT_PROFILE.md`

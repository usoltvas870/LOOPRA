# Format: Atmospheric Video

## 1. Назначение документа

Этот документ описывает универсальный формат **Atmospheric Video** для платформы **Content Plant**.

Он фиксирует:

- что такое `atmospheric_video`;
- для каких задач используется формат;
- какие входные данные нужны;
- как устроена структура ролика;
- какие ассеты требуются;
- как формат адаптируется под разные Brand Profiles;
- какие output files должны создаваться;
- какие QA-проверки обязательны;
- что входит и не входит в MVP.

Документ является платформенным и не привязан к конкретному проекту, бренду или нише.

---

## 2. Краткое определение

**Atmospheric Video** — это короткое вертикальное видео, построенное вокруг атмосферного визуального фона и последовательного появления текстовых смысловых блоков.

Базовая формула:

```text
Background image / video
+ Text sequence
+ Brand Profile
+ Motion style
+ Optional audio
+ Optional CTA
= Atmospheric Video
```

Формат может использоваться для:

- эмоциональных сообщений;
- коротких смысловых наблюдений;
- цитат;
- объясняющих микротекстов;
- soft-selling content;
- brand reminders;
- быстрых тестов hooks;
- repurpose из сценариев, постов или аналитических инсайтов.

---

## 3. Главный принцип формата

`atmospheric_video` должен быть **meaning-first** и **template-driven**.

Это значит:

```text
Universal format structure
+ Project Brand Profile
+ Text blocks
+ Background asset
+ Output settings
= Project-specific atmospheric video
```

Формат не должен содержать hardcoded брендовые цвета, тексты, CTA, персонажей, продукты, цены или project-specific визуальные правила.

Все project-specific элементы должны поступать из:

- Project Settings;
- Brand Profile;
- CTA Library;
- Content Rules;
- Platform Settings;
- project-level documents in `docs/07_projects/{project_slug}/`.

---

## 4. Для чего нужен формат

Atmospheric Video нужен, чтобы быстро превращать короткие смыслы в публикационные видео без сложной сцены, диалога или большого количества ассетов.

Формат особенно полезен, когда нужно:

- быстро протестировать hook;
- выпускать регулярный lightweight content;
- усиливать presence бренда между большими форматами;
- превращать текстовые идеи в видео;
- делать platform-ready ролики из одного background asset;
- создавать evergreen content;
- масштабировать удачные мысли в несколько платформ.

---

## 5. Роль в content portfolio

В портфеле форматов Content Plant `atmospheric_video` занимает место лёгкого production format.

Сравнение:

| Format | Complexity | Main input | Best for |
|---|---:|---|---|
| `dialog_miniseries` | higher | scenario + scene assets | storytelling, dialogue, emotional arc |
| `atmospheric_video` | medium / low | text sequence + background | hooks, reflections, simple messages |
| `dialog_carousel` | medium | scenario + slides | saves, visual explanation |
| `text_social_post` | low | idea / scenario / content item | text platforms |
| `pinterest_pin` | low / medium | short text + image | evergreen discovery |

Atmospheric Video не должен заменять более глубокие форматы. Он нужен как быстрый и повторяемый слой производства.

---

## 6. Supported platforms

MVP target platforms:

```text
tiktok
instagram
youtube_shorts
```

Should-have:

```text
pinterest
vk
telegram
```

Future:

```text
facebook_reels
linkedin_video
website_embed
```

Platform-specific rules должны храниться в Project Settings → Platform Settings.

---

## 7. Recommended video specs

Базовые требования для MVP:

```text
aspect_ratio: 9:16
resolution: 1080x1920
format: mp4
codec: h264
fps: 24 / 25 / 30
duration_sec: 8-20
recommended_default_duration_sec: 15
```

Should-have variants:

```text
square: 1080x1080
portrait_feed: 1080x1350
wide: 1920x1080
```

Но MVP должен начинаться с vertical video 9:16.

---

## 8. Basic structure

Рекомендуемая структура ролика:

```text
Opening hook
→ Meaning block 1
→ Meaning block 2
→ Reframe / insight
→ Optional CTA / closing line
```

Минимальная структура:

```text
Hook
→ Main thought
→ Closing
```

Расширенная структура:

```text
Hook
→ Problem
→ Observation
→ Reframe
→ Example
→ CTA
```

---

## 9. Text sequence model

Atmospheric Video строится на последовательности текстовых блоков.

```json
{
  "text_block_id": "text_block_001",
  "order": 1,
  "role": "hook",
  "text": "Short opening line.",
  "start_sec": 0.0,
  "end_sec": 3.0,
  "animation": "fade_in",
  "position": "center",
  "status": "draft"
}
```

Обязательные поля MVP:

```text
order
role
text
```

Желательные поля:

```text
start_sec
end_sec
animation
position
emphasis
```

---

## 10. Text block roles

Рекомендуемые роли:

```text
hook
context
problem
observation
insight
reframe
example
proof
cta
closing
```

### hook

Первая строка, которая должна остановить внимание.

### context

Короткое уточнение ситуации.

### problem

Напряжение, вопрос или боль.

### observation

Наблюдение или мысль.

### insight

Смысловой поворот.

### reframe

Новая рамка восприятия.

### example

Короткий пример.

### proof

Поддерживающий аргумент, если формат используется для education / B2B / product explanation.

### cta

Следующий шаг, если он нужен.

### closing

Финальная строка без прямого CTA.

---

## 11. Recommended text limits

Для vertical video MVP:

```text
blocks_per_video: 3-6
characters_per_block: 20-90
max_lines_per_block: 2
recommended_line_length: 18-32 characters
```

Правила:

- один смысловой акцент на экран;
- не перегружать кадр;
- не использовать длинные абзацы;
- сохранять читаемость на мобильном;
- учитывать platform safe zones.

---

## 12. Timing rules

Рекомендуемые длительности:

| Block role | Duration |
|---|---:|
| hook | 1.5–3 sec |
| context | 2–3 sec |
| problem | 2–4 sec |
| observation | 2–4 sec |
| insight | 2–4 sec |
| CTA / closing | 2–4 sec |

MVP может автоматически распределять timing по количеству text blocks.

Пример:

```text
15 sec video
5 text blocks
≈ 3 sec per block
```

Should-have: manual timing adjustment.

---

## 13. Required inputs

Для создания Atmospheric Video нужны:

```text
project_id
content_type = atmospheric_video
title
text_sequence
background_asset_id or background_prompt
Brand Profile
target_platforms
output_spec
optional CTA
optional audio
```

MVP допускает два входных сценария:

1. User uploads background asset.
2. User provides text sequence and generates/upload asset externally.

Built-in image/video generation through API is not required for MVP.

---

## 14. Scenario entity usage

Atmospheric Video может быть создан как Scenario.

Минимальный сценарий:

```json
{
  "scenario_id": "scenario_001",
  "project_id": "project_example",
  "content_type": "atmospheric_video",
  "title": "Example Atmospheric Video",
  "funnel_stage": "attention",
  "target_platforms": ["instagram", "tiktok"],
  "text_blocks": [],
  "visual_prompt": "",
  "cta_id": "cta_001",
  "status": "draft"
}
```

Если формат создаётся из `text_social_post`, Scenario Studio может автоматически извлечь короткую video sequence из post body.

---

## 15. Source types

Atmospheric Video может создаваться из:

```text
idea
scenario
text_social_post
trend
content_item
analytics_insight
manual_input
```

Примеры:

```text
Idea → Atmospheric Video
Text Social Post → Short video sequence
Trend → Adapted atmospheric hook video
Analytics Insight → Repurpose successful line into video
```

---

## 16. Background asset requirements

Supported background asset types:

```text
image
video
animated_background
template_asset
```

MVP supported:

```text
image
video
```

Recommended asset specs:

### Image

```text
aspect_ratio: 9:16 preferred
resolution: 1080x1920 preferred
formats: png, jpg, jpeg, webp
```

### Video

```text
aspect_ratio: 9:16 preferred
resolution: 1080x1920 preferred
formats: mp4, mov, webm
duration: equal or longer than output duration preferred
```

If asset is not 9:16, Production Engine may:

- crop;
- fit with background fill;
- blur edges;
- warn user;
- reject if project settings require exact match.

MVP default: warning + crop/fit.

---

## 17. Background visual rules

Background должен поддерживать текст, а не спорить с ним.

Рекомендации:

- избегать слишком контрастных деталей под текстом;
- не располагать важные лица или объекты в местах text overlay;
- учитывать safe zones;
- не использовать chaotic motion по умолчанию;
- избегать flicker / flashing;
- поддерживать motion style из Brand Profile.

Brand Profile может задавать:

```text
preferred_background_types
forbidden_visuals
image_style
motion_style
contrast_rules
logo_rules
```

---

## 18. Visual Prompt

Если background asset ещё не создан, Scenario Studio может подготовить visual prompt.

Prompt должен учитывать:

- topic;
- text mood;
- Brand Profile visual identity;
- forbidden visuals;
- platform aspect ratio;
- text safe areas;
- intended motion style.

Prompt entity:

```json
{
  "visual_prompt_id": "visual_prompt_001",
  "project_id": "project_example",
  "scenario_id": "scenario_001",
  "content_type": "atmospheric_video",
  "prompt_text": "",
  "target_aspect_ratio": "9:16",
  "status": "draft"
}
```

MVP actions:

```text
copy
edit
regenerate
mark_as_used
```

---

## 19. Motion rules

MVP allowed motion:

```text
fade_in
fade_out
crossfade
slow_zoom
slow_pan
gentle_parallax
static
```

Avoid by default:

```text
jerky_typing
fast_flashing
hard_glitch
chaotic_shake
rapid_zoom
strobe
```

Brand Profile может ограничивать motion style.

Template должен управлять motion, а не hardcode внутри renderer.

---

## 20. Text animation rules

Recommended animations:

```text
fade_in
soft_slide_up
soft_reveal
crossfade_text
```

MVP default:

```text
fade_in + fade_out
```

Text animation should:

- be readable;
- not distract from meaning;
- not create accessibility issues;
- respect Brand Profile motion style.

---

## 21. Layout rules

Text placement options:

```text
center
upper_middle
lower_middle
left_aligned_center
bottom_card
```

MVP default:

```text
center or lower_middle
```

Safe zones for 1080x1920 vertical video:

```text
top margin: 160 px
bottom margin: 260 px
left margin: 80 px
right margin: 80 px
```

These may be overridden by Platform Settings or Production Template.

---

## 22. Typography rules

Typography must come from Brand Profile.

Template can define typography slots:

```text
primary_text
secondary_text
cta_text
caption_text
```

Brand Profile provides:

```text
fonts
font_weights
text_color
accent_color
surface_color
```

MVP fallback:

```text
Use default safe font if project font is unavailable.
```

Do not hardcode one brand font globally.

---

## 23. CTA rules

CTA is optional.

CTA should be selected from Project CTA Library.

Atmospheric Video can use CTA as:

```text
last text block
caption CTA
subtle end card
no CTA
```

CTA intensity should depend on:

- funnel stage;
- platform;
- project settings;
- content type;
- campaign.

Recommended by funnel stage:

| Funnel stage | CTA intensity |
|---|---|
| attention | none / soft |
| trust | soft |
| conversion | medium / direct |
| retention | soft / medium |

CTA text must not be hardcoded in the format spec.

---

## 24. Audio rules

Audio is optional in MVP.

Supported audio inputs:

```text
background_music
ambient_sound
voiceover
none
```

MVP baseline:

```text
optional background audio
optional mute
```

Should-have:

```text
audio fade in/out
volume normalization
voiceover support
platform-native music note
```

If user plans to add platform-native music manually, export package can include:

```text
publishing_notes: "Add platform-native audio manually."
```

---

## 25. Output files

For each rendered Atmospheric Video, Production Engine / Export should produce:

```text
video.mp4
caption.txt
metadata.json
cover.txt or cover.png
```

For multi-platform export:

```text
exports/
  {project_slug}/
    {content_id}/
      video.mp4
      caption_tiktok.txt
      caption_instagram.txt
      caption_youtube_shorts.txt
      metadata.json
      cover.txt
```

---

## 26. Metadata

Required metadata:

```json
{
  "content_id": "content_001",
  "project_id": "project_example",
  "content_type": "atmospheric_video",
  "scenario_id": "scenario_001",
  "render_job_id": "render_001",
  "output_type": "vertical_video",
  "platforms": ["instagram", "tiktok"],
  "duration_sec": 15,
  "width": 1080,
  "height": 1920,
  "asset_ids": [],
  "cta_id": "cta_001",
  "status": "needs_review",
  "created_at": ""
}
```

Should-have metadata:

```text
source_type
source_id
funnel_stage
topic_id
hook_id
campaign_id
brand_profile_version
template_id
caption_ids
utm_urls
```

---

## 27. Content Item creation

After render, Production Engine creates a `Content Item`.

Minimum fields:

```text
content_id
project_id
content_type = atmospheric_video
output_type = vertical_video
scenario_id
render_job_id
files
caption
metadata
status
created_at
updated_at
```

Default status after render:

```text
needs_review
```

Rendered content must not automatically become approved.

---

## 28. Caption generation

Atmospheric Video should generate captions for target platforms.

Caption should account for:

- Brand Profile;
- platform rules;
- CTA;
- UTM;
- funnel stage;
- hashtags;
- link policy.

MVP caption outputs:

```text
caption_tiktok.txt
caption_instagram.txt
caption_youtube_shorts.txt
```

Should-have:

```text
caption_pinterest.txt
caption_vk.txt
caption_telegram.txt
```

---

## 29. Platform adaptation

Same video can have different captions and publishing notes per platform.

Examples:

```text
TikTok: short caption, trend/audio note, link-in-profile CTA if needed.
Instagram: short caption, soft CTA, hashtags if project uses them.
YouTube Shorts: short description, optional link.
Pinterest: evergreen title and description.
Telegram: can be paired with longer text post.
```

Rules must come from Project Settings → Platform Settings.

---

## 30. QA checks

### Scenario QA

- project_id exists;
- content_type = atmospheric_video;
- text sequence exists;
- text block length within limits;
- funnel stage valid;
- target platforms valid;
- CTA valid if selected;
- forbidden phrases absent;
- required visual prompt or background asset exists.

### Asset QA

- background asset exists;
- asset belongs to same project;
- file type supported;
- aspect ratio compatible;
- duration compatible if video;
- file exists in storage.

### Pre-render QA

- Brand Profile exists;
- Production Template exists;
- template supports atmospheric_video;
- output spec valid;
- text blocks not empty;
- safe zone settings available.

### Output QA

- video file exists;
- metadata exists;
- resolution correct;
- duration within expected range;
- text overlays present;
- output status set to needs_review.

### Publishing QA

- content item approved;
- export package ready;
- caption exists for selected platform;
- UTM exists if link is used;
- platform selected.

---

## 31. Review rules

Human Review is required before publication.

Reviewer should check:

- text readability;
- visual quality;
- background/text contrast;
- brand consistency;
- CTA appropriateness;
- absence of forbidden claims;
- technical readiness;
- platform suitability.

Actions:

```text
approve
reject
request_changes
edit_text
replace_background
rerender
export
schedule
```

MVP actions:

```text
approve
reject
edit_text
replace_background
rerender
export
```

---

## 32. Repurpose logic

Atmospheric Video can be created from:

```text
Idea → Atmospheric Video
Dialog Miniseries → Atmospheric Video variation
Text Social Post → Video
Analytics Insight → Scale winning phrase
Trend → Hook test video
```

Atmospheric Video can generate:

```text
caption variants
text social posts
pinterest pin
short quote asset
carousel cover idea
```

Source linkage must be preserved.

---

## 33. Batch production

Atmospheric Video is a good candidate for batch production.

Batch examples:

```text
10 ideas → 10 atmospheric videos
1 text post → 3 video variations
1 winning hook → 5 visual variations
1 background asset → 5 text versions
```

MVP batch can be simple:

```text
Select multiple scenarios
→ choose template
→ validate inputs
→ render jobs
→ review queue
```

Batch rendering should not skip QA or human review.

---

## 34. Templates

Production Templates for Atmospheric Video define:

```text
layout
typography slots
text animation
background treatment
logo position
CTA treatment
safe zones
default duration
export rules
```

Templates must not include project-specific hardcode.

Correct:

```text
template_atmospheric_video_soft_v1
+ Brand Profile
+ Project Settings
```

Incorrect:

```text
project_specific_atmospheric_video_renderer
```

---

## 35. MVP scope

MVP includes:

- create scenario for atmospheric video;
- create / edit text blocks;
- generate visual prompt;
- upload background image or video;
- link background asset;
- render vertical video 9:16;
- apply Brand Profile typography/colors/logo;
- basic fade/zoom motion;
- generate caption;
- create export package;
- run QA checks;
- human review;
- schedule/export manually.

MVP does not include:

- built-in image generation API;
- built-in video generation API;
- automatic trend scanning;
- mandatory autoposting;
- advanced AI optimization;
- multi-user approval workflows;
- full SaaS permissions.

---

## 36. Acceptance criteria

Atmospheric Video MVP is ready when:

1. User can create an `atmospheric_video` scenario for a project.
2. Scenario can store ordered text blocks.
3. User can upload or select a background asset.
4. Asset is validated and linked to scenario.
5. Production Engine can render 9:16 mp4.
6. Render uses Brand Profile values instead of hardcoded project values.
7. Output has metadata.json.
8. Content Item is created with status `needs_review`.
9. User can approve or reject the content item.
10. Export package can be created after approval.
11. Caption variant can be generated for at least one target platform.
12. Publication can be created manually or scheduled in Publishing Hub.
13. Metrics can later be attached to the publication.

---

## 37. Open questions

Questions to resolve later:

1. Should Atmospheric Video support voiceover in MVP or only background music?
2. Should text timing be fully automatic or manually editable in first version?
3. Should one video support multiple background scenes, or only one background asset in MVP?
4. Should cover image be generated from video frame or manually defined?
5. Should format support square/feed variants in the first implementation?
6. Should platform-native music notes be part of export package metadata?
7. Should template variants be managed in UI or configuration files first?

---

## 38. Related documents

This document should be used together with:

```text
docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md
docs/02_platform_architecture/DATA_MODEL.md
docs/02_platform_architecture/PIPELINES_SPEC.md
docs/03_modules/SCENARIO_STUDIO_SPEC.md
docs/03_modules/ASSET_LIBRARY_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/03_modules/PUBLISHING_HUB_SPEC.md
docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
```

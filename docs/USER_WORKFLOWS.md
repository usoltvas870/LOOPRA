# User Workflows

## 1. Назначение документа

Этот документ описывает ключевые пользовательские сценарии платформы **Content Plant**.

Он фиксирует:

- как пользователь работает с платформой;
- какие действия входят в MVP;
- какие экраны и модули участвуют в каждом сценарии;
- какие данные создаются на каждом шаге;
- где нужен human review;
- где система должна автоматизировать рутину;
- какие сценарии являются приоритетными для первой версии.

Документ является источником истины для проектирования интерфейса и продуктовой логики.

---

## 2. Главный принцип пользовательских сценариев

Content Plant должен проектироваться не как набор отдельных экранов, а как система рабочих потоков.

Главный принцип:

> Пользователь должен двигаться от идеи к готовому контенту с минимальным количеством ручных переходов между инструментами.

Базовый поток:

```text
Project
→ Brand Profile
→ Idea
→ Scenario
→ Visual Prompts
→ Assets
→ Production
→ Review
→ Export / Schedule
→ Metrics
→ Optimization
```

---

## 3. Главный пользователь MVP

На этапе MVP основной пользователь — владелец внутренних проектов.

Он совмещает роли:

- product owner;
- content strategist;
- editor;
- reviewer;
- asset operator;
- marketer;
- analyst.

Content Plant должен помогать ему не делать всё вручную, а управлять производственным циклом.

---

## 4. Основные модули, участвующие в workflows

В MVP сценариях участвуют следующие модули:

- Projects;
- Project Settings;
- Brand Profile;
- Idea Bank;
- Scenario Studio;
- Asset Library;
- Production;
- Review;
- Export Packages;
- Calendar / Publications;
- Analytics.

Дополнительные модули для следующих итераций:

- Trend Radar;
- Batch Production;
- Weekly Report;
- Optimization Recommendations.

---

## 5. Workflow 1: Создание нового проекта

### 5.1. Цель

Создать новый проект внутри Content Plant, чтобы отделить его бренд, ассеты, сценарии, публикации и аналитику от других проектов.

### 5.2. Участники

- пользователь;
- Projects module;
- Brand Profile module.

### 5.3. Шаги

```text
1. Пользователь открывает Projects.
2. Нажимает Create Project.
3. Вводит название проекта.
4. Вводит slug.
5. Указывает язык.
6. Указывает основной сайт.
7. Выбирает целевые платформы.
8. Создаёт базовый Brand Profile.
9. Сохраняет проект.
10. Проект появляется в Project Switcher.
```

### 5.4. Минимальные поля

```text
project_name
project_slug
description
default_language
primary_url
target_platforms
status
```

### 5.5. Результат

Создан Project:

```text
Project status: active
Brand Profile status: draft или completed
```

### 5.6. MVP notes

В MVP не нужны:

- команды;
- роли;
- приглашения пользователей;
- биллинг;
- внешний onboarding.

---

## 6. Workflow 2: Переключение проекта

### 6.1. Цель

Позволить пользователю работать с разными проектами без смешивания данных.

### 6.2. Шаги

```text
1. Пользователь открывает Project Switcher.
2. Выбирает проект.
3. Система делает проект активным.
4. Все модули показывают данные выбранного проекта.
5. Brand Profile активного проекта применяется к генерации и production.
```

### 6.3. После переключения должны меняться

- идеи;
- сценарии;
- ассеты;
- рендеры;
- публикации;
- аналитика;
- CTA;
- links;
- visual settings.

### 6.4. Важное правило

Нельзя показывать ассеты, сценарии и метрики другого проекта без явного переключения или фильтра.

---

## 7. Workflow 3: Заполнение Brand Profile

### 7.1. Цель

Задать правила бренда, чтобы система могла генерировать контент в стиле проекта.

### 7.2. Шаги

```text
1. Пользователь открывает Project Settings.
2. Переходит в Brand Profile.
3. Заполняет базовую информацию.
4. Описывает аудиторию.
5. Задаёт tone of voice.
6. Указывает цвета.
7. Указывает шрифты.
8. Загружает логотип.
9. Добавляет CTA.
10. Добавляет ссылки.
11. Указывает запреты и ограничения.
12. Сохраняет Brand Profile.
```

### 7.3. Минимальные блоки

- Basics;
- Audience;
- Tone of Voice;
- Visual Identity;
- CTA;
- Links;
- Restrictions;
- Platforms.

### 7.4. Результат

Brand Profile используется в:

- Scenario Studio;
- Visual Prompts;
- Production Engine;
- Publishing Hub;
- QA.

### 7.5. MVP notes

В MVP можно сделать Brand Profile одной страницей, если это ускоряет разработку.

---

## 8. Workflow 4: Создание идеи вручную

### 8.1. Цель

Добавить идею, из которой позже можно создать сценарий, видео, пост или карусель.

### 8.2. Шаги

```text
1. Пользователь выбирает активный проект.
2. Открывает Idea Bank.
3. Нажимает Add Idea.
4. Вводит заголовок.
5. Вводит краткое описание.
6. Выбирает funnel stage.
7. Выбирает предполагаемый формат.
8. Добавляет теги или тему.
9. Сохраняет идею.
```

### 8.3. Минимальные поля

```text
project_id
title
description
topic
funnel_stage
suggested_content_type
status
```

### 8.4. Статусы идеи

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

### 8.5. Результат

Идея появляется в Idea Bank и может быть отправлена в Scenario Studio.

---

## 9. Workflow 5: Создание сценария из идеи

### 9.1. Цель

Преобразовать идею в структурированный сценарий для конкретного формата.

### 9.2. Шаги

```text
1. Пользователь открывает идею.
2. Нажимает Generate Scenario.
3. Выбирает content type.
4. Система загружает Project Profile.
5. Система загружает Brand Profile.
6. Система загружает правила формата.
7. Система генерирует сценарий.
8. Пользователь смотрит черновик.
9. Пользователь утверждает, редактирует или генерирует заново.
```

### 9.3. Входные данные

- project_id;
- idea_id;
- content_type;
- Brand Profile;
- CTA Library;
- format spec;
- funnel stage.

### 9.4. Выходные данные

- scenario;
- scenes;
- dialogue;
- overlay text;
- visual prompts;
- caption draft;
- CTA.

### 9.5. Результат

Создан Scenario со статусом:

```text
draft
```

После утверждения:

```text
approved
```

---

## 10. Workflow 6: Генерация visual prompts

### 10.1. Цель

Создать prompts для генерации изображений или видео во внешних AI-инструментах.

### 10.2. Шаги

```text
1. Пользователь открывает сценарий.
2. Система показывает список сцен.
3. Для каждой сцены система генерирует visual prompt.
4. Пользователь копирует prompt во внешний сервис.
5. Пользователь генерирует изображение или видео.
6. Пользователь возвращается в Content Plant и загружает ассеты.
```

### 10.3. Prompt должен учитывать

- scene description;
- characters;
- mood;
- composition;
- Brand Profile;
- visual restrictions;
- target format;
- platform requirements.

### 10.4. Результат

Сценарий получает prompts, готовые для внешней генерации визуалов.

---

## 11. Workflow 7: Загрузка ассетов

### 11.1. Цель

Загрузить изображения, видео, аудио или логотипы для использования в production.

### 11.2. Шаги

```text
1. Пользователь открывает Asset Library.
2. Нажимает Upload Assets.
3. Выбирает файлы.
4. Указывает тип ассета.
5. Добавляет теги.
6. При необходимости связывает ассет со сценой.
7. Система сохраняет ассеты в папке проекта.
```

### 11.3. Типы ассетов

```text
image
video
audio
logo
background
character
template_asset
```

### 11.4. Требования

Каждый ассет должен иметь:

```text
asset_id
project_id
type
file_path
status
created_at
```

### 11.5. Результат

Ассеты доступны только внутри активного проекта.

---

## 12. Workflow 8: Привязка ассетов к сценам

### 12.1. Цель

Связать загруженные изображения или видео с конкретными сценами сценария.

### 12.2. Шаги

```text
1. Пользователь открывает сценарий.
2. Переходит в Scene Assets.
3. Для каждой сцены выбирает подходящий ассет.
4. Система проверяет project_id.
5. Система проверяет формат файла.
6. Пользователь сохраняет mapping.
```

### 12.3. Правило безопасности

Ассет можно привязать к сцене только если:

```text
asset.project_id == scenario.project_id
```

### 12.4. Результат

Сценарий получает статус:

```text
ready_to_render
```

если все обязательные сцены имеют ассеты.

---

## 13. Workflow 9: Рендер Dialog Miniseries

### 13.1. Цель

Собрать готовое вертикальное видео из сценария, ассетов, текстовых оверлеев и Brand Profile.

### 13.2. Шаги

```text
1. Пользователь открывает сценарий.
2. Проверяет, что все сцены имеют ассеты.
3. Нажимает Render.
4. Система создаёт Render Job.
5. Production Engine загружает Brand Profile.
6. Production Engine применяет template.
7. Production Engine собирает видео.
8. Система сохраняет output.
9. Статус меняется на needs_review.
```

### 13.3. Входные данные

- scenario_id;
- project_id;
- template_id;
- Brand Profile;
- scene assets;
- CTA;
- optional audio.

### 13.4. Выходные данные

```text
video.mp4
metadata.json
caption draft
```

### 13.5. Результат

Создан готовый render preview.

---

## 14. Workflow 10: Review готового контента

### 14.1. Цель

Проверить готовый материал перед экспортом или публикацией.

### 14.2. Шаги

```text
1. Пользователь открывает Review.
2. Видит список материалов со статусом needs_review.
3. Открывает материал.
4. Смотрит preview.
5. Проверяет текст, визуал, CTA.
6. Выбирает approve или reject.
7. При reject добавляет комментарий.
```

### 14.3. Возможные действия

- approve;
- reject;
- edit text;
- replace asset;
- regenerate caption;
- rerender.

### 14.4. Статусы

```text
needs_review
approved
rejected
```

### 14.5. Результат

После approve материал готов к export package.

---

## 15. Workflow 11: Создание export package

### 15.1. Цель

Подготовить файлы для ручной или полуавтоматической публикации.

### 15.2. Шаги

```text
1. Пользователь утверждает материал.
2. Система создаёт export package.
3. Система сохраняет видео/слайды/посты.
4. Система создаёт caption.txt.
5. Система создаёт metadata.json.
6. Пользователь скачивает или открывает пакет.
```

### 15.3. Пример для видео

```text
content_item/
  video.mp4
  caption.txt
  metadata.json
  cover.txt
```

### 15.4. Пример для текстового bundle

```text
text_social_post_bundle/
  telegram.txt
  threads.txt
  vk.txt
  metadata.json
```

### 15.5. Результат

Материал готов к публикации.

---

## 16. Workflow 12: Генерация текстовых постов из сценария

### 16.1. Цель

Превратить сценарий или идею в посты для Telegram, Threads и VK.

### 16.2. Шаги

```text
1. Пользователь открывает сценарий или идею.
2. Нажимает Generate Text Posts.
3. Выбирает платформы.
4. Система загружает Brand Profile.
5. Система генерирует посты.
6. Пользователь просматривает тексты.
7. Утверждает, редактирует или регенерирует.
8. Система создаёт .txt файлы и metadata.
```

### 16.3. Выходные данные

```text
telegram.txt
threads.txt
vk.txt
caption.txt
metadata.json
```

### 16.4. Результат

Текстовый bundle готов к публикации.

---

## 17. Workflow 13: Планирование публикации

### 17.1. Цель

Добавить готовый материал в календарь публикаций.

### 17.2. Шаги

```text
1. Пользователь открывает approved content item.
2. Нажимает Schedule.
3. Выбирает платформу.
4. Выбирает дату и время.
5. При необходимости выбирает caption version.
6. Сохраняет публикацию.
```

### 17.3. Минимальные поля публикации

```text
publication_id
project_id
content_id
platform
scheduled_at
status
caption
export_package_path
```

### 17.4. Статусы

```text
draft
scheduled
published
failed
cancelled
```

### 17.5. MVP notes

На MVP календарь может быть простым списком публикаций.

Автопостинг не обязателен.

---

## 18. Workflow 14: Ручная публикация через export package

### 18.1. Цель

Позволить пользователю публиковать вручную там, где API недоступен или нежелателен.

### 18.2. Шаги

```text
1. Пользователь открывает publication.
2. Скачивает или открывает export package.
3. Загружает видео/карусель в социальную сеть.
4. Копирует caption.
5. Публикует вручную.
6. Возвращается в Content Plant.
7. Отмечает publication as published.
8. Добавляет ссылку на опубликованный материал.
```

### 18.3. Результат

Публикация получает статус:

```text
published
```

---

## 19. Workflow 15: Ввод метрик вручную

### 19.1. Цель

Связать опубликованный контент с результатами.

### 19.2. Шаги

```text
1. Пользователь открывает публикацию.
2. Нажимает Add Metrics.
3. Вводит просмотры.
4. Вводит лайки, комментарии, сохранения, репосты.
5. Вводит клики, регистрации, покупки, revenue, если доступны.
6. Сохраняет snapshot.
```

### 19.3. Минимальные метрики

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

### 19.4. Результат

Создан MetricSnapshot.

---

## 20. Workflow 16: Импорт метрик из CSV

### 20.1. Цель

Позволить быстрее загрузить результаты по публикациям.

### 20.2. Шаги

```text
1. Пользователь открывает Analytics.
2. Нажимает Import CSV.
3. Загружает файл.
4. Система сопоставляет поля.
5. Пользователь подтверждает импорт.
6. Система создаёт MetricSnapshots.
```

### 20.3. MVP notes

CSV import является should-have.  
Ручной ввод является must-have.

---

## 21. Workflow 17: Просмотр аналитики проекта

### 21.1. Цель

Понять, какие форматы, темы и платформы работают.

### 21.2. Шаги

```text
1. Пользователь открывает Analytics.
2. Выбирает проект.
3. Выбирает период.
4. Смотрит показатели по форматам.
5. Смотрит показатели по платформам.
6. Смотрит лучшие публикации.
7. Смотрит слабые публикации.
```

### 21.3. Базовые срезы

- by content_type;
- by platform;
- by topic;
- by funnel_stage;
- by CTA;
- by date.

### 21.4. Результат

Пользователь понимает:

- что повторять;
- что останавливать;
- что изменить;
- какие темы развивать.

---

## 22. Workflow 18: Repurpose одного сценария

### 22.1. Цель

Превратить один сценарий в несколько единиц контента.

### 22.2. Пример

Источник:

```text
Scenario: "Я устала быть сильной"
```

Выход:

```text
dialog_miniseries video
telegram post
threads post
vk post
dialog carousel
pinterest pin
```

### 22.3. MVP version

В MVP достаточно:

```text
dialog_miniseries video
telegram post
threads post
vk post
caption
```

### 22.4. Результат

Одна идея становится контентным пакетом.

---

## 23. Workflow 19: Создание контента из тренда

### 23.1. Цель

Преобразовать внешний тренд в идею и сценарий для выбранного проекта.

### 23.2. Шаги

```text
1. Пользователь открывает Trend Radar.
2. Добавляет ссылку или CSV.
3. Система анализирует тренд.
4. Система выделяет hook, structure, emotion.
5. Пользователь выбирает проект.
6. Система предлагает адаптацию.
7. Пользователь сохраняет адаптацию как Idea.
8. Idea отправляется в Scenario Studio.
```

### 23.3. MVP notes

Trend Radar не является обязательным для первого production slice.  
Но workflow должен быть предусмотрен.

---

## 24. Workflow 20: Повтор успешного формата

### 24.1. Цель

Использовать аналитику для создания новых материалов на основе успешных тем и форматов.

### 24.2. Шаги

```text
1. Пользователь открывает Analytics.
2. Видит успешную публикацию.
3. Нажимает Create Variation.
4. Система создаёт новую идею или сценарий.
5. Пользователь утверждает.
6. Контент идёт в production.
```

### 24.3. MVP notes

На MVP можно сделать это вручную через duplicate idea/scenario.

В будущем система может предлагать:

- scale;
- create variation;
- turn into carousel;
- turn into thread;
- repeat topic.

---

## 25. Dashboard workflow

Dashboard должен показывать, где сейчас находится контентный поток.

Блоки MVP:

```text
Active project
Ideas waiting for scenario
Scenarios waiting for assets
Content waiting for review
Approved content
Scheduled publications
Recent metrics
```

Dashboard должен быть рабочей панелью, а не декоративной витриной.

---

## 26. Приоритетные workflows MVP

### Must-have

1. Создать проект.
2. Заполнить Brand Profile.
3. Создать идею.
4. Создать сценарий из идеи.
5. Получить visual prompts.
6. Загрузить ассеты.
7. Привязать ассеты к сценам.
8. Собрать Dialog Miniseries.
9. Провести review.
10. Создать export package.
11. Сгенерировать text social posts.
12. Внести базовые метрики вручную.

### Should-have

1. Запланировать публикацию.
2. Импортировать метрики из CSV.
3. Создать карусель из сценария.
4. Создать атмосферное видео.
5. Сделать basic analytics dashboard.

### Could-have

1. Trend Radar manual import.
2. Batch rendering.
3. Telegram/VK autopost.
4. Weekly recommendations.
5. Create variation from analytics.

---

## 27. Что не входит в workflows MVP

Не входят:

- публичная регистрация;
- тарифы;
- биллинг;
- команды;
- роли;
- сложная система прав;
- marketplace шаблонов;
- полноценный Canva-like editor;
- полный TikTok/Instagram autoposting;
- автоматическая генерация изображений через API;
- сложный AI optimization engine.

---

## 28. Human-in-the-loop points

Человек должен оставаться в контуре на следующих шагах:

- утверждение Brand Profile;
- выбор или утверждение идеи;
- review сценария;
- генерация ассетов во внешних инструментах;
- загрузка ассетов;
- review готового контента;
- публикация в платформах с ограниченным API;
- интерпретация аналитики.

В будущем часть этих шагов можно автоматизировать.

---

## 29. Основные статусы

### 29.1. Idea statuses

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

### 29.2. Scenario statuses

```text
draft
approved
needs_assets
ready_to_render
in_production
rendered
archived
```

### 29.3. Content statuses

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

### 29.4. Publication statuses

```text
draft
scheduled
published
failed
cancelled
```

---

## 30. Критерии готовности workflow MVP

Workflow MVP считается готовым, если пользователь может пройти путь:

```text
Create Project
→ Fill Brand Profile
→ Create Idea
→ Generate Scenario
→ Generate Prompts
→ Upload Assets
→ Render Video
→ Review
→ Export
→ Create Text Posts
→ Add Metrics
```

без ручного создания структуры файлов и без смешивания данных разных проектов.

---

## 31. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant  
Первый прикладной проект: NURA

---

## 32. Следующие документы

После этого документа необходимо создать:

1. `docs/07_projects/nura/PROJECT_PROFILE.md`
2. `docs/05_product_design/WEB_UI_SPEC.md`
3. `docs/05_product_design/DASHBOARD_SPEC.md`
4. `docs/03_modules/SCENARIO_STUDIO_SPEC.md`

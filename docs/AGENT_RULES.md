# Agent Rules

## 1. Назначение документа

Этот документ описывает правила работы агентов и разработчиков над проектом **Content Plant**.

Он нужен, чтобы:

- агенты работали по общей документации;
- изменения не ломали архитектуру;
- проект не зашивался под один бренд;
- документация обновлялась вместе с кодом;
- каждый результат был проверяемым;
- после каждой задачи оставался понятный отчёт;
- разработка шла по заранее согласованному плану, а не вслепую.

Документ является обязательным для чтения перед любой задачей по Content Plant.

---

## 2. Главный принцип работы

Главный принцип:

> Сначала понять документацию и границы задачи, потом менять код или документы.

Агент не должен начинать реализацию, если:

- задача противоречит существующей документации;
- задача требует изменения архитектуры, но архитектурный документ не обновлён;
- задача расширяет MVP без явного решения;
- задача зашивает платформу под NURA;
- задача смешивает платформенный и проектный уровни.

---

## 3. Обязательные документы перед началом любой задачи

Перед любой задачей агент обязан прочитать:

1. `docs/00_index.md`
2. `docs/01_platform/PLATFORM_OVERVIEW.md`
3. `docs/01_platform/MVP_SCOPE.md`
4. `docs/06_agents/AGENT_RULES.md`

После этого агент должен прочитать документы, относящиеся к конкретной задаче.

---

## 4. Документы по типам задач

### 4.1. Если задача про стратегию платформы

Прочитать:

- `docs/01_platform/PLATFORM_OVERVIEW.md`
- `docs/01_platform/PRODUCT_STRATEGY.md`
- `docs/01_platform/MVP_SCOPE.md`

---

### 4.2. Если задача про мультипроектность

Прочитать:

- `docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md`
- `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`
- `docs/01_platform/MVP_SCOPE.md`

---

### 4.3. Если задача про бренд или настройки проекта

Прочитать:

- `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`
- `docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md`
- `docs/07_projects/{project_slug}/PROJECT_PROFILE.md`
- `docs/07_projects/{project_slug}/VISUAL_GUIDELINES.md`
- `docs/07_projects/{project_slug}/TONE_OF_VOICE.md`
- `projects/{project_id}/project.yaml`, если задача затрагивает machine-readable project config

Если проектных документов ещё нет, агент должен указать это в отчёте.

---

### 4.4. Если задача про контентные форматы

Прочитать:

- `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
- соответствующий `docs/04_content_formats/FORMAT_*.md`
- `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`
- проектный `CONTENT_STRATEGY.md`, если задача относится к конкретному проекту.

---

### 4.5. Если задача про интерфейс

Прочитать:

- `docs/05_product_design/USER_WORKFLOWS.md`
- `docs/05_product_design/WEB_UI_SPEC.md`
- `docs/05_product_design/PROJECT_SETTINGS_SPEC.md`
- документы конкретного модуля.

---

### 4.6. Если задача про архитектуру или модель данных

Прочитать:

- `docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/02_platform_architecture/DATA_MODEL.md`
- `docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md`
- `docs/02_platform_architecture/PIPELINES_SPEC.md`

Если эти документы ещё не созданы, агент должен работать только в рамках существующих документов и явно отметить пробел.

---

### 4.7. Если задача про Trend Radar

Прочитать:

- `docs/03_modules/TREND_RADAR_SPEC.md`
- `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
- `docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md`

---

### 4.8. Если задача про Scenario Studio

Прочитать:

- `docs/03_modules/SCENARIO_STUDIO_SPEC.md`
- `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`
- `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
- проектный `PROMPT_LIBRARY.md`, если есть.

---

### 4.9. Если задача про Production Engine

Прочитать:

- `docs/03_modules/PRODUCTION_ENGINE_SPEC.md`
- `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
- соответствующий `FORMAT_*.md`
- `docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md`

---

### 4.10. Если задача про аналитику

Прочитать:

- `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`
- `docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md`
- `docs/02_platform_architecture/DATA_MODEL.md`

---

## 5. Запрет на хардкод NURA в платформе

NURA является первым проектом внутри Content Plant, но не является ядром платформы.

Агенту запрещено:

- называть универсальные функции `nura_*`, если функция должна работать для разных проектов;
- зашивать цвета NURA в production templates;
- зашивать CTA NURA в универсальные шаблоны;
- использовать персонажа NURA как обязательный элемент платформы;
- хранить все ассеты в общей папке без project separation;
- смешивать аналитику NURA с другими проектами;
- создавать модель данных, где NURA является особым случаем.

Правильный подход:

```text
Project → Brand Profile → Format → Production Template
```

Неправильный подход:

```text
NURA-specific script → hardcoded render → NURA-only output
```

---

## 6. Правило платформенного и проектного уровней

Все решения должны быть разделены на два уровня.

### 6.1. Platform-level

Платформенный уровень включает:

- универсальные форматы;
- production engine;
- scenario studio;
- trend radar;
- publishing hub;
- analytics engine;
- QA;
- workspace/project model;
- brand system.

### 6.2. Project-level

Проектный уровень включает:

- Brand Profile;
- Visual Guidelines;
- Tone of Voice;
- CTA Library;
- Prompt Library;
- Project Profile;
- Content Strategy;
- `projects/{project_id}/project.yaml`;
- ассеты;
- публикации;
- метрики.

Если агент не уверен, куда относится решение, он должен выбрать более универсальный вариант или запросить уточнение.

---

## 7. Правило MVP

Агент обязан соблюдать `MVP_SCOPE.md`.

Для первого implementation loop safest MVP format = `text_social_post`.

Video formats, включая `dialog_miniseries`, должны подключаться после стабилизации core loop:

```text
Project
→ Brand Profile
→ Idea
→ Scenario / Draft
→ QA
→ Review
→ Export Package
→ Manual Publication
→ Metric Snapshot
→ Insight
→ New Idea
```

`Export Package` belongs to `Publishing Hub`.

`Production Engine` owns only:

- `RenderJob`;
- `OutputFile`;
- `ContentItem`;
- technical QA result;
- render output metadata.

В MVP нельзя добавлять без отдельного решения:

- публичную регистрацию;
- биллинг;
- тарифы;
- команды;
- роли доступа;
- marketplace;
- публичный SaaS onboarding;
- сложную систему прав;
- сложный AI optimizer;
- обязательный автопостинг во все соцсети;
- генерацию изображений и видео через API.

Если агент считает, что функция нужна, он должен:

1. объяснить, зачем она нужна;
2. указать, почему она важна именно для MVP;
3. предложить обновление `MVP_SCOPE.md`;
4. не реализовывать её без подтверждения.

---

## 8. Правило documentation-first

Крупные изменения сначала описываются в документации.

Документацию нужно обновить до или вместе с изменением кода, если задача:

- добавляет новый модуль;
- меняет модель данных;
- меняет project model;
- меняет Brand Profile;
- добавляет новый формат контента;
- меняет production pipeline;
- добавляет интеграцию;
- меняет правила публикации;
- меняет аналитику;
- меняет QA-правила.

Агент не должен добавлять новый формат только в коде без соответствующего `FORMAT_*.md`.

---

## 9. Правило статусов и жизненного цикла

Агент должен использовать существующие статусы, если они уже описаны в документации.

Примеры статусов идей:

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

Примеры статусов production:

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
failed
```

Если нужен новый статус, агент должен:

1. объяснить необходимость;
2. проверить, нет ли существующего статуса;
3. обновить соответствующий документ;
4. только потом использовать статус в коде.

---

## 10. Правило данных

Все сущности, относящиеся к проекту, должны иметь `project_id`.

Это обязательно для:

- ideas;
- scenarios;
- scenes;
- assets;
- render jobs;
- content items;
- publications;
- metrics;
- CTA;
- platform accounts;
- prompt templates project-level.

Для SaaS-готовности желательно предусматривать `workspace_id`, даже если в MVP используется один workspace.

---

## 11. Правило файлов и ассетов

Агент должен хранить проектные файлы отдельно по проектам.

Правильно:

```text
storage/projects/nura/assets/
storage/projects/nura/renders/
storage/projects/nura/exports/

storage/projects/astra/assets/
storage/projects/astra/renders/
storage/projects/astra/exports/
```

Неправильно:

```text
assets/
renders/
exports/
```

если внутри нет project separation.

---

## 12. Правило naming

### 12.1. Папки

- lowercase;
- snake_case;
- без пробелов.

Примеры:

```text
01_platform/
02_platform_architecture/
07_projects/
```

### 12.2. Markdown-документы

- UPPER_SNAKE_CASE;
- расширение `.md`.

Примеры:

```text
MVP_SCOPE.md
BRAND_SYSTEM_SPEC.md
WORKSPACE_AND_PROJECT_MODEL.md
```

### 12.3. Project slug

- lowercase;
- латиница;
- стабильный;
- без пробелов.

Примеры:

```text
nura
astra
client_brand
```

### 12.4. Content type ids

- lowercase;
- snake_case.

Примеры:

```text
dialog_miniseries
atmospheric_video
dialog_carousel
text_social_post
pinterest_pin
```

---

## 13. Правило отчёта после задачи

После выполнения задачи агент обязан дать отчёт.

Минимальный формат отчёта:

```text
Готово.

Что сделано:
- ...

Изменённые файлы:
- path/to/file
- path/to/file

Документация:
- какие документы были прочитаны
- какие документы были обновлены
- если не обновлялись, почему

Проверка:
- какие проверки выполнены
- результат

Ограничения / замечания:
- ...

Следующие шаги:
- ...
```

Если задача не выполнена полностью, агент должен честно указать:

- что сделано;
- что не сделано;
- почему;
- что нужно для завершения.

---

## 14. Правило CHANGELOG

После значимого изменения агент должен обновить `CHANGELOG.md`.

Запись должна включать:

```text
## YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Docs
- ...

### Notes
- ...
```

Если `CHANGELOG.md` ещё не существует, агент должен создать его при первом значимом изменении.

---

## 15. Правило проверки перед изменением кода

Перед изменением кода агент должен выполнить короткий pre-check:

1. Какая задача?
2. Какой документ её регулирует?
3. Это platform-level или project-level изменение?
4. Входит ли это в MVP?
5. Нужна ли правка документации?
6. Какие файлы будут затронуты?
7. Какие риски?

Если задача явно противоречит документации, агент не должен молча реализовывать её.  
Он должен указать конфликт и предложить решение.

---

## 16. Правило минимальных изменений

Агент должен вносить минимально достаточные изменения.

Запрещено:

- переписывать большие части проекта без необходимости;
- менять архитектуру ради одной задачи;
- добавлять зависимости без причины;
- удалять существующую функциональность без указания;
- менять формат данных без миграции или объяснения;
- ломать существующие workflows.

Если нужна большая переработка, агент должен сначала предложить план.

---

## 17. Правило совместимости

Новые изменения должны быть совместимы с:

- мультипроектностью;
- Brand Profile;
- MVP boundaries;
- существующей документацией;
- текущими production flows;
- будущей возможностью SaaS.

Если изменение временно нарушает совместимость, это должно быть явно указано в отчёте.

---

## 18. Правило интеграций

Агент не должен строить MVP вокруг нестабильной или недоступной интеграции.

Для соцсетей приоритет такой:

1. export package;
2. manual/semi-auto publishing;
3. stable API integration;
4. advanced automation.

Если API ограничен, нужно сделать graceful fallback.

Пример:

```text
TikTok autopost unavailable → create export package for manual upload.
```

---

## 19. Правило LLM prompts

Если агент добавляет или меняет промт:

- промт должен быть сохранён в документации или prompt library;
- должно быть понятно, для какого проекта и формата он используется;
- нельзя смешивать project-specific prompt с universal prompt;
- prompts должны учитывать Brand Profile.

Типы промтов:

- universal format prompt;
- project-specific prompt;
- trend analysis prompt;
- visual prompt builder;
- CTA prompt;
- analytics summary prompt.

---

## 20. Правило QA

Перед завершением задачи агент должен проверить:

- не нарушена ли мультипроектность;
- нет ли хардкода NURA;
- не добавлены ли SaaS-функции в MVP;
- обновлена ли документация, если нужно;
- корректно ли работают статусы;
- есть ли project_id у проектных сущностей;
- не смешиваются ли ассеты разных проектов;
- не сломан ли существующий flow.

Для задач по контенту дополнительно проверить:

- соответствие Brand Profile;
- читаемость текста;
- корректность CTA;
- отсутствие запрещённых обещаний;
- корректность export package.

---

## 21. Правило обработки ошибок

Если агент сталкивается с ошибкой, он должен:

1. описать ошибку;
2. указать файл или модуль;
3. объяснить вероятную причину;
4. предложить исправление;
5. не скрывать неудачные проверки.

В отчёте не допускается писать “всё готово”, если часть задачи не выполнена.

---

## 22. Правило временных решений

Если агент использует временное решение, он должен явно пометить его.

Формат:

```text
TEMP:
Reason:
Remove when:
Related doc:
```

Временные решения не должны становиться скрытым техническим долгом.

---

## 23. Правило новых зависимостей

Перед добавлением новой зависимости агент должен объяснить:

- зачем она нужна;
- какие альтернативы рассмотрены;
- как она влияет на проект;
- нужна ли она для MVP;
- есть ли риски.

Запрещено добавлять тяжёлые библиотеки ради маленькой функции без обоснования.

---

## 24. Правило безопасности и секретов

Агент не должен:

- коммитить API keys;
- хранить токены в документации;
- писать реальные секреты в код;
- включать приватные данные в export examples;
- смешивать пользовательские данные с тестовыми.

Секреты должны храниться через environment variables или безопасный storage.

---

## 25. Правило тестовых данных

Тестовые данные должны быть явно помечены как demo/test.

Пример:

```text
project_demo
asset_test_001
scenario_demo_001
```

Для NURA можно использовать демо-сценарии, но нельзя считать их реальными production-данными без статуса.

---

## 26. Правило разработки документации

Документы должны быть:

- структурированными;
- читаемыми;
- без лишнего маркетингового шума;
- пригодными для агента;
- пригодными для разработки;
- в Markdown;
- с понятными заголовками;
- с примерами, где это полезно.

Если документ устарел, агент должен предложить его обновление.

---

## 27. Правило конфликтов между документами

Если два документа противоречат друг другу, приоритет такой:

### 27.1. Для платформы

1. `PLATFORM_OVERVIEW.md`
2. `PRODUCT_STRATEGY.md`
3. `MVP_SCOPE.md`
4. `WORKSPACE_AND_PROJECT_MODEL.md`
5. `SYSTEM_ARCHITECTURE.md`
6. `DATA_MODEL.md`

### 27.2. Для бренда

1. `BRAND_SYSTEM_SPEC.md`
2. `PROJECT_PROFILE.md`
3. `VISUAL_GUIDELINES.md`
4. `TONE_OF_VOICE.md`
5. `CTA_LIBRARY.md`

### 27.3. Для форматов

1. `CONTENT_FORMATS_OVERVIEW.md`
2. соответствующий `FORMAT_*.md`
3. проектный `CONTENT_STRATEGY.md`
4. проектный `PROMPT_LIBRARY.md`

При обнаружении конфликта агент должен указать его в отчёте.

---

## 28. Что агент может делать самостоятельно

Агент может самостоятельно:

- создавать недостающие папки документации согласно `00_index.md`;
- исправлять явные опечатки;
- добавлять документацию, если она соответствует уже утверждённой структуре;
- добавлять project_id в проектные сущности;
- улучшать отчётность;
- создавать export package, если это описано в MVP;
- добавлять простые QA-проверки;
- улучшать структуру файлов без изменения архитектуры.

---

## 29. Что требует отдельного согласования

Требует согласования:

- изменение MVP scope;
- добавление SaaS-функций;
- изменение модели Workspace/Project;
- изменение Brand Profile schema;
- новый content format;
- новая внешняя интеграция;
- добавление биллинга;
- добавление ролей и пользователей;
- изменение production engine;
- удаление существующего функционала;
- изменение проектного позиционирования NURA или другого бренда.

---

## 30. Definition of Done

Задача считается выполненной, если:

- результат соответствует задаче;
- не нарушены документы;
- код или документ обновлён в нужном месте;
- проектная и платформенная логика не смешаны;
- нет хардкода NURA в платформенном слое;
- соблюдён MVP scope;
- обновлён changelog при значимом изменении;
- агент дал отчёт;
- указаны проверки;
- указаны ограничения, если они есть.

---

## 31. Минимальный агентский preflight template

Перед работой агент должен мысленно или явно пройти такой чеклист:

```text
Task:
Related docs:
Platform-level or project-level:
MVP scope impact:
Needs docs update:
Expected files:
Risks:
```

---

## 32. Минимальный отчётный template

После работы агент должен использовать такой формат:

```text
Готово.

Задача:
- ...

Что сделано:
- ...

Изменённые файлы:
- ...

Документация:
- Прочитано:
  - ...
- Обновлено:
  - ...

Проверки:
- ...

Ограничения:
- ...

Следующие шаги:
- ...
```

---

## 33. Статус документа

Статус: Draft  
Версия: 0.1  
Дата создания: 2026-07-04  
Проект: Content Plant  
Первый прикладной проект: NURA

---

## 34. Следующие документы

После этого документа необходимо создать:

1. `docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md`
2. `docs/04_content_formats/FORMAT_DIALOG_MINISERIES.md`
3. `docs/05_product_design/USER_WORKFLOWS.md`
4. `docs/07_projects/nura/PROJECT_PROFILE.md`

# Task Prompt Templates

> **Legacy / future-scope note**
>
> This document is not the current foundation MVP source of truth.
> It may describe future modules, historical plans, or expanded-scope ideas.
> Current foundation MVP source of truth: `STATE.md`, `AGENTS.md`, `docs/00_index.md`, `docs/MVP_SCOPE.md`, `docs/DATA_MODEL.md`, `docs/PIPELINES_SPEC.md`.
> Do not treat API/UI/render/video/autoposting/external analytics/Trend Radar/automatic insight-to-idea loops as current scope unless a future Architecture Gate explicitly reactivates them.

## 1. Назначение документа

Этот документ содержит шаблоны задач для агентов и разработчиков, работающих над платформой **Content Plant**.

Он нужен, чтобы:

- формулировать задачи единообразно;
- не терять контекст платформы;
- не смешивать platform-level и project-level изменения;
- не расширять MVP без решения;
- требовать чтения правильных документов перед работой;
- получать проверяемые результаты;
- фиксировать отчёт после каждой задачи.

Документ является операционным приложением к `AGENT_RULES.md`.

---

## 2. Главный принцип

Каждая задача для агента должна отвечать на 7 вопросов:

```text
1. Что нужно сделать?
2. Это platform-level или project-level?
3. Какие документы регулируют задачу?
4. Входит ли это в MVP?
5. Какие файлы можно менять?
6. Какие проверки выполнить?
7. Какой отчёт вернуть?
```

Если этих ответов нет, агент может начать импровизировать.  
Импровизация в архитектуре — это маленький гремлин с отвёрткой.

---

## 3. Универсальный шаблон задачи

```text
Ты работаешь в проекте Content Plant.

Context:
Content Plant — самостоятельная мультипроектная платформа для системного производства, публикации и анализа контента.
Платформа не должна быть привязана к конкретному бренду.
Project-specific правила должны жить в docs/07_projects/{project_slug}/.

Task:
[Опиши задачу одним абзацем.]

Scope:
- Уровень задачи: [platform-level / project-level / mixed]
- MVP: [входит / не входит / спорно]
- Не делать: [ограничения]

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/06_agents/AGENT_RULES.md
4. [документы по задаче]

Allowed files:
- [список файлов или папок]

Do:
1. [шаг 1]
2. [шаг 2]
3. [шаг 3]

Do not:
- Не добавлять project-specific hardcode.
- Не менять архитектуру без обновления документации.
- Не добавлять SaaS-функции в MVP.
- Не создавать новые документы, если задача просит только правку существующих.
- Не удалять существующую логику без объяснения.

Checks:
- Проверить отсутствие project-specific hardcode.
- Проверить соответствие MVP_SCOPE.md.
- Проверить согласованность с DATA_MODEL.md и PIPELINES_SPEC.md, если они затронуты.
- Выполнить доступные технические проверки, если меняется код.

Report:
Верни отчёт:
- что сделано;
- какие файлы изменены;
- какие документы прочитаны;
- какие проверки выполнены;
- что осталось спорным;
- следующие шаги.
```

---

## 4. Шаблон: документационный cleanup

Использовать, когда нужно вычистить платформенный документ от проектных деталей.

```text
Ты работаешь в проекте Content Plant.

Задача:
Выполни cleanup платформенного документа [path/to/document.md].

Главное правило:
Content Plant — самостоятельная мультипроектная платформа.
Платформенные документы не должны содержать данные конкретного проекта: цены, URL, project_id, brand_id, персонажей, готовые CTA, product-specific claims, тексты конкретного бренда.

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
4. docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
5. docs/06_agents/AGENT_RULES.md

Do:
1. Прочитай документ полностью.
2. Найди project-specific элементы.
3. Замени их на нейтральные examples.
4. Сохрани платформенный смысл.
5. Не переписывай документ с нуля.
6. Не меняй структуру без необходимости.

Neutral examples:
- project_example
- brand_example
- Example Brand
- Demo Project
- Client Brand
- https://example.com
- storage/projects/{project_slug}/

Do not:
- Не добавлять новые проектные детали.
- Не создавать project docs в этом шаге.
- Не менять соседние документы без необходимости.

Checks:
- Проверить документ на project-specific markers.
- Проверить, что terms остались согласованы: Project, Workspace, Brand Profile, Idea, Scenario, Asset, Production, Review, Publication, Metrics.
- Проверить, что MVP-логика не изменилась.

Report:
- какие элементы удалены;
- какие примеры заменены;
- какие файлы изменены;
- осталось ли что-то спорное.
```

---

## 5. Шаблон: создание нового платформенного документа

```text
Ты работаешь в проекте Content Plant.

Задача:
Создай новый платформенный документ:
[path/to/document.md]

Документ должен быть platform-level и не привязан к конкретному бренду.

Read first:
1. docs/00_index.md
2. docs/01_platform/PLATFORM_OVERVIEW.md
3. docs/01_platform/MVP_SCOPE.md
4. docs/06_agents/AGENT_RULES.md
5. [документы, связанные с темой]

Документ должен:
- описывать назначение;
- фиксировать роль в системе;
- описывать связи с другими модулями;
- определять MVP scope;
- определять что не входит в MVP;
- использовать нейтральные examples;
- использовать согласованные термины;
- не содержать project-specific hardcode.

Структура:
1. Назначение документа
2. Главная роль
3. Основной принцип
4. Место в системе
5. Основные сущности
6. Основные workflow
7. MVP scope
8. Not in MVP
9. Acceptance criteria
10. Open questions

Do not:
- Не использовать конкретный бренд как норму.
- Не добавлять SaaS-функции в MVP.
- Не менять существующие документы без отдельной задачи.
- Не создавать код.

Checks:
- Проверить отсутствие project-specific данных.
- Проверить согласованность с MVP_SCOPE.md.
- Проверить, что все project-level сущности имеют project_id.
- Проверить, что документ не дублирует уже существующий источник истины.

Report:
- какой документ создан;
- какие документы прочитаны;
- какие ключевые решения зафиксированы;
- какие вопросы остались открытыми.
```

---

## 6. Шаблон: обновление существующей спецификации

```text
Ты работаешь в проекте Content Plant.

Задача:
Обнови существующую спецификацию:
[path/to/document.md]

Причина обновления:
[коротко описать причину]

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/06_agents/AGENT_RULES.md
4. [source of truth documents]

Do:
1. Прочитай документ полностью.
2. Найди места, которые нужно обновить.
3. Внеси минимальные изменения.
4. Сохрани стиль и структуру документа.
5. Если изменение влияет на model / pipeline / architecture, укажи это в отчёте.
6. Не расширяй scope сверх задачи.

Do not:
- Не переписывать документ целиком без необходимости.
- Не менять unrelated sections.
- Не добавлять новые сущности без проверки DATA_MODEL.md.
- Не добавлять новые статусы без проверки PIPELINES_SPEC.md.
- Не добавлять project-specific hardcode.

Checks:
- Проверить consistency с source of truth.
- Проверить термины.
- Проверить MVP boundaries.
- Проверить отсутствие противоречий.

Report:
- что изменено;
- почему;
- какие файлы изменены;
- какие проверки выполнены;
- какие документы могут потребовать follow-up.
```

---

## 7. Шаблон: аудит документации

```text
Ты работаешь в проекте Content Plant.

Задача:
Проведи аудит документации по списку:
[список документов]

Проверь:
1. Нет ли project-specific привязки в platform-level документах.
2. Нет ли противоречий между документами.
3. Нет ли сильных дублей.
4. Не нарушена ли MVP-логика.
5. Согласованы ли термины.
6. Нет ли missing source of truth.
7. Какие документы нужно добавить или обновить.

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/06_agents/AGENT_RULES.md

Report format:
# Content Plant Documentation Audit

## 1. Executive Summary
## 2. Project Neutrality Check
## 3. Terminology Check
## 4. MVP Logic Check
## 5. Duplicate Check
## 6. Missing Elements
## 7. Recommendations
## 8. Recommended Next Documents

Do not:
- Не исправлять файлы.
- Не создавать новые документы.
- Не делать кодовые изменения.
```

---

## 8. Шаблон: реализация модуля

```text
Ты работаешь в проекте Content Plant.

Задача:
Реализуй модуль:
[Module Name]

Scope:
[описать точный MVP scope]

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/02_platform_architecture/DATA_MODEL.md
4. docs/02_platform_architecture/PIPELINES_SPEC.md
5. docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md
6. docs/06_agents/AGENT_RULES.md
7. [module spec]

Do:
1. Проведи pre-check: какие сущности, статусы, API и UI нужны.
2. Реализуй только MVP scope.
3. Соблюдай project-scoped data model.
4. Добавь минимальные проверки / validation.
5. Не добавляй внешние интеграции, если они не входят в scope.
6. Обнови документацию, если реализация выявила несоответствие.
7. Верни отчёт.

Do not:
- Не создавать global data там, где нужен project_id.
- Не добавлять SaaS roles, billing или public onboarding.
- Не зашивать project-specific values.
- Не обходить Review, если контент идёт к публикации.
- Не делать autoposting обязательным.

Checks:
- Unit / integration checks, если есть.
- Manual flow check.
- Data scoping check.
- Status transition check.
- MVP boundary check.

Report:
- что реализовано;
- какие файлы изменены;
- какие migrations / models добавлены;
- какие API / UI добавлены;
- какие проверки выполнены;
- ограничения;
- следующие шаги.
```

---

## 9. Шаблон: реализация content format

```text
Ты работаешь в проекте Content Plant.

Задача:
Реализуй production support для content_type:
[content_type]

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/02_platform_architecture/DATA_MODEL.md
4. docs/02_platform_architecture/PIPELINES_SPEC.md
5. docs/03_modules/PRODUCTION_ENGINE_SPEC.md
6. docs/03_modules/QA_AND_REVIEW.md
7. docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md
8. docs/04_content_formats/FORMAT_[NAME].md
9. docs/06_agents/AGENT_RULES.md

Do:
1. Реализуй template-driven production flow.
2. Используй Brand Profile для colors, fonts, logo, CTA и restrictions.
3. Не hardcode проектные значения.
4. Создавай Render Job.
5. Сохраняй input snapshot.
6. Создавай Content Item.
7. Переводи output в needs_review.
8. Готовь base output files and metadata.
9. Передавай platform-ready package в Publishing / Export flow, если это входит в scope.

Do not:
- Не зашивать бренд, цену, URL или CTA в template.
- Не считать render output approved.
- Не пропускать QA.
- Не публиковать автоматически.
- Не добавлять новый content_type без format spec.

Checks:
- Format QA.
- Brand QA.
- Output file validation.
- Metadata validation.
- Review status check.
- Export package check.

Report:
- что реализовано;
- какие templates добавлены;
- какие entities используются;
- какие output files создаются;
- какие проверки выполнены;
- что осталось на later.
```

---

## 10. Шаблон: исправление бага

```text
Ты работаешь в проекте Content Plant.

Bug:
[описание бага]

Expected behavior:
[как должно быть]

Actual behavior:
[как сейчас]

Read first:
1. docs/00_index.md
2. docs/01_platform/MVP_SCOPE.md
3. docs/06_agents/AGENT_RULES.md
4. [документ модуля, где баг]

Do:
1. Найди причину бага.
2. Объясни root cause.
3. Исправь минимально.
4. Проверь, что исправление не ломает project scoping.
5. Проверь, что не добавлен project-specific hardcode.
6. Добавь или обнови тест, если возможно.
7. Верни отчёт.

Do not:
- Не переписывать модуль целиком.
- Не менять unrelated files.
- Не добавлять новые функции как побочный эффект.
- Не менять документацию без необходимости.

Report:
- root cause;
- changed files;
- verification;
- risks;
- follow-up, if needed.
```

---

## 11. Шаблон: добавление статуса

```text
Ты работаешь в проекте Content Plant.

Задача:
Добавить или изменить статус:
[entity] → [status]

Important:
Статусы нельзя добавлять только в коде. Сначала нужно проверить DATA_MODEL.md и PIPELINES_SPEC.md.

Read first:
1. docs/02_platform_architecture/DATA_MODEL.md
2. docs/02_platform_architecture/PIPELINES_SPEC.md
3. docs/06_agents/AGENT_RULES.md
4. relevant module spec

Do:
1. Проверь, нет ли уже подходящего статуса.
2. Объясни, зачем нужен новый статус.
3. Опиши allowed transitions.
4. Обнови документацию.
5. Только потом обнови код, если задача включает код.
6. Проверь UI / filters / QA / Dashboard impacts.

Do not:
- Не добавлять статус без lifecycle.
- Не использовать разные названия для одного смысла.
- Не смешивать Content Item status и Publication status.
- Не ломать existing flows.

Report:
- why status is needed;
- affected entity;
- allowed transitions;
- docs updated;
- code updated;
- checks.
```

---

## 12. Шаблон: добавление новой интеграции

```text
Ты работаешь в проекте Content Plant.

Задача:
Добавить интеграцию:
[integration_name]

Read first:
1. docs/02_platform_architecture/INTEGRATIONS_SPEC.md
2. docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md
3. docs/01_platform/MVP_SCOPE.md
4. docs/06_agents/AGENT_RULES.md
5. relevant module spec

Classify integration:
- storage
- LLM
- render
- publishing
- analytics_import
- website_event
- notification
- identity
- billing
- other

Do:
1. Проверь, входит ли интеграция в MVP.
2. Определи mode: manual / csv / api / export / webhook / disabled.
3. Опиши required credentials.
4. Реализуй через integration service layer.
5. Добавь error handling.
6. Добавь retry/fallback, если применимо.
7. Не делай интеграцию обязательной для MVP, если есть export/manual fallback.

Do not:
- Не хранить secrets в markdown, logs или export packages.
- Не завязывать core pipeline на одну внешнюю интеграцию.
- Не добавлять autoposting как mandatory path.
- Не обходить human review.

Report:
- integration added;
- mode;
- credentials handling;
- fallback;
- affected modules;
- checks;
- limitations.
```

---

## 13. Шаблон: UI-задача

```text
Ты работаешь в проекте Content Plant.

Задача:
Реализуй или обнови UI:
[screen / flow]

Read first:
1. docs/05_product_design/USER_WORKFLOWS.md
2. docs/05_product_design/WEB_UI_SPEC.md
3. docs/05_product_design/DASHBOARD_SPEC.md, если затронут Dashboard
4. docs/05_product_design/PROJECT_SETTINGS_SPEC.md, если затронут Settings
5. docs/02_platform_architecture/DATA_MODEL.md
6. docs/06_agents/AGENT_RULES.md

Do:
1. Определи основной user workflow.
2. Покажи active project context.
3. Не смешивай данные разных проектов.
4. Покажи status and next action.
5. Добавь empty/loading/error states.
6. Не добавляй SaaS UI, если это MVP.
7. Используй существующие statuses and entities.

Do not:
- Не делать decorative dashboard без actionability.
- Не скрывать project context.
- Не добавлять roles/billing/team UI.
- Не создавать unrelated screens.

Checks:
- Project switch behavior.
- Empty state.
- Loading state.
- Error state.
- Basic responsive behavior.
- Status filters.

Report:
- UI changed;
- workflow supported;
- files changed;
- checks;
- known limitations.
```

---

## 14. Шаблон: QA / Review задача

```text
Ты работаешь в проекте Content Plant.

Задача:
Добавить или обновить QA / Review logic:
[описание]

Read first:
1. docs/03_modules/QA_AND_REVIEW.md
2. docs/02_platform_architecture/PIPELINES_SPEC.md
3. docs/02_platform_architecture/DATA_MODEL.md
4. docs/06_agents/AGENT_RULES.md

Do:
1. Определи entity_type: idea / scenario / asset / render_job / content_item / publication.
2. Определи severity: info / warning / error / blocker.
3. Определи allowed user action.
4. Не блокируй всё подряд.
5. Сохрани actionable recommendation.
6. Убедись, что human review остаётся в loop.

Do not:
- Не заменять human review автоматическим QA.
- Не делать warning blocker без причины.
- Не пропускать content directly to publishing.
- Не hardcode project-specific rules outside Brand Profile.

Report:
- checks added;
- severity rules;
- affected flows;
- verification.
```

---

## 15. Шаблон: подготовка задачи для Codex

```text
Ты работаешь в репозитории Content Plant.

Сначала выполни короткий audit текущего состояния:
1. Найди релевантные файлы.
2. Прочитай документацию из списка.
3. Определи, что уже реализовано.
4. Определи минимальный safe change.

Документы:
- docs/00_index.md
- docs/01_platform/MVP_SCOPE.md
- docs/06_agents/AGENT_RULES.md
- [task-specific docs]

Задача:
[конкретная задача]

Ограничения:
- Не менять unrelated files.
- Не добавлять project-specific hardcode.
- Не расширять MVP.
- Не добавлять внешние API без задачи.
- Не ломать существующий pipeline.
- Если документация и код расходятся, сначала сообщи о конфликте.

Результат:
- Реализуй задачу.
- Запусти доступные проверки.
- Верни отчёт:
  - что изменено;
  - файлы;
  - проверки;
  - риски;
  - следующие шаги.
```

---

## 16. Шаблон: только анализ без изменений

```text
Ты работаешь в проекте Content Plant.

Задача:
Проанализируй:
[что анализировать]

Важно:
Не изменяй файлы.
Не создавай новые документы.
Не меняй код.

Read first:
- [список документов / файлов]

Проверь:
- соответствие документации;
- MVP scope;
- project-neutrality;
- data model;
- pipeline consistency;
- risks;
- missing pieces.

Report:
1. Summary
2. Findings
3. Risks
4. Recommendations
5. Next steps
```

---

## 17. Шаблон: project-level документ

Использовать только для документов внутри `docs/07_projects/{project_slug}/`.

```text
Ты работаешь в Content Plant.

Задача:
Создай или обнови project-level документ:
docs/07_projects/{project_slug}/[DOCUMENT].md

Важно:
Этот документ может содержать project-specific данные.
Но platform-level документы менять нельзя, если задача этого явно не требует.

Read first:
1. docs/00_index.md
2. docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
3. docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
4. docs/06_agents/AGENT_RULES.md
5. existing docs/07_projects/{project_slug}/ files, если есть

Do:
1. Используй структуру project profile layer.
2. Не меняй platform docs.
3. Не зашивай project-specific rules в templates или code.
4. Явно укажи, что документ относится только к этому Project.

Report:
- project document changed;
- project-specific decisions;
- platform docs untouched or changed with reason;
- next steps.
```

---

## 18. Шаблон: финальный отчёт агента

```text
Готово.

Что сделано:
- ...

Изменённые файлы:
- path/to/file
- path/to/file

Документация:
- Прочитано:
  - ...
- Обновлено:
  - ...
- Не обновлялось:
  - ... потому что ...

Проверка:
- [check] — passed / failed / not run
- [check] — passed / failed / not run

Ограничения / замечания:
- ...

Риски:
- ...

Следующие шаги:
- ...
```

---

## 19. Минимальный pre-check для любой задачи

Перед работой агент должен мысленно или явно пройти чеклист:

```text
Task:
Platform-level or project-level:
MVP scope:
Source of truth:
Affected entities:
Affected statuses:
Affected pipeline:
Affected files:
Risks:
Checks:
```

Если задача затрагивает архитектуру, модель данных или pipeline, отчёт должен явно упомянуть это.

---

## 20. Anti-patterns

Не использовать задачи вида:

```text
Сделай красиво.
Сделай как в прошлом проекте.
Добавь всё, что нужно.
Автоматизируй публикации во все соцсети.
Сделай универсально, сам реши как.
```

Такие задачи создают хаос.

Хорошая задача должна иметь:

- границы;
- документы;
- allowed files;
- checks;
- report format.

---

## 21. Open questions

1. Нужно ли хранить эти шаблоны также в отдельной папке для Codex prompts?
2. Нужно ли сделать короткие версии шаблонов для маленьких задач?
3. Нужно ли добавить шаблон для database migration?
4. Нужно ли добавить шаблон для release checklist?
5. Нужно ли добавить шаблон для project onboarding?

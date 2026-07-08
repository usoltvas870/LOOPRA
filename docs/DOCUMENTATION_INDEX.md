# LOOPRA Documentation Index

Status: Active  
Updated: 2026-07-08  
Project: LOOPRA — Autonomous Marketing Operating System

This document is the main navigator for LOOPRA documentation.
It reflects the current architecture and serves as the entry point for understanding the system.

---

## 00_foundation

**Назначение:** Фундамент MVP и базовые модели системы.

Documents:

| File | Description |
|---|---|
| `MVP_SCOPE.md` | Current minimal foundation MVP definition and boundaries |
| `DATA_MODEL.md` | Core data model: entities, relationships, ownership boundaries |
| `WORKSPACE_AND_PROJECT_MODEL.md` | Multi-project architecture: Workspace, Project, Brand Profile, storage separation |
| `DEVELOPER_QUICKSTART.md` | Developer onboarding: tests, smoke loop, package inspection, manual metrics |

---

## 01_product

**Назначение:** Продуктовая идентичность и стратегия.

Documents:

| File | Description |
|---|---|
| `LOOPRA_BRAND_POSITIONING.md` | Brand identity, mission, and positioning as Autonomous Marketing OS |
| `LOOPRA_TRANSITION_PLAN.md` | Transition from Content Plant to LOOPRA: decisions, scope, migration |

---

## 02_architecture

**Назначение:** Системная архитектура LOOPRA.

Documents:

| File | Description |
|---|---|
| `LOOPRA_ARCHITECTURE.md` | Core architectural source of truth for LOOPRA |
| `BRAND_SYSTEM_SPEC.md` | Brand System: operational knowledge layer for autonomous marketing cycles |
| `PLATFORM_OVERVIEW.md` | Top-level platform description: foundation loop, MVP boundaries, module ownership |
| `PIPELINES_SPEC.md` | Current pipeline stages: Idea → Scenario → ContentItem → ExportPackage → Publication → MetricSnapshot |

---

## 03_intelligence

**Назначение:** Будущие интеллектуальные модули.

Reserved for future:

- Trend Intelligence — market signal capture and analysis
- Content Intelligence — content optimization and insight generation
- Agent Architecture — autonomous agent orchestration
- Learning Memory — feedback loops and improvement tracking

---

## 04_production

**Назначение:** Производство контента.

Documents:

| File | Description |
|---|---|
| `CONTENT_FORMATS_OVERVIEW.md` | Platform-level content format portfolio: `text_social_post` and future candidates |

---

## 05_platform

**Назначение:** Будущая SaaS-платформа.

Reserved for future:

- Workspace Management
- Billing
- Multi-tenancy
- User Management

---

## 06_operations

**Назначение:** Эксплуатация системы.

Reserved for future:

- Deployment
- Monitoring
- Operations

---

## 07_projects

**Назначение:** Проектные конфигурации.

Current projects:

- `nura/` — NURA validation project
  - `README.md` — Navigation and scope
  - `POSITIONING.md` — Product definition, audience, value proposition
  - `TONE_OF_VOICE.md` — Brand voice rules and examples
  - `CONTENT_PILLARS.md` — Content themes and boundaries
  - `VALIDATION_PLAN.md` — Validation goals and success criteria

---

## 08_roadmap

**Назначение:** Будущее развитие LOOPRA.

Reserved for future:

- Product Roadmap
- Autonomous Cycles
- Agent Evolution

---

## Archive

`docs/archive/content-plant-era/`

Содержит исторические документы эпохи Content Plant.

Важно: Archive не является источником текущих архитектурных решений.
Все активные решения LOOPRA находятся в numbered directories выше.

---

## Documentation Rules

**Как использовать документацию:**

1. Для архитектурных решений использовать:
   - `02_architecture/LOOPRA_ARCHITECTURE.md` — архитектурный источник истины
   - `STATE.md` — текущее состояние системы
   - `AGENTS.md` — правила разработки для агентов

2. Для разработки использовать:
   - `00_foundation/` — фундамент MVP, модель данных, quickstart

3. Для понимания будущего направления:
   - `01_product/` — продуктовая стратегия и бренд
   - `08_roadmap/` — план развития (зарезервировано)

4. Исторические документы использовать только для контекста:
   - `archive/` — не является источником текущих решений

---

## Quick Reference

| Question | Document |
|---|---|
| What is LOOPRA? | `02_architecture/PLATFORM_OVERVIEW.md` |
| What is the architecture? | `02_architecture/LOOPRA_ARCHITECTURE.md` |
| What is the current MVP scope? | `00_foundation/MVP_SCOPE.md` |
| What is the data model? | `00_foundation/DATA_MODEL.md` |
| How do projects work? | `00_foundation/WORKSPACE_AND_PROJECT_MODEL.md` |
| How do I set up development? | `00_foundation/DEVELOPER_QUICKSTART.md` |
| What pipeline stages exist? | `02_architecture/PIPELINES_SPEC.md` |
| What content formats are available? | `04_production/CONTENT_FORMATS_OVERVIEW.md` |
| How did LOOPRA transition happen? | `01_product/LOOPRA_TRANSITION_PLAN.md` |
| What documents need updating? | `UPDATE_REQUIRED_LOOPRA_DOCS.md` |
| What is the current state? | `../STATE.md` |
| What are the agent rules? | `../AGENTS.md` |

---

## Boundary Rules

1. Active LOOPRA documentation lives in `docs/` numbered directories only.
2. `docs/archive/` contains historical Content Plant documents — these do NOT define current scope.
3. No document in active directories should reference "Content Plant" as active product identity.
4. Permitted "Content Plant" mentions: `archive/content-plant-era/`, `01_product/LOOPRA_TRANSITION_PLAN.md`.
5. Project-specific truth must stay in `docs/07_projects/{project_slug}/` or `projects/{project_id}/project.yaml`.
6. Platform docs must remain project-agnostic.

# Content Plant Documentation Index

## 1. Purpose

This document lists the current foundation docs that define the project-agnostic baseline for Content Plant.

It reflects the current flat docs layout and the current minimal foundation MVP.

---

## 2. Current Baseline

- Content Plant foundation is project-agnostic.
- Current foundation loop:

```text
Idea
-> Scenario
-> ContentItem
-> ExportPackage v1
-> Manual Publication Record v1
-> MetricSnapshot v1
```

- Current safest foundation format: `text_social_post`
- Current foundation is export-first.
- Current foundation is manual-publication-first.
- Current foundation is manual-metrics-first.

---

## 3. Read First

Read in this order at the start of a new task:

1. `STATE.md`
2. `AGENTS.md`
3. `docs/00_index.md`
4. `docs/PLATFORM_OVERVIEW.md`
5. `docs/MVP_SCOPE.md`
6. `docs/WORKSPACE_AND_PROJECT_MODEL.md`
7. `docs/CONTENT_FORMATS_OVERVIEW.md`
8. `docs/PRODUCT_STRATEGY.md`
9. `docs/USER_WORKFLOWS.md`
10. `docs/AGENT_RULES.md`
11. `docs/DATA_MODEL.md`
12. `docs/PIPELINES_SPEC.md`
13. task-specific docs

---

## 4. Current Flat Docs Layout

### 4.1. Foundation baseline

- `STATE.md`
- `AGENTS.md`
- `docs/PLATFORM_OVERVIEW.md`
- `docs/MVP_SCOPE.md`
- `docs/PRODUCT_STRATEGY.md`

### 4.2. Workflow and domain docs

- `docs/WORKSPACE_AND_PROJECT_MODEL.md`
- `docs/CONTENT_FORMATS_OVERVIEW.md`
- `docs/USER_WORKFLOWS.md`
- `docs/DATA_MODEL.md`
- `docs/PIPELINES_SPEC.md`

### 4.3. Agent guidance

- `docs/AGENT_RULES.md`

### 4.4. Broader platform references

Use only when a task explicitly needs them:

- `docs/SYSTEM_ARCHITECTURE.md`
- `docs/BRAND_SYSTEM_SPEC.md`
- `docs/PRODUCTION_ENGINE_SPEC.md`
- `docs/ANALYTICS_AND_OPTIMIZATION.md`
- `docs/WEB_UI_SPEC.md`
- `docs/PROJECT_SETTINGS_SPEC.md`

These documents must not override the current foundation baseline unless they are aligned with the current MVP.

---

## 5. Project-Specific Source Of Truth

Project-specific logic may live only in:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/project.yaml
```

Platform-level docs and platform-level code must remain project-agnostic.

---

## 6. Source Of Truth Priority

For current foundation work, prefer this order:

1. `STATE.md`
2. `AGENTS.md`
3. `docs/PLATFORM_OVERVIEW.md`
4. `docs/MVP_SCOPE.md`
5. `docs/WORKSPACE_AND_PROJECT_MODEL.md`
6. `docs/USER_WORKFLOWS.md`
7. `docs/AGENT_RULES.md`
8. `docs/DATA_MODEL.md`
9. `docs/PIPELINES_SPEC.md`

If documents conflict, do not silently follow older expanded-scope guidance.

---

## 7. Rules For Agents

- Use the current flat docs layout.
- Do not use old numbered docs tree paths as the active baseline.
- Do not add project-specific hardcode to the foundation layer.
- Do not treat generated runtime artifacts or `graphify-out/` as source changes.
- Do not expand the current MVP without explicit approval.

---

## 8. Status

Status: Draft  
Version: 0.3  
Updated: 2026-07-07  
Project: Content Plant  
Current docs layout: flat foundation docs baseline

# Pipelines Spec

## 1. Purpose

This document describes the current helper-supported local/manual pipeline for the Content Plant foundation MVP.

It documents the active baseline only and should not be read as a broader future automation plan.

---

## 2. Current Foundation Loop

The current active pipeline is:

```text
Idea
-> Scenario
-> ContentItem
-> ExportPackage v1
-> Manual Publication Record v1
-> MetricSnapshot v1
```

This is the current real foundation loop that must stay aligned across docs, code, and tests.

---

## 3. Source Of Truth

Use these documents together for the current baseline:

- `STATE.md`
- `AGENTS.md`
- `docs/PLATFORM_OVERVIEW.md`
- `docs/USER_WORKFLOWS.md`
- `docs/DATA_MODEL.md`

If older or broader pipeline descriptions conflict with this loop, follow the current minimal foundation baseline.

---

## 4. Current Helper-Supported Workflow

Current developer helpers:

```bash
python scripts/smoke_loop.py
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

These helpers define the current practical verification path for the local/manual foundation workflow.

---

## 5. Active Pipeline Stages

### 5.1. Idea -> Scenario

Current purpose:

- create or load a project-scoped `Idea`
- create a project-scoped `Scenario`
- approve the scenario for the minimal content flow

### 5.2. Scenario -> ContentItem

Current purpose:

- create a `ContentItem` from the approved scenario
- move the content item toward export inside the current production lifecycle

The current minimal `text_social_post` loop does not require a larger media pipeline to be considered MVP-ready.

### 5.3. ContentItem -> ExportPackage v1

Current purpose:

- prepare `ExportPackage v1`
- make the package inspectable
- make the package validatable

Current verification helpers:

```bash
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
```

### 5.4. ExportPackage v1 -> Manual Publication Record v1

Current purpose:

- publish manually outside the system
- store the manual publication outcome in `Publication`

Current rule:

- publication remains manual in the foundation MVP

### 5.5. Manual Publication Record v1 -> MetricSnapshot v1

Current purpose:

- create a draft `MetricSnapshot`
- find the draft snapshot in local storage
- import manually collected metrics into the draft snapshot

Current helpers:

```bash
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

Current metrics path is manual.

The current foundation does not automatically derive downstream recommendations or create follow-on work items from recorded metrics.

---

## 6. Current Export Output

For the current `text_social_post` loop, `ExportPackage v1` writes:

```text
title.txt
body.txt
caption_{platform}.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

This output is meant for inspection, validation, and manual publication.

---

## 7. Runtime Artifacts

Current local smoke workflow writes runtime artifacts under:

```text
storage/smoke_projects/{project_slug}/...
```

Rules:

- runtime artifacts are local-only
- generated runtime artifacts must not be committed
- `graphify-out/` remains generated local output

---

## 8. Current Boundary Rules

The active pipeline does not require:

- public API
- frontend UI
- database migrations
- SaaS layers
- autoposting
- external APIs
- external analytics APIs
- broader media automation as a current MVP dependency
- automatic downstream loops from recorded metrics

The current pipeline must remain project-agnostic.

---

## 9. Readiness Checks

The current pipeline baseline is healthy when:

- `python scripts/smoke_loop.py` completes
- the generated export package can be inspected
- the generated export package can be validated
- draft metric snapshots can be listed locally
- manual metrics can be imported into a draft snapshot
- tracked source files remain clean after verification

---

## 10. Status

Status: Draft  
Version: 0.3  
Updated: 2026-07-07  
Project: Content Plant  
Current pipeline scope: local/manual helper-supported foundation MVP

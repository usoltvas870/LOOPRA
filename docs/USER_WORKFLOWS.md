# User Workflows

## 1. Purpose

This document describes the current user-facing workflow for the Content Plant foundation MVP.

It is intentionally narrow and reflects the real local/manual workflow that is implemented today.

This document is project-agnostic. Project-specific behavior belongs only in:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/project.yaml
```

---

## 2. Current Foundation Workflow

The current foundation MVP supports this minimal loop:

```text
Idea
-> Scenario
-> ContentItem
-> ExportPackage v1
-> Manual Publication Record v1
-> MetricSnapshot v1
```

The current practical workflow is:

```text
1. Generate or create Idea
2. Create Scenario
3. Create ContentItem
4. Prepare ExportPackage v1
5. Inspect package
6. Validate package
7. Publish manually outside the system
8. Record Manual Publication Record v1
9. Find draft MetricSnapshot
10. Import manual metrics
```

---

## 3. Current MVP Shape

The current foundation MVP is:

- export-first
- manual-publication-first
- manual-metrics-first
- local/filesystem-first
- project-agnostic

The current foundation MVP does not require:

- UI
- API
- render/video engine
- autoposting
- external analytics APIs
- generated insights from metrics
- generated new ideas from metrics

---

## 4. Primary User

The current MVP assumes an internal operator who runs the local workflow, checks export packages, publishes manually outside the system, and records metrics manually.

The MVP is not a public SaaS flow and is not an end-user self-serve product.

---

## 5. Current User Journey

### 5.1. Create or generate Idea

Goal:
Create a project-scoped content idea.

Result:
An `Idea` exists for the selected project.

Current relevant statuses:

```text
raw
approved
scripted
archived
```

### 5.2. Create Scenario

Goal:
Turn an approved idea into a project-scoped scenario for the safest current format.

Current safest format:

```text
text_social_post
```

Result:
A `Scenario` exists and can be approved for content creation.

Current relevant statuses:

```text
draft
needs_review
approved
rejected
archived
```

### 5.3. Create ContentItem

Goal:
Create a `ContentItem` from an approved scenario inside the current production lifecycle.

Result:
A `ContentItem` exists and can move toward export.

Current relevant statuses:

```text
draft
in_production
rendered
qa_failed
needs_review
approved
rejected
exported
archived
```

### 5.4. Prepare ExportPackage v1

Goal:
Prepare an export-ready package for manual publication.

Current package files:

```text
title.txt
body.txt
caption_{platform}.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

Result:
An `ExportPackage` becomes ready for inspection and validation.

Current relevant statuses:

```text
draft
ready
failed
archived
```

### 5.5. Inspect package

Goal:
Read the prepared package summary and confirm the expected files and metadata are present.

Developer helper:

```bash
python scripts/inspect_package.py <export_package_directory>
```

Result:
The operator can verify package identity, platform, status, and included files.

### 5.6. Validate package

Goal:
Confirm the prepared package is complete and safe for manual publication.

Developer helper:

```bash
python scripts/validate_package.py <export_package_directory>
```

Result:
The operator knows whether the package is ready for manual publication.

### 5.7. Publish manually outside the system

Goal:
Publish the prepared content outside Content Plant using the generated export package.

Current rule:
Publication is manual for the current MVP.

Result:
The content is published on the target platform outside the system.

### 5.8. Record Manual Publication Record v1

Goal:
Store the publication outcome in `Publication`.

Current relevant statuses:

```text
planned
published
failed
archived
```

Current stored publication fields include:

```text
published_url
published_at
```

### 5.9. Find draft MetricSnapshot

Goal:
Locate the draft metric snapshot created for the manual metrics path.

Developer helper:

```bash
python scripts/find_metric_snapshots.py <project_id>
```

Local smoke usage:

```bash
CONTENT_PLANT_PROJECTS_ROOT=storage/smoke_projects python scripts/find_metric_snapshots.py example
```

Result:
The operator gets the `metric_snapshot_id` needed for manual metrics import.

### 5.10. Import manual metrics

Goal:
Record manually collected metrics into the draft snapshot.

Developer helper:

```bash
python scripts/import_manual_metrics.py <manual_metrics_json>
```

Result:
The draft `MetricSnapshot` becomes recorded.

Current relevant statuses:

```text
draft
recorded
invalid
```

---

## 6. Current Dev Helpers

The current local/manual workflow relies on these scripts:

```bash
python scripts/smoke_loop.py
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

Recommended local flow:

```text
Run smoke loop
-> inspect generated package
-> validate generated package
-> find draft metric snapshot
-> import manual metrics
```

---

## 7. Current Boundaries

The current workflow must stay within these boundaries:

- no UI workflow is required for the current MVP
- no API workflow is required for the current MVP
- no autoposting is required for the current MVP
- no external analytics APIs are required for the current MVP
- no platform-specific direct integrations are required for the current MVP
- no render/video engine is required for the current MVP
- no generated insights or generated new ideas are required for the current MVP

---

## 8. Future And Out-Of-Scope Items

The following items may exist later, but they are not current MVP requirements:

- Visual Prompts
- Asset Library
- Dialog Miniseries
- Trend Radar
- Render Video
- scheduling/calendar flows
- autoposting
- external analytics integrations

If these are introduced later, they must be documented as future expansions and must not rewrite the current foundation baseline retroactively.

---

## 9. Workflow Readiness Criteria

The current workflow can be considered aligned when:

- the loop remains `Idea -> Scenario -> ContentItem -> ExportPackage v1 -> Manual Publication Record v1 -> MetricSnapshot v1`
- `text_social_post` remains the safest current foundation format
- export package inspection works locally
- export package validation works locally
- manual publication remains outside the system
- manual metrics can be found and imported locally
- the workflow remains project-agnostic

---

## 10. Status

Status: Draft  
Version: 0.2  
Updated: 2026-07-07  
Project: Content Plant  
Current workflow scope: local/manual foundation MVP

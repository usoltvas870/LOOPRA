# Data Model

## 1. Purpose

This document describes the current high-level foundation data model for Content Plant.

It is intentionally narrow and describes only the active baseline that is relevant to the current minimal MVP.

---

## 2. Core Modeling Principle

Content Plant foundation must stay project-agnostic.

Anything that belongs to a concrete project must remain project-scoped and must not leak into the platform layer.

Project-specific source of truth may live only in:

```text
docs/07_projects/{project_slug}/
projects/{project_id}/project.yaml
```

---

## 3. Current Foundation Entity Set

The current minimal foundation loop depends on these entities:

```text
Project context
-> Idea
-> Scenario
-> ContentItem
-> ExportPackage
-> Publication
-> MetricSnapshot
```

This is the current active baseline for foundation work.

---

## 4. Entity Roles

### 4.1. Project context

`Project` and related project config define which project the content belongs to and keep the loop project-scoped.

### 4.2. Idea

`Idea` is the project-scoped starting point for the current loop.

### 4.3. Scenario

`Scenario` is the project-scoped content plan created from an `Idea` for the current minimal flow.

### 4.4. ContentItem

`ContentItem` is the produced content unit that moves toward export.

### 4.5. ExportPackage

`ExportPackage` is the prepared package for manual publication.

In the current MVP, `ExportPackage v1` is inspection-friendly and validation-friendly.

### 4.6. Publication

`Publication` is the manual publication record for the current MVP.

It stores publication outcome metadata such as `published_url` and `published_at` when available.

### 4.7. MetricSnapshot

`MetricSnapshot` stores the current manual metrics checkpoint for a publication.

Current foundation behavior:

- draft snapshots are created for the manual metrics path
- metrics are recorded through manual import
- `clicks` input is normalized to stored `link_clicks`
- `published_url` updates the related `Publication`
- `published_url` is not stored as a raw metric field inside snapshot metrics

---

## 5. Relationship Overview

Current high-level relationship:

```text
Project
-> Idea
-> Scenario
-> ContentItem
-> ExportPackage
-> Publication
-> MetricSnapshot
```

This is the canonical current foundation flow for the active MVP.

---

## 6. Ownership Boundaries

- `Production Engine` owns `ContentItem`, technical QA result, and render output metadata.
- `Publishing Hub` owns `ExportPackage` and `Publication`.
- analytics foundation owns `MetricSnapshot`.

`RenderJob` and `OutputFile` remain part of the broader domain boundary, but they are not required prerequisites for the current minimal `text_social_post` foundation loop and should not be treated as current MVP must-haves.

---

## 7. Status Guidance

This document does not duplicate long status enumerations.

Rules:

- use the current enum values from code and tests as canonical
- do not invent guessed statuses in docs
- do not mix `ContentItem` status and `Publication` status
- do not mix analytics state with publication state

If a task needs exact status names, verify them against the current domain model and transition tests.

---

## 8. Storage And Scoping

Current foundation storage remains project-scoped.

Important rules:

- content records stay tied to project context
- runtime smoke artifacts under `storage/smoke_projects/...` are local-only
- `graphify-out/` is local generated output
- generated/runtime artifacts must not be treated as source changes

---

## 9. Current Exclusions

The current foundation baseline does not require separate active MVP entities for broader discovery, media intake, scheduling, automation, or downstream recommendation loops.

If such entities are introduced later, they must be documented as future expansion rather than retroactively treated as current foundation requirements.

---

## 10. Readiness Criteria

The current data model baseline is aligned when:

- the minimal loop entities above are the active documented baseline
- project scoping remains explicit
- `ExportPackage` and `Publication` ownership stays in `Publishing Hub`
- `MetricSnapshot` remains a manual metrics record in the current MVP
- broader future concepts do not redefine the active baseline

---

## 11. Status

Status: Draft  
Version: 0.3  
Updated: 2026-07-07  
Project: Content Plant  
Current model scope: minimal foundation entity baseline

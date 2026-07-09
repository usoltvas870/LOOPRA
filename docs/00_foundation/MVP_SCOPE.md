# MVP Scope

## 1. Purpose

This document defines the current minimal foundation MVP for LOOPRA.

It describes the real baseline that is implemented today and must not be read as a broader future platform plan.

---

## 2. Current MVP Definition

The current foundation MVP is the smallest project-agnostic content loop that runs locally and can be verified end-to-end.

Current loop:

```text
Idea
-> Scenario
-> ContentItem
-> ExportPackage v1
-> Manual Publication Record v1
-> MetricSnapshot v1
```

---

## 3. Current MVP Principles

- project-agnostic foundation
- export-first
- manual-publication-first
- manual-metrics-first
- local/filesystem-first
- `text_social_post` as the safest current format

The current MVP does not depend on UI, API, media automation, or external service integrations.

---

## 4. What Is In Scope Now

The current foundation MVP includes:

- project loading and project config binding
- `Idea` creation and project scoping
- `Scenario` creation for the current minimal loop
- `ContentItem` creation inside the current production lifecycle
- `ExportPackage v1` preparation for manual publication
- manual publication recording through `Publication`
- draft `MetricSnapshot` creation for the manual metrics path
- local/manual metrics lookup and import
- filesystem persistence
- local smoke workflow verification

Current developer helpers:

```bash
python scripts/smoke_loop.py
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

---

## 5. Current MVP Boundaries

The current foundation MVP does not include:

- public API
- frontend UI
- database persistence layer or migrations
- SaaS, billing, users, roles, teams, or marketplace
- autoposting
- external APIs
- external analytics APIs
- real video/render pipeline as a current MVP requirement
- scheduling product layers as a current MVP requirement
- automatic analytical interpretation of metrics
- automatic follow-on idea generation from metrics
- project-specific validation behavior inside the foundation layer

The current MVP also does not require project-specific examples, templates, prompts, assets, or packages in platform docs or platform code.

---

## 6. Current Format Boundary

Current safest format:

```text
text_social_post
```

This format is the safest current foundation entry point because it allows the project to verify:

- project scoping
- scenario-to-content flow
- export package generation
- package inspection and validation
- manual publication recording
- manual metrics recording

without requiring a larger media stack.

---

## 7. Current Metrics Boundary

Current metrics behavior is intentionally narrow:

- `MetricSnapshot` starts in a draft state in the local/manual workflow
- metrics are imported manually
- the helper path is local and developer-oriented
- `clicks` input is normalized to stored `link_clicks`
- `published_url` updates the related `Publication`
- `published_url` is not stored as a raw metric field inside `MetricSnapshot` metrics

The current foundation does not generate downstream recommendations or new work items from recorded metrics.

---

## 8. Future And Out-Of-Scope Directions

Future expansion may later add broader discovery, richer media workflows, scheduling layers, automation, and deeper analytics.

These are future directions only. They are not current MVP requirements and must not be treated as part of the active baseline.

---

## 9. MVP Readiness Criteria

The current foundation MVP can be considered aligned when:

- the documented loop matches the implemented loop
- the foundation remains project-agnostic
- `text_social_post` remains the current safest format
- `smoke_loop.py` runs the minimal loop end-to-end
- export packages can be inspected and validated locally
- manual publication remains outside the system
- manual metrics can be found and imported locally
- generated runtime artifacts remain ignored by Git

---

## 10. Status

Status: Active  
Version: v1.0  
Updated: 2026-07-09  
Project: LOOPRA  
Current MVP scope: minimal local/manual foundation baseline

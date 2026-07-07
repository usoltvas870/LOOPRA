# NURA Validation Plan

## 1. Validation Goal

Verify that the Content Plant foundation MVP can serve a real project (NURA)
without modifying the project-agnostic foundation layer.

## 2. First Validation Output

```text
1 NURA text_social_post export package for manual publication
```

Generated through the existing foundation loop:

```text
Idea → Scenario → ContentItem → ExportPackage v1 → Manual Publication Record v1 → MetricSnapshot v1
```

Package content:

```text
title.txt
body.txt
caption_telegram.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

## 3. Manual Publication Only

```text
Publication is manual-only for the current foundation MVP.
The package is exported locally and published manually outside Content Plant.
No autoposting. No external platform APIs.
```

## 4. Manual Metrics Only

```text
Metrics are collected manually and imported through:
CONTENT_PLANT_PROJECTS_ROOT=storage/smoke_projects python scripts/import_manual_metrics.py <json>

No external analytics APIs. No automatic insights.
```

## 5. Success Criteria

```text
[ ] NURA project config passes ProjectService validation
[ ] Foundation core unchanged
[ ] 1 NURA text_social_post export package generated
[ ] Package passes inspect_package.py
[ ] Package passes validate_package.py (validation_status=ok, ready_for_manual_publication=true)
[ ] manual_publication_checklist.txt present
[ ] Manual Publication record created
[ ] Draft MetricSnapshot created and findable via find_metric_snapshots.py
[ ] Manual metrics importable via import_manual_metrics.py
[ ] MetricSnapshot becomes recorded
[ ] No NURA leakage into core/, scripts/, tests/
[ ] Foundation tests (107/107) pass unchanged
[ ] compileall core and compileall scripts pass
```

## 6. Non-Goals

```text
No video/image/render output
No autoposting
No external APIs
No analytics API integrations
No generated insights or new ideas from metrics
No new content formats beyond text_social_post
No foundation architecture changes
No NURA hardcode in foundation
```

## 7. Next Step After Skeleton Approval

```text
Run NURA smoke loop:
CONTENT_PLANT_SMOKE_PROJECT_ID=nura CONTENT_PLANT_SMOKE_PROJECTS_ROOT=storage/smoke_projects python scripts/smoke_loop.py

Then inspect, validate, find metrics, and import manual metrics.
```

## 8. Status

```text
Skeleton created: 2026-07-07
First content output: not yet generated
Validation status: pending
```

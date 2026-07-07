# Developer Quickstart v1

Status: Current  
Version: 1.0  
Updated: 2026-07-07  
Project: Content Plant

---

## 1. What This Foundation MVP Is

Content Plant foundation MVP is a project-agnostic local platform for systematic content production.

Current characteristics:

- export-first
- manual-publication-first
- manual-metrics-first
- filesystem-based persistence
- no external dependencies

Current loop:

```text
Idea → Scenario → ContentItem → ExportPackage v1 → Manual Publication Record v1 → MetricSnapshot v1
```

---

## 2. What It Is Not

Current MVP does not include:

- API or UI
- database or migrations
- SaaS, billing, users, roles, marketplace
- autoposting
- external APIs
- external analytics APIs
- HyperFrames, FFmpeg, video assembler
- Trend Radar implementation
- generated insights or new ideas from metrics
- NURA validation project

---

## 3. Source-of-Truth Docs

Current source-of-truth docs:

```text
STATE.md
AGENTS.md
docs/00_index.md
docs/PLATFORM_OVERVIEW.md
docs/MVP_SCOPE.md
docs/DATA_MODEL.md
docs/PIPELINES_SPEC.md
docs/CONTENT_FORMATS_OVERVIEW.md
docs/PRODUCT_STRATEGY.md
docs/WORKSPACE_AND_PROJECT_MODEL.md
docs/AGENT_RULES.md
docs/USER_WORKFLOWS.md
```

Legacy/spec docs with `Legacy / future-scope note` are future/archival docs. Do not use them to expand current MVP scope unless an Architecture Gate explicitly reactivates them.

---

## 4. Check Repository Baseline

```bash
git status --short
git log --oneline -5
```

Expected state:

- clean working tree
- latest baseline should include `Mark foundation MVP ready` or later

---

## 5. Run Tests

```bash
python -m unittest tests.domain.test_models tests.domain.test_transitions tests.services.test_ideas tests.services.test_projects tests.services.test_loop_engineering tests.services.test_smoke_loop -v
python -m unittest tests.services.test_inspect_package -v
python -m unittest tests.services.test_validate_package -v
python -m unittest tests.services.test_import_manual_metrics -v
python -m unittest tests.services.test_find_metric_snapshots -v
python -m unittest tests.services.test_manual_metrics_workflow -v
```

Expected current result: `107/107 tests OK`

If the system Python is broken, use the project runtime Python if available.

---

## 6. Run Compile Checks

```bash
python -m compileall core
python -m compileall scripts
```

---

## 7. Run Smoke Loop

```bash
python scripts/smoke_loop.py
```

Creates a generic smoke project under `storage/smoke_projects/`. Runtime artifacts are ignored and must not be committed.

---

## 8. Inspect Export Package

```bash
python scripts/inspect_package.py <export_directory_from_smoke_output>
```

Expected package files:

```text
title.txt
body.txt
caption_{platform}.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

---

## 9. Validate Export Package

```bash
python scripts/validate_package.py <export_directory_from_smoke_output>
```

Expected success:

```text
validation_status=ok
ready_for_manual_publication=true
```

---

## 10. Find Draft MetricSnapshot

```bash
CONTENT_PLANT_PROJECTS_ROOT=storage/smoke_projects python scripts/find_metric_snapshots.py example
```

Lists draft snapshots and gives `metric_snapshot_id` for manual metrics import.

---

## 11. Import Manual Metrics

JSON shape:

```json
{
  "project_id": "example",
  "metric_snapshot_id": "metric_...",
  "metrics": {
    "views": 100,
    "likes": 12,
    "comments": 3,
    "shares": 1,
    "saves": 2,
    "clicks": 5,
    "published_url": "https://example.invalid/post/123"
  }
}
```

Command:

```bash
CONTENT_PLANT_PROJECTS_ROOT=storage/smoke_projects python scripts/import_manual_metrics.py <manual_metrics_json>
```

Notes:

- `clicks` is accepted as input and stored as `link_clicks`
- `published_url` updates `Publication.published_url`
- `published_url` is not stored as a raw metric field inside `MetricSnapshot.content_metrics`

---

## 12. Generated Artifacts Rule

- `storage/smoke_projects/` is runtime output
- `graphify-out/` is generated output
- generated/runtime artifacts must not be staged/committed

Check commands:

```bash
git status --short --ignored -- storage graphify-out
git ls-files storage graphify-out
```

---

## 13. Safe Next Steps

Safe next step options (do not start without explicit task):

- developer/operator polish
- NURA as validation project only via Architecture Gate
- additional content format only as a scoped task
- UI/API only as Architecture Gate

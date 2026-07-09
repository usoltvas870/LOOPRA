# Data Model

## 1. Purpose

This document describes the current high-level foundation data model for LOOPRA.

It is intentionally narrow and describes only the active baseline that is relevant to the current minimal MVP.

---

## 2. Core Modeling Principle

LOOPRA foundation must stay project-agnostic.

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

## 4. Future Intelligence Layer Entities

Future versions of LOOPRA will include additional entities that belong to
the Intelligence Layer.

These entities are NOT part of the current Foundation MVP. They are
documented here as architectural direction only.

### 4.1. MarketSignal

Purpose:

An incoming market signal:

- trend
- audience behaviour change
- popular format emergence
- new behaviour pattern

Relationship:

`MarketSignal` feeds into Trend Intelligence.

---

### 4.2. TrendPattern

Purpose:

An extracted pattern of successful content.

Examples:

- hook pattern
- topic pattern
- format pattern
- audience response pattern

Relationship:

`TrendPattern` feeds into Content Intelligence.

---

### 4.3. ContentInsight

Purpose:

A system conclusion about which content has potential.

Example:

"Short videos with educational hooks perform better for this audience."

---

### 4.4. Experiment

Purpose:

A controlled content experiment.

Examples:

- new video format
- new hook
- new topic
- new CTA strategy

---

### 4.5. AgentDecision

Purpose:

A record of decisions made by the Orchestrator Agent.

Examples:

- select topic
- change format
- stop publication
- launch experiment

---

### 4.6. LearningMemoryEntry

Purpose:

Long-term system memory.

Stores:

- what works
- what does not work
- which patterns are effective
- which decisions produced results

---

### 4.7. OptimizationAction

Purpose:

A system action to improve the next cycle.

Example:

"Increase usage of educational carousel format based on previous performance."

---

## 5. Foundation Layer vs Intelligence Layer

Foundation Layer is responsible for:

- content creation
- object storage
- export
- publication
- metric recording

Intelligence Layer is responsible for:

- signal analysis
- pattern discovery
- decision making
- learning
- optimization

```text
Foundation:

Project
↓
Idea
↓
Scenario
↓
ContentItem
↓
Publication
↓
MetricSnapshot

Intelligence:

MarketSignal
↓
Insight
↓
Decision
↓
Learning
↓
Optimization
```

---

## 6. Future Relationship Model

The future expanded LOOPRA model:

```text
MarketSignal
    ↓
TrendPattern
    ↓
ContentInsight
    ↓
Idea
    ↓
Scenario
    ↓
ContentItem
    ↓
Publication
    ↓
MetricSnapshot
    ↓
LearningMemory
    ↓
OptimizationAction
    ↓
Next Cycle
```

This model represents the future architecture and does not replace the
current Foundation MVP.

---

## 7. Entity Roles

### 7.1. Project context

`Project` and related project config define which project the content belongs to and keep the loop project-scoped.

### 7.2. Idea

`Idea` is the project-scoped starting point for the current loop.

### 7.3. Scenario

`Scenario` is the project-scoped content plan created from an `Idea` for the current minimal flow.

### 7.4. ContentItem

`ContentItem` is the produced content unit that moves toward export.

### 7.5. ExportPackage

`ExportPackage` is the prepared package for manual publication.

In the current MVP, `ExportPackage v1` is inspection-friendly and validation-friendly.

### 7.6. Publication

`Publication` is the manual publication record for the current MVP.

It stores publication outcome metadata such as `published_url` and `published_at` when available.

### 7.7. MetricSnapshot

`MetricSnapshot` stores the current manual metrics checkpoint for a publication.

Current foundation behavior:

- draft snapshots are created for the manual metrics path
- metrics are recorded through manual import
- `clicks` input is normalized to stored `link_clicks`
- `published_url` updates the related `Publication`
- `published_url` is not stored as a raw metric field inside snapshot metrics

---

## 8. Relationship Overview

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

## 9. Ownership Boundaries

- `Production Engine` owns `ContentItem`, technical QA result, and render output metadata.
- `Publishing Hub` owns `ExportPackage` and `Publication`.
- analytics foundation owns `MetricSnapshot`.

`RenderJob` and `OutputFile` remain part of the broader domain boundary, but they are not required prerequisites for the current minimal `text_social_post` foundation loop and should not be treated as current MVP must-haves.

---

## 10. Status Guidance

This document does not duplicate long status enumerations.

Rules:

- use the current enum values from code and tests as canonical
- do not invent guessed statuses in docs
- do not mix `ContentItem` status and `Publication` status
- do not mix analytics state with publication state

If a task needs exact status names, verify them against the current domain model and transition tests.

---

## 11. Storage And Scoping

Current foundation storage remains project-scoped.

Important rules:

- content records stay tied to project context
- runtime smoke artifacts under `storage/smoke_projects/...` are local-only
- `graphify-out/` is local generated output
- generated/runtime artifacts must not be treated as source changes

---

## 12. Current Exclusions

The current foundation baseline does not require separate active MVP entities for broader discovery, media intake, scheduling, automation, or downstream recommendation loops.

If such entities are introduced later, they must be documented as future expansion rather than retroactively treated as current foundation requirements.

---

## 13. Readiness Criteria

The current data model baseline is aligned when:

- the minimal loop entities above are the active documented baseline
- project scoping remains explicit
- `ExportPackage` and `Publication` ownership stays in `Publishing Hub`
- `MetricSnapshot` remains a manual metrics record in the current MVP
- broader future concepts do not redefine the active baseline

---

## 14. Status

Status: Active  
Version: v1.0  
Updated: 2026-07-09  
Project: LOOPRA  
Current model scope: minimal foundation entity baseline

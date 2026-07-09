# STATE.md

## LOOPRA Project State

## Current Identity

Project name:

LOOPRA

Category:

Autonomous Marketing Operating System

Previous working name:

Content Plant

The transition from Content Plant to LOOPRA changes the product
identity, not the validated technical foundation.

-----------------------------------------------------------------------

# Current Status

## Foundation MVP

Status:

READY + OPERATIONALLY VERIFIED

The foundation layer is operationally verified.

Validated principles:

-   project-agnostic architecture;
-   separation of foundation and project configuration;
-   filesystem-first approach;
-   controlled development process.

-----------------------------------------------------------------------

# Stage 1 Foundation Hardening

## Documentation Baseline

Commit:
ff6589b — docs: complete LOOPRA documentation baseline

Status:
COMPLETE

36 active documents across 9 layers catalogued in
docs/DOCUMENTATION_INDEX.md. All previous documentation warnings
(W1, W2, W5, W6, W7) resolved in the Final Architecture Audit
(docs/FINAL_ARCHITECTURE_AUDIT.md v1.0).

## Naming Cleanup

Commit:
3c6c0a6 — fix: make LOOPRA env vars primary

W3/W4 resolved:

W3 — CONTENT_PLANT_* env var naming migrated to LOOPRA_*.
W4 — Content Plant user-facing strings replaced with LOOPRA.

## Runtime / Configuration Naming

LOOPRA_* env vars are primary:

-   LOOPRA_SMOKE_PROJECT_ID
-   LOOPRA_SMOKE_PROJECTS_ROOT
-   LOOPRA_PROJECTS_ROOT

CONTENT_PLANT_* env vars remain supported as legacy fallback:

-   CONTENT_PLANT_SMOKE_PROJECT_ID
-   CONTENT_PLANT_SMOKE_PROJECTS_ROOT
-   CONTENT_PLANT_PROJECTS_ROOT

Resolution order:

LOOPRA_* → CONTENT_PLANT_* → default

## CLI Help Support

Commit:
4cec363 — feat: add help support to CLI scripts

Status:
COMPLETE

Summary:

-   --help/-h supported by all current Foundation MVP CLI scripts:
    smoke_loop.py, inspect_package.py, validate_package.py,
    find_metric_snapshots.py, import_manual_metrics.py.
-   smoke_loop.py --help is now safe and does not execute the lifecycle.
-   Help mode exits with code 0.
-   Help mode has no side effects.
-   Normal CLI output contract remains unchanged.
-   --json output mode is NOT implemented and remains a future
    Stage 1 follow-up.

Verification:

-   tests: 120/120 OK
-   smoke_loop normal mode: PASS
-   inspect_package.py: PASS
-   validate_package.py: PASS
-   working tree clean after commit

## Operational Acceptance Run

Stage 1 Foundation Hardening Operational Acceptance: PASS

Checks:

-   tests: 109/109 OK
-   smoke_loop default mode: PASS
-   smoke_loop LOOPRA_* env mode: PASS
-   smoke_loop legacy CONTENT_PLANT_* fallback mode: PASS
-   inspect_package: PASS
-   validate_package: PASS
-   git status before run: clean
-   git status after run: clean
-   tracked files changed: none

Smoke loop default verification IDs:

project_id: example
idea_id: idea_d1ff05507da5
scenario_id: scenario_5922a10836e5
content_item_id: content_0157b7417c71
export_package_id: export_72ec3675f998
publication_id: publication_76a254518fb0
metric_snapshot_id: metric_b11f310f884f

Statuses:

scenario_status=approved
content_item_status=exported
export_package_status=ready
publication_status=published
metric_snapshot_status=draft

-----------------------------------------------------------------------

# Architecture Direction

LOOPRA is evolving toward:

Brand System

↓

Growth Loop

↓

Intelligence

↓

Production

↓

Publishing

↓

Analytics

↓

Learning Memory

↓

Improved Next Cycle

-----------------------------------------------------------------------

# Completed Foundation Capabilities

Implemented:

-   domain layer;
-   lifecycle services;
-   project configuration;
-   content item flow;
-   export package generation;
-   publication records;
-   metric snapshot foundation.

Validated lifecycle:

Idea

↓

Scenario

↓

ContentItem

↓

ExportPackage

↓

Publication

↓

MetricSnapshot

-----------------------------------------------------------------------

# Current Development Phase

Phase:

Stage 1 Foundation Hardening — small bounded improvements

Current objectives:

-   optional JSON output mode design review;
-   operational docs consistency checks;
-   maintain architecture boundaries;
-   no Stage 2 until explicitly approved.

Completed in this phase:

-   documentation baseline finalized and committed;
-   naming cleanup: LOOPRA_* primary, Content Plant removed from runtime;
-   operational acceptance run passed;
-   CLI --help/-h support added to all 5 scripts. smoke_loop.py --help is
    now side-effect-free.

-----------------------------------------------------------------------

# Important Boundaries

Current phase does NOT include:

-   UI development;
-   API development;
-   database implementation;
-   authentication;
-   billing;
-   SaaS infrastructure;
-   external publishing integrations;
-   autonomous agent swarm;
-   Stage 2 Content Intelligence;
-   connector development;
-   autoposting.

These belong to future phases.

-----------------------------------------------------------------------

# LOOPRA Transition

The project has moved from:

Content Plant

"content production platform"

to:

LOOPRA

"autonomous marketing operating system".

The architecture remains based on the validated foundation.

-----------------------------------------------------------------------

# Development Rules

Always preserve:

-   project-agnostic core;
-   clear separation of layers;
-   documentation as source of truth;
-   incremental validated progress.

-----------------------------------------------------------------------

# Next Direction

Stage 1 Foundation Hardening can continue with small bounded
improvements only:

1.  Optional JSON output mode design review and implementation
    (only after explicit approval).
2.  Operational docs consistency checks.

Do not start Stage 2 (Content Intelligence) without explicit
Architecture Gate approval.

-----------------------------------------------------------------------

# Final State Statement

LOOPRA is being built as an autonomous marketing operating system that
enables brands to continuously learn, create and improve through
intelligent growth loops.

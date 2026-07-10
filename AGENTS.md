# AGENTS.md

## LOOPRA Development Instructions

## Purpose

This document defines rules for AI coding agents working on LOOPRA.

The goal is to preserve architecture integrity while allowing controlled
development.

------------------------------------------------------------------------

# 1. Project Identity

Current project name:

LOOPRA

Category:

Autonomous Marketing Operating System.

Historical name:

Content Plant.

Content Plant is no longer the active product identity.

------------------------------------------------------------------------

# 2. Architecture Source of Truth

Before making architectural decisions, agents must read:

-   docs/02_architecture/LOOPRA_ARCHITECTURE.md
-   docs/01_product/LOOPRA_BRAND_POSITIONING.md
-   docs/01_product/LOOPRA_TRANSITION_PLAN.md
-   STATE.md

For document navigation, use:

-   docs/DOCUMENTATION_INDEX.md — single navigational index for all
    active LOOPRA documentation.

These documents define:

-   current architecture;
-   project direction;
-   development boundaries.

------------------------------------------------------------------------

# 3. Core Architecture Rules

## Project Agnostic Foundation

The core system must not contain project-specific logic.

Forbidden:

-   hardcoded brands;
-   customer-specific workflows;
-   project-specific prompts in core.

Allowed:

Project-specific configuration:

projects/{project_id}/

------------------------------------------------------------------------

# 4. Development Philosophy

LOOPRA development follows:

Foundation First.

Do not implement future platform features before validating the current
layer.

Architecture evolution:

Foundation MVP

↓

Content Intelligence

↓

Production Automation

↓

Agentic Operations

↓

Marketing Operating System

↓

SaaS Platform

------------------------------------------------------------------------

# 5. Current Development Scope

Current priority:

Stage 1 Foundation Hardening — small bounded improvements only.

Foundation MVP is verified. Stage 2 Slice 1 (Content Intelligence
Foundation) and Stage 2 Slice 2 (Content Intelligence Hardening) are
implemented. No further Stage 2 slices without explicit bounded
scope/gate approval.

Allowed:

-   domain models;
-   services;
-   project configuration;
-   validation;
-   documentation;
-   operational docs consistency checks;
-   architecture boundary maintenance.

Not allowed without explicit task:

-   UI;
-   API;
-   database;
-   authentication;
-   billing;
-   SaaS infrastructure;
-   external integrations;
-   autonomous agent systems;
-   further Stage 2 slices beyond implemented Slices 1 and 2;
-   connector development;
-   autoposting.

------------------------------------------------------------------------

# 6. Agent Principles

LOOPRA uses the principle:

Agents decide.

Tools execute.

Agents must not replace deterministic infrastructure without
architectural approval.

Avoid:

-   uncontrolled agent swarm;
-   duplicated automation;
-   hidden business logic.

------------------------------------------------------------------------

# 7. Code Quality Rules

Before changes:

-   understand existing architecture;
-   inspect related modules;
-   avoid unnecessary refactoring.

After changes:

-   run tests;
-   verify scope;
-   update documentation when architecture changes.

------------------------------------------------------------------------

# 8. Coding Agent Execution Discipline

These rules adapt Karpathy-inspired coding discipline to LOOPRA's
architecture and autonomous development workflow.

## 8.1 Think Before Coding

Before implementing, an agent must study the existing code, contracts,
tests and documentation relevant to the task.

Significant assumptions must be stated explicitly.

Do not silently choose one interpretation when different
interpretations materially change architecture, public contracts, data,
security or task scope.

If a simpler and architecturally correct path exists, prefer it.

Call out contradictions between the task, code, tests and
documentation.

### Material Ambiguity

The ambiguity is material when a decision could change:

-   an architectural boundary;
-   a public API or domain contract;
-   a stored data format;
-   an irreversible migration;
-   security;
-   task scope;
-   approved product semantics.

At a material ambiguity, stop, describe the conflict precisely and
request a decision — unless the answer can be reliably obtained from
source-of-truth documents.

### Minor Ambiguity

If the ambiguity is:

-   local;
-   reversible;
-   does not change public contracts;
-   does not affect architecture or data;

choose the simplest option consistent with existing code and
documentation, continue work and record the assumption in the final
report.

## 8.2 Simplicity Within Approved Architecture

Implement the minimum required for the current task.

Forbidden:

-   future features not required by current specifications;
-   single-use abstractions without architectural justification;
-   unrequested configurability;
-   additional modes, providers, registries, factories or extension
    points without current necessity.

If the implementation is noticeably more complex than required, simplify
it before finalization.

Simplicity does not mean violating the approved architecture.

Do not remove or bypass:

-   mandatory domain boundaries;
-   approved interfaces;
-   service contracts;
-   architectural invariants;
-   separation of deterministic tools and agent/orchestrator logic;
-   requirements of source-of-truth specifications;

solely because a more monolithic implementation is shorter.

Principle:

Minimum implementation that fully satisfies the current approved
contract.

## 8.3 Surgical Changes

Change only what is necessary for the current task.

Forbidden:

-   drive-by refactoring;
-   changing adjacent code, comments, typing or formatting without
    necessity;
-   removing pre-existing dead code unless the task requires it;
-   mixing multiple independent logical changes in one diff or commit.

Required:

-   remove imports, variables, functions and other elements made unused
    by the current change;
-   follow the existing project style.

Criterion:

Every changed line must be traceable to the task, its acceptance
criteria, or cleanup directly caused by the implementation.

If a separate problem is discovered outside scope, report it in the
final output — do not fix it silently.

## 8.4 Goal-Driven Execution

Before implementing, convert the task into verifiable acceptance
criteria.

Every non-trivial step must have a verification method.

For bugs:

-   first reproduce with a test or reliable diagnostic when technically
    possible;
-   after fixing, prove the problem is eliminated.

Run existing checks to exclude regressions.

Cycle: implementation → verification → correction until criteria are
met or an objective blocker appears.

For multi-step tasks, use the format:

    Step

    Verify: specific command, test, artifact or observable result.

Forbidden criteria:

-   "make it work";
-   "improve the code";
-   "fix everything";
-   "tests look fine".

## 8.5 Autonomous Execution

An agent must not request confirmation for every reversible local
decision.

An agent must independently read related files and perform necessary
checks.

An agent must not hide doubts or blockers.

Significant decisions must be confirmed by source-of-truth
documentation.

When no material ambiguity exists, the agent continues work until the
logical block is fully completed.

This does not grant permission to expand scope without explicit
approval.

## 8.6 Session and Context Management

A single logical work block should, when practical, be executed in one
CLI session — from audit through implementation, verification, commit
and push.

The agent that implements a block should also verify and finalize it
when possible.

A new session is preferred before starting a new logical block.

A new session is also required when the context becomes too large,
contradictory or the agent stops reliably distinguishing current
decisions from historical context.

Do not start a new session immediately before verification or commit of
a nearly complete block.

Avoid uncontrolled context growth.

Use repository navigation tools, including Graphify when available and
useful, instead of re-reading large quantities of irrelevant files.

Context must remain manageable and focused on the current block.

## 8.7 Pre-Finalization Checklist

Before declaring completion, the agent must verify:

-   all acceptance criteria are met;
-   every changed line relates to the task;
-   no unrequested functionality was added;
-   no premature abstractions were introduced;
-   no unrelated files were modified;
-   code matches existing contracts;
-   documentation was updated only if architecture actually changed;
-   relevant tests pass;
-   the full test suite passes when reasonable and available;
-   `git diff --check` is clean;
-   no warnings, skipped tests or blockers are concealed;
-   the final report matches the commands actually executed.

------------------------------------------------------------------------

# 9. Documentation Rules

Documentation is part of the product architecture.

When changing architecture:

Update the relevant source-of-truth document.

Avoid:

-   duplicate specifications;
-   conflicting documents;
-   outdated active instructions.

Historical documents belong in archive.

------------------------------------------------------------------------

# 10. Repository Boundaries

Keep separation:

core/

Contains generic platform logic.

projects/

Contains project-specific configurations.

docs/

Contains architecture and specifications.

storage/

Contains runtime artifacts only.

------------------------------------------------------------------------

# 11. Communication Rules

When reporting work:

Always include:

-   files changed;
-   tests executed;
-   architectural impact;
-   remaining risks.

Do not claim completion without verification.

------------------------------------------------------------------------

# Final Rule

Build LOOPRA as an evolving autonomous marketing platform.

Do not optimize for adding features.

Optimize for maintaining a clean architecture that can grow.

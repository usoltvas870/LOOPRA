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

-   LOOPRA_ARCHITECTURE.md
-   LOOPRA_BRAND_POSITIONING.md
-   LOOPRA_TRANSITION_PLAN.md
-   STATE.md

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

Foundation MVP improvements and validation.

Allowed:

-   domain models;
-   services;
-   project configuration;
-   validation;
-   documentation.

Not allowed without explicit task:

-   UI;
-   API;
-   database;
-   authentication;
-   billing;
-   SaaS infrastructure;
-   external integrations;
-   autonomous agent systems.

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

# 8. Documentation Rules

Documentation is part of the product architecture.

When changing architecture:

Update the relevant source-of-truth document.

Avoid:

-   duplicate specifications;
-   conflicting documents;
-   outdated active instructions.

Historical documents belong in archive.

------------------------------------------------------------------------

# 9. Repository Boundaries

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

# 10. Communication Rules

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

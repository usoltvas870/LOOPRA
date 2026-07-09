# DISTRIBUTION SPEC

## Version

v1.0

## Status

Active — LOOPRA Distribution / Publishing Boundary

## Purpose

This document defines the Distribution / Publishing boundary of the LOOPRA
Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA transform a Distribution Ready ExportPackage into a
> prepared, published or publication-ready content unit with a correct
> Publication record?

DISTRIBUTION_SPEC.md is the architectural blueprint for the layer that
bridges finished production output with channel delivery and analytics
readiness.

It describes:

- the Distribution boundary and its place in the LOOPRA architecture;
- the distribution intake and package validation process;
- channel mapping and channel adaptation rules;
- publication planning and approval gates;
- the current manual publication workflow (MVP baseline);
- the Publication record, status lifecycle and attempt model;
- the analytics handoff and Learning Memory context;
- future scheduling and connector-based publication boundaries;
- error handling, preflight checks and boundary rules.

It does NOT describe:

- content creation or production (Production Pipeline);
- asset selection or management (Asset Library);
- trend analysis or opportunity discovery (Intelligence Layer);
- performance analytics interpretation (Analytics Layer);
- learning extraction algorithms (Learning Memory);
- external platform API contracts;
- UI, database schemas, authentication or billing.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

DISTRIBUTION_SPEC.md defines the Distribution Layer as the subsystem that
receives a Distribution Ready ExportPackage and transforms it into a
publication-ready or published state with a correct Publication record.

It serves as the specification for:

- how Production output enters Distribution;
- how packages are validated for publication readiness;
- how channels are mapped and adapted;
- how publication plans are formed;
- how manual publication operates in the current MVP;
- how Publication records are created and maintained;
- how Distribution prepares data for Analytics;
- what future distribution capabilities the architecture supports.

## 1.2. In Scope

- ExportPackage intake and Distribution Job creation;
- package validation for publication readiness;
- channel mapping from Project Settings to Publication Targets;
- channel adaptation rules (captions, UTM, hashtags, format);
- publication plan formation;
- human approval gates;
- manual publication workflow (current MVP);
- Publication record entity and status lifecycle;
- publication attempts and error tracking;
- preflight checks;
- Distribution error handling;
- analytics handoff;
- Learning Memory context provision;
- future scheduling and connector-based publication boundaries.

## 1.3. Out of Scope

- content creation, generation or assembly (Production Pipeline);
- asset selection or library management (Asset Library);
- production QA (Production Pipeline QA stage);
- trend analysis, market signal detection (Intelligence Layer);
- performance analytics collection or interpretation (Analytics Layer);
- learning extraction or pattern formation (Learning Memory);
- external platform API implementation;
- UI, API, database schemas, authentication or billing;
- autoposting as a current implemented function;
- social media strategy or content marketing theory.

---

# 2. Role of Distribution in LOOPRA

## 2.1. Position in the LOOPRA Architecture

The Distribution Layer occupies a defined position between Production
(content manufacturing) and Analytics (performance measurement):

```text
Intelligence Layer
    │  "What to create, why, for whom, in what format"
    ↓
Production Layer
    │  "How to manufacture the selected content"
    │  Brief → Plan → Select → Generate → Assemble → QA → Export
    ↓
Production Boundary: Distribution Ready ExportPackage
    │
Distribution Layer  ← THIS DOCUMENT
    │  "How to deliver, adapt, approve and record publication"
    │  Intake → Validate → Map → Adapt → Plan → Approve → Publish → Record
    ↓
Distribution Boundary: Publication Record → Analytics Ready
    │
Analytics Layer
    │  "What happened after publication"
    │  MetricSnapshot collection and analysis
    ↓
Learning Memory
    │  "What the system should remember for the next cycle"
```

Reference: `SYSTEM_ARCHITECTURE.md`, Sections 8–11

## 2.2. What Distribution Does

Distribution:

- receives a Distribution Ready ExportPackage from the Production Pipeline;
- validates that the package is genuinely ready for publication;
- maps target channels from the Production Brief against Project Settings;
- adapts content for each target channel (captions, UTM, hashtags, formatting);
- creates a Publication Plan — the structured intent to publish;
- enforces approval gates according to the project's autonomy mode;
- provides a manual publication checklist for human execution (current MVP);
- records the fact of publication in a Publication record;
- prepares publication context for Analytics Layer handoff;
- captures errors, attempts and status transitions throughout.

## 2.3. What Distribution Does NOT Do

Distribution does NOT:

- decide what content to create (Intelligence Layer);
- produce content, generate copy or assemble media (Production Pipeline);
- select assets from the Asset Library (Production Pipeline Asset Selection);
- run production QA checks (Production Pipeline QA stage);
- collect or analyze performance metrics (Analytics Layer);
- extract learning patterns from results (Learning Memory);
- modify the Brand System, Project Settings or channel configuration;
- override strategic decisions made by the Intelligence Layer.

## 2.4. Distribution Answers

Distribution answers operational delivery questions:

- Is this package ready to publish?
- Which channels should receive this content?
- Has the content been adapted correctly for each channel?
- Does a human need to approve before publishing?
- What steps must a human follow to publish manually?
- Was the content published? When? Where? With what result?
- What context should Analytics receive for measurement?

---

# 3. Relationship to Foundation MVP

## 3.1. The Foundation MVP Chain Preserved

The Foundation MVP defines a validated, operational entity chain:

```text
Project
    ↓
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
```

Reference: `DATA_MODEL.md`, Section 3; `PIPELINES_SPEC.md`, Section 2

This chain is the reliable execution backbone of LOOPRA. The Distribution
Spec elaborates on the section between ExportPackage and Publication,
and the handoff from Publication toward MetricSnapshot readiness.

## 3.2. What Distribution Spec Elaborates

The Distribution Spec provides an expanded, detailed view of:

```text
Foundation MVP:
    ExportPackage → Publication

Distribution Spec (detailed):
    ExportPackage (Distribution Ready)
        ↓
    Distribution Intake
        ↓
    Package Validation
        ↓
    Channel Mapping
        ↓
    Channel Adaptation
        ↓
    Publication Plan
        ↓
    Approval Gate
        ↓
    Publication Execution (manual in current MVP)
        ↓
    Publication Record
        ↓
    Analytics Ready
```

The Foundation MVP entities (`ExportPackage`, `Publication`) remain in
place. The Distribution Spec explains what happens between and around
these entities without changing their identity or role.

## 3.3. Current MVP: Manual Publication Only

In the current Foundation MVP:

- publication is manual — a human posts content outside the system;
- LOOPRA prepares the ExportPackage and a manual publication checklist;
- the human records the publication outcome (URL, timestamp, platform, status);
- a Publication record is created or updated with this data;
- MetricSnapshot is created later in the Analytics Layer.

Autoposting, scheduling and connector-based publishing are future
capabilities. They are described in this document as architectural
direction, not as current implemented features.

## 3.4. What Does NOT Change

The Distribution Spec does NOT:

- modify the `ExportPackage` entity or its structure;
- modify the `Publication` entity's core identity (it extends conceptually);
- modify the `MetricSnapshot` entity;
- change the existing Foundation MVP lifecycle;
- require new database schemas or migrations;
- alter the smoke loop, inspect_package.py or validate_package.py.

It adds conceptual depth to the distribution process that will guide
future implementation, without requiring changes to the validated
current baseline.

---

# 4. Relationship to Production Pipeline

## 4.1. The Hard Boundary

Production and Distribution have a strictly defined boundary:

```text
Production Pipeline ends at:      Distribution Ready ExportPackage

Distribution begins with:         Distribution Intake
```

The Production Pipeline delivers:

- content files (text, images, video — per content type);
- media files;
- captions (per-channel caption variants);
- hashtags;
- metadata.json (content context, references, timestamps);
- manifest.json (file listing and structure);
- qa_report (QA outcomes, warnings);
- production_snapshot (production context for traceability);
- publication checklist draft (if the Production Pipeline generates one);
- channel-specific folders (organized per target channel).

Reference: `PRODUCTION_PIPELINE_SPEC.md`, Section 11

## 4.2. What Distribution Checks

Distribution validates the ExportPackage for publication readiness but
does NOT re-assemble production output.

Distribution checks:

- the package exists and is complete;
- the package status is Distribution Ready;
- the manifest is present and valid;
- metadata references are correct;
- required files exist for each target channel;
- QA outcome is acceptable (passed or warnings acceptable);
- no blocking production issues remain.

## 4.3. What Distribution Does NOT Re-Do

Distribution does NOT:

- re-generate content, captions or media;
- re-run production QA;
- re-select or change assets;
- modify the core content message or brand layer;
- alter the content type or format.

If a package fails Distribution validation, it is returned to Production
or flagged for human review. Distribution does not fix production output.

## 4.4. Production Snapshot Handoff

The Production Pipeline includes a `production_snapshot` in the
ExportPackage. This snapshot contains:

- Production Brief reference;
- generation context (model, parameters, prompts);
- asset selection records (which assets were used and why);
- QA report with all check results;
- content type and variant used;
- timestamps for each production stage.

Distribution preserves this snapshot and includes it in the analytics
handoff. This enables Learning Memory to correlate production decisions
with publication outcomes.

---

# 5. Relationship to Project Settings and Channels

## 5.1. Distribution Uses Project Settings

Distribution reads Project Settings to determine how and where to
publish:

| Project Setting | Distribution Use |
|---|---|
| `channels` (enabled platforms) | Determines which channels are valid targets |
| `channel.account_reference` | Identifies the platform account for publication |
| `channel.publishing_rules` | Channel constraints (max length, aspect ratio, format) |
| `channel.caption_rules` | How captions should be formatted per channel |
| `channel.hashtag_rules` | Hashtag strategy per channel |
| `channel.cta_rules` | CTA constraints per channel |
| `channel.schedule_preferences` | Preferred days and times (future scheduling) |
| `utm` configuration | UTM parameter templates for link generation |
| `default_export_path` | Where export packages are located |
| `autonomy_mode` | Whether human approval is required |
| `content_types` (enabled types) | Whether the content type is valid for the project |

Reference: `PROJECT_SETTINGS_SPEC.md`, Sections 5, 7, 8

## 5.2. No Hardcoded Platform Logic

Distribution must not hardcode platform-specific logic into the platform
core. Channel behaviour is defined through Project Settings configuration.

```text
CORRECT:   Distribution reads channel rules from Project Settings
           and applies them generically.

INCORRECT: Distribution contains hardcoded Instagram logic,
           TikTok logic or LinkedIn logic.
```

Each project defines its own channels with their own rules. Distribution
is the execution layer — it applies the rules, it does not define them.

## 5.3. Channel Configuration Drives Distribution

Channel configuration determines:

- which channels receive content (only enabled channels);
- what format constraints apply (character limits, aspect ratios, duration);
- what caption format is used (tone, hashtag count, CTA placement);
- what UTM parameters are applied;
- whether manual or future connector publishing applies;
- whether approval is required for that channel.

---

# 6. Distribution Modes

## 6.1. Mode Overview

LOOPRA supports a progression of distribution modes. The current
Foundation MVP implements Manual Mode only. Other modes are future
architecture direction.

| Mode | Current Status | Description |
|---|---|---|
| Manual | Current MVP | Human publishes manually using system checklist |
| Assisted | Future | System prepares drafts; human reviews and approves |
| Scheduled | Future | System plans publication time; human or connector executes |
| Connector / Autopost | Future | System dispatches via platform connector after approval |

## 6.2. Manual Mode — Current MVP

In Manual Mode:

- the system prepares the ExportPackage (Production Pipeline);
- the system generates a manual publication checklist;
- the human opens the target platform;
- the human copies the caption and uploads media;
- the human publishes the content;
- the human records the publication URL, timestamp and status;
- the system creates or updates the Publication record.

This is the only mode active in the current Foundation MVP. All other
modes are architectural direction for future phases.

## 6.3. Assisted Mode — Future

In Assisted Mode:

- the system prepares channel-specific publication drafts;
- the system generates a structured Publication Plan;
- the human reviews drafts and approves or requests changes;
- the human executes publication manually or triggers connector dispatch;
- the system records the outcome.

Assisted Mode adds structured planning and drafts but retains human
execution for publication.

## 6.4. Scheduled Mode — Future

In Scheduled Mode:

- the system plans publication date and time per channel;
- the Publication Plan includes `scheduled_at` with timezone;
- the package waits until the scheduled time;
- at the scheduled time, the human or connector publishes;
- the system records the actual publication time against the schedule.

Scheduling is a future capability. It does not imply autoposting — a
scheduled publication may still require manual execution if no connector
is configured.

## 6.5. Connector / Autopost Mode — Future

In Connector Mode:

- the system uses a platform-specific connector;
- the connector authenticates with the external platform;
- the connector uploads media and submits the caption;
- the connector receives a platform response (post ID, URL, status);
- the system records the connector result in the Publication record;
- approval rules are never bypassed — connectors only execute after
  explicit approval (or autopilot permission in future).

Connector-based publishing requires:

- explicit Project Settings enabling;
- a configured and tested platform connector;
- defined approval rules;
- error handling for connector failures;
- audit trail of all connector actions.

Do not implement connector-based publishing as current functionality.

---

# 7. Distribution Pipeline Overview

## 7.1. Current MVP Pipeline (Manual)

```text
Distribution Ready ExportPackage
    ↓
Distribution Intake
    ↓
Package Validation
    ↓
Channel Mapping
    ↓
Channel Adaptation
    ↓
Publication Plan
    ↓
Approval Gate
    ↓
Manual Publication Checklist
    ↓
Human Publishes Externally
    ↓
Human Records Publication Result
    ↓
Publication Record Created/Updated
    ↓
Analytics Ready
```

## 7.2. Future Pipeline Extension

```text
Publication Plan
    ↓
Scheduled Publication (future)
    ↓
Connector Dispatch (future)
    ↓
Publication Confirmation (future)
    ↓
Publication Record
    ↓
Analytics Ready
```

## 7.3. Stage-by-Stage Summary

| Stage | Purpose | Owner |
|---|---|---|
| Distribution Intake | Receive and register the ExportPackage for distribution | Distribution |
| Package Validation | Verify the package is genuinely ready for publication | Distribution |
| Channel Mapping | Determine which channels to publish to | Distribution |
| Channel Adaptation | Adapt content per channel without changing core message | Distribution |
| Publication Plan | Create a structured plan for publication | Distribution |
| Approval Gate | Enforce human approval according to autonomy mode | Distribution + Human |
| Publication Execution | Publish content (manual in MVP; connector in future) | Human (MVP) / Connector (future) |
| Publication Record | Record the fact of publication | Distribution |
| Analytics Ready | Prepare context for Analytics Layer handoff | Distribution |

---

# 8. Distribution Intake

## 8.1. Purpose

Distribution Intake is the entry point where a Distribution Ready
ExportPackage is received and registered for the distribution process.
It creates a Distribution Job that tracks the package through the
distribution pipeline.

## 8.2. Intake Inputs

| Input | Source | Required |
|---|---|---|
| `export_package_id` | Production Pipeline | Yes |
| `project_id` | Production Pipeline / metadata | Yes |
| `content_item_id` | Production Pipeline / metadata | Yes |
| `target_channels` | Production Brief / metadata | Yes |
| `export_package_path` | Production Pipeline output | Yes |
| `metadata.json` | ExportPackage | Yes |
| `manifest.json` | ExportPackage | Yes |
| `qa_report` | ExportPackage (Production QA stage) | Yes |
| `production_snapshot` | ExportPackage | Yes |
| `publication_checklist` | ExportPackage (if present) | No |

## 8.3. Intake Process

```text
ExportPackage arrives at Distribution boundary
    ↓
Distribution reads package metadata and manifest
    ↓
Distribution creates a DistributionJob
    ↓
Distribution validates basic package integrity:
    - package exists at export_package_path
    - package status is Distribution Ready
    - manifest.json exists and is parseable
    - metadata.json exists and is parseable
    - QA report exists and outcome is acceptable
    - target_channels list is not empty
    ↓
If basic checks pass:
    → DistributionJob status = intake_complete
    → proceed to Package Validation
If basic checks fail:
    → DistributionJob status = intake_failed
    → error recorded with reason
    → returned to Production or flagged for human review
```

## 8.4. Intake Outputs

| Output | Description |
|---|---|
| `DistributionJob` | The tracking entity for this distribution run |
| `intake_validation_result` | pass / fail with reasons |
| `channel_list` | Validated list of target channels |
| `initial_publication_plan_draft` | Empty plan structure for population in later stages |

## 8.5. DistributionJob Entity (Conceptual)

```text
DistributionJob:
    distribution_job_id       — unique identifier
    project_id                — project scope
    content_item_id           — the content being distributed
    export_package_id         — the package to distribute
    status                    — intake_complete, validating, ready, in_progress,
                                published, partially_published, failed, cancelled
    target_channels           — list of target channel identifiers
    created_at                — intake timestamp
    completed_at              — when distribution completed (all channels)
    error_code                — populated if distribution fails
    error_message             — human-readable error
```

---

# 9. Package Validation

## 9.1. Purpose

Package Validation verifies that the ExportPackage is genuinely ready for
publication. This is a distribution-readiness check — not a replacement
for Production QA.

## 9.2. Validation Checks

### 9.2.1. Manifest Completeness

- `manifest.json` is present and parseable;
- all files listed in the manifest exist at the specified paths;
- no files referenced in manifest are missing from the package.

### 9.2.2. Required Files Exist

For each target channel, the package must contain:

- channel-specific caption file (`caption_{platform}.txt`);
- channel-specific media files (if applicable for the content type);
- channel-specific folders (if `channel_specific_folders` was enabled in the Brief).

### 9.2.3. Captions for Target Channels

- a caption file exists for every channel in `target_channels`;
- caption file is non-empty;
- caption length is within the channel's character limit (from Project Settings).

### 9.2.4. Media Files Match Target Channels

- for visual content: slide images exist and match channel aspect ratios;
- for video content: video file exists and matches channel resolution/duration;
- file formats are compatible with the target platform.

### 9.2.5. QA Report Acceptability

- `qa_report` exists and is parseable;
- overall QA outcome is `pass` or `pass_with_warnings`;
- if QA outcome is `pass_with_warnings`, warnings are reviewed and determined
  to be non-blocking for publication;
- if QA outcome is `fail` or `changes_required`, publication is blocked.

### 9.2.6. Metadata References Correct

- `metadata.json` references the correct `project_id`;
- `metadata.json` references the correct `content_item_id`;
- `metadata.json` references the correct `export_package_id`;
- `metadata.json` content type matches what is in the package.

### 9.2.7. Package Not Stale

- the package was recently created (not an old abandoned package);
- the content has not been superseded by a newer version;
- the package references the current active Brand System version (if tracked).

### 9.2.8. No Blocking Warnings

- no QA warning is classified as blocking for publication;
- no missing critical file;
- no metadata inconsistency that would prevent correct publication recording.

### 9.2.9. Publication Checklist Present

- a publication checklist file exists OR can be generated by Distribution;
- the checklist covers all target channels.

## 9.3. Validation Outcomes

| Outcome | Meaning | Action |
|---|---|---|
| `valid` | All checks passed. Package is publication-ready. | Proceed to Channel Mapping |
| `valid_with_warnings` | Non-blocking issues found. Publication may proceed. | Proceed with warnings recorded in Distribution Job |
| `blocked` | Blocking issue found. Cannot publish. | Distribution stops. Error recorded. |
| `needs_production_revision` | Issue requires rework in the Production Pipeline. | Package returned to Production with specific issues |
| `needs_human_review` | Issue requires human judgment. | Distribution pauses; human operator notified |

## 9.4. Validation Is Not Production QA

Distribution validation is fundamentally different from Production QA:

```text
Production QA checks:                  Distribution Validation checks:
  - Is the content correct?              - Is the package complete?
  - Does the content match the Brief?    - Are all files present?
  - Is the brand voice consistent?       - Is the QA outcome acceptable?
  - Are restrictions respected?          - Are metadata references correct?
  - Is the format specification met?     - Are channel files present?
  - Is the technical output valid?       - Is the package publishable?
```

Production QA validates the content. Distribution validation validates
publication readiness. Both are required; neither replaces the other.

---

# 10. Channel Mapping

## 10.1. Purpose

Channel Mapping determines which channels the content will be published
to and creates a ChannelPublicationTarget for each.

## 10.2. Mapping Inputs

| Input | Source |
|---|---|
| `target_channels` | Production Brief / package metadata |
| `enabled_channels` | Project Settings |
| `channel_configurations` | Project Settings (per-channel rules) |
| `content_type` | Package metadata |
| `content_type_configuration` | Project Settings (enabled content types per channel) |

## 10.3. Mapping Process

```text
For each channel in target_channels:
    ↓
Check: Is the channel enabled in Project Settings?
    → NO  → Channel is blocked. Error: target_channel_disabled.
    → YES → Continue.
    ↓
Check: Does the channel support this content type?
    → NO  → Channel is blocked. Error: unsupported_content_type_for_channel.
    → YES → Continue.
    ↓
Check: Does the channel have an account reference configured?
    → NO  → Channel is blocked. Error: channel_account_not_configured.
    → YES → Continue.
    ↓
Check: What publication mode is configured for this channel?
    → manual (current MVP)  → proceed with manual mapping.
    → connector (future)    → would proceed with connector mapping.
    ↓
Create: ChannelPublicationTarget for this channel.
```

## 10.4. ChannelPublicationTarget Entity (Conceptual)

```text
ChannelPublicationTarget:
    channel_target_id          — unique identifier for this mapping
    distribution_job_id        — parent Distribution Job
    channel_id                 — channel reference from Project Settings
    platform                   — platform identifier (telegram, instagram, linkedin, etc.)
    account_reference          — platform account identifier or URL
    publication_mode           — manual (MVP), connector_future, scheduled_future
    content_type_supported     — true if channel supports this content type
    required_files             — list of files from package needed for this channel
    caption_source             — path to the caption file for this channel
    media_source               — path to media files for this channel
    link_strategy              — how links/UTM should be applied for this channel
    approval_required          — whether human approval is required for this channel
    channel_constraints        — platform constraints (max length, aspect ratio, duration)
```

## 10.5. Mapping Rules

- If no target channels map successfully, the Distribution Job fails with
  `no_valid_channels`.
- If some channels map and some are blocked, the valid channels proceed;
  blocked channels are recorded as errors.
- If a channel is not enabled in Project Settings but appears in
  `target_channels`, Distribution blocks that channel — it does not
  silently enable it.

---

# 11. Channel Adaptation

## 11.1. Purpose

Channel Adaptation prepares content for each target channel without
returning to the Production Pipeline or modifying core content.

## 11.2. Allowed Adaptation

Distribution may perform these adaptations:

### 11.2.1. Caption Selection

- select the correct caption file for the channel (`caption_{platform}.txt`);
- verify caption length fits channel limits;
- normalize line breaks for the platform (CRLF, LF, platform-specific);
- generate copyable text block suitable for manual posting.

### 11.2.2. UTM Link Application

- take the base URL from Project Settings or Brand System;
- apply UTM parameters from Project Settings UTM configuration;
- create channel-specific final URLs;
- include the final URL in the caption and publication checklist.

### 11.2.3. Hashtag Selection

- select channel-specific hashtags from the package or generate from rules;
- ensure hashtag count respects channel rules (e.g. 3–5 for LinkedIn, 5–15 for Instagram);
- format hashtags per platform convention.

### 11.2.4. Media Selection

- select the correct media file for the channel from the package;
- if multiple resolutions exist, select the channel-appropriate version;
- verify media file format is compatible with the channel.

### 11.2.5. Manual Posting Instructions

- generate step-by-step manual posting instructions per channel;
- include: login, navigate to post creation, paste caption, upload media,
  set any options, publish, record URL;
- make instructions human-readable and actionable.

### 11.2.6. Platform-Specific Copy Block

- assemble the final copy block for each channel:
  caption text + hashtags + UTM link (if applicable);
- format as a ready-to-copy text block;
- include any platform-specific notes (e.g. "first comment for hashtags").

## 11.3. Forbidden Adaptation

Distribution must NOT perform these adaptations without returning to
the Production Pipeline:

- rewrite the core message or key value proposition;
- change visual output (different images, altered video);
- change the brand layer (different logo, colors, branding);
- change the key CTA strategy (different CTA type or placement);
- replace assets with different assets;
- alter the content type (turn a carousel into a video);
- modify the content angle or tone of voice.

If such modifications are needed:

```text
Distribution returns the package to Production (or Orchestrator)
with a requested change specification:

    requested_change:
        reason: "Caption too long for channel constraint"
        current: "caption exceeds 2200 character limit by 400 characters"
        request: "generate shortened caption variant"
        channel: "instagram"
        severity: "blocking"
```

Distribution does not fix production output. It identifies the need and
routes back to the appropriate layer.

## 11.4. ChannelPublicationDraft Entity (Conceptual)

```text
ChannelPublicationDraft:
    draft_id                   — unique identifier
    publication_plan_id        — parent Publication Plan
    channel_id                 — target channel
    platform                   — platform identifier
    caption_text               — final adapted caption
    hashtags                   — final hashtag list
    media_files                — paths to selected media files
    thumbnail                  — path to thumbnail (video content)
    subtitles                  — path to subtitle file (video content)
    links                      — final URLs with UTM applied
    checklist_steps            — generated manual posting steps
    warnings                   — any adaptation warnings
    ready_for_manual_publish   — true when draft is complete
    ready_for_connector_publish — true when draft is connector-ready (future)
```

---

# 12. Publication Plan

## 12.1. Purpose

The Publication Plan is the structured intent to publish. It describes
what will be published, where, when, how and by whom. It is formed after
channel mapping and adaptation are complete.

The Publication Plan is NOT the Publication record. The Plan expresses
intent. The Publication record expresses fact.

## 12.2. PublicationPlan Entity (Conceptual)

```text
PublicationPlan:
    publication_plan_id        — unique identifier
    project_id                 — project scope
    content_item_id            — the content to publish
    export_package_id          — the package source
    distribution_job_id        — parent Distribution Job

    target_channels            — list of channels to publish to
    planned_publication_time   — intended publication time (optional in MVP,
                                  required for future scheduling)
    publication_mode           — manual (MVP), assisted, scheduled, connector

    approval_required          — whether human approval is required
    approval_status            — pending, approved, rejected, changes_requested,
                                  skipped, expired

    channel_publication_targets — list of ChannelPublicationTarget references
    channel_drafts              — list of ChannelPublicationDraft references

    publication_assets         — list of asset files used for publication
    captions                   — list of caption file references per channel
    links                      — list of final URLs per channel
    UTM_parameters             — applied UTM parameters

    checklist_generated        — whether the manual checklist has been generated
    checklist                  — reference to PublicationChecklist

    status                     — draft, awaiting_approval, approved,
                                  ready_to_publish, publishing, published,
                                  partially_published, failed, cancelled

    created_at                 — when the plan was created
    updated_at                 — last modification timestamp
```

## 12.3. Plan vs Publication

```text
PublicationPlan:
    "We intend to publish this content to LinkedIn and Telegram
     tomorrow at 10:00 MSK. The captions are ready. Approval is
     pending."

Publication:
    "Content was published to LinkedIn on 2026-07-09 at 10:15 MSK.
     Published URL: https://linkedin.com/posts/...
     Status: published."
```

The Plan is the instruction set. The Publication is the outcome record.
A single PublicationPlan may produce multiple Publication records
(one per channel).

---

# 13. Approval Gate

## 13.1. Purpose

The Approval Gate enforces human review requirements based on the
project's autonomy mode, channel configuration and content sensitivity.

Distribution never bypasses approval rules. Even in future autopilot
mode, blocking issues always escalate.

## 13.2. Approval Requirements by Autonomy Mode

### 13.2.1. Copilot Mode (Current MVP Default)

- every publication requires human approval;
- the human reviews the Publication Plan, drafts and checklist;
- the human explicitly approves before the checklist is finalized;
- no publication can proceed without approval.

### 13.2.2. Assisted Mode (Future)

- routine channels with low-risk content may proceed to checklist
  without explicit approval;
- new channels, first-time content types or channels with warnings
  require approval;
- paid channels or sensitive content always require approval;
- connector-based publishing requires approval.

### 13.2.3. Autopilot Mode (Future)

- publication can proceed without approval only if explicitly enabled
  in Project Settings for that channel and content type;
- blocking errors always escalate to human;
- sensitive content always escalates if configured;
- human retains emergency stop and can reduce autonomy at any time.

## 13.3. ApprovalRecord Entity (Conceptual)

```text
ApprovalRecord:
    approval_id                — unique identifier
    publication_plan_id        — the plan being approved
    project_id                 — project scope
    approver                   — human operator identifier (or "system" if auto)
    approval_type              — publication, channel, content
    decision                   — approved, rejected, changes_requested, skipped
    reason                     — reason for rejection or changes requested
    requested_changes          — specific changes requested
    approved_at                — timestamp of decision
    expires_at                 — approval validity period (if applicable)
    autonomy_mode_at_approval  — snapshot of autonomy mode at time of approval
```

## 13.4. Approval Outcomes

| Outcome | Meaning | Distribution Action |
|---|---|---|
| `approved` | Human approves publication | Proceed to checklist / execution |
| `rejected` | Human rejects publication | Distribution stops. Plan status = rejected. Record reason. |
| `changes_requested` | Human requests modifications | Package may return to Production or human adjusts. Plan paused. |
| `skipped` | Approval not required (future assisted/autopilot) | Proceed to execution. Recorded for audit. |
| `expired` | Approval window passed without decision | Plan status = expired. Re-approval required. |

## 13.5. Human Retains Final Authority

Regardless of autonomy mode:

- the human can stop any publication at any point;
- the human can reduce autonomy from autopilot to assisted to copilot;
- the human can modify approval rules;
- every approval decision is recorded for audit;
- rejection reasons are preserved for Learning Memory.

---

# 14. Manual Publication Workflow — Current MVP

## 14.1. The Current MVP Flow

```text
ExportPackage Distribution Ready
    ↓
Distribution Intake and Validation
    ↓
Channel Mapping and Adaptation
    ↓
Publication Plan Created
    ↓
Approval (copilot mode: required)
    ↓
Manual Publication Checklist Generated
    ↓
Human Opens Target Platform
    ↓
Human Copies Caption from Checklist
    ↓
Human Uploads Media (if applicable)
    ↓
Human Adds Hashtags and UTM Link
    ↓
Human Publishes Content
    ↓
Human Records:
    - platform
    - publication URL
    - publication timestamp
    - status (published, failed, error)
    - notes (any observations, errors)
    ↓
System Creates/Updates Publication Record
    ↓
Analytics Ready Handoff
```

## 14.2. Manual Publication Checklist

The checklist is the primary output of Distribution in the current MVP.
It provides everything a human needs to publish content manually.

### 14.2.1. Checklist Contents

For each target channel, the checklist includes:

```text
CHANNEL: [Platform Name] — [Account Reference]
─────────────────────────────────────────────

1. OPEN PLATFORM
   - Go to: [platform URL or app]
   - Log in to: [account name]
   - Navigate to: [post / reel / story creation]

2. CAPTION TEXT (copy exactly)
   ┌─────────────────────────────────────────┐
   │ [Full caption text]                     │
   │                                         │
   │ [Caption paragraph 2]                   │
   │                                         │
   │ [CTA text]                              │
   └─────────────────────────────────────────┘

3. HASHTAGS (add after caption or in first comment)
   #tag1 #tag2 #tag3 ...

4. MEDIA FILES
   - File: [path/to/image_or_video]
   - Thumbnail: [path/to/thumbnail] (if video)

5. LINKS
   - Use: [final URL with UTM parameters]

6. PLATFORM-SPECIFIC NOTES
   - [Any special instructions for this platform]

7. AFTER PUBLISHING — RECORD:
   - Platform: [platform name]
   - Publication URL: [________________]
   - Published at: [____-__-__ __:__ UTC]
   - Status: [ ] Published successfully
             [ ] Published with issues
             [ ] Failed to publish
   - Notes: [____________________________]

8. METRIC SNAPSHOT REMINDER
   - Return to this post in [X days] to record metrics.
   - Use the manual metrics import tool.
```

### 14.2.2. PublicationChecklist Entity (Conceptual)

```text
PublicationChecklist:
    checklist_id               — unique identifier
    publication_plan_id        — parent Publication Plan
    channel_id                 — target channel
    steps                      — list of step objects
    caption_file               — path to caption file
    media_files                — list of media file paths
    links                      — list of final URLs
    completion_status          — pending, in_progress, completed
    completed_by               — human operator identifier
    completed_at               — when checklist was marked complete
    publication_url_captured   — whether the URL was recorded after publishing
```

## 14.3. What the Human Does After Publishing

After publishing, the human records:

| Field | Required | Description |
|---|---|---|
| `platform` | Yes | Which platform was published to |
| `publication_url` | Yes | The URL of the published post |
| `published_at` | Yes | The date and time of publication |
| `status` | Yes | published, published_with_issues, failed |
| `platform_post_id` | No | Platform-native post identifier (if available) |
| `notes` | No | Any observations, errors, anomalies |
| `error_code` | Conditional | If publication failed, what error occurred |

The system uses this data to create or update the Publication record.

---

# 15. Future Scheduled Publication

## 15.1. Concept (Future)

Scheduled Publication extends the Publication Plan with a planned
execution time. The system prepares everything in advance and triggers
publication at the scheduled moment.

## 15.2. Scheduling Fields (Future)

```text
PublicationPlan (extended for scheduling):
    scheduled_at               — planned publication datetime with timezone
    scheduling_reason          — why this time was chosen
    schedule_source            — learning_memory, project_settings, manual
    schedule_confidence        — confidence score for this time choice
    approval_deadline          — when approval must be completed by
    execution_deadline         — latest acceptable publication time
    schedule_status            — pending, approaching, due, overdue, executed, missed
```

## 15.3. Important Constraints

- Scheduling is a future capability. Do not implement as current.
- Scheduling does not equal autoposting. A scheduled publication may
  notify a human to publish manually.
- Scheduling requires a configured timezone in Project Settings.
- Scheduling without a connector means "notify human at scheduled time."
- Scheduling with a connector means "dispatch via connector at scheduled
  time" — but only after explicit approval.

---

# 16. Future Connector-Based Publication

## 16.1. Concept (Future)

A Connector is a platform-specific module that can interact with an
external publishing platform's API to upload content and record the
result.

## 16.2. Connector Responsibilities (Future)

A connector:

- receives a prepared ChannelPublicationDraft;
- authenticates with the external platform using configured credentials;
- uploads media files to the platform;
- submits the caption, hashtags and links;
- receives the platform response (post ID, URL, status);
- returns the result to Distribution for recording.

## 16.3. LOOPRA Responsibilities (Future)

LOOPRA:

- prepares validated content through the Production Pipeline;
- validates publication readiness through Distribution;
- calls the connector only when:
  - the connector is configured and tested for the target channel;
  - approval has been obtained (unless autopilot mode allows);
  - the preflight checks have passed.
- records the connector result in the Publication record;
- handles connector errors with retry or escalation logic;
- never bypasses approval rules for connector publication.

## 16.4. What This Document Does NOT Define

- specific platform API endpoints;
- authentication mechanisms for external platforms;
- connector implementation code;
- rate limiting or API quota management;
- platform-specific media upload specifications.

These belong to future implementation specifications, not to the
architectural boundary definition.

---

# 17. Publication Record

## 17.1. Definition

The Publication record is a Foundation MVP entity that captures the fact
of publication — where content was published, when, by whom and with
what result.

Reference: `DATA_MODEL.md`, Section 7.6

## 17.2. Publication Entity Fields (Conceptual Extension)

```text
Publication:
    publication_id             — unique identifier
    project_id                 — project scope
    content_item_id            — the published content
    export_package_id          — the package that was published
    publication_plan_id        — the plan this publication executed (future)
    channel_id                 — the channel published to
    platform                   — platform identifier (telegram, instagram, etc.)
    account_reference          — platform account identifier

    publication_mode           — manual (MVP), connector, scheduled
    planned_at                 — when publication was planned (from Plan, future)
    published_at               — actual publication timestamp

    status                     — draft, ready, published, failed, cancelled, archived

    publication_url            — URL of the published post
    platform_post_id           — platform-native post identifier (if available)

    manual_operator            — human who published (MVP)
    connector_id               — connector used (future)

    error_code                 — populated if publication failed
    error_message              — human-readable error description
    notes                      — operator notes

    analytics_ready            — whether Analytics has been notified/context provided
    analytics_handoff_at       — when analytics context was provided

    production_snapshot_ref    — reference to production snapshot for traceability

    created_at                 — record creation timestamp
    updated_at                 — last modification timestamp
```

## 17.3. Publication and ExportPackage

Publication references the ExportPackage it was created from. This
ensures traceability:

```text
ExportPackage → Publication → MetricSnapshot
```

From Publication, the system can trace back to the exact content
version, production context and assets that were used.

## 17.4. One Package, Multiple Publications

A single ExportPackage may produce multiple Publication records — one per
target channel:

```text
ExportPackage (content_042)
    ├── Publication: LinkedIn (published, 2026-07-09)
    ├── Publication: Telegram (published, 2026-07-09)
    └── Publication: Instagram (failed, 2026-07-09)
```

Each Publication is independent. One channel failure does not block
other channels.

---

# 18. Publication Status Lifecycle

## 18.1. Conceptual Status Flow

```text
draft
    │  Publication record created, not yet planned or executed
    ↓
ready
    │  Publication is prepared and ready for execution
    ↓
scheduled
    │  Publication is scheduled for a future time (future capability)
    ↓
awaiting_approval
    │  Publication plan requires human approval
    ↓
approved
    │  Human has approved; publication may proceed
    ↓
ready_to_publish
    │  All checks passed; awaiting manual or connector action
    ↓
manual_action_required
    │  Human must manually publish (current MVP state)
    ↓
publishing
    │  Publication is in progress (connector dispatching, human executing)
    ↓
published
    │  Publication completed successfully; URL recorded
    ↓
analytics_ready
    │  Publication context has been handed to Analytics Layer
    ↓
archived
    │  Publication retained for history; no longer active
    │
    ├── failed
    │     Publication attempt resulted in failure
    │
    └── cancelled
          Publication was cancelled before execution
```

## 18.2. Status Transition Rules

```text
draft → ready:
    Publication record linked to valid ExportPackage and ContentItem.

ready → awaiting_approval:
    Approval is required for this channel/autonomy mode.

awaiting_approval → approved:
    Human has approved.

awaiting_approval → cancelled:
    Human rejected; publication cancelled.

approved → ready_to_publish:
    All preflight checks passed.

ready_to_publish → manual_action_required:
    Manual publication mode. Human must execute.

ready_to_publish → publishing:
    Connector or human executing publication (future).

publishing → published:
    Publication completed; URL and timestamp recorded.

publishing → failed:
    Publication failed; error details recorded.

published → analytics_ready:
    Analytics handoff completed.

published → archived:
    Publication record archived for history.

any → failed:
    Error occurred at any stage.

any → cancelled:
    Operator cancelled the publication.
```

## 18.3. Current MVP Status Subset

In the current MVP, the following statuses are actively used:

```text
draft → ready → published → archived
                ↓
              failed
```

Additional statuses (`awaiting_approval`, `scheduled`, `publishing`,
`analytics_ready`) are architectural direction for future phases.

---

# 19. Publication Attempts

## 19.1. Purpose

PublicationAttempt records each try to publish content. A single
Publication may have multiple attempts if the first attempt fails.

PublicationAttempt provides an audit trail and enables error analysis.

## 19.2. PublicationAttempt Entity (Conceptual)

```text
PublicationAttempt:
    attempt_id                 — unique identifier
    publication_id             — parent Publication record
    attempt_number             — which attempt this is (1, 2, 3...)
    attempted_at               — when the attempt was made
    attempted_by               — human operator or connector/system identifier
    mode                       — manual, connector
    status                     — in_progress, succeeded, failed, cancelled
    error_code                 — error code if failed
    error_message              — human-readable error description
    platform_response          — raw platform response (if connector)
    resulting_url              — URL if publication succeeded
    platform_post_id           — platform post ID if returned
    retry_allowed              — whether another attempt is permitted
    retry_recommendation       — recommended action before retry
    notes                      — operator observations
```

## 19.3. Attempt Rules

- Maximum retry attempts per Publication may be configured in Project
  Settings (default: 3).
- Each failed attempt must be logged with error details.
- After maximum retries, the Publication status transitions to `failed`.
- Manual attempts are recorded with the `manual_operator` identifier.
- Connector attempts (future) are recorded with the `connector_id`.
- A successful attempt transitions the Publication to `published`.

---

# 20. Channel-Specific Drafts

## 20.1. Purpose

The ChannelPublicationDraft is a prepared version of the publication
for a specific channel. It assembles the adapted caption, selected media,
links and checklist into a single actionable entity.

## 20.2. ChannelPublicationDraft Fields

```text
ChannelPublicationDraft:
    draft_id                   — unique identifier
    publication_plan_id        — parent Publication Plan
    channel_id                 — target channel
    platform                   — platform identifier
    caption_text               — final adapted caption, ready to copy
    hashtags                   — final hashtag list
    media_files                — paths to media files for this channel
    thumbnail                  — path to thumbnail (if video content)
    subtitles                  — path to subtitles file (if video content)
    links                      — final URLs with UTM
    checklist_steps            — generated manual posting instructions
    warnings                   — channel-specific warnings
    ready_for_manual_publish   — true when draft is complete and ready
    ready_for_connector_publish — true when draft is connector-ready (future)
    created_at                 — when draft was created
```

## 20.3. Draft Creation Rule

ChannelPublicationDraft is created from the ExportPackage content.
It does not change core content — it assembles the already-produced
elements for a specific channel.

If the ExportPackage does not contain the necessary channel-specific
elements (e.g. missing caption for a channel), Distribution flags the
missing item and either:
- returns to Production for the missing element;
- blocks the channel and proceeds with other channels;
- escalates to human review.

---

# 21. Link and UTM Handling

## 21.1. Link Sources

Distribution builds publication links from these sources:

| Source | Field |
|---|---|
| Project Settings | `primary_url`, UTM configuration |
| Brand System | Primary URL, campaign-specific URLs |
| Production metadata | Campaign reference, content series |

## 21.2. UTM Parameter Templates

UTM configuration is defined in Project Settings:

```text
utm_source    — {platform} (resolved per channel)
utm_medium    — "organic" (default)
utm_campaign  — "{project_slug}_{content_series}" (from project config)
utm_content   — "{content_id}" (from content metadata)
```

Reference: `PROJECT_SETTINGS_SPEC.md`, Section 8.3

## 21.3. Link Construction

```text
Base URL:      https://example.com

UTM Parameters:
    utm_source=instagram
    utm_medium=organic
    utm_campaign=example_project_ai_series
    utm_content=content_042

Final URL:
    https://example.com?utm_source=instagram&utm_medium=organic
    &utm_campaign=example_project_ai_series&utm_content=content_042
```

## 21.4. Link Fields in Publication Context

```text
LinkRecord:
    base_url                   — original URL from Brand System or Project
    utm_source                 — resolved platform name
    utm_medium                 — resolved medium
    utm_campaign               — resolved campaign identifier
    utm_content                — resolved content identifier
    utm_term                   — optional, for paid campaigns
    final_url                  — complete resolved URL
    link_notes                 — any link-specific notes
```

## 21.5. Link Rules

- Distribution selects the correct link based on content objective and
  Brand System primary URL.
- UTM parameters are applied per channel — `utm_source` varies by platform.
- The final URL is included in the caption or checklist for the human
  to copy.
- Distribution records the link used in the Publication record for
  Analytics correlation.
- Distribution does NOT change the strategic CTA or link destination
  without explicit approval. Link modification that changes business
  intent requires human review.

---

# 22. Distribution QA / Preflight Checks

## 22.1. Purpose

Preflight checks are the final validation before publication execution.
They verify that everything required for publication is in place and
that no new issues have appeared since earlier validation stages.

## 22.2. Preflight Checks

| Check | Rule |
|---|---|
| Channel enabled | Target channel is enabled in Project Settings |
| Account configured | Channel has a valid account reference |
| Publication mode configured | Channel publication mode is set (manual, future connector) |
| Approval complete | Publication Plan has been approved (if required) |
| Package valid | ExportPackage passed Distribution validation |
| Files available | All required media files exist and are readable |
| Caption exists | Caption file exists and is non-empty |
| Media meets constraints | Media format, resolution, duration match channel rules |
| Link valid | Final URL is well-formed and UTM parameters are applied |
| No blocking QA warnings | No QA warning classified as blocking |
| Package not expired | Package was created recently and is not stale |
| Checklist generated | Manual publication checklist is complete |
| Draft ready | ChannelPublicationDraft is ready for manual or connector publish |

## 22.3. Preflight Outcomes

| Outcome | Meaning | Action |
|---|---|---|
| `preflight_passed` | All checks passed. Ready to publish. | Proceed to publication execution |
| `preflight_warnings` | Non-blocking issues found. | Proceed with warnings logged |
| `preflight_failed` | Blocking issue found. | Distribution stops. Error recorded. |
| `human_review_required` | Issue requires human judgment. | Distribution pauses; human notified |

## 22.4. Preflight Is Not Production QA

Preflight is publication-readiness validation. Production QA is content
quality validation. They are separate with different purposes.

---

# 23. Error Handling

## 23.1. Distribution Error Codes

Every Distribution error has a structured format:

```text
DistributionError:
    error_code                 — standardized error identifier
    project_id                 — project context
    export_package_id          — package that failed
    content_item_id            — content that failed
    channel_id                 — channel that failed (if applicable)
    severity                   — blocking, warning, info
    message                    — human-readable description
    recommended_action         — what should be done to resolve
    timestamp                  — when the error occurred
    retry_allowed              — whether the operation can be retried
```

## 23.2. Error Catalog

### 23.2.1. Intake Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `export_package_missing` | Package not found at specified path | blocking | Verify export path; re-export |
| `export_package_not_distribution_ready` | Package status is not Distribution Ready | blocking | Return to Production Pipeline |
| `manifest_invalid` | manifest.json missing or unparseable | blocking | Re-export from Production |
| `metadata_invalid` | metadata.json missing or unparseable | blocking | Re-export from Production |
| `qa_report_missing` | QA report not found in package | blocking | Run Production QA |
| `qa_outcome_blocking` | QA outcome is fail or changes_required | blocking | Fix content and re-run QA |
| `no_target_channels` | target_channels list is empty | blocking | Verify Production Brief |

### 23.2.2. Channel Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `target_channel_disabled` | Channel is not enabled in Project Settings | blocking per channel | Enable channel in settings or remove from targets |
| `unsupported_content_type_for_channel` | Content type not supported on this channel | blocking per channel | Change content type or remove channel |
| `channel_account_not_configured` | No account reference for channel | blocking per channel | Configure account in Project Settings |
| `caption_missing` | No caption file for target channel | blocking per channel | Return to Production; generate caption |
| `caption_exceeds_limit` | Caption exceeds channel character limit | blocking per channel | Return to Production; shorten caption |
| `media_missing` | Required media file not found for channel | blocking per channel | Return to Production; generate media |
| `media_format_incompatible` | Media file format not supported by channel | blocking per channel | Return to Production; re-export in correct format |
| `media_resolution_insufficient` | Media resolution below channel minimum | warning or blocking | Return to Production if blocking |

### 23.2.3. Publication Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `approval_missing` | Publication requires approval that has not been obtained | blocking | Obtain human approval |
| `approval_expired` | Approval has expired | blocking | Re-approve |
| `checklist_generation_failed` | Could not generate manual publication checklist | blocking | Verify package contents; re-generate |
| `manual_publication_not_confirmed` | Human has not confirmed publication execution | blocking | Human executes publication and records result |
| `publication_url_missing` | Publication record lacks URL after claimed publication | blocking | Human provides publication URL |
| `publication_record_failed` | Could not create or update Publication record | blocking | System error; check logs |
| `connector_not_configured` | Connector mode requested but no connector configured | blocking | Configure connector or switch to manual |
| `connector_publish_failed` | Connector attempted but platform returned error | blocking per attempt | Review platform error; retry with correction |
| `connector_auth_failed` | Connector could not authenticate | blocking | Check credentials; update configuration |
| `connector_timeout` | Connector timed out waiting for platform response | blocking per attempt | Retry; if persistent, escalate |

### 23.2.4. Preflight Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `preflight_channel_blocked` | Channel failed preflight check | blocking per channel | Resolve the specific preflight failure |
| `preflight_approval_blocked` | Approval required and not obtained | blocking | Obtain approval |
| `preflight_package_stale` | Package is older than allowed threshold | warning or blocking | Verify content is still valid; re-export if needed |

---

# 24. Analytics Handoff

## 24.1. Purpose

Distribution prepares publication context for the Analytics Layer. It does
not collect metrics — it makes the publication analytics-ready.

## 24.2. What Distribution Passes to Analytics

```text
AnalyticsHandoffRecord:
    publication_id             — reference to the Publication record
    project_id                 — project scope
    content_item_id            — the published content
    export_package_id          — the package source
    channel_id                 — the channel published to
    platform                   — platform identifier
    publication_url            — URL of the published post
    platform_post_id           — platform-native post ID (if available)
    published_at               — publication timestamp
    publication_mode           — manual, connector
    link_used                  — final URL with UTM parameters
    UTM_parameters             — resolved UTM values
    campaign_reference         — campaign identifier if applicable
    production_snapshot_ref    — reference to production snapshot
    distribution_context       — distribution-specific data:
        - delay_between_export_and_publish
        - approval_required
        - approval_count
        - attempt_count
        - checklist_completed
        - preflight_passed
    initial_status             — published, published_with_issues
    handoff_timestamp          — when handoff was performed
```

## 24.3. Analytics Readiness

Distribution marks a Publication as `analytics_ready` when:

- the publication has been completed (status = `published`);
- the publication URL has been recorded;
- the publication timestamp has been recorded;
- the AnalyticsHandoffRecord has been created.

The Analytics Layer consumes this record to create and populate a
`MetricSnapshot`. Distribution does not create the MetricSnapshot itself.

## 24.4. Distribution Does NOT

- collect impressions, views, likes, comments or any engagement metrics;
- call external analytics APIs;
- calculate performance statistics;
- compare metrics against goals;
- generate analytics reports.

These are Analytics Layer responsibilities.

Reference: `DATA_MODEL.md`, Section 7.7; `SYSTEM_ARCHITECTURE.md`, Section 10

---

# 25. Relationship with Learning Memory

## 25.1. Distribution Does NOT Update Learning Memory

Distribution does not write to Learning Memory directly. Learning Memory
extraction happens in the Learning Memory Module, which consumes data
from Analytics.

## 25.2. Context Distribution Provides for Learning

Distribution creates context that is valuable for future learning:

| Context | Learning Value |
|---|---|
| Channel used | Which channels are being published to |
| Publication time | When content was published |
| Publication mode | Manual vs connector |
| Delay export-to-publish | How long between production completion and publication |
| Approval required | Which channels and content types required approval |
| Approval outcome | Which publications were approved, rejected, changed |
| Manual vs connector | Which mode was used and how it correlated with errors |
| Link strategy | Which UTM patterns were used |
| Publication errors | Which errors occurred and at what frequency |
| Attempt count | How many attempts were needed per publication |
| Checklist completion | Whether the human completed the checklist process |

## 25.3. What Learning Memory Can Learn from Distribution Data

```text
Channel effectiveness:
    - Which channels produce the best MetricSnapshots?
    - Which channels have the lowest publication error rate?

Timing effectiveness:
    - Which publication times correlate with higher performance?
    - Does delay between export and publish affect performance?

Mode effectiveness:
    - Does manual vs connector publishing affect outcomes?
    - Does having a checklist improve publication completeness?

Approval patterns:
    - Which content types are most frequently rejected?
    - Which channels require the most changes during approval?

Error patterns:
    - Which errors occur most frequently?
    - Which channels have the highest failure rates?
    - Do retries after specific error codes succeed?
```

Learning Memory consumes this context through the Analytics Layer, not
directly from Distribution.

---

# 26. Relationship with Human Review and Autonomy

## 26.1. Autonomy Mode Impact on Distribution

| Autonomy Mode | Publication Execution | Approval | Checklist |
|---|---|---|---|
| Copilot (MVP) | Manual by human | Required for all | Required for all |
| Assisted (future) | Manual by human | Required for warnings, new channels, paid | Generated for all |
| Autopilot (future) | Connector if configured; manual otherwise | Required for blocking issues only | Generated; human can review |

## 26.2. Human Controls in Distribution

Regardless of autonomy mode, the human retains:

- **Stop Publication** — halt any publication at any stage before execution;
- **Modify Checklist** — add, remove or change manual steps;
- **Change Approval Rules** — require approval where it was previously skipped;
- **Review Draft** — inspect any ChannelPublicationDraft before publishing;
- **Record Publication** — manually enter publication outcome data;
- **Override Error** — mark a blocking error as accepted with reason recorded;
- **Cancel Publication** — cancel a planned or in-progress publication.

## 26.3. Autonomy Escalation in Distribution

Distribution escalates to human when:

- a blocking error cannot be auto-resolved;
- approval is required and not yet obtained;
- connector publishing fails after maximum retries;
- a channel is disabled that was in the Production Brief;
- the QA report contains warnings the system cannot classify;
- the package references an outdated Brand System version;
- the human has configured mandatory review for this content type or channel.

---

# 27. Distribution Entities (Conceptual Summary)

## 27.1. Entity Catalog

These are functional entities for the Distribution Layer. They are
architectural definitions, not database schemas.

| Entity | Purpose |
|---|---|
| `DistributionJob` | Tracks a distribution run from intake to completion |
| `PackageValidationResult` | Records the outcome of package validation |
| `ChannelPublicationTarget` | Maps a channel to its publication configuration |
| `ChannelPublicationDraft` | Prepared publication content for a specific channel |
| `PublicationPlan` | Structured intent to publish — what, where, when, how |
| `ApprovalRecord` | Record of a human approval decision |
| `PublicationChecklist` | Manual publication step-by-step instructions |
| `Publication` | Record of publication fact — Foundation MVP entity |
| `PublicationAttempt` | Record of a single publication attempt |
| `DistributionError` | Structured error record for distribution failures |
| `AnalyticsHandoffRecord` | Context package passed to Analytics Layer |
| `LinkRecord` | Resolved UTM link for a channel publication |
| `PreflightResult` | Outcome of preflight checks before publication |

## 27.2. Entity Relationships

```text
DistributionJob
    ├── PackageValidationResult
    ├── ChannelPublicationTarget (1 per channel)
    │       └── ChannelPublicationDraft
    ├── PublicationPlan
    │       ├── ApprovalRecord
    │       ├── PublicationChecklist
    │       └── LinkRecord
    └── Publication (1 per channel)
            ├── PublicationAttempt
            └── AnalyticsHandoffRecord
```

---

# 28. Storage / File Outputs

## 28.1. Current MVP Outputs

In the current manual publication MVP, Distribution may produce:

```text
exports/{project_slug}/{content_id}/
    ├── content.{format}                    (from Production)
    ├── caption_{platform}.txt              (from Production)
    ├── metadata.json                       (from Production)
    ├── manifest.json                       (from Production)
    ├── qa_report.json                      (from Production)
    ├── manual_publication_checklist.txt    (generated by Distribution)
    ├── channel_draft_{platform}.txt        (assembled by Distribution)
    └── publication_metadata.json           (future: Distribution context)
```

## 28.2. Future Outputs

In future phases, Distribution may also produce:

```text
exports/{project_slug}/{content_id}/
    ├── publication_plan.json               (structured plan)
    ├── channel_draft_{platform}.json       (structured draft)
    ├── publication_record.json             (structured publication outcome)
    ├── publication_attempts.json           (attempt history)
    ├── analytics_handoff.json              (context for Analytics)
    └── connector_response_{platform}.json  (raw connector response)
```

Do not require these as current code changes.

---

# 29. Current MVP Compatibility

## 29.1. What Must Be Preserved

The current Foundation MVP must remain fully functional:

```text
Idea → Scenario → ContentItem → ExportPackage → Manual Publication → MetricSnapshot
```

DISTRIBUTION_SPEC.md preserves:

- manual publication as the only current publication mode;
- inspectable ExportPackage (inspect_package.py unaffected);
- validatable ExportPackage (validate_package.py unaffected);
- manual publication checklist as the primary Distribution deliverable;
- Publication record as the fact of publication;
- no external APIs, autoposting or connector dependencies;
- no UI dependency;
- smoke loop (smoke_loop.py) unaffected.

## 29.2. What the Distribution Spec Adds Conceptually

The Distribution Spec adds architectural definition for:

- distribution intake and validation as a formal boundary;
- channel mapping and adaptation rules;
- publication planning as a structured activity;
- approval gates tied to autonomy modes;
- detailed error handling for distribution failures;
- analytics handoff as a defined interface;
- Learning Memory context provision.

These are conceptual additions. They do not require changes to current
working code, tests or scripts. They define the architecture that future
implementation will follow.

---

# 30. Future Extension Path

## 30.1. Stage 1 — Current MVP (Now)

- Manual publication only.
- Distribution generates manual publication checklist.
- Human publishes and records Publication.
- ExportPackage is inspectable and validatable.

## 30.2. Stage 2 — Better Manual Publishing

- ChannelPublicationDraft for each channel.
- Structured PublicationPlan.
- ApprovalRecord tracking.
- Enhanced checklist with copy-paste blocks and step-by-step instructions.

## 30.3. Stage 3 — Scheduling

- `planned_at` with timezone in PublicationPlan.
- Scheduling reasons and confidence scores.
- Publication queues.
- Human reminders for scheduled publications.

## 30.4. Stage 4 — Connector-Assisted Publishing

- Platform connectors for content dispatch.
- Connectors prepare or publish after explicit approval.
- Connector response recording.
- Retry logic for connector failures.

## 30.5. Stage 5 — Controlled Autoposting

- Autoposting only after:
  - explicit Project Settings enabling;
  - configured and tested platform connectors;
  - defined approval rules;
  - safety gates and error escalation;
  - human emergency stop capability.
- Routine publications may proceed automatically within defined boundaries.

---

# 31. Readiness Criteria

The Distribution architecture is considered defined when:

- [x] Distribution boundary is defined — where Production ends and Distribution begins;
- [x] ExportPackage intake is defined — how packages enter Distribution;
- [x] Package validation is defined — what checks verify publication readiness;
- [x] Channel mapping is defined — how target channels are resolved;
- [x] Channel adaptation rules are defined — what may and may not be adapted;
- [x] Publication plan is defined — structured intent to publish;
- [x] Approval gate is defined — how autonomy modes control publication;
- [x] Manual workflow is defined — the current MVP publication process;
- [x] Publication record is defined — entity fields and purpose;
- [x] Publication status lifecycle is defined — conceptual status flow;
- [x] Publication attempts are defined — audit trail for retries;
- [x] Preflight checks are defined — final validation before execution;
- [x] Error handling is defined — structured error catalog;
- [x] Analytics handoff is defined — context passed to Analytics Layer;
- [x] Learning Memory context is defined — what distribution data informs learning;
- [x] Current MVP manual publication is preserved;
- [x] Future scheduling/autoposting is clearly marked as future;
- [x] Foundation MVP chain (ExportPackage → Publication → MetricSnapshot) is intact.

---

# 32. Related Documents

## 32.1. Core Architecture

```text
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
```

## 32.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration (channels, UTM, export)
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
```

## 32.3. Intelligence Layer

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Full content cycle (Distribution = Stage 7)
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Orchestrator Agent and autonomy modes
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content opportunity analysis
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory architecture
```

## 32.4. Production Layer

```text
docs/04_production/CONTENT_TYPES_SPEC.md            — Content type definitions
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — Production Pipeline (ends at Distribution Ready)
docs/04_production/ASSET_LIBRARY_SPEC.md            — Asset Library specification
docs/04_production/DISTRIBUTION_SPEC.md             — This document
```

## 32.5. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# 33. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-08 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Production Layer — Distribution / Publishing Boundary |

---

# Final Statement

The Distribution Layer is the delivery boundary of LOOPRA. It does not
create content, does not decide strategy, does not analyze performance.
It takes finished, validated production output and ensures it reaches
the right channels with the right adaptations, the right approvals and
the right records.

In the current Foundation MVP, Distribution provides a manual publication
checklist — a structured guide for the human operator to publish content
and record the outcome. In future phases, Distribution will expand to
support scheduling, connector-based publishing and controlled autoposting,
always within the boundaries of human-defined autonomy rules.

Distribution bridges Production and Analytics. It closes the loop from
"content created" to "content published" — providing the essential
record that enables measurement, learning and continuous improvement in
the next cycle.

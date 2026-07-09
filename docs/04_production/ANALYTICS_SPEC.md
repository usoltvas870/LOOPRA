# ANALYTICS SPEC

## Version

v1.0

## Status

Active — LOOPRA Analytics Layer

## Purpose

This document defines the Analytics Layer / Analytics boundary of the
LOOPRA Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA turn a Publication record and publication data into a
> MetricSnapshot, performance interpretation and structured analytics
> context for Learning Memory?

ANALYTICS_SPEC.md is the architectural blueprint for the measurement and
interpretation layer that bridges Distribution (publication outcome)
with Learning Memory (accumulated experience).

It describes:

- the Analytics boundary and its position in the LOOPRA architecture;
- the analytics intake and handoff from Distribution;
- the metric collection model (manual current MVP, connector future);
- raw metrics, normalization and metric taxonomy;
- the MetricSnapshot entity and derived metrics;
- performance evaluation against goals and baselines;
- the Analytics Summary and Analytics Observation model;
- anomaly detection, confidence and completeness scoring;
- the Learning Memory Handoff payload;
- current MVP manual MetricSnapshot limitations;
- future analytics capabilities as architectural direction.

It does NOT describe:

- content creation, production or distribution;
- asset selection or library management;
- publication execution or scheduling;
- learning extraction algorithms (see `LEARNING_MEMORY_SPEC.md`);
- strategic decision making or autonomous cycle optimization;
- external platform API contracts;
- UI dashboards, API contracts or database schemas;
- specific AI models, providers or code-level implementation.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

ANALYTICS_SPEC.md defines the Analytics Layer as the subsystem that
receives publication context from Distribution and produces a
MetricSnapshot, performance interpretation and a structured handoff
to Learning Memory.

It serves as the specification for:

- the Analytics Handoff intake — how publication context enters Analytics;
- metric collection modes — manual (current MVP) and connector-based (future);
- raw metrics — platform-specific metric data before normalization;
- metric normalization — how platform-specific metrics become normalized categories;
- the metric taxonomy — reach, engagement, retention, conversion, negative,
  operational, quality;
- the MetricSnapshot entity — the Foundation MVP performance record;
- derived metrics — computed from normalized base metrics;
- performance evaluation — how Analytics measures success against goals;
- benchmarks and baselines — historical comparisons and target references;
- the Analytics Summary — human-readable and machine-readable performance summary;
- Analytics Observations — structured interpretations, not durable memory;
- anomaly detection — conceptual flags for unusual performance;
- data completeness and confidence models;
- time windows and snapshot refresh;
- cross-channel comparison (future);
- relationship with content types, production snapshot and distribution context;
- the Learning Memory Handoff — what Analytics passes to the Intelligence Layer;
- current MVP manual MetricSnapshot compatibility and constraints;
- future analytics capabilities with clear marking.

## 1.2. In Scope

- Analytics Handoff intake from Distribution;
- metric collection model;
- manual metrics (current MVP);
- raw metrics and metric normalization;
- metric taxonomy and categories;
- MetricSnapshot entity;
- derived metrics;
- performance evaluation;
- benchmarks and baselines;
- Analytics Summary;
- Analytics Observations;
- anomaly detection (conceptual flags);
- confidence and completeness scoring;
- time windows and snapshot refresh;
- cross-channel comparison (future);
- relationship with content types, production snapshot and distribution context;
- Learning Memory Handoff payload;
- analytics error handling;
- current MVP compatibility;
- future extension path.

## 1.3. Out of Scope

- content creation, generation or assembly (Production Pipeline);
- asset selection or library management (Asset Library);
- publication execution or scheduling (Distribution Layer);
- strategic content opportunity discovery (Intelligence Layer);
- learning extraction algorithms (Learning Memory);
- trend detection or market signal analysis;
- Orchestrator Agent decision-making;
- external analytics platform API implementation;
- analytics dashboards, UI or reporting;
- database schemas, API contracts or storage engine selection;
- autoposting or automated distribution;
- paid advertising metrics or budget management beyond conceptual reference;
- code-level implementation of any component.

---

# 2. Role of Analytics in LOOPRA

## 2.1. Position in the LOOPRA Architecture

The Analytics Layer occupies a defined position between Distribution
(publication execution and recording) and Learning Memory (accumulated
operational experience):

```text
Intelligence Layer
    │  "What to create, why, for whom, in what format"
    ↓
Production Layer
    │  "How to manufacture the selected content"
    │  Brief → Plan → Select → Generate → Assemble → QA → Export
    ↓
Distribution Layer
    │  "How to deliver, adapt, approve and record publication"
    │  Intake → Validate → Map → Adapt → Plan → Approve → Publish → Record
    ↓
Distribution Boundary: Publication Record → Analytics Ready
    │
Analytics Layer  ← THIS DOCUMENT
    │  "How to measure, normalize, interpret and hand off performance data"
    │  Handoff Intake → Collect → Normalize → Snapshot → Evaluate → Summarize →
    │  Handoff to Learning Memory
    ↓
Analytics Boundary: MetricSnapshot → LearningMemoryHandoffPayload
    │
Learning Memory
    │  "What the system should remember for the next cycle"
    │  Extraction → Pattern Formation → Knowledge Storage → Retrieval
    ↓
Next Cycle (improved)
```

Reference: `SYSTEM_ARCHITECTURE.md`, Sections 8–11

## 2.2. What Analytics Does

Analytics:

- receives publication context from Distribution (AnalyticsHandoffRecord);
- manages metric collection — manual entry (current MVP) or connector-based (future);
- stores raw metrics as platform-specific records;
- normalizes platform-specific metrics into standardized categories;
- creates and populates MetricSnapshot — the Foundation MVP performance record;
- computes derived metrics from normalized base metrics;
- evaluates performance against goals, baselines and expectations;
- generates an Analytics Summary — human-readable and machine-readable;
- forms Analytics Observations — structured interpretations;
- detects anomalies conceptually;
- calculates confidence and completeness scores;
- assembles a LearningMemoryHandoffPayload for the Intelligence Layer.

## 2.3. What Analytics Does NOT Do

Analytics does NOT:

- decide what content to create (Intelligence Layer / Orchestrator Agent);
- produce content, generate copy or assemble media (Production Pipeline);
- publish content or manage distribution (Distribution Layer);
- extract durable knowledge from results (Learning Memory);
- update the Brand System or Project Settings;
- modify the Foundation MVP entity chain;
- make autonomous decisions about future cycles;
- replace the Orchestrator Agent's decision-making role.

## 2.4. Analytics Answers

Analytics answers measurement and interpretation questions:

- What metrics were recorded for this publication?
- How do platform-specific metrics map to standardized categories?
- What is the performance snapshot for this content?
- Did the content achieve its goal?
- How does performance compare to the baseline?
- What is the confidence level in this measurement?
- What signals (positive, negative, anomalous) does the data contain?
- What structured context should Learning Memory receive?

## 2.5. The Agent Principle Preserved

Analytics operates under LOOPRA's foundational principle:

> Agents decide. Tools execute.

Analytics is a measurement and interpretation tool. It provides data,
evaluation and structured observations. It does NOT decide what the
system should do next. That decision belongs to the Orchestrator Agent,
informed by Learning Memory.

```text
Analytics says:      "This carousel had a 40% higher save rate than the
                      project baseline. The educational angle and
                      step-by-step structure likely contributed."

Orchestrator says:   "Based on this evidence, I will increase the share
                      of educational carousels in the next cycle."

Analytics measures and interprets.
Orchestrator decides.
Learning Memory remembers.
```

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

This chain is the reliable execution backbone of LOOPRA. The Analytics
Spec elaborates on the section between Publication and MetricSnapshot,
and the handoff from MetricSnapshot toward Learning Memory.

## 3.2. What Analytics Spec Elaborates

The Analytics Spec provides an expanded, detailed view of:

```text
Foundation MVP:
    Publication → MetricSnapshot

Analytics Spec (detailed):
    Publication (published)
        ↓
    Analytics Handoff Intake (from Distribution)
        ↓
    Metric Collection (manual entry — current MVP)
        ↓
    RawMetricRecord
        ↓
    Metric Normalization
        ↓
    MetricSnapshot (populated)
        ↓
    Derived Metrics Computation
        ↓
    Performance Evaluation
        ↓
    Analytics Summary
        ↓
    Analytics Observations
        ↓
    Learning Memory Handoff
```

The Foundation MVP entities (`Publication`, `MetricSnapshot`) remain in
place. The Analytics Spec explains what happens between and around these
entities without changing their identity or role.

## 3.3. Current MVP: Manual MetricSnapshot

In the current Foundation MVP:

- `MetricSnapshot` can be created as a draft;
- metrics are recorded manually by the human operator;
- the `import_manual_metrics.py` helper imports metrics into a draft snapshot;
- `clicks` input is normalized to `link_clicks`;
- `published_url` updates the related `Publication` (not stored as a raw metric field);
- missing metrics are allowed if marked incomplete;
- analytics summary can be absent or draft until metrics exist;
- no external analytics APIs are called;
- no automated metric refresh exists.

Reference: `DATA_MODEL.md`, Section 7.7; `PIPELINES_SPEC.md`, Section 5.5

## 3.4. What Does NOT Change

The Analytics Spec does NOT:

- modify the `Publication` entity or its statuses;
- modify the `ContentItem` entity;
- modify the `ExportPackage` entity;
- change the existing Foundation MVP lifecycle;
- require new database schemas or migrations;
- alter the smoke loop, `find_metric_snapshots.py` or `import_manual_metrics.py`.

It adds conceptual depth to the analytics process that will guide future
implementation, without requiring changes to the validated current
baseline.

---

# 4. Relationship to Distribution

## 4.1. The Hard Boundary

Distribution and Analytics have a strictly defined boundary:

```text
Distribution ends at:        Publication Record → Analytics Ready

Analytics begins with:       Analytics Handoff Intake
```

Distribution delivers the `AnalyticsHandoffRecord`. Analytics consumes it.

Reference: `DISTRIBUTION_SPEC.md`, Section 24

## 4.2. What Distribution Passes to Analytics

Distribution creates an `AnalyticsHandoffRecord` containing:

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

Reference: `DISTRIBUTION_SPEC.md`, Section 24.2

## 4.3. Analytics Does NOT Validate Publication

Analytics does not:

- validate the publication checklist;
- verify that publication actually occurred;
- check whether UTM parameters are correct;
- re-run distribution preflight checks;
- confirm channel configuration.

Analytics trusts the Publication record as the source of truth for
publication fact. If the Publication status is not `published`, Analytics
rejects the handoff with an error (`publication_not_published`).

## 4.4. Analytics Does NOT Publish

Analytics never:

- triggers publication;
- modifies publication timing;
- changes publication mode;
- reschedules content;
- retries failed publications.

Distribution publishes. Analytics measures.

---

# 5. Relationship to Learning Memory

## 5.1. The Hard Boundary

Analytics and Learning Memory have a strictly defined boundary:

```text
Analytics ends at:            LearningMemoryHandoffPayload

Learning Memory begins with:  Learning Extraction
```

Analytics produces interpretation and context. Learning Memory extracts
durable, reusable knowledge.

Reference: `LEARNING_MEMORY_SPEC.md`, Sections 2, 7

## 5.2. What Analytics Passes to Learning Memory

Analytics assembles a `LearningMemoryHandoffPayload` containing:

- `MetricSnapshot` — the normalized, evaluated performance record;
- `PerformanceEvaluation` — success level, goal alignment, key observations;
- `AnalyticsSummary` — human-readable and machine-readable summary;
- `AnalyticsObservations` — structured interpretations (not yet durable memory);
- production context references (production_snapshot, content_type, variant, assets);
- distribution context references (channel, timing, mode, errors, links);
- `confidence_score` — how reliable the data and interpretation are;
- `completeness_score` — how complete the metric data is;
- `suggested_learning_categories` — categories of knowledge this data might inform.

Reference: See Section 26 — Learning Memory Handoff

## 5.3. Analytics Does NOT Update Learning Memory

Analytics does NOT:

- write directly to Learning Memory;
- create Learning Records or Performance Patterns;
- decide which observations become durable knowledge;
- update confidence scores in Learning Memory;
- modify existing patterns or knowledge entities.

Learning Memory owns the extraction and storage of durable knowledge.
Analytics provides the structured input. Learning Memory decides what
to retain and how to use it.

Reference: `LEARNING_MEMORY_SPEC.md`, Section 7 — Learning Extraction Process

## 5.4. What Analytics Produces vs What Learning Memory Stores

```text
Analytics produces:              Learning Memory stores:

MetricSnapshot                   →  raw evidence for Learning Records
PerformanceEvaluation            →  contextual data for pattern validation
AnalyticsSummary                 →  human-readable reference for audit
AnalyticsObservation             →  candidate signals for pattern detection
AnomalyFlag                      →  triggers for deeper analysis
Confidence/completeness scores   →  input for Learning Memory confidence model
Suggested learning categories    →  routing hints for knowledge organization
```

Analytics says: "These are the facts, the numbers, the interpretation
and the signals."

Learning Memory says: "Based on this, here is what we now know about
what works, for whom, under what conditions."

Analytics provides the evidence. Learning Memory forms the knowledge.

---

# 6. Analytics Pipeline Overview

## 6.1. Current MVP Pipeline (Manual)

```text
Publication Record (status = published)
    ↓
Analytics Handoff Intake
    ↓  (AnalyticsHandoffRecord consumed)
    ↓
Metric Source Resolution
    ↓  (manual mode selected — current MVP)
    ↓
Manual Metric Entry
    ↓  (human enters data or imports via import_manual_metrics.py)
    ↓
RawMetricRecord
    ↓
Metric Normalization
    ↓  (platform-specific → normalized categories)
    ↓
MetricSnapshot (populated)
    ↓
Derived Metrics
    ↓  (computed from normalized base metrics)
    ↓
Performance Evaluation
    ↓  (against goals, baselines if available)
    ↓
Analytics Summary
    ↓
Analytics Observations
    ↓
Learning Memory Handoff
    ↓
LearningMemoryHandoffPayload
```

## 6.2. Future Pipeline Extension

```text
Publication Record (status = published)
    ↓
Analytics Handoff Intake
    ↓
Metric Source Resolution
    ↓  (connector mode selected — future)
    ↓
Connector-Based Metric Collection
    ↓  (pulls data from platform API on schedule)
    ↓
RawMetricRecord (with source_confidence from connector)
    ↓
Metric Normalization
    ↓
MetricSnapshot (populated, time-windowed)
    ↓
Derived Metrics
    ↓
Performance Evaluation
    ↓
Multi-Snapshot Comparison (future)
    ↓  (time-series, cross-channel, cross-content-type)
    ↓
Analytics Summary
    ↓
Learning Memory Handoff
```

## 6.3. Stage-by-Stage Summary

| Stage | Purpose | Current MVP | Future |
|---|---|---|---|
| Handoff Intake | Receive publication context from Distribution | Yes | Yes |
| Metric Source Resolution | Determine how metrics will be collected | Manual only | Manual, connector, import, hybrid |
| Metric Collection | Gather performance data | Manual entry | Manual, connector pull, CSV import |
| Raw Metric Storage | Store platform-specific metrics | In MetricSnapshot | Separate RawMetricRecord |
| Metric Normalization | Convert platform-specific to standard categories | Basic mapping | Full normalization with validation |
| MetricSnapshot Creation | Create the Foundation MVP performance record | Draft → populated | Automated population |
| Derived Metrics | Compute rates and ratios | Conceptual | Automated computation |
| Performance Evaluation | Assess against goals and baselines | Basic | Full multi-dimensional |
| Analytics Summary | Form structured summary | Draft if data missing | Always generated |
| Analytics Observations | Generate structured interpretations | Conceptual | Automated observation generation |
| Anomaly Detection | Flag unusual performance | Not implemented | Rule-based → statistical |
| Learning Memory Handoff | Pass context to Intelligence Layer | Basic payload | Rich structured payload |

---

# 7. Analytics Intake

## 7.1. Purpose

Analytics Intake is the entry point where an `AnalyticsHandoffRecord` from
Distribution is received and registered for metric collection and
evaluation.

## 7.2. Intake Inputs

| Input | Source | Required |
|---|---|---|
| `AnalyticsHandoffRecord` | Distribution Layer | Yes |
| `Publication` record | Foundation MVP | Yes |
| `Project` context | Foundation / Project Settings | Yes |
| `ContentItem` reference | Foundation MVP | Yes |
| `ExportPackage` reference | Foundation MVP | Yes |
| `Production Snapshot` reference | Production Pipeline | Yes |
| `Distribution context` | Distribution Layer | Yes |
| `Goal / success criteria` | Project Settings / Brand System | No (may be unavailable) |

## 7.3. Intake Process

```text
AnalyticsHandoffRecord arrives from Distribution
    ↓
Analytics validates handoff:
    - publication_id references a valid Publication
    - Publication status = published or published_with_issues
    - publication_url exists (if required for metric collection)
    - published_at exists
    - project_id is valid
    - content_item_id is valid
    - channel_id / platform is known
    - goal context is available (or marked as unknown)
    ↓
If validation passes:
    → AnalyticsJob created
    → AnalyticsJob status = intake_complete
    → proceed to Metric Source Resolution
If validation fails:
    → AnalyticsJob status = intake_failed
    → error recorded with reason
    → handoff rejected (returned to Distribution or flagged for review)
```

## 7.4. Intake Outputs

| Output | Description |
|---|---|
| `AnalyticsJob` | The tracking entity for this analytics run |
| `intake_validation_result` | pass / fail with reasons |
| `metric_collection_plan` | Which metrics to collect, from which source, by when |
| `expected_metric_set` | The set of metrics relevant to this content type, channel and goal |

## 7.5. AnalyticsJob Entity (Conceptual)

```text
AnalyticsJob:
    analytics_job_id           — unique identifier
    project_id                 — project scope
    content_item_id            — the content being analyzed
    publication_id             — the publication being measured
    export_package_id          — the package source
    channel_id                 — the channel published to
    platform                   — platform identifier
    status                     — intake_complete, collection_pending,
                                 collecting, raw_metrics_collected,
                                 normalized, snapshot_created, evaluated,
                                 learning_handoff_ready, completed,
                                 collection_failed, insufficient_data,
                                 needs_manual_entry, stale, cancelled
    collection_mode            — manual, connector_future, import_future, hybrid_future
    collection_window_start    — start of the metric collection period
    collection_window_end      — end of the metric collection period
    created_at                 — intake timestamp
    completed_at               — when analytics processing completed
```

---

# 8. Metric Sources

## 8.1. Overview

Metric Sources define where performance data originates. The source type
determines collection method, reliability and confidence.

## 8.2. Source Type Catalog

### 8.2.1. Manual Entry — Current MVP

```text
Definition:
    Metrics are entered manually by the human operator. The operator
    visits the published post on the platform, observes the metrics
    and records them.

What it provides:
    views, likes, comments, shares, saves, link clicks — as observed
    by the human on the platform at a specific time.

Reliability:
    Medium. Subject to human observation error, timing variance and
    platform UI interpretation differences. Metrics may be incomplete.

Limitations:
    - Metrics may not be recorded at consistent time intervals.
    - Not all platform metrics may be visible to the operator.
    - Operator may not record all available metrics.
    - No automated time-series data.

Status:
    Current MVP. This is the only active collection mode.
```

### 8.2.2. Platform Connector — Future

```text
Definition:
    A platform-specific connector authenticates with the external
    platform API and retrieves performance data programmatically.

What it provides:
    Structured metric data directly from the platform's API,
    including metrics not visible in the standard UI.

Reliability:
    High. Data comes directly from the platform source. Consistent
    format and timing.

Limitations:
    - Requires platform API access and authentication.
    - Subject to platform API rate limits, availability and changes.
    - Some platforms limit historical data access.
    - API may not expose all metrics visible in platform analytics UI.

Status:
    Future. Not implemented in current MVP.
```

### 8.2.3. CSV / Platform Export Import — Future

```text
Definition:
    The operator exports analytics data from the platform
    (e.g., Instagram Insights CSV export, YouTube Analytics export)
    and imports it into LOOPRA.

What it provides:
    Batch metric data from platform export. Structured, but format
    varies by platform.

Reliability:
    Medium-High. Data comes from the platform but is processed through
    an intermediate export format that may lose detail.

Limitations:
    - Export formats differ per platform.
    - Export timing may not align with desired collection windows.
    - Manual step: operator must export, then import.
    - Not real-time.

Status:
    Future. Not implemented in current MVP.
```

### 8.2.4. Internal Tracking — Future

```text
Definition:
    LOOPRA tracks click-through events on UTM-tagged links using
    internal redirect or tracking pixel.

What it provides:
    Link click data, conversion events from LOOPRA-managed landing
    pages or tracking infrastructure.

Reliability:
    High. First-party data, fully controlled by LOOPRA.

Limitations:
    - Requires LOOPRA-managed link infrastructure.
    - Only tracks events that pass through LOOPRA-controlled paths.
    - Does not capture in-platform engagement metrics.

Status:
    Future. Not implemented in current MVP.
```

### 8.2.5. Payment / Subscription Events — Future

```text
Definition:
    Integration with payment processors or subscription platforms
    to track conversion events.

What it provides:
    Purchase events, subscription starts, revenue data, conversion
    attribution.

Reliability:
    High. Transactional data from payment systems.

Limitations:
    - Requires payment processor integration.
    - Attribution to specific content may be probabilistic.
    - Privacy and compliance constraints.

Status:
    Future. Not implemented in current MVP.
```

## 8.3. Source Reliability Comparison

| Source | Reliability | Availability | Data Completeness | Current/Future |
|---|---|---|---|---|
| Manual Entry | Medium | Always | Variable | Current MVP |
| Platform Connector | High | Per-platform | High | Future |
| CSV Import | Medium-High | Per-platform | Medium-High | Future |
| Internal Tracking | High | Always (if configured) | High | Future |
| Payment Events | High | Per-integration | High | Future |

---

# 9. Metric Collection Modes

## 9.1. Mode Overview

LOOPRA supports a progression of metric collection modes. The current
Foundation MVP implements Manual Mode only. Other modes are future
architecture direction.

| Mode | Current Status | Description |
|---|---|---|
| Manual | Current MVP | Human enters metrics after observing platform post |
| Connector | Future | System pulls metrics from platform API |
| Import | Future | Operator imports CSV/platform export data |
| Hybrid | Future | Connector data + manual correction or augmentation |

## 9.2. Manual Mode — Current MVP

In Manual Mode:

- the human operator publishes content (manual publication);
- the operator returns to the platform post after a defined period;
- the operator observes key metrics (views, likes, comments, shares, etc.);
- the operator records metrics using `import_manual_metrics.py` or equivalent;
- the system creates or populates a MetricSnapshot;
- missing metrics are allowed but marked incomplete;
- confidence is lower than connector-based collection.

Manual mode supports:

- recording metrics at any time (not on a schedule);
- partial metric entry (not all fields required);
- draft snapshots that can be updated later;
- human interpretation notes alongside metrics.

## 9.3. Connector Mode — Future

In Connector Mode:

- the system is configured with platform API credentials (future);
- at a defined collection schedule, the connector calls the platform API;
- the connector retrieves structured metric data;
- raw platform response is stored for audit;
- metrics are normalized into standard categories;
- the MetricSnapshot is populated automatically;
- retries are supported for transient API failures.

Connector mode requires:

- configured and authenticated platform connector;
- defined collection schedule (e.g., 24h, 72h, 7d post-publication);
- error handling for API failures, rate limits, authentication expiry.

## 9.4. Import Mode — Future

In Import Mode:

- the operator exports analytics data from the platform as CSV/Excel;
- the operator imports the file into LOOPRA;
- LOOPRA parses the file, maps columns to RawMetricRecords;
- raw metrics are normalized into MetricSnapshot;
- import validation checks for data integrity and completeness.

Import mode supports:

- batch import of metrics for multiple publications;
- platform-specific CSV format parsers;
- import error handling (malformed files, missing columns, type errors).

## 9.5. Hybrid Mode — Future

In Hybrid Mode:

- connector automatically collects available metrics;
- the operator can manually correct or augment connector data;
- manual overrides are captured and timestamped;
- the final MetricSnapshot indicates which values are connector-sourced
  and which are manual.

Hybrid mode provides:

- automation with human oversight;
- correction of connector errors or gaps;
- the ability to add metrics not available via API.

---

# 10. Raw Metrics

## 10.1. Definition

Raw Metrics are platform-specific metric values as they appear at the
source — before any normalization, mapping or interpretation.

Different platforms use different metric names, meanings and structures.
The Raw Metric layer respects these differences rather than forcing
all platforms into a single schema.

## 10.2. RawMetricRecord Entity (Conceptual)

```text
RawMetricRecord:
    raw_metric_id              — unique identifier
    project_id                 — project scope
    publication_id             — the publication being measured
    content_item_id            — the content being analyzed
    channel_id                 — the channel published to
    platform                   — platform identifier (instagram, telegram, linkedin, etc.)
    source_type                — manual, connector, import, hybrid
    collected_at               — when the metrics were collected/recorded
    collection_window_start    — start of the observation window
    collection_window_end      — end of the observation window
    raw_payload                — the full raw data as received (JSON blob, CSV row, etc.)
    raw_metric_values          — key-value pairs of platform-specific metric names and values
    source_confidence          — high, medium, low, unknown
    collection_status          — complete, partial, draft, error
    error_code                 — populated if collection failed
    notes                      — operator notes or observations
```

## 10.3. Platform-Specific Raw Metric Examples

### Instagram

```text
Raw metrics (as visible in Instagram Insights):
    accounts_reached
    impressions
    profile_visits
    website_taps
    likes
    comments
    saves
    shares
    follows
    unfollows
```

### Telegram

```text
Raw metrics (as visible in Telegram channel statistics):
    views
    forwards
    reactions
```

### LinkedIn

```text
Raw metrics (as visible in LinkedIn post analytics):
    impressions
    reactions
    comments
    reposts
    clicks
    engagement_rate
```

### YouTube

```text
Raw metrics (as visible in YouTube Studio Analytics):
    views
    watch_time_minutes
    average_view_duration
    likes
    dislikes
    comments
    shares
    subscribers_gained
    subscribers_lost
    impressions
    click_through_rate
```

## 10.4. Why Raw Metrics Are Platform-Specific

Forcing all platforms into the same raw schema would:

- lose platform-specific nuance (e.g., Instagram "saves" vs LinkedIn "reposts");
- create false equivalences (e.g., "views" means different things on different platforms);
- force missing values where a platform simply does not provide a metric.

Raw metrics preserve the original data. Normalization (Section 11) maps
them to standard categories for comparison.

## 10.5. Raw Metric Storage

In the current MVP, raw metrics are stored directly within the
MetricSnapshot. A separate `RawMetricRecord` entity is conceptual for
future implementation.

In future phases:

- raw metrics are stored in `RawMetricRecord` entities;
- `MetricSnapshot` references one or more `RawMetricRecord` entities;
- multiple `RawMetricRecord` entities may exist per publication
  (e.g., multiple collection windows).

---

# 11. Metric Normalization

## 11.1. Purpose

Metric normalization converts platform-specific raw metrics into a
standardized set of categories that can be compared across channels,
content types and time periods.

Normalization answers:

- "Instagram saves" → which normalized category?
- "Telegram forwards" → which normalized category?
- "LinkedIn reposts" → which normalized category?

## 11.2. Why Normalization Is Necessary

Without normalization:

```text
Platform A:  saves = 45
Platform B:  bookmarks = 30
Platform C:  (no equivalent metric)

Question: "Which platform had more content-saving behaviour?"
Answer: Cannot compare. Different names, different meanings.
```

With normalization:

```text
Platform A:  saves = 45       →  normalized: engagement = {saves: 45}
Platform B:  bookmarks = 30   →  normalized: engagement = {saves: 30}
Platform C:  (no equivalent)  →  normalized: engagement = {saves: unavailable}

Answer: Platform A had 45 saves, Platform B had 30 saves, Platform C
        does not provide this metric. Comparison possible with
        acknowledged gaps.
```

## 11.3. Normalization Rules

1. **Map to standard categories.** Each platform-specific metric maps
   to one or more normalized metric categories.

2. **Do not invent data.** If a platform does not provide a metric,
   mark it as `unavailable`, not as `0`. Zero means "the metric was
   measured and the value was zero." Unavailable means "the metric
   could not be measured."

3. **Preserve the raw value.** Normalization adds the normalized
   mapping. It does not delete or alter the raw value.

4. **Document platform differences.** Each normalized metric should
   carry information about how it was derived from the raw metric,
   including any platform-specific semantics.

5. **Version the mapping.** If a platform changes its metric definitions
   (e.g., Instagram changes how "reach" is calculated), the normalization
   mapping should be versioned.

## 11.4. Normalized Metric Categories

```text
Normalized metrics:
    reach                     — number of unique accounts/users that saw the content
    impressions               — total number of times the content was displayed
    views                     — number of times the content was viewed
    unique_viewers            — number of unique viewers (where distinguishable)
    likes                     — positive reactions (likes, hearts, thumbs up)
    reactions                 — all reactions including likes (where platform distinguishes)
    comments                  — user comments on the content
    shares                    — content shared to other users/audiences
    saves                     — content saved/bookmarked for later
    reposts                   — content re-shared to the user's own audience
    replies                   — direct replies (distinct from general comments)
    link_clicks               — clicks on links within the content
    profile_visits            — visits to the profile/channel page from this content
    follows                   — new follows/subscriptions from this content
    leads                     — qualified leads generated from this content
    conversions               — completed conversion events (purchases, signups)
    revenue                   — revenue attributed to this content
    watch_time_seconds        — total watch time in seconds (video content)
    average_watch_seconds     — average watch duration per viewer (video content)
    completion_rate           — percentage of viewers who watched to the end (video)
    retention_rate            — audience retention percentage (video)
    scroll_depth_percent      — how far users scrolled (text/article content)
    view_duration_seconds     — average time spent viewing (non-video content)
    unfollows                 — users who unfollowed after this content
    unsubscribes              — users who unsubscribed after this content
    hides                     — users who hid the content from their feed
    reports                   — users who reported the content
    dislikes                  — negative reactions
    negative_feedback_count   — aggregate negative feedback signals
    cost_currency             — money spent on this content (future paid channels)
    cost_per_result           — cost per defined result (future paid channels)
```

## 11.5. Normalization Mapping Examples

### Instagram → Normalized

```text
accounts_reached    → reach
impressions         → impressions
profile_visits      → profile_visits
website_taps        → link_clicks
likes               → likes
comments            → comments
saves               → saves
shares              → shares
follows             → follows
unfollows           → unfollows
```

### Telegram → Normalized

```text
views               → views
forwards            → shares
reactions           → reactions
```

### LinkedIn → Normalized

```text
impressions         → impressions
reactions           → likes
comments            → comments
reposts             → shares
clicks              → link_clicks
```

### YouTube → Normalized

```text
views               → views
watch_time_minutes  → watch_time_seconds (converted)
average_view_duration → average_watch_seconds
likes               → likes
dislikes            → dislikes
comments            → comments
shares              → shares
subscribers_gained  → follows
subscribers_lost    → unfollows
impressions         → impressions
click_through_rate  → (derived metric, stored separately)
```

## 11.6. Normalization Validation

After normalization, Analytics checks:

- every raw metric has been mapped to at least one normalized metric
  (or explicitly excluded with reason);
- no conflicting mappings exist (one raw metric mapped to two
  incompatible normalized categories);
- unavailable metrics are marked, not omitted;
- values that are truly zero are distinguishable from unavailable.

---

# 12. Metric Taxonomy

## 12.1. Overview

Analytics classifies normalized metrics into groups. Each group answers
a different question about how content performed.

## 12.2. Reach Metrics

Measures how many people the content reached.

```text
Question: "How many people saw or could have seen this content?"

Normalized metrics:
    impressions
    reach
    views
    unique_viewers

Relevance:
    Primary for awareness goals.
    Indicates content distribution breadth.
    High reach with low engagement signals weak content resonance.
    Low reach may indicate poor timing, weak hook or algorithm limitation.
```

## 12.3. Engagement Metrics

Measures how audiences interacted with the content.

```text
Question: "How did people interact with this content?"

Normalized metrics:
    likes
    reactions
    comments
    shares
    saves
    reposts
    replies

Relevance:
    Primary for engagement and community goals.
    Saves indicate reference/educational value.
    Shares/Reposts indicate viral potential.
    Comments indicate conversation and depth of interest.
    High engagement ratio relative to reach indicates strong resonance.
```

## 12.4. Attention / Retention Metrics

Measures how long and how completely audiences consumed the content.

```text
Question: "Did people actually consume the content, and how deeply?"

Normalized metrics:
    watch_time_seconds
    average_watch_seconds
    completion_rate
    retention_rate
    scroll_depth_percent
    view_duration_seconds

Relevance:
    Critical for video and long-form content.
    High views but low completion signals weak content delivery.
    Strong retention with low reach may indicate content that resonates
    deeply with a smaller audience.
    Completion rate benchmarks vary significantly by content length.
```

## 12.5. Conversion Metrics

Measures actions beyond the content platform that drive business results.

```text
Question: "Did the content drive valuable actions beyond the platform?"

Normalized metrics:
    link_clicks
    profile_visits
    follows
    leads
    conversions
    revenue
    purchases
    signups
    subscription_starts

Relevance:
    Primary for lead generation, sales and traffic goals.
    High engagement with low conversion may indicate a CTA gap.
    High conversion with low reach indicates efficient but narrow content.
    Link click data combined with UTM tracking enables attribution.
```

## 12.6. Negative Metrics

Measures adverse audience responses.

```text
Question: "Did the content produce negative or adverse responses?"

Normalized metrics:
    unfollows
    unsubscribes
    hides
    reports
    dislikes
    negative_feedback_count

Relevance:
    Warning signals for content strategy.
    Spikes in negative metrics after publication may indicate:
        - topic mismatch with audience expectations;
        - tone violation;
        - controversial or divisive content (even if high engagement);
        - aggressive CTA causing audience rejection.
    Negative metrics must be interpreted in context — a single unfollow
    may not be meaningful; a pattern across multiple posts is.
```

## 12.7. Operational Metrics

Measures process quality — how efficiently content moved from production
to publication to measurement.

```text
Question: "How well did the publication and measurement process function?"

Operational metrics (derived from distribution and analytics context):
    export_to_publish_delay     — time between export and publication
    publication_attempt_count   — how many attempts were needed
    approval_delay              — time spent in approval gates
    checklist_completion        — whether the publication checklist was completed
    publication_error           — whether errors occurred during publication
    metric_collection_delay     — time between publication and metric snapshot
    metric_completeness         — percentage of expected metrics actually collected

Relevance:
    Operational metrics reveal process inefficiencies.
    High delay between export and publish may reduce content freshness.
    Multiple publication attempts signal distribution friction.
    Missing checklist steps may correlate with publication errors.
    These metrics feed into Learning Memory for operational optimization,
    not content strategy.
```

## 12.8. Quality / Confidence Metrics

Measures how reliable the metric data itself is.

```text
Question: "How much should we trust these metrics and the conclusions
           drawn from them?"

Normalized metrics:
    data_completeness           — percentage of expected metrics that are available
    source_confidence           — reliability of the metric source
    metric_freshness            — how recently metrics were collected
    manual_vs_connector         — indicates collection reliability
    collection_error_count      — number of errors during metric collection

Relevance:
    High confidence is required before Analytics can make strong
    interpretations.
    Low confidence metrics should be flagged and may require human review.
    Manual metrics typically have lower confidence than connector metrics.
    Missing critical metrics lower completeness and confidence.
    Future decisions informed by low-confidence data should carry
    appropriate caveats.
```

---

# 13. MetricSnapshot

## 13.1. Definition

`MetricSnapshot` is a Foundation MVP entity that captures the performance
of a publication at a specific point in time or across a defined
collection window.

It is the primary output of the Analytics Layer and the primary input
for Learning Memory extraction.

Reference: `DATA_MODEL.md`, Section 7.7

## 13.2. MetricSnapshot Entity (Conceptual Extension)

```text
MetricSnapshot:
    metric_snapshot_id          — unique identifier
    project_id                  — project scope
    content_item_id             — the content being measured
    publication_id              — the publication being measured
    export_package_id           — the package source
    channel_id                  — the channel published to
    platform                    — platform identifier

    collected_at                — when this snapshot was created/recorded
    collection_window_start     — start of the metric observation period
    collection_window_end       — end of the metric observation period

    source_type                 — manual, connector, import, hybrid
    snapshot_status             — draft, partial, complete, stale, failed, superseded

    raw_metric_refs             — references to RawMetricRecord entities (future)
    raw_metrics                 — embedded raw metric values (current MVP)

    normalized_metrics          — key-value pairs of normalized metric names and values
        reach: {impressions: 1200, reach: 980, views: 1100}
        engagement: {likes: 85, comments: 12, saves: 34, shares: 8}
        attention: {watch_time_seconds: null, completion_rate: null}
        conversion: {link_clicks: 15, follows: 3}
        negative: {unfollows: 0, hides: 0}
        operational: {export_to_publish_delay_hours: 4.5, attempt_count: 1}

    derived_metrics             — computed metrics from normalized base metrics
        engagement_rate: 7.73
        click_through_rate: 1.25
        save_rate: 2.83
        share_rate: 0.67
        comment_rate: 1.00

    completeness_score          — 0.0–1.0: how complete is the metric data
    confidence_score            — 0.0–1.0: how reliable is the data and interpretation
    notes                       — operator or system notes
    created_at                  — when the snapshot was created
    updated_at                  — last modification timestamp
```

## 13.3. Snapshot Statuses

| Status | Description | Current/Future |
|---|---|---|
| `draft` | Snapshot created but metrics not yet populated | Current MVP |
| `partial` | Some metrics populated, some missing | Current MVP |
| `complete` | All expected metrics collected | Current MVP |
| `stale` | Metrics are older than the freshness threshold | Future |
| `failed` | Metric collection or normalization failed | Future |
| `superseded` | A newer snapshot exists for the same publication and window | Future |

### Current MVP Snapshot Status Flow

```text
draft
    │  Snapshot created for publication
    ↓
partial
    │  Some metrics entered; some still missing
    ↓
complete
    │  All expected metrics collected
    │
    ├── (remains complete — no further updates in MVP)
    │
    └── (may be archived for history)
```

### Future Snapshot Status Flow

```text
draft
    ↓
partial
    ↓
complete
    ↓
stale           — if not refreshed within freshness window
    ↓
superseded      — replaced by newer snapshot for same window
    ↓
archived        — retained for history
    │
    └── failed  — collection failed at any stage
```

## 13.4. MetricSnapshot and Publication

Each MetricSnapshot references exactly one Publication. A single
Publication may have multiple MetricSnapshots over time (future
time-series snapshots).

```text
Publication (content_042, LinkedIn)
    ├── MetricSnapshot (24h after publication)
    ├── MetricSnapshot (72h after publication)
    ├── MetricSnapshot (7d after publication)
    └── MetricSnapshot (30d after publication)

Current MVP:
    One MetricSnapshot per publication, typically manual.
```

## 13.5. Current MVP Behaviour

In the current Foundation MVP:

- `find_metric_snapshots.py` locates draft snapshots;
- `import_manual_metrics.py` imports manual metrics into a draft snapshot;
- `clicks` input is normalized to `link_clicks`;
- `published_url` updates the related `Publication`;
- `published_url` is not stored as a raw metric field inside the snapshot;
- snapshot status flows: draft → partial → complete/failed.

---

# 14. Derived Metrics

## 14.1. Definition

Derived Metrics are computed from normalized base metrics. They provide
ratios, rates and composite indicators that enable comparison across
content items of differing scale.

Base metrics (e.g., likes = 85) are absolute values.
Derived metrics (e.g., engagement_rate = 7.73%) are relative values.

## 14.2. Derived Metric Catalog

### Engagement Rate

```text
Metric: engagement_rate
Formula: (likes + comments + saves + shares) / impressions * 100

Purpose:
    Measures the percentage of people who saw the content and
    interacted with it. Normalizes engagement for comparison
    across content items with different reach.

Notes:
    - Some platforms provide native engagement rate (use if available).
    - In platforms where "reach" is more meaningful than "impressions"
      (e.g., Instagram), use reach as the denominator.
    - If denominator is 0 or unavailable, derived metric is unavailable.
```

### Click-Through Rate (CTR)

```text
Metric: click_through_rate
Formula: link_clicks / impressions * 100

Purpose:
    Measures how effectively the content drove link clicks relative
    to the audience that saw it.

Notes:
    - Different platforms may define "clicks" differently.
    - UTM-tagged links enable more precise click tracking.
    - If link_clicks or impressions are unavailable, CTR is unavailable.
```

### Save Rate

```text
Metric: save_rate
Formula: saves / impressions * 100

Purpose:
    Measures how many viewers found the content valuable enough to
    save for later reference. Strong indicator of educational or
    practical content value.

Notes:
    - Not all platforms support saves (e.g., Telegram).
    - High save rate with low engagement suggests content is seen as
      reference material, not conversational.
```

### Share Rate

```text
Metric: share_rate
Formula: shares / impressions * 100

Purpose:
    Measures viral distribution — how many viewers shared the content
    with their own audience.

Notes:
    - Shares/reposts/forwards may be measured differently per platform.
    - High share rate indicates content that audiences want to associate
      with or endorse.
```

### Comment Rate

```text
Metric: comment_rate
Formula: comments / impressions * 100

Purpose:
    Measures conversation depth — how many viewers engaged in discussion.

Notes:
    - Comments are a deeper form of engagement than likes.
    - High comment rate with high save rate suggests authoritative
      content that sparks discussion.
    - High comment rate with low save rate may indicate controversial
      content.
```

### Completion Rate

```text
Metric: completion_rate
Formula: number_of_viewers_who_completed / number_of_viewers_who_started * 100

Purpose:
    Measures how many viewers watched a video to the end.
    Critical for video content evaluation.

Notes:
    - Not all platforms provide completion data.
    - Completion rate benchmarks vary by video length:
      - 15-second video: 60–80% may be normal.
      - 60-second video: 40–60% may be normal.
      - 3-minute video: 20–40% may be normal.
    - If completion data is unavailable, derived metric is unavailable.
```

### Conversion Rate

```text
Metric: conversion_rate
Formula: conversions / unique_viewers * 100
         OR: conversions / link_clicks * 100 (click-to-conversion)

Purpose:
    Measures how effectively content drove desired business outcomes.

Notes:
    - "Conversion" must be defined per project (signup, purchase, lead).
    - Attribution to specific content may be probabilistic.
    - Without conversion tracking infrastructure, this metric is
      typically unavailable.
```

### Revenue Per View

```text
Metric: revenue_per_view
Formula: revenue / views

Purpose:
    Measures the monetary efficiency of content.

Notes:
    - Only applicable when direct revenue attribution is possible.
    - Typically unavailable for organic social content.
    - Relevant for future paid/commerce channels.
```

### Cost Per Click (Future)

```text
Metric: cost_per_click
Formula: total_spend / link_clicks

Purpose:
    Measures paid media efficiency.

Notes:
    - Only applicable for paid/promoted content.
    - Requires ad spend data from platform or external source.
    - Future capability.
```

### Cost Per Lead (Future)

```text
Metric: cost_per_lead
Formula: total_spend / leads

Purpose:
    Measures lead generation cost efficiency.

Notes:
    - Future paid channel capability only.
```

### Error Rate (Publication Operations)

```text
Metric: publication_error_rate
Formula: failed_attempts / total_attempts * 100

Purpose:
    Measures publication process reliability.

Notes:
    - Multiple attempts per publication are recorded in PublicationAttempt.
    - High error rate signals distribution process issues.
```

## 14.3. Derived Metric Availability Rules

1. **If the required base metric is unavailable**, the derived metric is
   `unavailable` — not zero, not omitted.

2. **If the denominator is zero** (e.g., impressions = 0), the derived
   metric is `unavailable` — division by zero is undefined.

3. **If the denominator is very small** (e.g., impressions < 10), the
   derived metric is computed but flagged with a `low_sample_size` warning.
   Confidence is reduced.

4. **Derived metrics depend on base metrics.** If base metrics are
   incomplete or low-confidence, derived metrics inherit that
   uncertainty.

---

# 15. Performance Evaluation

## 15.1. Purpose

Performance Evaluation is the stage where Analytics compares the
MetricSnapshot against goals, baselines and expectations to determine
how well the content performed.

Performance Evaluation answers:

- Did this content achieve its goal?
- How does performance compare to historical baselines?
- What signals (positive, negative, anomalous) are present?
- How confident are we in this evaluation?

## 15.2. Evaluation Inputs

| Input | Source | Required |
|---|---|---|
| `MetricSnapshot` | Analytics (populated) | Yes |
| Content goal | Production Brief / Scenario | Preferred |
| Channel | Distribution / Publication | Yes |
| Content type | Production Brief / ContentItem | Yes |
| Expected benchmark | Project historical baseline or manual target | No |
| Historical baseline | Previous MetricSnapshots for the project | No |
| Learning Memory context | Embedded in Scenario/Brief | No |
| Production context | Production Snapshot | No |
| Distribution context | Distribution / AnalyticsHandoffRecord | No |

## 15.3. Evaluation Dimensions

### 15.3.1. Goal Alignment

```text
Question: "Did the content serve its intended goal?"

Check:
    - If goal = awareness: did reach/impressions exceed baseline?
    - If goal = engagement: did likes/comments/saves/shares exceed baseline?
    - If goal = traffic: did link_clicks exceed baseline?
    - If goal = leads: did leads/conversions meet or exceed target?
    - If goal = sales: did revenue/conversions meet or exceed target?
    - If goal = retention: did positive engagement signals exceed baseline?

If goal is unknown, goal alignment evaluation is unavailable.
```

### 15.3.2. Channel Performance

```text
Question: "Did the content perform well on this specific channel?"

Check:
    - How does performance compare to the channel's historical average?
    - Is this channel typically effective for this content type?
    - Did the channel's constraints affect content delivery?
```

### 15.3.3. Content Type Performance

```text
Question: "Did this content type perform as expected?"

Check:
    - How does this content type typically perform for this audience?
    - Does the content type's expected metric profile match the actual?
    - Are metric patterns consistent with this content type's norm
      (e.g., carousels typically have higher save rates)?
```

### 15.3.4. Audience Response

```text
Question: "How did the target audience respond?"

Check:
    - Were engagement signals positive or negative?
    - Did the audience save, share, comment — or ignore, hide, unfollow?
    - Is the audience response consistent with the target segment's
      known behaviour patterns?
```

### 15.3.5. Conversion Impact

```text
Question: "Did the content drive valuable actions?"

Check:
    - Did link clicks, follows, leads, or conversions occur?
    - Was the CTA effective?
    - Is the conversion performance consistent with the content goal?
```

### 15.3.6. Operational Quality

```text
Question: "Did the publication and measurement process function well?"

Check:
    - Was the publication delayed after export?
    - Were there publication errors or multiple attempts?
    - Was the checklist completed?
    - Was the metric collection timely?
```

### 15.3.7. Data Confidence

```text
Question: "How reliable is this evaluation given the data quality?"

Check:
    - What is the completeness score of the MetricSnapshot?
    - What is the confidence score?
    - Were critical metrics missing?
    - Was the data source manual or connector?
```

## 15.4. PerformanceEvaluation Entity (Conceptual)

```text
PerformanceEvaluation:
    evaluation_id              — unique identifier
    metric_snapshot_id         — the snapshot being evaluated
    publication_id             — the publication being measured
    content_item_id            — the content being analyzed

    goal                       — the content goal (awareness, engagement, etc.)
    goal_alignment_score       — 0.0–1.0: how well the content served its goal
    channel_performance_score  — 0.0–1.0: how performance compares to channel baseline
    content_type_performance_score — 0.0–1.0: how performance compares to content type norms

    success_level              — strong_positive, positive, neutral, weak, negative,
                                 inconclusive
    key_observations           — list of top findings
    anomalies                  — list of anomalies detected
    confidence                 — 0.0–1.0: confidence in this evaluation
    evaluation_notes           — human-readable evaluation text
    evaluated_at               — when evaluation was performed
```

## 15.5. Success Levels

| Success Level | Meaning | Typical Indicators |
|---|---|---|
| `strong_positive` | Content significantly exceeded goals and baselines | All key metrics above baseline by significant margin; strong goal alignment |
| `positive` | Content met or moderately exceeded goals | Key metrics at or above baseline; goal served |
| `neutral` | Content performed within normal range | Metrics near baseline; goal partially served |
| `weak` | Content underperformed relative to baseline | Key metrics below baseline; goal not well served |
| `negative` | Content performed poorly or produced adverse effects | Metrics significantly below baseline; negative signals present; goal not served |
| `inconclusive` | Not enough data to determine performance | Critical metrics missing; low confidence; insufficient sample size |

## 15.6. Evaluation Rules

1. **If no baseline exists**, comparison to baseline is marked as
   `unavailable`. Goal alignment is evaluated against the goal definition
   alone.

2. **If goal is unknown**, goal alignment is `unavailable`. The evaluation
   focuses on absolute metrics rather than goal-based assessment.

3. **If confidence is low**, success_level should lean toward `inconclusive`
   or carry a low-confidence flag. Low-confidence data should not produce
   strong conclusions.

4. **If sample size is small** (e.g., impressions < 100), derived rates
   are unreliable. The evaluation should note this.

5. **Evaluation is a tool output**, not a strategic decision. Analytics
   says "strong_positive." The Orchestrator decides what to do with that
   information.

---

# 16. Benchmarks and Baselines

## 16.1. Definition

A **benchmark** or **baseline** is a reference point against which
content performance is compared.

Without a baseline, metrics are absolute numbers with no context.
With a baseline, the same metrics become performance signals.

## 16.2. Baseline Types

### 16.2.1. Project Historical Baseline

```text
Definition:
    The average or median performance of previous content items
    within the same project, filtered by content type, channel
    and goal where applicable.

Calculation (conceptual):
    For each normalized metric:
        - Collect MetricSnapshot values for the last N cycles.
        - Compute mean, median and standard deviation.
        - (Future) segment by content type, channel, goal.

Requirements:
    - At least 3 published content items with MetricSnapshots.
    - Less than 3 items → baseline unavailable or very low confidence.

Status:
    Conceptual. Current MVP may use simplified comparison
    (e.g., previous snapshot as the only reference).
```

### 16.2.2. Channel Baseline

```text
Definition:
    Performance baseline specific to a distribution channel.
    "How does this content perform compared to the average LinkedIn
     post for this project?"

Status:
    Future. Requires sufficient per-channel MetricSnapshots.
```

### 16.2.3. Content Type Baseline

```text
Definition:
    Performance baseline specific to a content type.
    "How does this carousel perform compared to the average
     carousel for this project?"

Status:
    Future. Requires sufficient per-content-type MetricSnapshots.
```

### 16.2.4. Campaign Baseline

```text
Definition:
    Performance baseline for a specific campaign or content series.
    "How does this item compare to others in the 'AI Tools' campaign?"

Status:
    Future.
```

### 16.2.5. Manually Defined Target

```text
Definition:
    A human-defined target value for key metrics.
    "We expect this post to reach at least 1,000 impressions."

Status:
    Current MVP. Operators can define manual targets.
```

### 16.2.6. Industry Baseline (Optional / Future)

```text
Definition:
    External industry benchmark data.
    "Average engagement rate for B2B LinkedIn posts is 2.5%."

Status:
    Future / optional. Not a dependency for core analytics.
    If available, provides additional context.
```

### 16.2.7. No Baseline

```text
Definition:
    No reference point is available for comparison.

Action:
    Comparison is marked as unavailable.
    Analytics evaluates absolute metrics only.
    Success level is determined with lower confidence.
```

## 16.3. Baseline Rules

1. **Do not fake benchmarks.** If no baseline exists, mark comparison
   as `unavailable`. Do not invent default values.

2. **Early MVP may use simple comparisons.** Comparing current
   MetricSnapshot against the previous snapshot is valid for early
   stages.

3. **Low sample size must lower confidence.** A baseline derived from
   3 data points has less confidence than one derived from 30.

4. **Baselines should age.** A baseline from 6 months ago may not
   reflect current platform dynamics. Baseline freshness should be
   tracked.

5. **Manually defined targets are valid.** If the operator defines a
   target ("reach 1,000 impressions"), this is a legitimate baseline
   for evaluation.

---

# 17. Analytics Summary

## 17.1. Purpose

The Analytics Summary is a structured, human-readable and machine-readable
summary of content performance. It condenses the MetricSnapshot, derived
metrics and performance evaluation into a single coherent result.

The Analytics Summary is NOT a Learning Memory entry. It is a summary
of what happened — the input from which Learning Memory may extract
durable knowledge.

## 17.2. AnalyticsSummary Entity (Conceptual)

```text
AnalyticsSummary:
    analytics_summary_id       — unique identifier
    metric_snapshot_id         — the snapshot this summarizes
    content_item_id            — the content being analyzed
    publication_id             — the publication being measured
    project_id                 — project scope

    goal                       — the content goal
    success_level              — strong_positive, positive, neutral, weak,
                                 negative, inconclusive

    top_positive_signals       — list of the strongest positive findings
        Example: "Save rate 2.8x above project historical baseline"
        Example: "Completion rate of 72% exceeds the 60% target"

    top_negative_signals       — list of the strongest negative findings
        Example: "Link click rate 60% below project baseline"
        Example: "Unfollow count 3x higher than average"

    anomalies                  — list of detected anomalies
        Example: "Engagement spike at hour 6 (unexplained)"
        Example: "Comments were 5x baseline, but sentiment was mixed"

    likely_causes              — plausible explanations for outcomes
        Example: "Educational angle + step-by-step structure likely
                  drove high save rate"
        Example: "CTA placed too late in video may have contributed
                  to low link clicks"

    confidence_score           — 0.0–1.0: confidence in this summary
    completeness_score         — 0.0–1.0: metric data completeness

    recommended_followup_type  — suggested category for follow-up action
        This is NOT an autonomous decision. It is a suggestion for
        the Orchestrator Agent or human operator to consider.

        Possible values:
            "candidate_for_reuse"          — format/approach worth repeating
            "candidate_for_revision"       — format/approach needs adjustment
            "needs_more_data"              — insufficient data for conclusions
            "possible_channel_mismatch"    — content may not fit this channel
            "possible_format_issue"        — content type may have been wrong
            "strong_asset_signal"          — assets used correlate with success
            "weak_hook_signal"             — hook may have underperformed
            "possible_timing_issue"        — publication time may have affected reach
            "operational_improvement_needed" — process issues identified
            "no_followup_suggested"        — no clear signal

        Forbidden values:
            "publish_10_more_immediately"  — autonomous action
            "double_budget"                — autonomous spending decision
            "change_strategy"              — strategy override without human

    learning_handoff_ready     — whether the summary is ready for
                                 Learning Memory handoff
    created_at                 — when the summary was created
    updated_at                 — last modification timestamp
```

## 17.3. Summary Generation Rules

1. **A summary can be generated from any MetricSnapshot** — even a
   partial or draft one. The completeness and confidence scores will
   reflect the data quality.

2. **If no metrics are available**, the summary status is `draft` or
   `needs_data`. The summary should not fabricate findings.

3. **The summary should state uncertainty explicitly.** "We do not
   have enough data to evaluate completion rate" is preferable to
   silence.

4. **`recommended_followup_type` is a suggestion, not a command.**
   It provides signal to the Orchestrator. It does not autonomously
   trigger actions.

5. **The Analytics Summary should be storable alongside the
   MetricSnapshot** for audit and Learning Memory retrieval.

---

# 18. Analytics Observations

## 18.1. Definition

An **AnalyticsObservation** is a structured fact or interpretation about
content performance — a single, specific finding derived from the
MetricSnapshot and evaluation.

Observations are NOT durable Learning Memory entries. They are candidate
signals that Learning Memory may or may not convert into lasting
knowledge.

Multiple cycles of consistent observations form the evidence base for
Learning Memory patterns. A single observation is a data point.

## 18.2. AnalyticsObservation Entity (Conceptual)

```text
AnalyticsObservation:
    observation_id             — unique identifier
    metric_snapshot_id         — the snapshot this observation is based on
    publication_id             — the publication context
    content_item_id            — the content context

    observation_type           — performance, behavioural, operational, anomaly
    severity                   — info, low, medium, high, critical

    evidence_metrics           — specific metric values supporting this observation
        Example: {save_rate: 2.83, baseline_save_rate: 0.85, delta_percent: +233}

    interpretation             — the analytical meaning
        Example: "This carousel had a significantly higher save rate
                  than the project baseline. The step-by-step structure
                  and educational angle likely made it valuable as
                  reference content."

    confidence                 — 0.0–1.0: how confident is this observation
    suggested_learning_category — which knowledge category this might inform:
        - content_type_performance
        - channel_performance
        - hook_performance
        - CTA_performance
        - asset_performance
        - template_performance
        - timing_performance
        - audience_response
        - operational_issue
        - insufficient_data

    created_at                 — when observation was generated
```

## 18.3. Observation Examples

```text
Example 1 — Positive Content Signal:

    observation_type: performance
    severity: low
    evidence_metrics:
        save_rate: 2.83%
        baseline_save_rate: 0.85%
        delta_percent: +233
    interpretation:
        "This carousel had high save rate compared to project baseline.
         The step-by-step structure and educational angle likely
         contributed."
    confidence: high
    suggested_learning_category: content_type_performance


Example 2 — Negative Content Signal:

    observation_type: performance
    severity: medium
    evidence_metrics:
        completion_rate: 22%
        average_completion_rate_for_type: 45%
        video_length_seconds: 180
    interpretation:
        "Video completion rate was low despite high initial views.
         The 3-minute length may exceed audience attention span for
         this channel. Drop-off occurred primarily after 45 seconds."
    confidence: medium
    suggested_learning_category: content_type_performance


Example 3 — Conversion Gap Signal:

    observation_type: behavioural
    severity: medium
    evidence_metrics:
        link_clicks: 120
        conversions: 2
        click_to_conversion_rate: 1.67%
        baseline_click_to_conversion_rate: 5.2%
    interpretation:
        "Link clicks were strong, but conversions were weak. The landing
         page or offer may not be aligned with the content's value
         proposition. Attractive hook, weak follow-through."
    confidence: medium
    suggested_learning_category: CTA_performance


Example 4 — Operational Signal:

    observation_type: operational
    severity: low
    evidence_metrics:
        export_to_publish_delay_hours: 18.5
        average_delay_for_project: 2.0
    interpretation:
        "Manual publication delay was unusually high — 18.5 hours
         between export and publish, compared to the project average
         of 2 hours. This may have affected timing-dependent reach."
    confidence: medium
    suggested_learning_category: operational_issue


Example 5 — Audience Confusion Signal:

    observation_type: behavioural
    severity: medium
    evidence_metrics:
        comment_count: 32
        comments_with_question_about_cta: 9
        comment_sentiment_mixed: true
    interpretation:
        "Caption comments indicate confusion around the CTA. Multiple
         users asked where to click or what action to take. The CTA
         may have been unclear or placed in an unexpected position."
    confidence: medium
    suggested_learning_category: CTA_performance
```

## 18.4. Observation vs Learning Record

```text
AnalyticsObservation (this layer):
    "This specific content item had a high save rate."

LearningRecord (Learning Memory):
    "Educational carousels with step-by-step frameworks produce
     3x higher save rates than theoretical carousels for professional
     audiences on LinkedIn. Evidence: 14 cycles."

Observation = single data point.
Learning Record = evidence contributing to a pattern.
Performance Pattern = validated, repeatable knowledge.
```

Analytics produces Observations. Learning Memory accumulates them into
patterns over time.

---

# 19. Anomaly Detection — Conceptual

## 19.1. Purpose

Anomaly detection flags unusual performance — outcomes that deviate
significantly from expected patterns.

An anomaly is not inherently good or bad. It is a signal that something
unusual happened and warrants attention.

## 19.2. AnomalyFlag Entity (Conceptual)

```text
AnomalyFlag:
    anomaly_id                 — unique identifier
    metric_snapshot_id         — the snapshot containing the anomaly
    publication_id             — the publication context
    anomaly_type               — type of anomaly detected
    detected_metric            — which metric exhibited the anomaly
    expected_value             — what the value was expected to be
    actual_value               — what the value actually was
    deviation_percent          — percentage deviation from expected
    severity                   — info, low, medium, high, critical
    possible_explanations      — list of plausible reasons
    requires_investigation     — whether this anomaly warrants deeper analysis
    created_at                 — when the anomaly was detected
```

## 19.3. Anomaly Types

| Anomaly Type | Description | Example |
|---|---|---|
| `unusually_high_engagement` | Engagement significantly above baseline | Post with 3x normal saves |
| `unusually_low_engagement` | Engagement significantly below baseline | Post with 70% fewer likes than normal |
| `high_reach_low_engagement` | Content reached many but few interacted | 5,000 impressions, 3 likes |
| `high_clicks_low_conversion` | Many clicked but few converted | Attractive hook, weak landing page |
| `high_negative_feedback` | Unusual spike in negative signals | Post with 5x normal unfollows |
| `metric_spike` | Sudden increase in a metric at a specific time | Views spiking 24h after publication |
| `metric_drop` | Sudden decrease in a metric | Engagement dropping to near zero |
| `missing_metrics` | Expected metrics not available | Platform connector returned empty data |
| `suspicious_data` | Data that appears implausible | "1,000,000 impressions" for a small account |
| `publication_error_impact` | Publication error affected metric availability | Failed first attempt may have delayed reach |

## 19.4. Anomaly Detection Approach

### Current MVP

Anomaly detection is not implemented. Metrics are manual and limited.

### Future Stage 1 — Rule-Based

```text
Simple threshold rules:
    - If metric > baseline * 2.0 → flag as unusually high.
    - If metric < baseline * 0.5 → flag as unusually low.
    - If negative_feedback > 0 and > baseline * 3.0 → flag.
    - If critical metric is missing → flag as missing_metrics.
```

### Future Stage 2 — Statistical

```text
Statistical deviation detection:
    - Mean, standard deviation from historical data.
    - Flag values beyond 2 standard deviations.
    - Flag values beyond 3 standard deviations as critical.
```

## 19.5. Important Constraints

1. **Do not implement anomaly detection algorithms** in the current MVP.
   This section describes the conceptual model for future implementation.

2. **Anomalies are flags, not conclusions.** An anomaly says "this is
   unusual." It does not say "this is good," "this is bad," or "this
   is why." Interpretation requires human or agent analysis.

3. **Low sample size produces unreliable anomalies.** With 3 data points,
   statistical deviation detection is meaningless.

4. **False positives are expected.** Anomaly detection should err toward
   flagging too much (and letting a human or agent filter) rather than
   missing genuine anomalies.

---

# 20. Data Completeness and Confidence

## 20.1. Purpose

Not all MetricSnapshots are equally reliable. Analytics must quantify
how complete the data is and how confident it is in the data and
interpretation.

## 20.2. Completeness Score

The completeness score measures what percentage of expected metrics are
actually available.

### 20.2.1. Calculation (Conceptual)

```text
completeness_score = number_of_available_expected_metrics /
                     total_number_of_expected_metrics

Where:
    "expected metrics" = the set of metrics defined as relevant for
    this content type, channel and goal.

    "available" = metric value is present and not marked as unavailable.

Example:
    For a carousel on Instagram with awareness goal:
        Expected metrics: impressions, reach, likes, comments, saves,
                           shares, link_clicks, follows
        Total expected: 8
        Available: impressions, reach, likes, comments, saves (5)
        Unavailable: shares, link_clicks, follows (3)

        completeness_score = 5 / 8 = 0.625
```

### 20.2.2. Completeness Score Ranges

| Range | Label | Meaning |
|---|---|---|
| 0.9–1.0 | Excellent | Nearly all expected metrics available |
| 0.7–0.89 | Good | Most expected metrics available |
| 0.5–0.69 | Partial | Significant metric gaps |
| 0.3–0.49 | Poor | Most metrics unavailable |
| 0.0–0.29 | Minimal | Very few metrics available; snapshot is draft-like |

## 20.3. Confidence Score

The confidence score measures how reliable the data and resulting
interpretation are — combining source reliability, completeness,
freshness and other factors.

### 20.3.1. Confidence Factors

| Factor | How It Affects Confidence |
|---|---|
| **Source type** | Manual metrics → lower confidence. Connector metrics → higher confidence. |
| **Metric completeness** | More complete data → higher confidence. |
| **Metric freshness** | Recently collected data → higher confidence. Older data → lower confidence. |
| **Sample size** | Large audience (many impressions/reach) → higher confidence. Small audience → lower confidence. |
| **Manual entry reliability** | Consistent manual recording → medium confidence. Irregular/ad-hoc → lower confidence. |
| **Platform metric reliability** | Some platforms have known metric inaccuracies. This lowers confidence. |
| **Collection errors** | Errors during collection reduce confidence. |
| **Baseline availability** | Having a baseline for comparison increases evaluation confidence. No baseline → lower confidence. |
| **Baseline quality** | Baseline derived from many cycles → higher confidence. From few cycles → lower. |
| **Anomaly presence** | Unexplained anomalies reduce confidence in interpretation. |

### 20.3.2. Confidence Score Ranges

| Range | Label | Meaning |
|---|---|---|
| 0.8–1.0 | High | Data is reliable. Interpretation is well-supported. |
| 0.6–0.79 | Medium | Data is adequate but with some uncertainty. |
| 0.4–0.59 | Low | Data has significant gaps or reliability concerns. |
| 0.0–0.39 | Very Low | Data is unreliable. Interpretation should not be used for decisions. |

## 20.4. Confidence Rules

1. **Manual metrics may have lower confidence** than connector metrics
   by default (e.g., manual baseline confidence = 0.7; connector
   baseline = 0.9).

2. **Missing critical metrics lower completeness**, which lowers
   confidence. A missing `impressions` metric makes it impossible to
   compute engagement rate — a critical derived metric.

3. **No baseline lowers evaluation confidence.** Even if metric data
   is complete, without a reference point the interpretation is less
   reliable.

4. **Small audience size lowers confidence.** An engagement rate from
   50 impressions is less reliable than one from 5,000 impressions.

5. **Confidence should be transparent.** Every MetricSnapshot,
   PerformanceEvaluation and AnalyticsSummary should display its
   confidence score. Low-confidence data should not be presented as
   definitive.

---

# 21. Time Windows and Snapshot Refresh

## 21.1. Purpose

Content performance changes over time. A MetricSnapshot taken 1 hour
after publication captures different data than one taken 7 days after.

Time windows define when metrics are collected and what period they
represent.

## 21.2. Current MVP

In the current MVP:

- one manual snapshot per publication;
- the collection time is recorded manually;
- no schedule or automated refresh exists;
- the operator records metrics at whatever time they choose.

## 21.3. Future Time Windows

```text
Time windows for MetricSnapshots:

    1-hour snapshot:
        Captures initial performance burst.
        Relevant for viral/real-time content.
        Typically sparse — only fast-accumulating metrics.
        Status: future.

    24-hour snapshot:
        Captures first full day of performance.
        Most platforms provide daily metrics.
        Primary snapshot for social media content.
        Status: future.

    72-hour snapshot:
        Captures extended engagement after initial burst.
        Reveals content longevity vs flash performance.
        Some content types (carousels, articles) show delayed engagement.
        Status: future.

    7-day snapshot:
        Captures a full week of performance.
        Standard analytics window for most platforms.
        Good baseline for comparison.
        Status: future.

    30-day snapshot:
        Captures long-tail performance.
        Reveals evergreen potential.
        Suitable for articles, videos, high-save content.
        Status: future.

    Final snapshot:
        The last snapshot for a publication.
        Captures total performance.
        Archived as the definitive record.
        Status: future.
```

## 21.4. Snapshot Refresh

In future connector-based analytics:

- a MetricSnapshot may be refreshed at defined intervals;
- the same snapshot window may receive updated data (e.g., the 7-day
  snapshot is refreshed daily until day 7);
- when a snapshot is refreshed, the previous version is superseded;
- `snapshot_status` transitions: `complete` → `superseded` (replaced
  by newer data for the same window).

## 21.5. Time Window Rules

1. **A MetricSnapshot always represents a defined time window.**
   If the operator records metrics "at some point after publication,"
   the window is the time between publication and collection.

2. **Snapshots from different time windows are not directly comparable.**
   A 24-hour snapshot from one publication should not be compared to a
   7-day snapshot from another without normalization.

3. **In the current MVP**, the time window is implicit: "from publication
   time to metric collection time." This is sufficient for manual
   measurement.

4. **Do not implement scheduling** in the current MVP. This section
   describes the conceptual model for future automated collection.

---

# 22. Cross-Channel Comparison — Future

## 22.1. Purpose

A single ContentItem may be published to multiple channels. Cross-channel
comparison evaluates how the same content performs across different
platforms.

## 22.2. Comparison Types

```text
Same content, different channels:
    "How did the carousel 'AI Tools for Business' perform on
     LinkedIn vs Instagram?"

Same content type, different channels:
    "How do educational carousels perform on LinkedIn vs Instagram
     in general?"

Same campaign, different channels:
    "For the 'Productivity Series' campaign, which channel drove
     the most engagement?"

Same asset/template, different channels:
    "Does template A perform better on LinkedIn or Instagram?"
```

## 22.3. Comparison Rules

1. **Compare only normalized metrics.** Do not compare raw Instagram
   metrics against raw LinkedIn metrics. Normalize first.

2. **Respect platform differences.** LinkedIn engagement patterns
   differ from Instagram patterns. Flag platform-specific context
   when interpreting comparisons.

3. **Avoid false equivalence.** "Views" on YouTube (counted after 30
   seconds) ≠ "views" on Instagram (counted after 3 seconds). The
   normalization layer should document these differences.

4. **Confidence depends on comparable data.** If one channel has
   extensive historical data and the other has minimal data, the
   comparison has low confidence.

5. **Channel audience overlap** may affect comparison. The same
   audience may follow the brand on multiple channels.

## 22.4. Current MVP

Cross-channel comparison is not implemented. The current MVP typically
produces one publication per channel and may not have enough data for
meaningful comparison.

---

# 23. Relationship with Content Types

## 23.1. Content Types Define Expected Metric Profiles

Different content types produce different metric profiles. Analytics
must evaluate content according to its type, not against a generic
standard.

## 23.2. Primary Metrics by Content Type

### Text Social Post

```text
Primary metrics:
    impressions, reach, likes, comments, shares, link_clicks

Key derived metrics:
    engagement_rate, comment_rate, click_through_rate

Evaluation focus:
    Did the text drive discussion (comments) and/or action (clicks)?
    Was the hook effective in capturing attention?
    Did the CTA drive the intended action?
```

### Carousel

```text
Primary metrics:
    impressions, reach, likes, comments, saves, shares, link_clicks

Key derived metrics:
    engagement_rate, save_rate, share_rate, click_through_rate

Evaluation focus:
    Did the carousel drive saves (educational value)?
    Was the slide-through/completion rate high?
    Did the visual structure maintain audience attention?
```

### Short Vertical Video

```text
Primary metrics:
    views, likes, comments, shares, saves, follows
    watch_time_seconds, average_watch_seconds, completion_rate

Key derived metrics:
    engagement_rate, completion_rate, share_rate

Evaluation focus:
    Did the hook retain viewers beyond 3 seconds?
    Was the completion rate consistent with the video length?
    Did the video drive shares (viral potential) or follows (growth)?
```

### Article / Long-Form Content

```text
Primary metrics:
    views/reads, scroll_depth_percent, time_on_page_seconds,
    link_clicks, shares, comments

Key derived metrics:
    completion_rate (scroll depth proxy), share_rate,
    click_through_rate

Evaluation focus:
    Did readers engage deeply with the content?
    Did the content drive referral traffic (shares)?
    Was the CTA effective after deep engagement?
```

### Product / Conversion Content

```text
Primary metrics:
    impressions, link_clicks, conversions, revenue,
    profile_visits, leads

Key derived metrics:
    click_through_rate, conversion_rate, revenue_per_click

Evaluation focus:
    Did the content drive purchase intent?
    Was the conversion rate above baseline?
    Did the CTA effectively bridge interest to action?
```

## 23.3. Analytics Does NOT Change the Content Type

Analytics uses the content type to contextualize evaluation. It does
not change what type the content is. Production Pipeline defines the
content type. Analytics evaluates performance within that type's
expected patterns.

---

# 24. Relationship with Production Snapshot

## 24.1. Production Snapshot Provides Context

The Production Snapshot is included in the ExportPackage and passed
through Distribution to Analytics. It contains:

- content_type — which content type was produced;
- production_variant — which production variant was used;
- assets_used — which assets were selected and used;
- template_version — which template was applied;
- generation_method — how content was generated (AI model, template, manual);
- QA_warnings — any warnings from the QA stage;
- export_metadata — format, resolution, duration, other technical details.

Reference: `PRODUCTION_PIPELINE_SPEC.md`, Section 11; `DISTRIBUTION_SPEC.md`, Section 4.4

## 24.2. How Analytics Correlates Production Context

Analytics can correlate performance with production decisions:

```text
Content type correlation:
    "Do educational carousels consistently outperform storytelling
     carousels for this audience?"

Production variant correlation:
    "Does stock footage video outperform AI-generated visual video
     for educational content?"

Asset correlation:
    "Does template A produce higher engagement than template B?"

Template version correlation:
    "Did the version 2.0 carousel template improve save rate?"

QA warning correlation:
    "Do posts published with QA warnings underperform posts that
     passed cleanly?"

Generation method correlation:
    "Does AI-generated text perform differently from human-written
     text?"
```

## 24.3. Analytics Does NOT Update Production Rules

Analytics identifies correlations. It does not:

- change which production variants are used;
- modify templates;
- update asset selection rules;
- alter generation parameters;
- rewrite the Production Brief.

These decisions belong to the Intelligence Layer (Orchestrator Agent),
informed by Learning Memory. Analytics provides the evidence. The system
decides how to use it.

## 24.4. Analytics Does NOT Update Asset Library

Analytics may note that Asset X correlated with high performance. It
does not:

- change asset quality scores;
- update asset usage preferences;
- modify asset lifecycle status;
- flag assets for reuse or deprecation.

The Asset Library is a Production Layer subsystem. Learning Memory may
inform Asset Library preferences based on analytics data, but Analytics
does not write to Asset Library directly.

---

# 25. Relationship with Distribution Context

## 25.1. Distribution Context Enriches Analysis

The Distribution Context, passed from Distribution via the
AnalyticsHandoffRecord, provides operational data that Analytics uses
to identify process-related performance factors.

## 25.2. Distribution Context Fields and Their Use

| Field | Analytics Use |
|---|---|
| `publication_time` | Compare against timing baselines. Did timing affect reach? |
| `delay_between_export_and_publish` | Identify operational lag. Does delay correlate with lower reach? |
| `publication_mode` | Manual vs connector. Does mode affect timeliness or completeness? |
| `approval_required` / `approval_count` | Did approval process delay publication? |
| `attempt_count` | Did multiple publication attempts affect timing or cause errors? |
| `checklist_completed` | Was the manual process followed? Does checklist completion correlate with fewer errors? |
| `preflight_passed` | Did pre-publication checks catch issues? |
| `link_used` / `UTM_parameters` | Validate link tracking setup. Were UTM parameters correctly applied? |
| `publication_errors` | Did errors during publication affect metric availability? |

## 25.3. Example: Operational Issue Detection

```text
Scenario:
    A high-quality educational carousel was exported at 14:00.
    It was published manually at 08:30 the next day.
    delay_between_export_and_publish = 18.5 hours.

    The carousel reached below-average impressions for its content type.

Analytics observation:
    "Unusually long delay between export and publication (18.5 hours)
     may have contributed to lower reach. The planned publication time
     was during the optimal engagement window, but the actual time was
     outside it."

    suggested_learning_category: operational_issue

Learning Memory may later form a pattern:
    "Publications with export-to-publish delay > 6 hours show
     30% lower reach than publications published within 2 hours
     of export."
```

## 25.4. Analytics Does NOT Modify Distribution

Analytics identifies operational patterns. It does not:

- change publication schedules;
- modify approval rules;
- adjust channel mapping;
- alter UTM parameters;
- reconfigure distribution modes.

These are Distribution Layer and Project Settings responsibilities.
Analytics provides evidence that may inform future configuration
changes through the Intelligence Layer.

---

# 26. Learning Memory Handoff

## 26.1. Purpose

The Learning Memory Handoff is the defined boundary where Analytics
passes structured performance context to the Intelligence Layer for
knowledge extraction.

This handoff does NOT update Learning Memory directly. It provides the
structured input that Learning Memory's extraction process consumes.

Reference: `LEARNING_MEMORY_SPEC.md`, Section 7 — Learning Extraction Process

## 26.2. LearningMemoryHandoffPayload Entity (Conceptual)

```text
LearningMemoryHandoffPayload:
    handoff_id                 — unique identifier
    project_id                 — project scope

    metric_snapshot            — the evaluated MetricSnapshot
    performance_evaluation     — the PerformanceEvaluation result
    analytics_summary          — the AnalyticsSummary
    analytics_observations     — list of AnalyticsObservations

    production_context:
        content_type           — content type produced
        production_variant     — which variant was used
        assets_used            — which assets were selected
        template_version       — which template was applied
        generation_method      — how content was generated
        qa_warnings            — any QA warnings present

    distribution_context:
        channel                — which channel was published to
        publication_mode       — manual or connector
        publication_time       — actual publication timestamp
        export_to_publish_delay — delay between production and publication
        attempt_count          — how many publication attempts
        checklist_completed    — whether the checklist was followed
        publication_errors     — any errors during publication
        link_strategy          — UTM parameters used

    confidence_score           — overall confidence in the data and interpretation
    completeness_score         — metric data completeness

    suggested_learning_categories — categories of knowledge this data could inform:
        - content_type_performance
        - channel_performance
        - hook_performance
        - CTA_performance
        - asset_performance
        - template_performance
        - timing_performance
        - audience_response
        - operational_issue
        - insufficient_data

    handoff_timestamp          — when the handoff was performed
```

## 26.3. Suggested Learning Categories

Analytics suggests which categories of knowledge the data most strongly
relates to. Learning Memory uses these as routing hints — it decides
which categories to actually update.

```text
content_type_performance:
    The data contains signals about how a content type performed.
    Example: "Educational carousel had 40% higher save rate than baseline."

channel_performance:
    The data contains signals about channel effectiveness.
    Example: "LinkedIn post outperformed Instagram post for the same
             content with professional audience."

hook_performance:
    The data contains signals about hook effectiveness.
    Example: "Question-based hook retained 65% of viewers past 3 seconds;
             statement-based hook for same format retained 40%."

CTA_performance:
    The data contains signals about call-to-action effectiveness.
    Example: "Soft CTA ('Save for later') generated 3x more saves than
             direct CTA ('Sign up now')."

asset_performance:
    The data contains signals about specific asset effectiveness.
    Example: "Template B slides produced higher completion rate than
             Template A slides."

template_performance:
    The data contains signals about template/format structure.
    Example: "7-slide carousel outperformed 5-slide carousel for
             educational content."

timing_performance:
    The data contains signals about publication timing impact.
    Example: "Tuesday 10:00 publication reached 40% more audience than
             Saturday 14:00 publication."

audience_response:
    The data contains signals about how the audience reacted.
    Example: "Professional audience engaged more with practical tips
             than theoretical discussion."

operational_issue:
    The data contains signals about process quality or issues.
    Example: "Export-to-publish delay correlated with lower reach."

insufficient_data:
    Not enough data to extract meaningful signals.
    Example: "Too few impressions to evaluate engagement rate reliably.
             More data needed before forming conclusions."
```

## 26.4. What Learning Memory Does With the Handoff

Analytics hands off the payload. Learning Memory:

1. receives the `LearningMemoryHandoffPayload`;
2. runs its Learning Extraction Process (see `LEARNING_MEMORY_SPEC.md`,
   Section 7);
3. creates or updates `LearningRecord` entities;
4. evaluates whether patterns are emerging, strengthening or weakening;
5. updates `PerformancePattern`, `FailedPattern` or `LearningHypothesis`
   entities as appropriate;
6. recalculates confidence scores in its own confidence model;
7. makes knowledge available for query by Intelligence Modules and the
   Orchestrator Agent.

Analytics does not control or observe this process. It provides input
and trusts Learning Memory to extract knowledge correctly.

## 26.5. Handoff Readiness

A LearningMemoryHandoffPayload is ready when:

- [x] MetricSnapshot exists and is populated (at least partial);
- [x] PerformanceEvaluation has been performed (or marked as pending);
- [x] AnalyticsSummary exists (may be draft if data is incomplete);
- [x] AnalyticsObservations have been generated (may be empty);
- [x] Production context references are included;
- [x] Distribution context references are included;
- [x] Confidence and completeness scores are calculated;
- [x] Suggested learning categories are populated.

If any of these are missing, the handoff may still proceed but is
flagged as incomplete. Learning Memory may choose to wait for more
data before extracting knowledge.

---

# 27. Analytics Entities (Conceptual Summary)

## 27.1. Entity Catalog

These are functional entities for the Analytics Layer. They are
architectural definitions, not database schemas.

| Entity | Purpose | Current / Future |
|---|---|---|
| `AnalyticsJob` | Tracks an analytics run from intake to completion | Conceptual |
| `AnalyticsHandoffRecord` | Context received from Distribution | Conceptual (defined in Distribution Spec) |
| `MetricSource` | Defines where metrics come from (manual, connector, import, hybrid) | Conceptual |
| `MetricCollectionPlan` | Which metrics to collect, from which source, by when | Conceptual |
| `RawMetricRecord` | Platform-specific raw metric data before normalization | Future |
| `NormalizedMetricSet` | Platform metrics mapped to standard categories | Conceptual |
| `MetricSnapshot` | Foundation MVP entity — performance record at a point in time | Current MVP |
| `DerivedMetric` | Computed metric from normalized base metrics (engagement_rate, CTR, etc.) | Conceptual / Future |
| `PerformanceEvaluation` | Assessment of content performance against goals and baselines | Conceptual |
| `AnalyticsSummary` | Structured human- and machine-readable performance summary | Conceptual |
| `AnalyticsObservation` | Single structured interpretation — a candidate signal for learning | Conceptual |
| `AnomalyFlag` | Flag for unusual performance requiring attention | Future |
| `LearningMemoryHandoffPayload` | Structured context package passed to Learning Memory | Conceptual |
| `MetricCollectionError` | Structured error record for collection failures | Conceptual |

## 27.2. Entity Relationships

```text
Publication (from Distribution)
    │
    ↓
AnalyticsHandoffRecord (from Distribution)
    │
    ↓
AnalyticsJob
    │
    ├── MetricCollectionPlan
    │       │
    │       └── RawMetricRecord (1+ per collection)
    │               │
    │               └── NormalizedMetricSet
    │
    ├── MetricSnapshot (1+ per publication, time-windowed)
    │       │
    │       ├── NormalizedMetricSet (embedded)
    │       ├── DerivedMetrics (computed)
    │       └── (referenced by PerformanceEvaluation)
    │
    ├── PerformanceEvaluation
    │       │
    │       └── (referenced by AnalyticsSummary)
    │
    ├── AnalyticsSummary
    │       │
    │       └── AnalyticsObservations (0+ per summary)
    │
    └── LearningMemoryHandoffPayload
            │
            ├── (contains MetricSnapshot ref)
            ├── (contains PerformanceEvaluation ref)
            ├── (contains AnalyticsSummary ref)
            ├── (contains AnalyticsObservations refs)
            ├── (contains production context)
            └── (contains distribution context)
```

---

# 28. Analytics Statuses and Lifecycle

## 28.1. AnalyticsJob Statuses

```text
analytics_ready
    │  Publication is published; Analytics can begin.
    ↓
collection_pending
    │  Job created; waiting for metric collection to start.
    ↓
collecting
    │  Metric data is being gathered (manual entry, connector pull, import).
    ↓
raw_metrics_collected
    │  Raw metric data has been received.
    ↓
normalized
    │  Raw metrics have been normalized into standard categories.
    ↓
snapshot_created
    │  MetricSnapshot has been created/populated.
    ↓
evaluated
    │  PerformanceEvaluation has been performed.
    ↓
learning_handoff_ready
    │  All analytics context assembled; ready for Learning Memory handoff.
    ↓
completed
    │  Handoff complete. Analytics run is finished.

Failure states:
    collection_failed         — metric collection could not be completed
    insufficient_data         — not enough data to create a meaningful snapshot
    needs_manual_entry        — manual metrics required but not yet provided
    stale                     — snapshot was not refreshed within the expected window
    cancelled                 — analytics run was cancelled
```

## 28.2. Status Transitions

```text
analytics_ready → collection_pending:
    Analytics receives a valid AnalyticsHandoffRecord.

collection_pending → collecting:
    Collection mode is determined; data gathering begins.

collecting → raw_metrics_collected:
    Raw metric data received from source (manual, connector, import).

raw_metrics_collected → normalized:
    Normalization completed successfully.

normalized → snapshot_created:
    MetricSnapshot populated with normalized metrics and derived metrics.

snapshot_created → evaluated:
    PerformanceEvaluation completed.

evaluated → learning_handoff_ready:
    AnalyticsSummary, Observations and LearningMemoryHandoffPayload assembled.

learning_handoff_ready → completed:
    Handoff delivered to Learning Memory.

any → collection_failed:
    Metric collection could not be completed.

any → insufficient_data:
    Data collected but too sparse to create a meaningful evaluation.

any → needs_manual_entry:
    Manual mode active; operator has not yet entered metrics.

any → cancelled:
    Analytics run cancelled by operator or system.
```

## 28.3. Current MVP Status Subset

In the current MVP, the following statuses are actively used:

```text
draft → partial → complete → (archived)
                → failed
```

Additional statuses (`collection_pending`, `collecting`, `normalized`,
`evaluated`, `learning_handoff_ready`, `insufficient_data`, `stale`)
are architectural direction for future phases.

---

# 29. Error Handling

## 29.1. Analytics Error Structure

Every Analytics error has a structured format:

```text
AnalyticsError:
    error_code                 — standardized error identifier
    project_id                 — project context
    publication_id             — publication that failed (if applicable)
    content_item_id            — content that failed (if applicable)
    metric_snapshot_id         — snapshot that failed (if applicable)
    severity                   — blocking, warning, info
    message                    — human-readable description
    recommended_action         — what should be done to resolve
    timestamp                  — when the error occurred
```

## 29.2. Error Catalog

### 29.2.1. Intake Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `publication_not_found` | Publication record does not exist | blocking | Verify publication_id; check Distribution output |
| `publication_not_published` | Publication status is not "published" | blocking | Complete publication before analytics starts |
| `publication_url_missing` | Publication lacks URL (required for some metric collection) | warning or blocking | Record publication URL; manual metrics may still be possible |
| `handoff_record_invalid` | AnalyticsHandoffRecord is malformed or incomplete | blocking | Verify Distribution output; return to Distribution |
| `project_context_missing` | Project context unavailable | blocking | Verify project configuration |
| `goal_context_unknown` | Content goal is not defined | warning | Proceed with evaluation but flag goal as unknown |

### 29.2.2. Collection Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `metric_source_missing` | No metric source configured (manual, connector, import) | blocking | Configure at least one metric source |
| `manual_metric_entry_missing` | Manual mode active but operator has not entered metrics | warning | Notify operator; snapshot remains in draft |
| `raw_metric_invalid` | Raw metric data is malformed or contains invalid values | blocking | Validate raw data; re-collect |
| `connector_collection_failed` | Connector could not retrieve metrics from platform API (future) | blocking | Check connector configuration; retry |
| `import_parse_failed` | Imported file could not be parsed (future) | blocking | Verify file format; re-export from platform |
| `collection_timeout` | Metric collection exceeded time limit (future) | blocking | Check source availability; retry |

### 29.2.3. Normalization Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `normalization_failed` | Raw metrics could not be normalized | blocking | Check raw data format; verify normalization mapping |
| `required_metric_unavailable` | A critical metric is not available in the data | warning or blocking | Flag snapshot as incomplete; lower confidence |
| `unnormalized_metrics_remaining` | Some raw metrics were not mapped to any normalized category | warning | Review normalization mapping; add missing mappings |

### 29.2.4. Evaluation Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `baseline_unavailable` | No baseline exists for comparison | warning | Evaluate based on absolute metrics only; lower confidence |
| `snapshot_creation_failed` | MetricSnapshot could not be created/populated | blocking | Check data integrity; re-collect if needed |
| `confidence_too_low` | Confidence score is below the threshold for evaluation | warning | Flag evaluation as inconclusive; gather more data |
| `insufficient_sample_size` | Too few impressions/views for reliable derived metrics | warning | Lower confidence; note sample size limitation |
| `goal_alignment_unavailable` | Content goal is unknown and cannot be evaluated against | warning | Skip goal alignment dimension; evaluate other dimensions |

### 29.2.5. Handoff Errors

| Error Code | Description | Severity | Recommended Action |
|---|---|---|---|
| `analytics_handoff_failed` | LearningMemoryHandoffPayload could not be assembled | blocking | Check all required context references |
| `production_snapshot_missing` | Production snapshot reference broken or unavailable | warning | Handoff proceeds but lacks production context |
| `distribution_context_incomplete` | Distribution context is missing key fields | warning | Handoff proceeds with available context |

---

# 30. Current MVP Compatibility

## 30.1. Foundation MVP Chain Preserved

The current Foundation MVP must remain fully functional:

```text
Idea → Scenario → ContentItem → ExportPackage → Manual Publication → MetricSnapshot
```

ANALYTICS_SPEC.md preserves:

- manual publication as the only current publication mode;
- manual/draft MetricSnapshot as the only current performance record;
- `find_metric_snapshots.py` and `import_manual_metrics.py` as current helpers;
- no external analytics API dependency;
- no connector dependency;
- no automated metric refresh;
- no UI dependency;
- no database schema dependency;
- the current smoke loop unaffected.

## 30.2. Minimum Current Analytics Support

In the current MVP, Analytics supports:

- MetricSnapshot can exist as draft (created before metrics are available);
- manual metric values can be recorded via `import_manual_metrics.py`;
- missing metrics are allowed if marked incomplete;
- `clicks` input is normalized to `link_clicks`;
- `published_url` updates the related `Publication`;
- analytics summary can be absent or draft until metrics exist — not blocking
  for the current MVP loop;
- confidence and completeness scoring may be basic or conceptual.

## 30.3. What Is Explicitly NOT Current

The following are NOT active in the current MVP:

- connector-based metric collection;
- automated snapshot scheduling;
- cross-channel metric comparison;
- complex derived metric computation;
- anomaly detection algorithms;
- PerformanceEvaluation as an automated process;
- AnalyticsObservation generation;
- LearningMemoryHandoffPayload assembly (conceptual, not executed);
- time-series snapshots.

These are documented as architectural direction for future implementation.
They must not be treated as current requirements or dependencies.

---

# 31. Future Extension Path

## 31.1. Stage 1 — Current MVP (Now)

- Manual MetricSnapshot creation.
- `find_metric_snapshots.py` — locate draft snapshots.
- `import_manual_metrics.py` — import manual metrics into draft snapshots.
- Basic `clicks` → `link_clicks` normalization.
- Snapshot statuses: draft, partial, complete, failed.

## 31.2. Stage 2 — Better Manual Analytics

- Structured manual metric entry (guided form with field validation).
- Basic derived metrics (engagement rate, click-through rate, save rate).
- Simple performance summary (comparison to manual target).
- AnalyticsSummary in draft form.
- Basic completeness scoring.

## 31.3. Stage 3 — Import-Based Analytics

- CSV/platform export parsing and import.
- Normalization from platform-specific CSV columns to standard categories.
- Multiple MetricSnapshots per publication (different time windows).
- Basic derived metric computation.
- Simple baseline calculation (averaging previous snapshots).

## 31.4. Stage 4 — Connector-Based Analytics

- Platform metrics connectors (API integration).
- Scheduled metric refresh (24h, 72h, 7d, 30d).
- RawMetricRecord storage (separate from MetricSnapshot).
- Automated normalization with platform-specific mapping.
- Multi-snapshot time-series for a single publication.
- Connector error handling and retry logic.

## 31.5. Stage 5 — Advanced Analytics

- Cross-channel performance comparison.
- Content type benchmarks (per-type averages and distributions).
- Asset/template performance correlation.
- Anomaly detection (rule-based, then statistical).
- Predictive scoring — estimated performance before content creation.
- Confidence model with decay over time.
- Cohort analysis (grouping content by audience, topic, campaign).

## 31.6. Stage 6 — Closed-Loop Learning

- Analytics feeds Learning Memory with high-confidence observations.
- Learning Memory extracts patterns from accumulated observations.
- Orchestrator Agent uses patterns to make improved decisions.
- The Growth Loop closes: Analytics → Learning Memory → Orchestrator →
  Better Content → Better Analytics → Deeper Learning.
- Full autonomous cycle with human governance through control points.

---

# 32. Readiness Criteria

## 32.1. Analytics Architecture Readiness

The Analytics architecture is considered defined when:

- [x] Analytics boundary is defined — where Distribution ends and Analytics begins;
- [x] Distribution handoff is defined — AnalyticsHandoffRecord specification;
- [x] Metric sources are defined — manual, connector, import, hybrid;
- [x] Collection modes are defined — Manual (current), Connector/Import/Hybrid (future);
- [x] Raw metrics are defined — platform-specific RawMetricRecord model;
- [x] Normalization is defined — mapping platform metrics to standard categories;
- [x] Metric taxonomy is defined — reach, engagement, attention, conversion, negative, operational, quality/confidence;
- [x] MetricSnapshot is defined — Foundation MVP entity, extended conceptually;
- [x] Derived metrics are defined — engagement_rate, CTR, save_rate, share_rate, comment_rate, completion_rate, conversion_rate, revenue_per_view;
- [x] Performance evaluation is defined — dimensions, success levels, evaluation rules;
- [x] Benchmarks and baselines are defined — project historical, channel, content type, campaign, manual target, industry, none;
- [x] Analytics Summary is defined — structured summary with signals, confidence, recommended followup type;
- [x] Observations are defined — structured interpretations, not durable memory;
- [x] Anomaly detection is defined — conceptual flag types, rule-based and statistical approaches;
- [x] Confidence/completeness model is defined — scores, factors, rules;
- [x] Time windows are defined — current manual, future 1h/24h/72h/7d/30d;
- [x] Cross-channel comparison is defined — future conceptual model;
- [x] Content type relationship is defined — expected metric profiles per content type;
- [x] Production snapshot relationship is defined — correlation without modification;
- [x] Distribution context relationship is defined — operational signal utilization;
- [x] Learning Memory Handoff is defined — LearningMemoryHandoffPayload specification;
- [x] Current MVP manual MetricSnapshot is preserved;
- [x] Future connector analytics is clearly marked as future;
- [x] Analytics error handling is defined — structured error catalog;
- [x] Foundation MVP chain (Publication → MetricSnapshot) is intact.

---

# 33. Related Documents

## 33.1. Core Architecture

```text
docs/02_architecture/SYSTEM_ARCHITECTURE.md         — System architecture layers
docs/02_architecture/LOOPRA_ARCHITECTURE.md         — Core architecture direction
docs/02_architecture/PIPELINES_SPEC.md              — Content lifecycle pipeline
docs/02_architecture/BRAND_SYSTEM_SPEC.md           — Brand System specification
```

## 33.2. Foundation Layer

```text
docs/00_foundation/DATA_MODEL.md                    — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md         — Project configuration (analytics settings, goals, channels)
docs/00_foundation/WORKSPACE_AND_PROJECT_MODEL.md   — Workspace and project model
```

## 33.3. Intelligence Layer

```text
docs/03_intelligence/CONTENT_CYCLE_SPEC.md          — Full content cycle (Analytics = Stage 8)
docs/03_intelligence/AGENT_SYSTEM_SPEC.md           — Orchestrator Agent and autonomy modes
docs/03_intelligence/CONTENT_INTELLIGENCE_SPEC.md   — Content opportunity analysis
docs/03_intelligence/LEARNING_MEMORY_SPEC.md        — Learning Memory architecture (consumes Analytics output)
docs/03_intelligence/TREND_INTELLIGENCE_SPEC.md     — Market signal analysis
```

## 33.4. Production Layer

```text
docs/04_production/CONTENT_TYPES_SPEC.md            — Content type definitions (expected metric profiles)
docs/04_production/PRODUCTION_PIPELINE_SPEC.md      — Production Pipeline (provides Production Snapshot)
docs/04_production/ASSET_LIBRARY_SPEC.md            — Asset Library specification
docs/04_production/DISTRIBUTION_SPEC.md             — Distribution Layer (provides AnalyticsHandoffRecord)
docs/04_production/ANALYTICS_SPEC.md                — This document
```

## 33.5. Project Governance

```text
AGENTS.md                                            — Development rules
STATE.md                                             — Current project state
```

---

# 34. Document Status

| Field | Value |
|---|---|
| Status | Active |
| Version | 1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Production Layer — Analytics Layer / Performance Measurement Boundary |

---

# Final Statement

The Analytics Layer is the measurement and interpretation boundary of
LOOPRA. It does not create content, does not publish, does not extract
durable knowledge and does not make strategic decisions.

It takes a Publication record from Distribution and produces:

- a **MetricSnapshot** — the record of what happened;
- a **PerformanceEvaluation** — the assessment against goals and baselines;
- an **AnalyticsSummary** — the structured summary of signals;
- **AnalyticsObservations** — structured interpretations for learning;
- a **LearningMemoryHandoffPayload** — the complete context package for
  knowledge extraction.

The Analytics Layer answers: "What happened, how well did it perform,
and what should the system know?"

It provides the evidence from which Learning Memory forms knowledge.
It provides the facts from which the Orchestrator Agent makes decisions.

In the current Foundation MVP, Analytics operates through manual
MetricSnapshots — simple, reliable, and sufficient for the validation
phase. In future phases, it will expand to support connector-based
collection, automated normalization, cross-channel comparison and
closed-loop learning.

The Analytics Layer bridges the gap between "content published" and
"system learned." It is the measurement foundation of the self-learning
autonomous marketing operating system.

```text
Publication → Analytics → MetricSnapshot → PerformanceEvaluation →
AnalyticsSummary → LearningMemoryHandoffPayload → Learning Memory →
Improved Next Cycle
```

The loop closes here.

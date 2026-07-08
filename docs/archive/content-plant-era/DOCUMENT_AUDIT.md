# Document Audit: Content Plant Legacy Archive

## Purpose

This audit evaluates all 35 legacy Content Plant documents found in `docs/archive/` and classifies them for the LOOPRA transition.

Status: Complete
Date: 2026-07-08
Auditor: LOOPRA documentation migration

---

## Classification Legend

| Decision | Meaning |
|---|---|
| **MOVE_TO_ACTIVE** | Document describes current LOOPRA foundation. Move back to `docs/` and rename for LOOPRA. |
| **UPDATE_REQUIRED** | Valuable architecture/design content that needs LOOPRA adaptation before reactivation. Keep archived until task is created. |
| **ARCHIVE** | Content Plant historical reference only. No active value for LOOPRA foundation. |
| **DELETE_CANDIDATE** | Fully superseded by other documents or has no lasting value. |

---

## Full Audit Table

| # | Document | Purpose | Decision | Target Location (if moved) | Reason |
|---|---|---|---|---|---|
| 1 | `MVP_SCOPE.md` | Current foundation MVP definition: Idea->Scenario->ContentItem->ExportPackage->Publication->MetricSnapshot loop. Project-agnostic, export-first, manual-publication-first. | **MOVE_TO_ACTIVE** | `docs/01_product/MVP_SCOPE.md` | Directly describes the implemented LOOPRA foundation loop. No legacy note. Core source of truth. Needs `s/Content Plant/LOOPRA/g`. |
| 2 | `DATA_MODEL.md` | Current foundation data model: Project, Idea, Scenario, ContentItem, ExportPackage, Publication, MetricSnapshot entities and relationships. | **MOVE_TO_ACTIVE** | `docs/02_architecture/DATA_MODEL.md` | Core data model that matches implemented code. No legacy note. Naming update only. |
| 3 | `WORKSPACE_AND_PROJECT_MODEL.md` | Multi-project architecture model: Workspace, Project, Brand Profile, project-scoped storage, slug conventions. | **MOVE_TO_ACTIVE** | `docs/02_architecture/WORKSPACE_AND_PROJECT_MODEL.md` | Foundation architectural concept. Project-agnostic separation is LOOPRA's core principle. No legacy note. |
| 4 | `PIPELINES_SPEC.md` | Current local/manual helper-supported pipeline stages and developer scripts. | **MOVE_TO_ACTIVE** | `docs/02_architecture/PIPELINES_SPEC.md` | Describes active pipeline matching `STATE.md`. No legacy note. Developer workflow documentation. |
| 5 | `PLATFORM_OVERVIEW.md` | Top-level platform description, project-agnostic principle, current foundation loop, module ownership, MVP boundaries. | **MOVE_TO_ACTIVE** | `docs/00_foundation/PLATFORM_OVERVIEW.md` | Core LOOPRA platform identity document. No legacy note. Core source of truth. |
| 6 | `CONTENT_FORMATS_OVERVIEW.md` | Platform-level content format portfolio. `text_social_post` as current safest format. Future candidate formats. | **MOVE_TO_ACTIVE** | `docs/04_production/CONTENT_FORMATS_OVERVIEW.md` | Format portfolio is active LOOPRA scope. No legacy note. Defines valid `content_type` identifiers. |
| 7 | `DEVELOPER_QUICKSTART.md` | Developer onboarding: run tests (107 tests), smoke loop, inspect/validate packages, manual metrics import. | **MOVE_TO_ACTIVE** | `docs/06_operations/DEVELOPER_QUICKSTART.md` | Operational document. Purely practical. References current scripts and test counts. Needs `s/Content Plant/LOOPRA/g`. |
| 8 | `SYSTEM_ARCHITECTURE.md` | Full system architecture: Web UI, Backend API, Application Services, Database, Workers, Render, modules, data flows, error handling. | **UPDATE_REQUIRED** | Keep archived | Has `Legacy / future-scope note`. Contains valid architecture principles (project-scoping, module boundaries, snapshots) mixed with future UI/API/database specs. Too large to reactivate without scoped rewrite task. |
| 9 | `BRAND_SYSTEM_SPEC.md` | Universal Brand Profile specification: identity, audience, tone of voice, visual identity, CTA library, content rules, platform settings. | **UPDATE_REQUIRED** | Keep archived | Has `Legacy / future-scope note`. Brand Profile concept IS core to LOOPRA. Document describes valid universal structure. Needs LOOPRA rewrite to remove Content Plant references and align with current foundation scope. |
| 10 | `PRODUCT_STRATEGY.md` | Product strategy: two horizons, multi-project strategy, brand profile as strategy boundary, current MVP strategy. | **UPDATE_REQUIRED** | Keep archived | No legacy note but describes Content Plant strategy. Valuable strategic thinking. Needs rebranding and alignment with LOOPRA's "Autonomous Marketing OS" positioning. |
| 11 | `USER_WORKFLOWS.md` | Current user-facing workflow: 10-step manual loop with developer helpers. | **UPDATE_REQUIRED** | Keep archived | No legacy note. Describes active workflow but references Content Plant. Close to MOVE_TO_ACTIVE but benefits from LOOPRA-aligned rewrite to avoid confusion. |
| 12 | `PROJECT_SETTINGS_SPEC.md` | Project Settings UI/data model: Basics, Brand Profile, Audience, Tone of Voice, Visual Identity, CTA, Links, Platforms, Export, Analytics settings. | **UPDATE_REQUIRED** | Keep archived | Has `Legacy / future-scope note`. Mixes valid data model with future UI spec. Valuable project settings structure. Needs LOOPRA adaptation separating model from UI. |
| 13 | `AGENT_RULES.md` | Agent and developer rules for Content Plant: required reading, naming conventions, MVP boundaries, report templates. | **ARCHIVE** | Keep archived | Superseded by `AGENTS.md` in repository root. Content Plant-specific. Historical interest only. |
| 14 | `PRODUCTION_ENGINE_SPEC.md` | Future Production Engine: render jobs, templates, vertical video, text bundles, carousels, output specs. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Describes future render pipeline. Not current foundation scope. Useful future reference. |
| 15 | `PUBLISHING_HUB_SPEC.md` | Future Publishing Hub: export packages, publications, captions, UTM, scheduling, calendar, platform adaptation. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Describes future publishing layer. Not current foundation scope. Useful future reference. |
| 16 | `QA_AND_REVIEW.md` | Future QA and Review module: scenario QA, asset QA, pre-render QA, output QA, human review, severity levels. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Detailed QA specification for future phases. Not current scope. |
| 17 | `SCENARIO_STUDIO_SPEC.md` | Future Scenario Studio: scenario generation, scenes, visual prompts, captions, repurpose logic. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Detailed specification for future AI-assisted module. Not current scope. |
| 18 | `ASSET_LIBRARY_SPEC.md` | Future Asset Library: upload, metadata, tags, scene mapping, asset slots, previews. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Detailed asset management spec. Not current scope. |
| 19 | `IDEA_BANK_SPEC.md` | Future Idea Bank: idea management, sources, statuses, lifecycle, scoring. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Detailed idea management spec. Not current scope. |
| 20 | `INTEGRATIONS_SPEC.md` | Integration layer: LLM, storage, render, publishing, analytics, CSV import, credentials, retry. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Comprehensive integration architecture. Useful future reference but not current scope. |
| 21 | `TREND_RADAR_SPEC.md` | Future Trend Radar: trend references, analysis, hook/topic/emotion extraction, trend-to-idea flow. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Detailed spec for market signal module. Not current scope. |
| 22 | `ANALYTICS_AND_OPTIMIZATION.md` | Future Analytics module: metric snapshots, summaries, insights, recommendations, optimization loop. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Full analytics spec. While `MetricSnapshot` is currently implemented via manual helpers, this full spec is future scope. |
| 23 | `SAAS_VISION.md` | Future SaaS direction: stages, users, billing, marketplace, multi-tenant, security. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Entirely future scope. Valuable strategic reference for later phases. |
| 24 | `WEB_UI_SPEC.md` | Web UI specification: screens, navigation, Project Switcher, layouts, UX principles. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. UI not in current scope. Future reference. |
| 25 | `DASHBOARD_SPEC.md` | Dashboard specification: project health, pipeline overview, next actions, blockers, widgets. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. UI not in current scope. Future reference. |
| 26 | `DEVELOPMENT_ROADMAP.md` | Historical development roadmap: 23 phases from documentation foundation to SaaS readiness. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Historical planning document. Referenced old numbered docs structure. |
| 27 | `TASK_PROMPT_TEMPLATES.md` | Reusable task prompt templates for agents: cleanup, audit, module implementation, bug fixes. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Operational templates for Content Plant agents. LOOPRA uses `AGENTS.md`. |
| 28 | `FORMAT_ATMOSPHERIC_VIDEO.md` | Atmospheric Video format specification. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Future format. Not current `text_social_post` scope. |
| 29 | `FORMAT_DIALOG_CAROUSEL.md` | Dialog Carousel format specification. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Future format. Not current scope. |
| 30 | `FORMAT_DIALOG_MINISERIES.md` | Dialog Miniseries format specification. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Future format. Not current scope. |
| 31 | `FORMAT_EXPLAINER_CAROUSEL.md` | Explainer Carousel format specification. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Future format. Not current scope. |
| 32 | `FORMAT_PINTEREST_PINS.md` | Pinterest Pins format specification. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Future format. Not current scope. |
| 33 | `FORMAT_TEXT_SOCIAL_POSTS.md` | Text Social Posts format specification. | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Describes `text_social_post` format in detail. While this IS the current format, the document has legacy warning and is superseded by `CONTENT_FORMATS_OVERVIEW.md` which already covers the format. |
| 34 | `CHANGELOG.md` | Historical changelog for Content Plant documentation changes (2026-07-05 to 2026-07-06). | **ARCHIVE** | Keep archived | `Legacy / future-scope note`. Historical record. Referenced old numbered docs tree. |
| 35 | `00_index.md` | Old Content Plant documentation index with flat docs layout. | **DELETE_CANDIDATE** | Keep archived | Fully superseded. References old flat docs layout. New LOOPRA docs use structured numbered directories. |

---

## Statistics

| Decision | Count | Documents |
|---|---|---|
| MOVE_TO_ACTIVE | 7 | MVP_SCOPE, DATA_MODEL, WORKSPACE_AND_PROJECT_MODEL, PIPELINES_SPEC, PLATFORM_OVERVIEW, CONTENT_FORMATS_OVERVIEW, DEVELOPER_QUICKSTART |
| UPDATE_REQUIRED | 5 | SYSTEM_ARCHITECTURE, BRAND_SYSTEM_SPEC, PRODUCT_STRATEGY, USER_WORKFLOWS, PROJECT_SETTINGS_SPEC |
| ARCHIVE | 22 | AGENT_RULES, PRODUCTION_ENGINE_SPEC, PUBLISHING_HUB_SPEC, QA_AND_REVIEW, SCENARIO_STUDIO_SPEC, ASSET_LIBRARY_SPEC, IDEA_BANK_SPEC, INTEGRATIONS_SPEC, TREND_RADAR_SPEC, ANALYTICS_AND_OPTIMIZATION, SAAS_VISION, WEB_UI_SPEC, DASHBOARD_SPEC, DEVELOPMENT_ROADMAP, TASK_PROMPT_TEMPLATES, FORMAT_ATMOSPHERIC_VIDEO, FORMAT_DIALOG_CAROUSEL, FORMAT_DIALOG_MINISERIES, FORMAT_EXPLAINER_CAROUSEL, FORMAT_PINTEREST_PINS, FORMAT_TEXT_SOCIAL_POSTS, CHANGELOG |
| DELETE_CANDIDATE | 1 | 00_index |

---

## Archive Subfolder Structure

Files are organized under `docs/archive/content-plant-era/` as follows:

```
docs/archive/content-plant-era/
├── DOCUMENT_AUDIT.md              (this file)
│
├── 00_governance/
│   ├── AGENT_RULES.md
│   ├── TASK_PROMPT_TEMPLATES.md
│   ├── DEVELOPER_QUICKSTART.md
│   ├── CHANGELOG.md
│   └── 00_index.md
│
├── 01_product/
│   ├── MVP_SCOPE.md
│   ├── PRODUCT_STRATEGY.md
│   ├── USER_WORKFLOWS.md
│   ├── PLATFORM_OVERVIEW.md
│   └── SAAS_VISION.md
│
├── 02_architecture/
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── WORKSPACE_AND_PROJECT_MODEL.md
│   ├── PIPELINES_SPEC.md
│   ├── BRAND_SYSTEM_SPEC.md
│   └── INTEGRATIONS_SPEC.md
│
├── 03_content/
│   ├── CONTENT_FORMATS_OVERVIEW.md
│   ├── FORMAT_ATMOSPHERIC_VIDEO.md
│   ├── FORMAT_DIALOG_CAROUSEL.md
│   ├── FORMAT_DIALOG_MINISERIES.md
│   ├── FORMAT_EXPLAINER_CAROUSEL.md
│   ├── FORMAT_PINTEREST_PINS.md
│   └── FORMAT_TEXT_SOCIAL_POSTS.md
│
├── 04_production/
│   ├── PRODUCTION_ENGINE_SPEC.md
│   ├── PUBLISHING_HUB_SPEC.md
│   ├── QA_AND_REVIEW.md
│   ├── SCENARIO_STUDIO_SPEC.md
│   ├── ASSET_LIBRARY_SPEC.md
│   ├── IDEA_BANK_SPEC.md
│   └── ANALYTICS_AND_OPTIMIZATION.md
│
├── 05_platform/
│   ├── PROJECT_SETTINGS_SPEC.md
│   ├── WEB_UI_SPEC.md
│   ├── DASHBOARD_SPEC.md
│   ├── DEVELOPMENT_ROADMAP.md
│   └── TREND_RADAR_SPEC.md
│
└── 06_misc/
    (empty — reserved for uncategorized items)
```

---

## Recommended Migration Actions

### Move back to active LOOPRA docs

These 7 documents describe the ACTUAL implemented foundation and should be copied back to `docs/`, renamed for LOOPRA, with `s/Content Plant/LOOPRA/g` applied:

| # | File | Target in LOOPRA docs | Notes |
|---|---|---|---|
| 1 | `MVP_SCOPE.md` | `docs/01_product/MVP_SCOPE.md` | Core MVP definition. Update project name in status footer. |
| 2 | `DATA_MODEL.md` | `docs/02_architecture/DATA_MODEL.md` | Core data model. Minor naming updates. |
| 3 | `WORKSPACE_AND_PROJECT_MODEL.md` | `docs/02_architecture/WORKSPACE_AND_PROJECT_MODEL.md` | Project model. Minor naming updates. |
| 4 | `PIPELINES_SPEC.md` | `docs/02_architecture/PIPELINES_SPEC.md` | Active pipeline. Minor naming updates. |
| 5 | `PLATFORM_OVERVIEW.md` | `docs/00_foundation/PLATFORM_OVERVIEW.md` | Top-level platform doc. Minor naming updates. |
| 6 | `CONTENT_FORMATS_OVERVIEW.md` | `docs/04_production/CONTENT_FORMATS_OVERVIEW.md` | Format portfolio. Minor naming updates. |
| 7 | `DEVELOPER_QUICKSTART.md` | `docs/06_operations/DEVELOPER_QUICKSTART.md` | Dev onboarding. Update project name, verify command references. |

**Action**: Create task "Rebrand 7 foundation documents from Content Plant to LOOPRA". These can be bulk-updated since changes are cosmetic (project name, doc references).

### Rewrite for LOOPRA (next tasks)

These 5 documents contain valuable architecture/design content that needs targeted LOOPRA adaptation:

| # | File | Recommended LOOPRA Target | Scope of Rewrite |
|---|---|---|---|
| 8 | `SYSTEM_ARCHITECTURE.md` | `docs/02_architecture/SYSTEM_ARCHITECTURE.md` | Major. Remove `Legacy / future-scope note`. Separate current foundation from future UI/API/database sections. Align module descriptions with implemented services. |
| 9 | `BRAND_SYSTEM_SPEC.md` | `docs/02_architecture/BRAND_SYSTEM_SPEC.md` | Medium. Brand Profile is core to LOOPRA. Remove legacy note. Update terminology. Align with current `project.yaml` config structure. |
| 10 | `PRODUCT_STRATEGY.md` | `docs/01_product/PRODUCT_STRATEGY.md` | Medium. Rebrand strategy from "Content Plant" to "LOOPRA — Autonomous Marketing Operating System". Update product positioning. |
| 11 | `USER_WORKFLOWS.md` | `docs/06_operations/USER_WORKFLOWS.md` | Light. Active workflow doc. Update naming, verify current scripts are referenced correctly. |
| 12 | `PROJECT_SETTINGS_SPEC.md` | `docs/02_architecture/PROJECT_SETTINGS_SPEC.md` | Medium. Remove legacy note. Extract data model from UI spec. Align with current `project.yaml` structure. |

**Action**: Create individual tasks for each document. Priority: BRAND_SYSTEM_SPEC and SYSTEM_ARCHITECTURE first (most architectural value).

### Keep archived

These 22 documents are Content Plant historical records. They remain in `docs/archive/content-plant-era/` with no changes:

- All 6 `FORMAT_*.md` files — future format specs
- All 8 `*_SPEC.md` module specs (PRODUCTION_ENGINE, PUBLISHING_HUB, QA_AND_REVIEW, SCENARIO_STUDIO, ASSET_LIBRARY, IDEA_BANK, INTEGRATIONS, TREND_RADAR) — future modules
- `ANALYTICS_AND_OPTIMIZATION.md` — future analytics
- `SAAS_VISION.md` — future SaaS direction
- `WEB_UI_SPEC.md` — future UI
- `DASHBOARD_SPEC.md` — future dashboard
- `DEVELOPMENT_ROADMAP.md` — historical roadmap
- `TASK_PROMPT_TEMPLATES.md` — historical agent templates
- `AGENT_RULES.md` — superseded by root `AGENTS.md`
- `CHANGELOG.md` — historical changelog

### Remove eventually

| # | File | Reason |
|---|---|---|
| 35 | `00_index.md` | Completely superseded by new LOOPRA `docs/` directory structure. References old flat docs layout. Can be deleted after verification that all referenced documents are accounted for in this audit. |

---

## Final Boundary Statement

After this audit, the LOOPRA documentation landscape should be:

**Active LOOPRA documentation** (`docs/` with numbered directories):
- Contains only LOOPRA-branded, current-foundation-aligned documents.
- No references to "Content Plant" as active product identity.
- No legacy/future-scope notes.

**Historical archive** (`docs/archive/content-plant-era/`):
- Contains all Content Plant era documents, organized by category.
- Serves as historical reference for future phases.
- Clear boundary: these documents do NOT define current LOOPRA scope.

**Next steps**:
1. Execute MOVE_TO_ACTIVE: copy 7 documents to `docs/`, apply `s/Content Plant/LOOPRA/g`.
2. Create tasks for UPDATE_REQUIRED documents (5 documents).
3. Verify active LOOPRA docs after migration are consistent and non-conflicting.
4. Consider deleting `00_index.md` once migration is verified.

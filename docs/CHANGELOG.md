# Changelog

All notable changes to **Content Plant** documentation and implementation should be recorded in this file.

This changelog follows a simple human-readable format.

---

## 2026-07-05

### Added

- Added `docs/02_platform_architecture/DATA_MODEL.md`.
  - Defines core platform entities.
  - Separates project-level and platform-level data.
  - Defines Workspace, Project, Brand Profile, Idea, Scenario, Asset, Render Job, Content Item, Publication and Metric Snapshot models.

- Added `docs/02_platform_architecture/PIPELINES_SPEC.md`.
  - Defines end-to-end platform pipelines.
  - Covers Project setup, Idea to Scenario, Asset mapping, Production, QA, Review, Publishing, Metrics and Optimization flows.
  - Clarifies separation between Content Item status and Publication status.

- Added `docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md`.
  - Defines high-level architecture: Web UI, Backend API, Application Services, Database, File Storage, Workers, Render Layer, Integration Layer and Analytics.
  - Establishes project-scoped storage and service boundaries.
  - Keeps SaaS readiness architectural but outside MVP.

- Added `docs/03_modules/IDEA_BANK_SPEC.md`.
  - Defines Idea Bank as project-scoped idea management module.
  - Covers Idea entity, sources, statuses, lifecycle, links to Scenario Studio and Analytics.

- Added `docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md`.
  - Defines Metric Snapshot, Performance Summary, Insight and Optimization Recommendation concepts.
  - Covers manual metrics, CSV import, reporting and feedback loop into Idea Bank.

- Added `docs/04_content_formats/FORMAT_ATMOSPHERIC_VIDEO.md`.
  - Defines universal Atmospheric Video format.
  - Covers text sequences, background assets, motion, captions, QA and export.

- Added `docs/04_content_formats/FORMAT_DIALOG_CAROUSEL.md`.
  - Defines universal Dialog Carousel format.
  - Covers slide roles, dialogue structure, layout, captions, repurpose and export package.

- Added `docs/04_content_formats/FORMAT_EXPLAINER_CAROUSEL.md`.
  - Defines universal Explainer Carousel format.
  - Covers explanation patterns, slide model, visual rules, QA and repurpose paths.

- Added `docs/04_content_formats/FORMAT_PINTEREST_PINS.md`.
  - Defines universal Pinterest Pin format.
  - Covers evergreen-first logic, pin package, keywords, destination URL, QA and metrics.

- Added `docs/01_platform/DEVELOPMENT_ROADMAP.md`.
  - Defines development phases from documentation foundation to MVP vertical slice, analytics loop, automation and SaaS readiness.
  - Clarifies MVP completion criteria.

- Added `docs/02_platform_architecture/INTEGRATIONS_SPEC.md`.
  - Defines integration layer principles.
  - Covers storage, LLM, render tools, publishing, analytics imports, website events, credentials handling and fallback modes.

- Added `docs/03_modules/TREND_RADAR_SPEC.md`.
  - Defines Trend Radar as source-flexible and MVP-safe market signal module.
  - Covers manual links, notes, CSV import, Trend Reference, Trend Analysis and Trend to Idea flow.

- Added `docs/06_agents/TASK_PROMPT_TEMPLATES.md`.
  - Defines reusable prompts for documentation cleanup, audit, module implementation, content format implementation, bug fixes, integrations, UI work and project-level documents.

- Added `docs/01_platform/SAAS_VISION.md`.
  - Defines future SaaS direction.
  - Separates internal MVP from public SaaS capabilities.
  - Covers future users, workspace model, roles, billing, marketplace, security, product analytics and SaaS readiness checklist.

- Added this `CHANGELOG.md`.

### Changed

- Cleaned platform documentation to reinforce Content Plant as a standalone multi-project platform.
- Normalized examples toward neutral placeholders:
  - `project_example`
  - `brand_example`
  - `Example Brand`
  - `Demo Project`
  - `Client Brand`
  - `https://example.com`
  - `storage/projects/{project_slug}/`

- Clarified that project-specific rules must live under:

```text
docs/07_projects/{project_slug}/
```

- Fixed `Export Package` ownership:
  - `Export Package` belongs to `Publishing Hub`.
  - `Production Engine` owns `RenderJob`, `OutputFile`, `ContentItem`, technical QA result and render output metadata.

- Clarified the first safest MVP content format:
  - `text_social_post` is the first format for validating the core platform loop.
  - video formats should be connected after the core loop is stable.

- Clarified hybrid project-specific source of truth:
  - `docs/07_projects/{project_slug}/` for project-level documentation;
  - `projects/{project_id}/project.yaml` for machine-readable settings for code.

- Clarified that platform documentation should remain project-neutral.

### Fixed

- Removed project-specific data from platform-level documents where it could incorrectly define the platform core.
- Removed hardcoded project examples from architecture and format specs.
- Replaced brand-specific product, pricing, URL, CTA and character examples with neutral placeholders.
- Clarified that the first validation project may be used to test the platform, but project-specific rules must not live in platform specs.

### Docs

The following documentation areas are now covered:

```text
Platform Core
Platform Architecture
Platform Modules
Content Format Specs
Product Design
Agent Rules
SaaS Vision
Changelog
```

Core documentation foundation includes:

```text
docs/00_index.md
docs/01_platform/PLATFORM_OVERVIEW.md
docs/01_platform/PRODUCT_STRATEGY.md
docs/01_platform/MVP_SCOPE.md
docs/01_platform/DEVELOPMENT_ROADMAP.md
docs/01_platform/SAAS_VISION.md

docs/02_platform_architecture/SYSTEM_ARCHITECTURE.md
docs/02_platform_architecture/DATA_MODEL.md
docs/02_platform_architecture/WORKSPACE_AND_PROJECT_MODEL.md
docs/02_platform_architecture/BRAND_SYSTEM_SPEC.md
docs/02_platform_architecture/PIPELINES_SPEC.md
docs/02_platform_architecture/INTEGRATIONS_SPEC.md

docs/03_modules/TREND_RADAR_SPEC.md
docs/03_modules/IDEA_BANK_SPEC.md
docs/03_modules/SCENARIO_STUDIO_SPEC.md
docs/03_modules/ASSET_LIBRARY_SPEC.md
docs/03_modules/PRODUCTION_ENGINE_SPEC.md
docs/03_modules/QA_AND_REVIEW.md
docs/03_modules/PUBLISHING_HUB_SPEC.md
docs/03_modules/ANALYTICS_AND_OPTIMIZATION.md

docs/04_content_formats/CONTENT_FORMATS_OVERVIEW.md
docs/04_content_formats/FORMAT_DIALOG_MINISERIES.md
docs/04_content_formats/FORMAT_ATMOSPHERIC_VIDEO.md
docs/04_content_formats/FORMAT_DIALOG_CAROUSEL.md
docs/04_content_formats/FORMAT_EXPLAINER_CAROUSEL.md
docs/04_content_formats/FORMAT_TEXT_SOCIAL_POSTS.md
docs/04_content_formats/FORMAT_PINTEREST_PINS.md

docs/05_product_design/USER_WORKFLOWS.md
docs/05_product_design/WEB_UI_SPEC.md
docs/05_product_design/DASHBOARD_SPEC.md
docs/05_product_design/PROJECT_SETTINGS_SPEC.md

docs/06_agents/AGENT_RULES.md
docs/06_agents/TASK_PROMPT_TEMPLATES.md

CHANGELOG.md
```

### Notes

- The documentation foundation is now ready for implementation planning.
- Next recommended step: start Task 1 for the canonical platform domain layer on top of the now-fixed documentation decisions.
- Project-level documents should be created separately under `docs/07_projects/{project_slug}/` and must not be merged into platform-level specs.

# CONFIGURATION AND ENVIRONMENT SPEC

## Version

v1.0

## Status

Active — LOOPRA Platform Layer

## Purpose

This document defines the Configuration and Environment Layer of the LOOPRA
Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA read, separate, validate and use different levels of
> configuration — project settings, runtime configuration, environment variables,
> defaults, local/dev/test modes, future secrets and future deployment settings —
> without violating the Foundation MVP and without mixing project settings,
> runtime settings and credentials?

CONFIGURATION_AND_ENVIRONMENT_SPEC.md is the bridge between `project.yaml`,
`ProjectService`, `ProjectConfig`, environment variables, runtime roots,
local/dev/test/smoke modes, future deployment configuration, future secrets and
future SaaS tenancy configuration.

It documents configuration as it actually exists in the codebase. Configuration
concepts that do not exist are explicitly marked as future/conceptual.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document describes:

- the configuration model — what sources of configuration exist, how they are
  read, separated, validated and applied;
- the configuration hierarchy — which source takes precedence;
- the roles of project configuration, runtime configuration and environment
  variables;
- the current Foundation MVP configuration scope;
- the boundaries between project settings, runtime settings, environment
  variables and secrets;
- future configuration extension paths (secrets, deployment, feature flags,
  SaaS tenancy);
- how configuration interacts with services, tools, storage and runtime.

## 1.2. In Scope

- Project configuration (`projects/{project_id}/project.yaml`).
- Runtime configuration (factory function `projects_root`, env var overrides).
- Environment variables (current `CONTENT_PLANT_*` historical naming).
- Configuration source hierarchy and precedence rules.
- Configuration validation (required fields, pydantic models, service validation).
- Local / dev / test / smoke modes.
- Project root resolution.
- Defaults and fallbacks.
- Brand configuration as derived from project config.
- Channel / platform configuration as resolved from project config.
- Future env var naming policy (`LOOPRA_*` migration path).
- Future secrets and credentials boundary.
- Future deployment configuration boundary.
- Future feature flags and capability flags.

## 1.3. Out of Scope

- Code implementation or modification.
- API endpoints.
- UI screens, forms, dashboards.
- Database schemas and migrations.
- Secrets manager implementation.
- Connector implementation or external platform integrations.
- SaaS billing, user management, tenancy implementation.
- Editing project settings through UI.
- New config files, env vars or settings (document-only).

---

# 2. Role of Configuration in LOOPRA

## 2.1. What Configuration Defines

Configuration defines how LOOPRA knows:

- which project is being operated;
- what brand context applies (name, positioning, audience, tone);
- what language and status the project has;
- what channels are targeted for content distribution;
- where runtime data is stored on the filesystem;
- what local mode is being used (smoke, dev, test);
- what future connectors, deployment environments and capability flags are
  enabled.

## 2.2. What Configuration Does NOT Do

Configuration does not:

- execute runtime logic;
- mutate domain entity state;
- decide content strategy or topic selection;
- publish content to external platforms;
- store secrets or credentials in project files;
- bypass service validation or domain transition rules.

## 2.3. Configuration and the Architecture Layers

```text
Project Config (project.yaml)
    ↓  loaded by FileSystemProjectRepository
    ↓  validated by ProjectService
    ↓  converted to Project domain entity
    ↓
Services (ProjectService, BrandProfileService, ScenarioService, etc.)
    ↓  use project identity, brand context, channel targets
    ↓
Runtime Orchestrator (LoopOrchestrator)
    ↓  uses services, passes project_id and resolved platform
    ↓
Tools / Scripts (smoke_loop.py, find_metric_snapshots.py, etc.)
    ↓  use env vars, CLI args, project_id
    ↓
Artifacts / State (export packages, metric snapshots)
```

---

# 3. Configuration Principles

1. **Project config is the source of project truth.** `project.yaml` defines
   what the project is — its identity, brand, language, channels and status.
   No other source overrides project identity.

2. **Runtime config is execution context, not project strategy.** Runtime
   configuration (projects_root, smoke project storage paths) describes how the
   system runs — where data is stored, what mode is active. It does not change
   what the project is or how content should be created.

3. **Environment variables are local/runtime overrides.** Env vars override
   runtime paths (projects_root, smoke project id) and local execution
   behaviour. They do not override project identity, brand configuration or
   content strategy.

4. **Secrets are never stored in `project.yaml`.** Credentials, API keys,
   tokens and any sensitive values must live outside project configuration.
   Current MVP has no secrets. Future secrets must use a dedicated secret
   manager.

5. **Services validate config before use.** Every service that reads
   configuration validates required fields before proceeding. Missing or
   invalid config raises explicit validation errors.

6. **Defaults must be explicit.** Every default value is documented in code
   (constant) or explicitly set in the configuration model. No hidden defaults
   that change behaviour silently.

7. **Historical names must be documented until migrated.** Current env var
   names use the `CONTENT_PLANT_*` prefix (historical working name). They
   remain operational. Future migration to `LOOPRA_*` must be documented,
   versioned and backward-compatible.

8. **Tests must isolate config roots.** Test suites use temporary directories
   and explicit `projects_root` overrides. No test pollutes the source
   `projects/` directory or commits to `storage/smoke_projects/`.

9. **Future deployment config must not break local MVP.** When deployment
   configuration is introduced (DB connection strings, object storage
   endpoints, service URLs), local filesystem MVP must remain fully
   operational without requiring deployment infrastructure.

10. **Agents must not silently edit configuration.** Future agents may propose
    config changes, but must not modify `project.yaml`, env vars or settings
    without explicit human approval and audit trail.

---

# 4. Configuration Source Hierarchy

## 4.1. Current Hierarchy (Verified from Code)

Configuration is resolved from the following sources, in order of increasing
precedence:

```text
1. Code-level defaults (constants in loader.py, services, scripts)
2. Canonical project.yaml at projects/{project_id}/project.yaml
3. Runtime copied project.yaml at storage/smoke_projects/{project_id}/project.yaml
   (same content as canonical copy, used as the runtime config source)
4. Environment variables (CONTENT_PLANT_*)
5. Factory function projects_root parameter (programmatic override)
6. Test-provided projects_root via temp directories

Future (conceptual):
7. Deployment configuration (environment name, DB DSN, object store bucket)
8. Secret store (credentials, API keys, tokens)
```

## 4.2. Precedence Rules (Current MVP, Verified)

| Source | Precedence | Scope | Overrides |
|---|---|---|---|
| Code defaults | Lowest | Global | Nothing |
| `project.yaml` (canonical) | Project identity | Per project | Code defaults |
| `project.yaml` (runtime copy) | Runtime context (same as canonical) | Per smoke run | None (identical to canonical) |
| Env vars (`CONTENT_PLANT_*`) | Runtime override | Process-wide | `projects_root`, smoke project ID |
| Factory `projects_root` param | Programmatic override | Per invocation | Env vars, code defaults |
| Test temp dirs | Test isolation | Per test | All of the above |

## 4.3. Conceptual Future Precedence

```text
Code defaults < project.yaml < env vars < CLI flags < deployment config < secret store
```

Exact precedence for future layers is conceptual and must be defined in
dedicated deployment and secrets specifications before implementation.

---

# 5. Project Configuration

## 5.1. Canonical Path

```text
projects/{project_id}/project.yaml
```

**Loaded by:** `FileSystemProjectRepository.load_project_config(project_id)`
→ `load_project(project_id, projects_root)` → `ProjectConfig.model_validate()`.

**Used by:** `ProjectService.get_project()`, `BrandProfileService.get_brand_profile()`,
`ScenarioService.create_from_idea()`.

## 5.2. Purpose

Project configuration defines:

- project identity (id, name, slug, description);
- workspace membership;
- language, timezone, status;
- primary URL;
- target platforms (channel preferences);
- brand context (name, positioning, audience, tone of voice, content rules);
- future: goals, analytics settings, autonomy mode, content type preferences.

## 5.3. ProjectConfig Model

**File:** `core/projects/loader.py:78-118`

The `ProjectConfig` pydantic model is the canonical deserialized form of
`project.yaml`.

### Required Fields

| Config field | Model field | Type | Purpose |
|---|---|---|---|
| `project_id` (or `id`) | `id` | `str` | Unique project identifier |
| (none other strictly required by pydantic — but service validates) | | | |

`ProjectConfig` itself only requires `id` at the pydantic level (all other
fields have defaults). Requiredness is enforced by `ProjectService` validation
(see Section 13).

### Fields (with aliases from YAML)

| YAML key | Model field | Type | Default | Alias support |
|---|---|---|---|---|
| `project_id` | `id` | `str` | (required) | `project_id` → `id` |
| `project_name` | `name` | `str` | `""` | `project_name` → `name` |
| `project_slug` | `slug` | `str` | `""` | `project_slug` → `slug` |
| `default_language` | `language` | `str` | `"ru"` | `default_language` → `language` |
| `workspace_id` | `workspace_id` | `str` | `"internal"` | — |
| `description` | `description` | `str` | `""` | — |
| `status` | `status` | `str` | `"active"` | — |
| `timezone` | `timezone` | `str` | `"UTC"` | — |
| `primary_url` | `primary_url` | `str` | `""` | — |
| `target_platforms` | `target_platforms` | `list[str]` | `[]` | — |
| `brand` | `brand` | `BrandConfig` | `BrandConfig()` | — |
| `audience` | `audience` | `dict` | `{}` | — |
| `cta` | `cta` | `dict` | `{}` | — |
| `video` | `video` | `VideoConfig` | `VideoConfig()` | — |
| `assets` | `assets` | `AssetsConfig` | `AssetsConfig()` | — |
| `prompts` | `prompts` | `PromptsConfig` | `PromptsConfig()` | — |
| `templates` | `templates` | `TemplatesConfig` | `TemplatesConfig()` | — |

`project_dir` is auto-populated during `load_project()` and is not stored in
YAML.

### Alias Normalization

`ProjectConfig.normalize_project_fields()` (a `@model_validator(mode="before")`)
supports legacy field names so that both old and new YAML keys are accepted:

| Legacy YAML key | Normalized to |
|---|---|
| `project_id` | `id` |
| `project_name` | `name` |
| `project_slug` | `slug` |
| `default_language` | `language` |

Current project YAML files use the legacy keys (`project_id`, `project_name`,
`project_slug`, `default_language`). The alias mechanism preserves backward
compatibility.

## 5.4. Required Fields (Service-Level Validation)

`ProjectService._validate_required_fields()` at
`core/services/projects.py:108-113` enforces that the following fields are
present and non-empty:

| Field | Config source | Validated by |
|---|---|---|
| `project_id` | `config.id` | `ProjectService._validate_required_fields()` |
| `project_name` | `config.name` | `ProjectService._validate_required_fields()` |
| `project_slug` | `config.slug` | `ProjectService._validate_required_fields()` |
| `default_language` | `config.language` | `ProjectService._validate_required_fields()` |
| `status` | `config.status` (must be valid `ProjectStatus` enum) | `ProjectService._parse_project_status()` |

Missing or empty fields raise `ProjectConfigValidationError`.

## 5.5. Status Validation

`ProjectService._parse_project_status()` validates that `config.status` is a
valid `ProjectStatus` enum value. Valid values:

```text
draft, active, paused, archived
```

Invalid status values raise `ProjectConfigValidationError` with a message
listing allowed values.

## 5.6. Project YAML Format

Current project YAML files use JSON syntax (even though the file extension is
`.yaml`). The loader (`_load_config`) tries `yaml.safe_load()` first (if
PyYAML is installed), falls back to `json.loads()`, and finally falls back to
a built-in simple YAML parser. Both JSON and YAML syntax are supported.

## 5.7. Project ID Validation

`validate_project_id()` in `core/projects/loader.py:136-147` enforces:

- must be a non-empty string;
- must match `^[a-z0-9][a-z0-9_-]*$`;
- must not contain path separators;
- must resolve within the projects root directory (path traversal protection).

Invalid project IDs raise `InvalidProjectIdError`.

## 5.8. Current Project Inventory

The `projects/` directory contains two projects:

| Project ID | Slug | Language | Status |
|---|---|---|---|
| `example` | `example_project` | `en` | `active` |
| `nura` | `nura` | `ru` | `active` |

---

# 6. Brand Configuration

## 6.1. Source

Brand configuration is embedded within `project.yaml` under the `brand` key.
It is not a separate file.

## 6.2. BrandConfig Model

**File:** `core/projects/loader.py:20-50`

| Field | Type | Default | Purpose |
|---|---|---|---|
| `name` | `str` | `""` | Brand name |
| `description` | `str` | `""` | Brand description |
| `positioning` | `str` | `""` | Market positioning statement |
| `audience_summary` | `str` | `""` | Target audience description |
| `language` | `str` | `""` | Brand language override (falls back to project language) |
| `status` | `str` | `""` | Brand status (raw string, resolved by service) |
| `brand_values` | `list[str]` | `[]` | Core brand values |
| `tone_of_voice` | `dict` | `{}` | Tone summary, keywords, allowed/forbidden phrases |
| `content_rules` | `dict` | `{}` | Allowed topics, forbidden topics, writing rules, claim restrictions |
| `colors` | `dict` | `{}` | Brand colors |
| `fonts` | `dict` | `{}` | Brand fonts |
| `tone` | `str` | `""` | Legacy tone field (merged into `tone_of_voice.tone_summary`) |

### Alias Normalization

`BrandConfig.normalize_brand_fields()` supports legacy aliases:

| Legacy YAML key | Normalized to |
|---|---|
| `brand_name` | `name` |
| `brand_description` | `description` |

## 6.3. BrandProfileService

**File:** `core/services/projects.py:116-175`

`BrandProfileService.get_brand_profile(project_id)` derives a `BrandProfile`
domain entity from the raw `ProjectConfig` + `BrandConfig`.

### Required Brand Fields (Service-Level Validation)

`BrandProfileService._validate_brand_fields()` enforces:

| Config path | Field | Error if |
|---|---|---|
| `brand.name` | `config.brand.name` | Missing or empty |
| `brand.positioning` | `config.brand.positioning` | Missing or empty |
| `brand.audience_summary` | `config.brand.audience_summary` | Missing or empty |

Missing brand fields raise `ProjectConfigValidationError` with a message
listing the missing fields.

### Status Resolution

```text
If config.brand.status is a valid BrandProfileStatus → use it.
If positioning and audience_summary are present → ACTIVE.
Otherwise → INCOMPLETE.
```

### Derived Fields

`BrandProfileService` constructs the `BrandProfile` with:

- `brand_profile_id`: `f"brand_{project.project_id}"`
- `name`: from `config.brand.name`
- `positioning`: from `config.brand.positioning`
- `audience_summary`: from `config.brand.audience_summary`
- `language`: from `config.brand.language` or project `default_language`
- `brand_values`: from `config.brand.brand_values`
- `tone_of_voice`: `BrandToneOfVoice` model from `config.brand.tone_of_voice`
  dict (legacy `config.brand.tone` merged into `tone_summary` if present)
- `content_rules`: `BrandContentRules` model from `config.brand.content_rules`
  dict
- `status`: resolved via `_resolve_brand_status()`

### Optional Brand Fields

These fields are validated at the domain model level (pydantic), not by
`BrandProfileService` directly:

| Field | Stored in `BrandProfile` |
|---|---|
| Tone of voice summary | `tone_of_voice.tone_summary` |
| Style keywords | `tone_of_voice.style_keywords` |
| Allowed phrases | `tone_of_voice.allowed_phrases` |
| Forbidden phrases | `tone_of_voice.forbidden_phrases` |
| Allowed topics | `content_rules.allowed_topics` |
| Forbidden topics | `content_rules.forbidden_topics` |
| Writing rules | `content_rules.writing_rules` |
| Claim restrictions | `content_rules.claim_restrictions` |

## 6.4. How Brand Config Is Used

| Service | Usage |
|---|---|
| `BrandProfileService` | Loads and validates brand config, returns `BrandProfile` |
| `ScenarioService.create_from_idea()` | Reads brand profile for tone, rules, QA checks |
| `PublishingService.prepare_export()` | Writes brand info into `metadata.json` |

---

# 7. Channel / Platform Configuration

## 7.1. Current MVP

Channel configuration in the current MVP is minimal:

- `project.yaml` may contain `target_platforms`: a list of platform
  identifiers (e.g., `["telegram", "threads", "vk"]`).
- `ScenarioService.create_from_idea()` resolves target platforms from:
  1. Explicit `target_platforms` parameter passed to the method.
  2. `config.target_platforms` from project config.
  3. Hardcoded defaults `[TELEGRAM, THREADS, VK]` (in `ScenarioService`).
- `LoopOrchestrator.run_minimal_loop()` resolves the target platform from:
  1. Explicit `target_platform` parameter.
  2. First platform in `scenario.target_platforms`.
- `PublishingService.prepare_export()` writes `caption_{platform}.txt` for
  the resolved platform.
- Current MVP supports a single platform per export. Multi-platform export is
  future.

### Current Supported Platforms

```text
telegram, threads, vk, instagram, tiktok, youtube_shorts, linkedin, x, facebook, pinterest
```

Only the resolved platform is used for export. Platform-specific constraints
(character limits, aspect ratios) are not enforced in current MVP.

## 7.2. Future Channel Configuration (Conceptual)

Future `project.yaml` may include structured channel configuration per
platform:

```yaml
channels:
  - platform: telegram
    enabled: true
    account_reference: "@channel_name"
    content_formats: [text_social_post, educational_carousel]
    schedule_preferences: {days: [mon, wed, fri], time: "10:00 MSK"}
    caption_rules: "..."
    hashtag_rules: "..."
    cta_rules: "..."
```

This is conceptual. Current MVP uses only `target_platforms` list.
Reference: `docs/00_foundation/PROJECT_SETTINGS_SPEC.md`, Section 5.

---

# 8. Runtime Configuration

## 8.1. What Runtime Configuration Answers

Runtime configuration answers:

- where project roots are (`projects_root`);
- where smoke project runtime storage is;
- which `project_id` to run the smoke loop for;
- which local mode is being used;
- which tests override which storage paths.

## 8.2. Current Runtime Config Sources

### `PROJECTS_ROOT` (Code Default)

**File:** `core/projects/loader.py:11-12`

```python
CONTENT_PLANT_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = CONTENT_PLANT_ROOT / "projects"
```

`PROJECTS_ROOT` is the default projects root — `{REPO_ROOT}/projects/`. It is
used as the fallback when no override is provided.

`CONTENT_PLANT_ROOT` is a historical internal variable name. It resolves to the
repository root and is not an env var.

### `projects_root` Parameter (Factory Functions)

All factory functions accept an optional `projects_root: Path | None = None`
parameter:

| Factory | File |
|---|---|
| `build_loop_orchestrator(projects_root)` | `core/services/loop.py:134` |
| `build_production_lifecycle_service(projects_root)` | `core/services/production.py:125` |
| `build_publishing_service(projects_root)` | `core/services/publishing.py:369` |
| `build_analytics_service(projects_root)` | `core/services/analytics.py:175` |
| `FileSystemProjectRepository(projects_root)` | `core/services/projects.py:29` |

When `projects_root` is `None`, each repository and service falls back to
`PROJECTS_ROOT`.

### Env Var Overrides (Process-Level)

| Env Var | Used By | Default |
|---|---|---|
| `CONTENT_PLANT_SMOKE_PROJECT_ID` | `smoke_loop.py` | `"example"` |
| `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` | `smoke_loop.py` | `{REPO_ROOT}/storage/smoke_projects` |
| `CONTENT_PLANT_PROJECTS_ROOT` | `find_metric_snapshots.py`, `import_manual_metrics.py` | `PROJECTS_ROOT` |

These env vars override runtime behaviour — not project identity.

### Test-Provided Roots (Test Isolation)

Tests create temporary directories and pass them as `projects_root`:

```python
with tempfile.TemporaryDirectory() as tmp_dir:
    projects_root = Path(tmp_dir) / "projects_root"
    # Write project fixture
    # Build services with projects_root
    # Run assertions
```

Tests also set `CONTENT_PLANT_PROJECTS_ROOT` and
`CONTENT_PLANT_SMOKE_PROJECTS_ROOT` env vars to point to temp directories when
running scripts as subprocesses.

## 8.3. Runtime Config Is Not Project Config

Critical boundary:

| What | Category | Source |
|---|---|---|
| Project identity, brand, language, channels | **Project config** | `project.yaml` |
| Where project data is stored on disk | **Runtime config** | `projects_root` param / env var |
| Which project to run smoke loop for | **Runtime config** | Env var / default |
| How the system behaves locally | **Runtime config** | Env var / default |

Runtime config must never override project identity.

---

# 9. Environment Variables — Current MVP

## 9.1. All Current Env Vars (Verified from Code)

| Env Var | Used By | Default | Purpose | Status |
|---|---|---|---|---|
| `CONTENT_PLANT_SMOKE_PROJECT_ID` | `scripts/smoke_loop.py:36` | `"example"` | Project ID to use for the smoke loop | Current (historical naming) |
| `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` | `scripts/smoke_loop.py:41` | `{REPO_ROOT}/storage/smoke_projects` | Root directory for runtime smoke project storage | Current (historical naming) |
| `CONTENT_PLANT_PROJECTS_ROOT` | `scripts/find_metric_snapshots.py:34`, `scripts/import_manual_metrics.py:39` | `PROJECTS_ROOT` (`{REPO_ROOT}/projects`) | Override projects root directory | Current (historical naming) |

## 9.2. Detailed Env Var Contracts

### `CONTENT_PLANT_SMOKE_PROJECT_ID`

- **File:** `scripts/smoke_loop.py:35-37`
- **Purpose:** Select which project to run the smoke loop for.
- **Default:** `"example"`
- **Resolution:** `os.environ.get("CONTENT_PLANT_SMOKE_PROJECT_ID", DEFAULT_PROJECT_ID).strip()`
  Falls back to `DEFAULT_PROJECT_ID` if env var is empty string after stripping.
- **Validation:** The resolved `project_id` must correspond to a directory under
  `REPO_ROOT / "projects"` containing a valid `project.yaml`. Absent or invalid
  config raises `FileNotFoundError`.
- **Migration note:** Uses `CONTENT_PLANT_*` historical prefix. Must be
  aliased to `LOOPRA_SMOKE_PROJECT_ID` in future without breaking existing
  usage.

### `CONTENT_PLANT_SMOKE_PROJECTS_ROOT`

- **File:** `scripts/smoke_loop.py:40-44`
- **Purpose:** Override the runtime directory where smoke project config is
  copied and artifacts are stored.
- **Default:** `{REPO_ROOT}/storage/smoke_projects`
- **Resolution:** If env var is set and non-empty, treat as a filesystem path
  (expanded via `Path.expanduser().resolve()`). If not set, use the default.
- **Effect:** Controls where `_ensure_runtime_project()` copies the source
  `project.yaml` and where all subsequent runtime entities and exports are
  written.
- **Migration note:** Uses `CONTENT_PLANT_*` historical prefix. Must be
  aliased to `LOOPRA_SMOKE_PROJECTS_ROOT`.

### `CONTENT_PLANT_PROJECTS_ROOT`

- **File:**
  - `scripts/find_metric_snapshots.py:33-37`
  - `scripts/import_manual_metrics.py:38-42`
- **Purpose:** Override the projects root directory used by
  `find_metric_snapshots.py` and `import_manual_metrics.py`.
- **Default:** `PROJECTS_ROOT` (`{REPO_ROOT}/projects`)
- **Resolution:** If env var is set and non-empty, treat as a filesystem path
  (expanded via `Path.expanduser().resolve()`). If not set, use `PROJECTS_ROOT`.
- **Effect:** Controls which `projects/` directory the tools read from when
  validating project existence and reading/writing metric snapshots.
- **Migration note:** Uses `CONTENT_PLANT_*` historical prefix. Must be
  aliased to `LOOPRA_PROJECTS_ROOT`.

## 9.3. Env Vars NOT Present in Current MVP

The following are confirmed absent:

- No `.env` file in the repository root (`trend-radar/.env` and
  `video-assembler/.env.example` belong to sub-projects, not LOOPRA core).
- No `.env.example` in the repository root.
- No `LOOPRA_*` env vars defined or used.
- No `DATABASE_URL`, `SECRET_KEY`, `API_KEY` or deployment-related env vars.
- No feature flag env vars.
- No log level env var.
- No environment name env var (e.g., `ENV`, `APP_ENV`).

## 9.4. How Tests Use Env Vars

Tests set env vars programmatically when running scripts as subprocesses:

```python
env = os.environ.copy()
env["CONTENT_PLANT_PROJECTS_ROOT"] = str(self.projects_root)
env["CONTENT_PLANT_SMOKE_PROJECTS_ROOT"] = str(runtime_projects_root)
subprocess.run([sys.executable, str(SCRIPT_PATH)], env=env, ...)
```

This ensures tests are fully isolated from source directories and other tests.

---

# 10. Environment Variable Naming Policy

## 10.1. Current State

All env vars currently use the `CONTENT_PLANT_*` prefix — the historical
working name of the project. These names are operational and must not be
broken.

## 10.2. Future LOOPRA Naming Convention

When migration occurs:

| Current Name | Future Canonical Name | Migration Rule |
|---|---|---|
| `CONTENT_PLANT_PROJECTS_ROOT` | `LOOPRA_PROJECTS_ROOT` | Support both; prefer new; document old as deprecated |
| `CONTENT_PLANT_SMOKE_PROJECT_ID` | `LOOPRA_SMOKE_PROJECT_ID` | Support both; prefer new; document old as deprecated |
| `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` | `LOOPRA_SMOKE_PROJECTS_ROOT` | Support both; prefer new; document old as deprecated |

### Migration Rules

1. Old env vars must remain supported during migration — no silent breaking
   changes.
2. New `LOOPRA_*` vars are checked first; fall back to `CONTENT_PLANT_*` if
   not set.
3. Document aliases in code and in this specification.
4. Remove old names only after a deprecation period with warnings.
5. Do not mix project settings with env vars — env vars are runtime overrides
   only.

### Possible Future Env Vars (Conceptual)

| Env Var | Purpose | Status |
|---|---|---|
| `LOOPRA_PROJECTS_ROOT` | Override projects root directory | Future (canonical alias) |
| `LOOPRA_SMOKE_PROJECT_ID` | Smoke loop project ID | Future (canonical alias) |
| `LOOPRA_SMOKE_PROJECTS_ROOT` | Smoke loop runtime storage root | Future (canonical alias) |
| `LOOPRA_ENV` | Environment name (development, staging, production) | Future |
| `LOOPRA_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | Future |
| `LOOPRA_DATABASE_URL` | Database connection string | Future |
| `LOOPRA_OBJECT_STORE_BUCKET` | Object storage bucket name | Future |
| `LOOPRA_SECRETS_PATH` | Path to secrets file or manager endpoint | Future |

None of these are implemented. Mark as future/conceptual.

---

# 11. Local / Dev / Test / Smoke Modes

## 11.1. Mode Definitions

### Local Development Mode

```text
Environment: Developer workstation
Project config: projects/{project_id}/project.yaml (source, committed)
Runtime artifacts: storage/smoke_projects/ (via smoke_loop.py)
Execution: Manual CLI invocation of scripts
Scope: Single project at a time
State: In-memory execution context
Storage: Filesystem JSON
Secrets: None
```

Current MVP operates exclusively in Local Development mode. There is no
distinction between "development" and "production" — the system runs the same
way regardless.

### Smoke Mode

```text
Environment: Developer workstation or CI
Project config: Copied from projects/ to storage/smoke_projects/
Runtime artifacts: storage/smoke_projects/{project_id}/data/ and exports/
Execution: smoke_loop.py via CLI or test subprocess
Scope: Single project, full Foundation MVP lifecycle
State: In-memory (LoopOrchestrator)
Artifacts: All entity types + export package files
Idempotency: Non-idempotent — new entities on every run
Git: storage/ is gitignored
```

Smoke mode is triggered by `python scripts/smoke_loop.py`. It copies the
source project config, runs the full lifecycle, and writes all artifacts under
`storage/smoke_projects/{project_id}/`.

Smoke mode is verified by `tests/services/test_smoke_loop.py`.

### Test Mode

```text
Environment: pytest runner
Project config: Generated fixture JSON in temp directory
Runtime artifacts: temp directory (cleaned up after test)
Execution: Programmatic service calls or subprocess invocations
Scope: Per-test isolation
State: Fresh services per test
Data: Clean temp directory per test
Isolation: No pollution of source projects/ or storage/
```

Test mode uses `tempfile.TemporaryDirectory()` to create isolated
`projects_root` directories. Test fixtures write minimal `project.yaml` files.
After each test, the temp directory is cleaned up.

Importantly, test mode does NOT use the source `projects/example/project.yaml`
for mutations — it copies the JSON payload into temp directories. The source
project config is read-only during tests.

### Future Production Mode (Conceptual)

```text
Environment: Deployed server
Project config: DB-backed project records
Runtime artifacts: DB + object storage
Execution: API triggers, scheduled jobs, agent-initiated cycles
Scope: Multi-project, multi-workspace
State: Persisted RuntimeExecutionContext
Secrets: Secret manager
Connectors: Enabled per project
```

Production mode is a future concept. The current MVP has no deployment
infrastructure, no API server, no DB, and no external connectors.

## 11.2. Mode Detection

Current MVP has no explicit mode detection mechanism. The "mode" is implicit
based on how the code is invoked:

| Invocation | Implicit Mode |
|---|---|
| `python scripts/smoke_loop.py` | Smoke |
| `python scripts/inspect_package.py <dir>` | Development |
| `python scripts/validate_package.py <dir>` | Development |
| `python scripts/find_metric_snapshots.py <id>` | Development |
| `python scripts/import_manual_metrics.py <json>` | Development |
| `pytest tests/` | Test |
| Programmatic service calls | Test (in tests) / Development (in tools) |

Future: a `LOOPRA_ENV` env var or `--env` CLI flag may explicitly set the
mode. Not implemented.

---

# 12. Project Root Resolution

## 12.1. Resolution Flow

```text
1. projects_root parameter passed to factory function
       │
       ├── If not None → use explicit projects_root
       │
       └── If None → use PROJECTS_ROOT constant
              │
              └── PROJECTS_ROOT = CONTENT_PLANT_ROOT / "projects"
                     │
                     └── CONTENT_PLANT_ROOT = repo root (parents[2] of loader.py)
```

## 12.2. Resolution Components

| Component | Definition | File |
|---|---|---|
| `CONTENT_PLANT_ROOT` | `Path(__file__).resolve().parents[2]` → repository root | `core/projects/loader.py:11` |
| `PROJECTS_ROOT` | `CONTENT_PLANT_ROOT / "projects"` → `{REPO_ROOT}/projects/` | `core/projects/loader.py:12` |
| `resolve_project_dir(project_id, projects_root)` | `(projects_root / safe_project_id).resolve()` | `core/projects/loader.py:150-160` |
| `projects_root` parameter | Optional override in all factory functions | Various |

## 12.3. Root Types by Context

| Context | Root Used | Path |
|---|---|---|
| Source config (canonical) | `PROJECTS_ROOT` | `{REPO_ROOT}/projects/` |
| Smoke runtime | `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` or default | `{REPO_ROOT}/storage/smoke_projects/` |
| Test | `tempfile.TemporaryDirectory()` | Random temp path |
| Programmatic (test/dev) | Explicit `projects_root` param | Caller-defined |

## 12.4. Path Traversal Protection

`resolve_project_dir()` at `core/projects/loader.py:150-160` protects against
path traversal attacks:

1. Validates `project_id` against `^[a-z0-9][a-z0-9_-]*$` (rejects `..`, `/`,
   spaces, uppercase).
2. Resolves the absolute path.
3. Verifies the resolved path is a child of `projects_root` via
   `Path.relative_to()`.
4. Raises `InvalidProjectIdError` if the path escapes the root.

---

# 13. Configuration Validation

## 13.1. Validation Points

Configuration is validated at multiple layers:

```text
Layer 1: Filesystem (file existence, directory structure)
    → FileSystemProjectRepository.list_project_ids()
    → load_project() config_path.exists()
    → resolve_project_dir() path traversal check

Layer 2: Deserialization (YAML/JSON parsing, pydantic model)
    → _load_config() YAML/JSON parser
    → ProjectConfig.model_validate()
    → BrandConfig.model_validate()

Layer 3: Domain Validation (service-level required fields, enum parsing)
    → ProjectService._validate_required_fields()
    → ProjectService._parse_project_status()
    → BrandProfileService._validate_brand_fields()
    → BrandProfileService._resolve_brand_status()

Layer 4: Input Validation (CLI args, JSON payloads, env vars)
    → Script-level argument parsing
    → import_manual_metrics.py _validate_payload()
    → find_metric_snapshots.py snapshot field validation
    → validate_project_id() ID format check
```

## 13.2. Validation Table

| Config Area | Validator | File | Error | When |
|---|---|---|---|---|
| Project ID format | `validate_project_id()` | `loader.py:136` | `InvalidProjectIdError` | Any project_id input |
| YAML/JSON parse | `_load_config()` | `loader.py:177` | `ValueError` | Loading project.yaml |
| Pydantic model | `ProjectConfig.model_validate()` | `loader.py:174` | `ValidationError` | Deserialization |
| Required project fields | `ProjectService._validate_required_fields()` | `projects.py:108` | `ProjectConfigValidationError` | `get_project()` |
| Project status enum | `ProjectService._parse_project_status()` | `projects.py:100` | `ProjectConfigValidationError` | `get_project()` |
| Required brand fields | `BrandProfileService._validate_brand_fields()` | `projects.py:162` | `ProjectConfigValidationError` | `get_brand_profile()` |
| Brand status resolution | `BrandProfileService._resolve_brand_status()` | `projects.py:153` | (falls back, no error) | `get_brand_profile()` |
| Script env var path | `_resolve_runtime_projects_root()` | `smoke_loop.py:40` | (uses default) | Script start |
| Script env var path | `_resolve_projects_root()` | `find_metric_snapshots.py:33` | (uses default) | Script start |
| JSON payload structure | `_validate_payload()` | `import_manual_metrics.py:61` | `ValueError` | Manual metrics import |
| Snapshot JSON fields | `_load_metric_snapshot()` | `find_metric_snapshots.py:62` | `ValueError` | Snapshot listing |
| Path traversal | `resolve_project_dir()` | `loader.py:150` | `InvalidProjectIdError` | Project dir resolution |

## 13.3. Entity ID Validation

Repository base class `FileSystemProjectModelRepository._validate_entity_id()`
at `core/services/_storage.py:69` validates entity IDs against
`^[a-z0-9][a-z0-9_-]*$` — same pattern as project IDs.

---

# 14. Configuration Errors

## 14.1. Error Catalog

| Error | Raised By | Typical Cause | Recommended Action |
|---|---|---|---|
| `ProjectConfigValidationError` — missing required fields | `ProjectService` | `project.yaml` missing `project_id`, `project_name`, `project_slug`, `default_language` or `status` | Populate missing fields in `project.yaml` |
| `ProjectConfigValidationError` — invalid status | `ProjectService._parse_project_status()` | `status` value is not a valid `ProjectStatus` enum member | Use `draft`, `active`, `paused` or `archived` |
| `ProjectConfigValidationError` — missing brand fields | `BrandProfileService._validate_brand_fields()` | `brand.name`, `brand.positioning` or `brand.audience_summary` missing/empty | Populate missing brand fields in `project.yaml` |
| `InvalidProjectIdError` | `validate_project_id()`, `resolve_project_dir()` | `project_id` contains invalid characters, is empty, or escapes root | Use `^[a-z0-9][a-z0-9_-]*$` compliant ID |
| `FileNotFoundError` — project config | `load_project()` | `project.yaml` does not exist at `projects/{project_id}/project.yaml` | Create `project.yaml` or use correct `project_id` |
| `FileNotFoundError` — smoke source config | `smoke_loop.py._ensure_runtime_project()` | Source `project.yaml` not found for resolved `project_id` | Ensure project exists under `projects/` |
| `FileNotFoundError` — entity not found | Repository `load_*()` methods | Entity JSON file does not exist at expected path | Verify entity ID and project state |
| `ValueError` — invalid entity ID | `_validate_entity_id()` | Entity ID does not match `^[a-z0-9][a-z0-9_-]*$` | Use correctly formatted entity ID |
| `ValueError` — invalid manual metrics JSON | `_load_json_file()`, `_validate_payload()` | JSON file is malformed, missing required fields, or contains wrong types | Fix JSON structure per `import_manual_metrics.py` contract |
| `ValueError` — invalid snapshot JSON | `_load_metric_snapshot()` | Snapshot JSON is malformed or missing required fields | Regenerate snapshot or fix JSON manually |

## 14.2. Error Handling Flow

```text
Config error raised
    ↓
Propagated to caller (service, script, test)
    ↓
Script: printed to stderr with ERROR: prefix, exit code 1
Test: caught by assertRaises, test fails with diagnostic
Programmatic: exception propagates to calling code
```

Current MVP does not catch and retry config errors — the operator or test must
fix the underlying issue and rerun.

---

# 15. Defaults and Fallbacks

## 15.1. Code-Level Defaults (Verified)

| Default | Value | Defined In | Used By |
|---|---|---|---|
| `projects_root` | `PROJECTS_ROOT` (`{REPO}/projects`) | `loader.py:12` | All repositories and services |
| `PROJECTS_ROOT` (fallback) | `PROJECTS_ROOT` | `loader.py:12` | `find_metric_snapshots.py`, `import_manual_metrics.py` |
| Smoke project ID | `"example"` | `smoke_loop.py:31` | `smoke_loop.py` |
| Smoke projects root | `{REPO}/storage/smoke_projects` | `smoke_loop.py:32` | `smoke_loop.py` |
| Default language | `"ru"` | `ProjectConfig.language` | `ProjectService` |
| Default status | `"active"` | `ProjectConfig.status` | `ProjectService` |
| Default workspace | `"internal"` | `WorkspaceService` | `ProjectService` |
| Default workspace ID | `"internal"` | `loader.py:81` | `ProjectConfig.workspace_id` |
| Target platforms | `[TELEGRAM, THREADS, VK]` (service fallback) | `ScenarioService` | `create_from_idea()` |
| Default funnel stage | `"attention"` | `IdeaService.create_idea()` | Idea creation |
| Default source type | `"manual"` | `IdeaService.create_idea()` | Idea creation |
| Default priority | `"medium"` | `IdeaService.create_idea()` | Idea creation |
| Default content format | `TEXT_SOCIAL_POST` | `IdeaService.create_idea()` | Idea creation |

## 15.2. Service-Level Fallbacks

| Fallback | Logic | Service |
|---|---|---|
| Brand language | `config.brand.language or project.default_language` | `BrandProfileService` |
| Brand status | Resolved from `config.brand.status`, then `config.status`, then positioning/audience check, then `INCOMPLETE` | `BrandProfileService` |
| Workspace ID | `config.workspace_id or workspace.workspace_id` | `ProjectService` |
| Tone summary | `config.brand.tone` merged into `tone_of_voice.tone_summary` if `tone_summary` empty | `BrandProfileService` |
| Target platform | Explicit param → scenario platforms[0] → `ValueError` | `LoopOrchestrator` |

## 15.3. Future Defaults (Conceptual)

None currently defined. Future defaults for deployment config, log levels, and
feature flags must be defined in dedicated specifications.

---

# 16. Configuration and Services

## 16.1. Service Configuration Usage

| Service | Config Dependency | How It Accesses Config |
|---|---|---|
| `ProjectService` | `project.yaml` via `FileSystemProjectRepository` | `load_project_config()` → `ProjectConfig` → validates required fields → returns `Project` |
| `BrandProfileService` | `project.yaml` brand section | `load_project_config()` → `BrandConfig` → validates brand fields → returns `BrandProfile` |
| `IdeaService` | Project existence | Calls `ProjectService.get_project()` for validation |
| `ScenarioService` | Project config, brand profile, target platforms | Reads `config.target_platforms`, calls `BrandProfileService.get_brand_profile()` |
| `ProductionLifecycleService` | Project existence | Calls `ProjectService.get_project()` for validation |
| `PublishingService` | Project existence, project root for export paths | Calls `ProjectService.get_project()`, uses `projects_root` for export directory |
| `AnalyticsService` | Project existence | Calls `ProjectService.get_project()` for validation |
| `LoopOrchestrator` | Project existence (via services) | Passes `project_id` to services |

## 16.2. Service Config Boundaries

Services must NOT:

- Read environment variables directly (scripts read env vars, not services).
- Read `project.yaml` directly outside of `ProjectService`/`BrandProfileService`.
- Modify project configuration.
- Store configuration-derived values as mutable global state.
- Access configuration from other projects.

Services must:

- Use `ProjectService.get_project()` for project identity and status.
- Use `BrandProfileService.get_brand_profile()` for brand context.
- Validate preconditions before using configuration values.
- Raise explicit errors when required configuration is missing.

## 16.3. Env Var Usage in Services

Current MVP services do NOT read environment variables. Env vars are read
exclusively by CLI scripts and tools. This is a deliberate separation:

```text
Scripts    →  read env vars, resolve paths, build services
Services   →  receive explicit parameters (projects_root, project_id, etc.)
Runtime    →  orchestrates services with parameters
```

---

# 17. Configuration and Tools

## 17.1. Tool Configuration Dependency

| Tool | Config Sources | Env Vars Used |
|---|---|---|
| `smoke_loop.py` | `project.yaml` (copied to runtime), hardcoded Idea params | `CONTENT_PLANT_SMOKE_PROJECT_ID`, `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` |
| `inspect_package.py` | `manifest.json` from export package directory | None |
| `validate_package.py` | `manifest.json` and export directory files | None |
| `find_metric_snapshots.py` | `project.yaml` for validation, `metric_snapshots/*.json` for data | `CONTENT_PLANT_PROJECTS_ROOT` |
| `import_manual_metrics.py` | Input JSON payload (project_id, metric_snapshot_id, metrics) | `CONTENT_PLANT_PROJECTS_ROOT` |

## 17.2. Tool Config Boundaries

- Tools must document their env var usage and defaults.
- Tools must not modify project configuration.
- Tools must validate CLI arguments before reading configuration.
- Tools must exit with code 1 on configuration errors.
- Tools must print error messages to stderr.

---

# 18. Configuration and Storage

## 18.1. Source vs Runtime Config Storage

```text
Source (committed):
    projects/{project_id}/project.yaml     — canonical config, authoritatively defines project

Runtime (gitignored):
    storage/smoke_projects/{project_id}/project.yaml  — copy of canonical, used as runtime source
```

## 18.2. Config Copy on Smoke Run

`smoke_loop.py._ensure_runtime_project()` at `scripts/smoke_loop.py:47-57`:

1. Reads source config from `{REPO_ROOT}/projects/{project_id}/project.yaml`.
2. Creates `storage/smoke_projects/{project_id}/` directory.
3. Copies project.yaml via `shutil.copyfile()`.
4. Returns the runtime project directory path.

The runtime copy is identical to the canonical config. Runtime never modifies
the canonical config.

## 18.3. Project Dir Resolution

`resolve_project_dir(project_id, projects_root)` at
`core/projects/loader.py:150-160`:

```text
Input:  project_id="example", projects_root=PROJECTS_ROOT
Result: {REPO_ROOT}/projects/example/
```

All entity JSON files are stored under `{project_dir}/data/{collection}/`.
All export files are stored under `{project_dir}/exports/{export_package_id}/`.

## 18.4. Future DB-Backed Config (Conceptual)

When project configuration moves to a database:

- `project.yaml` may become a DB record (`projects` table).
- `FileSystemProjectRepository` would be replaced by a DB-backed repository.
- Services must retain the same method signatures.
- Local filesystem MVP must remain operational for development and testing.
- A separate DB migration specification is required before implementation.

Reference: `docs/05_platform/STORAGE_AND_STATE_SPEC.md`, Sections 19, 26.

---

# 19. Configuration and Future Agents

## 19.1. What Agents May Request

Future agents may request:

- Read project config summary (identity, status, brand context).
- Validate project configuration.
- Propose configuration changes (new channels, updated brand fields, goal
  changes).
- Ask human to approve proposed changes.

## 19.2. What Agents Must NOT Do

Agents must not:

- Silently edit `project.yaml`.
- Inject secrets or credentials into project configuration.
- Override environment variables without operator knowledge.
- Change autonomy mode without explicit approval.
- Change connector settings without explicit approval.
- Access configuration from other projects without explicit scope.

## 19.3. Config Change Audit (Future)

All agent-initiated config changes must be:

- Recorded in an audit log.
- Linked to the agent decision that triggered the change.
- Reviewable by a human operator.
- Reversible or versioned.

Current MVP has no agent-layer config access. These rules are conceptual.

---

# 20. Secrets and Credentials Boundary

## 20.1. Current MVP State

Current Foundation MVP:

- has no connector secrets;
- has no external API keys;
- has no database credentials;
- has no secret store;
- requires no authentication.

All current system operations are local and file-based. No secrets exist.

## 20.2. Future Secrets Principles

When LOOPRA introduces external platform connectors, API integrations or
deployment infrastructure:

1. **Credentials never in `project.yaml`.** Project configuration files are
   source-committed and project-scoped. Secrets must live in a separate,
   access-controlled store.

2. **Never in Git.** Secrets must be excluded from version control via
   `.gitignore` (already present: `.env`), `.gitattributes`, or never written
   to disk at all.

3. **Never in CLI args.** Secrets passed as command-line arguments appear in
   shell history and process listings. Use env vars, files with restricted
   permissions, or a secret manager API.

4. **No secrets in logs.** Logging and debugging output must mask or exclude
   secret values.

5. **No secrets in export packages.** Export artifacts (`metadata.json`,
   `manifest.json`, `caption_*.txt`) must never contain credentials.

6. **No secrets in agent prompts.** Future agents receiving project context
   must not receive raw secret values.

## 20.3. Future Secret Types (Conceptual)

| Secret Type | Example | Storage |
|---|---|---|
| Platform API tokens | Telegram bot token, Instagram access token | Secret manager / encrypted env |
| SMTP credentials | Email sending password | Secret manager |
| Payment provider keys | Stripe/Paddle API keys | Secret manager |
| OAuth refresh tokens | Platform OAuth tokens | Encrypted DB or secret manager |
| Object storage keys | S3 access key + secret | Secret manager / encrypted env |
| Database credentials | PostgreSQL password | Secret manager / encrypted env |

## 20.4. Secret Separation Requirement

Before implementing any external platform integration, a dedicated Secrets
Management Specification must be approved. It must define:

- where secrets are stored;
- how services access secrets at runtime;
- how secrets are provisioned per workspace/project;
- how secret access is audited;
- how secrets are rotated;
- how secrets are excluded from logs, exports, agents and backups.

Current MVP does not require this infrastructure.

---

# 21. Feature Flags and Capability Flags — Future

## 21.1. Definition

Capability flags control which LOOPRA features are enabled for a project,
workspace or deployment. They allow progressive rollout and per-project
customization without code changes.

## 21.2. Potential Future Flags (Conceptual)

| Flag | Controls | Default |
|---|---|---|
| `content_text_social_post` | Enable text social post content type | `true` (MVP) |
| `content_carousel` | Enable carousel content type | `false` |
| `content_short_video` | Enable short video content type | `false` |
| `channel_telegram` | Enable Telegram channel | `false` |
| `channel_instagram` | Enable Instagram channel | `false` |
| `channel_linkedin` | Enable LinkedIn channel | `false` |
| `autopost_enabled` | Enable automatic publishing via connectors | `false` |
| `analytics_connector_enabled` | Enable automated metric collection | `false` |
| `learning_memory_enabled` | Enable Learning Memory accumulation | `false` |
| `asset_library_enabled` | Enable Asset Library | `false` |
| `agent_orchestrator_enabled` | Enable autonomous agent orchestration | `false` |

## 21.3. Current MVP State

The current MVP is capability-minimal:

- Only `text_social_post` content type is supported.
- Publication is manual only (`manual_publication_only = true`).
- Metrics are manual only (`source_type = "manual"`).
- No connectors, no autoposting, no learning memory.
- No feature flag system exists.

Capability flags are future/conceptual. They must not be implemented without a
dedicated Feature Flag Specification.

---

# 22. Deployment Configuration — Future

## 22.1. Definition

Deployment configuration describes the operational environment in which
LOOPRA runs — server endpoints, database connections, object storage, queue
services, worker settings and environment-specific parameters.

## 22.2. Potential Future Config Fields (Conceptual)

| Config Area | Fields |
|---|---|
| Environment identity | `environment_name` (`development`, `staging`, `production`) |
| Database | `database_url`, `database_pool_size`, `database_ssl_mode` |
| Object storage | `object_store_endpoint`, `object_store_bucket`, `object_store_region` |
| Queue / workers | `queue_broker_url`, `worker_concurrency`, `worker_timeout` |
| HTTP / API | `api_bind_host`, `api_bind_port`, `allowed_origins` (CORS) |
| Logging | `log_level`, `log_format`, `log_output` |
| Auth | `auth_issuer_url`, `auth_audience`, `session_ttl` |
| Email | `smtp_host`, `smtp_port`, `smtp_from_address` |

## 22.3. Current MVP State

None of these configuration areas are implemented. The current MVP runs as a
local Python process with:

- no API server;
- no database;
- no object storage (filesystem only);
- no queue;
- no authentication;
- no email;
- no deployment environment distinction.

## 22.4. Deployment Config Boundary

When deployment configuration is introduced:

1. Must not break local filesystem MVP — `projects_root` + filesystem repos
   must remain fully functional without deployment config.
2. Must be environment-specific — different config for development, staging,
   production.
3. Must not contain secrets — database URL embeds credentials; these must be
   resolved via secret manager.
4. Must not be committed with production values to version control.
5. Requires a dedicated Deployment Configuration Specification before
   implementation.

---

# 23. Configuration Migration Strategy

## 23.1. Identified Migration Needs

| Migration | From | To | Status |
|---|---|---|---|
| Env var naming | `CONTENT_PLANT_*` | `LOOPRA_*` | Planned, not started |
| Internal variable naming | `CONTENT_PLANT_ROOT` | `LOOPRA_ROOT` | Planned, not started |
| Code defaults constant | `CONTENT_PLANT_ROOT` in `loader.py` | Neutral name | Planned |
| Filesystem config → DB config | `project.yaml` | DB-backed project records | Future |

## 23.2. Migration Rules

1. **No silent breaking changes.** Old env vars must remain supported with
   deprecation warnings before removal.

2. **Migration must be versioned.** Each config format change increments a
   `config_schema_version` (future field).

3. **Backward compatibility required.** Current MVP config and env var names
   must remain readable through all migration stages.

4. **Dual support period.** New `LOOPRA_*` env vars are checked first; old
   `CONTENT_PLANT_*` env vars serve as fallback.

5. **Documentation update.** This specification, scripts and developer docs
   must be updated to reflect migration progress.

6. **Tests must not break.** Tests using old env var names must continue to
   pass during the dual-support period.

---

# 24. Configuration Versioning

## 24.1. Current State

`project.yaml` files currently have no `schema_version` field. The
`ProjectConfig` pydantic model has no version awareness. Configuration format
changes are not tracked or validated.

## 24.2. Future Versioning (Conceptual)

When configuration format evolves:

| Field | Purpose |
|---|---|
| `config_schema_version` | Integer or semver indicating the config format version |
| Migration path | Code that reads old versions and transforms to current |
| Validation by version | Different required fields, defaults or structure per version |
| Deprecation warnings | Console/log warnings when loading deprecated config versions |

Future rules:

- `config_schema_version` must be added to `project.yaml` before any breaking
  schema change.
- Old versions must remain loadable (with migration) or produce clear
  "unsupported version" errors.
- Version increments must be documented in this specification.

---

# 25. Configuration Security / Safety Rules

## 25.1. Hard Rules

| Rule | Enforcement |
|---|---|
| No secrets in Git | `.gitignore` excludes `.env`; secrets never in `project.yaml` |
| No credentials in `project.yaml` | `ProjectConfig` and `BrandConfig` models have no secret fields |
| No config edits without approval (future) | Agent guard rules (Section 19) |
| No cross-project config access | All services are project-scoped by `project_id` |
| No hidden autonomy changes | Autonomy mode changes require explicit config + approval |
| No connector enablement without explicit config | Connectors require channel config (future) |
| No production mode by accident | Future `LOOPRA_ENV` must default to safe mode |

## 25.2. Path Safety

`resolve_project_dir()` at `core/projects/loader.py:150-160` prevents path
traversal — `project_id` values like `../secrets` or `../../etc` are rejected
by `validate_project_id()` (must match `^[a-z0-9][a-z0-9_-]*$`). Even if a
valid ID somehow resolved outside `projects_root`, `Path.relative_to()` would
raise `InvalidProjectIdError`.

## 25.3. Current Safety Verification

- `.gitignore` line `storage/*` excludes all runtime artifacts.
- `.gitignore` line `.env` excludes dotenv files.
- `.gitignore` line `graphify-out/` excludes generated graph output.
- Tests verify no project-specific markers leak into platform code.
- Project ID validation rejects path separators and special characters.

---

# 26. Current MVP Configuration Flow

## 26.1. Full Configuration Load and Use (Verified from Code)

```text
1. Canonical project.yaml exists at projects/{project_id}/project.yaml
       │  Committed to Git. Defines project identity, brand, channels.

2. smoke_loop.py resolves project_id:
       │  CONTENT_PLANT_SMOKE_PROJECT_ID env var → "example" default
       │
3. smoke_loop.py resolves runtime projects_root:
       │  CONTENT_PLANT_SMOKE_PROJECTS_ROOT env var → storage/smoke_projects default
       │
4. smoke_loop.py copies project.yaml from source to runtime:
       │  projects/{project_id}/project.yaml → storage/smoke_projects/{project_id}/project.yaml
       │  (_ensure_runtime_project via shutil.copyfile)
       │
5. Smoke loop builds all services with runtime projects_root:
       │  FileSystemProjectRepository(projects_root=storage/smoke_projects)
       │  → ProjectService, BrandProfileService, IdeaService, etc.
       │
6. ProjectService.get_project(project_id):
       │  FileSystemProjectRepository.load_project_config(project_id)
       │      → load_project() → ProjectConfig.model_validate()
       │  _validate_required_fields(id, name, slug, language, status)
       │  _parse_project_status(config.status)
       │  Returns Project entity
       │
7. BrandProfileService.get_brand_profile(project_id):
       │  FileSystemProjectRepository.load_project_config(project_id)
       │  _validate_brand_fields(name, positioning, audience_summary)
       │  _resolve_brand_status(config)
       │  Constructs BrandProfile with tone_of_voice, content_rules, etc.
       │
8. ScenarioService.create_from_idea():
       │  Reads config.target_platforms for platform resolution
       │  Falls back to [TELEGRAM, THREADS, VK] if empty
       │  Uses brand profile for tone, content rules, QA checks
       │
9. PublishingService.prepare_export():
       │  Uses resolved platform to write caption_{platform}.txt
       │  Writes brand info into metadata.json
       │
10. AnalyticsService.create_metric_snapshot():
        │  Validates project exists via ProjectService
        │  Creates snapshot scoped to project_id

11. Post-loop tools resolve projects_root independently:
        │  find_metric_snapshots.py: CONTENT_PLANT_PROJECTS_ROOT → PROJECTS_ROOT default
        │  import_manual_metrics.py: CONTENT_PLANT_PROJECTS_ROOT → PROJECTS_ROOT default
        │  inspect_package.py, validate_package.py: no projects_root needed
        │      (operate directly on export directory path)
```

## 26.2. Runtime Config vs Source Config in Practice

```text
Source (committed):
    projects/example/project.yaml
    projects/nura/project.yaml

Runtime (gitignored, generated by smoke_loop.py):
    storage/smoke_projects/example/project.yaml     (copy)
    storage/smoke_projects/example/data/...         (entities)
    storage/smoke_projects/example/exports/...      (exports)

Test (temp dirs, cleaned up after test):
    /tmp/.../projects_root/example/project.yaml     (fixture)
    /tmp/.../projects_root/example/data/...         (entities)
```

---

# 27. Future Configuration Extension Path

## 27.1. Staged Evolution

All stages beyond Stage 1 are conceptual. Do not implement without approved
specifications.

| Stage | Description | Status |
|---|---|---|
| Stage 1 | Current `project.yaml` + `CONTENT_PLANT_*` env vars + factory `projects_root` param | **Current** |
| Stage 2 | Documented `LOOPRA_*` env var aliases with dual support | Future |
| Stage 3 | `config_schema_version` field in `project.yaml`; version-aware validation | Future |
| Stage 4 | Standardized CLI config flags (`--projects-root`, `--env`, `--log-level`) | Future |
| Stage 5 | Runtime config registry (structured object for all runtime settings) | Future |
| Stage 6 | Secret manager boundary — separate service for credential access | Future |
| Stage 7 | DB-backed project/workspace configuration — `project.yaml` → DB records | Future |
| Stage 8 | UI/API-managed settings — config editable through UI with audit | Future |
| Stage 9 | Agent-safe config change workflow — propose → approve → apply → audit | Future |

## 27.2. Stage Transition Rules

1. Each stage must be validated before the next begins.
2. Foundation MVP must remain operational through all stages.
3. Current service contracts must not break.
4. Tests must pass at every stage.
5. Documentation must be updated at each stage.

---

# 28. Configuration Readiness Criteria

The Configuration and Environment architecture is complete when:

- [x] Project config source defined (`projects/{project_id}/project.yaml`)
- [x] Runtime config source defined (env vars, `projects_root` param)
- [x] Environment variables documented (`CONTENT_PLANT_*`)
- [x] Configuration hierarchy defined (Section 4)
- [x] Required project fields documented (Section 5)
- [x] Brand config documented (Section 6)
- [x] Channel config documented (Section 7)
- [x] Project root resolution documented (Section 12)
- [x] Configuration validation documented (Section 13)
- [x] Configuration errors documented (Section 14)
- [x] Defaults and fallbacks documented (Section 15)
- [x] Service-config boundaries documented (Section 16)
- [x] Tool-config boundaries documented (Section 17)
- [x] Storage-config separation documented (Section 18)
- [x] Secrets boundary defined (Section 20)
- [x] Future LOOPRA env naming path defined (Section 10)
- [x] Future deployment config marked conceptual (Section 22)
- [x] Future feature flags marked conceptual (Section 21)
- [x] Future config migration strategy defined (Section 23)
- [x] Current MVP flow preserved (Section 26)
- [x] Test isolation documented (Section 11)

---

# 29. Related Documents

```text
AGENTS.md                                              — Development rules for agents
STATE.md                                               — Current project state and development phase
docs/00_foundation/PROJECT_SETTINGS_SPEC.md            — Project settings structure and fields
docs/00_foundation/DATA_MODEL.md                       — Foundation data model and entity chain
docs/02_architecture/SYSTEM_ARCHITECTURE.md            — System architecture layers
docs/02_architecture/PIPELINES_SPEC.md                 — Foundation MVP pipeline
docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md         — Runtime orchestration specification
docs/05_platform/SERVICE_CONTRACTS_SPEC.md             — Service contracts specification
docs/05_platform/TOOLING_AND_CLI_SPEC.md               — Tooling and CLI specification
docs/05_platform/STORAGE_AND_STATE_SPEC.md             — Storage and state specification
```

## 29.1. Relationship to PROJECT_SETTINGS_SPEC.md

`PROJECT_SETTINGS_SPEC.md` defines **what** project settings exist — the
fields, types and structure that LOOPRA requires to operate. It is the
specification of the project configuration schema.

This document (`CONFIGURATION_AND_ENVIRONMENT_SPEC.md`) defines **how** those
settings are loaded, validated, separated from other config sources, and
applied at runtime — the configuration model that connects `project.yaml` to
env vars, services, tools, tests and future deployment configuration.

```text
PROJECT_SETTINGS_SPEC.md        →  What configuration fields exist (schema)
CONFIGURATION_AND_ENVIRONMENT_SPEC.md  →  How configuration is loaded and used (mechanism)
```

## 29.2. Relationship to STORAGE_AND_STATE_SPEC.md

`STORAGE_AND_STATE_SPEC.md` defines **where** configuration is stored — the
filesystem layout, the separation between source `projects/` and runtime
`storage/smoke_projects/`, and the future DB/object-storage paths.

This document defines **how** configuration is read from those locations —
the loader, repositories, resolution logic and root path configuration.

```text
STORAGE_AND_STATE_SPEC.md       →  Where config files live on disk
CONFIGURATION_AND_ENVIRONMENT_SPEC.md  →  How config paths are resolved and files are loaded
```

## 29.3. Relationship to TOOLING_AND_CLI_SPEC.md

`TOOLING_AND_CLI_SPEC.md` defines **what** each tool does and **which** env
vars it uses.

This document defines **how** those env vars are named, resolved, defaulted and
migrated — the env var naming policy, resolution hierarchy and migration path.

```text
TOOLING_AND_CLI_SPEC.md         →  Tool contracts and their env var usage
CONFIGURATION_AND_ENVIRONMENT_SPEC.md  →  Env var naming policy, defaults, migration
```

---

# 30. Code References

```text
core/projects/loader.py                   — ProjectConfig, BrandConfig, PROJECTS_ROOT, validate_project_id,
                                             resolve_project_dir, load_project
core/services/projects.py                 — ProjectService, BrandProfileService, FileSystemProjectRepository,
                                             WorkspaceService, ProjectConfigValidationError
core/services/ideas.py                    — ScenarioService (target platform resolution, brand profile usage)
core/services/publishing.py               — PublishingService (platform usage, export writing)
core/services/analytics.py                — AnalyticsService (project validation)
core/services/loop.py                     — LoopOrchestrator, build_loop_orchestrator
core/services/_storage.py                 — FileSystemProjectModelRepository (entity ID validation)
scripts/smoke_loop.py                     — Env var resolution, runtime project copy, inline service wiring
scripts/find_metric_snapshots.py          — Env var resolution, project validation, snapshot reading
scripts/import_manual_metrics.py          — Env var resolution, JSON validation, AnalyticsService call
projects/example/project.yaml             — Example project canonical config
projects/nura/project.yaml                — NURA project canonical config
.gitignore                                — Secret and runtime artifact exclusion rules
tests/services/test_projects.py           — ProjectService and BrandProfileService validation tests
tests/services/test_smoke_loop.py         — Smoke loop end-to-end test with env var override
tests/services/test_find_metric_snapshots.py — Snapshot finding tests with env var override
tests/services/test_import_manual_metrics.py — Manual metrics import tests with env var override
```

---

# 31. Document Status

| Field | Value |
|---|---|
| Status | Active — LOOPRA Platform Layer |
| Version | v1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Platform Layer — Configuration and Environment |

---

# Final Statement

The Configuration and Environment Layer is the bridge between LOOPRA's
project identity, its runtime behaviour and its operational environment.

Project configuration (`project.yaml`) defines what a project IS — its
identity, brand, language, channels and status. It is the source of project
truth. It is loaded by deterministic services, validated for required fields,
and never modified by runtime.

Runtime configuration (env vars, `projects_root` parameter) defines HOW the
system runs — where data is stored, which project to operate, what mode is
active. It overrides paths and IDs, but never project identity.

Environment variables use the historical `CONTENT_PLANT_*` prefix. They
remain operational. Future migration to `LOOPRA_*` naming must preserve
backward compatibility and require no immediate code changes.

Secrets and credentials have no place in project configuration. They do not
exist in the current MVP. When they arrive, they must live in a dedicated
secret manager — never in `project.yaml`, never in Git, never in logs, never
in export packages, never in agent prompts.

The configuration hierarchy is clear: code defaults → project.yaml → env
vars → factory parameter. Each level overrides the ones below it within its
defined scope. Services load config through repositories and validate before
use. Tools read env vars and resolve paths before calling services.

Tests isolate their configuration through temporary directories and explicit
overrides — no test pollutes source config or runtime storage.

Future deployment configuration, feature flags, connector settings and SaaS
tenancy config are all conceptual. They must be introduced through dedicated
specifications without breaking the current filesystem MVP, without mixing
secrets into project config, and without silently changing the behaviour of
existing services and tools.

Configuration defines. It does not execute. It describes the project — it
does not decide strategy, mutate state, or publish content. It is the
foundation on which runtime, services and tools build the LOOPRA marketing
operating system.

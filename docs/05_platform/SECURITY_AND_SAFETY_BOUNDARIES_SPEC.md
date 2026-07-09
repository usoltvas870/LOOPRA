# SECURITY AND SAFETY BOUNDARIES SPEC

## Version

v1.0

## Status

Active — LOOPRA Platform Layer

## Purpose

This document defines the Security and Safety Boundaries Layer of the LOOPRA
Autonomous Marketing Operating System.

It answers the central question:

> What security, safety, scope, approval, secrets, project isolation and future
> agent boundaries must protect LOOPRA from incorrect runtime actions, tools,
> agents, connectors and operators, without adding premature auth/SaaS/users/roles
> implementation?

SECURITY_AND_SAFETY_BOUNDARIES_SPEC.md is the bridge between:

- project isolation rules;
- path safety protection;
- storage mutation boundaries;
- service/tool invocation boundaries;
- secrets and configuration boundaries;
- human approval gates;
- autonomy mode safety;
- future connector safety;
- future agent safety;
- future auditability;
- future access control.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document defines the security and safety boundaries that protect LOOPRA from
incorrect runtime actions. It establishes what guards exist today in the local
Foundation MVP and what guards the architecture requires before future
capabilities (agents, connectors, multi-tenancy) are activated.

This document is NOT a compliance policy, legal document, implementation backlog
or product strategy. It is an architectural boundary specification.

## 1.2. In Scope

- Current local MVP security boundaries (as implemented).
- Project isolation and scoping rules.
- Path safety and filesystem protection.
- Storage mutation safety (who may write what).
- Service boundary safety (preconditions, transitions, error handling).
- Tool invocation safety (CLI contracts, exit codes, read-only vs mutation).
- Configuration safety (project.yaml integrity, env var boundaries).
- Secrets boundary (what must never be stored where).
- .gitignore hygiene and runtime artifact separation.
- Publication safety (manual-only, no external calls).
- Analytics and metrics safety (manual import, supported keys, invalid rejection).
- Future agent safety boundaries (conceptual).
- Future autonomy mode safety (conceptual).
- Future connector safety (conceptual).
- Future auditability (conceptual).
- Future access control (conceptual).
- Destructive operation safety.
- Error and failure safety.
- Data safety and privacy boundary.
- Known current limitations.

## 1.3. Out of Scope

- Auth implementation (no auth exists; all descriptions are conceptual).
- RBAC implementation (no roles exist).
- SaaS tenancy implementation.
- Database security implementation (no database exists).
- API security implementation (no API exists).
- UI security implementation (no UI exists).
- Compliance certification.
- External connector implementation.
- Secret manager implementation.
- Production deployment hardening.
- CI/CD security scanning implementation.
- Legal or privacy policy drafting.

---

# 2. Role of Security and Safety in LOOPRA

## 2.1. What Security Protects

Security in LOOPRA protects:

| Boundary | What It Guards |
|---|---|
| Project boundaries | No cross-project data access or mutation. |
| Storage integrity | Only services may write entity state. |
| Config integrity | Runtime does not modify canonical configuration. |
| Secrets boundary | No credentials in Git, config, exports, logs, prompts. |
| Publication safety | No autoposting or external API calls in MVP. |
| Agent/tool execution safety | Agents decide; tools execute narrow contracts. |
| Future connector safety | Approval gates, credential scoping, preflight checks. |

## 2.2. What Safety Prevents

Safety in LOOPRA prevents:

- Accidental or unapproved publishing.
- Cross-project data leakage.
- Direct storage mutation outside services.
- Hidden background autonomy.
- Unapproved external actions.
- Destructive operations without confirmation.
- Path traversal attacks.
- Secret leakage into version control or exports.

## 2.3. Current MVP Security Model

In the current Foundation MVP, "security" does not mean SaaS authentication. It
means:

- **Project scope isolation** — every operation is bound to a single `project_id`.
- **No path traversal** — `project_id` is validated against a strict regex; `..` and `/` are rejected.
- **No secrets** — no API keys, no tokens, no credentials exist in the system.
- **No external calls** — no network requests, no platform APIs, no autoposting.
- **Manual publication only** — a human must copy content and publish externally.
- **Service-mediated mutations** — only services create, update and transition entities.
- **Read-only tools by default** — inspection tools do not modify storage.
- **No destructive operations** — no delete, purge, or archive in current CLI.

This is acceptable for a local Foundation MVP. It is NOT sufficient for
production SaaS. Future security layers are described in this document as
architectural direction only.

---

# 3. Security Principles

LOOPRA security follows these principles:

1. **Project-scoped by default.** Every entity, every storage path, every
   operation is bound to a specific `project_id`. Cross-project data access does
   not exist.

2. **No path traversal.** Project IDs and entity IDs are validated against strict
   regex patterns that reject `..`, `/`, and any characters unsafe for filesystem
   use.

3. **Services own mutations.** Only services may create, update or transition
   domain entities. Runtime, tools and future agents must route all mutations
   through services.

4. **Tools execute narrow contracts.** Tools perform single, well-defined
   operations. They receive explicit inputs and return structured outputs. They do
   not make strategic decisions.

5. **Agents must not bypass runtime/services.** Future agents issue execution
   requests through runtime entrypoints. They must not write entity JSON directly,
   skip service validation or call arbitrary shell commands.

6. **No secrets in Git, project.yaml, exports, logs or prompts.** If a secret is
   required in the future, it must live in a secret manager — never in plain text
   configuration or version control.

7. **Manual publication only in current MVP.** No content leaves the local system
   without explicit human action. Autoposting is a future capability governed by
   approval rules.

8. **No external calls in current MVP.** The system does not call any external
   API, connect to any platform or make any network request.

9. **Approval before irreversible or external actions.** Future external actions
   (connector publishing, connector metrics, destructive operations) require
   explicit approval gates.

10. **Future autonomy must be bounded, auditable and stoppable.** Any autonomous
    mode must include emergency stop, approval thresholds and a complete audit
    trail.

---

# 4. Current MVP Security Model

## 4.1. The Reality

The current LOOPRA Foundation MVP is a **local developer environment**:

- No authentication.
- No users.
- No roles.
- No API endpoints.
- No UI.
- No database.
- No external services.
- No secrets (no API keys, tokens or credentials).
- Filesystem-based project isolation.
- Manual operations (manual publication, manual metrics entry).

## 4.2. What This Means

All security boundaries in the current MVP are **local enforcement mechanisms** —
regex validation, path resolution, service preconditions, domain transition rules.
There is no network perimeter, no authentication layer, no access control.

This is **acceptable for the Foundation MVP**, which operates as a single-user
local tool. It is **not acceptable for production SaaS**.

## 4.3. The Honest Statement

| Capability | Current Status |
|---|---|
| Authentication | None. No users, no login, no sessions. |
| Authorization / RBAC | None. No roles, no permissions. |
| Access control | None. Local filesystem access is the only gate. |
| Audit log | None. No persisted execution context. |
| Secret manager | None. No secrets exist. |
| Runtime state persistence | None. In-memory only. Current execution is not saved across runs. |
| Locking / concurrency | None. Single-process, single-user. |
| Production hardening | None. No HTTPS, no WAF, no rate limiting. |
| Agent sandboxing | None. Future agents have no execution sandbox defined. |

This document honestly acknowledges these limitations while defining the
architectural boundaries that must be in place before future capabilities
activate.

---

# 5. Project Scope and Isolation

## 5.1. The Core Rule

Every operation in LOOPRA requires a valid `project_id`. No operation may span
projects. No entity may exist without a project scope.

## 5.2. Project Isolation Mechanisms

| Mechanism | Implementation | Code Reference |
|---|---|---|
| `project_id` validation | Regex `^[a-z0-9][a-z0-9_-]*$` rejects path separators and uppercase | `core/projects/loader.py:136-147` |
| Path traversal prevention | `resolve_project_dir()` calls `relative_to(root)` to detect escape | `core/projects/loader.py:150-158` |
| Entity ID validation | Same regex pattern via `ENTITY_ID_PATTERN` | `core/services/_storage.py:14` |
| Project-scoped storage | All data under `{project_dir}/data/{collection}/` | `core/services/_storage.py:58-60` |
| Project-scoped exports | All exports under `{project_dir}/exports/{export_package_id}/` | `core/services/publishing.py` `prepare_export` |
| Cross-project prevention | Repositories never access other project directories | All repository classes |

## 5.3. Project-Specific Configuration Isolation

Project-specific configuration lives in:

```
projects/{project_id}/project.yaml
docs/07_projects/{project_slug}/
```

Platform core (`core/`) must contain **no project-specific logic**:

- No `if project_id == "nura"` branches.
- No hardcoded brand names, channel lists or content strategies.
- No project-specific prompts in core.

Tests verify this via `test_task_2_files_do_not_contain_project_specific_branching_markers`
(`tests/services/test_projects.py:113`).

## 5.4. Current vs Future

| Boundary | Current Mechanism | Future Mechanism |
|---|---|---|
| Project identity | Regex-validated `project_id` in filesystem path | Database tenant ID + request-scoped project context |
| Cross-project access | Filesystem directory separation | Database row-level security, API scope validation |
| Project config | `projects/{project_id}/project.yaml` | Database-backed config with versioning |
| Brand isolation | `BrandProfile` derived per-project from config | Same, with access control |
| Entity scoping | `project_id` field on every entity | Same, with ownership and permission checks |

---

# 6. Path Safety and Project ID Validation

## 6.1. Path Traversal Protection

The current codebase implements explicit path traversal protection:

### 6.1.1. Project ID Regex (`core/projects/loader.py:11-13`)

```python
PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
```

This regex rejects:
- `..` (path traversal dots become invalid characters)
- `/` or `\` (path separators become invalid characters)
- Uppercase letters (enforces consistent lowercase)
- Spaces and special characters
- Empty strings

### 6.1.2. Project ID Validation (`core/projects/loader.py:136-147`)

```python
def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str):
        raise InvalidProjectIdError("project_id must be a string")
    normalized = project_id.strip()
    if not normalized:
        raise InvalidProjectIdError("project_id must not be empty")
    if not PROJECT_ID_PATTERN.fullmatch(normalized):
        raise InvalidProjectIdError(
            "project_id must match ^[a-z0-9][a-z0-9_-]*$ and must not contain path separators"
        )
    return normalized
```

### 6.1.3. Resolved Path Containment Check (`core/projects/loader.py:150-158`)

```python
def resolve_project_dir(project_id: str, projects_root: Path | None = None) -> Path:
    root = (projects_root or PROJECTS_ROOT).resolve()
    safe_project_id = validate_project_id(project_id)
    project_dir = (root / safe_project_id).resolve()

    try:
        project_dir.relative_to(root)
    except ValueError as exc:
        raise InvalidProjectIdError(
            f"project_id '{safe_project_id}' resolves outside projects root"
        ) from exc

    return project_dir
```

The `relative_to(root)` check ensures that even after path resolution (symlinks,
`..` injected elsewhere), the resulting path stays within the projects root. The
double layer of protection — regex validation AND resolved-path containment —
provides defense-in-depth against path traversal.

### 6.1.4. Entity ID Validation (`core/services/_storage.py:14,62-74`)

```python
ENTITY_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

@staticmethod
def _validate_entity_id(entity_id: str, entity_name: str) -> str:
    if not isinstance(entity_id, str):
        raise ValueError(f"{entity_name} must be a string")
    normalized = entity_id.strip()
    if not normalized:
        raise ValueError(f"{entity_name} must not be empty")
    if not ENTITY_ID_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{entity_name} must match ^[a-z0-9][a-z0-9_-]*$ and must not contain path separators"
        )
    return normalized
```

All entity IDs (idea_id, scenario_id, content_item_id, export_package_id,
publication_id, metric_snapshot_id) are validated against this same pattern before
any filesystem path is constructed from them.

## 6.2. Export Package Path Safety

The `inspect_package.py` and `validate_package.py` scripts additionally enforce:

- Manifest file entries must not be absolute paths (`test_rejects_absolute_paths_in_manifest_files`).
- Manifest file entries must not traverse upward.
- All referenced files must exist inside the export package directory.

## 6.3. Test Coverage

Path safety is verified by tests:

| Test | What It Verifies | Location |
|---|---|---|
| `test_invalid_project_id_is_rejected` | `../example`, `example/child`, empty, uppercase, spaces rejected | `tests/services/test_projects.py:58` |
| `test_rejects_absolute_paths_in_manifest_files` (inspect) | Absolute paths in manifest rejected | `tests/services/test_inspect_package.py:128` |
| `test_rejects_absolute_paths_in_manifest_files` (validate) | Absolute paths in manifest rejected | `tests/services/test_validate_package.py:200` |

---

# 7. Storage Mutation Safety

## 7.1. The Principle

> Services are the only layer that mutates domain entities. Runtime orchestrates
> services. Tools call services (or are read-only). Future agents must call
> runtime/service entrypoints.

## 7.2. Current Mutation Paths

| Operation | Who Mutates | How |
|---|---|---|
| Create entity | Service → Repository → JSON file | Service calls `repository.save_*()` after validation |
| Transition entity status | Service → `entity.transition_to()` → Repository | Service validates transition, calls domain method, persists |
| Record metrics | `AnalyticsService.record_metrics()` via `import_manual_metrics.py` | Service validates keys/values, updates snapshot, persists |
| Record publication | `PublishingService.publish_content()` | Service validates URL, transitions status, persists |

## 7.3. Read-Only Tool Operations

| Tool | Mutates Storage? | How It Works |
|---|---|---|
| `inspect_package.py` | **No** | Reads `manifest.json` and displays content. No service calls. |
| `validate_package.py` | **No** | Reads `manifest.json`, checks files exist. No service calls. |
| `find_metric_snapshots.py` | **No** | Reads `{project_dir}/data/metric_snapshots/*.json` via `MetricSnapshot.model_validate()`. Lists and displays. No writes. |

## 7.4. Rules Enforced

1. **Tools must not directly write entity JSON unless service-backed.**
   `import_manual_metrics.py` mutates via `AnalyticsService.record_metrics()` —
   not by writing JSON files directly.

2. **Read-only tools may inspect artifacts.** `inspect_package.py`,
   `validate_package.py`, `find_metric_snapshots.py` are read-only.

3. **No tool except `import_manual_metrics.py` modifies domain state.**
   And that tool does so through `AnalyticsService`.

4. **Future agents must not write storage directly.** All mutations must pass
   through services.

5. **Runtime orchestrates but does not mutate directly.** `LoopOrchestrator` calls
   services for every lifecycle step. It never calls repository methods directly.

## 7.5. Export Package Mutation Safety

Export packages, once written by `PublishingService.prepare_export()`, are treated
as immutable artifacts by tools. `smoke_loop.py` creates new entities on each run;
it does not modify existing export packages.

---

# 8. Service Boundary Safety

## 8.1. What Services Enforce

Every service enforces its contract through:

| Enforcement | Mechanism |
|---|---|
| Precondition validation | Checks entity status, required fields, input types before any mutation. |
| Domain transition enforcement | Calls `entity.transition_to()` which validates against `core/domain/transitions.py`. |
| Entity existence verification | Checks that referenced entities (project, idea, scenario, etc.) exist. |
| Cross-entity consistency | Verifies that linked entities match (e.g., `content_item_id` matches `export_package.content_item_id`). |
| Status requirements | Checks that prerequisite entities are in the required status (e.g., Idea must be APPROVED before Scenario creation). |
| Publication status requirements | Publication must be PUBLISHED before MetricSnapshot can be created. |
| Metric snapshot status requirements | Metrics can only be recorded into a DRAFT snapshot. |

## 8.2. Invalid Transitions Raise Errors

Every invalid operation raises a typed validation error:

| Error Class | When Raised |
|---|---|
| `ProjectConfigValidationError` | Missing required config fields; invalid status. |
| `IdeaBankValidationError` | Invalid funnel_stage, source_type, priority. |
| `ScenarioStudioValidationError` | Idea not APPROVED/SCRIPTED; unsupported content format. |
| `ProductionLifecycleValidationError` | Scenario not APPROVED before ContentItem creation. |
| `PublishingValidationError` | ContentItem not APPROVED; ExportPackage not DRAFT/READY; empty published_url. |
| `AnalyticsValidationError` | Publication not PUBLISHED; invalid metric keys/values; snapshot not DRAFT. |
| `InvalidStatusTransitionError` | Any illegal entity status transition. |

## 8.3. Runtime and Tools Must Not Bypass Services

- `LoopOrchestrator` calls services exclusively. It never calls repositories
  directly for mutations.
- `import_manual_metrics.py` calls `AnalyticsService.record_metrics()`.
- `inspect_package.py` and `validate_package.py` do not modify any entity state.
- `find_metric_snapshots.py` reads files directly but does not modify them.
- `smoke_loop.py` creates entities through `LoopOrchestrator.run_minimal_loop()`.

---

# 9. Tool Invocation Safety

## 9.1. Current Tool Safety Characteristics

| Characteristic | How It Is Enforced |
|---|---|
| Explicit CLI arguments | Every tool requires explicit, validated parameters. No hidden defaults that silently change behaviour. |
| No hidden background execution | Tools run only when explicitly invoked via terminal. No cron, no daemon, no scheduler. |
| No external network calls | No tool makes any HTTP request, socket connection or external API call. |
| No destructive operations | No tool deletes entities, removes artifacts or purges data. |
| No secrets in tool I/O | No tool reads, writes or accepts secrets. |
| No autoposting | No tool publishes content to external platforms. |
| Exit codes | Tools exit 0 on success, non-zero on error. |
| Error output | Error messages go to stderr. Success output goes to stdout. |

## 9.2. Current Tool Categorization by Safety Level

| Tool | Writes to Storage? | Calls External? | Calls Service? | Risk Level |
|---|---|---|---|---|
| `smoke_loop.py` | Yes (via services) | No | Yes (all services) | **Medium** — creates entities |
| `import_manual_metrics.py` | Yes (via AnalyticsService) | No | Yes | **Low** — imports metrics |
| `inspect_package.py` | No | No | No | **None** — read-only |
| `validate_package.py` | No | No | No | **None** — read-only |
| `find_metric_snapshots.py` | No | No | No | **None** — read-only |

## 9.3. Future Tool Safety Rules (Conceptual)

Future tool safety framework must include:

| Rule | Description |
|---|---|
| Tool registry | Allowed tools are registered; unknown commands rejected. |
| Approved commands only | Agents may only invoke tool names from the registry. |
| Audit trail | Every tool invocation logs: who called, with what inputs, what result. |
| No arbitrary shell | Agents must not invoke arbitrary shell commands. Only registered tools. |
| Input validation | Tool inputs validated before execution. No raw user input passed to shell. |

---

# 10. Configuration Safety

## 10.1. Current Configuration Model

Configuration layers (see `CONFIGURATION_AND_ENVIRONMENT_SPEC.md`):

```
Source config (canonical)     →  projects/{project_id}/project.yaml
Runtime config (derived)      →  ProjectConfig model, validated on load
Environment variables         →  Override runtime paths only (LOOPRA_SMOKE_PROJECTS_ROOT primary,
                                 LOOPRA_PROJECTS_ROOT primary, LOOPRA_SMOKE_PROJECT_ID primary;
                                 CONTENT_PLANT_* legacy fallback)
```

## 10.2. Configuration Safety Rules

1. **Runtime does not modify canonical config.** `project.yaml` is source; runtime
   reads from it but never writes to it.
2. **Env vars override runtime paths only.** They do not override project identity,
   brand strategy, channels, goals or content rules.
3. **No secrets in project.yaml.** Project configuration is plaintext and may be
   committed. It must never contain API keys, tokens or credentials.
4. **Future agents must not silently edit config.** Any config change must require
   approval and leave an audit trail.
5. **Config validation rejects unknown fields implicitly** through Pydantic schema
   enforcement. Only defined fields are accepted.

## 10.3. Config Mutation Boundary

| Who | May Modify project.yaml? | How |
|---|---|---|
| Human operator | Yes (manually, in editor) | Direct YAML editing |
| Runtime / LoopOrchestrator | No | Reads only |
| Services | No | Reads only via ProjectService |
| CLI tools | No | None modify config |
| Future agents | No | Must require approval + audit trail |
| `smoke_loop.py` | Copies to runtime dir, does not modify source | `_ensure_runtime_project()` copies |

---

# 11. Secrets Boundary

## 11.1. Current State

The current LOOPRA Foundation MVP **has no secrets**:

- No API keys.
- No OAuth tokens.
- No platform credentials.
- No database passwords.
- No SMTP credentials.
- No payment provider keys.

This is intentional — the system does not connect to any external service that
requires authentication.

## 11.2. Secrets Rules — Current

| Rule | Enforcement |
|---|---|
| No secrets in Git | `.env` in `.gitignore`. No other secrets exist to exclude. |
| No secrets in `project.yaml` | Project config contains only public brand/identity data. |
| No secrets in export packages | Export output is public content (title, body, captions). |
| No secrets in logs | No logging of sensitive data (no sensitive data exists). |
| No secrets in agent prompts | No agent, no prompts, no secrets. |

## 11.3. `.env` and `.gitignore`

Current `.gitignore` (line 1):

```
.env
```

If a `.env` file is created for local environment variables, it is excluded from
version control. This is the only active secret boundary file.

## 11.4. Future Secrets Rules

When LOOPRA adds connectors, databases or external integrations, the following
rules apply:

| Rule | Description |
|---|---|
| Never in Git | Secrets must never be committed. Secret files must be `.gitignore`-d. |
| Never in project.yaml | Project configuration stays secret-free. |
| Never in export packages | Exports contain only public content. |
| Never in logs | Logging must filter or mask secret values. |
| Never in agent prompts | Agent context must not include raw credentials. |
| Never in CLI args | CLI arguments are visible in process lists; secrets must not be passed there. |

## 11.5. Future Secret Types

When connectors and external integrations are added, the system will require:

| Secret Type | Purpose |
|---|---|
| Platform API tokens | Publishing to Telegram, Instagram, LinkedIn, etc. |
| OAuth refresh tokens | Long-lived platform authentication. |
| SMTP credentials | Email distribution. |
| Payment provider keys | Revenue tracking integrations. |
| Database credentials | PostgreSQL connection strings. |
| Object storage keys | S3-compatible storage access. |
| Internal service tokens | Inter-service authentication (future API layer). |

## 11.6. Secret Manager Requirement

> A secret manager is required before the first connector credential is stored.

This is an architectural rule, not a current implementation. Until a secret
manager (e.g., env-var-based vault, HashiCorp Vault, cloud secret store) is
integrated, no connector, no external API, and no database requiring credentials
may be activated.

---

# 12. Runtime Artifact and Git Hygiene Safety

## 12.1. The Separation

```
Source (committed)               Runtime (gitignored)
─────────────────────────        ──────────────────────────
projects/{project_id}/           storage/smoke_projects/{project_id}/
project.yaml                     data/ (entity JSON files)
                                 exports/ (export package output)
                                 graphify-out/
```

## 12.2. `.gitignore` Rules

Current `.gitignore` excludes:
- `.env` (secrets boundary)
- `storage/*` (all runtime artifacts)
- `graphify-out/` (generated graphify output)
- `projects/nura/*` except `project.yaml` (project-specific data not in core)
- `__pycache__/`, `*.pyc` (Python bytecode)
- `output/`, `renders/`, `jobs/*/input/`, `jobs/*/work/`, `jobs/*/output/` (generated artifacts)

## 12.3. Hygiene Rules

1. **Generated runtime artifacts must not be committed.** If an artifact was
   produced by `smoke_loop.py` or any script, it must not enter version control.
2. **Source docs and config are committed intentionally.** Architecture docs,
   project configs, code — committed.
3. **Runtime outputs excluded by blanket rules.** `storage/` and `graphify-out/`
   are fully gitignored.
4. **No modification of `.gitignore` needed for this document.** Current rules
   are sufficient for the Foundation MVP security boundary.

---

# 13. Publication Safety

## 13.1. Current State

In the Foundation MVP:

- Publication is **manual only**. A human copies content from the export package
  and publishes on the external platform.
- `PublishingService.publish_content()` records the publication outcome — it does
  **not** publish to an external platform.
- No platform API calls exist.
- No autoposting exists.
- `smoke_loop.py` uses a **placeholder URL** (`https://example.invalid/...`) for
  the simulated publication.
- `manual_publication_checklist.txt` guides the human operator.

## 13.2. Publication Safety Rules — Current

| Rule | How It Is Enforced |
|---|---|
| No external API calls | No code makes HTTP requests. The `requests` library is not imported by any service or tool. |
| No autoposting | `publication_method = "manual"` in all Publication records. |
| Manual publication checklist | Export package includes step-by-step instructions for human publication. |
| Publication record is descriptive, not active | `publish_content()` records what happened — it does not trigger external action. |
| Placeholder URL in smoke loop | Prevents accidental belief that the system auto-published. |

## 13.3. Future Publication Safety (Conceptual)

When connector-based publishing is added, the following gates are required:

| Gate | Description |
|---|---|
| Approval before connector publishing | No connector dispatch without explicit human approval (or autopilot permission rules). |
| Connector dispatch only through Distribution | PublishingService routes through the Distribution layer, not ad-hoc connector calls. |
| Publication attempt audit | Every connector dispatch attempt is recorded. |
| Emergency stop | Human can halt any pending or in-progress connector publication. |
| Preflight validation | Package is validated as publication-ready before connector is called. |
| Platform response recording | Connector response (post ID, URL, error) is stored in the Publication record. |
| No silent connector enablement | Connectors are explicitly enabled per-channel in Project Settings. |

---

# 14. Analytics and Metrics Safety

## 14.1. Current State

In the Foundation MVP:

- Metrics are collected **manually**. A human observes platform analytics and
  enters values.
- `import_manual_metrics.py` imports metrics via `AnalyticsService.record_metrics()`.
- `find_metric_snapshots.py` lists snapshots (read-only).
- `SUPPORTED_MANUAL_METRIC_KEYS` defines the allowed metric keys:
  `views`, `likes`, `comments`, `shares`, `saves`, `clicks`, `published_url`.
- Invalid keys are rejected.
- Invalid values (negative integers, non-integer numeric values) are rejected.
- `published_url` updates the related `Publication` — it is not stored as a raw
  metric field.
- Metrics cannot be recorded twice (snapshot transitions from DRAFT → RECORDED;
  only DRAFT snapshots can accept metrics).
- No external analytics API is called.
- No automated metric refresh exists.

## 14.2. Analytics Safety Rules — Current

| Rule | Enforcement |
|---|---|
| Supported keys only | `SUPPORTED_MANUAL_METRIC_KEYS` is a closed set. Unknown keys → `AnalyticsValidationError`. |
| Non-negative integers for numeric metrics | `record_metrics()` validates `>= 0` for all numeric fields. |
| DRAFT-only recording | Metrics can only be imported into DRAFT snapshots. Recorded snapshots cannot be modified. |
| `published_url` separated from metrics | `published_url` updates the Publication, not inserted as a raw metric field. |
| Empty metrics rejected | `record_metrics()` raises error if `metrics` dict is empty. |
| No external collection | Current system does not call any external analytics API. |

## 14.3. Future Analytics Safety (Conceptual)

| Rule | Description |
|---|---|
| Connector metric collection requires credentials | No connector pulls data without valid, scoped credentials. |
| Raw platform responses stored safely | Platform API responses (which may include tokens) must not be logged raw. |
| No secrets in metrics payload | Connector-collected metrics must not accidentally capture credentials. |
| Data provenance required | Every metric value must carry its source (manual, connector, import) and collection timestamp. |
| Metric stale detection | Snapshots older than a configured freshness window are flagged. |

---

# 15. Agent Safety Boundaries — Future

## 15.1. The Agent Contract

Future agents (Orchestrator Agent, Intelligence Modules) issue execution requests
to the runtime layer. The runtime layer executes through services. This contract
defines what agents may and may not do.

## 15.2. Agents Must NOT

| Forbidden Action | Why |
|---|---|
| Write files directly | All mutations must go through services. |
| Bypass services | Agents must not create, update or transition domain entities directly. |
| Call arbitrary shell commands | Only registered tools may be invoked. No `os.system()`, no `subprocess` from agent context. |
| Publish without approval | No connector dispatch without human approval (or explicit autopilot permission rules). |
| Access cross-project data | Agent operates within a single project scope. No project data leakage. |
| Read secrets | Agent must not access credential values. Secret manager access is denied to agents. |
| Change config silently | Any Brand System, Project Settings or channel config change requires approval + audit. |
| Run continuously without schedule/control | No 24/7 hidden background thinking. Agent execution is triggered and bounded. |
| Delete artifacts without approval | No destructive operations without explicit confirmation. |

## 15.3. Agents May

| Allowed Action | How |
|---|---|
| Request runtime commands | Issue structured requests through runtime entrypoints. |
| Request approved tool invocations | Call registered tools by name with validated inputs. |
| Propose changes | Suggest config updates, content directions, strategy adjustments — for human review. |
| Summarize state | Read and summarize entity states, metrics, publication records. |
| Ask for human approval | Escalate low-confidence or boundary-proximity decisions. |

## 15.4. Agent Safety Enforcement

All future agent actions must be:

1. **Scoped to a project** — agent operates on one `project_id` at a time.
2. **Routed through runtime** — agent calls runtime entrypoints, not services
   directly.
3. **Validated by runtime** — runtime checks preconditions before executing any
   agent-requested action.
4. **Recorded for audit** — every agent decision and every runtime action
   triggered by an agent is audit-logged.

---

# 16. Autonomy Mode Safety

## 16.1. Autonomy Modes

LOOPRA defines three autonomy modes (defined in `AGENT_SYSTEM_SPEC.md`, Section 8
and `PROJECT_SETTINGS_SPEC.md`, Section 7.3):

| Mode | Description | Current Status |
|---|---|---|
| **Copilot** | LOOPRA suggests, human decides. Every action requires human approval. | **Current MVP default.** |
| **Assisted** | Routine steps auto-execute; strategic decisions require confirmation. | **Future.** |
| **Autopilot** | LOOPRA operates autonomously within defined rules; emergency stop retained. | **Future.** |

## 16.2. Current MVP Autonomy Constraints

- The current MVP operates **exclusively in Copilot mode**.
- There is no autonomous background agent.
- There is no continuous 24/7 cycle.
- Runtime executes only when explicitly triggered via CLI.
- All publication is manual.
- All metrics entry is manual.

## 16.3. Future Autonomy Safety Rules

When Assisted and Autopilot modes are implemented, these rules apply:

| Rule | Description |
|---|---|
| Explicit opt-in | Autonomy mode is selected per-project in Project Settings or Brand System. Default is Copilot. |
| Emergency stop | Available in all modes. Immediately pauses all active cycles. |
| Mode reduction | Human can reduce autonomy from Autopilot → Assisted → Copilot at any time. |
| Mode escalation prohibited | Agents must NOT increase their own autonomy level. Only human can escalate. |
| External action approval | In Assisted mode, external actions (connector publishing, connector metrics) require approval. |
| Autopilot external action rules | If autopilot is enabled, explicit per-channel per-action approval rules must be configured. |
| No hidden 24/7 execution | Autonomous cycles must have defined schedules, checkpoints and stop conditions. |
| Cycle audit | Every autonomously triggered cycle must be logged with: who enabled it, what was executed, what was decided. |

---

# 17. Approval Gates

## 17.1. Definition

Approval gates are points in the execution flow where a human operator must
confirm before the system proceeds. They are the primary safety mechanism against
unintended or dangerous actions.

## 17.2. Current MVP Gates

| Gate | Type | How It Works |
|---|---|---|
| Idea creation | Manual input | Human creates Idea via script or programmatic call. |
| Manual publication | Manual action | Human copies caption, pastes into platform, publishes outside LOOPRA. |
| Publication URL recording | Manual input | Human records the published URL and timestamp. |
| Metric entry | Manual input | Human collects metrics from platform, imports via `import_manual_metrics.py`. |

These are not mid-flow pause-and-ask gates — they are steps where the human acts
outside the system and feeds results back in.

## 17.3. Future Approval Gates (Conceptual)

| Gate | Purpose | Current / Future | Blocking Condition |
|---|---|---|---|
| Content approval | Review content draft before production | Future | Content contains forbidden topics, claims or tone violations. |
| Asset approval | Review selected assets before assembly | Future | Asset licensing, quality or brand fit issues. |
| Publication approval | Review final export package before publishing | Future | Copilot/Assisted mode: every publication requires approval. |
| Connector publishing approval | Confirm dispatch to external platform | Future | No connector dispatch without approval (except autopilot with rules). |
| Config change approval | Confirm Brand System, Project Settings or channel changes | Future | Any config change that affects content strategy or publishing. |
| Autonomy mode change approval | Confirm increase or decrease of autonomy | Future | Mode escalation requires operator confirmation. |
| Destructive action approval | Confirm delete, archive, purge, revoke | Future | Any irreversible operation. |

## 17.4. Approval Record Requirements

Every future approval must be recorded with:

- `approval_id` — unique identifier.
- `publication_plan_id` or `action_id` — what was approved.
- `approver` — human operator identifier.
- `decision` — approved, rejected, changes_requested.
- `reason` — for rejections or change requests.
- `approved_at` — timestamp.
- `autonomy_mode_at_approval` — snapshot of autonomy mode.

---

# 18. Connector Safety — Future

## 18.1. Connector Risk Profile

When LOOPRA adds platform connectors (for publishing, analytics collection), the
risk surface expands:

| Risk | Impact |
|---|---|
| External publishing | Content posted to wrong account or at wrong time. |
| External analytics collection | Platform API credential exposure. |
| Platform authentication | Token leakage, expired credentials, unauthorized access. |
| Rate limits | API throttling, cost overruns, blocked accounts. |
| Token leakage | Credentials logged, exported or committed. |
| Wrong account/channel | Content published to the wrong brand account. |
| Irreversible posts | Content cannot be retracted once published. |

## 18.2. Required Connector Guardrails

| Guardrail | Description |
|---|---|
| Configured connector only | Connector must be explicitly enabled per-channel in Project Settings. |
| Scoped credentials | Connector tokens have minimum necessary permissions (publish-only, read-analytics-only). |
| Approval before dispatch | No connector publishes without explicit approval (except autopilot with defined rules). |
| Dry-run / preflight | Connector validates credentials, format and permissions before attempting publication. |
| Rate limiting | Client-side rate limiting prevents exceeding platform API quotas. |
| Retry policy | Defined retry with exponential backoff for transient failures. |
| Platform response recording | Full platform response stored in Publication record (without raw credentials). |
| Failure handling | Connector failures are recorded as `PublicationAttempt` with error details. |
| No connector without secrets spec | A connector implementation must reference the relevant secrets specification. |
| Connector audit trail | Every connector call logged: what, when, by whom, result. |

---

# 19. Data Safety and Privacy Boundary

## 19.1. Current State

The current Foundation MVP:

- Stores only local project data on the local filesystem.
- Has no user accounts, no personal data, no PII.
- Has no external data transfer — no API calls, no database synchronization.
- Project content may contain brand-specific information, but it is stored locally.

## 19.2. Current Data Classification

| Data Category | Where Stored | Risk |
|---|---|---|
| Project config (brand identity, channels, goals) | `projects/{project_id}/project.yaml` | **Low** — brand identity data. |
| Domain entity records (Idea, Scenario, etc.) | `storage/smoke_projects/{project_id}/data/` | **Low** — local content metadata. |
| Export package outputs (titles, captions, body) | `storage/smoke_projects/{project_id}/exports/` | **Low** — generated content. |
| Metric snapshots | `storage/smoke_projects/{project_id}/data/metric_snapshots/` | **Low** — numeric metrics. |
| Logs | stdout/stderr, terminal output | **Low** — transient. |

## 19.3. Future Privacy Boundaries (Conceptual)

When SaaS features are added:

| Boundary | Description |
|---|---|
| Workspace data isolation | Data isolated per workspace. Cross-workspace access prevented. |
| User data access rules | Users access only their workspace data. |
| Retention policies | Configurable data retention periods per project. |
| Export/delete workflows | Users can export or request deletion of their data. |
| Privacy compliance | GDPR, CCPA compliance handled at SaaS layer (not core architecture). |

This document defines the architectural boundary. It is not a legal policy.

---

# 20. Auditability

## 20.1. Current State

The current Foundation MVP has **limited auditability**:

- Entity JSON records contain `created_at` and `updated_at` timestamps.
- Terminal output from CLI scripts provides a human-readable execution log.
- No `RuntimeExecutionContext` is persisted (conceptual only).
- No audit log exists.

## 20.2. What Is Auditable Today

| Data | Where | Limitation |
|---|---|---|
| Entity creation timestamps | JSON files: `created_at` field | Only shows when entity was created, not who or why. |
| Entity status changes | JSON files: `updated_at` + current status | No transition history. Only current state visible. |
| Export package contents | `exports/{id}/` directory | Shows what was generated, not who generated it. |
| Publication records | JSON files: `published_at`, `published_url` | Shows publication outcome, not approval chain. |
| Terminal output | stdout from script execution | Transient. Not persisted. |

## 20.3. Future Audit Records (Conceptual)

Future audit trail must capture:

| Audit Record Type | Content |
|---|---|
| Runtime executions | `execution_id`, `project_id`, `requested_by`, `status`, `started_at`, `completed_at`. |
| Service mutations | `service_name`, `operation`, `entity_id`, `from_status`, `to_status`, `timestamp`. |
| Tool invocations | `tool_name`, `inputs`, `outputs`, `exit_code`, `called_by`, `timestamp`. |
| Agent decisions | `agent_decision_id`, `context`, `decision`, `reasoning`, `confidence`, `timestamp`. |
| Approvals | `approval_id`, `action`, `approver`, `decision`, `reason`, `timestamp`. |
| Connector calls | `connector_id`, `channel_id`, `action`, `result`, `response`, `timestamp`. |
| Config changes | `config_path`, `field`, `old_value`, `new_value`, `changed_by`, `timestamp`. |
| Secret access | `secret_type`, `accessed_by`, `purpose`, `timestamp` (access log, not value). |

Audit is a future capability. Current MVP does not implement audit persistence.

---

# 21. Error and Failure Safety

## 21.1. Current Error Handling

The current MVP handles errors through:

1. **Validation errors stop execution.** Invalid inputs, illegal transitions or
   missing prerequisites raise exceptions. Execution does not proceed with
   invalid state.
2. **CLI tools exit non-zero.** Scripts report errors via stderr and non-zero
   exit codes (`return 1`).
3. **Failed publication can be recorded.** `PublishingService.fail_publication()`
   marks a Publication as FAILED with an error reason.
4. **No retry/resume in MVP.** Failed smoke loop runs require full restart. No
   mid-flow resume.

## 21.2. Safety Properties of Current Error Model

| Property | How It Works |
|---|---|
| Fail-fast | Invalid inputs or states immediately raise. No partial execution. |
| No silent failures | Errors produce human-readable messages. |
| No data corruption on failure | Entity creation happens within a single service call. Partial entity writes do not occur. |
| Idempotency not required | Each `smoke_loop` run creates new entities with new IDs. Failed runs produce no side effects beyond file creation. |

## 21.3. Future Error Safety (Conceptual)

| Capability | Description |
|---|---|
| Structured runtime errors | `RuntimeError` records with error_code, stage, severity, recommended_action. |
| Retry policies | Configurable retry per operation type (publish, collect metrics). |
| Resume from stage | Runtime inspects entity states and resumes from the first incomplete step. |
| Safe failure states | All entities in defined terminal states on failure. No partial states. |
| No partial external side effects | If a connector publish fails, either the platform received it or it did not — no ambiguous state without record. |

---

# 22. Destructive Operation Safety

## 22.1. Current State

The current MVP does **not** support destructive operations:

- No CLI tool deletes entities, artifacts or project data.
- No archive/delete/purge functionality exists.
- `smoke_loop.py` creates new artifacts; it does not clean up old ones.
- `validate_package.py` reports issues but does not fix or delete anything.
- `import_manual_metrics.py` adds metrics but does not delete or overwrite
  existing snapshots (transitions DRAFT → RECORDED, no further writes).

## 22.2. Future Destructive Operations

When the system adds management capabilities, these operations require safety
rules:

| Operation | Required Safety Rules |
|---|---|
| Delete project | Explicit confirmation. Data export before deletion. Cool-down period. |
| Archive content | Soft archive preferred. Retain for history. Clear archive vs delete distinction. |
| Cleanup storage | Confirmation. Only cleans runtime artifacts, not source config. |
| Purge assets | Confirmation. Check for references (does any content use this asset?). |
| Revoke connector | Confirmation. Revoke tokens. Record revocation. |
| Delete publication draft | Confirmation. Record deletion for audit. |

## 22.3. Destructive Operation Rules

| Rule | Description |
|---|---|
| Explicit confirmation | Operator must confirm destructive action (CLI: `--force` or interactive prompt; API: confirmation token). |
| Permission check | Future: only users with appropriate role may perform destructive actions. |
| Audit trail | Every destructive action logged with: who, what, when, why. |
| Soft delete preferred | Archive/mark as deleted rather than permanent removal. |
| Irreversible actions require stronger approval | Hard deletes require escalated confirmation. |
| No bulk delete without preview | Operator must see what will be deleted before confirming. |

---

# 23. Testing Security Boundaries

## 23.1. Current Security Tests

Security boundaries are verified by:

| Test | What It Verifies | Location |
|---|---|---|
| `test_invalid_project_id_is_rejected` | `../example`, `example/child`, `""`, `"Example"`, `"demo project"` rejected by `validate_project_id` | `tests/services/test_projects.py:58` |
| `test_missing_project_raises_clear_error` | Non-existent project returns clear error | `tests/services/test_projects.py:52` |
| `test_required_project_fields_are_validated` | Missing `project_slug` raises `ProjectConfigValidationError` | `tests/services/test_projects.py:66` |
| `test_required_brand_profile_fields_are_validated` | Empty `positioning` raises `ProjectConfigValidationError` | `tests/services/test_projects.py:89` |
| `test_task_2_files_do_not_contain_project_specific_branching_markers` | Core files contain no `if project_id == ...` | `tests/services/test_projects.py:113` |
| `test_rejects_absolute_paths_in_manifest_files` (inspect) | Absolute paths in manifest rejected | `tests/services/test_inspect_package.py:128` |
| `test_rejects_absolute_paths_in_manifest_files` (validate) | Absolute paths in manifest rejected | `tests/services/test_validate_package.py:200` |
| Invalid transition tests | Illegal status transitions raise `InvalidStatusTransitionError` | `tests/domain/test_transitions.py` |
| Invalid input tests | Invalid funnel_stage, source_type, priority rejected | Various service tests |
| Metric validation tests | Unknown metric keys, negative values, empty metrics rejected | `tests/services/test_import_manual_metrics.py` |

## 23.2. Test Isolation

Tests use temporary directories (`tempfile.TemporaryDirectory`) for storage
isolation. Tests do not write to production `projects/` or `storage/` directories.
This prevents test interference with real project data.

## 23.3. Future Security Tests (Conceptual)

| Test Category | What It Verifies |
|---|---|
| Agent boundary tests | Agent cannot write files directly; cannot bypass services; cannot access cross-project data. |
| Secret leakage tests | Verify no secrets in export packages, logs, agent prompts, CLI output. |
| Connector mock security tests | Connector requires approval; connector handles auth failure safely; connector logs without secrets. |
| RBAC tests | User without role cannot perform restricted operation. |
| Audit tests | Audit records are created for all defined audit event types. |
| Path traversal with symlinks | Symlink-based escape from project root rejected. |

---

# 24. Current Known Security Limitations

## 24.1. Honest Assessment

The following are **known limitations** of the current Foundation MVP. They are
acceptable for a local single-user tool but must be addressed before production
SaaS deployment.

| Limitation | Impact | Mitigation in MVP |
|---|---|---|
| No authentication | Anyone with filesystem access can run scripts and read project data. | Local-only execution. No network exposure. |
| No user roles | All operations have equal access. No distinction between admin/operator/viewer. | Single-user model. No role separation needed. |
| No access control | Filesystem permissions are the only access mechanism. | Developer's local machine. No external access. |
| No audit log | No persisted record of who did what and when. | Terminal output provides transient trace. |
| No secret manager | Credentials would be stored in plaintext if they existed. | No secrets exist. No connectors, no DB, no APIs. |
| No runtime state persistence | Execution state is in-memory only. Crashes lose context. | Scripts are re-runnable from start. |
| No locking / concurrency protection | Multiple simultaneous script invocations could write conflicting files. | Single-process, single-user. Manual discipline. |
| No sandboxing of future agents | No isolation mechanism for agent execution. | No agents exist. Defined as future requirement. |
| No production hardening | No HTTPS, WAF, rate limiting, DDoS protection. | Not deployed. Local tool only. |
| No input sanitization beyond regex | Agent-generated inputs (future) would need additional sanitization. | No agents. All inputs are developer-supplied. |

## 24.2. When Each Limitation Must Be Addressed

| Limitation | Must Be Addressed Before |
|---|---|
| Authentication, user roles, access control | SaaS Platform stage |
| Audit log | Agentic Operations stage (agent decisions must be auditable) |
| Secret manager | First connector integration |
| Runtime state persistence | Agentic Operations stage (resume from failure) |
| Locking / concurrency | Multi-user deployment |
| Agent sandboxing | Agentic Operations stage (before agents execute autonomously) |
| Production hardening | SaaS Platform stage |
| Input sanitization | Agentic Operations stage (before agents generate inputs) |

---

# 25. Future Security Extension Path

## 25.1. Staged Extension

LOOPRA security evolves through defined stages, aligned with the overall
architecture evolution (`AGENTS.md`, Section 4):

```
Foundation MVP (current)
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
```

## 25.2. Security Stage Definitions

| Stage | Security Additions | Dependencies |
|---|---|---|
| **Stage 1 — Current local safety boundaries** | Regex project/entity ID validation. Path traversal prevention. Service ownership of mutations. Read-only tools. .gitignore hygiene. No secrets. No external calls. Manual publication only. | None (current). |
| **Stage 2 — Standardized audit records** | `RuntimeError` structured model. Execution context persistence. Entity mutation logging. Tool invocation logging. | Runtime state storage (DB or file). |
| **Stage 3 — ApprovalService** | Structured approval records. Approval gate enforcement per autonomy mode. Approval history. | Audit records (Stage 2). |
| **Stage 4 — Agent-safe tool invocation** | Tool registry. Approved commands only. Agent-to-runtime contract enforcement. Agent sandboxing. | ApprovalService (Stage 3). |
| **Stage 5 — Secret manager boundary** | Secret management integration. Credential scoping. No secrets in config/logs/exports. | None (can be added independently). |
| **Stage 6 — Connector safety framework** | Connector approval gates. Preflight validation. Dry-run support. Platform response recording. Retry policies. Failure handling. | Secret manager (Stage 5). ApprovalService (Stage 3). |
| **Stage 7 — Auth and workspace access control** | User accounts. Authentication. Workspace membership. Role-based permissions. | Database. API layer. |
| **Stage 8 — DB/object storage security** | Encrypted connections. Row-level security. Storage access policies. Backup encryption. | Database. Object storage. |
| **Stage 9 — Production deployment hardening** | HTTPS. WAF. Rate limiting. DDoS protection. Secrets rotation. Dependency scanning. | Cloud deployment. |
| **Stage 10 — Compliance/privacy controls (if SaaS)** | GDPR/CCPA compliance. Data export/delete. Retention policies. Privacy documentation. | Auth (Stage 7). Audit (Stage 2). |

## 25.3. Stage Ordering Rationale

The stages are ordered by dependency:

- Audit records (Stage 2) underpin approval (Stage 3), which underpins agent
  safety (Stage 4) and connector safety (Stage 6).
- Secret manager (Stage 5) can be added independently but is a prerequisite for
  connectors (Stage 6).
- Auth (Stage 7) depends on database and API layer — these belong to later
  architecture phases.
- Production hardening (Stage 9) and compliance (Stage 10) are final stages,
  relevant only when the system is deployed as SaaS.

---

# 26. Security Readiness Criteria

This document is considered ready when:

- [x] Current MVP security model defined (no auth, no users, no roles, local-only).
- [x] Project isolation defined (regex validation, path containment, scoped storage).
- [x] Path safety defined (validate_project_id, resolve_project_dir, entity ID patterns).
- [x] Storage mutation boundary defined (services own mutations, tools read-only or service-backed).
- [x] Service/tool boundaries defined (preconditions, transitions, error handling).
- [x] Configuration safety defined (project.yaml immutability, env var scope limits).
- [x] Secrets boundary defined (no secrets, future rules, secret manager prerequisite).
- [x] Publication safety defined (manual only, no external calls, no autoposting).
- [x] Analytics safety defined (supported keys only, draft-only recording, no external APIs).
- [x] Future agent safety defined (agents must not bypass runtime/services, no direct storage, auditable).
- [x] Autonomy safety defined (copilot only in MVP, future modes with emergency stop and approval gates).
- [x] Connector safety future defined (approval gates, credential scoping, preflight, audit).
- [x] Auditability future defined (current limited to timestamps + terminal; future structured audit records).
- [x] Known limitations documented (honest assessment of current gaps).
- [x] Foundation MVP constraints preserved (no premature auth/SaaS/API/DB features described as current).

---

# 27. Related Documents

| Document | Relevance |
|---|---|
| `AGENTS.md` | Development rules, architecture evolution stages, scope boundaries. |
| `STATE.md` | Current project status, Foundation MVP scope, important boundaries. |
| `docs/00_foundation/DATA_MODEL.md` | Current foundation entity set, entity roles, storage/scoping rules. |
| `docs/00_foundation/PROJECT_SETTINGS_SPEC.md` | Project configuration, security and secrets section, validation rules. |
| `docs/02_architecture/SYSTEM_ARCHITECTURE.md` | System layers, autonomy model, project scoping, Foundation MVP boundary. |
| `docs/02_architecture/PIPELINES_SPEC.md` | Current pipeline stages, runtime artifacts, boundary rules. |
| `docs/03_intelligence/AGENT_SYSTEM_SPEC.md` | Orchestrator Agent role, agent safety and boundaries, autonomy modes, human controls. |
| `docs/03_intelligence/CONTENT_CYCLE_SPEC.md` | Cycle stages, autonomy mode impact, Foundation MVP relationship. |
| `docs/04_production/DISTRIBUTION_SPEC.md` | Distribution modes, manual publication workflow, connector safety future, approval gates. |
| `docs/04_production/ANALYTICS_SPEC.md` | Metric sources, manual vs connector collection, MetricSnapshot safety, data completeness. |
| `docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md` | Runtime execution flow, entry points, agent-to-runtime contract, project scoping, tool invocation model. |
| `docs/05_platform/SERVICE_CONTRACTS_SPEC.md` | Service responsibilities, preconditions, transitions, errors, repository boundaries. |
| `docs/05_platform/TOOLING_AND_CLI_SPEC.md` | Tool responsibilities, inputs/outputs, service usage, read-only vs mutation boundaries. |
| `docs/05_platform/STORAGE_AND_STATE_SPEC.md` | Source vs runtime storage, git hygiene, project-scoped paths, artifact rules. |
| `docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md` | Configuration hierarchy, env var boundaries, future secrets and credentials, validation. |
| `docs/05_platform/TESTING_AND_VALIDATION_SPEC.md` | Test inventory, security boundary tests, future agent safety tests. |

---

# 28. Code References

| File | Relevance |
|---|---|
| `core/projects/loader.py` | `validate_project_id()` (regex), `resolve_project_dir()` (path containment), `ProjectConfig`, `InvalidProjectIdError`. |
| `core/services/_storage.py` | `ENTITY_ID_PATTERN`, `_validate_entity_id()`, `FileSystemProjectModelRepository` base class. |
| `core/services/projects.py` | `ProjectService`, `BrandProfileService`, `FileSystemProjectRepository`. |
| `core/services/ideas.py` | `IdeaService`, `ScenarioService`, `FileSystemIdeaRepository`, `FileSystemScenarioRepository`. |
| `core/services/production.py` | `ProductionLifecycleService`, `FileSystemContentItemRepository`. |
| `core/services/publishing.py` | `PublishingService`, `FileSystemExportPackageRepository`, `FileSystemPublicationRepository`. |
| `core/services/analytics.py` | `AnalyticsService`, `SUPPORTED_MANUAL_METRIC_KEYS`, `FileSystemMetricSnapshotRepository`. |
| `core/services/loop.py` | `LoopOrchestrator`, `build_loop_orchestrator()`. |
| `core/domain/transitions.py` | Status transition rules, `validate_status_transition()`, `InvalidStatusTransitionError`. |
| `scripts/smoke_loop.py` | End-to-end smoke loop, env var-based project selection, runtime project directory setup. |
| `scripts/inspect_package.py` | Read-only export package inspector. Absolute path rejection. |
| `scripts/validate_package.py` | Read-only export package validator. Absolute path rejection. |
| `scripts/find_metric_snapshots.py` | Read-only metric snapshot finder. Project validation via `load_project()`. |
| `scripts/import_manual_metrics.py` | Manual metrics import via `AnalyticsService.record_metrics()`. Payload validation. |
| `tests/domain/test_transitions.py` | Domain transition validation tests. |
| `tests/services/test_projects.py` | Project ID validation tests, config validation tests, project-agnostic marker tests. |
| `tests/services/test_ideas.py` | Idea/Scenario service tests. |
| `tests/services/test_loop_engineering.py` | Loop orchestrator tests. |
| `tests/services/test_validate_package.py` | Export package validation tests (structural, path safety). |
| `tests/services/test_import_manual_metrics.py` | Manual metrics import validation tests. |
| `.gitignore` | Artifact exclusion: `.env`, `storage/*`, `graphify-out/`, Python bytecode, generated outputs. |

---

# 29. Document Status

| Field | Value |
|---|---|
| Status | Active — LOOPRA Platform Layer |
| Version | 1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Platform Layer — Security and Safety Boundaries |

---

# Final Statement

Security in LOOPRA is currently local enforcement — regex validation, path
containment, service preconditions, manual operations. This is correct and
sufficient for the Foundation MVP.

As the system evolves toward autonomous marketing operations, every new
capability must bring its security boundary with it:

- Agents → auditable, sandboxed, runtime-bound.
- Autonomy → bounded, stoppable, approval-gated.
- Connectors → credential-scoped, preflight-validated, approval-gated.
- Multi-tenancy → auth-backed, project-isolated, permission-checked.
- Production → hardened, monitored, secret-managed.

No future capability may activate without its corresponding security boundary in
place. This document defines what those boundaries are — not as a product backlog,
but as architectural prerequisites for safe evolution.

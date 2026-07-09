# TESTING AND VALIDATION SPEC

## Version

v1.0

## Status

Active — LOOPRA Platform Layer

## Purpose

This document defines the Testing and Validation Layer of the LOOPRA
Autonomous Marketing Operating System.

It answers the central question:

> How does LOOPRA verify the correctness of domain models, service contracts,
> runtime loop, CLI tools, export packages, manual metrics workflow and future
> agent/runtime behaviour without violating the Foundation MVP?

TESTING_AND_VALIDATION_SPEC.md is the bridge between domain tests, service tests,
CLI/script tests, smoke loop, export package validation, manual metrics workflow,
operational acceptance and future runtime/agent testing.

It describes the real current test suite as it exists in the codebase. Tests,
validation layers and test categories that do not exist are explicitly marked as
future/conceptual.

---

# 1. Purpose and Scope

## 1.1. Document Purpose

This document defines:

- the role of testing and validation in the LOOPRA architecture;
- the current test inventory based on actual code in `tests/`;
- domain model and transition validation;
- service contract verification;
- runtime loop and smoke loop testing;
- CLI tool testing and validation;
- export package validation (structural, not content quality);
- manual metrics validation;
- configuration and storage validation in tests;
- test isolation rules and fixture model;
- layered validation model;
- error testing coverage;
- operational acceptance testing;
- regression testing rules;
- current coverage boundaries;
- future test categories (marked conceptual/future);
- future agent safety tests (conceptual);
- future CI/quality gates (conceptual);
- testing extension path (staged);
- Foundation MVP compatibility preservation.

## 1.2. In Scope

- current test structure (`tests/domain/`, `tests/services/`);
- domain tests — models, enums, status transitions;
- service tests — Projects, Ideas, Scenarios, Production, Publishing, Analytics;
- runtime loop tests — LoopOrchestrator, smoke loop;
- CLI/script tests — smoke_loop.py, inspect_package.py, validate_package.py,
  find_metric_snapshots.py, import_manual_metrics.py;
- export package validation — structural checks, manifest validation;
- manual metrics validation — JSON payload, metric keys, transitions;
- configuration validation — project.yaml required fields, brand fields, aliases;
- storage validation in tests — temp dirs, isolated project roots;
- operational acceptance — smoke loop, package inspect, package validate,
  manual metrics import;
- future testing path — agent safety, CI gates, integration tests, connector
  tests, DB tests.

## 1.3. Out of Scope

- writing new tests (this is a specification, not a task list);
- CI implementation (no CI exists in current MVP);
- API endpoint tests (no API exists);
- UI tests (no UI exists);
- database tests (no DB exists);
- external connector tests (no connectors exist);
- autoposting tests (no autoposting exists);
- media rendering tests (no media renderer exists);
- asset library implementation tests (not implemented);
- performance/load testing implementation;
- production monitoring implementation.

---

# 2. Role of Testing in LOOPRA

## 2.1. What Testing Verifies

Testing in LOOPRA verifies:

- **Domain invariants** — entities have correct fields, required fields are
  enforced, owner modules are valid.
- **Allowed transitions** — every entity status transition is validated;
  forbidden transitions raise errors.
- **Service contracts** — every service operation validates preconditions,
  enforces transitions, and returns correct outputs.
- **Runtime sequence** — the full lifecycle chain executes without errors;
  each step produces the correct intermediate state.
- **Artifact correctness** — export packages contain all required files with
  correct structure; entity JSON is parseable and valid.
- **CLI behaviours** — tools accept correct inputs, produce correct outputs,
  return correct exit codes.
- **Manual workflow correctness** — smoke loop → package inspect → package
  validate → find snapshots → import metrics works end-to-end.
- **Configuration correctness** — project.yaml required fields validated;
  brand fields validated; invalid statuses rejected.
- **Project agnosticism** — core code contains no project-specific branching
  markers or hardcoded project values.
- **Storage isolation** — tests do not pollute source projects; runtime artifacts
  stay under `storage/smoke_projects/`.

## 2.2. What Testing Does NOT Do

Testing does not:

- decide content strategy (what topic, what audience, what format);
- evaluate creative quality (whether content is "good");
- replace human review (approval gates remain human-operated in MVP);
- replace architectural specifications (specs are the source of truth);
- define product strategy (testing verifies correctness, not direction);
- guarantee business success (testing verifies behaviour, not market fit).

## 2.3. Principle

> Tests verify behaviour. Validation checks outputs and invariants. Tests do not
> define product strategy. Tests do not replace architectural specs. Tools
> validate artifacts, not strategic decisions. Future agent tests must verify
> boundaries and safety, not agent creativity.

---

# 3. Testing Principles

1. **Test from domain outward.** Verify domain models and transitions first,
   then services that use them, then runtime that orchestrates services, then
   CLI tools that provide entrypoints.

2. **Every lifecycle transition must be tested.** If a domain entity has allowed
   transitions, there must be tests that exercise those transitions and tests
   that reject invalid ones.

3. **Every service contract must be verified.** Each public service method must
   have tests that verify: valid inputs → correct output; invalid inputs →
   correct error; wrong entity state → correct error.

4. **Runtime smoke loop proves operational continuity.** The complete Foundation
   MVP chain (Project → Idea → Scenario → ContentItem → ExportPackage →
   Publication → MetricSnapshot) must execute without errors. A smoke loop
   failure signals a broken lifecycle.

5. **CLI tools must be testable and deterministic.** Given the same inputs and
   unchanged project state, a tool produces the same output. No randomness, no
   hidden state.

6. **Generated artifacts must be inspectable and validatable.** Export packages
   must pass `inspect_package.py` (readable) and `validate_package.py`
   (structurally correct).

7. **Tests must isolate project roots.** Every test uses `tempfile.
   TemporaryDirectory()` or explicit `projects_root` overrides. No test writes to
   source `projects/` or `storage/smoke_projects/` without explicit intent.

8. **Tests must not depend on external APIs.** All tests run locally with
   deterministic inputs. No network calls. No platform connectors.

9. **Future connectors require mocked/integration separation.** When external
   connectors are introduced, connector tests must use mocked APIs. Integration
   tests against real platforms require separate configuration and must never
   run in the default test suite.

10. **No MVP regression without test failure.** Any change that breaks the
    Foundation MVP chain must cause at least one test to fail.

---

# 4. Current Test Inventory

## 4.1. Test Framework

LOOPRA uses **Python `unittest`** (standard library). There is no `pyproject.toml`,
no `pytest.ini`, and no third-party test runner configured at the repository
root.

Tests are discovered and executed via:

```bash
python -m unittest discover -s tests
```

Or individually:

```bash
python -m unittest tests.domain.test_models
python -m unittest tests.services.test_loop_engineering
```

## 4.2. Test File Inventory

### Domain Tests

| File | Purpose | Layer Tested | Current/Future |
|---|---|---|---|
| `tests/domain/test_models.py` | Domain entity creation, field requirements, owner modules, format defaults | Domain models | Current |
| `tests/domain/test_transitions.py` | Status transition rules for Idea, Scenario, ContentItem, ExportPackage, Publication, MetricSnapshot, RenderJob | Domain transitions | Current |

### Service Tests

| File | Purpose | Layer Tested | Current/Future |
|---|---|---|---|
| `tests/services/test_projects.py` | ProjectService, BrandProfileService, project config validation, required fields, invalid project IDs, project-agnostic markers | Services — Projects | Current |
| `tests/services/test_ideas.py` | IdeaService, ScenarioService — create, approve, reject, archive, scenario generation, QA, project scoping | Services — Ideas/Scenarios | Current |
| `tests/services/test_loop_engineering.py` | ProductionLifecycleService, PublishingService, AnalyticsService, LoopOrchestrator — full lifecycle, export package creation, publication, metrics, dual-recording rejection | Services — Production/Publishing/Analytics, Runtime | Current |
| `tests/services/test_smoke_loop.py` | smoke_loop.py subprocess execution — stdout parsing, entity statuses, export file listing | CLI/Script + Runtime | Current |
| `tests/services/test_inspect_package.py` | inspect_package.py manifest reading, display, error handling (missing args, missing dir, missing manifest, invalid JSON, missing fields, absolute paths) | CLI/Script — Inspection | Current |
| `tests/services/test_validate_package.py` | validate_package.py structural validation, manifest checks, file existence, metadata, manual_publication_only, status, error conditions | CLI/Script — Validation | Current |
| `tests/services/test_find_metric_snapshots.py` | find_metric_snapshots.py snapshot listing, DRAFT filtering, error handling (missing project, invalid JSON, missing fields, non-directory storage), env var override | CLI/Script — Query | Current |
| `tests/services/test_import_manual_metrics.py` | import_manual_metrics.py JSON parsing, validation, service call, clicks→link_clicks normalization, published_url→Publication update, BOM handling, error conditions | CLI/Script — Mutation | Current |
| `tests/services/test_manual_metrics_workflow.py` | End-to-end manual metrics workflow: smoke loop → find snapshots → import metrics → verify recording | CLI/Script + Runtime | Current |

---

# 5. Domain Tests

## 5.1. test_models.py

**File:** `tests/domain/test_models.py:29-199`

**What is tested:**

| Test | What It Verifies |
|---|---|
| `test_domain_models_are_importable_and_can_be_created` | All domain entities (Workspace, Project, BrandProfile, Idea, Scenario, ContentItem, RenderJob, OutputFile, ExportPackage, Publication, MetricSnapshot) can be instantiated with valid fields. Verifies default content_format (`TEXT_SOCIAL_POST`), funnel_stage, platform assignment, owner_module (PRODUCTION_ENGINE, PUBLISHING_HUB, ANALYTICS). |
| `test_project_level_entities_require_project_id` | Every project-scoped entity (BrandProfile, Idea, Scenario, RenderJob, OutputFile, ContentItem, ExportPackage, Publication, MetricSnapshot) has `project_id` as a required field. |
| `test_publication_published_state_requires_url_and_timestamp` | Creating a Publication with `status=PUBLISHED` without `published_at` and `published_url` raises `ValidationError`. |
| `test_content_item_and_publication_statuses_are_separate_lifecycles` | ContentItem at `APPROVED` and Publication at `PLANNED` are independent — they do not interfere. |
| `test_export_package_boundary_rejects_production_engine_owner` | ExportPackage with `owner_module=PRODUCTION_ENGINE` raises `ValidationError`. ExportPackage must be owned by PUBLISHING_HUB. |

**Why it matters:** These tests validate that domain entities enforce their
structural rules at the model level (pydantic validators). A failure indicates
a model definition change that breaks entity invariants.

## 5.2. test_transitions.py

**File:** `tests/domain/test_transitions.py:26-169`

**What is tested:**

| Test | What It Verifies |
|---|---|
| `test_idea_valid_transitions` | RAW → APPROVED and APPROVED → SCRIPTED are allowed. |
| `test_idea_invalid_transition_is_rejected` | RAW → SCRIPTED is rejected (must go through APPROVED first). |
| `test_scenario_invalid_transition_is_rejected` | DRAFT → APPROVED is rejected (must go through NEEDS_REVIEW first). |
| `test_render_job_transition_flow` | PENDING → VALIDATING → RENDERING → RENDERED chain works. |
| `test_content_item_transition_flow` | DRAFT → IN_PRODUCTION → RENDERED → NEEDS_REVIEW → APPROVED → EXPORTED full chain works. |
| `test_export_package_transition_flow` | DRAFT → READY is allowed. |
| `test_publication_invalid_transition_is_rejected` | PUBLISHED → FAILED is rejected (cannot fail after success). |
| `test_publication_transition_to_published_sets_manual_publication_data` | PLANNED → PUBLISHED with `published_at` and `published_url` sets both fields correctly. |
| `test_metric_snapshot_invalid_transition_is_rejected` | RECORDED → DRAFT is rejected (cannot go backwards). |

**Why it matters:** Transitions define the lifecycle rules. Every allowed
transition must work. Every forbidden transition must raise
`InvalidStatusTransitionError`. The ContentItem full chain test
(DRAFT → EXPORTED) is the most critical — it exercises 5 sequential transitions
that form the production backbone.

---

# 6. Service Tests

## 6.1. test_projects.py

**File:** `tests/services/test_projects.py:19-137`

**Service tested:** `ProjectService`, `BrandProfileService`

**Operations covered:**

| Test | What It Verifies |
|---|---|
| `test_project_can_be_loaded_from_example_project_config` | `load_project()` and `ProjectService.get_project()` return matching projects for "example". |
| `test_list_projects_returns_example_project` | Project listing includes "example". |
| `test_brand_profile_can_be_built_from_project_config` | `BrandProfileService.get_brand_profile("example")` returns a complete BrandProfile with name, status, brand_values, and tone_of_voice. |
| `test_missing_project_raises_clear_error` | Non-existent project raises `FileNotFoundError` with project_id in message. |
| `test_invalid_project_id_is_rejected` | Invalid IDs (`../example`, empty, uppercase, spaces) raise `InvalidProjectIdError`. Path traversal protection verified. |
| `test_required_project_fields_are_validated` | Missing `project_slug` raises `ProjectConfigValidationError` with field name in message. |
| `test_required_brand_profile_fields_are_validated` | Empty `brand.positioning` raises `ProjectConfigValidationError` with `brand.positioning` in message. |
| `test_task_2_files_do_not_contain_project_specific_branching_markers` | Core project files do not contain `if project_id ==` patterns — project-agnostic enforcement. |

**Storage isolation:** Tests that require missing/invalid config use
`tempfile.TemporaryDirectory()` for isolated project roots. The
`test_project_can_be_loaded_from_example_project_config` test reads from the
source `projects/` directory (read-only).

## 6.2. test_ideas.py

**File:** `tests/services/test_ideas.py:22-153`

**Services tested:** `IdeaService`, `ScenarioService`

**Operations covered:**

| Test | What It Verifies |
|---|---|
| `test_create_idea_persists_project_scoped_records` | Ideas are scoped to project — only the creating project's ideas are listed. `next_action_for` returns correct action by status. |
| `test_invalid_funnel_stage_is_rejected` | Unknown `funnel_stage` ("awareness") raises `IdeaBankValidationError`. |
| `test_approved_idea_can_generate_text_social_post_scenario` | Full flow: create Idea → approve → create_from_idea. Verifies Scenario status (NEEDS_REVIEW), Idea transition (APPROVED → SCRIPTED), target platforms (TELEGRAM, THREADS, VK), blocks (3 per platform), caption_drafts, metadata. |
| `test_raw_idea_cannot_generate_scenario` | RAW Idea cannot be used for scenario creation — raises `ScenarioStudioValidationError`. |
| `test_generated_scenario_can_be_approved` | Full create → approve → generate → approve_scenario chain. Scenario reaches APPROVED. |
| `test_task_3_files_do_not_contain_project_specific_branching_markers` | Core files (enums.py, models.py, ideas.py) remain project-agnostic. |

**Storage isolation:** All tests use `tempfile.TemporaryDirectory()` for
`projects_root`. The `_write_project_fixture` method copies the source
example project config template and customizes `project_id`, `project_name`,
`project_slug`, and `brand.brand_name` — project-agnostic fixture construction.

**Domain transitions checked:**
- Idea: RAW → APPROVED (approve)
- Idea: APPROVED → SCRIPTED (create_from_idea side effect)
- Scenario: new → NEEDS_REVIEW (create_from_idea)
- Scenario: NEEDS_REVIEW → APPROVED (approve_scenario)

## 6.3. test_loop_engineering.py

**File:** `tests/services/test_loop_engineering.py:39-614`

**Services tested:** `ProductionLifecycleService`, `PublishingService`,
`AnalyticsService`, `LoopOrchestrator`

This is the largest and most comprehensive test file. It uses a shared
`LoopEngineeringFixture` base class that constructs all services, repositories,
and orchestrator against an isolated temp directory with project fixtures.

### ProductionLifecycleServiceTests

| Test | What It Verifies |
|---|---|
| `test_creates_content_item_from_approved_scenario` | ContentItem created with correct project_id, scenario_id, status=RENDERED, non-empty body. |
| `test_runs_minimal_technical_qa` | QA returns NEEDS_REVIEW, `technical_qa_passed=True`, no QA errors. |
| `test_approves_review_ready_content` | Full create → QA → approve chain. Content reaches APPROVED. |
| `test_rejects_invalid_content_approval_transition` | Cannot approve RENDERED content (must go through QA/NEEDS_REVIEW first). Raises `InvalidStatusTransitionError`. |

### PublishingServiceTests

| Test | What It Verifies |
|---|---|
| `test_creates_and_prepares_export_package` | Full export flow: create_export_package → prepare_export. Verifies all 6 files exist (title.txt, body.txt, caption_telegram.txt, manual_publication_checklist.txt, metadata.json, manifest.json), ExportPackage status=READY, ContentItem status=EXPORTED, file contents match (title, body, caption), metadata.json structure (all fields), manifest.json structure (all fields + file list), no project-specific markers, no absolute file paths in manifest. |
| `test_prepare_export_prefers_scenario_caption_draft_for_target_platform` | Custom caption_drafts are used for caption file output. |
| `test_prepare_export_falls_back_safely_when_caption_draft_is_missing` | When caption_drafts is empty, falls back to content_item.body. |
| `test_creates_manual_publication_and_marks_it_published` | Full publish flow: create_publication → publish_content. Verifies Publication statuses (PLANNED → PUBLISHED), metadata (manual_publication_only, publication_method, source, target_platform), URL and timestamp. |
| `test_rejects_empty_published_url` | Whitespace-only URL raises `PublishingValidationError`. |
| `test_marks_publication_as_failed` | `fail_publication()` transitions PLANNED → FAILED with failure_reason in notes. |
| `test_rejects_invalid_publication_transition` | Published publication cannot be failed — raises `InvalidStatusTransitionError`. |
| `test_rejects_publication_creation_before_export_is_ready` | Creating publication from DRAFT export package raises `PublishingValidationError`. |

### AnalyticsServiceTests

| Test | What It Verifies |
|---|---|
| `test_creates_metric_snapshot_and_records_metrics` | Full metrics flow: create_metric_snapshot → record_metrics. Verifies DRAFT→RECORDED transition, all 7 metric values (views, likes, comments, shares, saves, link_clicks), clicks→link_clicks normalization, published_url updates Publication, source_type="manual". |
| `test_future_facing_analytics_stubs_return_empty_lists` | `get_insights()` and `generate_new_ideas_from_metrics()` return `[]` — stubs exist but are not active. |
| `test_rejects_recording_metrics_twice` | Second `record_metrics()` on same snapshot raises `AnalyticsValidationError`. |
| `test_rejects_empty_metrics_dict` | Empty `{}` metrics raises `AnalyticsValidationError`. |
| `test_rejects_unknown_metric_keys` | "bookmarks" key raises `AnalyticsValidationError`. |
| `test_rejects_follows_until_model_has_storage_field` | "follows" key raises `AnalyticsValidationError`. |
| `test_rejects_negative_numeric_metrics` | `views=-1` raises `AnalyticsValidationError`. |
| `test_rejects_non_integer_numeric_metrics` | `clicks=1.5` raises `AnalyticsValidationError`. |
| `test_rejects_empty_published_url_in_metrics` | Whitespace-only `published_url` raises `AnalyticsValidationError`. |

### LoopOrchestratorTests

| Test | What It Verifies |
|---|---|
| `test_runs_minimal_end_to_end_loop_for_generic_project` | Full LoopOrchestrator.run_minimal_loop() on a non-"example" project ("second"). Verifies result dict (project_id, idea_id, status="completed"), Publication status=PUBLISHED, MetricSnapshot status=DRAFT, loop status counts, export directory exists. |
| `test_generated_scenario_is_approved_before_content_creation` | LoopOrchestrator explicitly approves the scenario. Scenario reaches APPROVED. |

**Storage isolation:** All tests use `tempfile.TemporaryDirectory()`. The
`_write_project_fixture` method generates project configs from a template.
Every entity mutation is scoped to the temp directory. `tearDown` cleans up.

---

# 7. Runtime / Loop Tests

## 7.1. LoopOrchestrator Tests

Covered in `test_loop_engineering.py` (Section 6.3). The
`LoopOrchestratorTests` class verifies:

- Full Foundation MVP chain execution (Project → Idea → Scenario → ContentItem →
  ExportPackage → Publication → MetricSnapshot).
- Result dict returns all entity IDs and `status="completed"`.
- Entity statuses reach expected terminal states.
- Project agnosticism — loop works for any valid project, not just "example".
- Scenario is explicitly approved before content creation.

## 7.2. Smoke Loop Tests

**File:** `tests/services/test_smoke_loop.py:15-58`

This is a **subprocess-level test** — it runs `python scripts/smoke_loop.py`
in a subprocess with isolated `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` pointing to
a temp directory.

**What is tested:**

| Assertion | What It Verifies |
|---|---|
| `completed.returncode == 0` | Full smoke loop exits successfully. |
| `project_id=example` | Default project is "example". |
| `scenario_status=approved` | Scenario was approved. |
| `content_item_status=exported` | ContentItem was exported (not just approved). |
| `export_package_status=ready` | ExportPackage is ready for manual publication. |
| `publication_status=published` | Publication record was created and marked published. |
| `metric_snapshot_status=draft` | Draft MetricSnapshot was created. |
| Export directory exists | The export output directory is on disk. |
| Generated export files match expected list | All 6 files: body.txt, caption_telegram.txt, manifest.json, manual_publication_checklist.txt, metadata.json, title.txt. |

**Why it matters:** This is the **definitive operational acceptance test**. If
this test fails, the entire Foundation MVP lifecycle is broken. It proves that
all services, repositories, transitions, and artifact generation work together
end-to-end.

## 7.3. Manual Metrics Workflow Tests

**File:** `tests/services/test_manual_metrics_workflow.py:29-176`

This test runs the complete manual metrics workflow as subprocess invocations:

1. Run `smoke_loop.py` → get entity IDs
2. Run `find_metric_snapshots.py` → locate DRAFT snapshot
3. Run `import_manual_metrics.py` → record metrics
4. Verify: snapshot is RECORDED, metrics are correct, Publication URL updated,
   `clicks` normalized to `link_clicks`, `published_url` not in content_metrics

**Why it matters:** This proves that the full operational workflow — from smoke
loop through metric recording — works as a sequence of real CLI tool invocations.
It is the closest current test to a full integration test.

---

# 8. CLI / Tool Tests

## 8.1. test_inspect_package.py

**File:** `tests/services/test_inspect_package.py:38-151`

Tests `inspect_package.py` via subprocess invocations.

| Test | Input | Expected Output | Exit |
|---|---|---|---|
| `test_inspects_valid_export_package_directory` | Valid export dir with correct manifest | All 8 manifest fields + file listing with roles | 0 |
| `test_returns_clear_error_when_argument_is_missing` | No arguments | "usage: python scripts/inspect_package.py..." | ≠0 |
| `test_returns_clear_error_when_directory_is_missing` | Non-existent path | "export package directory does not exist" | ≠0 |
| `test_returns_clear_error_when_manifest_is_missing` | Dir without manifest.json | "manifest.json not found" | ≠0 |
| `test_returns_clear_error_when_manifest_json_is_invalid` | Dir with `{not-json` | "manifest.json is not valid JSON" | ≠0 |
| `test_returns_clear_error_when_required_fields_are_missing` | Manifest without `scenario_id` | "manifest.json is missing required fields: scenario_id" | ≠0 |
| `test_rejects_absolute_paths_in_manifest_files` | Manifest with absolute file path | "must not be an absolute path" | ≠0 |
| `test_script_files_do_not_contain_project_specific_strings` | Reads script and test files | No project-specific markers found | N/A |

**Fixture model:** Uses a `_build_manifest()` helper that creates a standard
valid manifest dict. Tests override individual fields to trigger specific errors.
Export packages are built in temp directories with only the files needed for
each test case.

## 8.2. test_validate_package.py

**File:** `tests/services/test_validate_package.py:52-313`

Tests `validate_package.py` via subprocess invocations. More extensive than
inspect tests because validation has stricter rules.

| Test | Input | Expected Output | Exit |
|---|---|---|---|
| `test_validates_complete_export_package_directory` | Complete valid package with all files | "validation_status=ok", "ready_for_manual_publication=true", files_checked=6 | 0 |
| `test_returns_clear_error_when_argument_is_missing` | No arguments | "usage: python scripts/validate_package.py..." | ≠0 |
| `test_returns_clear_error_when_directory_is_missing` | Non-existent path | "export package directory does not exist" | ≠0 |
| `test_returns_clear_error_when_manifest_is_missing` | Dir without manifest.json | "manifest.json not found" | ≠0 |
| `test_returns_clear_error_when_manifest_json_is_invalid` | `{not-json` | "manifest.json is not valid JSON" | ≠0 |
| `test_returns_clear_error_when_required_manifest_field_is_missing` | Manifest without `scenario_id` | "manifest.json is missing required fields: scenario_id" | ≠0 |
| `test_returns_clear_error_when_files_field_is_not_a_list` | `"files": "not-a-list"` | "manifest.json field 'files' must be a list" | ≠0 |
| `test_returns_clear_error_when_file_entry_is_missing_name_or_role` | File object missing name or role | "manifest.json field 'files[0]' is missing required fields: name" / "role" | ≠0 |
| `test_rejects_absolute_paths_in_manifest_files` | Absolute path in manifest | "must not be an absolute path" | ≠0 |
| `test_returns_clear_error_when_manifest_lists_file_missing_on_disk` | Manifest references `extra_notes.txt` not on disk | "package file listed in manifest.json is missing on disk: extra_notes.txt" | ≠0 |
| `test_returns_clear_error_when_metadata_json_is_missing` | No metadata.json | "metadata.json not found" | ≠0 |
| `test_returns_clear_error_when_metadata_json_is_invalid` | `{not-json` in metadata.json | "metadata.json is not valid JSON" | ≠0 |
| `test_returns_clear_error_when_manual_publication_checklist_is_missing` | No checklist | "manual_publication_checklist.txt not found" | ≠0 |
| `test_returns_clear_error_when_expected_caption_file_is_missing` | No caption_telegram.txt | "expected package file not found: caption_telegram.txt" | ≠0 |
| `test_returns_clear_error_when_manual_publication_only_is_not_true` | `manual_publication_only: false` | "manifest.json field 'manual_publication_only' must be true" | ≠0 |
| `test_returns_clear_error_when_status_is_not_ready` | `status: "draft"` | "manifest.json field 'status' must be one of: ready" | ≠0 |
| `test_script_files_do_not_contain_project_specific_strings` | Reads script and test files | No project-specific markers found | N/A |

**Fixture model:** Uses `_write_valid_export_package()` helper that creates a
complete package with all required files. Supports parameters to omit specific
files, provide invalid manifest/override fields, or inject invalid metadata text.

## 8.3. test_find_metric_snapshots.py

**File:** `tests/services/test_find_metric_snapshots.py:34-366`

Tests `find_metric_snapshots.py` via subprocess invocations. Sets up a full
lifecycle (idea → scenario → content → export → publication → metric snapshot)
programmatically, then tests the script's ability to find and list snapshots.

| Test | What It Verifies |
|---|---|
| `test_lists_one_draft_metric_snapshot` | With one DRAFT snapshot, script finds 1, prints correct IDs and "status=draft". |
| `test_returns_success_when_no_draft_metric_snapshots_exist` | Empty project returns "metric_snapshots_found=0" with exit 0. |
| `test_returns_error_when_argument_is_missing` | No args → exit 1, usage message. |
| `test_returns_error_when_too_many_arguments_are_provided` | Extra arg → exit 1, usage message. |
| `test_returns_error_when_project_storage_is_missing` | Unknown project_id → exit 1, "Project config not found". |
| `test_returns_error_when_metric_snapshot_storage_cannot_be_read` | `metric_snapshots` is a file, not directory → exit 1, "metric snapshot storage is not a directory". |
| `test_returns_error_when_stored_snapshot_json_is_invalid` | Corrupted JSON → exit 1, "stored snapshot JSON is not valid JSON". |
| `test_returns_error_when_required_snapshot_fields_are_missing` | Snapshot JSON missing `publication_id` → exit 1, "missing required fields". |
| `test_recorded_metric_snapshots_are_not_listed` | After `record_metrics()`, snapshot is RECORDED → not listed (only DRAFT snapshots). |
| `test_respects_content_plant_projects_root_override` | `CONTENT_PLANT_PROJECTS_ROOT` env var points to alternate root → script uses it. |
| `test_new_script_does_not_introduce_project_specific_marker_strings` | Script text has no project-specific markers. |

## 8.4. test_import_manual_metrics.py

**File:** `tests/services/test_import_manual_metrics.py:34-402`

Tests `import_manual_metrics.py` via subprocess invocations. Tests the most
mutation-heavy CLI tool — it imports JSON, validates structure, calls service,
and records metrics.

| Test | What It Verifies |
|---|---|
| `test_imports_manual_metrics_from_valid_json` | Valid JSON with all 7 metric keys → exit 0, snapshot RECORDED, all metric values correct, published_url updates Publication. |
| `test_returns_error_when_argument_is_missing` | No args → exit 1, usage. |
| `test_returns_error_when_too_many_arguments_are_provided` | Extra arg → exit 1, usage. |
| `test_returns_error_when_json_file_is_missing` | Non-existent JSON path → exit 1. |
| `test_returns_error_when_json_is_invalid` | `{invalid` → exit 1, "not valid JSON". |
| `test_accepts_utf8_bom_json_written_by_powershell_style_tools` | UTF-8 BOM encoding → successfully imports. |
| `test_returns_error_when_required_top_level_fields_are_missing` | Missing `project_id` → exit 1, "missing required fields: project_id". |
| `test_returns_error_when_metrics_field_is_missing` | No `metrics` key → exit 1. |
| `test_returns_error_when_metrics_is_not_an_object` | `metrics` is an array → exit 1. |
| `test_returns_error_when_metrics_is_empty` | `metrics: {}` → exit 1. |
| `test_returns_error_for_unsupported_metric_keys` | `follows` key → exit 1, "Unknown metric keys: follows". |
| `test_returns_error_for_invalid_metric_values` | `clicks: 1.5` → exit 1, "clicks must be an integer". |
| `test_returns_error_when_project_is_unknown` | Unknown project_id → exit 1. |
| `test_returns_error_when_metric_snapshot_is_unknown` | Unknown snapshot_id → exit 1. |
| `test_returns_error_when_snapshot_publication_cannot_be_found` | Publication JSON deleted → exit 1. |
| `test_accepts_clicks_and_records_link_clicks` | `clicks: 7` → stored as `link_clicks: 7`. |
| `test_accepts_published_url_and_updates_related_publication` | `published_url` only (no numeric metrics) → Publication updated, snapshot transitioned. |
| `test_new_script_does_not_introduce_project_specific_marker_strings` | Script text is project-agnostic. |

---

# 9. Export Package Validation

## 9.1. Current Validation Scope

Export package validation in the current MVP is **structural**, not content-quality.

### What is validated:

| Validation | Tool | Checks |
|---|---|---|
| Manifest structure | `inspect_package.py` | JSON parseable, required fields present, `files` is a list of objects with name/role, no absolute paths |
| Manifest structure (stricter) | `validate_package.py` | All of inspect checks + non-empty strings, `manual_publication_only` must be `true`, `status` must be `"ready"` |
| File existence | `validate_package.py` | `metadata.json`, `manual_publication_checklist.txt`, `title.txt`, `body.txt`, `caption_{platform}.txt` exist on disk |
| Metadata validity | `validate_package.py` | `metadata.json` is parseable JSON |
| Manifest-to-disk consistency | `validate_package.py` | Every file listed in `manifest.files[].name` exists on disk |

### What is NOT validated (future/conceptual):

- Content quality (readability, brand voice, message coherence);
- Caption length relative to platform limits;
- Brand compliance (forbidden phrases, tone consistency);
- Production QA beyond the current minimal checks;
- Publication readiness beyond structural correctness;
- Strategy alignment (whether content matches goals).

## 9.2. Distinction: Structural vs Quality Validation

```text
Structural package validation (current MVP):
    - manifest.json exists and is valid JSON
    - manifest has required fields
    - all required files exist on disk
    - manifest references match disk contents
    - manual_publication_only is true
    - status is ready

Production QA (current MVP, limited):
    - empty title check
    - empty body check
    - missing brand_profile_id check

Content quality assessment:
    - NOT in current MVP
    - Future: brand voice consistency, readability, platform fit,
      goal alignment, audience appropriateness
```

## 9.3. Validation Flow

```text
PublishingService.prepare_export()
    ↓  writes export files to disk
    ↓
inspect_package.py  →  "Can I read the manifest? Are fields present?"
    ↓
validate_package.py  →  "Are all required files present? Is manifest valid?
                         Is the package structurally ready?"
    ↓
Manual publication  →  Human copies caption, publishes, records URL
```

---

# 10. Manual Metrics Validation

## 10.1. Current Validation Scope

Manual metrics validation in the current MVP checks:

### Payload structure (import_manual_metrics.py):

| Check | Rule |
|---|---|
| JSON parseable | File must be valid JSON or UTF-8 BOM JSON |
| Top-level fields | `project_id`, `metric_snapshot_id`, `metrics` must all be present and non-empty |
| `project_id` | Must be a non-empty string referencing a valid project |
| `metric_snapshot_id` | Must be a non-empty string referencing an existing DRAFT snapshot |
| `metrics` type | Must be a non-empty JSON object |

### Metric key validation (AnalyticsService):

| Check | Rule |
|---|---|
| Known keys | All keys must be in `SUPPORTED_MANUAL_METRIC_KEYS`: `views`, `likes`, `comments`, `shares`, `saves`, `clicks`, `published_url` |
| Numeric values | `views`, `likes`, `comments`, `shares`, `saves`, `clicks` must be non-negative integers (`>= 0`, type `int`) |
| `published_url` | If present, must be non-empty string (not whitespace-only) |

### Behaviour:

| Input | Normalization / Side Effect |
|---|---|
| `clicks` | Stored as `content_metrics.link_clicks` (not stored as "clicks") |
| `published_url` | Updates `Publication.published_url` via `FileSystemPublicationRepository`. NOT stored inside `content_metrics`. |
| All numeric keys | Merged into `ContentPerformanceMetrics` model |
| Successful import | MetricSnapshot transitions DRAFT → RECORDED |

### Snapshot status validation:

| Check | Rule |
|---|---|
| Snapshot must be DRAFT | `record_metrics()` validates `snapshot.status == MetricSnapshotStatus.DRAFT` before allowing import |
| Cannot record twice | RECORDED snapshot rejects `record_metrics()` with `AnalyticsValidationError` |

---

# 11. Configuration Validation Tests

## 11.1. Current Config Validation Coverage

Tests verify the following configuration validation behaviours:

| Validation | Test File | What Is Verified |
|---|---|---|
| Required project fields | `test_projects.py:test_required_project_fields_are_validated` | Missing `project_slug` raises `ProjectConfigValidationError` |
| Invalid project status | Not directly tested as a standalone case | Validated by `_parse_project_status()` in ProjectService |
| Required brand fields | `test_projects.py:test_required_brand_profile_fields_are_validated` | Empty `brand.positioning` raises `ProjectConfigValidationError` |
| Invalid project ID | `test_projects.py:test_invalid_project_id_is_rejected` | `../example`, empty, uppercase, spaces → `InvalidProjectIdError` |
| Alias normalization | Implicitly tested | Tests use legacy keys (`project_id`, `project_name`, `project_slug`, `default_language`) which are normalized |
| Project root isolation | All service tests | Tests use `tempfile.TemporaryDirectory()` with explicit `projects_root` |
| Env var overrides | `test_find_metric_snapshots.py:test_respects_content_plant_projects_root_override` | `CONTENT_PLANT_PROJECTS_ROOT` env var overrides script behaviour |
| Brand profile construction | `test_projects.py:test_brand_profile_can_be_built_from_project_config` | Name, status, brand_values, tone_of_voice correctly derived from config |

## 11.2. Config Validation Layers in Tests

```text
Layer 1: Filesystem — FileSystemProjectRepository, load_project()
    → Tested: test_project_can_be_loaded_from_example_project_config
    → Tested: test_missing_project_raises_clear_error

Layer 2: Deserialization — ProjectConfig.model_validate(), aliases
    → Implicitly tested via successful project loading

Layer 3: Service validation — ProjectService._validate_required_fields()
    → Tested: test_required_project_fields_are_validated
    → Tested: test_required_brand_profile_fields_are_validated

Layer 4: Input validation — validate_project_id()
    → Tested: test_invalid_project_id_is_rejected
```

---

# 12. Storage Validation in Tests

## 12.1. Test Isolation Model

All service tests use `tempfile.TemporaryDirectory()` for storage isolation:

```python
class LoopEngineeringFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._write_project_fixture("example")
        # ... construct services with self.projects_root

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
```

## 12.2. Storage Isolation Rules Verified by Tests

| Rule | How Tests Verify |
|---|---|
| Temporary project roots | `tempfile.TemporaryDirectory()` used in all service test setUp methods |
| Entity JSON written under temp dirs | All entity operations write to `{temp_dir}/data/` |
| No source project pollution | Source `projects/example/project.yaml` is read (template), never written |
| No `storage/smoke_projects/` pollution | Smoke loop test uses temp dir for `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` |
| Cleanup after test | `tearDown` calls `temp_dir.cleanup()` |
| No cross-project writes | Tests create two projects ("example" and "second") and verify scoping |

## 12.3. Tie to STORAGE_AND_STATE_SPEC.md

The storage isolation model in tests directly implements the rules from
`docs/05_platform/STORAGE_AND_STATE_SPEC.md`:

- **Section 4.3 — Boundary Rule:** Tests copy source config as a fixture template
  (read-only), never modify canonical `project.yaml`.
- **Section 7.2 — Programmatic Control:** Tests use `projects_root` parameter in
  factory functions to point to temp directories.
- **Section 16 — Git Hygiene:** Tests write only to temp directories that are
  cleaned up. No runtime artifacts are committed.
- **Section 23 — Multi-Project Isolation:** `test_create_idea_persists_project_
  scoped_records` verifies cross-project isolation.
- **Section 25 — Current MVP Storage Flow:** All entity writes go through
  repositories → services, not direct filesystem writes.

---

# 13. Test Isolation Rules

All current tests follow these isolation rules:

1. **Use `tempfile.TemporaryDirectory()`.** Every service test creates a
   temporary directory in `setUp()` and destroys it in `tearDown()`.

2. **Do not write to source `projects/`.** Source project config is read as a
   template for fixture generation. Tests that validate source files are
   read-only (`test_task_2_files_do_not_contain...`,
   `test_task_3_files_do_not_contain...`).

3. **Do not write to `storage/smoke_projects/`.** Smoke loop tests override
   `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` to point to a temp directory.

4. **Do not rely on global storage.** Every repository and service receives an
   explicit `projects_root`. No test uses the default `PROJECTS_ROOT` constant
   for write operations.

5. **Clean up after tests.** `tearDown` calls `temp_dir.cleanup()`. Nothing
   persists between test runs.

6. **No external network.** No test makes HTTP requests, API calls, or external
   connections.

7. **Deterministic inputs.** Tests use hardcoded strings, fixed UUIDs in
   assertions (pattern matching only), and explicit project fixtures.

8. **Subprocess tests use isolated env vars.** Tests that run scripts as
   subprocesses set `CONTENT_PLANT_PROJECTS_ROOT` and
   `CONTENT_PLANT_SMOKE_PROJECTS_ROOT` in a copy of `os.environ`.

---

# 14. Test Data / Fixtures

## 14.1. Current Fixture Model

### Project Config Fixture

The primary fixture is `_write_project_fixture()` (appears in multiple test
files):

```python
def _write_project_fixture(self, project_id: str, *, project_name=None):
    payload = json.loads(Path("projects/example/project.yaml").read_text("utf-8"))
    payload["project_id"] = project_id
    payload["project_name"] = project_name or f"{project_id.title()} Project"
    payload["project_slug"] = f"{project_id}_project"
    payload["brand"]["brand_name"] = f"{project_id.title()} Brand"
    project_dir = self.projects_root / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "project.yaml").write_text(json.dumps(payload), encoding="utf-8")
```

**Characteristics:**
- Reads the canonical `projects/example/project.yaml` as a template.
- Replaces identity fields (`project_id`, `project_name`, `project_slug`,
  `brand.brand_name`) to create isolated project configs.
- The template is project-agnostic — no project-specific values are hardcoded
  in test logic.
- Supports generating multiple project configs ("example", "second",
  "override_example") from the same template.

### Export Package Manifest Fixture

```python
def _build_manifest(**overrides):
    manifest = {
        "package_id": "export_001",
        "project_id": "example",
        "content_item_id": "content_001",
        ...
        "files": [...]
    }
    manifest.update(overrides)
    return manifest
```

Used in `test_inspect_package.py` and `test_validate_package.py` to create
valid-or-invalid manifest dicts for testing specific error conditions.

### Manual Metrics JSON Fixture

Tests construct JSON payloads inline:

```python
payload_path = self._write_json({
    "project_id": "example",
    "metric_snapshot_id": metric_snapshot_id,
    "metrics": {"views": 100, "likes": 12, ...}
})
```

### Pre-built Lifecycle Fixtures

`LoopEngineeringFixture` provides helper methods that create entities up to
specific lifecycle stages:

- `create_approved_scenario()` — Idea → Scenario (APPROVED)
- `create_approved_content_item()` — Scenario → ContentItem (APPROVED)
- `create_ready_export_package()` — ContentItem → ExportPackage (READY)
- `create_published_publication()` — ExportPackage → Publication (PUBLISHED)

These are used by multiple test classes to set up prerequisites without
duplicating setup code.

## 14.2. What Is NOT Present

- No recorded/golden fixture files (no `tests/fixtures/` directory).
- No NURA project used as a test fixture.
- No snapshot-based or VCR-style recorded responses.
- No seeded random data — all test data is deterministic and explicit.

---

# 15. Validation Layers

LOOPRA uses a layered validation model. Each layer validates a different
aspect of correctness.

| Layer | Owner | Current Tools/Tests | Future Direction |
|---|---|---|---|
| **1. Domain validation** | `core/domain/models.py`, `transitions.py` | `test_models.py`, `test_transitions.py` | Additional entity rules; pydantic validators extension |
| **2. Service precondition validation** | Service classes (`projects.py`, `ideas.py`, `production.py`, `publishing.py`, `analytics.py`) | `test_projects.py`, `test_ideas.py`, `test_loop_engineering.py` | Structured pre/post-condition specification; formal contract testing |
| **3. Runtime sequence validation** | `LoopOrchestrator` | `test_loop_engineering.py` (LoopOrchestratorTests) | Mid-flow resume testing; partial execution; retry validation |
| **4. Artifact validation** | `inspect_package.py`, `validate_package.py` | `test_inspect_package.py`, `test_validate_package.py` | Brand compliance checks; platform-specific preflight; media validation |
| **5. CLI input validation** | Script main() functions | All script test files | `--help` output; differentiated exit codes; `--json` output mode |
| **6. Manual workflow validation** | Smoke loop + find + import scripts | `test_manual_metrics_workflow.py` | Multi-project workflows; partial workflow resume |
| **7. Future: Integration validation** | Future connector tests | Not implemented | Mocked external APIs; platform connector contract tests; DB repository tests |
| **8. Future: Agent safety validation** | Agent boundary tests | Not implemented | Storage mutation prevention; service bypass prevention; cross-project access prevention; approval gate enforcement |

---

# 16. Error Testing

## 16.1. Current Error Coverage

The test suite covers these error conditions explicitly:

| Error Condition | Test File | Assertion |
|---|---|---|
| Invalid project config (missing slug) | `test_projects.py` | `assertRaises(ProjectConfigValidationError)` |
| Missing brand fields (empty positioning) | `test_projects.py` | `assertRaises(ProjectConfigValidationError)` |
| Invalid project_id (path traversal, empty, uppercase) | `test_projects.py` | `assertRaises(InvalidProjectIdError)` |
| Missing project | `test_projects.py` | `assertRaises(FileNotFoundError)` |
| Invalid funnel_stage | `test_ideas.py` | `assertRaises(IdeaBankValidationError)` |
| RAW Idea cannot generate scenario | `test_ideas.py` | `assertRaises(ScenarioStudioValidationError)` |
| Invalid content approval transition | `test_loop_engineering.py` | `assertRaises(InvalidStatusTransitionError)` |
| Empty published_url | `test_loop_engineering.py` | `assertRaises(PublishingValidationError)` |
| Publication before export ready | `test_loop_engineering.py` | `assertRaises(PublishingValidationError)` |
| Invalid publication transition (published → failed) | `test_loop_engineering.py` | `assertRaises(InvalidStatusTransitionError)` |
| Recording metrics twice | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Empty metrics dict | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Unknown metric keys | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Unsupported metric keys ("follows") | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Negative numeric metrics | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Non-integer numeric metrics | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Empty published_url in metrics | `test_loop_engineering.py` | `assertRaises(AnalyticsValidationError)` |
| Missing CLI argument | All script tests | `assertNotEqual(returncode, 0)` + stderr message |
| Missing directory/file | All script tests | `assertNotEqual(returncode, 0)` + stderr message |
| Invalid JSON (manifest, metadata, metrics) | Script tests | `assertNotEqual(returncode, 0)` + stderr message |
| Missing required manifest fields | Script tests | `assertNotEqual(returncode, 0)` + stderr message |
| Absolute paths in manifest | Script tests | `assertNotEqual(returncode, 0)` + stderr message |
| File missing on disk (manifest mismatch) | `test_validate_package.py` | `assertNotEqual(returncode, 0)` + stderr message |
| `manual_publication_only` not true | `test_validate_package.py` | `assertNotEqual(returncode, 0)` + stderr message |
| Status not "ready" | `test_validate_package.py` | `assertNotEqual(returncode, 0)` + stderr message |
| Corrupted snapshot JSON | `test_find_metric_snapshots.py` | `assertEqual(returncode, 1)` + stderr message |
| Missing snapshot fields | `test_find_metric_snapshots.py` | `assertEqual(returncode, 1)` + stderr message |
| Unknown project in metrics import | `test_import_manual_metrics.py` | `assertEqual(returncode, 1)` + stderr message |
| Unknown snapshot in metrics import | `test_import_manual_metrics.py` | `assertEqual(returncode, 1)` + stderr message |
| Deleted publication in metrics import | `test_import_manual_metrics.py` | `assertEqual(returncode, 1)` + stderr message |

## 16.2. Known Limitations

- **No differentiated exit code testing.** All script errors use exit code 1.
  Tests do not distinguish between "invalid input", "file not found",
  "validation failure" and "service error" at the exit code level.
- **No error boundary testing for all edge cases.** Not every possible
  combination of invalid states is tested.
- **No concurrent access error testing.** The current filesystem model does
  not protect against concurrent writes, and this is not tested.
- **Error message format is not contract-tested.** Tests check for substring
  presence in stderr, not for a structured error format.

---

# 17. Operational Acceptance Tests

## 17.1. Definition

Operational Acceptance is the set of verifications that prove the LOOPRA
Foundation MVP is operationally sound — that the system, as a whole, works
correctly end-to-end.

## 17.2. Current Operational Acceptance Steps

The current operational acceptance can be performed by executing:

```text
1. Run domain tests:
   python -m unittest tests.domain.test_models
   python -m unittest tests.domain.test_transitions

2. Run service tests:
   python -m unittest tests.services.test_projects
   python -m unittest tests.services.test_ideas
   python -m unittest tests.services.test_loop_engineering

3. Run smoke loop test (subprocess):
   python -m unittest tests.services.test_smoke_loop

4. Run CLI tool tests:
   python -m unittest tests.services.test_inspect_package
   python -m unittest tests.services.test_validate_package
   python -m unittest tests.services.test_find_metric_snapshots
   python -m unittest tests.services.test_import_manual_metrics

5. Run manual metrics workflow test:
   python -m unittest tests.services.test_manual_metrics_workflow

6. Run smoke loop directly (manual verification):
   python scripts/smoke_loop.py

7. Inspect export package:
   python scripts/inspect_package.py <export_directory_from_smoke_loop>

8. Validate export package:
   python scripts/validate_package.py <export_directory_from_smoke_loop>

9. Import manual metrics:
   python scripts/find_metric_snapshots.py example
   python scripts/import_manual_metrics.py <metrics.json>

10. Confirm no source changes except intended docs/code:
    git status
```

## 17.3. Smoke Loop as Operational Proof

The smoke loop (`python scripts/smoke_loop.py`) is the primary operational
acceptance test. It proves:

- Project config loads correctly.
- Idea is created and approved.
- Scenario is generated and approved.
- ContentItem is produced, QA'd, and approved.
- ExportPackage is created and prepared (all 6 files written).
- Publication record is created and published.
- MetricSnapshot is created as DRAFT.
- All entities are in valid terminal states.

If the smoke loop completes with exit code 0, the Foundation MVP lifecycle is
operationally verified.

## 17.4. Tie to STATE.md

STATE.md declares:

```text
Foundation MVP — Status: READY
The foundation layer is operationally verified.
Validated lifecycle: Idea → Scenario → ContentItem → ExportPackage →
Publication → MetricSnapshot
```

The operational acceptance tests described in this section are the verification
mechanism that supports the READY status declaration.

---

# 18. Regression Testing Rules

## 18.1. When Tests Must Be Run

Per AGENTS.md Section 7 (Code Quality Rules):

```text
After changes:
- run tests;
- verify scope;
- update documentation when architecture changes.
```

Concrete rules:

| Change Type | Must Run |
|---|---|
| Domain model changes (`core/domain/models.py`, `enums.py`) | All domain tests + all service tests |
| Transition rule changes (`core/domain/transitions.py`) | All domain transitions tests + service tests that exercise transitions |
| Service contract changes (`core/services/*.py`) | All service tests + smoke loop test |
| Repository/storage changes | All service tests |
| Runtime orchestration changes (`core/services/loop.py`) | LoopOrchestrator tests + smoke loop test |
| CLI tool changes (`scripts/*.py`) | Corresponding script test + smoke workflow test if affected |
| Config/loader changes (`core/projects/loader.py`) | Project tests + all service tests |
| Doc-only changes | Tests optional — unless docs reference generated line numbers or code paths |
| New entity addition | Domain tests for new entity + transition tests + service tests |

## 18.2. Mandatory Regression Chain

Any change that affects the Foundation MVP chain must preserve:

```text
Project → Idea → Scenario → ContentItem → ExportPackage → Publication →
MetricSnapshot
```

The definitive regression test is:

```bash
python -m unittest tests.services.test_loop_engineering.LoopOrchestratorTests.test_runs_minimal_end_to_end_loop_for_generic_project
```

If this test passes, the lifecycle chain is intact. If it fails, the chain is
broken.

---

# 19. Documentation Validation

## 19.1. Current State

Documentation validation is **conceptual** — there is no automated doc validation
in the current MVP.

## 19.2. Manual Documentation Checks

| Check | Current Status |
|---|---|
| Docs match code | Manual review |
| Path references valid | Manual review |
| No stale folder names (`docs/05_runtime/`) | Manual review |
| Document status/version present | Enforced by convention |
| Docs do not claim implemented features that are future | Manual review |
| Architecture source of truth consistent | Manual review per AGENTS.md |

## 19.3. Future Documentation Validation (Conceptual)

| Capability | Description | Status |
|---|---|---|
| Documentation index validator | Verify all referenced docs exist and have correct status | Future |
| Link checker | Validate internal cross-references between docs | Future |
| Spec/code consistency checks | Automated comparison of documented service contracts vs actual code signatures | Future |
| Changelog consistency | Verify change descriptions match actual diff | Future |

---

# 20. Test Commands

## 20.1. Current Test Commands

All tests use Python's built-in `unittest` framework. There is no `pytest`,
`tox`, or `nox` configured at the repository root.

### Run all domain tests:

```bash
python -m unittest discover -s tests/domain
```

### Run all service tests:

```bash
python -m unittest discover -s tests/services
```

### Run all tests:

```bash
python -m unittest discover -s tests
```

### Run a specific test file:

```bash
python -m unittest tests.domain.test_models
python -m unittest tests.services.test_loop_engineering
```

### Run a specific test case:

```bash
python -m unittest tests.services.test_loop_engineering.LoopOrchestratorTests.test_runs_minimal_end_to_end_loop_for_generic_project
```

## 20.2. Script Commands (Operational Verification)

```bash
python scripts/smoke_loop.py
python scripts/inspect_package.py <export_package_directory>
python scripts/validate_package.py <export_package_directory>
python scripts/find_metric_snapshots.py <project_id>
python scripts/import_manual_metrics.py <manual_metrics_json>
```

## 20.3. Recommended Verification Sequence

```bash
# 1. Run all tests
python -m unittest discover -s tests

# 2. Run smoke loop
python scripts/smoke_loop.py

# 3. Inspect the export package (use export_directory from step 2)
python scripts/inspect_package.py <export_directory>

# 4. Validate the export package
python scripts/validate_package.py <export_directory>

# 5. Find metric snapshots
python scripts/find_metric_snapshots.py example

# 6. Import manual metrics (create metrics.json with correct snapshot_id)
python scripts/import_manual_metrics.py metrics.json
```

---

# 21. Current Coverage Boundaries

## 21.1. Covered

| Area | Coverage | Verification |
|---|---|---|
| Domain model creation | All entities instantiated with valid fields | `test_models.py` |
| Domain model field requirements | `project_id` required for project-scoped entities | `test_models.py` |
| Domain model owner modules | PUBLISHING_HUB for ExportPackage, PRODUCTION_ENGINE rejected | `test_models.py` |
| Status transitions | All entity types: valid transitions pass, invalid transitions fail | `test_transitions.py` |
| Project config loading | Example project loads, missing project raises error | `test_projects.py` |
| Project ID validation | Invalid IDs rejected; path traversal protected | `test_projects.py` |
| Brand profile construction | Brand fields derived from config; required fields validated | `test_projects.py` |
| Idea lifecycle | Create, approve, reject, archive; invalid funnel_stage rejected | `test_ideas.py` |
| Scenario lifecycle | Create from idea, submit, approve, reject, archive; RAW idea blocked | `test_ideas.py` |
| ContentItem lifecycle | Create, QA, approve; wrong transition rejected | `test_loop_engineering.py` |
| ExportPackage lifecycle | Create, prepare; all 6 files written; caption fallbacks | `test_loop_engineering.py` |
| Publication lifecycle | Create, publish, fail; empty URL rejected; wrong transition rejected | `test_loop_engineering.py` |
| MetricSnapshot lifecycle | Create, record; double-record rejected; invalid keys/values rejected | `test_loop_engineering.py` |
| LoopOrchestrator | Full lifecycle execution; project-agnostic; scenario approval enforced | `test_loop_engineering.py` |
| Smoke loop subprocess | Exit 0; correct statuses; all export files generated | `test_smoke_loop.py` |
| inspect_package.py | Valid manifest; all error conditions (missing args, dir, manifest, JSON, fields, absolute paths) | `test_inspect_package.py` |
| validate_package.py | Valid package; all error conditions (16 test cases) | `test_validate_package.py` |
| find_metric_snapshots.py | Draft listing; empty listing; error conditions; env var override; DRAFT-only filter | `test_find_metric_snapshots.py` |
| import_manual_metrics.py | Valid import; all error conditions; clicks→link_clicks; published_url→Publication; BOM handling | `test_import_manual_metrics.py` |
| Manual metrics workflow | Full smoke→find→import chain as subprocesses | `test_manual_metrics_workflow.py` |
| Project agnosticism | No project-specific branching markers in core files | `test_projects.py`, `test_ideas.py`, script tests |
| Test isolation | All tests use temp directories | Throughout |
| Storage scoping | Cross-project isolation verified | `test_ideas.py`, `test_loop_engineering.py` |

## 21.2. Not Covered

| Area | Status |
|---|---|
| API endpoint tests | No API exists |
| UI tests | No UI exists |
| Database tests | No DB exists |
| External connector tests | No connectors exist |
| Real publishing tests | Manual publication only |
| Real analytics API tests | Manual metrics only |
| Media rendering tests | Not implemented |
| Asset library tests | Not implemented |
| Learning memory tests | Not implemented (stubs only) |
| Queue/worker tests | Not implemented |
| Concurrent access tests | Not implemented |
| Performance/load tests | Not implemented |
| Security/penetration tests | Not implemented |
| Migration tests | No DB migrations exist |
| Cross-platform export tests | Single platform per export in MVP |
| Multi-format content tests | Only `text_social_post` supported in MVP |
| Autonomy mode tests | Copilot-only in MVP; other modes are future |
| Agent behaviour tests | No agents exist in MVP |
| CI pipeline tests | No CI exists |

---

# 22. Future Test Categories

These test categories are architectural direction. They are NOT implemented in
the current Foundation MVP.

| Category | Description | Status |
|---|---|---|
| AssetLibraryService tests | Asset CRUD, licensing checks, quality assessment, brand fit validation | Future |
| ProductionPipelineService tests | Production Brief validation, variant selection, assembly verification | Future |
| Media render tests | Video rendering, image generation, audio synthesis output validation | Future |
| Distribution preflight tests | Platform-specific constraints: character limits, aspect ratios, hashtag counts, UTM presence | Future |
| Connector mock tests | Mocked platform API interactions: auth, media upload, caption submission, response parsing | Future |
| Analytics connector tests | Mocked metric collection from platform APIs: scheduling, normalization, error handling | Future |
| Learning memory tests | Pattern extraction, knowledge storage, retrieval accuracy, confidence scoring | Future |
| Runtime command tests | Individual lifecycle stage execution: create-scenario-only, run-qa-only, prepare-export-only | Future |
| Approval gate tests | Approval creation, rejection, expiry, mode-based gating (copilot/assisted/autopilot) | Future |
| Agent boundary tests | Agent safety constraints: storage access prevention, service bypass prevention, cross-project access prevention | Future |
| DB repository tests | PostgreSQL-backed repositories: CRUD operations, transactions, concurrent access, migration tests | Future |
| Object storage tests | S3-compatible export package storage: upload, download, versioning, retention | Future |
| Migration tests | Data migration from filesystem to DB; schema migration integrity | Future |
| API endpoint tests | HTTP API: request validation, authentication, response contracts, error handling | Future |
| UI component tests | Frontend component rendering, user interaction, state management | Future |
| Scheduled job tests | Scheduled publication, periodic metric collection, maintenance jobs | Future |
| Multi-project workflow tests | Cross-project analytics comparison, workspace-level operations | Future |
| Performance/load tests | Smoke loop throughput, export package generation speed, DB query performance | Future |
| Security tests | Authentication bypass, path traversal, secret leakage, input injection | Future |
| Documentation consistency tests | Spec/code contract verification, link validation, changelog accuracy | Future |

---

# 23. Future Agent Safety Tests

When autonomous agents are introduced, these safety boundaries must be tested.
All marked as future/conceptual.

| Safety Boundary | Test Description | Status |
|---|---|---|
| Agent cannot mutate storage directly | Agent tool calls must route through services; direct filesystem write attempts must fail or be blocked | Future |
| Agent cannot bypass service contracts | Agent must use `IdeaService`, `PublishingService`, etc.; creating domain entities directly must be prevented | Future |
| Agent cannot publish without approval | In copilot mode, `publish_content()` must require explicit human approval gate | Future |
| Agent cannot access cross-project data | Agent context must be project-scoped; loading another project's entities must be blocked or flagged | Future |
| Agent tool calls are auditable | Every tool invocation by an agent must be recorded with agent identity, exact inputs, timestamp, and result | Future |
| Autonomy mode gates respected | In copilot mode: all gates active. In assisted mode: routine gates auto-approved, strategic gates active. Autopilot must have emergency stop | Future |
| Emergency stop respected | Emergency stop signal must halt all agent-initiated actions; partial executions must leave entities in valid states | Future |
| Agent cannot modify project config silently | Config changes must require explicit human approval; no silent `project.yaml` edits | Future |
| Agent cannot access secrets | Agent prompts must not contain raw credential values; agent must not be able to read secret store | Future |
| Agent decision logs are preserved | Every agent decision (create content, change strategy, launch experiment) must be recorded for audit and Learning Memory | Future |

---

# 24. Future CI / Quality Gates

There is **no CI pipeline** in the current Foundation MVP. This section describes
conceptual future CI gates.

```text
Conceptual future CI stages:

Stage 1 — Test:
    - Run all domain tests
    - Run all service tests
    - Run all CLI script tests
    - Run smoke loop as subprocess test
    - Fail if any test fails

Stage 2 — Validate:
    - Run smoke_loop.py
    - Run inspect_package.py on generated export
    - Run validate_package.py on generated export
    - Run find_metric_snapshots.py
    - Run import_manual_metrics.py with fixture metrics

Stage 3 — Lint / Format:
    - Run code formatter (black, ruff format) — check mode
    - Run linter (ruff, pylint) — zero errors
    - Run type checker (mypy, pyright) if adopted

Stage 4 — Docs:
    - Validate documentation cross-references
    - Check for broken internal links
    - Verify spec/code consistency (service contracts)

Stage 5 — Artifact Hygiene:
    - Enforce no generated artifacts committed (storage/*, graphify-out/)
    - Enforce no secrets committed (secret scanning)
    - Enforce no project-specific values in core/

Stage 6 — Integration (future):
    - Run mocked connector tests
    - Run DB repository tests
    - Run agent boundary tests
```

**Current state:** None of these CI stages exist. CI implementation requires a
separate specification and infrastructure setup.

---

# 25. Testing and Foundation MVP Compatibility

## 25.1. Foundation MVP Chain Preservation

Tests must preserve the Foundation MVP entity chain:

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

Any change that breaks this chain must cause at least one test to fail or
require explicit migration with updated tests.

## 25.2. Chain-Specific Tests

| Chain Step | Primary Test |
|---|---|
| Project → Idea | `test_ideas.py:test_create_idea_persists_project_scoped_records` |
| Idea → Scenario | `test_ideas.py:test_approved_idea_can_generate_text_social_post_scenario` |
| Scenario → ContentItem | `test_loop_engineering.py:test_creates_content_item_from_approved_scenario` |
| ContentItem → ExportPackage | `test_loop_engineering.py:test_creates_and_prepares_export_package` |
| ExportPackage → Publication | `test_loop_engineering.py:test_creates_manual_publication_and_marks_it_published` |
| Publication → MetricSnapshot | `test_loop_engineering.py:test_creates_metric_snapshot_and_records_metrics` |
| Full chain | `test_loop_engineering.py:test_runs_minimal_end_to_end_loop_for_generic_project` |
| Full chain (subprocess) | `test_smoke_loop.py:test_script_runs_end_to_end_for_generic_example_project` |
| Full chain + metrics workflow | `test_manual_metrics_workflow.py:test_smoke_workflow_records_manual_metrics_for_draft_snapshot` |

## 25.3. Regression Guard

The `test_runs_minimal_end_to_end_loop_for_generic_project` test is the
definitive regression guard. It exercises every service and every transition in
the Foundation MVP chain. A failure in this test means the chain is broken.

Additionally, the `test_smoke_loop.py` test guards against regressions in the
CLI entrypoint and the end-to-end operational flow.

---

# 26. Testing Extension Path

Staged evolution of testing capabilities. All stages beyond Stage 1 are marked
as future/conceptual.

| Stage | Description | Status |
|---|---|---|
| **Stage 1** | Current domain/service/CLI tests with `unittest` and temp dir isolation | **Current** |
| **Stage 2** | Standardized CLI subprocess tests with differentiated exit codes and `--json` output mode | Future |
| **Stage 3** | Runtime command tests — individual lifecycle stage execution, mid-flow resume, retry validation | Future |
| **Stage 4** | Documentation consistency checks — automated spec/code contract verification, link validation | Future |
| **Stage 5** | Integration tests for future services — AssetLibraryService, ProductionPipelineService, distribution preflight | Future |
| **Stage 6** | Mocked connector tests — platform API mocks for publishing and analytics connectors | Future |
| **Stage 7** | DB repository tests — PostgreSQL-backed repositories with transactional tests | Future |
| **Stage 8** | Agent safety tests — boundary enforcement, audit trail, autonomy mode gates, emergency stop | Future |
| **Stage 9** | CI quality gates — automated test suite, lint, docs validation, artifact hygiene, secret scanning | Future |

Each stage must be validated before the next begins. The Foundation MVP must
remain operational through all stages.

---

# 27. Testing Readiness Criteria

The Testing and Validation architecture is ready when:

- [x] Current test inventory documented — Section 4
- [x] Domain tests documented — Section 5
- [x] Service tests documented — Section 6
- [x] Runtime/smoke tests documented — Section 7
- [x] CLI tool tests documented — Section 8
- [x] Export package validation documented — Section 9
- [x] Manual metrics validation documented — Section 10
- [x] Configuration validation documented — Section 11
- [x] Storage validation documented — Section 12
- [x] Test isolation rules documented — Section 13
- [x] Test data / fixtures documented — Section 14
- [x] Validation layers documented — Section 15
- [x] Error testing documented — Section 16
- [x] Operational acceptance documented — Section 17
- [x] Regression rules documented — Section 18
- [x] Future test categories marked future — Sections 22, 23
- [x] Future CI gates marked future — Section 24
- [x] Foundation MVP compatibility preserved — Section 25
- [x] Testing extension path defined — Section 26

---

# 28. Related Documents

```text
AGENTS.md                                              — Development rules and code quality requirements
STATE.md                                               — Current project state and Foundation MVP status
docs/00_foundation/DATA_MODEL.md                       — Foundation data model and entity chain
docs/00_foundation/PROJECT_SETTINGS_SPEC.md            — Project configuration specification
docs/02_architecture/PIPELINES_SPEC.md                 — Foundation MVP pipeline and helper-supported workflow
docs/04_production/PRODUCTION_PIPELINE_SPEC.md         — Production pipeline specification (future production details)
docs/04_production/DISTRIBUTION_SPEC.md                — Distribution specification (future publication boundary)
docs/04_production/ANALYTICS_SPEC.md                   — Analytics specification (future analytics boundary)
docs/05_platform/RUNTIME_ORCHESTRATION_SPEC.md         — Runtime orchestration — how runtime executes the lifecycle
docs/05_platform/SERVICE_CONTRACTS_SPEC.md             — Service contracts — which operations services expose
docs/05_platform/TOOLING_AND_CLI_SPEC.md               — Tooling and CLI — which tools exist and their contracts
docs/05_platform/STORAGE_AND_STATE_SPEC.md             — Storage and state — where artifacts live and how they persist
docs/05_platform/CONFIGURATION_AND_ENVIRONMENT_SPEC.md — Configuration — how config is loaded and validated
```

---

# 29. Code References

```text
tests/domain/test_models.py                    — Domain entity creation, field requirements, owner module validation
tests/domain/test_transitions.py               — Status transition rules for all entity types
tests/services/test_projects.py                — ProjectService, BrandProfileService, config validation
tests/services/test_ideas.py                   — IdeaService, ScenarioService lifecycle
tests/services/test_loop_engineering.py        — Production, Publishing, Analytics services + LoopOrchestrator
tests/services/test_smoke_loop.py              — smoke_loop.py subprocess end-to-end test
tests/services/test_inspect_package.py         — inspect_package.py manifest reading and error handling
tests/services/test_validate_package.py        — validate_package.py structural validation
tests/services/test_find_metric_snapshots.py   — find_metric_snapshots.py DRAFT snapshot discovery
tests/services/test_import_manual_metrics.py   — import_manual_metrics.py JSON import and validation
tests/services/test_manual_metrics_workflow.py — End-to-end manual metrics workflow
scripts/smoke_loop.py                          — End-to-end Foundation MVP lifecycle smoke test
scripts/inspect_package.py                     — Export package manifest inspection
scripts/validate_package.py                    — Export package structural validation
scripts/find_metric_snapshots.py               — Metric snapshot discovery tool
scripts/import_manual_metrics.py               — Manual metric import tool
core/domain/models.py                          — Domain entities (Project, Idea, Scenario, ContentItem, etc.)
core/domain/enums.py                           — Domain enums and statuses
core/domain/transitions.py                     — Domain transition rules
core/services/projects.py                      — ProjectService, BrandProfileService
core/services/ideas.py                         — IdeaService, ScenarioService
core/services/production.py                    — ProductionLifecycleService
core/services/publishing.py                    — PublishingService
core/services/analytics.py                     — AnalyticsService
core/services/loop.py                          — LoopOrchestrator
core/services/_storage.py                      — Base repository class
core/projects/loader.py                        — Project config loader and validation
```

---

# 30. Document Status

| Field | Value |
|---|---|
| Status | Active — LOOPRA Platform Layer |
| Version | v1.0 |
| Date | 2026-07-09 |
| Project | LOOPRA — Autonomous Marketing Operating System |
| Layer | Platform Layer — Testing and Validation |

---

# Final Statement

The Testing and Validation Layer is the verification substrate of LOOPRA. It
proves that domain models enforce their rules, service contracts are honoured,
runtime orchestration executes correctly, CLI tools behave deterministically,
export packages are structurally valid, and manual metrics workflows work
end-to-end.

In the current Foundation MVP, testing covers:

- **2 domain test files** — entity creation, field requirements, status transitions.
- **10 service/script test files** — every service operation, every CLI tool,
  every error condition, end-to-end smoke loop, manual metrics workflow.
- **Project agnosticism** — core code verified free of project-specific
  branching markers.
- **Storage isolation** — all tests use `tempfile.TemporaryDirectory()`, no
  source pollution.

Testing follows the Foundation First principle: tests start from domain models
and build outward through services, runtime, and CLI entrypoints. Tests verify
behaviour — they do not define strategy. Tools validate artifacts — they do not
make decisions.

Future testing evolution — CI quality gates, agent safety tests, connector mock
tests, DB repository tests — will extend this layer while preserving the
Foundation MVP compatibility. Every future test category builds on the current
foundation, never replaces it.

Tests verify. Validation checks. Architecture specifications define the source
of truth. Together, they ensure LOOPRA remains a reliable, project-agnostic
Autonomous Marketing Operating System.

# LOOPRA Documentation Update Requirements

Status: Pending review  
Created: 2026-07-08  
Purpose: Tracks 5 archive documents that contain valuable architecture/design content but need LOOPRA adaptation before reactivation.

Documents remain in `docs/archive/content-plant-era/` until updated.

---

| # | Document | Required Changes |
|---|---|---|
| 1 | `SYSTEM_ARCHITECTURE.md` | **Old Content Plant parts:** Title, section 1 description, architectural principle references "Content Plant". Has `Legacy / future-scope note` warning about future modules. Contains detailed Web UI, Backend API, Application Services, Database, Workers, Render sections that describe future SaaS scope not in current foundation.<br><br>**Replace with LOOPRA:** Rename all "Content Plant" → "LOOPRA". Update title header description to "Autonomous Marketing Operating System". Replace legacy note with current foundation scope note.<br><br>**New concepts to add:**<br>- Orchestrator Agent: autonomous agent layer for marketing operations<br>- Growth Loop: the LOOPRA autonomous marketing loop concept<br>- Brand System: brand profile as core architectural boundary<br>- Autonomous Marketing OS positioning<br><br>**Action:** Major rewrite. Remove future UI/API/database sections. Separate current foundation from future scope. Align module descriptions with implemented services. |
| 2 | `BRAND_SYSTEM_SPEC.md` | **Old Content Plant parts:** Title, section 1 references "Content Plant". Has `Legacy / future-scope note`. References old docs paths (`docs/00_index.md`, `docs/MVP_SCOPE.md`, etc.).<br><br>**Replace with LOOPRA:** Rename all "Content Plant" → "LOOPRA". Remove legacy note. Update document references to new `docs/` structure.<br><br>**New concepts to add:**<br>- Brand System as LOOPRA core architectural concept<br>- Brand Profile as boundary for Growth Loop decisions<br>- How Brand Profile feeds into Orchestrator Agent decisions<br><br>**Action:** Medium rewrite. Brand Profile concept IS core to LOOPRA. Document describes valid universal structure. Needs LOOPRA terminology update and alignment with current `project.yaml` config structure. |
| 3 | `PRODUCT_STRATEGY.md` | **Old Content Plant parts:** Title, section 2 "Content Plant строится как internal-first...". Product strategy describes Content Plant positioning, not LOOPRA's Autonomous Marketing OS.<br><br>**Replace with LOOPRA:** Rebrand strategy from "Content Plant — internal-first, multi-project foundation" to "LOOPRA — Autonomous Marketing Operating System". Update product positioning to reflect autonomous marketing operations.<br><br>**New concepts to add:**<br>- LOOPRA as Autonomous Marketing OS<br>- Growth Loop as core product strategy<br>- Orchestrator Agent as product differentiator<br>- Evolution from foundation MVP toward autonomous operations<br><br>**Action:** Medium rewrite. Valuable strategic thinking but needs complete rebranding and alignment with LOOPRA's "Autonomous Marketing OS" positioning. |
| 4 | `USER_WORKFLOWS.md` | **Old Content Plant parts:** Title, section 1 references "Content Plant". References `CONTENT_PLANT_PROJECTS_ROOT` env var. References old `docs/` paths.<br><br>**Replace with LOOPRA:** Rename all "Content Plant" → "LOOPRA". Update env var to `LOOPRA_PROJECTS_ROOT`. Update doc references to new `docs/` structure.<br><br>**New concepts to add:**<br>- Orchestrator Agent role in workflow<br>- Growth Loop feedback cycle<br><br>**Action:** Light rewrite. Active workflow doc describing current 10-step manual loop. Close to MOVE_TO_ACTIVE but benefits from LOOPRA-aligned rewrite to avoid confusion. |
| 5 | `PROJECT_SETTINGS_SPEC.md` | **Old Content Plant parts:** Title, section 1 references "Content Plant". Has `Legacy / future-scope note`. Mixes valid data model with future UI spec (screens, navigation, etc.). References old docs paths.<br><br>**Replace with LOOPRA:** Rename all "Content Plant" → "LOOPRA". Remove legacy note. Separate data model from UI spec. Update doc references.<br><br>**New concepts to add:**<br>- Brand System integration with project settings<br>- Growth Loop configuration parameters<br>- Orchestrator Agent project-level overrides<br><br>**Action:** Medium rewrite. Valuable project settings structure. Needs LOOPRA adaptation separating model from UI. Align with current `project.yaml` structure. |

---

## Priority Order

1. **BRAND_SYSTEM_SPEC.md** — Brand Profile is core to LOOPRA architecture
2. **SYSTEM_ARCHITECTURE.md** — Most architectural value, needs scoped rewrite
3. **PRODUCT_STRATEGY.md** — Strategic positioning for LOOPRA
4. **USER_WORKFLOWS.md** — Light rewrite, close to production-ready
5. **PROJECT_SETTINGS_SPEC.md** — Important but depends on architecture decisions above

---

## Status Footer

These 5 documents remain in `docs/archive/content-plant-era/` until individual rewrite tasks are created and executed. Original files should not be modified in place — create new LOOPRA-branded versions in the appropriate active `docs/` directories.

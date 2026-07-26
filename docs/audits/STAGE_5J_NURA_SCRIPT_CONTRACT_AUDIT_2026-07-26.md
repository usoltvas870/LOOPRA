# Stage 5J NURA Script Contract — Repository Audit

## Baseline

- Branch: `main`; HEAD: `9c4a3edb7824f3576060678516589b4230a12152`.
- The worktree was already dirty before this audit. Existing modified and
  untracked files are baseline and are outside Stage 5J.
- Commit `9c4a3ed` is the confirmed Stage 5I boundary. It adds the offline,
  deterministic NURA Production Brief builder and its focused tests.

## Reusable contracts

- `trend-radar/src/nura_production_brief.py` is the authoritative Stage 5I
  boundary. Briefs are immutable, hash-addressed JSON artifacts with portable
  references, atomic persistence, and stable reuse.
- `trend-radar/src/content_intelligence_review.py` establishes the human-review
  convention: versioned JSON, a decision template, explicit reviewer fields,
  hashes, atomic writes, and `COMPLETED` finalization.
- `projects/nura/content_intelligence_context.json` is the project-scoped
  context. It explicitly lists `avatar_talking_guide`, `background_voice`,
  `text_led_video`, `dialogue`, and `carousel`.
- `core/services/episode_package.py` is a separate downstream boundary. It
  accepts an `episode.json` with fully supplied frames and currently supports
  only `dialog_miniseries`; it is not a script input contract.

## Existing formats and decision

- `TALKING_GUIDE`: supported, mapped from the existing
  `avatar_talking_guide` project context.
- `BACKGROUND_VOICE`: supported.
- `TEXT_LED_VIDEO`: supported as distinct because it is explicitly separate in
  the NURA project context.
- `DIALOGUE_COMIC`: supported as a semantic script payload. The existing
  episode contract confirms the downstream nine-frame comic boundary, but no
  Episode Input Package is generated here.
- `CAROUSEL`: deferred. A carousel production path exists elsewhere, but it is
  not a required immediate consumer of this Stage 5J contract.

## Architectural conclusion

No canonical script package/provider boundary exists in `trend-radar`. The
canonical foundation `Scenario` model in `core` is intentionally not extended:
NURA-specific editorial rules cannot leak into project-agnostic core. The
minimal extension point is a new, offline `trend-radar/src/nura_script_contract.py`
module downstream from a validated Production Brief.

The supplied source guide was found at
`C:/Users/Bayzel/Downloads/NURA_CONTENT_STUDIO_PROJECT_GUIDE.md`, SHA-256
`d78ae3ad85169d6f479b059ba6d026599329693a60ea2c01e439ec44be29a1c4`.
It is used only to derive the bounded NURA editorial profile and script-layer
validation rules; it is not a global Codex skill or an engineering style guide.

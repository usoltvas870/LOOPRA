# NURA Script Contract

Stage 5J is an offline contract boundary after a validated NURA Production
Brief and before any future provider or Episode Input Package bridge. It does
not generate production scripts, call an AI provider, create media, or modify
upstream artifacts.

`nura_script_contract.py` builds a versioned Script Input Package from one
completed brief, a bounded project-scoped editorial profile, and an explicit
format. The package preserves candidate identity, original rank, brief and
review references, human-approved mechanism and hook, mandatory revisions,
prohibited copying elements, safety constraints, provenance, and visible
unresolved upstream fields.

The profile at `projects/nura/nura_editorial_profile.json` is a structured,
versioned derivative of the canonical source at
`projects/nura/editorial/NURA_CONTENT_STUDIO_PROJECT_GUIDE.md` (SHA-256
`d78ae3ad85169d6f479b059ba6d026599329693a60ea2c01e439ec44be29a1c4`).
The loader verifies the repository-relative path and exact source hash. The
external Downloads copy is no longer a runtime or reproducibility dependency.
The guide is not installed as a global skill and affects only the NURA
script/content layer.

The full Markdown is never placed in Script Input or passed to a provider.
Runtime uses only the bounded profile identity, version, hash, and relevant
format constraints. Engineering, Content Intelligence, Production Brief, and
runtime-chat scopes remain excluded. This fixation does not begin Stage 5K.

Supported output payload formats are `TALKING_GUIDE`, `BACKGROUND_VOICE`,
`TEXT_LED_VIDEO`, and `DIALOGUE_COMIC`. The comic payload is semantic only;
it does not create the separate nine-frame Episode Input Package. `CAROUSEL`
is deferred.

Hard errors reject identity/rank/brief provenance mismatches, changed human
mechanism or approved hook, missing mandatory revisions, returned prohibited
elements, unsupported or malformed formats, safety claims, and explicit author
imitation. Editorial warnings are best-effort and remain separate from errors.
Non-imitation and subjective language quality retain explicit human checks.

The deterministic fake provider is used solely for acceptance: it has no
network or credential access, produces synthetic fixture text, and leaves the
result `DRAFT_AWAITING_HUMAN_REVIEW`. A versioned human review package defaults
to `NEEDS_FURTHER_REVIEW` and `episode_bridge_ready=false`; no Episode bridge is
implemented in this stage.

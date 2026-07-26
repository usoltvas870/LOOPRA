# Human Editorial Review Workflow

Stage 5H adds an offline human-review layer downstream from a completed five-candidate Content Intelligence report. Source report, canonical ranking, cards, provider responses and evidence artifacts are immutable.

`manage_content_intelligence_review.py create` creates a Git-ignored pending package with `review_package.json`, a Russian `review_form.md`, `review_decisions.template.json` and `review_manifest.json`. It covers only ranks 1–5, has no reviewer identity, keeps every decision `PENDING`, and sets `human_confirmation=false`.

The NURA owner or editor fills the machine-readable template outside the automated pipeline, then runs `validate`; `finalize` is explicit and accepts only a completed review with `reviewer_id`, role `OWNER` or `EDITOR`, and `human_confirmation=true`. Human revisions are separate review-domain values and never mutate or relabel AI-card content.

Supported decisions do not change rank, score, classification or select a winner. `hook_type` and `production_complexity` remain `NOT_TYPED`. The workflow rejects scripts/HTML and local paths, performs no AI/provider/network calls, and reuses identical pending packages without timestamp churn. A real package is pending only; no real human decision is finalized, no Production Brief is generated, and ranks 6–20 are out of scope.

# LOOPRA 0.6 — Comment Intelligence

## Scope

LOOPRA 0.6 is a bounded, manual-first pilot for one owner-selected TikTok
video. It collects at most 800 publicly visible comments, anonymizes them
locally, removes deterministic noise, and produces evidence-linked NURA
insights. It does not search for videos, rank trends, log in, bypass CAPTCHA,
create a final script, render, publish, or start a multi-video workflow.

## Operator workflow

1. Put exactly one public TikTok video URL in
   `input/comment_intelligence/selected_video.txt` (UTF-8; `#` lines ignored).
2. Run:

   ```powershell
   python scripts/run_loopra_06_comment_intelligence.py --project nura
   ```

3. If the result is `READY_FOR_OWNER_COMMENT_INSIGHTS_REVIEW`, inspect
   `COMMENT_INSIGHTS_RU.md` and compare it with a manual reading before using
   any content opportunity.

`--url` has priority over the input file. `--dry-run` validates and prints the
bounded plan without opening a browser or calling a provider. `--reuse-only`
uses only a complete content-identical artifact; it performs zero browser,
network, or provider calls. A fresh snapshot requires explicit `--refresh`.

## Privacy and evidence

Canonical files contain only run-local `C0001`-style references, comment text,
thread relations, counts, and short owner-facing excerpts. They exclude
usernames, display names, profile URLs, avatars, user IDs, cookies,
Authorization headers, API keys, and browser-profile paths. Raw browser
payloads are never persisted.

The report describes only the collected public-visible sample. Commenters are
not all viewers; hidden, removed, filtered, and unavailable comments are not
known. Engagement is reported separately from frequency.

## Outputs

Each immutable package lives at `output/comment_intelligence/<run_id>/`:

- `00_OVERVIEW_RU.md`, `manifest.json`
- `comments_raw.jsonl`, `comments_clean.csv`
- `COMMENT_INSIGHTS_RU.md`, `GPT_HANDOFF_WITH_COMMENTS_RU.md` when analysis is
  available
- ignored internal request, raw-response, classification, and aggregate files.

The collection stops on max comments, max scrolls, no-new-comments, timeout,
CAPTCHA, rate limit, or public-comments block. Browser resources owned by the
run are closed in `finally`; an existing user Chrome is never attached to or
terminated.

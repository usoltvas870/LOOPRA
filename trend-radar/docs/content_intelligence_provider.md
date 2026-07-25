# Content Intelligence real-provider contract (Stage 5D)

Status: one bounded DeepSeek provider path for rank 1 only.

The selected provider is `deepseek`, model `deepseek-v4-flash`, through the existing
`httpx` OpenAI-compatible chat-completions transport. Credentials are read only
from `DEEPSEEK_API_KEY`; they are neither logged nor accepted by the CLI. The
legacy `src/ai_analyzer.py` remains retained for backward compatibility and is
not imported by Content Intelligence.

`ContentIntelligencePromptContract` version `1.0` uses DeepSeek JSON Output:
`response_format: {"type": "json_object"}`, an explicit JSON instruction and a
bounded synthetic JSON example. This follows the official
[DeepSeek JSON Output guide](https://api-docs.deepseek.com/guides/json_mode/).
Thinking is explicitly disabled with `thinking: {"type": "disabled"}` so the
bounded extraction continues to use controlled temperature and final assistant
content only. `reasoning_content`, if unexpectedly returned, is removed from
the persisted response and represented only by presence/length metadata.
The local response contract remains strict after parsing; no JSON-schema or
`strict` field is sent. The fixed policy is temperature `0.2`, maximum `1800`
output tokens, 45-second timeout, two total attempts only for invalid structured
output, and no cost estimate unless provider metadata supplies one.

The provider receives a privacy-minimized derived payload only: immutable rank
and video ID, bounded metrics and evidence summaries, opaque evidence IDs,
timestamps, bounded OCR/transcript excerpts, missing-evidence information and
the project-scoped NURA context snapshot. It never receives media, frame
binaries, URLs, cookies, local paths, hashes of full artifacts, credentials,
or unrelated candidates. Payload size is revalidated before network.

Claims may be only `INFERENCE` or `AI_INTERPRETATION`; local validation rejects
`FACT`, unknown evidence IDs, invalid confidence, malformed output, and any
attempt to mutate identity. Local immutable identity is attached after the
provider output. NURA safety requires calm Russian guidance without human lived
experience, therapy/diagnosis, predictions, guarantees, author imitation, or
copied visual production.

Runtime artifacts are ignored under `trend-radar/data/content-intelligence/real`:
analysis input, provider payload, project-context snapshot, request metadata,
raw response, card and validation result. Writes are atomic. Reuse requires the
same input hash, context hash, provider/model, prompt version and schema; a
reused valid card makes no transport call. Fake cards are never real-card reuse.

The CLI defaults to offline fake mode. A new real request requires exactly one
rank-1 candidate, `--provider-real` and `--allow-network`; `--dry-run` builds
the payload without network. `--reuse-only` instead forbids `--allow-network`,
requires an already validated real card and returns a typed miss without
creating transport. Ranks 2–5, TOP-20 analysis, reports and automatic
production briefs are explicitly out of scope.

## Acceptance status

The rank-1 dry-run validated the canonical `20260724_150816` evidence chain and
the minimized payload before network. The subsequent V4 Flash acceptance and
the separate network-free reuse acceptance are recorded below.

HTTP error metadata is atomically persisted in ignored runtime with only status,
provider error type/code, bounded message, request ID and response-body hash.
Authorization, request body content and arbitrary response headers are never
persisted. Empty HTTP-200 assistant content is classified as
`PROVIDER_EMPTY_CONTENT`, never converted into a card.

## Stage 5D-FIX probe result

The official JSON-mode transport probe returned HTTP 400 before any Content
Intelligence evidence was sent. The bounded provider error states that the
fixed `deepseek-chat` model is not supported by the current endpoint and names
`deepseek-v4-pro` and `deepseek-v4-flash` as supported alternatives. This is a
provider/model availability blocker, not a prompt, evidence, or JSON-output
schema failure. The orchestrator selected `deepseek-v4-flash` for the bounded
rank-1 acceptance because Pro is not required for this extraction and remains
untested. There is no compatibility mapping or automatic fallback.

## V4 Flash rank-1 acceptance

The canonical rank-1 request completed with HTTP 200 using
`deepseek-v4-flash`, JSON Output and explicitly disabled thinking. The persisted
card passed local schema, identity, claim-type and evidence-reference
validation. Provider claims contain no `FACT`; the card's single `FACT` is
attached locally by the deterministic input builder. Ranks 2–5 and TOP-20 were
not called.

The first reuse check exposed a local hash-comparison defect and unexpectedly
made a second provider call. The card carried the generic adapter-context hash
while reuse compared it with the full project snapshot hash. Reuse now keys on
the explicit snapshot-backed identity and normalizes that card metadata
atomically. A credentialless verification then returned `REUSED` with
`network: NOT_CALLED`.

Stage 5D-FINAL used a separate network-free acceptance process over the existing
validated card. `DEEPSEEK_API_KEY` was absent in that child process and
`httpx.Client` was replaced by a guard that fails on construction. The first
`--reuse-only` pass immediately returned `REUSED`; transport factory and HTTP
call counts were zero. A second idempotency pass also returned `REUSED`, and
hashes of all seven runtime files remained unchanged before, between and after
the passes. This clean block proves the final reuse contract without rewriting
the history of the earlier duplicate call.

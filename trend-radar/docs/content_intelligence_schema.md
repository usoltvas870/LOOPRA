# Content Intelligence schema — Stage 5A

Status: implemented offline design foundation; real AI analysis is not implemented.

The Stage 5A pipeline is strictly downstream of the immutable selection manifest:

`manifest + acquisition + format inspection + OCR + transcription -> bounded analysis input -> typed provider -> validated card`.

`trend-radar/src/content_intelligence.py` owns schema version `0.1`. It accepts portable, candidate-scoped evidence references only; it never copies media, frame bytes, full OCR corpora, or full transcripts. OCR events, transcript segments, and frames are capped at 12 each; text is capped at 240 characters per included item.

Claims are explicit:

| Type | Producer | Rule |
| --- | --- | --- |
| `FACT` | deterministic input builder | derives only from manifest/evidence and carries references |
| `INFERENCE` | provider | may cite validated evidence but is not a source fact |
| `AI_INTERPRETATION` | provider | never presented as fact; empty evidence is permitted by policy |

The provider protocol is structured and validates output before a card is written. It cannot change video ID or rank, cannot emit `FACT`, cannot cite unknown evidence, and cannot use non-finite confidence. `FakeDeterministicProvider` is the only enabled provider: it is local, deterministic, explicitly marked `fake/test`, and has no HTTP, browser, secret, or environment access.

`ProjectAnalysisContext` is generic (`project_id`, context version, audience context, requested adaptation fields, optional reference). NURA-specific semantics must remain in project configuration or an adapter and are represented only through generic `project_adaptation` output.

Runtime output is candidate-scoped under the caller-selected ignored root: `run_manifest.json`, `analysis_input.json`, `provider_result.json`, and `content_intelligence_card.json`. Writes are atomic and reject non-identical conflicts. Input reuse keys include manifest/evidence hashes, project-context hash, builder and input schema versions. Result reuse additionally requires fake provider ID/version/model/configuration and never reuses a fake result as a real-provider result.

The safe CLI is `trend-radar/analyze_content_intelligence.py`. It accepts canonical manifests and candidate IDs only, preserves manifest order, has a Stage 5A limit of 1–5, and does not start runtime work on `--help`. Real provider prompts, reports, production briefs, and all real-provider/network execution are intentionally out of scope. The legacy `src/ai_analyzer.py` remains untouched and isolated; it is not used by this pipeline.

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

## Stage 5B evidence resolution

`evidence_resolution.py` resolves one candidate only through fixed, portable candidate-scoped paths: acquisition record, canonical Format Inspection result, OCR result and transcription result. It validates manifest identity, rank, actual local-media SHA-256, inspection schema `1.1`, inspection/video identity, inspection media hash, frame existence, and downstream identity/status/media hashes. It does not scan runtime directories and it never invokes acquisition, inspection, OCR, transcription, browser, network, or an AI provider.

The canonical inspection location is `<inspection-root>/<video_id>/inspection.json`. When a verified Stage 3M result exists under an explicitly supplied legacy root, `adopt_legacy_inspection()` may atomically adopt its JSON and referenced frames into that canonical location. A conflicting schema `1.0` canonical artifact with no final status is first preserved byte-for-byte under `legacy-backups/`; any other conflict is rejected. This explicit repair preserves the legacy source, checks candidate/media/schema/frame identity, and never fabricates inspection evidence. Missing evidence remains typed diagnostics and keeps the input/card degraded; an invalid identity/hash is a hard failure.

The safe CLI is `trend-radar/analyze_content_intelligence.py`. It accepts canonical manifests and candidate IDs only, preserves manifest order, has a Stage 5A limit of 1–5, and does not start runtime work on `--help`. Real provider prompts, reports, production briefs, and all real-provider/network execution are intentionally out of scope. The legacy `src/ai_analyzer.py` remains untouched and isolated; it is not used by this pipeline.

## Stage 5C OCR canonical references

Stage 4A OCR schema `1.0` stored an absolute reference to the Stage 3M inspection location and did not store the canonical inspection schema or JSON hash. After the canonical schema `1.1` inspections were adopted in Stage 5B, the OCR observations were still current but their reference contract remained legacy.

OCR evidence schema `1.1` requires `inspection_result_ref: "inspection.json"`, the SHA-256 of that exact canonical inspection JSON, its schema version, media identity, complete frame set and a deterministic `result_sha256`. The resolver rejects legacy or absolute OCR inspection references, unsupported OCR schemas, cross-candidate references, inspection-hash mismatches, and frame-count, frame-reference, frame-hash, or timestamp mismatches. It remains path-bounded and never searches legacy runtime trees.

`migrate_ocr_evidence_references()` is manifest-bound and first performs a complete forensic audit of candidate, rank, manifest, media, frame count/hashes/timestamps, engine version and requested language. Only when every requested candidate is safe does its explicit `apply` mode atomically replace each OCR result. It preserves the original bytes once under the candidate's ignored `legacy-backups/` directory, records ref-only provenance, never edits raw or normalized OCR text, bounding boxes, observations, text events, first hook or engine metadata, and is idempotent. A conflicting backup blocks replacement. The migration does not instantiate the OCR engine, PowerShell, browser, network, acquisition, inspection or transcription, so recognition is not rerun when the existing frame identities match.

Changed evidence produces a new `evidence_set_hash` in the offline fake-analysis run identity. This prevents a stale input or fake card from being silently reused; an identical second pass reuses all cards. For manifest `20260724_150816`, ranks 1–5 now have canonical OCR schema `1.1` results and OCR reuse is 5/5. Transcription remained unchanged at schema `1.1` and `COMPLETED`. Rebuilt inputs and fake/test cards completed 5/5, and the second fake pass reused 5/5 with no missing evidence. The real-provider gate is open, but no real provider or production prompt is implemented, real AI was not called, and no real Content Intelligence cards or NURA adaptation were generated.

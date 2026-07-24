# Local transcription evidence

Stage 4C hardens the local, candidate-scoped speech-transcription evidence layer.
It is technical evidence only: it does not infer a video's meaning, hook type,
audience, CTA, or adaptation.

The selected engine is `faster-whisper 1.2.1` with the locally cached
`Systran/faster-whisper-base` model, CPU device, `int8` compute type and eight
bounded CPU threads. The
adapter uses direct MP4 input through the engine's local FFmpeg/PyAV path; it
does not modify acquisition media or Format Inspection. The engine reports
automatic language detection, segment and word timestamps, language
probability, `avg_logprob`, and `no_speech_prob` where available.

Run only against a canonical manifest and its existing local evidence:

```powershell
python trend-radar/extract_transcription_evidence.py `
  --selection-manifest trend-radar/data/runs/selection_manifest_20260724_150816.json `
  --acquisition-root trend-radar/data/acquisitions/20260724_150816 `
  --inspection-root trend-radar/data/format-inspections/stage3m-after
```

Results are atomically written below the ignored
`trend-radar/data/content-intelligence/<run-id>/candidates/<video-id>/transcription/`.
They contain candidate/media/acquisition and inspection references and hashes,
engine/model metadata, audio facts, language, ordered raw and mechanically
normalized segments, optional word probabilities, rejected low-speech
observations, first spoken words, timing, status and reuse inputs. All results
set `human_verified: false`.

## Contract and schema compatibility

The current result schema is `1.1`. `first_spoken_words` is structured evidence,
not a semantic hook: it contains mechanical text (at most 12 words), `start_sec`,
optional `end_sec`, `supporting_segment_id`, source, selection rule and
`human_verified: false`. It is selected from the earliest reliable accepted
segment by timestamp; when none exists it is `null` with
`no_reliable_speech_observed`.

Schema `1.0` results are not silently reused. When their manifest, acquisition,
inspection, engine/model and option identities match, their existing accepted and
rejected segment evidence is deterministically migrated to `1.1` without loading
the model. Migration records `migrated_from_schema_version: "1.0"`; incomplete or
invalid legacy evidence is reprocessed rather than represented as current schema.
All segment and word timestamps, language probability, log probabilities and
timings must be finite. Segment and word intervals are bounded against media and
supporting-segment time ranges with a 0.30-second tolerance. This accommodates
the observed faster-whisper word-boundary rounding (maximum 0.26 seconds) while
rejecting materially detached words. JSON writes reject
NaN and infinity.

## Controlled fixtures

- Russian Windows speech fixture: PASS — Russian was detected and timestamped
  output was produced.
- English Windows speech fixture: PASS — English was detected and timestamped
  output was produced.
- Silence fixture: PASS — no reliable final speech was accepted; high
  `no_speech_prob` evidence remains as a rejected raw observation.
- Music-only fixture: NOT TESTED. Music-over-speech and noisy speech can still
  contain recognition errors.

## Real acceptance and reuse

| Rank | Language | Segments | Elapsed seconds | Realtime factor | Status |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | en | 1 | 9.16 | 0.454 | COMPLETED |
| 2 | ru | 122 | 123.99 | 0.269 | COMPLETED |
| 3 | en | 3 | 1.63 | 0.259 | COMPLETED |
| 4 | ru | 335 | 583.47 | 0.912 | COMPLETED |
| 5 | en | 1 | 22.89 | 2.999 | COMPLETED |

All five canonical candidates were processed in manifest order. The subsequent
pass reused 5/5 results without model transcription, browser, or network use.

`COMPLETED_NO_AUDIO` skips the engine. `COMPLETED_NO_SPEECH` retains rejected
raw observations but exposes no final segment or `first_spoken_words`. Reuse
requires matching manifest, media, acquisition and inspection hashes,
engine/model version and revision, requested language, and decoding options.

Model binaries, extracted audio and real transcription results are runtime data
and remain ignored. The adapter never downloads a model: it only accepts the
approved local cache. OCR is already implemented; AI Content Intelligence and
Content Intelligence Cards are not implemented by this layer.

## Limitations

Automatic transcripts are not human verified; no WER, dataset-level accuracy or
accuracy guarantee is claimed. The local model cache is required, rank 4 has
substantial CPU cost, and rank 5's elevated realtime factor is not yet explained.
No external STT/API is used. AI Content Intelligence analysis, Content
Intelligence Cards and NURA adaptation remain unimplemented.

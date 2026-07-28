# LOOPRA 0.5 Trend Workbook

`scripts/run_loopra_05_trend_workbook.py` builds a portable local review package from a bounded, acquired candidate list. It performs no Content Intelligence, Script Provider, image, HeyGen, or render call.

For a fresh run, `--fresh --target-count 20` composes the existing public-first v2 collector with its per-item browser capture primitive. Guest/no-session collection is supported; the legacy five-item acquisition wrapper is not used.

The package contains one `.xlsx`, `manifest.json`, `README_RU.txt`, and `videos/`. The workbook's primary video links are relative `videos\<rank>_<video_id>.mp4` links; TikTok URLs remain provenance only.

Run:

```powershell
python scripts/run_loopra_05_trend_workbook.py --project nura --search-run-id <id> --candidates-json <acquired-candidates.json> --json

python scripts/run_loopra_05_trend_workbook.py --project nura --fresh --target-count 20 --json
```

Resume an existing canonical collection without running a new TikTok search:

```powershell
python scripts/run_loopra_05_trend_workbook.py --project nura --runtime-root <existing-runtime> --resume --build-id <build-id> --target-count 20 --json
```

`--resume` scans the existing ranked pool, reuses validated acquisition records,
and performs bounded per-item acquisition until the target number of unique valid
MP4 files is reached. The independent safety bounds are
`--maximum-attempts`, `--maximum-shortlist-size`, and
`--maximum-consecutive-failures`. A stable `--build-id` creates a versioned
package and makes an identical second invocation reuse-only: no search, browser,
download, or transcription execution.

For each final MP4, resume runs canonical format inspection before canonical
transcription. The workbook stores typed audio/transcription status and all
accepted segments. Music-only, no-speech, no-audio, unreliable, and failed ASR
results remain explicit and are never converted into invented transcript text.

Every input candidate must point to a local acquired MP4 in `local_media_path`. Missing media and exact SHA-256 duplicates are rejected and never reach `Кандидаты`. The package builder validates byte-for-byte copies and reloads the workbook to validate relative links.

The operator opens `Кандидаты`, clicks `Открыть MP4`, enters `ДА/НЕТ/ПОЗЖЕ`, priority, and comments, then transfers selected local MP4 files to GPT manually. Automatic scenario generation is outside LOOPRA 0.5.

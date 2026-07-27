# LOOPRA 0.5 Trend Workbook

`scripts/run_loopra_05_trend_workbook.py` builds a portable local review package from a bounded, acquired candidate list. It performs no Content Intelligence, Script Provider, image, HeyGen, or render call.

The package contains one `.xlsx`, `manifest.json`, `README_RU.txt`, and `videos/`. The workbook's primary video links are relative `videos\<rank>_<video_id>.mp4` links; TikTok URLs remain provenance only.

Run:

```powershell
python scripts/run_loopra_05_trend_workbook.py --project nura --search-run-id <id> --candidates-json <acquired-candidates.json> --json
```

Every input candidate must point to a local acquired MP4 in `local_media_path`. Missing media and exact SHA-256 duplicates are rejected and never reach `Кандидаты`. The package builder validates byte-for-byte copies and reloads the workbook to validate relative links.

The operator opens `Кандидаты`, clicks `Открыть MP4`, enters `ДА/НЕТ/ПОЗЖЕ`, priority, and comments, then transfers selected local MP4 files to GPT manually. Automatic scenario generation is outside LOOPRA 0.5.

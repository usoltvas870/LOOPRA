# Content Plant

| | |
|---|---|
| Path | `C:\git\content-plant` |
| Stack | Python 3.11+, Node.js, HyperFrames (HTML → MP4), FFmpeg |
| Components | `hyperframes/`, `trend-radar/`, `video-assembler/` |

## Компоненты

- `hyperframes/` — генерация видео из HTML (HeyGen HyperFrames)
- `trend-radar/` — сбор и анализ TikTok-трендов (Python, Playwright)
- `video-assembler/` — сборка видео из сценариев (Python, FFmpeg)

## Commands

| Task | Command |
|------|---------|
| Trend Radar | `cd trend-radar && python run_radar.py` |
| Video Assemble | `cd video-assembler && python assemble.py <scenario.json>` |
| HyperFrames Dev | `cd hyperframes && npm run dev` |
| HyperFrames Render | `cd hyperframes && npm run render` |
| HyperFrames Check | `cd hyperframes && npm run check` |

## Требования

- Node.js 22+
- FFmpeg
- Playwright (для trend-radar)
- Python 3.11+

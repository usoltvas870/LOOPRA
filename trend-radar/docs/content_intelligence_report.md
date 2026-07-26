# Content Intelligence Report Contract

## Назначение и границы

Stage 5G создаёт offline-отчёт для владельца или редактора NURA. Он помогает сопоставить только пять уже валидированных Content Intelligence cards в неизменяемом порядке canonical selection manifest. Отчёт не выбирает winner, не меняет ranking, не создаёт Production Brief, сценарий, TOP-20 или новый контент.

## Источники и schema

`content_intelligence_report.py` читает canonical manifest, NURA context snapshot и только cards real-provider namespace с `deepseek` / `deepseek-v4-flash` / prompt `2.0`. Report schema, builder и JSON/Markdown renderers имеют отдельные версии. Identity включает manifest, упорядоченные rank/video IDs, hashes и schema versions source cards, provider/model/prompt, context hash и версии renderer-ов.

Каждая candidate entry ограничена ranking snapshot, portable card ref/hash, provider metadata, quality/evidence summaries, существующими claims, existing NURA adaptation, warnings и editorial readiness. Полные OCR, transcript, raw provider responses, media, frames, local absolute paths и signed URLs не копируются.

## Presentation

Ranking snapshot показан как FACT. Существующие card claims сохраняют `FACT`, `INFERENCE` или `AI_INTERPRETATION`; Markdown явно помечает AI-generated и `human_verified=false`. Evidence quality, source warnings и отсутствие human review не скрываются. Если current card не имеет dedicated typed `hook_type` или `production_complexity`, report показывает `NOT_TYPED` и не извлекает значение из prose.

## Runtime, persistence and reuse

CLI `generate_content_intelligence_report.py` не импортирует provider adapter, не читает API key и не выполняет AI/network calls. Runtime размещается в Git-ignored `trend-radar/data/content-intelligence-reports/<deterministic-report-id>/` и содержит `report.json`, `report.md`, `report_manifest.json`. Запись атомарна; read-back сверяет hashes. При совпадении identity и hashes повторный запуск возвращает `REUSED` без перезаписи файлов.

Stage 5G ограничен canonical ranks 1–5. Missing, corrupt, fake, prompt-v1, mismatched, provider-FACT или invalid-quality cards отклоняются до создания отчёта.

## Ограничения

Отчёт отражает только AI-generated source cards и не заменяет human editorial review. Он не делает выводов за пределами existing cards/evidence и не расширяет выборку за пять кандидатов.

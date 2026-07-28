# LOOPRA 0.5 — manual-first scope freeze

Текущий acceptance status: `READY_FOR_OWNER_SMOKE_INPUT`.

Причина: implementation и offline acceptance подготовлены, но в канонических owner-input
путях ещё нет реальной ссылки или MP4. Этот документ нельзя переводить в
`ACCEPTED_WITH_RESCOPED_SCOPE` до успешной обработки 1–2 вручную выбранных источников и
повторного `--reuse-only` запуска.

```text
LOOPRA_0_5_STATUS=READY_FOR_OWNER_SMOKE_INPUT
SCOPE_FROZEN=false
OPERATING_MODEL=MANUAL_FIRST_LOCAL_PRODUCTION
AUTOMATIC_TREND_RADAR=EXPERIMENTAL_FAILED_PRODUCT_ACCEPTANCE
MANUAL_SOURCE_INPUT=SUPPORTED
LINK_ACQUISITION=SUPPORTED
LOCAL_MP4_INPUT=SUPPORTED
TRANSCRIPTION=SUPPORTED
BEST_EFFORT_OCR=SUPPORTED
GPT_HANDOFF=SUPPORTED
AUTOMATIC_SCRIPT_GENERATION=OUT_OF_SCOPE
AUTOMATIC_TREND_RANKING=OUT_OF_SCOPE
LOOPRA_1_0=NOT_STARTED
```

## Gate для финальной фиксации

1. Владелец добавляет реальную TikTok-ссылку или MP4 в канонический input.
2. Каноническая команда успешно создаёт source package и GPT handoff.
3. Повтор с `--reuse-only` подтверждает нулевые browser/network, acquisition, inspection,
   transcription и OCR calls и равенство identity/hash.
4. После проверки документация получает `LOOPRA_0_5_STATUS=ACCEPTED_WITH_RESCOPED_SCOPE`
   и `SCOPE_FROZEN=true` отдельным Phase B commit.

Старые TOP-20/TOP-30 counts не являются основанием этой приёмки.

# LOOPRA 0.5 — ручной workflow источников

LOOPRA 0.5 работает локально и начинается с источников, вручную выбранных владельцем.

## Подготовка входов

Ссылки добавляются по одной на строку в:

`C:\git\LOOPRA\input\selected_sources\selected_links.txt`

Пустые строки, окружающие пробелы и строки-комментарии с `#` игнорируются. Одинаковые
нормализованные TikTok-ссылки дедуплицируются с сохранением первого порядка. Пример
лежит в `templates/manual_intake/selected_links.example.txt`.

Готовые MP4 можно положить в:

`C:\git\LOOPRA\input\selected_sources\media\`

Ссылки и MP4 разрешено использовать одновременно. LOOPRA не изменяет эти входы.

## Запуск в PowerShell

```powershell
cd C:\git\LOOPRA
python scripts/run_loopra_05_manual_intake.py --project nura
```

Результат появляется в `output\manual_intake\<intake_id>\`. Сводка находится в
`00_OVERVIEW_RU.md`; каждый успешно обработанный источник — в отдельной папке `items`.

## Работа с ChatGPT

Из выбранной item-папки загрузите в ChatGPT:

- `source.mp4`;
- `GPT_HANDOFF_RU.md`.

Готовый запрос:

> Выполни инструкции из GPT_HANDOFF_RU.md строго в два этапа. Сначала посмотри видео,
> буквально опиши содержание, фактический hook и механизм удержания внимания. Не начинай
> адаптацию, пока я не подтвержу понимание источника. Затем создай самостоятельную
> адаптацию NURA без копирования формулировок, персонажа, монтажа, музыки или footage.

При сомнениях сначала проверьте `transcript.txt`, `screen_text.txt` и само видео.

## Повторный запуск и ошибки

Обычный повтор идентичных входов переиспользует проверенный package. Строгая offline-проверка:

```powershell
python scripts/run_loopra_05_manual_intake.py --project nura --reuse-only
```

`--reuse-only` не открывает browser и не выполняет acquisition, inspection, transcription
или OCR. Если артефакт отсутствует или повреждён, команда возвращает typed blocker.

Ошибка одного источника не останавливает остальные. Откройте `00_OVERVIEW_RU.md`, исправьте
конкретный вход и запустите ту же команду. Для проверки плана без side effects используйте
`--dry-run`; для машинного результата — `--json`.

После успешной обработки вручную удалите ссылки, перенесите MP4 в архив или оставьте их
для reuse.

## Граница LOOPRA 0.5

Команда не запускает автоматический TikTok search или ranking, Content Intelligence batch,
Production Brief, Script Provider, автоматическую генерацию сценариев, ImageGen, HeyGen,
render, публикацию, deploy или VPS.

Автоматический Trend Radar сохранён в repository как historical foundation со статусом
`EXPERIMENTAL_FAILED_PRODUCT_ACCEPTANCE`, исключён из основного workflow и не запускается
этой командой. Его переосмысление возможно только в LOOPRA 1.0.

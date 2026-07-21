# Nura TikTok Viral Screening Radar

**MVP** — локальный инструмент для сбора TikTok-роликов по заданным источникам, расчёта метрик вирусности и формирования отчёта.

## Возможности

- Поиск видео по трём типам источников: аккаунты, хэштеги, ключевые слова
- Сбор метрик: просмотры, лайки, комментарии, репосты
- Расчёт viral score, engagement rate, comment density
- Дедупликация видео (SQLite)
- Markdown-отчёт с топ-30 роликами
- AI-анализ вирусных паттернов через DeepSeek (опционально)
- Telegram-digest (опционально)
- Playwright — сбор данных через браузер без API-ключей

## Установка

```bash
# 1. Клонировать / перейти в директорию
cd nura-trend-radar

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Установить браузеры Playwright
playwright install chromium
```

## Настройка

### 1. Файлы источников

Заполните файлы в `config/`:

| Файл | Формат | Пример |
|---|---|---|
| `competitors.txt` | username (с @ или без) | `@matrica_sudby` |
| `hashtags.txt` | хэштег (с # или без) | `нумерология` |
| `keywords.txt` | поисковый запрос | `матрица судьбы` |

Строки, начинающиеся с `#`, игнорируются.

### 2. .env

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Основные параметры:

| Параметр | По умолчанию | Описание |
|---|---|---|
| `MIN_VIEWS` | 10000 | Мин. просмотров для попадания в отчёт |
| `MAX_RESULTS_PER_SOURCE` | 20 | Макс. роликов с одного источника |
| `HEADLESS` | true | Запускать браузер в фоне |
| `DIAGNOSTIC_MODE` | false | Безопасная диагностика без изменения cookies и ожидания login |
| `COOKIE_PATH` | data/tiktok_cookies.json | Путь к файлу cookies |
| `ENABLE_AI_ANALYSIS` | false | Включить DeepSeek-анализ |
| `DEEPSEEK_API_KEY` | — | Ключ API DeepSeek |
| `ENABLE_TELEGRAM` | false | Отправлять digest в Telegram |
| `TELEGRAM_BOT_TOKEN` | — | Токен бота Telegram |
| `TELEGRAM_CHAT_ID` | — | ID чата для отправки |
| `EXPORT_XLSX` | true | Экспорт отчёта в Excel |

## Запуск

```bash
python run_radar.py
```

### Diagnostic mode

Для безопасной проверки без обновления сессии:

```bash
DIAGNOSTIC_MODE=true ENABLE_AI_ANALYSIS=false ENABLE_TELEGRAM=false python run_radar.py
```

В этом режиме cookies используются только для чтения, ручной login не ожидается, а operational failures завершаются ненулевым exit code. В конце выводится машинно-читаемая строка `RADAR_RESULT=...`. Diagnostic mode предназначен для проверки состояния, а не для обновления TikTok-сессии.

Скрипт:
1. Читает источники из `config/`
2. Открывает браузер через Playwright
3. Собирает видео с TikTok
4. Сохраняет в SQLite (`data/videos.db`)
5. Считает метрики вирусности
6. Формирует markdown-отчёт (`data/reports/report_*.md`)
7. Выводит краткую сводку в консоль

## Результат

Отчёт сохраняется в `data/reports/report_YYYY-MM-DD_HH-MM.md`:

- Статистика запуска
- Топ-30 роликов с метриками
- AI-анализ (если включён)

## Ограничения

- **MVP, не production.** Код предназначен для личного ознакомительного использования.
- **TikTok может блокировать.** Работает через браузер — TikTok может показать login wall или captcha.
- **Разметка TikTok меняется.** `src/parser.py` максимально изолирован. Если парсинг сломался — править нужно только этот файл.
- **Нет скачивания.** Видео не сохраняются, только метаданные.
- **Не агрессивный.** Между запросами паузы 3–6 секунд.

## Авторизация в TikTok

**TikTok требует авторизации** для просмотра хештегов, поиска и большинства профилей.  
Без входа радар найдёт видео только у некоторых открытых аккаунтов.  
Чтобы всё работало полноценно — нужно сохранить cookies реального аккаунта.

### Безопасное обновление cookies

```bash
python refresh_tiktok_cookies.py
```

Helper открывает Chromium в видимом режиме и удерживает его до нажатия Enter в терминале. Пользователь входит только в браузере. Перед обновлением создаётся backup, новые cookies сохраняются сначала в pending-файл, затем проверяются в новом browser context; рабочий cookie-файл заменяется только после двух успешных проверок. Credentials и содержимое cookies нельзя передавать агенту или выводить в терминал.

### Способ 2 — логин во время запуска

1. Установите `HEADLESS=false` в `.env`
2. Запустите: `python run_radar.py`
3. Откроется окно браузера — **вручную войдите** в TikTok (email/телефон + пароль)
4. После входа скрипт продолжит сбор и **автоматически сохранит cookies**
5. При следующих запусках cookies будут подгружаться

### Если cookies протухли

Не удаляйте cookie-файл автоматически. Запустите `python refresh_tiktok_cookies.py` и выполните ручной вход в браузере.

### Current operational limitation

Collector зависит от действующей TikTok-сессии. Login wall возвращает `authentication_required`; до подтверждения авторизации parser нельзя считать сломанным. Текущий recovery status: безопасная диагностика реализована, первый актуальный сбор ещё не подтверждён.

## Структура проекта

```
nura-trend-radar/
  run_radar.py          # Точка входа
  config/               # Файлы с источниками
    competitors.txt
    hashtags.txt
    keywords.txt
  data/                 # SQLite + отчёты
    videos.db
    reports/
  src/                  # Модули
    collector.py        # Playwright-сборщик
    parser.py           # Парсер TikTok (изолирован)
    storage.py          # SQLite + дедупликация
    scoring.py          # Расчёт метрик
    ai_analyzer.py      # DeepSeek API
    telegram.py         # Telegram-нотификации
    report.py           # Markdown-отчёт
    utils.py            # Утилиты, конфиг
  prompts/              # Шаблоны промтов
    pattern_analysis_ru.txt
  .env.example
  requirements.txt
  README.md
```

## DeepSeek AI

1. Установите `ENABLE_AI_ANALYSIS=true` в `.env`
2. Добавьте `DEEPSEEK_API_KEY=sk-...`
3. При необходимости укажите `DEEPSEEK_BASE_URL` и `DEEPSEEK_MODEL`

Совместимо с любым OpenAI-совместимым API (OpenRouter, Together AI и т.д.)

## Telegram

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Установите `ENABLE_TELEGRAM=true` в `.env`
3. Добавьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`

## Лицензия

MIT

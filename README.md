# Content Plant

Набор инструментов для генерации контента: поиск трендов в TikTok и сборка видео.

## Структура проекта

```
content-plant/
├── trend-radar/        # Тренд-радар — сбор и анализ TikTok-видео
├── video-assembler/    # Сборщик видео — FFmpeg-пайплайн + AI-генерация сценариев
├── hyperframes/        # HeyGen HyperFrames — HTML → MP4 (экспериментальный рендер)
└── README.md
```

## Связь с другими проектами

- **NURA** (`C:\git\NURA`) — оригинальный монолит. Content Plant — выделенные модули.
- **Hyperframes** (`hyperframes/`) — экспериментальный рендер HTML-композиций в MP4.

Модули внутри content-plant **не зависят друг от друга**. Каждый можно запускать отдельно.

---

## Быстрый старт

### 1. Тренд-радар

```bash
cd trend-radar

# Установка
pip install -r requirements.txt
playwright install chromium

# Настройка
cp .env.example .env
# отредактируйте .env (впишите DEEPSEEK_API_KEY)

# Запуск
python run_radar.py
```

Результат: `data/trend_top.json` — топ-10 видео для передачи в видео-ассемблер.

### 2. Сборщик видео (изолированно)

```bash
cd video-assembler

# Установка
pip install -r requirements.txt

# Настройка
cp .env.example .env
# отредактируйте .env (впишите DEEPSEEK_API_KEY для AI-пайплайна)

# Прямая сборка из готового сценария
python assemble.py ../scenarios/example.json

# AI-пайплайн из данных тренд-радара (dry-run)
python assemble.py --from-trend ../trend-radar/data/trend_top.json

# AI-пайплайн с реальной сборкой
python assemble.py --from-trend ../trend-radar/data/trend_top.json --assemble

# Сборка из job-директории
python assemble.py --job jobs/my_job/
```

## Переменные окружения

### Trend Radar (`trend-radar/.env`)

| Переменная | Описание | По умолчанию |
|---|---|---|
| `MIN_VIEWS` | Минимум просмотров для попадания в топ | `10000` |
| `HEADLESS` | Режим браузера (true/false) | `true` |
| `DEEPSEEK_API_KEY` | Ключ DeepSeek AI для анализа трендов | — |
| `ENABLE_TELEGRAM` | Отправлять дайджест в Telegram | `false` |

### Video Assembler (`video-assembler/.env`)

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DEEPSEEK_API_KEY` | Ключ DeepSeek AI для генерации сценариев | — |
| `DEEPSEEK_BASE_URL` | Базовый URL DeepSeek API | `https://api.deepseek.com/v1` |
| `CONTENT_PLANT_ROOT` | Корень проекта (авто если пусто) | авто |
| `JOBS_DIR` | Путь к job-директориям | `<root>/jobs` |
| `MEDIA_DIR` | Путь к медиа-файлам | `<root>/videos/media` |

## Команды разработки

| Команда | Описание |
|---|---|
| `npm run dev` (в `hyperframes/`) | HTTP-превью HyperFrames на порту 3002 |
| `python run_radar.py` (в `trend-radar/`) | Запуск тренд-радара |
| `python assemble.py <file>` (в `video-assembler/`) | Сборка видео |

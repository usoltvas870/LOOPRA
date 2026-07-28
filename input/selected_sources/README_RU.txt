LOOPRA 0.5 — ручной ввод источников

1. Добавьте TikTok-ссылки в selected_links.txt: одна ссылка на строку.
   Пустые строки и строки, начинающиеся с #, игнорируются.

2. Либо положите готовые MP4 в папку media.

3. Запустите из C:\git\LOOPRA:

   python scripts/run_loopra_05_manual_intake.py --project nura

Ссылки, MP4 и runtime output не включаются в Git. LOOPRA не удаляет и не
перемещает входные файлы автоматически.

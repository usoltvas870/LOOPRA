# NURA Validation Project

Status: Active
Updated: 2026-07-07

## 1. Purpose

NURA is the first validation project for the Content Plant foundation.
It uses the project-agnostic foundation MVP to produce manual-publication-ready content
for the NURA brand and verifies that the platform foundation works correctly
with a real project without modifying the foundation layer.

## 2. What NURA Is

NURA is an AI self-understanding product based on Destiny Matrix and Tarot-like
archetypal content. It is a soft self-understanding tool — not fortune telling,
not therapy, not occult promises.

Primary market: Russia / Russian language.
Primary commercial route: social traffic → landing page → registration/payment/subscription.

## 3. Current Scope

Current foundation format used:

```text
text_social_post
```

Current target platform for validation:

```text
telegram
```

Note: Telegram is used only as a manual validation channel for the current
foundation loop. NURA's real commercial route goes through the landing page
at https://nura-ai.ru.

## 4. Allowed Outputs

```text
NURA text_social_post export packages for manual publication
```

Each package includes:

```text
title.txt
body.txt
caption_telegram.txt
manual_publication_checklist.txt
metadata.json
manifest.json
```

## 5. Non-Goals

- No video/image/render output
- No autoposting
- No external API integrations
- No analytics automation beyond manual metrics import
- No foundation architecture changes
- No new content formats

## 6. Project Docs

| Document | Purpose |
|---|---|
| `README.md` | This file — navigation and scope |
| `POSITIONING.md` | Product definition, audience, value proposition |
| `TONE_OF_VOICE.md` | Brand voice rules and examples |
| `CONTENT_PILLARS.md` | Content themes and boundaries |
| `VALIDATION_PLAN.md` | Validation goals and success criteria |

## 7. Machine-Readable Config

Path: `projects/nura/project.yaml`

Loaded by Content Plant foundation through `ProjectConfig` / `load_project()`.
Must remain project-scoped and must not modify foundation architecture.

## 8. Boundary

NURA is a project-specific validation layer.
It must not modify Content Plant foundation architecture.
No NURA-specific hardcode may appear in `core/`, `scripts/`, or `tests/`.

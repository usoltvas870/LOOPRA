# Explainable Manual Trend Ranking

`Final Score` is an ordering aid for manual review. It is not a prediction
that a new NURA video will become viral.

## Inputs and derived rates

- proven reach: `views`;
- `like_rate = likes / views`;
- `comment_rate = comments / views`;
- `share_rate = shares / views`;
- total engagement rate is the sum of available reactions divided by views.

Missing reactions remain missing. They are not converted to zero, and reduce
the amount of evidence shown to the reviewer.

## Components (0–100)

| Component | Calculation | Meaning |
|---|---|---|
| Reach score | `100 × log(1 + views) / log(1 + max_views_in_run)` | Proven absolute reach, without raw-million dominance. |
| Engagement score | weighted capped rates: likes 40%, comments 25%, shares 35%; then multiplied by `min(1, sqrt(views / 10,000))` | Reaction quality, stabilised for small samples. |
| Freshness score | `100 × exp(-age_hours / 336)` | Recency only; unavailable without a valid publication time. |
| Momentum proxy | log-normalised `views / max(1, age_hours)` | Age-normalised reach from one observation. It is **not** true growth velocity. |

Rate caps are 10% likes, 2% comments and 2% shares. They make the component
bounded; a small video with an extreme percentage cannot receive an unlimited
boost. A video under 10,000 views is classified `LOW_SIGNAL`, even when its
raw rates are high.

## Ranking and confidence

```
final_score = 0.30 × reach
            + 0.30 × engagement
            + 0.20 × freshness
            + 0.20 × momentum_proxy
```

Confidence is `HIGH` only when views are at least 10,000, publication time is
known and all three reaction metrics are available. `MEDIUM` means the core
evidence exists with a limitation. `LOW` means no views or fewer than two
reaction metrics.

Classifications are deliberately separate from ranking:

- `EMERGING`: very fresh with strong age-normalised reach;
- `CURRENT`: recent with a meaningful proxy;
- `PROVEN`: established reach and engagement;
- `EVERGREEN`: old, proven reference;
- `LOW_SIGNAL`: insufficient strength or volume for priority;
- `INSUFFICIENT_DATA`: views or required reaction evidence is missing.

There is no true velocity, acceleration, semantic pattern clustering or causal
claim in this model. Those would require repeated observations or a separately
validated analysis slice.

"""Deterministic, explainable ranking for manual Trend Radar review.

The radar has one observation per video.  ``momentum_proxy`` is therefore
age-normalised reach, not observed growth velocity.
"""

import math


MIN_EVIDENCE_VIEWS = 10_000


def compute_scores(videos: list[dict]) -> list[dict]:
    """Mutate and return videos in stable, reproducible manual-review order."""
    if not videos:
        return videos

    max_views = max((max(0, _number(v.get('views'))) for v in videos), default=0)
    for video in videos:
        _score_video(video, max_views)

    # Python's stable sort keeps collector order for completely equal records.
    videos.sort(key=lambda video: _number(video.get('final_score')), reverse=True)
    return videos


def _score_video(video: dict, max_views: int) -> None:
    views = max(0, _number(video.get('views')))
    likes, comments, shares = (_metric(video, name) for name in ('likes', 'comments', 'shares'))
    known_reactions = [value for value in (likes, comments, shares) if value is not None]
    missing_fields = [name for name, value in (('views', video.get('views')), ('likes', likes), ('comments', comments), ('shares', shares)) if value is None]

    like_rate = _rate(likes, views)
    comment_rate = _rate(comments, views)
    share_rate = _rate(shares, views)
    total_engagement_rate = sum(known_reactions) / views if views > 0 and known_reactions else None
    volume_factor = min(1.0, math.sqrt(views / MIN_EVIDENCE_VIEWS)) if views else 0.0

    reach_score = _percentile_log(views, max_views)
    engagement_raw = _engagement_score(like_rate, comment_rate, share_rate)
    engagement_score = round(engagement_raw * volume_factor, 2)
    freshness_score = _freshness_score(video.get('age_hours'), video.get('freshness_known'))
    momentum_proxy = _momentum_proxy(views, max_views, video.get('age_hours'), video.get('freshness_known'))
    confidence = _confidence(views, like_rate, comment_rate, share_rate, video.get('freshness_known'))

    if views <= 0:
        final_score = 0.0
        classification = 'INSUFFICIENT_DATA'
    else:
        final_score = round(
            reach_score * 0.30 + engagement_score * 0.30
            + freshness_score * 0.20 + momentum_proxy * 0.20,
            2,
        )
        classification = _classification(views, freshness_score, momentum_proxy, engagement_score, confidence)

    video.update(
        like_rate=like_rate,
        comment_rate=comment_rate,
        share_rate=share_rate,
        total_engagement_rate=total_engagement_rate,
        engagement_rate=total_engagement_rate or 0.0,  # legacy field
        comment_density=comment_rate or 0.0,  # legacy field
        viral_score=_viral_score(video),
        reach_score=reach_score,
        engagement_score=engagement_score,
        freshness_score=freshness_score,
        momentum_proxy=momentum_proxy,
        data_confidence=confidence,
        classification=classification,
        final_score=final_score,
        subscriber_potential=round((reach_score * 0.6 + engagement_score * 0.4) / 10, 2),
        score_breakdown={
            'reach_score': reach_score,
            'engagement_score': engagement_score,
            'freshness_score': freshness_score,
            'momentum_proxy': momentum_proxy,
            'data_confidence': confidence,
            'volume_factor': round(volume_factor, 4),
            'ranking_weights': {'reach': 0.30, 'engagement': 0.30, 'freshness': 0.20, 'momentum_proxy': 0.20},
        },
        missing_fields=missing_fields,
        ranking_reasons=_reasons(reach_score, engagement_score, freshness_score, momentum_proxy, confidence, missing_fields),
        caveats=_caveats(views, video.get('freshness_known'), shares, missing_fields),
    )


def _number(value) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _metric(video: dict, name: str) -> int | None:
    value = video.get(name)
    return None if value is None else max(0, int(_number(value)))


def _rate(metric: int | None, views: float) -> float | None:
    return round(metric / views, 6) if metric is not None and views > 0 else None


def _percentile_log(views: float, max_views: int) -> float:
    return round(100 * math.log1p(views) / math.log1p(max_views), 2) if views and max_views else 0.0


def _engagement_score(like_rate, comment_rate, share_rate) -> float:
    # Saturation points are explicit; unavailable metrics do not become zero.
    parts = [(like_rate, 0.10, 0.40), (comment_rate, 0.02, 0.25), (share_rate, 0.02, 0.35)]
    available = [(min(rate / cap, 1.0), weight) for rate, cap, weight in parts if rate is not None]
    if not available:
        return 0.0
    weight_total = sum(weight for _, weight in available)
    return round(100 * sum(score * weight for score, weight in available) / weight_total, 2)


def _freshness_score(age_hours, freshness_known) -> float:
    if not freshness_known or age_hours is None:
        return 0.0
    age = max(0.0, _number(age_hours))
    return round(100 * math.exp(-age / (14 * 24)), 2)


def _momentum_proxy(views, max_views, age_hours, freshness_known) -> float:
    if not views or not max_views or not freshness_known or age_hours is None:
        return 0.0
    # A +1 hour floor prevents an unbounded score for newly indexed videos.
    rate = views / max(1.0, _number(age_hours))
    max_rate = max_views / 1.0
    return round(100 * math.log1p(rate) / math.log1p(max_rate), 2)


def _confidence(views, like_rate, comment_rate, share_rate, freshness_known) -> str:
    metric_count = sum(rate is not None for rate in (like_rate, comment_rate, share_rate))
    if not views or metric_count < 2:
        return 'LOW'
    if views >= MIN_EVIDENCE_VIEWS and freshness_known and metric_count == 3:
        return 'HIGH'
    return 'MEDIUM'


def _classification(views, freshness, momentum, engagement, confidence) -> str:
    if confidence == 'LOW':
        return 'INSUFFICIENT_DATA' if views < MIN_EVIDENCE_VIEWS else 'LOW_SIGNAL'
    if views < MIN_EVIDENCE_VIEWS:
        return 'LOW_SIGNAL'
    if freshness >= 80 and momentum >= 45:
        return 'EMERGING'
    if freshness >= 35 and momentum >= 25:
        return 'CURRENT'
    if freshness < 15 and views >= MIN_EVIDENCE_VIEWS:
        return 'EVERGREEN'
    if views >= MIN_EVIDENCE_VIEWS and engagement >= 35:
        return 'PROVEN'
    return 'LOW_SIGNAL'


def _viral_score(video: dict) -> float | None:
    followers = _metric(video, 'author_followers')
    views = _number(video.get('views'))
    return round(views / followers, 4) if followers and views else None


def _reasons(reach, engagement, freshness, momentum, confidence, missing) -> list[str]:
    reasons = []
    if reach >= 70: reasons.append('высокий подтверждённый охват')
    if engagement >= 70: reasons.append('сильная стабилизированная вовлечённость')
    if freshness >= 70: reasons.append('свежая публикация')
    if momentum >= 45: reasons.append('высокий age-normalized reach (momentum proxy)')
    if not reasons: reasons.append('недостаточно сильных компонент для приоритета')
    if confidence != 'HIGH': reasons.append(f'confidence {confidence.lower()}')
    if missing: reasons.append('есть неполные метрики')
    return reasons


def _caveats(views, freshness_known, shares, missing) -> list[str]:
    caveats = ['momentum proxy основан на одном наблюдении и не является true growth velocity']
    if views < MIN_EVIDENCE_VIEWS: caveats.append('малый объём просмотров понижает вклад engagement')
    if not freshness_known: caveats.append('дата публикации недоступна: freshness и momentum proxy не оценены')
    if shares is None: caveats.append('shares отсутствуют и не интерпретируются как ноль')
    if missing: caveats.append('неполные исходные метрики ограничивают сравнение')
    return caveats

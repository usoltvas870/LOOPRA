"""Structured, secret-free evidence for one Trend Radar run."""

import json
from datetime import datetime, timezone
from pathlib import Path

from utils import get_config


FRESHNESS_BUCKETS = ('emerging', 'current', 'recent_evergreen', 'historical_evergreen', 'unknown')


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso(value: datetime | None = None) -> str:
    return (value or utc_now()).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def normalize_published_at(value) -> str | None:
    if value in (None, ''):
        return None
    try:
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if isinstance(value, (int, float)):
            # TikTok createTime is a Unix timestamp in seconds; milliseconds are accepted too.
            seconds = value / 1000 if value > 10_000_000_000 else value
            return utc_iso(datetime.fromtimestamp(seconds, timezone.utc))
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            return None
        return utc_iso(parsed.astimezone(timezone.utc))
    except (ValueError, OverflowError, OSError, TypeError):
        return None


def apply_freshness(video: dict, collected_at: str) -> dict:
    published_at = normalize_published_at(video.get('published_at') or video.get('publish_time'))
    video['published_at'] = published_at
    video['collected_at'] = collected_at
    if not published_at:
        video.update(age_hours=None, age_days=None, freshness_bucket='unknown', freshness_known=False)
        return video
    try:
        age_hours = max(0.0, (datetime.fromisoformat(collected_at.replace('Z', '+00:00')) - datetime.fromisoformat(published_at.replace('Z', '+00:00'))).total_seconds() / 3600)
    except ValueError:
        video.update(age_hours=None, age_days=None, freshness_bucket='unknown', freshness_known=False)
        return video
    bucket = 'emerging' if age_hours <= 72 else 'current' if age_hours <= 14 * 24 else 'recent_evergreen' if age_hours <= 90 * 24 else 'historical_evergreen'
    video.update(age_hours=round(age_hours, 2), age_days=round(age_hours / 24, 2), freshness_bucket=bucket, freshness_known=True)
    return video


def evidence_path(run_id: str) -> Path:
    base = Path(get_config('RADAR_EVIDENCE_DIR', str(Path(__file__).resolve().parent.parent / 'data' / 'runs')))
    base.mkdir(parents=True, exist_ok=True)
    return base / f'run_{run_id}.json'


def write_journal(run: dict) -> str:
    path = evidence_path(run['run_id'])
    # Data comes from normalized fields only; do not include cookies, headers or query strings.
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)

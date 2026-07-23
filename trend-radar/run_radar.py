#!/usr/bin/env python3
"""
Nura TikTok Viral Screening Radar — MVP

Сбор и анализ TikTok-роликов для поиска вирусного контента.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils import (
    load_env, setup_logging, get_config_int, get_config_bool,
    read_source_file,
)
from storage import init_db, get_connection, save_video, save_run_evidence
from collector import RadarOperationalError, TikTokCollector
from scoring import compute_scores
from ai_analyzer import analyze_top_videos
from telegram import send_digest
from report import generate_report, save_report, save_xlsx, save_ai_analyses, save_scenarios_xlsx, save_carousel_texts
from run_data import utc_iso, write_journal

logger = logging.getLogger('run_radar')


def finish(reason: str, exit_code: int) -> int:
    print(f'RADAR_RESULT={reason}')
    return exit_code


def format_console_summary(total: int, videos_found: int, new_videos: int, top_videos: int) -> str:
    """Return an ASCII-only final summary safe for legacy Windows consoles."""
    return '\n'.join((
        f'Sources:     {total}',
        f'Found:       {videos_found}',
        f'New:         {new_videos}',
        f'Top report:  {top_videos}',
    ))


async def main() -> int:
    load_env()
    setup_logging()

    logger.info('=' * 60)
    logger.info('Nura TikTok Viral Screening Radar — MVP')
    logger.info('=' * 60)

    competitors = read_source_file('competitors.txt')
    hashtags = read_source_file('hashtags.txt')
    keywords = read_source_file('keywords.txt')
    rotational_raw = read_source_file('rotational.txt')

    rotational_h = [e for e in rotational_raw if len(e.split()) == 1]
    rotational_k = [e for e in rotational_raw if len(e.split()) > 1]

    logger.info(f'Competitors: {len(competitors)}, '
                f'Hashtags: {len(hashtags)}, '
                f'Keywords: {len(keywords)}, '
                f'Rotational: {len(rotational_h)} hashtags + {len(rotational_k)} keywords')

    sources = {
        'competitors': competitors,
        'hashtags': hashtags,
        'keywords': keywords,
        'rotational': {'hashtags': rotational_h, 'keywords': rotational_k},
    }

    total = len(competitors) + len(hashtags) + len(keywords) + len(rotational_raw)
    if total == 0:
        logger.warning('No sources found. Fill config files in config/')
        return finish('collection_failed', 3)

    init_db()
    conn = get_connection()
    started_at = utc_iso()
    started_clock = datetime.now()

    collector = None
    collection_duration_ms = 0
    shutdown_duration_ms = 0
    try:
        headless = get_config_bool('HEADLESS', True)
        collector = TikTokCollector(headless=headless)

        try:
            await collector.start()
            videos = await collector.collect_all(sources)
            videos = await collector.enrich_missing_stats(videos)
            collection_duration_ms = int((datetime.now() - started_clock).total_seconds() * 1000)
        except RadarOperationalError as e:
            logger.error(str(e))
            code = 4 if e.reason == 'authentication_timeout' else 2
            failed = {'run_id': collector.run_id, 'started_at': started_at, 'completed_at': utc_iso(),
                      'duration_ms': int((datetime.now() - started_clock).total_seconds() * 1000),
                      'mode': 'headless' if headless else 'visible', 'result': e.reason, 'exit_code': code,
                      'source_attempts': getattr(collector, 'source_attempts', []), 'provenance': []}
            journal_path = write_journal(failed)
            if hasattr(conn, 'execute'):
                save_run_evidence(conn, failed, journal_path)
                conn.commit()
            return finish(e.reason, code)
        finally:
            if collector:
                shutdown_started = datetime.now()
                await collector.close()
                shutdown_duration_ms = int((datetime.now() - shutdown_started).total_seconds() * 1000)

        logger.info(f'Total videos collected: {len(videos)}')
        if not videos:
            reason = collector.last_collection_reason or 'no_videos_found'
            logger.warning(f'No videos found. Reason: {reason}')
            return finish(reason, 3)

        new_count = 0
        for v in videos:
            is_new = save_video(conn, v)
            if is_new:
                new_count += 1
            if v.get('provenance'):
                v['provenance']['new_to_database'] = is_new
        conn.commit()

        logger.info(f'New videos saved: {new_count}')

        def _is_playlist(v: dict) -> bool:
            if v.get('is_playlist'):
                return True
            caption = v.get('caption') or ''
            return caption.startswith('[Playlist]')

        real_videos = [v for v in videos if not _is_playlist(v)]
        playlists = [v for v in videos if _is_playlist(v)]

        min_views = get_config_int('MIN_VIEWS', 10000)

        scored = compute_scores(real_videos)
        with_views = [
            v for v in scored
            if v.get('views') is not None and v['views'] >= min_views
        ]
        without_views = [
            v for v in scored
            if v.get('views') is None
        ]
        top_videos = (with_views[:30] + without_views[:max(0, 30 - len(with_views))])[:30]

        logger.info(f'Videos with views >= {min_views}: {len(with_views)}, '
                    f'without views: {len(without_views)}, '
                    f'playlists: {len(playlists)}, '
                    f'in report: {len(top_videos)}')

        ai_analyses = []
        if get_config_bool('ENABLE_AI_ANALYSIS', False) and top_videos:
            logger.info('Running AI analysis on top 10...')
            ai_analyses = await analyze_top_videos(top_videos[:10])

        stats = {
            'date': collector.collected_at,
            'run_id': collector.run_id,
            'sources_processed': total,
            'videos_found': len(videos),
            'new_videos': new_count,
            'min_views': min_views,
            'mode': get_config_bool('HEADLESS', True) and 'headless' or 'visible',
            'source_attempts': getattr(collector, 'source_attempts', []),
            'provenance': getattr(collector, 'provenance', []),
            'started_at': started_at,
            'completed_at': utc_iso(),
            'duration_ms': int((datetime.now() - started_clock).total_seconds() * 1000),
            'collection_duration_ms': collection_duration_ms,
            'shutdown_duration_ms': shutdown_duration_ms,
            'raw_discoveries': sum(
                attempt.get('raw_items_received', 0)
                for attempt in getattr(collector, 'source_attempts', [])
            ),
            'unique_discoveries': len(videos),
            'duplicates_in_run': sum(
                attempt.get('duplicates_already_seen_in_run', 0)
                + attempt.get('duplicates_within_source', 0)
                for attempt in getattr(collector, 'source_attempts', [])
            ),
            'already_known': len(videos) - new_count,
            'freshness_summary': {
                bucket: sum(1 for video in videos if video.get('freshness_bucket') == bucket)
                for bucket in (
                    'emerging', 'current', 'recent_evergreen',
                    'historical_evergreen', 'unknown',
                )
            },
            'run_videos': [
                {
                    'video_id': video.get('video_id'),
                    'canonical_url': video.get('url'),
                    'published_at': video.get('published_at'),
                    'age_hours': video.get('age_hours'),
                    'age_days': video.get('age_days'),
                    'freshness_bucket': video.get('freshness_bucket'),
                    'freshness_known': video.get('freshness_known'),
                    'new_to_database': bool(
                        video.get('provenance', {}).get('new_to_database')
                    ),
                }
                for video in videos
            ],
        }

        export_started = datetime.now()
        report_md = generate_report(stats, top_videos, ai_analyses, playlists)
        report_path = save_report(report_md)

        analysis_map = {}
        if ai_analyses:
            for a in ai_analyses:
                analysis_map[a.get('video_id')] = a

        if get_config_bool('EXPORT_XLSX', True):
            xlsx_path = save_xlsx(top_videos, analysis_map, stats)
        else:
            xlsx_path = None

        if ai_analyses:
            try:
                ai_dir = save_ai_analyses(top_videos, analysis_map)
            except Exception as e:
                logger.error(f'Failed to save AI analysis files: {e}')
                ai_dir = None
        else:
            ai_dir = None

        try:
            scenarios_path = save_scenarios_xlsx(top_videos, analysis_map)
        except Exception as e:
            logger.error(f'Failed to save scenarios XLSX: {e}')
            scenarios_path = None

        try:
            carousel_dir = save_carousel_texts(top_videos, analysis_map)
        except Exception as e:
            logger.error(f'Failed to save carousel texts: {e}')
            carousel_dir = None

        print()
        logger.info('=' * 60)
        logger.info(f'REPORT: {report_path}')
        if xlsx_path:
            logger.info(f'XLSX:   {xlsx_path}')
        if ai_dir:
            logger.info(f'AI:     {ai_dir}')
        if scenarios_path:
            logger.info(f'SCENARIOS: {scenarios_path}')
        if carousel_dir:
            logger.info(f'CAROUSELS: {carousel_dir}')
        logger.info('=' * 60)
        print()
        print(format_console_summary(total, len(videos), new_count, len(top_videos)))
        print()

        if top_videos:
            print('TOP-5:')
            for i, v in enumerate(top_videos[:5]):
                cap = (v.get('caption') or '\u0411\u0435\u0437 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u044f')[:60]
                print(f'  {i + 1}. {cap}')
                print(f'     Views: {v.get("views", "?")}  '
                      f'Score: {v.get("final_score", 0)}  '
                      f'@{v.get("author_username", "?")}')
                print()

        # ── export top-10 for Video Pipeline ──
        try:
            import json as _json

            trend_data_path = Path(__file__).parent / 'data' / 'trend_top.json'
            trend_data_path.parent.mkdir(parents=True, exist_ok=True)
            export_data = []
            for v in top_videos[:10]:
                export_data.append({
                    'video_id': v.get('video_id'),
                    'url': v.get('url'),
                    'author_username': v.get('author_username'),
                    'caption': v.get('caption'),
                    'views': v.get('views'),
                    'likes': v.get('likes'),
                    'comments': v.get('comments'),
                    'shares': v.get('shares'),
                    'engagement_rate': v.get('engagement_rate'),
                    'comment_density': v.get('comment_density'),
                    'viral_score': v.get('viral_score'),
                    'final_score': v.get('final_score'),
                    'subscriber_potential': v.get('subscriber_potential'),
                    'source_type': v.get('source_type'),
                    'source_value': v.get('source_value'),
                    'ai_analysis': v.get('ai_analysis'),
                })
            with open(trend_data_path, 'w', encoding='utf-8') as f:
                _json.dump(export_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Trend top-10 exported: {trend_data_path}")
        except Exception as e:
            logger.warning(f"Failed to export trend top-10: {e}")

        if get_config_bool('ENABLE_TELEGRAM', False):
            logger.info('Sending Telegram digest...')
            await send_digest(top_videos, ai_analyses)

        stats.update(
            result='success',
            exit_code=0,
            completed_at=utc_iso(),
            duration_ms=int((datetime.now() - started_clock).total_seconds() * 1000),
            export_duration_ms=int((datetime.now() - export_started).total_seconds() * 1000),
        )
        journal_path = write_journal(stats)
        if hasattr(conn, 'execute'):
            save_run_evidence(conn, stats, journal_path)
        conn.commit()
        logger.info('Done! Journal: %s', journal_path)
        return finish('success', 0)
    except Exception:
        logger.exception('Unexpected radar failure')
        return finish('internal_error', 1)
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))

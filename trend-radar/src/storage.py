import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'videos.db'


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                url TEXT UNIQUE NOT NULL,
                platform TEXT DEFAULT 'tiktok',
                source_type TEXT NOT NULL,
                source_value TEXT NOT NULL,
                author_username TEXT,
                caption TEXT,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                publish_time TEXT,
                author_followers INTEGER,
                is_playlist INTEGER DEFAULT 0,
                collected_at TEXT NOT NULL,
                run_id TEXT NOT NULL
            )
        ''')
        conn.execute('''CREATE TABLE IF NOT EXISTS radar_runs (
            run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, completed_at TEXT,
            duration_ms INTEGER, mode TEXT, result TEXT, exit_code INTEGER, journal_path TEXT
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS source_attempts (
            run_id TEXT NOT NULL, ordinal INTEGER NOT NULL, source_type TEXT NOT NULL,
            source_value TEXT NOT NULL, started_at TEXT, completed_at TEXT, duration_ms INTEGER,
            requested_limit INTEGER, raw_items_received INTEGER, parsed_items INTEGER,
            items_with_valid_url INTEGER, unique_within_source INTEGER, duplicates_within_source INTEGER,
            unique_added_to_run INTEGER, duplicates_already_seen_in_run INTEGER, items_rejected INTEGER,
            rejection_reasons TEXT, collection_method TEXT, status TEXT, error_reason TEXT,
            final_page_url TEXT, authentication_state TEXT,
            PRIMARY KEY (run_id, ordinal)
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS run_video_provenance (
            run_id TEXT NOT NULL, video_id TEXT NOT NULL, canonical_url TEXT NOT NULL,
            primary_source_type TEXT, primary_source_value TEXT, first_discovery_ordinal INTEGER,
            matched_sources TEXT NOT NULL, discovery_methods TEXT NOT NULL, repeat_discoveries INTEGER NOT NULL,
            new_to_database INTEGER NOT NULL, PRIMARY KEY (run_id, canonical_url)
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_video_id ON videos(video_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_run_id ON videos(run_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_url ON videos(url)')
        try:
            conn.execute('ALTER TABLE videos ADD COLUMN is_playlist INTEGER DEFAULT 0')
        except Exception:
            pass
        try:
            conn.execute('ALTER TABLE videos ADD COLUMN published_at TEXT')
        except Exception:
            pass
        conn.commit()
        logger.info("Database initialized")
    finally:
        conn.close()


def save_video(conn: sqlite3.Connection, video: dict) -> bool:
    try:
        before = conn.total_changes
        conn.execute('''
            INSERT OR IGNORE INTO videos
            (video_id, url, platform, source_type, source_value,
             author_username, caption, views, likes, comments, shares,
             publish_time, author_followers, is_playlist, collected_at, run_id, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video.get('video_id'),
            video['url'],
            video.get('platform', 'tiktok'),
            video['source_type'],
            video['source_value'],
            video.get('author_username'),
            video.get('caption'),
            video.get('views'),
            video.get('likes'),
            video.get('comments'),
            video.get('shares'),
            video.get('publish_time'),
            video.get('author_followers'),
            1 if video.get('is_playlist') else 0,
            video['collected_at'],
            video['run_id'],
            video.get('published_at'),
        ))
        return conn.total_changes > before
    except Exception as e:
        logger.error(f"Failed to save video {video.get('url')}: {e}")
        return False


def save_run_evidence(conn: sqlite3.Connection, run: dict, journal_path: str) -> None:
    conn.execute('INSERT OR REPLACE INTO radar_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
        run['run_id'], run['started_at'], run.get('completed_at'), run.get('duration_ms'), run.get('mode'),
        run.get('result'), run.get('exit_code'), journal_path,
    ))
    for attempt in run.get('source_attempts', []):
        values = [attempt.get(key) for key in (
            'run_id', 'ordinal', 'source_type', 'source_value', 'started_at', 'completed_at', 'duration_ms',
            'requested_limit', 'raw_items_received', 'parsed_items', 'items_with_valid_url', 'unique_within_source',
            'duplicates_within_source', 'unique_added_to_run', 'duplicates_already_seen_in_run', 'items_rejected',
            'collection_method', 'status', 'error_reason', 'final_page_url', 'authentication_state')]
        values.insert(16, __import__('json').dumps(attempt.get('rejection_reasons', {}), ensure_ascii=False))
        conn.execute(
            'INSERT OR REPLACE INTO source_attempts VALUES ('
            + ','.join('?' * len(values))
            + ')',
            values,
        )
    for item in run.get('provenance', []):
        conn.execute('INSERT OR REPLACE INTO run_video_provenance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
            run['run_id'], item.get('video_id'), item['canonical_url'], item.get('primary_source_type'), item.get('primary_source_value'),
            item.get('first_discovery_ordinal'), __import__('json').dumps(item.get('matched_sources', []), ensure_ascii=False),
            __import__('json').dumps(item.get('discovery_methods', []), ensure_ascii=False), item.get('repeat_discoveries', 0),
            1 if item.get('new_to_database') else 0,
        ))


def get_videos_by_run_id(conn: sqlite3.Connection, run_id: str) -> list[dict]:
    cursor = conn.execute(
        'SELECT * FROM videos WHERE run_id = ? ORDER BY id', (run_id,)
    )
    return [dict(row) for row in cursor.fetchall()]


def get_top_videos(
    conn: sqlite3.Connection,
    run_id: str,
    limit: int = 30,
    min_views: int = 10000,
) -> list[dict]:
    cursor = conn.execute(
        'SELECT * FROM videos WHERE run_id = ? AND views >= ? ORDER BY views DESC LIMIT ?',
        (run_id, min_views, limit),
    )
    return [dict(row) for row in cursor.fetchall()]

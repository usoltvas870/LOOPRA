"""Endpoint-aware TikTok video normalisation.

Only a self-contained video object with its own ID and ``author.uniqueId`` is
accepted.  Containers, music/challenge IDs and display names are never used as
fallback identity.
"""

import json
import logging
import re
from typing import Any, Optional
from urllib.parse import quote

from run_data import normalize_published_at

logger = logging.getLogger(__name__)
_VIDEO_ID = re.compile(r'^\d{15,25}$')
_USERNAME = re.compile(r'^[A-Za-z0-9._-]+$')


def extract_from_api_responses(api_data, source_type: str, source_value: str) -> list[dict]:
    """Parse captured endpoint bodies; unsupported schema is intentionally skipped."""
    videos = []
    for captured in api_data:
        endpoint, body = captured if isinstance(captured, tuple) else ('unknown', captured)
        for item, path in _endpoint_items(body):
            video = _parse_item(item, endpoint=endpoint, object_path=path)
            if video:
                video.update(source_type=source_type, source_value=source_value)
                videos.append(video)
    return videos


def _endpoint_items(body: Any):
    if not isinstance(body, dict):
        return []
    candidates = []
    for key, path in (('itemList', '$.itemList[]'), ('items', '$.items[]'), ('data', '$.data[]')):
        value = body.get(key)
        if isinstance(value, list):
            candidates.extend((item, path) for item in value if isinstance(item, dict))
    return candidates


def _video_struct(item: dict) -> tuple[dict | None, str]:
    if isinstance(item.get('item'), dict):
        item = item['item']; prefix = '.item'
    else:
        prefix = ''
    if isinstance(item.get('itemInfo', {}).get('itemStruct'), dict):
        return item['itemInfo']['itemStruct'], prefix + '.itemInfo.itemStruct'
    if isinstance(item.get('aweme_info'), dict):
        return item['aweme_info'], prefix + '.aweme_info'
    # A direct item is accepted only when it carries the complete video identity.
    if isinstance(item.get('author'), dict) and (isinstance(item.get('stats'), dict) or 'createTime' in item):
        return item, prefix
    return None, prefix


def _parse_item(item: dict, endpoint: str = 'unknown', object_path: str = '$') -> Optional[dict]:
    struct, suffix = _video_struct(item)
    if not struct:
        return None
    video_id = str(struct.get('id') or '')
    author = struct.get('author') or {}
    username = str(author.get('uniqueId') or '').lstrip('@')
    if not _VIDEO_ID.fullmatch(video_id) or not _USERNAME.fullmatch(username):
        return None
    stats = struct.get('stats') or struct.get('statistics') or {}
    if not isinstance(stats, dict):
        return None
    share_url = struct.get('share_url') or struct.get('shareUrl')
    canonical = _canonical_url(share_url, username, video_id)
    create_time = next((value for value in (stats.get('createTime'), struct.get('createTime'), struct.get('create_time')) if value is not None), None)
    author_stats = struct.get('authorStats') or {}
    return {
        'video_id': video_id,
        'url': canonical,
        'canonical_url': canonical,
        'fallback_url': f'https://www.tiktok.com/@/video/{video_id}',
        'author_username': username,
        'author_display_name': author.get('nickname'),
        'caption': struct.get('desc') or struct.get('description') or struct.get('text'),
        'views': _safe_int(stats.get('playCount') or stats.get('play_count') or stats.get('views')),
        'likes': _safe_int(stats.get('diggCount') or stats.get('digg_count') or stats.get('likes')),
        'comments': _safe_int(stats.get('commentCount') or stats.get('comment_count') or stats.get('comments')),
        'shares': _safe_int(stats.get('shareCount') or stats.get('share_count') or stats.get('shares')),
        'publish_time': str(create_time or ''),
        'published_at': normalize_published_at(create_time),
        'author_followers': _safe_int(author_stats.get('followerCount') or stats.get('followerCount')),
        'identity_source_endpoint': endpoint,
        'video_id_source_path': object_path + suffix + '.id',
        'author_source_path': object_path + suffix + '.author.uniqueId',
        'identity_confidence': 'HIGH',
        'canonical_url_status': 'UNVALIDATED',
        'identity_warnings': [],
    }


def _canonical_url(share_url, username: str, video_id: str) -> str:
    if isinstance(share_url, str):
        match = re.match(r'https?://(?:www\.)?tiktok\.com/@([^/?]+)/video/(\d+)(?:\?|$)', share_url)
        if match and match.group(2) == video_id and _USERNAME.fullmatch(match.group(1)):
            return share_url.split('?', 1)[0]
    return f'https://www.tiktok.com/@{quote(username)}/video/{video_id}'


async def extract_video_data(page: Any, source_type: str, source_value: str) -> list[dict]:
    # SSR/DOM fallbacks are deliberately diagnostic-only: without endpoint identity
    # provenance they cannot enter the user-facing manual-review ranking.
    return []


def parse_detail_page_stats(json_data: dict) -> dict | None:
    for item, path in _endpoint_items(json_data):
        video = _parse_item(item, endpoint='detail_page', object_path=path)
        if video:
            return video
    struct = json_data.get('__DEFAULT_SCOPE__', {}).get('webapp.video-detail', {}).get('itemInfo', {}).get('itemStruct')
    return _parse_item(struct, endpoint='detail_page', object_path='$.webapp.video-detail.itemInfo.itemStruct') if isinstance(struct, dict) else None


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None

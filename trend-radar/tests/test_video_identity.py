import sys
import unittest
from pathlib import Path

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT / 'src'))

from parser import extract_from_api_responses


VIDEO_ID = '7261234567890123456'


def video(**overrides):
    value = {
        'id': VIDEO_ID, 'author': {'uniqueId': 'valid.author', 'nickname': 'Display Name'},
        'stats': {'playCount': 100, 'diggCount': 10, 'commentCount': 2, 'shareCount': 1, 'createTime': 1_700_000_000},
        'desc': 'caption',
    }
    value.update(overrides)
    return value


class VideoIdentityTests(unittest.TestCase):
    def test_supported_item_has_same_object_identity_and_canonical_url(self):
        items = extract_from_api_responses([('/api/search/general/full', {'data': [{'item': video()}]})], 'keyword', 'test')
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item['video_id'], VIDEO_ID)
        self.assertEqual(item['author_username'], 'valid.author')
        self.assertEqual(item['url'], f'https://www.tiktok.com/@valid.author/video/{VIDEO_ID}')
        self.assertEqual(item['identity_confidence'], 'HIGH')

    def test_nested_music_or_challenge_ids_are_rejected(self):
        bad = {'id': 'challenge-1', 'music': {'id': VIDEO_ID}, 'author': {'uniqueId': 'valid.author'}, 'stats': {}}
        self.assertEqual(extract_from_api_responses([('/challenge/item_list', {'itemList': [bad]})], 'hashtag', 'x'), [])

    def test_nickname_is_not_an_identity_fallback(self):
        item = video(author={'nickname': 'Display Name'})
        self.assertEqual(extract_from_api_responses([('/api/search/general/full', {'data': [item]})], 'keyword', 'x'), [])

    def test_unknown_container_and_invalid_id_are_rejected(self):
        self.assertEqual(extract_from_api_responses([('/api/unknown', {'data': [{'entity': video()}]})], 'keyword', 'x'), [])
        self.assertEqual(extract_from_api_responses([('/api/search/general/full', {'data': [video(id='42')]})], 'keyword', 'x'), [])

    def test_share_url_must_match_the_same_video(self):
        item = video(share_url='https://www.tiktok.com/@other/video/7261234567890123457?x=1')
        result = extract_from_api_responses([('/api/search/general/full', {'data': [item]})], 'keyword', 'x')[0]
        self.assertEqual(result['url'], f'https://www.tiktok.com/@valid.author/video/{VIDEO_ID}')

import math
import sys
import unittest
from pathlib import Path

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RADAR_ROOT / 'src')]

from scoring import compute_scores


def video(video_id, views, likes, comments, shares, age_hours, **extra):
    result = {
        'video_id': video_id, 'url': f'https://example.test/video/{video_id}',
        'views': views, 'likes': likes, 'comments': comments, 'shares': shares,
        'age_hours': age_hours, 'freshness_known': age_hours is not None,
        'freshness_bucket': 'emerging' if age_hours is not None and age_hours <= 72 else 'historical_evergreen',
    }
    result.update(extra)
    return result


class ExplainableScoringTests(unittest.TestCase):
    def test_old_million_view_video_is_evergreen_not_emerging(self):
        result = compute_scores([video('old', 5_000_000, 250_000, 5_000, 10_000, 600 * 24)])[0]
        self.assertEqual(result['classification'], 'EVERGREEN')
        self.assertLess(result['freshness_score'], 1)

    def test_fresh_high_share_video_is_emerging(self):
        result = compute_scores([video('fresh', 120_000, 18_000, 1_200, 5_000, 8)])[0]
        self.assertEqual(result['classification'], 'EMERGING')
        self.assertGreater(result['momentum_proxy'], 45)

    def test_small_sample_is_stabilized(self):
        results = compute_scores([
            video('small', 8_000, 7_000, 500, 300, 2),
            video('proven', 200_000, 20_000, 2_000, 4_000, 24),
        ])
        small = next(result for result in results if result['video_id'] == 'small')
        proven = next(result for result in results if result['video_id'] == 'proven')
        self.assertLess(small['score_breakdown']['volume_factor'], 1)
        self.assertLess(small['engagement_score'], 100)
        self.assertNotEqual(small['classification'], 'EMERGING')
        self.assertGreater(proven['final_score'], small['final_score'])

    def test_missing_shares_are_not_measured_zero(self):
        result = compute_scores([video('missing', 100_000, 10_000, 1_000, None, 24)])[0]
        self.assertIsNone(result['share_rate'])
        self.assertIn('shares', result['missing_fields'])
        self.assertIn('shares отсутствуют и не интерпретируются как ноль', result['caveats'])

    def test_unknown_age_has_no_freshness_or_momentum(self):
        result = compute_scores([video('unknown', 100_000, 10_000, 1_000, 500, None)])[0]
        self.assertEqual(result['freshness_score'], 0)
        self.assertEqual(result['momentum_proxy'], 0)
        self.assertIn('дата публикации недоступна: freshness и momentum proxy не оценены', result['caveats'])

    def test_same_metrics_different_age_rank_deterministically(self):
        fresh, old = compute_scores([
            video('fresh', 100_000, 10_000, 1_000, 2_000, 8),
            video('old', 100_000, 10_000, 1_000, 2_000, 600 * 24),
        ])
        self.assertEqual(fresh['video_id'], 'fresh')
        self.assertGreater(fresh['final_score'], old['final_score'])

    def test_zero_and_invalid_values_never_create_nan(self):
        results = compute_scores([video('zero', 0, 0, 0, None, 1), video('bad', float('nan'), 1, 1, 1, 1)])
        for result in results:
            self.assertEqual(result['classification'], 'INSUFFICIENT_DATA')
            self.assertTrue(math.isfinite(result['final_score']))


if __name__ == '__main__':
    unittest.main()

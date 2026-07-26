import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src')]
from content_intelligence_review import ContentIntelligenceReviewError, create_review, finalize_review, validate_decisions

REPORT=ROOT/'data'/'content-intelligence-reports'/'content-intelligence-report-20260724_150816-bf8ca1f1950e'

def test_pending_package_is_deterministic_and_preserves_rank(tmp_path):
    first=create_review(report_root=REPORT,output_root=tmp_path); second=create_review(report_root=REPORT,output_root=tmp_path)
    assert first['status']=='COMPLETED' and second['status']=='REUSED'
    package=json.loads((tmp_path/first['review_id']/'review_package.json').read_text(encoding='utf-8'))
    assert package['final_status']=='PENDING_HUMAN_REVIEW' and package['reviewer']['human_confirmation'] is False
    assert [x['original_rank'] for x in package['candidate_reviews']]==[1,2,3,4,5]
    assert all(x['overall_decision']=='PENDING' for x in package['candidate_reviews'])

def test_synthetic_completed_review_validates_and_finalizes(tmp_path):
    created=create_review(report_root=REPORT,output_root=tmp_path); template=tmp_path/created['review_id']/'review_decisions.template.json'
    value=json.loads(template.read_text(encoding='utf-8')); value['reviewer'].update({'reviewer_id':'synthetic-editor','reviewer_role':'EDITOR','human_confirmation':True})
    for candidate in value['candidate_reviews']:
        candidate['overall_decision']='APPROVED_FOR_PRODUCTION_BRIEF'
        for dimension in candidate['dimension_reviews']: dimension['decision']='PASS'
    decision=tmp_path/'synthetic.json'; decision.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    assert validate_decisions(decision,require_completed=True)['completed'] is True
    assert finalize_review(decision_path=decision,output_root=tmp_path)['status']=='COMPLETED'

def test_completed_review_requires_human_confirmation(tmp_path):
    created=create_review(report_root=REPORT,output_root=tmp_path)
    with pytest.raises(ContentIntelligenceReviewError,match='COMPLETED'):
        validate_decisions(tmp_path/created['review_id']/'review_decisions.template.json',require_completed=True)

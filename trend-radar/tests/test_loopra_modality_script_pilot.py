import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src')]
from modality_understanding import assess_modality, build_text_consensus, normalize_confusables
from loopra_modality_script_pilot import PILOT_RANKS, run_pilot

def packet(rank=6): return {'batch_id':'b','item_id':f'rank-{rank:02d}','media_reference':'m','media_hash':'h','content_hash':'p','original_rank':rank,'video_id':'v','transcript_language':'ru','transcript_segments':[{'evidence_ref':'segment-1','text':'Это достаточно длинная авторская речь о конкретной теме.'}],'OCR_normalized_lines':[]}
def test_speech_led_priority(): assert assess_modality(packet=packet(),rank=6)['detected_modality']=='SPEECH_LED'
def test_music_asr_is_not_rank_two_meaning(): assert assess_modality(packet=packet(2),rank=2)['detected_modality']=='INSUFFICIENT'
def test_consensus_deduplicates_and_normalizes():
    value=build_text_consensus([{'normalized_text':'readable text','quality_status':'READABLE','timestamp_seconds':0,'observation_id':'x'},{'normalized_text':'readable text','quality_status':'READABLE','timestamp_seconds':1,'observation_id':'y'}])
    assert len(value['ordered_text_lines'])==1 and normalize_confusables('A')
def test_rank_nine_is_irrelevant_and_no_script(tmp_path):
    root=tmp_path/'evidence'; root.mkdir()
    import json
    for rank in PILOT_RANKS: (root/f'{rank:02d}.json').write_text(json.dumps(packet(rank)),encoding='utf-8')
    result=run_pilot(evidence_root=root,output_root=tmp_path,ranks=PILOT_RANKS)
    item=next(x for x in result['ranks'] if x['rank']==9); assert item['relevance']=='IRRELEVANT' and item['script_calls']==0
def test_exact_scope_required(tmp_path):
    import pytest
    with pytest.raises(ValueError): run_pilot(evidence_root=tmp_path,output_root=tmp_path,ranks=(2,))

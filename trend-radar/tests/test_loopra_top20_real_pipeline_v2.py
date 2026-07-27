from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'trend-radar/src'))
import loopra_top20_real_pipeline_v2 as v2
from loopra_top20_real_pipeline_v2 import *

def test_offline_v2_exactly_twenty_and_owner_gate(tmp_path):
 r=run_offline_acceptance(root=tmp_path)
 assert r['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW'
 assert [x['original_rank'] for x in r['acquisition']]==list(range(1,21))
 assert len(r['cards'])==len(r['review']['items'])==20
 assert r['review']['reviewer']['human_confirmation'] is False and r['review']['production_brief_allowed'] is False
 assert r['network_calls']==r['browser_calls']==r['provider_calls']==0 and r['credentials_required'] is False

def test_b1a_uses_v2_offline_contracts(tmp_path):
 from loopra_top20_b1_adapter import LoopraTop20B1Adapter
 assert LoopraTop20B1Adapter(runtime_root=tmp_path).run_v2_offline_acceptance()['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW'

def test_v2_rank_six_and_twenty_are_not_remapped(tmp_path):
 r=run_offline_acceptance(root=tmp_path)
 assert r['cards'][5]['original_rank']==6 and r['cards'][19]['original_rank']==20

def test_duplicate_and_rank_remap_are_rejected(tmp_path):
 entries=[{'candidate_id':str(i),'video_id':str(i),'original_rank':i} for i in range(1,21)]; entries[5]['original_rank']=1
 with pytest.raises(LoopraTop20V2Error): v2._validate(entries)
 entries=[{'candidate_id':'same','video_id':str(i),'original_rank':i} for i in range(1,21)]
 with pytest.raises(LoopraTop20V2Error): v2._validate(entries)

def test_failure_is_partial_and_resumable(tmp_path):
 r=run_offline_acceptance(root=tmp_path,fail_rank=7)
 assert r['status']=='PARTIAL' and r['failed_ranks']==[7] and r['acquisition'][6]['retryable_status']=='RESUMABLE'

def test_provider_created_fact_is_rejected(tmp_path):
 entries=[{'candidate_id':f'c{i}','video_id':f'v{i}','original_rank':i} for i in range(1,21)]; batch={'batch_id':'b','fresh_cycle_id':'c','project_context_hash':'h','semantic_hash':'s'}; acquisition=LoopraTop20MediaAcquisitionV2().run(root=tmp_path,batch=batch,entries=entries)
 with pytest.raises(LoopraTop20V2Error,match='SOURCE_FACT'):
  LoopraTop20ContentIntelligenceV2().run(root=tmp_path,batch=batch,entries=entries,acquisition=acquisition,provider=lambda _: {'claims':[{'claim_type':'FACT'}]})

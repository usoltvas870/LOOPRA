from pathlib import Path
import sys
import asyncio
import hashlib
import importlib.util
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import pytest
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'trend-radar/src'))
import loopra_top20_real_pipeline_v2 as v2
from loopra_top20_real_pipeline_v2 import *
from collector import RadarOperationalError, TikTokCollector

def test_navigation_propagates_authentication_timeout():
 class Page:
  url='https://www.tiktok.com/login'
  def on(self,*args): pass
  def remove_listener(self,*args): pass
  async def goto(self,*args,**kwargs): pass
  async def wait_for_selector(self,*args,**kwargs): pass
  async def close(self): pass
 collector=TikTokCollector(); collector.context=type('Context',(),{'new_page':AsyncMock(return_value=Page())})()
 collector._dismiss_overlays=AsyncMock(); collector._is_blocked=AsyncMock(return_value=(True,'login overlay detected')); collector._save_debug_screenshot=AsyncMock()
 async def run():
  with patch('collector.asyncio.sleep',AsyncMock()):
   await collector._navigate_and_extract('https://www.tiktok.com/tag/test','hashtag','test')
 with pytest.raises(RadarOperationalError) as error:
  asyncio.run(run())
 assert error.value.reason=='authentication_timeout' and collector.last_collection_reason=='authentication_timeout'

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

def test_same_orchestrator_uses_injected_boundaries_once_and_preserves_twenty(tmp_path):
 calls={name:0 for name in ('collect','select','acquire','inspect','ocr','transcribe','provider')}
 entries=[{'candidate_id':f'c{i:02d}','video_id':f'v{i:02d}','original_rank':i} for i in range(1,21)]
 def fake(name, value):
  def call(*args): calls[name]+=1; return value(*args) if callable(value) else value
  return call
 deps={'collect':fake('collect',entries),'select':fake('select',lambda _:entries),'acquire':fake('acquire',lambda e:{'status':'COMPLETED','source_media_reference':f'media/{e["original_rank"]:02d}.mp4','source_media_sha256':str(e['original_rank']),'duration_seconds':1,'ffprobe_status':'VALID','method':'fake'}),'inspect':fake('inspect',lambda _:{'status':'COMPLETED'}),'ocr':fake('ocr',lambda _:{'status':'COMPLETED'}),'transcribe':fake('transcribe',lambda _:{'status':'COMPLETED'}),'provider':fake('provider',lambda _:{'claims':[],'project_adaptation':{},'warnings':[]})}
 result=run_fresh_top20_b1(root=tmp_path,dependencies=deps,offline=True)
 assert result['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW' and len(result['cards'])==20
 assert calls['collect']==calls['select']==1 and all(calls[n]==20 for n in ('acquire','inspect','ocr','transcribe','provider'))

def test_real_requires_configured_canonical_boundaries(tmp_path):
 assert run_fresh_top20_b1(root=tmp_path)['status']=='BLOCKED'

def test_production_readiness_and_factory_expose_complete_canonical_set(tmp_path):
 readiness=validate_fresh_top20_b1_production_readiness(runtime_root=tmp_path)
 assert readiness['ready'] is True and readiness['runtime_root_git_ignored'] is True
 deps=build_fresh_top20_b1_production_dependencies(root=tmp_path)
 assert {'collect','select','acquire','inspect','ocr','transcribe','analyze_content_intelligence','close'} <= deps.keys()
 assert all(callable(value) for value in deps.values())

def test_readiness_returns_typed_missing_dependency(monkeypatch,tmp_path):
 services=v2._canonical_services(); services['post_deepseek_request']=None
 monkeypatch.setattr(v2,'_canonical_services',lambda:services)
 result=validate_fresh_top20_b1_production_readiness(runtime_root=tmp_path)
 assert result['ready'] is False and result['reason']=='B1_REAL_DEPENDENCY_MISSING:content_intelligence'

def test_production_wiring_calls_canonical_boundaries_and_reuses_without_side_effects(monkeypatch,tmp_path):
 calls={name:0 for name in ('start','collect_all','enrich_missing_stats','close','build_selection_manifest','write_selection_manifest','capture','inspect','ocr','prepare','build_analysis_input','post','validate')}
 candidates=[{'video_id':f'video-{rank:02d}','url':f'https://www.tiktok.com/@owner/video/{1000000000000000000+rank}','views':1000+rank,'likes':rank,'comments':rank,'shares':rank} for rank in range(1,21)]
 class Collector:
  def __init__(self,headless=True): self.run_id='fresh-run'; self.collected_at='2026-07-27T00:00:00Z'; self.source_attempts=[]; self.context=object()
  async def start(self): calls['start']+=1
  async def collect_all(self,sources): calls['collect_all']+=1; return list(candidates)
  async def enrich_missing_stats(self,values): calls['enrich_missing_stats']+=1; return values
  async def close(self): calls['close']+=1
 services=v2._canonical_services(); actual_build=services['build_selection_manifest']; actual_write=services['write_selection_manifest']
 def build(*args,**kwargs): calls['build_selection_manifest']+=1; return actual_build(*args,**kwargs)
 def write(*args,**kwargs): calls['write_selection_manifest']+=1; return actual_write(*args,**kwargs)
 def reusable(candidate_root,run_root,manifest_hash,video_id,maximum):
  value=v2._read_json(candidate_root/'acquisition_record.json')
  return {**value,'status':'REUSED'} if value else None
 async def capture(request,manifest,candidate,context,started_at=None):
  calls['capture']+=1; run_root=request.output_root/manifest.radar_run_id; candidate_root=run_root/candidate.video_id; candidate_root.mkdir(parents=True,exist_ok=True)
  media=candidate_root/'source.mp4'; media.write_bytes(b'bounded-test-media'); digest=hashlib.sha256(media.read_bytes()).hexdigest()
  record={'status':'COMPLETED','local_media_path':f'{candidate.video_id}/source.mp4','media_sha256':digest,'acquisition_method':'authenticated_browser_response','warnings':[],'errors':[]}
  (candidate_root/'acquisition_record.json').write_text(json.dumps(record),encoding='utf-8'); return record
 def inspect_media(media,output,video_id,canonical_url):
  calls['inspect']+=1; output.mkdir(parents=True,exist_ok=True); result={'schema_version':'1.1','status':'COMPLETED','media_sha256':hashlib.sha256(media.read_bytes()).hexdigest(),'evidence':{'warnings':[]},'media_facts':{'audio_present':False}}
  (output/'inspection.json').write_text(json.dumps(result),encoding='utf-8'); return result
 class Engine:
  def availability(self): return {'available':True,'languages':['en-US'],'engine_id':'test','engine_version':'1'}
 def ocr(candidate,manifest,request,engine,availability):
  calls['ocr']+=1; target=request.output_root/manifest.radar_run_id/'candidates'/candidate.video_id/'ocr'/'ocr_result.json'; target.parent.mkdir(parents=True,exist_ok=True); result={'status':'COMPLETED','first_text_hook':None,'first_text_hook_reason':'no_reliable_text_observed','warnings':[]}; target.write_text(json.dumps(result),encoding='utf-8'); return result
 def prepare(candidate,manifest,request,availability,options):
  calls['prepare']+=1; target=request.output_root/manifest.radar_run_id/'candidates'/candidate.video_id/'transcription'/'transcription_result.json'; return {'candidate':candidate,'target':target,'inspection':{'media_facts':{'duration_seconds':1}},'record':{},'availability':availability,'options':options,'manifest_hash':manifest.manifest_hash,'language':None,'no_audio':True}
 def no_audio(item): return {'status':'COMPLETED_NO_AUDIO','first_spoken_words':None,'first_spoken_words_reason':'no_audio_stream','warnings':[]}
 def write_transcription(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value),encoding='utf-8')
 class Provider:
  provider_id='deepseek'; model_id='deepseek-v4-flash'; provider_version='1'; configuration={}
  def __init__(self): self._api_key='top-secret'; self._transport=None
  def build_request_body(self,payload): return {'model':self.model_id,'messages':[{'role':'user','content':'bounded'}]}
  def metadata(self): return {'provider_id':self.provider_id,'model_id':self.model_id}
 class Response:
  def json(self): return {'choices':[{'message':{'content':json.dumps({'claims':[],'project_adaptation':{},'warnings':[]})}}]}
 def build_input(*args,**kwargs): calls['build_analysis_input']+=1; candidate_id=args[1]; return {'candidate_identity':{'video_id':candidate_id,'rank':int(candidate_id[-2:])},'input_hash':f'input-{candidate_id}','project_context_hash':'context','evidence':{},'evidence_index':[],'missing_evidence':[]}
 def post(*args,**kwargs): calls['post']+=1; return Response(),1
 def validate(result,analysis_input,provider):
  calls['validate']+=1
  raw=tmp_path/'canonical'/'content-intelligence'/analysis_input['candidate_identity']['video_id']/'raw-response.json'; assert raw.is_file()
  return result
 services.update({'TikTokCollector':Collector,'read_source_file':lambda name:['source'],'get_config_bool':lambda *args:True,'compute_scores':lambda values:values,'build_selection_manifest':build,'write_selection_manifest':write,'_read_reusable_record':reusable,'capture_browser_media_in_context':capture,'_ffprobe':lambda path:{'valid':True,'duration_seconds':1},'inspect_media':inspect_media,'WindowsMediaOcrEngine':Engine,'_run_candidate':ocr,'FasterWhisperEngine':Engine,'_prepare':prepare,'_no_audio_result':no_audio,'write_transcription':write_transcription,'build_analysis_input':build_input,'load_project_context':lambda path:(SimpleNamespace(),{},'context'),'DeepSeekContentIntelligenceProvider':Provider,'build_provider_payload':lambda *args:{},'post_deepseek_request':post,'_without_reasoning_content':lambda raw:(raw,{}),'validate_provider_result':validate,'build_card':lambda analysis,result:{'claims':result['claims'],'project_adaptation':result['project_adaptation'],'warnings':result['warnings']}})
 monkeypatch.setattr(v2,'_canonical_services',lambda:services)
 deps=build_fresh_top20_b1_production_dependencies(root=tmp_path)
 first=run_fresh_top20_b1(root=tmp_path,dependencies=deps)
 assert first['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW'
 assert [item['original_rank'] for item in first['cards']][5::14]==[6,20]
 assert calls['collect_all']==calls['enrich_missing_stats']==1 and calls['build_selection_manifest']==calls['write_selection_manifest']==1
 assert all(calls[name]==20 for name in ('capture','inspect','ocr','prepare','build_analysis_input','post','validate'))
 assert calls['close']==2
 assert 'top-secret' not in '\n'.join(path.read_text(encoding='utf-8') for path in tmp_path.rglob('*.json'))
 second_calls=dict(calls); second=run_fresh_top20_b1(root=tmp_path,dependencies=build_fresh_top20_b1_production_dependencies(root=tmp_path))
 assert second['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW'
 assert calls['collect_all']==second_calls['collect_all'] and calls['capture']==second_calls['capture'] and calls['post']==second_calls['post']

def test_b1_real_cli_runs_preflight_factory_and_existing_orchestrator(monkeypatch,tmp_path,capsys):
 script=ROOT/'scripts'/'run_loopra_05_fresh_acceptance.py'; spec=importlib.util.spec_from_file_location('fresh_acceptance_cli',script); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
 calls=[]
 monkeypatch.setattr(module,'validate_fresh_top20_b1_production_readiness',lambda **kwargs:(calls.append('preflight') or {'ready':True,'status':'READY'}))
 dependencies={'collect':lambda:None}
 monkeypatch.setattr(module,'build_fresh_top20_b1_production_dependencies',lambda **kwargs:(calls.append('factory') or dependencies))
 def run(**kwargs): calls.append('orchestrator'); assert kwargs['dependencies'] is dependencies; return {'status':'READY_FOR_OWNER_EDITORIAL_REVIEW'}
 monkeypatch.setattr(module,'run_fresh_top20_b1',run)
 assert module.main(['--runtime-root',str(tmp_path),'--b1-real','--json'])==0
 assert calls==['preflight','factory','orchestrator']
 assert json.loads(capsys.readouterr().out)['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW'

def test_production_collection_auth_failure_is_resumable_and_keeps_identity(monkeypatch,tmp_path):
 services=v2._canonical_services(); instances=[]
 class Collector:
  def __init__(self,headless=True):
   self.run_id=f'fresh-run-{len(instances)+1}'; self.collected_at=f'2026-07-27T00:00:0{len(instances)}Z'; self.last_authentication_state='login_overlay'; instances.append(self)
  async def start(self): pass
  async def collect_all(self,sources):
   if len(instances)==2:
    assert self.run_id=='fresh-run-1' and self.collected_at=='2026-07-27T00:00:00Z'
   raise services['RadarOperationalError']('authentication_timeout','login overlay')
  async def enrich_missing_stats(self,values): pytest.fail('enrichment must not run')
  async def close(self): self.closed=True
 services.update({'TikTokCollector':Collector,'read_source_file':lambda name:['source'],'get_config_bool':lambda *args:True})
 monkeypatch.setattr(v2,'_canonical_services',lambda:services)
 deps=build_fresh_top20_b1_production_dependencies(root=tmp_path)
 for _ in range(2):
  with pytest.raises(LoopraTop20V2Error,match='AUTHENTICATION_REQUIRED'):
   deps['collect']()
 status=json.loads((tmp_path/'canonical'/'collection-status.json').read_text(encoding='utf-8'))
 assert status['status']=='AUTHENTICATION_REQUIRED' and status['resumable'] is True
 assert status['search_run_id']=='fresh-run-1' and status['raw_candidate_count']==status['deduplicated_candidate_count']==0
 assert all(instance.closed for instance in instances)
 assert 'secret' not in json.dumps(status).lower()

def test_b1_real_cli_reports_authentication_required(monkeypatch,tmp_path,capsys):
 script=ROOT/'scripts'/'run_loopra_05_fresh_acceptance.py'; spec=importlib.util.spec_from_file_location('fresh_acceptance_auth_cli',script); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
 monkeypatch.setattr(module,'validate_fresh_top20_b1_production_readiness',lambda **kwargs:{'ready':True,'status':'READY'})
 monkeypatch.setattr(module,'build_fresh_top20_b1_production_dependencies',lambda **kwargs:{})
 monkeypatch.setattr(module,'run_fresh_top20_b1',lambda **kwargs:(_ for _ in ()).throw(module.LoopraTop20V2Error('AUTHENTICATION_REQUIRED')))
 assert module.main(['--runtime-root',str(tmp_path),'--b1-real','--json'])==1
 assert json.loads(capsys.readouterr().out)=={'status':'AUTHENTICATION_REQUIRED','reason':'AUTHENTICATION_REQUIRED'}

def test_retry_reuses_completed_item_side_effects_and_only_retries_failed_rank(tmp_path):
 entries=[{'candidate_id':f'c{i:02d}','video_id':f'v{i:02d}','original_rank':i} for i in range(1,21)]
 effects={rank:0 for rank in range(1,21)}; completed=set(); attempt=0
 def acquire(entry):
  rank=entry['original_rank']
  if rank in completed: return {'status':'REUSED'}
  effects[rank]+=1
  if rank==7 and attempt==0: return {'status':'FAILED','source_media_reference':None,'source_media_sha256':None}
  completed.add(rank); return {'status':'COMPLETED','source_media_reference':f'media/{rank}.mp4','source_media_sha256':str(rank),'duration_seconds':1,'ffprobe_status':'VALID','method':'mock'}
 deps={'collect':lambda:entries,'select':lambda pool:pool,'acquire':acquire,'inspect':lambda entry:{'status':'COMPLETED'},'ocr':lambda entry:{'status':'COMPLETED'},'transcribe':lambda entry:{'status':'COMPLETED'},'provider':lambda request:{'claims':[],'project_adaptation':{},'warnings':[]}}
 first=run_fresh_top20_b1(root=tmp_path,dependencies=deps,offline=True)
 assert first['status']=='PARTIAL' and first['failed_ranks']==[7]
 attempt=1
 second=run_fresh_top20_b1(root=tmp_path,dependencies=deps,offline=True)
 assert second['status']=='READY_FOR_OWNER_EDITORIAL_REVIEW'
 assert effects[7]==2 and all(effects[rank]==1 for rank in effects if rank!=7)

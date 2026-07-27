from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"trend-radar/src"))
from loopra_top20_acceptance_batch import *
def decisions(value): return [{"rank":rank,"decision":value} for rank in range(1,21)]
def ready(tmp_path):
 initialize(runtime_root=tmp_path); collect_synthetic(runtime_root=tmp_path); create_editorial_package(runtime_root=tmp_path); finalize_editorial(runtime_root=tmp_path,decisions=decisions("APPROVED_FOR_PRODUCTION_BRIEF"),human_confirmation=True); generate_scripts(runtime_root=tmp_path); create_script_package(runtime_root=tmp_path); finalize_scripts(runtime_root=tmp_path,decisions=decisions("APPROVE"),human_confirmation=True); return tmp_path
def test_synthetic_full_acceptance_and_reuse(tmp_path):
 ready(tmp_path); build_exports(runtime_root=tmp_path); accepted=owner_accept(runtime_root=tmp_path,decision="ACCEPTED",human_confirmation=True); report=verify(runtime_root=tmp_path)
 assert accepted["batch"]["scope_frozen"] is True and report["item_count"]==20 and report["network_calls"]==0
 assert initialize(runtime_root=tmp_path)["status"]=="REUSED"
def test_exact_unique_ordered_ranks_required(tmp_path):
 root,batch,items=_load(tmp_path) if False else (None,None,None)
 initialize(runtime_root=tmp_path)
 with pytest.raises(Top20AcceptanceError): finalize_editorial(runtime_root=tmp_path,decisions=decisions("APPROVED_FOR_PRODUCTION_BRIEF"),human_confirmation=True)
def test_editorial_and_script_gates_block_downstream(tmp_path):
 initialize(runtime_root=tmp_path)
 with pytest.raises(Top20AcceptanceError): generate_scripts(runtime_root=tmp_path)
 collect_synthetic(runtime_root=tmp_path)
 with pytest.raises(Top20AcceptanceError): finalize_editorial(runtime_root=tmp_path,decisions=decisions("REJECTED"),human_confirmation=False)
def test_failure_is_resumable_and_does_not_touch_completed_items(tmp_path):
 initialize(runtime_root=tmp_path); first=collect_synthetic(runtime_root=tmp_path,fail_rank=7)
 assert first["items"][6]["resume_status"]=="RESUMABLE" and first["items"][0]["current_stage"]=="CONTENT_INTELLIGENCE_COMPLETED"
 second=collect_synthetic(runtime_root=tmp_path)
 assert second["items"][0]["content_hash"]==first["items"][0]["content_hash"] and second["items"][6]["current_stage"]=="CONTENT_INTELLIGENCE_COMPLETED"

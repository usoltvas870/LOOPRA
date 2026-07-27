import struct, sys
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]
from loopra_content_cycle import ContentCycleError, EVENTS, TITLE, build_cycle, practical_template, register_selected_image, technical_acceptance, validate_owner_decision

def test_builds_deterministic_reused_rank_one_cycle(tmp_path):
    first = build_cycle(root=ROOT, runtime_root=tmp_path)
    second = build_cycle(root=ROOT, runtime_root=tmp_path)
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED"
    cycle = first["cycle"]
    assert cycle["original_rank"] == 1 and cycle["video_title"] == TITLE
    assert cycle["lifecycle_status"] == "PRACTICAL_PRODUCTION_PENDING"
    assert [event["event_type"] for event in cycle["cycle_events"]] == list(EVENTS)

def test_technical_acceptance_is_offline_and_reused(tmp_path):
    result = technical_acceptance(root=ROOT, runtime_root=tmp_path)["report"]
    assert result["technical_end_to_end_pass"] is True
    assert result["practical_acceptance_status"] == "PENDING"
    assert result["network_calls"] == result["provider_calls"] == result["heygen_calls"] == result["renderer_calls"] == 0
    assert result["credentials_required"] is False and result["reuse_identity"] is True

def _png(path: Path) -> None:
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + struct.pack(">II", 9, 16) + b"\x08\x02\0\0\0" + b"\0" * 16)

def test_pending_package_readiness_and_template_are_honest(tmp_path):
    result = build_cycle(root=ROOT, runtime_root=tmp_path)
    assert result["package"]["selected_image"]["status"] == "PENDING"
    assert result["package"]["heygen_clip"]["status"] == "PENDING"
    assert practical_template(result["cycle"])["reviewer"]["human_confirmation"] is False
    readiness = __import__("json").loads(result["readiness_path"].read_text(encoding="utf-8"))
    assert readiness["loopra_0_5_status"] == "TECHNICALLY_COMPLETE_PRACTICAL_ACCEPTANCE_PENDING" and readiness["scope_frozen"] is False

def test_selected_image_registration_copies_exact_bytes_and_requires_owner_confirmation(tmp_path):
    cycle = build_cycle(root=ROOT, runtime_root=tmp_path)["cycle"]
    source = tmp_path / "synthetic.png"; _png(source)
    first = register_selected_image(source_path=source, cycle=cycle, runtime_root=tmp_path, owner_selected=True, visual_identity_confirmed=True, blur_panel_absent=True)
    second = register_selected_image(source_path=source, cycle=cycle, runtime_root=tmp_path, owner_selected=True, visual_identity_confirmed=True, blur_panel_absent=True)
    assert first["registration"]["orientation"] == "VERTICAL" and second["status"] == "REUSED"
    with pytest.raises(ContentCycleError, match="OWNER_IMAGE_CONFIRMATION_REQUIRED"):
        register_selected_image(source_path=source, cycle=cycle, runtime_root=tmp_path, owner_selected=False, visual_identity_confirmed=True, blur_panel_absent=True)

def test_owner_acceptance_rejects_missing_evidence_and_incomplete_confirmation():
    decision = {"decision": "ACCEPT_LOOPRA_0_5", "reviewer": {"human_confirmation": True}, "workflow": {"final_video_practically_usable": True, "workflow_reduced_manual_work": True, "would_use_again": True}, "content": {"approved_script_preserved": True, "NURA_identity_preserved": True, "source_video_not_copied": True, "safety_acceptable": True}}
    with pytest.raises(ContentCycleError, match="SELECTED_IMAGE_EVIDENCE_REQUIRED"): validate_owner_decision(decision, image_registered=False, clip_registered=False)
    assert validate_owner_decision({"decision": "NEEDS_MORE_TESTING"}, image_registered=False, clip_registered=False) == "PENDING"

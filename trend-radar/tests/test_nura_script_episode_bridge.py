import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from nura_script_episode_bridge import (
    NuraScriptEpisodeBridgeError,
    build_and_persist_bridge,
    hash_payload,
    persist_bridge,
)


HOOK = "Ты продолжаешь поддерживать других, даже когда сама уже выгораешь?"
BLOCKS = [
    {"kind": "hook", "text": HOOK},
    {"kind": "development", "text": "Ты слушаешь и снова откладываешь свою усталость на потом."},
    {"kind": "turn", "text": "Поддерживать близкого не значит исчезать из собственной жизни."},
    {"kind": "ending", "text": "Спроси себя: «Что сейчас нужно мне?»"},
    {"kind": "ending", "text": "Это возможность остаться рядом, не оставляя себя."},
]


def _write(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    candidate = {"video_id": "video-1"}
    brief = {"brief_id": "brief-1", "candidate_identity": candidate, "original_rank": 1}
    brief["brief_hash"] = hash_payload(brief)
    script_input = {"content_hash": "script-input-hash"}
    provider = {"content_hash": "provider-hash"}
    script = {"script_kind": "nura_human_approved_script", "script_id": "approved-1", "script_input_hash": script_input["content_hash"], "candidate_identity": candidate, "original_rank": 1, "format": "TALKING_GUIDE", "language": "ru", "payload": {"text": "\n\n".join(block["text"] for block in BLOCKS), "blocks": BLOCKS}, "status": "HUMAN_APPROVED", "episode_bridge_ready": True, "source_provider_script": {"script_id": "provider-1", "content_hash": provider["content_hash"]}, "provenance": {"brief_hash": brief["brief_hash"]}}
    script["content_hash"] = hash_payload(script)
    review = {"review_kind": "nura_finalized_human_script_review", "finalization_identity": "final-1", "final_script_id": script["script_id"], "final_script_hash": script["content_hash"], "provider_output_hash": provider["content_hash"], "decision": "APPROVED_FOR_EPISODE_BRIDGE", "final_status": "HUMAN_APPROVED", "episode_bridge_ready": True, "reviewer": {"human_confirmation": True}}
    review["review_hash"] = hash_payload(review)
    root = tmp_path / "runtime"; root.mkdir(parents=True, exist_ok=True)
    _write(root / "script_input.json", script_input)
    _write(root / "validated_script_output.json", provider)
    return _write(root / "finalized_human_script_review.json", review), _write(root / "human_approved_script_output.json", script), _write(tmp_path / "production_brief.json", brief)


def test_builds_exact_rank_one_talking_guide_bridge_and_reuses(tmp_path: Path) -> None:
    review, script, brief = _fixture(tmp_path / "provider-substitution")
    first = build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")
    second = build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")
    bridge = first["bridge"]
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED"
    assert bridge["spoken_script"]["text"] == "\n\n".join(block["text"] for block in BLOCKS)
    assert bridge["spoken_script"]["blocks"][0]["text"] == HOOK
    assert bridge["subtitle_source"]["text"] == bridge["spoken_script"]["text"]
    assert bridge["subtitle_source"]["timing"] == "PROVISIONAL_NO_AUDIO_MEASUREMENT"
    assert bridge["production_input_ready"] is True and bridge["production_execution_ready"] is False
    assert "frames" not in bridge and bridge["music"]["track_reference"] is None


@pytest.mark.parametrize("field,value,error", [
    ("decision", "REJECTED", "FINALIZED_REVIEW_NOT_APPROVED"),
    ("episode_bridge_ready", False, "EPISODE_BRIDGE_READINESS_REQUIRED"),
])
def test_rejects_unready_finalized_review(tmp_path: Path, field: str, value: object, error: str) -> None:
    review, script, brief = _fixture(tmp_path / "rank-two")
    body = json.loads(review.read_text(encoding="utf-8")); body[field] = value; body["review_hash"] = hash_payload({k: v for k, v in body.items() if k != "review_hash"}); _write(review, body)
    with pytest.raises(NuraScriptEpisodeBridgeError, match=error):
        build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")


def test_rejects_non_confirmed_reviewer_and_provider_substitution(tmp_path: Path) -> None:
    review, script, brief = _fixture(tmp_path)
    body = json.loads(review.read_text(encoding="utf-8")); body["reviewer"]["human_confirmation"] = False; body["review_hash"] = hash_payload({k: v for k, v in body.items() if k != "review_hash"}); _write(review, body)
    with pytest.raises(NuraScriptEpisodeBridgeError, match="HUMAN_CONFIRMATION_REQUIRED"):
        build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")
    review, script, brief = _fixture(tmp_path)
    provider = json.loads((script.parent / "validated_script_output.json").read_text(encoding="utf-8")); provider["content_hash"] = "other"; _write(script.parent / "validated_script_output.json", provider)
    with pytest.raises(NuraScriptEpisodeBridgeError, match="PROVIDER_OUTPUT_PROVENANCE_MISMATCH"):
        build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")


def test_rejects_altered_text_and_non_rank_one(tmp_path: Path) -> None:
    review, script, brief = _fixture(tmp_path)
    body = json.loads(script.read_text(encoding="utf-8")); body["payload"]["blocks"][1]["text"] += "!"; body["content_hash"] = hash_payload({k: v for k, v in body.items() if k != "content_hash"}); _write(script, body)
    with pytest.raises(NuraScriptEpisodeBridgeError, match="FINAL_REVIEW_SCRIPT_IDENTITY_MISMATCH"):
        build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")
    review, script, brief = _fixture(tmp_path)
    body = json.loads(script.read_text(encoding="utf-8")); body["original_rank"] = 2; body["content_hash"] = hash_payload({k: v for k, v in body.items() if k != "content_hash"}); _write(script, body)
    review_body = json.loads(review.read_text(encoding="utf-8")); review_body["final_script_hash"] = body["content_hash"]; review_body["review_hash"] = hash_payload({k: v for k, v in review_body.items() if k != "review_hash"}); _write(review, review_body)
    with pytest.raises(NuraScriptEpisodeBridgeError, match="CANDIDATE_OR_RANK_PROVENANCE_MISMATCH"):
        build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")


def test_conflicting_reuse_is_rejected_atomically(tmp_path: Path) -> None:
    review, script, brief = _fixture(tmp_path)
    result = build_and_persist_bridge(finalized_review_path=review, approved_script_path=script, production_brief_path=brief, output_root=tmp_path / "out")
    changed = dict(result["bridge"]); changed["warnings"] = ["changed"]
    with pytest.raises(NuraScriptEpisodeBridgeError, match="CONFLICTING_BRIDGE_REUSE"):
        persist_bridge(output_root=tmp_path / "out", bridge=changed)

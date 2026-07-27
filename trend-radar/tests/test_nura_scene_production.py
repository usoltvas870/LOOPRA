import sys
import json
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT / "src")]
from nura_scene_production import FakeSceneProvider, NuraSceneProductionError, run_scene_production
BRIDGE = ROOT / "data/nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json"
PROFILE = ROOT / "data/nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json"
def test_fake_scene_package_is_exact_and_reused(tmp_path: Path) -> None:
    first = run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path, provider=FakeSceneProvider())
    second = run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path, provider=FakeSceneProvider(), reuse_only=True)
    package = first["package"]
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED"
    assert [s["source_block_ids"] for s in package["scenes"]] == [[f"block-{i}"] for i in range(1, 6)]
    assert package["status"] == "READY_FOR_OPERATOR_REVIEW" and package["production_execution_ready"] is False
    assert package["image_generation_performed"] is False and package["heygen_called"] is False
def test_real_provider_requires_explicit_network_permission(tmp_path: Path) -> None:
    with pytest.raises(NuraSceneProductionError, match="REAL_PROVIDER_REQUIRES_ALLOW_NETWORK"):
        run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path)

def test_raw_response_is_persisted_before_scene_validation(tmp_path: Path) -> None:
    class InvalidProvider:
        def metadata(self): return {"provider_id": "test", "fake": True}
        def generate(self, request): return {"scenes": [{"source_block_ids": ["unknown"]}]}, {"http_status": 200}
    with pytest.raises(NuraSceneProductionError, match="INVALID_SCENE_STRUCTURE"):
        run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path, provider=InvalidProvider())
    raw = list(tmp_path.rglob("raw_provider_response.json"))
    assert len(raw) == 1
    assert json.loads(raw[0].read_text(encoding="utf-8"))["metadata"]["http_status"] == 200

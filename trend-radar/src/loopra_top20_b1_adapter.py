"""Stage 5O-B1A offline adapter for a future fresh TOP-20 execution.

This is a versioned adapter, not an extension of the legacy five-item flow.
It persists only synthetic fixtures and deliberately has no network, browser or
provider integration points enabled.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "2.1-b1a"
TARGET_COUNT = 20
REAL_B1_BLOCK = "REAL_B1_NOT_ENABLED_UNTIL_ADAPTER_FOUNDATION_COMMITTED"


class LoopraTop20B1Error(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _atomic(path: Path, value: dict[str, Any]) -> str:
    text = _json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise LoopraTop20B1Error("CONFLICTING_B1_ARTIFACT")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    try:
        os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise LoopraTop20B1Error("CONFLICTING_B1_ARTIFACT")
    finally:
        temporary.unlink(missing_ok=True)
    return "COMPLETED"


def _read(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LoopraTop20B1Error("INVALID_B1_ARTIFACT") from error
    if not isinstance(result, dict):
        raise LoopraTop20B1Error("B1_OBJECT_REQUIRED")
    return result


def _with_hash(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result["content_hash"] = _hash({key: data for key, data in result.items() if key != "content_hash"})
    return result


def _portable(rank: int, name: str) -> str:
    return f"b1/items/{rank:02d}/{name}.json"


class LoopraTop20B1Adapter:
    """Owns only the B1 TOP-20 envelope and offline synthetic lifecycle."""

    def __init__(self, *, runtime_root: Path, project_id: str = "nura") -> None:
        self.runtime_root = Path(runtime_root)
        self.project_id = project_id

    @property
    def batch_id(self) -> str:
        return "loopra-top20-b1-" + _hash({"schema": SCHEMA_VERSION, "project": self.project_id})[:12]

    @property
    def root(self) -> Path:
        return self.runtime_root / self.batch_id

    def synthetic_selection(self) -> list[dict[str, Any]]:
        return [{"candidate_id": f"candidate-synthetic-b1-{rank:02d}", "video_id": f"synthetic-b1-video-{rank:02d}", "original_rank": rank, "source_platform_reference": "synthetic://tiktok"} for rank in range(1, TARGET_COUNT + 1)]

    def _validate_selection(self, entries: list[dict[str, Any]]) -> None:
        ranks = [entry.get("original_rank") for entry in entries]
        candidates = [entry.get("candidate_id") for entry in entries]
        videos = [entry.get("video_id") for entry in entries]
        if ranks != list(range(1, TARGET_COUNT + 1)):
            raise LoopraTop20B1Error("B1_EXACT_ORIGINAL_RANKS_REQUIRED")
        if len(set(candidates)) != TARGET_COUNT or len(set(videos)) != TARGET_COUNT or any(not value for value in candidates + videos):
            raise LoopraTop20B1Error("B1_UNIQUE_CANDIDATE_AND_VIDEO_IDS_REQUIRED")

    def _item(self, entry: dict[str, Any], batch: dict[str, Any]) -> dict[str, Any]:
        rank = entry["original_rank"]
        entry_hash = _hash(entry)
        call_identity = _hash({"candidate_id": entry["candidate_id"], "video_id": entry["video_id"], "original_rank": rank, "input_hash": entry_hash, "provider": "OFFLINE_SYNTHETIC", "model": "OFFLINE_SYNTHETIC", "prompt_version": "b1a-offline", "effective_request_hash": entry_hash, "project_id": self.project_id, "fresh_batch_id": batch["batch_id"]})
        return _with_hash({
            "schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_top20_b1_item_execution_plan",
            "adapter_item_id": f"b1-item-{batch['batch_id'][-12:]}-{rank:02d}", "batch_reference": batch["batch_id"],
            "batch_hash": batch["selection_manifest_hash"], "fresh_cycle_id": batch["fresh_cycle_id"], "search_run_id": batch["search_run_id"],
            "selection_manifest_reference": batch["selection_manifest_reference"], "selection_manifest_hash": batch["selection_manifest_hash"], "selection_entry_hash": entry_hash,
            "candidate_id": entry["candidate_id"], "video_id": entry["video_id"], "original_rank": rank, "source_platform_reference": entry["source_platform_reference"],
            "acquisition_plan_identity": _hash({"candidate_id": entry["candidate_id"], "video_id": entry["video_id"], "rank": rank}),
            "inspection_plan_identity": _hash({"video_id": entry["video_id"], "rank": rank, "kind": "inspection"}),
            "ocr_plan_identity": _hash({"video_id": entry["video_id"], "rank": rank, "kind": "ocr"}),
            "transcript_plan_identity": _hash({"video_id": entry["video_id"], "rank": rank, "kind": "transcript"}),
            "content_intelligence_call_identity": call_identity,
            "expected_runtime_references": {name: _portable(rank, name) for name in ("media", "acquisition", "inspection", "ocr", "transcript", "content_intelligence_card")},
            "state_reference": f"b1/items/{rank:02d}",
            "current_stage": "INITIALIZED", "stage_statuses": {name: "PENDING" for name in ("acquisition", "inspection", "ocr", "transcript", "content_intelligence")},
            "retryable_failures": [], "nonretryable_failures": [], "reuse_metadata": {"mode": "CONTENT_IDENTICAL_ONLY", "reused": False}, "content_hash": "",
        })

    def initialize(self, *, entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        entries = self.synthetic_selection() if entries is None else entries
        self._validate_selection(entries)
        manifest = _with_hash({"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_top20_b1_synthetic_selection_manifest", "fresh_cycle_id": "synthetic-b1-cycle", "search_run_id": "synthetic-b1-no-search", "entries": entries, "offline": True, "content_hash": ""})
        batch = _with_hash({"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_top20_b1_adapter_batch", "batch_id": self.batch_id, "project_id": self.project_id, "fresh_cycle_id": manifest["fresh_cycle_id"], "search_run_id": manifest["search_run_id"], "selection_manifest_reference": "b1/selection_manifest.json", "selection_manifest_hash": manifest["content_hash"], "target_count": TARGET_COUNT, "current_phase": "INITIALIZED", "network_calls": 0, "browser_calls": 0, "provider_calls": 0, "credentials_required": False, "content_hash": ""})
        items = [self._item(entry, batch) for entry in entries]
        statuses = [_atomic(self.root / "selection_manifest.json", manifest), _atomic(self.root / "batch.json", batch)]
        statuses.extend(_atomic(self.root / "items" / f"{item['original_rank']:02d}" / f"{item['content_hash'][:16]}.json", item) for item in items)
        return {"status": "COMPLETED" if "COMPLETED" in statuses else "REUSED", "root": self.root, "batch": batch, "items": items}

    def _load(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        self.initialize()
        batch = _read(self.root / "batch.json")
        items = []
        for rank in range(1, TARGET_COUNT + 1):
            paths = sorted((self.root / "items" / f"{rank:02d}").glob("*.json"), key=lambda item: item.stat().st_mtime_ns)
            if not paths:
                raise LoopraTop20B1Error("B1_MISSING_ITEM")
            items.append(_read(paths[-1]))
        self._validate_selection([{key: item[key] for key in ("candidate_id", "video_id", "original_rank", "source_platform_reference")} for item in items])
        return batch, items

    def _store_item(self, item: dict[str, Any]) -> str:
        return _atomic(self.root / "items" / f"{item['original_rank']:02d}" / f"{item['content_hash'][:16]}.json", item)

    def _write_fixture(self, item: dict[str, Any], name: str, payload: dict[str, Any]) -> str:
        return _atomic(self.root / "runtime" / _portable(item["original_rank"], name), _with_hash({"schema_version": SCHEMA_VERSION, "synthetic": True, "candidate_id": item["candidate_id"], "video_id": item["video_id"], "original_rank": item["original_rank"], **payload, "content_hash": ""}))

    def simulate_execution(self, *, fail_rank: int | None = None) -> dict[str, Any]:
        batch, items = self._load()
        result = []
        for item in items:
            rank = item["original_rank"]
            if item["current_stage"] == "CONTENT_INTELLIGENCE_COMPLETED":
                result.append(item)
                continue
            if rank == fail_rank:
                updated = _with_hash({**item, "current_stage": "RETRYABLE_FAILURE", "stage_statuses": {**item["stage_statuses"], "acquisition": "RETRYABLE_FAILURE"}, "retryable_failures": ["SYNTHETIC_INJECTED_FAILURE"], "reuse_metadata": {**item["reuse_metadata"], "reused": False}, "content_hash": ""})
                self._store_item(updated); result.append(updated); continue
            for name in ("media", "acquisition", "inspection", "ocr", "transcript"):
                self._write_fixture(item, name, {"reference": item["expected_runtime_references"][name]})
            input_hash = _hash({"candidate_id": item["candidate_id"], "video_id": item["video_id"], "rank": rank})
            self._write_fixture(item, "content_intelligence_card", {"reference": item["expected_runtime_references"]["content_intelligence_card"], "input_hash": input_hash, "call_identity": item["content_intelligence_call_identity"], "provider": "OFFLINE_SYNTHETIC", "quality_warnings": ["SYNTHETIC_OFFLINE_FIXTURE"]})
            updated = _with_hash({**item, "current_stage": "CONTENT_INTELLIGENCE_COMPLETED", "stage_statuses": {name: "COMPLETED" for name in item["stage_statuses"]}, "retryable_failures": [], "reuse_metadata": {**item["reuse_metadata"], "reused": True}, "content_hash": ""})
            self._store_item(updated); result.append(updated)
        return {"status": "COMPLETED", "root": self.root, "batch": batch, "items": result, "completed": sum(item["current_stage"] == "CONTENT_INTELLIGENCE_COMPLETED" for item in result)}

    def build_content_intelligence_report(self) -> dict[str, Any]:
        batch, items = self._load()
        if any(item["current_stage"] != "CONTENT_INTELLIGENCE_COMPLETED" for item in items):
            raise LoopraTop20B1Error("B1_REPORT_REQUIRES_20_COMPLETED_ITEMS")
        report = _with_hash({"schema_version": SCHEMA_VERSION, "artifact_kind": "LoopraTop20ContentIntelligenceReport", "batch_reference": batch["batch_id"], "selection_manifest_hash": batch["selection_manifest_hash"], "original_ranking_preserved": True, "cards": [{"original_rank": item["original_rank"], "candidate_id": item["candidate_id"], "video_id": item["video_id"], "card_reference": item["expected_runtime_references"]["content_intelligence_card"], "quality_warnings": ["SYNTHETIC_OFFLINE_FIXTURE"]} for item in items], "winner": None, "human_verified": False, "incomplete": False, "reuse_metadata": {"mode": "CONTENT_IDENTICAL_ONLY"}, "content_hash": ""})
        _atomic(self.root / "content_intelligence_report.json", report)
        return {"status": "COMPLETED", "root": self.root, "report": report}

    def build_pending_editorial_review(self) -> dict[str, Any]:
        report = self.build_content_intelligence_report()["report"]
        review = _with_hash({"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_top20_b1_pending_editorial_review", "report_reference": "b1/content_intelligence_report.json", "report_hash": report["content_hash"], "items": [{"original_rank": card["original_rank"], "candidate_id": card["candidate_id"], "video_id": card["video_id"], "card_reference": card["card_reference"], "decision": "PENDING"} for card in report["cards"]], "reviewer": {"human_confirmation": False}, "finalized": False, "production_brief_allowed": False, "content_hash": ""})
        _atomic(self.root / "pending_editorial_review.json", review)
        return {"status": "COMPLETED", "root": self.root, "review": review}

    def verify(self) -> dict[str, Any]:
        batch, items = self._load()
        completed = sum(item["current_stage"] == "CONTENT_INTELLIGENCE_COMPLETED" for item in items)
        return {"status": "PASS", "batch_id": batch["batch_id"], "item_count": len(items), "original_ranks": [item["original_rank"] for item in items], "completed": completed, "resumable": TARGET_COUNT - completed, "network_calls": batch["network_calls"], "browser_calls": batch["browser_calls"], "provider_calls": batch["provider_calls"], "credentials_required": batch["credentials_required"], "root": str(self.root)}

    def aggregate_progress(self) -> dict[str, int]:
        """Return the B1-only progress view without changing any v1 contract."""
        _, items = self._load()
        completed = sum(item["current_stage"] == "CONTENT_INTELLIGENCE_COMPLETED" for item in items)
        retryable = sum(item["current_stage"] == "RETRYABLE_FAILURE" for item in items)
        return {"total": TARGET_COUNT, "completed": completed, "retryable_failures": retryable, "resumable": TARGET_COUNT - completed}

    def run_v2_offline_acceptance(self, *, fail_rank: int | None = None) -> dict[str, Any]:
        """Exercise the approved v2 contracts without a browser or provider."""
        from loopra_top20_real_pipeline_v2 import run_offline_acceptance
        return run_offline_acceptance(root=self.root / "v2", batch_id=self.batch_id, fail_rank=fail_rank)

    @staticmethod
    def real_b1_not_enabled() -> dict[str, Any]:
        return {"status": "BLOCKED", "reason": REAL_B1_BLOCK, "network_calls": 0, "browser_calls": 0, "provider_calls": 0}


def run_synthetic_acceptance(*, runtime_root: Path, project_id: str = "nura", fail_rank: int | None = None) -> dict[str, Any]:
    adapter = LoopraTop20B1Adapter(runtime_root=runtime_root, project_id=project_id)
    adapter.initialize()
    execution = adapter.simulate_execution(fail_rank=fail_rank)
    if execution["completed"] != TARGET_COUNT:
        return {**adapter.verify(), "status": "PARTIAL", "reason": "B1_RESUMABLE_ITEMS_REMAIN"}
    report = adapter.build_content_intelligence_report()["report"]
    review = adapter.build_pending_editorial_review()["review"]
    return {**adapter.verify(), "report_hash": report["content_hash"], "review_hash": review["content_hash"], "human_gate": "EDITORIAL_REVIEW_PENDING", "production_brief_allowed": False}

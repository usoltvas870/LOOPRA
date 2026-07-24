"""Offline, evidence-first inspection of one explicitly selected local video."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

INSPECTOR_VERSION = "1.1"
FRAME_TIMEOUT_SECONDS = 20
TOTAL_TIMEOUT_SECONDS = 180
TERMINAL_MARGIN_SECONDS = 0.05
MIN_SUCCESSFUL_FRAMES = 3
REQUESTED_SAMPLE_COUNT = 17


def _run(command: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout)


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plan_sample_times(duration: float, *, requested_count: int = REQUESTED_SAMPLE_COUNT,
                       terminal_margin: float = TERMINAL_MARGIN_SECONDS) -> list[float]:
    """Return finite, ordered, millisecond timestamps strictly inside media."""
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("input duration is unavailable")
    if requested_count < 1:
        raise ValueError("requested sample count must be positive")
    if not math.isfinite(terminal_margin) or terminal_margin <= 0:
        raise ValueError("terminal margin must be positive")
    safe_end = max(0.0, duration - min(terminal_margin, duration / 2))
    candidates = [0.0, 0.5, 1.0, 2.0, 3.0]
    candidates.extend(duration * index / 11 for index in range(12))
    planned: list[float] = []
    for value in candidates:
        value = min(max(0.0, value), safe_end)
        rounded = min(round(value, 3), math.floor(safe_end * 1000) / 1000)
        if rounded >= duration:
            rounded = round(max(0.0, duration - 0.001), 3)
        if rounded < duration and (not planned or rounded > planned[-1]):
            planned.append(rounded)
    return planned[:requested_count]


def _frame(source: Path, timestamp: float, target: Path, *, timeout: int = FRAME_TIMEOUT_SECONDS) -> None:
    target.unlink(missing_ok=True)
    try:
        # Input seeking avoids decoding a whole long video for every sample.
        result = _run(["ffmpeg", "-y", "-ss", f"{timestamp:.3f}", "-i", str(source), "-frames:v", "1", str(target)], timeout=timeout)
    except subprocess.TimeoutExpired as error:
        target.unlink(missing_ok=True)
        raise ValueError("FRAME_TIMEOUT") from error
    if result.returncode or not target.is_file() or not target.stat().st_size:
        target.unlink(missing_ok=True)
        raise ValueError("FRAME_EXTRACTION_FAILED")


def _extract_frames(source: Path, frames: Path, times: list[float], duration: float,
                    started: float) -> tuple[list[Path], list[float], list[dict], list[str]]:
    paths: list[Path] = []
    successful_times: list[float] = []
    results: list[dict] = []
    warnings: list[str] = []
    for index, timestamp in enumerate(times):
        if time.monotonic() - started >= TOTAL_TIMEOUT_SECONDS:
            warnings.append("TOTAL_INSPECTION_TIMEOUT")
            for remaining in times[index:]:
                results.append({"requested_timestamp_seconds": remaining, "effective_timestamp_seconds": None, "status": "not_attempted", "retry_count": 0, "error": "TOTAL_INSPECTION_TIMEOUT", "frame_path": None})
            break
        target = frames / f"sample_{index:02d}_{timestamp:.3f}s.png"
        try:
            _frame(source, timestamp, target)
            paths.append(target); successful_times.append(timestamp)
            results.append({"requested_timestamp_seconds": timestamp, "effective_timestamp_seconds": timestamp, "status": "success", "retry_count": 0, "error": None, "frame_path": str(target.name)})
            continue
        except ValueError as error:
            failure = str(error)
        retry_timestamp = round(max(0.0, timestamp - max(0.25, TERMINAL_MARGIN_SECONDS * 2)), 3)
        if timestamp == times[-1] and retry_timestamp < timestamp and retry_timestamp < duration:
            retry_target = frames / f"sample_{index:02d}_{retry_timestamp:.3f}s_retry.png"
            try:
                _frame(source, retry_timestamp, retry_target)
                paths.append(retry_target); successful_times.append(retry_timestamp)
                results.append({"requested_timestamp_seconds": timestamp, "effective_timestamp_seconds": retry_timestamp, "status": "success", "retry_count": 1, "error": failure, "frame_path": str(retry_target.name)})
                warnings.append("TERMINAL_FRAME_RETRIED")
                continue
            except ValueError as retry_error:
                failure = f"{failure}; retry: {retry_error}"
        results.append({"requested_timestamp_seconds": timestamp, "effective_timestamp_seconds": None, "status": "failed", "retry_count": 0, "error": failure, "frame_path": None})
        warnings.append(f"FRAME_FAILED_AT_{timestamp:.3f}")
    return paths, successful_times, results, warnings


def _difference(left: Image.Image, right: Image.Image) -> float:
    a = np.asarray(left.convert("RGB").resize((64, 64)), dtype=np.float32)
    b = np.asarray(right.convert("RGB").resize((64, 64)), dtype=np.float32)
    return float(np.mean(np.abs(a - b)) / 255)


def _phash(image: Image.Image):
    size = 32
    pixels = np.asarray(image.convert("L").resize((size, size)), dtype=np.float32)
    positions = np.arange(size); frequencies = np.arange(size)[:, None]
    transform = np.sqrt(2 / size) * np.cos(np.pi * (2 * positions + 1) * frequencies / (2 * size)); transform[0, :] = np.sqrt(1 / size)
    coefficients = (transform @ pixels @ transform.T)[:8, :8].flatten()[1:]
    colour = np.asarray(image.convert("RGB").resize((8, 8)), dtype=np.float32).mean(axis=(0, 1))
    return coefficients > coefficients.mean(), colour


def _same_visual_state(left, right) -> bool:
    return int(np.count_nonzero(left[0] != right[0])) <= 16 and float(np.mean(np.abs(left[1] - right[1]))) <= 35


def _metrics(paths: list[Path], times: list[float], duration: float) -> tuple[dict, list[str]]:
    if len(paths) < 2:
        return {"sampled_frame_count": len(paths), "sample_times_seconds": times, "frame_differences": [], "perceptual_hash_distances": [], "average_frame_difference": None, "static_ratio": None, "mostly_static": None, "scene_count_estimate": None, "scene_boundaries_seconds": [], "first_visual_change_seconds": None, "cuts_per_10_seconds": None, "unique_visual_state_count_estimate": None, "uses_one_or_two_visual_states": None, "dominant_motion_level": None}, ["INSUFFICIENT_FRAMES_FOR_VISUAL_METRICS"]
    images = [Image.open(path).convert("RGB") for path in paths]
    try:
        diffs = [_difference(images[index - 1], image) for index, image in enumerate(images[1:], 1)]
        hashes = [_phash(image) for image in images]
    finally:
        for image in images:
            image.close()
    distances = [int(np.count_nonzero(hashes[index - 1][0] != value[0])) for index, value in enumerate(hashes[1:], 1)]
    cuts = [times[index] for index, (difference, distance) in enumerate(zip(diffs, distances, strict=True), 1) if difference >= .12 or (difference >= .08 and distance >= 20)]
    states = []
    for value in hashes:
        if not any(_same_visual_state(value, old) for old in states):
            states.append(value)
    static_ratio = round(sum(value < .015 for value in diffs) / len(diffs), 3)
    return {"sampled_frame_count": len(paths), "sample_times_seconds": times, "frame_differences": [round(value, 4) for value in diffs], "perceptual_hash_distances": distances, "average_frame_difference": round(sum(diffs) / len(diffs), 4), "static_ratio": static_ratio, "mostly_static": static_ratio >= .7, "scene_count_estimate": max(1, len(cuts) + 1), "scene_boundaries_seconds": cuts, "first_visual_change_seconds": next((times[index] for index, value in enumerate(diffs, 1) if value >= .015), None), "cuts_per_10_seconds": round(len(cuts) * 10 / duration, 3), "unique_visual_state_count_estimate": len(states), "uses_one_or_two_visual_states": len(states) <= 2, "dominant_motion_level": "low" if static_ratio >= .7 else "high" if static_ratio < .3 else "medium"}, []


def _sheet(paths: list[Path], target: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in paths]
    try:
        width, height, columns = 240, 426, min(4, len(images)); rows = math.ceil(len(images) / columns)
        sheet = Image.new("RGB", (columns * width, rows * (height + 22)), "black"); draw = ImageDraw.Draw(sheet)
        for index, image in enumerate(images):
            image.thumbnail((width, height)); x, y = index % columns * width, index // columns * (height + 22)
            sheet.paste(image, (x + (width - image.width) // 2, y)); draw.text((x + 3, y + height + 3), paths[index].stem, fill="white")
        sheet.save(target)
    finally:
        for image in images:
            image.close()


def _write_json(path: Path, payload: dict) -> None:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as temporary:
        json.dump(payload, temporary, ensure_ascii=False, indent=2); temporary.write("\n"); temp_path = Path(temporary.name)
    os.replace(temp_path, path)


def inspect(source: Path, output: Path, video_id: str, canonical_url: str | None = None) -> dict:
    if not source.is_file() or source.suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm"}:
        raise ValueError("input must be an existing supported local media file")
    if not all(shutil.which(item) for item in ("ffmpeg", "ffprobe")):
        raise RuntimeError("ffmpeg and ffprobe are required")
    started = time.monotonic(); output.mkdir(parents=True, exist_ok=True); frames = output / "frames"; frames.mkdir(exist_ok=True)
    try:
        probe_result = _run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)], timeout=FRAME_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        raise ValueError("ffprobe timed out") from error
    if probe_result.returncode:
        raise ValueError(probe_result.stderr.strip() or "ffprobe failed")
    probe = json.loads(probe_result.stdout); _write_json(output / "ffprobe.json", probe)
    streams = probe.get("streams", []); video = next((item for item in streams if item.get("codec_type") == "video"), None); audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if not video:
        raise ValueError("input has no video stream")
    duration = float(probe.get("format", {}).get("duration") or video.get("duration") or 0)
    times = _plan_sample_times(duration)
    paths, successful_times, frame_results, warnings = _extract_frames(source, frames, times, duration, started)
    metrics, metric_warnings = _metrics(paths, successful_times, duration); warnings.extend(metric_warnings)
    status = "COMPLETED" if len(paths) == len(times) else "DEGRADED" if len(paths) >= MIN_SUCCESSFUL_FRAMES else "FAILED"
    contact_sheets: list[str] = []
    if paths:
        for name, selection in (("first_second_contact_sheet.png", paths[:3]), ("first_three_seconds_contact_sheet.png", paths[:5]), ("full_video_contact_sheet.png", paths)):
            _sheet(selection, output / name); contact_sheets.append(name)
    _write_json(output / "scene_metrics.json", metrics)
    rate = video.get("avg_frame_rate", "0/0").split("/"); fps = float(rate[0]) / float(rate[1]) if len(rate) == 2 and float(rate[1]) else None
    facts = {"container": probe.get("format", {}).get("format_name"), "codec": video.get("codec_name"), "width": video.get("width"), "height": video.get("height"), "aspect_ratio": round(video["width"] / video["height"], 4), "duration_seconds": duration, "duration_source": "format.duration", "fps": fps, "estimated_frame_count": round(duration * fps) if fps else None, "audio_present": audio is not None, "audio_codec": audio.get("codec_name") if audio else None, "audio_duration": float(audio.get("duration")) if audio and audio.get("duration") else None, "sample_rate": audio.get("sample_rate") if audio else None, "channels": audio.get("channels") if audio else None, "file_size_bytes": source.stat().st_size}
    result = {"schema_version": "1.1", "inspection_id": f"inspection-{video_id}", "run_id": None, "video_id": video_id, "canonical_url": canonical_url, "local_media_path": source.name, "media_sha256": _hash(source), "inspected_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "inspector_version": INSPECTOR_VERSION, "status": status, "media_facts": facts, "sampling": {"requested_sample_count": REQUESTED_SAMPLE_COUNT, "planned_sample_count": len(times), "terminal_margin_seconds": TERMINAL_MARGIN_SECONDS, "per_frame_timeout_seconds": FRAME_TIMEOUT_SECONDS, "total_timeout_seconds": TOTAL_TIMEOUT_SECONDS, "successful_frame_count": len(paths), "failed_frame_count": len(times) - len(paths), "frame_results": frame_results}, "visual_structure": metrics, "opening": {"first_frame_path": str(paths[0].relative_to(output)) if paths else None, "first_second_contact_sheet_path": "first_second_contact_sheet.png" if paths else None, "first_three_seconds_contact_sheet_path": "first_three_seconds_contact_sheet.png" if paths else None, "first_visual_change_seconds": metrics["first_visual_change_seconds"], "opening_motion_level": metrics["dominant_motion_level"], "opening_text_presence": "unknown", "opening_face_presence": "unknown"}, "audio": {"audio_present": audio is not None, "speech_likelihood": "unknown", "music_likelihood": "unknown", "transcription_status": "unavailable"}, "text": {"ocr_status": "unavailable", "extracted_screen_text": None}, "semantic_interpretation": {"status": "manual_review_required", "confidence": 0}, "evidence": {"sampled_frame_paths": [str(path.relative_to(output)) for path in paths], "contact_sheets": contact_sheets, "ffprobe_json": "ffprobe.json", "scene_metrics_json": "scene_metrics.json", "warnings": ["OCR and transcription are not run automatically in the local baseline.", *warnings], "manual_review_required": True}, "timings": {"total_seconds": round(time.monotonic() - started, 3)}}
    _write_json(output / "inspection.json", result)
    _write_json(output / "manual_review.json", {"schema_version": "1.0", "sample_id": video_id, "review_status": "pending", "manual_observations": {"visible_text_present": "unknown", "first_screen_text": None, "estimated_words_first_screen": None, "text_changes_count": None, "voice_present": "unknown", "music_present": "unknown", "first_spoken_words": None, "speech_start_seconds": None}, "inferences": {"central_thought_count": None, "delayed_reveal": "unknown", "delayed_reveal_seconds": None, "hook_text": None, "hook_type": None, "cta_present": "unknown", "emotional_theme": None, "estimated_required_assets": None, "reproducibility_complexity": None}, "reviewer_notes": None})
    report = f"# Video Format Inspection: {video_id}\n\n## Measured facts\n\n- Status: {status}\n- Duration: {duration:.3f}s\n- Resolution: {video['width']}×{video['height']}\n- Successful samples: {len(paths)}/{len(times)}\n- Audio present: {audio is not None}\n\n## Limits\n\nOCR, transcription, face detection and semantic interpretation require manual review.\n"
    (output / "inspection.md").write_text(report, encoding="utf-8")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect one local video without network access.")
    parser.add_argument("--input", required=True, type=Path); parser.add_argument("--video-id", required=True); parser.add_argument("--output-dir", required=True, type=Path); parser.add_argument("--canonical-url")
    args = parser.parse_args(argv)
    try:
        result = inspect(args.input, args.output_dir, args.video_id, args.canonical_url)
        _write_json(args.output_dir / "process_result.json", {"result": "success" if result["status"] != "FAILED" else "failed", "inspection_status": result["status"], "video_id": result["video_id"], "exit_code": 0 if result["status"] != "FAILED" else 2})
        print(f"INSPECTION_RESULT={'success' if result['status'] != 'FAILED' else 'failed'}"); return 0 if result["status"] != "FAILED" else 2
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"INSPECTION_RESULT=failed: {exc}"); return 2


if __name__ == "__main__":
    raise SystemExit(main())

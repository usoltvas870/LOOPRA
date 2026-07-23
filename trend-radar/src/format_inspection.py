"""Offline, evidence-first inspection of one explicitly selected local video."""
from __future__ import annotations

import argparse, hashlib, json, math, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

INSPECTOR_VERSION = "1.0"

def _run(command):
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def _frame(source, timestamp, target):
    result = _run(["ffmpeg", "-y", "-i", str(source), "-ss", f"{timestamp:.3f}", "-frames:v", "1", str(target)])
    if result.returncode or not target.is_file(): raise ValueError(result.stderr.strip() or "frame extraction failed")

def _difference(left, right):
    a = np.asarray(left.convert("RGB").resize((64, 64)), dtype=np.float32)
    b = np.asarray(right.convert("RGB").resize((64, 64)), dtype=np.float32)
    return float(np.mean(np.abs(a - b)) / 255)

def _phash(image):
    """Return a compact DCT perceptual hash plus average colour."""
    size = 32
    pixels = np.asarray(image.convert("L").resize((size, size)), dtype=np.float32)
    positions = np.arange(size)
    frequencies = np.arange(size)[:, None]
    transform = np.sqrt(2 / size) * np.cos(
        np.pi * (2 * positions + 1) * frequencies / (2 * size)
    )
    transform[0, :] = np.sqrt(1 / size)
    coefficients = (transform @ pixels @ transform.T)[:8, :8].flatten()[1:]
    bits = coefficients > coefficients.mean()
    colour = np.asarray(
        image.convert("RGB").resize((8, 8)), dtype=np.float32
    ).mean(axis=(0, 1))
    return bits, colour


def _same_visual_state(left, right):
    left_bits, left_colour = left
    right_bits, right_colour = right
    hamming = int(np.count_nonzero(left_bits != right_bits))
    colour_distance = float(np.mean(np.abs(left_colour - right_colour)))
    return hamming <= 16 and colour_distance <= 35

def _sheet(paths, target):
    images = [Image.open(path).convert("RGB") for path in paths]
    try:
        width, height, columns = 240, 426, min(4, len(images)); rows = math.ceil(len(images) / columns)
        sheet = Image.new("RGB", (columns * width, rows * (height + 22)), "black"); draw = ImageDraw.Draw(sheet)
        for index, image in enumerate(images):
            image.thumbnail((width, height)); x, y = index % columns * width, index // columns * (height + 22)
            sheet.paste(image, (x + (width - image.width) // 2, y)); draw.text((x + 3, y + height + 3), paths[index].stem, fill="white")
        sheet.save(target)
    finally:
        for image in images: image.close()

def inspect(source: Path, output: Path, video_id: str, canonical_url: str | None = None) -> dict:
    if not source.is_file() or source.suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm"}: raise ValueError("input must be an existing supported local media file")
    if not all(shutil.which(item) for item in ("ffmpeg", "ffprobe")): raise RuntimeError("ffmpeg and ffprobe are required")
    output.mkdir(parents=True, exist_ok=True); frames = output / "frames"; frames.mkdir(exist_ok=True)
    probe_result = _run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)])
    if probe_result.returncode: raise ValueError(probe_result.stderr.strip() or "ffprobe failed")
    probe = json.loads(probe_result.stdout); (output / "ffprobe.json").write_text(json.dumps(probe, ensure_ascii=False, indent=2), encoding="utf-8")
    streams = probe.get("streams", []); video = next((x for x in streams if x.get("codec_type") == "video"), None); audio = next((x for x in streams if x.get("codec_type") == "audio"), None)
    if not video: raise ValueError("input has no video stream")
    duration = float(probe.get("format", {}).get("duration") or video.get("duration") or 0)
    if duration <= 0: raise ValueError("input duration is unavailable")
    times = sorted({round(value, 3) for value in [0, .5, 1, 2, 3, *[duration * index / 11 for index in range(12)]] if value < duration})
    paths = []
    for index, timestamp in enumerate(times):
        path = frames / f"sample_{index:02d}_{timestamp:.3f}s.png"; _frame(source, timestamp, path); paths.append(path)
    images = [Image.open(path).convert("RGB") for path in paths]
    try:
        diffs = [_difference(images[i - 1], images[i]) for i in range(1, len(images))]
        hashes = [_phash(image) for image in images]
        hash_distances = [
            int(np.count_nonzero(hashes[i - 1][0] != hashes[i][0]))
            for i in range(1, len(hashes))
        ]
        cuts = [
            times[i]
            for i, (difference, hash_distance) in enumerate(
                zip(diffs, hash_distances, strict=True), 1
            )
            if difference >= .12 or (difference >= .08 and hash_distance >= 20)
        ]
        states = []
        for value in hashes:
            if not any(_same_visual_state(value, old) for old in states):
                states.append(value)
    finally:
        for image in images: image.close()
    static_ratio = round(sum(value < .015 for value in diffs) / max(1, len(diffs)), 3)
    first_change = next((times[i] for i, value in enumerate(diffs, 1) if value >= .015), None)
    metrics = {"sampled_frame_count": len(paths), "sample_times_seconds": times, "frame_differences": [round(value, 4) for value in diffs], "perceptual_hash_distances": hash_distances, "average_frame_difference": round(sum(diffs) / max(1, len(diffs)), 4), "static_ratio": static_ratio, "mostly_static": static_ratio >= .7, "scene_count_estimate": max(1, len(cuts) + 1), "scene_boundaries_seconds": cuts, "first_visual_change_seconds": first_change, "cuts_per_10_seconds": round(len(cuts) * 10 / duration, 3), "unique_visual_state_count_estimate": len(states), "uses_one_or_two_visual_states": len(states) <= 2, "dominant_motion_level": "low" if static_ratio >= .7 else "high" if static_ratio < .3 else "medium"}
    (output / "scene_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _sheet(paths[:3], output / "first_second_contact_sheet.png"); _sheet(paths[:5], output / "first_three_seconds_contact_sheet.png"); _sheet(paths, output / "full_video_contact_sheet.png")
    rate = video.get("avg_frame_rate", "0/0").split("/"); fps = float(rate[0]) / float(rate[1]) if len(rate) == 2 and float(rate[1]) else None
    facts = {"container": probe.get("format", {}).get("format_name"), "codec": video.get("codec_name"), "width": video.get("width"), "height": video.get("height"), "aspect_ratio": round(video["width"] / video["height"], 4), "duration_seconds": duration, "fps": fps, "estimated_frame_count": round(duration * fps) if fps else None, "audio_present": audio is not None, "audio_codec": audio.get("codec_name") if audio else None, "audio_duration": float(audio.get("duration")) if audio and audio.get("duration") else None, "sample_rate": audio.get("sample_rate") if audio else None, "channels": audio.get("channels") if audio else None, "file_size_bytes": source.stat().st_size}
    result = {"schema_version": "1.0", "inspection_id": f"inspection-{video_id}", "run_id": None, "video_id": video_id, "canonical_url": canonical_url, "local_media_path": str(source), "media_sha256": _hash(source), "inspected_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "inspector_version": INSPECTOR_VERSION, "media_facts": facts, "visual_structure": metrics, "opening": {"first_frame_path": str(paths[0].relative_to(output)), "first_second_contact_sheet_path": "first_second_contact_sheet.png", "first_three_seconds_contact_sheet_path": "first_three_seconds_contact_sheet.png", "first_visual_change_seconds": first_change, "opening_motion_level": metrics["dominant_motion_level"], "opening_text_presence": "unknown", "opening_face_presence": "unknown"}, "audio": {"audio_present": audio is not None, "speech_likelihood": "unknown", "music_likelihood": "unknown", "transcription_status": "unavailable"}, "text": {"ocr_status": "unavailable", "extracted_screen_text": None}, "semantic_interpretation": {"status": "manual_review_required", "confidence": 0}, "evidence": {"sampled_frame_paths": [str(path.relative_to(output)) for path in paths], "contact_sheets": ["first_second_contact_sheet.png", "first_three_seconds_contact_sheet.png", "full_video_contact_sheet.png"], "ffprobe_json": "ffprobe.json", "scene_metrics_json": "scene_metrics.json", "warnings": ["OCR and transcription are not run automatically in the local baseline."], "manual_review_required": True}}
    (output / "inspection.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    manual_review = {
        "schema_version": "1.0",
        "sample_id": video_id,
        "review_status": "pending",
        "manual_observations": {
            "visible_text_present": "unknown", "first_screen_text": None,
            "estimated_words_first_screen": None, "text_changes_count": None,
            "voice_present": "unknown", "music_present": "unknown",
            "first_spoken_words": None, "speech_start_seconds": None,
        },
        "inferences": {
            "central_thought_count": None, "delayed_reveal": "unknown",
            "delayed_reveal_seconds": None, "hook_text": None,
            "hook_type": None, "cta_present": "unknown",
            "emotional_theme": None, "estimated_required_assets": None,
            "reproducibility_complexity": None,
        },
        "reviewer_notes": None,
    }
    (output / "manual_review.json").write_text(
        json.dumps(manual_review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = f"# Video Format Inspection: {video_id}\n\n## Measured facts\n\n- Duration: {duration:.3f}s\n- Resolution: {video['width']}×{video['height']}\n- Estimated scenes: {metrics['scene_count_estimate']}\n- Unique visual states: {len(states)}\n- Mostly static: {metrics['mostly_static']}\n- Audio present: {audio is not None}\n\n## Limits\n\nOCR, transcription, face detection and semantic interpretation require manual review.\n"
    (output / "inspection.md").write_text(report, encoding="utf-8")
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect one local video without network access."); parser.add_argument("--input", required=True, type=Path); parser.add_argument("--video-id", required=True); parser.add_argument("--output-dir", required=True, type=Path); parser.add_argument("--canonical-url"); args = parser.parse_args(argv)
    try:
        result = inspect(args.input, args.output_dir, args.video_id, args.canonical_url); (args.output_dir / "process_result.json").write_text(json.dumps({"result": "success", "video_id": result["video_id"], "exit_code": 0}, ensure_ascii=False, indent=2), encoding="utf-8"); print("INSPECTION_RESULT=success"); return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"INSPECTION_RESULT=failed: {exc}"); return 2

if __name__ == "__main__": raise SystemExit(main())

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from core.domain import ContentFormat, ProductionBrief

try:
    import imageio_ffmpeg

    _FFMPEG_EXE = Path(imageio_ffmpeg.get_ffmpeg_exe())
except ImportError:
    _FFMPEG_EXE = Path("ffmpeg")

_DEFAULT_FONTS = [
    "C\\:/Windows/Fonts/arial.ttf",
    "C\\:/Windows/Fonts/calibri.ttf",
    "C\\:/Windows/Fonts/segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]

_FONT_CACHE: Path | None = None


def _find_ffmpeg() -> str:
    return str(_FFMPEG_EXE)


def _find_default_font() -> str | None:
    global _FONT_CACHE
    if _FONT_CACHE is not None:
        return str(_FONT_CACHE) if _FONT_CACHE.exists() else None
    for fp in _DEFAULT_FONTS:
        normalized = fp.replace("\\:", ":")
        if Path(normalized).exists():
            _FONT_CACHE = Path(normalized)
            return str(_FONT_CACHE)
    return None


def _fmt_time(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int((secs - int(secs)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _ease_fn(kind: str) -> str:
    if kind == "cubic-in-out":
        return "if(lte(t,0.5),4*pow(t,3),1-pow(-2*t+2,3)/2)"
    if kind == "cubic-out":
        return "1-pow(1-t,3)"
    if kind == "cubic-in":
        return "pow(t,3)"
    return "t"


def _esc(v: str) -> str:
    return (
        v.replace("\\", "\\\\")
        .replace("'", "'\\''")
        .replace(":", "\\:")
        .replace("=", "\\=")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def _ffpath(p: Path) -> str:
    return str(p).replace("\\", "/")


def _ffpath_filter(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", "\\:")


def _resolve_asset(raw: str, project_root: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    return candidate


def _probe_duration(path: Path) -> float:
    ffmpeg = _find_ffmpeg()
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)[.,](\d+)", proc.stderr)
    if not m:
        raise RuntimeError(f"Could not probe duration: {path}")
    return (
        int(m.group(1)) * 3600
        + int(m.group(2)) * 60
        + int(m.group(3))
        + int(m.group(4)) / (10 ** len(m.group(4)))
    )


def generate_srt_from_brief(brief: ProductionBrief) -> str:
    lines: list[str] = []
    idx = 1
    current_time = 0.0

    for i, scene in enumerate(brief.scenes):
        if not scene.narration_text.strip():
            current_time += scene.duration_sec
            if i < len(brief.scenes) - 1:
                current_time -= scene.transition_duration
            continue

        start = current_time
        end = current_time + scene.duration_sec
        lines.append(str(idx))
        lines.append(f"{_fmt_time(start)} --> {_fmt_time(end)}")
        lines.append(scene.narration_text.strip())
        lines.append("")
        idx += 1

        current_time += scene.duration_sec
        if i < len(brief.scenes) - 1:
            current_time -= scene.transition_duration

    return "\n".join(lines)


def _build_scene_filter(
    input_idx: int,
    index: int,
    scene_duration: float,
    W: int,
    H: int,
    fps: int,
    from_scale: float = 1.0,
    to_scale: float = 1.08,
    easing: str = "cubic-in-out",
    label_ctr_start: int = 0,
) -> tuple[str, str, int]:
    label_ctr = label_ctr_start

    def _nl(kind: str = "v") -> str:
        nonlocal label_ctr
        lbl = f"[s{index}n{label_ctr}{kind}]"
        label_ctr += 1
        return lbl

    total_frames = max(1, int(scene_duration * fps))
    scale_diff = abs(to_scale - from_scale) < 0.0001

    fps_label = _nl()
    cmd_parts = [
        f"[{input_idx}:v]fps=fps={fps}{fps_label}",
    ]

    scale_label = _nl()
    cmd_parts.append(
        f"{fps_label}scale=width={W}:height={H}:"
        f"force_original_aspect_ratio=1{scale_label}"
    )

    pad_label = _nl()
    cmd_parts.append(
        f"{scale_label}pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black{pad_label}"
    )

    if not scale_diff:
        t_sub = f"on/{total_frames}"
        ease = _ease_fn(easing)
        ease_expr = re.sub(r"\bt\b", f"({t_sub})", ease)
        rng = to_scale - from_scale
        z_expr = (
            f"if(lt(on,0),{from_scale},"
            f"if(gt(on,{total_frames}),{to_scale},"
            f"{from_scale}+{rng}*({ease_expr})))"
        )
        zoom_label = _nl()
        cmd_parts.append(
            f"{pad_label}zoompan=z='{z_expr}':d=1:s={W}x{H}:fps={fps}:"
            f"x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2){zoom_label}"
        )
        trim_src = zoom_label
    else:
        trim_src = pad_label

    trim_label = _nl()
    cmd_parts.append(
        f"{trim_src}trim=duration={scene_duration},setpts=PTS-STARTPTS{trim_label}"
    )

    filter_str = ";".join(cmd_parts)
    return filter_str, trim_label, label_ctr


def _build_audio_filter(
    voiceover_path: Path | None,
    music_path: Path | None,
    vo_input_idx: int | None,
    music_input_idx: int | None,
    ducking_enabled: bool = True,
    ducking_db: int = 12,
    music_volume: float = 0.15,
    total_duration: float = 0.0,
) -> tuple[str, str]:
    has_vo = voiceover_path is not None and voiceover_path.exists()
    has_music = music_path is not None and music_path.exists()

    if not has_vo and not has_music:
        silence_filter = (
            f"aevalsrc=0:d={total_duration}:s=44100[out]"
        )
        return silence_filter, "[out]"

    if has_vo and has_music:
        threshold = 0.005
        ratio = max(2, min(10, ducking_db // 3))
        attack = 10
        release = 200
        makeup = -ducking_db

        if not ducking_enabled:
            filter_str = (
                f"[{vo_input_idx}:a]asplit[voice_mix][silent];"
                f"[{music_input_idx}:a]aloop=loop=-1:size=2e+09,"
                f"volume={music_volume}[music_vol];"
                f"[voice_mix][music_vol]amix=inputs=2:duration=first[out]"
            )
            return filter_str, "[out]"

        filter_str = (
            f"[{vo_input_idx}:a]asplit[voice_mix][sidechain];"
            f"[{music_input_idx}:a]aloop=loop=-1:size=2e+09,"
            f"volume={music_volume}[music_adj];"
            f"[music_adj][sidechain]sidechaincompress="
            f"threshold={threshold}:ratio={ratio}:"
            f"attack={attack}:release={release}:"
            f"makeup={makeup}:level_sc=1.0[ducked];"
            f"[voice_mix][ducked]amix=inputs=2:duration=first[out]"
        )
        return filter_str, "[out]"

    if has_vo:
        return f"[{vo_input_idx}:a]acopy[out]", "[out]"

    filter_str = (
        f"[{music_input_idx}:a]aloop=loop=-1:size=2e+09,"
        f"volume={music_volume}[out]"
    )
    return filter_str, "[out]"


def build_video_filtergraph(
    brief: ProductionBrief,
    resolution: tuple[int, int],
    fps: int,
) -> str:
    W, H = resolution
    scenes = brief.scenes
    n_scenes = len(scenes)

    if n_scenes == 0:
        raise ValueError("ProductionBrief must have at least one scene")

    parts: list[str] = []
    scene_v_labels: list[str] = []
    label_ctr = 0

    for i, scene in enumerate(scenes):
        from_scale = scene.animation.from_scale
        to_scale = scene.animation.to_scale
        easing = scene.animation.easing

        filter_str, v_label, label_ctr = _build_scene_filter(
            input_idx=i,
            index=i,
            scene_duration=scene.duration_sec,
            W=W,
            H=H,
            fps=fps,
            from_scale=from_scale,
            to_scale=to_scale,
            easing=easing,
            label_ctr_start=label_ctr,
        )
        parts.append(filter_str)
        scene_v_labels.append(v_label)

    if n_scenes == 1:
        fv = scene_v_labels[0]
    else:
        cur_dur = scenes[0].duration_sec
        for i in range(1, n_scenes):
            tr_dur = scenes[i].transition_duration
            tr_type = scenes[i].transition_type or "dissolve"
            offset = cur_dur - tr_dur

            xl = f"[s_xfade_{i}]"

            if i == 1:
                parts.append(
                    f"{scene_v_labels[0]}{scene_v_labels[1]}"
                    f"xfade=transition={tr_type}:duration={tr_dur}:offset={offset}{xl}"
                )
            else:
                prev_xl = f"[s_xfade_{i - 1}]"
                parts.append(
                    f"{prev_xl}{scene_v_labels[i]}"
                    f"xfade=transition={tr_type}:duration={tr_dur}:offset={offset}{xl}"
                )

            cur_dur = cur_dur + scenes[i].duration_sec - tr_dur

        fv = f"[s_xfade_{n_scenes - 1}]"

    return ";".join(parts), fv


def render_narrative_video(
    brief: ProductionBrief,
    output_dir: Path,
    project_root: Path,
) -> dict:
    W = brief.output.resolution_width
    H = brief.output.resolution_height
    fps = brief.output.fps

    if not brief.scenes:
        raise ValueError("ProductionBrief must have at least one scene")

    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = _find_ffmpeg()

    scene_image_paths: list[Path] = []
    for scene in brief.scenes:
        img_path = _resolve_asset(scene.image_source, project_root)
        if not img_path.exists():
            raise FileNotFoundError(f"Scene image not found: {img_path}")
        scene_image_paths.append(img_path)

    total_duration = 0.0
    for i, scene in enumerate(brief.scenes):
        total_duration += scene.duration_sec
        if i < len(brief.scenes) - 1:
            total_duration -= scene.transition_duration

    voiceover_path: Path | None = None
    if brief.audio.voiceover_path:
        vo = _resolve_asset(brief.audio.voiceover_path, project_root)
        if vo.exists():
            voiceover_path = vo

    music_path: Path | None = None
    if brief.audio.music_path:
        mu = _resolve_asset(brief.audio.music_path, project_root)
        if mu.exists():
            music_path = mu

    srt_path: Path | None = None
    if brief.subtitles.enabled and brief.subtitles.mode == "manual":
        srt_content = generate_srt_from_brief(brief)
        if srt_content.strip():
            srt_path = output_dir / "subtitles.srt"
            srt_path.write_text(srt_content, encoding="utf-8")

    video_filter, video_label = build_video_filtergraph(brief, (W, H), fps)

    voiceover_input_idx = len(scene_image_paths)
    music_input_idx = voiceover_input_idx + (1 if voiceover_path else 0)
    vo_idx = voiceover_input_idx if voiceover_path else None
    mu_idx = music_input_idx if music_path else None

    audio_filter, audio_label = _build_audio_filter(
        voiceover_path=voiceover_path,
        music_path=music_path,
        vo_input_idx=vo_idx,
        music_input_idx=mu_idx,
        ducking_enabled=brief.audio.ducking_enabled,
        ducking_db=brief.audio.ducking_reduction_db,
        music_volume=brief.audio.music_volume,
        total_duration=total_duration,
    )

    full_filter = video_filter
    if audio_filter:
        full_filter += ";" + audio_filter

    if srt_path:
        font_path = _resolve_asset(brief.subtitles.font_path, project_root)
        font_file = (
            str(font_path).replace("\\", "/").replace(":", "\\:")
            if font_path and font_path.exists()
            else (_find_default_font() or "")
        )
        font_file_esc = font_file.replace("\\", "\\\\").replace(":", "\\:")

        font_size = brief.subtitles.font_size
        color_hex = brief.subtitles.color.lstrip("#")
        stroke_hex = brief.subtitles.stroke_color.lstrip("#")
        stroke_w = brief.subtitles.stroke_width
        margin_v = int(H * (1.0 - brief.subtitles.y_position))

        force_style = (
            f"FontName=Default,FontSize={font_size},"
            f"PrimaryColour=&H{color_hex},"
            f"OutlineColour=&H{stroke_hex},"
            f"Outline={stroke_w},"
            f"Alignment=2,MarginV={margin_v}"
        )

        sl = f"[s_sub]"
        full_filter += (
            f";{video_label}subtitles="
            f"filename='{_ffpath_filter(srt_path)}':"
            f"fontsdir='{Path(font_file).parent.as_posix()}':"
            f"force_style='{force_style}'{sl}"
        )
        video_label = sl

    cmd: list[str] = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
    ]

    for img_path in scene_image_paths:
        cmd += ["-loop", "1", "-i", str(img_path)]

    if voiceover_path:
        cmd += ["-i", str(voiceover_path)]
    if music_path:
        cmd += ["-i", str(music_path)]

    cmd += [
        "-filter_complex", full_filter,
        "-map", video_label,
        "-map", audio_label,
    ]

    cmd += [
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-t", str(total_duration),
    ]

    output_video = output_dir / "final_video.mp4"
    cmd.append(str(output_video))

    creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
        creationflags=creationflags,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"FFmpeg render failed (code {proc.returncode}):\n{proc.stderr[-3000:]}"
        )

    result: dict[str, Path] = {
        "final_video": output_video,
    }

    if srt_path and srt_path.exists():
        result["subtitles"] = srt_path

    if brief.output.generate_cover and output_video.exists():
        cover_path = output_dir / "cover.png"
        cover_cmd = [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(output_video),
            "-vframes", "1",
            "-q:v", "2",
            str(cover_path),
        ]
        cover_proc = subprocess.run(
            cover_cmd,
            capture_output=True,
            text=True,
            timeout=60,
            creationflags=creationflags,
        )
        if cover_proc.returncode == 0:
            result["cover"] = cover_path

    if brief.output.generate_audio_only and output_video.exists():
        audio_path = output_dir / "audio_only.mp3"
        audio_cmd = [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(output_video),
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "2",
            str(audio_path),
        ]
        audio_proc = subprocess.run(
            audio_cmd,
            capture_output=True,
            text=True,
            timeout=60,
            creationflags=creationflags,
        )
        if audio_proc.returncode == 0:
            result["audio_only"] = audio_path

    return result

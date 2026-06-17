import json
import sys
import librosa
import numpy as np


def analyze(audio_path: str, fps: int = 30, output_path: str = None) -> dict:
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    hop_length = int(sr / fps)
    n_frames = int(np.ceil(len(y) / hop_length))

    mse = np.array([
        np.mean(y[i * hop_length:(i + 1) * hop_length] ** 2)
        for i in range(n_frames)
    ])

    amplitude = np.sqrt(np.maximum(mse, 0))
    max_val = amplitude.max()
    if max_val > 0:
        amplitude = amplitude / max_val

    result = {
        "fps": fps,
        "duration_sec": float(len(y) / sr),
        "frame_count": len(amplitude),
        "amplitudes": amplitude.tolist()
    }

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_voice.py <audio_file> [fps] [output_json]")
        sys.exit(1)

    audio_file = sys.argv[1]
    fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    result = analyze(audio_file, fps, output_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))

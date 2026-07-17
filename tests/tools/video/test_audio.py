from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class MixAudioWithDuckingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_voiceover(self) -> None:
        from core.tools.video.audio import mix_audio_with_ducking

        with self.assertRaises(FileNotFoundError):
            mix_audio_with_ducking(
                voiceover_path=Path("/nonexistent/voice.wav"),
                music_path=Path("/nonexistent/music.mp3"),
                output_path=Path(self.temp_dir.name) / "out.mp3",
            )

    def test_missing_music(self) -> None:
        from core.tools.video.audio import mix_audio_with_ducking

        vo_path = Path(self.temp_dir.name) / "voice.wav"
        vo_path.write_bytes(b"\x00" * 100)

        with self.assertRaises(FileNotFoundError):
            mix_audio_with_ducking(
                voiceover_path=vo_path,
                music_path=Path("/nonexistent/music.mp3"),
                output_path=Path(self.temp_dir.name) / "out.mp3",
            )


class NormalizeAudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_missing_input(self) -> None:
        from core.tools.video.audio import normalize_audio

        with self.assertRaises(FileNotFoundError):
            normalize_audio(
                input_path=Path("/nonexistent/audio.mp3"),
                output_path=Path(self.temp_dir.name) / "out.mp3",
            )

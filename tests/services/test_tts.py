from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.services.tts import FileTTSService, TTSService


class TTSServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tts = FileTTSService()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_tts_service_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            TTSService()  # type: ignore[abstract]

    def test_file_tts_copies_file(self) -> None:
        source_dir = Path(self.temp_dir.name) / "source"
        source_dir.mkdir()
        source_file = source_dir / "voice.wav"
        source_file.write_bytes(b"RIFF...test audio data")

        output_path = Path(self.temp_dir.name) / "output" / "result.wav"

        result = self.tts.synthesize(
            text="test text",
            voice_profile=str(source_file),
            output_path=output_path,
        )

        self.assertEqual(result, output_path)
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.read_bytes(), b"RIFF...test audio data")

    def test_file_tts_missing_source(self) -> None:
        output_path = Path(self.temp_dir.name) / "output" / "result.wav"

        with self.assertRaises(FileNotFoundError):
            self.tts.synthesize(
                text="test text",
                voice_profile="/nonexistent/voice.wav",
                output_path=output_path,
            )

    def test_file_tts_creates_parent_dirs(self) -> None:
        source_dir = Path(self.temp_dir.name) / "source"
        source_dir.mkdir()
        source_file = source_dir / "voice.wav"
        source_file.write_bytes(b"RIFF...test audio data")

        output_path = Path(self.temp_dir.name) / "deeply" / "nested" / "output" / "result.wav"

        result = self.tts.synthesize(
            text="test text",
            voice_profile=str(source_file),
            output_path=output_path,
        )

        self.assertTrue(output_path.exists())
        self.assertEqual(result, output_path)

    def test_tts_interface_has_abstract_method(self) -> None:
        self.assertIn("synthesize", TTSService.__abstractmethods__)

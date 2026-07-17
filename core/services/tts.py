from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path


class TTSService(ABC):

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice_profile: str,
        output_path: Path,
        language: str | None = None,
    ) -> Path:
        ...


class FileTTSService(TTSService):

    def synthesize(
        self,
        text: str,
        voice_profile: str,
        output_path: Path,
        language: str | None = None,
    ) -> Path:
        source = Path(voice_profile)
        if not source.exists():
            raise FileNotFoundError(f"Voiceover file not found: {source}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, output_path)
        return output_path

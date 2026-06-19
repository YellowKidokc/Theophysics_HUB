"""Text-to-speech provider (no UI).

Windows-first: speech goes through the built-in ``System.Speech`` SAPI voices
via PowerShell, so there is no extra Python dependency to install. The call is
isolated here behind a small class so it can be swapped for another backend
later without touching the TTS panel.
"""

from __future__ import annotations

import platform
import subprocess
from typing import Any


class TTSError(RuntimeError):
    """Raised when speech synthesis fails or is unsupported on this platform."""


class TTSProvider:
    """Speaks text aloud using the host platform's speech engine."""

    def __init__(self, voice: str = "", rate: int = 0):
        self.voice = voice
        # SAPI rate is an integer in [-10, 10]; clamp to keep callers honest.
        self.rate = max(-10, min(10, int(rate)))

    @classmethod
    def from_config(cls, tts_cfg: dict[str, Any]) -> "TTSProvider":
        return cls(voice=str(tts_cfg.get("voice", "")), rate=int(tts_cfg.get("rate", 0)))

    def is_supported(self) -> bool:
        return platform.system() == "Windows"

    def speak(self, text: str) -> None:
        """Speak ``text`` synchronously. Raises :class:`TTSError` on failure."""
        if not text.strip():
            raise TTSError("No text to speak.")
        if not self.is_supported():
            raise TTSError("Text-to-speech is only wired for Windows (System.Speech) right now.")
        self._speak_windows(text)

    def _speak_windows(self, text: str) -> None:
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$s.Rate = {self.rate};"
        )
        if self.voice:
            # SelectVoice throws on an unknown voice; guard so a bad config name
            # falls back to the default voice instead of failing the whole call.
            script += f"try {{ $s.SelectVoice('{self.voice}') }} catch {{ }};"
        script += "$s.Speak([Console]::In.ReadToEnd());"

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or "").strip()[:300]
            raise TTSError(f"Speech synthesis failed: {detail or 'unknown error'}")

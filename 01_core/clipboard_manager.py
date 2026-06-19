"""Clipboard and selection payload helpers with no UI dependencies."""

from __future__ import annotations

import datetime as dt
import os
import platform
import subprocess
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class TextPayload:
    selection: str
    clipboard: str
    timestamp: str
    source_app: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ClipboardManager:
    """Captures text payloads for action execution.

    AHK is responsible for copying selected text before invoking Python on
    Windows. This class reads the resulting clipboard text and accepts an
    explicit selection supplied by the trigger layer.
    """

    def build_payload(self, selection: str = "", clipboard: str | None = None, source_app: str = "") -> TextPayload:
        clip = self.get_clipboard_text() if clipboard is None else clipboard
        return TextPayload(
            selection=selection or "",
            clipboard=clip or "",
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            source_app=source_app or self.get_source_app(),
        )

    def get_clipboard_text(self) -> str:
        if platform.system() == "Windows":
            return self._powershell_clipboard()
        return self._tk_clipboard()

    def set_clipboard_text(self, text: str) -> None:
        if platform.system() == "Windows":
            script = "Set-Clipboard -Value ([Console]::In.ReadToEnd())"
            subprocess.run(["powershell", "-NoProfile", "-Command", script], input=text, text=True, check=False)
            return
        self._tk_set_clipboard(text)

    def get_source_app(self) -> str:
        return os.environ.get("THEOPHYSICS_SOURCE_APP", "unknown")

    @staticmethod
    def _powershell_clipboard() -> str:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True,
            text=True,
            check=False,
        )
        return completed.stdout.rstrip("\r\n") if completed.returncode == 0 else ""

    @staticmethod
    def _tk_clipboard() -> str:
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            try:
                return root.clipboard_get()
            finally:
                root.destroy()
        except Exception:
            return ""

    @staticmethod
    def _tk_set_clipboard(text: str) -> None:
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
        except Exception:
            return


def current_clipboard_payload() -> dict[str, Any]:
    return ClipboardManager().build_payload().as_dict()

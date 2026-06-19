"""Clipboard and selection payload helpers with no UI dependencies."""

from __future__ import annotations

import datetime as dt
import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from typing import Any


class ClipboardError(RuntimeError):
    """Raised when clipboard access fails in a predictable way."""


@dataclass(frozen=True)
class TextPayload:
    """Text context passed from trigger/UI layers into action execution."""

    selection: str
    clipboard: str
    timestamp: str
    source_app: str
    trigger_source: str = "unknown"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def text(self) -> str:
        return self.selection or self.clipboard


class ClipboardManager:
    """Captures clipboard-backed text payloads for action execution."""

    def build_payload(
        self,
        selection: str = "",
        clipboard: str | None = None,
        source_app: str = "",
        trigger_source: str = "unknown",
    ) -> TextPayload:
        clip = self.get_clipboard_text() if clipboard is None else clipboard
        return TextPayload(
            selection=selection or "",
            clipboard=clip or "",
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            source_app=source_app or self.get_source_app(),
            trigger_source=trigger_source,
        )

    def get_clipboard_text(self) -> str:
        if platform.system() == "Windows":
            return self._powershell_clipboard()
        return self._tk_clipboard()

    def set_clipboard_text(self, text: str) -> None:
        if platform.system() == "Windows":
            script = "Set-Clipboard -Value ([Console]::In.ReadToEnd())"
            completed = subprocess.run(["powershell", "-NoProfile", "-Command", script], input=text, text=True, check=False)
            if completed.returncode != 0:
                raise ClipboardError("PowerShell Set-Clipboard failed")
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
        if completed.returncode != 0:
            raise ClipboardError("PowerShell Get-Clipboard failed")
        return completed.stdout.rstrip("\r\n")

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
        except Exception as exc:
            raise ClipboardError(f"Tk clipboard read failed: {exc}") from exc

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
        except Exception as exc:
            raise ClipboardError(f"Tk clipboard write failed: {exc}") from exc


def current_clipboard_payload() -> dict[str, Any]:
    return ClipboardManager().build_payload().as_dict()

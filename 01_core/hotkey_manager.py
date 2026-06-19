"""Hotkey configuration helper.

On Windows the actual key capture lives in ``07_ahk/Stratum.ahk`` (the thin
native trigger layer). This module does not hook keys itself; it exposes the
configured hotkey-to-command mapping so the value is testable and the GUI can
display an accurate, single-sourced hotkey reference.
"""

from __future__ import annotations

from pathlib import Path

from config_loader import ConfigLoader

# Maps the logical hotkey names in config.json to the stratum_cli command the
# AHK layer invokes. Keeping this here means the AHK script and the in-app
# hotkey reference never drift from one another silently.
HOTKEY_COMMANDS: dict[str, str] = {
    "gui": "gui",
    "clipboard": "gui clipboard",
    "prompts": "gui prompts",
    "links": "gui links",
    "tts": "gui tts",
    "rewrite": "rewrite",
}


class HotkeyManager:
    """Reads the configured hotkeys and pairs them with their commands."""

    def __init__(self, root: Path, config: ConfigLoader | None = None):
        self.config = config or ConfigLoader(root.resolve())

    def bindings(self) -> dict[str, str]:
        """Return ``{key_combo: command}`` for every configured hotkey."""
        configured = self.config.app_config().get("hotkeys", {})
        bindings: dict[str, str] = {}
        for name, command in HOTKEY_COMMANDS.items():
            keys = configured.get(name)
            if isinstance(keys, str) and keys.strip():
                bindings[keys.strip()] = command
        return bindings

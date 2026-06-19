"""Centralized JSON configuration access for Theophysics HUB.

Every part of the app reads configuration through this loader so that
``04_config`` stays the single source of truth. Keeping config access in one
place avoids scattered ``open()`` calls and gives callers typed, validated
accessors instead of raw dictionaries.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigError(RuntimeError):
    """Raised when a required configuration file is missing or malformed."""


class ConfigLoader:
    """Loads source-of-truth JSON config files from ``04_config``."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.config_dir = self.root / "04_config"

    # -- raw access ---------------------------------------------------------
    def load_json(self, name: str) -> Any:
        path = self.config_dir / name
        if not path.exists():
            raise ConfigError(f"Missing config file: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc

    def load_json_or(self, name: str, default: Any) -> Any:
        """Return parsed config or ``default`` when the file is absent.

        Used for optional config (links, prompts) so the app degrades to an
        empty panel instead of crashing when a file has not been created yet.
        """
        path = self.config_dir / name
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc

    # -- typed accessors ----------------------------------------------------
    def app_config(self) -> dict[str, Any]:
        value = self.load_json("config.json")
        if not isinstance(value, dict):
            raise ConfigError("04_config/config.json must contain a JSON object")
        return value

    def actions_config(self) -> list[dict[str, Any]]:
        value = self.load_json("actions.json")
        return self._require_object_list(value, "04_config/actions.json")

    def prompts_config(self) -> list[dict[str, Any]]:
        value = self.load_json_or("prompts.json", [])
        return self._require_object_list(value, "04_config/prompts.json")

    def links_config(self) -> list[dict[str, Any]]:
        value = self.load_json_or("links.json", [])
        return self._require_object_list(value, "04_config/links.json")

    def hotkeys_config(self) -> list[dict[str, Any]]:
        value = self.load_json_or("hotkeys.json", [])
        return self._require_object_list(value, "04_config/hotkeys.json")

    def openai_config(self) -> dict[str, Any]:
        value = self.app_config().get("openai", {})
        return value if isinstance(value, dict) else {}

    def clipboard_config(self) -> dict[str, Any]:
        value = self.app_config().get("clipboard", {})
        return value if isinstance(value, dict) else {}

    def tts_config(self) -> dict[str, Any]:
        value = self.app_config().get("tts", {})
        return value if isinstance(value, dict) else {}

    def panels(self) -> list[str]:
        value = self.app_config().get("panels", [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ConfigError("config.json 'panels' must be a list of strings")
        return value

    @staticmethod
    def _require_object_list(value: Any, label: str) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ConfigError(f"{label} must contain a JSON list")
        if not all(isinstance(item, dict) for item in value):
            raise ConfigError(f"Every record in {label} must be a JSON object")
        return value

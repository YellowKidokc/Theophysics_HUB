"""Centralized JSON configuration access for Theophysics HUB."""

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

    def load_json(self, name: str) -> Any:
        path = self.config_dir / name
        if not path.exists():
            raise ConfigError(f"Missing config file: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc

    def app_config(self) -> dict[str, Any]:
        value = self.load_json("config.json")
        if not isinstance(value, dict):
            raise ConfigError("04_config/config.json must contain a JSON object")
        return value

    def actions_config(self) -> list[dict[str, Any]]:
        value = self.load_json("actions.json")
        if not isinstance(value, list):
            raise ConfigError("04_config/actions.json must contain a JSON list")
        if not all(isinstance(item, dict) for item in value):
            raise ConfigError("Every action record must be a JSON object")
        return value

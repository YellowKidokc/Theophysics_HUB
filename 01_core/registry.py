"""Content registry that feeds the shell's panels.

This is deliberately separate from :class:`action_registry.ActionRegistry`:
that registry *executes* code, while this one only loads declarative content
(prompts, links, hotkeys) into typed records for display. Keeping the two
apart preserves a clear boundary between "things we run" and "things we show".
"""

from __future__ import annotations

from pathlib import Path

from config_loader import ConfigLoader
from models import AppState, HotkeyRecord, LinkRecord, PromptRecord


class Registry:
    """Loads prompts, links, and hotkeys from ``04_config`` into an ``AppState``."""

    def __init__(self, root: Path, config: ConfigLoader | None = None):
        self.root = root.resolve()
        self.config = config or ConfigLoader(self.root)

    def load(self) -> AppState:
        prompts = [PromptRecord.from_config(item) for item in self.config.prompts_config()]
        links = [LinkRecord.from_config(item) for item in self.config.links_config()]
        hotkeys = [HotkeyRecord.from_config(item) for item in self.config.hotkeys_config()]
        meta = {"app_name": self.config.app_config().get("app_name", "Stratum")}
        return AppState(prompts=prompts, links=links, hotkeys=hotkeys, meta=meta)

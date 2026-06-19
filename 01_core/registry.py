import json
from pathlib import Path

from models import ActionRecord, AppState, HotkeyRecord, PromptRecord


class Registry:
    def __init__(self, root: Path):
        self.root = root
        self.config_dir = root / "04_config"
        self.state = AppState()

    def load(self) -> AppState:
        prompts = self._read_json("prompts.json", [])
        hotkeys = self._read_json("hotkeys.json", [])
        actions = self._read_json("actions.json", [])
        self.state.prompts = [PromptRecord(**item) for item in prompts]
        self.state.hotkeys = [HotkeyRecord(**item) for item in hotkeys]
        self.state.actions = [ActionRecord(**item) for item in actions]
        return self.state

    def _read_json(self, name: str, default):
        path = self.config_dir / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

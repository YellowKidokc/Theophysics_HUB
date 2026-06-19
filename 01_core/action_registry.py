import importlib.util
import json
from pathlib import Path


class ActionRegistry:
    def __init__(self, root: Path):
        self.root = root
        self.actions_dir = root / "08_actions"
        self.actions = json.loads((root / "04_config" / "actions.json").read_text(encoding="utf-8"))

    def list_actions(self) -> list[dict]:
        return self.actions

    def run(self, action_id: str, data: dict) -> str:
        record = next(item for item in self.actions if item["id"] == action_id)
        module_path = self.root / record["entry"]
        spec = importlib.util.spec_from_file_location(action_id, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module.process(data)

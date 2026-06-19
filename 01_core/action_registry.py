"""Config-driven action registry and runner for Theophysics HUB."""

from __future__ import annotations

import importlib.util
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class ActionExecutionError(RuntimeError):
    """Raised when an action cannot be loaded or executed."""


@dataclass(frozen=True)
class ActionRecord:
    """Validated action metadata loaded from ``04_config/actions.json``."""

    id: str
    name: str
    entry: Path
    description: str = ""

    @classmethod
    def from_config(cls, raw: dict[str, Any], root: Path) -> "ActionRecord":
        missing = [key for key in ("id", "name", "entry") if not raw.get(key)]
        if missing:
            raise ValueError(f"Action record missing required fields: {', '.join(missing)}")

        entry = (root / str(raw["entry"])).resolve()
        actions_dir = (root / "08_actions").resolve()
        if actions_dir not in entry.parents:
            raise ValueError(f"Action entry must live in 08_actions: {raw['entry']}")
        if not entry.exists():
            raise ValueError(f"Action entry does not exist: {raw['entry']}")

        return cls(
            id=str(raw["id"]),
            name=str(raw["name"]),
            entry=entry,
            description=str(raw.get("description", "")),
        )


@dataclass(frozen=True)
class ActionResult:
    """Stable result shape returned by action executions."""

    action_id: str
    ok: bool
    output: str
    error: str | None = None


class ActionRegistry:
    """Loads configured action scripts and executes their ``process(data)`` function."""

    def __init__(self, root: Path, logger: logging.Logger | None = None):
        self.root = root.resolve()
        self.logger = logger or logging.getLogger("theophysics.actions")
        self._records = self._load_records()

    def list_actions(self) -> list[ActionRecord]:
        return list(self._records.values())

    def get(self, action_id: str) -> ActionRecord:
        try:
            return self._records[action_id]
        except KeyError as exc:
            raise ActionExecutionError(f"Unknown action: {action_id}") from exc

    def run(self, action_id: str, payload: dict[str, Any]) -> ActionResult:
        self.logger.info("action_start", extra={"action_id": action_id})
        try:
            record = self.get(action_id)
            module = self._load_module(record)
            processor = self._get_processor(module, record)
            output = processor(payload)
            result = ActionResult(action_id=action_id, ok=True, output=str(output or ""))
            self.logger.info("action_success", extra={"action_id": action_id})
            return result
        except Exception as exc:  # keep UI alive; report cleanly
            message = str(exc) or exc.__class__.__name__
            self.logger.error(
                "action_failure",
                extra={"action_id": action_id, "error": message},
                exc_info=True,
            )
            return ActionResult(action_id=action_id, ok=False, output="", error=message)

    def _load_records(self) -> dict[str, ActionRecord]:
        config_path = self.root / "04_config" / "actions.json"
        raw_records = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw_records, list):
            raise ValueError("04_config/actions.json must contain a list of actions")

        records: dict[str, ActionRecord] = {}
        for raw in raw_records:
            record = ActionRecord.from_config(raw, self.root)
            if record.id in records:
                raise ValueError(f"Duplicate action id: {record.id}")
            records[record.id] = record
        return records

    def _load_module(self, record: ActionRecord) -> ModuleType:
        spec = importlib.util.spec_from_file_location(f"theophysics_action_{record.id}", record.entry)
        if spec is None or spec.loader is None:
            raise ActionExecutionError(f"Cannot import action module: {record.entry}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def _get_processor(module: ModuleType, record: ActionRecord) -> Callable[[dict[str, Any]], Any]:
        processor = getattr(module, "process", None)
        if not callable(processor):
            raise ActionExecutionError(f"Action {record.id} does not expose process(data)")
        return processor

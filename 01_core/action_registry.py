"""Config-driven action registry and runner for Theophysics HUB."""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from config_loader import ConfigLoader


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
        missing = [key for key in ("id", "name", "entry") if not str(raw.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Action record missing required fields: {', '.join(missing)}")

        action_id = str(raw["id"]).strip()
        if not action_id.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Action id contains unsupported characters: {action_id}")

        entry = (root / str(raw["entry"])).resolve()
        actions_dir = (root / "08_actions").resolve()
        if actions_dir != entry.parent and actions_dir not in entry.parents:
            raise ValueError(f"Action entry must live in 08_actions: {raw['entry']}")
        if entry.suffix != ".py":
            raise ValueError(f"Action entry must be a Python file: {raw['entry']}")
        if not entry.exists():
            raise ValueError(f"Action entry does not exist: {raw['entry']}")

        return cls(
            id=action_id,
            name=str(raw["name"]).strip(),
            entry=entry,
            description=str(raw.get("description", "")).strip(),
        )


@dataclass(frozen=True)
class ActionResult:
    """Stable result shape returned by action executions."""

    action_id: str
    ok: bool
    output: str = ""
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ActionRegistry:
    """Loads configured action scripts and executes their ``process(data)`` function."""

    def __init__(self, root: Path, logger: logging.Logger | None = None, config: ConfigLoader | None = None):
        self.root = root.resolve()
        self.logger = logger or logging.getLogger("theophysics.actions")
        self.config = config or ConfigLoader(self.root)
        self._records = self._load_records()
        self._module_cache: dict[str, ModuleType] = {}

    def list_actions(self) -> list[ActionRecord]:
        """Return configured actions in config order."""
        return list(self._records.values())

    def get(self, action_id: str) -> ActionRecord:
        try:
            return self._records[action_id]
        except KeyError as exc:
            raise ActionExecutionError(f"Unknown action: {action_id}") from exc

    def run(self, action_id: str, payload: dict[str, Any]) -> ActionResult:
        """Run an action and return a non-throwing result for UI callers."""
        trigger_source = str(payload.get("trigger_source", "unknown"))
        self.logger.info("action_start", extra={"action_id": action_id, "trigger_source": trigger_source})
        try:
            record = self.get(action_id)
            processor = self._get_processor(self._load_module(record), record)
            output = processor(dict(payload))
            result = ActionResult(action_id=action_id, ok=True, output=str(output or ""))
            self.logger.info("action_success", extra={"action_id": action_id, "trigger_source": trigger_source})
            return result
        except Exception as exc:  # keep UI alive; report cleanly
            message = str(exc) or exc.__class__.__name__
            self.logger.error(
                "action_failure",
                extra={"action_id": action_id, "trigger_source": trigger_source, "error": message},
                exc_info=True,
            )
            return ActionResult(action_id=action_id, ok=False, error=message)

    def _load_records(self) -> dict[str, ActionRecord]:
        records: dict[str, ActionRecord] = {}
        for raw in self.config.actions_config():
            record = ActionRecord.from_config(raw, self.root)
            if record.id in records:
                raise ValueError(f"Duplicate action id: {record.id}")
            records[record.id] = record
        return records

    def _load_module(self, record: ActionRecord) -> ModuleType:
        cached = self._module_cache.get(record.id)
        if cached is not None:
            return cached
        spec = importlib.util.spec_from_file_location(f"theophysics_action_{record.id}", record.entry)
        if spec is None or spec.loader is None:
            raise ActionExecutionError(f"Cannot import action module: {record.entry}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._module_cache[record.id] = module
        return module

    @staticmethod
    def _get_processor(module: ModuleType, record: ActionRecord) -> Callable[[dict[str, Any]], Any]:
        processor = getattr(module, "process", None)
        if not callable(processor):
            raise ActionExecutionError(f"Action {record.id} does not expose process(data)")
        return processor

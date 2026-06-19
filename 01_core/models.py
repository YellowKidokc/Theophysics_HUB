from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptRecord:
    name: str
    content: str
    hotkey: str | None = None


@dataclass
class HotkeyRecord:
    keys: str
    action: str


@dataclass
class ActionRecord:
    id: str
    name: str
    entry: str
    description: str = ""
    kind: str = "python"


@dataclass
class AppState:
    prompts: list[PromptRecord] = field(default_factory=list)
    hotkeys: list[HotkeyRecord] = field(default_factory=list)
    actions: list[ActionRecord] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

"""Typed domain models shared by the UI panels.

Action execution has its own authoritative ``ActionRecord``/``ActionResult``
in :mod:`action_registry`. These models cover the *content* surfaces the shell
renders (prompts, links, hotkeys, clipboard slots), so the panels work with
typed objects instead of loose dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PromptRecord:
    """A reusable prompt template from ``04_config/prompts.json``."""

    name: str
    content: str
    hotkey: str | None = None

    @classmethod
    def from_config(cls, raw: dict[str, Any]) -> "PromptRecord":
        name = str(raw.get("name", "")).strip()
        content = str(raw.get("content", ""))
        if not name or not content:
            raise ValueError("Prompt records require 'name' and 'content'")
        hotkey = raw.get("hotkey")
        return cls(name=name, content=content, hotkey=str(hotkey) if hotkey else None)


@dataclass(frozen=True)
class LinkRecord:
    """A quick-access link from ``04_config/links.json``."""

    label: str
    url: str
    category: str = ""

    @classmethod
    def from_config(cls, raw: dict[str, Any]) -> "LinkRecord":
        label = str(raw.get("label", "")).strip()
        url = str(raw.get("url", "")).strip()
        if not label or not url:
            raise ValueError("Link records require 'label' and 'url'")
        return cls(label=label, url=url, category=str(raw.get("category", "")).strip())


@dataclass(frozen=True)
class HotkeyRecord:
    """A configured hotkey-to-action binding from ``04_config/hotkeys.json``."""

    keys: str
    action: str

    @classmethod
    def from_config(cls, raw: dict[str, Any]) -> "HotkeyRecord":
        keys = str(raw.get("keys", "")).strip()
        action = str(raw.get("action", "")).strip()
        if not keys or not action:
            raise ValueError("Hotkey records require 'keys' and 'action'")
        return cls(keys=keys, action=action)


@dataclass
class ClipboardSlot:
    """One persisted clipboard slot in the multi-slot store."""

    index: int
    text: str = ""
    timestamp: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.text

    def preview(self, width: int = 60) -> str:
        flattened = " ".join(self.text.split())
        if len(flattened) <= width:
            return flattened
        return flattened[: width - 1] + "…"


@dataclass
class AppState:
    """Aggregated content the shell renders, loaded by :class:`registry.Registry`."""

    prompts: list[PromptRecord] = field(default_factory=list)
    links: list[LinkRecord] = field(default_factory=list)
    hotkeys: list[HotkeyRecord] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

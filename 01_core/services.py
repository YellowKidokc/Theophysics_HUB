"""Composition root for backend services.

A single place that wires the core objects together so the app shell, popup,
and CLI all build services the same way. UI code receives a ready
:class:`CoreServices` bundle instead of constructing registries itself, which
keeps the dependency graph explicit and the UI free of backend assembly logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from action_registry import ActionRegistry
from clipboard_manager import ClipboardManager
from clipboard_store import ClipboardStore
from config_loader import ConfigLoader
from logger import configure_file_logger
from models import AppState
from prompt_engine import PromptEngine
from registry import Registry
from tts import TTSProvider


@dataclass
class CoreServices:
    """Everything the UI layers need, assembled once at startup."""

    root: Path
    config: ConfigLoader
    actions: ActionRegistry
    content: AppState
    prompts: PromptEngine
    clipboard: ClipboardManager
    clipboard_store: ClipboardStore
    tts: TTSProvider
    app_logger: logging.Logger
    action_logger: logging.Logger


def build_core_services(root: Path) -> CoreServices:
    """Construct and return the full backend service bundle."""
    root = root.resolve()
    config = ConfigLoader(root)

    action_logger = configure_file_logger(root, "theophysics.actions", "actions.log")
    app_logger = configure_file_logger(root, "theophysics.app", "app.log")

    actions = ActionRegistry(root, action_logger, config)
    content = Registry(root, config).load()
    prompts = PromptEngine(content.prompts)
    clipboard = ClipboardManager()
    clipboard_store = ClipboardStore.from_config(root, config.clipboard_config())
    tts = TTSProvider.from_config(config.tts_config())

    app_logger.info("services_ready")
    return CoreServices(
        root=root,
        config=config,
        actions=actions,
        content=content,
        prompts=prompts,
        clipboard=clipboard,
        clipboard_store=clipboard_store,
        tts=tts,
        app_logger=app_logger,
        action_logger=action_logger,
    )

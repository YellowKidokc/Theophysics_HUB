"""Command bridge used by AHK to open GUI surfaces and run actions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_core"))
sys.path.insert(0, str(ROOT / "03_ui_python"))

from action_registry import ActionRegistry  # noqa: E402
from clipboard_manager import ClipboardError, ClipboardManager  # noqa: E402
from logger import configure_file_logger  # noqa: E402


def _services() -> tuple[ActionRegistry, ClipboardManager]:
    action_logger = configure_file_logger(ROOT, "theophysics.actions", "actions.log")
    app_logger = configure_file_logger(ROOT, "theophysics.app", "app.log")
    app_logger.info("services_ready")
    return ActionRegistry(ROOT, action_logger), ClipboardManager()


def open_gui() -> int:
    from PySide6 import QtWidgets
    from action_popup import MainShellWindow

    configure_file_logger(ROOT, "theophysics.app", "app.log").info("open_gui", extra={"trigger_source": "ahk"})
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    shell = MainShellWindow(ROOT)
    shell.show()
    return app.exec()


def open_popup() -> int:
    from PySide6 import QtWidgets
    from action_popup import ActionPopup

    registry, clipboard = _services()
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    popup = ActionPopup(registry, clipboard)
    try:
        payload = clipboard.build_payload(trigger_source="popup").as_dict()
    except ClipboardError as exc:
        payload = {"selection": "", "clipboard": "", "source_app": "unknown", "trigger_source": "popup", "error": str(exc)}
    popup.load(payload)
    popup.show()
    return app.exec()


def rewrite() -> int:
    registry, clipboard = _services()
    try:
        payload = clipboard.build_payload(trigger_source="rewrite_hotkey").as_dict()
        result = registry.run("rewrite_coherent_openai", payload)
        text = result.output if result.ok else f"Action failed: {result.error}"
        clipboard.set_clipboard_text(text)
        print(text)
        return 0 if result.ok else 1
    except ClipboardError as exc:
        print(f"Clipboard failed: {exc}")
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Theophysics HUB command bridge")
    parser.add_argument("command", choices=["gui", "popup", "rewrite"])
    args = parser.parse_args(argv)
    if args.command == "gui":
        return open_gui()
    if args.command == "popup":
        return open_popup()
    if args.command == "rewrite":
        return rewrite()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Command bridge used by AHK to open GUI surfaces and run actions.

This is the single entry point the thin AHK trigger layer shells out to. It
owns no application logic itself: it builds the core service bundle and hands
control to the shell window, popup, or rewrite flow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_core"))
sys.path.insert(0, str(ROOT / "03_ui_python"))

from clipboard_manager import ClipboardError  # noqa: E402
from services import build_core_services  # noqa: E402

# Named pipe used so panel hotkeys reuse one running shell instead of stacking
# duplicate windows.
SHELL_SERVER_NAME = "TheophysicsHubShell"
DEFAULT_PANEL = "dashboard"


def open_gui(panel: str) -> int:
    """Open the shell on ``panel``, or route to an already-running shell."""
    from PySide6 import QtWidgets
    from main_window import MainShellWindow
    from single_instance import PanelRouter

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    router = PanelRouter(SHELL_SERVER_NAME)
    if router.send_to_running(panel):
        return 0

    services = build_core_services(ROOT)
    services.app_logger.info("open_gui", extra={"trigger_source": panel or DEFAULT_PANEL})
    shell = MainShellWindow(services)
    router.start_server(lambda requested: shell.show_panel(requested or DEFAULT_PANEL))

    # When a tray is available, keep the process resident on window close so
    # panel hotkeys keep routing to this instance.
    from tray_icon import TrayIcon

    tray: TrayIcon | None = None
    if TrayIcon.is_available():
        app.setQuitOnLastWindowClosed(False)
        tray = TrayIcon(app, shell)
        tray.show()

    shell.show()
    shell.show_panel(panel or DEFAULT_PANEL)
    return app.exec()


def open_popup() -> int:
    """Open the middle-mouse action popup with the current selection/clipboard."""
    from PySide6 import QtWidgets
    from action_popup import ActionPopup

    services = build_core_services(ROOT)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    popup = ActionPopup(services.actions, services.clipboard)
    try:
        payload = services.clipboard.build_payload(trigger_source="popup").as_dict()
    except ClipboardError as exc:
        payload = {
            "selection": "",
            "clipboard": "",
            "source_app": "unknown",
            "trigger_source": "popup",
            "error": str(exc),
        }
    popup.load(payload)
    popup.show()
    return app.exec()


def rewrite() -> int:
    """Run the OpenAI coherent rewrite on selected/clipboard text (Ctrl+Space)."""
    services = build_core_services(ROOT)
    try:
        payload = services.clipboard.build_payload(trigger_source="rewrite_hotkey").as_dict()
        result = services.actions.run("rewrite_coherent_openai", payload)
        text = result.output if result.ok else f"Action failed: {result.error}"
        services.clipboard.set_clipboard_text(text)
        print(text)
        return 0 if result.ok else 1
    except ClipboardError as exc:
        print(f"Clipboard failed: {exc}")
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Theophysics HUB command bridge")
    parser.add_argument("command", choices=["gui", "popup", "rewrite"])
    parser.add_argument(
        "panel",
        nargs="?",
        default=DEFAULT_PANEL,
        help="Panel to focus when command is 'gui' (dashboard, clipboard, prompts, links, tts)",
    )
    args = parser.parse_args(argv)
    if args.command == "gui":
        return open_gui(args.panel)
    if args.command == "popup":
        return open_popup()
    if args.command == "rewrite":
        return rewrite()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

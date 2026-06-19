"""System tray icon for the resident shell.

The first shell instance stays resident so panel hotkeys can route to it. The
tray icon gives that resident process a visible affordance: click to reopen the
window, or quit the hub entirely.
"""

from __future__ import annotations

from typing import Any


class TrayIcon:
    """Wraps a ``QSystemTrayIcon`` bound to the running shell window."""

    def __init__(self, app: Any, shell: Any):
        from PySide6 import QtWidgets

        self._icon = QtWidgets.QSystemTrayIcon()
        self._icon.setIcon(app.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        self._icon.setToolTip("Theophysics HUB")

        menu = QtWidgets.QMenu()
        menu.addAction("Open HUB").triggered.connect(shell.raise_window)
        menu.addSeparator()
        menu.addAction("Quit").triggered.connect(app.quit)
        self._icon.setContextMenu(menu)

        def on_activated(reason: Any) -> None:
            if reason == QtWidgets.QSystemTrayIcon.Trigger:
                shell.raise_window()

        self._icon.activated.connect(on_activated)

    def show(self) -> None:
        self._icon.show()

    @staticmethod
    def is_available() -> bool:
        from PySide6 import QtWidgets

        return QtWidgets.QSystemTrayIcon.isSystemTrayAvailable()

"""PySide6 action popup and main shell windows."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ActionPopup:
    """Popup widget that delegates action execution to injected services."""

    def __init__(self, registry: Any, clipboard_manager: Any):
        from PySide6 import QtWidgets

        self.registry = registry
        self.clipboard_manager = clipboard_manager
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("Theophysics Actions")
        self.window.resize(760, 560)

        layout = QtWidgets.QVBoxLayout(self.window)
        self.preview = QtWidgets.QPlainTextEdit()
        self.preview.setPlaceholderText("Selected text or clipboard preview")
        self.preview.setMaximumHeight(130)
        self.actions = QtWidgets.QListWidget()
        self.result = QtWidgets.QPlainTextEdit()
        self.result.setPlaceholderText("Action result")
        self.run_button = QtWidgets.QPushButton("Run Action")
        self.copy_button = QtWidgets.QPushButton("Copy Result")
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.copy_button)

        layout.addWidget(self.preview)
        layout.addWidget(self.actions)
        layout.addLayout(buttons)
        layout.addWidget(self.result)

        self._payload: dict[str, Any] = {}
        self._records = []
        self.run_button.clicked.connect(self.run_selected_action)
        self.copy_button.clicked.connect(self.copy_result)

    def load(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        text = payload.get("selection") or payload.get("clipboard") or ""
        self.preview.setPlainText(text)
        self.actions.clear()
        self._records = self.registry.list_actions()
        for record in self._records:
            self.actions.addItem(f"{record.name} — {record.description}")
        if self._records:
            self.actions.setCurrentRow(0)

    def show(self) -> None:
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def run_selected_action(self) -> None:
        row = self.actions.currentRow()
        if row < 0 or row >= len(self._records):
            self.result.setPlainText("Select an action first.")
            return
        record = self._records[row]
        result = self.registry.run(record.id, self._payload)
        self.result.setPlainText(result.output if result.ok else f"Action failed: {result.error}")

    def copy_result(self) -> None:
        self.clipboard_manager.set_clipboard_text(self.result.toPlainText())


class MainShellWindow:
    """Small PySide6 shell that proves the desktop app has a real GUI surface."""

    def __init__(self, root: Path):
        from PySide6 import QtWidgets

        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("Theophysics HUB")
        self.window.resize(900, 620)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        title = QtWidgets.QLabel("Theophysics HUB")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QtWidgets.QLabel("Windows-first action hub: clipboard, prompts, links, TTS, and rewrite tools.")
        paths = QtWidgets.QPlainTextEdit()
        paths.setReadOnly(True)
        paths.setPlainText(f"Repo: {root}\nConfig: {root / '04_config'}\nLogs: {root / '05_logs'}")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(paths)
        self.window.setCentralWidget(central)

    def show(self) -> None:
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

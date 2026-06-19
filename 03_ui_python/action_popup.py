"""PySide6 action popup triggered by the middle-mouse button."""

from __future__ import annotations

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
        layout.addWidget(QtWidgets.QLabel("Selected text / clipboard preview"))
        self.preview = QtWidgets.QPlainTextEdit()
        self.preview.setPlaceholderText("Selected text or clipboard preview")
        self.preview.setMaximumHeight(130)

        layout.addWidget(QtWidgets.QLabel("Configured actions"))
        self.actions = QtWidgets.QListWidget()

        self.status = QtWidgets.QLabel("Ready")
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
        layout.addWidget(self.status)
        layout.addWidget(self.result)

        self._payload: dict[str, Any] = {}
        self._records = []
        self.run_button.clicked.connect(self.run_selected_action)
        self.copy_button.clicked.connect(self.copy_result)

    def load(self, payload: dict[str, Any]) -> None:
        self._payload = dict(payload)
        text = self._payload.get("selection") or self._payload.get("clipboard") or ""
        self.preview.setPlainText(text)
        self.result.clear()
        self.status.setText("Ready")
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
            self.status.setText("Select an action first.")
            return
        record = self._records[row]
        self.status.setText(f"Running {record.name}...")
        self.run_button.setEnabled(False)
        try:
            result = self.registry.run(record.id, self._payload)
        finally:
            self.run_button.setEnabled(True)
        if result.ok:
            self.status.setText(f"Completed {record.name}.")
            self.result.setPlainText(result.output)
        else:
            self.status.setText(f"{record.name} failed.")
            self.result.setPlainText(f"Action failed: {result.error}")

    def copy_result(self) -> None:
        try:
            self.clipboard_manager.set_clipboard_text(self.result.toPlainText())
            self.status.setText("Result copied to clipboard.")
        except Exception as exc:
            self.status.setText(f"Copy failed: {exc}")



"""The main PySide6 shell window and its panels.

The shell is a real navigable application surface: a sidebar of panels backed by
a ``QStackedWidget``. Each panel is a small, focused widget that receives the
backend service bundle and contains no backend assembly logic of its own. The
``Ctrl+Alt+{C,P,L,T}`` hotkeys map to ``show_panel(...)`` so a single window is
reused instead of spawning one per surface.
"""

from __future__ import annotations

import webbrowser

from PySide6 import QtCore, QtGui, QtWidgets

from services import CoreServices

PANEL_TITLES = {
    "dashboard": "Dashboard",
    "clipboard": "Clipboard",
    "prompts": "Prompts",
    "links": "Links",
    "tts": "Text to Speech",
}
DEFAULT_PANEL_ORDER = ["dashboard", "clipboard", "prompts", "links", "tts"]


class MainShellWindow(QtWidgets.QMainWindow):
    """Sidebar-driven shell hosting the hub's panels."""

    def __init__(self, services: CoreServices):
        super().__init__()
        self.services = services
        self.setWindowTitle("Theophysics HUB")
        self.resize(1000, 660)

        self._panel_keys: list[str] = self._resolve_panel_order()
        self._sidebar = QtWidgets.QListWidget()
        self._sidebar.setMaximumWidth(210)
        self._stack = QtWidgets.QStackedWidget()

        for key in self._panel_keys:
            self._sidebar.addItem(PANEL_TITLES.get(key, key.title()))
            self._stack.addWidget(self._build_panel(key))

        self._sidebar.currentRowChanged.connect(self._on_panel_changed)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._sidebar)
        splitter.addWidget(self._stack)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        if self._panel_keys:
            self._sidebar.setCurrentRow(0)

    def _resolve_panel_order(self) -> list[str]:
        try:
            configured = self.services.config.panels()
        except Exception:
            configured = []
        order = [key for key in configured if key in PANEL_TITLES]
        return order or DEFAULT_PANEL_ORDER

    def _build_panel(self, key: str) -> QtWidgets.QWidget:
        builders = {
            "dashboard": lambda: DashboardPanel(self.services),
            "clipboard": lambda: ClipboardPanel(self.services),
            "prompts": lambda: PromptsPanel(self.services),
            "links": lambda: LinksPanel(self.services),
            "tts": lambda: TTSPanel(self.services),
        }
        builder = builders.get(key)
        return builder() if builder else _PlaceholderPanel(key)

    # -- external entry points ---------------------------------------------
    def show_panel(self, panel: str) -> None:
        """Select ``panel`` (logical key) and bring the window forward."""
        if panel in self._panel_keys:
            self._sidebar.setCurrentRow(self._panel_keys.index(panel))
        self.raise_window()

    def raise_window(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_panel_changed(self, row: int) -> None:
        if 0 <= row < len(self._panel_keys):
            key = self._panel_keys[row]
            self.services.app_logger.info("panel_open", extra={"trigger_source": key})
            widget = self._stack.widget(row)
            self._stack.setCurrentIndex(row)
            if hasattr(widget, "on_shown"):
                widget.on_shown()


class _PlaceholderPanel(QtWidgets.QWidget):
    def __init__(self, key: str):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(f"Panel '{key}' is not implemented yet."))


class DashboardPanel(QtWidgets.QWidget):
    """Read-only overview of hotkeys and key paths."""

    def __init__(self, services: CoreServices):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("Theophysics HUB")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        subtitle = QtWidgets.QLabel(
            "Windows-first action hub for selected text, clipboard rewrites, and configured tools."
        )
        subtitle.setWordWrap(True)

        hotkeys = self.services_hotkey_lines(services)
        reference = QtWidgets.QPlainTextEdit()
        reference.setReadOnly(True)
        reference.setPlainText(
            "Hotkeys\n"
            + "\n".join(hotkeys)
            + "\n\n"
            + f"Repo:   {services.root}\n"
            + f"Config: {services.root / '04_config'}\n"
            + f"Logs:   {services.root / '05_logs'}"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(reference)

    @staticmethod
    def services_hotkey_lines(services: CoreServices) -> list[str]:
        hotkeys = services.config.app_config().get("hotkeys", {})
        labels = {
            "gui": "open / focus this GUI",
            "clipboard": "open Clipboard panel",
            "prompts": "open Prompts panel",
            "links": "open Links panel",
            "tts": "open Text-to-Speech panel",
            "rewrite": "rewrite selected/clipboard text with OpenAI",
        }
        lines = []
        for name, description in labels.items():
            combo = hotkeys.get(name)
            if combo:
                lines.append(f"{combo:<12} {description}")
        lines.append(f"{'Middle Mouse':<12} open action popup")
        return lines


class ClipboardPanel(QtWidgets.QWidget):
    """Browse and manage the persistent multi-slot clipboard."""

    def __init__(self, services: CoreServices):
        super().__init__()
        self.services = services
        self.store = services.clipboard_store

        layout = QtWidgets.QVBoxLayout(self)
        header = QtWidgets.QLabel(f"Clipboard slots (0 .. {self.store.slot_count - 1})")
        header.setStyleSheet("font-weight: 600;")

        self.slot_list = QtWidgets.QListWidget()
        self.slot_list.currentRowChanged.connect(self._on_slot_selected)

        self.detail = QtWidgets.QPlainTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setPlaceholderText("Slot contents")
        self.detail.setMaximumHeight(150)

        self.status = QtWidgets.QLabel("Ready")

        buttons = QtWidgets.QHBoxLayout()
        capture_btn = QtWidgets.QPushButton("Capture Clipboard → Slot")
        copy_btn = QtWidgets.QPushButton("Copy Slot → Clipboard")
        clear_btn = QtWidgets.QPushButton("Clear Slot")
        capture_btn.clicked.connect(self.capture_into_slot)
        copy_btn.clicked.connect(self.copy_slot)
        clear_btn.clicked.connect(self.clear_slot)
        for btn in (capture_btn, copy_btn, clear_btn):
            buttons.addWidget(btn)

        layout.addWidget(header)
        layout.addWidget(self.slot_list)
        layout.addLayout(buttons)
        layout.addWidget(self.detail)
        layout.addWidget(self.status)

        self._refresh()

    def on_shown(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        row = self.slot_list.currentRow()
        self.slot_list.clear()
        for slot in self.store.slots():
            label = slot.preview() if not slot.is_empty else "(empty)"
            self.slot_list.addItem(f"{slot.index:>2}  {label}")
        if 0 <= row < self.slot_list.count():
            self.slot_list.setCurrentRow(row)
        elif self.slot_list.count():
            self.slot_list.setCurrentRow(0)

    def _on_slot_selected(self, row: int) -> None:
        if 0 <= row < self.store.slot_count:
            self.detail.setPlainText(self.store.get(row).text)

    def _selected_index(self) -> int | None:
        row = self.slot_list.currentRow()
        return row if 0 <= row < self.store.slot_count else None

    def capture_into_slot(self) -> None:
        try:
            text = self.services.clipboard.get_clipboard_text()
        except Exception as exc:
            self.status.setText(f"Clipboard read failed: {exc}")
            return
        if not text.strip():
            self.status.setText("Clipboard is empty; nothing captured.")
            return
        target = self._selected_index()
        if target is None or not self.store.get(target).is_empty:
            target = self.store.first_empty_index()
        if target is None:
            self.status.setText("All slots are full. Clear one first.")
            return
        self.store.set(target, text)
        self._refresh()
        self.slot_list.setCurrentRow(target)
        self.status.setText(f"Captured clipboard into slot {target}.")

    def copy_slot(self) -> None:
        index = self._selected_index()
        if index is None:
            self.status.setText("Select a slot first.")
            return
        slot = self.store.get(index)
        if slot.is_empty:
            self.status.setText(f"Slot {index} is empty.")
            return
        try:
            self.services.clipboard.set_clipboard_text(slot.text)
            self.status.setText(f"Copied slot {index} to clipboard.")
        except Exception as exc:
            self.status.setText(f"Copy failed: {exc}")

    def clear_slot(self) -> None:
        index = self._selected_index()
        if index is None:
            self.status.setText("Select a slot first.")
            return
        self.store.clear(index)
        self._refresh()
        self.detail.clear()
        self.status.setText(f"Cleared slot {index}.")


class PromptsPanel(QtWidgets.QWidget):
    """List configured prompts and copy them to the clipboard."""

    def __init__(self, services: CoreServices):
        super().__init__()
        self.services = services
        self.prompts = services.content.prompts

        layout = QtWidgets.QVBoxLayout(self)
        self.prompt_list = QtWidgets.QListWidget()
        self.preview = QtWidgets.QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Prompt content")
        self.status = QtWidgets.QLabel("Ready")
        copy_btn = QtWidgets.QPushButton("Copy Prompt → Clipboard")

        for prompt in self.prompts:
            suffix = f"  [{prompt.hotkey}]" if prompt.hotkey else ""
            self.prompt_list.addItem(f"{prompt.name}{suffix}")

        self.prompt_list.currentRowChanged.connect(self._on_selected)
        copy_btn.clicked.connect(self.copy_prompt)

        layout.addWidget(QtWidgets.QLabel("Configured prompts"))
        layout.addWidget(self.prompt_list)
        layout.addWidget(copy_btn)
        layout.addWidget(self.preview)
        layout.addWidget(self.status)

        if self.prompts:
            self.prompt_list.setCurrentRow(0)

    def _on_selected(self, row: int) -> None:
        if 0 <= row < len(self.prompts):
            self.preview.setPlainText(self.prompts[row].content)

    def copy_prompt(self) -> None:
        row = self.prompt_list.currentRow()
        if not 0 <= row < len(self.prompts):
            self.status.setText("Select a prompt first.")
            return
        try:
            self.services.clipboard.set_clipboard_text(self.prompts[row].content)
            self.status.setText(f"Copied '{self.prompts[row].name}' to clipboard.")
        except Exception as exc:
            self.status.setText(f"Copy failed: {exc}")


class LinksPanel(QtWidgets.QWidget):
    """List quick-access links and open them in the default browser."""

    def __init__(self, services: CoreServices):
        super().__init__()
        self.services = services
        self.links = services.content.links

        layout = QtWidgets.QVBoxLayout(self)
        self.link_list = QtWidgets.QListWidget()
        self.status = QtWidgets.QLabel("Ready")
        open_btn = QtWidgets.QPushButton("Open Link")

        for link in self.links:
            category = f"[{link.category}] " if link.category else ""
            item = QtWidgets.QListWidgetItem(f"{category}{link.label} — {link.url}")
            item.setData(QtCore.Qt.UserRole, link.url)
            self.link_list.addItem(item)

        self.link_list.itemActivated.connect(lambda _item: self.open_link())
        open_btn.clicked.connect(self.open_link)

        layout.addWidget(QtWidgets.QLabel("Quick links"))
        layout.addWidget(self.link_list)
        layout.addWidget(open_btn)
        layout.addWidget(self.status)

        if self.links:
            self.link_list.setCurrentRow(0)

    def open_link(self) -> None:
        item = self.link_list.currentItem()
        if item is None:
            self.status.setText("Select a link first.")
            return
        url = item.data(QtCore.Qt.UserRole)
        try:
            webbrowser.open(url)
            self.status.setText(f"Opened {url}")
        except Exception as exc:
            self.status.setText(f"Could not open link: {exc}")


class TTSPanel(QtWidgets.QWidget):
    """Speak clipboard or typed text aloud via the platform TTS engine."""

    def __init__(self, services: CoreServices):
        super().__init__()
        self.services = services
        self._thread: _SpeakThread | None = None

        layout = QtWidgets.QVBoxLayout(self)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setPlaceholderText("Text to speak")
        self.status = QtWidgets.QLabel("Ready")

        buttons = QtWidgets.QHBoxLayout()
        load_btn = QtWidgets.QPushButton("Load Clipboard")
        self.speak_btn = QtWidgets.QPushButton("Speak")
        load_btn.clicked.connect(self.load_clipboard)
        self.speak_btn.clicked.connect(self.speak)
        buttons.addWidget(load_btn)
        buttons.addWidget(self.speak_btn)

        layout.addWidget(QtWidgets.QLabel("Text to speech"))
        layout.addWidget(self.text)
        layout.addLayout(buttons)
        layout.addWidget(self.status)

        if not self.services.tts.is_supported():
            self.status.setText("TTS backend available on Windows only on this machine.")

    def on_shown(self) -> None:
        if not self.text.toPlainText().strip():
            self.load_clipboard()

    def load_clipboard(self) -> None:
        try:
            self.text.setPlainText(self.services.clipboard.get_clipboard_text())
            self.status.setText("Loaded clipboard text.")
        except Exception as exc:
            self.status.setText(f"Clipboard read failed: {exc}")

    def speak(self) -> None:
        text = self.text.toPlainText()
        if not text.strip():
            self.status.setText("Nothing to speak.")
            return
        self.speak_btn.setEnabled(False)
        self.status.setText("Speaking...")
        self._thread = _SpeakThread(self.services.tts, text)
        self._thread.done.connect(self._on_speak_done)
        self._thread.start()

    def _on_speak_done(self, error: str) -> None:
        self.speak_btn.setEnabled(True)
        self.status.setText("Done." if not error else f"Speech failed: {error}")


class _SpeakThread(QtCore.QThread):
    """Runs blocking speech synthesis off the UI thread."""

    done = QtCore.Signal(str)

    def __init__(self, tts, text: str):
        super().__init__()
        self._tts = tts
        self._text = text

    def run(self) -> None:
        try:
            self._tts.speak(self._text)
            self.done.emit("")
        except Exception as exc:  # surfaced in the panel status line
            self.done.emit(str(exc))

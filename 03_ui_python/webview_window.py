"""Optional host for the React build inside PySide6.

The native ``MainShellWindow`` remains the supported runtime surface. This
module is intentionally dependency-tolerant: Qt WebEngine is imported lazily so
headless Linux test environments and Windows installs without WebEngine can keep
using the Python shell without failing at import time.
"""

from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets


class WebViewUnavailable(RuntimeError):
    """Raised when the optional Qt WebEngine host cannot be constructed."""


class WebViewWindow(QtWidgets.QMainWindow):
    """Display the built React dashboard when Qt WebEngine and assets exist."""

    def __init__(self, root: Path):
        super().__init__()
        self.root = root.resolve()
        self.setWindowTitle("Theophysics HUB · React Preview")
        self.resize(1180, 760)

        try:
            from PySide6 import QtWebEngineWidgets
        except Exception as exc:  # optional dependency/runtime support
            raise WebViewUnavailable(
                "Qt WebEngine is unavailable. Keep using MainShellWindow, or install a PySide6 build with WebEngine "
                "and required graphics libraries before embedding the React dashboard."
            ) from exc

        index_path = self.root / "02_ui_react" / "dist" / "index.html"
        if not index_path.exists():
            raise WebViewUnavailable(
                "React build assets are missing. Run `npm run build` in 02_ui_react before opening WebViewWindow."
            )

        view = QtWebEngineWidgets.QWebEngineView(self)
        view.setUrl(QtCore.QUrl.fromLocalFile(str(index_path)))
        self.setCentralWidget(view)

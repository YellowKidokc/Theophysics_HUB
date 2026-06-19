"""Future host for the React build inside PySide6.

Intentionally unimplemented for the current Python-shell slice. When the
``02_ui_react`` frontend is ready, this window will host the built assets via
``QWebEngineView`` so the native shell and the web UI share one process.
"""

from __future__ import annotations


class WebViewWindow:
    def show(self) -> None:
        raise NotImplementedError(
            "React webview host is not part of the current slice; use MainShellWindow."
        )

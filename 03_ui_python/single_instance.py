"""Single-instance routing for the shell via a Qt local socket (named pipe).

The AHK layer launches a fresh ``stratum_cli gui <panel>`` process for every
panel hotkey. To avoid stacking duplicate windows, the first process becomes a
server on a local named pipe; later processes connect as clients, hand off the
requested panel name, and exit. The already-running shell then raises itself
and switches panels.

This is direct local coordination (a named pipe), not an HTTP service, which
fits the Windows-first, low-overhead design of the hub.
"""

from __future__ import annotations

from typing import Callable

_CONNECT_TIMEOUT_MS = 300
_READ_TIMEOUT_MS = 300


class PanelRouter:
    """Routes a panel request to a running shell, or hosts the routing server."""

    def __init__(self, server_name: str):
        self.server_name = server_name
        self._server = None  # held to keep the QLocalServer alive

    def send_to_running(self, panel: str) -> bool:
        """Hand ``panel`` to an already-running shell. Returns ``True`` if one answered."""
        from PySide6 import QtNetwork

        socket = QtNetwork.QLocalSocket()
        socket.connectToServer(self.server_name)
        if not socket.waitForConnected(_CONNECT_TIMEOUT_MS):
            return False
        socket.write((panel or "").encode("utf-8"))
        socket.flush()
        socket.waitForBytesWritten(_CONNECT_TIMEOUT_MS)
        socket.disconnectFromServer()
        return True

    def start_server(self, on_panel: Callable[[str], None]) -> None:
        """Listen for panel requests from later processes and dispatch them."""
        from PySide6 import QtNetwork

        # Clear any stale socket left by a previous unclean shutdown.
        QtNetwork.QLocalServer.removeServer(self.server_name)
        server = QtNetwork.QLocalServer()
        if not server.listen(self.server_name):
            # Routing is a convenience, not a hard requirement; the window still
            # works standalone if the pipe can't be created.
            return
        self._server = server

        def handle_connection() -> None:
            connection = server.nextPendingConnection()
            if connection is None:
                return
            if connection.waitForReadyRead(_READ_TIMEOUT_MS):
                panel = bytes(connection.readAll()).decode("utf-8", "replace").strip()
                on_panel(panel)
            connection.disconnectFromServer()

        server.newConnection.connect(handle_connection)

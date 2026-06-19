"""Application lifecycle entry points.

``main.py`` calls :func:`start_app` to bring up the desktop shell. The heavy
lifting lives in :mod:`stratum_cli`, which both this lifecycle path and the AHK
trigger layer share, so there is exactly one way the shell is constructed.
"""

from __future__ import annotations


def start_app() -> int:
    """Launch the PySide6 shell on the default panel and run its event loop."""
    from stratum_cli import DEFAULT_PANEL, open_gui

    return open_gui(DEFAULT_PANEL)


def stop_app() -> None:
    """Stop background processes.

    The resident shell is closed from its window/tray, and the AHK trigger
    layer is exited from the tray menu, so there is nothing to tear down here
    for the current single-window slice.
    """
    return None


def restart_app() -> None:
    stop_app()
    start_app()

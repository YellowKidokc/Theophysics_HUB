"""Placeholder for an optional local API.

The current slice coordinates AHK and the shell through a Qt local socket (see
``single_instance.py``), so no HTTP server is needed yet. This module is kept
as the seam for a future local API if the React frontend or external tools ever
require one.
"""

from __future__ import annotations


def start_api() -> None:
    raise NotImplementedError(
        "Local API is not required for the current slice; panel routing uses a Qt local socket."
    )

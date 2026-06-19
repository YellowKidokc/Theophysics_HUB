"""Logging configuration for local desktop runs."""

from __future__ import annotations

import logging
from pathlib import Path


def log_path(root: Path, name: str) -> Path:
    path = root / "05_logs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def configure_file_logger(root: Path, logger_name: str, file_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    target = log_path(root, file_name)
    existing = [h for h in logger.handlers if isinstance(h, logging.FileHandler) and Path(h.baseFilename) == target]
    if not existing:
        handler = logging.FileHandler(target, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False
    return logger

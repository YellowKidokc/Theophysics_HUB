from pathlib import Path


def log_path(root: Path, name: str) -> Path:
    path = root / "05_logs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

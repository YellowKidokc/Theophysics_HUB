from pathlib import Path


STARTUP_DIR = Path(r"C:\Users\lowes\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")


def ensure_startup_shortcut() -> None:
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    marker = STARTUP_DIR / "stratum-startup.txt"
    if not marker.exists():
        marker.write_text(
            "Replace this marker with a real shortcut or launcher once the shell is packaged.\n",
            encoding="utf-8",
        )

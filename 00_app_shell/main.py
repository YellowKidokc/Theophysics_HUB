from bootstrapper import ensure_startup_shortcut
from lifecycle import start_app


def main() -> int:
    ensure_startup_shortcut()
    start_app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

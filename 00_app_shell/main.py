from bootstrapper import ensure_startup_shortcut
from lifecycle import start_app


def main() -> int:
    ensure_startup_shortcut()
    return start_app()


if __name__ == "__main__":
    raise SystemExit(main())

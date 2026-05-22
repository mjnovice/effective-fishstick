from __future__ import annotations

from pathlib import Path


APP_DB = Path(__file__).resolve().parent.parent / "app.db"


def main() -> int:
    if APP_DB.exists():
        APP_DB.unlink()
        print(f"Deleted {APP_DB}")
    else:
        print(f"No database file found at {APP_DB}")

    print("Run `python3 run.py` again to recreate a fresh local database.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

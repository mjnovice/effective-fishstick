from __future__ import annotations

from framework.server import run_server
from workspace.database import initialize_database


def main() -> int:
    initialize_database(include_conversation_categories=True, seed_saved_categories=True)
    run_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

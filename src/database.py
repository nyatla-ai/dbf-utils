from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    """Simple wrapper around :class:`sqlite3.Connection`."""

    def __init__(self, db_path: str | Path) -> None:
        self.path = Path(db_path)
        self.conn = sqlite3.connect(str(self.path))

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


__all__ = ["Database"]

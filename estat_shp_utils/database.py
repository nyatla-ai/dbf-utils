from __future__ import annotations

import sqlite3
from pathlib import Path


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    """Return True if the given table exists."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    )
    return cur.fetchone() is not None


def create_codes_view(conn: sqlite3.Connection) -> None:
    """Create ``codes_view`` if required tables are present."""
    required = ['prefectures', 'cities', 'sub_areas']
    if not all(_table_exists(conn, t) for t in required):
        return
    conn.execute(
        """
        CREATE VIEW IF NOT EXISTS codes_view AS
        SELECT
            sa.sub_area_id AS sub_area_id,
            p.pref_code AS prefecture_code,
            c.city_code AS city_code,
            sa.s_area_code AS s_area_code,
            ((p.pref_code * 1000 + c.city_code) * 1000000 + sa.s_area_code) AS jis_code
        FROM sub_areas sa
        JOIN cities c ON sa.city_id = c.city_id
        JOIN prefectures p ON sa.prefecture_id = p.prefecture_id
        """
    )
    conn.commit()


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


__all__ = ["Database", "create_codes_view"]

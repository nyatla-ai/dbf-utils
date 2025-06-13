from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple

from .database import Database


def get_city_id(db: Database, pref_code: int, city_code: int) -> Optional[int]:
    """Return city_id for given prefecture and city codes or None."""
    query = (
        "SELECT city_id FROM cities "
        "WHERE pref_code = ? AND city_code = ? "
        "LIMIT 1"
    )
    cur = db.conn.execute(query, (pref_code, city_code))
    row = cur.fetchone()
    return int(row[0]) if row else None


def get_sub_area_id(
    db: Database,
    pref_code: int,
    city_code: int,
    s_area_code: int,
) -> Optional[int]:
    """Return sub_area_id for given codes or None if not found."""
    query = (
        "SELECT sa.sub_area_id "
        "FROM sub_areas sa "
        "JOIN cities c ON sa.city_id = c.city_id "
        "JOIN prefectures p ON sa.prefecture_id = p.prefecture_id "
        "WHERE p.pref_code = ? AND c.city_code = ? AND sa.s_area_code = ? "
        "LIMIT 1"
    )
    cur = db.conn.execute(query, (pref_code, city_code, s_area_code))
    row = cur.fetchone()
    return int(row[0]) if row else None


class SubAreaIdSelector:
    """Cache-aware helper for looking up ``sub_area_id`` values."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._conn = db.conn
        self._cache: Dict[Tuple[int, int, int], Optional[int]] = {}

    def close(self) -> None:
        pass

    def __enter__(self) -> "SubAreaIdSelector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def get_sub_area_id(
        self, pref_code: int, city_code: int, s_area_code: int
    ) -> Optional[int]:
        key = (pref_code, city_code, s_area_code)
        if key in self._cache:
            return self._cache[key]

        query = (
            "SELECT sa.sub_area_id "
            "FROM sub_areas sa "
            "JOIN cities c ON sa.city_id = c.city_id "
            "JOIN prefectures p ON sa.prefecture_id = p.prefecture_id "
            "WHERE p.pref_code = ? AND c.city_code = ? AND sa.s_area_code = ? "
            "LIMIT 1"
        )
        cur = self._conn.execute(query, key)
        row = cur.fetchone()
        result = int(row[0]) if row else None
        self._cache[key] = result
        return result


class CityIdSelector:
    """Cache-aware helper for looking up ``city_id`` values."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._conn = db.conn
        self._cache: Dict[Tuple[int, int], Optional[int]] = {}

    def close(self) -> None:
        pass

    def __enter__(self) -> "CityIdSelector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def get_city_id(self, pref_code: int, city_code: int) -> Optional[int]:
        key = (pref_code, city_code)
        if key in self._cache:
            return self._cache[key]

        query = (
            "SELECT city_id FROM cities "
            "WHERE pref_code = ? AND city_code = ? "
            "LIMIT 1"
        )
        cur = self._conn.execute(query, key)
        row = cur.fetchone()
        result = int(row[0]) if row else None
        self._cache[key] = result
        return result


class SubAreaReader:
    """Return total row count and records within a range."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def fetch(self, offset: int = 0, limit: int = 100) -> tuple[int, list[dict[str, object]]]:
        """Return total rows and a slice of records from ``sub_areas``."""
        total = self._db.conn.execute("SELECT COUNT(*) FROM sub_areas").fetchone()[0]
        cur = self._db.conn.execute(
            "SELECT sub_area_id, s_area_code, area_id, section_id, city_id, prefecture_id "
            "FROM sub_areas ORDER BY sub_area_id LIMIT ? OFFSET ?",
            (limit, offset),
        )
        cols = [d[0] for d in cur.description]
        records = [dict(zip(cols, row)) for row in cur.fetchall()]
        return int(total), records


__all__ = [
    "get_city_id",
    "CityIdSelector",
    "get_sub_area_id",
    "SubAreaIdSelector",
    "SubAreaReader",
]


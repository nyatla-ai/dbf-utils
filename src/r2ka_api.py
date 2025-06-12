from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple


def get_city_id(db_path: str | Path, pref_code: int, city_code: int) -> Optional[int]:
    """Return city_id for given prefecture and city codes or None."""
    query = (
        "SELECT city_id FROM cities "
        "WHERE pref_code = ? AND city_code = ? "
        "LIMIT 1"
    )
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.execute(query, (pref_code, city_code))
        row = cur.fetchone()
    return int(row[0]) if row else None


def get_sub_area_id(
    db_path: str | Path,
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
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.execute(query, (pref_code, city_code, s_area_code))
        row = cur.fetchone()
    return int(row[0]) if row else None


class SubAreaIdSelector:
    """Cache-aware helper for looking up ``sub_area_id`` values."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._conn = sqlite3.connect(str(self.db_path))
        self._cache: Dict[Tuple[int, int, int], Optional[int]] = {}

    def close(self) -> None:
        if self._conn:
            self._conn.close()

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

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._conn = sqlite3.connect(str(self.db_path))
        self._cache: Dict[Tuple[int, int], Optional[int]] = {}

    def close(self) -> None:
        if self._conn:
            self._conn.close()

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


__all__ = [
    "get_city_id",
    "CityIdSelector",
    "get_sub_area_id",
    "SubAreaIdSelector",
]


from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Tuple

from dbfread import DBF


class R2KAImporter:
    """Import records from r2ka11.dbf into a normalized SQLite database."""

    def __init__(self, db_path: str, dbf_path: str) -> None:
        self.db_path = Path(db_path)
        self.dbf_path = Path(dbf_path)

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS prefectures (
                prefecture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pref_code INTEGER UNIQUE NOT NULL,
                pref_name TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cities (
                city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pref_code INTEGER NOT NULL REFERENCES prefectures(pref_code),
                city_code INTEGER NOT NULL,
                city_name TEXT NOT NULL,
                UNIQUE(pref_code, city_code)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sub_areas (
                sub_area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                s_area_code INTEGER NOT NULL,
                city_id INTEGER NOT NULL REFERENCES cities(city_id),
                prefecture_id INTEGER NOT NULL REFERENCES prefectures(prefecture_id),
                s_name TEXT NOT NULL,
                UNIQUE(s_area_code, city_id, prefecture_id)
            )
            """
        )
        conn.commit()

    def import_data(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            self._create_schema(conn)
            cur = conn.cursor()

            pref_cache: Dict[int, int] = {}
            city_cache: Dict[Tuple[int, int], int] = {}
            sub_area_cache: Dict[Tuple[int, int, int], int] = {}

            for record in DBF(self.dbf_path, encoding="cp932"):
                pref_code = int(record["PREF"])
                city_code = int(record["CITY"])
                s_area_code = int(record["S_AREA"])
                pref_name = record["PREF_NAME"].strip()
                city_name = record["CITY_NAME"].strip()
                s_name = record["S_NAME"].strip()

                if pref_code not in pref_cache:
                    cur.execute(
                        "INSERT INTO prefectures (pref_code, pref_name) VALUES (?, ?)",
                        (pref_code, pref_name),
                    )
                    pref_cache[pref_code] = cur.lastrowid
                pref_id = pref_cache[pref_code]

                city_key = (pref_code, city_code)
                if city_key not in city_cache:
                    cur.execute(
                        "INSERT INTO cities (pref_code, city_code, city_name) VALUES (?, ?, ?)",
                        (pref_code, city_code, city_name),
                    )
                    city_cache[city_key] = cur.lastrowid
                city_id = city_cache[city_key]

                sub_key = (s_area_code, city_id, pref_id)
                if sub_key not in sub_area_cache:
                    cur.execute(
                        "INSERT INTO sub_areas (s_area_code, city_id, prefecture_id, s_name) VALUES (?, ?, ?, ?)",
                        (s_area_code, city_id, pref_id, s_name),
                    )
                    sub_area_cache[sub_key] = cur.lastrowid

            conn.commit()


__all__ = ["R2KAImporter"]

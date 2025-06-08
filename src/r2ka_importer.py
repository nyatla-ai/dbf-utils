from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable, Tuple

import csv


class R2KAImporter:
    """Import records from one or more CSV files into a normalized SQLite database."""

    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)

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

    def import_csvs(self, csv_paths: Iterable[str]) -> tuple[int, int]:
        """Import one or more CSV files.

        Returns a tuple of (records_read, records_inserted)."""

        attempted = 0
        inserted = 0

        with sqlite3.connect(self.db_path) as conn:
            self._create_schema(conn)
            cur = conn.cursor()

            cur.execute("SELECT pref_code, prefecture_id FROM prefectures")
            pref_cache: Dict[int, int] = {code: pid for code, pid in cur.fetchall()}

            cur.execute("SELECT pref_code, city_code, city_id FROM cities")
            city_cache: Dict[Tuple[int, int], int] = {
                (p, c): cid for p, c, cid in cur.fetchall()
            }

            cur.execute("SELECT s_area_code, city_id, prefecture_id FROM sub_areas")
            sub_area_cache: Dict[Tuple[int, int, int], int] = {
                (s, cid, pid): 1 for s, cid, pid in cur.fetchall()
            }

            for path in csv_paths:
                with open(path, encoding="cp932", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        attempted += 1
                        pref_code = int(row["PREF"])
                        city_code = int(row["CITY"])
                        s_area_code = int(row["S_AREA"])
                        pref_name = row["PREF_NAME"].strip()
                        city_name = row["CITY_NAME"].strip()
                        s_name = row["S_NAME"].strip()

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
                            sub_area_cache[sub_key] = 1
                            inserted += 1

            conn.commit()

        return attempted, inserted


__all__ = ["R2KAImporter"]

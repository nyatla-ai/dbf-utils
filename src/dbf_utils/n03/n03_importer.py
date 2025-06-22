from __future__ import annotations

import sqlite3
from typing import Dict, Iterable, Tuple

from dbfread import DBF

from ..database import Database


class N03Importer:
    """Import municipalities from the MLIT N03 DBF format."""

    def __init__(self, db: Database, encoding: str = "cp932") -> None:
        self.db = db
        self.encoding = encoding

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
        conn.commit()

    def import_dbf(self, path: str) -> tuple[int, int]:
        """Import a single N03 DBF file.

        Returns a tuple of (records_read, cities_inserted).
        """
        table = DBF(path, encoding=self.encoding)
        conn = self.db.conn
        self._create_schema(conn)
        cur = conn.cursor()

        cur.execute("SELECT pref_code, prefecture_id FROM prefectures")
        pref_cache: Dict[int, int] = {code: pid for code, pid in cur.fetchall()}

        cur.execute("SELECT pref_code, city_code, city_id FROM cities")
        city_cache: Dict[Tuple[int, int], int] = {
            (p, c): cid for p, c, cid in cur.fetchall()
        }

        attempted = 0
        inserted = 0

        for rec in table:
            attempted += 1
            pref_name = str(rec.get("N03_001", "")).strip()
            city_name = str(rec.get("N03_004", "")).strip()
            code = str(rec.get("N03_007", "")).strip()
            if not code.isdigit() or len(code) != 5:
                # Skip invalid records
                continue
            pref_code = int(code[:2])
            city_code = int(code[2:])

            if pref_code not in pref_cache:
                cur.execute(
                    "INSERT INTO prefectures (pref_code, pref_name) VALUES (?, ?)",
                    (pref_code, pref_name),
                )
                pref_cache[pref_code] = cur.lastrowid

            if (pref_code, city_code) not in city_cache:
                cur.execute(
                    "INSERT INTO cities (pref_code, city_code, city_name) VALUES (?, ?, ?)",
                    (pref_code, city_code, city_name),
                )
                city_cache[(pref_code, city_code)] = cur.lastrowid
                inserted += 1

        conn.commit()
        return attempted, inserted


__all__ = ["N03Importer"]

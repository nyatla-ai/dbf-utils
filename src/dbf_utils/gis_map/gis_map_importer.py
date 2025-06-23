from __future__ import annotations

import sqlite3
from typing import Dict, Iterable, Tuple

from ..dbf import parse_dbf

from ..database import Database, create_cities_view


class GISMapImporter:
    """Import municipalities from the MLIT GIS Map (formerly N03) DBF format."""

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
            CREATE TABLE IF NOT EXISTS subprefecters (
                subpref_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subpref_name TEXT UNIQUE NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS distincts (
                distinct_id INTEGER PRIMARY KEY AUTOINCREMENT,
                distinct_name TEXT UNIQUE NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS wards (
                ward_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ward_name TEXT UNIQUE NOT NULL
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
                subpref_id INTEGER REFERENCES subprefecters(subpref_id),
                distinct_id INTEGER REFERENCES distincts(distinct_id),
                ward_id INTEGER REFERENCES wards(ward_id),
                UNIQUE(pref_code, city_code)
            )
            """
        )
        conn.commit()
        create_cities_view(conn)

    def import_dbf(self, path: str) -> tuple[int, int]:
        """Import a single GIS Map DBF file.

        Returns a tuple of (records_read, cities_inserted).
        """
        records = parse_dbf(path, encoding=self.encoding)
        conn = self.db.conn
        self._create_schema(conn)
        cur = conn.cursor()

        cur.execute("SELECT pref_code, prefecture_id FROM prefectures")
        pref_cache: Dict[int, int] = {code: pid for code, pid in cur.fetchall()}

        cur.execute("SELECT pref_code, city_code, city_id FROM cities")
        city_cache: Dict[Tuple[int, int], int] = {
            (p, c): cid for p, c, cid in cur.fetchall()
        }
        cur.execute("SELECT subpref_name, subpref_id FROM subprefecters")
        subpref_cache: Dict[str, int] = {n: i for n, i in cur.fetchall()}
        cur.execute("SELECT distinct_name, distinct_id FROM distincts")
        distinct_cache: Dict[str, int] = {n: i for n, i in cur.fetchall()}
        cur.execute("SELECT ward_name, ward_id FROM wards")
        ward_cache: Dict[str, int] = {n: i for n, i in cur.fetchall()}

        attempted = 0
        inserted = 0

        for rec in records:
            attempted += 1
            pref_name = str(rec.get("N03_001", "")).strip()
            subpref_name = str(rec.get("N03_002", "")).strip()
            distinct_name = str(rec.get("N03_003", "")).strip()
            city_name = str(rec.get("N03_004", "")).strip()
            ward_name = str(rec.get("N03_005", "")).strip()
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

            if subpref_name:
                if subpref_name not in subpref_cache:
                    cur.execute(
                    "INSERT INTO subprefecters (subpref_name) VALUES (?)",
                        (subpref_name,),
                    )
                    subpref_cache[subpref_name] = cur.lastrowid
                subpref_id = subpref_cache[subpref_name]
            else:
                subpref_id = None

            if distinct_name:
                if distinct_name not in distinct_cache:
                    cur.execute(
                        "INSERT INTO distincts (distinct_name) VALUES (?)",
                        (distinct_name,),
                    )
                    distinct_cache[distinct_name] = cur.lastrowid
                distinct_id = distinct_cache[distinct_name]
            else:
                distinct_id = None

            if ward_name:
                if ward_name not in ward_cache:
                    cur.execute(
                        "INSERT INTO wards (ward_name) VALUES (?)",
                        (ward_name,),
                    )
                    ward_cache[ward_name] = cur.lastrowid
                ward_id = ward_cache[ward_name]
            else:
                ward_id = None

            if (pref_code, city_code) not in city_cache:
                cur.execute(
                    "INSERT INTO cities (pref_code, city_code, city_name, subpref_id, distinct_id, ward_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (pref_code, city_code, city_name, subpref_id, distinct_id, ward_id),
                )
                city_cache[(pref_code, city_code)] = cur.lastrowid
                inserted += 1

        conn.commit()
        return attempted, inserted


__all__ = ["GISMapImporter"]

from __future__ import annotations

import sqlite3
from typing import Dict, Iterable, Tuple, List
import re
from collections import defaultdict

import csv
from ..dbf import parse_dbf
from ..database import Database, create_codes_view


class R2KAImporter:
    """Import records from one or more CSV files into a normalized SQLite database."""

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
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS areas (
                area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT UNIQUE NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sections (
                section_id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_name TEXT UNIQUE NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sub_areas (
                sub_area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                s_area_code INTEGER NOT NULL,
                area_id INTEGER NOT NULL REFERENCES areas(area_id),
                section_id INTEGER REFERENCES sections(section_id),
                city_id INTEGER NOT NULL REFERENCES cities(city_id),
                prefecture_id INTEGER NOT NULL REFERENCES prefectures(prefecture_id),
                UNIQUE(s_area_code, city_id, prefecture_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS x_districts (
                x_district_id INTEGER PRIMARY KEY,
                prefecture_id INTEGER NOT NULL REFERENCES prefectures(prefecture_id),
                city_id INTEGER NOT NULL REFERENCES cities(city_id),
                area_id INTEGER NOT NULL REFERENCES areas(area_id),
                section_id INTEGER NOT NULL,
                first_sub_area_id INTEGER NOT NULL REFERENCES sub_areas(sub_area_id),
                UNIQUE(prefecture_id, city_id, area_id, section_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS x_sub_area_districts (
                sub_area_id INTEGER PRIMARY KEY REFERENCES sub_areas(sub_area_id),
                x_district_id INTEGER NOT NULL REFERENCES x_districts(x_district_id)
            )
            """
        )
        conn.commit()

        create_codes_view(conn)

    def _parse_numeric_code(self, value: str, length: int) -> int:
        """Validate and convert a zero padded numeric code to int."""
        trimmed = value.strip()
        if not trimmed.isdigit() or len(trimmed) != length:
            raise ValueError(
                f"Expected {length}-digit numeric code, got {value!r}"
            )
        return int(trimmed)

    def _iter_records(self, path: str) -> Iterable[dict[str, str]]:
        """Yield records from a CSV or DBF file as dictionaries."""
        if path.lower().endswith(".dbf"):
            for rec in parse_dbf(path, encoding=self.encoding):
                yield {k: (str(v) if v is not None else "") for k, v in rec.items()}
        else:
            with open(path, encoding=self.encoding, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row

    def _longest_common_prefix(self, strings: List[str]) -> str:
        """Return the longest common prefix of the given strings."""
        if not strings:
            return ""
        prefix = strings[0]
        for s in strings[1:]:
            i = 0
            while i < len(prefix) and i < len(s) and prefix[i] == s[i]:
                i += 1
            prefix = prefix[:i]
            if not prefix:
                break
        return prefix

    def import_csvs(self, csv_paths: Iterable[str]) -> tuple[int, int]:
        """Import one or more CSV files.

        Returns a tuple of (records_read, records_inserted)."""

        attempted = 0
        inserted = 0

        records: List[Tuple[int, int, int, str, str, str]] = []

        for path in csv_paths:
            for row in self._iter_records(path):
                try:
                    pref_code = self._parse_numeric_code(row["PREF"], 2)
                    city_code = self._parse_numeric_code(row["CITY"], 3)
                    s_area_code = self._parse_numeric_code(row["S_AREA"], 6)
                except ValueError as e:
                    raise ValueError(f"Invalid record {row}: {e}") from e

                pref_name = row["PREF_NAME"].strip()
                city_name = row["CITY_NAME"].strip()
                s_name = row["S_NAME"].strip()

                records.append(
                    (pref_code, city_code, s_area_code, pref_name, city_name, s_name)
                )
                attempted += 1

        conn = self.db.conn
        self._create_schema(conn)
        cur = conn.cursor()

        cur.execute("SELECT pref_code, prefecture_id FROM prefectures")
        pref_cache: Dict[int, int] = {code: pid for code, pid in cur.fetchall()}

        cur.execute("SELECT pref_code, city_code, city_id FROM cities")
        city_cache: Dict[Tuple[int, int], int] = {(p, c): cid for p, c, cid in cur.fetchall()}

        cur.execute("SELECT area_name, area_id FROM areas")
        area_cache: Dict[str, int] = {n: aid for n, aid in cur.fetchall()}

        cur.execute("SELECT section_name, section_id FROM sections")
        section_cache: Dict[str, int] = {n: sid for n, sid in cur.fetchall()}

        cur.execute("SELECT s_area_code, city_id, prefecture_id FROM sub_areas")
        sub_area_cache: Dict[Tuple[int, int, int], int] = {(s, cid, pid): 1 for s, cid, pid in cur.fetchall()}

        grouped: Dict[Tuple[int, int, int], List[Tuple[int, int, int, str, str, str]]] = defaultdict(list)
        for rec in records:
            area_code = rec[2] // 100
            grouped[(rec[0], rec[1], area_code)].append(rec)

        for key, recs in grouped.items():
            names = [r[5] for r in recs]
            prefix = self._longest_common_prefix(names).strip()

            for pref_code, city_code, s_area_code, pref_name, city_name, s_name in recs:
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

                section_code = s_area_code % 100

                if prefix:
                    area_name = prefix
                    if section_code == 0:
                        section_name = None
                    else:
                        remainder = s_name[len(prefix):].strip()
                        section_name = remainder or None
                else:
                    if section_code == 0:
                        area_name = s_name
                        section_name = None
                    else:
                        m = re.search(r"([一二三四五六七八九十百]+丁目)$", s_name)
                        if m:
                            area_name = s_name[: -len(m.group(1))]
                            section_name = m.group(1)
                        else:
                            area_name = s_name
                            section_name = None

                if area_name not in area_cache:
                    cur.execute("INSERT INTO areas (area_name) VALUES (?)", (area_name,))
                    area_cache[area_name] = cur.lastrowid
                area_id = area_cache[area_name]

                if section_name is not None:
                    if section_name not in section_cache:
                        cur.execute(
                            "INSERT INTO sections (section_name) VALUES (?)",
                            (section_name,),
                        )
                        section_cache[section_name] = cur.lastrowid
                    section_id = section_cache[section_name]
                else:
                    section_id = None

                sub_key = (s_area_code, city_id, pref_id)
                if sub_key not in sub_area_cache:
                    cur.execute(
                        "INSERT INTO sub_areas (s_area_code, area_id, section_id, city_id, prefecture_id) VALUES (?, ?, ?, ?, ?)",
                        (s_area_code, area_id, section_id, city_id, pref_id),
                    )
                    sub_area_cache[sub_key] = 1
                    inserted += 1

        conn.commit()

        self._rebuild_district_tables(conn)

        return attempted, inserted

    def _rebuild_district_tables(self, conn: sqlite3.Connection) -> None:
        """Rebuild display-name district tables from current sub_areas."""
        cur = conn.cursor()
        cur.execute("DELETE FROM x_sub_area_districts")
        cur.execute("DELETE FROM x_districts")

        rows = cur.execute(
            """
            SELECT
                sub_area_id,
                prefecture_id,
                city_id,
                area_id,
                COALESCE(section_id, 0) AS section_id
            FROM sub_areas
            ORDER BY
                prefecture_id,
                city_id,
                area_id,
                COALESCE(section_id, 0),
                sub_area_id
            """
        ).fetchall()

        district_key_to_id: Dict[Tuple[int, int, int, int], int] = {}
        next_id = 0
        for sub_area_id, pref_id, city_id, area_id, section_id in rows:
            key = (pref_id, city_id, area_id, section_id)
            x_district_id = district_key_to_id.get(key)
            if x_district_id is None:
                x_district_id = next_id
                district_key_to_id[key] = x_district_id
                cur.execute(
                    """
                    INSERT INTO x_districts (
                        x_district_id,
                        prefecture_id,
                        city_id,
                        area_id,
                        section_id,
                        first_sub_area_id
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        x_district_id,
                        pref_id,
                        city_id,
                        area_id,
                        section_id,
                        sub_area_id,
                    ),
                )
                next_id += 1
            cur.execute(
                """
                INSERT INTO x_sub_area_districts (
                    sub_area_id,
                    x_district_id
                ) VALUES (?, ?)
                """,
                (sub_area_id, x_district_id),
            )

        conn.commit()


def validate_district_hierarchy(conn: sqlite3.Connection) -> None:
    """Raise ValueError if x_districts is not a contiguous hierarchy order."""
    rows = conn.execute(
        """
        SELECT
            x_district_id,
            prefecture_id,
            city_id,
            area_id,
            section_id
        FROM x_districts
        ORDER BY x_district_id
        """
    )
    closed = [set() for _ in range(4)]
    current: Tuple[int, int, int, int] | None = None
    for x_district_id, pref_id, city_id, area_id, section_id in rows:
        path = (pref_id, city_id, area_id, section_id)
        if current is None:
            current = path
            continue
        if path == current:
            continue
        change_depth = next(
            (
                index
                for index, (current_value, path_value) in enumerate(zip(current, path))
                if current_value != path_value
            ),
            None,
        )
        if change_depth is None:
            continue
        for depth in range(change_depth, 4):
            closed[depth].add(current[:depth + 1])
        for depth in range(change_depth, 4):
            prefix = path[:depth + 1]
            if prefix in closed[depth]:
                raise ValueError(
                    "x_districts is not a contiguous hierarchy order: "
                    f"x_district_id={x_district_id} depth={depth + 1} prefix={prefix}"
                )
        current = path


__all__ = ["R2KAImporter", "validate_district_hierarchy"]

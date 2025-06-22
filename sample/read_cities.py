#!/usr/bin/env python3
"""Example script to read cities table from a SQLite database."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple


from dbf_utils.database import Database

def load_city_mapping(db_path: Path) -> Dict[int, Tuple[int, int]]:
    """Return a mapping from city_id to (pref_code, city_code)."""
    mapping: Dict[int, Tuple[int, int]] = {}
    with Database(db_path) as db:
        cur = db.conn.cursor()
        for row in cur.execute(
            "SELECT city_id, pref_code, city_code FROM cities ORDER BY city_id"
        ):
            city_id, pref_code, city_code = row
            mapping[city_id] = (pref_code, city_code)
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read the cities table and build a city_id mapping"
    )
    parser.add_argument("db_path", type=Path, help="Path to SQLite database")
    args = parser.parse_args()

    mapping = load_city_mapping(args.db_path)

    for city_id, codes in mapping.items():
        print(city_id, codes)


if __name__ == "__main__":
    main()

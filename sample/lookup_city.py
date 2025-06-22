#!/usr/bin/env python3
"""Example script to look up city_id by codes."""

from __future__ import annotations

import argparse
from pathlib import Path

from dbf_utils.database import Database
from dbf_utils.r2ka import CityIdSelector


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup city_id")
    parser.add_argument("db_path", type=Path, help="SQLite database path")
    parser.add_argument("pref_code", type=int, help="Prefecture code")
    parser.add_argument("city_code", type=int, help="City code")
    args = parser.parse_args()

    with Database(args.db_path) as db:
        selector = CityIdSelector(db)
        city_id = selector.get_city_id(args.pref_code, args.city_code)
        if city_id is None:
            print("Not found")
        else:
            print(city_id)


if __name__ == "__main__":
    main()

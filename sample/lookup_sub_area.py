#!/usr/bin/env python3
"""Example script to look up sub_area_id by codes."""

from __future__ import annotations

import argparse
from pathlib import Path


from dbf_utils.database import Database
from dbf_utils.r2ka import SubAreaIdSelector


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup sub_area_id")
    parser.add_argument("db_path", type=Path, help="SQLite database path")
    parser.add_argument("pref_code", type=int, help="Prefecture code")
    parser.add_argument("city_code", type=int, help="City code")
    parser.add_argument("s_area_code", type=int, help="Sub area code")
    args = parser.parse_args()

    with Database(args.db_path) as db:
        selector = SubAreaIdSelector(db)
        sub_area_id = selector.get_sub_area_id(
            args.pref_code, args.city_code, args.s_area_code
        )
        if sub_area_id is None:
            print("Not found")
        else:
            print(sub_area_id)


if __name__ == "__main__":
    main()

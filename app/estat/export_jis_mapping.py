#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


from dbf_utils.database import Database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export jis_code to sub_area_id mapping as CSV"
    )
    parser.add_argument("db_path", type=Path, help="SQLite database path")
    parser.add_argument("csv_path", type=Path, help="Output CSV file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Database(args.db_path) as db:
        cur = db.conn.execute(
            "SELECT sub_area_id, prefecture_code, city_code, s_area_code "
            "FROM codes_view ORDER BY sub_area_id"
        )
        rows = cur.fetchall()

    with open(args.csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        for sub_area_id, pref_code, city_code, s_area_code in rows:
            jis_code = f"{pref_code}{city_code:03d}{s_area_code:06d}"
            writer.writerow([jis_code, sub_area_id])


if __name__ == "__main__":
    main()

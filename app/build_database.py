#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


from dbf_utils.csv_to_sqlite import CsvToSqliteConverter
from dbf_utils.database import create_codes_view, Database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert CSV files to a normalized SQLite database")
    parser.add_argument("csv_dir", type=Path, help="Directory containing CSV files")
    parser.add_argument("db_path", type=Path, help="Output SQLite database path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    converter = CsvToSqliteConverter(csv_dir=str(args.csv_dir), db_path=str(args.db_path))
    converter.convert()
    # Create view if the required tables exist
    with Database(args.db_path) as db:
        create_codes_view(db.conn)
    print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

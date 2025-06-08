#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.r2ka_importer import R2KAImporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create database defined in R2KA_database_spec.md and import CSV files"
    )
    parser.add_argument("db_path", type=Path, help="SQLite database path")
    parser.add_argument(
        "csv_files",
        nargs="+",
        type=Path,
        help="R2KA CSV files encoded in SJIS",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    importer = R2KAImporter(db_path=str(args.db_path))
    attempted, inserted = importer.import_csvs([str(p) for p in args.csv_files])
    print(f"Processed {attempted} rows, inserted {inserted} new records.")
    print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

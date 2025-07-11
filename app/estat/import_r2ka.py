#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import glob


from dbf_utils.database import Database, create_codes_view
from dbf_utils.r2ka import R2KAImporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create database defined in R2KA_database_spec.md and import CSV/DBF files"
    )
    parser.add_argument("db_path", type=Path, help="SQLite database path")
    parser.add_argument(
        "csv_files",
        nargs="+",
        type=str,
        help="R2KA CSV or DBF files encoded in SJIS or glob patterns",
    )
    parser.add_argument(
        "--encoding",
        default="cp932",
        help="File encoding for input CSV/DBF (default: cp932)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = []
    for pattern in args.csv_files:
        matches = glob.glob(pattern)
        paths.extend(matches if matches else [pattern])
    with Database(args.db_path) as db:
        importer = R2KAImporter(db, encoding=args.encoding)
        try:
            attempted, inserted = importer.import_csvs(paths)
        except ValueError as e:
            print(e)
            sys.exit(1)
        create_codes_view(db.conn)
        print(f"Processed {attempted} rows, inserted {inserted} new records.")
        print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

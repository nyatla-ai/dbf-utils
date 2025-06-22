#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from dbf_utils.database import Database
from dbf_utils.n03 import N03Importer


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import N03 DBF into SQLite")
    p.add_argument("db_path", type=Path, help="SQLite database path")
    p.add_argument("dbf_file", type=Path, help="N03 DBF file")
    p.add_argument("--encoding", default="cp932", help="File encoding (default: cp932)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    with Database(args.db_path) as db:
        importer = N03Importer(db, encoding=args.encoding)
        attempted, inserted = importer.import_dbf(str(args.dbf_file))
        print(f"Processed {attempted} rows, inserted {inserted} cities.")
        print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

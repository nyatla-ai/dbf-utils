#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import io
import sys

# Allow running without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbf_utils.database import Database
from dbf_utils.gis_map import GISMapImporter


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import GIS Map DBF into SQLite")
    p.add_argument("db_path", type=Path, help="SQLite database path")
    p.add_argument("dbf_file", type=Path, help="GIS Map DBF file")
    p.add_argument("--encoding", default="cp932", help="File encoding (default: cp932)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    with Database(args.db_path) as db:
        importer = GISMapImporter(db, encoding=args.encoding)
        with io.open(args.dbf_file, "rb") as f:
            attempted, inserted = importer.import_dbf(f.name)
        print(f"Processed {attempted} rows, inserted {inserted} cities.")
        print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.r2ka_importer import R2KAImporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create database defined in R2KA_database_spec.md and import r2ka11.dbf"
    )
    parser.add_argument(
        "db_path", type=Path, help="Output SQLite database path"
    )
    parser.add_argument(
        "--dbf", type=Path, default=Path("dev/r2ka11.dbf"), help="Path to r2ka11.dbf"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    importer = R2KAImporter(db_path=str(args.db_path), dbf_path=str(args.dbf))
    importer.import_data()
    print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

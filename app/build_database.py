#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.csv_to_sqlite import CsvToSqliteConverter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert CSV files to a normalized SQLite database")
    parser.add_argument("csv_dir", type=Path, help="Directory containing CSV files")
    parser.add_argument("db_path", type=Path, help="Output SQLite database path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    converter = CsvToSqliteConverter(csv_dir=str(args.csv_dir), db_path=str(args.db_path))
    converter.convert()
    print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

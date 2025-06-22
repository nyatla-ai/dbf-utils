#!/usr/bin/env python3
"""Simple script to import a DBF file into a SQLite database."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable

from dbfread import DBF


def import_dbf(db_path: Path, dbf_files: Iterable[Path], encoding: str = "cp932") -> None:
    conn = sqlite3.connect(db_path)
    for dbf_path in dbf_files:
        table = dbf_path.stem
        dbf = DBF(str(dbf_path), encoding=encoding)
        fields = dbf.field_names
        columns = ", ".join(f'"{f}" TEXT' for f in fields)
        conn.execute(f'CREATE TABLE IF NOT EXISTS {table} ({columns})')
        placeholders = ", ".join("?" for _ in fields)
        for record in dbf:
            values = [record[f] for f in fields]
            conn.execute(f'INSERT INTO {table} VALUES ({placeholders})', values)
    conn.commit()
    conn.close()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import DBF files into a SQLite database")
    p.add_argument("db_path", type=Path, help="SQLite database path")
    p.add_argument("dbf_files", nargs="+", type=Path, help="DBF files to import")
    p.add_argument("--encoding", default="cp932", help="File encoding (default: cp932)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    import_dbf(args.db_path, args.dbf_files, encoding=args.encoding)
    print(f"Database saved to {args.db_path}")


if __name__ == "__main__":
    main()

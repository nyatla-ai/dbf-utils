from __future__ import annotations

import pandas as pd
import sqlite3
from pathlib import Path
from typing import Dict, List


def read_csv_files(csv_dir: Path) -> Dict[str, pd.DataFrame]:
    """Read all CSV files in a directory into a dictionary of DataFrames."""
    dataframes: Dict[str, pd.DataFrame] = {}
    for csv_file in csv_dir.glob("*.csv"):
        df = pd.read_csv(csv_file)
        table_name = csv_file.stem
        dataframes[table_name] = df
    return dataframes


def find_common_columns(frames: Dict[str, pd.DataFrame]) -> List[str]:
    """Find column names that appear in more than one DataFrame."""
    column_count: Dict[str, int] = {}
    for df in frames.values():
        for col in df.columns:
            column_count[col] = column_count.get(col, 0) + 1
    return [col for col, count in column_count.items() if count > 1]


def create_lookup_tables(frames: Dict[str, pd.DataFrame], common_columns: List[str]) -> Dict[str, pd.DataFrame]:
    """Create lookup tables for common columns and replace values with ids."""
    lookups: Dict[str, pd.DataFrame] = {}
    for col in common_columns:
        # gather unique values across all frames
        unique_values = pd.concat([df[col] for df in frames.values() if col in df.columns]).drop_duplicates().reset_index(drop=True)
        lookup_df = pd.DataFrame({col + "_id": range(1, len(unique_values) + 1), col: unique_values})
        lookups[col] = lookup_df
        value_to_id = {value: idx for idx, value in zip(lookup_df[col], lookup_df[col + "_id"])}
        for df in frames.values():
            if col in df.columns:
                df[col + "_id"] = df[col].map(value_to_id)
                df.drop(columns=[col], inplace=True)
    return lookups


def save_to_sqlite(db_path: Path, tables: Dict[str, pd.DataFrame]) -> None:
    """Save a dictionary of DataFrames to a SQLite database."""
    with sqlite3.connect(db_path) as conn:
        for table_name, df in tables.items():
            df.to_sql(table_name, conn, if_exists="replace", index=False)


class CsvToSqliteConverter:
    """Convert multiple CSV files to a normalized SQLite database."""

    def __init__(self, csv_dir: str, db_path: str):
        self.csv_dir = Path(csv_dir)
        self.db_path = Path(db_path)

    def convert(self) -> None:
        frames = read_csv_files(self.csv_dir)
        common_cols = find_common_columns(frames)
        lookup_tables = create_lookup_tables(frames, common_cols)
        all_tables = {**frames, **lookup_tables}
        save_to_sqlite(self.db_path, all_tables)


__all__ = ["CsvToSqliteConverter", "read_csv_files", "save_to_sqlite"]

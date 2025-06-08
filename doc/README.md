# CSV to SQLite Converter

This project provides a simple system for converting multiple CSV files into a normalized SQLite database. The main components are located in the `src` package and a script in `app` that performs the conversion.

## Usage

```bash
python app/build_database.py path/to/csv_directory output.db
```

The script reads all `*.csv` files inside the specified directory and creates a SQLite database. Columns that appear across multiple CSV files are normalized into lookup tables.

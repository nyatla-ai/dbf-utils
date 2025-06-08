# Estat SHP Utils

This repository contains tools for converting CSV files into an SQLite database in a normalized form.

Directory structure:

- `src/` - common source code
- `app/` - command line scripts built on top of `src`
- `dev/` - development helpers and internal files
- `doc/` - documentation
- `app/import_r2ka.py` - import R2KA CSV files using the schema described in
  `doc/R2KA_database_spec.md`

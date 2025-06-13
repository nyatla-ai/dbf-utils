import sqlite3
import tempfile
from pathlib import Path
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database
from src.r2ka_importer import R2KAImporter
from src.r2ka_api import CityIdSelector, SubAreaIdSelector, SubAreaReader


def test_get_sub_area_id():
    dbf_path = Path('dev/r2ka11.dbf')
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'out.db'
        with Database(db_path) as db:
            importer = R2KAImporter(db)
            importer.import_csvs([str(dbf_path)])

            selector = SubAreaIdSelector(db)

            # Known record from sample data
            sub_id = selector.get_sub_area_id(11, 101, 1000)
            assert sub_id is not None

            # second call should hit cache and not query database again
            class DummyConn:
                def execute(self, *args, **kwargs):
                    raise RuntimeError("db queried")

            selector._conn = DummyConn()
            again = selector.get_sub_area_id(11, 101, 1000)
            assert again == sub_id

            selector._conn = sqlite3.connect(str(db_path))
            missing = selector.get_sub_area_id(99, 999, 999999)
            assert missing is None


def test_get_city_id():
    dbf_path = Path('dev/r2ka11.dbf')
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'out.db'
        with Database(db_path) as db:
            importer = R2KAImporter(db)
            importer.import_csvs([str(dbf_path)])

            selector = CityIdSelector(db)

            # Known record from sample data
            city_id = selector.get_city_id(11, 101)
            assert city_id is not None

            class DummyConn:
                def execute(self, *args, **kwargs):
                    raise RuntimeError('db queried')

            selector._conn = DummyConn()
            again = selector.get_city_id(11, 101)
            assert again == city_id

            selector._conn = sqlite3.connect(str(db_path))
            missing = selector.get_city_id(99, 999)
            assert missing is None

def test_sub_area_reader():
    dbf_path = Path('dev/r2ka11.dbf')
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'out.db'
        with Database(db_path) as db:
            importer = R2KAImporter(db)
            importer.import_csvs([str(dbf_path)])

            reader = SubAreaReader(db)
            total = reader.count()
            rows = reader.fetch(0, 5)
            all_rows = reader.fetch_all()
            assert total > 0
            assert 0 < len(rows) <= 5
            assert len(all_rows) == total
            assert all('sub_area_id' in r for r in rows)

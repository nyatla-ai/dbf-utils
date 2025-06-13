import sqlite3
import tempfile
from pathlib import Path


from estat_shp_utils.database import Database
from estat_shp_utils.r2ka_importer import R2KAImporter
from estat_shp_utils.r2ka_api import (
    CityIdSelector,
    SubAreaIdSelector,
    SubAreaReader,
    CodesViewReader,
)


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


def test_codes_view_reader():
    dbf_path = Path('dev/r2ka11.dbf')
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'out.db'
        with Database(db_path) as db:
            importer = R2KAImporter(db)
            importer.import_csvs([str(dbf_path)])

            reader = CodesViewReader(db)
            total = reader.count()
            rows = reader.fetch(0, 5)
            assert total > 0
            assert 0 < len(rows) <= 5
            for r in rows:
                expect = ((r['prefecture_code'] * 1000 + r['city_code']) * 1000000 + r['s_area_code'])
                assert r['jis_code'] == expect

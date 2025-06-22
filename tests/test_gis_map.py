import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from dbf_utils.database import Database
from dbf_utils.gis_map import GISMapImporter


def test_import_gis_map_dbf():
    dbf_path = Path('dev/N03-20240101_33.dbf')
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'out.db'
        with Database(db_path) as db:
            importer = GISMapImporter(db, encoding='cp932')
            attempted, inserted = importer.import_dbf(str(dbf_path))
            assert attempted > 0
            assert inserted > 0
            cur = db.conn.execute('SELECT COUNT(*) FROM cities')
            count = cur.fetchone()[0]
            assert count == inserted
            # verify lookup tables
            cur = db.conn.execute('SELECT COUNT(*) FROM distincts')
            assert cur.fetchone()[0] >= 0
            cur = db.conn.execute('SELECT COUNT(*) FROM wards')
            assert cur.fetchone()[0] > 0
            cur = db.conn.execute('PRAGMA table_info(cities)')
            cols = [row[1] for row in cur.fetchall()]
            assert 'subprefecter_id' in cols
            assert 'distinct_id' in cols
            assert 'ward_id' in cols

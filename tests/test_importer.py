import sqlite3
import tempfile
from pathlib import Path
import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.r2ka_importer import R2KAImporter

class TestR2KAImporterIntegration(unittest.TestCase):
    def test_db_created_from_dbf(self):
        dbf_path = Path('dev/r2ka11.dbf')
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'out.db'
            importer = R2KAImporter(db_path=str(db_path))
            attempted, inserted = importer.import_csvs([str(dbf_path)])
            self.assertTrue(db_path.exists(), 'Database file should be created')
            self.assertGreater(attempted, 0)
            self.assertGreater(inserted, 0)
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) FROM prefectures')
                pref_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM cities')
                city_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM sub_areas')
                sub_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM areas')
                area_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM sections')
                section_count = cur.fetchone()[0]
            self.assertGreater(pref_count, 0)
            self.assertGreater(city_count, 0)
            self.assertGreater(sub_count, 0)
            self.assertGreater(area_count, 0)
            self.assertGreater(section_count, 0)

    def test_section_id_nullable(self):
        dbf_path = Path('dev/r2ka11.dbf')
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'out.db'
            importer = R2KAImporter(db_path=str(db_path))
            importer.import_csvs([str(dbf_path)])
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) FROM sub_areas WHERE section_id IS NULL')
                null_count = cur.fetchone()[0]

                # s_area_code % 100 == 0 -> section_id should be NULL
                cur.execute(
                    'SELECT sa.section_id FROM sub_areas sa '\
                    'JOIN areas a ON sa.area_id = a.area_id '\
                    'WHERE sa.s_area_code = ? AND a.area_name = ?',
                    (1000, '宮前町')
                )
                area_only_row = cur.fetchone()

                # section_code != 0 but name without 丁目 -> section_id should be NULL
                cur.execute(
                    'SELECT sa.section_id FROM sub_areas sa '\
                    'JOIN areas a ON sa.area_id = a.area_id '\
                    'WHERE sa.s_area_code = ? AND a.area_name = ?',
                    (3001, '大字指扇')
                )
                non_chome_row = cur.fetchone()

            self.assertGreater(null_count, 0)
            self.assertIsNotNone(area_only_row)
            self.assertIsNone(area_only_row[0])
            self.assertIsNotNone(non_chome_row)
            self.assertIsNone(non_chome_row[0])

if __name__ == '__main__':
    unittest.main()

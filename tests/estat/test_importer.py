import sqlite3
import tempfile
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))


from dbf_utils.database import Database
from dbf_utils.r2ka import R2KAImporter, validate_district_hierarchy

class TestR2KAImporterIntegration(unittest.TestCase):
    def test_db_created_from_dbf(self):
        dbf_path = Path('dev/r2ka11.dbf')
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'out.db'
            with Database(db_path) as db:
                importer = R2KAImporter(db, encoding="cp932")
                attempted, inserted = importer.import_csvs([str(dbf_path)])
                self.assertTrue(db_path.exists(), 'Database file should be created')
                self.assertGreater(attempted, 0)
                self.assertGreater(inserted, 0)
                conn = db.conn
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
                cur.execute('SELECT COUNT(*) FROM x_districts')
                district_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM x_sub_area_districts')
                sub_area_district_count = cur.fetchone()[0]
            self.assertGreater(pref_count, 0)
            self.assertGreater(city_count, 0)
            self.assertGreater(sub_count, 0)
            self.assertGreater(area_count, 0)
            self.assertGreater(section_count, 0)
            self.assertGreater(district_count, 0)
            self.assertEqual(sub_area_district_count, sub_count)

    def test_section_id_nullable(self):
        dbf_path = Path('dev/r2ka11.dbf')
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'out.db'
            with Database(db_path) as db:
                importer = R2KAImporter(db, encoding="cp932")
                importer.import_csvs([str(dbf_path)])
                conn = db.conn
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

    def test_district_tables_created(self):
        dbf_path = Path('dev/r2ka11.dbf')
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'out.db'
            with Database(db_path) as db:
                importer = R2KAImporter(db, encoding="cp932")
                importer.import_csvs([str(dbf_path)])
                conn = db.conn
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) FROM sub_areas')
                sub_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM x_districts')
                district_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM x_sub_area_districts')
                mapping_count = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM x_districts WHERE section_id IS NULL')
                null_section_count = cur.fetchone()[0]
                cur.execute('SELECT MIN(x_district_id), MAX(x_district_id) FROM x_districts')
                min_id, max_id = cur.fetchone()

            self.assertEqual(mapping_count, sub_count)
            self.assertGreater(district_count, 0)
            self.assertLessEqual(district_count, sub_count)
            self.assertEqual(null_section_count, 0)
            self.assertEqual(min_id, 0)
            self.assertEqual(max_id, district_count - 1)

    def test_district_tables_are_hierarchy_contiguous_when_area_reappears(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'r2ka.csv'
            csv_path.write_text(
                'PREF,CITY,S_AREA,PREF_NAME,CITY_NAME,S_NAME\n'
                '01,106,010000,Hokkaido,Sapporo Minami,Moiwa\n'
                '01,106,320001,Hokkaido,Sapporo Minami,Kashiwa 1\n'
                '01,106,320002,Hokkaido,Sapporo Minami,Kashiwa 2\n'
                '01,106,330001,Hokkaido,Sapporo Minami,Moiwa 1\n'
                '01,106,330002,Hokkaido,Sapporo Minami,Moiwa 2\n',
                encoding='cp932',
            )
            db_path = Path(tmpdir) / 'out.db'
            with Database(db_path) as db:
                importer = R2KAImporter(db, encoding="cp932")
                importer.import_csvs([str(csv_path)])
                validate_district_hierarchy(db.conn)
                rows = db.conn.execute(
                    """
                    SELECT
                        a.area_name,
                        COALESCE(s.section_name, '') AS section_name
                    FROM x_districts xd
                    JOIN areas a ON xd.area_id = a.area_id
                    LEFT JOIN sections s ON xd.section_id = s.section_id
                    ORDER BY xd.x_district_id
                    """
                ).fetchall()

            self.assertEqual(
                rows,
                [
                    ('Moiwa', ''),
                    ('Moiwa', '1'),
                    ('Moiwa', '2'),
                    ('Kashiwa', '1'),
                    ('Kashiwa', '2'),
                ],
            )

if __name__ == '__main__':
    unittest.main()

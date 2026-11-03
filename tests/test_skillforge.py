import json
import math
import os
import tempfile
import unittest
from pathlib import Path

import skillforge as sf


def fresh():
    return {"settings": dict(sf.DEFAULT_SETTINGS), "skills": []}


class TestCore(unittest.TestCase):
    def setUp(self):
        self.d = fresh()
        sf.add_skill(self.d, "Python", 5, "Programming")
        sf.add_skill(self.d, "SQL", 3, "Database")

    def test_add_normalises_and_defaults_category(self):
        sf.add_skill(self.d, "  Git   Basics ", 2)
        skill = sf.find(self.d, "git basics")
        self.assertEqual(skill["name"], "Git Basics")
        self.assertEqual(skill["category"], "General")

    def test_add_rejects_duplicate_empty_and_bad_target(self):
        with self.assertRaises(ValueError):
            sf.add_skill(self.d, "python", 2)
        with self.assertRaises(ValueError):
            sf.add_skill(self.d, "   ", 2)
        with self.assertRaises(ValueError):
            sf.add_skill(self.d, "Go", 6)
        with self.assertRaises(ValueError):
            sf.add_skill(self.d, "Go", 0)

    def test_update_category_and_target(self):
        sf.update_skill(self.d, "sql", category="Data", target=4)
        skill = sf.find(self.d, "SQL")
        self.assertEqual((skill["category"], skill["target"]), ("Data", 4))
        sf.update_skill(self.d, "SQL")  # no-op keeps values
        self.assertEqual(sf.find(self.d, "SQL")["target"], 4)

    def test_delete(self):
        sf.delete_skill(self.d, "Python")
        self.assertIsNone(sf.find(self.d, "Python"))
        with self.assertRaises(ValueError):
            sf.delete_skill(self.d, "Python")

    def test_missing_skill_raises(self):
        with self.assertRaises(ValueError):
            sf.track_skill(self.d, "Rust", 1)


class TestTracking(unittest.TestCase):
    def setUp(self):
        self.d = fresh()
        sf.add_skill(self.d, "Python", 5)

    def level(self):
        return sf.rows(self.d)[0]["level"]

    def test_level_from_hours(self):
        sf.track_skill(self.d, "Python", 12)
        self.assertEqual(self.level(), 2)
        sf.track_skill(self.d, "Python", 8)
        self.assertEqual(self.level(), 3)

    def test_level_capped_at_max(self):
        sf.track_skill(self.d, "Python", 1000)
        self.assertEqual(self.level(), sf.DEFAULT_SETTINGS["max_level"])

    def test_achieved_flag(self):
        self.assertFalse(sf.rows(self.d)[0]["achieved"])
        sf.track_skill(self.d, "Python", 40)
        self.assertTrue(sf.rows(self.d)[0]["achieved"])

    def test_invalid_hours_rejected(self):
        for bad in (0, -3, math.nan, math.inf):
            with self.assertRaises(ValueError):
                sf.track_skill(self.d, "Python", bad)
        self.assertEqual(self.d["skills"][0]["hours"], 0.0)

    def test_settings_change_recomputes_levels(self):
        sf.track_skill(self.d, "Python", 20)
        sf.set_settings(self.d, 5, 5)
        self.assertEqual(self.level(), 5)

    def test_settings_validation(self):
        with self.assertRaises(ValueError):
            sf.set_settings(self.d, 0, 5)
        with self.assertRaises(ValueError):
            sf.set_settings(self.d, 10, 4)  # below existing target 5
        self.assertEqual(self.d["settings"], sf.DEFAULT_SETTINGS)


class TestReports(unittest.TestCase):
    def setUp(self):
        self.d = fresh()
        sf.add_skill(self.d, "Python", 5, "Programming")
        sf.add_skill(self.d, "SQL", 2, "Database")
        sf.add_skill(self.d, "Java", 2, "programming")
        sf.track_skill(self.d, "Python", 12)
        sf.track_skill(self.d, "SQL", 10)

    def test_filter_category_case_insensitive(self):
        names = [r["name"] for r in sf.filter_rows(self.d, category="PROGRAMMING")]
        self.assertEqual(names, ["Python", "Java"])

    def test_filter_status(self):
        self.assertEqual([r["name"] for r in sf.filter_rows(self.d, achieved=True)], ["SQL"])
        self.assertEqual(len(sf.filter_rows(self.d, achieved=False)), 2)

    def test_summary(self):
        s = sf.summary(self.d)
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["achieved"], 1)
        self.assertEqual(s["in_progress"], 2)
        self.assertEqual(s["total_hours"], 22.0)
        self.assertEqual(s["categories"], {"Programming": 2, "Database": 1})

    def test_summary_empty(self):
        s = sf.summary(fresh())
        self.assertEqual((s["total"], s["avg_level"]), (0, 0))

    def test_csv_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = sf.export_csv(self.d, os.path.join(tmp, "out.csv"))
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], ",".join(sf.FIELDS))
        self.assertEqual(len(lines), 4)


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "data.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_gives_empty_store(self):
        self.assertEqual(sf.load(self.path), fresh())

    def test_corrupt_or_wrong_shape_gives_empty_store(self):
        for content in ("{not json", "[1, 2]", '{"skills": 5, "settings": 3}'):
            Path(self.path).write_text(content, encoding="utf-8")
            data = sf.load(self.path)
            self.assertEqual(data["skills"], [])
            self.assertEqual(data["settings"], sf.DEFAULT_SETTINGS)

    def test_round_trip(self):
        d = fresh()
        sf.add_skill(d, "Python", 4, "Programming")
        sf.track_skill(d, "Python", 3.5)
        sf.save(d, self.path)
        self.assertEqual(sf.load(self.path), d)
        self.assertEqual(json.loads(Path(self.path).read_text())["skills"][0]["hours"], 3.5)
        self.assertEqual(os.listdir(self.tmp.name), ["data.json"])  # no temp leftovers


class TestPdf(unittest.TestCase):
    def test_pdf_export(self):
        try:
            import reportlab  # noqa: F401
        except ImportError:
            self.skipTest("reportlab not installed")
        d = fresh()
        sf.add_skill(d, "Python", 5)
        with tempfile.TemporaryDirectory() as tmp:
            path = sf.export_pdf(d, os.path.join(tmp, "r.pdf"))
            self.assertTrue(Path(path).read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()

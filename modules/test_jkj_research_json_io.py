import json
import math
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from modules.jkj_research_json_io import write_json_new


class TestResearchJsonIO(unittest.TestCase):
    def test_datetime_is_serialized_as_iso_string(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.json"
            write_json_new(path, {"time": datetime(2026, 10, 12, 13, 0)})
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["time"], "2026-10-12T13:00:00")

    def test_existing_file_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.json"
            path.write_text('{"original": true}\n', encoding="utf-8")
            with self.assertRaises(FileExistsError):
                write_json_new(path, {"replacement": True})
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"original": True},
            )

    def test_existing_temporary_file_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.json"
            temporary = path.with_name(path.name + ".tmp")
            original = json.dumps({"temporary": True})
            temporary.write_text(original, encoding="utf-8")

            with self.assertRaises(FileExistsError):
                write_json_new(path, {"replacement": True})

            self.assertFalse(path.exists())
            self.assertEqual(
                temporary.read_text(encoding="utf-8"),
                original,
            )

    def test_non_finite_number_fails_before_file_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.json"
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        write_json_new(path, {"value": value})
                    self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)

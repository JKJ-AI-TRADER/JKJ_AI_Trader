"""Offline tests for the V21.2.18 baseline store.

All writes use temporary files. No Zerodha calls, live orders, or paper trades.
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from modules.nifty_option_v21_2_18_baseline_store import (
    save_baseline,
    load_today_baseline,
)


CAPTURED_AT = "2026-10-09T09:15:04+05:30"
TEST_NOW = datetime.fromisoformat("2026-10-09T09:15:00+05:30")


def valid_result():
    return {
        "Status": "BASELINE_CAPTURE_COMPLETE",
        "Baseline Type": "GENUINE_915",
        "Baseline Time": "09:15",
        "Captured At": CAPTURED_AT,
        "NIFTY Spot": 23114.0,
        "Expiry": "2026-10-13",
        "Universe Count": 1,
        "Baseline Count": 1,
        "Baseline": [{
            "Trading Symbol": "NIFTYTEST",
            "Option Type": "CE",
            "Strike": 23000.0,
            "Captured At": CAPTURED_AT,
            "9:15 Price": 100.0,
            "Previous Close": 98.0,
        }],
        "Live Order": False,
        "Paper Trade": False,
    }


class BaselineStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "baseline.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_baseline_saves_and_loads(self):
        result = valid_result()
        saved = save_baseline(result, path=self.path)
        loaded = load_today_baseline(path=self.path, now=TEST_NOW)

        self.assertEqual(saved["Status"], "BASELINE_SAVED")
        self.assertEqual(saved["Trading Date"], "2026-10-09")
        self.assertEqual(loaded, result)
        self.assertFalse(saved["Live Order"])
        self.assertFalse(saved["Paper Trade"])

    def test_rejects_invalid_results_without_writing(self):
        cases = []

        item = valid_result()
        item["Status"] = "WRONG_STATUS"
        cases.append(("wrong status", item))

        item = valid_result()
        item["Baseline Type"] = "SYNTHETIC"
        cases.append(("synthetic", item))

        item = valid_result()
        item["Captured At"] = "TEST"
        cases.append(("malformed timestamp", item))

        item = valid_result()
        item["Captured At"] = "2026-10-09T09:15:04"
        cases.append(("timezone-naive timestamp", item))

        item = valid_result()
        item["Captured At"] = "2026-10-09T09:17:00+05:30"
        cases.append(("late timestamp", item))

        item = valid_result()
        item["Captured At"] = "2026-10-09T09:14:00+05:30"
        cases.append(("early timestamp", item))

        item = valid_result()
        item["Baseline"] = []
        cases.append(("empty records", item))

        item = valid_result()
        item["Baseline Count"] = 2
        cases.append(("record count mismatch", item))

        for name, result in cases:
            with self.subTest(case=name):
                self.assertEqual(
                    save_baseline(result, path=self.path)["Status"],
                    "BASELINE_NOT_SAVED",
                )
                self.assertFalse(self.path.exists())

    def test_rejected_capture_does_not_overwrite_existing_file(self):
        first = valid_result()
        self.assertEqual(
            save_baseline(first, path=self.path)["Status"],
            "BASELINE_SAVED",
        )
        original_bytes = self.path.read_bytes()

        late = valid_result()
        late["Captured At"] = "2026-10-09T09:17:00+05:30"
        result = save_baseline(late, path=self.path)

        self.assertEqual(result["Status"], "BASELINE_NOT_SAVED")
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_rejects_record_timestamp_mismatch(self):
        result = valid_result()
        result["Baseline"][0]["Captured At"] = "2026-10-09T09:15:05+05:30"

        saved = save_baseline(result, path=self.path)

        self.assertEqual(saved["Status"], "BASELINE_NOT_SAVED")
        self.assertFalse(self.path.exists())

    def test_valid_second_capture_cannot_overwrite_existing_baseline(self):
        first = valid_result()
        self.assertEqual(
            save_baseline(first, path=self.path)["Status"],
            "BASELINE_SAVED",
        )
        original_bytes = self.path.read_bytes()

        second = valid_result()
        second["Captured At"] = "2026-10-09T09:15:10+05:30"
        second["Baseline"][0]["Captured At"] = second["Captured At"]
        second["NIFTY Spot"] = 23200.0

        saved = save_baseline(second, path=self.path)

        self.assertEqual(saved["Status"], "BASELINE_NOT_SAVED")
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_loader_rejects_wrong_trading_date(self):
        result = valid_result()
        payload = {
            "Trading Date": "2026-10-08",
            "Baseline Type": "GENUINE_915",
            "Baseline": result,
        }
        self.path.write_text(json.dumps(payload), encoding="utf-8")
        self.assertIsNone(load_today_baseline(path=self.path, now=TEST_NOW))

    def test_loader_rejects_invalid_json(self):
        self.path.write_text("{not json", encoding="utf-8")
        self.assertIsNone(load_today_baseline(path=self.path, now=TEST_NOW))


if __name__ == "__main__":
    unittest.main(verbosity=2)

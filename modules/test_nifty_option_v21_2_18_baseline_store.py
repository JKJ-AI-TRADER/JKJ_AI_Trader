"""Offline tests for the V21.2.18 baseline store.

All writes use temporary files. No Zerodha calls, live orders, or paper trades.
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import modules.nifty_option_v21_2_18_baseline_store as store
from modules.nifty_option_v21_2_18_baseline_store import (
    baseline_file_for_date,
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


def result_for_date(trading_date, capture_clock="09:15:04"):
    captured_at = f"{trading_date}T{capture_clock}+05:30"
    result = valid_result()
    result["Captured At"] = captured_at
    result["Baseline"][0]["Captured At"] = captured_at
    return result


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

    def test_baseline_filename_uses_ist_trading_date(self):
        utc_time = datetime.fromisoformat("2026-10-08T20:00:00+00:00")
        dated_path = baseline_file_for_date(
            utc_time,
            base_path=self.path,
        )
        self.assertEqual(
            dated_path.name,
            "baseline_2026-10-09.json",
        )

        with self.assertRaises(ValueError):
            baseline_file_for_date(
                datetime(2026, 10, 9, 9, 15),
                base_path=self.path,
            )

    def test_default_storage_keeps_each_trading_date_separate(self):
        day_8 = datetime.fromisoformat("2026-10-08T09:15:00+05:30")
        day_12 = datetime.fromisoformat("2026-10-12T09:15:00+05:30")
        first = result_for_date("2026-10-08")
        second = result_for_date("2026-10-12")

        with patch.object(store, "BASELINE_FILE", self.path):
            first_saved = save_baseline(first)
            second_saved = save_baseline(second)

            file_8 = baseline_file_for_date(day_8)
            file_12 = baseline_file_for_date(day_12)

            self.assertEqual(first_saved["Status"], "BASELINE_SAVED")
            self.assertEqual(second_saved["Status"], "BASELINE_SAVED")
            self.assertTrue(file_8.exists())
            self.assertTrue(file_12.exists())
            self.assertFalse(self.path.exists())

            self.assertEqual(load_today_baseline(now=day_8), first)
            self.assertEqual(load_today_baseline(now=day_12), second)
            self.assertIsNone(
                load_today_baseline(
                    now=datetime.fromisoformat("2026-10-09T09:15:00+05:30")
                )
            )

            original_day_8 = file_8.read_bytes()
            replacement = result_for_date("2026-10-08", "09:15:10")
            replacement["NIFTY Spot"] = 99999.0
            refused = save_baseline(replacement)

            self.assertEqual(refused["Status"], "BASELINE_NOT_SAVED")
            self.assertEqual(file_8.read_bytes(), original_day_8)
            self.assertEqual(load_today_baseline(now=day_8), first)

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

    def test_loader_rejects_valid_json_non_object_payloads(self):
        for payload in [[], "invalid structure", 123, None]:
            with self.subTest(payload=payload):
                self.path.write_text(json.dumps(payload), encoding="utf-8")
                self.assertIsNone(
                    load_today_baseline(path=self.path, now=TEST_NOW)
                )

    def test_rejects_non_finite_or_non_positive_baseline_prices(self):
        for price in [float("nan"), float("inf"), float("-inf"), 0.0, -1.0]:
            with self.subTest(price=price):
                result = valid_result()
                result["Baseline"][0]["9:15 Price"] = price

                saved = save_baseline(result, path=self.path)

                self.assertEqual(saved["Status"], "BASELINE_NOT_SAVED")
                self.assertFalse(self.path.exists())



if __name__ == "__main__":
    unittest.main(verbosity=2)

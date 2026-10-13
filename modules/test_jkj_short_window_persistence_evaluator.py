import math
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.jkj_short_window_persistence_evaluator import evaluate_log

IST = ZoneInfo("Asia/Kolkata")
BASE = datetime(2026, 10, 12, 10, 0, tzinfo=IST)


def observation(symbol, seconds, price):
    return {
        "Symbol": symbol,
        "Time": (BASE + timedelta(seconds=seconds)).isoformat(),
        "Price": price,
    }


def log(records):
    return {"Trading Date": "2026-10-12", "Live Observations": records}


class TestShortWindowPersistence(unittest.TestCase):
    def test_six_current_samples_split_at_long_gap(self):
        records = [
            observation("NIFTYCE", 0, 80.75),
            observation("NIFTYCE", 306, 81.10),
            observation("NIFTYCE", 311, 81.25),
            observation("NIFTYCE", 316, 80.70),
        ]
        result = evaluate_log(log(records))
        self.assertEqual(
            [w["Samples"] for w in result["Windows"]], [1, 3]
        )
        self.assertTrue(all(
            w["Status"] == "INSUFFICIENT_SAMPLE"
            for w in result["Windows"]
        ))

    def test_five_samples_over_sixty_seconds_are_eligible(self):
        records = [
            observation("NIFTYCE", t, 100 + t / 100)
            for t in (0, 15, 30, 45, 60)
        ]
        result = evaluate_log(log(records))
        self.assertEqual(len(result["Windows"]), 1)
        self.assertEqual(
            result["Windows"][0]["Status"],
            "ELIGIBLE_FOR_PERSISTENCE_REVIEW",
        )

    def test_gap_boundary_exactly_15_seconds_vs_16_seconds(self):
        records = [
            observation("CE", 0, 100),
            observation("CE", 15, 101),
            observation("CE", 30, 102),
            observation("CE", 46, 103),
        ]
        result = evaluate_log(log(records))
        self.assertEqual(
            [window["Samples"] for window in result["Windows"]],
            [3, 1],
        )

    def test_interleaved_symbols_keep_independent_windows(self):
        records = [
            observation("CE", 0, 100),
            observation("PE", 5, 200),
            observation("CE", 10, 101),
            observation("PE", 15, 199),
        ]
        result = evaluate_log(log(records))
        by_symbol = {
            w["Symbol"]: w["Samples"] for w in result["Windows"]
        }
        self.assertEqual(by_symbol, {"CE": 2, "PE": 2})

    def test_invalid_prices_are_rejected(self):
        records = [
            observation("CE", 0, True),
            observation("CE", 5, math.nan),
            observation("CE", 10, 0),
        ]
        result = evaluate_log(log(records))
        self.assertEqual(result["Accepted Observations"], 0)
        self.assertEqual(result["Rejected Observations"], 3)

    def test_full_timestamp_from_wrong_trading_date_is_rejected(self):
        records = [
            observation("CE", 0, 100),
            {
                "Symbol": "CE",
                "Time": "2026-10-13T10:00:05+05:30",
                "Price": 101,
            },
        ]
        result = evaluate_log(log(records))
        self.assertEqual(result["Accepted Observations"], 1)
        self.assertEqual(result["Rejected Observations"], 1)
        self.assertEqual(result["Windows"][0]["Samples"], 1)

    def test_evaluator_keeps_trading_disabled(self):
        result = evaluate_log(log([
            observation("CE", 0, 100)
        ]))
        self.assertIs(result["Trading Decision"], False)
        self.assertIs(result["Live Order"], False)
        self.assertIs(result["Paper Trade"], False)
        self.assertIs(result["Baseline Write"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)

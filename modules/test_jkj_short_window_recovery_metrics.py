"""Offline tests for peak, trough, pullback and recovery metrics."""

import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.jkj_short_window_persistence_evaluator import evaluate_log

IST = ZoneInfo("Asia/Kolkata")
BASE = datetime(2026, 10, 12, 10, 0, tzinfo=IST)


def make_log(prices):
    records = [
        {
            "Symbol": "TESTCE",
            "Time": (BASE + timedelta(seconds=i * 15)).isoformat(),
            "Price": price,
        }
        for i, price in enumerate(prices)
    ]
    return {"Trading Date": "2026-10-12", "Live Observations": records}


class TestRecoveryMetrics(unittest.TestCase):
    def metric(self, prices):
        result = evaluate_log(make_log(prices))
        self.assertEqual(len(result["Windows"]), 1)
        return result["Windows"][0]

    def test_sustained_rise_has_no_peak_giveback(self):
        result = self.metric([100, 101, 102, 103, 104])
        self.assertEqual(result["Peak Price"], 104)
        self.assertEqual(result["Trough After Peak Price"], 104)
        self.assertEqual(result["Peak-to-Trough Drawdown"], 0)
        self.assertIsNone(result["Giveback Recovered %"])

    def test_sharp_pullback_without_recovery(self):
        result = self.metric([100, 105, 102, 99, 98])
        self.assertEqual(result["Peak Price"], 105)
        self.assertEqual(result["Trough After Peak Price"], 98)
        self.assertEqual(result["Peak-to-Trough Drawdown"], 7)
        self.assertEqual(result["Giveback Recovered %"], 0)

    def test_partial_recovery_recovers_half_the_drawdown(self):
        result = self.metric([100, 110, 105, 102, 106])
        self.assertEqual(result["Peak Price"], 110)
        self.assertEqual(result["Trough After Peak Price"], 102)
        self.assertEqual(result["Peak-to-Trough Drawdown"], 8)
        self.assertEqual(result["Giveback Recovered %"], 50.0)
        self.assertAlmostEqual(result["Recovery from Trough %"], 3.9216, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)

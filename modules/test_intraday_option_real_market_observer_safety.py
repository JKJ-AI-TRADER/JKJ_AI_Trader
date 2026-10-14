"""Offline safety tests for the V12.1 real-market option observer."""

import math
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)

IST = ZoneInfo("Asia/Kolkata")


class TestIntradayOptionRealMarketObserverSafety(unittest.TestCase):
    def setUp(self):
        self.data = {
            "Trading Symbol": "NIFTY26O1322350CE",
            "Instrument Token": 123456,
            "Current Price": 104.55,
            "Volume": 38260365,
            "Last Trade Time": datetime.now(IST).isoformat(),
        }

    def test_accepts_valid_recent_observation(self):
        result = observe_option_market(self.data)
        self.assertEqual(result["Status"], "READY")
        self.assertEqual(result["Data Status"], "VALID")
        self.assertEqual(result["Trading Symbol"], self.data["Trading Symbol"])

    def test_rejects_boolean_and_non_finite_prices(self):
        for value in (True, False, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                data = self.data.copy()
                data["Current Price"] = value
                result = observe_option_market(data)
                self.assertEqual(result["Status"], "INVALID")

    def test_rejects_boolean_and_non_finite_volume(self):
        for value in (True, False, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                data = self.data.copy()
                data["Volume"] = value
                result = observe_option_market(data)
                self.assertEqual(result["Status"], "INVALID")

    def test_zero_volume_remains_incomplete(self):
        data = self.data.copy()
        data["Volume"] = 0
        result = observe_option_market(data)
        self.assertEqual(result["Status"], "INCOMPLETE")

    def test_rejects_invalid_instrument_tokens(self):
        for value in (True, False, 0, -1, 1.5):
            with self.subTest(value=value):
                data = self.data.copy()
                data["Instrument Token"] = value
                result = observe_option_market(data)
                self.assertEqual(result["Status"], "INVALID")

    def test_rejects_stale_timestamp(self):
        data = self.data.copy()
        data["Last Trade Time"] = (
            datetime.now(IST) - timedelta(seconds=301)
        ).isoformat()
        result = observe_option_market(data)
        self.assertEqual(result["Status"], "STALE")

    def test_rejects_timestamp_too_far_in_future(self):
        data = self.data.copy()
        data["Last Trade Time"] = (
            datetime.now(IST) + timedelta(seconds=10)
        ).isoformat()
        result = observe_option_market(data)
        self.assertEqual(result["Status"], "INVALID")

    def test_naive_exchange_timestamp_is_interpreted_as_ist(self):
        data = self.data.copy()
        data["Last Trade Time"] = (
            datetime.now(IST).replace(tzinfo=None).isoformat()
        )
        result = observe_option_market(data)
        self.assertEqual(result["Status"], "READY")

    def test_rejects_malformed_timestamp(self):
        data = self.data.copy()
        data["Last Trade Time"] = "not-a-timestamp"
        result = observe_option_market(data)
        self.assertEqual(result["Status"], "INVALID")

    def test_rejects_empty_symbol(self):
        data = self.data.copy()
        data["Trading Symbol"] = "   "
        result = observe_option_market(data)
        self.assertEqual(result["Status"], "INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)

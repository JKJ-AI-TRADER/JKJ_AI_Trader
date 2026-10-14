"""Offline safety tests for the broker-independent option market-data provider."""

import math
import unittest

from modules.intraday_option_market_data import create_option_market_data


class TestOptionMarketDataSafety(unittest.TestCase):
    def setUp(self):
        self.data = {
            "trading_symbol": "NIFTY26O1322350CE",
            "instrument_token": 123456,
            "underlying": "NIFTY",
            "expiry": "2026-10-13",
            "strike": 22350,
            "option_type": "CE",
            "current_price": 100.0,
            "open_price": 98.0,
            "high_price": 105.0,
            "low_price": 95.0,
            "volume": 1000,
            "timestamp": "2026-10-12T12:00:00+05:30",
        }

    def test_valid_quote_remains_ready(self):
        result = create_option_market_data(**self.data)
        self.assertEqual(result["Status"], "READY")
        self.assertEqual(result["Data Status"], "VALID")
        self.assertEqual(result["Current Price"], 100.0)

    def test_rejects_non_finite_values_in_all_numeric_fields(self):
        fields = (
            "current_price", "open_price", "high_price",
            "low_price", "volume", "strike",
        )
        for field in fields:
            for invalid in (math.nan, math.inf, -math.inf):
                with self.subTest(field=field, value=invalid):
                    data = self.data.copy()
                    data[field] = invalid
                    result = create_option_market_data(**data)
                    self.assertEqual(result["Status"], "INVALID")

    def test_rejects_booleans_in_all_numeric_fields(self):
        fields = (
            "current_price", "open_price", "high_price",
            "low_price", "volume", "strike",
        )
        for field in fields:
            with self.subTest(field=field):
                data = self.data.copy()
                data[field] = True
                result = create_option_market_data(**data)
                self.assertEqual(result["Status"], "INVALID")

    def test_rejects_high_below_low(self):
        data = self.data.copy()
        data.update(high_price=90.0, low_price=95.0)
        result = create_option_market_data(**data)
        self.assertEqual(result["Status"], "INVALID")

    def test_rejects_current_price_outside_reported_range(self):
        for price in (94.0, 106.0):
            with self.subTest(current_price=price):
                data = self.data.copy()
                data["current_price"] = price
                result = create_option_market_data(**data)
                self.assertEqual(result["Status"], "INVALID")

    def test_rejects_open_price_outside_reported_range(self):
        for price in (94.0, 106.0):
            with self.subTest(open_price=price):
                data = self.data.copy()
                data["open_price"] = price
                result = create_option_market_data(**data)
                self.assertEqual(result["Status"], "INVALID")

    def test_rejects_non_finite_derived_calculations(self):
        data = self.data.copy()
        data.update(
            current_price=1e308,
            open_price=1e-308,
            high_price=1e308,
            low_price=1e-308,
        )
        result = create_option_market_data(**data)
        self.assertEqual(result["Status"], "INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)

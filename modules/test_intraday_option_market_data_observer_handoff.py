"""Offline integration tests: option normalizer -> real-market observer."""

import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from modules.intraday_option_market_data import create_option_market_data
from modules.intraday_option_real_market_observer import observe_option_market

IST = ZoneInfo("Asia/Kolkata")


class TestMarketDataObserverHandoff(unittest.TestCase):
    def make_market_data(self, timestamp=None, **overrides):
        values = {
            "trading_symbol": "NIFTY26O1322350CE",
            "instrument_token": 123456,
            "underlying": "NIFTY",
            "expiry": "2026-10-13",
            "strike": 22350,
            "option_type": "CE",
            "current_price": 104.55,
            "open_price": 299.95,
            "high_price": 333.15,
            "low_price": 98.80,
            "volume": 38260365,
            "timestamp": datetime.now(IST).isoformat() if timestamp is None else timestamp,
        }
        values.update(overrides)
        return create_option_market_data(**values)

    def test_valid_normalized_data_reaches_observer(self):
        normalized = self.make_market_data()
        self.assertEqual(normalized["Status"], "READY")

        result = observe_option_market(
            normalized,
            {"Underlying": "NIFTY", "Current Price": 22372.90},
        )

        self.assertEqual(result["Status"], "READY")
        self.assertEqual(result["Data Status"], "VALID")
        self.assertEqual(result["Trading Symbol"], "NIFTY26O1322350CE")
        self.assertEqual(result["Underlying Data"]["Underlying"], "NIFTY")

    def test_stale_data_is_rejected_by_observer(self):
        old_timestamp = (
            datetime.now(IST) - timedelta(seconds=301)
        ).isoformat()
        normalized = self.make_market_data(timestamp=old_timestamp)
        self.assertEqual(normalized["Status"], "READY")

        result = observe_option_market(normalized)
        self.assertEqual(result["Status"], "STALE")

    def test_future_timestamp_is_rejected_by_observer(self):
        future_timestamp = (
            datetime.now(IST) + timedelta(seconds=10)
        ).isoformat()
        normalized = self.make_market_data(timestamp=future_timestamp)
        self.assertEqual(normalized["Status"], "READY")

        result = observe_option_market(normalized)
        self.assertEqual(result["Status"], "INVALID")

    def test_non_finite_price_is_rejected_by_normalizer(self):
        normalized = self.make_market_data(current_price=float("nan"))
        self.assertEqual(normalized["Status"], "INVALID")

    def test_inconsistent_ohlc_is_rejected_by_normalizer(self):
        normalized = self.make_market_data(
            current_price=350.0,
            high_price=333.15,
        )
        self.assertEqual(normalized["Status"], "INVALID")

    def test_missing_timestamp_is_not_accepted_as_fresh_market_time(self):
        normalized = self.make_market_data(timestamp="")
        # The provider supplies its default timestamp when given None only;
        # an empty string is passed through and the observer rejects it.
        self.assertEqual(normalized["Status"], "READY")
        result = observe_option_market(normalized)
        self.assertEqual(result["Status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main(verbosity=2)

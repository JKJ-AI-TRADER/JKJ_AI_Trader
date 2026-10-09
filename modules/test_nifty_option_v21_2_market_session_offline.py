import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from modules.nifty_option_v21_2_market_session import (
    get_market_session_state,
)

IST = ZoneInfo("Asia/Kolkata")


class MarketSessionTimezoneTests(unittest.TestCase):
    def test_utc_time_is_converted_to_ist(self):
        now = datetime(2026, 10, 9, 3, 44, 45, tzinfo=timezone.utc)
        result = get_market_session_state(now)

        self.assertEqual(result["Session State"], "PRE_MARKET")
        self.assertTrue(result["Current Time"].endswith("+05:30"))
        self.assertIn("09:14:45", result["Current Time"])

    def test_naive_time_is_interpreted_as_ist(self):
        now = datetime(2026, 10, 9, 9, 5)
        result = get_market_session_state(now)

        self.assertEqual(result["Session State"], "PRE_MARKET")
        self.assertIn("+05:30", result["Current Time"])

    def test_market_open_boundary_uses_ist(self):
        now = datetime(2026, 10, 9, 3, 45, tzinfo=timezone.utc)
        result = get_market_session_state(now)

        self.assertEqual(result["Session State"], "MARKET_SESSION")


if __name__ == "__main__":
    unittest.main(verbosity=2)

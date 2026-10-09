"""Offline tests for baseline capture timing. No Zerodha API calls."""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from modules.nifty_option_v21_2_18_baseline import capture_915_baseline

IST = ZoneInfo("Asia/Kolkata")


def fake_instrument():
    return {
        "name": "NIFTY",
        "instrument_type": "CE",
        "expiry": datetime(2026, 10, 13).date(),
        "strike": 23000.0,
        "tradingsymbol": "NIFTYTEST",
    }


class BaselineCaptureOfflineTests(unittest.TestCase):
    def make_kite(self):
        kite = MagicMock()
        kite.instruments.return_value = [fake_instrument()]
        kite.ltp.return_value = {"NSE:NIFTY 50": {"last_price": 23000.0}}
        kite.quote.return_value = {
            "NFO:NIFTYTEST": {
                "last_price": 100.0,
                "ohlc": {"close": 98.0},
            }
        }
        return kite

    def test_capture_start_outside_window_skips_api(self):
        kite = self.make_kite()
        outside = datetime(2026, 10, 9, 9, 17, 0, tzinfo=IST)

        with patch(
            "modules.nifty_option_v21_2_18_baseline.datetime"
        ) as mocked_datetime:
            mocked_datetime.now.return_value = outside
            result = capture_915_baseline(kite)

        self.assertEqual(result["Status"], "BASELINE_CAPTURE_OUTSIDE_WINDOW")
        kite.instruments.assert_not_called()
        kite.quote.assert_not_called()
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])

    def test_quote_completion_after_window_is_rejected(self):
        kite = self.make_kite()
        start = datetime(2026, 10, 9, 9, 15, 0, tzinfo=IST)
        finish = datetime(2026, 10, 9, 9, 16, 1, tzinfo=IST)

        with patch(
            "modules.nifty_option_v21_2_18_baseline.datetime"
        ) as mocked_datetime:
            mocked_datetime.now.side_effect = [start, start, finish]
            result = capture_915_baseline(kite)

        self.assertEqual(result["Status"], "BASELINE_CAPTURE_OUTSIDE_WINDOW")
        self.assertEqual(kite.quote.call_count, 1)
        self.assertNotIn("Baseline", result)
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])

    def test_capture_finishing_inside_window_is_accepted(self):
        kite = self.make_kite()
        start = datetime(2026, 10, 9, 9, 15, 0, tzinfo=IST)
        finish = datetime(2026, 10, 9, 9, 15, 20, tzinfo=IST)

        with patch(
            "modules.nifty_option_v21_2_18_baseline.datetime"
        ) as mocked_datetime:
            mocked_datetime.now.side_effect = [start, start, finish]
            result = capture_915_baseline(kite, strikes_each_side=0)

        self.assertEqual(result["Status"], "BASELINE_CAPTURE_COMPLETE")
        self.assertEqual(result["Captured At"], finish.isoformat(timespec="seconds"))
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

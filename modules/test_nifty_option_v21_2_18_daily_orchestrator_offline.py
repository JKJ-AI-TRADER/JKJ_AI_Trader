"""Offline safety tests for the V21.2.18 daily orchestrator."""

import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from modules import nifty_option_v21_2_18_daily_orchestrator as orchestrator

IST = ZoneInfo("Asia/Kolkata")


class DailyOrchestratorOfflineTests(unittest.TestCase):
    def setUp(self):
        self.patches = [
            patch.object(
                orchestrator, "get_market_session_state",
                return_value={"Session State": "PRE_MARKET"},
            ),
            patch.object(
                orchestrator, "evaluate_pre_market_controller",
                return_value={"Status": "PRE_MARKET_READY"},
            ),
            patch.object(orchestrator, "load_today_baseline", return_value=None),
            patch.object(
                orchestrator, "_get_kite",
                return_value={"Status": "SESSION_NOT_READY",
                              "Reason": "Mocked offline session"},
            ),
            patch.object(
                orchestrator, "capture_915_baseline",
                return_value={"Status": "BASELINE_CAPTURE_FAILED"},
            ),
            patch.object(
                orchestrator, "save_baseline",
                return_value={"Status": "BASELINE_NOT_SAVED"},
            ),
            patch.object(orchestrator, "run_early_surge_session"),
        ]
        self.mocks = [item.start() for item in self.patches]
        self.addCleanup(self._stop_patches)

    def _stop_patches(self):
        for item in reversed(self.patches):
            item.stop()

    def test_capture_window_does_not_start_premarket_preparation(self):
        now = datetime(2026, 10, 9, 9, 14, 45, tzinfo=IST)
        result = orchestrator.run_v21_2_18_daily_orchestrator(
            current_time=now
        )
        self.assertFalse(self.mocks[1].called)
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])

    def test_capture_failure_never_starts_observation(self):
        now = datetime(2026, 10, 9, 9, 14, 45, tzinfo=IST)
        result = orchestrator.run_v21_2_18_daily_orchestrator(
            current_time=now
        )
        self.mocks[6].assert_not_called()
        self.assertNotEqual(
            result["Status"], "V21_2_18_ORCHESTRATION_COMPLETE"
        )
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])

    def test_baseline_missing_outside_window_never_captures(self):
        now = datetime(2026, 10, 9, 10, 0, tzinfo=IST)
        self.mocks[0].return_value = {"Session State": "MARKET_SESSION"}
        result = orchestrator.run_v21_2_18_daily_orchestrator(
            current_time=now
        )
        self.mocks[4].assert_not_called()
        self.mocks[5].assert_not_called()
        self.mocks[6].assert_not_called()
        self.assertEqual(result["Status"], "BASELINE_REQUIRED")
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

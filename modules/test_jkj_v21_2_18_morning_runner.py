"""Offline tests for the JKJ V21.2.18 morning runner."""

import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from modules import jkj_v21_2_18_morning_runner as runner


IST = ZoneInfo("Asia/Kolkata")


class MorningRunnerTests(unittest.TestCase):
    def test_timing_boundaries(self):
        cases = [
            ("08:59:59", "WAIT_FOR_PREMARKET", False),
            ("09:00:00", "PREPARE_THEN_WAIT", False),
            ("09:14:29", "PREPARE_THEN_WAIT", False),
            ("09:14:30", "RUN_ONCE", False),
            ("09:16:00", "RUN_ONCE", False),
            ("09:16:01", "LATE_START_NO_BASELINE", False),
            ("09:16:01", "LATE_START_WITH_BASELINE", True),
        ]
        for clock, expected, baseline in cases:
            with self.subTest(clock=clock, baseline=baseline):
                now = datetime.fromisoformat(
                    f"2026-10-09T{clock}+05:30"
                )
                self.assertEqual(
                    runner.get_runner_action(now, baseline),
                    expected,
                )

    def test_market_closed_never_calls_orchestrator(self):
        closed_time = datetime(
            2026, 10, 9, 15, 30, tzinfo=IST
        )
        with (
            patch.object(runner, "datetime") as mock_datetime,
            patch.object(
                runner, "validate_stored_baseline",
                return_value=(True, "Mock valid baseline"),
            ),
            patch.object(
                runner, "get_runner_action",
                return_value="LATE_START_WITH_BASELINE",
            ),
            patch.object(
                runner, "run_v21_2_18_daily_orchestrator"
            ) as mock_orchestrator,
        ):
            mock_datetime.now.return_value = closed_time
            result = runner.run_morning_runner()

        self.assertEqual(result["Status"], "MARKET_CLOSED")
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])
        mock_orchestrator.assert_not_called()

    def test_missing_baseline_skips_observation(self):
        late_time = datetime(2026, 10, 9, 10, 0, tzinfo=IST)
        with (
            patch.object(runner, "datetime") as mock_datetime,
            patch.object(
                runner, "validate_stored_baseline",
                return_value=(False, "Baseline file does not exist."),
            ),
            patch.object(
                runner, "get_runner_action",
                return_value="LATE_START_NO_BASELINE",
            ),
            patch.object(
                runner, "run_v21_2_18_daily_orchestrator"
            ) as mock_orchestrator,
        ):
            mock_datetime.now.return_value = late_time
            result = runner.run_morning_runner()

        self.assertEqual(
            result["Status"], "BASELINE_MISSED_LATE_START"
        )
        self.assertTrue(result["Dependent_Observation_Skipped"])
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])
        mock_orchestrator.assert_not_called()

    def test_orchestrator_outcome_is_preserved(self):
        market_time = datetime(2026, 10, 9, 10, 0, tzinfo=IST)
        with (
            patch.object(runner, "datetime") as mock_datetime,
            patch.object(
                runner, "validate_stored_baseline",
                return_value=(True, "Mock valid baseline"),
            ),
            patch.object(
                runner, "get_runner_action",
                return_value="LATE_START_WITH_BASELINE",
            ),
            patch.object(
                runner, "run_v21_2_18_daily_orchestrator",
                return_value={
                    "Status": "BASELINE_REQUIRED",
                    "Live Order": False,
                    "Paper Trade": False,
                },
            ) as mock_orchestrator,
        ):
            mock_datetime.now.return_value = market_time
            result = runner.run_morning_runner()

        self.assertEqual(
            result["Status"], "LATE_START_OBSERVATION_ATTEMPTED"
        )
        self.assertEqual(
            result["Orchestrator_Status"], "BASELINE_REQUIRED"
        )
        self.assertFalse(result["Live Order"])
        self.assertFalse(result["Paper Trade"])
        mock_orchestrator.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)

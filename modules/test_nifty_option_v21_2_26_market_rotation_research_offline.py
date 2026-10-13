import math
import unittest

from modules.nifty_option_v21_2_26_market_rotation_research import (
    _safe_float,
    analyze_market_rotation,
)


def candidate(symbol, option_type, movement, acceleration=0.0):
    return {
        "Trading Symbol": symbol,
        "Option Type": option_type,
        "Expiry": "2026-10-29",
        "Strike": 23000,
        "Movement %": movement,
        "Acceleration": acceleration,
    }


def result_for(candidates):
    return {
        "Status": "ONE_HOUR_OBSERVATION_COMPLETE",
        "Observation History": [
            {
                "Timestamp": "2026-10-13T10:00:00+05:30",
                "Elapsed Minutes": 0.0,
                "NIFTY Spot": 23000.0,
                "NIFTY Movement %": 0.1,
                "Candidates": candidates,
            }
        ],
    }
class TestMarketRotationOffline(unittest.TestCase):

    def test_safe_float_rejects_boolean_and_non_finite_values(self):
        values = [
            True,
            False,
            math.nan,
            math.inf,
            -math.inf,
            "nan",
            "inf",
            "-inf",
        ]

        for value in values:
            with self.subTest(value=repr(value)):
                self.assertIsNone(_safe_float(value))

    def test_safe_float_accepts_finite_values(self):
        self.assertEqual(_safe_float(4), 4.0)
        self.assertEqual(_safe_float(4.25), 4.25)
        self.assertEqual(_safe_float("4.25"), 4.25)

    def test_invalid_movement_and_acceleration_do_not_inflate_metrics(self):
        candidates = [
            candidate("CE_VALID", "CE", 5.0, 1.0),
            candidate("CE_BAD_ACCEL", "CE", 3.0, math.inf),
            candidate("CE_BOOL", "CE", True, 9.0),
            candidate("CE_NAN", "CE", math.nan, 9.0),
            candidate("CE_INF", "CE", math.inf, 9.0),
            candidate("PE_VALID", "PE", 2.0, 0.0),
        ]

        result = analyze_market_rotation(result_for(candidates))
        timeline = result["Timeline"]
        ce = timeline[0]["CE"]
        pe = timeline[0]["PE"]

        self.assertEqual(ce["Candidate Count"], 2)
        self.assertEqual(ce["Positive Count"], 2)
        self.assertEqual(ce["Accelerating Count"], 1)
        self.assertAlmostEqual(ce["Average Movement %"], 4.0)

        strongest = ce["Strongest Acceleration Candidate"]
        self.assertEqual(strongest["Trading Symbol"], "CE_VALID")

        self.assertEqual(pe["Candidate Count"], 1)
        self.assertEqual(pe["Positive Count"], 1)



    def test_invalid_observations_keep_trading_disabled(self):
        candidates = [
            candidate("CE_NAN", "CE", math.nan, 1.0),
            candidate("PE_INF", "PE", math.inf, 1.0),
        ]

        result = analyze_market_rotation(result_for(candidates))

        self.assertEqual(result["Observation Count"], 1)

        timeline = result["Timeline"]
        self.assertEqual(timeline[0]["CE"]["Candidate Count"], 0)
        self.assertEqual(timeline[0]["PE"]["Candidate Count"], 0)

        for flag in (
            "Trading Decision",
            "Live Order",
            "Paper Trade",
            "BUY",
            "SELL",
        ):
            self.assertFalse(result[flag], flag)

    def test_all_error_responses_keep_trading_flags_disabled(self):
        cases = [
            (
                None,
                "INVALID_OBSERVATION_RESULT",
            ),
            (
                {"Status": "WRONG_STATUS"},
                "INVALID_OBSERVATION_STATUS",
            ),
            (
                {
                    "Status": "ONE_HOUR_OBSERVATION_COMPLETE",
                    "Observation History": "invalid",
                },
                "INVALID_OBSERVATION_HISTORY",
            ),
        ]

        flags = (
            "Trading Decision",
            "Live Order",
            "Paper Trade",
            "BUY",
            "SELL",
        )

        for observation, expected_status in cases:
            with self.subTest(status=expected_status):
                result = analyze_market_rotation(observation)

                self.assertEqual(result["Status"], expected_status)

                for flag in flags:
                    self.assertIs(result.get(flag), False, flag)

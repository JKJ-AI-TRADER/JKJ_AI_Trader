import math
import unittest

from modules.nifty_option_v21_2_24_2_movement_analyzer import (
    _safe_float,
    _analyze_candidate,
    analyze_one_hour_observation,
)


class TestMovementAnalyzerOffline(unittest.TestCase):
    def test_safe_float_rejects_boolean_and_non_finite_values(self):
        for value in (True, False, math.nan, math.inf, -math.inf, "nan", "inf", "-inf"):
            with self.subTest(value=repr(value)):
                self.assertIsNone(_safe_float(value))

    def test_safe_float_accepts_finite_values(self):
        self.assertEqual(_safe_float(4), 4.0)
        self.assertEqual(_safe_float(4.25), 4.25)
        self.assertEqual(_safe_float("4.25"), 4.25)

    def test_analyzer_reads_observer_current_price_field(self):
        result = analyze_one_hour_observation({
            "Status": "ONE_HOUR_OBSERVATION_COMPLETE",
            "Duration Minutes": 60,
            "Interval Seconds": 60,
            "Observation History": [
                {"Candidates": [{
                    "Trading Symbol": "TESTCE",
                    "Movement %": 2.0,
                    "Elapsed Minutes": 0.0,
                    "Timestamp": "2026-10-13T10:00:00+05:30",
                    "Current Price": 100.0,
                    "NIFTY Movement %": 0.1,
                }]},
                {"Candidates": [{
                    "Trading Symbol": "TESTCE",
                    "Movement %": 5.0,
                    "Elapsed Minutes": 1.0,
                    "Timestamp": "2026-10-13T10:01:00+05:30",
                    "Current Price": 105.0,
                    "NIFTY Movement %": 0.2,
                }]},
                {"Candidates": [{
                    "Trading Symbol": "TESTCE",
                    "Movement %": 3.0,
                    "Elapsed Minutes": 2.0,
                    "Timestamp": "2026-10-13T10:02:00+05:30",
                    "Current Price": 103.0,
                    "NIFTY Movement %": 0.15,
                }]},
            ],
        })
        candidate = result["Candidates"][0]
        self.assertEqual(candidate["Peak Price"], 105.0)
        self.assertEqual(candidate["Final Price"], 103.0)
        self.assertIs(result["Trading Decision"], False)
        self.assertIs(result["Live Order"], False)
        self.assertIs(result["Paper Trade"], False)

    def test_invalid_movements_do_not_distort_analysis(self):
        observations = [
            {"Movement %": 2.0, "Elapsed Minutes": 0, "Timestamp": "t0", "Latest Price": 100.0},
            {"Movement %": True, "Elapsed Minutes": 1},
            {"Movement %": math.nan, "Elapsed Minutes": 2},
            {"Movement %": math.inf, "Elapsed Minutes": 3},
            {"Movement %": -math.inf, "Elapsed Minutes": 4},
            {"Movement %": 4.0, "Elapsed Minutes": 5, "Timestamp": "t5", "Latest Price": 104.0},
        ]
        result = _analyze_candidate("TESTCE", observations)

        self.assertEqual(result["Observation Count"], 2)
        self.assertEqual(result["Peak Movement %"], 4.0)
        self.assertEqual(result["Final Movement %"], 4.0)
        self.assertEqual(result["Outcome Classification"], "SUSTAINED")
        self.assertIs(result["Live Order"], False)
        self.assertIs(result["Paper Trade"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)

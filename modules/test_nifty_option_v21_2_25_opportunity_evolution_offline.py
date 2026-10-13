import math
import unittest

from modules.nifty_option_v21_2_25_opportunity_evolution import (
    _safe_float,
    analyze_opportunity_evolution,
)


def make_candidate(movement, elapsed):
    return {
        "Trading Symbol": "TESTCE",
        "Option Type": "CE",
        "Expiry": "2026-10-29",
        "Strike": 23000,
        "Timestamp": "2026-10-13T10:00:00+05:30",
        "Elapsed Minutes": elapsed,
        "Movement %": movement,
        "Initial Price": 100.0,
        "Current Price": 100.0,
        "NIFTY Movement %": 0.1,
    }


def make_result(movements):
    return {
        "Status": "ONE_HOUR_OBSERVATION_COMPLETE",
        "Observation History": [
            {
                "Timestamp": "2026-10-13T10:00:00+05:30",
                "Elapsed Minutes": index,
                "Candidates": [make_candidate(value, index)],
            }
            for index, value in enumerate(movements)
        ],
        "Trading Decision": False,
        "Live Order": False,
        "Paper Trade": False,
    }


class TestOpportunityEvolutionOffline(unittest.TestCase):
    def test_safe_float_rejects_boolean_and_non_finite_values(self):
        for value in (
            True, False, math.nan, math.inf, -math.inf,
            "nan", "inf", "-inf",
        ):
            with self.subTest(value=repr(value)):
                self.assertIsNone(_safe_float(value))

    def test_safe_float_accepts_finite_values(self):
        self.assertEqual(_safe_float(4), 4.0)
        self.assertEqual(_safe_float(4.25), 4.25)
        self.assertEqual(_safe_float("4.25"), 4.25)

    def test_invalid_movements_do_not_distort_candidate_analysis(self):
        result = analyze_opportunity_evolution(
            make_result([2.0, math.nan, math.inf, -math.inf, True, 5.0])
        )
        self.assertEqual(result["Candidate Count"], 1)
        candidate = result["Candidates"][0]
        self.assertEqual(candidate["Observation Count"], 2)
        self.assertEqual(candidate["Peak Movement %"], 5.0)
        self.assertEqual(candidate["Final Movement %"], 5.0)
        self.assertIs(
            result["Trading Decision"],
            False,
        )
        self.assertIs(result["Live Order"], False)
        self.assertIs(result["Paper Trade"], False)

    def test_all_invalid_movements_create_no_candidates(self):
        result = analyze_opportunity_evolution(
            make_result([True, math.nan, math.inf, -math.inf])
        )
        self.assertEqual(result["Candidate Count"], 0)
        self.assertEqual(result["Candidates"], [])
        self.assertIs(result["Trading Decision"], False)
        self.assertIs(result["Live Order"], False)
        self.assertIs(result["Paper Trade"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)

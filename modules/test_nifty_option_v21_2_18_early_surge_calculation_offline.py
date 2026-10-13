import unittest

from modules.nifty_option_v21_2_18_early_surge_scanner import (
    _evaluate_candidate,
)


class TestEarlySurgeMovementOffline(unittest.TestCase):
    def make_candidate(self, baseline_price=2.85):
        return {
            "Initial Price": 4.65,
            "Previous Close": 10.0,
            "Daily Change %": -53.5,
            "9:15 Price": baseline_price,
            "Movement Since 9:15 %": 19.35,
            "9:15 Movement Level": "MAJOR",
            "Latest Price": 4.65,
            "Window Change %": 0.0,
            "Acceleration %": 0.0,
        }

    def test_movement_uses_genuine_baseline_and_latest_price(self):
        candidate = self.make_candidate()
        result = _evaluate_candidate(candidate, 5.60)

        self.assertEqual(result["Movement Since 9:15 %"], 96.49)
        self.assertEqual(result["Latest Price"], 5.60)
        self.assertEqual(result["9:15 Price"], 2.85)
        self.assertEqual(result["9:15 Movement Level"], "SURGE")

    def test_movement_refreshes_on_each_observation(self):
        first = _evaluate_candidate(self.make_candidate(), 5.60)
        second = _evaluate_candidate(dict(first), 6.00)

        self.assertEqual(first["Movement Since 9:15 %"], 96.49)
        self.assertEqual(second["Movement Since 9:15 %"], 110.53)
        self.assertEqual(second["9:15 Price"], 2.85)

    def test_missing_baseline_remains_unavailable(self):
        result = _evaluate_candidate(self.make_candidate(None), 5.60)

        self.assertIsNone(result["Movement Since 9:15 %"])
        self.assertEqual(
            result["9:15 Movement Level"],
            "BASELINE_UNAVAILABLE",
        )


if __name__ == "__main__":
    unittest.main()

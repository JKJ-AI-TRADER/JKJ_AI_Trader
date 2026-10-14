"""Offline safety tests for position slicing input validation."""

import unittest

from modules.intraday_position_slicing import calculate_slice_plan


def plan(**overrides):
    values = {
        "total_quantity": 300,
        "current_quantity": 300,
        "entry_price": 100.0,
        "current_price": 108.0,
        "peak_price": 110.0,
        "exit_signal": "WATCH — DETERIORATION WATCH",
        "momentum_status": "WEAK",
        "volume_status": "DECREASING",
        "underlying_status": "SUPPORTIVE",
        "structure_status": "STABLE",
    }
    values.update(overrides)
    return calculate_slice_plan(**values)


class PositionSlicingSafetyTests(unittest.TestCase):
    def test_invalid_quantities_are_rejected(self):
        invalid_values = (
            float("nan"), float("inf"), float("-inf"),
            True, False, 300.5, "300.5", "nan", "inf",
            10**1000,
        )
        for field in ("total_quantity", "current_quantity"):
            for value in invalid_values:
                with self.subTest(field=field, value_type=type(value).__name__):
                    result = plan(**{field: value})
                    self.assertEqual(result["Position Status"], "NO ACTION")
                    self.assertEqual(result["Exit Quantity"], 0)

    def test_invalid_prices_are_rejected(self):
        invalid_values = (
            float("nan"), float("inf"), float("-inf"),
            True, False, "nan", "inf", 10**1000,
        )
        for field in ("entry_price", "current_price", "peak_price"):
            for value in invalid_values:
                with self.subTest(field=field, value_type=type(value).__name__):
                    result = plan(**{field: value})
                    self.assertEqual(result["Position Status"], "NO ACTION")
                    self.assertEqual(result["Exit Quantity"], 0)

    def test_valid_partial_exit_rule_is_preserved(self):
        result = plan()
        self.assertEqual(result["Position Status"], "PARTIAL EXIT")
        # Weak momentum + decreasing volume gives weakness score 3,
        # so the existing rule selects a 33% slice.
        self.assertEqual(result["Weakness Score"], 3)
        self.assertEqual(result["Slice Percentage"], 33)
        self.assertEqual(result["Exit Quantity"], 99)
        self.assertEqual(result["Remaining Quantity"], 201)

    def test_stop_loss_still_requests_full_exit(self):
        result = plan(
            current_price=97.0,
            peak_price=101.0,
            exit_signal="EXIT — STOP LOSS",
        )
        self.assertEqual(result["Position Status"], "FULL EXIT")
        self.assertEqual(result["Exit Quantity"], 300)
        self.assertEqual(result["Remaining Quantity"], 0)

    def test_zero_quantity_is_still_no_action(self):
        result = plan(current_quantity=0)
        self.assertEqual(result["Position Status"], "NO ACTION")
        self.assertEqual(result["Exit Quantity"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

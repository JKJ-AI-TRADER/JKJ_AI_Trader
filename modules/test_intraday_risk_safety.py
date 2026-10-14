"""Offline safety tests for the intraday risk engine."""

import unittest

from modules.intraday_risk_engine import analyse_intraday_risk


def assess(**overrides):
    values = {
        "entry_price": 1000.0,
        "stop_loss": 990.0,
        "target_price": 1020.0,
        "setup_score": 80,
        "trading_allowed": True,
    }
    values.update(overrides)
    return analyse_intraday_risk(**values)


class IntradayRiskSafetyTests(unittest.TestCase):
    def test_valid_trade_is_accepted(self):
        result = assess()
        self.assertIs(result["Trade Allowed"], True)
        self.assertEqual(result["Risk Percentage"], 1.0)
        self.assertEqual(result["Risk Reward Ratio"], 2.0)

    def test_true_risk_above_two_percent_is_rejected_even_if_display_rounds_to_two(self):
        result = assess(
            entry_price=1000.0,
            stop_loss=979.96,
            target_price=1060.12,
        )
        self.assertEqual(result["Risk Percentage"], 2.0)
        self.assertEqual(result["Risk Level"], "HIGH")
        self.assertIs(result["Trade Allowed"], False)

    def test_true_reward_risk_below_one_point_five_is_rejected_even_if_display_rounds_to_one_point_five(self):
        result = assess(
            entry_price=1000.0,
            stop_loss=990.0,
            target_price=1014.99,
        )
        self.assertEqual(result["Risk Reward Ratio"], 1.5)
        self.assertIs(result["Trade Allowed"], False)

    def test_nonfinite_boolean_and_non_numeric_inputs_are_rejected(self):
        invalid_values = (
            float("nan"),
            float("inf"),
            float("-inf"),
            True,
            False,
            "1000",
            None,
        )
        fields = (
            "entry_price",
            "stop_loss",
            "target_price",
            "setup_score",
        )
        for field in fields:
            for invalid in invalid_values:
                with self.subTest(field=field, value=repr(invalid)):
                    result = assess(**{field: invalid})
                    self.assertIs(result["Trade Allowed"], False)
                    self.assertEqual(result["Risk Status"], "INVALID INPUT")

    def test_non_boolean_market_permission_is_rejected(self):
        result = assess(trading_allowed=1)
        self.assertIs(result["Trade Allowed"], False)
        self.assertEqual(result["Risk Status"], "INVALID INPUT")

    def test_disallowed_market_still_blocks_trade(self):
        result = assess(trading_allowed=False)
        self.assertIs(result["Trade Allowed"], False)
        self.assertEqual(result["Risk Status"], "MARKET NOT SUITABLE")

    def test_zero_or_negative_stop_is_rejected(self):
        for stop in (0, -1):
            with self.subTest(stop=stop):
                result = assess(stop_loss=stop)
                self.assertIs(result["Trade Allowed"], False)
                self.assertEqual(result["Risk Status"], "INVALID STOP LOSS")


if __name__ == "__main__":
    unittest.main(verbosity=2)

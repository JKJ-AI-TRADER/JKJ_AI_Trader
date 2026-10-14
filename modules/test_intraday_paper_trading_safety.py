"""Offline safety tests for paper-position price updates and exits."""

import copy
import unittest

from modules.intraday_paper_trading import (
    open_paper_trade,
    update_paper_price,
    process_paper_exit,
)


def make_open_trade():
    trade = open_paper_trade(
        trade_id="OFFLINE-SAFETY-001",
        symbol="NIFTY-TEST",
        instrument_type="options",
        entry_price=100.0,
        quantity=10,
        stop_loss=95.0,
        target=110.0,
    )
    if not isinstance(trade, dict) or trade.get("Status") != "OPEN":
        raise AssertionError(f"Could not create offline test trade: {trade}")
    return trade


class PaperTradingPriceSafetyTests(unittest.TestCase):
    def test_invalid_prices_do_not_mutate_update_paper_price(self):
        invalid_prices = (
            float("nan"),
            float("inf"),
            float("-inf"),
            True,
            False,
            "nan",
            "inf",
        )
        for price in invalid_prices:
            with self.subTest(price=repr(price)):
                trade = make_open_trade()
                before = copy.deepcopy(trade)
                result = update_paper_price(trade, price)
                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(trade, before)

    def test_invalid_prices_do_not_mutate_process_paper_exit(self):
        invalid_prices = (
            float("nan"),
            float("inf"),
            float("-inf"),
            True,
            False,
            "nan",
            "inf",
        )
        for price in invalid_prices:
            with self.subTest(price=repr(price)):
                trade = make_open_trade()
                before = copy.deepcopy(trade)
                result = process_paper_exit(
                    trade=trade,
                    current_price=price,
                    exit_signal="SAFETY_TEST",
                )
                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(trade, before)

    def test_rejected_sell_does_not_mutate_trade_record(self):
        invalid_cases = (
            {"gross_pnl": 999.0},
            {"costs": -1.0},
            {"slippage": float("nan")},
        )
        for extra in invalid_cases:
            with self.subTest(extra=extra):
                trade = make_open_trade()
                before = copy.deepcopy(trade)

                result = process_paper_exit(
                    trade=trade,
                    current_price=110.0,
                    exit_signal="EXIT — STOP LOSS",
                    **extra,
                )

                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(trade, before)

    def test_valid_price_update_still_works(self):
        trade = make_open_trade()
        result = update_paper_price(trade, 101.25)
        self.assertEqual(result["Status"], "UPDATED")
        self.assertEqual(trade["Current Price"], 101.25)


if __name__ == "__main__":
    unittest.main(verbosity=2)

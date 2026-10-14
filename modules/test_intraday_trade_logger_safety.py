"""Offline safety regression tests for the paper-trade logger."""

import unittest

from modules.intraday_trade_logger import (
    create_trade_record,
    record_sell_event,
    update_peak_price,
)


def make_trade(quantity=5):
    return create_trade_record(
        trade_id="SAFETY-TEST-001",
        symbol="NIFTYTEST",
        instrument_type="options",
        entry_price=100.0,
        quantity=quantity,
        stop_loss=95.0,
        target=120.0,
    )


class TradeLoggerSafetyTests(unittest.TestCase):
    def test_fractional_open_quantity_is_rejected(self):
        result = make_trade(quantity=1.5)
        self.assertEqual(result["Status"], "ERROR")

    def test_boolean_entry_price_is_rejected(self):
        for entry_price in (True, False):
            with self.subTest(entry_price=entry_price):
                result = create_trade_record(
                    trade_id="BOOLEAN-ENTRY",
                    symbol="NIFTYTEST",
                    instrument_type="options",
                    entry_price=entry_price,
                    quantity=1,
                )
                self.assertEqual(result["Status"], "ERROR")

    def test_boolean_sell_financial_values_are_rejected(self):
        cases = (
            ("price", True, 101.0, 1.0),
            ("gross_pnl", True, 101.0, 1.0),
            ("costs", True, 101.0, 1.0),
            ("slippage", True, 101.0, 1.0),
            ("trade_entry_price", True, 2.0, 1.0),
        )
        for field, bad_value, price, gross_pnl in cases:
            with self.subTest(field=field):
                trade = make_trade()
                kwargs = {
                    "price": price,
                    "quantity": 1,
                    "gross_pnl": gross_pnl,
                    "costs": 0.0,
                    "slippage": 0.0,
                }
                if field == "trade_entry_price":
                    trade["Entry Price"] = bad_value
                else:
                    kwargs[field] = bad_value

                result = record_sell_event(trade, **kwargs)
                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(trade["Current Quantity"], 5)
                self.assertEqual(trade["Exit Events"], [])

    def test_sell_requires_open_trade_status(self):
        trade = make_trade()
        trade["Status"] = "CLOSED"
        before_quantity = trade["Current Quantity"]
        before_events = list(trade["Exit Events"])

        result = record_sell_event(
            trade, price=110, quantity=1, gross_pnl=10
        )

        self.assertEqual(result["Status"], "ERROR")
        self.assertEqual(trade["Current Quantity"], before_quantity)
        self.assertEqual(trade["Exit Events"], before_events)

    def test_fractional_sell_quantity_is_rejected_without_mutation(self):
        for quantity in (1.5, True, float("nan")):
            with self.subTest(quantity=quantity):
                trade = make_trade()
                before_quantity = trade["Current Quantity"]
                before_events = list(trade["Exit Events"])

                result = record_sell_event(
                    trade,
                    price=110,
                    quantity=quantity,
                    gross_pnl=10,
                )

                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(
                    trade["Current Quantity"], before_quantity
                )
                self.assertEqual(trade["Exit Events"], before_events)

    def test_inconsistent_gross_pnl_is_rejected(self):
        trade = make_trade()
        before_quantity = trade["Current Quantity"]

        result = record_sell_event(
            trade, price=110, quantity=2, gross_pnl=999
        )

        self.assertEqual(result["Status"], "ERROR")
        self.assertEqual(trade["Current Quantity"], before_quantity)
        self.assertEqual(trade["Exit Events"], [])

    def test_negative_costs_or_slippage_are_rejected(self):
        for field, value in (("costs", -1), ("slippage", -1)):
            with self.subTest(field=field):
                trade = make_trade()
                kwargs = {field: value}

                result = record_sell_event(
                    trade,
                    price=110,
                    quantity=1,
                    gross_pnl=10,
                    **kwargs,
                )

                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(trade["Current Quantity"], 5)
                self.assertEqual(trade["Exit Events"], [])

    def test_non_finite_financial_values_are_rejected(self):
        cases = (
            {"price": float("nan"), "quantity": 1, "gross_pnl": 10},
            {"price": 110, "quantity": 1, "gross_pnl": float("inf")},
            {"price": 110, "quantity": 1, "gross_pnl": 10,
             "costs": float("nan")},
            {"price": 110, "quantity": 1, "gross_pnl": 10,
             "slippage": float("inf")},
        )

        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                trade = make_trade()
                result = record_sell_event(trade, **kwargs)

                self.assertEqual(result["Status"], "ERROR")
                self.assertEqual(trade["Current Quantity"], 5)
                self.assertEqual(trade["Exit Events"], [])

    def test_peak_price_rejects_boolean_infinity_and_overflow(self):
        invalid_prices = (True, float("inf"), 10**1000)
        for price in invalid_prices:
            with self.subTest(price_type=type(price).__name__):
                trade = make_trade()
                # Make an attempted conversion of True into 1.0 observable.
                trade["Peak Price"] = 0.5
                trade["Peak Profit %"] = -50.0
                before = __import__("copy").deepcopy(trade)

                update_peak_price(trade, price)

                self.assertEqual(trade, before)

    def test_valid_partial_sell_updates_pnl_and_quantity(self):
        trade = make_trade()

        result = record_sell_event(
            trade,
            price=110,
            quantity=2,
            gross_pnl=20,
            costs=1,
            slippage=0.5,
        )

        self.assertEqual(result["Status"], "RECORDED")
        self.assertEqual(trade["Current Quantity"], 3)
        self.assertEqual(trade["Status"], "OPEN")
        self.assertEqual(trade["Gross P&L"], 20.0)
        self.assertEqual(trade["Trading Costs"], 1.0)
        self.assertEqual(trade["Slippage"], 0.5)
        self.assertEqual(trade["Net P&L"], 18.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)

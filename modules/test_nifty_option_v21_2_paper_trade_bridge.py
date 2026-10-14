"""Offline safety tests for the V21.2-to-paper-trade bridge."""

import unittest
from unittest.mock import patch

from modules import nifty_option_v21_2_paper_trade_bridge as bridge


def valid_risk_result():
    return {
        "Status": "RISK_STOP_TARGETS_COMPLETE",
        "Live Order": False,
        "Paper Trade": False,
        "Trading Symbol": "NIFTYTEST",
        "Underlying": "NIFTY",
        "Expiry": "2026-10-13",
        "Strike": 23000,
        "Option Type": "CE",
        "Entry Price": 100.0,
        "Stop Price": 95.0,
        "Target 1": 110.0,
        "Target 2": 115.0,
        "Target 3": 120.0,
        "Risk Reward 1": 2.0,
        "Risk Reward 2": 3.0,
        "Risk Reward 3": 4.0,
        "Entry Qualification": "QUALIFIED",
        "Entry Risk Context": "VALID",
        "Stop-Loss Context": "SUPPORTED",
        "Exit Structure": "VALID",
    }


class PaperTradeBridgeSafetyTests(unittest.TestCase):
    def test_unsafe_or_incomplete_inputs_never_reach_coordinator(self):
        cases = []

        result = valid_risk_result()
        result["Status"] = "INCOMPLETE"
        cases.append(("incomplete status", result, "TEST-001", 5))

        result = valid_risk_result()
        result["Live Order"] = True
        cases.append(("live order enabled", result, "TEST-001", 5))

        result = valid_risk_result()
        result["Paper Trade"] = True
        cases.append(("paper trade flag already enabled", result, "TEST-001", 5))

        result = valid_risk_result()
        del result["Trading Symbol"]
        cases.append(("missing contract field", result, "TEST-001", 5))

        cases.append(("missing trade ID", valid_risk_result(), "", 5))
        cases.append(("zero quantity", valid_risk_result(), "TEST-001", 0))
        cases.append(("negative quantity", valid_risk_result(), "TEST-001", -1))

        for name, result, trade_id, quantity in cases:
            with self.subTest(case=name):
                with patch.object(
                    bridge, "create_qualified_paper_trade"
                ) as coordinator:
                    outcome = bridge.create_v21_2_paper_trade(
                        result,
                        trade_id=trade_id,
                        quantity=quantity,
                    )

                self.assertEqual(
                    outcome["Status"], "PAPER_TRADE_BRIDGE_REJECTED"
                )
                self.assertFalse(outcome["Live Order"])
                self.assertFalse(outcome["Broker Communication"])
                self.assertFalse(outcome["Order Placement Permitted"])
                coordinator.assert_not_called()

    def test_fractional_or_boolean_quantity_is_rejected(self):
        for quantity in (1.5, True, float("nan")):
            with self.subTest(quantity=quantity):
                with patch.object(
                    bridge, "create_qualified_paper_trade"
                ) as coordinator:
                    outcome = bridge.create_v21_2_paper_trade(
                        valid_risk_result(),
                        trade_id="TEST-001",
                        quantity=quantity,
                    )

                self.assertEqual(
                    outcome["Status"], "PAPER_TRADE_BRIDGE_REJECTED"
                )
                coordinator.assert_not_called()

    def test_valid_input_hands_off_only_to_mocked_coordinator(self):
        mocked_result = {
            "Status": "PAPER_TRADE_OPENED",
            "Trade": {"Trade ID": "TEST-001", "Status": "OPEN"},
        }

        with patch.object(
            bridge,
            "create_qualified_paper_trade",
            return_value=mocked_result,
        ) as coordinator:
            outcome = bridge.create_v21_2_paper_trade(
                valid_risk_result(),
                trade_id="TEST-001",
                quantity=5,
                entry_time="2026-10-12 10:00:00",
            )

        self.assertEqual(outcome["Status"], "V21_2_PAPER_TRADE_OPENED")
        self.assertTrue(outcome["Paper Execution"])
        self.assertFalse(outcome["Live Order"])
        self.assertFalse(outcome["Broker Communication"])
        self.assertFalse(outcome["Order Placement Permitted"])
        coordinator.assert_called_once()

        passed = coordinator.call_args.kwargs
        self.assertEqual(passed["quantity"], 5)
        self.assertEqual(passed["trade_id"], "TEST-001")


if __name__ == "__main__":
    unittest.main(verbosity=2)

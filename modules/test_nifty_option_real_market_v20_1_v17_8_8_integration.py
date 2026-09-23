"""
JKJ AI Trader
V20.1 -> V17.8.8 Real-Market Lifecycle Boundary Integration Test

Real-market integration chain:

V20.1
    -> V17.6
    -> V17.7
    -> V17.8.1
    -> V17.8.2
    -> V17.8.5
    -> V17.8.6
    -> V17.8.7
    -> V17.8.8

V17.8.8 remains validation-only.

No lifecycle action.
No exit processing.
No position closure.
No live Zerodha order.
No broker communication.
No automatic ranking.
No capital reassignment.
No main.py modification.

Wisdom Before Wealth.
"""

from nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)

from nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
)

from nifty_option_v20_1_v17_8_integration import (
    integrate_v20_1_to_v17_8,
)

from nifty_option_v20_1_v17_8_2_integration import (
    integrate_v20_1_to_v17_8_2,
)

from nifty_option_v20_1_v17_8_5_integration import (
    integrate_v20_1_to_v17_8_5,
)

from nifty_option_v20_1_v17_8_6_integration import (
    integrate_v20_1_to_v17_8_6,
)

from nifty_option_v20_1_v17_8_7_integration import (
    integrate_v20_1_to_v17_8_7,
)

from nifty_option_v20_1_v17_8_8_integration import (
    integrate_v20_1_to_v17_8_8,
)


SYMBOL = "NIFTY26SEP25000CE"


def build_opportunity():
    return {
        "Trading Symbol": SYMBOL,
        "Paper Trade Permission": "PERMITTED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }


def build_contract():
    return {
        "Status": "CONTRACT_VALIDATED",
        "Lot Size": 65,
        "Trading Symbol": SYMBOL,
        "Instrument Token": 123456,
        "Contract Identity Valid": True,
    }


def build_v14_5_evaluated():
    return {
        "Status": "EVALUATED",
        "Trading Symbol": SYMBOL,
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 25000,
        "Option Type": "CE",
        "Entry Price": 100.0,
        "Stop Price": 90.0,
        "Target 1": 120.0,
        "Target 2": 140.0,
        "Target 3": 160.0,
        "Risk Reward 1": 2.0,
        "Risk Reward 2": 4.0,
        "Risk Reward 3": 6.0,
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }


def build_v20_1_v17_8_7_result():
    v20_result = qualify_capital_allocation(
        build_opportunity(),
        priority=1,
        requested_allocation=20000,
    )

    market_data = [
        {
            "Candidate": SYMBOL,
            "Entry Price": 100,
            "Contract Validation": build_contract(),
        }
    ]

    v17_7_result = integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    v17_8_result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    v17_8_2_result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    v17_8_5_result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        {
            "Status": "QUALIFIED",
            "Paper Trade Permission": "PERMITTED",
            "Trading Symbol": SYMBOL,
            "Underlying": "NIFTY",
            "Expiry": "2026-09-22",
            "Strike": 25000,
            "Option Type": "CE",
            "Entry Price": 100.0,
            "Stop Price": 90.0,
            "Target 1": 120.0,
            "Target 2": 140.0,
            "Target 3": 160.0,
            "Risk Reward 1": 2.0,
            "Risk Reward 2": 4.0,
            "Risk Reward 3": 6.0,
            "Entry Qualification": "QUALIFIED",
            "Qualification Reason": "V14.5 exit-qualified setup",
        },
        "JKJ-TRADE-001",
        entry_time="2026-09-22T09:30:00",
    )

    v17_8_6_result = integrate_v20_1_to_v17_8_6(
        v17_8_5_result
    )

    return integrate_v20_1_to_v17_8_7(
        v17_8_6_result,
        build_v14_5_evaluated(),
        entry_time="2026-09-22T09:30:00",
    )


def test_successful_lifecycle_boundary():
    result = integrate_v20_1_to_v17_8_8(
        build_v20_1_v17_8_7_result()
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_8_INTEGRATION_COMPLETE"
    )

    assert result["Lifecycle Ready"] is True
    assert result["Lifecycle Owner"] == "V15.4 / V11"
    assert result["Trade ID"] == "JKJ-TRADE-001"
    assert result["Symbol"] == SYMBOL
    assert result["Instrument Type"] == "OPTION"
    assert result["Current Quantity"] == 195
    assert result["V15.4 Lifecycle Action Permitted"] is True

    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Automatic Ranking"] is False
    assert result["Capital Reassignment"] is False
    assert result["Priority Source"] == "DECISION_RISK_LAYER"

    print(
        "Real-market V20.1 -> V17.8.8 lifecycle boundary: PASS"
    )


def test_incomplete_v17_8_7_blocked():
    result = build_v20_1_v17_8_7_result()

    result["V17.8.7 Result"]["Status"] = (
        "V17_8_7_PAPER_HANDOFF_REJECTED"
    )

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )
    assert output["Lifecycle Ready"] is False

    print("Incomplete V17.8.7 safeguard: PASS")


def test_broker_communication_blocked():
    result = build_v20_1_v17_8_7_result()
    result["Broker Communication"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print("Broker communication safeguard: PASS")


def test_live_order_blocked():
    result = build_v20_1_v17_8_7_result()
    result["Order Placement Permitted"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print("Live order placement safeguard: PASS")


def test_capital_reassignment_blocked():
    result = build_v20_1_v17_8_7_result()
    result["Capital Reassignment"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print("Capital reassignment safeguard: PASS")


def test_automatic_ranking_blocked():
    result = build_v20_1_v17_8_7_result()
    result["Automatic Ranking"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print("Automatic ranking safeguard: PASS")


def test_trade_not_open_blocked():
    result = build_v20_1_v17_8_7_result()

    result["V17.8.7 Result"]["Trade"]["Status"] = "CLOSED"

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print("Non-OPEN V11 trade safeguard: PASS")


def test_v15_permission_blocked():
    result = build_v20_1_v17_8_7_result()

    result["V17.8.7 Result"][
        "Paper Trade Qualification"
    ]["Paper Trade Permission"] = "NOT_PERMITTED"

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print("V15 paper permission safeguard: PASS")


def run_test():
    test_successful_lifecycle_boundary()
    test_incomplete_v17_8_7_blocked()
    test_broker_communication_blocked()
    test_live_order_blocked()
    test_capital_reassignment_blocked()
    test_automatic_ranking_blocked()
    test_trade_not_open_blocked()
    test_v15_permission_blocked()

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> "
        "V17.8.2 -> V17.8.5 -> V17.8.6 -> "
        "V17.8.7 -> V17.8.8 "
        "REAL-MARKET INTEGRATION: ALL TESTS PASSED"
    )

    print("V15.4 / V11 remains lifecycle authority.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No live Zerodha order.")
    print("No broker communication.")
    print("No lifecycle action performed.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
    
"""
JKJ AI Trader
V20.1 -> V17.8.7 Real-Market Controlled V15 Paper-Trade Handoff Test

Real-market integration chain:

V20.1
    -> V17.6
    -> V17.7
    -> V17.8.1
    -> V17.8.2
    -> V17.8.5
    -> V17.8.6
    -> V17.8.7

V17.8.7 is a controlled PAPER-TRADING handoff.

V14.5 EVALUATED qualification remains authoritative.

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


def build_v20_1_v17_8_6_result():
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

    return integrate_v20_1_to_v17_8_6(
        v17_8_5_result
    )


def test_successful_v15_paper_handoff():
    result = integrate_v20_1_to_v17_8_7(
        build_v20_1_v17_8_6_result(),
        build_v14_5_evaluated(),
        entry_time="2026-09-22T09:30:00",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_COMPLETE"
    )

    handoff = result["V17.8.7 Result"]

    assert (
        handoff["Status"]
        == "V17_8_7_PAPER_HANDOFF_COMPLETE"
    )

    assert result["V15 Handoff"] is True
    assert result["V15 Call Permitted"] is True
    assert result["V11 Call Permitted"] is True
    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Capital Reassignment"] is False
    assert result["Automatic Ranking"] is False
    assert result["Priority Source"] == "DECISION_RISK_LAYER"

    assert result["Quantity"] == 195
    assert result["Qualified Entry Price"] == 100.0
    assert result["Paper Fill Price"] == 100.0

    trade = result["Trade"]

    assert trade is not None
    assert trade["Trade ID"] == "JKJ-TRADE-001"
    assert trade["Symbol"] == SYMBOL


def test_non_evaluated_v14_5_blocked():
    result = integrate_v20_1_to_v17_8_7(
        build_v20_1_v17_8_6_result(),
        {
            "Status": "QUALIFIED",
            "Trading Symbol": SYMBOL,
        },
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def test_symbol_mismatch_blocked():
    qualification = build_v14_5_evaluated()
    qualification["Trading Symbol"] = "NIFTY26SEP25000PE"

    result = integrate_v20_1_to_v17_8_7(
        build_v20_1_v17_8_6_result(),
        qualification,
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def test_incomplete_v17_8_6_blocked():
    result = integrate_v20_1_to_v17_8_7(
        {
            "Status": "V20_1_V17_8_6_INTEGRATION_BLOCKED",
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
        },
        build_v14_5_evaluated(),
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def test_live_order_safeguard():
    source = build_v20_1_v17_8_6_result()
    source["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_7(
        source,
        build_v14_5_evaluated(),
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    source = build_v20_1_v17_8_6_result()
    source["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_7(
        source,
        build_v14_5_evaluated(),
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    source = build_v20_1_v17_8_6_result()
    source["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_7(
        source,
        build_v14_5_evaluated(),
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def test_automatic_ranking_safeguard():
    source = build_v20_1_v17_8_6_result()
    source["Automatic Ranking"] = True

    result = integrate_v20_1_to_v17_8_7(
        source,
        build_v14_5_evaluated(),
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_7_INTEGRATION_BLOCKED"
    )


def run_test():
    test_successful_v15_paper_handoff()
    print("Real-market V20.1 -> V17.8.7 V15 paper handoff: PASS")

    test_non_evaluated_v14_5_blocked()
    print("V14.5 EVALUATED qualification safeguard: PASS")

    test_symbol_mismatch_blocked()
    print("V14.5 symbol identity safeguard: PASS")

    test_incomplete_v17_8_6_blocked()
    print("Incomplete V17.8.6 safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    test_automatic_ranking_safeguard()
    print("Automatic ranking safeguard: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> "
        "V17.8.2 -> V17.8.5 -> V17.8.6 -> V17.8.7 "
        "REAL-MARKET INTEGRATION: ALL TESTS PASSED"
    )

    print("V14.5 EVALUATED qualification remains authoritative.")
    print("Controlled V15.3 paper handoff only.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No live Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
"""
JKJ AI Trader
Real-Market → V20.1 → V17.6 → V17.7 → V17.8.1 Integration Test

Purpose:
    Validate the controlled handoff from an already-qualified
    real-market Decision/Risk opportunity through V20.1,
    V17.6 capital allocation, V17.7 quantity/contract
    reconciliation, and V17.8.1 paper execution.

This test does NOT:
- generate priority
- generate requested allocation
- rank candidates
- change capital allocation policy
- calculate quantity itself
- place live orders
- communicate with Zerodha
- modify V16.1
- modify V20.1
- modify V17.6
- modify V17.7
- modify V17.8
- modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_real_market_v20_1_integration import (
    integrate_real_market_to_v20_1,
)

from modules.nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
)

from modules.nifty_option_v20_1_v17_8_integration import (
    integrate_v20_1_to_v17_8,
)


def qualified_inputs(symbol="NIFTY26SEP25000CE"):

    entry_risk_context = {
        "Status": "EVALUATED",
        "Trading Symbol": symbol,
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
    }

    stop_loss_context = {
        "Status": "EVALUATED",
        "Trading Symbol": symbol,
        "Stop-Loss Context": "STOP_SUPPORTED",
    }

    exit_qualification = {
        "Status": "EVALUATED",
        "Trading Symbol": symbol,
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }

    paper_qualification = {
        "Status": "QUALIFIED",
        "Paper Trade Permission": "PERMITTED",
    }

    return (
        entry_risk_context,
        stop_loss_context,
        exit_qualification,
        paper_qualification,
    )


def build_contract(symbol, token, lot_size=65):
    return {
        "Status": "CONTRACT_VALIDATED",
        "Lot Size": lot_size,
        "Trading Symbol": symbol,
        "Instrument Token": token,
        "Contract Identity Valid": True,
    }


def run_test():

    print(
        "\nJKJ AI Trader — "
        "Real-Market → V20.1 → V17.6 → V17.7 → V17.8.1 "
        "Integration Test"
    )
    print("=" * 100)

    # ---------------------------------------------------------
    # TEST 1 — Complete real-market → paper execution chain
    # ---------------------------------------------------------

    inputs = qualified_inputs()

    real_market_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert real_market_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    v20_result = real_market_result["V20.1 Result"]

    assert v20_result["Status"] == (
        "CAPITAL_ALLOCATION_QUALIFIED"
    )

    market_data = [
        {
            "Candidate": "NIFTY26SEP25000CE",
            "Entry Price": 100,
            "Contract Validation": build_contract(
                "NIFTY26SEP25000CE",
                123456,
            ),
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

    assert v17_7_result["Status"] == (
        "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    reconciliation = v17_7_result["V17.7 Reconciliation"]

    assert reconciliation["Status"] == (
        "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
    )

    item = reconciliation["Reconciliations"][0]

    assert item["Candidate"] == "NIFTY26SEP25000CE"
    assert item["Priority"] == 1
    assert item["Allocated Capital"] == 20000
    assert item["Entry Price"] == 100
    assert item["Lot Size"] == 65
    assert item["Reconciled Quantity"] == 195
    assert item["Estimated Capital Required"] == 19500
    assert item["Contract Identity Valid"] is True
    assert item["Order Placement Permitted"] is False

    # V17.7 → V17.8.1
    paper_execution_result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert paper_execution_result["Status"] == (
        "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    execution_request = paper_execution_result[
        "Execution Request"
    ]["Execution Request"]

    assert execution_request["Candidate"] == (
        "NIFTY26SEP25000CE"
    )
    assert execution_request["Priority"] == 1
    assert execution_request["Priority Source"] == (
        "DECISION_RISK_LAYER"
    )
    assert execution_request["Trading Symbol"] == (
        "NIFTY26SEP25000CE"
    )
    assert execution_request["Instrument Token"] == 123456
    assert execution_request["Transaction Type"] == "BUY"
    assert execution_request["Order Type"] == "MARKET"
    assert execution_request["Product"] == "MIS"
    assert execution_request["Quantity"] == 195
    assert execution_request["Lot Size"] == 65
    assert execution_request["Entry Price Reference"] == 100
    assert execution_request["Allocated Capital"] == 20000
    assert execution_request["Required Capital"] == 19500
    assert execution_request["Contract Valid"] is True
    assert execution_request["Execution Ready"] is True
    assert execution_request["Order Placement Permitted"] is False
    assert execution_request["Broker Communication"] is False

    paper_order = paper_execution_result[
        "V17.8.1 Paper Order"
    ]

    assert paper_order["Status"] == (
        "PAPER_ORDER_ACCEPTED"
    )

    paper_order_data = paper_order["Paper Order"]

    assert paper_order_data["Trading Symbol"] == (
        "NIFTY26SEP25000CE"
    )
    assert paper_order_data["Instrument Token"] == 123456
    assert paper_order_data["Quantity"] == 195
    assert paper_order_data["Lot Size"] == 65
    assert paper_order_data["Transaction Type"] == "BUY"
    assert paper_order_data["Order Type"] == "MARKET"
    assert paper_order_data["Product"] == "MIS"
    assert paper_order_data["Paper Status"] == (
        "PAPER_ACCEPTED"
    )

    print(
        "Real-Market → V20.1 → V17.6 → V17.7 → "
        "V17.8.1 paper execution: PASS"
    )

    # ---------------------------------------------------------
    # TEST 2 — Blocked V17.7 result cannot reach paper order
    # ---------------------------------------------------------

    blocked_result = {
        "Status": "V20_1_V17_7_INTEGRATION_BLOCKED",
        "Reason": "Test blocked result",
    }

    blocked_paper_result = integrate_v20_1_to_v17_8(
        blocked_result
    )

    assert blocked_paper_result["Status"] == (
        "V20_1_V17_8_INTEGRATION_BLOCKED"
    )

    assert blocked_paper_result["Paper Order"] is None
    assert blocked_paper_result[
        "Order Placement Permitted"
    ] is False

    print("Blocked V17.7 safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 3 — Live order safeguard
    # ---------------------------------------------------------

    live_order_test = dict(v17_7_result)

    live_reconciliation = dict(
        v17_7_result["V17.7 Reconciliation"]
    )

    live_reconciliations = list(
        live_reconciliation["Reconciliations"]
    )

    live_reconciliation["Reconciliations"] = [
        dict(live_reconciliations[0])
    ]

    live_reconciliation[
        "Order Placement Permitted"
    ] = True

    live_order_test[
        "V17.7 Reconciliation"
    ] = live_reconciliation

    blocked_live_result = integrate_v20_1_to_v17_8(
        live_order_test
    )

    assert blocked_live_result["Status"] == (
        "V20_1_V17_8_INTEGRATION_BLOCKED"
    )

    assert blocked_live_result[
        "Order Placement Permitted"
    ] is False

    print("Live order placement safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 4 — End-to-end safety boundary
    # ---------------------------------------------------------

    assert real_market_result[
        "Automatic Ranking"
    ] is False

    assert real_market_result[
        "Broker Communication"
    ] is False

    assert real_market_result[
        "Order Placement Permitted"
    ] is False

    assert v17_7_result[
        "Automatic Ranking"
    ] is False

    assert v17_7_result[
        "Capital Reassignment"
    ] is False

    assert v17_7_result[
        "Broker Communication"
    ] is False

    assert v17_7_result[
        "Order Placement Permitted"
    ] is False

    assert paper_execution_result[
        "Paper Execution"
    ] is True

    assert paper_execution_result[
        "Broker Communication"
    ] is False

    assert paper_execution_result[
        "Order Placement Permitted"
    ] is False

    assert paper_execution_result[
        "Capital Reassignment"
    ] is False

    assert paper_execution_result[
        "Automatic Ranking"
    ] is False

    assert paper_execution_result[
        "Wisdom Before Wealth"
    ] is True

    print("End-to-end paper execution safety boundary: PASS")

    print()
    print(
        "REAL-MARKET → V20.1 → V17.6 → V17.7 → V17.8.1 "
        "INTEGRATION: ALL TESTS PASSED"
    )
    print("Priority explicitly supplied.")
    print("Requested allocation explicitly supplied.")
    print("V17.6 performed policy allocation.")
    print("V17.7 performed quantity/contract reconciliation.")
    print("V17.8.1 created a paper order only.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha communication.")
    print("No live order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
    
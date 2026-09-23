"""
JKJ AI Trader
Real-Market → V20.1 → V17.6 → V17.7 Integration Test

Purpose:
    Validate the controlled handoff from an already-qualified
    real-market Decision/Risk opportunity through V20.1,
    V17.6 capital allocation, and V17.7 quantity/contract
    reconciliation.

This test does NOT:
- generate priority
- generate requested allocation
- rank candidates
- change capital allocation policy
- calculate quantity itself
- place orders
- communicate with Zerodha
- modify V16.1
- modify V20.1
- modify V17.6
- modify V17.7
- modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_real_market_v20_1_integration import (
    integrate_real_market_to_v20_1,
)

from modules.nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
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
        "\nJKJ AI Trader — Real-Market → V20.1 → V17.6 → V17.7 "
        "Integration Test"
    )
    print("=" * 85)

    # ---------------------------------------------------------
    # TEST 1 — Complete real-market single-candidate chain
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

    result = integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert result["Status"] == (
        "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    reconciliation = result["V17.7 Reconciliation"]

    assert reconciliation["Status"] == (
        "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
    )

    assert reconciliation["Successful Candidates"] == 1
    assert reconciliation["Blocked Candidates"] == 0

    item = reconciliation["Reconciliations"][0]

    assert item["Candidate"] == "NIFTY26SEP25000CE"
    assert item["Priority"] == 1
    assert item["Allocated Capital"] == 20000
    assert item["Entry Price"] == 100
    assert item["Lot Size"] == 65
    assert item["Reconciled Lots"] == 3
    assert item["Reconciled Quantity"] == 195
    assert item["Estimated Capital Required"] == 19500
    assert item["Unused Allocated Capital"] == 500
    assert item["Trading Symbol"] == "NIFTY26SEP25000CE"
    assert item["Instrument Token"] == 123456
    assert item["Contract Identity Valid"] is True
    assert item["Order Placement Permitted"] is False

    print(
        "Real-Market → V20.1 → V17.6 → V17.7 chain: PASS"
    )

    # ---------------------------------------------------------
    # TEST 2 — Invalid contract blocks quantity reconciliation
    # ---------------------------------------------------------

    invalid_market_data = [
        {
            "Candidate": "NIFTY26SEP25000CE",
            "Entry Price": 100,
            "Contract Validation": {
                "Lot Size": 0,
                "Trading Symbol": "NIFTY26SEP25000CE",
                "Instrument Token": 123456,
                "Contract Identity Valid": False,
            },
        }
    ]

    blocked_result = integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=invalid_market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert blocked_result["Status"] == (
        "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    blocked_reconciliation = blocked_result[
        "V17.7 Reconciliation"
    ]

    assert blocked_reconciliation[
        "Successful Candidates"
    ] == 0

    assert blocked_reconciliation[
        "Blocked Candidates"
    ] == 1

    blocked_item = blocked_reconciliation[
        "Reconciliations"
    ][0]

    assert blocked_item["Status"] == (
        "RECONCILIATION_BLOCKED"
    )

    assert blocked_item["Reconciled Quantity"] == 0
    assert blocked_item["Order Placement Permitted"] is False

    print("Invalid contract safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 3 — Capital insufficient for one full lot
    # ---------------------------------------------------------

    small_allocation_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=5000,
    )

    assert small_allocation_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    small_v20_result = small_allocation_result[
        "V20.1 Result"
    ]

    small_result = integrate_v20_1_to_v17_7(
        v20_1_results=[small_v20_result],
        candidate_market_data=market_data,
        usable_capital=5000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    small_reconciliation = small_result[
        "V17.7 Reconciliation"
    ]

    assert small_reconciliation[
        "Successful Candidates"
    ] == 0

    assert small_reconciliation[
        "Blocked Candidates"
    ] == 1

    small_item = small_reconciliation[
        "Reconciliations"
    ][0]

    assert small_item["Status"] == (
        "RECONCILIATION_BLOCKED"
    )

    assert small_item["Reconciled Quantity"] == 0
    assert small_item["Uncommitted Capital"] == 5000
    assert small_item["Order Placement Permitted"] is False

    print("Insufficient quantity capital safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 4 — End-to-end execution safety boundary
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

    assert result[
        "Automatic Ranking"
    ] is False

    assert result[
        "Capital Reassignment"
    ] is False

    assert result[
        "Broker Communication"
    ] is False

    assert result[
        "Order Placement Permitted"
    ] is False

    assert result[
        "Wisdom Before Wealth"
    ] is True

    print("End-to-end execution safety boundary: PASS")

    print()
    print(
        "REAL-MARKET → V20.1 → V17.6 → V17.7 "
        "INTEGRATION: ALL TESTS PASSED"
    )
    print("Priority explicitly supplied.")
    print("Requested allocation explicitly supplied.")
    print("V17.6 performed policy allocation.")
    print("V17.7 performed quantity/contract reconciliation.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha communication.")
    print("No order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
"""
JKJ AI Trader
Real-Market → V20.1 → V17.6 Integration Test

Purpose:
    Validate the controlled handoff from an already-qualified
    real-market Decision/Risk opportunity through V20.1 and
    into the existing V17.6 capital-allocation layer.

This test does NOT:
- generate priority
- generate requested allocation
- calculate quantity
- rank candidates
- place orders
- communicate with Zerodha
- modify V16.1
- modify V20.1
- modify V17.6
- modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_real_market_v20_1_integration import (
    integrate_real_market_to_v20_1,
)

from modules.nifty_option_v20_1_v17_6_integration import (
    integrate_v20_1_to_v17_6,
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


def run_test():

    print(
        "\nJKJ AI Trader — Real-Market → V20.1 → V17.6 "
        "Integration Test"
    )
    print("=" * 75)

    # ---------------------------------------------------------
    # TEST 1 — Complete single-candidate chain
    # ---------------------------------------------------------

    inputs = qualified_inputs()

    v20_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert v20_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    assert v20_result["V20.1 Result"]["Status"] == (
        "CAPITAL_ALLOCATION_QUALIFIED"
    )

    v17_6_result = integrate_v20_1_to_v17_6(
        v20_1_results=[
            v20_result["V20.1 Result"]
        ],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert v17_6_result["Status"] == (
        "V20_1_V17_6_INTEGRATION_COMPLETE"
    )

    allocation = v17_6_result["Policy Allocation Result"]

    assert allocation["Status"] == (
        "POLICY_ALLOCATION_COMPLETE"
    )

    assert allocation["Allocations"][0]["Candidate"] == (
        "NIFTY26SEP25000CE"
    )

    assert allocation["Allocations"][0]["Priority"] == 1

    assert allocation["Allocations"][0][
        "Requested Allocation"
    ] == 20000

    assert allocation["Allocations"][0][
        "Allocated Capital"
    ] == 20000

    assert allocation["Remaining Capital"] == 10000

    print("Real-Market → V20.1 → V17.6 chain: PASS")

    # ---------------------------------------------------------
    # TEST 2 — Paper permission blocked
    # ---------------------------------------------------------

    blocked_inputs = list(inputs)

    blocked_paper = dict(blocked_inputs[3])
    blocked_paper["Paper Trade Permission"] = "BLOCKED"
    blocked_inputs[3] = blocked_paper

    v20_result = integrate_real_market_to_v20_1(
        *blocked_inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert v20_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Paper permission blocks downstream allocation: PASS")

    # ---------------------------------------------------------
    # TEST 3 — Invalid priority blocked before V17.6
    # ---------------------------------------------------------

    v20_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=0,
        requested_allocation=20000,
    )

    assert v20_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Invalid priority blocked before V17.6: PASS")

    # ---------------------------------------------------------
    # TEST 4 — Invalid requested allocation blocked
    # ---------------------------------------------------------

    v20_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=0,
    )

    assert v20_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print(
        "Invalid requested allocation blocked before V17.6: PASS"
    )

    # ---------------------------------------------------------
    # TEST 5 — Capital remains with V17.6
    # ---------------------------------------------------------

    v20_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=10000,
    )

    assert v20_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    v17_6_result = integrate_v20_1_to_v17_6(
        v20_1_results=[
            v20_result["V20.1 Result"]
        ],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    allocation = v17_6_result["Policy Allocation Result"]

    assert allocation["Status"] == (
        "POLICY_ALLOCATION_COMPLETE"
    )

    assert allocation["Allocations"][0][
        "Allocated Capital"
    ] == 10000

    assert allocation["Remaining Capital"] == 20000

    print("Unused capital preservation through V17.6: PASS")

    # ---------------------------------------------------------
    # TEST 6 — Final safety boundary
    # ---------------------------------------------------------

    assert v20_result["Automatic Ranking"] is False
    assert v20_result["Broker Communication"] is False
    assert v20_result["Order Placement Permitted"] is False
    assert v20_result["Wisdom Before Wealth"] is True

    assert v17_6_result["Automatic Ranking"] is False
    assert v17_6_result["Broker Communication"] is False
    assert v17_6_result["Order Placement Permitted"] is False
    assert v17_6_result["Wisdom Before Wealth"] is True

    print("End-to-end execution safety boundary: PASS")

    print()
    print(
        "REAL-MARKET → V20.1 → V17.6 INTEGRATION: "
        "ALL TESTS PASSED"
    )
    print("Priority explicitly supplied.")
    print("Requested allocation explicitly supplied.")
    print("V17.6 performed policy allocation.")
    print("No quantity calculation.")
    print("No Zerodha communication.")
    print("No order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()

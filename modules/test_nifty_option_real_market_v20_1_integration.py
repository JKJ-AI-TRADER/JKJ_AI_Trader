"""
JKJ AI Trader
Real-Market → V20.1 Integration Test

Purpose:
    Validate the controlled integration boundary between an
    already-qualified real-market Decision/Risk result and V20.1.

This test does NOT:
- place orders
- communicate with Zerodha
- allocate capital
- calculate quantity
- rank candidates
- modify V16.1
- modify V20.1
- modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_real_market_v20_1_integration import (
    integrate_real_market_to_v20_1,
)


def qualified_inputs():
    entry_risk_context = {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY26SEP25000CE",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
    }

    stop_loss_context = {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY26SEP25000CE",
        "Stop-Loss Context": "STOP_SUPPORTED",
    }

    exit_qualification = {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY26SEP25000CE",
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

    print("\nJKJ AI Trader — Real-Market → V20.1 Integration Test")
    print("=" * 65)

    # ---------------------------------------------------------
    # 1. Valid Decision/Risk opportunity
    # ---------------------------------------------------------

    inputs = qualified_inputs()

    result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    v20_1 = result["V20.1 Result"]

    assert v20_1["Status"] == (
        "CAPITAL_ALLOCATION_QUALIFIED"
    )

    assert v20_1["Capital Allocation Eligible"] is True
    assert v20_1["Trading Symbol"] == "NIFTY26SEP25000CE"
    assert v20_1["Priority"] == 1
    assert v20_1["Requested Allocation"] == 20000
    assert v20_1["Priority Source"] == "DECISION_RISK_LAYER"
    assert v20_1["Automatic Ranking"] is False
    assert v20_1["Broker Communication"] is False
    assert v20_1["Order Placement Permitted"] is False

    print("Valid real-market Decision/Risk integration: PASS")

    # ---------------------------------------------------------
    # 2. Paper permission blocked
    # ---------------------------------------------------------

    blocked = list(inputs)

    blocked_paper = dict(blocked[3])
    blocked_paper["Paper Trade Permission"] = "BLOCKED"
    blocked[3] = blocked_paper

    result = integrate_real_market_to_v20_1(
        *blocked,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Paper permission safeguard: PASS")

    # ---------------------------------------------------------
    # 3. Invalid priority
    # ---------------------------------------------------------

    result = integrate_real_market_to_v20_1(
        *inputs,
        priority=0,
        requested_allocation=20000,
    )

    assert result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Priority safeguard: PASS")

    # ---------------------------------------------------------
    # 4. Invalid requested allocation
    # ---------------------------------------------------------

    result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=0,
    )

    assert result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Requested allocation safeguard: PASS")

    # ---------------------------------------------------------
    # 5. Missing required field
    # ---------------------------------------------------------

    incomplete_exit = dict(inputs[2])
    del incomplete_exit["Exit Structure"]

    incomplete_inputs = (
        inputs[0],
        inputs[1],
        incomplete_exit,
        inputs[3],
    )

    result = integrate_real_market_to_v20_1(
        *incomplete_inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Required-field safeguard: PASS")

    # ---------------------------------------------------------
    # 6. Symbol mismatch safeguard
    # ---------------------------------------------------------

    mismatch_exit = dict(inputs[2])
    mismatch_exit["Trading Symbol"] = "NIFTY26SEP25100CE"

    mismatch_inputs = (
        inputs[0],
        inputs[1],
        mismatch_exit,
        inputs[3],
    )

    result = integrate_real_market_to_v20_1(
        *mismatch_inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_BLOCKED"
    )

    print("Trading-symbol mismatch safeguard: PASS")

    # ---------------------------------------------------------
    # 7. Final safety checks
    # ---------------------------------------------------------

    assert result["Automatic Ranking"] is False
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Wisdom Before Wealth"] is True

    print("Execution safety safeguards: PASS")

    print()
    print(
        "REAL-MARKET → V20.1 INTEGRATION: "
        "ALL TESTS PASSED"
    )
    print("No automatic ranking.")
    print("No capital allocation performed.")
    print("No quantity calculation.")
    print("No Zerodha communication.")
    print("No order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()

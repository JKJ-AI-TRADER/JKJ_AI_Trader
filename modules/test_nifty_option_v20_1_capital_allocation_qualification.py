"""
JKJ AI Trader V20.1
Decision/Risk Capital Allocation Qualification Test
"""

from modules.nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)


def run_test():
    opportunity = {
        "Trading Symbol": "NIFTY26SEP25000CE",
        "Paper Trade Permission": "PERMITTED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }

    # ---------------------------------------------------------
    # 1. Valid qualified candidate
    # ---------------------------------------------------------
    result = qualify_capital_allocation(
        opportunity,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == "CAPITAL_ALLOCATION_QUALIFIED"
    assert result["Capital Allocation Eligible"] is True
    assert result["Priority"] == 1
    assert result["Priority Source"] == "DECISION_RISK_LAYER"
    assert result["Requested Allocation"] == 20000
    assert result["Automatic Ranking"] is False
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Wisdom Before Wealth"] is True

    print("Valid qualified candidate: PASS")

    # ---------------------------------------------------------
    # 2. Paper trade permission blocked
    # ---------------------------------------------------------
    blocked_permission = dict(opportunity)
    blocked_permission["Paper Trade Permission"] = "BLOCKED"

    result = qualify_capital_allocation(
        blocked_permission,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == "CAPITAL_ALLOCATION_BLOCKED"
    assert result["Capital Allocation Eligible"] is False

    print("Paper permission safeguard: PASS")

    # ---------------------------------------------------------
    # 3. Invalid priority
    # ---------------------------------------------------------
    result = qualify_capital_allocation(
        opportunity,
        priority=0,
        requested_allocation=20000,
    )

    assert result["Status"] == "CAPITAL_ALLOCATION_BLOCKED"
    assert result["Capital Allocation Eligible"] is False

    print("Priority safeguard: PASS")

    # ---------------------------------------------------------
    # 4. Invalid requested allocation
    # ---------------------------------------------------------
    result = qualify_capital_allocation(
        opportunity,
        priority=1,
        requested_allocation=0,
    )

    assert result["Status"] == "CAPITAL_ALLOCATION_BLOCKED"
    assert result["Capital Allocation Eligible"] is False

    print("Requested allocation safeguard: PASS")

    # ---------------------------------------------------------
    # 5. Missing required opportunity field
    # ---------------------------------------------------------
    incomplete = {
        "Trading Symbol": "NIFTY26SEP25000CE",
    }

    result = qualify_capital_allocation(
        incomplete,
        priority=1,
        requested_allocation=20000,
    )

    assert result["Status"] == "CAPITAL_ALLOCATION_BLOCKED"
    assert result["Capital Allocation Eligible"] is False

    print("Required-field safeguard: PASS")

    print()
    print("V20.1 CAPITAL ALLOCATION QUALIFICATION: ALL TESTS PASSED")
    print("No capital allocation performed.")
    print("No quantity calculation.")
    print("No ranking performed.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()

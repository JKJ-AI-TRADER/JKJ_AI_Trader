"""
JKJ AI Trader V20.1 -> V17.6 Integration Test
"""

from modules.nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)

from modules.nifty_option_v20_1_v17_6_integration import (
    integrate_v20_1_to_v17_6,
)


def build_opportunity(symbol):
    return {
        "Trading Symbol": symbol,
        "Paper Trade Permission": "PERMITTED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }


def run_test():

    # ---------------------------------------------------------
    # TEST 1 — Single qualified candidate
    # ---------------------------------------------------------
    v20_result = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=20000,
    )

    result = integrate_v20_1_to_v17_6(
        v20_1_results=[v20_result],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert result["Status"] == "V20_1_V17_6_INTEGRATION_COMPLETE"

    allocation = result["Policy Allocation Result"]

    assert allocation["Status"] == "POLICY_ALLOCATION_COMPLETE"
    assert allocation["Allocations"][0]["Candidate"] == "NIFTY26SEP25000CE"
    assert allocation["Allocations"][0]["Priority"] == 1
    assert allocation["Allocations"][0]["Requested Allocation"] == 20000
    assert allocation["Allocations"][0]["Allocated Capital"] == 20000

    print("Single V20.1 -> V17.6 handoff: PASS")

    # ---------------------------------------------------------
    # TEST 2 — Multiple qualified candidates
    # ---------------------------------------------------------
    ce = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=20000,
    )

    pe = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000PE"),
        priority=2,
        requested_allocation=10000,
    )

    result = integrate_v20_1_to_v17_6(
        v20_1_results=[pe, ce],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    allocation = result["Policy Allocation Result"]

    assert allocation["Status"] == "POLICY_ALLOCATION_COMPLETE"
    assert allocation["Allocations"][0]["Candidate"] == "NIFTY26SEP25000CE"
    assert allocation["Allocations"][1]["Candidate"] == "NIFTY26SEP25000PE"
    assert allocation["Allocations"][0]["Allocated Capital"] == 20000
    assert allocation["Allocations"][1]["Allocated Capital"] == 10000

    print("Multiple V20.1 -> V17.6 handoff: PASS")

    # ---------------------------------------------------------
    # TEST 3 — V20.1 blocked candidate must not proceed
    # ---------------------------------------------------------
    blocked_opportunity = build_opportunity("NIFTY26SEP25000CE")
    blocked_opportunity["Paper Trade Permission"] = "BLOCKED"

    blocked = qualify_capital_allocation(
        blocked_opportunity,
        priority=1,
        requested_allocation=20000,
    )

    result = integrate_v20_1_to_v17_6(
        v20_1_results=[blocked],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert result["Status"] == "V20_1_V17_6_INTEGRATION_BLOCKED"

    print("Blocked V20.1 candidate safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 4 — Duplicate priority remains V17.6 responsibility
    # ---------------------------------------------------------
    first = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=10000,
    )

    second = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000PE"),
        priority=1,
        requested_allocation=10000,
    )

    result = integrate_v20_1_to_v17_6(
        v20_1_results=[first, second],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    allocation = result["Policy Allocation Result"]

    assert allocation["Status"] == "POLICY_ALLOCATION_BLOCKED"
    assert allocation["Reason"] == "Duplicate candidate priority"

    print("Duplicate priority safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 5 — Unused capital remains with V17.6
    # ---------------------------------------------------------
    v20_result = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=10000,
    )

    result = integrate_v20_1_to_v17_6(
        v20_1_results=[v20_result],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    allocation = result["Policy Allocation Result"]

    assert allocation["Allocations"][0]["Allocated Capital"] == 10000
    assert allocation["Remaining Capital"] == 20000

    print("Unused capital preservation: PASS")

    print()
    print("V20.1 -> V17.6 INTEGRATION: ALL TESTS PASSED")
    print("V20.1 did not generate Priority.")
    print("V20.1 did not generate Requested Allocation.")
    print("V17.6 performed policy allocation.")
    print("No quantity calculation.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()

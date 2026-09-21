"""
JKJ AI Trader V20.1 -> V17.6 -> V17.7 Integration Test
"""

from nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)

from nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
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


def build_contract(symbol, token, lot_size=65):
    return {
        "Status": "CONTRACT_VALIDATED",
        "Lot Size": lot_size,
        "Trading Symbol": symbol,
        "Instrument Token": token,
        "Contract Identity Valid": True,
    }


def run_test():

    # ---------------------------------------------------------
    # TEST 1 — Single candidate full chain
    # ---------------------------------------------------------

    v20_result = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=20000,
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

    assert result["Status"] == "V20_1_V17_7_INTEGRATION_COMPLETE"

    reconciliation = result["V17.7 Reconciliation"]

    assert (
        reconciliation["Status"]
        == "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
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

    print("Single V20.1 -> V17.6 -> V17.7: PASS")

    # ---------------------------------------------------------
    # TEST 2 — Multiple candidates
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

    market_data = [
        {
            "Candidate": "NIFTY26SEP25000CE",
            "Entry Price": 100,
            "Contract Validation": build_contract(
                "NIFTY26SEP25000CE",
                123456,
            ),
        },
        {
            "Candidate": "NIFTY26SEP25000PE",
            "Entry Price": 100,
            "Contract Validation": build_contract(
                "NIFTY26SEP25000PE",
                123457,
            ),
        },
    ]

    result = integrate_v20_1_to_v17_7(
        v20_1_results=[pe, ce],
        candidate_market_data=market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    reconciliation = result["V17.7 Reconciliation"]

    assert reconciliation["Successful Candidates"] == 2
    assert reconciliation["Blocked Candidates"] == 0

    assert (
        reconciliation["Reconciliations"][0]["Candidate"]
        == "NIFTY26SEP25000CE"
    )

    assert (
        reconciliation["Reconciliations"][1]["Candidate"]
        == "NIFTY26SEP25000PE"
    )

    print("Multiple candidate reconciliation: PASS")

    # ---------------------------------------------------------
    # TEST 3 — V20.1 blocked candidate
    # ---------------------------------------------------------

    blocked_opportunity = build_opportunity(
        "NIFTY26SEP25000CE"
    )
    blocked_opportunity["Paper Trade Permission"] = "BLOCKED"

    blocked = qualify_capital_allocation(
        blocked_opportunity,
        priority=1,
        requested_allocation=20000,
    )

    result = integrate_v20_1_to_v17_7(
        v20_1_results=[blocked],
        candidate_market_data=market_data[:1],
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert result["Status"] == "V20_1_V17_7_INTEGRATION_BLOCKED"
    assert result["Stage"] == "V20.1_TO_V17.6"

    print("Blocked V20.1 safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 4 — Capital insufficient for a full lot
    # ---------------------------------------------------------

    v20_result = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=5000,
    )

    result = integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=market_data[:1],
        usable_capital=5000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    reconciliation = result["V17.7 Reconciliation"]

    assert reconciliation["Successful Candidates"] == 0
    assert reconciliation["Blocked Candidates"] == 1

    item = reconciliation["Reconciliations"][0]

    assert item["Status"] == "RECONCILIATION_BLOCKED"
    assert item["Reconciled Quantity"] == 0
    assert item["Uncommitted Capital"] == 5000
    assert item["Order Placement Permitted"] is False

    print("Insufficient quantity capital safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 5 — Invalid contract
    # ---------------------------------------------------------

    v20_result = qualify_capital_allocation(
        build_opportunity("NIFTY26SEP25000CE"),
        priority=1,
        requested_allocation=20000,
    )

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

    result = integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=invalid_market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    reconciliation = result["V17.7 Reconciliation"]

    assert reconciliation["Successful Candidates"] == 0
    assert reconciliation["Blocked Candidates"] == 1
    assert (
        reconciliation["Reconciliations"][0]["Status"]
        == "RECONCILIATION_BLOCKED"
    )

    print("Invalid contract safeguard: PASS")

    # ---------------------------------------------------------
    # Final architecture safeguards
    # ---------------------------------------------------------

    assert result["Priority Source"] == "DECISION_RISK_LAYER"
    assert result["Automatic Ranking"] is False
    assert result["Capital Reassignment"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Broker Communication"] is False
    assert result["Wisdom Before Wealth"] is True

    print()
    print("V20.1 -> V17.6 -> V17.7 INTEGRATION: ALL TESTS PASSED")
    print("No Priority generation.")
    print("No Requested Allocation generation.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()

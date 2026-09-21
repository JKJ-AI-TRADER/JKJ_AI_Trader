"""
JKJ AI Trader
V20.1 -> V17.6 -> V17.7 -> V17.8.1 Integration Test
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


def build_v20_1_v17_7_result():
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

    return integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )


def test_successful_paper_order():
    v17_7_result = build_v20_1_v17_7_result()

    assert (
        v17_7_result["Status"]
        == "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    request = result["Execution Request"][
        "Execution Request"
    ]

    assert request["Transaction Type"] == "BUY"
    assert request["Order Type"] == "MARKET"
    assert request["Product"] == "MIS"
    assert request["Quantity"] == 195
    assert request["Lot Size"] == 65
    assert request["Entry Price Reference"] == 100
    assert request["Allocated Capital"] == 20000
    assert request["Required Capital"] == 19500
    assert request["Contract Valid"] is True
    assert request["Execution Ready"] is True
    assert request["Order Placement Permitted"] is False
    assert request["Broker Communication"] is False

    paper_order = result["V17.8.1 Paper Order"]

    assert (
        paper_order["Status"]
        == "PAPER_ORDER_ACCEPTED"
    )

    order = paper_order["Paper Order"]

    assert order["Trading Symbol"] == (
        "NIFTY26SEP25000CE"
    )
    assert order["Instrument Token"] == 123456
    assert order["Quantity"] == 195
    assert order["Lot Size"] == 65
    assert order["Transaction Type"] == "BUY"
    assert order["Order Type"] == "MARKET"
    assert order["Product"] == "MIS"
    assert order["Paper Status"] == "PAPER_ACCEPTED"


def test_blocked_v17_7_result():
    blocked_result = {
        "Status": "V20_1_V17_7_INTEGRATION_BLOCKED",
        "Reason": "Test blocked result",
    }

    result = integrate_v20_1_to_v17_8(
        blocked_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_INTEGRATION_BLOCKED"
    )

    assert result["Paper Order"] is None
    assert result["Order Placement Permitted"] is False


def test_multiple_successful_candidates_blocked():
    v17_7_result = build_v20_1_v17_7_result()

    reconciliation = v17_7_result[
        "V17.7 Reconciliation"
    ]

    original = reconciliation["Reconciliations"][0]

    reconciliation["Reconciliations"].append(
        dict(original)
    )

    result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_INTEGRATION_BLOCKED"
    )


def test_live_order_safeguard():
    v17_7_result = build_v20_1_v17_7_result()

    v17_7_result[
        "V17.7 Reconciliation"
    ]["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    v17_7_result = build_v20_1_v17_7_result()

    v17_7_result[
        "V17.7 Reconciliation"
    ]["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_INTEGRATION_BLOCKED"
    )


def run_test():
    test_successful_paper_order()
    print("Successful V20.1 -> V17.7 -> V17.8.1 paper order: PASS")

    test_blocked_v17_7_result()
    print("Blocked V17.7 safeguard: PASS")

    test_multiple_successful_candidates_blocked()
    print("Multiple successful candidates safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 "
        "INTEGRATION: ALL TESTS PASSED"
    )
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

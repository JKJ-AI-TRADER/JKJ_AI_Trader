"""
JKJ AI Trader
V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> V17.8.2 Integration Test
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


def build_v20_1_v17_8_result():
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

    v17_7_result = integrate_v20_1_to_v17_7(
        v20_1_results=[v20_result],
        candidate_market_data=market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    return integrate_v20_1_to_v17_8(
        v17_7_result
    )


def test_successful_paper_fill():
    v17_8_result = build_v20_1_v17_8_result()

    assert (
        v17_8_result["Status"]
        == "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    paper_fill_result = result["V17.8.2 Paper Fill"]

    assert (
        paper_fill_result["Status"]
        == "PAPER_FILL_COMPLETE"
    )

    fill = paper_fill_result["Paper Fill"]

    assert fill["Trading Symbol"] == (
        "NIFTY26SEP25000CE"
    )
    assert fill["Instrument Token"] == 123456
    assert fill["Transaction Type"] == "BUY"
    assert fill["Requested Quantity"] == 195
    assert fill["Filled Quantity"] == 195
    assert fill["Lot Size"] == 65
    assert fill["Entry Price Reference"] == 100
    assert fill["Fill Price"] == 100
    assert fill["Required Capital at Request"] == 19500
    assert fill["Simulated Fill Capital"] == 19500
    assert fill["Fill Type"] == "FULL"
    assert fill["Paper Fill Status"] == "FILLED"


def test_custom_fill_price():
    v17_8_result = build_v20_1_v17_8_result()

    result = integrate_v20_1_to_v17_8_2(
        v17_8_result,
        fill_price=102,
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    fill = result["V17.8.2 Paper Fill"]["Paper Fill"]

    assert fill["Fill Price"] == 102
    assert fill["Filled Quantity"] == 195
    assert fill["Simulated Fill Capital"] == 19890


def test_blocked_v17_8_result():
    blocked_result = {
        "Status": "V20_1_V17_8_INTEGRATION_BLOCKED",
        "Reason": "Test blocked result",
    }

    result = integrate_v20_1_to_v17_8_2(
        blocked_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )

    assert result["V17.8.2 Paper Fill"] is None


def test_live_order_safeguard():
    v17_8_result = build_v20_1_v17_8_result()

    v17_8_result["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    v17_8_result = build_v20_1_v17_8_result()

    v17_8_result["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    v17_8_result = build_v20_1_v17_8_result()

    v17_8_result["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )


def run_test():
    test_successful_paper_fill()
    print("Successful V20.1 -> V17.8.2 paper fill: PASS")

    test_custom_fill_price()
    print("Custom fill price: PASS")

    test_blocked_v17_8_result()
    print("Blocked V17.8.1 safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> V17.8.2 "
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
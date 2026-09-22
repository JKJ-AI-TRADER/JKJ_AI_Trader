"""
JKJ AI Trader
V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> V17.8.2 -> V17.8.3 Integration Test
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

from nifty_option_v20_1_v17_8_3_integration import (
    integrate_v20_1_to_v17_8_3,
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


def build_v20_1_v17_8_2_result():
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

    v17_8_result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    return integrate_v20_1_to_v17_8_2(
        v17_8_result
    )


def test_successful_paper_position():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    assert (
        v17_8_2_result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    result = integrate_v20_1_to_v17_8_3(
        v17_8_2_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_COMPLETE"
    )

    position_result = result["V17.8.3 Paper Position"]

    assert (
        position_result["Status"]
        == "PAPER_POSITION_CREATED"
    )

    position = position_result["Paper Position"]

    assert position["Trading Symbol"] == (
        "NIFTY26SEP25000CE"
    )
    assert position["Instrument Token"] == 123456
    assert position["Position Type"] == "LONG"
    assert position["Transaction Type"] == "BUY"
    assert position["Quantity"] == 195
    assert position["Lot Size"] == 65
    assert position["Entry Price"] == 100
    assert position["Capital Used"] == 19500
    assert position["Paper Status"] == "PAPER_POSITION_OPEN"


def test_blocked_v17_8_2_result():
    blocked_result = {
        "Status": "V20_1_V17_8_2_INTEGRATION_BLOCKED",
        "Reason": "Test blocked result",
    }

    result = integrate_v20_1_to_v17_8_3(
        blocked_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_BLOCKED"
    )

    assert result["V17.8.3 Paper Position"] is None


def test_live_order_safeguard():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    v17_8_2_result["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_3(
        v17_8_2_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    v17_8_2_result["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_3(
        v17_8_2_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    v17_8_2_result["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_3(
        v17_8_2_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_BLOCKED"
    )


def run_test():
    test_successful_paper_position()
    print("Successful V20.1 -> V17.8.3 paper position: PASS")

    test_blocked_v17_8_2_result()
    print("Blocked V17.8.2 safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> "
        "V17.8.2 -> V17.8.3 INTEGRATION: ALL TESTS PASSED"
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
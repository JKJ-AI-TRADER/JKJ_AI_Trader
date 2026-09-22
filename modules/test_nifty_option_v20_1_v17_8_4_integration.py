"""
JKJ AI Trader
V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> V17.8.2
-> V17.8.3 -> V17.8.4 Integration Test
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

from nifty_option_v20_1_v17_8_4_integration import (
    integrate_v20_1_to_v17_8_4,
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


def build_v20_1_v17_8_3_result():
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

    v17_8_2_result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    return integrate_v20_1_to_v17_8_3(
        v17_8_2_result
    )


def test_successful_paper_audit():
    v17_8_3_result = build_v20_1_v17_8_3_result()

    assert (
        v17_8_3_result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_COMPLETE"
    )

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_COMPLETE"
    )

    audit_result = result["V17.8.4 Paper Audit"]

    assert (
        audit_result["Status"]
        == "PAPER_EXECUTION_AUDIT_COMPLETE"
    )

    assert audit_result["Read Only"] is True

    audit = audit_result["Audit Record"]

    assert audit["Trading Symbol"] == (
        "NIFTY26SEP25000CE"
    )
    assert audit["Instrument Token"] == 123456
    assert audit["Position Type"] == "LONG"
    assert audit["Transaction Type"] == "BUY"
    assert audit["Quantity"] == 195
    assert audit["Lot Size"] == 65
    assert audit["Entry Price"] == 100
    assert audit["Capital Used"] == 19500
    assert audit["Audit Status"] == (
        "PAPER_EXECUTION_AUDITED"
    )
    assert audit["Audit Scope"] == "POSITION_CREATION"
    assert audit["Read Only"] is True


def test_blocked_v17_8_3_result():
    blocked_result = {
        "Status": "V20_1_V17_8_3_INTEGRATION_BLOCKED",
        "Reason": "Test blocked result",
    }

    result = integrate_v20_1_to_v17_8_4(
        blocked_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )

    assert result["V17.8.4 Paper Audit"] is None


def test_live_order_safeguard():
    v17_8_3_result = build_v20_1_v17_8_3_result()

    v17_8_3_result["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    v17_8_3_result = build_v20_1_v17_8_3_result()

    v17_8_3_result["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    v17_8_3_result = build_v20_1_v17_8_3_result()

    v17_8_3_result["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )


def test_read_only_boundary():
    v17_8_3_result = build_v20_1_v17_8_3_result()

    original_position = dict(
        v17_8_3_result["V17.8.3 Paper Position"][
            "Paper Position"
        ]
    )

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    current_position = (
        v17_8_3_result["V17.8.3 Paper Position"][
            "Paper Position"
        ]
    )

    assert current_position == original_position

    assert (
        result["V17.8.4 Paper Audit"]["Read Only"]
        is True
    )


def run_test():
    test_successful_paper_audit()
    print("Successful V20.1 -> V17.8.4 paper audit: PASS")

    test_blocked_v17_8_3_result()
    print("Blocked V17.8.3 safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    test_read_only_boundary()
    print("Read-only audit boundary: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> "
        "V17.8.2 -> V17.8.3 -> V17.8.4 "
        "INTEGRATION: ALL TESTS PASSED"
    )
    print("No Priority generation.")
    print("No Requested Allocation generation.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No position modification.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
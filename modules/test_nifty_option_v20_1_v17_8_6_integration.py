"""
JKJ AI Trader
V20.1 -> V17.8.6 V15 Entry Boundary Integration Test
"""

from nifty_option_v20_1_v17_8_5_integration import (
    integrate_v20_1_to_v17_8_5,
)

from nifty_option_v20_1_v17_8_2_integration import (
    integrate_v20_1_to_v17_8_2,
)

from nifty_option_v20_1_v17_8_integration import (
    integrate_v20_1_to_v17_8,
)

from nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
)

from nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)

from nifty_option_v20_1_v17_8_6_integration import (
    integrate_v20_1_to_v17_8_6,
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


def build_contract(symbol):
    return {
        "Status": "CONTRACT_VALIDATED",
        "Lot Size": 65,
        "Trading Symbol": symbol,
        "Instrument Token": 123456,
        "Contract Identity Valid": True,
    }


def build_v15_qualification(symbol):
    return {
        "Status": "QUALIFIED",
        "Paper Trade Permission": "PERMITTED",
        "Trading Symbol": symbol,
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 25000,
        "Option Type": "CE",
        "Entry Price": 100.0,
        "Stop Price": 90.0,
        "Target 1": 120.0,
        "Target 2": 140.0,
        "Target 3": 160.0,
        "Risk Reward 1": 2.0,
        "Risk Reward 2": 4.0,
        "Risk Reward 3": 6.0,
        "Entry Qualification": "QUALIFIED",
        "Qualification Reason": "V14.5 exit-qualified setup",
    }


def build_v20_1_v17_8_5_result():
    symbol = "NIFTY26SEP25000CE"

    v20_result = qualify_capital_allocation(
        build_opportunity(symbol),
        priority=1,
        requested_allocation=20000,
    )

    market_data = [
        {
            "Candidate": symbol,
            "Entry Price": 100,
            "Contract Validation": build_contract(symbol),
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

    v15_qualification = build_v15_qualification(symbol)

    return integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        v15_qualification,
        "JKJ-TRADE-001",
        entry_time="2026-09-22T09:30:00",
    )


def test_successful_boundary_validation():
    result = integrate_v20_1_to_v17_8_6(
        build_v20_1_v17_8_5_result()
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_COMPLETE"
    )

    assert (
        result["V15 Entry Boundary"]["Status"]
        == "V15_ENTRY_BOUNDARY_VALIDATED"
    )

    payload = result["V15 Entry Payload"]

    assert payload["Trade ID"] == "JKJ-TRADE-001"
    assert payload["Trading Symbol"] == "NIFTY26SEP25000CE"
    assert payload["Instrument Type"] == "OPTION"
    assert payload["Underlying"] == "NIFTY"
    assert payload["Expiry"] == "2026-09-22"
    assert payload["Strike"] == 25000
    assert payload["Option Type"] == "CE"
    assert payload["Entry Price"] == 100
    assert payload["Quantity"] == 195
    assert payload["Stop Loss"] == 90.0
    assert payload["Target"] == 120.0
    assert payload["Target1"] == 120.0
    assert payload["Target2"] == 140.0
    assert payload["Target3"] == 160.0
    assert payload["RR1"] == 2.0
    assert payload["RR2"] == 4.0
    assert payload["RR3"] == 6.0

    assert result["V15 Call Permitted"] is False
    assert result["V11 Call Permitted"] is False
    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False


def test_incomplete_v17_8_5_blocked():
    result = integrate_v20_1_to_v17_8_6({
        "Status": "V20_1_V17_8_5_INTEGRATION_BLOCKED",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
    })

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_live_order_safeguard():
    source = build_v20_1_v17_8_5_result()
    source["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    source = build_v20_1_v17_8_5_result()
    source["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    source = build_v20_1_v17_8_5_result()
    source["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_automatic_ranking_safeguard():
    source = build_v20_1_v17_8_5_result()
    source["Automatic Ranking"] = True

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_priority_source_safeguard():
    source = build_v20_1_v17_8_5_result()
    source["Priority Source"] = "AUTOMATIC"

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_mapped_entry_missing():
    source = build_v20_1_v17_8_5_result()
    source["V17.8.5 Result"].pop("V15 Entry Mapping")

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def test_boundary_rejects_invalid_mapped_entry():
    source = build_v20_1_v17_8_5_result()

    mapping = source["V17.8.5 Result"]["V15 Entry Mapping"]
    mapping["Contract Valid"] = False

    result = integrate_v20_1_to_v17_8_6(source)

    assert (
        result["Status"]
        == "V20_1_V17_8_6_INTEGRATION_BLOCKED"
    )


def run_test():
    test_successful_boundary_validation()
    print("Successful V20.1 -> V17.8.6 boundary validation: PASS")

    test_incomplete_v17_8_5_blocked()
    print("Incomplete V17.8.5 safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    test_automatic_ranking_safeguard()
    print("Automatic ranking safeguard: PASS")

    test_priority_source_safeguard()
    print("Priority source safeguard: PASS")

    test_mapped_entry_missing()
    print("Missing mapped entry safeguard: PASS")

    test_boundary_rejects_invalid_mapped_entry()
    print("V17.8.6 boundary validation safeguard: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> "
        "V17.8.2 -> V17.8.5 -> V17.8.6 "
        "INTEGRATION: ALL TESTS PASSED"
    )
    print("No Priority generation.")
    print("No Requested Allocation generation.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No V15 call.")
    print("No V11 call.")
    print("No paper trade opening.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
    
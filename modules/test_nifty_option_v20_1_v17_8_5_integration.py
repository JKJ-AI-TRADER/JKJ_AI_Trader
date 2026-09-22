"""
JKJ AI Trader
V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> V17.8.2
-> V17.8.5 Integration Test
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

from nifty_option_v20_1_v17_8_5_integration import (
    integrate_v20_1_to_v17_8_5,
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


def build_v20_1_v17_8_2_result():
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
            "Contract Validation": build_contract(
                symbol,
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


def test_successful_v15_entry_mapping():
    symbol = "NIFTY26SEP25000CE"

    v17_8_2_result = build_v20_1_v17_8_2_result()

    assert (
        v17_8_2_result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(symbol),
        "JKJ-TRADE-001",
        entry_time="2026-09-22T09:30:00",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Status"] == "MAPPED"
    assert mapping["Trade ID"] == "JKJ-TRADE-001"
    assert mapping["Trading Symbol"] == symbol
    assert mapping["Instrument Type"] == "OPTION"
    assert mapping["Underlying"] == "NIFTY"
    assert mapping["Expiry"] == "2026-09-22"
    assert mapping["Strike"] == 25000
    assert mapping["Option Type"] == "CE"
    assert mapping["Quantity"] == 195

    # Actual V17.8 fill price is authoritative for execution entry.
    assert mapping["Entry Price"] == 100
    assert mapping["Qualified Entry Price"] == 100.0

    # V15 remains authoritative for risk/exit structure.
    assert mapping["Stop Loss"] == 90.0
    assert mapping["Target 1"] == 120.0
    assert mapping["Target 2"] == 140.0
    assert mapping["Target 3"] == 160.0
    assert mapping["Risk Reward 1"] == 2.0
    assert mapping["Risk Reward 2"] == 4.0
    assert mapping["Risk Reward 3"] == 6.0
    assert mapping["Entry Time"] == "2026-09-22T09:30:00"


def test_actual_fill_price_overrides_qualified_entry():
    symbol = "NIFTY26SEP25000CE"

    v17_8_2_result = build_v20_1_v17_8_2_result()

    fill = v17_8_2_result["V17.8.2 Paper Fill"]["Paper Fill"]
    fill["Fill Price"] = 102

    # Keep the simulated capital consistent with the changed fill.
    fill["Simulated Fill Capital"] = 102 * 195

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(symbol),
        "JKJ-TRADE-002",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Entry Price"] == 102
    assert mapping["Qualified Entry Price"] == 100.0


def test_symbol_mismatch_blocked():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    qualification = build_v15_qualification(
        "NIFTY26SEP25000PE"
    )

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        qualification,
        "JKJ-TRADE-003",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_unqualified_v15_blocked():
    symbol = "NIFTY26SEP25000CE"

    v17_8_2_result = build_v20_1_v17_8_2_result()

    qualification = build_v15_qualification(symbol)
    qualification["Status"] = "REJECTED"

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        qualification,
        "JKJ-TRADE-004",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_live_order_safeguard():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    v17_8_2_result["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification("NIFTY26SEP25000CE"),
        "JKJ-TRADE-005",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    v17_8_2_result["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification("NIFTY26SEP25000CE"),
        "JKJ-TRADE-006",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    v17_8_2_result = build_v20_1_v17_8_2_result()

    v17_8_2_result["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification("NIFTY26SEP25000CE"),
        "JKJ-TRADE-007",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_v15_risk_fields_remain_authoritative():
    symbol = "NIFTY26SEP25000CE"

    v17_8_2_result = build_v20_1_v17_8_2_result()

    qualification = build_v15_qualification(symbol)
    qualification["Stop Price"] = 88.0
    qualification["Target 1"] = 125.0

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        qualification,
        "JKJ-TRADE-008",
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Stop Loss"] == 88.0
    assert mapping["Target 1"] == 125.0


def run_test():
    test_successful_v15_entry_mapping()
    print("Successful V20.1 -> V17.8.5 V15 mapping: PASS")

    test_actual_fill_price_overrides_qualified_entry()
    print("Actual fill price mapping: PASS")

    test_symbol_mismatch_blocked()
    print("Symbol identity safeguard: PASS")

    test_unqualified_v15_blocked()
    print("V15 qualification safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    test_v15_risk_fields_remain_authoritative()
    print("V15 risk/exit authority safeguard: PASS")

    print()
    print(
        "V20.1 -> V17.6 -> V17.7 -> V17.8.1 -> "
        "V17.8.2 -> V17.8.5 INTEGRATION: ALL TESTS PASSED"
    )
    print("No Priority generation.")
    print("No Requested Allocation generation.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No V15/V11 trade opening.")
    print("No Stop/Target generation.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
"""
JKJ AI Trader
Real-Market -> V20.1 -> V17.6 -> V17.7 -> V17.8.1
-> V17.8.2 -> V17.8.5 Integration Test
"""

from modules.nifty_option_real_market_v20_1_integration import (
    integrate_real_market_to_v20_1,
)

from modules.nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
)

from modules.nifty_option_v20_1_v17_8_integration import (
    integrate_v20_1_to_v17_8,
)

from modules.nifty_option_v20_1_v17_8_2_integration import (
    integrate_v20_1_to_v17_8_2,
)

from modules.nifty_option_v20_1_v17_8_5_integration import (
    integrate_v20_1_to_v17_8_5,
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


def build_full_real_market_v17_8_2_result():
    (
        entry_risk_context,
        stop_loss_context,
        exit_qualification,
        paper_qualification,
    ) = qualified_inputs()

    real_market_result = integrate_real_market_to_v20_1(
        entry_risk_context=entry_risk_context,
        stop_loss_context=stop_loss_context,
        exit_qualification=exit_qualification,
        paper_qualification=paper_qualification,
        priority=1,
        requested_allocation=20000,
    )

    assert (
        real_market_result["Status"]
        == "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
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
        v20_1_results=[
            real_market_result["V20.1 Result"]
        ],
        candidate_market_data=market_data,
        usable_capital=30000,
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    assert (
        v17_7_result["Status"]
        == "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    v17_8_result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert (
        v17_8_result["Status"]
        == "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    v17_8_2_result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    assert (
        v17_8_2_result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    return (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
    )


def test_successful_v15_entry_mapping():
    symbol = "NIFTY26SEP25000CE"

    (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    assert (
        real_market_result["Status"]
        == "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    assert (
        v17_7_result["Status"]
        == "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    assert (
        v17_8_result["Status"]
        == "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    assert (
        v17_8_2_result["Status"]
        == "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(symbol),
        "JKJ-REAL-TRADE-001",
        entry_time="2026-09-22T09:30:00",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Status"] == "MAPPED"
    assert mapping["Trade ID"] == "JKJ-REAL-TRADE-001"
    assert mapping["Trading Symbol"] == symbol
    assert mapping["Instrument Type"] == "OPTION"
    assert mapping["Underlying"] == "NIFTY"
    assert mapping["Expiry"] == "2026-09-22"
    assert mapping["Strike"] == 25000
    assert mapping["Option Type"] == "CE"
    assert mapping["Quantity"] == 195

    # Actual V17.8.2 fill price remains authoritative.
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

    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    fill = v17_8_2_result[
        "V17.8.2 Paper Fill"
    ]["Paper Fill"]

    fill["Fill Price"] = 102
    fill["Simulated Fill Capital"] = 102 * 195

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(symbol),
        "JKJ-REAL-TRADE-002",
        entry_time="2026-09-22T09:31:00",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Entry Price"] == 102
    assert mapping["Qualified Entry Price"] == 100.0


def test_symbol_mismatch_blocked():
    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    qualification = build_v15_qualification(
        "NIFTY26SEP25000PE"
    )

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        qualification,
        "JKJ-REAL-TRADE-003",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_unqualified_v15_blocked():
    symbol = "NIFTY26SEP25000CE"

    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    qualification = build_v15_qualification(symbol)
    qualification["Status"] = "REJECTED"

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        qualification,
        "JKJ-REAL-TRADE-004",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_live_order_safeguard():
    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    v17_8_2_result["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(
            "NIFTY26SEP25000CE"
        ),
        "JKJ-REAL-TRADE-005",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    v17_8_2_result["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(
            "NIFTY26SEP25000CE"
        ),
        "JKJ-REAL-TRADE-006",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    v17_8_2_result["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(
            "NIFTY26SEP25000CE"
        ),
        "JKJ-REAL-TRADE-007",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_BLOCKED"
    )


def test_v15_risk_fields_remain_authoritative():
    symbol = "NIFTY26SEP25000CE"

    (
        _,
        _,
        _,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    qualification = build_v15_qualification(symbol)
    qualification["Stop Price"] = 88.0
    qualification["Target 1"] = 125.0

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        qualification,
        "JKJ-REAL-TRADE-008",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Stop Loss"] == 88.0
    assert mapping["Target 1"] == 125.0


def test_end_to_end_paper_mapping_safety_boundary():
    (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
    ) = build_full_real_market_v17_8_2_result()

    result = integrate_v20_1_to_v17_8_5(
        v17_8_2_result,
        build_v15_qualification(
            "NIFTY26SEP25000CE"
        ),
        "JKJ-REAL-TRADE-009",
        entry_time="2026-09-22T09:35:00",
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    )

    assert (
        real_market_result["Automatic Ranking"]
        is False
    )
    assert (
        real_market_result["Broker Communication"]
        is False
    )
    assert (
        real_market_result["Order Placement Permitted"]
        is False
    )

    assert (
        v17_7_result["Automatic Ranking"]
        is False
    )
    assert (
        v17_7_result["Capital Reassignment"]
        is False
    )
    assert (
        v17_7_result["Broker Communication"]
        is False
    )
    assert (
        v17_7_result["Order Placement Permitted"]
        is False
    )

    assert (
        v17_8_result["Paper Execution"]
        is True
    )
    assert (
        v17_8_result["Broker Communication"]
        is False
    )
    assert (
        v17_8_result["Order Placement Permitted"]
        is False
    )

    assert (
        v17_8_2_result["Paper Execution"]
        is True
    )
    assert (
        v17_8_2_result["Broker Communication"]
        is False
    )
    assert (
        v17_8_2_result["Order Placement Permitted"]
        is False
    )
    assert (
        v17_8_2_result["Capital Reassignment"]
        is False
    )
    assert (
        v17_8_2_result["Automatic Ranking"]
        is False
    )

    assert (
        result["Paper Execution"]
        is True
    )
    assert (
        result["Broker Communication"]
        is False
    )
    assert (
        result["Order Placement Permitted"]
        is False
    )
    assert (
        result["Capital Reassignment"]
        is False
    )
    assert (
        result["Automatic Ranking"]
        is False
    )
    assert (
        result["Wisdom Before Wealth"]
        is True
    )


def run_test():
    test_successful_v15_entry_mapping()
    print(
        "Real-Market -> V20.1 -> V17.6 -> V17.7 -> "
        "V17.8.1 -> V17.8.2 -> V17.8.5 "
        "V15 entry mapping: PASS"
    )

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

    test_end_to_end_paper_mapping_safety_boundary()
    print("End-to-end paper mapping safety boundary: PASS")

    print()
    print(
        "REAL-MARKET -> V20.1 -> V17.6 -> V17.7 -> "
        "V17.8.1 -> V17.8.2 -> V17.8.5 "
        "INTEGRATION: ALL TESTS PASSED"
    )
    print("Priority explicitly supplied.")
    print("Requested allocation explicitly supplied.")
    print("V17.6 performed policy allocation.")
    print("V17.7 performed quantity/contract reconciliation.")
    print("V17.8.1 created a paper order.")
    print("V17.8.2 created a simulated paper fill.")
    print("V17.8.5 mapped the paper fill to the V15 entry boundary.")
    print("No V15/V11 trade opening.")
    print("No Stop/Target generation.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha communication.")
    print("No live order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
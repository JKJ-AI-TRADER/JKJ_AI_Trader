"""
JKJ AI Trader
Real-Market -> V20.1 -> V17.6 -> V17.7 -> V17.8.1
-> V17.8.2 -> V17.8.3 -> V17.8.4 Integration Test
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

from modules.nifty_option_v20_1_v17_8_3_integration import (
    integrate_v20_1_to_v17_8_3,
)

from modules.nifty_option_v20_1_v17_8_4_integration import (
    integrate_v20_1_to_v17_8_4,
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


def build_full_audit_chain():
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

    v17_8_3_result = integrate_v20_1_to_v17_8_3(
        v17_8_2_result
    )

    assert (
        v17_8_3_result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_COMPLETE"
    )

    v17_8_4_result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    return (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
        v17_8_3_result,
        v17_8_4_result,
    )


def test_full_real_market_to_paper_audit():
    (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
        v17_8_3_result,
        v17_8_4_result,
    ) = build_full_audit_chain()

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

    assert (
        v17_8_3_result["Status"]
        == "V20_1_V17_8_3_INTEGRATION_COMPLETE"
    )

    assert (
        v17_8_4_result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_COMPLETE"
    )

    audit_result = v17_8_4_result[
        "V17.8.4 Paper Audit"
    ]

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


def test_blocked_v17_8_3_safeguard():
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
    (
        _,
        _,
        _,
        _,
        v17_8_3_result,
        _,
    ) = build_full_audit_chain()

    v17_8_3_result["Order Placement Permitted"] = True

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )


def test_broker_communication_safeguard():
    (
        _,
        _,
        _,
        _,
        v17_8_3_result,
        _,
    ) = build_full_audit_chain()

    v17_8_3_result["Broker Communication"] = True

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )


def test_capital_reassignment_safeguard():
    (
        _,
        _,
        _,
        _,
        v17_8_3_result,
        _,
    ) = build_full_audit_chain()

    v17_8_3_result["Capital Reassignment"] = True

    result = integrate_v20_1_to_v17_8_4(
        v17_8_3_result
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_BLOCKED"
    )


def test_read_only_audit_boundary():
    (
        _,
        _,
        _,
        _,
        v17_8_3_result,
        v17_8_4_result,
    ) = build_full_audit_chain()

    original_position = dict(
        v17_8_3_result["V17.8.3 Paper Position"][
            "Paper Position"
        ]
    )

    assert (
        v17_8_4_result["Status"]
        == "V20_1_V17_8_4_INTEGRATION_COMPLETE"
    )

    current_position = (
        v17_8_3_result["V17.8.3 Paper Position"][
            "Paper Position"
        ]
    )

    assert current_position == original_position

    assert (
        v17_8_4_result["V17.8.4 Paper Audit"][
            "Read Only"
        ]
        is True
    )

    assert (
        v17_8_4_result["Order Placement Permitted"]
        is False
    )

    assert (
        v17_8_4_result["Broker Communication"]
        is False
    )


def test_end_to_end_paper_audit_safety_boundary():
    (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
        v17_8_3_result,
        v17_8_4_result,
    ) = build_full_audit_chain()

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
        v17_8_3_result["Paper Execution"]
        is True
    )
    assert (
        v17_8_3_result["Broker Communication"]
        is False
    )
    assert (
        v17_8_3_result["Order Placement Permitted"]
        is False
    )
    assert (
        v17_8_3_result["Capital Reassignment"]
        is False
    )
    assert (
        v17_8_3_result["Automatic Ranking"]
        is False
    )

    assert (
        v17_8_4_result["Paper Execution"]
        is True
    )
    assert (
        v17_8_4_result["Broker Communication"]
        is False
    )
    assert (
        v17_8_4_result["Order Placement Permitted"]
        is False
    )
    assert (
        v17_8_4_result["Capital Reassignment"]
        is False
    )
    assert (
        v17_8_4_result["Automatic Ranking"]
        is False
    )
    assert (
        v17_8_4_result["Read Only"]
        is True
    )
    assert (
        v17_8_4_result["Wisdom Before Wealth"]
        is True
    )


def run_test():
    test_full_real_market_to_paper_audit()
    print(
        "Real-Market -> V20.1 -> V17.6 -> V17.7 -> "
        "V17.8.1 -> V17.8.2 -> V17.8.3 -> V17.8.4 "
        "paper audit: PASS"
    )

    test_blocked_v17_8_3_safeguard()
    print("Blocked V17.8.3 safeguard: PASS")

    test_live_order_safeguard()
    print("Live order placement safeguard: PASS")

    test_broker_communication_safeguard()
    print("Broker communication safeguard: PASS")

    test_capital_reassignment_safeguard()
    print("Capital reassignment safeguard: PASS")

    test_read_only_audit_boundary()
    print("Read-only audit boundary: PASS")

    test_end_to_end_paper_audit_safety_boundary()
    print("End-to-end paper audit safety boundary: PASS")

    print()
    print(
        "REAL-MARKET -> V20.1 -> V17.6 -> V17.7 -> "
        "V17.8.1 -> V17.8.2 -> V17.8.3 -> V17.8.4 "
        "INTEGRATION: ALL TESTS PASSED"
    )
    print("Priority explicitly supplied.")
    print("Requested allocation explicitly supplied.")
    print("V17.6 performed policy allocation.")
    print("V17.7 performed quantity/contract reconciliation.")
    print("V17.8.1 created a paper order.")
    print("V17.8.2 created a simulated paper fill.")
    print("V17.8.3 created a paper position.")
    print("V17.8.4 performed a read-only paper execution audit.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No position modification.")
    print("No Zerodha communication.")
    print("No live order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
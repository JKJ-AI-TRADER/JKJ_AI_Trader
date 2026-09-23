"""
JKJ AI Trader
Real-Market → V20.1 → V17.6 → V17.7 → V17.8.1 → V17.8.2
Integration Test

Purpose:
    Validate the controlled handoff from an already-qualified
    real-market Decision/Risk opportunity through V20.1,
    V17.6 capital allocation, V17.7 quantity/contract
    reconciliation, V17.8.1 paper order, and V17.8.2
    paper fill.

This test does NOT:
- generate priority
- generate requested allocation
- rank candidates
- change capital allocation policy
- calculate quantity itself
- place live orders
- communicate with Zerodha
- modify V16.1
- modify V20.1
- modify V17.6
- modify V17.7
- modify V17.8
- modify main.py

Wisdom Before Wealth.
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


def qualified_inputs(symbol="NIFTY26SEP25000CE"):

    entry_risk_context = {
        "Status": "EVALUATED",
        "Trading Symbol": symbol,
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
    }

    stop_loss_context = {
        "Status": "EVALUATED",
        "Trading Symbol": symbol,
        "Stop-Loss Context": "STOP_SUPPORTED",
    }

    exit_qualification = {
        "Status": "EVALUATED",
        "Trading Symbol": symbol,
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


def build_full_paper_execution_chain():

    inputs = qualified_inputs()

    # ---------------------------------------------------------
    # Real-Market → V20.1
    # ---------------------------------------------------------

    real_market_result = integrate_real_market_to_v20_1(
        *inputs,
        priority=1,
        requested_allocation=20000,
    )

    assert real_market_result["Status"] == (
        "REAL_MARKET_V20_1_INTEGRATION_COMPLETE"
    )

    v20_result = real_market_result["V20.1 Result"]

    assert v20_result["Status"] == (
        "CAPITAL_ALLOCATION_QUALIFIED"
    )

    # ---------------------------------------------------------
    # V20.1 → V17.7
    # ---------------------------------------------------------

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

    assert v17_7_result["Status"] == (
        "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    # ---------------------------------------------------------
    # V17.7 → V17.8.1
    # ---------------------------------------------------------

    v17_8_result = integrate_v20_1_to_v17_8(
        v17_7_result
    )

    assert v17_8_result["Status"] == (
        "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    assert v17_8_result["Paper Execution"] is True
    assert v17_8_result["Broker Communication"] is False
    assert v17_8_result["Order Placement Permitted"] is False

    # ---------------------------------------------------------
    # V17.8.1 → V17.8.2
    # ---------------------------------------------------------

    v17_8_2_result = integrate_v20_1_to_v17_8_2(
        v17_8_result
    )

    return (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
    )


def run_test():

    print(
        "\nJKJ AI Trader — "
        "Real-Market → V20.1 → V17.6 → V17.7 → "
        "V17.8.1 → V17.8.2 Integration Test"
    )
    print("=" * 110)

    # ---------------------------------------------------------
    # TEST 1 — Complete real-market → paper-fill chain
    # ---------------------------------------------------------

    (
        real_market_result,
        v17_7_result,
        v17_8_result,
        v17_8_2_result,
    ) = build_full_paper_execution_chain()

    assert v17_8_2_result["Status"] == (
        "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    paper_fill_result = v17_8_2_result[
        "V17.8.2 Paper Fill"
    ]

    assert paper_fill_result["Status"] == (
        "PAPER_FILL_COMPLETE"
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

    print(
        "Real-Market → V20.1 → V17.6 → V17.7 → "
        "V17.8.1 → V17.8.2 full fill: PASS"
    )

    # ---------------------------------------------------------
    # TEST 2 — Custom paper fill price
    # ---------------------------------------------------------

    custom_fill_result = integrate_v20_1_to_v17_8_2(
        v17_8_result,
        fill_price=102,
    )

    assert custom_fill_result["Status"] == (
        "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    )

    custom_fill = custom_fill_result[
        "V17.8.2 Paper Fill"
    ]["Paper Fill"]

    assert custom_fill["Fill Price"] == 102
    assert custom_fill["Filled Quantity"] == 195
    assert custom_fill["Simulated Fill Capital"] == 19890

    print("Custom paper fill price: PASS")

    # ---------------------------------------------------------
    # TEST 3 — Blocked V17.8 result
    # ---------------------------------------------------------

    blocked_result = {
        "Status": "V20_1_V17_8_INTEGRATION_BLOCKED",
        "Reason": "Test blocked result",
    }

    blocked_fill_result = integrate_v20_1_to_v17_8_2(
        blocked_result
    )

    assert blocked_fill_result["Status"] == (
        "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )

    assert blocked_fill_result[
        "V17.8.2 Paper Fill"
    ] is None

    print("Blocked V17.8.1 safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 4 — Live order safeguard
    # ---------------------------------------------------------

    live_order_result = dict(v17_8_result)

    live_order_result[
        "Order Placement Permitted"
    ] = True

    blocked_live_result = integrate_v20_1_to_v17_8_2(
        live_order_result
    )

    assert blocked_live_result["Status"] == (
        "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )

    print("Live order placement safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 5 — Broker communication safeguard
    # ---------------------------------------------------------

    broker_result = dict(v17_8_result)

    broker_result[
        "Broker Communication"
    ] = True

    blocked_broker_result = integrate_v20_1_to_v17_8_2(
        broker_result
    )

    assert blocked_broker_result["Status"] == (
        "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )

    print("Broker communication safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 6 — Capital reassignment safeguard
    # ---------------------------------------------------------

    reassignment_result = dict(v17_8_result)

    reassignment_result[
        "Capital Reassignment"
    ] = True

    blocked_reassignment_result = (
        integrate_v20_1_to_v17_8_2(
            reassignment_result
        )
    )

    assert blocked_reassignment_result["Status"] == (
        "V20_1_V17_8_2_INTEGRATION_BLOCKED"
    )

    print("Capital reassignment safeguard: PASS")

    # ---------------------------------------------------------
    # TEST 7 — End-to-end paper execution safety
    # ---------------------------------------------------------

    assert real_market_result[
        "Automatic Ranking"
    ] is False

    assert real_market_result[
        "Broker Communication"
    ] is False

    assert real_market_result[
        "Order Placement Permitted"
    ] is False

    assert v17_7_result[
        "Automatic Ranking"
    ] is False

    assert v17_7_result[
        "Capital Reassignment"
    ] is False

    assert v17_7_result[
        "Broker Communication"
    ] is False

    assert v17_7_result[
        "Order Placement Permitted"
    ] is False

    assert v17_8_result[
        "Paper Execution"
    ] is True

    assert v17_8_result[
        "Broker Communication"
    ] is False

    assert v17_8_result[
        "Order Placement Permitted"
    ] is False

    assert v17_8_2_result[
        "Paper Execution"
    ] is True

    assert v17_8_2_result[
        "Broker Communication"
    ] is False

    assert v17_8_2_result[
        "Order Placement Permitted"
    ] is False

    assert v17_8_2_result[
        "Capital Reassignment"
    ] is False

    assert v17_8_2_result[
        "Automatic Ranking"
    ] is False

    assert v17_8_2_result[
        "Wisdom Before Wealth"
    ] is True

    print(
        "End-to-end paper fill safety boundary: PASS"
    )

    print()
    print(
        "REAL-MARKET → V20.1 → V17.6 → V17.7 → "
        "V17.8.1 → V17.8.2 INTEGRATION: "
        "ALL TESTS PASSED"
    )
    print("Priority explicitly supplied.")
    print("Requested allocation explicitly supplied.")
    print("V17.6 performed policy allocation.")
    print("V17.7 performed quantity/contract reconciliation.")
    print("V17.8.1 created a paper order.")
    print("V17.8.2 created a simulated paper fill.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No Zerodha communication.")
    print("No live order placement.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
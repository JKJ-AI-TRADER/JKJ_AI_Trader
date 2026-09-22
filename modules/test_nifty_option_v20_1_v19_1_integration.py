"""
JKJ AI Trader
V20.1 -> V19.1 Paper Trade Closure Validation Integration Test

Wisdom Before Wealth.
"""

from nifty_option_v20_1_v19_1_integration import (
    integrate_v20_1_to_v19_1,
)


SYMBOL = "NIFTY26SEP25000CE"


def valid_v20_1_v18_1_result():
    return {
        "Status": "V20_1_V18_1_INTEGRATION_COMPLETE",
        "V18.1 Result": {
            "Status": "SYNCHRONIZED",
            "Synchronization Confirmed": True,
            "Cumulative Filled Quantity": 65,
            "Expected Remaining Quantity": 0,
            "V11 Remaining Quantity": 0,
            "Target Stage": "TARGET 3",
            "V11 Event Exit Quantity": 28,
            "Previous Cumulative Filled": 37,
        },
        "Lifecycle Owner": "V15.4 / V11",
        "Trade ID": "JKJ-TRADE-001",
        "Symbol": SYMBOL,
        "Original Quantity": 65,
        "Cumulative Filled Quantity": 65,
        "Expected Remaining Quantity": 0,
        "V11 Remaining Quantity": 0,
        "Synchronization Confirmed": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Wisdom Before Wealth": True,
    }


def valid_closed_trade():
    return {
        "Trade ID": "JKJ-TRADE-001",
        "Status": "CLOSED",
        "Symbol": SYMBOL,
        "Instrument Type": "OPTION",
        "Original Quantity": 65,
        "Current Quantity": 0,
        "Entry Price": 100.0,
        "Entry Time": "2026-09-22T09:30:00",
        "Exit Time": "2026-09-22T10:30:00",
        "Exit Reason": "TARGET 3",
        "Exit Events": [
            {
                "Action": "SELL",
                "Quantity": 15,
                "Price": 120.0,
            },
            {
                "Action": "SELL",
                "Quantity": 22,
                "Price": 140.0,
            },
            {
                "Action": "SELL",
                "Quantity": 28,
                "Price": 160.0,
            },
        ],
        "Gross P&L": 3600.0,
        "Trading Costs": 100.0,
        "Slippage": 20.0,
        "Net P&L": 3480.0,
    }


def test_successful_final_audit():
    result = integrate_v20_1_to_v19_1(
        valid_v20_1_v18_1_result(),
        valid_closed_trade(),
    )

    assert (
        result["Status"]
        == "V20_1_V19_1_INTEGRATION_COMPLETE"
    )
    assert result["Final Audit"] is True
    assert result["Read Only"] is True
    assert (
        result["Closure Record"]["Closure Status"]
        == "PAPER_TRADE_CLOSED"
    )
    assert result["Closure Record"]["Trade Status"] == "CLOSED"
    assert (
        result["Closure Record"]["Final Remaining Quantity"]
        == 0
    )
    assert (
        result["Closure Record"]["Total Exited Quantity"]
        == 65
    )
    assert (
        result["Closure Record"][
            "V18.1 Cumulative Filled Quantity"
        ]
        == 65
    )

    print(
        "Successful V20.1 -> V19.1 final audit: PASS"
    )


def test_incomplete_v18_1_blocked():
    result = valid_v20_1_v18_1_result()
    result["Status"] = (
        "V20_1_V18_1_INTEGRATION_BLOCKED"
    )

    output = integrate_v20_1_to_v19_1(
        result,
        valid_closed_trade(),
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Incomplete V18.1 safeguard: PASS"
    )


def test_trade_not_closed_blocked():
    trade = valid_closed_trade()
    trade["Status"] = "OPEN"

    output = integrate_v20_1_to_v19_1(
        valid_v20_1_v18_1_result(),
        trade,
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Non-CLOSED V11 trade safeguard: PASS"
    )


def test_trade_id_mismatch_blocked():
    trade = valid_closed_trade()
    trade["Trade ID"] = "JKJ-TRADE-999"

    output = integrate_v20_1_to_v19_1(
        valid_v20_1_v18_1_result(),
        trade,
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Trade identity safeguard: PASS"
    )


def test_symbol_mismatch_blocked():
    trade = valid_closed_trade()
    trade["Symbol"] = "NIFTY26SEP25000PE"

    output = integrate_v20_1_to_v19_1(
        valid_v20_1_v18_1_result(),
        trade,
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Symbol identity safeguard: PASS"
    )


def test_remaining_quantity_blocked():
    result = valid_v20_1_v18_1_result()
    result["V11 Remaining Quantity"] = 5

    output = integrate_v20_1_to_v19_1(
        result,
        valid_closed_trade(),
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Non-zero remaining quantity safeguard: PASS"
    )


def test_cumulative_quantity_mismatch_blocked():
    result = valid_v20_1_v18_1_result()
    result["Cumulative Filled Quantity"] = 60

    output = integrate_v20_1_to_v19_1(
        result,
        valid_closed_trade(),
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Cumulative quantity mismatch safeguard: PASS"
    )


def test_broker_communication_blocked():
    result = valid_v20_1_v18_1_result()
    result["Broker Communication"] = True

    output = integrate_v20_1_to_v19_1(
        result,
        valid_closed_trade(),
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Broker communication safeguard: PASS"
    )


def test_live_order_blocked():
    result = valid_v20_1_v18_1_result()
    result["Order Placement Permitted"] = True

    output = integrate_v20_1_to_v19_1(
        result,
        valid_closed_trade(),
    )

    assert (
        output["Status"]
        == "V20_1_V19_1_INTEGRATION_BLOCKED"
    )

    print(
        "Live order placement safeguard: PASS"
    )


def test_read_only_boundary():
    trade = valid_closed_trade()

    original_trade = dict(trade)

    result = integrate_v20_1_to_v19_1(
        valid_v20_1_v18_1_result(),
        trade,
    )

    assert result["Final Audit"] is True
    assert result["Read Only"] is True
    assert trade == original_trade

    print(
        "Read-only closure validation safeguard: PASS"
    )


def run_test():
    test_successful_final_audit()
    test_incomplete_v18_1_blocked()
    test_trade_not_closed_blocked()
    test_trade_id_mismatch_blocked()
    test_symbol_mismatch_blocked()
    test_remaining_quantity_blocked()
    test_cumulative_quantity_mismatch_blocked()
    test_broker_communication_blocked()
    test_live_order_blocked()
    test_read_only_boundary()

    print()
    print(
        "V20.1 -> V19.1 INTEGRATION: ALL TESTS PASSED"
    )
    print(
        "V11 remains authoritative for the final trade record."
    )
    print(
        "V18.1 remains authoritative for synchronization."
    )
    print(
        "V19.1 performs read-only final closure validation."
    )
    print("No P&L calculation.")
    print("No exit quantity generation.")
    print("No V11 modification.")
    print("No V17.2 modification.")
    print("No live Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()
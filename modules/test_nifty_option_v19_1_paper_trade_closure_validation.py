"""
JKJ AI Trader
V19.1 Paper Trade Closure Validation Test

Purpose:
    Validate the final closed paper-trade boundary between
    V11 paper trading and V18.1 lifecycle synchronization.

This test does NOT:
    - place real orders
    - connect to Zerodha
    - modify V11
    - modify V18.1
    - modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_v19_1_paper_trade_closure_validation import (
    validate_paper_trade_closure,
)


# ---------------------------------------------------------
# Common test data
# ---------------------------------------------------------

ORIGINAL_QUANTITY = 65
FINAL_REMAINING_QUANTITY = 0
CUMULATIVE_FILLED = 65


# ---------------------------------------------------------
# Build controlled closed V11 trade
# ---------------------------------------------------------

def build_closed_trade():
    return {
        "Trade ID": "JKJ-V19-TEST-001",
        "Status": "CLOSED",

        "Symbol": "NIFTY26SEP23000CE",
        "Instrument Type": "OPTION",

        "Expiry": "2026-09-24",
        "Strike": 23000,
        "Option Type": "CE",
        "Underlying": "NIFTY",

        "Entry Time": "2026-09-21 10:00:00",
        "Entry Price": 100.0,
        "Original Quantity": ORIGINAL_QUANTITY,
        "Current Quantity": FINAL_REMAINING_QUANTITY,

        "Stop Loss": 90.0,
        "Target": 105.0,

        "Gross P&L": 1200.0,
        "Trading Costs": 50.0,
        "Slippage": 10.0,
        "Net P&L": 1140.0,

        "Exit Time": "2026-09-21 11:00:00",
        "Exit Reason": "TARGET 3",

        "Exit Events": [
            {
                "Action": "SELL",
                "Time": "2026-09-21 10:20:00",
                "Price": 106.0,
                "Quantity": 15,
                "Gross P&L": 90.0,
                "Costs": 5.0,
                "Slippage": 1.0,
                "Net P&L": 84.0,
                "Reason": "TARGET 1",
            },
            {
                "Action": "SELL",
                "Time": "2026-09-21 10:40:00",
                "Price": 111.0,
                "Quantity": 22,
                "Gross P&L": 242.0,
                "Costs": 15.0,
                "Slippage": 3.0,
                "Net P&L": 224.0,
                "Reason": "TARGET 2",
            },
            {
                "Action": "SELL",
                "Time": "2026-09-21 11:00:00",
                "Price": 121.0,
                "Quantity": 28,
                "Gross P&L": 868.0,
                "Costs": 30.0,
                "Slippage": 6.0,
                "Net P&L": 832.0,
                "Reason": "TARGET 3",
            },
        ],
    }


# ---------------------------------------------------------
# Build final V18.1 synchronization
# ---------------------------------------------------------

def build_final_v18_1_sync():
    return {
        "Status": "SYNCHRONIZED",
        "Target Stage": "TARGET 3",

        "Original Quantity": ORIGINAL_QUANTITY,
        "Planned Quantity": 28,

        "V11 Event Exit Quantity": 28,
        "Previous Cumulative Filled": 37,
        "Cumulative Filled Quantity": CUMULATIVE_FILLED,

        "V11 Remaining Quantity": FINAL_REMAINING_QUANTITY,
        "Expected Remaining Quantity": FINAL_REMAINING_QUANTITY,

        "V17.2 Execution Status": "FILLED",
        "V17.2 Execution Confirmed": True,

        "Synchronization Confirmed": True,

        "Broker Communication": False,
        "Order Placement Permitted": False,

        "Wisdom Before Wealth": True,
    }


# ---------------------------------------------------------
# Main test
# ---------------------------------------------------------

def main():

    trade = build_closed_trade()
    v18_1_final_sync = build_final_v18_1_sync()

    result = validate_paper_trade_closure(
        trade,
        v18_1_final_sync,
    )

    assert result["Status"] == (
        "PAPER_TRADE_CLOSURE_VALIDATED"
    )

    assert result["Final Audit"] is True
    assert result["Read Only"] is True
    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False

    closure = result["Closure Record"]

    assert closure["Closure Status"] == (
        "PAPER_TRADE_CLOSED"
    )

    assert closure["Trade ID"] == "JKJ-V19-TEST-001"
    assert closure["Trading Symbol"] == "NIFTY26SEP23000CE"

    assert closure["Original Quantity"] == 65
    assert closure["Total Exited Quantity"] == 65
    assert closure["Final Remaining Quantity"] == 0
    assert closure["Trade Status"] == "CLOSED"

    assert closure["V18.1 Synchronization Confirmed"] is True
    assert closure["V18.1 Cumulative Filled Quantity"] == 65
    assert closure["V18.1 Expected Remaining Quantity"] == 0

    assert closure["Gross P&L"] == 1200.0
    assert closure["Trading Costs"] == 50.0
    assert closure["Slippage"] == 10.0
    assert closure["Net P&L"] == 1140.0

    assert len(closure["Exit Events"]) == 3

    # -----------------------------------------------------
    # Read-only validation
    # -----------------------------------------------------

    assert trade["Current Quantity"] == 0
    assert trade["Status"] == "CLOSED"

    # -----------------------------------------------------
    # Safety test: open trade must be blocked
    # -----------------------------------------------------

    open_trade = build_closed_trade()
    open_trade["Status"] = "OPEN"
    open_trade["Current Quantity"] = 28

    blocked_open = validate_paper_trade_closure(
        open_trade,
        v18_1_final_sync,
    )

    assert blocked_open["Status"] == (
        "PAPER_TRADE_CLOSURE_BLOCKED"
    )

    # -----------------------------------------------------
    # Safety test: V18.1 mismatch must be blocked
    # -----------------------------------------------------

    mismatch_sync = build_final_v18_1_sync()
    mismatch_sync["Cumulative Filled Quantity"] = 37

    blocked_mismatch = validate_paper_trade_closure(
        trade,
        mismatch_sync,
    )

    assert blocked_mismatch["Status"] == (
        "PAPER_TRADE_CLOSURE_BLOCKED"
    )

    # -----------------------------------------------------
    # Safety test: remaining quantity must be zero
    # -----------------------------------------------------

    remaining_sync = build_final_v18_1_sync()
    remaining_sync["Expected Remaining Quantity"] = 5

    blocked_remaining = validate_paper_trade_closure(
        trade,
        remaining_sync,
    )

    assert blocked_remaining["Status"] == (
        "PAPER_TRADE_CLOSURE_BLOCKED"
    )

    print()
    print("V19.1 Paper Trade Closure Validation: PASS")
    print("V11 CLOSED position: PASS")
    print("V18.1 final synchronization: PASS")
    print("Original quantity: 65")
    print("Total exited quantity: 65")
    print("Final remaining quantity: 0")
    print("Exit events: 3")
    print("Gross P&L preserved: 1200.0")
    print("Net P&L preserved: 1140.0")
    print("Open-position safeguard: PASS")
    print("V18.1 mismatch safeguard: PASS")
    print("Remaining-quantity safeguard: PASS")
    print("No P&L recalculation.")
    print("No V11 modification.")
    print("No V18.1 modification.")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print()
    print(
        "V19.1 PAPER TRADE CLOSURE VALIDATION: "
        "ALL TESTS PASSED"
    )
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    main()

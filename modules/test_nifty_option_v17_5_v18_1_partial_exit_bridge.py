"""
JKJ AI Trader
V17.5 + V18.1 Partial Exit Bridge Integration Test

Purpose:
    Validate that a synchronized V18.1 partial paper exit
    provides the correct remaining quantity to the V17.5
    execution eligibility boundary.

This test does NOT:
    - connect to Zerodha
    - place orders
    - modify V11
    - modify V17.2
    - modify V18.1
    - modify V19.1
    - modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_v18_1_paper_target_exit_synchronization import (
    synchronize_target_exit,
)

from modules.nifty_option_v17_5_execution_eligibility import (
    validate_execution_eligibility,
)

from modules.nifty_option_target_exit_execution import (
    create_target_exit_execution,
)


TRADING_SYMBOL = "NIFTY2692223300CE"
INSTRUMENT_TOKEN = 14588162
EXPIRY = "2026-09-22"
STRIKE = 23300.0
OPTION_TYPE = "CE"
LOT_SIZE = 65

GLOBAL_ORIGINAL_QUANTITY = 65
FIRST_EXIT_QUANTITY = 15
EXPECTED_REMAINING_QUANTITY = 50


def build_v11_exit_result():
    return {
        "Status": "SELL_RECORDED",
        "Exit Quantity": FIRST_EXIT_QUANTITY,
        "Remaining Quantity": EXPECTED_REMAINING_QUANTITY,
    }


def build_v17_2_execution_record():
    return create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=GLOBAL_ORIGINAL_QUANTITY,
        planned_quantity=FIRST_EXIT_QUANTITY,
    )


def main():

    print("=" * 60)
    print("JKJ V17.5 + V18.1 PARTIAL EXIT BRIDGE")
    print("=" * 60)

    # ---------------------------------------------------------
    # STEP 1 — V18.1 partial paper-exit synchronization
    # ---------------------------------------------------------

    v18_1_result = synchronize_target_exit(
        v11_exit_result=build_v11_exit_result(),
        execution_record=build_v17_2_execution_record(),
        global_original_quantity=GLOBAL_ORIGINAL_QUANTITY,
        previous_cumulative_filled=0,
    )

    assert v18_1_result["Status"] == "SYNCHRONIZED"
    assert v18_1_result["Synchronization Confirmed"] is True
    assert v18_1_result["V11 Event Exit Quantity"] == FIRST_EXIT_QUANTITY
    assert v18_1_result["Cumulative Filled Quantity"] == FIRST_EXIT_QUANTITY
    assert (
        v18_1_result["Expected Remaining Quantity"]
        == EXPECTED_REMAINING_QUANTITY
    )
    assert (
        v18_1_result["V11 Remaining Quantity"]
        == EXPECTED_REMAINING_QUANTITY
    )
    assert v18_1_result["V17.2 Execution Status"] == "FILLED"

    print("V18.1 Partial Paper Exit Synchronization: PASS")

    # ---------------------------------------------------------
    # STEP 2 — Extract synchronized remaining quantity
    # ---------------------------------------------------------

    remaining_quantity = v18_1_result[
        "Expected Remaining Quantity"
    ]

    assert remaining_quantity == EXPECTED_REMAINING_QUANTITY

    print(
        "V18.1 Synchronized Remaining Quantity:",
        remaining_quantity,
    )

    # ---------------------------------------------------------
    # STEP 3 — V17.5 validates the remaining position
    #
    # The remaining position is 50.
    # A further exit of one valid lot (65) must be blocked
    # because it exceeds the actual remaining quantity.
    # ---------------------------------------------------------

    blocked_quantity = validate_execution_eligibility(
        {
            "tradingsymbol": TRADING_SYMBOL,
            "instrument_token": INSTRUMENT_TOKEN,
            "expiry": EXPIRY,
            "strike": STRIKE,
            "instrument_type": OPTION_TYPE,
            "lot_size": LOT_SIZE,
        },
        current_quantity=remaining_quantity,
        requested_quantity=LOT_SIZE,
    )

    assert blocked_quantity["Status"] == "EXECUTION_BLOCKED"
    assert blocked_quantity["Order Placement Permitted"] is False

    print(
        "V17.5 Excess Exit Quantity Protection: SAFELY BLOCKED"
    )

    

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    print()
    print("V17.5 + V18.1 PARTIAL EXIT BRIDGE: PASS")
    print("V18.1 PARTIAL SYNCHRONIZATION CONFIRMED")
    print("REMAINING QUANTITY = 50")
    print("EXCESS EXIT REQUEST SAFELY BLOCKED")
    
    print("NO ORDER PLACEMENT")
    print("NO ZERODHA ORDER")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    main()
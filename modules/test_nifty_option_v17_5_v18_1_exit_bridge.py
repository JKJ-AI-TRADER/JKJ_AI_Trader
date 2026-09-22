"""
JKJ AI Trader
V17.5 + V18.1 Exit Bridge Integration Test

Purpose:
    Validate that a synchronized V18.1 paper exit can provide
    the correct remaining quantity to the V17.5 execution
    eligibility boundary.

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


def build_v11_exit_result():
    return {
        "Status": "SELL_RECORDED",
        "Exit Quantity": 65,
        "Remaining Quantity": 0,
    }


def build_v17_2_execution_record():
    return create_target_exit_execution(
        target_stage="TARGET 3",
        original_quantity=GLOBAL_ORIGINAL_QUANTITY,
        planned_quantity=65,
    )


def main():

    print("=" * 60)
    print("JKJ V17.5 + V18.1 EXIT BRIDGE")
    print("=" * 60)

    # ---------------------------------------------------------
    # STEP 1 — V18.1 paper exit synchronization
    # ---------------------------------------------------------

    v18_1_result = synchronize_target_exit(
        v11_exit_result=build_v11_exit_result(),
        execution_record=build_v17_2_execution_record(),
        global_original_quantity=GLOBAL_ORIGINAL_QUANTITY,
        previous_cumulative_filled=0,
    )

    assert v18_1_result["Status"] == "SYNCHRONIZED"
    assert v18_1_result["Synchronization Confirmed"] is True
    assert v18_1_result["Expected Remaining Quantity"] == 0
    assert v18_1_result["V11 Remaining Quantity"] == 0
    assert v18_1_result["Cumulative Filled Quantity"] == 65

    print("V18.1 Paper Exit Synchronization: PASS")

    # ---------------------------------------------------------
    # STEP 2 — Extract synchronized remaining quantity
    # ---------------------------------------------------------

    remaining_quantity = v18_1_result[
        "Expected Remaining Quantity"
    ]

    assert remaining_quantity == 0

    print(
        "V18.1 Synchronized Remaining Quantity:",
        remaining_quantity,
    )

    # ---------------------------------------------------------
    # STEP 3 — V17.5 quantity eligibility
    #
    # A zero remaining quantity means the position is fully
    # exited. Therefore the next execution request must NOT
    # attempt another exit.
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
        requested_quantity=65,
    )

    assert blocked_quantity["Status"] == "EXECUTION_BLOCKED"
    assert blocked_quantity["Order Placement Permitted"] is False

    print(
        "V17.5 Zero-Quantity Exit Protection: SAFELY BLOCKED"
    )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    print()
    print("V17.5 + V18.1 EXIT BRIDGE: PASS")
    print("V18.1 SYNCHRONIZATION CONFIRMED")
    print("REMAINING QUANTITY = 0")
    print("SECOND EXIT SAFELY BLOCKED")
    print("NO ORDER PLACEMENT")
    print("NO ZERODHA ORDER")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    main()
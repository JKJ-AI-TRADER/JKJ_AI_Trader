"""
JKJ AI Trader
V17.5 + V18.1 Valid Partial Exit Bridge Integration Test

Purpose:
    Validate a valid multi-lot partial paper exit flowing from
    V18.1 synchronization into the V17.5 execution eligibility
    boundary.

Scenario:
    Original position: 130
    First exit:         65
    Remaining:          65
    Next exit request:  65
    Result:             EXECUTION_ELIGIBLE

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

GLOBAL_ORIGINAL_QUANTITY = 130
FIRST_EXIT_QUANTITY = 65
EXPECTED_REMAINING_QUANTITY = 65


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
    print("JKJ V17.5 + V18.1 VALID PARTIAL EXIT BRIDGE")
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
    assert v18_1_result["V11 Event Exit Quantity"] == 65
    assert v18_1_result["Cumulative Filled Quantity"] == 65
    assert (
        v18_1_result["Expected Remaining Quantity"]
        == EXPECTED_REMAINING_QUANTITY
    )
    assert (
        v18_1_result["V11 Remaining Quantity"]
        == EXPECTED_REMAINING_QUANTITY
    )
    assert v18_1_result["V17.2 Execution Status"] == "FILLED"

    print("V18.1 Valid Partial Exit Synchronization: PASS")

    # ---------------------------------------------------------
    # STEP 2 — Extract synchronized remaining quantity
    # ---------------------------------------------------------

    remaining_quantity = v18_1_result[
        "Expected Remaining Quantity"
    ]

    assert remaining_quantity == 65

    print(
        "V18.1 Synchronized Remaining Quantity:",
        remaining_quantity,
    )

    # ---------------------------------------------------------
    # STEP 3 — V17.5 validates the next full-lot exit
    # ---------------------------------------------------------

    valid_quantity = validate_execution_eligibility(
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

    assert valid_quantity["Status"] == "EXECUTION_ELIGIBLE"
    assert valid_quantity["Requested Exit Quantity"] == 65
    assert valid_quantity["Remaining Quantity"] == 0
    assert valid_quantity["Order Placement Permitted"] is True

    print(
        "V17.5 Valid Remaining Lot: EXECUTION ELIGIBLE"
    )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    print()
    print("V17.5 + V18.1 VALID PARTIAL EXIT BRIDGE: PASS")
    print("ORIGINAL QUANTITY = 130")
    print("FIRST EXIT = 65")
    print("REMAINING QUANTITY = 65")
    print("NEXT FULL-LOT EXIT = ELIGIBLE")
    print("NO ORDER PLACEMENT")
    print("NO ZERODHA ORDER")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    main()
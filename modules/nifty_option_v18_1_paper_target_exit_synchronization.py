"""
JKJ AI Trader
V18.1 Paper Target Exit Synchronization

Purpose:
    Synchronize actual V11 paper-exit events with
    V17.2 target-stage execution state.

Architecture:

    V11 remains authoritative for actual position quantity.

    V17.2 remains authoritative for target-stage
    execution state.

    V18.1 reconciles the two without changing
    either engine.

Important:
    This module does NOT:
    - calculate exit quantity
    - modify V11
    - modify V17.2
    - modify V15
    - place real orders
    - connect to Zerodha
    - modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_target_exit_execution import (
    update_target_exit_execution,
)


VALID_TARGET_STAGES = {
    "TARGET 1",
    "TARGET 2",
    "TARGET 3",
}


def _blocked(reason):
    return {
        "Status": "SYNCHRONIZATION_BLOCKED",
        "Reason": reason,
        "Synchronization Confirmed": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }


def synchronize_target_exit(
    v11_exit_result,
    execution_record,
    previous_cumulative_filled=0,
):
    """
    Synchronize one actual V11 exit event with one
    V17.2 target-stage execution record.

    V11 supplies the actual event-level exit quantity.

    V18.1 converts that event quantity into the
    cumulative filled quantity required by the
    V17.2 execution-state model.

    V11 remaining quantity must agree with the
    resulting cumulative position state.
    """

    # ---------------------------------------------------------
    # 1. Validate V11 exit result
    # ---------------------------------------------------------

    if not isinstance(v11_exit_result, dict):
        return _blocked(
            "Invalid V11 exit result"
        )

    if v11_exit_result.get("Status") not in {
        "SELL_RECORDED",
        "PARTIAL",
        "FILLED",
        "CLOSED",
    }:
        return _blocked(
            "V11 exit result does not represent a completed exit event"
        )

    if "Exit Quantity" not in v11_exit_result:
        return _blocked(
            "V11 exit result missing Exit Quantity"
        )

    if "Remaining Quantity" not in v11_exit_result:
        return _blocked(
            "V11 exit result missing Remaining Quantity"
        )

    try:
        event_exit_quantity = int(
            v11_exit_result["Exit Quantity"]
        )
        v11_remaining_quantity = int(
            v11_exit_result["Remaining Quantity"]
        )
        previous_cumulative_filled = int(
            previous_cumulative_filled
        )
    except (TypeError, ValueError):
        return _blocked(
            "V11 quantities must be integers"
        )

    if event_exit_quantity <= 0:
        return _blocked(
            "V11 exit quantity must be greater than zero"
        )

    if v11_remaining_quantity < 0:
        return _blocked(
            "V11 remaining quantity cannot be negative"
        )

    if previous_cumulative_filled < 0:
        return _blocked(
            "Previous cumulative filled quantity cannot be negative"
        )

    # ---------------------------------------------------------
    # 2. Validate V17.2 execution record
    # ---------------------------------------------------------

    if not isinstance(execution_record, dict):
        return _blocked(
            "Invalid V17.2 execution record"
        )

    if execution_record.get("Status") != "PLANNED":
        return _blocked(
            "V17.2 execution record must have Status PLANNED"
        )

    target_stage = execution_record.get(
        "Target Stage"
    )

    if target_stage not in VALID_TARGET_STAGES:
        return _blocked(
            "Invalid V17.2 target stage"
        )

    try:
        original_quantity = int(
            execution_record["Original Quantity"]
        )
        planned_quantity = int(
            execution_record["Planned Quantity"]
        )
    except (KeyError, TypeError, ValueError):
        return _blocked(
            "Invalid V17.2 execution quantities"
        )

    if original_quantity <= 0:
        return _blocked(
            "Original quantity must be greater than zero"
        )

    if planned_quantity <= 0:
        return _blocked(
            "Planned quantity must be greater than zero"
        )

    # ---------------------------------------------------------
    # 3. Calculate cumulative actual execution
    # ---------------------------------------------------------

    cumulative_filled = (
        previous_cumulative_filled
        + event_exit_quantity
    )

    if cumulative_filled > original_quantity:
        return _blocked(
            "Cumulative filled quantity exceeds original quantity"
        )

    expected_remaining_quantity = (
        original_quantity - cumulative_filled
    )

    # ---------------------------------------------------------
    # 4. Reconcile V11 position state
    # ---------------------------------------------------------

    if (
        v11_remaining_quantity
        != expected_remaining_quantity
    ):
        return _blocked(
            "V11 remaining quantity does not match "
            "cumulative execution state"
        )

    # ---------------------------------------------------------
    # 5. Determine V17.2 execution state
    # ---------------------------------------------------------

    if event_exit_quantity == planned_quantity:
        execution_status = "FILLED"
    elif event_exit_quantity < planned_quantity:
        execution_status = "PARTIAL"
    else:
        return _blocked(
            "V11 exit quantity exceeds V17.2 planned quantity"
        )

    # ---------------------------------------------------------
    # 6. Update V17.2 state
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # V17.2 receives the actual event-level fill for
    # this target stage.
    #
    # Its own Actual Remaining Quantity is stage-record
    # accounting, while V18.1 separately verifies the
    # global V11 position remaining quantity.
    # ---------------------------------------------------------

    updated_execution = update_target_exit_execution(
        execution_record=execution_record,
        execution_status=execution_status,
        filled_quantity=event_exit_quantity,
        submitted_quantity=planned_quantity,
    )

    if updated_execution.get("Status") != "UPDATED":
        return _blocked(
            "V17.2 rejected the synchronized execution update"
        )

    # ---------------------------------------------------------
    # 7. Final reconciliation
    # ---------------------------------------------------------

    return {
        "Status": "SYNCHRONIZED",
        "Target Stage": target_stage,

        "Original Quantity": original_quantity,
        "Planned Quantity": planned_quantity,

        "V11 Event Exit Quantity": (
            event_exit_quantity
        ),

        "Previous Cumulative Filled": (
            previous_cumulative_filled
        ),

        "Cumulative Filled Quantity": (
            cumulative_filled
        ),

        "V11 Remaining Quantity": (
            v11_remaining_quantity
        ),

        "Expected Remaining Quantity": (
            expected_remaining_quantity
        ),

        "V17.2 Execution Status": (
            updated_execution.get(
                "Execution Status"
            )
        ),

        "V17.2 Execution Confirmed": (
            updated_execution.get(
                "Execution Confirmed"
            )
        ),

        "V17.2 Execution State": updated_execution,

        "Synchronization Confirmed": True,

        "Broker Communication": False,
        "Order Placement Permitted": False,

        "Wisdom Before Wealth": True,
    }
"""
JKJ AI Trader
V17.2 Target Exit Execution State

Purpose:
    Record the execution state of a planned target exit.

Architecture:
    V15.5 determines WHAT target has been reached.
    V17.1 determines HOW MUCH is planned for that target.
    V17.2 records WHAT ACTUALLY happened.

Important:
    This module does NOT:
    - connect to Zerodha
    - place real orders
    - assume an order was filled
    - modify V11
    - modify V14
    - modify V15.5
    - modify main.py

Execution states:
    PLANNED
    SUBMITTED
    FILLED
    PARTIAL
    PENDING
    REJECTED

Actual remaining quantity is calculated from the actual
filled quantity.

Wisdom Before Wealth.
"""


VALID_TARGET_STAGES = {
    "TARGET 1",
    "TARGET 2",
    "TARGET 3",
}

VALID_EXECUTION_STATES = {
    "PLANNED",
    "SUBMITTED",
    "FILLED",
    "PARTIAL",
    "PENDING",
    "REJECTED",
}


def create_target_exit_execution(
    target_stage,
    original_quantity,
    planned_quantity,
):
    """
    Create an initial target-exit execution record.

    No execution is assumed.

    The initial state is PLANNED.
    """

    # ---------------------------------------------------------
    # 1. Validate target stage
    # ---------------------------------------------------------

    if target_stage not in VALID_TARGET_STAGES:
        return _rejected_result("Invalid target stage")

    # ---------------------------------------------------------
    # 2. Validate quantities
    # ---------------------------------------------------------

    try:
        original_quantity = int(original_quantity)
        planned_quantity = int(planned_quantity)
    except (TypeError, ValueError):
        return _rejected_result(
            "Quantities must be integers"
        )

    if original_quantity <= 0:
        return _rejected_result(
            "Original quantity must be greater than zero"
        )

    if planned_quantity <= 0:
        return _rejected_result(
            "Planned quantity must be greater than zero"
        )

    if planned_quantity > original_quantity:
        return _rejected_result(
            "Planned quantity cannot exceed original quantity"
        )

    # ---------------------------------------------------------
    # 3. Create planned execution state
    # ---------------------------------------------------------

    return {
        "Status": "PLANNED",
        "Target Stage": target_stage,

        "Original Quantity": original_quantity,
        "Planned Quantity": planned_quantity,

        "Submitted Quantity": 0,
        "Filled Quantity": 0,

        "Actual Remaining Quantity": original_quantity,

        "Execution Status": "PLANNED",

        "Execution Confirmed": False,
    }


def update_target_exit_execution(
    execution_record,
    execution_status,
    filled_quantity=0,
    submitted_quantity=None,
):
    """
    Update a target-exit execution record with an execution result.

    This is a simulation/state function only.

    The supplied filled quantity is treated as the actual
    execution result.

    Examples:
        FILLED   -> filled quantity equals planned quantity
        PARTIAL  -> filled quantity is greater than zero but
                    less than planned quantity
        PENDING  -> no confirmed fill
        REJECTED -> no confirmed fill
    """

    # ---------------------------------------------------------
    # 1. Validate execution record
    # ---------------------------------------------------------

    if not isinstance(execution_record, dict):
        return _rejected_result(
            "Invalid execution record"
        )

    if execution_record.get("Status") != "PLANNED":
        return _rejected_result(
            "Execution record must have Status PLANNED"
        )

    target_stage = execution_record.get("Target Stage")

    if target_stage not in VALID_TARGET_STAGES:
        return _rejected_result(
            "Invalid target stage"
        )

    # ---------------------------------------------------------
    # 2. Validate execution status
    # ---------------------------------------------------------

    if execution_status not in VALID_EXECUTION_STATES:
        return _rejected_result(
            "Invalid execution status"
        )

    # ---------------------------------------------------------
    # 3. Validate quantities
    # ---------------------------------------------------------

    original_quantity = execution_record.get(
        "Original Quantity"
    )

    planned_quantity = execution_record.get(
        "Planned Quantity"
    )

    try:
        original_quantity = int(original_quantity)
        planned_quantity = int(planned_quantity)
        filled_quantity = int(filled_quantity)

        if submitted_quantity is None:
            submitted_quantity = planned_quantity

        submitted_quantity = int(submitted_quantity)

    except (TypeError, ValueError):
        return _rejected_result(
            "Execution quantities must be integers"
        )

    if filled_quantity < 0:
        return _rejected_result(
            "Filled quantity cannot be negative"
        )

    if submitted_quantity < 0:
        return _rejected_result(
            "Submitted quantity cannot be negative"
        )

    if submitted_quantity > original_quantity:
        return _rejected_result(
            "Submitted quantity cannot exceed original quantity"
        )

    if filled_quantity > submitted_quantity:
        return _rejected_result(
            "Filled quantity cannot exceed submitted quantity"
        )

    if filled_quantity > original_quantity:
        return _rejected_result(
            "Filled quantity cannot exceed original quantity"
        )

    # ---------------------------------------------------------
    # 4. Validate state-specific rules
    # ---------------------------------------------------------

    if execution_status == "FILLED":
        if filled_quantity != planned_quantity:
            return _rejected_result(
                "FILLED requires filled quantity equal to planned quantity"
            )

    if execution_status == "PARTIAL":
        if filled_quantity <= 0:
            return _rejected_result(
                "PARTIAL requires a positive filled quantity"
            )

        if filled_quantity >= planned_quantity:
            return _rejected_result(
                "PARTIAL requires filled quantity below planned quantity"
            )

    if execution_status in {"PENDING", "REJECTED"}:
        if filled_quantity != 0:
            return _rejected_result(
                f"{execution_status} cannot have confirmed filled quantity"
            )

    # ---------------------------------------------------------
    # 5. Calculate actual remaining quantity
    # ---------------------------------------------------------

    actual_remaining_quantity = (
        original_quantity - filled_quantity
    )

    # ---------------------------------------------------------
    # 6. Determine confirmation state
    # ---------------------------------------------------------

    execution_confirmed = execution_status in {
        "FILLED",
        "PARTIAL",
    }

    # ---------------------------------------------------------
    # 7. Return updated state
    # ---------------------------------------------------------

    return {
        "Status": "UPDATED",
        "Target Stage": target_stage,

        "Original Quantity": original_quantity,
        "Planned Quantity": planned_quantity,

        "Submitted Quantity": submitted_quantity,
        "Filled Quantity": filled_quantity,

        "Actual Remaining Quantity": (
            actual_remaining_quantity
        ),

        "Execution Status": execution_status,

        "Execution Confirmed": execution_confirmed,
    }


def _rejected_result(reason):
    """
    Return a safe result when execution data is invalid.
    """

    return {
        "Status": "REJECTED",
        "Execution Status": "REJECTED",
        "Execution Confirmed": False,
        "Reason": reason,
    }
"""
JKJ AI Trader
V17.1 Target Exit Plan

Purpose:
    Create a deterministic three-stage target exit allocation
    for an open paper/real-market position.

Architecture:
    V15.5 determines WHAT target has been reached.
    V17.1 determines the PLANNED quantity for each target stage.

Important:
    This module does NOT:
    - decide whether a target has been reached
    - place orders
    - connect to Zerodha
    - verify broker fills
    - reconcile actual position quantity
    - modify V11
    - modify V14
    - modify V15.5
    - modify main.py

Target 3 represents the final planned stage.
At execution time, the actual remaining quantity must be
used rather than assuming the planned quantity was filled.

Wisdom Before Wealth.
"""


def create_target_exit_plan(total_quantity):
    """
    Create a deterministic three-stage target exit plan.

    The total quantity is divided as evenly as possible
    between Target 1, Target 2 and Target 3.

    Any remainder is distributed from Target 1 onward.

    Examples:
        60 -> 20 / 20 / 20
        61 -> 21 / 20 / 20
        62 -> 21 / 21 / 20
        65 -> 22 / 22 / 21

    Returns
    -------
    dict
        Target exit allocation and validation status.
    """

    # ---------------------------------------------------------
    # 1. Validate quantity
    # ---------------------------------------------------------

    if total_quantity is None:
        return _rejected_result("Total quantity is required")

    try:
        quantity = int(total_quantity)
    except (TypeError, ValueError):
        return _rejected_result("Total quantity must be an integer")

    if quantity <= 0:
        return _rejected_result(
            "Total quantity must be greater than zero"
        )

    # ---------------------------------------------------------
    # 2. Calculate base allocation and remainder
    # ---------------------------------------------------------

    base_quantity = quantity // 3
    remainder = quantity % 3

    target_1_quantity = base_quantity
    target_2_quantity = base_quantity
    target_3_quantity = base_quantity

    # ---------------------------------------------------------
    # 3. Distribute remainder from Target 1 onward
    # ---------------------------------------------------------

    if remainder >= 1:
        target_1_quantity += 1

    if remainder >= 2:
        target_2_quantity += 1

    # ---------------------------------------------------------
    # 4. Validate allocation
    # ---------------------------------------------------------

    planned_total = (
        target_1_quantity
        + target_2_quantity
        + target_3_quantity
    )

    if planned_total != quantity:
        return _rejected_result(
            "Target allocation does not equal total quantity"
        )

    if (
        target_1_quantity <= 0
        or target_2_quantity <= 0
        or target_3_quantity <= 0
    ):
        return _rejected_result(
            "Target allocation produced a zero-sized slice"
        )

    # ---------------------------------------------------------
    # 5. Return plan
    # ---------------------------------------------------------

    return {
        "Status": "VALIDATED",
        "Total Quantity": quantity,

        "Target 1 Quantity": target_1_quantity,
        "Target 2 Quantity": target_2_quantity,
        "Target 3 Quantity": target_3_quantity,

        "Planned Exit Quantity": planned_total,
        "Allocation Valid": True,

        "Target 3 Rule": (
            "Final target exits the actual remaining quantity "
            "at execution time"
        ),

        "Wisdom Before Wealth": True,
    }


def _rejected_result(reason):
    """
    Return a safe result when the quantity is invalid.
    """

    return {
        "Status": "REJECTED",
        "Total Quantity": 0,

        "Target 1 Quantity": 0,
        "Target 2 Quantity": 0,
        "Target 3 Quantity": 0,

        "Planned Exit Quantity": 0,
        "Allocation Valid": False,

        "Reason": reason,
        "Wisdom Before Wealth": True,
    }
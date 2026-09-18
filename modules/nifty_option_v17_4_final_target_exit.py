"""
JKJ AI Trader
V17.4 Final Target Exit

Purpose:
    Create the final Target 3 exit using the actual
    remaining position quantity.

Architecture:
    T1/T2 use planned target slices.
    T3 exits the actual remaining quantity.

Important:
    This module does NOT:
    - place orders
    - connect to Zerodha
    - assume execution
    - modify V11
    - modify V14
    - modify V15.5
    - modify V17.1
    - modify V17.2
    - modify V17.3
    - modify main.py

Wisdom Before Wealth.
"""


def create_final_target_exit(
    target_progression,
    actual_remaining_quantity,
):
    """
    Create a final Target 3 exit using the actual
    remaining position quantity.
    """

    # ---------------------------------------------------------
    # 1. Validate target progression
    # ---------------------------------------------------------

    if not isinstance(target_progression, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid target progression data",
        }

    if target_progression.get("Status") != "TARGET_REACHED":
        return {
            "Status": "REJECTED",
            "Reason": "Target must have Status TARGET_REACHED",
        }

    if target_progression.get("Target Event") != "TARGET 3":
        return {
            "Status": "REJECTED",
            "Reason": "Final target must be TARGET 3",
        }

    # ---------------------------------------------------------
    # 2. Validate final-target flag
    # ---------------------------------------------------------

    if target_progression.get("Final Target") is not True:
        return {
            "Status": "REJECTED",
            "Reason": "Target 3 must be marked as Final Target",
        }

    # ---------------------------------------------------------
    # 3. Validate actual remaining quantity
    # ---------------------------------------------------------

    try:
        actual_remaining_quantity = int(
            actual_remaining_quantity
        )
    except (TypeError, ValueError):
        return {
            "Status": "REJECTED",
            "Reason": "Actual remaining quantity must be an integer",
        }

    if actual_remaining_quantity <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "No actual remaining quantity to exit",
        }

    # ---------------------------------------------------------
    # 4. Create final exit instruction
    # ---------------------------------------------------------

    return {
        "Status": "VALIDATED",
        "Target Stage": "TARGET 3",
        "Final Target": True,

        "Actual Remaining Quantity": (
            actual_remaining_quantity
        ),

        "Planned Final Exit Quantity": (
            actual_remaining_quantity
        ),

        "Exit Rule": (
            "Exit the complete actual remaining position"
        ),

        "Execution Confirmed": False,

        "Wisdom Before Wealth": True,
    }
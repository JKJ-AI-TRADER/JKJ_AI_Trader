"""
JKJ AI Trader
V15.5 Target Progression Controller

Purpose:
    Track progression through the three V14 target levels.

Architecture:
    V15 controls target progression.
    V11 controls exit quantity.

This module does NOT:
    - decide exit quantity
    - execute paper SELL
    - modify V11
    - modify V14
    - connect to Zerodha
    - place real orders
    - modify main.py

Wisdom Before Wealth.
"""


# ---------------------------------------------------------
# 1. Evaluate target progression
# ---------------------------------------------------------

def evaluate_target_progression(
    target_data,
    current_price,
    targets_reached=None,
):
    """
    Evaluate whether a V14 target level has been reached.

    targets_reached:
        Optional list containing already completed targets,
        for example:
            ["TARGET 1"]

    Target progression is sequential:

        TARGET 1
            ↓
        TARGET 2
            ↓
        TARGET 3

    The function does not determine exit quantity.
    """

    if not isinstance(target_data, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid target data",
        }

    if target_data.get("Status") != "TARGETS_VALIDATED":
        return {
            "Status": "REJECTED",
            "Reason": "Target data must have Status TARGETS_VALIDATED",
        }

    required_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Entry Price",
        "Stop Price",
        "Target 1",
        "Target 2",
        "Target 3",
    ]

    for field in required_fields:
        if field not in target_data:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}",
            }

    try:
        current_price = float(current_price)
    except (TypeError, ValueError):
        return {
            "Status": "REJECTED",
            "Reason": "Current price must be numeric",
        }

    if current_price <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Current price must be greater than zero",
        }

    entry_price = float(target_data["Entry Price"])
    stop_price = float(target_data["Stop Price"])
    target_1 = float(target_data["Target 1"])
    target_2 = float(target_data["Target 2"])
    target_3 = float(target_data["Target 3"])

    if stop_price >= entry_price:
        return {
            "Status": "REJECTED",
            "Reason": "Stop price must be below entry price",
        }

    if not (
        target_1 > entry_price
        and target_2 > target_1
        and target_3 > target_2
    ):
        return {
            "Status": "REJECTED",
            "Reason": "Targets must be strictly increasing",
        }

    # -----------------------------------------------------
    # Normalize target history
    # -----------------------------------------------------

    if targets_reached is None:
        targets_reached = []

    if not isinstance(targets_reached, list):
        return {
            "Status": "REJECTED",
            "Reason": "Targets reached must be a list",
        }

    valid_targets = {
        "TARGET 1",
        "TARGET 2",
        "TARGET 3",
    }

    for target in targets_reached:
        if target not in valid_targets:
            return {
                "Status": "REJECTED",
                "Reason": f"Invalid target history: {target}",
            }

    # -----------------------------------------------------
    # Enforce sequential target progression
    # -----------------------------------------------------

    expected_history = [
        "TARGET 1",
        "TARGET 2",
        "TARGET 3",
    ]

    if targets_reached != expected_history[:len(targets_reached)]:
        return {
            "Status": "REJECTED",
            "Reason": "Target history must follow sequential progression",
        }

    # -----------------------------------------------------
    # Determine next target
    # -----------------------------------------------------

    if "TARGET 1" not in targets_reached:

        next_target = "TARGET 1"
        next_target_price = target_1

    elif "TARGET 2" not in targets_reached:

        next_target = "TARGET 2"
        next_target_price = target_2

    elif "TARGET 3" not in targets_reached:

        next_target = "TARGET 3"
        next_target_price = target_3

    else:

        return {
            "Status": "COMPLETE",
            "Reason": "All three targets have already been reached",
            "Targets Reached": list(targets_reached),
        }

    # -----------------------------------------------------
    # Check whether next target has been reached
    # -----------------------------------------------------

    if current_price < next_target_price:

        return {
            "Status": "WAITING",
            "Target Event": None,
            "Next Target": next_target,
            "Next Target Price": next_target_price,
            "Current Price": current_price,
            "Targets Reached": list(targets_reached),
        }

    # -----------------------------------------------------
    # Target reached
    # -----------------------------------------------------

    updated_targets = list(targets_reached)
    updated_targets.append(next_target)

    final_target = (
        next_target == "TARGET 3"
    )

    return {
        "Status": "TARGET_REACHED",
        "Target Event": next_target,
        "Target Price": next_target_price,
        "Current Price": current_price,
        "Targets Reached": updated_targets,
        "Final Target": final_target,

        "Trading Symbol": target_data["Trading Symbol"],
        "Underlying": target_data["Underlying"],
        "Expiry": target_data["Expiry"],
        "Strike": target_data["Strike"],
        "Option Type": target_data["Option Type"],
    }
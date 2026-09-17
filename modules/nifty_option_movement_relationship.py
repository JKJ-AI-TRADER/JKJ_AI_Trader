"""
JKJ AI Trader
NIFTY Option Movement Relationship — V12.5 Stage 3

Purpose:
Classify the relationship between option price direction
and NIFTY spot direction from V12.5 Stage 1 output.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- calculate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


VALID_DIRECTIONS = {
    "UP",
    "DOWN",
    "FLAT",
}


def classify_movement_relationship(option_direction, nifty_direction):
    """
    Classify the relationship between option and NIFTY direction.
    """

    if option_direction not in VALID_DIRECTIONS:
        return "INVALID"

    if nifty_direction not in VALID_DIRECTIONS:
        return "INVALID"

    if option_direction == "FLAT" and nifty_direction == "FLAT":
        return "BOTH_FLAT"

    if option_direction == nifty_direction:
        return "MOVING_TOGETHER"

    if option_direction in {"UP", "DOWN"} and nifty_direction in {"UP", "DOWN"}:
        return "DIVERGING"

    if option_direction in {"UP", "DOWN"} and nifty_direction == "FLAT":
        return "OPTION_MOVING_NIFTY_FLAT"

    if option_direction == "FLAT" and nifty_direction in {"UP", "DOWN"}:
        return "OPTION_FLAT_NIFTY_MOVING"

    return "INVALID"


def interpret_movement_relationship(direction_result):
    """
    Classify the relationship using V12.5 Stage 1 output.
    """

    if not isinstance(direction_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Direction result must be a dictionary.",
        }

    if direction_result.get("Status") != "INTERPRETED":
        return {
            "Status": "REJECTED",
            "Reason": "Direction result must have Status INTERPRETED.",
        }

    required_fields = [
        "Option Direction",
        "NIFTY Direction",
    ]

    for field in required_fields:
        if field not in direction_result:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    option_direction = direction_result["Option Direction"]
    nifty_direction = direction_result["NIFTY Direction"]

    relationship = classify_movement_relationship(
        option_direction,
        nifty_direction,
    )

    if relationship == "INVALID":
        return {
            "Status": "REJECTED",
            "Reason": "Option or NIFTY direction is invalid.",
        }

    return {
        "Status": "INTERPRETED",
        "Trading Symbol": direction_result.get("Trading Symbol"),
        "Underlying": direction_result.get("Underlying"),
        "Expiry": direction_result.get("Expiry"),
        "Strike": direction_result.get("Strike"),
        "Option Type": direction_result.get("Option Type"),
        "Option Direction": option_direction,
        "NIFTY Direction": nifty_direction,
        "Movement Relationship": relationship,
    }
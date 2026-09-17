"""
JKJ AI Trader
NIFTY Option Movement Direction — V12.5 Stage 1

Purpose:
Classify the direction of measured option and NIFTY movement
from V12.4 analysis output.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- calculate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


def classify_direction(change):
    """
    Classify a measured change as UP, DOWN, or FLAT.
    """

    if not isinstance(change, (int, float)):
        return "INVALID"

    if change > 0:
        return "UP"

    if change < 0:
        return "DOWN"

    return "FLAT"


def interpret_movement_direction(analyzed_movement):
    """
    Classify option price and NIFTY spot movement
    from a V12.4 ANALYZED movement record.
    """

    if not isinstance(analyzed_movement, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Analyzed movement must be a dictionary.",
        }

    if analyzed_movement.get("Status") != "ANALYZED":
        return {
            "Status": "REJECTED",
            "Reason": "Movement must have Status ANALYZED.",
        }

    required_fields = [
        "Option Price Change",
        "NIFTY Spot Change",
    ]

    for field in required_fields:
        if field not in analyzed_movement:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    option_change = analyzed_movement["Option Price Change"]
    nifty_change = analyzed_movement["NIFTY Spot Change"]

    if not isinstance(option_change, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Option Price Change must be numeric.",
        }

    if not isinstance(nifty_change, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "NIFTY Spot Change must be numeric.",
        }

    option_direction = classify_direction(option_change)
    nifty_direction = classify_direction(nifty_change)

    return {
        "Status": "INTERPRETED",
        "Trading Symbol": analyzed_movement.get("Trading Symbol"),
        "Underlying": analyzed_movement.get("Underlying"),
        "Expiry": analyzed_movement.get("Expiry"),
        "Strike": analyzed_movement.get("Strike"),
        "Option Type": analyzed_movement.get("Option Type"),
        "Option Price Change": option_change,
        "Option Direction": option_direction,
        "NIFTY Spot Change": nifty_change,
        "NIFTY Direction": nifty_direction,
    }
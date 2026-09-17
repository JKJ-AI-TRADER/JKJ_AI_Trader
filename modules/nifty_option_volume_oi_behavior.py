"""
JKJ AI Trader
NIFTY Option Volume & OI Behaviour — V12.5 Stage 2

Purpose:
Classify volume and open interest behaviour from
V12.4 analyzed movement data.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- calculate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


def classify_volume_oi_change(change):
    """
    Classify a volume or open interest change.
    """

    if not isinstance(change, (int, float)):
        return "INVALID"

    if change > 0:
        return "INCREASING"

    if change < 0:
        return "DECREASING"

    return "UNCHANGED"


def interpret_volume_oi_behavior(analyzed_movement):
    """
    Classify volume and open interest behaviour
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
        "Volume Change",
        "Open Interest Change",
    ]

    for field in required_fields:
        if field not in analyzed_movement:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    volume_change = analyzed_movement["Volume Change"]
    open_interest_change = analyzed_movement["Open Interest Change"]

    if not isinstance(volume_change, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Volume Change must be numeric.",
        }

    if not isinstance(open_interest_change, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Open Interest Change must be numeric.",
        }

    volume_behavior = classify_volume_oi_change(volume_change)
    open_interest_behavior = classify_volume_oi_change(
        open_interest_change
    )

    return {
        "Status": "INTERPRETED",
        "Trading Symbol": analyzed_movement.get("Trading Symbol"),
        "Underlying": analyzed_movement.get("Underlying"),
        "Expiry": analyzed_movement.get("Expiry"),
        "Strike": analyzed_movement.get("Strike"),
        "Option Type": analyzed_movement.get("Option Type"),
        "Volume Change": volume_change,
        "Volume Behaviour": volume_behavior,
        "Open Interest Change": open_interest_change,
        "Open Interest Behaviour": open_interest_behavior,
    }
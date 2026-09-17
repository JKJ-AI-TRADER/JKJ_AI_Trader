"""
JKJ AI Trader
NIFTY Option Combined Interpretation — V12.5 Stage 4

Purpose:
Combine independently classified movement information
from V12.5 Stages 1, 2, and 3.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- calculate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


def combine_movement_interpretation(
    direction_result,
    volume_oi_result,
    relationship_result,
):
    """
    Combine V12.5 Stage 1, Stage 2, and Stage 3 results.
    """

    if not isinstance(direction_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Direction result must be a dictionary.",
        }

    if not isinstance(volume_oi_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Volume and OI result must be a dictionary.",
        }

    if not isinstance(relationship_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Relationship result must be a dictionary.",
        }

    if direction_result.get("Status") != "INTERPRETED":
        return {
            "Status": "REJECTED",
            "Reason": "Direction result must have Status INTERPRETED.",
        }

    if volume_oi_result.get("Status") != "INTERPRETED":
        return {
            "Status": "REJECTED",
            "Reason": "Volume and OI result must have Status INTERPRETED.",
        }

    if relationship_result.get("Status") != "INTERPRETED":
        return {
            "Status": "REJECTED",
            "Reason": "Relationship result must have Status INTERPRETED.",
        }

    required_direction_fields = [
        "Option Direction",
        "NIFTY Direction",
    ]

    required_volume_oi_fields = [
        "Volume Behaviour",
        "Open Interest Behaviour",
    ]

    required_relationship_fields = [
        "Movement Relationship",
    ]

    for field in required_direction_fields:
        if field not in direction_result:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing direction field: {field}.",
            }

    for field in required_volume_oi_fields:
        if field not in volume_oi_result:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing volume/OI field: {field}.",
            }

    for field in required_relationship_fields:
        if field not in relationship_result:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing relationship field: {field}.",
            }

    identity_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
    ]

    for field in identity_fields:
        direction_value = direction_result.get(field)
        volume_oi_value = volume_oi_result.get(field)
        relationship_value = relationship_result.get(field)

        if (
            direction_value is not None
            and volume_oi_value is not None
            and direction_value != volume_oi_value
        ):
            return {
                "Status": "REJECTED",
                "Reason": f"Identity mismatch between direction and volume/OI: {field}.",
            }

        if (
            direction_value is not None
            and relationship_value is not None
            and direction_value != relationship_value
        ):
            return {
                "Status": "REJECTED",
                "Reason": f"Identity mismatch between direction and relationship: {field}.",
            }

    return {
        "Status": "INTERPRETED",
        "Trading Symbol": direction_result.get("Trading Symbol"),
        "Underlying": direction_result.get("Underlying"),
        "Expiry": direction_result.get("Expiry"),
        "Strike": direction_result.get("Strike"),
        "Option Type": direction_result.get("Option Type"),
        "Option Direction": direction_result["Option Direction"],
        "NIFTY Direction": direction_result["NIFTY Direction"],
        "Movement Relationship": relationship_result["Movement Relationship"],
        "Volume Behaviour": volume_oi_result["Volume Behaviour"],
        "Open Interest Behaviour": volume_oi_result[
            "Open Interest Behaviour"
        ],
    }
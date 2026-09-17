"""
JKJ AI Trader
NIFTY Option Momentum Evidence — V12.6 Stage 1

Purpose:
Define observable evidence relevant to developing option momentum.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- claim momentum persistence
- modify main.py
- modify frozen JKJ modules

Persistence requirement:
At least 3 observations are required before persistence
can be evaluated.
"""


MIN_OBSERVATIONS_FOR_PERSISTENCE = 3


def evaluate_momentum_evidence(combined_interpretation):
    """
    Evaluate observable momentum evidence from V12.5
    combined interpretation output.
    """

    if not isinstance(combined_interpretation, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Combined interpretation must be a dictionary.",
        }

    if combined_interpretation.get("Status") != "INTERPRETED":
        return {
            "Status": "REJECTED",
            "Reason": "Combined interpretation must have Status INTERPRETED.",
        }

    required_fields = [
        "Option Direction",
        "NIFTY Direction",
        "Movement Relationship",
        "Volume Behaviour",
        "Open Interest Behaviour",
    ]

    for field in required_fields:
        if field not in combined_interpretation:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    option_direction = combined_interpretation["Option Direction"]
    nifty_direction = combined_interpretation["NIFTY Direction"]
    relationship = combined_interpretation["Movement Relationship"]
    volume_behaviour = combined_interpretation["Volume Behaviour"]
    oi_behaviour = combined_interpretation["Open Interest Behaviour"]

    price_movement_evidence = option_direction in {"UP", "DOWN"}
    nifty_movement_evidence = nifty_direction in {"UP", "DOWN"}
    volume_evidence = volume_behaviour == "INCREASING"
    oi_evidence = oi_behaviour != "UNCHANGED"

    return {
        "Status": "EVALUATED",
        "Trading Symbol": combined_interpretation.get("Trading Symbol"),
        "Underlying": combined_interpretation.get("Underlying"),
        "Expiry": combined_interpretation.get("Expiry"),
        "Strike": combined_interpretation.get("Strike"),
        "Option Type": combined_interpretation.get("Option Type"),
        "Option Direction": option_direction,
        "NIFTY Direction": nifty_direction,
        "Movement Relationship": relationship,
        "Volume Behaviour": volume_behaviour,
        "Open Interest Behaviour": oi_behaviour,
        "Price Movement Evidence": price_movement_evidence,
        "NIFTY Movement Evidence": nifty_movement_evidence,
        "Volume Evidence": volume_evidence,
        "Open Interest Evidence": oi_evidence,
        "Minimum Observations For Persistence":
            MIN_OBSERVATIONS_FOR_PERSISTENCE,
        "Persistence Status": "NOT_YET_ESTABLISHED",
    }
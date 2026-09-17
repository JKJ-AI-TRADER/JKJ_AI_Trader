"""
JKJ AI Trader
NIFTY Option Momentum Sequence — V12.6 Stage 2

Purpose:
Evaluate whether option price direction persists across
multiple V12.5 Stage 1 direction observations.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules

Persistence requirement:
At least 3 observations are required.
"""


MIN_OBSERVATIONS_FOR_PERSISTENCE = 3

VALID_DIRECTIONS = {
    "UP",
    "DOWN",
    "FLAT",
}


def evaluate_momentum_sequence(direction_results):
    """
    Evaluate option direction persistence across multiple
    V12.5 Stage 1 direction results.
    """

    if not isinstance(direction_results, list):
        return {
            "Status": "REJECTED",
            "Reason": "Direction results must be a list.",
        }

    if len(direction_results) < MIN_OBSERVATIONS_FOR_PERSISTENCE:
        return {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Reason": (
                f"At least {MIN_OBSERVATIONS_FOR_PERSISTENCE} "
                "observations are required."
            ),
            "Observation Count": len(direction_results),
        }

    for result in direction_results:
        if not isinstance(result, dict):
            return {
                "Status": "REJECTED",
                "Reason": "Each direction result must be a dictionary.",
            }

        if result.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Every direction result must have "
                    "Status INTERPRETED."
                ),
            }

        if "Option Direction" not in result:
            return {
                "Status": "REJECTED",
                "Reason": "Missing Option Direction.",
            }

        if result["Option Direction"] not in VALID_DIRECTIONS:
            return {
                "Status": "REJECTED",
                "Reason": "Invalid Option Direction.",
            }

    directions = [
        result["Option Direction"]
        for result in direction_results
    ]

    first_direction = directions[0]

    if first_direction == "FLAT":
        return {
            "Status": "NOT_PERSISTENT",
            "Reason": "Initial option direction is FLAT.",
            "Observation Count": len(direction_results),
            "Direction": "FLAT",
            "Persistence Status": "NOT_PERSISTENT",
            "Direction Sequence": directions,
        }

    if all(direction == first_direction for direction in directions):
        return {
            "Status": "PERSISTENT",
            "Reason": "Option direction remained consistent.",
            "Observation Count": len(direction_results),
            "Direction": first_direction,
            "Persistence Status": "PERSISTENT",
            "Direction Sequence": directions,
        }

    return {
        "Status": "NOT_PERSISTENT",
        "Reason": "Option direction changed during the sequence.",
        "Observation Count": len(direction_results),
        "Direction": first_direction,
        "Persistence Status": "NOT_PERSISTENT",
        "Direction Sequence": directions,
    }
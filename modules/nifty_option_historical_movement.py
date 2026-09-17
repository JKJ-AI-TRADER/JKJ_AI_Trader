"""
JKJ AI Trader
NIFTY Option Historical Movement — V12.4 Stage 3

Purpose:
Read stored NIFTY option observations and calculate movement
between consecutive observations of the same contract.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate momentum
- calculate opportunity scores
- place orders
- modify main.py
- modify frozen JKJ modules
"""

from modules.nifty_option_observation_reader import (
    read_option_observations,
)
from modules.nifty_option_movement_analyzer import (
    analyze_option_movement,
)


NUMERIC_FIELDS = [
    "Strike",
    "Current Price",
    "NIFTY Spot Price",
    "Volume",
    "Open Interest",
]


def convert_observation_types(observation):
    """
    Convert numeric CSV fields from strings to numeric values.
    """

    converted = dict(observation)

    try:
        converted["Strike"] = float(converted["Strike"])
        converted["Current Price"] = float(converted["Current Price"])
        converted["NIFTY Spot Price"] = float(
            converted["NIFTY Spot Price"]
        )
        converted["Volume"] = float(converted["Volume"])
        converted["Open Interest"] = float(
            converted["Open Interest"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "Status": "REJECTED",
            "Reason": f"Invalid numeric observation field: {exc}",
        }

    converted["Status"] = "RECORDED"

    return converted


def analyze_historical_movement(file_path):
    """
    Read historical observations and analyze movement between
    consecutive observations of the same option contract.
    """

    result = read_option_observations(file_path)

    if result["Status"] != "LOADED":
        return {
            "Status": result["Status"],
            "Reason": result["Reason"],
            "Movements": [],
        }

    observations = result["Observations"]

    if len(observations) < 2:
        return {
            "Status": "INSUFFICIENT_DATA",
            "Reason": "At least two observations are required.",
            "Movements": [],
        }

    converted_observations = []

    for observation in observations:
        converted = convert_observation_types(observation)

        if converted["Status"] != "RECORDED":
            return {
                "Status": "REJECTED",
                "Reason": converted["Reason"],
                "Movements": [],
            }

        converted_observations.append(converted)

    movements = []

    for index in range(1, len(converted_observations)):
        previous = converted_observations[index - 1]
        current = converted_observations[index]

        movement = analyze_option_movement(
            previous,
            current,
        )

        if movement["Status"] == "ANALYZED":
            movements.append(movement)

    return {
        "Status": "ANALYZED",
        "Observation Count": len(converted_observations),
        "Movement Count": len(movements),
        "Movements": movements,
    }
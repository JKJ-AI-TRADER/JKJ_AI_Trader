"""
JKJ AI Trader
NIFTY Option Observation Storage — Stage 2

Purpose:
Store validated NIFTY option observations in a CSV file.

This stage does NOT:
- make BUY decisions
- make SELL decisions
- calculate momentum
- calculate opportunity scores
- place orders
- modify main.py
"""

import csv
import os


OBSERVATION_FILE = "nifty_option_observations.csv"


FIELDNAMES = [
    "Timestamp",
    "Trading Symbol",
    "Underlying",
    "Expiry",
    "Strike",
    "Option Type",
    "Current Price",
    "NIFTY Spot Price",
    "Volume",
    "Open Interest",
]


def save_option_observation(observation):
    """
    Append one validated observation to the CSV file.

    Returns
    -------
    dict
        Storage result.
    """

    if not isinstance(observation, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Observation must be a dictionary.",
        }

    if observation.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Reason": "Observation must have RECORDED status.",
        }

    try:

        file_exists = os.path.isfile(
            OBSERVATION_FILE
        )

        with open(
            OBSERVATION_FILE,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES,
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                field: observation.get(field)
                for field in FIELDNAMES
            })

        return {
            "Status": "SAVED",
            "File": OBSERVATION_FILE,
        }

    except Exception as error:

        return {
            "Status": "FAILED",
            "Reason": str(error),
        }
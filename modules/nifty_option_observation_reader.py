"""
JKJ AI Trader
NIFTY Option Observation Reader — V12.4 Stage 2

Purpose:
Read stored NIFTY option observations from the V12.3 CSV file.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate momentum
- calculate opportunity scores
- place orders
- modify main.py
- modify frozen JKJ modules
"""

import csv
import os


OBSERVATION_FILE = "nifty_option_observations.csv"


def read_option_observations(file_path=OBSERVATION_FILE):
    """
    Read stored NIFTY option observations from CSV.

    Returns
    -------
    dict
        Status and observations.
    """

    if not os.path.exists(file_path):
        return {
            "Status": "REJECTED",
            "Reason": "Observation file does not exist.",
            "Observations": [],
        }

    try:
        with open(file_path, "r", newline="") as file:
            reader = csv.DictReader(file)

            observations = list(reader)

    except Exception as exc:
        return {
            "Status": "FAILED",
            "Reason": f"Unable to read observation file: {exc}",
            "Observations": [],
        }

    return {
        "Status": "LOADED",
        "File": file_path,
        "Observation Count": len(observations),
        "Observations": observations,
    }
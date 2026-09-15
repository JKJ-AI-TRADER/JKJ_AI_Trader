"""
JKJ AI Trader
V12.1 — Intraday Option Observation Record

Purpose:
Create a clean, auditable record from a validated option
market observation.

This module does NOT:
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify V1–V11
- modify main.py
"""


def create_option_observation_record(
    validated_option_data,
):
    """
    Create a standardized observation record.

    Parameters
    ----------
    validated_option_data : dict
        Output from the V12.1 observation layer.

    Returns
    -------
    dict
        Clean observation record.
    """

    if not isinstance(validated_option_data, dict):
        return {
            "Status": "INVALID",
            "Reasons": [
                "Validated option data must be a dictionary."
            ],
        }

    if validated_option_data.get("Status") != "READY":
        return {
            "Status": "REJECTED",
            "Reasons": [
                "Only READY observations can create an observation record."
            ],
        }

    return {
        "Status": "RECORDED",
        "Data Status": validated_option_data.get("Data Status"),
        "Trading Symbol": validated_option_data.get(
            "Trading Symbol"
        ),
        "Instrument Token": validated_option_data.get(
            "Instrument Token"
        ),
        "Underlying": validated_option_data.get(
            "Underlying"
        ),
        "Current Price": validated_option_data.get(
            "Current Price"
        ),
        "Open": validated_option_data.get(
            "Open"
        ),
        "High": validated_option_data.get(
            "High"
        ),
        "Low": validated_option_data.get(
            "Low"
        ),
        "Previous Close": validated_option_data.get(
            "Previous Close"
        ),
        "Volume": validated_option_data.get(
            "Volume"
        ),
        "Open Interest": validated_option_data.get(
            "Open Interest"
        ),
        "Last Trade Time": validated_option_data.get(
            "Last Trade Time"
        ),
        "Observation Timestamp": validated_option_data.get(
            "Observation Timestamp"
        ),
    }
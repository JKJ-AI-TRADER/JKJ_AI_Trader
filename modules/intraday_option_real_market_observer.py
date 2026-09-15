"""
JKJ AI Trader
V12.1 — Intraday Option Real-Market Observer

Purpose:
Observe and validate real-market option data supplied by the broker.

This module does NOT:
- place orders
- make BUY/SELL decisions
- calculate new momentum
- modify V1–V11
- connect to main.py
"""


from datetime import datetime


def observe_option_market(
    option_data,
    underlying_data=None,
):
    """
    Validate and normalize a single real-market option observation.

    Parameters
    ----------
    option_data : dict
        Raw option market observation.

    underlying_data : dict, optional
        Raw underlying (NIFTY) market observation.

    Returns
    -------
    dict
        Validated market observation.
    """

    if not isinstance(option_data, dict):
        return {
            "Status": "INVALID",
            "Data Status": "INVALID",
            "Reasons": ["Option market data must be a dictionary."],
        }

    required_fields = [
    "Trading Symbol",
    "Instrument Token",
    "Current Price",
    "Volume",
    "Last Trade Time",
]

    missing_fields = [
        field for field in required_fields
        if field not in option_data
    ]

    if missing_fields:
        return {
            "Status": "INCOMPLETE",
            "Data Status": "INCOMPLETE",
            "Reasons": [
                f"Missing required field: {field}"
                for field in missing_fields
            ],
        }

    current_price = option_data.get("Current Price")

    if not isinstance(current_price, (int, float)):
        return {
            "Status": "INVALID",
            "Data Status": "INVALID",
            "Reasons": ["Current Price must be numeric."],
        }

    if current_price <= 0:
        return {
            "Status": "INVALID",
            "Data Status": "INVALID",
            "Reasons": ["Current Price must be greater than zero."],
        }
    volume = option_data.get("Volume")

    if not isinstance(volume, (int, float)):
        return {
            "Status": "INCOMPLETE",
            "Data Status": "INCOMPLETE",
            "Reasons": ["Volume must be numeric."],
        }

    if volume <= 0:
        return {
            "Status": "INCOMPLETE",
            "Data Status": "INCOMPLETE",
            "Reasons": ["Volume must be greater than zero."],
        }

    last_trade_time = option_data.get("Last Trade Time")

    if not last_trade_time:
        return {
            "Status": "INCOMPLETE",
            "Data Status": "INCOMPLETE",
            "Reasons": ["Last Trade Time is required."],
        }
    try:
        if isinstance(last_trade_time, str):
            trade_time = datetime.fromisoformat(
                last_trade_time.replace("Z", "+00:00")
            )
        else:
            trade_time = last_trade_time

        observation_time = datetime.now(
            trade_time.tzinfo
        ) if trade_time.tzinfo else datetime.now()

        age_seconds = (
            observation_time - trade_time
        ).total_seconds()

    except (TypeError, ValueError):
        return {
            "Status": "INVALID",
            "Data Status": "INVALID",
            "Reasons": ["Last Trade Time could not be parsed."],
        }

    if age_seconds > 300:
        return {
            "Status": "STALE",
            "Data Status": "STALE",
            "Reasons": [
                "Last Trade Time is older than 5 minutes."
            ],
        }
    observation = dict(option_data)

    observation["Observation Timestamp"] = datetime.now().isoformat()

    observation["Underlying Data"] = (
        dict(underlying_data)
        if isinstance(underlying_data, dict)
        else None
    )

    observation["Status"] = "READY"
    observation["Data Status"] = "VALID"

    observation["Reasons"] = [
        "Option market observation received and basic validation passed."
    ]

    return observation
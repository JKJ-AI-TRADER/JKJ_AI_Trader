"""
JKJ AI Trader
NIFTY Option Movement Analyzer — V12.4 Stage 1

Purpose:
Compare two observations of the SAME NIFTY option contract
and calculate measurable market movement.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- calculate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


def analyze_option_movement(previous_observation, current_observation):
    """
    Compare two recorded observations of the same NIFTY option contract.

    Returns
    -------
    dict
        Measured movement between the two observations.
    """

    if not isinstance(previous_observation, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Previous observation must be a dictionary.",
        }

    if not isinstance(current_observation, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Current observation must be a dictionary.",
        }

    if previous_observation.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Reason": "Previous observation must have Status RECORDED.",
        }

    if current_observation.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Reason": "Current observation must have Status RECORDED.",
        }

    contract_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
    ]

    for field in contract_fields:
        if previous_observation.get(field) != current_observation.get(field):
            return {
                "Status": "REJECTED",
                "Reason": f"Observations belong to different contracts: {field}.",
            }

    required_fields = [
        "Current Price",
        "NIFTY Spot Price",
        "Volume",
        "Open Interest",
        "Timestamp",
    ]

    for field in required_fields:
        if field not in previous_observation or field not in current_observation:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    previous_price = previous_observation["Current Price"]
    current_price = current_observation["Current Price"]

    previous_spot = previous_observation["NIFTY Spot Price"]
    current_spot = current_observation["NIFTY Spot Price"]

    previous_volume = previous_observation["Volume"]
    current_volume = current_observation["Volume"]

    previous_oi = previous_observation["Open Interest"]
    current_oi = current_observation["Open Interest"]

    numeric_values = [
        previous_price,
        current_price,
        previous_spot,
        current_spot,
        previous_volume,
        current_volume,
        previous_oi,
        current_oi,
    ]

    if not all(isinstance(value, (int, float)) for value in numeric_values):
        return {
            "Status": "REJECTED",
            "Reason": "Movement fields must be numeric.",
        }

    if previous_price <= 0 or previous_spot <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Previous price and NIFTY spot must be greater than zero.",
        }

    if current_price <= 0 or current_spot <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Current price and NIFTY spot must be greater than zero.",
        }

    if previous_volume < 0 or current_volume < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Volume cannot be negative.",
        }

    if previous_oi < 0 or current_oi < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Open interest cannot be negative.",
        }

    option_price_change = current_price - previous_price
    option_price_change_pct = (
        option_price_change / previous_price
    ) * 100

    nifty_spot_change = current_spot - previous_spot
    nifty_spot_change_pct = (
        nifty_spot_change / previous_spot
    ) * 100

    volume_change = current_volume - previous_volume
    open_interest_change = current_oi - previous_oi

    return {
        "Status": "ANALYZED",
        "Trading Symbol": current_observation["Trading Symbol"],
        "Underlying": current_observation["Underlying"],
        "Expiry": current_observation["Expiry"],
        "Strike": current_observation["Strike"],
        "Option Type": current_observation["Option Type"],
        "Previous Timestamp": previous_observation["Timestamp"],
        "Current Timestamp": current_observation["Timestamp"],
        "Previous Option Price": previous_price,
        "Current Option Price": current_price,
        "Option Price Change": option_price_change,
        "Option Price Change %": option_price_change_pct,
        "Previous NIFTY Spot": previous_spot,
        "Current NIFTY Spot": current_spot,
        "NIFTY Spot Change": nifty_spot_change,
        "NIFTY Spot Change %": nifty_spot_change_pct,
        "Previous Volume": previous_volume,
        "Current Volume": current_volume,
        "Volume Change": volume_change,
        "Previous Open Interest": previous_oi,
        "Current Open Interest": current_oi,
        "Open Interest Change": open_interest_change,
    }
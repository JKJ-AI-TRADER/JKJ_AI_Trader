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

import math
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MAX_AGE_SECONDS = 300
MAX_FUTURE_SKEW_SECONDS = 5


def _is_finite_number(value):
    """Reject Booleans, non-numeric values, NaN and infinity."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False

    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _result(status, reason):
    return {
        "Status": status,
        "Data Status": status if status != "READY" else "VALID",
        "Reasons": [reason],
    }


def _parse_trade_time(value):
    """Parse a trade timestamp; naive exchange times are interpreted as IST."""
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValueError("Empty timestamp.")
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if not isinstance(value, datetime):
        raise TypeError("Timestamp must be a string or datetime.")

    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=IST)

    return value.astimezone(IST)


def observe_option_market(option_data, underlying_data=None):
    """
    Validate and normalize a single real-market option observation.

    This function performs validation only. It does not connect to a broker,
    place orders, or create or modify a trade.
    """

    if not isinstance(option_data, dict):
        return _result(
            "INVALID",
            "Option market data must be a dictionary.",
        )

    required_fields = [
        "Trading Symbol",
        "Instrument Token",
        "Current Price",
        "Volume",
        "Last Trade Time",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in option_data or option_data[field] is None
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

    trading_symbol = option_data["Trading Symbol"]
    if not isinstance(trading_symbol, str) or not trading_symbol.strip():
        return _result("INVALID", "Trading Symbol must be non-empty text.")

    token = option_data["Instrument Token"]
    if isinstance(token, bool) or not isinstance(token, int) or token <= 0:
        return _result(
            "INVALID",
            "Instrument Token must be a positive integer.",
        )

    current_price = option_data["Current Price"]
    if not _is_finite_number(current_price):
        return _result(
            "INVALID",
            "Current Price must be a finite number.",
        )

    if current_price <= 0:
        return _result(
            "INVALID",
            "Current Price must be greater than zero.",
        )

    volume = option_data["Volume"]
    if not _is_finite_number(volume):
        return _result("INVALID", "Volume must be a finite number.")

    # Preserve the existing observer rule: zero or negative volume is
    # incomplete data and is not accepted as a READY observation.
    if volume <= 0:
        return _result(
            "INCOMPLETE",
            "Volume must be greater than zero.",
        )

    last_trade_time = option_data["Last Trade Time"]
    if not last_trade_time:
        return _result("INCOMPLETE", "Last Trade Time is required.")

    try:
        trade_time = _parse_trade_time(last_trade_time)
        observation_time = datetime.now(IST)
        age_seconds = (observation_time - trade_time).total_seconds()
    except (TypeError, ValueError, OverflowError):
        return _result(
            "INVALID",
            "Last Trade Time could not be parsed.",
        )

    if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
        return _result(
            "INVALID",
            "Last Trade Time is too far in the future.",
        )

    # Allow a small five-second clock skew without assigning a negative age.
    if age_seconds < 0:
        age_seconds = 0

    if age_seconds > MAX_AGE_SECONDS:
        return _result(
            "STALE",
            "Last Trade Time is older than 5 minutes.",
        )

    observation = dict(option_data)
    observation["Observation Timestamp"] = observation_time.isoformat()
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

"""
JKJ AI Trader
Intraday Option Market Data Provider V3

Purpose:
Provide a clean structure for option market data.

V3 is intentionally broker-independent.

This module does NOT:
- connect to Zerodha
- place orders
- make BUY/SELL decisions
- modify main.py
"""

import math
from datetime import datetime


def _is_finite_number(value):
    """Accept finite integers/floats, but reject booleans and invalid values."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False

    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _invalid(reason):
    return {
        "Status": "INVALID",
        "Reasons": [reason],
    }


def create_option_market_data(
    trading_symbol,
    instrument_token,
    underlying,
    expiry,
    strike,
    option_type,
    current_price,
    open_price,
    high_price,
    low_price,
    volume,
    timestamp=None,
):
    """
    Create a standardized option market-data record.
    """

    # ---------------------------------------------------------
    # REQUIRED IDENTIFIERS
    # ---------------------------------------------------------

    if not trading_symbol:
        return _invalid("Trading symbol is required.")

    if instrument_token is None:
        return _invalid("Instrument token is required.")

    if underlying != "NIFTY":
        return _invalid("Only NIFTY options are supported in V3.")

    if option_type not in ("CE", "PE"):
        return _invalid("Option type must be CE or PE.")

    # ---------------------------------------------------------
    # NUMERIC VALIDATION
    # ---------------------------------------------------------

    numeric_values = {
        "Current Price": current_price,
        "Open": open_price,
        "High": high_price,
        "Low": low_price,
        "Volume": volume,
        "Strike": strike,
    }

    for field, value in numeric_values.items():
        if value is None:
            return _invalid(f"{field} is required.")

        if isinstance(value, bool):
            return _invalid(f"{field} must be a finite number, not a Boolean.")

        if not isinstance(value, (int, float)):
            return _invalid(f"{field} must be numeric.")

        if not _is_finite_number(value):
            return _invalid(f"{field} must be finite.")

    if current_price <= 0:
        return _invalid("Current price must be greater than zero.")

    if open_price <= 0:
        return _invalid("Open price must be greater than zero.")

    if high_price <= 0:
        return _invalid("High price must be greater than zero.")

    if low_price <= 0:
        return _invalid("Low price must be greater than zero.")

    if volume < 0:
        return _invalid("Volume cannot be negative.")

    if strike <= 0:
        return _invalid("Strike must be greater than zero.")

    # ---------------------------------------------------------
    # OHLC CONSISTENCY
    # ---------------------------------------------------------

    if high_price < low_price:
        return _invalid("High price cannot be lower than low price.")

    if not low_price <= current_price <= high_price:
        return _invalid(
            "Current price must be within the reported low-high range."
        )

    if not low_price <= open_price <= high_price:
        return _invalid(
            "Open price must be within the reported low-high range."
        )

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    # ---------------------------------------------------------
    # PRICE CHANGE AND INTRADAY RANGE
    # ---------------------------------------------------------

    price_change = current_price - open_price
    price_change_percentage = (price_change / open_price) * 100
    intraday_range = high_price - low_price
    intraday_range_percentage = (intraday_range / low_price) * 100

    calculated_values = {
        "Price Change": price_change,
        "Price Change %": price_change_percentage,
        "Intraday Range": intraday_range,
        "Intraday Range %": intraday_range_percentage,
    }

    for field, value in calculated_values.items():
        if not _is_finite_number(value):
            return _invalid(
                f"Calculated {field} is non-finite; market data rejected."
            )

    # ---------------------------------------------------------
    # STANDARDIZED OUTPUT
    # ---------------------------------------------------------

    return {
        "Status": "READY",
        "Data Status": "VALID",
        "Trading Symbol": trading_symbol,
        "Instrument Token": instrument_token,
        "Underlying": underlying,
        "Expiry": expiry,
        "Strike": strike,
        "Option Type": option_type,
        "Current Price": current_price,
        "Open": open_price,
        "High": high_price,
        "Low": low_price,
        "Volume": volume,
        "Price Change": round(price_change, 4),
        "Price Change %": round(price_change_percentage, 4),
        "Intraday Range": round(intraday_range, 4),
        "Intraday Range %": round(intraday_range_percentage, 4),
        "Timestamp": timestamp,
        "Last Trade Time": timestamp,
    }

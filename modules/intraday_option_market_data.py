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

from datetime import datetime


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
    # VALIDATION
    # ---------------------------------------------------------

    if not trading_symbol:
        return {
            "Status": "INVALID",
            "Reasons": ["Trading symbol is required."],
        }

    if instrument_token is None:
        return {
            "Status": "INVALID",
            "Reasons": ["Instrument token is required."],
        }

    if underlying != "NIFTY":
        return {
            "Status": "INVALID",
            "Reasons": ["Only NIFTY options are supported in V3."],
        }

    if option_type not in ("CE", "PE"):
        return {
            "Status": "INVALID",
            "Reasons": ["Option type must be CE or PE."],
        }

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
            return {
                "Status": "INVALID",
                "Reasons": [f"{field} is required."],
            }

        if not isinstance(value, (int, float)):
            return {
                "Status": "INVALID",
                "Reasons": [f"{field} must be numeric."],
            }

    if current_price <= 0:
        return {
            "Status": "INVALID",
            "Reasons": ["Current price must be greater than zero."],
        }

    if open_price <= 0:
        return {
            "Status": "INVALID",
            "Reasons": ["Open price must be greater than zero."],
        }

    if high_price <= 0:
        return {
            "Status": "INVALID",
            "Reasons": ["High price must be greater than zero."],
        }

    if low_price <= 0:
        return {
            "Status": "INVALID",
            "Reasons": ["Low price must be greater than zero."],
        }

    if volume < 0:
        return {
            "Status": "INVALID",
            "Reasons": ["Volume cannot be negative."],
        }

    if strike <= 0:
        return {
            "Status": "INVALID",
            "Reasons": ["Strike must be greater than zero."],
        }

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    # ---------------------------------------------------------
    # PRICE CHANGE
    # ---------------------------------------------------------

    price_change = current_price - open_price

    if open_price > 0:
        price_change_percentage = (
            price_change / open_price
        ) * 100
    else:
        price_change_percentage = 0.0

    # ---------------------------------------------------------
    # INTRADAY RANGE
    # ---------------------------------------------------------

    intraday_range = high_price - low_price

    if low_price > 0:
        intraday_range_percentage = (
            intraday_range / low_price
        ) * 100
    else:
        intraday_range_percentage = 0.0

    # ---------------------------------------------------------
    # DATA STATUS
    # ---------------------------------------------------------

    data_status = "VALID"

    return {
        "Status": "READY",
        "Data Status": data_status,
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
        "Price Change %": round(
            price_change_percentage,
            4
        ),
        "Intraday Range": round(
            intraday_range,
            4
        ),
        "Intraday Range %": round(
            intraday_range_percentage,
            4
        ),
        "Timestamp": timestamp,
    }
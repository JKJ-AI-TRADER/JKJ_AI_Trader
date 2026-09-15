"""
JKJ AI Trader
V12.1 — Zerodha Option Market Adapter

Purpose:
Convert a Zerodha Kite quote response into the normalized
market-data structure expected by the V12.1 observer.

This module does NOT:
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify V1–V11
- modify main.py
"""


def adapt_zerodha_option_quote(
    quote_response,
    trading_symbol,
    instrument_token,
    underlying="NIFTY",
):
    """
    Convert a Zerodha quote response into V12.1 option data.

    Parameters
    ----------
    quote_response : dict
        Raw response returned by kite.quote().

    trading_symbol : str
        Zerodha option trading symbol.

    instrument_token : int
        Zerodha instrument token.

    underlying : str
        Underlying instrument name.

    Returns
    -------
    dict
        Normalized option market observation.
    """

    if not isinstance(quote_response, dict):
        return {
            "Status": "INVALID",
            "Reasons": ["Zerodha quote response must be a dictionary."],
        }

    if not trading_symbol:
        return {
            "Status": "INVALID",
            "Reasons": ["Trading Symbol is required."],
        }

    if instrument_token is None:
        return {
            "Status": "INVALID",
            "Reasons": ["Instrument Token is required."],
        }

    quote_key = f"NFO:{trading_symbol}"

    raw_data = quote_response.get(quote_key)

    if not isinstance(raw_data, dict):
        return {
            "Status": "INCOMPLETE",
            "Reasons": [
                "Option quote was not found or is not a valid dictionary."
            ],
        }

    if not isinstance(raw_data, dict):
        return {
            "Status": "INCOMPLETE",
            "Reasons": [
                "Option quote was not found in the Zerodha response."
            ],
        }

    return {
        "Trading Symbol": trading_symbol,
        "Instrument Token": instrument_token,
        "Underlying": underlying,
        "Current Price": raw_data.get("last_price"),
        "Open": raw_data.get("ohlc", {}).get("open"),
        "High": raw_data.get("ohlc", {}).get("high"),
        "Low": raw_data.get("ohlc", {}).get("low"),
        "Previous Close": raw_data.get("ohlc", {}).get("close"),
        "Volume": raw_data.get("volume"),
        "Open Interest": raw_data.get("oi"),
        "Last Trade Time": raw_data.get("last_trade_time"),
    }
"""
JKJ AI Trader
NIFTY Option Movement Recorder — Stage 1

Purpose:
Record a single validated NIFTY option market observation.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- place orders
- modify main.py
- modify frozen JKJ modules
"""

from datetime import datetime


def record_option_observation(
    trading_symbol,
    underlying,
    expiry,
    strike,
    option_type,
    current_price,
    volume,
    open_interest,
    nifty_spot_price,
    timestamp=None,
):
    """
    Create one validated NIFTY option market observation.

    Returns
    -------
    dict
        Recorded option observation.
    """

    if not isinstance(trading_symbol, str) or not trading_symbol.strip():
        return {
            "Status": "REJECTED",
            "Reason": "Trading symbol is required.",
        }

    if not isinstance(underlying, str) or not underlying.strip():
        return {
            "Status": "REJECTED",
            "Reason": "Underlying is required.",
        }

    if not isinstance(expiry, str) or not expiry.strip():
        return {
            "Status": "REJECTED",
            "Reason": "Expiry is required.",
        }

    if not isinstance(strike, (int, float)) or strike <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Strike must be greater than zero.",
        }

    if option_type not in ("CE", "PE"):
        return {
            "Status": "REJECTED",
            "Reason": "Option type must be CE or PE.",
        }

    if not isinstance(current_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Current price must be numeric.",
        }

    if current_price <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Current price must be greater than zero.",
        }
    if not isinstance(nifty_spot_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "NIFTY spot price must be numeric.",
        }

    if nifty_spot_price <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "NIFTY spot price must be greater than zero.",
        }

    if not isinstance(volume, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Volume must be numeric.",
        }

    if volume < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Volume cannot be negative.",
        }

    if not isinstance(open_interest, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Open interest must be numeric.",
        }

    if open_interest < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Open interest cannot be negative.",
        }

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    if not isinstance(timestamp, str) or not timestamp.strip():
        return {
            "Status": "REJECTED",
            "Reason": "Timestamp is required.",
        }

    return {
        "Status": "RECORDED",
        "Trading Symbol": trading_symbol.strip(),
        "Underlying": underlying.strip(),
        "Expiry": expiry.strip(),
        "Strike": strike,
        "Option Type": option_type,
        "Current Price": current_price,
        "NIFTY Spot Price": nifty_spot_price,
        "Volume": volume,
        "Open Interest": open_interest,
        "Timestamp": timestamp,
    }
"""
JKJ AI Trader
V12.2 — Real Market to Paper Position Bridge

Purpose:
Convert a validated real-market option observation into a
safe paper-position price update.

This module does NOT:
- place live orders
- create live positions
- make BUY decisions
- calculate new momentum
- modify V1–V11
- modify main.py
"""


def bridge_real_market_to_paper(
    observation_record,
    paper_trade,
):
    """
    Apply a validated real-market option price to an
    existing paper trade.

    Parameters
    ----------
    observation_record : dict
        Validated V12.1 observation record.

    paper_trade : dict
        Existing paper trade.

    Returns
    -------
    dict
        Safe bridge result.
    """

    if not isinstance(observation_record, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Observation record must be a dictionary.",
        }

    if observation_record.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Reason": "Only RECORDED observations can enter the paper bridge.",
        }

    if observation_record.get("Data Status") != "VALID":
        return {
            "Status": "REJECTED",
            "Reason": "Observation data is not VALID.",
        }

    if not isinstance(paper_trade, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Paper trade must be a dictionary.",
        }

    current_price = observation_record.get("Current Price")

    if not isinstance(current_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Observation price must be numeric.",
        }

    if current_price <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Observation price must be greater than zero.",
        }

    updated_trade = dict(paper_trade)

    updated_trade["Current Price"] = current_price
    updated_trade["Market Source"] = "ZERODHA REAL MARKET"
    updated_trade["Market Data Status"] = "VALID"
    updated_trade["Observation Timestamp"] = (
        observation_record.get("Observation Timestamp")
    )

    return {
        "Status": "BRIDGED",
        "Market Source": "ZERODHA REAL MARKET",
        "Market Data Status": "VALID",
        "Trading Symbol": observation_record.get(
            "Trading Symbol"
        ),
        "Current Price": current_price,
        "Observation Timestamp": observation_record.get(
            "Observation Timestamp"
        ),
        "Paper Trade": updated_trade,
    }
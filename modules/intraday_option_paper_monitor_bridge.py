"""
JKJ AI Trader
V12.3 — Option Paper Monitor Bridge

Purpose:
Pass an existing V11 paper position and a validated
real-market price into the frozen V10 option position monitor.

This module does NOT:
- place live orders
- create live positions
- make BUY decisions
- execute paper exits
- calculate new momentum
- modify V1–V12.2
- modify main.py
"""


from modules.intraday_option_paper_position_monitor import (
    monitor_option_paper_position,
)


def monitor_real_market_paper_position(
    observation_record,
    paper_trade,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    holding_minutes=0,
    max_holding_minutes=60,
):
    """
    Send a validated real-market observation into V10.

    Parameters
    ----------
    observation_record : dict
        V12.2 recorded market observation.

    paper_trade : dict
        Existing V11 paper position.

    Returns
    -------
    dict
        V10 monitoring result.
    """

    if not isinstance(observation_record, dict):
        return {
            "Status": "REJECTED",
            "Decision": "NO TRADE",
            "Reason": "Observation record must be a dictionary.",
        }

    if observation_record.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Decision": "NO TRADE",
            "Reason": "Observation must have RECORDED status.",
        }

    if observation_record.get("Data Status") != "VALID":
        return {
            "Status": "REJECTED",
            "Decision": "NO TRADE",
            "Reason": "Observation data is not VALID.",
        }

    if not isinstance(paper_trade, dict):
        return {
            "Status": "REJECTED",
            "Decision": "NO TRADE",
            "Reason": "Paper trade must be a dictionary.",
        }

    current_price = observation_record.get(
        "Current Price"
    )

    if not isinstance(current_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Decision": "NO TRADE",
            "Reason": "Current market price must be numeric.",
        }

    if current_price <= 0:
        return {
            "Status": "REJECTED",
            "Decision": "NO TRADE",
            "Reason": "Current market price must be greater than zero.",
        }

    monitor_result = monitor_option_paper_position(
        trade=paper_trade,
        current_price=current_price,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
        holding_minutes=holding_minutes,
        max_holding_minutes=max_holding_minutes,
    )

    return {
        "Status": "MONITORED",
        "Market Source": "ZERODHA REAL MARKET",
        "Market Data Status": "VALID",
        "Trading Symbol": observation_record.get(
            "Trading Symbol"
        ),
        "Current Price": current_price,
        "V10 Result": monitor_result,
    }
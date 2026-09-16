"""
JKJ AI Trader
Intraday Option Paper Coordinator V9

Wisdom Before Wealth.

Purpose:
Coordinate an approved option entry into the
existing paper-trading engine.

V9 does NOT:
- place broker orders
- connect to Zerodha
- modify main.py
- recalculate momentum
- replace the Entry Gate
- modify the existing paper-trading engine
"""

from modules.intraday_paper_trading import (
    open_paper_trade
)


def open_option_paper_position(
    entry_result,
    trading_symbol,
    underlying,
    expiry,
    strike,
    option_type,
    entry_price,
    quantity,
    stop_loss_price,
    target_price,
):
    """
    Open an option paper position only when the
    V8 Entry Bridge has approved the trade.

    Returns a paper-trade assessment.
    """

    # -----------------------------------------
    # 1. BASIC VALIDATION
    # -----------------------------------------

    if not isinstance(entry_result, dict):

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Entry result must be a dictionary."
            ]
        }

    if entry_result.get("Status") != "READY":

        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Reasons": [
                "Entry result is not ready."
            ]
        }

    if entry_result.get("Decision") not in (
        "ENTRY CANDIDATE",
        "STRONG ENTRY CANDIDATE"
    ):

        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Reasons": [
                "Entry bridge has not approved a paper entry."
            ]
        }

    # -----------------------------------------
    # 2. REQUIRED OPTION INFORMATION
    # -----------------------------------------

    if not isinstance(trading_symbol, str) or not trading_symbol.strip():

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Trading symbol is required."
            ]
        }

    if option_type not in ("CE", "PE"):

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Option type must be CE or PE."
            ]
        }

    # -----------------------------------------
    # 3. NUMERIC VALIDATION
    # -----------------------------------------

    numeric_values = {
        "Entry Price": entry_price,
        "Quantity": quantity,
        "Stop Loss": stop_loss_price,
        "Target Price": target_price
    }

    for field, value in numeric_values.items():

        if not isinstance(value, (int, float)):

            return {
                "Status": "INVALID",
                "Decision": "NO TRADE",
                "Reasons": [
                    f"{field} must be numeric."
                ]
            }

    if entry_price <= 0:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Entry price must be greater than zero."
            ]
        }

    if quantity <= 0:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Quantity must be greater than zero."
            ]
        }

    if stop_loss_price >= entry_price:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Stop loss must be below entry price."
            ]
        }

    if target_price <= entry_price:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Target price must be above entry price."
            ]
        }

    # -----------------------------------------
    # 4. OPEN PAPER TRADE
    # -----------------------------------------

    trade = open_paper_trade(
    trade_id=f"OPT-{trading_symbol}",
    symbol=trading_symbol,
    instrument_type="OPTION",
    entry_price=entry_price,
    quantity=quantity,
    stop_loss=stop_loss_price,
    target=target_price,
    momentum_score=entry_result.get("Momentum Score"),
    entry_status=entry_result.get("Decision"),
    entry_reason="Approved by V8 Option Entry Bridge",
    expiry=expiry,
    strike=strike,
    option_type=option_type,
    underlying=underlying,
)

    # -----------------------------------------
    # 5. PAPER TRADE RESULT
    # -----------------------------------------

    return {
        "Status": "READY",
        "Decision": "PAPER TRADE OPENED",
        "Trading Symbol": trading_symbol,
        "Underlying": underlying,
        "Expiry": expiry,
        "Strike": strike,
        "Option Type": option_type,
        "Entry Price": entry_price,
        "Quantity": quantity,
        "Stop Loss": stop_loss_price,
        "Target Price": target_price,
        "Entry Result": entry_result,
        "Paper Trade": trade,
        "Reasons": [
            "Approved option entry has been opened "
            "in paper trading only."
        ],
    }
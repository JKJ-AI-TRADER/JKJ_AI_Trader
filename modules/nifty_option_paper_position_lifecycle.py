"""
JKJ AI Trader
V15.4 Paper Position Lifecycle

Purpose:
    Orchestrate the existing V11 paper-trading lifecycle
    without duplicating its trading logic.

Flow:

    OPEN PAPER TRADE
          ↓
    PRICE UPDATE / PEAK
          ↓
    EXPLICIT EXIT EVENT
          ↓
    V11 POSITION SLICING
          ↓
    PAPER SELL
          ↓
    REMAINING POSITION
          ↓
    CLOSED POSITION

This module does NOT:
    - generate trading signals
    - decide BUY/SELL
    - modify V11
    - modify V12/V13/V14
    - connect to Zerodha
    - place real orders
    - modify main.py

Wisdom Before Wealth.
"""

from modules.intraday_paper_trading import (
    update_paper_price,
    process_paper_exit,
    get_paper_position,
)


# ---------------------------------------------------------
# 1. Update paper position price
# ---------------------------------------------------------

def update_paper_position(
    trade,
    current_price,
):
    """
    Update the current price and peak price using V11.
    """

    return update_paper_price(
        trade=trade,
        current_price=current_price,
    )


# ---------------------------------------------------------
# 2. Process an explicit exit event
# ---------------------------------------------------------

def process_paper_position_exit(
    trade,
    current_price,
    exit_signal,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    costs=0.0,
    slippage=0.0,
    timestamp=None,
):
    """
    Pass an explicit exit event to the V11 paper engine.

    V11 remains responsible for:
        - slicing
        - exit quantity
        - paper SELL
        - remaining position
        - closed position
        - P&L recording
    """

    return process_paper_exit(
        trade=trade,
        current_price=current_price,
        exit_signal=exit_signal,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
        costs=costs,
        slippage=slippage,
        timestamp=timestamp,
    )


# ---------------------------------------------------------
# 3. Read current paper position
# ---------------------------------------------------------

def get_current_paper_position(
    trade,
):
    """
    Return the current V11 paper position state.
    """

    return get_paper_position(
        trade=trade,
    )
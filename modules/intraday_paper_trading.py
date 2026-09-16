"""
JKJ AI Trader
Intraday Paper Trading Engine V1

Purpose:
    Simulate the lifecycle of an intraday trade without placing
    any real broker orders.

Flow:
    PAPER BUY
        ↓
    OPEN POSITION
        ↓
    UPDATE PRICE / PEAK
        ↓
    EXIT SIGNAL
        ↓
    POSITION & SLICING
        ↓
    PAPER SELL
        ↓
    REMAINING POSITION
        ↓
    CLOSED POSITION

This module does NOT:
    - place live orders
    - connect to Zerodha
    - modify main.py
    - generate trading signals

Wisdom Before Wealth.
"""

from modules.intraday_trade_logger import (
    create_trade_record,
    update_peak_price,
    record_sell_event,
)

from modules.intraday_position_slicing import (
    calculate_slice_plan,
)


# ---------------------------------------------------------
# 1. Open a paper trade
# ---------------------------------------------------------

def open_paper_trade(
    trade_id,
    symbol,
    instrument_type,
    entry_price,
    quantity,
    stop_loss=None,
    target=None,
    momentum_score=None,
    entry_status=None,
    entry_reason=None,
    expiry=None,
    strike=None,
    option_type=None,
    underlying=None,
    entry_time=None,
):
    """
    Open a new paper-trading position.
    """

    trade = create_trade_record(
        trade_id=trade_id,
        symbol=symbol,
        instrument_type=instrument_type,
        expiry=expiry,
        strike=strike,
        option_type=option_type,
        underlying=underlying,
        entry_time=entry_time,
        entry_price=entry_price,
        quantity=quantity,
        stop_loss=stop_loss,
        target=target,
        momentum_score=momentum_score,
        entry_status=entry_status,
        entry_reason=entry_reason,
    )

    return trade


# ---------------------------------------------------------
# 2. Update the paper position with current price
# ---------------------------------------------------------

def update_paper_price(
    trade,
    current_price,
):
    """
    Update the current market price and peak price.

    No BUY/SELL decision is made here.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    if trade.get("Status") != "OPEN":
        return {
            "Status": "ERROR",
            "Reason": "Trade is not open",
        }

    try:
        current_price = float(current_price)
    except (TypeError, ValueError):
        return {
            "Status": "ERROR",
            "Reason": "Invalid current price",
        }

    if current_price <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Current price must be greater than zero",
        }

    update_peak_price(
        trade,
        current_price,
    )

    trade["Current Price"] = round(
        current_price,
        4,
    )

    entry_price = trade.get("Entry Price", 0)

    if entry_price > 0:
        current_profit_percentage = (
            (current_price - entry_price)
            / entry_price
        ) * 100
    else:
        current_profit_percentage = 0.0

    return {
        "Status": "UPDATED",
        "Current Price": round(current_price, 4),
        "Peak Price": trade.get("Peak Price"),
        "Current Profit %": round(
            current_profit_percentage,
            2,
        ),
        "Peak Profit %": trade.get("Peak Profit %", 0.0),
        "Current Quantity": trade.get(
            "Current Quantity",
            0,
        ),
    }


# ---------------------------------------------------------
# 3. Process an exit signal
# ---------------------------------------------------------

def process_paper_exit(
    trade,
    current_price,
    exit_signal,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    gross_pnl=None,
    costs=0.0,
    slippage=0.0,
    timestamp=None,
):
    """
    Process an exit signal.

    The Position & Slicing Engine decides HOW MUCH to exit.

    This function then records that paper SELL.

    For V1, gross_pnl is supplied by the test/calling layer.
    Later versions can calculate it automatically from the
    actual entry and exit prices.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    if trade.get("Status") != "OPEN":
        return {
            "Status": "ERROR",
            "Reason": "Trade is not open",
        }

    try:
        current_price = float(current_price)
    except (TypeError, ValueError):
        return {
            "Status": "ERROR",
            "Reason": "Invalid current price",
        }

    if current_price <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Current price must be greater than zero",
        }

    # Update price / peak first.
    update_paper_price(
        trade,
        current_price,
    )

    current_quantity = trade.get(
        "Current Quantity",
        0,
    )

    if current_quantity <= 0:
        return {
            "Status": "ERROR",
            "Reason": "No open quantity remaining",
        }

    # -----------------------------------------------------
    # Calculate slicing decision
    # -----------------------------------------------------

    slicing_result = calculate_slice_plan(
        total_quantity=trade.get(
            "Original Quantity",
            current_quantity,
        ),
        current_quantity=current_quantity,
        entry_price=trade.get(
            "Entry Price",
            0,
        ),
        current_price=current_price,
        peak_price=trade.get(
            "Peak Price",
            current_price,
        ),
        exit_signal=exit_signal,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
    )

    if slicing_result.get("Position Status") == "NO ACTION":
        return {
            "Status": "NO ACTION",
            "Reason": slicing_result.get("Reason"),
            "Slicing Result": slicing_result,
        }

    exit_quantity = slicing_result.get(
        "Exit Quantity",
        0,
    )

    if exit_quantity <= 0:
        return {
            "Status": "HOLD",
            "Reason": slicing_result.get(
                "Reason",
                "No exit quantity recommended",
            ),
            "Slicing Result": slicing_result,
        }

    # -----------------------------------------------------
    # Calculate gross P&L automatically if not supplied
    # -----------------------------------------------------

    if gross_pnl is None:

        entry_price = trade.get(
            "Entry Price",
            0,
        )

        gross_pnl = (
            current_price - entry_price
        ) * exit_quantity

    # -----------------------------------------------------
    # Record paper SELL
    # -----------------------------------------------------

    sell_result = record_sell_event(
        trade=trade,
        price=current_price,
        quantity=exit_quantity,
        gross_pnl=gross_pnl,
        costs=costs,
        slippage=slippage,
        timestamp=timestamp,
        reason=exit_signal,
    )

    return {
        "Status": sell_result.get(
            "Status",
            "ERROR",
        ),
        "Exit Quantity": exit_quantity,
        "Remaining Quantity": sell_result.get(
            "Remaining Quantity",
            trade.get("Current Quantity"),
        ),
        "Trade Status": sell_result.get(
            "Trade Status",
            trade.get("Status"),
        ),
        "Slicing Result": slicing_result,
        "Sell Result": sell_result,
    }


# ---------------------------------------------------------
# 4. Get current paper position
# ---------------------------------------------------------

def get_paper_position(trade):
    """
    Return the current state of the paper position.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    return {
        "Trade ID": trade.get("Trade ID"),
        "Symbol": trade.get("Symbol"),
        "Status": trade.get("Status"),

        "Entry Price": trade.get("Entry Price"),
        "Current Price": trade.get("Current Price"),

        "Original Quantity": trade.get(
            "Original Quantity"
        ),
        "Current Quantity": trade.get(
            "Current Quantity"
        ),

        "Peak Price": trade.get("Peak Price"),
        "Peak Profit %": trade.get(
            "Peak Profit %",
            0.0,
        ),

        "Gross P&L": trade.get(
            "Gross P&L",
            0.0,
        ),
        "Trading Costs": trade.get(
            "Trading Costs",
            0.0,
        ),
        "Slippage": trade.get(
            "Slippage",
            0.0,
        ),
        "Net P&L": trade.get(
            "Net P&L",
            0.0,
        ),
    }
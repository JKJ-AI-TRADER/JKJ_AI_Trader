"""
JKJ AI Trader
Intraday Trade Logger V1

Purpose:
    Record every paper-trading event so that JKJ can later produce
    accurate daily, monthly and overall report cards.

This module does NOT:
    - place orders
    - make BUY/SELL decisions
    - calculate trading signals
    - modify main.py

It only records and summarizes trade information.

Wisdom Before Wealth.
"""

from datetime import datetime


# ---------------------------------------------------------
# 1. Create a trade record
# ---------------------------------------------------------

def create_trade_record(
    trade_id,
    symbol,
    instrument_type,
    expiry=None,
    strike=None,
    option_type=None,
    underlying=None,
    entry_time=None,
    entry_price=None,
    quantity=0,
    stop_loss=None,
    target=None,
    momentum_score=None,
    entry_status=None,
    entry_reason=None,
):
    """
    Create a new trade record.

    The record represents the opening of a paper trade.
    """

    if not trade_id:
        return {
            "Status": "ERROR",
            "Reason": "Trade ID is required",
        }

    if not symbol:
        return {
            "Status": "ERROR",
            "Reason": "Symbol is required",
        }

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return {
            "Status": "ERROR",
            "Reason": "Quantity must be numeric",
        }

    if quantity <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Quantity must be greater than zero",
        }

    try:
        entry_price = float(entry_price)
    except (TypeError, ValueError):
        return {
            "Status": "ERROR",
            "Reason": "Entry price must be numeric",
        }

    if entry_price <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Entry price must be greater than zero",
        }

    if entry_time is None:
        entry_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return {
        "Trade ID": trade_id,
        "Status": "OPEN",

        "Symbol": symbol,
        "Instrument Type": instrument_type,

        "Expiry": expiry,
        "Strike": strike,
        "Option Type": option_type,
        "Underlying": underlying,

        "Entry Time": entry_time,
        "Entry Price": round(entry_price, 4),
        "Original Quantity": quantity,
        "Current Quantity": quantity,

        "Stop Loss": stop_loss,
        "Target": target,

        "Momentum Score": momentum_score,
        "Entry Status": entry_status,
        "Entry Reason": entry_reason,

        "Peak Price": round(entry_price, 4),
        "Peak Profit %": 0.0,

        "Gross P&L": 0.0,
        "Trading Costs": 0.0,
        "Slippage": 0.0,
        "Net P&L": 0.0,

        "Exit Time": None,
        "Exit Reason": None,

        "Exit Events": [],
        "Notes": [],
    }


# ---------------------------------------------------------
# 2. Update peak price
# ---------------------------------------------------------

def update_peak_price(trade, current_price):
    """
    Update the highest price reached by the position.
    """

    if not isinstance(trade, dict):
        return trade

    try:
        current_price = float(current_price)
    except (TypeError, ValueError):
        return trade

    if current_price <= 0:
        return trade

    peak_price = trade.get("Peak Price", trade.get("Entry Price", 0))

    if current_price > peak_price:
        trade["Peak Price"] = round(current_price, 4)

        entry_price = trade.get("Entry Price", 0)

        if entry_price > 0:
            peak_profit = (
                (current_price - entry_price)
                / entry_price
            ) * 100

            trade["Peak Profit %"] = round(
                peak_profit,
                2
            )

    return trade


# ---------------------------------------------------------
# 3. Record a BUY event
# ---------------------------------------------------------

def record_buy_event(
    trade,
    price,
    quantity,
    timestamp=None,
    reason="ENTRY",
):
    """
    Record a BUY event.

    Normally used when a position is opened or when a future
    version supports additional entries.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    try:
        price = float(price)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return {
            "Status": "ERROR",
            "Reason": "Invalid price or quantity",
        }

    if price <= 0 or quantity <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Price and quantity must be greater than zero",
        }

    if timestamp is None:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    event = {
        "Action": "BUY",
        "Time": timestamp,
        "Price": round(price, 4),
        "Quantity": quantity,
        "Reason": reason,
    }

    trade.setdefault("Exit Events", []).append(event)

    return {
        "Status": "RECORDED",
        "Event": event,
    }


# ---------------------------------------------------------
# 4. Record a SELL / slice
# ---------------------------------------------------------

def record_sell_event(
    trade,
    price,
    quantity,
    gross_pnl,
    costs=0.0,
    slippage=0.0,
    timestamp=None,
    reason="EXIT",
):
    """
    Record a SELL event or partial exit.

    This function updates the remaining quantity and cumulative
    P&L of the trade.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    try:
        price = float(price)
        quantity = int(quantity)
        gross_pnl = float(gross_pnl)
        costs = float(costs)
        slippage = float(slippage)
    except (TypeError, ValueError):
        return {
            "Status": "ERROR",
            "Reason": "Invalid numeric input",
        }

    if price <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Sell price must be greater than zero",
        }

    if quantity <= 0:
        return {
            "Status": "ERROR",
            "Reason": "Sell quantity must be greater than zero",
        }

    current_quantity = trade.get("Current Quantity", 0)

    if quantity > current_quantity:
        return {
            "Status": "ERROR",
            "Reason": "Sell quantity exceeds current position",
        }

    if timestamp is None:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    net_pnl = gross_pnl - costs - slippage

    event = {
        "Action": "SELL",
        "Time": timestamp,
        "Price": round(price, 4),
        "Quantity": quantity,
        "Gross P&L": round(gross_pnl, 2),
        "Costs": round(costs, 2),
        "Slippage": round(slippage, 2),
        "Net P&L": round(net_pnl, 2),
        "Reason": reason,
    }

    trade["Exit Events"].append(event)

    trade["Current Quantity"] = (
        current_quantity - quantity
    )

    trade["Gross P&L"] = round(
        trade.get("Gross P&L", 0.0) + gross_pnl,
        2,
    )

    trade["Trading Costs"] = round(
        trade.get("Trading Costs", 0.0) + costs,
        2,
    )

    trade["Slippage"] = round(
        trade.get("Slippage", 0.0) + slippage,
        2,
    )

    trade["Net P&L"] = round(
        trade.get("Net P&L", 0.0) + net_pnl,
        2,
    )

    # Position completely closed
    if trade["Current Quantity"] == 0:
        trade["Status"] = "CLOSED"
        trade["Exit Time"] = timestamp
        trade["Exit Reason"] = reason

    return {
        "Status": "RECORDED",
        "Event": event,
        "Remaining Quantity": trade["Current Quantity"],
        "Trade Status": trade["Status"],
    }


# ---------------------------------------------------------
# 5. Add a note
# ---------------------------------------------------------

def add_trade_note(trade, note):
    """
    Add a learning / observation note to a trade.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    if not note:
        return {
            "Status": "ERROR",
            "Reason": "Note cannot be empty",
        }

    trade.setdefault("Notes", []).append(
        {
            "Time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Note": str(note),
        }
    )

    return {
        "Status": "RECORDED",
        "Note": note,
    }


# ---------------------------------------------------------
# 6. Close trade
# ---------------------------------------------------------

def close_trade(
    trade,
    exit_reason,
    timestamp=None,
):
    """
    Close a trade after all quantity has already been sold.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    if trade.get("Current Quantity", 0) != 0:
        return {
            "Status": "ERROR",
            "Reason": "Position still has open quantity",
        }

    if timestamp is None:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    trade["Status"] = "CLOSED"
    trade["Exit Time"] = timestamp
    trade["Exit Reason"] = exit_reason

    return {
        "Status": "CLOSED",
        "Trade ID": trade.get("Trade ID"),
        "Net P&L": trade.get("Net P&L", 0.0),
    }


# ---------------------------------------------------------
# 7. Summarize one trade
# ---------------------------------------------------------

def summarize_trade(trade):
    """
    Return a clean summary of one completed or open trade.
    """

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Reason": "Invalid trade record",
        }

    return {
        "Trade ID": trade.get("Trade ID"),
        "Symbol": trade.get("Symbol"),
        "Instrument Type": trade.get("Instrument Type"),
        "Status": trade.get("Status"),

        "Entry Time": trade.get("Entry Time"),
        "Entry Price": trade.get("Entry Price"),
        "Original Quantity": trade.get("Original Quantity"),
        "Current Quantity": trade.get("Current Quantity"),

        "Peak Price": trade.get("Peak Price"),
        "Peak Profit %": trade.get("Peak Profit %"),

        "Gross P&L": trade.get("Gross P&L"),
        "Trading Costs": trade.get("Trading Costs"),
        "Slippage": trade.get("Slippage"),
        "Net P&L": trade.get("Net P&L"),

        "Exit Time": trade.get("Exit Time"),
        "Exit Reason": trade.get("Exit Reason"),

        "Number of Exit Events": len(
            trade.get("Exit Events", [])
        ),
    }


# ---------------------------------------------------------
# 8. Daily report summary
# ---------------------------------------------------------

def create_daily_summary(trades):
    """
    Create a basic daily summary from a list of trade records.

    This is the foundation for the future JKJ Daily Report Card.
    """

    if not isinstance(trades, list):
        return {
            "Status": "ERROR",
            "Reason": "Trades must be provided as a list",
        }

    completed_trades = [
        trade
        for trade in trades
        if isinstance(trade, dict)
        and trade.get("Status") == "CLOSED"
    ]

    winning_trades = [
        trade
        for trade in completed_trades
        if trade.get("Net P&L", 0) > 0
    ]

    losing_trades = [
        trade
        for trade in completed_trades
        if trade.get("Net P&L", 0) < 0
    ]

    gross_profit = sum(
        max(trade.get("Gross P&L", 0), 0)
        for trade in completed_trades
    )

    gross_loss = sum(
        min(trade.get("Gross P&L", 0), 0)
        for trade in completed_trades
    )

    total_costs = sum(
        trade.get("Trading Costs", 0)
        for trade in completed_trades
    )

    total_slippage = sum(
        trade.get("Slippage", 0)
        for trade in completed_trades
    )

    net_pnl = sum(
        trade.get("Net P&L", 0)
        for trade in completed_trades
    )

    total_trades = len(completed_trades)

    if total_trades > 0:
        win_rate = (
            len(winning_trades)
            / total_trades
        ) * 100
    else:
        win_rate = 0.0

    return {
        "Status": "OK",

        "Total Trades": total_trades,
        "Winning Trades": len(winning_trades),
        "Losing Trades": len(losing_trades),

        "Win Rate %": round(win_rate, 2),

        "Gross Profit": round(gross_profit, 2),
        "Gross Loss": round(gross_loss, 2),

        "Trading Costs": round(total_costs, 2),
        "Slippage": round(total_slippage, 2),

        "Net P&L": round(net_pnl, 2),

        "Average Trade": round(
            net_pnl / total_trades,
            2
        ) if total_trades else 0.0,
    }

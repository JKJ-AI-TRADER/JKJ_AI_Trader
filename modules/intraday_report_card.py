"""
JKJ AI Trader
Intraday Report Card Engine V1

Purpose:
    Convert recorded paper trades into measurable performance
    reports.

Reports:
    - Daily report
    - Monthly report
    - Overall report

Important:
    NET P&L is the primary performance measure.

    Gross P&L
        - Trading Costs
        - Slippage
        = NET P&L

This module does NOT:
    - place orders
    - make trading decisions
    - connect to Zerodha
    - modify main.py

Wisdom Before Wealth.
"""

from collections import Counter
from datetime import datetime


# ---------------------------------------------------------
# 1. Basic trade filtering
# ---------------------------------------------------------

def _completed_trades(trades):
    """
    Return only completed trades.
    """

    if not isinstance(trades, list):
        return []

    return [
        trade
        for trade in trades
        if isinstance(trade, dict)
        and trade.get("Status") == "CLOSED"
    ]


# ---------------------------------------------------------
# 2. Calculate win/loss statistics
# ---------------------------------------------------------

def calculate_trade_statistics(trades):
    """
    Calculate basic performance statistics.
    """

    completed = _completed_trades(trades)

    total_trades = len(completed)

    winning_trades = [
        trade
        for trade in completed
        if trade.get("Net P&L", 0) > 0
    ]

    losing_trades = [
        trade
        for trade in completed
        if trade.get("Net P&L", 0) < 0
    ]

    breakeven_trades = [
        trade
        for trade in completed
        if trade.get("Net P&L", 0) == 0
    ]

    gross_profit = sum(
        max(trade.get("Gross P&L", 0), 0)
        for trade in completed
    )

    gross_loss = sum(
        min(trade.get("Gross P&L", 0), 0)
        for trade in completed
    )

    total_costs = sum(
        trade.get("Trading Costs", 0)
        for trade in completed
    )

    total_slippage = sum(
        trade.get("Slippage", 0)
        for trade in completed
    )

    net_pnl = sum(
        trade.get("Net P&L", 0)
        for trade in completed
    )

    if total_trades:
        win_rate = (
            len(winning_trades)
            / total_trades
        ) * 100
    else:
        win_rate = 0.0

    average_trade = (
        net_pnl / total_trades
        if total_trades
        else 0.0
    )

    average_winner = (
        sum(
            trade.get("Net P&L", 0)
            for trade in winning_trades
        )
        / len(winning_trades)
        if winning_trades
        else 0.0
    )

    average_loser = (
        sum(
            trade.get("Net P&L", 0)
            for trade in losing_trades
        )
        / len(losing_trades)
        if losing_trades
        else 0.0
    )

    total_winning_pnl = sum(
        trade.get("Net P&L", 0)
        for trade in winning_trades
    )

    total_losing_pnl = abs(
        sum(
            trade.get("Net P&L", 0)
            for trade in losing_trades
        )
    )

    if total_losing_pnl > 0:
        profit_factor = (
            total_winning_pnl
            / total_losing_pnl
        )
    else:
        profit_factor = (
            float("inf")
            if total_winning_pnl > 0
            else 0.0
        )

    if completed:
        best_trade = max(
            completed,
            key=lambda trade: trade.get(
                "Net P&L",
                0,
            ),
        )

        worst_trade = min(
            completed,
            key=lambda trade: trade.get(
                "Net P&L",
                0,
            ),
        )

    else:
        best_trade = None
        worst_trade = None

    return {
        "Total Trades": total_trades,
        "Winning Trades": len(winning_trades),
        "Losing Trades": len(losing_trades),
        "Breakeven Trades": len(breakeven_trades),

        "Win Rate %": round(win_rate, 2),

        "Gross Profit": round(gross_profit, 2),
        "Gross Loss": round(gross_loss, 2),

        "Trading Costs": round(
            total_costs,
            2,
        ),

        "Slippage": round(
            total_slippage,
            2,
        ),

        "Net P&L": round(
            net_pnl,
            2,
        ),

        "Average Trade": round(
            average_trade,
            2,
        ),

        "Average Winner": round(
            average_winner,
            2,
        ),

        "Average Loser": round(
            average_loser,
            2,
        ),

        "Profit Factor": (
            round(profit_factor, 2)
            if profit_factor != float("inf")
            else "INF"
        ),

        "Best Trade": (
            best_trade.get("Trade ID")
            if best_trade
            else None
        ),

        "Best Trade P&L": round(
            best_trade.get("Net P&L", 0),
            2,
        ) if best_trade else 0.0,

        "Worst Trade": (
            worst_trade.get("Trade ID")
            if worst_trade
            else None
        ),

        "Worst Trade P&L": round(
            worst_trade.get("Net P&L", 0),
            2,
        ) if worst_trade else 0.0,
    }


# ---------------------------------------------------------
# 3. Exit reason statistics
# ---------------------------------------------------------

def calculate_exit_statistics(trades):
    """
    Count how trades were closed.
    """

    completed = _completed_trades(trades)

    reasons = []

    for trade in completed:
        reason = trade.get(
            "Exit Reason",
            "UNKNOWN",
        )

        reasons.append(reason)

    counts = Counter(reasons)

    return {
        "Exit Reason Counts": dict(counts),
        "Total Closed Trades": len(completed),
    }


# ---------------------------------------------------------
# 4. Slicing statistics
# ---------------------------------------------------------

def calculate_slicing_statistics(trades):
    """
    Analyze partial exits recorded inside each trade.
    """

    completed = _completed_trades(trades)

    total_exit_events = 0
    partial_exit_trades = 0
    full_exit_trades = 0

    for trade in completed:

        events = trade.get(
            "Exit Events",
            [],
        )

        sell_events = [
            event
            for event in events
            if isinstance(event, dict)
            and event.get("Action") == "SELL"
        ]

        total_exit_events += len(
            sell_events
        )

        if len(sell_events) > 1:
            partial_exit_trades += 1

        elif len(sell_events) == 1:
            full_exit_trades += 1

    return {
        "Total Exit Events": total_exit_events,
        "Trades With Multiple Exits": partial_exit_trades,
        "Trades With Single Exit": full_exit_trades,
    }


# ---------------------------------------------------------
# 5. Profit capture statistics
# ---------------------------------------------------------

def calculate_profit_capture(trades):
    """
    Compare actual realized net P&L with the theoretical
    peak-price profit for each completed trade.

    This is an initial V1 measure.

    It is not intended to represent every possible future
    opportunity. It measures how much of the trade's peak
    price profit was ultimately realized.
    """

    completed = _completed_trades(trades)

    capture_values = []

    for trade in completed:

        entry_price = trade.get(
            "Entry Price",
            0,
        )

        peak_price = trade.get(
            "Peak Price",
            0,
        )

        original_quantity = trade.get(
            "Original Quantity",
            0,
        )

        net_pnl = trade.get(
            "Net P&L",
            0,
        )

        if (
            entry_price is None
            or peak_price is None
            or original_quantity is None
        ):
            continue

        if (
            entry_price <= 0
            or peak_price <= entry_price
            or original_quantity <= 0
            or net_pnl < 0
        ):
            continue
        peak_gross_pnl = (
            peak_price - entry_price
        ) * original_quantity

        if peak_gross_pnl <= 0:
            continue

        capture_percentage = (
            net_pnl
            / peak_gross_pnl
        ) * 100

        capture_values.append(
            capture_percentage
        )

    if capture_values:
        average_capture = (
            sum(capture_values)
            / len(capture_values)
        )
    else:
        average_capture = 0.0

    return {
        "Trades Measured": len(
            capture_values
        ),
        "Average Profit Capture %": round(
            average_capture,
            2,
        ),
    }


# ---------------------------------------------------------
# 6. Maximum drawdown
# ---------------------------------------------------------

def calculate_max_drawdown(trades):
    """
    Calculate maximum cumulative net-P&L drawdown.

    Trades are processed in their supplied order.
    """

    completed = _completed_trades(trades)

    cumulative = 0.0
    peak = 0.0
    maximum_drawdown = 0.0

    for trade in completed:

        cumulative += trade.get(
            "Net P&L",
            0,
        )

        if cumulative > peak:
            peak = cumulative

        drawdown = peak - cumulative

        if drawdown > maximum_drawdown:
            maximum_drawdown = drawdown

    return round(
        maximum_drawdown,
        2,
    )


# ---------------------------------------------------------
# 7. Daily Report Card
# ---------------------------------------------------------

def create_daily_report(trades, report_date=None):
    """
    Create a complete daily report card.
    """

    if report_date is None:
        report_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    completed = _completed_trades(trades)

    statistics = calculate_trade_statistics(
        completed
    )

    exit_statistics = calculate_exit_statistics(
        completed
    )

    slicing_statistics = calculate_slicing_statistics(
        completed
    )

    profit_capture = calculate_profit_capture(
        completed
    )

    max_drawdown = calculate_max_drawdown(
        completed
    )

    return {
        "Report Type": "DAILY",
        "Report Date": report_date,

        "Trade Statistics": statistics,

        "Exit Statistics": exit_statistics,

        "Slicing Statistics": slicing_statistics,

        "Profit Capture": profit_capture,

        "Maximum Drawdown": max_drawdown,
    }


# ---------------------------------------------------------
# 8. Monthly Report Card
# ---------------------------------------------------------

def create_monthly_report(
    trades,
    year,
    month,
):
    """
    Create a monthly report card.

    Trades are selected using Entry Time.
    """

    monthly_trades = []

    for trade in trades:

        if not isinstance(trade, dict):
            continue

        entry_time = trade.get(
            "Entry Time"
        )

        if not entry_time:
            continue

        try:
            parsed_time = datetime.strptime(
                entry_time,
                "%Y-%m-%d %H:%M:%S",
            )

        except ValueError:
            continue

        if (
            parsed_time.year == year
            and parsed_time.month == month
        ):
            monthly_trades.append(trade)

    report = create_daily_report(
        monthly_trades,
        report_date=f"{year}-{month:02d}",
    )

    report["Report Type"] = "MONTHLY"

    return report


# ---------------------------------------------------------
# 9. Overall Report Card
# ---------------------------------------------------------

def create_overall_report(trades):
    """
    Create an overall report from all completed trades.
    """

    completed = _completed_trades(trades)

    statistics = calculate_trade_statistics(
        completed
    )

    exit_statistics = calculate_exit_statistics(
        completed
    )

    slicing_statistics = calculate_slicing_statistics(
        completed
    )

    profit_capture = calculate_profit_capture(
        completed
    )

    max_drawdown = calculate_max_drawdown(
        completed
    )

    return {
        "Report Type": "OVERALL",

        "Trade Statistics": statistics,

        "Exit Statistics": exit_statistics,

        "Slicing Statistics": slicing_statistics,

        "Profit Capture": profit_capture,

        "Maximum Drawdown": max_drawdown,
    }
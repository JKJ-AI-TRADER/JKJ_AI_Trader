"""
JKJ AI Trader
Intraday Option Paper Position Monitor V10

Wisdom Before Wealth.

Purpose:
Monitor an open option paper position and coordinate:

    Current Price
          ↓
    Peak Price Tracking
          ↓
    Profit Protection
          ↓
    Exit Engine
          ↓
    Position Slicing

V10 does NOT:
- place broker orders
- connect to Zerodha
- modify main.py
- modify V1-V9
- execute real trades
"""

from intraday_profit_protection import (
    evaluate_profit_protection
)

from intraday_exit_engine import (
    evaluate_intraday_exit
)

from intraday_position_slicing import (
    calculate_slice_plan
)


def monitor_option_paper_position(
    trade,
    current_price,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    holding_minutes=0,
    max_holding_minutes=60,
):
    """
    Monitor an existing option paper position.

    V10 evaluates the position but does not execute
    the paper exit itself.
    """

    # -----------------------------------------
    # 1. BASIC VALIDATION
    # -----------------------------------------

    if not isinstance(trade, dict):

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Paper trade must be a dictionary."
            ]
        }

    if not isinstance(current_price, (int, float)):

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Current price must be numeric."
            ]
        }

    if current_price <= 0:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Current price must be greater than zero."
            ]
        }

    # -----------------------------------------
    # 2. READ PAPER POSITION
    # -----------------------------------------

    entry_price = trade.get(
        "Entry Price"
    )

    current_quantity = trade.get(
        "Current Quantity"
    )

    total_quantity = trade.get(
        "Original Quantity"
    )

    stop_loss_price = trade.get(
        "Stop Loss"
    )

    target_price = trade.get(
    "Target"
)

    peak_price = trade.get(
        "Peak Price",
        entry_price
    )

    if entry_price is None:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Paper trade entry price is missing."
            ]
        }

    if current_quantity is None:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Paper trade current quantity is missing."
            ]
        }

    if total_quantity is None:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Paper trade original quantity is missing."
            ]
        }

    if stop_loss_price is None:

        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Paper trade stop loss is missing."
            ]
        }

    # -----------------------------------------
    # 3. UPDATE PEAK PRICE
    # -----------------------------------------

    updated_peak_price = max(
        float(peak_price),
        float(current_price)
    )

    # -----------------------------------------
    # 4. PROFIT PROTECTION
    # -----------------------------------------

    profit_protection_result = evaluate_profit_protection(
        entry_price=entry_price,
        current_price=current_price,
        peak_price=updated_peak_price,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
        stop_loss_price=stop_loss_price,
    )

    # -----------------------------------------
    # 5. EXIT ENGINE
    # -----------------------------------------

    exit_result = evaluate_intraday_exit(
        entry_price=entry_price,
        current_price=current_price,
        stop_loss_price=stop_loss_price,
        target_price=target_price,
        profit_protection_result=profit_protection_result,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
        holding_minutes=holding_minutes,
        max_holding_minutes=max_holding_minutes,
    )

    exit_signal = "EXIT" if exit_result.get("Exit Required", False) else "HOLD"

    # -----------------------------------------
    # 6. POSITION SLICING
    # -----------------------------------------

    slice_result = calculate_slice_plan(
        total_quantity=total_quantity,
        current_quantity=current_quantity,
        entry_price=entry_price,
        current_price=current_price,
        peak_price=updated_peak_price,
        exit_signal=exit_signal,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
    )

    # -----------------------------------------
    # 7. FINAL MONITOR DECISION
    # -----------------------------------------

    if exit_result.get("Exit Required", False):
        decision = "EXIT"

    elif slice_result.get("Slice Decision") == "SLICE":

        decision = "PARTIAL EXIT"

    else:

        decision = "HOLD"

    return {
        "Status": "READY",
        "Decision": decision,
        "Current Price": current_price,
        "Entry Price": entry_price,
        "Original Quantity": total_quantity,
        "Current Quantity": current_quantity,
        "Peak Price": updated_peak_price,
        "Stop Loss": stop_loss_price,
        "Target Price": target_price,
        "Holding Minutes": holding_minutes,
        "Profit Protection Result": profit_protection_result,
        "Exit Result": exit_result,
        "Slice Result": slice_result,
        "Reasons": [
            "Open option paper position evaluated "
            "through profit protection, exit and slicing."
        ],
    }
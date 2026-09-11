"""
JKJ AI Trader
Intraday Position & Slicing Engine V1

Purpose:
    Decide HOW MUCH of an open position should be exited.

Important:
    This module does NOT decide whether an exit should happen.
    The Exit Engine decides WHEN/WHY to exit.

    This engine decides the quantity to exit once an exit or
    profit-protection condition exists.

Wisdom Before Wealth.
"""


def calculate_slice_plan(
    total_quantity,
    current_quantity,
    entry_price,
    current_price,
    peak_price,
    exit_signal,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
):
    """
    Calculate a partial-exit plan for an open intraday position.

    Parameters
    ----------
    total_quantity : int
        Original position quantity.

    current_quantity : int
        Quantity currently remaining.

    entry_price : float
        Original entry price.

    current_price : float
        Current market price.

    peak_price : float
        Highest price reached since entry.

    exit_signal : str
        Signal from the Exit / Profit Protection Engine.

    momentum_status : str
        STRONG, STABLE, WEAK, DETERIORATING, REVERSING, etc.

    volume_status : str
        STRONG, STABLE, WEAK, DECREASING, etc.

    underlying_status : str
        SUPPORTIVE, STABLE, WEAK, DETERIORATING, etc.

    structure_status : str
        STRONG, STABLE, WEAK, DETERIORATING, etc.

    Returns
    -------
    dict
        Slicing decision and recommended quantities.
    """

    # ---------------------------------------------------------
    # 1. Basic validation
    # ---------------------------------------------------------

    if total_quantity is None or current_quantity is None:
        return _no_trade_result("Invalid quantity")

    if entry_price is None or current_price is None:
        return _no_trade_result("Invalid price")

    if peak_price is None:
        peak_price = current_price

    try:
        total_quantity = int(total_quantity)
        current_quantity = int(current_quantity)
        entry_price = float(entry_price)
        current_price = float(current_price)
        peak_price = float(peak_price)
    except (TypeError, ValueError):
        return _no_trade_result("Invalid numeric input")

    if total_quantity <= 0:
        return _no_trade_result("Total quantity must be greater than zero")

    if current_quantity <= 0:
        return _no_trade_result("No open quantity remaining")

    if current_quantity > total_quantity:
        return _no_trade_result(
            "Current quantity cannot exceed total quantity"
        )

    if entry_price <= 0 or current_price <= 0:
        return _no_trade_result("Price must be greater than zero")

    # ---------------------------------------------------------
    # 2. Position profit calculation
    # ---------------------------------------------------------

    current_profit_percentage = (
        (current_price - entry_price) / entry_price
    ) * 100

    peak_profit_percentage = (
        (peak_price - entry_price) / entry_price
    ) * 100

    if peak_price > 0:
        retracement_percentage = (
            (peak_price - current_price) / peak_price
        ) * 100
    else:
        retracement_percentage = 0.0

    # ---------------------------------------------------------
    # 3. Normalize status values
    # ---------------------------------------------------------

    momentum = str(momentum_status).upper()
    volume = str(volume_status).upper()
    underlying = str(underlying_status).upper()
    structure = str(structure_status).upper()
    signal = str(exit_signal).upper()

    # ---------------------------------------------------------
    # 4. Immediate FULL EXIT conditions
    # ---------------------------------------------------------

    full_exit_reasons = []

    if "STOP LOSS" in signal:
        full_exit_reasons.append("Stop loss")

    if "MOMENTUM REVERSAL" in signal:
        full_exit_reasons.append("Momentum reversal")

    if "TIME EXIT" in signal:
        full_exit_reasons.append("Maximum holding time reached")

    if "EMERGENCY" in signal:
        full_exit_reasons.append("Emergency exit")

    if full_exit_reasons:
        return {
            "Position Status": "FULL EXIT",
            "Slice Decision": "EXIT ENTIRE POSITION",
            "Total Quantity": total_quantity,
            "Current Quantity": current_quantity,
            "Exit Quantity": current_quantity,
            "Remaining Quantity": 0,
            "Current Profit %": round(current_profit_percentage, 2),
            "Peak Profit %": round(peak_profit_percentage, 2),
            "Retracement %": round(retracement_percentage, 2),
            "Reason": ", ".join(full_exit_reasons),
        }

    # ---------------------------------------------------------
    # 5. Target reached
    # ---------------------------------------------------------

    if "TARGET" in signal:
        return {
            "Position Status": "FULL EXIT",
            "Slice Decision": "EXIT ENTIRE POSITION",
            "Total Quantity": total_quantity,
            "Current Quantity": current_quantity,
            "Exit Quantity": current_quantity,
            "Remaining Quantity": 0,
            "Current Profit %": round(current_profit_percentage, 2),
            "Peak Profit %": round(peak_profit_percentage, 2),
            "Retracement %": round(retracement_percentage, 2),
            "Reason": "Target reached",
        }

    # ---------------------------------------------------------
    # 6. Calculate weakness score
    # ---------------------------------------------------------

    weakness_score = 0

    if momentum in {
        "WEAK",
        "DETERIORATING",
        "EXHAUSTED",
        "REVERSING",
    }:
        weakness_score += 2

    if volume in {
        "WEAK",
        "DECREASING",
        "DETERIORATING",
    }:
        weakness_score += 1

    if underlying in {
        "WEAK",
        "DETERIORATING",
        "REVERSING",
    }:
        weakness_score += 1

    if structure in {
        "WEAK",
        "DETERIORATING",
        "REVERSING",
    }:
        weakness_score += 1

    # ---------------------------------------------------------
    # 7. Decide whether slicing is required
    # ---------------------------------------------------------

    slice_percentage = 0
    decision = "HOLD POSITION"
    reason = "No slicing condition"

    # Strong reversal / deterioration:
    # exit a larger portion but still allow the engine to
    # preserve some position where appropriate.
    if weakness_score >= 4 and current_profit_percentage > 0:
        slice_percentage = 50
        decision = "PARTIAL EXIT"
        reason = "Multiple signals weakening"

    elif weakness_score >= 3 and current_profit_percentage > 0:
        slice_percentage = 33
        decision = "PARTIAL EXIT"
        reason = "Momentum and supporting signals weakening"

    elif (
        current_profit_percentage >= 10
        and retracement_percentage >= 3
        and weakness_score >= 2
    ):
        slice_percentage = 25
        decision = "PARTIAL EXIT"
        reason = "High profit with meaningful retracement"

    elif (
        current_profit_percentage >= 5
        and retracement_percentage >= 2
        and weakness_score >= 1
    ):
        slice_percentage = 25
        decision = "PARTIAL EXIT"
        reason = "Profit protection condition"

    elif (
        current_profit_percentage >= 3
        and retracement_percentage >= 1.5
        and weakness_score >= 1
    ):
        slice_percentage = 20
        decision = "PARTIAL EXIT"
        reason = "Early profit protection"

    # ---------------------------------------------------------
    # 8. Convert percentage into actual quantity
    # ---------------------------------------------------------

    if slice_percentage > 0:

        proposed_quantity = int(
            current_quantity * slice_percentage / 100
        )

        # Always exit at least one unit if slicing is required.
        proposed_quantity = max(1, proposed_quantity)

        # Never exceed current position.
        proposed_quantity = min(
            proposed_quantity,
            current_quantity
        )

        remaining_quantity = (
            current_quantity - proposed_quantity
        )

    else:
        proposed_quantity = 0
        remaining_quantity = current_quantity

    # ---------------------------------------------------------
    # 9. If only a very small quantity remains,
    #    avoid meaningless slicing.
    # ---------------------------------------------------------

    if (
        proposed_quantity > 0
        and remaining_quantity > 0
        and remaining_quantity < 1
    ):
        proposed_quantity = current_quantity
        remaining_quantity = 0
        decision = "FULL EXIT"
        reason = "Insufficient quantity for meaningful remaining position"

    # ---------------------------------------------------------
    # 10. Final result
    # ---------------------------------------------------------

    return {
        "Position Status": (
            "PARTIAL EXIT"
            if proposed_quantity > 0
            else "HOLD"
        ),
        "Slice Decision": decision,
        "Total Quantity": total_quantity,
        "Current Quantity": current_quantity,
        "Exit Quantity": proposed_quantity,
        "Remaining Quantity": remaining_quantity,
        "Slice Percentage": slice_percentage,
        "Current Profit %": round(current_profit_percentage, 2),
        "Peak Profit %": round(peak_profit_percentage, 2),
        "Retracement %": round(retracement_percentage, 2),
        "Weakness Score": weakness_score,
        "Reason": reason,
    }


def _no_trade_result(reason):
    """
    Return a safe result when the position input is invalid.
    """

    return {
        "Position Status": "NO ACTION",
        "Slice Decision": "NO ACTION",
        "Total Quantity": 0,
        "Current Quantity": 0,
        "Exit Quantity": 0,
        "Remaining Quantity": 0,
        "Slice Percentage": 0,
        "Current Profit %": 0,
        "Peak Profit %": 0,
        "Retracement %": 0,
        "Weakness Score": 0,
        "Reason": reason,
    }
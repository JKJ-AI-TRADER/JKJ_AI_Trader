"""
JKJ AI Trader
V15.2 Paper Trade Entry Bridge

Purpose:
    Convert a V15.1 permitted paper-trade qualification into
    a validated set of parameters for the existing V11
    open_paper_trade() function.

This module does NOT:
    - open a paper trade
    - place real orders
    - connect to Zerodha
    - modify V11
    - modify V12/V13/V14
    - modify main.py

Wisdom Before Wealth.
"""

import math


def _coerce_whole_quantity(value):
    """Accept finite whole-number quantities, but reject booleans."""
    if isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(numeric) or not numeric.is_integer():
        return None
    return int(numeric)


def _validate_price_structure(data):
    """Validate entry, stop, targets and stated risk/reward ratios."""
    required = [
        "Trading Symbol", "Underlying", "Expiry", "Strike",
        "Option Type", "Entry Price", "Stop Price",
        "Target 1", "Target 2", "Target 3",
        "Risk Reward 1", "Risk Reward 2", "Risk Reward 3",
        "Entry Qualification", "Qualification Reason",
    ]

    for field in required:
        if field not in data or data[field] is None:
            return f"Missing required field: {field}"

    numeric_fields = [
        "Strike", "Entry Price", "Stop Price",
        "Target 1", "Target 2", "Target 3",
        "Risk Reward 1", "Risk Reward 2", "Risk Reward 3",
    ]
    values = {}

    for field in numeric_fields:
        value = data[field]
        if isinstance(value, bool):
            return f"{field} must be a finite number"
        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            return f"{field} must be a finite number"
        if not math.isfinite(value):
            return f"{field} must be a finite number"
        values[field] = value

    entry = values["Entry Price"]
    stop = values["Stop Price"]
    targets = [
        values["Target 1"],
        values["Target 2"],
        values["Target 3"],
    ]

    if values["Strike"] <= 0 or entry <= 0 or stop <= 0:
        return "Strike, entry price and stop price must be positive"

    if stop >= entry:
        return "Stop price must be below entry price"

    if not (entry < targets[0] < targets[1] < targets[2]):
        return "Targets must be above entry and strictly ascending"

    risk = entry - stop
    for index, target in enumerate(targets, start=1):
        supplied = values[f"Risk Reward {index}"]
        expected = round((target - entry) / risk, 2)
        if supplied <= 0 or round(supplied, 2) != expected:
            return f"Risk Reward {index} does not match the supplied prices"

    return None


# ---------------------------------------------------------
# 1. Prepare V11 paper-trade entry
# ---------------------------------------------------------

def prepare_paper_trade_entry(
    paper_trade_qualification,
    quantity,
    trade_id,
    entry_time=None,
):
    """
    Prepare a V11-compatible paper-trade entry request.

    Only a V15.1 PERMITTED setup may proceed.
    """

    if not isinstance(paper_trade_qualification, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid paper trade qualification",
        }

    if paper_trade_qualification.get("Status") != "QUALIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Paper trade qualification must have Status QUALIFIED",
        }

    if (
        paper_trade_qualification.get("Paper Trade Permission")
        != "PERMITTED"
    ):
        return {
            "Status": "REJECTED",
            "Reason": "Paper trade permission is not PERMITTED",
        }

    # -----------------------------------------------------
    # Validate quantity
    # -----------------------------------------------------

    quantity = _coerce_whole_quantity(quantity)
    if quantity is None:
        return {
            "Status": "REJECTED",
            "Reason": "Quantity must be a finite whole number",
        }

    if quantity <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Quantity must be greater than zero",
        }

    # -----------------------------------------------------
    # Validate trade ID
    # -----------------------------------------------------

    if trade_id is None or str(trade_id).strip() == "":
        return {
            "Status": "REJECTED",
            "Reason": "Trade ID is required",
        }

    validation_error = _validate_price_structure(
        paper_trade_qualification
    )
    if validation_error:
        return {
            "Status": "REJECTED",
            "Reason": validation_error,
        }

    # -----------------------------------------------------
    # Prepare V11 entry request
    # -----------------------------------------------------

    return {
        "Status": "PREPARED",

        "Trade ID": trade_id,

        "Symbol": paper_trade_qualification[
            "Trading Symbol"
        ],

        "Instrument Type": "OPTION",

        "Underlying": paper_trade_qualification[
            "Underlying"
        ],

        "Expiry": paper_trade_qualification[
            "Expiry"
        ],

        "Strike": paper_trade_qualification[
            "Strike"
        ],

        "Option Type": paper_trade_qualification[
            "Option Type"
        ],

        "Entry Price": paper_trade_qualification[
            "Entry Price"
        ],

        "Quantity": quantity,

        "Stop Loss": paper_trade_qualification[
            "Stop Price"
        ],

        # V11 currently accepts one target.
        # V15 preserves all three targets separately.
        "Target": paper_trade_qualification[
            "Target 1"
        ],

        "Target 1": paper_trade_qualification[
            "Target 1"
        ],

        "Target 2": paper_trade_qualification[
            "Target 2"
        ],

        "Target 3": paper_trade_qualification[
            "Target 3"
        ],

        "Risk Reward 1": paper_trade_qualification[
            "Risk Reward 1"
        ],

        "Risk Reward 2": paper_trade_qualification[
            "Risk Reward 2"
        ],

        "Risk Reward 3": paper_trade_qualification[
            "Risk Reward 3"
        ],

        "Entry Status": paper_trade_qualification[
            "Entry Qualification"
        ],

        "Entry Reason": paper_trade_qualification[
            "Qualification Reason"
        ],

        "Entry Time": entry_time,

        "Paper Trade Permission": "PERMITTED",
        }
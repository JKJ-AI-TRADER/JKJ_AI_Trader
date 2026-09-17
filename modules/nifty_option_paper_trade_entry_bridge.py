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

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return {
            "Status": "REJECTED",
            "Reason": "Quantity must be an integer",
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
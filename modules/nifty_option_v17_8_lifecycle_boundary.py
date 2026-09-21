"""
JKJ AI Trader
V17.8.8 Controlled Lifecycle Boundary

Purpose:
    Validate that a successful V17.8.7 paper-trade handoff
    has produced a valid OPEN V11 paper trade that is ready
    for the existing V15.4 paper-position lifecycle.

This module does NOT:
    - generate trading signals
    - decide BUY/SELL
    - update prices
    - process exits
    - slice positions
    - close positions
    - connect to Zerodha
    - place real orders
    - modify V11
    - modify V15.4
    - modify main.py

V15.4 remains the authoritative paper-position lifecycle owner.

Wisdom Before Wealth.
"""


# ---------------------------------------------------------
# 1. Block helper
# ---------------------------------------------------------

def _blocked(reason):
    return {
        "Status": "V17_8_8_LIFECYCLE_BOUNDARY_BLOCKED",
        "Reason": reason,
        "Lifecycle Ready": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }


# ---------------------------------------------------------
# 2. Validate lifecycle boundary
# ---------------------------------------------------------

def validate_lifecycle_boundary(handoff_result):
    """
    Validate the V17.8.7 → V15.4 lifecycle boundary.

    No lifecycle action is performed here.
    """

    if not isinstance(handoff_result, dict):
        return _blocked(
            "V17.8.7 handoff result must be a dictionary"
        )

    if (
        handoff_result.get("Status")
        != "V17_8_7_PAPER_HANDOFF_COMPLETE"
    ):
        return _blocked(
            "V17.8.7 paper handoff is not complete"
        )

    trade = handoff_result.get("Trade")

    if not isinstance(trade, dict):
        return _blocked(
            "V11 trade record is missing"
        )

    if trade.get("Status") != "OPEN":
        return _blocked(
            "V11 paper trade is not OPEN"
        )

    required_trade_fields = [
        "Trade ID",
        "Symbol",
        "Instrument Type",
        "Entry Price",
        "Original Quantity",
        "Current Quantity",
        "Stop Loss",
        "Target",
    ]

    for field in required_trade_fields:
        if field not in trade:
            return _blocked(
                f"V11 trade field missing: {field}"
            )

    if trade.get("Instrument Type") != "OPTION":
        return _blocked(
            "V11 trade is not an OPTION"
        )

    if not isinstance(trade.get("Trade ID"), str) or not trade.get(
        "Trade ID"
    ).strip():
        return _blocked(
            "Trade ID must be a non-empty string"
        )

    if not isinstance(trade.get("Symbol"), str) or not trade.get(
        "Symbol"
    ).strip():
        return _blocked(
            "Symbol must be a non-empty string"
        )

    if trade.get("Entry Price") <= 0:
        return _blocked(
            "Entry Price must be positive"
        )

    if trade.get("Stop Loss") <= 0:
        return _blocked(
            "Stop Loss must be positive"
        )

    if trade.get("Target") <= 0:
        return _blocked(
            "Target must be positive"
        )

    original_quantity = trade.get("Original Quantity")
    current_quantity = trade.get("Current Quantity")

    if (
        not isinstance(original_quantity, int)
        or isinstance(original_quantity, bool)
        or original_quantity <= 0
    ):
        return _blocked(
            "Original Quantity must be a positive integer"
        )

    if (
        not isinstance(current_quantity, int)
        or isinstance(current_quantity, bool)
        or current_quantity <= 0
    ):
        return _blocked(
            "Current Quantity must be a positive integer"
        )

    if current_quantity > original_quantity:
        return _blocked(
            "Current Quantity cannot exceed Original Quantity"
        )

    qualification = handoff_result.get(
        "Paper Trade Qualification"
    )

    if not isinstance(qualification, dict):
        return _blocked(
            "V15 paper trade qualification is missing"
        )

    if qualification.get("Status") != "QUALIFIED":
        return _blocked(
            "V15 paper trade qualification is not QUALIFIED"
        )

    if (
        qualification.get("Paper Trade Permission")
        != "PERMITTED"
    ):
        return _blocked(
            "V15 paper trade permission is not PERMITTED"
        )

    if handoff_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution flag is not True"
        )

    if handoff_result.get("Broker Communication") is not False:
        return _blocked(
            "Broker communication must remain False"
        )

    if handoff_result.get("Order Placement Permitted") is not False:
        return _blocked(
            "Order placement must remain False"
        )

    return {
        "Status": "V17_8_8_LIFECYCLE_BOUNDARY_VALIDATED",
        "Lifecycle Ready": True,
        "Lifecycle Owner": "V15.4 / V11",
        "Trade ID": trade["Trade ID"],
        "Symbol": trade["Symbol"],
        "Instrument Type": trade["Instrument Type"],
        "Entry Price": trade["Entry Price"],
        "Original Quantity": trade["Original Quantity"],
        "Current Quantity": trade["Current Quantity"],
        "Stop Loss": trade["Stop Loss"],
        "Target": trade["Target"],
        "Paper Trade Qualification": qualification,
        "Trade": trade,
        "V15.4 Lifecycle Action Permitted": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }

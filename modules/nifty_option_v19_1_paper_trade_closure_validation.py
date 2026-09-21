"""
JKJ AI Trader
V19.1 Paper Trade Closure Validation & Final Audit

Purpose:
    Validate that a completed V11 paper trade is fully closed
    and that its final state agrees with the V18.1 synchronized
    lifecycle.

Architecture:

    V11 remains authoritative for the actual paper trade record.

    V18.1 remains authoritative for target-exit synchronization.

    V19.1 validates the completed lifecycle without modifying
    either source.

Important:
    This module does NOT:
    - calculate P&L
    - calculate exit quantities
    - modify V11
    - modify V17.2
    - modify V17.3
    - modify V17.4
    - modify V18.1
    - place real orders
    - connect to Zerodha
    - modify main.py

Wisdom Before Wealth.
"""


def _blocked(reason):
    return {
        "Status": "PAPER_TRADE_CLOSURE_BLOCKED",
        "Reason": reason,
        "Final Audit": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }


def validate_paper_trade_closure(
    trade,
    v18_1_final_sync,
):
    """
    Validate a completed V11 paper trade against the
    final V18.1 synchronization state.

    This function is READ-ONLY.

    It does not modify the supplied trade or synchronization
    result.
    """

    # ---------------------------------------------------------
    # 1. Validate V11 trade
    # ---------------------------------------------------------

    if not isinstance(trade, dict):
        return _blocked(
            "V11 trade record must be a dictionary"
        )

    if trade.get("Status") != "CLOSED":
        return _blocked(
            "V11 trade must have Status CLOSED"
        )

    required_trade_fields = [
        "Trade ID",
        "Symbol",
        "Instrument Type",
        "Original Quantity",
        "Current Quantity",
        "Entry Price",
        "Exit Time",
        "Exit Reason",
        "Exit Events",
        "Gross P&L",
        "Trading Costs",
        "Slippage",
        "Net P&L",
    ]

    for field in required_trade_fields:
        if field not in trade:
            return _blocked(
                f"Missing V11 trade field: {field}"
            )

    try:
        original_quantity = int(
            trade["Original Quantity"]
        )
        current_quantity = int(
            trade["Current Quantity"]
        )
    except (TypeError, ValueError):
        return _blocked(
            "V11 quantities must be integers"
        )

    if original_quantity <= 0:
        return _blocked(
            "V11 original quantity must be positive"
        )

    if current_quantity != 0:
        return _blocked(
            "V11 current quantity must be zero"
        )

    if not trade.get("Exit Time"):
        return _blocked(
            "V11 Exit Time is required"
        )

    if not trade.get("Exit Reason"):
        return _blocked(
            "V11 Exit Reason is required"
        )

    exit_events = trade.get("Exit Events")

    if not isinstance(exit_events, list):
        return _blocked(
            "V11 Exit Events must be a list"
        )

    if not exit_events:
        return _blocked(
            "V11 Exit Events cannot be empty"
        )

    # ---------------------------------------------------------
    # 2. Validate V18.1 final synchronization
    # ---------------------------------------------------------

    if not isinstance(v18_1_final_sync, dict):
        return _blocked(
            "V18.1 final synchronization must be a dictionary"
        )

    if v18_1_final_sync.get("Status") != "SYNCHRONIZED":
        return _blocked(
            "V18.1 final synchronization must have Status SYNCHRONIZED"
        )

    if (
        v18_1_final_sync.get(
            "Synchronization Confirmed"
        )
        is not True
    ):
        return _blocked(
            "V18.1 synchronization must be confirmed"
        )

    try:
        cumulative_filled = int(
            v18_1_final_sync[
                "Cumulative Filled Quantity"
            ]
        )
        expected_remaining = int(
            v18_1_final_sync[
                "Expected Remaining Quantity"
            ]
        )
    except (KeyError, TypeError, ValueError):
        return _blocked(
            "V18.1 final quantity fields are invalid"
        )

    if cumulative_filled != original_quantity:
        return _blocked(
            "V18.1 cumulative filled quantity does not "
            "match V11 original quantity"
        )

    if expected_remaining != 0:
        return _blocked(
            "V18.1 expected remaining quantity must be zero"
        )

    if (
        v18_1_final_sync.get(
            "V11 Remaining Quantity"
        )
        != 0
    ):
        return _blocked(
            "V18.1 V11 remaining quantity must be zero"
        )

    # ---------------------------------------------------------
    # 3. Validate paper-only safety boundary
    # ---------------------------------------------------------

    if (
        v18_1_final_sync.get(
            "Broker Communication",
            False,
        )
        is True
    ):
        return _blocked(
            "Broker communication must remain disabled"
        )

    if (
        v18_1_final_sync.get(
            "Order Placement Permitted",
            False,
        )
        is True
    ):
        return _blocked(
            "Live order placement must remain disabled"
        )

    # ---------------------------------------------------------
    # 4. Calculate exited quantity from the authoritative
    #    V11 position state.
    #
    #    This is reconciliation, not P&L calculation.
    # ---------------------------------------------------------

    total_exited_quantity = (
        original_quantity - current_quantity
    )

    if total_exited_quantity != cumulative_filled:
        return _blocked(
            "V11 exited quantity does not match V18.1 "
            "cumulative filled quantity"
        )

    # ---------------------------------------------------------
    # 5. Create final read-only closure record
    # ---------------------------------------------------------

    closure_record = {
        "Closure Status": "PAPER_TRADE_CLOSED",
        "Trade ID": trade["Trade ID"],
        "Trading Symbol": trade["Symbol"],
        "Instrument Type": trade["Instrument Type"],

        "Original Quantity": original_quantity,
        "Total Exited Quantity": total_exited_quantity,
        "Final Remaining Quantity": current_quantity,
        "Trade Status": trade["Status"],

        "Entry Price": trade["Entry Price"],
        "Entry Time": trade.get("Entry Time"),

        "Exit Time": trade["Exit Time"],
        "Exit Reason": trade["Exit Reason"],

        "Gross P&L": trade["Gross P&L"],
        "Trading Costs": trade["Trading Costs"],
        "Slippage": trade["Slippage"],
        "Net P&L": trade["Net P&L"],

        "Exit Events": list(exit_events),

        "V18.1 Synchronization Confirmed": True,
        "V18.1 Cumulative Filled Quantity": cumulative_filled,
        "V18.1 Expected Remaining Quantity": expected_remaining,

        "Final Audit": True,
        "Read Only": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Wisdom Before Wealth": True,
    }

    return {
        "Status": "PAPER_TRADE_CLOSURE_VALIDATED",
        "Closure Record": closure_record,
        "Final Audit": True,
        "Read Only": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Wisdom Before Wealth": True,
    }

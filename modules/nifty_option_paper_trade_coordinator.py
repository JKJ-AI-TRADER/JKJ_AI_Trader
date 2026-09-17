"""
JKJ AI Trader
V15.3 Paper Trade Coordinator

Purpose:
    Connect the V15.1 qualification layer and V15.2 entry
    bridge to the existing V11 paper-trading engine.

Flow:

    V14.5 Exit Qualification
            ↓
    V15.1 Paper Trade Qualification
            ↓
    V15.2 Entry Bridge
            ↓
    V11 open_paper_trade()
            ↓
       OPEN PAPER TRADE

This module does NOT:
    - place real orders
    - connect to Zerodha
    - generate trading signals
    - modify V11
    - modify V12/V13/V14
    - modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_paper_trade_qualification import (
    evaluate_paper_trade_qualification,
)

from modules.nifty_option_paper_trade_entry_bridge import (
    prepare_paper_trade_entry,
)

from modules.intraday_paper_trading import (
    open_paper_trade,
)


# ---------------------------------------------------------
# 1. Create paper trade
# ---------------------------------------------------------

def create_qualified_paper_trade(
    exit_qualification,
    quantity,
    trade_id,
    entry_time=None,
):
    """
    Create a V11 paper trade only when the complete
    V14.5 setup is permitted by V15.1 and successfully
    prepared by V15.2.
    """

    # -----------------------------------------------------
    # V15.1 — qualification
    # -----------------------------------------------------

    qualification = evaluate_paper_trade_qualification(
        exit_qualification
    )

    if qualification.get("Status") != "QUALIFIED":
        return {
            "Status": "REJECTED",
            "Stage": "V15.1",
            "Reason": qualification.get(
                "Reason",
                "Paper trade qualification failed",
            ),
        }

    if (
        qualification.get("Paper Trade Permission")
        != "PERMITTED"
    ):
        return {
            "Status": "NOT_PERMITTED",
            "Stage": "V15.1",
            "Reason": qualification.get(
                "Qualification Reason",
                "Paper trade permission not granted",
            ),
            "Paper Trade Qualification": qualification,
        }

    # -----------------------------------------------------
    # V15.2 — entry preparation
    # -----------------------------------------------------

    entry_request = prepare_paper_trade_entry(
        paper_trade_qualification=qualification,
        quantity=quantity,
        trade_id=trade_id,
        entry_time=entry_time,
    )

    if entry_request.get("Status") != "PREPARED":
        return {
            "Status": "REJECTED",
            "Stage": "V15.2",
            "Reason": entry_request.get(
                "Reason",
                "Paper trade entry preparation failed",
            ),
            "Paper Trade Qualification": qualification,
        }

    # -----------------------------------------------------
    # V11 — create paper position
    # -----------------------------------------------------

    trade = open_paper_trade(
        trade_id=entry_request["Trade ID"],
        symbol=entry_request["Symbol"],
        instrument_type=entry_request["Instrument Type"],
        entry_price=entry_request["Entry Price"],
        quantity=entry_request["Quantity"],
        stop_loss=entry_request["Stop Loss"],
        target=entry_request["Target"],
        entry_status=entry_request["Entry Status"],
        entry_reason=entry_request["Entry Reason"],
        expiry=entry_request["Expiry"],
        strike=entry_request["Strike"],
        option_type=entry_request["Option Type"],
        underlying=entry_request["Underlying"],
        entry_time=entry_request["Entry Time"],
    )

    # -----------------------------------------------------
    # Validate V11 result
    # -----------------------------------------------------

    if not isinstance(trade, dict):
        return {
            "Status": "ERROR",
            "Stage": "V11",
            "Reason": "V11 did not return a valid trade record",
        }

    if trade.get("Status") != "OPEN":
        return {
            "Status": "ERROR",
            "Stage": "V11",
            "Reason": "V11 paper trade was not opened",
            "Trade": trade,
        }

    return {
        "Status": "PAPER_TRADE_OPENED",
        "Stage": "V11",

        "Trade": trade,

        "Paper Trade Qualification": qualification,

        "Entry Request": entry_request,
    }
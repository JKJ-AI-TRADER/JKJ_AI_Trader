"""
JKJ AI Trader
Option Paper Trading Session Engine V1

Purpose:
    Orchestrate one complete option paper-trading session
    using the existing frozen JKJ engines.

Flow:

    OPEN PAPER POSITION
            ↓
       PRICE UPDATE
            ↓
       V10 MONITOR
            ↓
       HOLD / PARTIAL EXIT / EXIT
            ↓
      PAPER EXIT PROCESS
            ↓
      POSITION UPDATED
            ↓
       CONTINUE / CLOSED

This module does NOT:
    - generate trading signals
    - calculate momentum
    - change stop loss
    - change target
    - override the Exit Engine
    - override Profit Protection
    - place live broker orders
    - connect to Zerodha
    - modify main.py

Wisdom Before Wealth.
"""

from intraday_paper_trading import (
    update_paper_price,
    process_paper_exit,
)

from intraday_option_paper_position_monitor import (
    monitor_option_paper_position,
)


def run_option_paper_session(
    trade,
    price_sequence,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    max_holding_minutes=60,
):
    """
    Run one complete option paper-trading session.

    Parameters
    ----------
    trade : dict
        An OPEN paper option trade created by V9.

    price_sequence : list
        Sequence of simulated market prices.

    momentum_status : str
        Current momentum condition.

    volume_status : str
        Current volume condition.

    underlying_status : str
        Current underlying condition.

    structure_status : str
        Current price-structure condition.

    max_holding_minutes : int or float
        Maximum allowed holding time.

    Returns
    -------
    dict
        Complete paper-trading session result.
    """

    # ---------------------------------------------------------
    # 1. BASIC VALIDATION
    # ---------------------------------------------------------

    if not isinstance(trade, dict):
        return {
            "Status": "INVALID",
            "Session Status": "NOT STARTED",
            "Reasons": [
                "Trade must be a dictionary."
            ],
        }

    if trade.get("Status") != "OPEN":
        return {
            "Status": "INVALID",
            "Session Status": "NOT STARTED",
            "Reasons": [
                "Paper trade must be OPEN."
            ],
        }

    if not isinstance(price_sequence, list):
        return {
            "Status": "INVALID",
            "Session Status": "NOT STARTED",
            "Reasons": [
                "Price sequence must be a list."
            ],
        }

    if len(price_sequence) == 0:
        return {
            "Status": "INVALID",
            "Session Status": "NOT STARTED",
            "Reasons": [
                "Price sequence must contain at least one price."
            ],
        }

    # ---------------------------------------------------------
    # 2. SESSION EVENT LOG
    # ---------------------------------------------------------

    session_events = []

    # ---------------------------------------------------------
    # 3. PROCESS EACH PRICE
    # ---------------------------------------------------------

    for observation_number, current_price in enumerate(
        price_sequence,
        start=1
    ):

        if trade.get("Status") != "OPEN":
            break

        # -----------------------------------------------------
        # PRICE UPDATE
        # -----------------------------------------------------

        update_result = update_paper_price(
            trade,
            current_price,
        )

        if update_result.get("Status") != "UPDATED":
            return {
                "Status": "ERROR",
                "Session Status": "ERROR",
                "Trade": trade,
                "Session Events": session_events,
                "Reasons": [
                    "Paper price update failed."
                ],
                "Update Result": update_result,
            }

        # -----------------------------------------------------
        # HOLDING TIME
        # -----------------------------------------------------

        holding_minutes = observation_number

        # -----------------------------------------------------
        # V10 MONITOR
        # -----------------------------------------------------

        monitor_result = monitor_option_paper_position(
            trade=trade,
            current_price=current_price,
            momentum_status=momentum_status,
            volume_status=volume_status,
            underlying_status=underlying_status,
            structure_status=structure_status,
            holding_minutes=holding_minutes,
            max_holding_minutes=max_holding_minutes,
        )

        if monitor_result.get("Status") != "READY":
            return {
                "Status": "ERROR",
                "Session Status": "ERROR",
                "Trade": trade,
                "Session Events": session_events,
                "Reasons": [
                    "Option paper position monitoring failed."
                ],
                "Monitor Result": monitor_result,
            }

        decision = monitor_result.get(
            "Decision",
            "HOLD",
        )

        # -----------------------------------------------------
        # RECORD MONITOR EVENT
        # -----------------------------------------------------

        session_events.append(
            {
                "Observation": observation_number,
                "Price": current_price,
                "Decision": decision,
                "Monitor Result": monitor_result,
            }
        )

        # -----------------------------------------------------
        # HOLD
        # -----------------------------------------------------

        if decision == "HOLD":
            continue

        # -----------------------------------------------------
        # PARTIAL EXIT / EXIT
        # -----------------------------------------------------

        if decision in (
            "PARTIAL EXIT",
            "EXIT",
        ):

            exit_result = process_paper_exit(
                trade=trade,
                current_price=current_price,
                exit_signal=monitor_result.get(
                    "Exit Result",
                    {}
                ).get(
                    "Exit Reason",
                    decision,
                ),
                momentum_status=momentum_status,
                volume_status=volume_status,
                underlying_status=underlying_status,
                structure_status=structure_status,
            )

            session_events[-1]["Exit Result"] = exit_result

            if exit_result.get("Status") not in (
                "RECORDED",
                "NO ACTION",
                "HOLD",
            ):
                return {
                    "Status": "ERROR",
                    "Session Status": "ERROR",
                    "Trade": trade,
                    "Session Events": session_events,
                    "Reasons": [
                        "Paper exit processing failed."
                    ],
                    "Exit Result": exit_result,
                }

            # -------------------------------------------------
            # POSITION CLOSED
            # -------------------------------------------------

            if trade.get("Status") == "CLOSED":
                break

    # ---------------------------------------------------------
    # 4. FINAL SESSION STATUS
    # ---------------------------------------------------------

    if trade.get("Status") == "CLOSED":

        session_status = "CLOSED"

    else:

        session_status = "OPEN"

    # ---------------------------------------------------------
    # 5. FINAL RESULT
    # ---------------------------------------------------------

    return {
        "Status": "READY",
        "Session Status": session_status,
        "Trade ID": trade.get("Trade ID"),
        "Trading Symbol": trade.get("Symbol"),
        "Entry Price": trade.get("Entry Price"),
        "Original Quantity": trade.get(
            "Original Quantity"
        ),
        "Final Quantity": trade.get(
            "Current Quantity"
        ),
        "Peak Price": trade.get(
            "Peak Price"
        ),
        "Gross P&L": trade.get(
            "Gross P&L",
            0.0
        ),
        "Trading Costs": trade.get(
            "Trading Costs",
            0.0
        ),
        "Slippage": trade.get(
            "Slippage",
            0.0
        ),
        "Net P&L": trade.get(
            "Net P&L",
            0.0
        ),
        "Exit Time": trade.get(
            "Exit Time"
        ),
        "Exit Reason": trade.get(
            "Exit Reason"
        ),
        "Exit Events": trade.get(
            "Exit Events",
            []
        ),
        "Session Events": session_events,
        "Trade": trade,
        "Reasons": [
            "Option paper-trading session completed "
            "using the existing JKJ monitoring and "
            "paper-exit engines."
        ],
    }
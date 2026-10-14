"""
JKJ AI Trader
V21.2 -> Paper Trade Bridge

Purpose:
    Connect a completed V21.2.17 Risk + Stop + Targets result
    to the existing V15.3 paper-trade coordinator.

Flow:

    V21.2.17
        ↓
    Qualified Risk/Stop/Target Contract
        ↓
    V15.1 Paper Qualification
        ↓
    V15.2 Entry Bridge
        ↓
    V15.3 Paper Trade Coordinator
        ↓
    PAPER BUY

Safety:
    - No live orders
    - No broker order placement
    - No new market observations
    - Does not modify V21.2.16
    - Does not modify V21.2.17
    - Does not modify V11

Wisdom Before Wealth.
"""

import math

from modules.nifty_option_paper_trade_coordinator import (
    create_qualified_paper_trade,
)


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


def _blocked(reason):
    return {
        "Status": "PAPER_TRADE_BRIDGE_REJECTED",
        "Reason": reason,
        "Paper Execution": False,
        "Live Order": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }


def create_v21_2_paper_trade(
    risk_stop_targets_result,
    trade_id,
    quantity,
    entry_time=None,
):
    """
    Convert one completed V21.2.17 contract result into
    an existing V15.3 paper trade.

    This function does not create a new trading decision.
    It only passes an already-qualified V21.2.17 result
    into the existing paper-trading infrastructure.
    """

    # ---------------------------------------------------------
    # 1. Validate V21.2.17 result
    # ---------------------------------------------------------

    if not isinstance(risk_stop_targets_result, dict):
        return _blocked(
            "V21.2.17 result must be a dictionary"
        )

    if (
        risk_stop_targets_result.get("Status")
        != "RISK_STOP_TARGETS_COMPLETE"
    ):
        return _blocked(
            "V21.2.17 result is not complete"
        )

    if risk_stop_targets_result.get("Live Order") is not False:
        return _blocked(
            "Live Order flag must remain False"
        )

    if risk_stop_targets_result.get("Paper Trade") is not False:
        return _blocked(
            "V21.2.17 Paper Trade flag must remain False"
        )

    # ---------------------------------------------------------
    # 2. Validate required V21.2.17 contract fields
    # ---------------------------------------------------------

    required_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Entry Price",
        "Stop Price",
        "Target 1",
        "Target 2",
        "Target 3",
    ]

    for field in required_fields:

        if field not in risk_stop_targets_result:

            return _blocked(
                f"Missing required V21.2.17 field: {field}"
            )

    # ---------------------------------------------------------
    # 3. Validate trade identity
    # ---------------------------------------------------------

    if trade_id is None or str(trade_id).strip() == "":
        return _blocked(
            "Trade ID is required"
        )

    quantity = _coerce_whole_quantity(quantity)
    if quantity is None:
        return _blocked(
            "Quantity must be a finite whole number"
        )

    if quantity <= 0:
        return _blocked(
            "Quantity must be greater than zero"
        )

    # ---------------------------------------------------------
    # 4. Build the V15.1-compatible exit qualification
    # ---------------------------------------------------------

    exit_qualification = {
        "Status": "EVALUATED",

        "Trading Symbol": risk_stop_targets_result[
            "Trading Symbol"
        ],

        "Underlying": risk_stop_targets_result[
            "Underlying"
        ],

        "Expiry": risk_stop_targets_result[
            "Expiry"
        ],

        "Strike": risk_stop_targets_result[
            "Strike"
        ],

        "Option Type": risk_stop_targets_result[
            "Option Type"
        ],

        "Entry Price": risk_stop_targets_result[
            "Entry Price"
        ],

        "Stop Price": risk_stop_targets_result[
            "Stop Price"
        ],

        "Target 1": risk_stop_targets_result[
            "Target 1"
        ],

        "Target 2": risk_stop_targets_result[
            "Target 2"
        ],

        "Target 3": risk_stop_targets_result[
            "Target 3"
        ],

        "Risk Reward 1": risk_stop_targets_result.get(
            "Risk Reward 1"
        ),

        "Risk Reward 2": risk_stop_targets_result.get(
            "Risk Reward 2"
        ),

        "Risk Reward 3": risk_stop_targets_result.get(
            "Risk Reward 3"
        ),

        "Entry Qualification": risk_stop_targets_result.get(
            "Entry Qualification"
        ),

        "Entry Risk Context": risk_stop_targets_result.get(
            "Entry Risk Context"
        ),

        "Stop-Loss Context": risk_stop_targets_result.get(
            "Stop-Loss Context"
        ),

        "Exit Structure": risk_stop_targets_result.get(
            "Exit Structure"
        ),
    }

    # ---------------------------------------------------------
    # 5. Required V15.1 fields must be complete
    # ---------------------------------------------------------

    v15_required = [
        "Risk Reward 1",
        "Risk Reward 2",
        "Risk Reward 3",
        "Entry Qualification",
        "Entry Risk Context",
        "Stop-Loss Context",
        "Exit Structure",
    ]

    for field in v15_required:

        if exit_qualification.get(field) is None:

            return _blocked(
                f"Missing V15 qualification field: {field}"
            )

    # ---------------------------------------------------------
    # 6. Existing V15.3 -> V11 paper execution
    # ---------------------------------------------------------

    result = create_qualified_paper_trade(
        exit_qualification=exit_qualification,
        quantity=quantity,
        trade_id=trade_id,
        entry_time=entry_time,
    )

    # ---------------------------------------------------------
    # 7. Preserve paper-only safety
    # ---------------------------------------------------------

    if not isinstance(result, dict):

        return _blocked(
            "V15.3 did not return a valid result"
        )

    if result.get("Status") != "PAPER_TRADE_OPENED":

        return {
            **result,
            "Paper Execution": False,
            "Live Order": False,
            "Broker Communication": False,
            "Order Placement Permitted": False,
        }

    return {
        "Status": "V21_2_PAPER_TRADE_OPENED",

        "Trade ID": trade_id,

        "Trading Symbol": risk_stop_targets_result[
            "Trading Symbol"
        ],

        "V21.2.17 Result": risk_stop_targets_result,

        "V15.3 Result": result,

        "Trade": result.get("Trade"),

        "Paper Execution": True,
        "Live Order": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,

        "Wisdom Before Wealth": True,
    }

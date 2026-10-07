"""
JKJ AI Trader

V21.2 -> V14.5 -> V17.8.7 -> V15.3 Paper Handoff

Purpose
-------
Controlled adapter from the V21.2.17 Risk/Stop/Targets result
into the existing V14.5 Exit Qualification and V17.8.7
V15 paper-trade handoff.

Architecture
------------
V21.2.17
    -> V14.5 Exit Qualification
    -> V15.1 Paper Trade Qualification
    -> V17.8.7 Controlled V15 Handoff
    -> V15.3 Paper Trade Coordinator
    -> V11 Paper Trade

Safety
------
No new market observations.
No candidate ranking.
No live broker communication.
No live order placement.
No capital reassignment.
Paper execution only.
"""

from modules.nifty_option_exit_qualification import (
    evaluate_exit_qualification,
)

from modules.nifty_option_paper_trade_qualification import (
    evaluate_paper_trade_qualification,
)

from modules.nifty_option_v17_8_v15_paper_handoff import (
    handoff_to_v15_paper_trade,
)


def _blocked(reason, stage=None):
    return {
        "Status": "V21_2_V14_5_PAPER_HANDOFF_BLOCKED",
        "Stage": stage,
        "Reason": reason,
        "V14.5 Exit Qualification": None,
        "V15.1 Paper Trade Qualification": None,
        "V17.8.7 Handoff": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "New Market Observations": False,
        "Wisdom Before Wealth": True,
    }


def create_v21_2_v14_5_paper_handoff(
    risk_stop_targets_contract,
    trade_id,
    quantity,
    entry_time=None,
):
    """
    Convert one successful V21.2.17 contract into a controlled
    V15 paper-trade handoff.

    Parameters
    ----------
    risk_stop_targets_contract : dict
        One successful contract result from V21.2.17.

    trade_id : str
        Explicit paper-trade identifier.

    quantity : int
        Explicit paper-trade quantity.

    entry_time : optional
        Paper-trade entry timestamp.

    Returns
    -------
    dict
        Controlled handoff result.
    """

    # ---------------------------------------------------------
    # Step 1 — Validate V21.2.17 input
    # ---------------------------------------------------------

    if not isinstance(
        risk_stop_targets_contract,
        dict,
    ):
        return _blocked(
            "V21.2.17 contract result must be a dictionary",
            "V21.2.17",
        )

    if risk_stop_targets_contract.get(
        "Status"
    ) != "RISK_STOP_TARGETS_COMPLETE":
        return _blocked(
            "V21.2.17 contract must have Status "
            "RISK_STOP_TARGETS_COMPLETE",
            "V21.2.17",
        )

    if not isinstance(trade_id, str) or not trade_id.strip():
        return _blocked(
            "Trade ID is required",
            "V15_BOUNDARY",
        )

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return _blocked(
            "Quantity must be a positive integer",
            "V15_BOUNDARY",
        )

    # ---------------------------------------------------------
    # Step 2 — Validate required V21.2.17 fields
    # ---------------------------------------------------------

    required_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Option Direction",
        "Entry Qualification",
        "Entry Risk Context",
        "Stop-Loss Context",
        "Entry Price",
        "Stop Price",
        "Stop Distance",
        "Target 1",
        "Target 2",
        "Target 3",
    ]

    missing = [
        field
        for field in required_fields
        if field not in risk_stop_targets_contract
    ]

    if missing:
        return _blocked(
            f"V21.2.17 required fields missing: {missing}",
            "V21.2.17",
        )

    # ---------------------------------------------------------
    # Step 3 — Build V14.5 target-data payload
    #
    # V14.5 remains authoritative for:
    #   Risk Reward 1
    #   Risk Reward 2
    #   Risk Reward 3
    #   Exit Structure
    # ---------------------------------------------------------

    target_data = {
        "Status": "TARGETS_VALIDATED",

        "Trading Symbol": risk_stop_targets_contract[
            "Trading Symbol"
        ],
        "Underlying": risk_stop_targets_contract[
            "Underlying"
        ],
        "Expiry": risk_stop_targets_contract[
            "Expiry"
        ],
        "Strike": risk_stop_targets_contract[
            "Strike"
        ],
        "Option Type": risk_stop_targets_contract[
            "Option Type"
        ],

        "Option Direction": risk_stop_targets_contract[
            "Option Direction"
        ],

        "Entry Qualification": risk_stop_targets_contract[
            "Entry Qualification"
        ],

        "Entry Risk Context": risk_stop_targets_contract[
            "Entry Risk Context"
        ],

        "Stop-Loss Context": risk_stop_targets_contract[
            "Stop-Loss Context"
        ],

        "Entry Price": risk_stop_targets_contract[
            "Entry Price"
        ],

        "Stop Price": risk_stop_targets_contract[
            "Stop Price"
        ],

        "Stop Distance": risk_stop_targets_contract[
            "Stop Distance"
        ],

        "Target 1": risk_stop_targets_contract[
            "Target 1"
        ],

        "Target 2": risk_stop_targets_contract[
            "Target 2"
        ],

        "Target 3": risk_stop_targets_contract[
            "Target 3"
        ],
    }

    # ---------------------------------------------------------
    # Step 4 — V14.5 Exit Qualification
    # ---------------------------------------------------------

    exit_qualification = evaluate_exit_qualification(
        target_data
    )

    if exit_qualification.get("Status") != "EVALUATED":
        return {
            **_blocked(
                exit_qualification.get(
                    "Reason",
                    "V14.5 exit qualification rejected",
                ),
                "V14.5",
            ),
            "V14.5 Exit Qualification": (
                exit_qualification
            ),
        }

    # ---------------------------------------------------------
    # Step 5 — V15.1 Paper Trade Qualification
    #
    # Reuse the existing authoritative qualification logic.
    # This determines whether paper execution is permitted.
    # ---------------------------------------------------------

    paper_trade_qualification = (
        evaluate_paper_trade_qualification(
            exit_qualification
        )
    )

    if paper_trade_qualification.get(
        "Status"
    ) != "QUALIFIED":
        return {
            **_blocked(
                paper_trade_qualification.get(
                    "Reason",
                    "V15.1 paper-trade qualification rejected",
                ),
                "V15.1",
            ),
            "V14.5 Exit Qualification": (
                exit_qualification
            ),
            "V15.1 Paper Trade Qualification": (
                paper_trade_qualification
            ),
        }

    # ---------------------------------------------------------
    # Step 6 — Build V17.8.7 mapped-entry boundary
    # ---------------------------------------------------------

    mapped_entry = {
        "Status": "MAPPED",

        "Trade ID": trade_id,

        "Trading Symbol": exit_qualification[
            "Trading Symbol"
        ],

        "Instrument Type": "OPTION",

        "Underlying": exit_qualification[
            "Underlying"
        ],

        "Expiry": exit_qualification[
            "Expiry"
        ],

        "Strike": exit_qualification[
            "Strike"
        ],

        "Option Type": exit_qualification[
            "Option Type"
        ],

        "Entry Price": exit_qualification[
            "Entry Price"
        ],

        "Quantity": quantity,

        "Stop Loss": exit_qualification[
            "Stop Price"
        ],

        "Target": exit_qualification[
            "Target 1"
        ],

        "Target1": exit_qualification[
            "Target 1"
        ],

        "Target2": exit_qualification[
            "Target 2"
        ],

        "Target3": exit_qualification[
            "Target 3"
        ],

        "RR1": exit_qualification[
            "Risk Reward 1"
        ],

        "RR2": exit_qualification[
            "Risk Reward 2"
        ],

        "RR3": exit_qualification[
            "Risk Reward 3"
        ],

        "Entry Status": exit_qualification[
            "Entry Qualification"
        ],

        "Entry Reason": (
            "V21.2 Decision + V14.5 Exit "
            "Qualification approved for paper handoff"
        ),

        "Paper Trade Permission": "PERMITTED",

        "Contract Valid": True,

        "Execution Ready": True,

        "Paper Execution": True,

        "Broker Communication": False,

        "Order Placement Permitted": False,
    }

    # ---------------------------------------------------------
    # Step 7 — Existing V17.8.7 controlled handoff
    # ---------------------------------------------------------

    handoff_result = handoff_to_v15_paper_trade(
        mapped_entry=mapped_entry,
        exit_qualification=exit_qualification,
        entry_time=entry_time,
    )

    if handoff_result.get(
        "Status"
    ) != "V17_8_7_PAPER_HANDOFF_COMPLETE":
        return {
            "Status": (
                "V21_2_V14_5_PAPER_HANDOFF_REJECTED"
            ),
            "Stage": handoff_result.get("Stage"),
            "Reason": handoff_result.get(
                "Reason",
                "Existing V17.8.7 handoff rejected",
            ),
            "V14.5 Exit Qualification": (
                exit_qualification
            ),
            "V15.1 Paper Trade Qualification": (
                paper_trade_qualification
            ),
            "Mapped Entry": mapped_entry,
            "V17.8.7 Handoff": handoff_result,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "New Market Observations": False,
            "Wisdom Before Wealth": True,
        }

    # ---------------------------------------------------------
    # Step 8 — Complete result
    # ---------------------------------------------------------

    return {
        "Status": (
            "V21_2_V14_5_PAPER_HANDOFF_COMPLETE"
        ),
        "Stage": "V11_PAPER_TRADE",
        "Trade ID": trade_id,
        "Trading Symbol": exit_qualification[
            "Trading Symbol"
        ],
        "Quantity": quantity,
        "Entry Price": exit_qualification[
            "Entry Price"
        ],
        "Stop Price": exit_qualification[
            "Stop Price"
        ],
        "Target 1": exit_qualification[
            "Target 1"
        ],
        "Target 2": exit_qualification[
            "Target 2"
        ],
        "Target 3": exit_qualification[
            "Target 3"
        ],
        "Risk Reward 1": exit_qualification[
            "Risk Reward 1"
        ],
        "Risk Reward 2": exit_qualification[
            "Risk Reward 2"
        ],
        "Risk Reward 3": exit_qualification[
            "Risk Reward 3"
        ],
        "Entry Qualification": exit_qualification[
            "Entry Qualification"
        ],
        "Entry Risk Context": exit_qualification[
            "Entry Risk Context"
        ],
        "Stop-Loss Context": exit_qualification[
            "Stop-Loss Context"
        ],
        "Exit Structure": exit_qualification[
            "Exit Structure"
        ],
        "V14.5 Exit Qualification": (
            exit_qualification
        ),
        "V15.1 Paper Trade Qualification": (
            paper_trade_qualification
        ),
        "Mapped Entry": mapped_entry,
        "V17.8.7 Handoff": handoff_result,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "New Market Observations": False,
        "Wisdom Before Wealth": True,
    }

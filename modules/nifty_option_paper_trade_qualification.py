"""
JKJ AI Trader
V15.1 Paper Trade Qualification Bridge

Purpose:
    Determine whether a V14.5 qualified setup is permitted
    to enter the existing V11 paper-trading engine.

This module does NOT:
    - place real orders
    - connect to Zerodha
    - open a paper trade
    - modify V11
    - modify V12/V13/V14
    - modify main.py

Principle:
    V13-V14 decides whether the setup qualifies.
    V15.1 enforces that decision.

Wisdom Before Wealth.
"""


# ---------------------------------------------------------
# 1. Paper Trade Qualification
# ---------------------------------------------------------

def evaluate_paper_trade_qualification(
    exit_qualification,
):
    """
    Evaluate whether a completed V14.5 setup is permitted
    to enter the V11 paper-trading engine.
    """

    if not isinstance(exit_qualification, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid exit qualification",
        }

    if exit_qualification.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Exit qualification must have Status EVALUATED",
        }

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
        "Risk Reward 1",
        "Risk Reward 2",
        "Risk Reward 3",
        "Entry Qualification",
        "Entry Risk Context",
        "Stop-Loss Context",
        "Exit Structure",
    ]

    for field in required_fields:
        if field not in exit_qualification:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}",
            }

    # -----------------------------------------------------
    # Controlled paper-trade permission
    # -----------------------------------------------------

    if (
        exit_qualification["Entry Qualification"]
        == "ENTRY_QUALIFIED"
        and
        exit_qualification["Entry Risk Context"]
        == "CONTROLLED_RISK_CONTEXT"
        and
        exit_qualification["Stop-Loss Context"]
        == "STOP_SUPPORTED"
        and
        exit_qualification["Exit Structure"]
        == "EXIT_STRUCTURE_SUPPORTED"
    ):

        paper_trade_permission = "PERMITTED"
        qualification_reason = (
            "V14.5 setup satisfies all controlled "
            "paper-trade entry requirements"
        )

    else:

        paper_trade_permission = "NOT_PERMITTED"

        qualification_reason = (
            "V14.5 setup does not satisfy all controlled "
            "paper-trade entry requirements"
        )

    # -----------------------------------------------------
    # Return complete qualification record
    # -----------------------------------------------------

    return {
        "Status": "QUALIFIED",

        "Trading Symbol": exit_qualification["Trading Symbol"],
        "Underlying": exit_qualification["Underlying"],
        "Expiry": exit_qualification["Expiry"],
        "Strike": exit_qualification["Strike"],
        "Option Type": exit_qualification["Option Type"],

        "Entry Price": exit_qualification["Entry Price"],
        "Stop Price": exit_qualification["Stop Price"],

        "Target 1": exit_qualification["Target 1"],
        "Target 2": exit_qualification["Target 2"],
        "Target 3": exit_qualification["Target 3"],

        "Risk Reward 1": exit_qualification["Risk Reward 1"],
        "Risk Reward 2": exit_qualification["Risk Reward 2"],
        "Risk Reward 3": exit_qualification["Risk Reward 3"],

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

        "Paper Trade Permission": paper_trade_permission,

        "Qualification Reason": qualification_reason,
    }
"""
JKJ AI Trader
Real-Market → V20.1 Integration

Purpose:
    Convert an already-qualified Decision/Risk result from the
    real-market validation chain into the existing V20.1
    capital-allocation qualification boundary.

This module does NOT:
- create trading decisions
- create risk decisions
- generate priority
- generate requested allocation
- rank candidates
- allocate capital
- calculate option quantity
- communicate with Zerodha
- place orders
- modify V16.1
- modify V20.1
- modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)


def _blocked(reason):
    return {
        "Status": "REAL_MARKET_V20_1_INTEGRATION_BLOCKED",
        "Capital Allocation Eligible": False,
        "Reason": reason,
        "Automatic Ranking": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }


def integrate_real_market_to_v20_1(
    entry_risk_context,
    stop_loss_context,
    exit_qualification,
    paper_qualification,
    priority,
    requested_allocation,
):
    """
    Integrate an already-qualified real-market Decision/Risk
    result into V20.1.

    Priority and Requested Allocation must be explicitly supplied.
    """

    inputs = {
        "Entry Risk Context": entry_risk_context,
        "Stop-Loss Context": stop_loss_context,
        "Exit Qualification": exit_qualification,
        "Paper Qualification": paper_qualification,
    }

    for name, value in inputs.items():
        if not isinstance(value, dict):
            return _blocked(
                f"{name} must be a dictionary."
            )

    if entry_risk_context.get("Status") != "EVALUATED":
        return _blocked(
            "Entry Risk Context status must be EVALUATED."
        )

    if stop_loss_context.get("Status") != "EVALUATED":
        return _blocked(
            "Stop-Loss Context status must be EVALUATED."
        )

    if exit_qualification.get("Status") != "EVALUATED":
        return _blocked(
            "Exit Qualification status must be EVALUATED."
        )

    if paper_qualification.get("Status") != "QUALIFIED":
        return _blocked(
            "Paper Qualification status must be QUALIFIED."
        )

    required_fields = {
        "Trading Symbol": exit_qualification,
        "Entry Qualification": exit_qualification,
        "Entry Risk Context": exit_qualification,
        "Stop-Loss Context": stop_loss_context,
        "Exit Structure": exit_qualification,
        "Paper Trade Permission": paper_qualification,
    }

    for field, source in required_fields.items():
        if field not in source:
            return _blocked(
                f"Missing required field: {field}."
            )

    if exit_qualification["Trading Symbol"] != (
        entry_risk_context.get("Trading Symbol")
    ):
        return _blocked(
            "Trading Symbol mismatch between Decision/Risk stages."
        )

    if exit_qualification["Trading Symbol"] != (
        stop_loss_context.get("Trading Symbol")
    ):
        return _blocked(
            "Trading Symbol mismatch between stop-loss context "
            "and exit qualification."
        )

    if exit_qualification["Entry Risk Context"] != (
        entry_risk_context.get("Entry Risk Context")
    ):
        return _blocked(
            "Entry Risk Context mismatch."
        )

    if exit_qualification["Stop-Loss Context"] != (
        stop_loss_context.get("Stop-Loss Context")
    ):
        return _blocked(
            "Stop-Loss Context mismatch."
        )

    opportunity = {
        "Trading Symbol": exit_qualification[
            "Trading Symbol"
        ],
        "Paper Trade Permission": paper_qualification[
            "Paper Trade Permission"
        ],
        "Entry Risk Context": exit_qualification[
            "Entry Risk Context"
        ],
        "Entry Qualification": exit_qualification[
            "Entry Qualification"
        ],
        "Stop-Loss Context": exit_qualification[
            "Stop-Loss Context"
        ],
        "Exit Structure": exit_qualification[
            "Exit Structure"
        ],
    }

    v20_1_result = qualify_capital_allocation(
        opportunity=opportunity,
        priority=priority,
        requested_allocation=requested_allocation,
    )

    if v20_1_result.get("Status") != (
        "CAPITAL_ALLOCATION_QUALIFIED"
    ):
        return {
            "Status": "REAL_MARKET_V20_1_INTEGRATION_BLOCKED",
            "V20.1 Result": v20_1_result,
            "Automatic Ranking": False,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "REAL_MARKET_V20_1_INTEGRATION_COMPLETE",
        "Trading Symbol": opportunity["Trading Symbol"],
        "Priority": priority,
        "Requested Allocation": requested_allocation,
        "V20.1 Result": v20_1_result,
        "Automatic Ranking": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }

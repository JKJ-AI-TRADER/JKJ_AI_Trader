"""
JKJ AI Trader
V17.8.7 - Controlled V15 Paper-Trade Handoff

V17.8 provides the paper execution result.
V14.5 provides the authoritative EVALUATED qualification.
V15.3 remains the existing paper-trade coordinator.

No live broker communication.
No live order placement.
No changes to V15/V11/main.py.
"""

from modules.nifty_option_v17_8_v15_entry_boundary import (
    validate_v15_entry_boundary,
)

from modules.nifty_option_paper_trade_coordinator import (
    create_qualified_paper_trade,
)


def _blocked(reason):
    return {
        "Status": "V15_PAPER_HANDOFF_BLOCKED",
        "Reason": reason,
        "V15 Handoff": None,
        "V15 Call Permitted": False,
        "V11 Call Permitted": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def handoff_to_v15_paper_trade(
    mapped_entry,
    exit_qualification,
    entry_time=None,
):
    """
    Validate the V17.8 mapped execution and genuine V14.5
    EVALUATED qualification, then hand off to V15.3.
    """

    if not isinstance(mapped_entry, dict):
        return _blocked("Mapped entry must be a dictionary")

    boundary = validate_v15_entry_boundary(mapped_entry)

    if boundary.get("Status") != "V15_ENTRY_BOUNDARY_VALIDATED":
        return _blocked(
            boundary.get(
                "Reason",
                "V15 entry boundary validation failed",
            )
        )

    if not isinstance(exit_qualification, dict):
        return _blocked(
            "V14.5 exit qualification must be a dictionary"
        )

    if exit_qualification.get("Status") != "EVALUATED":
        return _blocked(
            "V14.5 exit qualification must have Status EVALUATED"
        )

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

    missing = [
        field
        for field in required_fields
        if field not in exit_qualification
    ]

    if missing:
        return _blocked(
            f"V14.5 qualification fields missing: {missing}"
        )

    payload = boundary.get("V15 Entry Payload")

    if not isinstance(payload, dict):
        return _blocked("V15 entry payload is missing")

    if (
        payload.get("Trading Symbol")
        != exit_qualification.get("Trading Symbol")
    ):
        return _blocked(
            "Paper fill symbol does not match V14.5 qualification"
        )

    trade_id = payload.get("Trade ID")

    if not trade_id:
        return _blocked("Trade ID is required")

    quantity = payload.get("Quantity")

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return _blocked("Quantity must be a positive integer")

    # V14.5 remains authoritative.
    # Do not replace its Entry Price with the V17.8 fill price.
    result = create_qualified_paper_trade(
        exit_qualification=exit_qualification,
        quantity=quantity,
        trade_id=trade_id,
        entry_time=entry_time,
    )

    if not isinstance(result, dict):
        return _blocked(
            "V15.3 did not return a valid result"
        )

    if result.get("Status") == "PAPER_TRADE_OPENED":
        return {
            "Status": "V17_8_7_PAPER_HANDOFF_COMPLETE",
            "Stage": "V15.3",
            "Trade": result.get("Trade"),
            "Paper Trade Qualification": result.get(
                "Paper Trade Qualification"
            ),
            "Entry Request": result.get("Entry Request"),
            "Qualified Entry Price": exit_qualification[
                "Entry Price"
            ],
            "Paper Fill Price": payload["Entry Price"],
            "Quantity": quantity,
            "V15 Handoff": True,
            "V15 Call Permitted": True,
            "V11 Call Permitted": True,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V17_8_7_PAPER_HANDOFF_REJECTED",
        "Stage": result.get("Stage"),
        "Reason": result.get(
            "Reason",
            "V15.3 rejected the paper-trade handoff",
        ),
        "V15 Result": result,
        "V15 Handoff": False,
        "V15 Call Permitted": True,
        "V11 Call Permitted": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

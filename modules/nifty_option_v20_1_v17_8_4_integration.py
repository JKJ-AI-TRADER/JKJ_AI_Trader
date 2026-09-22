"""
JKJ AI Trader
V20.1 -> V17.8.4 Paper Execution Audit Integration

Purpose:
    Convert a successful V20.1 -> V17.8.3 paper position
    into the existing V17.8.4 read-only audit engine.

Safety boundary:
    - READ-ONLY AUDIT
    - PAPER EXECUTION ONLY
    - NO ZERODHA IMPORT
    - NO BROKER COMMUNICATION
    - NO LIVE ORDER PLACEMENT
    - NO PRIORITY GENERATION
    - NO REQUESTED ALLOCATION GENERATION
    - NO AUTOMATIC RANKING
    - NO CAPITAL REASSIGNMENT
    - NO POSITION OR CAPITAL MODIFICATION
    - NO MAIN.PY MODIFICATION

Wisdom Before Wealth.
"""

from nifty_option_v17_8_paper_execution_audit import (
    create_paper_execution_audit,
)


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_4_INTEGRATION_BLOCKED",
        "Reason": reason,
        "V17.8.4 Paper Audit": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Read Only": True,
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v17_8_4(
    v20_1_v17_8_3_result,
):
    """
    Convert a successful V20.1 -> V17.8.3 paper position
    into a V17.8.4 read-only execution audit.

    This function does not modify the position or capital.
    """

    if not isinstance(v20_1_v17_8_3_result, dict):
        return _blocked(
            "V20.1 -> V17.8.3 result must be a dictionary"
        )

    if (
        v20_1_v17_8_3_result.get("Status")
        != "V20_1_V17_8_3_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8.3 integration is not complete"
        )

    if v20_1_v17_8_3_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution must remain enabled"
        )

    if v20_1_v17_8_3_result.get("Broker Communication") is True:
        return _blocked(
            "Broker communication must remain disabled"
        )

    if v20_1_v17_8_3_result.get("Order Placement Permitted") is True:
        return _blocked(
            "Live order placement must remain disabled"
        )

    if v20_1_v17_8_3_result.get("Capital Reassignment") is True:
        return _blocked(
            "Capital reassignment is not permitted"
        )

    if v20_1_v17_8_3_result.get("Automatic Ranking") is True:
        return _blocked(
            "Automatic ranking is not permitted"
        )

    if (
        v20_1_v17_8_3_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain Decision/Risk layer"
        )

    paper_position_result = v20_1_v17_8_3_result.get(
        "V17.8.3 Paper Position"
    )

    if not isinstance(paper_position_result, dict):
        return _blocked(
            "V17.8.3 paper position result is missing"
        )

    if paper_position_result.get("Status") != "PAPER_POSITION_CREATED":
        return _blocked(
            "V17.8.3 paper position is not created"
        )

    audit_result = create_paper_execution_audit(
        paper_position_result
    )

    if audit_result.get("Status") != "PAPER_EXECUTION_AUDIT_COMPLETE":
        return {
            "Status": "V20_1_V17_8_4_INTEGRATION_BLOCKED",
            "Reason": "V17.8.4 paper execution audit was not completed",
            "V17.8.4 Paper Audit": audit_result,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Read Only": True,
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_4_INTEGRATION_COMPLETE",
        "V17.8.3 Paper Position": paper_position_result,
        "V17.8.4 Paper Audit": audit_result,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Read Only": True,
        "Wisdom Before Wealth": True,
    }
"""
JKJ AI Trader
V20.1 -> V17.8.3 Paper Position Integration

Purpose:
    Convert a successful V20.1 -> V17.8.2 paper fill
    into the existing V17.8.3 paper position engine.

Safety boundary:
    - PAPER POSITION ONLY
    - NO ZERODHA IMPORT
    - NO BROKER COMMUNICATION
    - NO LIVE ORDER PLACEMENT
    - NO PRIORITY GENERATION
    - NO REQUESTED ALLOCATION GENERATION
    - NO AUTOMATIC RANKING
    - NO CAPITAL REASSIGNMENT
    - NO MAIN.PY MODIFICATION

Wisdom Before Wealth.
"""

from nifty_option_v17_8_paper_position import (
    create_paper_position,
)


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_3_INTEGRATION_BLOCKED",
        "Reason": reason,
        "V17.8.3 Paper Position": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v17_8_3(
    v20_1_v17_8_2_result,
):
    """
    Convert a successful V20.1 -> V17.8.2 paper fill
    into a V17.8.3 paper position.

    This function does not generate priority, allocation,
    quantity, or contract identity.
    """

    if not isinstance(v20_1_v17_8_2_result, dict):
        return _blocked(
            "V20.1 -> V17.8.2 result must be a dictionary"
        )

    if (
        v20_1_v17_8_2_result.get("Status")
        != "V20_1_V17_8_2_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8.2 integration is not complete"
        )

    if v20_1_v17_8_2_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution must remain enabled"
        )

    if v20_1_v17_8_2_result.get("Broker Communication") is True:
        return _blocked(
            "Broker communication must remain disabled"
        )

    if v20_1_v17_8_2_result.get("Order Placement Permitted") is True:
        return _blocked(
            "Live order placement must remain disabled"
        )

    if v20_1_v17_8_2_result.get("Capital Reassignment") is True:
        return _blocked(
            "Capital reassignment is not permitted"
        )

    if v20_1_v17_8_2_result.get("Automatic Ranking") is True:
        return _blocked(
            "Automatic ranking is not permitted"
        )

    if (
        v20_1_v17_8_2_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain Decision/Risk layer"
        )

    paper_fill_result = v20_1_v17_8_2_result.get(
        "V17.8.2 Paper Fill"
    )

    if not isinstance(paper_fill_result, dict):
        return _blocked(
            "V17.8.2 paper fill result is missing"
        )

    if paper_fill_result.get("Status") != "PAPER_FILL_COMPLETE":
        return _blocked(
            "V17.8.2 paper fill is not complete"
        )

    position_result = create_paper_position(
        paper_fill_result
    )

    if position_result.get("Status") != "PAPER_POSITION_CREATED":
        return {
            "Status": "V20_1_V17_8_3_INTEGRATION_BLOCKED",
            "Reason": "V17.8.3 paper position was not created",
            "V17.8.3 Paper Position": position_result,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_3_INTEGRATION_COMPLETE",
        "V17.8.2 Paper Fill": paper_fill_result,
        "V17.8.3 Paper Position": position_result,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }
"""
JKJ AI Trader
V20.1 -> V17.8.2 Paper Fill Integration

Purpose:
    Convert a successful V20.1 -> V17.8.1 paper order
    into the existing V17.8.2 full paper fill engine.

Safety boundary:
    - PAPER EXECUTION ONLY
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

from nifty_option_v17_8_paper_fill_engine import (
    simulate_paper_fill,
)


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_2_INTEGRATION_BLOCKED",
        "Reason": reason,
        "V17.8.2 Paper Fill": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v17_8_2(
    v20_1_v17_8_result,
    fill_price=None,
):
    """
    Convert a successful V20.1 -> V17.8.1 paper order
    into a V17.8.2 full paper fill.

    This function does not generate priority, allocation,
    quantity, or contract identity.
    """

    if not isinstance(v20_1_v17_8_result, dict):
        return _blocked(
            "V20.1 -> V17.8 result must be a dictionary"
        )

    if (
        v20_1_v17_8_result.get("Status")
        != "V20_1_V17_8_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8 integration is not complete"
        )

    if v20_1_v17_8_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution must remain enabled"
        )

    if v20_1_v17_8_result.get("Broker Communication") is True:
        return _blocked(
            "Broker communication must remain disabled"
        )

    if v20_1_v17_8_result.get("Order Placement Permitted") is True:
        return _blocked(
            "Live order placement must remain disabled"
        )

    if v20_1_v17_8_result.get("Capital Reassignment") is True:
        return _blocked(
            "Capital reassignment is not permitted"
        )

    if v20_1_v17_8_result.get("Automatic Ranking") is True:
        return _blocked(
            "Automatic ranking is not permitted"
        )

    if (
        v20_1_v17_8_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain Decision/Risk layer"
        )

    paper_order_result = v20_1_v17_8_result.get(
        "V17.8.1 Paper Order"
    )

    if not isinstance(paper_order_result, dict):
        return _blocked(
            "V17.8.1 paper order result is missing"
        )

    if paper_order_result.get("Status") != "PAPER_ORDER_ACCEPTED":
        return _blocked(
            "V17.8.1 paper order is not accepted"
        )

    paper_fill_result = simulate_paper_fill(
        paper_order_result,
        fill_price=fill_price,
    )

    if paper_fill_result.get("Status") != "PAPER_FILL_COMPLETE":
        return {
            "Status": "V20_1_V17_8_2_INTEGRATION_BLOCKED",
            "Reason": "V17.8.2 paper fill was not completed",
            "V17.8.2 Paper Fill": paper_fill_result,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_2_INTEGRATION_COMPLETE",
        "V17.8.1 Paper Order": paper_order_result,
        "V17.8.2 Paper Fill": paper_fill_result,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }
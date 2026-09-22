"""
JKJ AI Trader
V20.1 -> V17.8.5 Paper Fill -> V15 Entry Mapping Integration

Purpose:
    Convert a successful V20.1 -> V17.8.2 paper fill into the
    existing V17.8.5 V15 entry mapping boundary.

    V15 qualification remains authoritative for:
    - Stop Loss
    - Targets
    - Risk/Reward
    - Entry qualification

Safety boundary:
    - MAPPING ONLY
    - NO PAPER TRADE OPENING
    - NO V15 MODIFICATION
    - NO V11 MODIFICATION
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

from nifty_option_v17_8_paper_fill_v15_entry_bridge import (
    map_paper_fill_to_v15_entry,
)


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_5_INTEGRATION_BLOCKED",
        "Reason": reason,
        "V15 Entry Mapping": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v17_8_5(
    v20_1_v17_8_2_result,
    v15_qualification,
    trade_id,
    entry_time=None,
):
    """
    Convert a successful V20.1 -> V17.8.2 paper fill into
    the existing V17.8.5 V15 entry mapping.

    V15 qualification remains authoritative for decision/risk
    fields. This function does not open a V15/V11 paper trade.
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

    mapping_result = map_paper_fill_to_v15_entry(
        paper_fill_result,
        v15_qualification,
        trade_id,
        entry_time=entry_time,
    )

    if mapping_result.get("Status") != (
        "V15_ENTRY_MAPPING_COMPLETE"
    ):
        return {
            "Status": "V20_1_V17_8_5_INTEGRATION_BLOCKED",
            "Reason": "V17.8.5 V15 entry mapping was not completed",
            "V17.8.5 Result": mapping_result,
            "V15 Entry Mapping": None,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_5_INTEGRATION_COMPLETE",
        "V17.8.2 Paper Fill": paper_fill_result,
        "V17.8.5 Result": mapping_result,
        "V15 Entry Mapping": mapping_result["V15 Entry Mapping"],
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }
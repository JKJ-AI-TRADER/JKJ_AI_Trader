"""
JKJ AI Trader
V20.1 -> V17.8.1 Paper Execution Integration

Purpose:
    Convert a successful V20.1 -> V17.7 reconciliation
    into the existing V17.8.1 paper execution request.

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

from nifty_option_v17_8_paper_order_simulator import (
    simulate_paper_order,
)


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_INTEGRATION_BLOCKED",
        "Reason": reason,
        "Paper Order": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v17_8(
    v20_1_v17_7_result,
):
    """
    Convert a successful V20.1 -> V17.7 reconciliation
    into a V17.8.1 paper order.

    This function does not generate allocation policy,
    priority, quantity, or contract identity.
    """

    if not isinstance(v20_1_v17_7_result, dict):
        return _blocked(
            "V20.1 -> V17.7 result must be a dictionary"
        )

    if (
        v20_1_v17_7_result.get("Status")
        != "V20_1_V17_7_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.7 integration is not complete"
        )

    reconciliation = v20_1_v17_7_result.get(
        "V17.7 Reconciliation"
    )

    if not isinstance(reconciliation, dict):
        return _blocked(
            "V17.7 reconciliation result is missing"
        )

    if (
        reconciliation.get("Status")
        != "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
    ):
        return _blocked(
            "V17.7 reconciliation is not complete"
        )

    if reconciliation.get("Capital Reassignment") is True:
        return _blocked(
            "Capital reassignment is not permitted"
        )

    if reconciliation.get("Automatic Ranking") is True:
        return _blocked(
            "Automatic ranking is not permitted"
        )

    if reconciliation.get("Priority Source") != (
        "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain Decision/Risk layer"
        )

    if reconciliation.get("Order Placement Permitted") is True:
        return _blocked(
            "Live order placement must remain disabled"
        )

    reconciliations = reconciliation.get(
        "Reconciliations"
    )

    if not isinstance(reconciliations, list):
        return _blocked(
            "V17.7 reconciliation list is missing"
        )

    successful = [
        item
        for item in reconciliations
        if isinstance(item, dict)
        and item.get("Status") == "RECONCILIATION_COMPLETE"
    ]

    if len(successful) != 1:
        return _blocked(
            "Integration requires exactly one successful "
            "reconciled candidate"
        )

    item = successful[0]

    required_fields = [
        "Candidate",
        "Priority",
        "Allocated Capital",
        "Entry Price",
        "Lot Size",
        "Reconciled Quantity",
        "Estimated Capital Required",
        "Trading Symbol",
        "Instrument Token",
        "Contract Identity Valid",
    ]

    for field in required_fields:
        if field not in item:
            return _blocked(
                f"Missing V17.7 reconciliation field: {field}"
            )

    if item["Contract Identity Valid"] is not True:
        return _blocked(
            "V17.7 contract identity is not valid"
        )

    quantity = item["Reconciled Quantity"]
    lot_size = item["Lot Size"]

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return _blocked(
            "V17.7 reconciled quantity must be a positive integer"
        )

    if (
        not isinstance(lot_size, int)
        or isinstance(lot_size, bool)
        or lot_size <= 0
    ):
        return _blocked(
            "V17.7 lot size must be a positive integer"
        )

    if quantity % lot_size != 0:
        return _blocked(
            "V17.7 quantity must be a multiple of lot size"
        )

    execution_request = {
        "Candidate": item["Candidate"],
        "Priority": item["Priority"],
        "Priority Source": "DECISION_RISK_LAYER",
        "Trading Symbol": item["Trading Symbol"],
        "Instrument Token": item["Instrument Token"],
        "Transaction Type": "BUY",
        "Order Type": "MARKET",
        "Product": "MIS",
        "Quantity": quantity,
        "Lot Size": lot_size,
        "Entry Price Reference": item["Entry Price"],
        "Allocated Capital": item["Allocated Capital"],
        "Required Capital": item["Estimated Capital Required"],
        "Contract Valid": True,
        "Execution Ready": True,
        "Order Placement Permitted": False,
        "Broker Communication": False,
    }

    execution_request_result = {
        "Status": "EXECUTION_REQUEST_SPECIFIED",
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Execution Request": execution_request,
    }

    paper_order_result = simulate_paper_order(
        execution_request_result
    )

    if paper_order_result.get("Status") != (
        "PAPER_ORDER_ACCEPTED"
    ):
        return {
            "Status": "V20_1_V17_8_INTEGRATION_BLOCKED",
            "Reason": "V17.8.1 paper order was not accepted",
            "V17.8.1 Result": paper_order_result,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_INTEGRATION_COMPLETE",
        "Execution Request": execution_request_result,
        "V17.8.1 Paper Order": paper_order_result,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

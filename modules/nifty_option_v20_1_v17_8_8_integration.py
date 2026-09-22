"""
JKJ AI Trader
V20.1 -> V17.8.8 Integration

Purpose:
    Connect the successful V20.1 -> V17.8.7 controlled
    V15 paper-trade handoff to the existing V17.8.8
    lifecycle boundary.

V17.8.8 remains validation-only.

This module does NOT:
    - generate priority
    - generate requested allocation
    - rank candidates
    - reassign capital
    - process lifecycle actions
    - process exits
    - close positions
    - communicate with Zerodha
    - place live orders
    - modify V15.4
    - modify V11
    - modify main.py

Wisdom Before Wealth.
"""

try:
    from nifty_option_v17_8_lifecycle_boundary import (
        validate_lifecycle_boundary,
    )
except ModuleNotFoundError:
    from modules.nifty_option_v17_8_lifecycle_boundary import (
        validate_lifecycle_boundary,
    )


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_8_INTEGRATION_BLOCKED",
        "Reason": reason,
        "Lifecycle Ready": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v17_8_8(v20_1_v17_8_7_result):
    """
    Integrate the successful V20.1 -> V17.8.7
    paper-trade handoff into the V17.8.8
    controlled lifecycle boundary.

    V17.8.8 remains validation-only.
    """

    if not isinstance(v20_1_v17_8_7_result, dict):
        return _blocked(
            "V20.1 -> V17.8.7 result must be a dictionary"
        )

    if (
        v20_1_v17_8_7_result.get("Status")
        != "V20_1_V17_8_7_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8.7 integration is not complete"
        )

    # Preserve all upstream safeguards.
    if v20_1_v17_8_7_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution flag must remain True"
        )

    if (
        v20_1_v17_8_7_result.get("Broker Communication")
        is not False
    ):
        return _blocked(
            "Broker communication must remain False"
        )

    if (
        v20_1_v17_8_7_result.get("Order Placement Permitted")
        is not False
    ):
        return _blocked(
            "Order placement must remain False"
        )

    if (
        v20_1_v17_8_7_result.get("Capital Reassignment")
        is not False
    ):
        return _blocked(
            "Capital reassignment must remain False"
        )

    if (
        v20_1_v17_8_7_result.get("Automatic Ranking")
        is not False
    ):
        return _blocked(
            "Automatic ranking must remain False"
        )

    if (
        v20_1_v17_8_7_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain DECISION_RISK_LAYER"
        )

    v17_8_7_result = v20_1_v17_8_7_result.get(
        "V17.8.7 Result"
    )

    if not isinstance(v17_8_7_result, dict):
        return _blocked(
            "V17.8.7 handoff result is missing"
        )

    if (
        v17_8_7_result.get("Status")
        != "V17_8_7_PAPER_HANDOFF_COMPLETE"
    ):
        return _blocked(
            "V17.8.7 paper handoff is not complete"
        )

    if v17_8_7_result.get("Paper Execution") is not True:
        return _blocked(
            "V17.8.7 paper execution flag must remain True"
        )

    if (
        v17_8_7_result.get("Broker Communication")
        is not False
    ):
        return _blocked(
            "V17.8.7 broker communication must remain False"
        )

    if (
        v17_8_7_result.get("Order Placement Permitted")
        is not False
    ):
        return _blocked(
            "V17.8.7 order placement must remain False"
        )

    if (
        v17_8_7_result.get("Capital Reassignment")
        is not False
    ):
        return _blocked(
            "V17.8.7 capital reassignment must remain False"
        )

    if (
        v17_8_7_result.get("Automatic Ranking")
        is not False
    ):
        return _blocked(
            "V17.8.7 automatic ranking must remain False"
        )

    if (
        v17_8_7_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "V17.8.7 priority source must remain DECISION_RISK_LAYER"
        )

    # V17.8.8 is the authoritative lifecycle boundary.
    lifecycle_result = validate_lifecycle_boundary(
        v17_8_7_result
    )

    if (
        lifecycle_result.get("Status")
        != "V17_8_8_LIFECYCLE_BOUNDARY_VALIDATED"
    ):
        return {
            "Status": "V20_1_V17_8_8_INTEGRATION_BLOCKED",
            "Reason": lifecycle_result.get(
                "Reason",
                "V17.8.8 lifecycle boundary validation failed",
            ),
            "V17.8.8 Result": lifecycle_result,
            "Lifecycle Ready": False,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Automatic Ranking": False,
            "Capital Reassignment": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_8_INTEGRATION_COMPLETE",
        "V20.1 -> V17.8.7 Result": v20_1_v17_8_7_result,
        "V17.8.7 Result": v17_8_7_result,
        "V17.8.8 Result": lifecycle_result,
        "Lifecycle Ready": True,
        "Lifecycle Owner": "V15.4 / V11",
        "Trade ID": lifecycle_result["Trade ID"],
        "Symbol": lifecycle_result["Symbol"],
        "Instrument Type": lifecycle_result["Instrument Type"],
        "Current Quantity": lifecycle_result["Current Quantity"],
        "V15.4 Lifecycle Action Permitted": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }
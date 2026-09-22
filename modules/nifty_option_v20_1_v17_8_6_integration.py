"""
JKJ AI Trader
V20.1 -> V17.8.6 V15 Entry Boundary Integration

Purpose:
    Validate the V20.1 -> V17.8.5 mapped entry at the
    existing V17.8.6 V15 entry boundary.

Safety boundary:
    - VALIDATION ONLY
    - NO V15 CALL
    - NO V11 CALL
    - NO PAPER TRADE OPENING
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

from nifty_option_v17_8_v15_entry_boundary import (
    validate_v15_entry_boundary,
)


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_6_INTEGRATION_BLOCKED",
        "Reason": reason,
        "V15 Entry Boundary": None,
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


def integrate_v20_1_to_v17_8_6(
    v20_1_v17_8_5_result,
):
    """
    Validate the successful V20.1 -> V17.8.5 mapped entry
    through the existing V17.8.6 validation-only boundary.

    This function does not call V15/V11 and does not open
    a paper trade.
    """

    if not isinstance(v20_1_v17_8_5_result, dict):
        return _blocked(
            "V20.1 -> V17.8.5 result must be a dictionary"
        )

    if (
        v20_1_v17_8_5_result.get("Status")
        != "V20_1_V17_8_5_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8.5 integration is not complete"
        )

    if v20_1_v17_8_5_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper Execution flag must remain True"
        )

    if (
        v20_1_v17_8_5_result.get("Broker Communication")
        is not False
    ):
        return _blocked(
            "Broker Communication must remain False"
        )

    if (
        v20_1_v17_8_5_result.get("Order Placement Permitted")
        is not False
    ):
        return _blocked(
            "Order Placement Permitted must remain False"
        )

    if (
        v20_1_v17_8_5_result.get("Capital Reassignment")
        is not False
    ):
        return _blocked(
            "Capital Reassignment must remain False"
        )

    if (
        v20_1_v17_8_5_result.get("Automatic Ranking")
        is not False
    ):
        return _blocked(
            "Automatic Ranking must remain False"
        )

    if (
        v20_1_v17_8_5_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain Decision/Risk layer"
        )

    mapping_result = v20_1_v17_8_5_result.get(
        "V17.8.5 Result"
    )

    if not isinstance(mapping_result, dict):
        return _blocked(
            "V17.8.5 mapping result is missing"
        )

    if mapping_result.get("Status") != "V15_ENTRY_MAPPING_COMPLETE":
        return _blocked(
            "V17.8.5 entry mapping is not complete"
        )

    mapped_entry = mapping_result.get(
        "V15 Entry Mapping"
    )

    if not isinstance(mapped_entry, dict):
        return _blocked(
            "V17.8.5 mapped entry is missing"
        )

    # V17.8.5 uses descriptive field names.
    # V17.8.6 has its established boundary field names.
    # Create a validation-only adapter copy.
    boundary_entry = dict(mapped_entry)

    boundary_entry["Target1"] = mapped_entry["Target 1"]
    boundary_entry["Target2"] = mapped_entry["Target 2"]
    boundary_entry["Target3"] = mapped_entry["Target 3"]

    boundary_entry["RR1"] = mapped_entry["Risk Reward 1"]
    boundary_entry["RR2"] = mapped_entry["Risk Reward 2"]
    boundary_entry["RR3"] = mapped_entry["Risk Reward 3"]

    boundary_result = validate_v15_entry_boundary(
        boundary_entry
    )

    if not isinstance(boundary_result, dict):
        return _blocked(
            "V17.8.6 boundary did not return a valid result"
        )

    if (
        boundary_result.get("Status")
        != "V15_ENTRY_BOUNDARY_VALIDATED"
    ):
        return {
            "Status": "V20_1_V17_8_6_INTEGRATION_BLOCKED",
            "Reason": boundary_result.get(
                "Reason",
                "V17.8.6 boundary validation failed",
            ),
            "V15 Entry Boundary": boundary_result,
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

    return {
        "Status": "V20_1_V17_8_6_INTEGRATION_COMPLETE",
        "V17.8.5 Result": mapping_result,
        "V15 Entry Boundary": boundary_result,
        "V15 Entry Payload": boundary_result[
            "V15 Entry Payload"
        ],
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
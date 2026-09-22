"""
JKJ AI Trader
V20.1 -> V17.8.7 Controlled V15 Paper-Trade Handoff

Purpose:
    Connect the validated V20.1 -> V17.8.6 entry boundary
    to the existing V17.8.7 controlled V15 paper-trade handoff.

Safety boundary:
    - PAPER TRADING ONLY
    - V15/V11 HANDOFF ALLOWED ONLY THROUGH V17.8.7
    - NO LIVE BROKER COMMUNICATION
    - NO LIVE ORDER PLACEMENT
    - NO PRIORITY GENERATION
    - NO REQUESTED ALLOCATION GENERATION
    - NO AUTOMATIC RANKING
    - NO CAPITAL REASSIGNMENT
    - NO MAIN.PY MODIFICATION

V14.5 EVALUATED qualification remains authoritative.

Wisdom Before Wealth.
"""

try:
    from nifty_option_v17_8_v15_paper_handoff import (
        handoff_to_v15_paper_trade,
    )
except ModuleNotFoundError:
    from modules.nifty_option_v17_8_v15_paper_handoff import (
        handoff_to_v15_paper_trade,
    )


def _blocked(reason):
    return {
        "Status": "V20_1_V17_8_7_INTEGRATION_BLOCKED",
        "Reason": reason,
        "V17.8.7 Result": None,
        "V15 Handoff": False,
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


def integrate_v20_1_to_v17_8_7(
    v20_1_v17_8_6_result,
    exit_qualification,
    entry_time=None,
):
    """
    Convert a validated V20.1 -> V17.8.6 entry boundary
    into the existing V17.8.7 controlled V15 paper-trade handoff.

    V14.5 EVALUATED qualification remains authoritative.
    """

    if not isinstance(v20_1_v17_8_6_result, dict):
        return _blocked(
            "V20.1 -> V17.8.6 result must be a dictionary"
        )

    if (
        v20_1_v17_8_6_result.get("Status")
        != "V20_1_V17_8_6_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8.6 integration is not complete"
        )

    if v20_1_v17_8_6_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper Execution flag must remain True"
        )

    if (
        v20_1_v17_8_6_result.get("Broker Communication")
        is not False
    ):
        return _blocked(
            "Broker Communication must remain False"
        )

    if (
        v20_1_v17_8_6_result.get("Order Placement Permitted")
        is not False
    ):
        return _blocked(
            "Order Placement Permitted must remain False"
        )

    if (
        v20_1_v17_8_6_result.get("Capital Reassignment")
        is not False
    ):
        return _blocked(
            "Capital Reassignment must remain False"
        )

    if (
        v20_1_v17_8_6_result.get("Automatic Ranking")
        is not False
    ):
        return _blocked(
            "Automatic Ranking must remain False"
        )

    if (
        v20_1_v17_8_6_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain Decision/Risk layer"
        )

    boundary_result = v20_1_v17_8_6_result.get(
        "V15 Entry Boundary"
    )

    if not isinstance(boundary_result, dict):
        return _blocked(
            "V17.8.6 boundary result is missing"
        )

    if (
        boundary_result.get("Status")
        != "V15_ENTRY_BOUNDARY_VALIDATED"
    ):
        return _blocked(
            "V17.8.6 entry boundary is not validated"
        )

    v17_8_5_result = v20_1_v17_8_6_result.get(
        "V17.8.5 Result"
    )

    if not isinstance(v17_8_5_result, dict):
        return _blocked(
            "V17.8.5 result is missing"
        )

    if v17_8_5_result.get("Status") != (
        "V15_ENTRY_MAPPING_COMPLETE"
    ):
        return _blocked(
            "V17.8.5 entry mapping is not complete"
        )

    mapped_entry = v17_8_5_result.get(
        "V15 Entry Mapping"
    )

    if not isinstance(mapped_entry, dict):
        return _blocked(
            "V17.8.5 mapped entry is missing"
        )

    mapped_entry = v17_8_5_result.get(
        "V15 Entry Mapping"
    )

    if not isinstance(mapped_entry, dict):
        return _blocked(
            "V17.8.5 mapped entry is missing"
        )

    if not isinstance(v17_8_5_result, dict):
        return _blocked(
            "V17.8.5 result is missing"
        )

    if v17_8_5_result.get("Status") != (
        "V15_ENTRY_MAPPING_COMPLETE"
    ):
        return _blocked(
            "V17.8.5 entry mapping is not complete"
        )

    mapped_entry = v17_8_5_result.get(
        "V15 Entry Mapping"
    )

    if not isinstance(mapped_entry, dict):
        return _blocked(
            "V15 entry payload is missing"
        )
    
    # V17.8.5 uses descriptive field names.
    # V17.8.7/V17.8.6 use the established boundary names.
    # Create a validation-only adapter copy.
    mapped_entry = dict(mapped_entry)

    mapped_entry["Target1"] = mapped_entry["Target 1"]
    mapped_entry["Target2"] = mapped_entry["Target 2"]
    mapped_entry["Target3"] = mapped_entry["Target 3"]

    mapped_entry["RR1"] = mapped_entry["Risk Reward 1"]
    mapped_entry["RR2"] = mapped_entry["Risk Reward 2"]
    mapped_entry["RR3"] = mapped_entry["Risk Reward 3"]
    if not isinstance(exit_qualification, dict):
        return _blocked(
            "V14.5 exit qualification must be a dictionary"
        )

    if exit_qualification.get("Status") != "EVALUATED":
        return _blocked(
            "V14.5 exit qualification must have Status EVALUATED"
        )

    handoff_result = handoff_to_v15_paper_trade(
        mapped_entry,
        exit_qualification,
        entry_time=entry_time,
    )

    if not isinstance(handoff_result, dict):
        return _blocked(
            "V17.8.7 handoff did not return a valid result"
        )

    if (
        handoff_result.get("Status")
        != "V17_8_7_PAPER_HANDOFF_COMPLETE"
    ):
        return {
            "Status": "V20_1_V17_8_7_INTEGRATION_BLOCKED",
            "Reason": handoff_result.get(
                "Reason",
                "V17.8.7 paper handoff was not completed",
            ),
            "V17.8.7 Result": handoff_result,
            "V15 Handoff": False,
            "V15 Call Permitted": handoff_result.get(
                "V15 Call Permitted",
                False,
            ),
            "V11 Call Permitted": handoff_result.get(
                "V11 Call Permitted",
                False,
            ),
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Capital Reassignment": False,
            "Automatic Ranking": False,
            "Priority Source": "DECISION_RISK_LAYER",
            "Wisdom Before Wealth": True,
        }

    return {
        "Status": "V20_1_V17_8_7_INTEGRATION_COMPLETE",
        "V17.8.6 Result": v20_1_v17_8_6_result,
        "V17.8.7 Result": handoff_result,
        "Trade": handoff_result.get("Trade"),
        "Paper Trade Qualification": handoff_result.get(
            "Paper Trade Qualification"
        ),
        "Entry Request": handoff_result.get(
            "Entry Request"
        ),
        "Qualified Entry Price": handoff_result.get(
            "Qualified Entry Price"
        ),
        "Paper Fill Price": handoff_result.get(
            "Paper Fill Price"
        ),
        "Quantity": handoff_result.get("Quantity"),
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

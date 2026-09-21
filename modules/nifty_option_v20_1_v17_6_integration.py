"""
JKJ AI Trader V20.1 -> V17.6 Integration

Purpose:
    Convert already-qualified V20.1 capital-allocation candidates
    into the exact candidate structure required by V17.6.5.

This module does NOT:
    - generate Priority
    - generate Requested Allocation
    - rank candidates
    - calculate quantity
    - modify capital policy
    - place orders
    - communicate with Zerodha
    - modify V20.1
    - modify V17.6.5
    - modify main.py

Wisdom Before Wealth.
"""

from nifty_option_v17_6_policy_allocation import (
    allocate_with_policy,
)


def integrate_v20_1_to_v17_6(
    v20_1_results,
    usable_capital,
    max_positions,
    max_capital_per_candidate,
    minimum_candidate_allocation,
):
    """
    Convert qualified V20.1 results into V17.6.5 candidates
    and pass them to the existing policy allocation engine.
    """

    if not isinstance(v20_1_results, list):
        return {
            "Status": "V20_1_V17_6_INTEGRATION_BLOCKED",
            "Reason": "V20.1 results must be a list.",
            "Wisdom Before Wealth": True,
        }

    candidates = []

    for result in v20_1_results:

        if not isinstance(result, dict):
            return {
                "Status": "V20_1_V17_6_INTEGRATION_BLOCKED",
                "Reason": "Each V20.1 result must be a dictionary.",
                "Wisdom Before Wealth": True,
            }

        if result.get("Status") != "CAPITAL_ALLOCATION_QUALIFIED":
            return {
                "Status": "V20_1_V17_6_INTEGRATION_BLOCKED",
                "Reason": "All V20.1 candidates must be CAPITAL_ALLOCATION_QUALIFIED.",
                "Wisdom Before Wealth": True,
            }

        if result.get("Capital Allocation Eligible") is not True:
            return {
                "Status": "V20_1_V17_6_INTEGRATION_BLOCKED",
                "Reason": "V20.1 candidate is not eligible for capital allocation.",
                "Wisdom Before Wealth": True,
            }

        if result.get("Priority Source") != "DECISION_RISK_LAYER":
            return {
                "Status": "V20_1_V17_6_INTEGRATION_BLOCKED",
                "Reason": "Invalid Priority Source.",
                "Wisdom Before Wealth": True,
            }

        candidates.append({
            "Candidate": result["Trading Symbol"],
            "Priority": result["Priority"],
            "Requested Allocation": result["Requested Allocation"],
        })

    if not candidates:
        return {
            "Status": "V20_1_V17_6_INTEGRATION_BLOCKED",
            "Reason": "No qualified V20.1 candidates supplied.",
            "Wisdom Before Wealth": True,
        }

    allocation_result = allocate_with_policy(
        usable_capital=usable_capital,
        candidates=candidates,
        max_positions=max_positions,
        max_capital_per_candidate=max_capital_per_candidate,
        minimum_candidate_allocation=minimum_candidate_allocation,
    )

    return {
        "Status": "V20_1_V17_6_INTEGRATION_COMPLETE",
        "V20.1 Candidates": v20_1_results,
        "V17.6 Candidates": candidates,
        "Policy Allocation Result": allocation_result,
        "Priority Source": "DECISION_RISK_LAYER",
        "Automatic Ranking": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }

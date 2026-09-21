"""
JKJ AI Trader V20.1 -> V17.6 -> V17.7 Integration

Purpose:
    Validate the complete controlled handoff from a qualified V20.1
    candidate through V17.6.5 policy allocation into V17.7.3
    quantity and contract reconciliation.

This module does NOT:
    - generate Priority
    - generate Requested Allocation
    - rank candidates
    - change capital allocation policy
    - calculate quantities itself
    - place orders
    - communicate with Zerodha
    - modify V20.1
    - modify V17.6
    - modify V17.7
    - modify main.py

Wisdom Before Wealth.
"""

from nifty_option_v20_1_v17_6_integration import (
    integrate_v20_1_to_v17_6,
)

from nifty_option_v17_7_multi_candidate_quantity_reconciliation import (
    reconcile_multi_candidate_quantities,
)


def integrate_v20_1_to_v17_7(
    v20_1_results,
    candidate_market_data,
    usable_capital,
    max_positions,
    max_capital_per_candidate,
    minimum_candidate_allocation,
):
    """
    Execute the controlled V20.1 -> V17.6 -> V17.7 handoff.
    """

    # ---------------------------------------------------------
    # 1. V20.1 -> V17.6
    # ---------------------------------------------------------

    v20_to_v17_6 = integrate_v20_1_to_v17_6(
        v20_1_results=v20_1_results,
        usable_capital=usable_capital,
        max_positions=max_positions,
        max_capital_per_candidate=max_capital_per_candidate,
        minimum_candidate_allocation=minimum_candidate_allocation,
    )

    if (
        v20_to_v17_6.get("Status")
        != "V20_1_V17_6_INTEGRATION_COMPLETE"
    ):
        return {
            "Status": "V20_1_V17_7_INTEGRATION_BLOCKED",
            "Stage": "V20.1_TO_V17.6",
            "Reason": v20_to_v17_6.get(
                "Reason",
                "V20.1 to V17.6 integration failed.",
            ),
            "V20.1 -> V17.6": v20_to_v17_6,
            "Wisdom Before Wealth": True,
        }

    # ---------------------------------------------------------
    # 2. V17.6 -> V17.7.3
    # ---------------------------------------------------------

    allocation_result = v20_to_v17_6[
        "Policy Allocation Result"
    ]

    reconciliation_result = (
        reconcile_multi_candidate_quantities(
            allocation_result=allocation_result,
            candidate_market_data=candidate_market_data,
        )
    )

    if (
        reconciliation_result.get("Status")
        != "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
    ):
        return {
            "Status": "V20_1_V17_7_INTEGRATION_BLOCKED",
            "Stage": "V17.7",
            "Reason": reconciliation_result.get(
                "Reason",
                "V17.7 reconciliation failed.",
            ),
            "V20.1 -> V17.6": v20_to_v17_6,
            "V17.7 Reconciliation": reconciliation_result,
            "Wisdom Before Wealth": True,
        }

    # ---------------------------------------------------------
    # 3. Complete controlled handoff
    # ---------------------------------------------------------

    return {
        "Status": "V20_1_V17_7_INTEGRATION_COMPLETE",
        "V20.1 -> V17.6": v20_to_v17_6,
        "V17.7 Reconciliation": reconciliation_result,
        "Priority Source": "DECISION_RISK_LAYER",
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Order Placement Permitted": False,
        "Broker Communication": False,
        "Wisdom Before Wealth": True,
    }

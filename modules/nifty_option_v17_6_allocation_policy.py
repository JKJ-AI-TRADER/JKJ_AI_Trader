"""
JKJ AI Trader
V17.6.4 — Allocation Policy & Priority Validation

Purpose:
    Validate the rules supplied to the capital allocation engine.

Important:
    This module does NOT:
    - rank candidates
    - create an opportunity score
    - allocate capital
    - place orders
    - connect to Zerodha
    - modify V13/V14/V15/V17.5
    - modify main.py

The priority supplied here must come from an earlier
Decision/Risk layer.

Wisdom Before Wealth.
"""


def validate_allocation_policy(
    max_positions,
    max_capital_per_candidate,
    minimum_candidate_allocation,
):
    """
    Validate JKJ capital allocation policy parameters.
    """

    # ---------------------------------------------------------
    # 1. Maximum positions
    # ---------------------------------------------------------

    if not isinstance(max_positions, int):
        return _blocked(
            "Maximum positions must be an integer"
        )

    if max_positions <= 0:
        return _blocked(
            "Maximum positions must be greater than zero"
        )

    # ---------------------------------------------------------
    # 2. Maximum capital per candidate
    # ---------------------------------------------------------

    if not isinstance(
        max_capital_per_candidate,
        (int, float)
    ):
        return _blocked(
            "Maximum capital per candidate must be numeric"
        )

    if max_capital_per_candidate <= 0:
        return _blocked(
            "Maximum capital per candidate must be greater than zero"
        )

    # ---------------------------------------------------------
    # 3. Minimum candidate allocation
    # ---------------------------------------------------------

    if not isinstance(
        minimum_candidate_allocation,
        (int, float)
    ):
        return _blocked(
            "Minimum candidate allocation must be numeric"
        )

    if minimum_candidate_allocation <= 0:
        return _blocked(
            "Minimum candidate allocation must be greater than zero"
        )

    # ---------------------------------------------------------
    # 4. Minimum cannot exceed maximum
    # ---------------------------------------------------------

    if (
        minimum_candidate_allocation
        > max_capital_per_candidate
    ):
        return _blocked(
            "Minimum candidate allocation cannot exceed "
            "maximum candidate allocation"
        )

    # ---------------------------------------------------------
    # 5. Policy validated
    # ---------------------------------------------------------

    return {
        "Status": "ALLOCATION_POLICY_VALIDATED",

        "Maximum Positions": max_positions,

        "Maximum Capital Per Candidate":
            float(max_capital_per_candidate),

        "Minimum Candidate Allocation":
            float(minimum_candidate_allocation),

        "Priority Source":
            "DECISION_RISK_LAYER",

        "Automatic Ranking":
            False,

        "Capital Allocation Permitted":
            True,

        "Wisdom Before Wealth":
            True,
    }


def _blocked(reason):
    return {
        "Status": "ALLOCATION_POLICY_BLOCKED",

        "Automatic Ranking": False,

        "Capital Allocation Permitted": False,

        "Reason": reason,

        "Wisdom Before Wealth": True,
    }

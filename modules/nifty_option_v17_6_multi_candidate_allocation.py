"""
JKJ AI Trader
V17.6.3 — Multi-Candidate Capital Allocation

Purpose:
    Allocate usable trading capital across multiple already-qualified
    option candidates.

Important:
    This module does NOT:
    - qualify candidates
    - rank candidates
    - place orders
    - connect to Zerodha
    - change V13/V14/V15
    - change V17.5
    - modify main.py

Each candidate must already have an approved maximum allocation.

Core principle:

    Qualified candidates
            ↓
    Candidate allocation limits
            ↓
    Remaining usable capital
            ↓
    Capital allocation

Unused capital is acceptable.

Wisdom Before Wealth.
"""


def allocate_capital(
    usable_capital,
    candidates,
):
    """
    Allocate capital sequentially across qualified candidates.

    Parameters
    ----------
    usable_capital : float
        Total capital available for allocation.

    candidates : list of dict
        Each candidate must contain:
            Candidate
            Maximum Allocation

    Returns
    -------
    dict
        CAPITAL_ALLOCATED or CAPITAL_NOT_ALLOCATED
    """

    # ---------------------------------------------------------
    # 1. Validate usable capital
    # ---------------------------------------------------------

    if not isinstance(
        usable_capital,
        (int, float)
    ):
        return _blocked(
            "Usable capital must be numeric"
        )

    if usable_capital < 0:
        return _blocked(
            "Usable capital cannot be negative"
        )

    # ---------------------------------------------------------
    # 2. Validate candidate list
    # ---------------------------------------------------------

    if not isinstance(candidates, list):
        return _blocked(
            "Candidates must be provided as a list"
        )

    if len(candidates) == 0:
        return _blocked(
            "No candidates supplied"
        )

    # ---------------------------------------------------------
    # 3. Process candidates
    # ---------------------------------------------------------

    remaining_capital = float(
        usable_capital
    )

    allocations = []

    for candidate in candidates:

        if not isinstance(candidate, dict):
            return _blocked(
                "Invalid candidate data"
            )

        candidate_name = candidate.get(
            "Candidate"
        )

        maximum_allocation = candidate.get(
            "Maximum Allocation"
        )

        if candidate_name is None:
            return _blocked(
                "Candidate name is missing"
            )

        if not isinstance(
            maximum_allocation,
            (int, float)
        ):
            return _blocked(
                f"Maximum allocation is invalid for "
                f"{candidate_name}"
            )

        if maximum_allocation < 0:
            return _blocked(
                f"Maximum allocation cannot be negative "
                f"for {candidate_name}"
            )

        # -----------------------------------------------------
        # Allocate only from remaining capital
        # -----------------------------------------------------

        allocated_amount = min(
            float(maximum_allocation),
            remaining_capital,
        )

        remaining_capital -= allocated_amount

        allocations.append({
            "Candidate": candidate_name,
            "Maximum Allocation": float(
                maximum_allocation
            ),
            "Allocated Capital": float(
                allocated_amount
            ),
            "Allocation Status": (
                "ALLOCATED"
                if allocated_amount > 0
                else "NOT_ALLOCATED"
            ),
        })

    # ---------------------------------------------------------
    # 4. Calculate totals
    # ---------------------------------------------------------

    total_allocated = sum(
        item["Allocated Capital"]
        for item in allocations
    )

    # ---------------------------------------------------------
    # 5. Return allocation plan
    # ---------------------------------------------------------

    return {
        "Status": "CAPITAL_ALLOCATED",

        "Usable Capital": float(
            usable_capital
        ),

        "Total Allocated Capital": float(
            total_allocated
        ),

        "Remaining Capital": float(
            remaining_capital
        ),

        "Candidate Count": len(
            candidates
        ),

        "Allocations": allocations,

        "Capital Limit Respected": (
            total_allocated <= usable_capital
        ),

        "Wisdom Before Wealth": True,
    }


def _blocked(reason):
    """
    Safe allocation-blocked result.
    """

    return {
        "Status": "CAPITAL_NOT_ALLOCATED",

        "Usable Capital": 0.0,
        "Total Allocated Capital": 0.0,
        "Remaining Capital": 0.0,

        "Allocations": [],

        "Capital Limit Respected": True,

        "Reason": reason,

        "Wisdom Before Wealth": True,
    }
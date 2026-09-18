"""
JKJ AI Trader
V17.6.2 — Candidate Affordability Engine

Purpose:
    Determine the maximum quantity and estimated capital that can
    be allocated to one qualified option candidate.

Important:
    This module does NOT:
    - rank candidates
    - decide whether a trade is qualified
    - place orders
    - connect to Zerodha
    - override V13/V14/V15
    - modify V17.5
    - modify main.py

It calculates affordability only.

Wisdom Before Wealth.
"""


def evaluate_candidate_affordability(
    entry_price,
    lot_size,
    available_capital,
    max_candidate_allocation=None,
):
    """
    Calculate affordable quantity for one candidate.

    Parameters
    ----------
    entry_price : float
        Expected option entry price.

    lot_size : int
        Contract lot size.

    available_capital : float
        Capital currently available for this candidate.

    max_candidate_allocation : float, optional
        Maximum capital JKJ allows this candidate to use.

    Returns
    -------
    dict
        CANDIDATE_AFFORDABLE or CANDIDATE_NOT_AFFORDABLE
    """

    # ---------------------------------------------------------
    # 1. Validate entry price
    # ---------------------------------------------------------

    if not isinstance(entry_price, (int, float)):
        return _blocked(
            "Entry price must be numeric"
        )

    if entry_price <= 0:
        return _blocked(
            "Entry price must be greater than zero"
        )

    # ---------------------------------------------------------
    # 2. Validate lot size
    # ---------------------------------------------------------

    if not isinstance(lot_size, int):
        return _blocked(
            "Lot size must be an integer"
        )

    if lot_size <= 0:
        return _blocked(
            "Lot size must be greater than zero"
        )

    # ---------------------------------------------------------
    # 3. Validate available capital
    # ---------------------------------------------------------

    if not isinstance(
        available_capital,
        (int, float)
    ):
        return _blocked(
            "Available capital must be numeric"
        )

    if available_capital <= 0:
        return _blocked(
            "Available capital must be greater than zero"
        )

    # ---------------------------------------------------------
    # 4. Determine candidate budget
    # ---------------------------------------------------------

    candidate_budget = available_capital

    if max_candidate_allocation is not None:

        if not isinstance(
            max_candidate_allocation,
            (int, float)
        ):
            return _blocked(
                "Maximum candidate allocation must be numeric"
            )

        if max_candidate_allocation <= 0:
            return _blocked(
                "Maximum candidate allocation must be greater than zero"
            )

        candidate_budget = min(
            available_capital,
            max_candidate_allocation,
        )

    # ---------------------------------------------------------
    # 5. Calculate cost of one complete lot
    # ---------------------------------------------------------

    cost_per_lot = (
        float(entry_price) * lot_size
    )

    # ---------------------------------------------------------
    # 6. Determine affordable lots
    # ---------------------------------------------------------

    affordable_lots = int(
        candidate_budget // cost_per_lot
    )

    if affordable_lots <= 0:
        return _blocked(
            "Available capital cannot purchase one complete lot"
        )

    # ---------------------------------------------------------
    # 7. Calculate quantity and estimated capital
    # ---------------------------------------------------------

    affordable_quantity = (
        affordable_lots * lot_size
    )

    estimated_capital = (
        affordable_quantity
        * float(entry_price)
    )

    unused_capital = (
        candidate_budget
        - estimated_capital
    )

    # ---------------------------------------------------------
    # 8. Return affordability result
    # ---------------------------------------------------------

    return {
        "Status": "CANDIDATE_AFFORDABLE",

        "Entry Price": float(entry_price),
        "Lot Size": lot_size,

        "Available Capital": float(
            available_capital
        ),

        "Candidate Budget": float(
            candidate_budget
        ),

        "Affordable Lots": affordable_lots,

        "Maximum Affordable Quantity":
            affordable_quantity,

        "Estimated Capital Required":
            estimated_capital,

        "Unused Candidate Capital":
            unused_capital,

        "Affordability Confirmed": True,

        "Wisdom Before Wealth": True,
    }


def _blocked(reason):
    """
    Safe affordability-blocked result.
    """

    return {
        "Status": "CANDIDATE_NOT_AFFORDABLE",

        "Affordable Lots": 0,

        "Maximum Affordable Quantity": 0,

        "Estimated Capital Required": 0.0,

        "Unused Candidate Capital": 0.0,

        "Affordability Confirmed": False,

        "Reason": reason,

        "Wisdom Before Wealth": True,
    }
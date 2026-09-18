"""
JKJ AI Trader
V17.7.1 — Capital-to-Quantity Reconciliation

Purpose:
    Reconcile an already-approved V17.6 capital allocation
    with the actual affordable quantity for an option candidate.

Important:
    This module does NOT:
    - rank candidates
    - qualify trades
    - change the allocated capital
    - change entry, stop, or target decisions
    - place orders
    - connect to Zerodha
    - override V17.5
    - modify main.py

Wisdom Before Wealth.
"""


def reconcile_capital_to_quantity(
    allocated_capital,
    entry_price,
    lot_size,
):
    """
    Determine the valid quantity supported by allocated capital.

    Allocated capital is treated as a ceiling.

    A complete lot must be affordable. The quantity is always
    calculated in complete lots.

    Returns:
        RECONCILIATION_COMPLETE
        or
        RECONCILIATION_BLOCKED
    """

    # ---------------------------------------------------------
    # 1. Validate allocated capital
    # ---------------------------------------------------------

    if not isinstance(
        allocated_capital,
        (int, float)
    ):
        return _blocked(
            "Allocated capital must be numeric"
        )

    if allocated_capital <= 0:
        return _blocked(
            "Allocated capital must be greater than zero"
        )

    # ---------------------------------------------------------
    # 2. Validate entry price
    # ---------------------------------------------------------

    if not isinstance(
        entry_price,
        (int, float)
    ):
        return _blocked(
            "Entry price must be numeric"
        )

    if entry_price <= 0:
        return _blocked(
            "Entry price must be greater than zero"
        )

    # ---------------------------------------------------------
    # 3. Validate lot size
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
    # 4. Calculate complete-lot cost
    # ---------------------------------------------------------

    cost_per_lot = (
        float(entry_price) * lot_size
    )

    # ---------------------------------------------------------
    # 5. Determine affordable complete lots
    # ---------------------------------------------------------

    affordable_lots = int(
        float(allocated_capital)
        // cost_per_lot
    )

    if affordable_lots <= 0:
        return _blocked(
            "Allocated capital cannot purchase one complete lot"
        )

    # ---------------------------------------------------------
    # 6. Calculate quantity
    # ---------------------------------------------------------

    reconciled_quantity = (
        affordable_lots * lot_size
    )

    estimated_capital_required = (
        reconciled_quantity
        * float(entry_price)
    )

    unused_allocated_capital = (
        float(allocated_capital)
        - estimated_capital_required
    )

    # ---------------------------------------------------------
    # 7. Final reconciliation
    # ---------------------------------------------------------

    return {
        "Status": "RECONCILIATION_COMPLETE",

        "Allocated Capital":
            float(allocated_capital),

        "Entry Price":
            float(entry_price),

        "Lot Size":
            lot_size,

        "Cost Per Lot":
            cost_per_lot,

        "Reconciled Lots":
            affordable_lots,

        "Reconciled Quantity":
            reconciled_quantity,

        "Estimated Capital Required":
            estimated_capital_required,

        "Unused Allocated Capital":
            unused_allocated_capital,

        "Capital Ceiling Respected":
            estimated_capital_required
            <= float(allocated_capital),

        "Quantity Reconciled":
            True,

        "Wisdom Before Wealth":
            True,
    }


def _blocked(reason):
    """
    Safe reconciliation-blocked result.
    """

    return {
        "Status":
            "RECONCILIATION_BLOCKED",

        "Reconciled Lots":
            0,

        "Reconciled Quantity":
            0,

        "Estimated Capital Required":
            0.0,

        "Unused Allocated Capital":
            0.0,

        "Capital Ceiling Respected":
            True,

        "Quantity Reconciled":
            False,

        "Reason":
            reason,

        "Wisdom Before Wealth":
            True,
    }
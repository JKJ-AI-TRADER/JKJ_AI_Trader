"""
JKJ AI Trader
V17.6.1 — Capital Availability & Reserve Engine

Purpose:
    Determine the amount of capital JKJ may use for trading
    after protecting the configured capital reserve.

This module does NOT:
    - select trades
    - rank candidates
    - place orders
    - modify V13/V14/V15/V17
    - connect to Zerodha
    - modify main.py

Core principle:

    Available Capital
        -
    JKJ Capital Reserve
        =
    Usable Trading Capital

Wisdom Before Wealth.
"""


def evaluate_available_capital(
    available_funds,
    reserve_amount,
):
    """
    Calculate JKJ usable trading capital.

    Parameters
    ----------
    available_funds : float
        Funds currently available for trading.

    reserve_amount : float
        Capital that JKJ must keep untouched.

    Returns
    -------
    dict
        CAPITAL_AVAILABLE or CAPITAL_BLOCKED
    """

    # ---------------------------------------------------------
    # 1. Validate available funds
    # ---------------------------------------------------------

    if not isinstance(
        available_funds,
        (int, float)
    ):
        return _blocked(
            "Available funds must be numeric"
        )

    if available_funds < 0:
        return _blocked(
            "Available funds cannot be negative"
        )

    # ---------------------------------------------------------
    # 2. Validate reserve
    # ---------------------------------------------------------

    if not isinstance(
        reserve_amount,
        (int, float)
    ):
        return _blocked(
            "Reserve amount must be numeric"
        )

    if reserve_amount < 0:
        return _blocked(
            "Reserve amount cannot be negative"
        )

    # ---------------------------------------------------------
    # 3. Calculate usable capital
    # ---------------------------------------------------------

    usable_capital = (
        available_funds - reserve_amount
    )

    # ---------------------------------------------------------
    # 4. Reserve cannot exceed available funds
    # ---------------------------------------------------------

    if usable_capital < 0:
        return _blocked(
            "Capital reserve exceeds available funds"
        )

    # ---------------------------------------------------------
    # 5. Capital available
    # ---------------------------------------------------------

    return {
        "Status": "CAPITAL_AVAILABLE",

        "Available Funds": float(
            available_funds
        ),

        "JKJ Reserve": float(
            reserve_amount
        ),

        "Usable Trading Capital": float(
            usable_capital
        ),

        "Capital Reserve Protected": True,

        "Wisdom Before Wealth": True,
    }


def _blocked(reason):
    """
    Safe capital-blocked result.
    """

    return {
        "Status": "CAPITAL_BLOCKED",

        "Available Funds": None,
        "JKJ Reserve": None,
        "Usable Trading Capital": 0.0,

        "Capital Reserve Protected": True,

        "Reason": reason,

        "Wisdom Before Wealth": True,
    }
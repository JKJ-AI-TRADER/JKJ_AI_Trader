"""
JKJ AI Trader
V17.5 Zerodha Execution Eligibility & Contract Validation

Purpose:
    Validate whether a proposed option exit is eligible for
    eventual Zerodha execution.

Architecture:
    V17.1 creates the abstract target exit plan.
    V17.2 records execution state.
    V17.3 integrates target progression.
    V17.4 handles actual remaining quantity.
    V17.5 validates broker/exchange execution eligibility.

Important:
    This module does NOT:
    - connect to Zerodha
    - place orders
    - modify V11
    - modify V14
    - modify V15.5
    - modify V17.1
    - modify V17.2
    - modify V17.3
    - modify V17.4
    - modify main.py

For live option execution, quantity must be compatible
with the actual contract lot size.

Wisdom Before Wealth.
"""


def validate_execution_eligibility(
    contract,
    current_quantity,
    requested_quantity,
):
    """
    Validate an option exit against the supplied contract.

    Parameters
    ----------
    contract : dict
        Exact option contract information.

    current_quantity : int
        Actual current open position quantity.

    requested_quantity : int
        Quantity intended for the proposed exit.

    Returns
    -------
    dict
        EXECUTION_ELIGIBLE or EXECUTION_BLOCKED.
    """

    # ---------------------------------------------------------
    # 1. Validate contract
    # ---------------------------------------------------------

    if not isinstance(contract, dict):
        return _blocked(
            "Invalid contract data"
        )

    required_contract_fields = {
        "tradingsymbol",
        "instrument_token",
        "expiry",
        "strike",
        "instrument_type",
        "lot_size",
    }

    missing_fields = [
        field
        for field in required_contract_fields
        if contract.get(field) is None
    ]

    if missing_fields:
        return _blocked(
            "Missing contract fields: "
            + ", ".join(missing_fields)
        )

    # ---------------------------------------------------------
    # 2. Validate contract values
    # ---------------------------------------------------------

    try:
        instrument_token = int(
            contract["instrument_token"]
        )

        strike = float(
            contract["strike"]
        )

        lot_size = int(
            contract["lot_size"]
        )

    except (TypeError, ValueError):
        return _blocked(
            "Invalid contract numeric values"
        )

    if instrument_token <= 0:
        return _blocked(
            "Instrument token must be greater than zero"
        )

    if strike <= 0:
        return _blocked(
            "Strike must be greater than zero"
        )

    if lot_size <= 0:
        return _blocked(
            "Lot size must be greater than zero"
        )

    if contract["instrument_type"] not in {
        "CE",
        "PE",
    }:
        return _blocked(
            "Instrument type must be CE or PE"
        )

    # ---------------------------------------------------------
    # 3. Validate position quantities
    # ---------------------------------------------------------

    try:
        current_quantity = int(
            current_quantity
        )

        requested_quantity = int(
            requested_quantity
        )

    except (TypeError, ValueError):
        return _blocked(
            "Position quantities must be integers"
        )

    if current_quantity <= 0:
        return _blocked(
            "Current quantity must be greater than zero"
        )

    if requested_quantity <= 0:
        return _blocked(
            "Requested quantity must be greater than zero"
        )

    if requested_quantity > current_quantity:
        return _blocked(
            "Requested quantity cannot exceed current quantity"
        )

    # ---------------------------------------------------------
    # 4. Validate current position against lot size
    # ---------------------------------------------------------

    if current_quantity % lot_size != 0:
        return _blocked(
            "Current position quantity is not a valid "
            "multiple of the contract lot size"
        )

    # ---------------------------------------------------------
    # 5. Validate requested exit quantity
    # ---------------------------------------------------------

    if requested_quantity % lot_size != 0:
        return _blocked(
            "Requested quantity is not a valid "
            "multiple of the contract lot size"
        )

    # ---------------------------------------------------------
    # 6. Calculate remaining quantity
    # ---------------------------------------------------------

    remaining_quantity = (
        current_quantity - requested_quantity
    )

    # Remaining quantity must also remain exchange-valid.
    if remaining_quantity % lot_size != 0:
        return _blocked(
            "Remaining quantity is not a valid "
            "multiple of the contract lot size"
        )

    # ---------------------------------------------------------
    # 7. Execution eligibility confirmed
    # ---------------------------------------------------------

    return {
        "Status": "EXECUTION_ELIGIBLE",

        "Trading Symbol": contract["tradingsymbol"],
        "Instrument Token": instrument_token,
        "Expiry": contract["expiry"],
        "Strike": strike,
        "Option Type": contract["instrument_type"],
        "Lot Size": lot_size,

        "Current Quantity": current_quantity,
        "Requested Exit Quantity": requested_quantity,
        "Remaining Quantity": remaining_quantity,

        "Quantity Valid": True,
        "Contract Valid": True,

        "Order Placement Permitted": True,

        "Wisdom Before Wealth": True,
    }


def _blocked(reason):
    """
    Return a safe execution-blocked result.
    """

    return {
        "Status": "EXECUTION_BLOCKED",

        "Quantity Valid": False,
        "Contract Valid": False,

        "Order Placement Permitted": False,

        "Reason": reason,

        "Wisdom Before Wealth": True,
    }
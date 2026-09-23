"""
JKJ AI Trader
V17.5 Stage 3 — Execution Request Validation

Purpose:
    Validate a proposed Zerodha option exit request before any
    future execution layer is allowed to submit an order.

Important:
    This module does NOT:
    - place orders
    - modify positions
    - connect to Zerodha
    - modify V11/V14/V15/V17.1-V17.4
    - modify main.py

Wisdom Before Wealth.
"""


VALID_ORDER_TYPES = {
    "MARKET",
    "LIMIT",
    "SL",
}

VALID_PRODUCTS = {
    "MIS",
    "NRML",
}


def validate_execution_request(
    contract_validation,
    execution_eligibility,
    order_type,
    product,
    transaction_type="SELL",
):
    """
    Validate the complete proposed exit request.

    Returns:
        EXECUTION_READY
        or
        EXECUTION_BLOCKED
    """

    # ---------------------------------------------------------
    # 1. Validate previous safety gates
    # ---------------------------------------------------------

    if not isinstance(contract_validation, dict):
        return _blocked("Invalid contract validation data")

    if not isinstance(execution_eligibility, dict):
        return _blocked("Invalid execution eligibility data")

    if contract_validation.get("Status") != "CONTRACT_VALIDATED":
        return _blocked(
            "Zerodha contract validation has not passed"
        )

    if execution_eligibility.get("Status") != "EXECUTION_ELIGIBLE":
        return _blocked(
            "Execution eligibility has not passed"
        )

    # ---------------------------------------------------------
    # 2. Validate order type
    # ---------------------------------------------------------

    if order_type not in VALID_ORDER_TYPES:
        return _blocked(
            f"Unsupported order type: {order_type}"
        )

    # ---------------------------------------------------------
    # 3. Validate product
    # ---------------------------------------------------------

    if product not in VALID_PRODUCTS:
        return _blocked(
            f"Unsupported product type: {product}"
        )

    # ---------------------------------------------------------
    # 4. Validate transaction type
    # ---------------------------------------------------------

    if transaction_type != "SELL":
        return _blocked(
            "V17.5 exit request must be a SELL transaction"
        )

    # ---------------------------------------------------------
    # 5. Extract validated contract information
    # ---------------------------------------------------------

    trading_symbol = contract_validation.get(
        "Trading Symbol"
    )

    instrument_token = contract_validation.get(
        "Instrument Token"
    )

    expiry = contract_validation.get(
        "Expiry"
    )

    strike = contract_validation.get(
        "Strike"
    )

    option_type = contract_validation.get(
        "Option Type"
    )

    lot_size = contract_validation.get(
        "Lot Size"
    )

    # ---------------------------------------------------------
    # 6. Extract validated quantity information
    # ---------------------------------------------------------

    current_quantity = execution_eligibility.get(
        "Current Quantity"
    )

    requested_quantity = execution_eligibility.get(
        "Requested Exit Quantity"
    )

    remaining_quantity = execution_eligibility.get(
        "Remaining Quantity"
    )

    # ---------------------------------------------------------
    # 7. Final consistency checks
    # ---------------------------------------------------------

    if requested_quantity <= 0:
        return _blocked(
            "Requested exit quantity must be greater than zero"
        )

    if current_quantity <= 0:
        return _blocked(
            "Current position quantity must be greater than zero"
        )

    if requested_quantity > current_quantity:
        return _blocked(
            "Requested exit quantity exceeds current position"
        )

    if lot_size <= 0:
        return _blocked(
            "Invalid contract lot size"
        )

    if requested_quantity % lot_size != 0:
        return _blocked(
            "Requested exit quantity is not a valid "
            "multiple of the contract lot size"
        )

    if remaining_quantity % lot_size != 0:
        return _blocked(
            "Remaining quantity is not a valid "
            "multiple of the contract lot size"
        )

    # ---------------------------------------------------------
    # 8. Execution request is structurally ready
    # ---------------------------------------------------------

    return {
        "Status": "EXECUTION_READY",

        "Trading Symbol": trading_symbol,
        "Instrument Token": instrument_token,
        "Expiry": expiry,
        "Strike": strike,
        "Option Type": option_type,
        "Lot Size": lot_size,

        "Transaction Type": transaction_type,
        "Order Type": order_type,
        "Product": product,

        "Current Quantity": current_quantity,
        "Requested Exit Quantity": requested_quantity,
        "Remaining Quantity": remaining_quantity,

        "Contract Validation": "PASSED",
        "Quantity Validation": "PASSED",

        "Order Placement Permitted": False,

        "Wisdom Before Wealth": True,
    }


def _blocked(reason):
    return {
        "Status": "EXECUTION_BLOCKED",
        "Reason": reason,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }
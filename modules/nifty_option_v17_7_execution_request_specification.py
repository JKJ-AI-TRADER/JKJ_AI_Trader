"""
JKJ AI Trader
V17.7.6 — Execution Request Specification

Purpose:
Define and validate the structure of a future execution request
after V17.7.5 execution readiness.

This module:
- Validates execution request fields.
- Preserves the validated quantity.
- Preserves Decision/Risk priority.
- Preserves validated contract identity.
- Requires explicit BUY transaction type.
- Requires explicit order type and product.
- Does NOT modify quantity.
- Does NOT modify capital allocation.
- Does NOT rank candidates.
- Does NOT reassign capital.
- Does NOT communicate with Zerodha.
- Does NOT place orders.

IMPORTANT:
Execution request specification is NOT order placement.
"""

from typing import Any, Dict


VALID_ORDER_TYPES = {
    "MARKET",
    "LIMIT",
}

VALID_PRODUCTS = {
    "MIS",
    "NRML",
}


def _blocked(reason: str) -> Dict[str, Any]:
    """Return a safely blocked execution request."""
    return {
        "Status": "EXECUTION_REQUEST_BLOCKED",
        "Reason": reason,
        "Execution Request": None,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Broker Communication": False,
        "Wisdom Before Wealth": True,
    }


def create_execution_request(
    execution_candidate: Dict[str, Any],
    order_type: str,
    product: str,
    transaction_type: str = "BUY",
) -> Dict[str, Any]:
    """
    Validate and construct a future execution request specification.

    No broker communication occurs.

    Expected input:
        One candidate from V17.7.5 execution readiness.

    Returns:
        EXECUTION_REQUEST_SPECIFIED
        or
        EXECUTION_REQUEST_BLOCKED
    """

    if not isinstance(execution_candidate, dict):
        return _blocked(
            "Execution candidate must be a dictionary"
        )

    if execution_candidate.get("Execution Ready") is not True:
        return _blocked(
            "Candidate is not execution ready"
        )

    if execution_candidate.get("Validated") is not True:
        return _blocked(
            "Candidate is not validated"
        )

    if execution_candidate.get(
        "Contract Identity Valid"
    ) is not True:
        return _blocked(
            "Contract identity is not valid"
        )

    if execution_candidate.get(
        "Order Placement Permitted"
    ) is not False:
        return _blocked(
            "Order placement must remain disabled"
        )

    candidate = execution_candidate.get("Candidate")

    if not candidate:
        return _blocked(
            "Candidate identity is missing"
        )

    priority = execution_candidate.get("Priority")

    if not isinstance(priority, int) or priority <= 0:
        return _blocked(
            "Invalid candidate priority"
        )

    trading_symbol = execution_candidate.get(
        "Trading Symbol"
    )

    if not trading_symbol:
        return _blocked(
            "Trading symbol is missing"
        )

    instrument_token = execution_candidate.get(
        "Instrument Token"
    )

    if (
        not isinstance(instrument_token, int)
        or instrument_token <= 0
    ):
        return _blocked(
            "Instrument token is invalid"
        )

    quantity = execution_candidate.get(
        "Reconciled Quantity"
    )

    if not isinstance(quantity, int) or quantity <= 0:
        return _blocked(
            "Execution quantity must be a positive integer"
        )

    lot_size = execution_candidate.get(
        "Lot Size"
    )

    if not isinstance(lot_size, int) or lot_size <= 0:
        return _blocked(
            "Contract lot size must be a positive integer"
        )

    if quantity % lot_size != 0:
        return _blocked(
            "Execution quantity is not a valid contract multiple"
        )

    entry_price = execution_candidate.get(
        "Entry Price"
    )

    if (
        not isinstance(entry_price, (int, float))
        or entry_price <= 0
    ):
        return _blocked(
            "Entry price must be positive"
        )

    allocated_capital = execution_candidate.get(
        "Allocated Capital"
    )

    required_capital = execution_candidate.get(
        "Required Capital"
    )

    if (
        not isinstance(allocated_capital, (int, float))
        or allocated_capital <= 0
    ):
        return _blocked(
            "Allocated capital must be positive"
        )

    if (
        not isinstance(required_capital, (int, float))
        or required_capital <= 0
    ):
        return _blocked(
            "Required capital must be positive"
        )

    if required_capital > allocated_capital + 0.01:
        return _blocked(
            "Required capital exceeds allocated capital"
        )

    if transaction_type != "BUY":
        return _blocked(
            "Transaction type must be BUY"
        )

    if order_type not in VALID_ORDER_TYPES:
        return _blocked(
            f"Invalid order type: {order_type}"
        )

    if product not in VALID_PRODUCTS:
        return _blocked(
            f"Invalid product: {product}"
        )

    execution_request = {
        "Candidate": candidate,
        "Priority": priority,
        "Priority Source": "DECISION_RISK_LAYER",
        "Trading Symbol": trading_symbol,
        "Instrument Token": instrument_token,
        "Transaction Type": "BUY",
        "Order Type": order_type,
        "Product": product,
        "Quantity": quantity,
        "Lot Size": lot_size,
        "Entry Price Reference": entry_price,
        "Allocated Capital": float(
            allocated_capital
        ),
        "Required Capital": float(
            required_capital
        ),
        "Contract Identity Valid": True,
        "Execution Ready": True,

        # Safety boundary:
        "Order Placement Permitted": False,
        "Broker Communication": False,
    }

    return {
        "Status": "EXECUTION_REQUEST_SPECIFIED",
        "Execution Request": execution_request,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Broker Communication": False,
        "Wisdom Before Wealth": True,
    }
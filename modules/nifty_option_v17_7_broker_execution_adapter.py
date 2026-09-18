"""
JKJ AI Trader
V17.7.7 — Broker Execution Adapter Boundary

Purpose:
Translate a validated V17.7.6 execution request into a
broker-compatible request representation.

IMPORTANT:
This module is DRY-RUN ONLY.

It:
- Validates the execution request.
- Builds a broker request payload.
- Preserves quantity and contract identity.
- Preserves Decision/Risk priority.
- Does NOT communicate with Zerodha.
- Does NOT import the Kite order-placement API.
- Does NOT place orders.
- Does NOT modify quantity.
- Does NOT reallocate capital.
- Does NOT rank candidates.
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
    """Return a safely blocked broker-adapter result."""
    return {
        "Status": "BROKER_REQUEST_BLOCKED",
        "Reason": reason,
        "Broker Request": None,
        "Dry Run": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def prepare_broker_request(
    execution_request_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate a V17.7.6 execution request and prepare a
    broker-compatible request representation.

    NO broker communication occurs.
    NO order is placed.
    """

    if not isinstance(execution_request_result, dict):
        return _blocked(
            "Execution request result must be a dictionary"
        )

    if execution_request_result.get("Status") != (
        "EXECUTION_REQUEST_SPECIFIED"
    ):
        return _blocked(
            "Execution request is not specified"
        )

    if execution_request_result.get(
        "Order Placement Permitted"
    ) is not False:
        return _blocked(
            "Order placement must remain disabled"
        )

    if execution_request_result.get(
        "Broker Communication"
    ) is not False:
        return _blocked(
            "Broker communication must remain disabled"
        )

    if execution_request_result.get(
        "Capital Reassignment"
    ) is not False:
        return _blocked(
            "Capital reassignment must remain False"
        )

    if execution_request_result.get(
        "Automatic Ranking"
    ) is not False:
        return _blocked(
            "Automatic ranking must remain False"
        )

    if execution_request_result.get(
        "Priority Source"
    ) != "DECISION_RISK_LAYER":
        return _blocked(
            "Priority source must remain DECISION_RISK_LAYER"
        )

    request = execution_request_result.get(
        "Execution Request"
    )

    if not isinstance(request, dict):
        return _blocked(
            "Execution Request payload is missing"
        )

    candidate = request.get("Candidate")

    if not candidate:
        return _blocked(
            "Candidate identity is missing"
        )

    priority = request.get("Priority")

    if not isinstance(priority, int) or priority <= 0:
        return _blocked(
            "Invalid candidate priority"
        )

    trading_symbol = request.get(
        "Trading Symbol"
    )

    if not trading_symbol:
        return _blocked(
            "Trading symbol is missing"
        )

    instrument_token = request.get(
        "Instrument Token"
    )

    if (
        not isinstance(instrument_token, int)
        or instrument_token <= 0
    ):
        return _blocked(
            "Instrument token is invalid"
        )

    transaction_type = request.get(
        "Transaction Type"
    )

    if transaction_type != "BUY":
        return _blocked(
            "Transaction type must be BUY"
        )

    order_type = request.get(
        "Order Type"
    )

    if order_type not in VALID_ORDER_TYPES:
        return _blocked(
            f"Invalid order type: {order_type}"
        )

    product = request.get(
        "Product"
    )

    if product not in VALID_PRODUCTS:
        return _blocked(
            f"Invalid product: {product}"
        )

    quantity = request.get(
        "Quantity"
    )

    if not isinstance(quantity, int) or quantity <= 0:
        return _blocked(
            "Quantity must be a positive integer"
        )

    lot_size = request.get(
        "Lot Size"
    )

    if not isinstance(lot_size, int) or lot_size <= 0:
        return _blocked(
            "Lot size must be a positive integer"
        )

    if quantity % lot_size != 0:
        return _blocked(
            "Quantity is not a valid contract multiple"
        )

    entry_price = request.get(
        "Entry Price Reference"
    )

    if (
        not isinstance(entry_price, (int, float))
        or entry_price <= 0
    ):
        return _blocked(
            "Entry price reference must be positive"
        )

    allocated_capital = request.get(
        "Allocated Capital"
    )

    required_capital = request.get(
        "Required Capital"
    )

    if (
        not isinstance(
            allocated_capital, (int, float)
        )
        or allocated_capital <= 0
    ):
        return _blocked(
            "Allocated capital must be positive"
        )

    if (
        not isinstance(
            required_capital, (int, float)
        )
        or required_capital <= 0
    ):
        return _blocked(
            "Required capital must be positive"
        )

    if required_capital > allocated_capital + 0.01:
        return _blocked(
            "Required capital exceeds allocated capital"
        )

    if request.get(
        "Contract Identity Valid"
    ) is not True:
        return _blocked(
            "Contract identity is not valid"
        )

    if request.get(
        "Execution Ready"
    ) is not True:
        return _blocked(
            "Execution request is not execution ready"
        )

    # ---------------------------------------------------------
    # BROKER-COMPATIBLE REPRESENTATION
    # ---------------------------------------------------------
    broker_request = {
        "tradingsymbol": trading_symbol,
        "instrument_token": instrument_token,
        "transaction_type": "BUY",
        "order_type": order_type,
        "product": product,
        "quantity": quantity,

        # Reference information retained for auditability.
        "entry_price_reference": entry_price,
        "allocated_capital": float(
            allocated_capital
        ),
        "required_capital": float(
            required_capital
        ),
        "candidate": candidate,
        "priority": priority,
        "priority_source": "DECISION_RISK_LAYER",

        # Explicit dry-run safety controls.
        "dry_run": True,
        "broker_communication": False,
        "order_placement_permitted": False,
    }

    return {
        "Status": "BROKER_REQUEST_PREPARED",
        "Broker Request": broker_request,
        "Candidate": candidate,
        "Priority": priority,
        "Quantity": quantity,
        "Trading Symbol": trading_symbol,
        "Instrument Token": instrument_token,
        "Dry Run": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }
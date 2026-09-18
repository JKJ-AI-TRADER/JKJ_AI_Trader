"""
JKJ AI Trader
V17.8.1 - Paper Order Simulator

Safety boundary:
- PAPER EXECUTION ONLY
- NO ZERODHA IMPORT
- NO BROKER COMMUNICATION
- NO LIVE ORDER PLACEMENT
"""

VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
VALID_PRODUCTS = {"MIS", "NRML"}


def _blocked(reason):
    return {
        "Status": "PAPER_ORDER_BLOCKED",
        "Reason": reason,
        "Paper Order": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def simulate_paper_order(execution_request_result):
    """
    Convert a validated V17.7.6 execution request into
    a paper order.

    This function does NOT communicate with Zerodha.
    """

    if not isinstance(execution_request_result, dict):
        return _blocked("Execution request result must be a dictionary")

    if execution_request_result.get("Status") != "EXECUTION_REQUEST_SPECIFIED":
        return _blocked("Execution request is not specified")

    if execution_request_result.get("Broker Communication", False) is True:
        return _blocked("Broker communication must remain disabled")

    if execution_request_result.get("Order Placement Permitted", False) is True:
        return _blocked("Live order placement must remain disabled")

    if execution_request_result.get("Capital Reassignment", False) is True:
        return _blocked("Capital reassignment is not permitted")

    if execution_request_result.get("Automatic Ranking", False) is True:
        return _blocked("Automatic ranking is not permitted")

    if execution_request_result.get("Priority Source") != "DECISION_RISK_LAYER":
        return _blocked("Priority source must remain Decision/Risk layer")

    request = execution_request_result.get("Execution Request")

    if not isinstance(request, dict):
        return _blocked("Execution Request payload is missing")

    required_fields = [
        "Candidate",
        "Priority",
        "Priority Source",
        "Trading Symbol",
        "Instrument Token",
        "Transaction Type",
        "Order Type",
        "Product",
        "Quantity",
        "Lot Size",
        "Entry Price Reference",
        "Allocated Capital",
        "Required Capital",
        "Contract Valid",
        "Execution Ready",
        "Order Placement Permitted",
        "Broker Communication",
    ]

    for field in required_fields:
        if field not in request:
            return _blocked(f"Missing execution request field: {field}")

    if request["Transaction Type"] != "BUY":
        return _blocked("Paper simulator accepts BUY requests only")

    if request["Order Type"] not in VALID_ORDER_TYPES:
        return _blocked("Invalid order type")

    if request["Product"] not in VALID_PRODUCTS:
        return _blocked("Invalid product")

    quantity = request["Quantity"]
    lot_size = request["Lot Size"]

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return _blocked("Quantity must be a positive integer")

    if (
        not isinstance(lot_size, int)
        or isinstance(lot_size, bool)
        or lot_size <= 0
    ):
        return _blocked("Lot Size must be a positive integer")

    if quantity % lot_size != 0:
        return _blocked("Quantity must be a multiple of Lot Size")

    entry_price = request["Entry Price Reference"]

    if not isinstance(entry_price, (int, float)) or isinstance(entry_price, bool):
        return _blocked("Entry Price Reference must be numeric")

    if entry_price <= 0:
        return _blocked("Entry Price Reference must be positive")

    allocated_capital = request["Allocated Capital"]
    required_capital = request["Required Capital"]

    if (
        not isinstance(allocated_capital, (int, float))
        or isinstance(allocated_capital, bool)
        or allocated_capital <= 0
    ):
        return _blocked("Allocated Capital must be positive")

    if (
        not isinstance(required_capital, (int, float))
        or isinstance(required_capital, bool)
        or required_capital <= 0
    ):
        return _blocked("Required Capital must be positive")

    if required_capital > allocated_capital:
        return _blocked("Required capital exceeds allocated capital")

    if request["Contract Valid"] is not True:
        return _blocked("Contract must be valid")

    if request["Execution Ready"] is not True:
        return _blocked("Execution request must be execution-ready")

    if request["Order Placement Permitted"] is True:
        return _blocked("Live order placement must remain disabled")

    if request["Broker Communication"] is True:
        return _blocked("Broker communication must remain disabled")

    paper_order = {
        "Paper Order ID": "JKJ-PAPER-ORDER-001",
        "Candidate": request["Candidate"],
        "Priority": request["Priority"],
        "Priority Source": request["Priority Source"],
        "Trading Symbol": request["Trading Symbol"],
        "Instrument Token": request["Instrument Token"],
        "Transaction Type": request["Transaction Type"],
        "Order Type": request["Order Type"],
        "Product": request["Product"],
        "Quantity": quantity,
        "Lot Size": lot_size,
        "Entry Price Reference": entry_price,
        "Allocated Capital": allocated_capital,
        "Required Capital": required_capital,
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Status": "PAPER_ACCEPTED",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }

    return {
        "Status": "PAPER_ORDER_ACCEPTED",
        "Paper Order": paper_order,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

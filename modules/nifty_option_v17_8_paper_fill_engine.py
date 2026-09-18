"""
JKJ AI Trader
V17.8.2 - Paper Fill Engine

Safety boundary:
- PAPER EXECUTION ONLY
- FULL FILL ONLY
- NO ZERODHA IMPORT
- NO BROKER COMMUNICATION
- NO LIVE ORDER PLACEMENT
"""

def _blocked(reason):
    return {
        "Status": "PAPER_FILL_BLOCKED",
        "Reason": reason,
        "Paper Fill": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def simulate_paper_fill(paper_order_result, fill_price=None):
    """
    Simulate a FULL paper fill for an accepted paper order.

    No broker communication occurs.
    No live order is placed.
    No real capital is moved.

    Partial fills are intentionally NOT supported in V17.8.2 Stage 1.
    """

    if not isinstance(paper_order_result, dict):
        return _blocked("Paper order result must be a dictionary")

    if paper_order_result.get("Status") != "PAPER_ORDER_ACCEPTED":
        return _blocked("Paper order is not accepted")

    if paper_order_result.get("Paper Execution") is not True:
        return _blocked("Paper execution must be enabled")

    if paper_order_result.get("Broker Communication", False) is True:
        return _blocked("Broker communication must remain disabled")

    if paper_order_result.get("Order Placement Permitted", False) is True:
        return _blocked("Live order placement must remain disabled")

    if paper_order_result.get("Capital Reassignment", False) is True:
        return _blocked("Capital reassignment is not permitted")

    if paper_order_result.get("Automatic Ranking", False) is True:
        return _blocked("Automatic ranking is not permitted")

    if paper_order_result.get("Priority Source") != "DECISION_RISK_LAYER":
        return _blocked("Priority source must remain Decision/Risk layer")

    paper_order = paper_order_result.get("Paper Order")

    if not isinstance(paper_order, dict):
        return _blocked("Paper Order payload is missing")

    required_fields = [
        "Paper Order ID",
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
        "Paper Status",
        "Paper Execution",
        "Broker Communication",
        "Order Placement Permitted",
    ]

    for field in required_fields:
        if field not in paper_order:
            return _blocked(f"Missing paper order field: {field}")

    if paper_order["Paper Status"] != "PAPER_ACCEPTED":
        return _blocked("Paper order status must be PAPER_ACCEPTED")

    if paper_order["Transaction Type"] != "BUY":
        return _blocked("Paper fill engine accepts BUY orders only")

    quantity = paper_order["Quantity"]
    lot_size = paper_order["Lot Size"]

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

    if paper_order["Contract Valid"] is not True:
        return _blocked("Contract must be valid")

    if paper_order["Execution Ready"] is not True:
        return _blocked("Paper order must be execution-ready")

    if paper_order["Broker Communication"] is True:
        return _blocked("Broker communication must remain disabled")

    if paper_order["Order Placement Permitted"] is True:
        return _blocked("Live order placement must remain disabled")

    reference_price = paper_order["Entry Price Reference"]

    if (
        not isinstance(reference_price, (int, float))
        or isinstance(reference_price, bool)
        or reference_price <= 0
    ):
        return _blocked("Entry Price Reference must be positive")

    if fill_price is None:
        fill_price = reference_price

    if (
        not isinstance(fill_price, (int, float))
        or isinstance(fill_price, bool)
        or fill_price <= 0
    ):
        return _blocked("Fill Price must be positive")

    required_capital = paper_order["Required Capital"]

    if (
        not isinstance(required_capital, (int, float))
        or isinstance(required_capital, bool)
        or required_capital <= 0
    ):
        return _blocked("Required Capital must be positive")

    simulated_fill_capital = fill_price * quantity

    if simulated_fill_capital <= 0:
        return _blocked("Simulated fill capital must be positive")

    paper_fill = {
        "Paper Fill ID": f"{paper_order['Paper Order ID']}-FILL-001",
        "Paper Order ID": paper_order["Paper Order ID"],
        "Candidate": paper_order["Candidate"],
        "Priority": paper_order["Priority"],
        "Priority Source": paper_order["Priority Source"],
        "Trading Symbol": paper_order["Trading Symbol"],
        "Instrument Token": paper_order["Instrument Token"],
        "Transaction Type": paper_order["Transaction Type"],
        "Order Type": paper_order["Order Type"],
        "Product": paper_order["Product"],
        "Requested Quantity": quantity,
        "Filled Quantity": quantity,
        "Lot Size": lot_size,
        "Entry Price Reference": reference_price,
        "Fill Price": fill_price,
        "Required Capital at Request": required_capital,
        "Simulated Fill Capital": simulated_fill_capital,
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Order Status": "PAPER_ACCEPTED",
        "Paper Fill Status": "FILLED",
        "Fill Type": "FULL",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }

    return {
        "Status": "PAPER_FILL_COMPLETE",
        "Paper Fill": paper_fill,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

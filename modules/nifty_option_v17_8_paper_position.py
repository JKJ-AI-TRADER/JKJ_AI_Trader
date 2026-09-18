"""
JKJ AI Trader
V17.8.3 - Paper Position Creation

Safety boundary:
- PAPER POSITION ONLY
- Created only from a completed FULL paper fill
- NO ZERODHA IMPORT
- NO BROKER COMMUNICATION
- NO LIVE ORDER PLACEMENT
"""

def _blocked(reason):
    return {
        "Status": "PAPER_POSITION_BLOCKED",
        "Reason": reason,
        "Paper Position": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def create_paper_position(paper_fill_result):
    """
    Create a paper position from a completed FULL paper fill.

    This function does not communicate with Zerodha and does not
    create or modify any real broker position.
    """

    if not isinstance(paper_fill_result, dict):
        return _blocked("Paper fill result must be a dictionary")

    if paper_fill_result.get("Status") != "PAPER_FILL_COMPLETE":
        return _blocked("Paper fill is not complete")

    if paper_fill_result.get("Paper Execution") is not True:
        return _blocked("Paper execution must be enabled")

    if paper_fill_result.get("Broker Communication", False) is True:
        return _blocked("Broker communication must remain disabled")

    if paper_fill_result.get("Order Placement Permitted", False) is True:
        return _blocked("Live order placement must remain disabled")

    if paper_fill_result.get("Capital Reassignment", False) is True:
        return _blocked("Capital reassignment is not permitted")

    if paper_fill_result.get("Automatic Ranking", False) is True:
        return _blocked("Automatic ranking is not permitted")

    if paper_fill_result.get("Priority Source") != "DECISION_RISK_LAYER":
        return _blocked("Priority source must remain Decision/Risk layer")

    fill = paper_fill_result.get("Paper Fill")

    if not isinstance(fill, dict):
        return _blocked("Paper Fill payload is missing")

    required_fields = [
        "Paper Fill ID",
        "Paper Order ID",
        "Candidate",
        "Priority",
        "Priority Source",
        "Trading Symbol",
        "Instrument Token",
        "Transaction Type",
        "Order Type",
        "Product",
        "Requested Quantity",
        "Filled Quantity",
        "Lot Size",
        "Entry Price Reference",
        "Fill Price",
        "Required Capital at Request",
        "Simulated Fill Capital",
        "Contract Valid",
        "Execution Ready",
        "Paper Order Status",
        "Paper Fill Status",
        "Fill Type",
        "Paper Execution",
        "Broker Communication",
        "Order Placement Permitted",
    ]

    for field in required_fields:
        if field not in fill:
            return _blocked(f"Missing paper fill field: {field}")

    if fill["Paper Fill Status"] != "FILLED":
        return _blocked("Paper fill status must be FILLED")

    if fill["Fill Type"] != "FULL":
        return _blocked("Only FULL fills are supported in V17.8.3 Stage 1")

    if fill["Transaction Type"] != "BUY":
        return _blocked("Paper position creation accepts BUY fills only")

    requested_quantity = fill["Requested Quantity"]
    filled_quantity = fill["Filled Quantity"]
    lot_size = fill["Lot Size"]

    if (
        not isinstance(requested_quantity, int)
        or isinstance(requested_quantity, bool)
        or requested_quantity <= 0
    ):
        return _blocked("Requested Quantity must be a positive integer")

    if (
        not isinstance(filled_quantity, int)
        or isinstance(filled_quantity, bool)
        or filled_quantity <= 0
    ):
        return _blocked("Filled Quantity must be a positive integer")

    if requested_quantity != filled_quantity:
        return _blocked("FULL fill must equal requested quantity")

    if (
        not isinstance(lot_size, int)
        or isinstance(lot_size, bool)
        or lot_size <= 0
    ):
        return _blocked("Lot Size must be a positive integer")

    if filled_quantity % lot_size != 0:
        return _blocked("Filled Quantity must be a multiple of Lot Size")

    if fill["Contract Valid"] is not True:
        return _blocked("Contract must be valid")

    if fill["Execution Ready"] is not True:
        return _blocked("Execution must be ready")

    if fill["Paper Execution"] is not True:
        return _blocked("Paper execution must remain enabled")

    if fill["Broker Communication"] is True:
        return _blocked("Broker communication must remain disabled")

    if fill["Order Placement Permitted"] is True:
        return _blocked("Live order placement must remain disabled")

    fill_price = fill["Fill Price"]

    if (
        not isinstance(fill_price, (int, float))
        or isinstance(fill_price, bool)
        or fill_price <= 0
    ):
        return _blocked("Fill Price must be positive")

    simulated_fill_capital = fill["Simulated Fill Capital"]

    if (
        not isinstance(simulated_fill_capital, (int, float))
        or isinstance(simulated_fill_capital, bool)
        or simulated_fill_capital <= 0
    ):
        return _blocked("Simulated Fill Capital must be positive")

    expected_capital = fill_price * filled_quantity

    if simulated_fill_capital != expected_capital:
        return _blocked("Simulated fill capital calculation mismatch")

    paper_position = {
        "Paper Position ID": f"{fill['Paper Fill ID']}-POSITION-001",
        "Paper Fill ID": fill["Paper Fill ID"],
        "Paper Order ID": fill["Paper Order ID"],
        "Candidate": fill["Candidate"],
        "Priority": fill["Priority"],
        "Priority Source": fill["Priority Source"],
        "Trading Symbol": fill["Trading Symbol"],
        "Instrument Token": fill["Instrument Token"],
        "Position Type": "LONG",
        "Transaction Type": "BUY",
        "Order Type": fill["Order Type"],
        "Product": fill["Product"],
        "Quantity": filled_quantity,
        "Lot Size": lot_size,
        "Entry Price": fill_price,
        "Entry Price Reference": fill["Entry Price Reference"],
        "Capital Used": simulated_fill_capital,
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Status": "PAPER_POSITION_OPEN",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }

    return {
        "Status": "PAPER_POSITION_CREATED",
        "Paper Position": paper_position,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

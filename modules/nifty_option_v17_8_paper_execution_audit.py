"""
JKJ AI Trader
V17.8.4 - Paper Execution Audit

Safety boundary:
- READ-ONLY AUDIT
- PAPER EXECUTION ONLY
- NO ZERODHA IMPORT
- NO BROKER COMMUNICATION
- NO LIVE ORDER PLACEMENT
- DOES NOT MODIFY POSITION OR CAPITAL
"""


def _blocked(reason):
    return {
        "Status": "PAPER_AUDIT_BLOCKED",
        "Reason": reason,
        "Audit Record": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def create_paper_execution_audit(paper_position_result):
    """
    Create a read-only audit record from a completed paper position.

    The function does not modify the supplied position and does not
    communicate with Zerodha.
    """

    if not isinstance(paper_position_result, dict):
        return _blocked("Paper position result must be a dictionary")

    if paper_position_result.get("Status") != "PAPER_POSITION_CREATED":
        return _blocked("Paper position is not created")

    if paper_position_result.get("Paper Execution") is not True:
        return _blocked("Paper execution must be enabled")

    if paper_position_result.get("Broker Communication", False) is True:
        return _blocked("Broker communication must remain disabled")

    if paper_position_result.get("Order Placement Permitted", False) is True:
        return _blocked("Live order placement must remain disabled")

    if paper_position_result.get("Capital Reassignment", False) is True:
        return _blocked("Capital reassignment is not permitted")

    if paper_position_result.get("Automatic Ranking", False) is True:
        return _blocked("Automatic ranking is not permitted")

    if paper_position_result.get("Priority Source") != "DECISION_RISK_LAYER":
        return _blocked("Priority source must remain Decision/Risk layer")

    position = paper_position_result.get("Paper Position")

    if not isinstance(position, dict):
        return _blocked("Paper Position payload is missing")

    required_fields = [
        "Paper Position ID",
        "Paper Fill ID",
        "Paper Order ID",
        "Candidate",
        "Priority",
        "Priority Source",
        "Trading Symbol",
        "Instrument Token",
        "Position Type",
        "Transaction Type",
        "Order Type",
        "Product",
        "Quantity",
        "Lot Size",
        "Entry Price",
        "Entry Price Reference",
        "Capital Used",
        "Contract Valid",
        "Execution Ready",
        "Paper Status",
        "Paper Execution",
        "Broker Communication",
        "Order Placement Permitted",
    ]

    for field in required_fields:
        if field not in position:
            return _blocked(f"Missing paper position field: {field}")

    if position["Paper Status"] != "PAPER_POSITION_OPEN":
        return _blocked("Paper position must be open")

    if position["Position Type"] != "LONG":
        return _blocked("Paper audit currently supports LONG positions only")

    if position["Transaction Type"] != "BUY":
        return _blocked("Paper audit currently supports BUY positions only")

    quantity = position["Quantity"]
    lot_size = position["Lot Size"]

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

    entry_price = position["Entry Price"]

    if (
        not isinstance(entry_price, (int, float))
        or isinstance(entry_price, bool)
        or entry_price <= 0
    ):
        return _blocked("Entry Price must be positive")

    capital_used = position["Capital Used"]

    if (
        not isinstance(capital_used, (int, float))
        or isinstance(capital_used, bool)
        or capital_used <= 0
    ):
        return _blocked("Capital Used must be positive")

    expected_capital = entry_price * quantity

    if capital_used != expected_capital:
        return _blocked("Capital calculation mismatch")

    if position["Contract Valid"] is not True:
        return _blocked("Contract must be valid")

    if position["Execution Ready"] is not True:
        return _blocked("Execution must be ready")

    if position["Paper Execution"] is not True:
        return _blocked("Paper execution must remain enabled")

    if position["Broker Communication"] is True:
        return _blocked("Broker communication must remain disabled")

    if position["Order Placement Permitted"] is True:
        return _blocked("Live order placement must remain disabled")

    audit_record = {
        "Audit ID": f"{position['Paper Position ID']}-AUDIT-001",
        "Paper Position ID": position["Paper Position ID"],
        "Paper Fill ID": position["Paper Fill ID"],
        "Paper Order ID": position["Paper Order ID"],
        "Candidate": position["Candidate"],
        "Priority": position["Priority"],
        "Priority Source": position["Priority Source"],
        "Trading Symbol": position["Trading Symbol"],
        "Instrument Token": position["Instrument Token"],
        "Position Type": position["Position Type"],
        "Transaction Type": position["Transaction Type"],
        "Order Type": position["Order Type"],
        "Product": position["Product"],
        "Quantity": quantity,
        "Lot Size": lot_size,
        "Entry Price": entry_price,
        "Entry Price Reference": position["Entry Price Reference"],
        "Capital Used": capital_used,
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Status": position["Paper Status"],
        "Audit Status": "PAPER_EXECUTION_AUDITED",
        "Audit Scope": "POSITION_CREATION",
        "Read Only": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }

    return {
        "Status": "PAPER_EXECUTION_AUDIT_COMPLETE",
        "Audit Record": audit_record,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Read Only": True,
        "Wisdom Before Wealth": True,
    }

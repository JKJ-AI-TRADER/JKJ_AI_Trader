"""
JKJ AI Trader
V17.8.5 - Paper Fill -> V15 Entry Mapping Bridge

Purpose:
    Validate and map a completed V17.8 paper fill into the
    execution-side fields required by the existing V15/V11
    paper-trade entry structure.

This module does NOT:
    - open a paper trade
    - modify V11
    - modify V15
    - generate stop-loss or targets
    - generate BUY/SELL decisions
    - connect to Zerodha
    - place live orders
    - modify main.py

Stop Loss and Targets must continue to come from the
existing V14/V15 qualification chain.

Wisdom Before Wealth.
"""


def _blocked(reason):
    return {
        "Status": "V15_ENTRY_MAPPING_BLOCKED",
        "Reason": reason,
        "V15 Entry Mapping": None,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def map_paper_fill_to_v15_entry(
    paper_fill_result,
    v15_qualification,
    trade_id,
    entry_time=None,
):
    """
    Validate a completed V17.8 paper fill and create a
    V15-compatible entry mapping.

    This function does not call V15 or V11.
    """

    if not isinstance(paper_fill_result, dict):
        return _blocked("Paper fill result must be a dictionary")

    if paper_fill_result.get("Status") != "PAPER_FILL_COMPLETE":
        return _blocked("Paper fill must have Status PAPER_FILL_COMPLETE")

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

    required_fill_fields = [
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
        "Contract Valid",
        "Execution Ready",
        "Paper Fill Status",
        "Fill Type",
        "Paper Execution",
        "Broker Communication",
        "Order Placement Permitted",
    ]

    for field in required_fill_fields:
        if field not in fill:
            return _blocked(f"Missing paper fill field: {field}")

    if fill["Paper Fill Status"] != "FILLED":
        return _blocked("Paper fill status must be FILLED")

    if fill["Fill Type"] != "FULL":
        return _blocked("Only FULL fills may be mapped in V17.8.5")

    if fill["Transaction Type"] != "BUY":
        return _blocked("Only BUY fills may be mapped")

    if fill["Contract Valid"] is not True:
        return _blocked("Contract must be valid")

    if fill["Execution Ready"] is not True:
        return _blocked("Execution must be ready")

    quantity = fill["Filled Quantity"]
    lot_size = fill["Lot Size"]

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return _blocked("Filled Quantity must be a positive integer")

    if (
        not isinstance(lot_size, int)
        or isinstance(lot_size, bool)
        or lot_size <= 0
    ):
        return _blocked("Lot Size must be a positive integer")

    if quantity % lot_size != 0:
        return _blocked("Filled Quantity must be a multiple of Lot Size")

    fill_price = fill["Fill Price"]

    if (
        not isinstance(fill_price, (int, float))
        or isinstance(fill_price, bool)
        or fill_price <= 0
    ):
        return _blocked("Fill Price must be positive")

    # ---------------------------------------------------------
    # V15 qualification remains authoritative for decision/risk
    # fields.
    # ---------------------------------------------------------

    if not isinstance(v15_qualification, dict):
        return _blocked("V15 qualification must be a dictionary")

    if v15_qualification.get("Status") != "QUALIFIED":
        return _blocked("V15 qualification must have Status QUALIFIED")

    if v15_qualification.get("Paper Trade Permission") != "PERMITTED":
        return _blocked("V15 paper trade permission must be PERMITTED")

    qualification_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Entry Price",
        "Stop Price",
        "Target 1",
        "Target 2",
        "Target 3",
        "Risk Reward 1",
        "Risk Reward 2",
        "Risk Reward 3",
        "Entry Qualification",
        "Qualification Reason",
    ]

    for field in qualification_fields:
        if field not in v15_qualification:
            return _blocked(
                f"Missing V15 qualification field: {field}"
            )

    # ---------------------------------------------------------
    # Identity must agree between execution and qualification.
    # ---------------------------------------------------------

    if (
        fill["Trading Symbol"]
        != v15_qualification["Trading Symbol"]
    ):
        return _blocked("Trading Symbol mismatch")

    if (
        fill["Fill Price"] <= 0
        or v15_qualification["Entry Price"] <= 0
    ):
        return _blocked("Entry prices must be positive")

    # V17.8 execution records the actual simulated fill price.
    # V15 qualification remains the source of decision/risk data.
    entry_price = fill["Fill Price"]

    if trade_id is None or str(trade_id).strip() == "":
        return _blocked("Trade ID is required")

    mapping = {
        "Status": "MAPPED",
        "Trade ID": trade_id,
        "Paper Fill ID": fill["Paper Fill ID"],
        "Paper Order ID": fill["Paper Order ID"],
        "Trading Symbol": fill["Trading Symbol"],
        "Instrument Type": "OPTION",
        "Underlying": v15_qualification["Underlying"],
        "Expiry": v15_qualification["Expiry"],
        "Strike": v15_qualification["Strike"],
        "Option Type": v15_qualification["Option Type"],
        "Entry Price": entry_price,
        "Qualified Entry Price": v15_qualification["Entry Price"],
        "Quantity": quantity,
        "Stop Loss": v15_qualification["Stop Price"],
        "Target": v15_qualification["Target 1"],
        "Target 1": v15_qualification["Target 1"],
        "Target 2": v15_qualification["Target 2"],
        "Target 3": v15_qualification["Target 3"],
        "Risk Reward 1": v15_qualification["Risk Reward 1"],
        "Risk Reward 2": v15_qualification["Risk Reward 2"],
        "Risk Reward 3": v15_qualification["Risk Reward 3"],
        "Entry Status": v15_qualification["Entry Qualification"],
        "Entry Reason": v15_qualification["Qualification Reason"],
        "Entry Time": entry_time,
        "Paper Trade Permission": "PERMITTED",
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }

    return {
        "Status": "V15_ENTRY_MAPPING_COMPLETE",
        "V15 Entry Mapping": mapping,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

"""
JKJ AI Trader
V17.8.6 - V15 Entry Boundary Validation

Validation-only boundary between V17.8 paper execution
and the existing V15/V11 paper-trade entry layer.

No V15/V11 calls.
No broker communication.
No live order placement.
No main.py changes.
"""

REQUIRED_FIELDS = {
    "Trade ID",
    "Trading Symbol",
    "Instrument Type",
    "Underlying",
    "Expiry",
    "Strike",
    "Option Type",
    "Entry Price",
    "Quantity",
    "Stop Loss",
    "Target",
    "Target1",
    "Target2",
    "Target3",
    "RR1",
    "RR2",
    "RR3",
    "Entry Status",
    "Entry Reason",
    "Paper Trade Permission",
    "Contract Valid",
    "Execution Ready",
    "Paper Execution",
    "Broker Communication",
    "Order Placement Permitted",
}


def _blocked(reason):
    return {
        "Status": "V15_ENTRY_BOUNDARY_BLOCKED",
        "Reason": reason,
        "V15 Entry Payload": None,
        "V15 Call Permitted": False,
        "V11 Call Permitted": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def validate_v15_entry_boundary(mapped_entry):
    """Validate a V17.8.5 mapped entry before V15/V11 handoff."""

    if not isinstance(mapped_entry, dict):
        return _blocked("Mapped entry must be a dictionary")

    if mapped_entry.get("Status") != "MAPPED":
        return _blocked("Mapped entry status is not MAPPED")

    if mapped_entry.get("Paper Execution") is not True:
        return _blocked("Paper Execution flag must be True")

    if mapped_entry.get("Broker Communication") is not False:
        return _blocked("Broker Communication must be False")

    if mapped_entry.get("Order Placement Permitted") is not False:
        return _blocked("Order Placement Permitted must be False")

    missing = [
        field for field in REQUIRED_FIELDS
        if field not in mapped_entry
    ]

    if missing:
        return _blocked(
            f"Required mapped entry fields missing: {missing}"
        )

    if not mapped_entry.get("Trade ID"):
        return _blocked("Trade ID is required")

    if not mapped_entry.get("Trading Symbol"):
        return _blocked("Trading Symbol is required")

    if mapped_entry.get("Instrument Type") != "OPTION":
        return _blocked("Instrument Type must be OPTION")

    if mapped_entry.get("Paper Trade Permission") != "PERMITTED":
        return _blocked("Paper Trade Permission must be PERMITTED")

    if mapped_entry.get("Contract Valid") is not True:
        return _blocked("Contract must be valid")

    if mapped_entry.get("Execution Ready") is not True:
        return _blocked("Execution must be ready")

    quantity = mapped_entry.get("Quantity")

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return _blocked("Quantity must be a positive integer")

    entry_price = mapped_entry.get("Entry Price")

    if (
        not isinstance(entry_price, (int, float))
        or isinstance(entry_price, bool)
        or entry_price <= 0
    ):
        return _blocked("Entry Price must be positive")

    stop_loss = mapped_entry.get("Stop Loss")

    if (
        not isinstance(stop_loss, (int, float))
        or isinstance(stop_loss, bool)
        or stop_loss <= 0
    ):
        return _blocked("Stop Loss must be positive")

    targets = [
        mapped_entry.get("Target1"),
        mapped_entry.get("Target2"),
        mapped_entry.get("Target3"),
    ]

    if any(
        not isinstance(target, (int, float))
        or isinstance(target, bool)
        or target <= 0
        for target in targets
    ):
        return _blocked("All three targets must be positive")

    if mapped_entry.get("Target") != mapped_entry.get("Target1"):
        return _blocked("Target must remain equal to Target1")

    risk_rewards = [
        mapped_entry.get("RR1"),
        mapped_entry.get("RR2"),
        mapped_entry.get("RR3"),
    ]

    if any(
        not isinstance(rr, (int, float))
        or isinstance(rr, bool)
        or rr < 0
        for rr in risk_rewards
    ):
        return _blocked("Risk/reward values must be non-negative")

    if not mapped_entry.get("Entry Status"):
        return _blocked("Entry Status is required")

    if not mapped_entry.get("Entry Reason"):
        return _blocked("Entry Reason is required")

    payload = {
        field: mapped_entry[field]
        for field in REQUIRED_FIELDS
    }

    return {
        "Status": "V15_ENTRY_BOUNDARY_VALIDATED",
        "Reason": "V17.8.5 mapped entry is valid for V15 handoff",
        "V15 Entry Payload": payload,
        "V15 Call Permitted": False,
        "V11 Call Permitted": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

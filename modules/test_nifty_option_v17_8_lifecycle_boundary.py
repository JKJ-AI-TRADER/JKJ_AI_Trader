"""
JKJ AI Trader
V17.8.8 Controlled Lifecycle Boundary Test

Wisdom Before Wealth.
"""

from modules.nifty_option_v17_8_lifecycle_boundary import (
    validate_lifecycle_boundary,
)


def valid_handoff():
    trade = {
        "Trade ID": "JKJ-V1788-TEST-001",
        "Status": "OPEN",
        "Symbol": "NIFTY26SEP25000CE",
        "Instrument Type": "OPTION",
        "Entry Price": 103.0,
        "Original Quantity": 65,
        "Current Quantity": 65,
        "Stop Loss": 100.0,
        "Target": 106.0,
    }

    qualification = {
        "Status": "QUALIFIED",
        "Trading Symbol": "NIFTY26SEP25000CE",
        "Entry Price": 103.0,
        "Stop Price": 100.0,
        "Target 1": 106.0,
        "Target 2": 109.0,
        "Target 3": 112.0,
        "Paper Trade Permission": "PERMITTED",
    }

    return {
        "Status": "V17_8_7_PAPER_HANDOFF_COMPLETE",
        "Trade": trade,
        "Paper Trade Qualification": qualification,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }


# ---------------------------------------------------------
# Test 1 — valid lifecycle boundary
# ---------------------------------------------------------

result = validate_lifecycle_boundary(
    valid_handoff()
)

assert result["Status"] == (
    "V17_8_8_LIFECYCLE_BOUNDARY_VALIDATED"
)
assert result["Lifecycle Ready"] is True
assert result["Lifecycle Owner"] == "V15.4 / V11"
assert result["Trade ID"] == "JKJ-V1788-TEST-001"
assert result["Symbol"] == "NIFTY26SEP25000CE"
assert result["Instrument Type"] == "OPTION"
assert result["Entry Price"] == 103.0
assert result["Original Quantity"] == 65
assert result["Current Quantity"] == 65
assert result["Stop Loss"] == 100.0
assert result["Target"] == 106.0
assert result["V15.4 Lifecycle Action Permitted"] is True
assert result["Paper Execution"] is True
assert result["Broker Communication"] is False
assert result["Order Placement Permitted"] is False
assert result["Automatic Ranking"] is False
assert result["Capital Reassignment"] is False
assert result["Wisdom Before Wealth"] is True


# ---------------------------------------------------------
# Test 2 — incomplete V17.8.7 handoff blocked
# ---------------------------------------------------------

blocked = validate_lifecycle_boundary({
    "Status": "V17_8_7_PAPER_HANDOFF_REJECTED"
})

assert blocked["Status"] == (
    "V17_8_8_LIFECYCLE_BOUNDARY_BLOCKED"
)
assert blocked["Lifecycle Ready"] is False
assert blocked["Order Placement Permitted"] is False


# ---------------------------------------------------------
# Test 3 — closed V11 trade blocked
# ---------------------------------------------------------

closed_handoff = valid_handoff()
closed_handoff["Trade"]["Status"] = "CLOSED"

blocked = validate_lifecycle_boundary(
    closed_handoff
)

assert blocked["Status"] == (
    "V17_8_8_LIFECYCLE_BOUNDARY_BLOCKED"
)
assert blocked["Lifecycle Ready"] is False


# ---------------------------------------------------------
# Test 4 — missing current quantity blocked
# ---------------------------------------------------------

missing_quantity = valid_handoff()
del missing_quantity["Trade"]["Current Quantity"]

blocked = validate_lifecycle_boundary(
    missing_quantity
)

assert blocked["Status"] == (
    "V17_8_8_LIFECYCLE_BOUNDARY_BLOCKED"
)
assert blocked["Lifecycle Ready"] is False


# ---------------------------------------------------------
# Test 5 — invalid V15 qualification blocked
# ---------------------------------------------------------

invalid_qualification = valid_handoff()
invalid_qualification[
    "Paper Trade Qualification"
]["Paper Trade Permission"] = "NOT_PERMITTED"

blocked = validate_lifecycle_boundary(
    invalid_qualification
)

assert blocked["Status"] == (
    "V17_8_8_LIFECYCLE_BOUNDARY_BLOCKED"
)
assert blocked["Lifecycle Ready"] is False


# ---------------------------------------------------------
# Test 6 — broker communication blocked
# ---------------------------------------------------------

broker_handoff = valid_handoff()
broker_handoff["Broker Communication"] = True

blocked = validate_lifecycle_boundary(
    broker_handoff
)

assert blocked["Status"] == (
    "V17_8_8_LIFECYCLE_BOUNDARY_BLOCKED"
)
assert blocked["Lifecycle Ready"] is False


print("ALL V17.8.8 TESTS PASSED")

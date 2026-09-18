"""
JKJ AI Trader
V17.7.2 — Quantity-to-Contract Validation Test
"""

from nifty_option_v17_7_quantity_contract_validation import (
    validate_quantity_against_contract
)


print("\n==============================================")
print("JKJ V17.7.2 QUANTITY-CONTRACT VALIDATION TEST")
print("==============================================")


# ---------------------------------------------------------
# Common valid reconciliation result
# ---------------------------------------------------------

valid_reconciliation = {
    "Status": "RECONCILIATION_COMPLETE",
    "Allocated Capital": 20000.0,
    "Entry Price": 300.0,
    "Lot Size": 65,
    "Cost Per Lot": 19500.0,
    "Reconciled Lots": 1,
    "Reconciled Quantity": 65,
    "Estimated Capital Required": 19500.0,
    "Unused Allocated Capital": 500.0,
}


# ---------------------------------------------------------
# Common valid contract validation result
# ---------------------------------------------------------

valid_contract = {
    "Status": "CONTRACT_VALIDATED",
    "Trading Symbol": "NIFTY2692223300CE",
    "Instrument Token": 14588162,
    "Expiry": "2026-09-22",
    "Strike": 23300.0,
    "Option Type": "CE",
    "Lot Size": 65,
    "Contract Identity Valid": True,
    "Order Placement Permitted": False,
}


# ---------------------------------------------------------
# TEST 1
# One valid complete lot
# ---------------------------------------------------------

print("\nTEST 1 — Valid One-Lot Quantity")

result = validate_quantity_against_contract(
    valid_reconciliation,
    valid_contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_VALIDATED"
assert result["Validated Quantity"] == 65
assert result["Validated Lots"] == 1
assert result["Lot Size"] == 65
assert result["Quantity Matches Contract"] is True
assert result["Contract Identity Valid"] is True
assert result["Order Placement Permitted"] is False


# ---------------------------------------------------------
# TEST 2
# Multiple complete lots
# ---------------------------------------------------------

print("\nTEST 2 — Valid Multiple-Lot Quantity")

reconciliation = dict(valid_reconciliation)
reconciliation["Reconciled Quantity"] = 195
reconciliation["Reconciled Lots"] = 3

result = validate_quantity_against_contract(
    reconciliation,
    valid_contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_VALIDATED"
assert result["Validated Quantity"] == 195
assert result["Validated Lots"] == 3


# ---------------------------------------------------------
# TEST 3
# Important invalid quantity:
# 75 is not a multiple of lot size 65.
# ---------------------------------------------------------

print("\nTEST 3 — Invalid 75 Quantity Against 65 Lot")

reconciliation = dict(valid_reconciliation)
reconciliation["Reconciled Quantity"] = 75
reconciliation["Reconciled Lots"] = 1

result = validate_quantity_against_contract(
    reconciliation,
    valid_contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_BLOCKED"
assert result["Validated Quantity"] == 0
assert result["Quantity Matches Contract"] is False


# ---------------------------------------------------------
# TEST 4
# Contract validation failed
# ---------------------------------------------------------

print("\nTEST 4 — Unvalidated Contract")

invalid_contract = dict(valid_contract)
invalid_contract["Status"] = "CONTRACT_BLOCKED"
invalid_contract["Contract Identity Valid"] = False

result = validate_quantity_against_contract(
    valid_reconciliation,
    invalid_contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_BLOCKED"


# ---------------------------------------------------------
# TEST 5
# Reconciliation failed
# ---------------------------------------------------------

print("\nTEST 5 — Failed Reconciliation")

blocked_reconciliation = {
    "Status": "RECONCILIATION_BLOCKED",
    "Reconciled Quantity": 0,
}

result = validate_quantity_against_contract(
    blocked_reconciliation,
    valid_contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_BLOCKED"


# ---------------------------------------------------------
# TEST 6
# Zero quantity
# ---------------------------------------------------------

print("\nTEST 6 — Zero Quantity")

reconciliation = dict(valid_reconciliation)
reconciliation["Reconciled Quantity"] = 0

result = validate_quantity_against_contract(
    reconciliation,
    valid_contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_BLOCKED"


# ---------------------------------------------------------
# TEST 7
# Different valid lot size
# ---------------------------------------------------------

print("\nTEST 7 — Valid Different Contract Lot Size")

reconciliation = dict(valid_reconciliation)
reconciliation["Reconciled Quantity"] = 50
reconciliation["Reconciled Lots"] = 1

contract = dict(valid_contract)
contract["Lot Size"] = 50

result = validate_quantity_against_contract(
    reconciliation,
    contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_VALIDATED"
assert result["Validated Quantity"] == 50
assert result["Validated Lots"] == 1


# ---------------------------------------------------------
# TEST 8
# Invalid contract lot size
# ---------------------------------------------------------

print("\nTEST 8 — Invalid Contract Lot Size")

contract = dict(valid_contract)
contract["Lot Size"] = 0

result = validate_quantity_against_contract(
    valid_reconciliation,
    contract,
)

print(result)

assert result["Status"] == "QUANTITY_CONTRACT_BLOCKED"


print("\n==============================================")
print("ALL V17.7.2 TESTS PASSED")
print("==============================================")
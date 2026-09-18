"""
JKJ AI Trader
V17.7.1 — Capital-to-Quantity Reconciliation Test
"""

from nifty_option_v17_7_capital_quantity_reconciliation import (
    reconcile_capital_to_quantity
)


print("\n==============================================")
print("JKJ V17.7.1 CAPITAL-TO-QUANTITY TEST")
print("==============================================")


# ---------------------------------------------------------
# TEST 1
# ₹20,000 allocation, ₹300 option, lot 65
# One complete lot is affordable.
# ---------------------------------------------------------
print("\nTEST 1 — One Affordable Lot")

result = reconcile_capital_to_quantity(
    allocated_capital=20000,
    entry_price=300,
    lot_size=65,
)

print(result)

assert result["Status"] == "RECONCILIATION_COMPLETE"
assert result["Reconciled Lots"] == 1
assert result["Reconciled Quantity"] == 65
assert result["Estimated Capital Required"] == 19500
assert result["Unused Allocated Capital"] == 500
assert result["Capital Ceiling Respected"] is True
assert result["Quantity Reconciled"] is True


# ---------------------------------------------------------
# TEST 2
# ₹30,000 allocation, ₹300 option, lot 65
# One lot costs ₹19,500; two lots cost ₹39,000.
# ---------------------------------------------------------
print("\nTEST 2 — Multiple Affordable Lots")

result = reconcile_capital_to_quantity(
    allocated_capital=30000,
    entry_price=300,
    lot_size=65,
)

print(result)

assert result["Status"] == "RECONCILIATION_COMPLETE"
assert result["Reconciled Lots"] == 1
assert result["Reconciled Quantity"] == 65
assert result["Estimated Capital Required"] == 19500
assert result["Unused Allocated Capital"] == 10500


# ---------------------------------------------------------
# TEST 3
# Allocation is insufficient for one complete lot.
# ---------------------------------------------------------
print("\nTEST 3 — Insufficient Capital For One Lot")

result = reconcile_capital_to_quantity(
    allocated_capital=20000,
    entry_price=350,
    lot_size=65,
)

print(result)

assert result["Status"] == "RECONCILIATION_BLOCKED"
assert result["Reconciled Lots"] == 0
assert result["Reconciled Quantity"] == 0
assert result["Quantity Reconciled"] is False


# ---------------------------------------------------------
# TEST 4
# Exact capital required for one lot.
# ---------------------------------------------------------
print("\nTEST 4 — Exact Lot Capital")

result = reconcile_capital_to_quantity(
    allocated_capital=19500,
    entry_price=300,
    lot_size=65,
)

print(result)

assert result["Status"] == "RECONCILIATION_COMPLETE"
assert result["Reconciled Lots"] == 1
assert result["Reconciled Quantity"] == 65
assert result["Estimated Capital Required"] == 19500
assert result["Unused Allocated Capital"] == 0


# ---------------------------------------------------------
# TEST 5
# Invalid zero allocation.
# ---------------------------------------------------------
print("\nTEST 5 — Zero Allocation")

result = reconcile_capital_to_quantity(
    allocated_capital=0,
    entry_price=300,
    lot_size=65,
)

print(result)

assert result["Status"] == "RECONCILIATION_BLOCKED"


# ---------------------------------------------------------
# TEST 6
# Invalid entry price.
# ---------------------------------------------------------
print("\nTEST 6 — Invalid Entry Price")

result = reconcile_capital_to_quantity(
    allocated_capital=20000,
    entry_price=0,
    lot_size=65,
)

print(result)

assert result["Status"] == "RECONCILIATION_BLOCKED"


# ---------------------------------------------------------
# TEST 7
# Invalid lot size.
# ---------------------------------------------------------
print("\nTEST 7 — Invalid Lot Size")

result = reconcile_capital_to_quantity(
    allocated_capital=20000,
    entry_price=300,
    lot_size=0,
)

print(result)

assert result["Status"] == "RECONCILIATION_BLOCKED"


print("\n==============================================")
print("ALL V17.7.1 TESTS PASSED")
print("==============================================")
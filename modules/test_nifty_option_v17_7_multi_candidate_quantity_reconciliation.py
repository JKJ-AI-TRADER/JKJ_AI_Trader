"""
JKJ AI Trader
V17.7.3 — Multi-Candidate Quantity Reconciliation Test
"""

from nifty_option_v17_7_multi_candidate_quantity_reconciliation import (
    reconcile_multi_candidate_quantities
)


print("\n==============================================")
print("JKJ V17.7.3 MULTI-CANDIDATE QUANTITY TEST")
print("==============================================")


# ---------------------------------------------------------
# Common V17.6.5 allocation result
#
# Candidate A:
#   Priority 1
#   Allocated ₹20,000
#
# Candidate B:
#   Priority 2
#   Allocated ₹10,000
# ---------------------------------------------------------

allocation_result = {
    "Status": "POLICY_ALLOCATION_COMPLETE",
    "Usable Capital": 30000,
    "Maximum Positions": 6,
    "Maximum Capital Per Candidate": 20000,
    "Minimum Candidate Allocation": 5000,
    "Allocations": [
        {
            "Candidate": "NIFTY CE A",
            "Priority": 1,
            "Requested Allocation": 20000,
            "Allocated Capital": 20000,
            "Allocation Status": "ALLOCATED",
        },
        {
            "Candidate": "NIFTY PE B",
            "Priority": 2,
            "Requested Allocation": 10000,
            "Allocated Capital": 10000,
            "Allocation Status": "ALLOCATED",
        },
    ],
    "Positions Allocated": 2,
    "Remaining Capital": 0.0,
    "Priority Source": "DECISION_RISK_LAYER",
    "Automatic Ranking": False,
}


# ---------------------------------------------------------
# TEST 1
# Both candidates are affordable.
#
# A: ₹20,000 / ₹300 / lot 65
# B: ₹10,000 / ₹100 / lot 65
# ---------------------------------------------------------

print("\nTEST 1 — Two Affordable Candidates")

candidate_market_data = [
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "CE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
    {
        "Candidate": "NIFTY PE B",
        "Entry Price": 100,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300PE",
            "Instrument Token": 14588163,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "PE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
]

result = reconcile_multi_candidate_quantities(
    allocation_result,
    candidate_market_data,
)

print(result)

assert result["Status"] == (
    "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
)
assert result["Successful Candidates"] == 2
assert result["Blocked Candidates"] == 0
assert result["Reconciliations"][0]["Candidate"] == "NIFTY CE A"
assert result["Reconciliations"][0]["Reconciled Quantity"] == 65
assert result["Reconciliations"][1]["Candidate"] == "NIFTY PE B"
assert result["Reconciliations"][1]["Reconciled Quantity"] == 65
assert result["Capital Reassignment"] is False
assert result["Order Placement Permitted"] is False


# ---------------------------------------------------------
# TEST 2
# Candidate B cannot afford one complete lot.
#
# B: ₹10,000 allocation
# Entry ₹200
# Lot 65
# One lot = ₹13,000
#
# B must be blocked.
# Its ₹10,000 must NOT be reassigned.
# ---------------------------------------------------------

print("\nTEST 2 — One Candidate Unaffordable")

candidate_market_data = [
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "CE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
    {
        "Candidate": "NIFTY PE B",
        "Entry Price": 200,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300PE",
            "Instrument Token": 14588163,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "PE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
]

result = reconcile_multi_candidate_quantities(
    allocation_result,
    candidate_market_data,
)

print(result)

assert result["Successful Candidates"] == 1
assert result["Blocked Candidates"] == 1
assert result["Reconciliations"][0]["Status"] == (
    "RECONCILIATION_COMPLETE"
)
assert result["Reconciliations"][1]["Status"] == (
    "RECONCILIATION_BLOCKED"
)
assert result["Reconciliations"][1]["Uncommitted Capital"] == 10000
assert result["Capital Reassignment"] is False


# ---------------------------------------------------------
# TEST 3
# Candidate market data missing.
#
# Allocated capital must remain uncommitted.
# ---------------------------------------------------------

print("\nTEST 3 — Missing Candidate Market Data")

candidate_market_data = [
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "CE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
]

result = reconcile_multi_candidate_quantities(
    allocation_result,
    candidate_market_data,
)

print(result)

assert result["Successful Candidates"] == 1
assert result["Blocked Candidates"] == 1
assert result["Reconciliations"][1]["Candidate"] == (
    "NIFTY PE B"
)
assert result["Reconciliations"][1]["Uncommitted Capital"] == 10000


# ---------------------------------------------------------
# TEST 4
# Contract validation fails.
# ---------------------------------------------------------

print("\nTEST 4 — Invalid Contract")

candidate_market_data = [
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_BLOCKED",
            "Lot Size": 65,
            "Contract Identity Valid": False,
            "Order Placement Permitted": False,
        },
    },
    {
        "Candidate": "NIFTY PE B",
        "Entry Price": 100,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300PE",
            "Instrument Token": 14588163,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "PE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
]

result = reconcile_multi_candidate_quantities(
    allocation_result,
    candidate_market_data,
)

print(result)

assert result["Successful Candidates"] == 1
assert result["Blocked Candidates"] == 1
assert result["Reconciliations"][0]["Status"] == (
    "RECONCILIATION_BLOCKED"
)
assert result["Reconciliations"][0]["Uncommitted Capital"] == 20000


# ---------------------------------------------------------
# TEST 5
# Candidate was not allocated by V17.6.5.
# It must not be reconciled into a position.
# ---------------------------------------------------------

print("\nTEST 5 — Unallocated Candidate")

allocation_with_unallocated = {
    **allocation_result,
    "Allocations": [
        {
            "Candidate": "NIFTY CE A",
            "Priority": 1,
            "Requested Allocation": 20000,
            "Allocated Capital": 20000,
            "Allocation Status": "ALLOCATED",
        },
        {
            "Candidate": "NIFTY PE B",
            "Priority": 2,
            "Requested Allocation": 10000,
            "Allocated Capital": 0,
            "Allocation Status": "UNALLOCATED",
        },
    ],
}

candidate_market_data = [
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "CE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
    {
        "Candidate": "NIFTY PE B",
        "Entry Price": 100,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Trading Symbol": "NIFTY2692223300PE",
            "Instrument Token": 14588163,
            "Expiry": "2026-09-22",
            "Strike": 23300.0,
            "Option Type": "PE",
            "Lot Size": 65,
            "Contract Identity Valid": True,
            "Order Placement Permitted": False,
        },
    },
]

result = reconcile_multi_candidate_quantities(
    allocation_with_unallocated,
    candidate_market_data,
)

print(result)

assert result["Successful Candidates"] == 1
assert result["Reconciliations"][1]["Status"] == (
    "NOT_ALLOCATED"
)
assert result["Reconciliations"][1]["Reconciled Quantity"] == 0


# ---------------------------------------------------------
# TEST 6
# Duplicate candidate market data must be blocked.
# ---------------------------------------------------------

print("\nTEST 6 — Duplicate Candidate Market Data")

candidate_market_data = [
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Lot Size": 65,
        },
    },
    {
        "Candidate": "NIFTY CE A",
        "Entry Price": 300,
        "Contract Validation": {
            "Status": "CONTRACT_VALIDATED",
            "Lot Size": 65,
        },
    },
]

result = reconcile_multi_candidate_quantities(
    allocation_result,
    candidate_market_data,
)

print(result)

assert result["Status"] == (
    "MULTI_CANDIDATE_RECONCILIATION_BLOCKED"
)


print("\n==============================================")
print("ALL V17.7.3 TESTS PASSED")
print("==============================================")
"""
JKJ AI Trader
V17.7.4 — Final Quantity Plan Validation Test
"""

from nifty_option_v17_7_final_quantity_plan_validation import (
    validate_final_quantity_plan,
)


def valid_candidate(
    candidate,
    priority,
    allocated_capital,
    entry_price,
    lot_size,
    symbol,
    token,
):
    quantity = lot_size
    required_capital = entry_price * quantity

    return {
        "Candidate": candidate,
        "Priority": priority,
        "Allocated Capital": allocated_capital,
        "Entry Price": entry_price,
        "Lot Size": lot_size,
        "Reconciled Lots": 1,
        "Reconciled Quantity": quantity,
        "Estimated Capital Required": required_capital,
        "Unused Allocated Capital": (
            allocated_capital - required_capital
        ),
        "Status": "RECONCILIATION_COMPLETE",
        "Trading Symbol": symbol,
        "Instrument Token": token,
        "Contract Identity Valid": True,
        "Order Placement Permitted": False,
    }


print("\n==============================================")
print("JKJ V17.7.4 FINAL QUANTITY PLAN TEST")
print("==============================================")

# ---------------------------------------------------------
# TEST 1 — Valid Two-Candidate Final Plan
# ---------------------------------------------------------
allocation_1 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 30000.0,
    "Total Reconciled Capital": 26000.0,
    "Total Uncommitted Capital": 4000.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        ),
        valid_candidate(
            "NIFTY PE B",
            2,
            10000.0,
            100.0,
            65,
            "NIFTY2692223300PE",
            14588163,
        ),
    ],
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
}

result = validate_final_quantity_plan(allocation_1)
print("\nTEST 1 — Valid Two-Candidate Final Plan")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_VALIDATED"
assert result["Validated Candidates"] == 2
assert result["Blocked Candidates"] == 0
assert result["Total Required Capital"] == 26000.0
assert result["Total Uncommitted Capital"] == 4000.0
assert result["Order Placement Permitted"] is False


# ---------------------------------------------------------
# TEST 2 — Required Capital Exceeds Allocation
# ---------------------------------------------------------
allocation_2 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 20000.0,
    "Total Reconciled Capital": 19500.0,
    "Total Uncommitted Capital": 500.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        )
    ],
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
}

allocation_2["Reconciliations"][0][
    "Estimated Capital Required"
] = 21000.0

result = validate_final_quantity_plan(allocation_2)
print("\nTEST 2 — Required Capital Exceeds Allocation")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_BLOCKED"


# ---------------------------------------------------------
# TEST 3 — Quantity Does Not Match Lot Size
# ---------------------------------------------------------
allocation_3 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 20000.0,
    "Total Reconciled Capital": 19500.0,
    "Total Uncommitted Capital": 500.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        )
    ],
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
}

allocation_3["Reconciliations"][0][
    "Reconciled Quantity"
] = 75

result = validate_final_quantity_plan(allocation_3)
print("\nTEST 3 — Quantity Does Not Match Lot Size")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_BLOCKED"


# ---------------------------------------------------------
# TEST 4 — Invalid Contract Identity
# ---------------------------------------------------------
allocation_4 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 20000.0,
    "Total Reconciled Capital": 19500.0,
    "Total Uncommitted Capital": 500.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        )
    ],
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
}

allocation_4["Reconciliations"][0][
    "Contract Identity Valid"
] = False

result = validate_final_quantity_plan(allocation_4)
print("\nTEST 4 — Invalid Contract Identity")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_BLOCKED"


# ---------------------------------------------------------
# TEST 5 — Capital Reassignment Detected
# ---------------------------------------------------------
allocation_5 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 20000.0,
    "Total Reconciled Capital": 19500.0,
    "Total Uncommitted Capital": 500.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        )
    ],
    "Capital Reassignment": True,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
}

result = validate_final_quantity_plan(allocation_5)
print("\nTEST 5 — Capital Reassignment Detected")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_BLOCKED"


# ---------------------------------------------------------
# TEST 6 — Automatic Ranking Detected
# ---------------------------------------------------------
allocation_6 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 20000.0,
    "Total Reconciled Capital": 19500.0,
    "Total Uncommitted Capital": 500.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        )
    ],
    "Capital Reassignment": False,
    "Automatic Ranking": True,
    "Priority Source": "DECISION_RISK_LAYER",
}

result = validate_final_quantity_plan(allocation_6)
print("\nTEST 6 — Automatic Ranking Detected")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_BLOCKED"


# ---------------------------------------------------------
# TEST 7 — Unallocated Candidate Preserved
# ---------------------------------------------------------
allocation_7 = {
    "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",
    "Total Allocated Capital": 20000.0,
    "Total Reconciled Capital": 19500.0,
    "Total Uncommitted Capital": 500.0,
    "Reconciliations": [
        valid_candidate(
            "NIFTY CE A",
            1,
            20000.0,
            300.0,
            65,
            "NIFTY2692223300CE",
            14588162,
        ),
        {
            "Candidate": "NIFTY PE B",
            "Priority": 2,
            "Allocated Capital": 0.0,
            "Status": "NOT_ALLOCATED",
            "Reconciled Quantity": 0,
            "Reconciled Lots": 0,
            "Allocation Status": "UNALLOCATED",
        },
    ],
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
}

result = validate_final_quantity_plan(allocation_7)
print("\nTEST 7 — Unallocated Candidate Preserved")
print(result)

assert result["Status"] == "FINAL_QUANTITY_PLAN_VALIDATED"
assert result["Validated Candidates"] == 1
assert result["Blocked Candidates"] == 0
assert result["Validation Results"][1]["Status"] == "NOT_ALLOCATED"


print("\n==============================================")
print("ALL V17.7.4 TESTS PASSED")
print("==============================================")
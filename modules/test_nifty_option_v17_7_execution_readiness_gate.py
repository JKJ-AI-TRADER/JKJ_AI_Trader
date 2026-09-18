"""
JKJ AI Trader
V17.7.5 — Execution Readiness Gate Test
"""

from nifty_option_v17_7_execution_readiness_gate import (
    validate_execution_readiness,
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
        "Status": "FINAL_QUANTITY_VALIDATED",
        "Validated": True,
        "Execution Eligible": True,
        "Trading Symbol": symbol,
        "Instrument Token": token,
        "Entry Price": entry_price,
        "Lot Size": lot_size,
        "Reconciled Lots": 1,
        "Reconciled Quantity": quantity,
        "Allocated Capital": allocated_capital,
        "Required Capital": required_capital,
        "Contract Identity Valid": True,
        "Order Placement Permitted": False,
    }


print("\n==============================================")
print("JKJ V17.7.5 EXECUTION READINESS GATE TEST")
print("==============================================")


# ---------------------------------------------------------
# TEST 1 — Valid Execution Readiness
# ---------------------------------------------------------
plan_1 = {
    "Status": "FINAL_QUANTITY_PLAN_VALIDATED",
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
    "Order Placement Permitted": False,
    "Validation Results": [
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
}

result = validate_execution_readiness(plan_1)

print("\nTEST 1 — Valid Execution Readiness")
print(result)

assert result["Status"] == "EXECUTION_READINESS_VALIDATED"
assert result["Execution Ready Candidates"] == 2
assert result["Order Placement Permitted"] is False


# ---------------------------------------------------------
# TEST 2 — V17.7.4 Not Validated
# ---------------------------------------------------------
plan_2 = dict(plan_1)
plan_2["Status"] = "FINAL_QUANTITY_PLAN_BLOCKED"

result = validate_execution_readiness(plan_2)

print("\nTEST 2 — V17.7.4 Not Validated")
print(result)

assert result["Status"] == "EXECUTION_READINESS_BLOCKED"


# ---------------------------------------------------------
# TEST 3 — Capital Reassignment Detected
# ---------------------------------------------------------
plan_3 = dict(plan_1)
plan_3["Capital Reassignment"] = True

result = validate_execution_readiness(plan_3)

print("\nTEST 3 — Capital Reassignment Detected")
print(result)

assert result["Status"] == "EXECUTION_READINESS_BLOCKED"


# ---------------------------------------------------------
# TEST 4 — Automatic Ranking Detected
# ---------------------------------------------------------
plan_4 = dict(plan_1)
plan_4["Automatic Ranking"] = True

result = validate_execution_readiness(plan_4)

print("\nTEST 4 — Automatic Ranking Detected")
print(result)

assert result["Status"] == "EXECUTION_READINESS_BLOCKED"


# ---------------------------------------------------------
# TEST 5 — Order Placement Accidentally Enabled
# ---------------------------------------------------------
plan_5 = dict(plan_1)
plan_5["Order Placement Permitted"] = True

result = validate_execution_readiness(plan_5)

print("\nTEST 5 — Order Placement Accidentally Enabled")
print(result)

assert result["Status"] == "EXECUTION_READINESS_BLOCKED"


# ---------------------------------------------------------
# TEST 6 — Invalid Quantity / Lot Relationship
# ---------------------------------------------------------
plan_6 = {
    "Status": "FINAL_QUANTITY_PLAN_VALIDATED",
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
    "Order Placement Permitted": False,
    "Validation Results": [
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
}

plan_6["Validation Results"][0]["Reconciled Quantity"] = 75

result = validate_execution_readiness(plan_6)

print("\nTEST 6 — Invalid Quantity / Lot Relationship")
print(result)

assert result["Status"] == "EXECUTION_READINESS_BLOCKED"


# ---------------------------------------------------------
# TEST 7 — Invalid Contract Identity
# ---------------------------------------------------------
plan_7 = {
    "Status": "FINAL_QUANTITY_PLAN_VALIDATED",
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
    "Order Placement Permitted": False,
    "Validation Results": [
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
}

plan_7["Validation Results"][0][
    "Contract Identity Valid"
] = False

result = validate_execution_readiness(plan_7)

print("\nTEST 7 — Invalid Contract Identity")
print(result)

assert result["Status"] == "EXECUTION_READINESS_BLOCKED"


# ---------------------------------------------------------
# TEST 8 — Unallocated Candidate Cannot Become Executable
# ---------------------------------------------------------
plan_8 = {
    "Status": "FINAL_QUANTITY_PLAN_VALIDATED",
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
    "Order Placement Permitted": False,
    "Validation Results": [
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
            "Status": "NOT_ALLOCATED",
            "Validated": False,
            "Execution Eligible": False,
            "Order Placement Permitted": False,
        },
    ],
}

result = validate_execution_readiness(plan_8)

print("\nTEST 8 — Unallocated Candidate Cannot Become Executable")
print(result)

assert result["Status"] == "EXECUTION_READINESS_VALIDATED"
assert result["Execution Ready Candidates"] == 1


# ---------------------------------------------------------
# TEST 9 — Blocked Candidate Cannot Become Executable
# ---------------------------------------------------------
plan_9 = {
    "Status": "FINAL_QUANTITY_PLAN_VALIDATED",
    "Capital Reassignment": False,
    "Automatic Ranking": False,
    "Priority Source": "DECISION_RISK_LAYER",
    "Order Placement Permitted": False,
    "Validation Results": [
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
            "Status": "BLOCKED",
            "Validated": False,
            "Execution Eligible": False,
            "Order Placement Permitted": False,
        },
    ],
}

result = validate_execution_readiness(plan_9)

print("\nTEST 9 — Blocked Candidate Cannot Become Executable")
print(result)

assert result["Status"] == "EXECUTION_READINESS_VALIDATED"
assert result["Execution Ready Candidates"] == 1
assert result["Blocked Candidates"] == 1


print("\n==============================================")
print("ALL V17.7.5 TESTS PASSED")
print("==============================================")
"""
JKJ AI Trader
V17.7.6 — Execution Request Specification Test
"""

from nifty_option_v17_7_execution_request_specification import (
    create_execution_request,
)


def valid_candidate():
    return {
        "Candidate": "NIFTY CE A",
        "Priority": 1,
        "Trading Symbol": "NIFTY2692223300CE",
        "Instrument Token": 14588162,
        "Entry Price": 300.0,
        "Lot Size": 65,
        "Reconciled Lots": 1,
        "Reconciled Quantity": 65,
        "Allocated Capital": 20000.0,
        "Required Capital": 19500.0,
        "Contract Identity Valid": True,
        "Validated": True,
        "Execution Ready": True,
        "Order Placement Permitted": False,
    }


print("\n==============================================")
print("JKJ V17.7.6 EXECUTION REQUEST SPECIFICATION TEST")
print("==============================================")


# ---------------------------------------------------------
# TEST 1 — Valid MARKET / MIS BUY Request
# ---------------------------------------------------------
result = create_execution_request(
    valid_candidate(),
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 1 — Valid MARKET / MIS BUY Request")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_SPECIFIED"
assert result["Execution Request"]["Transaction Type"] == "BUY"
assert result["Execution Request"]["Order Type"] == "MARKET"
assert result["Execution Request"]["Product"] == "MIS"
assert result["Execution Request"]["Quantity"] == 65
assert result["Order Placement Permitted"] is False
assert result["Broker Communication"] is False


# ---------------------------------------------------------
# TEST 2 — Valid LIMIT / NRML BUY Request
# ---------------------------------------------------------
result = create_execution_request(
    valid_candidate(),
    order_type="LIMIT",
    product="NRML",
    transaction_type="BUY",
)

print("\nTEST 2 — Valid LIMIT / NRML BUY Request")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_SPECIFIED"
assert result["Execution Request"]["Order Type"] == "LIMIT"
assert result["Execution Request"]["Product"] == "NRML"
assert result["Order Placement Permitted"] is False


# ---------------------------------------------------------
# TEST 3 — SELL Transaction Blocked
# ---------------------------------------------------------
result = create_execution_request(
    valid_candidate(),
    order_type="MARKET",
    product="MIS",
    transaction_type="SELL",
)

print("\nTEST 3 — SELL Transaction Blocked")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 4 — Invalid Order Type Blocked
# ---------------------------------------------------------
result = create_execution_request(
    valid_candidate(),
    order_type="SL-M",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 4 — Invalid Order Type Blocked")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 5 — Invalid Product Blocked
# ---------------------------------------------------------
result = create_execution_request(
    valid_candidate(),
    order_type="MARKET",
    product="INVALID",
    transaction_type="BUY",
)

print("\nTEST 5 — Invalid Product Blocked")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 6 — Candidate Not Execution Ready
# ---------------------------------------------------------
candidate_6 = valid_candidate()
candidate_6["Execution Ready"] = False

result = create_execution_request(
    candidate_6,
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 6 — Candidate Not Execution Ready")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 7 — Invalid Quantity Blocked
# ---------------------------------------------------------
candidate_7 = valid_candidate()
candidate_7["Reconciled Quantity"] = 75

result = create_execution_request(
    candidate_7,
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 7 — Invalid Quantity Blocked")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 8 — Invalid Contract Blocked
# ---------------------------------------------------------
candidate_8 = valid_candidate()
candidate_8["Contract Identity Valid"] = False

result = create_execution_request(
    candidate_8,
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 8 — Invalid Contract Blocked")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 9 — Order Placement Accidentally Enabled
# ---------------------------------------------------------
candidate_9 = valid_candidate()
candidate_9["Order Placement Permitted"] = True

result = create_execution_request(
    candidate_9,
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 9 — Order Placement Accidentally Enabled")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 10 — Required Capital Exceeds Allocation
# ---------------------------------------------------------
candidate_10 = valid_candidate()
candidate_10["Required Capital"] = 21000.0

result = create_execution_request(
    candidate_10,
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 10 — Required Capital Exceeds Allocation")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 11 — Broker Communication Must Remain Disabled
# ---------------------------------------------------------
result = create_execution_request(
    valid_candidate(),
    order_type="MARKET",
    product="MIS",
    transaction_type="BUY",
)

print("\nTEST 11 — Broker Communication Must Remain Disabled")
print(result)

assert result["Status"] == "EXECUTION_REQUEST_SPECIFIED"
assert result["Broker Communication"] is False
assert result["Order Placement Permitted"] is False


print("\n==============================================")
print("ALL V17.7.6 TESTS PASSED")
print("==============================================")
"""
JKJ AI Trader
V17.7.7 — Broker Execution Adapter Boundary Test
"""

from nifty_option_v17_7_broker_execution_adapter import (
    prepare_broker_request,
)


def valid_execution_request():
    return {
        "Status": "EXECUTION_REQUEST_SPECIFIED",
        "Execution Request": {
            "Candidate": "NIFTY CE A",
            "Priority": 1,
            "Priority Source": "DECISION_RISK_LAYER",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Transaction Type": "BUY",
            "Order Type": "MARKET",
            "Product": "MIS",
            "Quantity": 65,
            "Lot Size": 65,
            "Entry Price Reference": 300.0,
            "Allocated Capital": 20000.0,
            "Required Capital": 19500.0,
            "Contract Identity Valid": True,
            "Execution Ready": True,
            "Order Placement Permitted": False,
            "Broker Communication": False,
        },
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Broker Communication": False,
    }


print("\n==============================================")
print("JKJ V17.7.7 BROKER EXECUTION ADAPTER TEST")
print("==============================================")


# ---------------------------------------------------------
# TEST 1 — Valid MARKET / MIS Request
# ---------------------------------------------------------
result = prepare_broker_request(
    valid_execution_request()
)

print("\nTEST 1 — Valid MARKET / MIS Request")
print(result)

assert result["Status"] == "BROKER_REQUEST_PREPARED"
assert result["Broker Request"]["tradingsymbol"] == (
    "NIFTY2692223300CE"
)
assert result["Broker Request"]["quantity"] == 65
assert result["Broker Request"]["transaction_type"] == "BUY"
assert result["Broker Request"]["order_type"] == "MARKET"
assert result["Broker Request"]["product"] == "MIS"
assert result["Dry Run"] is True
assert result["Broker Communication"] is False
assert result["Order Placement Permitted"] is False


# ---------------------------------------------------------
# TEST 2 — Valid LIMIT / NRML Request
# ---------------------------------------------------------
request_2 = valid_execution_request()
request_2["Execution Request"]["Order Type"] = "LIMIT"
request_2["Execution Request"]["Product"] = "NRML"

result = prepare_broker_request(request_2)

print("\nTEST 2 — Valid LIMIT / NRML Request")
print(result)

assert result["Status"] == "BROKER_REQUEST_PREPARED"
assert result["Broker Request"]["order_type"] == "LIMIT"
assert result["Broker Request"]["product"] == "NRML"


# ---------------------------------------------------------
# TEST 3 — Execution Request Not Specified
# ---------------------------------------------------------
request_3 = valid_execution_request()
request_3["Status"] = "EXECUTION_REQUEST_BLOCKED"

result = prepare_broker_request(request_3)

print("\nTEST 3 — Execution Request Not Specified")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 4 — Broker Communication Accidentally Enabled
# ---------------------------------------------------------
request_4 = valid_execution_request()
request_4["Broker Communication"] = True

result = prepare_broker_request(request_4)

print("\nTEST 4 — Broker Communication Accidentally Enabled")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 5 — Order Placement Accidentally Enabled
# ---------------------------------------------------------
request_5 = valid_execution_request()
request_5["Order Placement Permitted"] = True

result = prepare_broker_request(request_5)

print("\nTEST 5 — Order Placement Accidentally Enabled")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 6 — Capital Reassignment Detected
# ---------------------------------------------------------
request_6 = valid_execution_request()
request_6["Capital Reassignment"] = True

result = prepare_broker_request(request_6)

print("\nTEST 6 — Capital Reassignment Detected")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 7 — Automatic Ranking Detected
# ---------------------------------------------------------
request_7 = valid_execution_request()
request_7["Automatic Ranking"] = True

result = prepare_broker_request(request_7)

print("\nTEST 7 — Automatic Ranking Detected")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 8 — Invalid Quantity
# ---------------------------------------------------------
request_8 = valid_execution_request()
request_8["Execution Request"]["Quantity"] = 75

result = prepare_broker_request(request_8)

print("\nTEST 8 — Invalid Quantity")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 9 — Invalid Contract Identity
# ---------------------------------------------------------
request_9 = valid_execution_request()
request_9["Execution Request"][
    "Contract Identity Valid"
] = False

result = prepare_broker_request(request_9)

print("\nTEST 9 — Invalid Contract Identity")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 10 — Invalid Transaction Type
# ---------------------------------------------------------
request_10 = valid_execution_request()
request_10["Execution Request"][
    "Transaction Type"
] = "SELL"

result = prepare_broker_request(request_10)

print("\nTEST 10 — Invalid Transaction Type")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 11 — Required Capital Exceeds Allocation
# ---------------------------------------------------------
request_11 = valid_execution_request()
request_11["Execution Request"][
    "Required Capital"
] = 21000.0

result = prepare_broker_request(request_11)

print("\nTEST 11 — Required Capital Exceeds Allocation")
print(result)

assert result["Status"] == "BROKER_REQUEST_BLOCKED"


# ---------------------------------------------------------
# TEST 12 — Broker Payload Must Preserve Quantity
# ---------------------------------------------------------
result = prepare_broker_request(
    valid_execution_request()
)

print("\nTEST 12 — Broker Payload Must Preserve Quantity")
print(result)

assert result["Status"] == "BROKER_REQUEST_PREPARED"
assert result["Broker Request"]["quantity"] == 65
assert result["Quantity"] == 65


# ---------------------------------------------------------
# TEST 13 — Dry Run Must Remain True
# ---------------------------------------------------------
result = prepare_broker_request(
    valid_execution_request()
)

print("\nTEST 13 — Dry Run Must Remain True")
print(result)

assert result["Status"] == "BROKER_REQUEST_PREPARED"
assert result["Dry Run"] is True
assert result["Broker Request"]["dry_run"] is True
assert result["Broker Communication"] is False
assert result["Broker Request"][
    "broker_communication"
] is False


print("\n==============================================")
print("ALL V17.7.7 TESTS PASSED")
print("==============================================")
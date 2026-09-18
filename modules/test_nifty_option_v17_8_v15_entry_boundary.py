"""
JKJ AI Trader
V17.8.6 Tests - V15 Entry Boundary Validation
"""

from nifty_option_v17_8_v15_entry_boundary import (
    validate_v15_entry_boundary,
)


def valid_entry():
    return {
        "Status": "MAPPED",
        "Trade ID": "JKJ-PAPER-TRADE-001",
        "Paper Fill ID": "JKJ-PAPER-FILL-001",
        "Paper Order ID": "JKJ-PAPER-ORDER-001",
        "Trading Symbol": "NIFTY2692223300CE",
        "Instrument Type": "OPTION",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Entry Price": 305,
        "Qualified Entry Price": 300,
        "Quantity": 65,
        "Stop Loss": 270,
        "Target": 330,
        "Target1": 330,
        "Target2": 360,
        "Target3": 390,
        "RR1": 1.0,
        "RR2": 2.0,
        "RR3": 3.0,
        "Entry Status": "QUALIFIED",
        "Entry Reason": "V14.5 exit-qualified setup",
        "Paper Trade Permission": "PERMITTED",
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }


def assert_blocked(result):
    assert result["Status"] == "V15_ENTRY_BOUNDARY_BLOCKED"
    assert result["V15 Entry Payload"] is None
    assert result["V15 Call Permitted"] is False
    assert result["V11 Call Permitted"] is False


# 1. Valid boundary
result = validate_v15_entry_boundary(valid_entry())
assert result["Status"] == "V15_ENTRY_BOUNDARY_VALIDATED"
assert result["V15 Entry Payload"]["Entry Price"] == 305
assert result["V15 Entry Payload"]["Stop Loss"] == 270
assert result["V15 Entry Payload"]["Target1"] == 330

# 2. V15 is not actually called
assert result["V15 Call Permitted"] is False

# 3. V11 is not actually called
assert result["V11 Call Permitted"] is False

# 4. Broker communication remains blocked
assert result["Broker Communication"] is False

# 5. Live order placement remains blocked
assert result["Order Placement Permitted"] is False

# 6. Missing Trade ID
test = valid_entry()
del test["Trade ID"]
assert_blocked(validate_v15_entry_boundary(test))

# 7. Wrong instrument type
test = valid_entry()
test["Instrument Type"] = "EQUITY"
assert_blocked(validate_v15_entry_boundary(test))

# 8. Permission blocked
test = valid_entry()
test["Paper Trade Permission"] = "BLOCKED"
assert_blocked(validate_v15_entry_boundary(test))

# 9. Invalid contract
test = valid_entry()
test["Contract Valid"] = False
assert_blocked(validate_v15_entry_boundary(test))

# 10. Execution not ready
test = valid_entry()
test["Execution Ready"] = False
assert_blocked(validate_v15_entry_boundary(test))

# 11. Invalid quantity
test = valid_entry()
test["Quantity"] = 0
assert_blocked(validate_v15_entry_boundary(test))

# 12. Target must remain Target1
test = valid_entry()
test["Target"] = 350
assert_blocked(validate_v15_entry_boundary(test))

# 13. Broker communication attempt
test = valid_entry()
test["Broker Communication"] = True
assert_blocked(validate_v15_entry_boundary(test))

# 14. Live order permission attempt
test = valid_entry()
test["Order Placement Permitted"] = True
assert_blocked(validate_v15_entry_boundary(test))

# 15. Missing risk field
test = valid_entry()
del test["Stop Loss"]
assert_blocked(validate_v15_entry_boundary(test))

print("ALL V17.8.6 TESTS PASSED")
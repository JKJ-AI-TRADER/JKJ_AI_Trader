"""
JKJ AI Trader
V17.8.7 Tests - Controlled V15 Paper-Trade Handoff
"""

from modules.nifty_option_v17_8_v15_paper_handoff import (
    handoff_to_v15_paper_trade,
)


def valid_mapped_entry():
    return {
        "Status": "MAPPED",
        "Trade ID": "JKJ-V1787-TEST-001",
        "Paper Fill ID": "JKJ-PAPER-FILL-001",
        "Paper Order ID": "JKJ-PAPER-ORDER-001",
        "Trading Symbol": "NIFTY26SEP25000CE",
        "Instrument Type": "OPTION",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 25000,
        "Option Type": "CE",
        "Entry Price": 105.0,
        "Qualified Entry Price": 103.0,
        "Quantity": 65,
        "Stop Loss": 100.0,
        "Target": 106.0,
        "Target1": 106.0,
        "Target2": 109.0,
        "Target3": 112.0,
        "RR1": 1.0,
        "RR2": 2.0,
        "RR3": 3.0,
        "Entry Status": "ENTRY_QUALIFIED",
        "Entry Reason": "V14.5 exit-qualified setup",
        "Paper Trade Permission": "PERMITTED",
        "Contract Valid": True,
        "Execution Ready": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
    }


def valid_v14_5_exit_qualification():
    return {
        "Status": "EVALUATED",

        "Trading Symbol": "NIFTY26SEP25000CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 25000,
        "Option Type": "CE",

        "Entry Price": 103.0,
        "Stop Price": 100.0,

        "Target 1": 106.0,
        "Target 2": 109.0,
        "Target 3": 112.0,

        "Risk Reward 1": 1.0,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,

        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }


def assert_blocked(result):
    assert result["Status"] == "V15_PAPER_HANDOFF_BLOCKED"
    assert result["V15 Handoff"] is None
    assert result["V15 Call Permitted"] is False
    assert result["V11 Call Permitted"] is False


# 1. Invalid V14.5 status must be blocked
test = valid_v14_5_exit_qualification()
test["Status"] = "QUALIFIED"

result = handoff_to_v15_paper_trade(
    valid_mapped_entry(),
    test,
)

assert_blocked(result)


# 2. Symbol mismatch must be blocked
test = valid_v14_5_exit_qualification()
test["Trading Symbol"] = "NIFTY26SEP25000PE"

result = handoff_to_v15_paper_trade(
    valid_mapped_entry(),
    test,
)

assert_blocked(result)


# 3. Missing V14.5 risk context must be blocked
test = valid_v14_5_exit_qualification()
del test["Entry Risk Context"]

result = handoff_to_v15_paper_trade(
    valid_mapped_entry(),
    test,
)

assert_blocked(result)


# 4. Valid V14.5 → V15.3 → V11 paper handoff
result = handoff_to_v15_paper_trade(
    valid_mapped_entry(),
    valid_v14_5_exit_qualification(),
    entry_time="2026-09-21 10:00:00",
)

assert result["Status"] == "V17_8_7_PAPER_HANDOFF_COMPLETE"
assert result["Stage"] == "V15.3"

assert result["V15 Handoff"] is True
assert result["V15 Call Permitted"] is True
assert result["V11 Call Permitted"] is True

assert result["Paper Execution"] is True
assert result["Broker Communication"] is False
assert result["Order Placement Permitted"] is False

assert result["Trade"] is not None
assert result["Trade"]["Status"] == "OPEN"

# V14.5 qualified price remains authoritative for V11.
assert result["Qualified Entry Price"] == 103.0

# V17.8 simulated fill remains separately recorded.
assert result["Paper Fill Price"] == 105.0

# Existing V11 paper trade uses V15/V14.5 qualified price.
assert result["Trade"]["Entry Price"] == 103.0

print("V11 TRADE RECORD:")
print(result["Trade"])


# 5. V14.5 risk/exit structure survives the handoff
qualification = result["Paper Trade Qualification"]

assert qualification["Status"] == "QUALIFIED"
assert qualification["Entry Price"] == 103.0
assert qualification["Stop Price"] == 100.0
assert qualification["Target 1"] == 106.0
assert qualification["Target 2"] == 109.0
assert qualification["Target 3"] == 112.0

assert qualification["Entry Risk Context"] == (
    "CONTROLLED_RISK_CONTEXT"
)

assert qualification["Stop-Loss Context"] == (
    "STOP_SUPPORTED"
)

assert qualification["Exit Structure"] == (
    "EXIT_STRUCTURE_SUPPORTED"
)


# 6. Safety remains intact
assert result["Capital Reassignment"] is False
assert result["Automatic Ranking"] is False
assert result["Broker Communication"] is False
assert result["Order Placement Permitted"] is False


print("ALL V17.8.7 TESTS PASSED")

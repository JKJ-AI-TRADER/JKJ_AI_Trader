"""
JKJ AI Trader
Intraday Option Paper Coordinator V9 Test

Wisdom Before Wealth.

Purpose:
Test the V9 Option Paper Coordinator independently.

No broker.
No Zerodha.
No live orders.
"""

from modules.intraday_option_paper_coordinator import (
    open_option_paper_position
)


# ---------------------------------------------------------
# TEST HELPERS
# ---------------------------------------------------------

def strong_entry_result():
    return {
        "Status": "READY",
        "Decision": "STRONG ENTRY CANDIDATE",
        "Momentum Score": 90,
    }


def normal_entry_result():
    return {
        "Status": "READY",
        "Decision": "ENTRY CANDIDATE",
        "Momentum Score": 82,
    }


def no_trade_result():
    return {
        "Status": "READY",
        "Decision": "NO TRADE",
        "Momentum Score": 70,
    }


# ---------------------------------------------------------
# TEST 1 — STRONG OPTION PAPER ENTRY
# ---------------------------------------------------------

print()
print("TEST 1 — STRONG OPTION PAPER ENTRY")
print("-" * 55)

result = open_option_paper_position(
    entry_result=strong_entry_result(),
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    entry_price=100.00,
    quantity=75,
    stop_loss_price=95.00,
    target_price=112.50,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Trading Symbol:", result["Trading Symbol"])
print("Option Type:", result["Option Type"])
print("Entry Price:", result["Entry Price"])
print("Quantity:", result["Quantity"])
print("Stop Loss:", result["Stop Loss"])
print("Target Price:", result["Target Price"])

assert result["Status"] == "READY"
assert result["Decision"] == "PAPER TRADE OPENED"
assert result["Trading Symbol"] == "NIFTY15SEP2623300CE"
assert result["Option Type"] == "CE"
assert result["Entry Price"] == 100.00
assert result["Quantity"] == 75
assert result["Stop Loss"] == 95.00
assert result["Target Price"] == 112.50
assert isinstance(result["Paper Trade"], dict)

print("PASS")


# ---------------------------------------------------------
# TEST 2 — NORMAL OPTION PAPER ENTRY
# ---------------------------------------------------------

print()
print("TEST 2 — NORMAL OPTION PAPER ENTRY")
print("-" * 55)

result = open_option_paper_position(
    entry_result=normal_entry_result(),
    trading_symbol="NIFTY15SEP2623400PE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23400,
    option_type="PE",
    entry_price=120.00,
    quantity=75,
    stop_loss_price=114.00,
    target_price=132.00,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "READY"
assert result["Decision"] == "PAPER TRADE OPENED"
assert result["Option Type"] == "PE"
assert result["Quantity"] == 75

print("PASS")


# ---------------------------------------------------------
# TEST 3 — NO TRADE MUST NOT OPEN PAPER POSITION
# ---------------------------------------------------------

print()
print("TEST 3 — NO TRADE MUST NOT OPEN PAPER POSITION")
print("-" * 55)

result = open_option_paper_position(
    entry_result=no_trade_result(),
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    entry_price=100.00,
    quantity=75,
    stop_loss_price=95.00,
    target_price=112.50,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"
assert "Paper Trade" not in result

print("PASS")


# ---------------------------------------------------------
# TEST 4 — INVALID ENTRY RESULT
# ---------------------------------------------------------

print()
print("TEST 4 — INVALID ENTRY RESULT")
print("-" * 55)

result = open_option_paper_position(
    entry_result="INVALID",
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    entry_price=100.00,
    quantity=75,
    stop_loss_price=95.00,
    target_price=112.50,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — INVALID OPTION TYPE
# ---------------------------------------------------------

print()
print("TEST 5 — INVALID OPTION TYPE")
print("-" * 55)

result = open_option_paper_position(
    entry_result=strong_entry_result(),
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="XX",
    entry_price=100.00,
    quantity=75,
    stop_loss_price=95.00,
    target_price=112.50,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 6 — INVALID QUANTITY
# ---------------------------------------------------------

print()
print("TEST 6 — INVALID QUANTITY")
print("-" * 55)

result = open_option_paper_position(
    entry_result=strong_entry_result(),
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    entry_price=100.00,
    quantity=0,
    stop_loss_price=95.00,
    target_price=112.50,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 7 — INVALID STOP LOSS
# ---------------------------------------------------------

print()
print("TEST 7 — INVALID STOP LOSS")
print("-" * 55)

result = open_option_paper_position(
    entry_result=strong_entry_result(),
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    entry_price=100.00,
    quantity=75,
    stop_loss_price=105.00,
    target_price=112.50,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 8 — INVALID TARGET
# ---------------------------------------------------------

print()
print("TEST 8 — INVALID TARGET")
print("-" * 55)

result = open_option_paper_position(
    entry_result=strong_entry_result(),
    trading_symbol="NIFTY15SEP2623300CE",
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    entry_price=100.00,
    quantity=75,
    stop_loss_price=95.00,
    target_price=98.00,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# COMPLETE
# ---------------------------------------------------------

print()
print("=" * 55)
print("JKJ OPTION PAPER COORDINATOR V9 TEST COMPLETE")
print("=" * 55)
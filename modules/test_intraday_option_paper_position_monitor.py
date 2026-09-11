"""
JKJ AI Trader
Intraday Option Paper Position Monitor V10 Test

Wisdom Before Wealth.

No broker.
No Zerodha.
No live orders.
"""

from intraday_option_paper_position_monitor import (
    monitor_option_paper_position
)


# ---------------------------------------------------------
# HELPER — OPEN PAPER POSITION
# ---------------------------------------------------------

def open_test_trade(
    entry_price=100.00,
    quantity=75,
    stop_loss=95.00,
    target=120.00,
    peak_price=100.00,
):
    return {
        "Trade ID": "TEST-OPTION-001",
        "Status": "OPEN",
        "Symbol": "NIFTY15SEP2623300CE",
        "Instrument Type": "OPTION",
        "Expiry": "2026-09-15",
        "Strike": 23300,
        "Option Type": "CE",
        "Underlying": "NIFTY",

        "Entry Price": entry_price,
        "Original Quantity": quantity,
        "Current Quantity": quantity,

        "Stop Loss": stop_loss,
        "Target": target,

        "Momentum Score": 90,
        "Entry Status": "STRONG ENTRY CANDIDATE",
        "Entry Reason": "TEST",

        "Peak Price": peak_price,
        "Peak Profit %": 0.0,

        "Gross P&L": 0.0,
        "Trading Costs": 0.0,
        "Slippage": 0.0,
        "Net P&L": 0.0,

        "Exit Events": [],
        "Notes": [],
    }


# ---------------------------------------------------------
# TEST 1 — HEALTHY POSITION
# ---------------------------------------------------------

print()
print("TEST 1 — HEALTHY POSITION")
print("-" * 55)

trade = open_test_trade()

result = monitor_option_paper_position(
    trade=trade,
    current_price=101.00,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Peak Price:", result["Peak Price"])

assert result["Status"] == "READY"
assert result["Decision"] == "HOLD"
assert result["Peak Price"] == 101.00

print("PASS")


# ---------------------------------------------------------
# TEST 2 — PROFIT PROTECTION
# ---------------------------------------------------------

print()
print("TEST 2 — PROFIT PROTECTION")
print("-" * 55)

trade = open_test_trade(
    peak_price=105.00
)

result = monitor_option_paper_position(
    trade=trade,
    current_price=104.00,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Profit Protection Result:", result["Profit Protection Result"])
print("Exit Result:", result["Exit Result"])
print(
    "Profit Protection:",
    result["Profit Protection Result"]["Status"]
)

assert result["Status"] == "READY"
assert result["Decision"] in (
    "HOLD",
    "PARTIAL EXIT"
)

print("PASS")


# ---------------------------------------------------------
# TEST 3 — PROFITABLE POSITION WEAKENING
# ---------------------------------------------------------

print()
print("TEST 3 — PROFITABLE POSITION WEAKENING")
print("-" * 55)

trade = open_test_trade(
    peak_price=120.00
)

result = monitor_option_paper_position(
    trade=trade,
    current_price=117.00,
    momentum_status="WEAK",
    volume_status="DECREASING",
    underlying_status="DETERIORATING",
    structure_status="DETERIORATING",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Profit Protection Result:", result["Profit Protection Result"])
print("Exit Result:", result["Exit Result"])

assert result["Status"] == "READY"
assert result["Decision"] in (
    "EXIT",
    "PARTIAL EXIT"
)

print("PASS")


# ---------------------------------------------------------
# TEST 4 — STOP LOSS
# ---------------------------------------------------------

print()
print("TEST 4 — STOP LOSS")
print("-" * 55)

trade = open_test_trade(
    stop_loss=95.00
)

result = monitor_option_paper_position(
    trade=trade,
    current_price=94.00,
    momentum_status="WEAK",
    volume_status="DECREASING",
    underlying_status="DETERIORATING",
    structure_status="DETERIORATING",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "READY"
assert result["Decision"] == "EXIT"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — TARGET REACHED
# ---------------------------------------------------------

print()
print("TEST 5 — TARGET REACHED")
print("-" * 55)

trade = open_test_trade(
    target=120.00
)

result = monitor_option_paper_position(
    trade=trade,
    current_price=120.00,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "READY"
assert result["Decision"] == "EXIT"

print("PASS")


# ---------------------------------------------------------
# TEST 6 — PARTIAL EXIT / SLICING
# ---------------------------------------------------------

print()
print("TEST 6 — PARTIAL EXIT / SLICING")
print("-" * 55)

trade = open_test_trade(
    peak_price=110.00
)

result = monitor_option_paper_position(
    trade=trade,
    current_price=108.00,
    momentum_status="WEAK",
    volume_status="DECREASING",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print(
    "Slice Decision:",
    result["Slice Result"]["Slice Decision"]
)

assert result["Status"] == "READY"

if result["Decision"] == "PARTIAL EXIT":
    assert result["Slice Result"]["Slice Quantity"] > 0

print("PASS")


# ---------------------------------------------------------
# TEST 7 — INVALID TRADE
# ---------------------------------------------------------

print()
print("TEST 7 — INVALID TRADE")
print("-" * 55)

result = monitor_option_paper_position(
    trade="INVALID",
    current_price=105.00,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 8 — INVALID CURRENT PRICE
# ---------------------------------------------------------

print()
print("TEST 8 — INVALID CURRENT PRICE")
print("-" * 55)

trade = open_test_trade()

result = monitor_option_paper_position(
    trade=trade,
    current_price=0,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "INVALID"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# COMPLETE
# ---------------------------------------------------------

print()
print("=" * 55)
print("JKJ OPTION PAPER POSITION MONITOR V10 TEST COMPLETE")
print("=" * 55)
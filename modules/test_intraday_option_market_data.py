"""
JKJ AI Trader
Test — Intraday Option Market Data Provider V3
"""

from modules.intraday_option_market_data import (
    create_option_market_data
)


print("=" * 45)
print("JKJ OPTION MARKET DATA V3 TEST")
print("=" * 45)


# ---------------------------------------------------------
# TEST 1 — VALID CE MARKET DATA
# ---------------------------------------------------------

print()
print("TEST 1 — VALID CE MARKET DATA")
print("-" * 45)

result = create_option_market_data(
    trading_symbol="NIFTY15SEP2623300CE",
    instrument_token=111113,
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    current_price=125.50,
    open_price=100.00,
    high_price=130.00,
    low_price=98.00,
    volume=250000,
    timestamp="2026-09-11T10:00:00"
)

print("Status:", result["Status"])
print("Trading Symbol:", result["Trading Symbol"])
print("Current Price:", result["Current Price"])
print("Price Change %:", result["Price Change %"])
print("Intraday Range %:", result["Intraday Range %"])
print("Volume:", result["Volume"])

assert result["Status"] == "READY"
assert result["Data Status"] == "VALID"
assert result["Option Type"] == "CE"
assert result["Current Price"] == 125.50
assert result["Price Change"] == 25.50
assert result["Price Change %"] == 25.5
assert result["Intraday Range"] == 32.0
assert result["Volume"] == 250000

print("PASS")


# ---------------------------------------------------------
# TEST 2 — VALID PE MARKET DATA
# ---------------------------------------------------------

print()
print("TEST 2 — VALID PE MARKET DATA")
print("-" * 45)

result = create_option_market_data(
    trading_symbol="NIFTY15SEP2623300PE",
    instrument_token=111114,
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="PE",
    current_price=175.00,
    open_price=150.00,
    high_price=180.00,
    low_price=145.00,
    volume=350000,
    timestamp="2026-09-11T10:01:00"
)

print("Status:", result["Status"])
print("Trading Symbol:", result["Trading Symbol"])
print("Option Type:", result["Option Type"])
print("Current Price:", result["Current Price"])
print("Price Change %:", result["Price Change %"])

assert result["Status"] == "READY"
assert result["Option Type"] == "PE"
assert result["Current Price"] == 175.00
assert result["Price Change %"] == 16.6667

print("PASS")


# ---------------------------------------------------------
# TEST 3 — NEGATIVE PRICE MOVEMENT
# ---------------------------------------------------------

print()
print("TEST 3 — NEGATIVE PRICE MOVEMENT")
print("-" * 45)

result = create_option_market_data(
    trading_symbol="NIFTY15SEP2623400CE",
    instrument_token=111115,
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23400,
    option_type="CE",
    current_price=80.00,
    open_price=100.00,
    high_price=105.00,
    low_price=75.00,
    volume=150000,
    timestamp="2026-09-11T10:02:00"
)

print("Status:", result["Status"])
print("Price Change:", result["Price Change"])
print("Price Change %:", result["Price Change %"])

assert result["Status"] == "READY"
assert result["Price Change"] == -20.0
assert result["Price Change %"] == -20.0

print("PASS")


# ---------------------------------------------------------
# TEST 4 — INVALID OPTION TYPE
# ---------------------------------------------------------

print()
print("TEST 4 — INVALID OPTION TYPE")
print("-" * 45)

result = create_option_market_data(
    trading_symbol="NIFTY15SEP2623300XX",
    instrument_token=111116,
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="XX",
    current_price=100.00,
    open_price=100.00,
    high_price=105.00,
    low_price=95.00,
    volume=100000
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — INVALID PRICE
# ---------------------------------------------------------

print()
print("TEST 5 — INVALID PRICE")
print("-" * 45)

result = create_option_market_data(
    trading_symbol="NIFTY15SEP2623300CE",
    instrument_token=111113,
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    current_price=0,
    open_price=100.00,
    high_price=105.00,
    low_price=95.00,
    volume=100000
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 6 — INVALID VOLUME
# ---------------------------------------------------------

print()
print("TEST 6 — INVALID VOLUME")
print("-" * 45)

result = create_option_market_data(
    trading_symbol="NIFTY15SEP2623300CE",
    instrument_token=111113,
    underlying="NIFTY",
    expiry="2026-09-15",
    strike=23300,
    option_type="CE",
    current_price=100.00,
    open_price=100.00,
    high_price=105.00,
    low_price=95.00,
    volume=-100
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 45)
print("JKJ OPTION MARKET DATA V3 TEST COMPLETE")
print("=" * 45)
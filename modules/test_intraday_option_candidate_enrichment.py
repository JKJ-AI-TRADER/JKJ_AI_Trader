"""
JKJ AI Trader
Test — Intraday Option Candidate Enrichment V6
"""

from intraday_option_candidate_enrichment import (
    enrich_option_candidate
)


print("=" * 52)
print("JKJ OPTION CANDIDATE ENRICHMENT V6 TEST")
print("=" * 52)


# ---------------------------------------------------------
# BASE TEST DATA
# ---------------------------------------------------------

option_data = {
    "Trading Symbol": "NIFTY15SEP2623300CE",
    "Underlying": "NIFTY",
    "Expiry": "2026-09-15",
    "Strike": 23300,
    "Option Type": "CE",
    "Current Price": 125.50,
    "Volume": 250000,
}


underlying_data = {
    "Current Price": 23420.00,
    "MA20": 23380.00,
    "MA50": 23320.00,
    "RSI": 58.00,
}


# ---------------------------------------------------------
# TEST 1 — BULLISH CE
# ---------------------------------------------------------

print()
print("TEST 1 — BULLISH CE ENRICHMENT")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=underlying_data,
    spread_percentage=0.10,
    remaining_profit_percentage=2.50,
    risk_reward_ratio=2.00,
)

print("Status:", result["Status"])
print("Trading Symbol:", result["Trading Symbol"])
print("Underlying Trend:", result["Underlying Trend"])
print("Option Alignment:", result["Option Alignment"])
print("Underlying Momentum:", result["Underlying Momentum"])
print("Liquidity Status:", result["Liquidity Status"])
print("Economic Status:", result["Economic Status"])

assert result["Status"] == "READY"
assert result["Underlying Trend"] == "BULLISH"
assert result["Option Alignment"] == "SUPPORTIVE"
assert result["Underlying Momentum"] == "HEALTHY"
assert result["Liquidity Status"] == "EXCELLENT"
assert result["Economic Status"] == "VIABLE"

print("PASS")


# ---------------------------------------------------------
# TEST 2 — BEARISH PE
# ---------------------------------------------------------

print()
print("TEST 2 — BEARISH PE ENRICHMENT")
print("-" * 52)

pe_option_data = {
    "Trading Symbol": "NIFTY15SEP2623300PE",
    "Underlying": "NIFTY",
    "Expiry": "2026-09-15",
    "Strike": 23300,
    "Option Type": "PE",
    "Current Price": 175.00,
    "Volume": 350000,
}


bearish_underlying = {
    "Current Price": 23200.00,
    "MA20": 23300.00,
    "MA50": 23400.00,
    "RSI": 35.00,
}


result = enrich_option_candidate(
    option_data=pe_option_data,
    underlying_data=bearish_underlying,
    spread_percentage=0.20,
    remaining_profit_percentage=3.00,
    risk_reward_ratio=2.00,
)

print("Status:", result["Status"])
print("Underlying Trend:", result["Underlying Trend"])
print("Option Alignment:", result["Option Alignment"])
print("Underlying Momentum:", result["Underlying Momentum"])
print("Liquidity Status:", result["Liquidity Status"])
print("Economic Status:", result["Economic Status"])

assert result["Status"] == "READY"
assert result["Underlying Trend"] == "BEARISH"
assert result["Option Alignment"] == "SUPPORTIVE"
assert result["Underlying Momentum"] == "WEAK"
assert result["Liquidity Status"] == "GOOD"
assert result["Economic Status"] == "VIABLE"

print("PASS")


# ---------------------------------------------------------
# TEST 3 — MIXED MARKET
# ---------------------------------------------------------

print()
print("TEST 3 — MIXED MARKET")
print("-" * 52)

mixed_underlying = {
    "Current Price": 23350.00,
    "MA20": 23320.00,
    "MA50": 23380.00,
    "RSI": 50.00,
}


result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=mixed_underlying,
    spread_percentage=0.40,
    remaining_profit_percentage=1.00,
    risk_reward_ratio=1.60,
)

print("Status:", result["Status"])
print("Underlying Trend:", result["Underlying Trend"])
print("Option Alignment:", result["Option Alignment"])
print("Underlying Momentum:", result["Underlying Momentum"])
print("Liquidity Status:", result["Liquidity Status"])
print("Economic Status:", result["Economic Status"])

assert result["Status"] == "READY"
assert result["Underlying Trend"] == "MIXED"
assert result["Option Alignment"] == "MIXED"
assert result["Underlying Momentum"] == "HEALTHY"
assert result["Liquidity Status"] == "ACCEPTABLE"
assert result["Economic Status"] == "VIABLE"

print("PASS")


# ---------------------------------------------------------
# TEST 4 — ECONOMIC INFORMATION PENDING
# ---------------------------------------------------------

print()
print("TEST 4 — ECONOMIC INFORMATION PENDING")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=underlying_data,
)

print("Status:", result["Status"])
print("Liquidity Status:", result["Liquidity Status"])
print("Economic Status:", result["Economic Status"])

assert result["Status"] == "READY"
assert result["Liquidity Status"] == "PENDING"
assert result["Economic Status"] == "PENDING"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — POOR LIQUIDITY
# ---------------------------------------------------------

print()
print("TEST 5 — POOR LIQUIDITY")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=underlying_data,
    spread_percentage=1.00,
    remaining_profit_percentage=3.00,
    risk_reward_ratio=2.00,
)

print("Status:", result["Status"])
print("Liquidity Status:", result["Liquidity Status"])

assert result["Status"] == "READY"
assert result["Liquidity Status"] == "POOR"

print("PASS")


# ---------------------------------------------------------
# TEST 6 — NON-VIABLE ECONOMICS
# ---------------------------------------------------------

print()
print("TEST 6 — NON-VIABLE ECONOMICS")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=underlying_data,
    spread_percentage=0.10,
    remaining_profit_percentage=0.00,
    risk_reward_ratio=1.00,
)

print("Status:", result["Status"])
print("Economic Status:", result["Economic Status"])

assert result["Status"] == "READY"
assert result["Economic Status"] == "NOT VIABLE"

print("PASS")


# ---------------------------------------------------------
# TEST 7 — INVALID OPTION DATA
# ---------------------------------------------------------

print()
print("TEST 7 — INVALID OPTION DATA")
print("-" * 52)

result = enrich_option_candidate(
    option_data="INVALID",
    underlying_data=underlying_data,
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 8 — INVALID UNDERLYING DATA
# ---------------------------------------------------------

print()
print("TEST 8 — INVALID UNDERLYING DATA")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data="INVALID",
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 9 — INVALID SPREAD
# ---------------------------------------------------------

print()
print("TEST 9 — INVALID SPREAD")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=underlying_data,
    spread_percentage=-0.10,
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 10 — INVALID RISK/REWARD
# ---------------------------------------------------------

print()
print("TEST 10 — INVALID RISK/REWARD")
print("-" * 52)

result = enrich_option_candidate(
    option_data=option_data,
    underlying_data=underlying_data,
    risk_reward_ratio=-1.00,
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 52)
print("JKJ OPTION CANDIDATE ENRICHMENT V6 TEST COMPLETE")
print("=" * 52)
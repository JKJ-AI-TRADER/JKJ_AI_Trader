from intraday_market_engine import (
    analyse_intraday_market
)


# -----------------------------------------
# TEST MARKET DATA
# -----------------------------------------

test_market_data = {
    "Current Price": 25000,
    "MA20": 24800,
    "MA50": 24500,
    "RSI": 60
}


# -----------------------------------------
# RUN ANALYSIS
# -----------------------------------------

result = analyse_intraday_market(
    test_market_data
)


# -----------------------------------------
# DISPLAY RESULT
# -----------------------------------------

print()
print("=" * 50)
print("JKJ AI INTRADAY MARKET ENGINE TEST")
print("=" * 50)

print()

print(
    "Intraday Market Status:",
    result.get("Intraday Market Status")
)

print(
    "Trading Environment:",
    result.get("Trading Environment")
)

print(
    "Trading Allowed:",
    result.get("Trading Allowed")
)

print(
    "Confidence:",
    result.get("Confidence")
)

print()
print("REASONS:")

for reason in result.get("Reasons", []):
    print(f"• {reason}")

print()
print("=" * 50)
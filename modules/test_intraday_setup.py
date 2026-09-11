from intraday_setup_engine import (
    analyse_intraday_setup
)


# -----------------------------------------
# TEST STOCK DATA
# -----------------------------------------

test_stock_data = {
    "Current Price": 1000,
    "MA20": 980,
    "RSI": 60,
    "Volume Trend": "Increasing",
    "Short-Term Trend": "Improving"
}


# -----------------------------------------
# RUN ANALYSIS
# -----------------------------------------

result = analyse_intraday_setup(
    test_stock_data
)


# -----------------------------------------
# DISPLAY RESULT
# -----------------------------------------

print()
print("=" * 50)
print("JKJ AI INTRADAY SETUP ENGINE TEST")
print("=" * 50)

print()

print(
    "Intraday Setup Status:",
    result.get("Intraday Setup Status")
)

print(
    "Setup Strength:",
    result.get("Setup Strength")
)

print(
    "Trade Candidate:",
    result.get("Trade Candidate")
)

print(
    "Setup Score:",
    result.get("Setup Score")
)

print()
print("REASONS:")

for reason in result.get("Reasons", []):
    print(f"• {reason}")

print()
print("=" * 50)
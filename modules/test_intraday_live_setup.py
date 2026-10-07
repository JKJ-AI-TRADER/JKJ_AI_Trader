from intraday_data_provider import get_intraday_data
from intraday_indicator_engine import analyse_intraday_indicators
from intraday_setup_engine import analyse_intraday_setup

import yfinance as yf


print("========================================")
print("JKJ AI LIVE INTRADAY SETUP TEST")
print("========================================")

symbol = "RELIANCE"

# -----------------------------------------
# STEP 1 — GET REAL 5-MINUTE DATA
# -----------------------------------------

data_result = get_intraday_data(symbol)

print("\nData Provider:", data_result.get("Status"))

if data_result.get("Data Status") != "COMPLETE":
    print("ERROR: Intraday data unavailable.")
    raise SystemExit


# -----------------------------------------
# STEP 2 — GET THE ACTUAL PRICE HISTORY
# -----------------------------------------

ticker = yf.Ticker(symbol + ".NS")

history = ticker.history(
    period="5d",
    interval="5m"
)


# -----------------------------------------
# STEP 3 — CALCULATE INTRADAY INDICATORS
# -----------------------------------------

indicator_result = analyse_intraday_indicators(history)

print("Indicator Engine:", indicator_result.get("Status"))

if indicator_result.get("Data Status") != "COMPLETE":
    print("ERROR: Intraday indicators unavailable.")
    raise SystemExit


# -----------------------------------------
# STEP 4 — PREPARE DATA FOR SETUP ENGINE
# -----------------------------------------

stock_data = {
    "Current Price": indicator_result.get("Current Price"),
    "MA20": indicator_result.get("MA20"),
    "RSI": indicator_result.get("RSI"),

    # Standardise values for the setup engine
    "Volume Trend": str(
        indicator_result.get("Volume Trend")
    ).upper(),

    "Short-Term Trend": str(
        indicator_result.get("Short-Term Trend")
    ).upper(),
}


# -----------------------------------------
# STEP 5 — RUN INTRADAY SETUP ENGINE
# -----------------------------------------

setup_result = analyse_intraday_setup(stock_data)


# -----------------------------------------
# DISPLAY RESULTS
# -----------------------------------------

print("\n========================================")
print("LIVE INTRADAY SETUP RESULT")
print("========================================")

print("\nCurrent Price:", stock_data["Current Price"])
print("MA20:", stock_data["MA20"])
print("RSI:", stock_data["RSI"])
print("Short-Term Trend:", stock_data["Short-Term Trend"])
print("Volume Trend:", stock_data["Volume Trend"])

print("\nSetup Status:", setup_result.get("Intraday Setup Status"))
print("Setup Strength:", setup_result.get("Setup Strength"))
print("Trade Candidate:", setup_result.get("Trade Candidate"))
print("Setup Score:", setup_result.get("Setup Score"))

print("\nREASONS:")

for reason in setup_result.get("Reasons", []):
    print("•", reason)

print("\n========================================")
from intraday_indicator_engine import analyse_intraday_indicators

import yfinance as yf
from intraday_market_engine import analyse_intraday_market

print("========================================")
print("JKJ AI LIVE INTRADAY MARKET TEST")
print("========================================")

symbol = "^NSEI"

# -----------------------------------------
# STEP 1 — GET REAL NIFTY 5-MINUTE DATA
# -----------------------------------------

ticker = yf.Ticker(symbol)

history = ticker.history(
    period="5d",
    interval="5m"
)

if history.empty:
    print("\nERROR: NIFTY intraday data unavailable.")
    raise SystemExit


# -----------------------------------------
# STEP 2 — CALCULATE INTRADAY INDICATORS
# -----------------------------------------

indicator_result = analyse_intraday_indicators(history)

print("\nIndicator Engine:", indicator_result.get("Status"))

if indicator_result.get("Data Status") != "COMPLETE":
    print("ERROR: NIFTY intraday indicators unavailable.")
    raise SystemExit


# -----------------------------------------
# STEP 3 — PREPARE MARKET DATA
# -----------------------------------------

market_data = {
    "Current Price": indicator_result.get("Current Price"),
    "MA20": indicator_result.get("MA20"),
    "MA50": indicator_result.get("MA50"),
    "RSI": indicator_result.get("RSI"),
}


# -----------------------------------------
# DISPLAY RAW MARKET EVIDENCE
# -----------------------------------------

print("\n========================================")
print("NIFTY INTRADAY MARKET DATA")
print("========================================")

print("\nCurrent Price:", market_data["Current Price"])
print("MA20:", market_data["MA20"])
print("MA50:", market_data["MA50"])
print("RSI:", market_data["RSI"])
# -----------------------------------------
# STEP 4 — RUN INTRADAY MARKET ENGINE
# -----------------------------------------

market_result = analyse_intraday_market(market_data)

print("\n========================================")
print("JKJ INTRADAY MARKET DECISION")
print("========================================")

print("\nMarket Status:",
      market_result.get("Intraday Market Status"))

print("Trading Environment:",
      market_result.get("Trading Environment"))

print("Trading Allowed:",
      market_result.get("Trading Allowed"))

print("Confidence:",
      market_result.get("Confidence"))

print("\nREASONS:")

for reason in market_result.get("Reasons", []):
    print("•", reason)

print("\n========================================")
print("\n========================================")
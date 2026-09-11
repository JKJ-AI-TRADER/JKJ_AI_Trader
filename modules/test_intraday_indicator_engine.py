from intraday_data_provider import get_intraday_data
from intraday_indicator_engine import analyse_intraday_indicators


print("========================================")
print("JKJ AI INTRADAY INDICATOR ENGINE TEST")
print("========================================")

symbol = "RELIANCE"

# Get real intraday data
data_result = get_intraday_data(symbol)

print("\nData Provider Status:", data_result.get("Status"))

# The indicator engine needs the actual OHLCV history.
# This test retrieves the same 5-minute data directly.
import yfinance as yf

ticker = yf.Ticker(symbol + ".NS")

history = ticker.history(
    period="5d",
    interval="5m"
)

# Analyse the intraday data
result = analyse_intraday_indicators(history)

print("\nIndicator Status:", result.get("Status"))
print("Data Status:", result.get("Data Status"))

print("\nCurrent Price:", result.get("Current Price"))
print("MA20:", result.get("MA20"))
print("MA50:", result.get("MA50"))
print("RSI:", result.get("RSI"))

print("\nShort-Term Trend:", result.get("Short-Term Trend"))
print("Volume Trend:", result.get("Volume Trend"))

print("\n========================================")
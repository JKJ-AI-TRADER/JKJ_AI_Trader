from intraday_data_provider import get_intraday_data
from intraday_indicator_engine import analyse_intraday_indicators
from intraday_market_engine import analyse_intraday_market
from intraday_setup_engine import analyse_intraday_setup
from intraday_risk_engine import analyse_intraday_risk
from intraday_decision_engine import make_intraday_decision

import yfinance as yf


print("========================================")
print("JKJ AI LIVE INTRADAY TRADE TEST")
print("========================================")


# =================================================
# 1. NIFTY MARKET ANALYSIS
# =================================================

print("\n[1] NIFTY MARKET ANALYSIS")

nifty = yf.Ticker("^NSEI")

nifty_history = nifty.history(
    period="5d",
    interval="5m"
)

nifty_indicators = analyse_intraday_indicators(
    nifty_history
)

market_data = {
    "Current Price": nifty_indicators.get("Current Price"),
    "MA20": nifty_indicators.get("MA20"),
    "MA50": nifty_indicators.get("MA50"),
    "RSI": nifty_indicators.get("RSI")
}

market_result = analyse_intraday_market(
    market_data
)

print("NIFTY Price:", market_data["Current Price"])
print("NIFTY MA20:", market_data["MA20"])
print("NIFTY MA50:", market_data["MA50"])
print("NIFTY RSI:", market_data["RSI"])

print("Market Status:",
      market_result.get("Intraday Market Status"))

print("Trading Allowed:",
      market_result.get("Trading Allowed"))


# =================================================
# 2. STOCK ANALYSIS
# =================================================

print("\n[2] STOCK ANALYSIS")

symbol = "RELIANCE"

stock_data_provider = get_intraday_data(
    symbol
)

stock = yf.Ticker(symbol + ".NS")

stock_history = stock.history(
    period="5d",
    interval="5m"
)

stock_indicators = analyse_intraday_indicators(
    stock_history
)

stock_data = {
    "Current Price":
        stock_indicators.get("Current Price"),

    "MA20":
        stock_indicators.get("MA20"),

    "RSI":
        stock_indicators.get("RSI"),

    "Volume Trend":
        str(
            stock_indicators.get("Volume Trend")
        ).upper(),

    "Short-Term Trend":
        str(
            stock_indicators.get("Short-Term Trend")
        ).upper()
}

setup_result = analyse_intraday_setup(
    stock_data
)

print("Stock:", symbol)
print("Price:", stock_data["Current Price"])
print("MA20:", stock_data["MA20"])
print("RSI:", stock_data["RSI"])
print("Short-Term Trend:",
      stock_data["Short-Term Trend"])
print("Volume Trend:",
      stock_data["Volume Trend"])

print("Setup Status:",
      setup_result.get("Intraday Setup Status"))

print("Setup Score:",
      setup_result.get("Setup Score"))

print("Trade Candidate:",
      setup_result.get("Trade Candidate"))


# =================================================
# 3. PROPOSED TRADE PLAN
# =================================================

print("\n[3] PROPOSED TRADE PLAN")

entry_price = stock_data["Current Price"]

stop_loss = round(
    entry_price * 0.99,
    2
)

target_price = round(
    entry_price * 1.02,
    2
)

print("Entry Price:", entry_price)
print("Stop Loss:", stop_loss)
print("Target Price:", target_price)


# =================================================
# 4. RISK ANALYSIS
# =================================================

print("\n[4] RISK ANALYSIS")

risk_result = analyse_intraday_risk(
    entry_price=entry_price,
    stop_loss=stop_loss,
    target_price=target_price,
    setup_score=setup_result.get(
        "Setup Score",
        0
    ),
    trading_allowed=market_result.get(
        "Trading Allowed",
        False
    )
)

print("Risk Status:",
      risk_result.get("Risk Status"))

print("Risk Level:",
      risk_result.get("Risk Level"))

print("Risk %:",
      risk_result.get("Risk Percentage"))

print("Reward %:",
      risk_result.get("Reward Percentage"))

print("Risk/Reward:",
      risk_result.get("Risk Reward Ratio"))

print("Trade Allowed:",
      risk_result.get("Trade Allowed"))


# =================================================
# 5. FINAL JKJ DECISION
# =================================================

print("\n[5] FINAL JKJ DECISION")

decision_result = make_intraday_decision(
    market_result,
    setup_result,
    risk_result
)

print("\n========================================")
print("FINAL DECISION:",
      decision_result.get("Final Decision"))

print("CONFIDENCE:",
      decision_result.get("Confidence"),
      "%")
print("========================================")

print("\nREASONS:")

for reason in decision_result.get(
    "Reasons",
    []
):
    print("•", reason)

warnings = decision_result.get(
    "Warnings",
    []
)

if warnings:

    print("\nWARNINGS:")

    for warning in warnings:
        print("⚠", warning)

print("\n========================================")
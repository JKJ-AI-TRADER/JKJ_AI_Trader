import yfinance as yf
import pandas as pd

def get_nifty_data():
    """
    Fetch NIFTY 50 market data using Yahoo Finance.

    Raw market evidence only.
    No scoring or decision-making is performed here.
    """

    try:
        ticker = yf.Ticker("^NSEI")
        history = ticker.history(period="1y")

        if history.empty:
            return {
                "Status": "No NIFTY market data found",
                "Data Status": "FAILED",
                "Current Price": None,
                "MA20": None,
                "MA50": None,
                "MA200": None,
                "RSI": None,
            }

        history = history.dropna(subset=["Close"])

        close_prices = history["Close"]

        current_price = float(close_prices.iloc[-1])

        ma20 = (
            float(close_prices.rolling(20).mean().iloc[-1])
            if len(close_prices) >= 20
            else None
        )   

        ma50 = (
            float(close_prices.rolling(50).mean().iloc[-1])
            if len(close_prices) >= 50
            else None
        )

        ma200 = (
            float(close_prices.rolling(200).mean().iloc[-1])
            if len(close_prices) >= 200
            else None
        )

        delta = close_prices.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        average_gain = gains.rolling(14).mean()
        average_loss = losses.rolling(14).mean()

        if average_loss.iloc[-1] == 0:
            rsi = 100.0
        else:
            rs = average_gain.iloc[-1] / average_loss.iloc[-1]
            rsi = 100 - (100 / (1 + rs))

        return {
            "Status": "OK",
            "Data Status": "COMPLETE",
            "Current Price": round(current_price, 2),
            "MA20": round(ma20, 2) if ma20 is not None else None,
            "MA50": round(ma50, 2) if ma50 is not None else None,
            "MA200": round(ma200, 2) if ma200 is not None else None,
            "RSI": round(float(rsi), 2),
        }

    except Exception as e:
        return {
            "Status": f"NIFTY data error: {str(e)}",
            "Data Status": "FAILED",
            "Current Price": None,
            "MA20": None,
            "MA50": None,
            "MA200": None,
            "RSI": None,
        }
    
def calculate_rsi(prices, period=14):
    """Calculate a basic RSI from closing prices."""

    delta = prices.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.rolling(period).mean()
    average_loss = losses.rolling(period).mean()

    if average_loss.iloc[-1] == 0:
        return 100.0

    rs = average_gain.iloc[-1] / average_loss.iloc[-1]

    rsi = 100 - (100 / (1 + rs))

    return round(float(rsi), 2)


def get_stock_data(symbol):
    """
    Fetch market data for an NSE stock using Yahoo Finance.

    Example:
    KITEX -> KITEX.NS

    This module provides raw market evidence.
    Intelligence engines interpret that evidence separately.
    """

    symbol = symbol.strip().upper()

    # Convert a simple NSE symbol into Yahoo Finance format
    if not symbol.endswith(".NS"):
        ticker_symbol = f"{symbol}.NS"
    else:
        ticker_symbol = symbol

    try:
        ticker = yf.Ticker(ticker_symbol)
        nifty_data = get_nifty_data()

        # Get approximately one year of daily data
        history = ticker.history(period="1y")

        if history.empty:
            return {
                "Symbol": symbol,
                "Status": "No market data found",
                "Data Status": "FAILED",
                "Missing Data": "Stock history",
                "Current Price": None,
                "Open": None,
                "High": None,
                "Low": None,
                "Close": None,
                "Volume": None,
                "MA20": None,
                "MA50": None,
                "MA200": None,
                "52 Week High": None,
                "52 Week Low": None,
                "RSI": None,
                "Volume Trend": "Unknown",
            }

        # Remove rows without closing prices
        history = history.dropna(subset=["Close"])

        close_prices = history["Close"]

        # Historical prices for relative strength analysis
        price_20d_ago = (
            float(close_prices.iloc[-21])
            if len(close_prices) >= 21
            else None
        )

        price_50d_ago = (
            float(close_prices.iloc[-51])
            if len(close_prices) >= 51
            else None
        )
       
        volume = history["Volume"].fillna(0)

        # Current OHLC values
        current_price = float(close_prices.iloc[-1])
        current_open = float(history["Open"].iloc[-1])
        current_high = float(history["High"].iloc[-1])
        current_low = float(history["Low"].iloc[-1])

        # 52-week range
        week_52_high = float(close_prices.max())
        week_52_low = float(close_prices.min())

        # Moving averages
        ma20 = (
            float(close_prices.rolling(20).mean().iloc[-1])
            if len(close_prices) >= 20
            else None
        )

        ma50 = (
            float(close_prices.rolling(50).mean().iloc[-1])
            if len(close_prices) >= 50
            else None
        )

        ma200 = (
            float(close_prices.rolling(200).mean().iloc[-1])
            if len(close_prices) >= 200
            else None
        )

        # RSI
        rsi = (
            calculate_rsi(close_prices)
            if len(close_prices) >= 14
            else None
        )

        # Volume trend
        recent_volume = volume.tail(20).mean()
        previous_volume = volume.tail(60).head(40).mean()

        if previous_volume == 0:
            volume_trend = "Unknown"
        elif recent_volume > previous_volume * 1.10:
            volume_trend = "Increasing"
        elif recent_volume < previous_volume * 0.90:
            volume_trend = "Decreasing"
        else:
            volume_trend = "Stable"

        return {
            "Symbol": symbol,
            "Status": "OK",
            "Data Status": "COMPLETE",
            "Missing Data": None,

            "Current Price": round(current_price, 2),
            "Open": round(current_open, 2),
            "High": round(current_high, 2),
            "Low": round(current_low, 2),
            "Close": round(current_price, 2),
            "Volume": int(volume.iloc[-1]),

            "MA20": round(ma20, 2) if ma20 is not None else None,
            "MA50": round(ma50, 2) if ma50 is not None else None,
            "MA200": round(ma200, 2) if ma200 is not None else None,

            "52 Week High": round(week_52_high, 2),
            "52 Week Low": round(week_52_low, 2),

            "RSI": rsi,
            "Volume Trend": volume_trend,
            "Market Data": nifty_data,            
        }

    except Exception as e:
        return {
            "Symbol": symbol,
            "Status": f"Data error: {str(e)}",
            "Data Status": "FAILED",
            "Missing Data": "Stock market data",

            "Current Price": None,
            "Open": None,
            "High": None,
            "Low": None,
            "Close": None,
            "Volume": None,

            "MA20": None,
            "MA50": None,
            "MA200": None,

            "52 Week High": None,
            "52 Week Low": None,

            "RSI": None,
            "Volume Trend": "Unknown",
        }
    
import yfinance as yf
import pandas as pd


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
    """

    symbol = symbol.strip().upper()

    # Convert a simple NSE symbol into Yahoo Finance format
    if not symbol.endswith(".NS"):
        ticker_symbol = f"{symbol}.NS"
    else:
        ticker_symbol = symbol

    try:
        ticker = yf.Ticker(ticker_symbol)

        # Get approximately one year of daily data
        history = ticker.history(period="1y")

        if history.empty:
            return {
                "Symbol": symbol,
                "Status": "No market data found",
                "Current Price": None,
                "52 Week High": None,
                "52 Week Low": None,
                "RSI": None,
                "Volume Trend": "Unknown",
                "Sector Strength": None,
            }

        close_prices = history["Close"].dropna()
        volume = history["Volume"].dropna()

        current_price = float(close_prices.iloc[-1])
        week_52_high = float(close_prices.max())
        week_52_low = float(close_prices.min())

        rsi = calculate_rsi(close_prices)

        # Compare recent average volume with the previous period
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
            "Current Price": round(current_price, 2),
            "52 Week High": round(week_52_high, 2),
            "52 Week Low": round(week_52_low, 2),
            "RSI": rsi,
            "Volume Trend": volume_trend,
            "Sector Strength": None,
        }

    except Exception as e:
        return {
            "Symbol": symbol,
            "Status": f"Data error: {str(e)}",
            "Current Price": None,
            "52 Week High": None,
            "52 Week Low": None,
            "RSI": None,
            "Volume Trend": "Unknown",
            "Sector Strength": None,
        }
    
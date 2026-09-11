import yfinance as yf


def get_intraday_data(symbol, interval="5m"):
    """
    Fetch recent intraday market data for an NSE stock.

    This module provides raw intraday market evidence only.
    No scoring or trading decision is performed here.

    Example:
        get_intraday_data("RELIANCE")
    """

    symbol = symbol.strip().upper()

    # Convert NSE symbol to Yahoo Finance format
    if not symbol.endswith(".NS"):
        ticker_symbol = f"{symbol}.NS"
    else:
        ticker_symbol = symbol

    try:
        ticker = yf.Ticker(ticker_symbol)

        # Fetch recent intraday data
        history = ticker.history(
            period="5d",
            interval=interval
        )

        if history.empty:
            return {
                "Symbol": symbol,
                "Status": "No intraday market data found",
                "Data Status": "FAILED",
                "Current Price": None,
                "Open": None,
                "High": None,
                "Low": None,
                "Close": None,
                "Volume": None,
                "Interval": interval,
                "Bars": 0
            }

        # Remove rows without closing prices
        history = history.dropna(subset=["Close"])

        if history.empty:
            return {
                "Symbol": symbol,
                "Status": "No valid intraday price data found",
                "Data Status": "FAILED",
                "Current Price": None,
                "Open": None,
                "High": None,
                "Low": None,
                "Close": None,
                "Volume": None,
                "Interval": interval,
                "Bars": 0
            }

        latest = history.iloc[-1]

        current_price = float(latest["Close"])
        current_open = float(latest["Open"])
        current_high = float(latest["High"])
        current_low = float(latest["Low"])
        current_volume = int(latest["Volume"])

        return {
            "Symbol": symbol,
            "Status": "OK",
            "Data Status": "COMPLETE",

            "Current Price": round(current_price, 2),
            "Open": round(current_open, 2),
            "High": round(current_high, 2),
            "Low": round(current_low, 2),
            "Close": round(current_price, 2),
            "Volume": current_volume,

            "Interval": interval,
            "Bars": len(history)
        }

    except Exception as e:
        return {
            "Symbol": symbol,
            "Status": f"Intraday data error: {str(e)}",
            "Data Status": "FAILED",

            "Current Price": None,
            "Open": None,
            "High": None,
            "Low": None,
            "Close": None,
            "Volume": None,

            "Interval": interval,
            "Bars": 0
        }
import pandas as pd


def analyse_intraday_indicators(history):
    """
    Calculate intraday technical indicators from OHLCV data.

    This module provides raw intraday technical evidence only.
    No trading decision is made here.
    """

    if history is None or history.empty:
        return {
            "Status": "FAILED",
            "Data Status": "NO DATA",
            "Current Price": None,
            "MA20": None,
            "MA50": None,
            "RSI": None,
            "Short-Term Trend": "UNKNOWN",
            "Volume Trend": "Unknown",
        }

    history = history.dropna(subset=["Close"])

    if history.empty:
        return {
            "Status": "FAILED",
            "Data Status": "NO VALID DATA",
            "Current Price": None,
            "MA20": None,
            "MA50": None,
            "RSI": None,
            "Short-Term Trend": "UNKNOWN",
            "Volume Trend": "Unknown",
        }

    close_prices = history["Close"]
    volume = history["Volume"].fillna(0)

    current_price = float(close_prices.iloc[-1])

    # -----------------------------------------
    # MOVING AVERAGES
    # -----------------------------------------

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

    # -----------------------------------------
    # RSI
    # -----------------------------------------

    rsi = None

    if len(close_prices) >= 14:

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

        rsi = round(float(rsi), 2)

    # -----------------------------------------
    # SHORT-TERM TREND
    # -----------------------------------------

    if (
        ma20 is not None
        and ma50 is not None
        and current_price > ma20
        and ma20 > ma50
    ):
        short_term_trend = "IMPROVING"

    elif (
        ma20 is not None
        and ma50 is not None
        and current_price < ma20
        and ma20 < ma50
    ):
        short_term_trend = "DETERIORATING"

    else:
        short_term_trend = "STABLE"

    # -----------------------------------------
    # VOLUME TREND
    # -----------------------------------------

    if len(volume) >= 40:

        recent_volume = volume.tail(20).mean()
        previous_volume = volume.tail(40).head(20).mean()

        if previous_volume == 0:
            volume_trend = "Unknown"

        elif recent_volume > previous_volume * 1.10:
            volume_trend = "Increasing"

        elif recent_volume < previous_volume * 0.90:
            volume_trend = "Decreasing"

        else:
            volume_trend = "Stable"

    else:
        volume_trend = "Unknown"

    return {
        "Status": "OK",
        "Data Status": "COMPLETE",

        "Current Price": round(current_price, 2),

        "MA20": round(ma20, 2) if ma20 is not None else None,
        "MA50": round(ma50, 2) if ma50 is not None else None,

        "RSI": rsi,

        "Short-Term Trend": short_term_trend,
        "Volume Trend": volume_trend,
    }
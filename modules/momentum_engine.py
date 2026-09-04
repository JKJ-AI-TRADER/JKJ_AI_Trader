"""
JKJ AI Short-Term Momentum Engine v0.1

Wisdom Before Wealth.

This engine evaluates whether short-term momentum
is beginning to build or whether a stock may already
be overextended.

It does not predict the future.
It evaluates available evidence.
"""


def analyse_momentum(stock_data):

    current_price = stock_data.get("Current Price")
    price_20_days_ago = stock_data.get("Price 20 Days Ago")
    rsi = stock_data.get("RSI")
    volume_trend = stock_data.get("Volume Trend", "UNKNOWN")
    short_term_trend = stock_data.get(
        "Short-Term Trend",
        "UNKNOWN"
    )

    explanation = []
    score = 0

    # -----------------------------------------
    # VALIDATE REQUIRED DATA
    # -----------------------------------------

    if (
        current_price is None
        or price_20_days_ago is None
        or rsi is None
    ):

        return {
            "Momentum Condition": "UNKNOWN",
            "Momentum Score": 0,
            "Maximum Score": 4,
            "Standard Score": 0,
            "Explanation": [
                "Insufficient data for momentum analysis."
            ]
        }

    # -----------------------------------------
    # PRICE MOMENTUM
    # -----------------------------------------

    if current_price > price_20_days_ago:

        score += 1

        explanation.append(
            "Price is higher than 20 days ago."
        )

    else:

        explanation.append(
            "Price is not higher than 20 days ago."
        )

    # -----------------------------------------
    # SHORT-TERM TREND
    # -----------------------------------------

    if str(short_term_trend).upper() == "IMPROVING":

        score += 1

        explanation.append(
            "Short-term trend is improving."
        )

    else:

        explanation.append(
            "Short-term trend is not yet improving."
        )

    # -----------------------------------------
    # RSI MOMENTUM
    # -----------------------------------------

    if 50 <= rsi <= 70:

        score += 1

        explanation.append(
            "RSI supports healthy upward momentum."
        )

    elif rsi > 70:

        explanation.append(
            "RSI indicates possible overextension."
        )

    else:

        explanation.append(
            "RSI does not yet confirm strong momentum."
        )

    # -----------------------------------------
    # VOLUME
    # -----------------------------------------

    if str(volume_trend).upper() == "INCREASING":

        score += 1

        explanation.append(
            "Volume trend supports momentum."
        )

    else:

        explanation.append(
            "Volume trend does not yet support momentum."
        )

    # -----------------------------------------
    # DETERMINE CONDITION
    # -----------------------------------------

    if rsi > 70 and score >= 2:

        condition = "OVEREXTENDED"

    elif score >= 3:

        condition = "BUILDING MOMENTUM"

    elif score == 2:

        condition = "EARLY MOMENTUM"

    else:

        condition = "NEUTRAL"

    standard_score = round(
        (score / 4) * 100,
        2
    )

    return {
        "Momentum Condition": condition,
        "Momentum Score": score,
        "Maximum Score": 4,
        "Standard Score": standard_score,
        "Explanation": explanation
    }
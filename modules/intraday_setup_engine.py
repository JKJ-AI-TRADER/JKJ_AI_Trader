"""
JKJ AI Intraday Setup Engine v0.1

Wisdom Before Wealth.

This engine analyses whether an individual stock
has a suitable setup for an intraday trade.

The engine does NOT place a trade.

It evaluates:
- Price position
- Short-term moving average
- RSI
- Momentum
- Volume

The output is an explainable intraday setup assessment.
"""


def analyse_intraday_setup(stock_data):
    """
    Analyse an individual stock for an intraday setup.

    Expected stock_data:

    {
        "Current Price": float,
        "MA20": float,
        "RSI": float,
        "Volume Trend": str,
        "Short-Term Trend": str
    }
    """

    reasons = []

    # -----------------------------------------
    # GET STOCK DATA
    # -----------------------------------------

    current_price = stock_data.get(
        "Current Price",
        0
    )

    ma20 = stock_data.get(
        "MA20",
        0
    )

    rsi = stock_data.get(
        "RSI",
        None
    )

    volume_trend = str(
        stock_data.get(
            "Volume Trend",
            "UNKNOWN"
        )
    ).upper()

    short_term_trend = str(
        stock_data.get(
            "Short-Term Trend",
            "UNKNOWN"
        )
    ).upper()

    # -----------------------------------------
    # DATA VALIDATION
    # -----------------------------------------

    if (
        current_price is None
        or ma20 is None
        or current_price <= 0
        or ma20 <= 0
    ):

        return {
            "Intraday Setup Status":
                "NO SETUP",

            "Setup Strength":
                "UNKNOWN",

            "Trade Candidate":
                False,

            "Setup Score":
                0,

            "Reasons": [
                "Insufficient stock data "
                "for intraday setup analysis."
            ]
        }

    # -----------------------------------------
    # INITIAL SCORE
    # -----------------------------------------

    score = 0

    # -----------------------------------------
    # PRICE VS MA20
    # -----------------------------------------

    if current_price > ma20:

        score += 30

        reasons.append(
            "Price is trading above MA20."
        )

    else:

        reasons.append(
            "Price is trading below MA20."
        )

    # -----------------------------------------
    # RSI
    # -----------------------------------------

    if rsi is not None:

        try:

            rsi_value = float(rsi)

            if 50 <= rsi_value <= 70:

                score += 25

                reasons.append(
                    "RSI supports healthy upward momentum."
                )

            elif 45 <= rsi_value < 50:

                score += 15

                reasons.append(
                    "RSI indicates neutral to improving momentum."
                )

            elif rsi_value > 70:

                score += 10

                reasons.append(
                    "RSI indicates strong momentum but "
                    "possible overextension."
                )

            else:

                reasons.append(
                    "RSI indicates weak momentum."
                )

        except (
            ValueError,
            TypeError
        ):

            reasons.append(
                "RSI data could not be evaluated."
            )

    # -----------------------------------------
    # SHORT-TERM TREND
    # -----------------------------------------

    if short_term_trend == "IMPROVING":

        score += 25

        reasons.append(
            "Short-term trend is improving."
        )

    elif short_term_trend == "STABLE":

        score += 10

        reasons.append(
            "Short-term trend is stable."
        )

    elif short_term_trend == "DETERIORATING":

        reasons.append(
            "Short-term trend is deteriorating."
        )

    else:

        reasons.append(
            "Short-term trend is not clearly confirmed."
        )

    # -----------------------------------------
    # VOLUME TREND
    # -----------------------------------------

    if volume_trend in [
        "INCREASING",
        "HIGH"
    ]:

        score += 20

        reasons.append(
            "Volume supports the price movement."
        )

    elif volume_trend == "STABLE":

        score += 10

        reasons.append(
            "Volume remains stable."
        )

    else:

        reasons.append(
            "Volume confirmation is weak or unavailable."
        )

    # -----------------------------------------
    # LIMIT SCORE
    # -----------------------------------------

    score = min(
        score,
        100
    )

    # -----------------------------------------
    # FINAL CLASSIFICATION
    # -----------------------------------------

    if score >= 75:

        status = "STRONG SETUP"
        strength = "STRONG"
        trade_candidate = True

    elif score >= 50:

        status = "POSSIBLE SETUP"
        strength = "MODERATE"
        trade_candidate = True

    else:

        status = "NO SETUP"
        strength = "WEAK"
        trade_candidate = False

    return {
        "Intraday Setup Status":
            status,

        "Setup Strength":
            strength,

        "Trade Candidate":
            trade_candidate,

        "Setup Score":
            score,

        "Reasons":
            reasons
    }
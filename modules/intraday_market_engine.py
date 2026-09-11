"""
JKJ AI Intraday Market Engine v0.1

Wisdom Before Wealth.

This engine determines whether the overall market
environment is suitable for considering intraday trades.

The purpose is capital protection first.

This engine does NOT select a stock.
This engine does NOT place a trade.

It only answers:

Is the market environment suitable for intraday trading?
"""


def analyse_intraday_market(market_data):
    """
    Analyse the overall market environment
    for intraday trading.

    Expected market_data:

    {
        "Current Price": float,
        "MA20": float,
        "MA50": float,
        "RSI": float
    }
    """

    reasons = []

    # -----------------------------------------
    # GET MARKET DATA
    # -----------------------------------------

    current_price = market_data.get(
        "Current Price",
        0
    )

    ma20 = market_data.get(
        "MA20",
        0
    )

    ma50 = market_data.get(
        "MA50",
        0
    )

    rsi = market_data.get(
        "RSI",
        None
    )

    # -----------------------------------------
    # DATA VALIDATION
    # -----------------------------------------

    if (
        current_price is None
        or ma20 is None
        or ma50 is None
        or current_price <= 0
        or ma20 <= 0
        or ma50 <= 0
    ):

        return {
            "Intraday Market Status":
                "NO TRADE",

            "Trading Environment":
                "UNKNOWN",

            "Trading Allowed":
                False,

            "Confidence":
                0,

            "Reasons": [
                "Insufficient market data "
                "for intraday analysis."
            ]
        }

    # -----------------------------------------
    # MARKET STRENGTH CHECKS
    # -----------------------------------------

    above_ma20 = current_price > ma20
    above_ma50 = current_price > ma50

    healthy_rsi = (
        rsi is not None
        and 45 <= rsi <= 70
    )

    weak_rsi = (
        rsi is not None
        and rsi < 40
    )

    overextended_rsi = (
        rsi is not None
        and rsi > 75
    )

    # -----------------------------------------
    # STRONG MARKET ENVIRONMENT
    # -----------------------------------------

    if (
        above_ma20
        and above_ma50
        and healthy_rsi
    ):

        reasons.append(
            "Market is trading above MA20."
        )

        reasons.append(
            "Market is trading above MA50."
        )

        reasons.append(
            "RSI indicates healthy market momentum."
        )

        return {
            "Intraday Market Status":
                "FAVOURABLE",

            "Trading Environment":
                "STRONG",

            "Trading Allowed":
                True,

            "Confidence":
                80,

            "Reasons": reasons
        }

    # -----------------------------------------
    # WEAK MARKET
    # -----------------------------------------

    if (
        not above_ma20
        and not above_ma50
    ):

        reasons.append(
            "Market is trading below MA20."
        )

        reasons.append(
            "Market is trading below MA50."
        )

        if weak_rsi:

            reasons.append(
                "RSI indicates weak market momentum."
            )

        return {
            "Intraday Market Status":
                "NO TRADE",

            "Trading Environment":
                "WEAK",

            "Trading Allowed":
                False,

            "Confidence":
                80,

            "Reasons": reasons
        }

    # -----------------------------------------
    # EXTREME RSI CONDITIONS
    # -----------------------------------------

    if weak_rsi:

        reasons.append(
            "RSI indicates weak market momentum."
        )

        return {
            "Intraday Market Status":
                "NO TRADE",

            "Trading Environment":
                "WEAK",

            "Trading Allowed":
                False,

            "Confidence":
                70,

            "Reasons": reasons
        }

    if overextended_rsi:

        reasons.append(
            "RSI indicates an overextended market."
        )

        return {
            "Intraday Market Status":
                "CAUTIOUS",

            "Trading Environment":
                "OVEREXTENDED",

            "Trading Allowed":
                True,

            "Confidence":
                60,

            "Reasons": reasons
        }

    # -----------------------------------------
    # MIXED MARKET CONDITIONS
    # -----------------------------------------

    reasons.append(
        "Market signals are mixed."
    )

    if above_ma20:

        reasons.append(
            "Market remains above MA20."
        )

    else:

        reasons.append(
            "Market is below MA20."
        )

    if above_ma50:

        reasons.append(
            "Market remains above MA50."
        )

    else:

        reasons.append(
            "Market is below MA50."
        )

    if rsi is not None:

        reasons.append(
            f"Current market RSI: {rsi:.2f}."
        )

    return {
        "Intraday Market Status":
            "CAUTIOUS",

        "Trading Environment":
            "MIXED",

        "Trading Allowed":
            True,

        "Confidence":
            50,

        "Reasons": reasons
    }
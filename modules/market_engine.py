def calculate_market_alignment(stock):
    """
    JKJ AI Market Alignment Engine v0.1

    Wisdom Before Wealth.

    Market condition must support decisions.
    Every score must have a reason.
    """

    score = 0
    reasons = []

    current_price = stock.get("Current Price", 0)
    high_52 = stock.get("52 Week High", 0)

    # Temporary market assessment
    # Later connected to Nifty API

    if current_price > 0 and high_52 > 0:

        distance_from_high = (
            (high_52 - current_price) / high_52
        ) * 100

        if distance_from_high < 10:
            score += 10
            reasons.append(
                "Stock is showing relative strength"
            )

        elif distance_from_high < 25:
            score += 7
            reasons.append(
                "Stock is moderately aligned with market strength"
            )

        else:
            score += 5
            reasons.append(
                "Market alignment requires caution"
            )

    else:
        score += 5
        reasons.append(
            "Insufficient market data"
        )


    # Placeholder until Nifty integration

    score += 5

    reasons.append(
        "Overall market trend requires Nifty confirmation"
    )


    return {
        "Market Alignment Score": score,
        "Market Explanation": reasons
    }

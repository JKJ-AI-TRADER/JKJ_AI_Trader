def calculate_market_alignment(stock):
    """
    JKJ AI Market Alignment Engine v0.3

    Components:
    1. NIFTY Market Trend = 8 points
    2. Market Momentum = 4 points

    Wisdom Before Wealth:
    Every point must be explainable.
    Missing data receives no positive score.
    """

    market = stock.get("Market Data", {})

    score = 0
    reasons = []

    current_price = market.get("Current Price")
    ma20 = market.get("MA20")
    ma50 = market.get("MA50")
    ma200 = market.get("MA200")
    rsi = market.get("RSI")

    # --------------------------------------------------
    # NIFTY Market Trend — 8 Points
    # --------------------------------------------------

    # Price vs MA20 — 1 point
    if current_price is not None and ma20 is not None:
        if current_price > ma20:
            score += 1
            reasons.append("NIFTY is above MA20 (+1/1)")
        else:
            reasons.append("NIFTY is below MA20 (+0/1)")
    else:
        reasons.append("NIFTY price or MA20 data unavailable (+0/1)")

    # Price vs MA50 — 2 points
    if current_price is not None and ma50 is not None:
        if current_price > ma50:
            score += 2
            reasons.append("NIFTY is above MA50 (+2/2)")
        else:
            reasons.append("NIFTY is below MA50 (+0/2)")
    else:
        reasons.append("NIFTY price or MA50 data unavailable (+0/2)")

    # Price vs MA200 — 2 points
    if current_price is not None and ma200 is not None:
        if current_price > ma200:
            score += 2
            reasons.append("NIFTY is above MA200 (+2/2)")
        else:
            reasons.append("NIFTY is below MA200 (+0/2)")
    else:
        reasons.append("NIFTY price or MA200 data unavailable (+0/2)")

    # MA20 vs MA50 — 1 point
    if ma20 is not None and ma50 is not None:
        if ma20 > ma50:
            score += 1
            reasons.append("NIFTY MA20 is above MA50 (+1/1)")
        else:
            reasons.append("NIFTY MA20 is below MA50 (+0/1)")
    else:
        reasons.append("NIFTY MA20 or MA50 data unavailable (+0/1)")

    # MA50 vs MA200 — 2 points
    if ma50 is not None and ma200 is not None:
        if ma50 > ma200:
            score += 2
            reasons.append("NIFTY MA50 is above MA200 (+2/2)")
        else:
            reasons.append("NIFTY MA50 is below MA200 (+0/2)")
    else:
        reasons.append("NIFTY MA50 or MA200 data unavailable (+0/2)")

    # --------------------------------------------------
    # Market Momentum — 4 Points
    # --------------------------------------------------

    momentum_score = 0

    # NIFTY RSI — 2 points
    if rsi is not None:
        if 50 <= rsi <= 70:
            momentum_score += 2
            reasons.append("NIFTY RSI is in a healthy momentum range (+2/2)")
        elif 40 <= rsi < 50 or 70 < rsi <= 80:
            momentum_score += 1
            reasons.append("NIFTY RSI shows moderate momentum (+1/2)")
        else:
            reasons.append("NIFTY RSI is outside the preferred momentum range (+0/2)")
    else:
        reasons.append("NIFTY RSI data unavailable (+0/2)")

    # Short-term price momentum — 2 points
    short_term_points = 0

    if current_price is not None and ma20 is not None:
        if current_price > ma20:
            short_term_points += 1

    if ma20 is not None and ma50 is not None:
        if ma20 > ma50:
            short_term_points += 1

    momentum_score += short_term_points

    if current_price is not None and ma20 is not None and ma50 is not None:
        if short_term_points == 2:
            reasons.append(
                "NIFTY price is above MA20 and MA20 is above MA50 (+2/2)"
            )
        elif short_term_points == 1:
            reasons.append(
                "NIFTY has one positive short-term momentum condition (+1/2)"
            )
        else:
            reasons.append(
                "NIFTY has no positive short-term momentum conditions (+0/2)"
            )
    else:
        reasons.append(
            "NIFTY short-term momentum data unavailable (+0/2)"
        )

    score += momentum_score

    return {
        "Market Alignment Score": score,
        "NIFTY Market Trend Score": score - momentum_score,
        "NIFTY Market Trend Maximum": 8,
        "Market Momentum Score": momentum_score,
        "Market Momentum Maximum": 4,
        "Market Alignment Maximum": 12,
        "Market Explanation": reasons,
    }

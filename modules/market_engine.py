def analyze_market(nifty_data):
    """
    Analyse overall NIFTY market conditions.

    This engine interprets market evidence.
    It does not place trades or generate buy/sell orders.
    """

    if not nifty_data:
        return {
            "Market Condition": "Unknown",
            "Market Score": 0,
            "Explanation": "No NIFTY market data available."
        }

    if nifty_data.get("Data Status") != "COMPLETE":
        return {
            "Market Condition": "Unknown",
            "Market Score": 0,
            "Explanation": "NIFTY market data is incomplete."
        }

    current_price = nifty_data.get("Current Price")
    ma20 = nifty_data.get("MA20")
    ma50 = nifty_data.get("MA50")
    ma200 = nifty_data.get("MA200")
    rsi = nifty_data.get("RSI")

    score = 0
    reasons = []

    # Price compared with moving averages
    if current_price is not None and ma20 is not None:
        if current_price > ma20:
            score += 1
            reasons.append("NIFTY is above MA20")
        else:
            reasons.append("NIFTY is below MA20")

    if current_price is not None and ma50 is not None:
        if current_price > ma50:
            score += 1
            reasons.append("NIFTY is above MA50")
        else:
            reasons.append("NIFTY is below MA50")

    if current_price is not None and ma200 is not None:
        if current_price > ma200:
            score += 1
            reasons.append("NIFTY is above MA200")
        else:
            reasons.append("NIFTY is below MA200")

    # RSI interpretation
    if rsi is not None:

        if 50 <= rsi <= 70:
            score += 1
            reasons.append(
                "RSI indicates positive market momentum"
            )

        elif 40 <= rsi < 50:
            reasons.append(
                "RSI indicates neutral to weak market momentum"
            )

        elif 30 <= rsi < 40:
            reasons.append(
                "RSI indicates weak market momentum"
            )

        elif rsi < 30:
            reasons.append(
                "RSI indicates oversold market conditions and possible recovery potential"
            )

        else:
            reasons.append(
                "RSI indicates overbought market conditions"
            )

    # -----------------------------------------
    # FINAL MARKET CONDITION
    # -----------------------------------------

    if score >= 3:
        market_condition = "Bullish"

    elif score == 2:
        market_condition = "Neutral"

    else:
        market_condition = "Bearish"

    # -----------------------------------------
    # MARKET STATE
    # -----------------------------------------

    if rsi is not None and rsi < 30:
        market_state = "Oversold — Possible Recovery Zone"

    elif rsi is not None and rsi > 70:
        market_state = "Overbought — Caution Zone"

    elif market_condition == "Bullish":
        market_state = "Positive Trend"

    elif market_condition == "Neutral":
        market_state = "Mixed Market Conditions"

    else:
        market_state = "Weak Market Conditions"

    standard_score = round((score / 4) * 100, 2)

    return {
        "Market Condition": market_condition,
        "Market State": market_state,
        "Market Score": score,
        "Maximum Score": 4,
        "Standard Score": standard_score,
        "Explanation": reasons
    }

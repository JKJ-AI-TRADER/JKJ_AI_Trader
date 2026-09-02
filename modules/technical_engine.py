def analyze_technical(stock_data):
    """
    Analyse the technical condition of an individual stock.

    This engine interprets technical market evidence.
    It does not make buy or sell decisions.
    """

    if not stock_data:
        return {
            "Technical Condition": "Unknown",
            "Technical Score": 0,
            "Maximum Score": 5,
            "Explanation": ["No stock data available."]
        }

    if stock_data.get("Data Status") != "COMPLETE":
        return {
            "Technical Condition": "Unknown",
            "Technical Score": 0,
            "Maximum Score": 5,
            "Explanation": ["Stock market data is incomplete."]
        }

    current_price = stock_data.get("Current Price")
    ma20 = stock_data.get("MA20")
    ma50 = stock_data.get("MA50")
    ma200 = stock_data.get("MA200")
    rsi = stock_data.get("RSI")

    score = 0
    reasons = []

    # Price versus MA20
    if current_price is not None and ma20 is not None:
        if current_price > ma20:
            score += 1
            reasons.append("Price is above MA20")
        else:
            reasons.append("Price is below MA20")

    # Price versus MA50
    if current_price is not None and ma50 is not None:
        if current_price > ma50:
            score += 1
            reasons.append("Price is above MA50")
        else:
            reasons.append("Price is below MA50")

    # Price versus MA200
    if current_price is not None and ma200 is not None:
        if current_price > ma200:
            score += 1
            reasons.append("Price is above MA200")
        else:
            reasons.append("Price is below MA200")

    # RSI momentum
    if rsi is not None:
        if 50 <= rsi <= 70:
            score += 1
            reasons.append("RSI indicates positive momentum")
        elif rsi > 70:
            reasons.append("RSI indicates overbought conditions")
        elif rsi < 30:
            reasons.append("RSI indicates oversold conditions")
        else:
            reasons.append("RSI indicates weak momentum")

    # Moving-average alignment
    if ma20 is not None and ma50 is not None and ma200 is not None:
        if ma20 > ma50 > ma200:
            score += 1
            reasons.append("Moving averages show bullish alignment")
        elif ma20 < ma50 < ma200:
            reasons.append("Moving averages show bearish alignment")
        else:
            reasons.append("Moving averages show mixed alignment")

    # Final technical condition
    if score >= 4:
        technical_condition = "Strong Bullish"
    elif score == 3:
        technical_condition = "Bullish"
    elif score == 2:
        technical_condition = "Neutral"
    else:
        technical_condition = "Bearish"

    standard_score = round((score / 5) * 100, 2)

    return {
        "Technical Condition": technical_condition,
        "Technical Score": score,
        "Maximum Score": 5,
        "Standard Score": standard_score,
        "Explanation": reasons
    }


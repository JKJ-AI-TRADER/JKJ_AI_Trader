def calculate_technical_quality(stock):
    """
    JKJ AI Technical Quality Engine v0.1

    Wisdom Before Wealth:
    Every score must have a reason.
    """

    score = 0
    reasons = []

    rsi = stock.get("RSI", 0)
    current_price = stock.get("Current Price", 0)
    high_52 = stock.get("52 Week High", 0)
    low_52 = stock.get("52 Week Low", 0)

    # RSI analysis
    if rsi < 30:
        score += 8
        reasons.append("RSI indicates oversold condition")
    elif rsi < 50:
        score += 5
        reasons.append("RSI shows moderate momentum")
    else:
        score += 2
        reasons.append("RSI indicates weaker entry zone")

    # Price position analysis
    if high_52 > 0:
        position = current_price / high_52

        if position < 0.70:
            score += 8
            reasons.append("Price is trading significantly below 52 week high")
        elif position < 0.90:
            score += 5
            reasons.append("Price has correction opportunity")
        else:
            score += 2
            reasons.append("Price is near previous high zone")

    return {
        "Technical Quality Score": score,
        "Technical Explanation": reasons
    }

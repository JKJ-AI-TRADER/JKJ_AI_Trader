def analyze_risk(stock_data):
    """
    Analyze risk based on available market and technical evidence.

    Risk evaluation is separate from opportunity evaluation.
    The purpose is capital protection before considering a trade.
    """

    score = 0
    reasons = []

    current_price = stock_data.get("Current Price")
    ma20 = stock_data.get("MA20")
    ma50 = stock_data.get("MA50")
    ma200 = stock_data.get("MA200")
    rsi = stock_data.get("RSI")
    volume_trend = stock_data.get("Volume Trend")

    # Safety check for missing market data
    if current_price is None:
        return {
            "Risk Level": "High",
            "Risk Score": 0,
            "Maximum Score": 5,
            "Explanation": ["Current price data is unavailable"]
        }

    # Price below MA20 increases short-term risk
    if ma20 is not None and current_price < ma20:
        score += 1
        reasons.append("Price is below MA20")

    # Price below MA50 increases medium-term risk
    if ma50 is not None and current_price < ma50:
        score += 1
        reasons.append("Price is below MA50")

    # Price below MA200 indicates longer-term weakness
    if ma200 is not None and current_price < ma200:
        score += 1
        reasons.append("Price is below MA200")

    # Extreme RSI conditions
    if rsi is not None and rsi > 70:
        score += 1
        reasons.append("RSI indicates overbought conditions")
    elif rsi is not None and rsi < 30:
        score += 1
        reasons.append("RSI indicates strong downside weakness")

    # Declining volume may increase risk
    if volume_trend == "Decreasing":
        score += 1
        reasons.append("Volume trend is decreasing")

    # Determine overall risk level
    if score >= 4:
        risk_level = "High"
    elif score >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "Risk Level": risk_level,
        "Risk Score": score,
        "Maximum Score": 5,
        "Explanation": reasons
    }

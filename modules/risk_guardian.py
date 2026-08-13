def calculate_stock_risk(
    buy_price,
    current_price,
    technical_data=None,
    volume_data=None,
    market_data=None
):
    """
    JKJ AI Risk Guardian
    Purpose: Protect capital through explainable risk assessment.
    """

    risk_score = 0
    reasons = []

    # 1. Calculate loss percentage
    if buy_price > 0:
        loss_percent = ((current_price - buy_price) / buy_price) * 100
    else:
        loss_percent = 0


    # 2. Capital Risk Assessment
    if loss_percent <= -40:
        risk_score += 40
        reasons.append(
            "Loss exceeds 40%. Capital protection review required."
        )

    elif loss_percent <= -30:
        risk_score += 30
        reasons.append(
            "Loss exceeds 30%. High downside exposure."
        )

    elif loss_percent <= -10:
        risk_score += 15
        reasons.append(
            "Loss exceeds 10%. Monitor closely."
        )


    # 3. Technical Risk
    if technical_data:

        rsi = technical_data.get("RSI")

        if rsi and rsi < 30:
            reasons.append(
                "RSI indicates oversold condition. "
                "Reversal confirmation required."
            )


    # 4. Volume Risk
    if volume_data:

        volume_trend = volume_data.get("Volume Trend")

        if volume_trend == "Decreasing":
            risk_score += 10
            reasons.append(
                "Volume confirmation is weak."
            )


    # 5. Market Risk
    if market_data:

        market_status = market_data.get("Market Trend")

        if market_status == "Weak":
            risk_score += 10
            reasons.append(
                "Overall market trend is weak."
            )


    # Risk Classification

    if risk_score >= 60:
        risk_level = "HIGH"

        action = (
            "Protect capital. "
            "Avoid averaging until recovery signs appear."
        )

    elif risk_score >= 30:
        risk_level = "MEDIUM"

        action = (
            "Monitor closely. "
            "Wait for confirmation before adding exposure."
        )

    else:
        risk_level = "LOW"

        action = (
            "Risk currently within acceptable limits."
        )


    return {

        "Risk Score": risk_score,
        "Risk Level": risk_level,
        "Loss Percentage": round(loss_percent, 2),
        "Reasons": reasons,
        "JKJ Action": action

    }

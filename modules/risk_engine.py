"""
JKJ AI Trader
Risk Engine v0.1

Purpose:
Evaluate the risk level of a stock holding using measurable evidence.

Wisdom Before Wealth.

This module:
- Measures risk
- Explains risk
- Does NOT make trade decisions
- Does NOT execute trades
- Does NOT modify the portfolio
"""


def calculate_risk(
    opportunity_score,
    stock_loss,
    rsi=None,
    volume_trend="Unknown",
    portfolio_concentration=0,
    distance_from_high=None,
):
    """
    Calculate an explainable risk level.

    Returns:
        LOW / MEDIUM / HIGH
        together with risk score and explanations.
    """

    risk_score = 0
    reasons = []

    # ---------------------------------------------------------
    # 1. Opportunity Score
    # ---------------------------------------------------------

    if opportunity_score is None:
        reasons.append(
            "Opportunity score unavailable."
        )
    else:
        opportunity_score = float(opportunity_score)

        if opportunity_score < 50:
            risk_score += 25
            reasons.append(
                f"Opportunity score is weak at "
                f"{opportunity_score:.0f}/100."
            )

        elif opportunity_score < 70:
            risk_score += 15
            reasons.append(
                f"Opportunity score is moderate at "
                f"{opportunity_score:.0f}/100."
            )

        else:
            reasons.append(
                f"Opportunity score is supportive at "
                f"{opportunity_score:.0f}/100."
            )

    # ---------------------------------------------------------
    # 2. Holding Loss
    # ---------------------------------------------------------

    stock_loss = float(stock_loss)

    if stock_loss <= -30:
        risk_score += 30
        reasons.append(
            f"Severe holding loss of {stock_loss:.2f}%."
        )

    elif stock_loss <= -20:
        risk_score += 20
        reasons.append(
            f"Significant holding loss of {stock_loss:.2f}%."
        )

    elif stock_loss < 0:
        risk_score += 10
        reasons.append(
            f"Holding is down {abs(stock_loss):.2f}%."
        )

    else:
        reasons.append(
            f"Holding is profitable at {stock_loss:.2f}%."
        )

    # ---------------------------------------------------------
    # 3. RSI
    # ---------------------------------------------------------

    if rsi is not None:

        rsi = float(rsi)

        if rsi < 20:
            risk_score += 5
            reasons.append(
                f"RSI is deeply oversold at {rsi:.2f}; "
                "reversal risk exists."
            )

        elif rsi < 30:
            risk_score += 3
            reasons.append(
                f"RSI is oversold at {rsi:.2f}."
            )

        elif rsi > 70:
            risk_score += 5
            reasons.append(
                f"RSI is overbought at {rsi:.2f}."
            )

    else:
        reasons.append(
            "RSI data unavailable."
        )

    # ---------------------------------------------------------
    # 4. Volume Trend
    # ---------------------------------------------------------

    volume_trend = str(volume_trend).upper()

    if volume_trend == "DECREASING":
        risk_score += 10
        reasons.append(
            "Volume is decreasing; confirmation is limited."
        )

    elif volume_trend == "INCREASING":
        reasons.append(
            "Volume is increasing and provides stronger confirmation."
        )

    else:
        risk_score += 5
        reasons.append(
            "Volume confirmation is limited."
        )

    # ---------------------------------------------------------
    # 5. Portfolio Concentration
    # ---------------------------------------------------------

    portfolio_concentration = float(
        portfolio_concentration
    )

    if portfolio_concentration >= 75:
        risk_score += 20
        reasons.append(
            f"Very high portfolio concentration at "
            f"{portfolio_concentration:.2f}%."
        )

    elif portfolio_concentration >= 50:
        risk_score += 15
        reasons.append(
            f"High portfolio concentration at "
            f"{portfolio_concentration:.2f}%."
        )

    elif portfolio_concentration > 0:
        risk_score += 5
        reasons.append(
            f"Portfolio concentration is "
            f"{portfolio_concentration:.2f}%."
        )

    # ---------------------------------------------------------
    # 6. Distance From 52-Week High
    # ---------------------------------------------------------

    if distance_from_high is not None:

        distance_from_high = float(
            distance_from_high
        )

        if distance_from_high >= 40:
            risk_score += 10
            reasons.append(
                f"Price is {distance_from_high:.2f}% "
                "below the 52-week high."
            )

        elif distance_from_high >= 25:
            risk_score += 5
            reasons.append(
                f"Price is {distance_from_high:.2f}% "
                "below the 52-week high."
            )

    else:
        reasons.append(
            "52-week high distance unavailable."
        )

    # ---------------------------------------------------------
    # 7. Final Risk Classification
    # ---------------------------------------------------------

    if risk_score >= 60:
        risk_level = "HIGH"

    elif risk_score >= 35:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    # ---------------------------------------------------------
    # 8. Capital Protection Message
    # ---------------------------------------------------------

    if risk_level == "HIGH":
        reasons.append(
            "Capital protection should take priority."
        )

    elif risk_level == "MEDIUM":
        reasons.append(
            "Additional exposure should be considered carefully."
        )

    else:
        reasons.append(
            "Current measurable risk is within acceptable limits."
        )

    return {
        "Risk Level": risk_level,
        "Risk Score": risk_score,
        "Risk Explanation": reasons
    }
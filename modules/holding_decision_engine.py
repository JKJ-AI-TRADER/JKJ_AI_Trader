"""
JKJ AI Trader
Existing Holding Decision Engine v0.2

Purpose:
Evaluate an existing stock holding and produce an explainable
JKJ decision.

This module does NOT:
- execute trades
- connect to Zerodha
- modify the database
- modify the portfolio

It only evaluates evidence and returns a decision.
"""


def evaluate_holding(
    stock_name,
    stock_loss,
    opportunity_score,
    risk_level,
    trend,
    rsi=None,
    sector_strength="UNKNOWN",
    volume_trend="UNKNOWN",
    portfolio_concentration=0,
):
    """
    Evaluate an existing portfolio holding.

    Parameters
    ----------
    stock_name : str
        Stock symbol/name.

    stock_loss : float
        Current profit/loss percentage of the holding.
        Example: -43.11 means a 43.11% loss.

    opportunity_score : float
        JKJ Opportunity Intelligence Score, 0-100.

    risk_level : str
        LOW / MEDIUM / HIGH.

    trend : str
        IMPROVING / STABLE / DETERIORATING / UNKNOWN.

    rsi : float, optional
        Relative Strength Index.

    sector_strength : str
        STRONG / NEUTRAL / WEAK / UNKNOWN.

    volume_trend : str
        INCREASING / STABLE / DECREASING / UNKNOWN.

    portfolio_concentration : float
        Percentage of portfolio represented by this holding.

    Returns
    -------
    dict
        Explainable JKJ holding decision.
    """

    reasons = []
    warnings = []
    positive_signals = []

    # Normalize text inputs
    risk_level = str(risk_level).upper()
    trend = str(trend).upper()
    sector_strength = str(sector_strength).upper()
    volume_trend = str(volume_trend).upper()

    # ---------------------------------------------------------
    # 1. Validate core inputs
    # ---------------------------------------------------------

    if opportunity_score is None:
        return {
            "Stock": stock_name,
            "JKJ Decision": "INSUFFICIENT DATA",
            "Confidence": 0,
            "Reasons": ["Opportunity score is unavailable."],
            "Warnings": [],
            "Positive Signals": [],
        }

    try:
        opportunity_score = float(opportunity_score)
        stock_loss = float(stock_loss)
        portfolio_concentration = float(portfolio_concentration)
    except (TypeError, ValueError):
        return {
            "Stock": stock_name,
            "JKJ Decision": "INSUFFICIENT DATA",
            "Confidence": 0,
            "Reasons": ["Invalid holding data supplied to decision engine."],
            "Warnings": [],
            "Positive Signals": [],
        }

    # ---------------------------------------------------------
    # 2. Holding loss assessment
    # ---------------------------------------------------------

    severe_loss = stock_loss <= -30
    major_loss = stock_loss <= -20
    loss_position = stock_loss < 0
    profitable = stock_loss >= 0

    if severe_loss:
        warnings.append(
            f"Holding loss is severe at {stock_loss:.2f}%."
        )
    elif major_loss:
        warnings.append(
            f"Holding loss is significant at {stock_loss:.2f}%."
        )
    elif loss_position:
        warnings.append(
            f"Holding is currently down {abs(stock_loss):.2f}%."
        )
    else:
        positive_signals.append(
            f"Holding is currently profitable at {stock_loss:.2f}%."
        )

    # ---------------------------------------------------------
    # 3. Opportunity assessment
    # ---------------------------------------------------------

    if opportunity_score >= 80:
        positive_signals.append(
            f"Strong opportunity score of {opportunity_score:.0f}/100."
        )
    elif opportunity_score >= 70:
        positive_signals.append(
            f"Reasonable opportunity score of {opportunity_score:.0f}/100."
        )
    elif opportunity_score >= 60:
        reasons.append(
            f"Opportunity score is moderate at {opportunity_score:.0f}/100."
        )
    else:
        warnings.append(
            f"Opportunity score is weak at {opportunity_score:.0f}/100."
        )

    # ---------------------------------------------------------
    # 4. Trend assessment
    # ---------------------------------------------------------

    if trend == "IMPROVING":
        positive_signals.append(
            "Trend is showing signs of improvement."
        )
    elif trend == "STABLE":
        reasons.append(
            "Trend is currently stable."
        )
    elif trend == "DETERIORATING":
        warnings.append(
            "Trend is deteriorating."
        )
    else:
        reasons.append(
            "Trend confirmation is unavailable."
        )

    # ---------------------------------------------------------
    # 5. Risk assessment
    # ---------------------------------------------------------

    if risk_level == "HIGH":
        warnings.append(
            "Holding is classified as HIGH risk."
        )
    elif risk_level == "MEDIUM":
        reasons.append(
            "Holding is classified as MEDIUM risk."
        )
    elif risk_level == "LOW":
        positive_signals.append(
            "Holding is classified as LOW risk."
        )
    else:
        reasons.append(
            "Risk classification requires confirmation."
        )

    # ---------------------------------------------------------
    # 6. RSI assessment
    # ---------------------------------------------------------

    deeply_oversold = False

    if rsi is not None:
        try:
            rsi = float(rsi)

            if rsi < 20:
                deeply_oversold = True
                positive_signals.append(
                    f"RSI is deeply oversold at {rsi:.2f}."
                )
                reasons.append(
                    "Deeply oversold conditions argue against an "
                    "automatic exit based only on price loss."
                )

            elif rsi < 30:
                positive_signals.append(
                    f"RSI is oversold at {rsi:.2f}."
                )

            elif rsi > 70:
                warnings.append(
                    f"RSI is overbought at {rsi:.2f}."
                )

        except (TypeError, ValueError):
            reasons.append(
                "RSI data is unavailable or invalid."
            )

    # ---------------------------------------------------------
    # 7. Sector assessment
    # ---------------------------------------------------------

    if sector_strength == "STRONG":
        positive_signals.append(
            "Sector strength is supportive."
        )
    elif sector_strength == "WEAK":
        warnings.append(
            "Sector momentum is weak."
        )
    elif sector_strength == "NEUTRAL":
        reasons.append(
            "Sector strength is neutral."
        )
    else:
        reasons.append(
            "Sector strength requires confirmation."
        )

    # ---------------------------------------------------------
    # 8. Volume assessment
    # ---------------------------------------------------------

    if volume_trend == "INCREASING":
        positive_signals.append(
            "Volume is increasing and may provide confirmation."
        )
    elif volume_trend == "DECREASING":
        warnings.append(
            "Volume is decreasing and confirmation is limited."
        )
    elif volume_trend == "STABLE":
        reasons.append(
            "Volume is stable."
        )
    else:
        reasons.append(
            "Volume confirmation is unavailable."
        )

    # ---------------------------------------------------------
    # 9. Portfolio concentration
    # ---------------------------------------------------------

    concentrated = portfolio_concentration >= 50

    if portfolio_concentration >= 75:
        warnings.append(
            f"Portfolio concentration is very high at "
            f"{portfolio_concentration:.2f}%."
        )
    elif portfolio_concentration >= 50:
        warnings.append(
            f"Portfolio concentration is high at "
            f"{portfolio_concentration:.2f}%."
        )
    elif portfolio_concentration > 0:
        reasons.append(
            f"Portfolio concentration is "
            f"{portfolio_concentration:.2f}%."
        )

    # ---------------------------------------------------------
    # 10. Decision logic
    # ---------------------------------------------------------

    decision = "HOLD & MONITOR"

    # Strong recovery setup
    if (
        opportunity_score >= 80
        and risk_level != "HIGH"
        and trend == "IMPROVING"
    ):
        decision = "HOLD"

    # Strong deterioration
    elif (
        severe_loss
        and opportunity_score < 50
        and risk_level == "HIGH"
        and trend == "DETERIORATING"
    ):
        decision = "EXIT"

    # Significant deterioration
    elif (
        severe_loss
        and (
            opportunity_score < 60
            or risk_level == "HIGH"
        )
        and trend == "DETERIORATING"
    ):
        decision = "REVIEW EXIT"

    # Large loss with weak conditions
    elif (
        major_loss
        and opportunity_score < 60
        and risk_level == "HIGH"
    ):
        decision = "REDUCE"

    # Large loss but evidence of recovery
    elif (
        major_loss
        and opportunity_score >= 75
        and risk_level != "HIGH"
        and trend == "IMPROVING"
    ):
        decision = "HOLD"

    # Large loss + uncertain recovery
    elif severe_loss:
        decision = "REDUCE"

    # Profitable but deteriorating
    elif (
        profitable
        and trend == "DETERIORATING"
        and (
            opportunity_score < 60
            or risk_level == "HIGH"
        )
    ):
        decision = "REDUCE"

    # Moderate loss with weak opportunity
    elif (
        loss_position
        and opportunity_score < 60
        and trend == "DETERIORATING"
    ):
        decision = "REDUCE"

    # Healthy holding
    elif (
        opportunity_score >= 70
        and risk_level != "HIGH"
        and trend in ("IMPROVING", "STABLE")
    ):
        decision = "HOLD"

    # ---------------------------------------------------------
    # 11. Capital protection rules
    # ---------------------------------------------------------

    if concentrated:
        reasons.append(
            "Capital protection is important because this holding "
            "represents a large portion of the portfolio."
        )

    if severe_loss:
        reasons.append(
            "JKJ will not recommend additional exposure solely "
            "because the stock has fallen significantly."
        )

    # ---------------------------------------------------------
    # 12. Confidence
    # ---------------------------------------------------------

    confidence = 50

    if opportunity_score >= 70:
        confidence += 10

    if trend in ("IMPROVING", "DETERIORATING"):
        confidence += 10

    if risk_level in ("LOW", "MEDIUM", "HIGH"):
        confidence += 5

    if sector_strength in ("STRONG", "WEAK"):
        confidence += 5

    if volume_trend in ("INCREASING", "DECREASING"):
        confidence += 5

    if rsi is not None:
        confidence += 5

    confidence = min(confidence, 95)

    # Deeply oversold situations should have slightly lower
    # confidence in an EXIT decision because reversal risk exists.
    if deeply_oversold and decision in ("EXIT", "REVIEW EXIT"):
        confidence = max(confidence - 10, 40)

    return {
        "Stock": stock_name,
        "JKJ Decision": decision,
        "Confidence": confidence,
        "Reasons": reasons,
        "Warnings": warnings,
        "Positive Signals": positive_signals,
    }

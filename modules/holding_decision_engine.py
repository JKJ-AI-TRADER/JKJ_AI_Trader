"""
JKJ AI Holding Decision Engine v0.2

Wisdom Before Wealth.

A loss alone is NOT a reason to hold a stock.

Continued holding must be supported by evidence of recovery,
acceptable risk and a favourable longer-term outlook.
"""


def analyze_holding(
    stock_name,
    stock_loss,
    opportunity_score,
    risk_level,
    trend,
    long_term_trend="UNKNOWN",
    recovery_confirmed=False,
    rsi=None,
    sector_strength="UNKNOWN",
    volume_trend="UNKNOWN",
    portfolio_concentration=0,
):
    """
    Analyse an existing stock holding.

    Parameters
    ----------
    stock_name : str
        Stock symbol or name.

    stock_loss : float
        Current profit/loss percentage.
        Negative value means loss.

    opportunity_score : float
        Opportunity score from 0 to 100.

    risk_level : str
        LOW, MEDIUM or HIGH.

    trend : str
        Short-term trend:
        IMPROVING, STABLE, DETERIORATING or UNKNOWN.

    long_term_trend : str
        UPTREND, DOWNTREND, SIDEWAYS or UNKNOWN.

    recovery_confirmed : bool
        True only when evidence supports a genuine recovery.

    Returns
    -------
    dict
        Explainable JKJ holding decision.
    """

    reasons = []
    warnings = []
    positive_signals = []

    risk_level = str(risk_level).upper()
    trend = str(trend).upper()
    long_term_trend = str(long_term_trend).upper()

    # ---------------------------------------------
    # 1. LONG-TERM DOWNTREND WARNING
    # ---------------------------------------------

    long_term_weak = (
        long_term_trend == "DOWNTREND"
        and not recovery_confirmed
    )

    if long_term_weak:
        warnings.append(
            "Long-term trend remains in a downtrend without confirmed recovery."
        )

    # ---------------------------------------------
    # 2. SEVERE LOSS
    # ---------------------------------------------

    if stock_loss <= -30:

        if long_term_weak:

            if opportunity_score < 70 or risk_level == "HIGH":
                decision = "EXIT"

                reasons.append(
                    "The stock has suffered a severe loss."
                )

                reasons.append(
                    "The longer-term downtrend has not shown confirmed recovery."
                )

                reasons.append(
                    "Continuing to hold does not currently provide sufficient "
                    "evidence of capital protection."
                )

            else:
                decision = "REDUCE"

                reasons.append(
                    "The stock has suffered a severe loss."
                )

                reasons.append(
                    "There are some positive signals, but the longer-term "
                    "downtrend remains unresolved."
                )

                reasons.append(
                    "Reducing exposure protects capital while allowing "
                    "limited participation in a possible recovery."
                )

        elif (
            opportunity_score >= 80
            and risk_level != "HIGH"
            and trend == "IMPROVING"
            and recovery_confirmed
        ):
            decision = "HOLD"

            reasons.append(
                "Recovery is supported by improving conditions."
            )

            positive_signals.append(
                "Strong opportunity score."
            )

            positive_signals.append(
                "Recovery has been confirmed."
            )

        else:
            decision = "REDUCE"

            reasons.append(
                "The stock has suffered a severe loss."
            )

            reasons.append(
                "Recovery evidence is not yet strong enough for a full HOLD."
            )

    # ---------------------------------------------
    # 3. SIGNIFICANT LOSS
    # ---------------------------------------------

    elif stock_loss <= -20:

        if long_term_weak:

            if (
                opportunity_score < 60
                or risk_level == "HIGH"
                or trend == "DETERIORATING"
            ):
                decision = "EXIT"

                reasons.append(
                    "The stock has a significant loss combined with "
                    "an unresolved longer-term downtrend."
                )

                reasons.append(
                    "Capital should not remain committed without "
                    "credible recovery evidence."
                )

            else:
                decision = "REDUCE"

                reasons.append(
                    "The stock remains significantly below the purchase price."
                )

                reasons.append(
                    "Short-term signals are not sufficient to override "
                    "the longer-term downtrend."
                )

        elif (
            opportunity_score >= 75
            and risk_level != "HIGH"
            and trend == "IMPROVING"
            and recovery_confirmed
        ):
            decision = "HOLD"

            reasons.append(
                "The position is at a significant loss, but recovery "
                "conditions are supported by evidence."
            )

            positive_signals.append(
                "Strong opportunity conditions."
            )

            positive_signals.append(
                "Recovery has been confirmed."
            )

        else:
            decision = "WATCH"

            reasons.append(
                "The stock is under pressure and requires continued monitoring."
            )

            reasons.append(
                "Recovery evidence is not yet strong enough for a confident HOLD."
            )

    # ---------------------------------------------
    # 4. MODERATE LOSS
    # ---------------------------------------------

    elif stock_loss < 0:

        if long_term_weak:

            decision = "WATCH"

            reasons.append(
                "The position is losing value and the longer-term trend remains weak."
            )

        elif (
            opportunity_score >= 70
            and risk_level != "HIGH"
        ):
            decision = "HOLD"

            reasons.append(
                "The loss is moderate and overall conditions remain acceptable."
            )

        else:
            decision = "WATCH"

            reasons.append(
                "The position requires closer monitoring."
            )

    # ---------------------------------------------
    # 5. PROFIT OR BREAKEVEN
    # ---------------------------------------------

    else:

        if long_term_trend == "DOWNTREND":

            decision = "WATCH"

            reasons.append(
                "The position is currently profitable or breakeven, "
                "but the longer-term trend is weakening."
            )

        elif opportunity_score >= 70 and risk_level != "HIGH":

            decision = "HOLD"

            reasons.append(
                "The existing position remains supported by acceptable conditions."
            )

        else:

            decision = "WATCH"

            reasons.append(
                "Opportunity conditions have weakened."
            )

    # ---------------------------------------------
    # ADDITIONAL WARNINGS
    # ---------------------------------------------

    if portfolio_concentration > 25:
        warnings.append(
            "Portfolio concentration in this position is above the preferred level."
        )

    if rsi is not None:
        try:
            rsi_value = float(rsi)

            if rsi_value >= 70:
                warnings.append(
                    "RSI indicates the stock may be overbought."
                )

            elif rsi_value <= 30:
                positive_signals.append(
                    "RSI indicates potentially oversold conditions."
                )

        except (ValueError, TypeError):
            pass

    return {
        "Stock": stock_name,
        "JKJ Decision": decision,
        "Confidence": opportunity_score,
        "Reasons": reasons,
        "Warnings": warnings,
        "Positive Signals": positive_signals,
        "Short-Term Trend": trend,
        "Long-Term Trend": long_term_trend,
        "Recovery Confirmed": recovery_confirmed,
    }
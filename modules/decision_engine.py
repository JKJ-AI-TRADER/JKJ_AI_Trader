"""
JKJ AI Decision Engine v0.3

Wisdom Before Wealth.

The Decision Engine considers:
- Opportunity Score
- Risk Level
- Portfolio Loss
- Whether the stock is already held
- Individual Stock Loss
- Stock Trend

The engine must explain every decision.
"""


def generate_decision(
    opportunity_score,
    risk_level,
    portfolio_loss,
    holding_status=False,
    stock_loss=0,
    trend="UNKNOWN"
):
    """
    Generate an explainable JKJ AI decision.

    Parameters
    ----------
    opportunity_score : int or float
        Opportunity score from 0 to 100.

    risk_level : str
        LOW, MEDIUM or HIGH.

    portfolio_loss : float
        Portfolio return/loss percentage.

    holding_status : bool
        True if the stock is already in the portfolio.

    stock_loss : float
        Profit/loss percentage of the individual stock.

    trend : str
        IMPROVING, STABLE, DETERIORATING or UNKNOWN.

    Returns
    -------
    dict
        JKJ Decision and Reasons.
    """

    reasons = []

    risk_level = str(risk_level).upper()
    trend = str(trend).upper()

    # -------------------------------------------------
    # 1. CAPITAL PROTECTION
    # -------------------------------------------------

    if portfolio_loss <= -20:
        reasons.append(
            "Portfolio drawdown exceeds the JKJ safety threshold."
        )

        if not holding_status:
            reasons.append(
                "New exposure should be avoided until portfolio risk improves."
            )

            return {
                "JKJ Decision": "WAIT",
                "Reasons": reasons
            }

    # -------------------------------------------------
    # 2. EXISTING HOLDING ANALYSIS
    # -------------------------------------------------

    if holding_status:

        # Severe individual stock loss
        if stock_loss <= -30:

            if (
                opportunity_score >= 80
                and risk_level != "HIGH"
                and trend == "IMPROVING"
            ):
                decision = "HOLD"

                reasons.append(
                    "Stock is deeply below purchase price."
                )

                reasons.append(
                    "Strong opportunity score and improving trend "
                    "provide evidence for continued holding."
                )

            elif (
                opportunity_score < 60
                or risk_level == "HIGH"
                or trend == "DETERIORATING"
            ):
                decision = "EXIT"

                reasons.append(
                    "Stock has suffered a severe decline."
                )

                reasons.append(
                    "Current opportunity/risk/trend conditions do not "
                    "justify continuing the position."
                )

            else:
                decision = "REDUCE"

                reasons.append(
                    "Stock is down more than 30%."
                )

                reasons.append(
                    "Evidence is insufficient for a full HOLD."
                )

                reasons.append(
                    "Reduce exposure and protect remaining capital."
                )

        # Significant individual stock loss
        elif stock_loss <= -20:

            if (
                opportunity_score >= 75
                and risk_level != "HIGH"
                and trend == "IMPROVING"
            ):
                decision = "HOLD"

                reasons.append(
                    "Stock is significantly below purchase price."
                )

                reasons.append(
                    "Opportunity score and improving trend support holding."
                )

            elif (
                opportunity_score < 50
                or risk_level == "HIGH"
                or trend == "DETERIORATING"
            ):
                decision = "REDUCE"

                reasons.append(
                    "Significant stock loss combined with weak conditions."
                )

                reasons.append(
                    "Capital protection takes priority."
                )

            else:
                decision = "HOLD"

                reasons.append(
                    "Stock is under pressure but current evidence "
                    "does not justify an immediate exit."
                )

        # Moderate loss
        elif stock_loss < 0:

            if opportunity_score >= 70 and risk_level != "HIGH":
                decision = "HOLD"

                reasons.append(
                    "Moderate loss with acceptable opportunity conditions."
                )

            else:
                decision = "WATCH"

                reasons.append(
                    "Position is losing value and requires closer monitoring."
                )

        # Profitable / breakeven holding
        else:

            if (
                opportunity_score >= 85
                and risk_level != "HIGH"
            ):
                decision = "HOLD"

                reasons.append(
                    "Existing position remains supported by a strong "
                    "opportunity score."
                )

            elif opportunity_score >= 70:
                decision = "HOLD"

                reasons.append(
                    "Existing position remains acceptable."
                )

            else:
                decision = "WATCH"

                reasons.append(
                    "Opportunity score has weakened."
                )

        # Add portfolio-level warning where relevant
        if portfolio_loss <= -20:
            reasons.append(
                "Portfolio-level capital protection remains active."
            )

        return {
            "JKJ Decision": decision,
            "Reasons": reasons
        }

    # -------------------------------------------------
    # 3. NEW STOCK / NOT CURRENTLY HELD
    # -------------------------------------------------

    if risk_level == "HIGH":

        if opportunity_score >= 85:
            decision = "WATCH"

            reasons.append(
                "Strong opportunity score but risk level is HIGH."
            )

            reasons.append(
                "Confirmation is required before considering entry."
            )

        else:
            decision = "WAIT"

            reasons.append(
                "Risk level is HIGH and opportunity score is insufficient."
            )

    elif opportunity_score >= 85:

        decision = "REVIEW BUY"

        reasons.append(
            "Strong opportunity score."
        )

        reasons.append(
            "Further validation is required before entry."
        )

    elif opportunity_score >= 70:

        decision = "WATCH"

        reasons.append(
            "Good opportunity setup but confirmation is required."
        )

    else:

        decision = "WAIT"

        reasons.append(
            "Opportunity score is below the preferred level."
        )

    return {
        "JKJ Decision": decision,
        "Reasons": reasons
    }

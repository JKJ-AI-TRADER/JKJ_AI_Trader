"""
JKJ AI Intraday Decision Engine v0.1

Wisdom Before Wealth.

A trade should only be taken when:

1. The intraday market environment is suitable.
2. The stock setup is strong enough.
3. The trade risk is acceptable.

This engine combines those three layers
into one clear trading decision.
"""


def make_intraday_decision(
    market_result,
    setup_result,
    risk_result
):
    """
    Combine Market, Setup and Risk evidence
    into a final intraday trading decision.

    Returns:

    TRADE NOW
    WATCH FOR ENTRY
    WAIT
    NO TRADE
    """

    reasons = []
    warnings = []

    # -----------------------------------------
    # EXTRACT VALUES SAFELY
    # -----------------------------------------

    market_allowed = market_result.get(
        "Trading Allowed",
        False
    )

    market_status = market_result.get(
        "Intraday Market Status",
        "UNKNOWN"
    )

    setup_candidate = setup_result.get(
        "Trade Candidate",
        False
    )

    setup_score = setup_result.get(
        "Setup Score",
        0
    )

    setup_status = setup_result.get(
        "Intraday Setup Status",
        "UNKNOWN"
    )

    risk_allowed = risk_result.get(
        "Trade Allowed",
        False
    )

    risk_status = risk_result.get(
        "Risk Status",
        "UNKNOWN"
    )

    risk_level = risk_result.get(
        "Risk Level",
        "HIGH"
    )

    # -----------------------------------------
    # 1. MARKET NOT SUITABLE
    # -----------------------------------------

    if not market_allowed:

        decision = "NO TRADE"

        reasons.append(
            "The overall intraday market environment "
            "is not suitable for new trades."
        )

        warnings.append(
            "Do not force a trade against the "
            "broader market conditions."
        )

    # -----------------------------------------
    # 2. SETUP NOT STRONG ENOUGH
    # -----------------------------------------

    elif not setup_candidate:

        decision = "WATCH FOR ENTRY"

        reasons.append(
            "The market environment is acceptable, "
            "but the stock setup is not yet strong enough."
        )

        warnings.append(
            "Wait for better technical confirmation."
        )

    # -----------------------------------------
    # 3. RISK NOT ACCEPTABLE
    # -----------------------------------------

    elif not risk_allowed:

        decision = "NO TRADE"

        reasons.append(
            "The trade setup may be attractive, "
            "but the proposed risk is not acceptable."
        )

        warnings.append(
            "Do not compromise capital protection "
            "for a potential opportunity."
        )

    # -----------------------------------------
    # 4. CAUTION CONDITIONS
    # -----------------------------------------

    elif (
        setup_score < 70
        or risk_level == "MEDIUM"
    ):

        decision = "WATCH FOR ENTRY"

        reasons.append(
            "The trade conditions are acceptable, "
            "but confirmation is not yet strong enough "
            "for immediate entry."
        )

        warnings.append(
            "Wait for stronger setup or lower risk "
            "before entering the trade."
        )

    # -----------------------------------------
    # 5. STRONG TRADE CONDITIONS
    # -----------------------------------------

    else:

        decision = "TRADE NOW"

        reasons.append(
            "Market conditions are suitable."
        )

        reasons.append(
            "The stock has a strong intraday setup."
        )

        reasons.append(
            "Trade risk is within acceptable limits."
        )

        reasons.append(
            "The trade satisfies the minimum JKJ "
            "intraday confirmation requirements."
        )

    # -----------------------------------------
    # CONFIDENCE SCORE
    # -----------------------------------------

    confidence = 0

    if market_allowed:
        confidence += 30

    if setup_candidate:
        confidence += 40

    if risk_allowed:
        confidence += 30

    confidence = min(
        confidence,
        100
    )

    return {
        "Final Decision": decision,
        "Confidence": confidence,
        "Market Status": market_status,
        "Setup Status": setup_status,
        "Risk Status": risk_status,
        "Risk Level": risk_level,
        "Reasons": reasons,
        "Warnings": warnings
    }
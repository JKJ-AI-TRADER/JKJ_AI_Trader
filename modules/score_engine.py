"""
JKJ AI Score Engine v0.1

Wisdom Before Wealth.

This engine combines evidence from:
- Market Engine
- Technical Engine
- Opportunity Engine

The result is an explainable combined score
out of 100.

No BUY or SELL decision is made here.
"""


def calculate_combined_score(
    market_result,
    technical_result,
    opportunity_result
):
    """
    Combine standardized scores from the
    Market, Technical and Opportunity engines.

    Returns an explainable combined score out of 100.
    """

    reasons = []

    # Extract standardized scores safely
    market_score = market_result.get("Standard Score", 0)
    technical_score = technical_result.get("Standard Score", 0)
    opportunity_score = opportunity_result.get(
        "Standard Score",
        0
    )

    # Equal weighting for Version 0.1
    market_weight = 1 / 3
    technical_weight = 1 / 3
    opportunity_weight = 1 / 3

    combined_score = (
        market_score * market_weight
        + technical_score * technical_weight
        + opportunity_score * opportunity_weight
    )

    combined_score = round(combined_score, 2)

    # Explain the evidence
    reasons.append(
        f"Market Standard Score: {market_score}"
    )

    reasons.append(
        f"Technical Standard Score: {technical_score}"
    )

    reasons.append(
        f"Opportunity Standard Score: {opportunity_score}"
    )

    reasons.append(
        "Combined using equal weighting across "
        "Market, Technical and Opportunity evidence."
    )

    return {
        "Combined Opportunity Score": combined_score,
        "Maximum Score": 100,
        "Market Weight": round(market_weight * 100, 2),
        "Technical Weight": round(technical_weight * 100, 2),
        "Opportunity Weight": round(
            opportunity_weight * 100,
            2
        ),
        "Explanation": reasons
    }
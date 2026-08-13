def calculate_opportunity_score(
    market_alignment,
    sector_strength,
    technical_quality,
    volume_confirmation,
    risk_reward
):
    """
    JKJ AI Opportunity Engine v0.1

    Every score must be explainable.
    Wisdom Before Wealth.
    """

    total_score = (
        market_alignment
        + sector_strength
        + technical_quality
        + volume_confirmation
        + risk_reward
    )

    explanation = []

    if market_alignment >= 16:
        explanation.append("Market trend is supportive")
    else:
        explanation.append("Market trend needs caution")

    if sector_strength >= 16:
        explanation.append("Sector strength is positive")
    else:
        explanation.append("Sector momentum is weak")

    if technical_quality >= 16:
        explanation.append("Technical setup is healthy")
    else:
        explanation.append("Technical setup needs review")

    if volume_confirmation >= 16:
        explanation.append("Volume confirms interest")
    else:
        explanation.append("Volume confirmation is limited")

    if risk_reward >= 16:
        explanation.append("Risk reward is favourable")
    else:
        explanation.append("Risk reward requires caution")

    return {
        "Market Alignment": market_alignment,
        "Sector Strength": sector_strength,
        "Technical Quality": technical_quality,
        "Volume Confirmation": volume_confirmation,
        "Risk Reward": risk_reward,
        "Overall Score": total_score,
        "Explanation": explanation
    }
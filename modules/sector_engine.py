def calculate_sector_strength(stock):
    """
    JKJ AI Sector Intelligence Engine v0.1

    Wisdom Before Wealth:
    Every score must have a reason.
    """

    score = 0
    reasons = []

    sector = stock.get("Sector", "Unknown")

    if sector == "Unknown":
        score += 10
        reasons.append(
            "Sector data unavailable; neutral sector score applied"
        )

    else:
        score += 15
        reasons.append(
            f"Sector identified: {sector}"
        )

    return {
        "Sector Strength Score": score,
        "Sector Explanation": reasons
    }

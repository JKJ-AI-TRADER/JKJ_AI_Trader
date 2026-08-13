def calculate_volume_confirmation(stock):
    """
    JKJ AI Volume Confirmation Engine v0.1

    Wisdom Before Wealth.

    Every score must have a reason.
    """

    score = 0
    reasons = []

    volume_trend = stock.get("Volume Trend", "Unknown")
    current_price = stock.get("Current Price", 0)
    high_52 = stock.get("52 Week High", 0)

    # Volume analysis

    if volume_trend == "Increasing":
        score += 15
        reasons.append(
            "Volume is increasing, showing market interest"
        )

    elif volume_trend == "Decreasing":
        score += 8
        reasons.append(
            "Volume is decreasing, confirmation is limited"
        )

    else:
        score += 10
        reasons.append(
            "Volume data requires further analysis"
        )


    # Price-volume relationship

    if current_price > 0 and high_52 > 0:

        distance_from_high = (
            (high_52 - current_price) / high_52
        ) * 100

        if distance_from_high < 15:
            score += 5
            reasons.append(
                "Price strength is supported near high levels"
            )

        else:
            score += 3
            reasons.append(
                "Price is away from high levels; confirmation needed"
            )


    return {
        "Volume Confirmation Score": score,
        "Volume Explanation": reasons
    }

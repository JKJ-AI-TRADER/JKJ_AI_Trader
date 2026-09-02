"""
JKJ AI Opportunity Engine v0.2

Wisdom Before Wealth.

A falling stock is not automatically an opportunity.

This engine looks for:
- Price momentum
- Volume support
- Healthy momentum
- Early recovery evidence

Recovery candidates may be identified for WATCH,
but strong evidence is required before a stock
is considered a strong opportunity.
"""


def analyze_opportunity(stock_data):
    """
    Identify whether a stock shows a potential opportunity.

    This engine analyses market evidence only.
    It does not generate a final buy or sell decision.
    """

    if not stock_data:
        return {
            "Opportunity Condition": "Unknown",
            "Opportunity Score": 0,
            "Maximum Score": 5,
            "Standard Score": 0,
            "Explanation": ["No stock data available."]
        }

    if stock_data.get("Data Status") != "COMPLETE":
        return {
            "Opportunity Condition": "Unknown",
            "Opportunity Score": 0,
            "Maximum Score": 5,
            "Standard Score": 0,
            "Explanation": ["Stock market data is incomplete."]
        }

    current_price = stock_data.get("Current Price")
    price_20d_ago = stock_data.get("Price 20 Days Ago")
    price_50d_ago = stock_data.get("Price 50 Days Ago")

    ma20 = stock_data.get("MA20")

    volume_trend = stock_data.get("Volume Trend")
    rsi = stock_data.get("RSI")

    short_term_trend = stock_data.get(
        "Short-Term Trend",
        "UNKNOWN"
    )

    recovery_confirmed = stock_data.get(
        "Recovery Confirmed",
        False
    )

    score = 0
    reasons = []

    # -----------------------------------------
    # 1. SHORT-TERM PRICE MOMENTUM
    # -----------------------------------------

    if (
        current_price is not None
        and price_20d_ago is not None
    ):

        if current_price > price_20d_ago:

            score += 1

            reasons.append(
                "Price is higher than 20 days ago."
            )

        else:

            reasons.append(
                "Price is not higher than 20 days ago."
            )

    # -----------------------------------------
    # 2. MEDIUM-TERM PRICE MOMENTUM
    # -----------------------------------------

    if (
        current_price is not None
        and price_50d_ago is not None
    ):

        if current_price > price_50d_ago:

            score += 1

            reasons.append(
                "Price is higher than 50 days ago."
            )

        else:

            reasons.append(
                "Price is not higher than 50 days ago."
            )

    # -----------------------------------------
    # 3. VOLUME SUPPORT
    # -----------------------------------------

    if volume_trend == "Increasing":

        score += 1

        reasons.append(
            "Volume is increasing."
        )

    elif volume_trend == "Decreasing":

        reasons.append(
            "Volume is decreasing."
        )

    else:

        reasons.append(
            "Volume is stable or unavailable."
        )

    # -----------------------------------------
    # 4. RSI MOMENTUM / RECOVERY
    # -----------------------------------------

    if rsi is not None:

        if 40 <= rsi <= 65:

            score += 1

            reasons.append(
                "RSI is in a favourable opportunity zone."
            )

        elif 30 <= rsi < 40:

            reasons.append(
                "RSI remains weak but may support a future "
                "recovery watch."
            )

        elif rsi < 30:

            reasons.append(
                "RSI is deeply oversold, but this alone is "
                "not a buy signal."
            )

        else:

            reasons.append(
                "RSI is relatively high."
            )

    # -----------------------------------------
    # 5. RECOVERY EVIDENCE
    # -----------------------------------------

    recovery_evidence = False

    if (
        short_term_trend == "IMPROVING"
        and current_price is not None
        and ma20 is not None
        and current_price > ma20
        and rsi is not None
        and rsi >= 40
    ):

        recovery_evidence = True

        score += 1

        reasons.append(
            "Short-term recovery evidence is appearing."
        )

    # -----------------------------------------
    # CONFIRMED RECOVERY
    # -----------------------------------------

    if recovery_confirmed:

        reasons.append(
            "Recovery has been confirmed by the trend engine."
        )

    # -----------------------------------------
    # FINAL OPPORTUNITY CONDITION
    # -----------------------------------------

    if score >= 4:

        opportunity_condition = (
            "Strong Opportunity"
        )

    elif score >= 2:

        opportunity_condition = (
            "Possible Opportunity"
        )

    elif recovery_evidence:

        opportunity_condition = (
            "Recovery Candidate"
        )

    else:

        opportunity_condition = (
            "Weak Opportunity"
        )

    standard_score = round(
        (score / 5) * 100,
        2
    )

    return {
        "Opportunity Condition": opportunity_condition,
        "Opportunity Score": score,
        "Maximum Score": 5,
        "Standard Score": standard_score,
        "Recovery Evidence": recovery_evidence,
        "Explanation": reasons
    }
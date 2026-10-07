"""
JKJ AI Buy Trigger Engine v0.1

Wisdom Before Wealth.

This engine identifies a potential price level where
a strong stock may become eligible for closer buying
consideration.

It does not place trades.
It does not guarantee a buy.
"""

def calculate_buy_trigger(
    stock_data,
    technical_result,
    decision_result,
    market_confirmation_result,
    stock_strength_score,
    momentum_score,
    risk_level
):

    # -----------------------------------------
    # BASIC DATA
    # -----------------------------------------

    current_price = stock_data.get(
        "Current Price",
        0
    )

    current_high = stock_data.get(
        "High",
        0
    )

    ma20 = stock_data.get(
        "MA20",
        0
    )

    technical_score = technical_result.get(
        "Standard Score",
        0
    )

    decision = decision_result.get(
        "JKJ Decision",
        "UNKNOWN"
    )

    # -----------------------------------------
    # DEFAULT RESULT
    # -----------------------------------------

    result = {
    "Buy Trigger": None,

    "Buy Trigger Status": "NOT AVAILABLE",

    "Trigger Explanation": (
        "No suitable buy trigger identified."
    ),

    "Buy Readiness": "NOT READY",

    "Missing Conditions": []
}
        # -----------------------------------------
    # BUY READINESS CHECK
    # -----------------------------------------

    missing_conditions = []

    buying_allowed = (
        market_confirmation_result.get(
            "Buying Allowed",
            False
        )
    )

    market_strength = (
        market_confirmation_result.get(
            "Market Strength",
            "UNKNOWN"
        )
    )

    if not buying_allowed:
        missing_conditions.append(
            "Market buying confirmation is not available"
        )

    if market_strength not in [
        "IMPROVING",
        "STRONG"
    ]:
        missing_conditions.append(
            "Market strength must improve"
        )

    if stock_strength_score < 80:
        missing_conditions.append(
            "Stock Strength Score must be 80 or above"
        )

    if momentum_score < 60:
        missing_conditions.append(
            "Momentum Score must improve to 60 or above"
        )

    if risk_level == "High":
        missing_conditions.append(
            "Risk level must not be High"
        )

    if decision != "BUY":
        missing_conditions.append(
            "JKJ Decision must change to BUY"
        )

    result["Missing Conditions"] = (
        missing_conditions
    )

    if not missing_conditions:

        result["Buy Readiness"] = (
            "BUY READY"
        )

    else:

        result["Buy Readiness"] = (
            "NOT READY"
        )
    # -----------------------------------------
    # CHECK TECHNICAL DATA
    # -----------------------------------------

    if (
        current_price is None
        or current_high is None
        or ma20 is None
    ):
        return result

    if (
        current_price <= 0
        or current_high <= 0
        or ma20 <= 0
    ):
        return result

    # -----------------------------------------
    # CHECK STOCK QUALITY
    # -----------------------------------------

    if technical_score < 60:

        result["Trigger Explanation"] = (
            "Technical strength is not yet sufficient "
            "for a buy trigger."
        )

        return result

    # -----------------------------------------
    # BASE TRIGGER LEVEL
    # -----------------------------------------

    base_trigger = max(
        current_high,
        ma20
    )

    # -----------------------------------------
    # CONFIRMATION BUFFER
    # -----------------------------------------

    confirmation_buffer = 0.005

    buy_trigger = (
        base_trigger
        * (1 + confirmation_buffer)
    )

    # -----------------------------------------
    # FINAL RESULT
    # -----------------------------------------

    result["Buy Trigger"] = round(
        buy_trigger,
        2
    )

    result["Buy Trigger Status"] = (
        "WAIT FOR PRICE CONFIRMATION"
    )

    result["Trigger Explanation"] = (
        "Consider entry only if price confirms "
        "strength above the trigger level."
    )

    return result
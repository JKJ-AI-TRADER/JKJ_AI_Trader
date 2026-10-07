"""
JKJ AI Market Confirmation Engine v0.3

Wisdom Before Wealth.

This engine determines whether the overall market
environment is suitable for taking new positions.

A strong stock alone is not enough.

The market must also provide sufficient confirmation.
"""


def analyse_market_confirmation(
    market_state,
    market_score
):
    """
    Determine the market confirmation status.

    Returns a clear market environment classification,
    market strength, recovery stage and whether
    new buying should be considered.
    """

    # -----------------------------------------
    # BEARISH MARKET
    # -----------------------------------------

    if market_state == "Bearish":

        return {
            "Market Confirmation Status":
                "MARKET UNFAVOURABLE",

            "Market Strength":
                "WEAK",

            "Recovery Stage":
                "BEARISH",

            "Buying Environment":
                "WEAK",

            "Buying Allowed":
                False,

            "Market Message":
                "Market is bearish. New buying is not recommended."
        }

    # -----------------------------------------
    # WEAK / EARLY RECOVERY MARKET
    # -----------------------------------------

    if market_score < 40:

        return {
            "Market Confirmation Status":
                "WEAK MARKET CONDITIONS",

            "Market Strength":
                "WEAK",

            "Recovery Stage":
                "EARLY RECOVERY",

            "Buying Environment":
                "CAUTIOUS",

            "Buying Allowed":
                False,

            "Market Message":
                "The market is weak but may be showing "
                "early signs of stabilisation. "
                "Wait for stronger confirmation."
        }

    # -----------------------------------------
    # MARKET RECOVERING
    # -----------------------------------------

    if market_score < 70:

        return {
            "Market Confirmation Status":
                "MARKET RECOVERING",

            "Market Strength":
                "IMPROVING",

            "Recovery Stage":
                "RECOVERING",

            "Buying Environment":
                "IMPROVING",

            "Buying Allowed":
                True,

            "Market Message":
                "Market recovery is developing. "
                "Only strong and lower-risk stocks "
                "should be considered."
        }

    # -----------------------------------------
    # BULLISH / CONFIRMED MARKET
    # -----------------------------------------

    return {
        "Market Confirmation Status":
            "MARKET CONFIRMED",

        "Market Strength":
            "STRONG",

        "Recovery Stage":
            "BULLISH",

        "Buying Environment":
            "FAVOURABLE",

        "Buying Allowed":
            True,

        "Market Message":
            "Market conditions are favourable for "
            "strong buying opportunities."
    }
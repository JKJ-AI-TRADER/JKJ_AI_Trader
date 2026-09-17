"""
JKJ AI Trader
NIFTY Option Market Context Evidence — V12.7 Stage 1

Purpose:
Extract observable market-context evidence from the
validated V12.6 momentum confirmation result.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


def evaluate_market_context_evidence(momentum_confirmation):
    """
    Evaluate observable market-context evidence from
    V12.6 Momentum Confirmation.
    """

    if not isinstance(momentum_confirmation, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Momentum confirmation must be a dictionary.",
        }

    if momentum_confirmation.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Momentum confirmation must have "
                "Status EVALUATED."
            ),
        }

    required_fields = [
        "Option Direction",
        "NIFTY Movement Evidence",
        "Price Movement Evidence",
        "Volume Evidence",
        "Open Interest Evidence",
        "Movement Relationship",
        "Momentum Confirmation",
    ]

    for field in required_fields:
        if field not in momentum_confirmation:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    option_direction = momentum_confirmation[
        "Option Direction"
    ]

    nifty_evidence = momentum_confirmation[
        "NIFTY Movement Evidence"
    ]

    price_evidence = momentum_confirmation[
        "Price Movement Evidence"
    ]

    volume_evidence = momentum_confirmation[
        "Volume Evidence"
    ]

    oi_evidence = momentum_confirmation[
        "Open Interest Evidence"
    ]

    relationship = momentum_confirmation[
        "Movement Relationship"
    ]

    momentum_status = momentum_confirmation[
        "Momentum Confirmation"
    ]

    return {
        "Status": "EVALUATED",
        "Trading Symbol": momentum_confirmation.get(
            "Trading Symbol"
        ),
        "Underlying": momentum_confirmation.get(
            "Underlying"
        ),
        "Expiry": momentum_confirmation.get(
            "Expiry"
        ),
        "Strike": momentum_confirmation.get(
            "Strike"
        ),
        "Option Type": momentum_confirmation.get(
            "Option Type"
        ),
        "Option Direction": option_direction,
        "NIFTY Movement Evidence": nifty_evidence,
        "Price Movement Evidence": price_evidence,
        "Volume Evidence": volume_evidence,
        "Open Interest Evidence": oi_evidence,
        "Movement Relationship": relationship,
        "Momentum Confirmation": momentum_status,
    }
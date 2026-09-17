"""
JKJ AI Trader
NIFTY Option Market Context Classification — V12.7 Stage 2

Purpose:
Classify observable market context using the existing
V12.5 Movement Relationship.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


VALID_CONTEXTS = {
    "MOVING_TOGETHER",
    "DIVERGING",
    "OPTION_MOVING_NIFTY_FLAT",
    "OPTION_FLAT_NIFTY_MOVING",
    "BOTH_FLAT",
}


def classify_market_context(movement_relationship):
    """
    Classify market context from the established
    V12.5 movement relationship.
    """

    if movement_relationship not in VALID_CONTEXTS:
        return "INVALID"

    return movement_relationship


def evaluate_market_context_classification(
    context_evidence,
):
    """
    Classify the market context from V12.7 Stage 1
    market-context evidence.
    """

    if not isinstance(context_evidence, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Context evidence must be a dictionary.",
        }

    if context_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Context evidence must have "
                "Status EVALUATED."
            ),
        }

    required_fields = [
        "Movement Relationship",
        "Option Direction",
        "NIFTY Movement Evidence",
    ]

    for field in required_fields:
        if field not in context_evidence:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing required field: {field}.",
            }

    relationship = context_evidence[
        "Movement Relationship"
    ]

    context = classify_market_context(
        relationship
    )

    if context == "INVALID":
        return {
            "Status": "REJECTED",
            "Reason": "Invalid movement relationship.",
        }

    return {
        "Status": "CLASSIFIED",
        "Trading Symbol": context_evidence.get(
            "Trading Symbol"
        ),
        "Underlying": context_evidence.get(
            "Underlying"
        ),
        "Expiry": context_evidence.get(
            "Expiry"
        ),
        "Strike": context_evidence.get(
            "Strike"
        ),
        "Option Type": context_evidence.get(
            "Option Type"
        ),
        "Option Direction": context_evidence[
            "Option Direction"
        ],
        "NIFTY Movement Evidence": context_evidence[
            "NIFTY Movement Evidence"
        ],
        "Movement Relationship": relationship,
        "Market Context": context,
    }
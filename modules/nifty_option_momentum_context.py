"""
JKJ AI Trader
NIFTY Option Momentum Context — V12.7 Stage 3

Purpose:
Combine V12.6 Momentum Confirmation with V12.7
Market Context Classification.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


SUPPORTED_CONTEXTS = {
    "MOVING_TOGETHER",
    "OPTION_MOVING_NIFTY_FLAT",
}

CONFLICT_CONTEXTS = {
    "DIVERGING",
    "OPTION_FLAT_NIFTY_MOVING",
    "BOTH_FLAT",
}

VALID_MOMENTUM_STATES = {
    "CONFIRMED",
    "PARTIALLY_CONFIRMED",
    "NOT_CONFIRMED",
}


def classify_momentum_context(
    momentum_confirmation,
    market_context,
):
    """
    Classify the relationship between momentum confirmation
    and market context.
    """

    if momentum_confirmation not in VALID_MOMENTUM_STATES:
        return "INVALID"

    if market_context not in (
        SUPPORTED_CONTEXTS
        | CONFLICT_CONTEXTS
    ):
        return "INVALID"

    if momentum_confirmation == "CONFIRMED":

        if market_context in SUPPORTED_CONTEXTS:
            return "SUPPORTED"

        return "CONTEXT_CONFLICT"

    if momentum_confirmation == "PARTIALLY_CONFIRMED":

        return "MIXED_CONTEXT"

    return "MIXED_CONTEXT"


def evaluate_momentum_context(
    momentum_confirmation,
    market_context,
):
    """
    Combine V12.6 momentum confirmation and V12.7
    market context classification.
    """

    if not isinstance(momentum_confirmation, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Momentum confirmation must be a dictionary."
            ),
        }

    if not isinstance(market_context, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Market context must be a dictionary."
            ),
        }

    if momentum_confirmation.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Momentum confirmation must have "
                "Status EVALUATED."
            ),
        }

    if market_context.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Market context must have "
                "Status CLASSIFIED."
            ),
        }

    required_momentum_fields = [
        "Momentum Confirmation",
        "Option Direction",
    ]

    required_context_fields = [
        "Market Context",
        "Movement Relationship",
    ]

    for field in required_momentum_fields:
        if field not in momentum_confirmation:
            return {
                "Status": "REJECTED",
                "Reason": (
                    f"Missing momentum field: {field}."
                ),
            }

    for field in required_context_fields:
        if field not in market_context:
            return {
                "Status": "REJECTED",
                "Reason": (
                    f"Missing context field: {field}."
                ),
            }

    momentum_state = momentum_confirmation[
        "Momentum Confirmation"
    ]

    market_state = market_context[
        "Market Context"
    ]

    combined_state = classify_momentum_context(
        momentum_state,
        market_state,
    )

    if combined_state == "INVALID":
        return {
            "Status": "REJECTED",
            "Reason": "Invalid momentum or market context state.",
        }

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
        "Option Direction": momentum_confirmation[
            "Option Direction"
        ],
        "Momentum Confirmation": momentum_state,
        "Market Context": market_state,
        "Movement Relationship": market_context[
            "Movement Relationship"
        ],
        "Momentum Context": combined_state,
    }
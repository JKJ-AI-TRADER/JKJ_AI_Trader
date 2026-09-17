"""
JKJ AI Trader
V12.8 Stage 1 — Opportunity Evidence

Extracts opportunity-related evidence from V12.7 Momentum Context.

This module does not generate a trading signal.
"""

REQUIRED_FIELDS = {
    "Trading Symbol",
    "Underlying",
    "Expiry",
    "Strike",
    "Option Type",
    "Option Direction",
    "Momentum Confirmation",
    "Market Context",
    "Movement Relationship",
    "Momentum Context",
}


def evaluate_opportunity_evidence(momentum_context):
    """
    Extract opportunity evidence from V12.7 Momentum Context.
    """

    if not isinstance(momentum_context, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Momentum Context must be a dictionary",
        }

    if momentum_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum Context status must be EVALUATED",
        }

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if field not in momentum_context
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    return {
        "Status": "EVALUATED",

        "Trading Symbol": momentum_context["Trading Symbol"],
        "Underlying": momentum_context["Underlying"],
        "Expiry": momentum_context["Expiry"],
        "Strike": momentum_context["Strike"],
        "Option Type": momentum_context["Option Type"],

        "Option Direction": momentum_context["Option Direction"],
        "Momentum Confirmation": momentum_context["Momentum Confirmation"],
        "Market Context": momentum_context["Market Context"],
        "Movement Relationship": momentum_context["Movement Relationship"],
        "Momentum Context": momentum_context["Momentum Context"],

        "Price Movement Evidence": (
            momentum_context["Option Direction"]
            in {"UP", "DOWN"}
        ),

        "Volume Evidence": (
            momentum_context.get("Volume Evidence", False)
        ),

        "Open Interest Evidence": (
            momentum_context.get("OI Evidence", False)
        ),

        "NIFTY Movement Evidence": (
            momentum_context.get("NIFTY Movement Evidence")
        ),
    }
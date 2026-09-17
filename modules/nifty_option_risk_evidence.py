"""
JKJ AI Trader
V12.9 Stage 1 — Risk Evidence

Extracts risk-related evidence from V12.8 Opportunity Strength.

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
    "Opportunity Classification",
    "Opportunity Strength",
}


def evaluate_risk_evidence(opportunity_strength):
    """
    Extract risk-related evidence from V12.8 Opportunity Strength.
    """

    if not isinstance(opportunity_strength, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity Strength must be a dictionary",
        }

    if opportunity_strength.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity Strength status must be EVALUATED",
        }

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if field not in opportunity_strength
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    return {
        "Status": "EVALUATED",

        "Trading Symbol": opportunity_strength["Trading Symbol"],
        "Underlying": opportunity_strength["Underlying"],
        "Expiry": opportunity_strength["Expiry"],
        "Strike": opportunity_strength["Strike"],
        "Option Type": opportunity_strength["Option Type"],

        "Option Direction": opportunity_strength["Option Direction"],
        "Momentum Confirmation": opportunity_strength[
            "Momentum Confirmation"
        ],
        "Market Context": opportunity_strength["Market Context"],
        "Movement Relationship": opportunity_strength[
            "Movement Relationship"
        ],
        "Momentum Context": opportunity_strength["Momentum Context"],

        "Opportunity Classification": opportunity_strength[
            "Opportunity Classification"
        ],
        "Opportunity Strength": opportunity_strength[
            "Opportunity Strength"
        ],

        "Momentum Risk Evidence": (
            opportunity_strength["Momentum Confirmation"]
        ),

        "Market Context Risk Evidence": (
            opportunity_strength["Market Context"]
        ),

        "Opportunity Strength Risk Evidence": (
            opportunity_strength["Opportunity Strength"]
        ),
    }
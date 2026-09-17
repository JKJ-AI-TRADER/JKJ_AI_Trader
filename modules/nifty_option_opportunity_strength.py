"""
JKJ AI Trader
V12.8 Stage 3 — Opportunity Strength

Determines the strength of the opportunity context
from V12.8 Opportunity Classification.

This module does not generate a trading signal.
"""

VALID_CLASSIFICATIONS = {
    "SUPPORTED_OPPORTUNITY",
    "CONTEXT_CONFLICT",
    "MIXED_OPPORTUNITY",
    "NO_CLEAR_OPPORTUNITY",
}

VALID_CONFIRMATIONS = {
    "CONFIRMED",
    "PARTIALLY_CONFIRMED",
    "NOT_CONFIRMED",
}

VALID_STRENGTHS = {
    "STRONG",
    "DEVELOPING",
    "WEAK",
}


def classify_opportunity_strength(
    opportunity_classification,
    momentum_confirmation,
):
    """
    Classify opportunity strength using the
    V12.8 opportunity classification and
    V12.7 momentum confirmation.
    """

    if opportunity_classification not in VALID_CLASSIFICATIONS:
        return "INVALID"

    if momentum_confirmation not in VALID_CONFIRMATIONS:
        return "INVALID"

    if (
        opportunity_classification == "SUPPORTED_OPPORTUNITY"
        and momentum_confirmation == "CONFIRMED"
    ):
        return "STRONG"

    if (
        opportunity_classification == "SUPPORTED_OPPORTUNITY"
        and momentum_confirmation == "PARTIALLY_CONFIRMED"
    ):
        return "DEVELOPING"

    if (
        opportunity_classification == "CONTEXT_CONFLICT"
        and momentum_confirmation == "CONFIRMED"
    ):
        return "WEAK"

    if opportunity_classification == "NO_CLEAR_OPPORTUNITY":
        return "WEAK"

    if opportunity_classification == "MIXED_OPPORTUNITY":
        return "DEVELOPING"

    return "INVALID"


def evaluate_opportunity_strength(opportunity_classification):
    """
    Evaluate V12.8 Stage 2 Opportunity Classification
    and determine opportunity strength.
    """

    if not isinstance(opportunity_classification, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity Classification must be a dictionary",
        }

    if opportunity_classification.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity Classification status must be CLASSIFIED",
        }

    required_fields = {
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
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in opportunity_classification
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    classification = opportunity_classification[
        "Opportunity Classification"
    ]

    momentum_confirmation = opportunity_classification[
        "Momentum Confirmation"
    ]

    strength = classify_opportunity_strength(
        classification,
        momentum_confirmation,
    )

    if strength == "INVALID":
        return {
            "Status": "REJECTED",
            "Reason": "Invalid opportunity classification or confirmation",
        }

    return {
        "Status": "EVALUATED",

        "Trading Symbol": opportunity_classification["Trading Symbol"],
        "Underlying": opportunity_classification["Underlying"],
        "Expiry": opportunity_classification["Expiry"],
        "Strike": opportunity_classification["Strike"],
        "Option Type": opportunity_classification["Option Type"],

        "Option Direction": opportunity_classification["Option Direction"],
        "Momentum Confirmation": momentum_confirmation,
        "Market Context": opportunity_classification["Market Context"],
        "Movement Relationship": opportunity_classification[
            "Movement Relationship"
        ],
        "Momentum Context": opportunity_classification[
            "Momentum Context"
        ],

        "Opportunity Classification": classification,
        "Opportunity Strength": strength,
    }
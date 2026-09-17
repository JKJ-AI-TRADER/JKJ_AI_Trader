"""
JKJ AI Trader
V12.9 Stage 3 — Trade Quality

Classifies the quality of the opportunity/risk context.

This module does not generate a trading signal.
"""

VALID_MOMENTUM_CONTEXTS = {
    "SUPPORTED",
    "CONTEXT_CONFLICT",
    "MIXED_CONTEXT",
}

VALID_CONFIRMATIONS = {
    "CONFIRMED",
    "PARTIALLY_CONFIRMED",
    "NOT_CONFIRMED",
}

VALID_OPPORTUNITY_STRENGTHS = {
    "STRONG",
    "DEVELOPING",
    "WEAK",
}

VALID_RISK_CLASSIFICATIONS = {
    "LOWER_RISK_CONTEXT",
    "MODERATE_RISK_CONTEXT",
    "HIGHER_RISK_CONTEXT",
}

VALID_QUALITY_CLASSIFICATIONS = {
    "HIGH_QUALITY_CONTEXT",
    "DEVELOPING_QUALITY_CONTEXT",
    "LOW_QUALITY_CONTEXT",
    "UNDEFINED_QUALITY",
}


def classify_trade_quality(
    momentum_context,
    momentum_confirmation,
    opportunity_strength,
    opportunity_classification,
    risk_classification,
):
    """
    Classify trade quality from V12.9 evidence.
    """

    if momentum_context not in VALID_MOMENTUM_CONTEXTS:
        return "UNDEFINED_QUALITY"

    if momentum_confirmation not in VALID_CONFIRMATIONS:
        return "UNDEFINED_QUALITY"

    if opportunity_strength not in VALID_OPPORTUNITY_STRENGTHS:
        return "UNDEFINED_QUALITY"

    if risk_classification not in VALID_RISK_CLASSIFICATIONS:
        return "UNDEFINED_QUALITY"

    if (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "CONFIRMED"
        and opportunity_strength == "STRONG"
        and opportunity_classification == "SUPPORTED_OPPORTUNITY"
        and risk_classification == "LOWER_RISK_CONTEXT"
    ):
        return "HIGH_QUALITY_CONTEXT"

    if (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "PARTIALLY_CONFIRMED"
        and opportunity_strength == "DEVELOPING"
        and opportunity_classification == "SUPPORTED_OPPORTUNITY"
        and risk_classification == "MODERATE_RISK_CONTEXT"
    ):
        return "DEVELOPING_QUALITY_CONTEXT"

    if opportunity_classification == "MIXED_OPPORTUNITY":
        return "DEVELOPING_QUALITY_CONTEXT"

    if (
        risk_classification == "HIGHER_RISK_CONTEXT"
        or opportunity_classification == "CONTEXT_CONFLICT"
        or opportunity_classification == "NO_CLEAR_OPPORTUNITY"
    ):
        return "LOW_QUALITY_CONTEXT"

    return "UNDEFINED_QUALITY"


def evaluate_trade_quality(risk_classification):
    """
    Evaluate V12.9 Stage 2 Risk Classification
    and classify Trade Quality.
    """

    if not isinstance(risk_classification, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Risk Classification must be a dictionary",
        }

    if risk_classification.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Risk Classification status must be CLASSIFIED",
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
        "Opportunity Strength",
        "Risk Classification",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in risk_classification
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    quality = classify_trade_quality(
        risk_classification["Momentum Context"],
        risk_classification["Momentum Confirmation"],
        risk_classification["Opportunity Strength"],
        risk_classification["Opportunity Classification"],
        risk_classification["Risk Classification"],
    )

    return {
        "Status": "CLASSIFIED",

        "Trading Symbol": risk_classification["Trading Symbol"],
        "Underlying": risk_classification["Underlying"],
        "Expiry": risk_classification["Expiry"],
        "Strike": risk_classification["Strike"],
        "Option Type": risk_classification["Option Type"],

        "Option Direction": risk_classification["Option Direction"],
        "Momentum Confirmation": risk_classification[
            "Momentum Confirmation"
        ],
        "Market Context": risk_classification["Market Context"],
        "Movement Relationship": risk_classification[
            "Movement Relationship"
        ],
        "Momentum Context": risk_classification["Momentum Context"],

        "Opportunity Classification": risk_classification[
            "Opportunity Classification"
        ],
        "Opportunity Strength": risk_classification[
            "Opportunity Strength"
        ],

        "Risk Classification": risk_classification[
            "Risk Classification"
        ],

        "Trade Quality": quality,
    }
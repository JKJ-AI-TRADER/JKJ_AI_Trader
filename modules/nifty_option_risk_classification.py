"""
JKJ AI Trader
V12.9 Stage 2 — Risk Classification

Classifies the risk context from V12.9 Risk Evidence.

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

VALID_CLASSIFICATIONS = {
    "LOWER_RISK_CONTEXT",
    "MODERATE_RISK_CONTEXT",
    "HIGHER_RISK_CONTEXT",
    "UNDEFINED_RISK",
}


def classify_risk_context(
    momentum_context,
    momentum_confirmation,
    opportunity_strength,
    opportunity_classification,
):
    """
    Classify risk context from V12.9 evidence.
    """

    if momentum_context not in VALID_MOMENTUM_CONTEXTS:
        return "UNDEFINED_RISK"

    if momentum_confirmation not in VALID_CONFIRMATIONS:
        return "UNDEFINED_RISK"

    if opportunity_strength not in VALID_OPPORTUNITY_STRENGTHS:
        return "UNDEFINED_RISK"

    if (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "CONFIRMED"
        and opportunity_strength == "STRONG"
        and opportunity_classification == "SUPPORTED_OPPORTUNITY"
    ):
        return "LOWER_RISK_CONTEXT"

    if (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "PARTIALLY_CONFIRMED"
        and opportunity_strength == "DEVELOPING"
        and opportunity_classification == "SUPPORTED_OPPORTUNITY"
    ):
        return "MODERATE_RISK_CONTEXT"

    if (
        momentum_context == "CONTEXT_CONFLICT"
        or opportunity_classification == "CONTEXT_CONFLICT"
    ):
        return "HIGHER_RISK_CONTEXT"

    if opportunity_classification == "MIXED_OPPORTUNITY":
        return "MODERATE_RISK_CONTEXT"

    if opportunity_classification == "NO_CLEAR_OPPORTUNITY":
        return "HIGHER_RISK_CONTEXT"

    return "UNDEFINED_RISK"


def evaluate_risk_classification(risk_evidence):
    """
    Evaluate V12.9 Stage 1 Risk Evidence
    and classify the risk context.
    """

    if not isinstance(risk_evidence, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Risk Evidence must be a dictionary",
        }

    if risk_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Risk Evidence status must be EVALUATED",
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
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in risk_evidence
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    classification = classify_risk_context(
        risk_evidence["Momentum Context"],
        risk_evidence["Momentum Confirmation"],
        risk_evidence["Opportunity Strength"],
        risk_evidence["Opportunity Classification"],
    )

    return {
        "Status": "CLASSIFIED",

        "Trading Symbol": risk_evidence["Trading Symbol"],
        "Underlying": risk_evidence["Underlying"],
        "Expiry": risk_evidence["Expiry"],
        "Strike": risk_evidence["Strike"],
        "Option Type": risk_evidence["Option Type"],

        "Option Direction": risk_evidence["Option Direction"],
        "Momentum Confirmation": risk_evidence[
            "Momentum Confirmation"
        ],
        "Market Context": risk_evidence["Market Context"],
        "Movement Relationship": risk_evidence[
            "Movement Relationship"
        ],
        "Momentum Context": risk_evidence["Momentum Context"],

        "Opportunity Classification": risk_evidence[
            "Opportunity Classification"
        ],
        "Opportunity Strength": risk_evidence[
            "Opportunity Strength"
        ],

        "Risk Classification": classification,
    }
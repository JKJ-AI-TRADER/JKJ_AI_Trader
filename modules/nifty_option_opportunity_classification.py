"""
JKJ AI Trader
V12.8 Stage 2 — Opportunity Classification

Classifies the opportunity context from V12.8 Stage 1 evidence.

This module does not generate a trading signal.
"""

VALID_MOMENTUM_CONTEXTS = {
    "SUPPORTED",
    "CONTEXT_CONFLICT",
    "MIXED_CONTEXT",
}

VALID_MOMENTUM_CONFIRMATIONS = {
    "CONFIRMED",
    "PARTIALLY_CONFIRMED",
    "NOT_CONFIRMED",
}

CLASSIFICATIONS = {
    "SUPPORTED_OPPORTUNITY",
    "CONTEXT_CONFLICT",
    "MIXED_OPPORTUNITY",
    "NO_CLEAR_OPPORTUNITY",
}


def classify_opportunity(momentum_context, momentum_confirmation):
    """
    Classify opportunity context using V12.7 Momentum Context
    and Momentum Confirmation.
    """

    if momentum_context not in VALID_MOMENTUM_CONTEXTS:
        return "INVALID"

    if momentum_confirmation not in VALID_MOMENTUM_CONFIRMATIONS:
        return "INVALID"

    if (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "CONFIRMED"
    ):
        return "SUPPORTED_OPPORTUNITY"

    if (
        momentum_context == "CONTEXT_CONFLICT"
        and momentum_confirmation == "CONFIRMED"
    ):
        return "CONTEXT_CONFLICT"

    if momentum_context == "MIXED_CONTEXT":
        return "MIXED_OPPORTUNITY"

    if momentum_confirmation == "NOT_CONFIRMED":
        return "NO_CLEAR_OPPORTUNITY"

    return "MIXED_OPPORTUNITY"


def evaluate_opportunity_classification(opportunity_evidence):
    """
    Evaluate V12.8 Stage 1 Opportunity Evidence
    and classify the opportunity context.
    """

    if not isinstance(opportunity_evidence, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity Evidence must be a dictionary",
        }

    if opportunity_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity Evidence status must be EVALUATED",
        }

    required_fields = {
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Momentum Confirmation",
        "Momentum Context",
        "Market Context",
        "Movement Relationship",
        "Option Direction",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in opportunity_evidence
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    momentum_context = opportunity_evidence["Momentum Context"]
    momentum_confirmation = opportunity_evidence["Momentum Confirmation"]

    classification = classify_opportunity(
        momentum_context,
        momentum_confirmation,
    )

    if classification == "INVALID":
        return {
            "Status": "REJECTED",
            "Reason": "Invalid momentum context or confirmation",
        }

    return {
        "Status": "CLASSIFIED",

        "Trading Symbol": opportunity_evidence["Trading Symbol"],
        "Underlying": opportunity_evidence["Underlying"],
        "Expiry": opportunity_evidence["Expiry"],
        "Strike": opportunity_evidence["Strike"],
        "Option Type": opportunity_evidence["Option Type"],

        "Option Direction": opportunity_evidence["Option Direction"],
        "Momentum Confirmation": momentum_confirmation,
        "Market Context": opportunity_evidence["Market Context"],
        "Movement Relationship": opportunity_evidence["Movement Relationship"],
        "Momentum Context": momentum_context,

        "Opportunity Classification": classification,
    }
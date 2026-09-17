"""
JKJ AI Trader
V13.2 — Entry Qualification

Determines whether the V13.1 Decision Context
qualifies for entry, is developing, or is not qualified.

This module does not place orders.
It does not calculate entry price, stop-loss,
target, or position size.
"""


def evaluate_entry_qualification(decision_context):
    """
    Evaluate V13.1 Decision Context for entry qualification.
    """

    if not isinstance(decision_context, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Decision Context must be a dictionary",
        }

    if decision_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Decision Context status must be EVALUATED",
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
        "Trade Quality",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in decision_context
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    momentum_context = decision_context["Momentum Context"]
    momentum_confirmation = decision_context["Momentum Confirmation"]
    opportunity_classification = decision_context[
        "Opportunity Classification"
    ]
    opportunity_strength = decision_context["Opportunity Strength"]
    risk_classification = decision_context["Risk Classification"]
    trade_quality = decision_context["Trade Quality"]

    # Fully qualified entry context
    if (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "CONFIRMED"
        and opportunity_classification == "SUPPORTED_OPPORTUNITY"
        and opportunity_strength == "STRONG"
        and risk_classification == "LOWER_RISK_CONTEXT"
        and trade_quality == "HIGH_QUALITY_CONTEXT"
    ):
        qualification = "ENTRY_QUALIFIED"

    # Developing context — watch/wait, not a trade
    elif (
        momentum_context == "SUPPORTED"
        and momentum_confirmation == "PARTIALLY_CONFIRMED"
        and opportunity_classification == "SUPPORTED_OPPORTUNITY"
        and opportunity_strength == "DEVELOPING"
        and risk_classification == "MODERATE_RISK_CONTEXT"
        and trade_quality == "DEVELOPING_QUALITY_CONTEXT"
    ):
        qualification = "ENTRY_DEVELOPING"

    # All other valid contexts are not qualified
    else:
        qualification = "ENTRY_NOT_QUALIFIED"

    return {
        "Status": "QUALIFIED",
        "Trading Symbol": decision_context["Trading Symbol"],
        "Underlying": decision_context["Underlying"],
        "Expiry": decision_context["Expiry"],
        "Strike": decision_context["Strike"],
        "Option Type": decision_context["Option Type"],
        "Option Direction": decision_context["Option Direction"],
        "Momentum Confirmation": momentum_confirmation,
        "Market Context": decision_context["Market Context"],
        "Movement Relationship": decision_context[
            "Movement Relationship"
        ],
        "Momentum Context": momentum_context,
        "Opportunity Classification": opportunity_classification,
        "Opportunity Strength": opportunity_strength,
        "Risk Classification": risk_classification,
        "Trade Quality": trade_quality,
        "Entry Qualification": qualification,
    }

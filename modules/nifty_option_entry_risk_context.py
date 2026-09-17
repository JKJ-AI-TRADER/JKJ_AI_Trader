"""
JKJ AI Trader
V14.1 — Entry Risk Context

Classifies the risk context surrounding a V13
entry qualification.

This module does not calculate stop-loss,
targets, position size, or place orders.
"""


def evaluate_entry_risk_context(entry_qualification):
    """
    Evaluate V13 Entry Qualification for risk context.
    """

    if not isinstance(entry_qualification, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Entry Qualification must be a dictionary",
        }

    if entry_qualification.get("Status") != "QUALIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Entry Qualification status must be QUALIFIED",
        }

    required_fields = {
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Option Direction",
        "Entry Qualification",
        "Risk Classification",
        "Trade Quality",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in entry_qualification
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    entry_status = entry_qualification["Entry Qualification"]
    risk_classification = entry_qualification["Risk Classification"]
    trade_quality = entry_qualification["Trade Quality"]

    # Controlled risk
    if (
        entry_status == "ENTRY_QUALIFIED"
        and risk_classification == "LOWER_RISK_CONTEXT"
        and trade_quality == "HIGH_QUALITY_CONTEXT"
    ):
        risk_context = "CONTROLLED_RISK_CONTEXT"

    # Developing risk
    elif (
        entry_status == "ENTRY_DEVELOPING"
        and risk_classification == "MODERATE_RISK_CONTEXT"
        and trade_quality == "DEVELOPING_QUALITY_CONTEXT"
    ):
        risk_context = "DEVELOPING_RISK_CONTEXT"

    # Elevated risk
    elif (
        entry_status == "ENTRY_NOT_QUALIFIED"
        or risk_classification == "HIGHER_RISK_CONTEXT"
        or trade_quality == "LOW_QUALITY_CONTEXT"
    ):
        risk_context = "ELEVATED_RISK_CONTEXT"

    else:
        risk_context = "UNDEFINED_RISK_CONTEXT"

    return {
        "Status": "EVALUATED",

        "Trading Symbol": entry_qualification["Trading Symbol"],
        "Underlying": entry_qualification["Underlying"],
        "Expiry": entry_qualification["Expiry"],
        "Strike": entry_qualification["Strike"],
        "Option Type": entry_qualification["Option Type"],

        "Option Direction": entry_qualification["Option Direction"],
        "Entry Qualification": entry_status,
        "Risk Classification": risk_classification,
        "Trade Quality": trade_quality,

        "Entry Risk Context": risk_context,
    }
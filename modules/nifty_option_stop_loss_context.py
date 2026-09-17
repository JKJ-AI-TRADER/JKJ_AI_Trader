"""
JKJ AI Trader
V14.2 — Stop-Loss Context

Determines whether the current entry risk context
supports proceeding toward stop-loss establishment.

This module does not calculate a stop-loss price.
It does not calculate targets, position size,
or place orders.
"""


def evaluate_stop_loss_context(entry_risk_context):
    """
    Evaluate V14.1 Entry Risk Context for stop-loss support.
    """

    if not isinstance(entry_risk_context, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Entry Risk Context must be a dictionary",
        }

    if entry_risk_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Entry Risk Context status must be EVALUATED",
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
        "Entry Risk Context",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in entry_risk_context
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    risk_context = entry_risk_context["Entry Risk Context"]

    if risk_context == "CONTROLLED_RISK_CONTEXT":
        stop_loss_context = "STOP_SUPPORTED"

    elif risk_context == "DEVELOPING_RISK_CONTEXT":
        stop_loss_context = "STOP_DEVELOPING"

    elif risk_context == "ELEVATED_RISK_CONTEXT":
        stop_loss_context = "STOP_NOT_SUPPORTED"

    elif risk_context == "UNDEFINED_RISK_CONTEXT":
        stop_loss_context = "STOP_UNDEFINED"

    else:
        stop_loss_context = "STOP_UNDEFINED"

    return {
        "Status": "EVALUATED",

        "Trading Symbol": entry_risk_context["Trading Symbol"],
        "Underlying": entry_risk_context["Underlying"],
        "Expiry": entry_risk_context["Expiry"],
        "Strike": entry_risk_context["Strike"],
        "Option Type": entry_risk_context["Option Type"],

        "Option Direction": entry_risk_context["Option Direction"],
        "Entry Qualification": entry_risk_context[
            "Entry Qualification"
        ],
        "Risk Classification": entry_risk_context[
            "Risk Classification"
        ],
        "Trade Quality": entry_risk_context["Trade Quality"],
        "Entry Risk Context": risk_context,

        "Stop-Loss Context": stop_loss_context,
    }
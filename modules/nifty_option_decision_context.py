"""
JKJ AI Trader
V13.1 — Decision Context

Builds a structured decision context from V12.9
Risk & Trade Quality output.

This module does not generate a trading signal.
"""


def evaluate_decision_context(trade_quality):
    """
    Build V13.1 Decision Context from V12.9 Trade Quality.
    """

    if not isinstance(trade_quality, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Trade Quality must be a dictionary",
        }

    if trade_quality.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Trade Quality status must be CLASSIFIED",
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
        if field not in trade_quality
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    return {
        "Status": "EVALUATED",

        "Trading Symbol": trade_quality["Trading Symbol"],
        "Underlying": trade_quality["Underlying"],
        "Expiry": trade_quality["Expiry"],
        "Strike": trade_quality["Strike"],
        "Option Type": trade_quality["Option Type"],

        "Option Direction": trade_quality["Option Direction"],
        "Momentum Confirmation": trade_quality[
            "Momentum Confirmation"
        ],
        "Market Context": trade_quality["Market Context"],
        "Movement Relationship": trade_quality[
            "Movement Relationship"
        ],
        "Momentum Context": trade_quality["Momentum Context"],

        "Opportunity Classification": trade_quality[
            "Opportunity Classification"
        ],
        "Opportunity Strength": trade_quality[
            "Opportunity Strength"
        ],

        "Risk Classification": trade_quality[
            "Risk Classification"
        ],
        "Trade Quality": trade_quality[
            "Trade Quality"
        ],
    }
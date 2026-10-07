"""
JKJ AI Trader
V21.2.13 — Real-Market Decision + Entry Qualification

Bridges V21.2.12 real-market Opportunity/Risk/Trade Quality
output into the existing V13.1 Decision Context and
V13.2 Entry Qualification modules.

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.nifty_option_decision_context import (
    evaluate_decision_context,
)

from modules.nifty_option_entry_qualification import (
    evaluate_entry_qualification,
)


def evaluate_real_market_decision_entry(opportunity_risk_result):
    """
    Evaluate V21.2.12 real-market output through V13.1
    Decision Context and V13.2 Entry Qualification.
    """

    if not isinstance(opportunity_risk_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity/Risk result must be a dictionary",
            "Live Order": False,
            "Paper Trade": False,
        }

    if opportunity_risk_result.get("Status") != (
        "OPPORTUNITY_RISK_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Opportunity/Risk result status must be "
                "OPPORTUNITY_RISK_COMPLETE"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # V21.2.12 → V13.1
    # ---------------------------------------------------------
    #
    # V13.1 expects the V12.9 Trade Quality structure.
    #
    trade_quality = {
        "Status": "CLASSIFIED",

        "Trading Symbol": opportunity_risk_result.get(
            "Trading Symbol"
        ),
        "Underlying": opportunity_risk_result.get(
            "Underlying"
        ),
        "Expiry": opportunity_risk_result.get(
            "Expiry"
        ),
        "Strike": opportunity_risk_result.get(
            "Strike"
        ),
        "Option Type": opportunity_risk_result.get(
            "Option Type"
        ),

        "Option Direction": opportunity_risk_result.get(
            "Option Direction"
        ),
        "Momentum Confirmation": opportunity_risk_result.get(
            "Momentum Confirmation"
        ),
        "Market Context": opportunity_risk_result.get(
            "Market Context"
        ),
        "Movement Relationship": opportunity_risk_result.get(
            "Movement Relationship"
        ),
        "Momentum Context": opportunity_risk_result.get(
            "Momentum Context"
        ),

        "Opportunity Classification": opportunity_risk_result.get(
            "Opportunity Classification"
        ),
        "Opportunity Strength": opportunity_risk_result.get(
            "Opportunity Strength"
        ),

        "Risk Classification": opportunity_risk_result.get(
            "Risk Classification"
        ),
        "Trade Quality": opportunity_risk_result.get(
            "Trade Quality"
        ),
    }

    # ---------------------------------------------------------
    # V13.1 Decision Context
    # ---------------------------------------------------------
    decision_context = evaluate_decision_context(
        trade_quality
    )

    if decision_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "V13.1 Decision Context rejected "
                "the V21.2.12 result"
            ),
            "Decision Context": decision_context,
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # V13.2 Entry Qualification
    # ---------------------------------------------------------
    entry_qualification = evaluate_entry_qualification(
        decision_context
    )

    if entry_qualification.get("Status") != "QUALIFIED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "V13.2 Entry Qualification rejected "
                "the Decision Context"
            ),
            "Decision Context": decision_context,
            "Entry Qualification": entry_qualification,
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # Final V21.2.13 result
    # ---------------------------------------------------------
    return {
        "Status": "DECISION_ENTRY_COMPLETE",

        "Trading Symbol": entry_qualification[
            "Trading Symbol"
        ],
        "Underlying": entry_qualification[
            "Underlying"
        ],
        "Expiry": entry_qualification[
            "Expiry"
        ],
        "Strike": entry_qualification[
            "Strike"
        ],
        "Option Type": entry_qualification[
            "Option Type"
        ],

        "Option Direction": entry_qualification[
            "Option Direction"
        ],
        "Momentum Confirmation": entry_qualification[
            "Momentum Confirmation"
        ],
        "Market Context": entry_qualification[
            "Market Context"
        ],
        "Movement Relationship": entry_qualification[
            "Movement Relationship"
        ],
        "Momentum Context": entry_qualification[
            "Momentum Context"
        ],

        "Opportunity Classification": entry_qualification[
            "Opportunity Classification"
        ],
        "Opportunity Strength": entry_qualification[
            "Opportunity Strength"
        ],

        "Risk Classification": entry_qualification[
            "Risk Classification"
        ],
        "Trade Quality": entry_qualification[
            "Trade Quality"
        ],

        "Entry Qualification": entry_qualification[
            "Entry Qualification"
        ],

        "Decision Context": decision_context,
        "Entry Qualification Result": entry_qualification,

        "Live Order": False,
        "Paper Trade": False,
    }
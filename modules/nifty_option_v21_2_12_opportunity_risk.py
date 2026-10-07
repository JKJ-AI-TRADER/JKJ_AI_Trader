"""
JKJ AI Trader
V21.2.12 — Real-Market Opportunity + Risk/Trade Quality Bridge

Purpose:
Connect the completed V21.2.11 real-market Market Context
result into the existing frozen V12.8 and V12.9 pipeline.

Pipeline:
V21.2.11 Market Context
    ->
V12.8 Opportunity Evidence
    ->
V12.8 Opportunity Classification
    ->
V12.8 Opportunity Strength
    ->
V12.9 Risk Evidence
    ->
V12.9 Risk Classification
    ->
V12.9 Trade Quality

Safety:
- No live orders
- No paper trades
- No BUY/SELL/EXIT decision
- No modification of frozen JKJ modules
"""

from modules.nifty_option_opportunity_evidence import (
    evaluate_opportunity_evidence,
)

from modules.nifty_option_opportunity_classification import (
    evaluate_opportunity_classification,
)

from modules.nifty_option_opportunity_strength import (
    evaluate_opportunity_strength,
)

from modules.nifty_option_risk_evidence import (
    evaluate_risk_evidence,
)

from modules.nifty_option_risk_classification import (
    evaluate_risk_classification,
)

from modules.nifty_option_trade_quality import (
    evaluate_trade_quality,
)


def evaluate_real_market_opportunity_risk(
    market_context_result,
):
    """
    Connect V21.2.11 Market Context into the
    existing V12.8 and V12.9 decision-support pipeline.
    """

    # --------------------------------------------------
    # Step 1 — V12.8 Stage 1
    # Opportunity Evidence
    # --------------------------------------------------

    momentum_context = (
        market_context_result.get(
            "Momentum Context Result"
        )
    )

    if not isinstance(momentum_context, dict):
        return {
            "Status": "REJECTED",
            "Stage": "V12.8_STAGE_1",
            "Reason": (
                "V21.2.11 Momentum Context Result "
                "is unavailable."
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    opportunity_evidence = (
        evaluate_opportunity_evidence(
            momentum_context
        )
    )

    if opportunity_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.8_STAGE_1",
            "Reason": (
                "V12.8 opportunity evidence "
                "evaluation failed."
            ),
            "Opportunity Evidence": opportunity_evidence,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 2 — V12.8 Stage 2
    # Opportunity Classification
    # --------------------------------------------------

    opportunity_classification = (
        evaluate_opportunity_classification(
            opportunity_evidence
        )
    )

    if opportunity_classification.get(
        "Status"
    ) != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.8_STAGE_2",
            "Reason": (
                "V12.8 opportunity classification "
                "failed."
            ),
            "Opportunity Evidence": opportunity_evidence,
            "Opportunity Classification":
                opportunity_classification,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 3 — V12.8 Stage 3
    # Opportunity Strength
    # --------------------------------------------------

    opportunity_strength = (
        evaluate_opportunity_strength(
            opportunity_classification
        )
    )

    if opportunity_strength.get(
        "Status"
    ) != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.8_STAGE_3",
            "Reason": (
                "V12.8 opportunity strength "
                "evaluation failed."
            ),
            "Opportunity Classification":
                opportunity_classification,
            "Opportunity Strength":
                opportunity_strength,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 4 — V12.9 Stage 1
    # Risk Evidence
    # --------------------------------------------------

    risk_evidence = evaluate_risk_evidence(
        opportunity_strength
    )

    if risk_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.9_STAGE_1",
            "Reason": (
                "V12.9 risk evidence "
                "evaluation failed."
            ),
            "Opportunity Strength":
                opportunity_strength,
            "Risk Evidence": risk_evidence,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 5 — V12.9 Stage 2
    # Risk Classification
    # --------------------------------------------------

    risk_classification = (
        evaluate_risk_classification(
            risk_evidence
        )
    )

    if risk_classification.get(
        "Status"
    ) != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.9_STAGE_2",
            "Reason": (
                "V12.9 risk classification "
                "failed."
            ),
            "Risk Evidence": risk_evidence,
            "Risk Classification":
                risk_classification,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 6 — V12.9 Stage 3
    # Trade Quality
    # --------------------------------------------------

    trade_quality = evaluate_trade_quality(
        risk_classification
    )

    if trade_quality.get(
        "Status"
    ) != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.9_STAGE_3",
            "Reason": (
                "V12.9 trade quality "
                "evaluation failed."
            ),
            "Risk Classification":
                risk_classification,
            "Trade Quality": trade_quality,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Final V21.2.12 result
    # --------------------------------------------------

    return {
        "Status": "OPPORTUNITY_RISK_COMPLETE",

        "Trading Symbol": trade_quality.get(
            "Trading Symbol"
        ),
        "Underlying": trade_quality.get(
            "Underlying"
        ),
        "Expiry": trade_quality.get(
            "Expiry"
        ),
        "Strike": trade_quality.get(
            "Strike"
        ),
        "Option Type": trade_quality.get(
            "Option Type"
        ),

        "Option Direction": trade_quality.get(
            "Option Direction"
        ),

        "Momentum Confirmation": trade_quality.get(
            "Momentum Confirmation"
        ),

        "Market Context": trade_quality.get(
            "Market Context"
        ),

        "Movement Relationship": trade_quality.get(
            "Movement Relationship"
        ),

        "Momentum Context": trade_quality.get(
            "Momentum Context"
        ),

        "Opportunity Classification":
            trade_quality.get(
                "Opportunity Classification"
            ),

        "Opportunity Strength":
            trade_quality.get(
                "Opportunity Strength"
            ),

        "Risk Classification":
            trade_quality.get(
                "Risk Classification"
            ),

        "Trade Quality": trade_quality.get(
            "Trade Quality"
        ),

        "Opportunity Evidence":
            opportunity_evidence,

        "Opportunity Classification Result":
            opportunity_classification,

        "Opportunity Strength Result":
            opportunity_strength,

        "Risk Evidence":
            risk_evidence,

        "Risk Classification Result":
            risk_classification,

        "Trade Quality Result":
            trade_quality,

        "Live Order": False,
        "Paper Trade": False,
    }

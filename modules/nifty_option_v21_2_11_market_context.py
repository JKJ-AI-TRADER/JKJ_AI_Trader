"""
JKJ AI Trader
NIFTY Option V21.2.11 — Real-Market Market Context Bridge

Purpose:
Connect the completed V21.2.10 real-market momentum
confirmation result into the existing frozen V12.7
Market Context pipeline.

Pipeline:
V21.2.10 Momentum Confirmation
    ->
V12.7 Stage 1 Market Context Evidence
    ->
V12.7 Stage 2 Market Context Classification
    ->
V12.7 Stage 3 Momentum Context

Safety:
- No live orders
- No paper trades
- No changes to frozen V12.6/V12.7 modules
- No BUY/SELL/EXIT decision
"""

from modules.nifty_option_market_context_evidence import (
    evaluate_market_context_evidence,
)

from modules.nifty_option_market_context_classification import (
    evaluate_market_context_classification,
)

from modules.nifty_option_momentum_context import (
    evaluate_momentum_context,
)


def evaluate_real_market_market_context(
    momentum_confirmation,
):
    """
    Connect the completed V21.2.10 / V12.6 momentum
    confirmation into the existing V12.7 pipeline.
    """

    # --------------------------------------------------
    # Step 1 — V12.7 Stage 1
    # Market Context Evidence
    # --------------------------------------------------

    context_evidence = evaluate_market_context_evidence(
        momentum_confirmation
    )

    if context_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.7_STAGE_1",
            "Reason": (
                "V12.7 market context evidence "
                "evaluation failed."
            ),
            "Context Evidence": context_evidence,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 2 — V12.7 Stage 2
    # Market Context Classification
    # --------------------------------------------------

    market_context = evaluate_market_context_classification(
        context_evidence
    )

    if market_context.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.7_STAGE_2",
            "Reason": (
                "V12.7 market context classification "
                "failed."
            ),
            "Context Evidence": context_evidence,
            "Market Context": market_context,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # Step 3 — V12.7 Stage 3
    # Momentum Context
    # --------------------------------------------------

    momentum_context = evaluate_momentum_context(
        momentum_confirmation,
        market_context,
    )

    if momentum_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Stage": "V12.7_STAGE_3",
            "Reason": (
                "V12.7 momentum context "
                "evaluation failed."
            ),
            "Context Evidence": context_evidence,
            "Market Context": market_context,
            "Momentum Context": momentum_context,
            "Live Order": False,
            "Paper Trade": False,
        }

    return {
        "Status": "MARKET_CONTEXT_COMPLETE",

        "Trading Symbol": momentum_context.get(
            "Trading Symbol"
        ),
        "Underlying": momentum_context.get(
            "Underlying"
        ),
        "Expiry": momentum_context.get(
            "Expiry"
        ),
        "Strike": momentum_context.get(
            "Strike"
        ),
        "Option Type": momentum_context.get(
            "Option Type"
        ),

        "Option Direction": momentum_context.get(
            "Option Direction"
        ),

        "Momentum Confirmation": momentum_context.get(
            "Momentum Confirmation"
        ),

        "Market Context": momentum_context.get(
            "Market Context"
        ),

        "Movement Relationship": momentum_context.get(
            "Movement Relationship"
        ),

        "Momentum Context": momentum_context.get(
            "Momentum Context"
        ),

        "Context Evidence": context_evidence,
        "Market Context Classification": market_context,
        "Momentum Context Result": momentum_context,

        "Live Order": False,
        "Paper Trade": False,
    }

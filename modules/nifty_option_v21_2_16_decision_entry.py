"""
JKJ AI Trader
NIFTY Option V21.2.16 — Unified Decision & Entry Bridge

Purpose:
Connect one completed V21.2.15 unified observation session
through the frozen V12.6, V12.7, V12.8, V12.9 and V13
decision pipeline.

Pipeline:

V21.2.15 Unified Observation
    ->
V12.6 Momentum
    ->
V12.7 Market Context
    ->
V12.8 Opportunity
    ->
V12.9 Risk / Trade Quality
    ->
V13.1 Decision Context
    ->
V13.2 Entry Qualification

Safety:
- No new market observations
- No live orders
- No paper trades
- No changes to frozen V12.6/V12.7/V12.8/V12.9/V13 modules
- No BUY/SELL/EXIT decision
"""

from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)

from modules.nifty_option_market_context_evidence import (
    evaluate_market_context_evidence,
)

from modules.nifty_option_market_context_classification import (
    evaluate_market_context_classification,
)

from modules.nifty_option_momentum_context import (
    evaluate_momentum_context,
)

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

from modules.nifty_option_decision_context import (
    evaluate_decision_context,
)

from modules.nifty_option_entry_qualification import (
    evaluate_entry_qualification,
)


def _reject(stage, reason, **data):
    """Return a consistent safe rejection result."""

    result = {
        "Status": "REJECTED",
        "Stage": stage,
        "Reason": reason,
        "Live Order": False,
        "Paper Trade": False,
    }

    result.update(data)
    return result


def evaluate_unified_decision_entry(
    unified_observation_result,
):
    """
    Process one completed V21.2.15 unified observation
    through V12.6 -> V13.2.

    This function does NOT capture market data.
    """

    # --------------------------------------------------
    # Step 0 — Validate unified observation
    # --------------------------------------------------

    if not isinstance(unified_observation_result, dict):
        return _reject(
            "V21.2.15",
            "Unified observation result must be a dictionary.",
        )

    if unified_observation_result.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        return _reject(
            "V21.2.15",
            "Unified observation must be COMPLETE.",
            Unified_Observation=unified_observation_result,
        )

    # --------------------------------------------------
    # Step 1 — V12.6 Momentum
    #
    # Reuses the existing V21.2.15 momentum bridge.
    # IMPORTANT: this does not collect observations.
    # --------------------------------------------------

    momentum_result = evaluate_unified_observation_momentum(
        unified_observation_result
    )

    if momentum_result.get("Status") != (
        "UNIFIED_MOMENTUM_COMPLETE"
    ):
        return _reject(
            "V12.6",
            "Unified momentum evaluation failed.",
            Unified_Observation=unified_observation_result,
            Momentum_Result=momentum_result,
        )

    results = []

    momentum_contract_results = momentum_result.get(
        "Results",
        []
    )

    # The V21.2.15 momentum bridge produces one result
    # for each observed contract.
    for momentum_item in momentum_contract_results:

        # --------------------------------------------------
        # Step 2 — V12.7 Stage 1
        # Market Context Evidence
        # --------------------------------------------------

        # V21.2.15 wraps the V12.6 result inside
        # the per-contract momentum result.
        # V12.7 requires the inner Momentum Confirmation
        # dictionary directly.
        momentum_confirmation = momentum_item.get(
            "Momentum Confirmation"
        )

        context_evidence = evaluate_market_context_evidence(
            momentum_confirmation
        )

        if context_evidence.get("Status") != "EVALUATED":
            results.append(
                _reject(
                    "V12.7_STAGE_1",
                    "Market context evidence evaluation failed.",
                    Momentum_Result=momentum_item,
                    Context_Evidence=context_evidence,
                )
            )
            continue

        # --------------------------------------------------
        # Step 3 — V12.7 Stage 2
        # Market Context Classification
        # --------------------------------------------------

        market_context = (
            evaluate_market_context_classification(
                context_evidence
            )
        )

        if market_context.get("Status") != "CLASSIFIED":
            results.append(
                _reject(
                    "V12.7_STAGE_2",
                    "Market context classification failed.",
                    Momentum_Result=momentum_item,
                    Context_Evidence=context_evidence,
                    Market_Context=market_context,
                )
            )
            continue

        # --------------------------------------------------
        # Step 4 — V12.7 Stage 3
        # Momentum Context
        # --------------------------------------------------

        momentum_context = evaluate_momentum_context(
            momentum_confirmation,
            market_context,
        )

        if momentum_context.get("Status") != "EVALUATED":
            results.append(
                _reject(
                    "V12.7_STAGE_3",
                    "Momentum context evaluation failed.",
                    Momentum_Result=momentum_item,
                    Context_Evidence=context_evidence,
                    Market_Context=market_context,
                    Momentum_Context=momentum_context,
                )
            )
            continue

        # --------------------------------------------------
        # Step 5 — V12.8 Stage 1
        # Opportunity Evidence
        # --------------------------------------------------

        opportunity_evidence = evaluate_opportunity_evidence(
            momentum_context
        )

        if opportunity_evidence.get("Status") != "EVALUATED":
            results.append(
                _reject(
                    "V12.8_STAGE_1",
                    "Opportunity evidence evaluation failed.",
                    Momentum_Context=momentum_context,
                    Opportunity_Evidence=opportunity_evidence,
                )
            )
            continue

        # --------------------------------------------------
        # Step 6 — V12.8 Stage 2
        # Opportunity Classification
        # --------------------------------------------------

        opportunity_classification = (
            evaluate_opportunity_classification(
                opportunity_evidence
            )
        )

        if opportunity_classification.get("Status") != (
            "CLASSIFIED"
        ):
            results.append(
                _reject(
                    "V12.8_STAGE_2",
                    "Opportunity classification failed.",
                    Opportunity_Evidence=opportunity_evidence,
                    Opportunity_Classification=(
                        opportunity_classification
                    ),
                )
            )
            continue

        # --------------------------------------------------
        # Step 7 — V12.8 Stage 3
        # Opportunity Strength
        # --------------------------------------------------

        opportunity_strength = evaluate_opportunity_strength(
            opportunity_classification
        )

        if opportunity_strength.get("Status") != "EVALUATED":
            results.append(
                _reject(
                    "V12.8_STAGE_3",
                    "Opportunity strength evaluation failed.",
                    Opportunity_Classification=(
                        opportunity_classification
                    ),
                    Opportunity_Strength=opportunity_strength,
                )
            )
            continue

        # --------------------------------------------------
        # Step 8 — V12.9 Stage 1
        # Risk Evidence
        # --------------------------------------------------

        risk_evidence = evaluate_risk_evidence(
            opportunity_strength
        )

        if risk_evidence.get("Status") != "EVALUATED":
            results.append(
                _reject(
                    "V12.9_STAGE_1",
                    "Risk evidence evaluation failed.",
                    Opportunity_Strength=opportunity_strength,
                    Risk_Evidence=risk_evidence,
                )
            )
            continue

        # --------------------------------------------------
        # Step 9 — V12.9 Stage 2
        # Risk Classification
        # --------------------------------------------------

        risk_classification = evaluate_risk_classification(
            risk_evidence
        )

        if risk_classification.get("Status") != "CLASSIFIED":
            results.append(
                _reject(
                    "V12.9_STAGE_2",
                    "Risk classification failed.",
                    Risk_Evidence=risk_evidence,
                    Risk_Classification=risk_classification,
                )
            )
            continue

        # --------------------------------------------------
        # Step 10 — V12.9 Stage 3
        # Trade Quality
        # --------------------------------------------------

        trade_quality = evaluate_trade_quality(
            risk_classification
        )

        if trade_quality.get("Status") != "CLASSIFIED":
            results.append(
                _reject(
                    "V12.9_STAGE_3",
                    "Trade quality evaluation failed.",
                    Risk_Classification=risk_classification,
                    Trade_Quality=trade_quality,
                )
            )
            continue

        # --------------------------------------------------
        # Step 11 — V13.1 Decision Context
        # --------------------------------------------------

        decision_context = evaluate_decision_context(
            trade_quality
        )

        if decision_context.get("Status") != "EVALUATED":
            results.append(
                _reject(
                    "V13.1",
                    "Decision context evaluation failed.",
                    Trade_Quality=trade_quality,
                    Decision_Context=decision_context,
                )
            )
            continue

        # --------------------------------------------------
        # Step 12 — V13.2 Entry Qualification
        # --------------------------------------------------

        entry_qualification = evaluate_entry_qualification(
            decision_context
        )

        if entry_qualification.get("Status") != "QUALIFIED":
            results.append(
                _reject(
                    "V13.2",
                    "Entry qualification evaluation failed.",
                    Decision_Context=decision_context,
                    Entry_Qualification=entry_qualification,
                )
            )
            continue

        # --------------------------------------------------
        # Complete contract result
        # --------------------------------------------------

        results.append(
            {
                "Status": "DECISION_ENTRY_EVALUATED",

                "Trading Symbol": decision_context.get(
                    "Trading Symbol"
                ),
                "Underlying": decision_context.get(
                    "Underlying"
                ),
                "Expiry": decision_context.get("Expiry"),
                "Strike": decision_context.get("Strike"),
                "Option Type": decision_context.get(
                    "Option Type"
                ),

                "Option Direction": decision_context.get(
                    "Option Direction"
                ),
                "Momentum Confirmation": decision_context.get(
                    "Momentum Confirmation"
                ),
                "Market Context": decision_context.get(
                    "Market Context"
                ),
                "Movement Relationship": decision_context.get(
                    "Movement Relationship"
                ),
                "Momentum Context": decision_context.get(
                    "Momentum Context"
                ),

                "Opportunity Classification": (
                    decision_context.get(
                        "Opportunity Classification"
                    )
                ),
                "Opportunity Strength": (
                    decision_context.get(
                        "Opportunity Strength"
                    )
                ),
                "Risk Classification": (
                    decision_context.get(
                        "Risk Classification"
                    )
                ),
                "Trade Quality": decision_context.get(
                    "Trade Quality"
                ),

                "Entry Qualification": (
                    entry_qualification.get(
                        "Entry Qualification"
                    )
                ),

                "Market Context Result": momentum_context,
                "Opportunity Evidence": opportunity_evidence,
                "Opportunity Classification Result": (
                    opportunity_classification
                ),
                "Opportunity Strength Result": (
                    opportunity_strength
                ),
                "Risk Evidence": risk_evidence,
                "Risk Classification Result": (
                    risk_classification
                ),
                "Trade Quality Result": trade_quality,
                "Decision Context": decision_context,
                "Entry Qualification Result": (
                    entry_qualification
                ),

                "Live Order": False,
                "Paper Trade": False,
            }
        )

    return {
        "Status": "DECISION_ENTRY_COMPLETE",
        "Contract Count": len(results),
        "Results": results,

        "Unified Observation": unified_observation_result,
        "Momentum Result": momentum_result,

        "New Market Observations": False,
        "Live Order": False,
        "Paper Trade": False,
    }

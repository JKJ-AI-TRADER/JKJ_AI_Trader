"""
JKJ AI Trader
Intraday Option Opportunity Decision V7

Purpose:
Combine momentum and candidate-enrichment information into a
pre-entry opportunity decision.

This module does NOT:
- place orders
- connect to Zerodha
- modify main.py
- modify the existing Momentum Engine
- replace the Entry Gate
"""

def decide_option_opportunity(
    momentum_result,
    enrichment_result,
):
    """
    Decide whether an option deserves further entry evaluation.

    Decision levels:
        NO TRADE
        WATCH
        ENTRY CANDIDATE
        STRONG ENTRY CANDIDATE

    The final execution decision remains with the Entry Gate.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not isinstance(momentum_result, dict):
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Momentum result must be a dictionary."
            ],
        }

    if not isinstance(enrichment_result, dict):
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Enrichment result must be a dictionary."
            ],
        }

    if momentum_result.get("Status") != "READY":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 100,
            "Reasons": [
                "Momentum analysis is not ready."
            ],
        }

    if enrichment_result.get("Status") != "READY":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 100,
            "Reasons": [
                "Candidate enrichment is not ready."
            ],
        }

    # ---------------------------------------------------------
    # READ MOMENTUM
    # ---------------------------------------------------------

    momentum_score = momentum_result.get(
        "Momentum Score",
        0
    )

    momentum_status = momentum_result.get(
        "Momentum Status",
        "NO TRADE"
    )

    trade_candidate = momentum_result.get(
        "Trade Candidate",
        False
    )

    exhaustion_score = momentum_result.get(
        "Exhaustion Score",
        0
    )

    # ---------------------------------------------------------
    # READ ENRICHMENT
    # ---------------------------------------------------------

    alignment = enrichment_result.get(
        "Option Alignment",
        "MIXED"
    )

    liquidity_status = enrichment_result.get(
        "Liquidity Status",
        "PENDING"
    )

    economic_status = enrichment_result.get(
        "Economic Status",
        "PENDING"
    )

    underlying_momentum = enrichment_result.get(
        "Underlying Momentum",
        "MIXED"
    )

    # ---------------------------------------------------------
    # HARD SAFETY CHECKS
    # ---------------------------------------------------------

    if not trade_candidate:
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 90,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Momentum score is below the entry-candidate "
                "threshold."
            ],
        }

    if momentum_score < 80:
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 90,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Momentum score is below 80."
            ],
        }

    if exhaustion_score <= -13:
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 100,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Severe exhaustion blocks a fresh option entry."
            ],
        }

    if alignment == "AGAINST":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 90,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Option momentum is moving against the "
                "underlying direction."
            ],
        }

    if liquidity_status == "POOR":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 100,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Poor liquidity is not acceptable for entry."
            ],
        }

    if economic_status == "NOT VIABLE":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Confidence": 100,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Trade economics are not viable."
            ],
        }

    # ---------------------------------------------------------
    # INFORMATION PENDING
    # ---------------------------------------------------------

    pending_items = []

    if liquidity_status == "PENDING":
        pending_items.append(
            "Live spread/liquidity confirmation is required."
        )

    if economic_status == "PENDING":
        pending_items.append(
            "Profit potential and risk/reward confirmation "
            "are required."
        )

    if len(pending_items) > 0:
        return {
            "Status": "READY",
            "Decision": "WATCH",
            "Confidence": 70,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": pending_items,
        }

    # ---------------------------------------------------------
    # CAUTION CONDITIONS
    # ---------------------------------------------------------

    caution_reasons = []

    if exhaustion_score <= -10:
        caution_reasons.append(
            "Strong exhaustion warning is present."
        )

    if alignment == "MIXED":
        caution_reasons.append(
            "Underlying direction is not fully aligned."
        )

    if underlying_momentum == "WEAK":
        caution_reasons.append(
            "Underlying momentum is weak."
        )

    if liquidity_status == "ACCEPTABLE":
        caution_reasons.append(
            "Liquidity is acceptable but not ideal."
        )

    # ---------------------------------------------------------
    # STRONG CANDIDATE
    # ---------------------------------------------------------

    if (
        momentum_score >= 85
        and alignment == "SUPPORTIVE"
        and economic_status == "VIABLE"
        and liquidity_status in (
            "EXCELLENT",
            "GOOD",
        )
        and exhaustion_score > -10
        and underlying_momentum == "HEALTHY"
    ):

        return {
            "Status": "READY",
            "Decision": "STRONG ENTRY CANDIDATE",
            "Confidence": 90,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Strong momentum, supportive underlying, "
                "healthy underlying momentum and viable "
                "trade economics are confirmed."
            ],
        }

    # ---------------------------------------------------------
    # NORMAL ENTRY CANDIDATE
    # ---------------------------------------------------------

    if (
        momentum_score >= 80
        and alignment == "SUPPORTIVE"
        and economic_status == "VIABLE"
        and liquidity_status in (
            "EXCELLENT",
            "GOOD",
            "ACCEPTABLE",
        )
    ):

        if len(caution_reasons) > 0:
            return {
                "Status": "READY",
                "Decision": "ENTRY CANDIDATE",
                "Confidence": 80,
                "Momentum Score": momentum_score,
                "Exhaustion Score": exhaustion_score,
                "Reasons": caution_reasons,
            }

        return {
            "Status": "READY",
            "Decision": "ENTRY CANDIDATE",
            "Confidence": 85,
            "Momentum Score": momentum_score,
            "Exhaustion Score": exhaustion_score,
            "Reasons": [
                "Momentum, underlying alignment, liquidity "
                "and economics support further entry evaluation."
            ],
        }

    # ---------------------------------------------------------
    # DEFAULT
    # ---------------------------------------------------------

    return {
        "Status": "READY",
        "Decision": "WATCH",
        "Confidence": 65,
        "Momentum Score": momentum_score,
        "Exhaustion Score": exhaustion_score,
        "Reasons": [
            "Momentum exists, but all confirmation conditions "
            "for an entry candidate are not yet satisfied."
        ],
    }
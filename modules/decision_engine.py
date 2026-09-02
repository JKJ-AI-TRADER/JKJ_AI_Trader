"""
JKJ AI Decision Engine v0.5

Wisdom Before Wealth.

This engine evaluates NEW investment opportunities.

A high Opportunity Score means a stock deserves attention.
It does NOT automatically mean BUY.

Every decision must be explainable.
"""


def generate_decision(
    opportunity_score,
    risk_level,
    portfolio_loss=0,
    holding_status=False,
    stock_loss=0,
    trend="UNKNOWN",
    long_term_trend="UNKNOWN",
    recovery_confirmed=False
):

    risk_level = str(risk_level).upper()
    trend = str(trend).upper()
    long_term_trend = str(long_term_trend).upper()

    positive_evidence = []
    risk_warnings = []
    missing_confirmation = []
    reasons = []

    # -----------------------------------------
    # EXISTING HOLDING
    # -----------------------------------------

    if holding_status:

        return {
            "JKJ Decision": "USE HOLDING ENGINE",
            "Reasons": [
                "This stock is already held in the portfolio.",
                "Existing positions should be evaluated by the Holding Decision Engine."
            ],
            "Positive Evidence": [],
            "Risk Warnings": [],
            "Missing Confirmation": [],
            "Next Required Signal":
                "Evaluate the position using the Holding Decision Engine."
        }

    # -----------------------------------------
    # CAPITAL PROTECTION
    # -----------------------------------------

    if portfolio_loss <= -20:

        return {
            "JKJ Decision": "WAIT",
            "Reasons": [
                "Portfolio drawdown exceeds the JKJ safety threshold.",
                "New exposure should be avoided until portfolio risk improves."
            ],
            "Positive Evidence": [],
            "Risk Warnings": [
                "Portfolio drawdown is above the JKJ safety threshold."
            ],
            "Missing Confirmation": [
                "Portfolio risk must improve before adding new exposure."
            ],
            "Next Required Signal":
                "Wait for portfolio drawdown and overall risk conditions to improve."
        }

    # -----------------------------------------
    # BUILD POSITIVE EVIDENCE
    # -----------------------------------------

    if opportunity_score >= 70:
        positive_evidence.append(
            "Opportunity score is above the preferred minimum level."
        )

    if trend == "IMPROVING":
        positive_evidence.append(
            "Short-term conditions are improving."
        )

    if long_term_trend == "UPTREND":
        positive_evidence.append(
            "Long-term trend is positive."
        )

    if recovery_confirmed:
        positive_evidence.append(
            "Recovery confirmation is available."
        )

    # -----------------------------------------
    # HIGH RISK
    # -----------------------------------------

    if risk_level == "HIGH":

        risk_warnings.append(
            "Overall risk level is HIGH."
        )

        missing_confirmation.append(
            "Risk reduction or stronger confirmation is required."
        )

        if opportunity_score >= 85:

            return {
                "JKJ Decision": "WATCH",
                "Reasons": [
                    "Opportunity score is strong, but risk level is HIGH.",
                    "Capital should not be committed without stronger confirmation."
                ],
                "Positive Evidence": positive_evidence,
                "Risk Warnings": risk_warnings,
                "Missing Confirmation": missing_confirmation,
                "Next Required Signal":
                    "Wait for risk conditions to improve before considering new capital exposure."
            }

        return {
            "JKJ Decision": "WAIT",
            "Reasons": [
                "Risk level is HIGH.",
                "Opportunity conditions are not strong enough to justify new exposure."
            ],
            "Positive Evidence": positive_evidence,
            "Risk Warnings": risk_warnings,
            "Missing Confirmation": missing_confirmation,
            "Next Required Signal":
                "Wait for both risk conditions and opportunity evidence to improve."
        }

    # -----------------------------------------
    # LONG-TERM DOWNTREND
    # -----------------------------------------

    if (
        long_term_trend == "DOWNTREND"
        and not recovery_confirmed
    ):

        risk_warnings.append(
            "Long-term trend remains in a DOWNTREND."
        )

        missing_confirmation.append(
            "Confirmed recovery from the long-term downtrend."
        )

        return {
            "JKJ Decision": "WATCH",
            "Reasons": [
                "The stock may have an attractive opportunity score.",
                "However, the longer-term trend remains a downtrend.",
                "Recovery has not yet been confirmed.",
                "A fresh entry should wait for stronger evidence."
            ],
            "Positive Evidence": positive_evidence,
            "Risk Warnings": risk_warnings,
            "Missing Confirmation": missing_confirmation,
            "Next Required Signal":
                "Wait for confirmed recovery before considering new capital exposure."
        }

    # -----------------------------------------
    # STRONG CONFIRMED RECOVERY
    # -----------------------------------------

    if (
        opportunity_score >= 85
        and trend == "IMPROVING"
        and (
            long_term_trend == "UPTREND"
            or recovery_confirmed
        )
    ):

        return {
            "JKJ Decision": "REVIEW BUY",
            "Reasons": [
                "Strong opportunity score.",
                "Short-term conditions are improving.",
                "Trend or recovery evidence supports further entry review.",
                "Final position sizing and capital checks are still required."
            ],
            "Positive Evidence": positive_evidence,
            "Risk Warnings": risk_warnings,
            "Missing Confirmation": [],
            "Next Required Signal":
                "Review position size and capital allocation before considering a new entry."
        }

    # -----------------------------------------
    # GOOD OPPORTUNITY
    # -----------------------------------------

    if opportunity_score >= 70:

        missing_confirmation.append(
            "Additional trend confirmation is required."
        )

        return {
            "JKJ Decision": "WATCH",
            "Reasons": [
                "The stock shows a good opportunity score.",
                "Further trend confirmation is required before committing new capital."
            ],
            "Positive Evidence": positive_evidence,
            "Risk Warnings": risk_warnings,
            "Missing Confirmation": missing_confirmation,
            "Next Required Signal":
                "Wait for stronger trend confirmation."
        }

    # -----------------------------------------
    # WEAK OPPORTUNITY
    # -----------------------------------------

    missing_confirmation.append(
        "Stronger opportunity evidence is required."
    )

    return {
        "JKJ Decision": "WAIT",
        "Reasons": [
            "Opportunity score is below the preferred level for a new position."
        ],
        "Positive Evidence": positive_evidence,
        "Risk Warnings": risk_warnings,
        "Missing Confirmation": missing_confirmation,
        "Next Required Signal":
            "Wait for the opportunity score and supporting evidence to improve."
    }
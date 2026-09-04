"""
JKJ AI Decision Engine v0.5

Wisdom Before Wealth.

This engine evaluates NEW investment opportunities.

A high Opportunity Score means a stock deserves attention.
It does NOT automatically mean BUY.

Every decision must be explainable.
"""
def calculate_confidence(
    opportunity_score,
    risk_level
):
    """
    Calculate a simple explainable confidence score.

    Confidence begins with the opportunity score
    and is reduced according to the risk level.
    """

    confidence = float(opportunity_score)

    risk_level = str(risk_level).upper()

    if risk_level == "HIGH":
        confidence -= 30

    elif risk_level == "MEDIUM":
        confidence -= 15

    confidence = max(0, min(100, confidence))

    return round(confidence, 2)


def generate_decision(
    opportunity_score,
    risk_level,
    portfolio_loss=0,
    holding_status=False,
    trend="UNKNOWN",
    long_term_trend="UNKNOWN",
    recovery_confirmed=False,
    momentum_condition="UNKNOWN",
    momentum_score=0,
    base_opportunity_score=0,
    technical_score=0,
    market_score=0,
    market_state="UNKNOWN"
):


    risk_level = str(risk_level).upper()
    trend = str(trend).upper()
    long_term_trend = str(long_term_trend).upper()
    momentum_condition = str(momentum_condition).upper()
    market_state = str(market_state).upper()
    momentum_score = float(momentum_score)
    confidence = calculate_confidence(
        opportunity_score,
        risk_level
    )

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
            "Confidence": confidence,
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
            "Confidence": 95.0,
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
    if momentum_condition == "EARLY MOMENTUM":
        positive_evidence.append(
        "Early momentum signals are appearing, but confirmation is still limited."
    )

    elif momentum_condition == "BUILDING MOMENTUM":
        positive_evidence.append(
        "Momentum is building with improving price, RSI or volume evidence."
    )

    elif momentum_condition == "CONFIRMED MOMENTUM":
        positive_evidence.append(
        "Momentum confirmation supports the opportunity."
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
                "Confidence": 75.0,
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
            "Confidence": 90.0,
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

        # If the stock has no meaningful positive evidence,
        # remain in WAIT rather than WATCH.
        if (
            opportunity_score < 60
            and technical_score < 60
            and momentum_score < 60
        ):

            return {
                "JKJ Decision": "WAIT",
                "Confidence": 90.0,
                "Reasons": [
                    "The long-term trend remains in a downtrend.",
                    "Technical conditions do not currently support an entry.",
                    "Momentum does not currently support an entry.",
                    "Opportunity evidence is currently weak.",
                    "Recovery from the downtrend has not yet been confirmed."
                ],
                "Positive Evidence": positive_evidence,
                "Risk Warnings": risk_warnings,
                "Missing Confirmation": missing_confirmation,
                "Next Required Signal":
                    "Wait for clear technical and momentum improvement and confirmed recovery before considering a new entry."
            }

        # Some positive evidence exists, but recovery is not confirmed.
        return {
            "JKJ Decision": "WATCH",
            "Confidence": 80.0,
            "Reasons": [
                "The stock shows some developing positive evidence.",
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
    # STRONG MOMENTUM CONFIRMATION
    # -----------------------------------------

    if (
        momentum_condition == "BUILDING MOMENTUM"
        and momentum_score >= 70
        and technical_score >= 60
        and market_score >= 40
        and base_opportunity_score >= 60
        and risk_level != "HIGH"
        and long_term_trend != "DOWNTREND"
    ):
        return {
        "JKJ Decision": "REVIEW BUY",
        "Confidence": 75.0,
        "Reasons": [
            "Momentum is building strongly.",
            "Technical conditions are bullish.",
            "Market conditions provide supporting confirmation.",
            "The opportunity has sufficient evidence for further entry review.",
            "Final position sizing and capital checks are still required."
        ],
        "Positive Evidence": positive_evidence,
        "Risk Warnings": risk_warnings,
        "Missing Confirmation": [],
        "Next Required Signal":
            "Review position size and capital allocation before considering a new entry."
    }
# -----------------------------------------
# EARLY MOMENTUM SETUP
# -----------------------------------------

    if (
        momentum_condition == "BUILDING MOMENTUM"
        and momentum_score >= 70
        and base_opportunity_score >= 60
        and risk_level != "HIGH"
        and long_term_trend != "DOWNTREND"
    ):

        if market_score < 40:

            if market_state == "OVERSOLD — POSSIBLE RECOVERY ZONE":

                missing_confirmation.append(
                    "Market recovery confirmation is required before committing new capital."
                )

            else:

                missing_confirmation.append(
                    "Broader market confirmation is required before committing new capital."
                )

        # Stronger trend confirmation is required unless
        # the stock already has very strong evidence.
        if not (
            technical_score >= 80
            and momentum_score >= 80
            and base_opportunity_score >= 80
            and (
                long_term_trend == "UPTREND"
                or recovery_confirmed
            )
        ):

            missing_confirmation.append(
                "Stronger trend confirmation before committing new capital."
            )

        return {
            "JKJ Decision": "WATCH",

            "Confidence": (
                70.0
                - (10.0 if market_score < 40 else 0.0)
                - (5.0 if risk_level == "MEDIUM" else 0.0)
                + (5.0 if technical_score >= 80 else 0.0)
                + (5.0 if momentum_score >= 80 else 0.0)
            ),

            "Reasons": [
                "Momentum is building.",
                "Price, RSI or volume evidence suggests increasing market interest.",
                "The opportunity is developing but is not yet fully confirmed.",
                "The stock should be watched for stronger trend confirmation."
            ] + (
                [
                    "The broader market remains bearish, but oversold conditions suggest a possible recovery zone. Confirmation is still required."
                ]
                if (
                    market_score < 40
                    and market_state == "OVERSOLD — POSSIBLE RECOVERY ZONE"
                )
                else (
                    [
                        "Market conditions remain weak or bearish, so additional caution is required."
                    ]
                    if market_score < 40
                    else []
                )
            ),

            "Positive Evidence": positive_evidence,
            "Risk Warnings": risk_warnings,
            "Missing Confirmation": missing_confirmation,

            "Next Required Signal": (
                "Wait for market recovery confirmation before considering a new entry."
                if (
                    market_score < 40
                    and market_state == "OVERSOLD — POSSIBLE RECOVERY ZONE"
                )
                else (
                    "Wait for broader market conditions to improve and for stronger trend confirmation before considering a new entry."
                    if market_score < 40
                    else
                    "Wait for improving technical and trend confirmation before considering a new entry."
                )
            )
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
            "Confidence": confidence,
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
            "Confidence": 65.0,
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
    # BLOCKED STRONG SIGNALS
    # -----------------------------------------

    if (
        momentum_score >= 70
        or technical_score >= 60
    ):

        if market_score < 40:

            if market_state == "OVERSOLD — POSSIBLE RECOVERY ZONE":

                missing_confirmation.append(
                    "Market recovery confirmation is required before committing new capital."
                )

        else:

            missing_confirmation.append(
            "Broader market confirmation is required before committing new capital."
            )

        if base_opportunity_score < 60:

            missing_confirmation.append(
                "Opportunity evidence is not yet strong enough."
            )

    # -----------------------------------------
    # WEAK OPPORTUNITY
    # -----------------------------------------

    if not missing_confirmation:

        missing_confirmation.append(
            "Stronger opportunity evidence is required."
        )

    return {
        "JKJ Decision": "WAIT",
        "Confidence": 85.0,
        "Reasons": [
            "The opportunity score is below the preferred level for a new position."
        ] + (
            ["Market conditions are currently not supportive enough."]
            if market_score < 40
            else []
        ) + (
            ["Momentum and technical conditions show positive development."]
            if momentum_score >= 70 or technical_score >= 60
            else []
        ) + (
            ["Opportunity evidence is not yet strong enough."]
            if base_opportunity_score < 60
            else []
        ),
        "Positive Evidence": positive_evidence,
        "Risk Warnings": risk_warnings,
        "Missing Confirmation": missing_confirmation,
        "Next Required Signal":
            "Wait for the opportunity score and supporting evidence to improve."
    }
"""
JKJ AI Trader — Intraday Entry Gate V1

Wisdom Before Wealth.

Purpose:
Decide whether a strong momentum opportunity is suitable
for entry NOW.

The Momentum Engine identifies opportunity.
The Cost Engine determines economic viability.
The Entry Gate decides whether JKJ should enter.

No broker connection.
No live orders.
"""


def evaluate_intraday_entry(
    momentum_result,
    cost_result,
    risk_reward_ratio,
    current_price,
    peak_price=None
):

    reasons = []
    warnings = []

    # -----------------------------------------
    # 1. BASIC VALIDATION
    # -----------------------------------------

    if not isinstance(momentum_result, dict):

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Reasons": [
                "Momentum result is invalid."
            ],
            "Warnings": []
        }

    if not isinstance(cost_result, dict):

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Reasons": [
                "Cost result is invalid."
            ],
            "Warnings": []
        }

    try:

        current_price = float(
            current_price
        )

        risk_reward_ratio = float(
            risk_reward_ratio
        )

    except (
        ValueError,
        TypeError
    ):

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Reasons": [
                "Price or risk/reward input is invalid."
            ],
            "Warnings": []
        }

    if current_price <= 0:

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Reasons": [
                "Current price must be greater than zero."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # 2. READ MOMENTUM RESULT
    # -----------------------------------------

    momentum_score = float(
        momentum_result.get(
            "Momentum Score",
            0
        )
    )

    momentum_status = momentum_result.get(
        "Momentum Status",
        "NO TRADE"
    )

    trade_candidate = momentum_result.get(
        "Trade Candidate",
        False
    )

    exhaustion_penalty = float(
        momentum_result.get(
            "Exhaustion Penalty",
            0
        )
    )

    # -----------------------------------------
    # 3. MOMENTUM HARD GATE
    # -----------------------------------------

    if not trade_candidate:

        reasons.append(
            "Momentum engine has not identified "
            "a valid trade candidate."
        )

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Momentum Score": momentum_score,
            "Exhaustion Penalty": exhaustion_penalty,
            "Reasons": reasons,
            "Warnings": warnings
        }

    if momentum_score < 80:

        reasons.append(
            "Momentum score is below the entry threshold."
        )

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Momentum Score": momentum_score,
            "Exhaustion Penalty": exhaustion_penalty,
            "Reasons": reasons,
            "Warnings": warnings
        }

    reasons.append(
        "Momentum score meets the strong-entry threshold."
    )

    # -----------------------------------------
    # 4. EXHAUSTION GATE
    # -----------------------------------------

    if exhaustion_penalty <= -13:

        reasons.append(
            "Severe exhaustion is detected."
        )

        warnings.append(
            "Fresh entry is blocked because exhaustion "
            "risk is severe."
        )

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Momentum Score": momentum_score,
            "Exhaustion Penalty": exhaustion_penalty,
            "Reasons": reasons,
            "Warnings": warnings
        }

    elif exhaustion_penalty <= -10:

        reasons.append(
            "Strong exhaustion warning is present."
        )

        warnings.append(
            "Entry requires exceptional confirmation."
        )

    elif exhaustion_penalty <= -5:

        reasons.append(
            "Moderate exhaustion warning is present."
        )

        warnings.append(
            "Avoid chasing the move."
        )

    else:

        reasons.append(
            "Exhaustion remains within an acceptable range."
        )

    # -----------------------------------------
    # 5. COST VIABILITY GATE
    # -----------------------------------------

    cost_viable = cost_result.get(
        "Trade Viable",
        False
    )

    net_pnl = float(
        cost_result.get(
            "Net P&L",
            0
        )
    )

    if not cost_viable:

        reasons.append(
            "Expected trade economics are not profitable "
            "after estimated costs."
        )

        warnings.append(
            "Gross profit is insufficient after costs."
        )

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Momentum Score": momentum_score,
            "Exhaustion Penalty": exhaustion_penalty,
            "Net P&L": net_pnl,
            "Reasons": reasons,
            "Warnings": warnings
        }

    reasons.append(
        "Trade remains economically viable after costs."
    )

    # -----------------------------------------
    # 6. RISK / REWARD GATE
    # -----------------------------------------

    if risk_reward_ratio < 1.5:

        reasons.append(
            "Risk/reward ratio is below the minimum "
            "entry requirement."
        )

        warnings.append(
            "Insufficient reward relative to risk."
        )

        return {
            "Entry Status": "NO TRADE",
            "Entry Allowed": False,
            "Confidence": 0,
            "Momentum Score": momentum_score,
            "Exhaustion Penalty": exhaustion_penalty,
            "Net P&L": net_pnl,
            "Risk/Reward": risk_reward_ratio,
            "Reasons": reasons,
            "Warnings": warnings
        }

    elif risk_reward_ratio < 2.0:

        reasons.append(
            "Risk/reward is acceptable but moderate."
        )

        warnings.append(
            "Trade has limited risk/reward margin."
        )

    else:

        reasons.append(
            "Risk/reward is favourable."
        )

    # -----------------------------------------
    # 7. TOO-LATE / EXTENSION CHECK
    # -----------------------------------------

    if peak_price is not None:

        try:

            peak_price = float(
                peak_price
            )

            if peak_price > 0:

                distance_from_peak = (
                    (
                        peak_price
                        - current_price
                    )
                    / peak_price
                ) * 100

                if distance_from_peak < 0:

                    distance_from_peak = 0

                if distance_from_peak <= 0.50:

                    reasons.append(
                        "Price is very close to the recent peak."
                    )

                    warnings.append(
                        "Entry is vulnerable to chasing "
                        "near the peak."
                    )

        except (
            ValueError,
            TypeError
        ):

            peak_price = None

    # -----------------------------------------
    # 8. ENTRY STATUS
    # -----------------------------------------

    if exhaustion_penalty <= -10:

        entry_status = "ENTRY READY — CAUTION"
        confidence = 70

        warnings.append(
            "Strong momentum exists, but exhaustion "
            "requires careful entry confirmation."
        )

    elif exhaustion_penalty <= -5:

        entry_status = "ENTRY READY"
        confidence = 80

    else:

        entry_status = "STRONG ENTRY"
        confidence = 90

    # -----------------------------------------
    # 9. FINAL DECISION
    # -----------------------------------------

    reasons.append(
        "All mandatory entry gates have passed."
    )

    return {

        "Entry Status": entry_status,

        "Entry Allowed": True,

        "Confidence": confidence,

        "Momentum Score": momentum_score,

        "Momentum Status": momentum_status,

        "Exhaustion Penalty": exhaustion_penalty,

        "Net P&L": net_pnl,

        "Risk/Reward": risk_reward_ratio,

        "Reasons": reasons,

        "Warnings": warnings
    }
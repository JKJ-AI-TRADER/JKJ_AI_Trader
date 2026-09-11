"""
JKJ AI Trader — Intraday Exit Engine V1

Wisdom Before Wealth.

Purpose:
Determine when an existing intraday position should be exited.

The engine considers:
- Stop loss
- Profit protection
- Momentum deterioration
- Volume deterioration
- Underlying deterioration
- Structure deterioration
- Time-based exit

No broker connection.
No live orders.
"""


def evaluate_intraday_exit(
    entry_price,
    current_price,
    stop_loss_price,
    target_price=None,
    profit_protection_result=None,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    holding_minutes=0,
    max_holding_minutes=60
):

    reasons = []
    warnings = []

    # -----------------------------------------
    # 1. INPUT VALIDATION
    # -----------------------------------------

    try:

        entry_price = float(entry_price)
        current_price = float(current_price)
        stop_loss_price = float(stop_loss_price)
        holding_minutes = float(holding_minutes)
        max_holding_minutes = float(
            max_holding_minutes
        )

    except (
        ValueError,
        TypeError
    ):

        return {
            "Exit Status": "NO TRADE",
            "Exit Required": False,
            "Exit Reason": "INVALID INPUT",
            "Current Profit %": 0.0,
            "Reasons": [
                "Invalid exit input."
            ],
            "Warnings": []
        }

    if entry_price <= 0:

        return {
            "Exit Status": "NO TRADE",
            "Exit Required": False,
            "Exit Reason": "INVALID INPUT",
            "Current Profit %": 0.0,
            "Reasons": [
                "Entry price must be greater than zero."
            ],
            "Warnings": []
        }

    if current_price <= 0:

        return {
            "Exit Status": "NO TRADE",
            "Exit Required": False,
            "Exit Reason": "INVALID INPUT",
            "Current Profit %": 0.0,
            "Reasons": [
                "Current price must be greater than zero."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # 2. CURRENT PROFIT
    # -----------------------------------------

    current_profit_percentage = (
        (
            current_price
            - entry_price
        )
        / entry_price
    ) * 100

    # -----------------------------------------
    # 3. NORMALISE SIGNALS
    # -----------------------------------------

    momentum_status = str(
        momentum_status
    ).strip().upper()

    volume_status = str(
        volume_status
    ).strip().upper()

    underlying_status = str(
        underlying_status
    ).strip().upper()

    structure_status = str(
        structure_status
    ).strip().upper()

    # -----------------------------------------
    # 4. HARD STOP LOSS
    # -----------------------------------------

    if current_price <= stop_loss_price:

        reasons.append(
            "Current price has reached or crossed "
            "the predefined stop-loss."
        )

        warnings.append(
            "Capital protection takes priority."
        )

        return {
            "Exit Status": "EXIT",
            "Exit Required": True,
            "Exit Reason": "STOP LOSS",
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 5. PROFIT PROTECTION RESULT
    # -----------------------------------------

    if isinstance(
        profit_protection_result,
        dict
    ):

        protection_exit = (
            profit_protection_result.get(
                "Exit Decision"
            )
        )

        protection_status = (
            profit_protection_result.get(
                "Status",
                ""
            )
        )

        if protection_exit == "EXIT":

            reasons.append(
                "Profit Protection Engine recommends "
                "an exit."
            )

            warnings.append(
                f"Protection status: "
                f"{protection_status}"
            )

            return {
                "Exit Status": "EXIT",
                "Exit Required": True,
                "Exit Reason": "PROFIT PROTECTION",
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

    # -----------------------------------------
    # 6. TARGET CHECK
    # -----------------------------------------

    if target_price is not None:

        try:

            target_price = float(
                target_price
            )

            if (
                target_price > 0
                and current_price >= target_price
            ):

                reasons.append(
                    "Current price has reached "
                    "the predefined target."
                )

                return {
                    "Exit Status": "EXIT",
                    "Exit Required": True,
                    "Exit Reason": "TARGET REACHED",
                    "Current Profit %": round(
                        current_profit_percentage,
                        2
                    ),
                    "Reasons": reasons,
                    "Warnings": warnings
                }

        except (
            ValueError,
            TypeError
        ):

            warnings.append(
                "Target price could not be evaluated."
            )

    # -----------------------------------------
    # 7. SIGNAL DETERIORATION
    # -----------------------------------------

    momentum_weak = momentum_status in {
        "WEAK",
        "DETERIORATING",
        "EXHAUSTED",
        "REVERSING"
    }

    volume_weak = volume_status in {
        "WEAK",
        "DECREASING",
        "DETERIORATING"
    }

    underlying_weak = underlying_status in {
        "WEAK",
        "NEGATIVE",
        "DETERIORATING",
        "REVERSING"
    }

    structure_weak = structure_status in {
        "WEAK",
        "DETERIORATING",
        "REVERSING"
    }

    weakness_count = 0

    if momentum_weak:
        weakness_count += 1

    if volume_weak:
        weakness_count += 1

    if underlying_weak:
        weakness_count += 1

    if structure_weak:
        weakness_count += 1

    # -----------------------------------------
    # 8. MOMENTUM REVERSAL
    # -----------------------------------------

    if (
        momentum_status == "REVERSING"
        and weakness_count >= 2
    ):

        reasons.append(
            "Momentum is reversing with confirmation "
            "from other market signals."
        )

        warnings.append(
            "Do not allow a weakening position "
            "to deteriorate further."
        )

        return {
            "Exit Status": "EXIT",
            "Exit Required": True,
            "Exit Reason": "MOMENTUM REVERSAL",
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 9. MULTIPLE SIGNAL DETERIORATION
    # -----------------------------------------

    if (
        weakness_count >= 3
        and current_profit_percentage > 0
    ):

        reasons.append(
            "Multiple supporting signals have "
            "deteriorated while the trade is profitable."
        )

        warnings.append(
            "Protect established profit."
        )

        return {
            "Exit Status": "EXIT",
            "Exit Required": True,
            "Exit Reason": "SIGNAL DETERIORATION",
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 10. LOSING TRADE WITH WEAK MOMENTUM
    # -----------------------------------------

    if (
        current_profit_percentage < 0
        and weakness_count >= 2
    ):

        reasons.append(
            "The trade is losing while multiple "
            "supporting signals are weakening."
        )

        warnings.append(
            "Capital protection takes priority "
            "over waiting for recovery."
        )

        return {
            "Exit Status": "EXIT",
            "Exit Required": True,
            "Exit Reason": "LOSING TRADE — WEAKENING",
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 11. TIME EXIT
    # -----------------------------------------

    if (
        max_holding_minutes > 0
        and holding_minutes >= max_holding_minutes
    ):

        reasons.append(
            "Maximum planned holding time has been reached."
        )

        warnings.append(
            "Intraday positions should not remain open "
            "without sufficient momentum."
        )

        return {
            "Exit Status": "EXIT",
            "Exit Required": True,
            "Exit Reason": "TIME EXIT",
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 12. WATCH CONDITION
    # -----------------------------------------

    if weakness_count == 2:

        reasons.append(
            "Two supporting signals are weakening."
        )

        warnings.append(
            "Exit conditions are developing; "
            "monitor closely."
        )

        return {
            "Exit Status": "WATCH",
            "Exit Required": False,
            "Exit Reason": "DETERIORATION WATCH",
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 13. HOLD
    # -----------------------------------------

    reasons.append(
        "No mandatory exit condition is currently present."
    )

    return {
        "Exit Status": "HOLD",
        "Exit Required": False,
        "Exit Reason": "NO EXIT CONDITION",
        "Current Profit %": round(
            current_profit_percentage,
            2
        ),
        "Reasons": reasons,
        "Warnings": warnings
    }
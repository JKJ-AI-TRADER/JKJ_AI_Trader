"""
JKJ AI Trader — Intraday Profit Protection Engine V1

Wisdom Before Wealth.

Purpose:
Protect profits after an intraday position has been entered.

The engine tracks:
- Entry price
- Current price
- Peak price
- Peak profit
- Current profit
- Retracement from peak
- Momentum condition
- Volume condition
- Underlying condition
- Structure condition

No broker connection.
No live orders.
"""


def evaluate_profit_protection(
    entry_price,
    current_price,
    peak_price,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
    stop_loss_price=None
):

    reasons = []
    warnings = []

    # -----------------------------------------
    # 1. INPUT VALIDATION
    # -----------------------------------------

    try:

        entry_price = float(entry_price)
        current_price = float(current_price)
        peak_price = float(peak_price)

    except (
        ValueError,
        TypeError
    ):

        return {
            "Status": "NO TRADE",
            "Exit Decision": "NO TRADE",
            "Profit Protected": False,
            "Current Profit %": 0.0,
            "Peak Profit %": 0.0,
            "Retracement %": 0.0,
            "Reasons": [
                "Invalid price input."
            ],
            "Warnings": []
        }

    if entry_price <= 0:

        return {
            "Status": "NO TRADE",
            "Exit Decision": "NO TRADE",
            "Profit Protected": False,
            "Current Profit %": 0.0,
            "Peak Profit %": 0.0,
            "Retracement %": 0.0,
            "Reasons": [
                "Entry price must be greater than zero."
            ],
            "Warnings": []
        }

    if current_price <= 0:

        return {
            "Status": "NO TRADE",
            "Exit Decision": "NO TRADE",
            "Profit Protected": False,
            "Current Profit %": 0.0,
            "Peak Profit %": 0.0,
            "Retracement %": 0.0,
            "Reasons": [
                "Current price must be greater than zero."
            ],
            "Warnings": []
        }

    if peak_price <= 0:

        return {
            "Status": "NO TRADE",
            "Exit Decision": "NO TRADE",
            "Profit Protected": False,
            "Current Profit %": 0.0,
            "Peak Profit %": 0.0,
            "Retracement %": 0.0,
            "Reasons": [
                "Peak price must be greater than zero."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # 2. PEAK PRICE PROTECTION
    # -----------------------------------------

    if current_price > peak_price:

        peak_price = current_price

        reasons.append(
            "A new peak price has been established."
        )

    # -----------------------------------------
    # 3. PROFIT CALCULATION
    # -----------------------------------------

    current_profit_percentage = (
        (
            current_price
            - entry_price
        )
        / entry_price
    ) * 100

    peak_profit_percentage = (
        (
            peak_price
            - entry_price
        )
        / entry_price
    ) * 100

    # -----------------------------------------
    # 4. RETRACEMENT FROM PEAK
    # -----------------------------------------

    if peak_profit_percentage > 0:

        retracement_percentage = (
            (
                peak_price
                - current_price
            )
            / (
                peak_price
                - entry_price
            )
        ) * 100

    else:

        retracement_percentage = 0.0

    if retracement_percentage < 0:

        retracement_percentage = 0.0

    # -----------------------------------------
    # 5. PROFIT STAGE
    # -----------------------------------------

    if current_profit_percentage < 2:

        profit_stage = "STAGE 1"
        protection_level = "LOW"

    elif current_profit_percentage < 5:

        profit_stage = "STAGE 2"
        protection_level = "MODERATE"

    elif current_profit_percentage < 10:

        profit_stage = "STAGE 3"
        protection_level = "HIGH"

    elif current_profit_percentage < 20:

        profit_stage = "STAGE 4"
        protection_level = "VERY HIGH"

    else:

        profit_stage = "STAGE 5"
        protection_level = "MAXIMUM"

    # -----------------------------------------
    # 6. MOMENTUM ASSESSMENT
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

    # -----------------------------------------
    # 7. STOP-LOSS CHECK
    # -----------------------------------------

    if stop_loss_price is not None:

        try:

            stop_loss_price = float(
                stop_loss_price
            )

            if current_price <= stop_loss_price:

                reasons.append(
                    "Current price has reached or crossed "
                    "the predefined stop-loss."
                )

                warnings.append(
                    "Capital protection takes priority."
                )

                return {
                    "Status": "EXIT — STOP LOSS",
                    "Exit Decision": "EXIT",
                    "Profit Protected": False,
                    "Profit Stage": profit_stage,
                    "Protection Level": protection_level,
                    "Current Profit %": round(
                        current_profit_percentage,
                        2
                    ),
                    "Peak Profit %": round(
                        peak_profit_percentage,
                        2
                    ),
                    "Retracement %": round(
                        retracement_percentage,
                        2
                    ),
                    "Peak Price": round(
                        peak_price,
                        4
                    ),
                    "Reasons": reasons,
                    "Warnings": warnings
                }

        except (
            ValueError,
            TypeError
        ):

            warnings.append(
                "Stop-loss value could not be evaluated."
            )

    # -----------------------------------------
    # 8. NO PROFIT YET
    # -----------------------------------------

    if current_profit_percentage <= 0:

        if momentum_weak:

            reasons.append(
                "Trade is not profitable and momentum "
                "is weakening."
            )

            return {
                "Status": "EXIT — MOMENTUM WEAKENING",
                "Exit Decision": "EXIT",
                "Profit Protected": False,
                "Profit Stage": profit_stage,
                "Protection Level": protection_level,
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Peak Profit %": round(
                    peak_profit_percentage,
                    2
                ),
                "Retracement %": round(
                    retracement_percentage,
                    2
                ),
                "Peak Price": round(
                    peak_price,
                    4
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

        reasons.append(
            "Trade has not yet established meaningful profit."
        )

        warnings.append(
            "Allow room while monitoring the predefined risk."
        )

        return {
            "Status": "PROFIT RUNNING",
            "Exit Decision": "HOLD",
            "Profit Protected": False,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 9. PROFIT PROTECTION LOGIC
    # -----------------------------------------

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
    # 10. STAGE 1
    # -----------------------------------------

    if current_profit_percentage < 2:

        reasons.append(
            "Profit is still in the early stage."
        )

        warnings.append(
            "Do not over-tighten protection prematurely."
        )

        return {
            "Status": "PROFIT RUNNING",
            "Exit Decision": "HOLD",
            "Profit Protected": False,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 11. STAGE 2 — 2% TO 5%
    # -----------------------------------------

    if current_profit_percentage < 5:

        if retracement_percentage >= 50:

            reasons.append(
                "A significant portion of the established "
                "profit has been retraced."
            )

            warnings.append(
                "Profit protection is becoming important."
            )

            return {
                "Status": "WATCH PROFIT",
                "Exit Decision": "WATCH",
                "Profit Protected": True,
                "Profit Stage": profit_stage,
                "Protection Level": protection_level,
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Peak Profit %": round(
                    peak_profit_percentage,
                    2
                ),
                "Retracement %": round(
                    retracement_percentage,
                    2
                ),
                "Peak Price": round(
                    peak_price,
                    4
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

        reasons.append(
            "Profit is developing with acceptable retracement."
        )

        return {
            "Status": "PROFIT RUNNING",
            "Exit Decision": "HOLD",
            "Profit Protected": True,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 12. STAGE 3 — 5% TO 10%
    # -----------------------------------------

    if current_profit_percentage < 10:

        if weakness_count >= 2 and retracement_percentage >= 20:

            reasons.append(
                "Multiple momentum quality signals are weakening "
                "while profit is retracing."
            )

            warnings.append(
                "Exit is recommended to protect established profit."
            )

            return {
                "Status": "EXIT — PROFIT PROTECTION",
                "Exit Decision": "EXIT",
                "Profit Protected": True,
                "Profit Stage": profit_stage,
                "Protection Level": protection_level,
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Peak Profit %": round(
                    peak_profit_percentage,
                    2
                ),
                "Retracement %": round(
                    retracement_percentage,
                    2
                ),
                "Peak Price": round(
                    peak_price,
                    4
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

        if retracement_percentage >= 35:

            reasons.append(
                "Profit retracement has become significant."
            )

            warnings.append(
                "Profit protection is strongly recommended."
            )

            return {
                "Status": "TRAILING EXIT ARMED",
                "Exit Decision": "WATCH",
                "Profit Protected": True,
                "Profit Stage": profit_stage,
                "Protection Level": protection_level,
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Peak Profit %": round(
                    peak_profit_percentage,
                    2
                ),
                "Retracement %": round(
                    retracement_percentage,
                    2
                ),
                "Peak Price": round(
                    peak_price,
                    4
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

        reasons.append(
            "Profit is meaningful and remains reasonably protected."
        )

        return {
            "Status": "PROFIT PROTECTED",
            "Exit Decision": "HOLD",
            "Profit Protected": True,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 13. STAGE 4 — 10% TO 20%
    # -----------------------------------------

    if current_profit_percentage < 20:

        if weakness_count >= 2 and retracement_percentage >= 15:

            reasons.append(
                "Profit is substantial but multiple "
                "supporting signals are weakening."
            )

            warnings.append(
                "Protect the established profit."
            )

            return {
                "Status": "EXIT — PROFIT PROTECTION",
                "Exit Decision": "EXIT",
                "Profit Protected": True,
                "Profit Stage": profit_stage,
                "Protection Level": protection_level,
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Peak Profit %": round(
                    peak_profit_percentage,
                    2
                ),
                "Retracement %": round(
                    retracement_percentage,
                    2
                ),
                "Peak Price": round(
                    peak_price,
                    4
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

        if retracement_percentage >= 25:

            reasons.append(
                "A meaningful portion of peak profit "
                "has been given back."
            )

            warnings.append(
                "Trailing protection is strongly active."
            )

            return {
                "Status": "TRAILING EXIT ARMED",
                "Exit Decision": "WATCH",
                "Profit Protected": True,
                "Profit Stage": profit_stage,
                "Protection Level": protection_level,
                "Current Profit %": round(
                    current_profit_percentage,
                    2
                ),
                "Peak Profit %": round(
                    peak_profit_percentage,
                    2
                ),
                "Retracement %": round(
                    retracement_percentage,
                    2
                ),
                "Peak Price": round(
                    peak_price,
                    4
                ),
                "Reasons": reasons,
                "Warnings": warnings
            }

        reasons.append(
            "Substantial profit remains supported."
        )

        return {
            "Status": "PROFIT PROTECTED",
            "Exit Decision": "HOLD",
            "Profit Protected": True,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    # -----------------------------------------
    # 14. STAGE 5 — 20%+
    # -----------------------------------------

    if weakness_count >= 2 and retracement_percentage >= 10:

        reasons.append(
            "Exceptional profit is established, but "
            "multiple supporting signals are weakening."
        )

        warnings.append(
            "Protecting capital and realised profit "
            "takes priority over chasing additional upside."
        )

        return {
            "Status": "EXIT — PROFIT PROTECTION",
            "Exit Decision": "EXIT",
            "Profit Protected": True,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    if retracement_percentage >= 20:

        reasons.append(
            "A significant portion of exceptional "
            "peak profit has been retraced."
        )

        warnings.append(
            "Adaptive trailing protection is active."
        )

        return {
            "Status": "TRAILING EXIT ARMED",
            "Exit Decision": "WATCH",
            "Profit Protected": True,
            "Profit Stage": profit_stage,
            "Protection Level": protection_level,
            "Current Profit %": round(
                current_profit_percentage,
                2
            ),
            "Peak Profit %": round(
                peak_profit_percentage,
                2
            ),
            "Retracement %": round(
                retracement_percentage,
                2
            ),
            "Peak Price": round(
                peak_price,
                4
            ),
            "Reasons": reasons,
            "Warnings": warnings
        }

    reasons.append(
        "Exceptional profit remains supported; "
        "continue monitoring closely."
    )

    return {
        "Status": "PROFIT PROTECTED",
        "Exit Decision": "HOLD",
        "Profit Protected": True,
        "Profit Stage": profit_stage,
        "Protection Level": protection_level,
        "Current Profit %": round(
            current_profit_percentage,
            2
        ),
        "Peak Profit %": round(
            peak_profit_percentage,
            2
        ),
        "Retracement %": round(
            retracement_percentage,
            2
        ),
        "Peak Price": round(
            peak_price,
            4
        ),
        "Reasons": reasons,
        "Warnings": warnings
    }
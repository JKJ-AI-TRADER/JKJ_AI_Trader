"""
JKJ AI Intraday Risk Engine v0.1

Wisdom Before Wealth.

A strong setup is not enough.

Every intraday trade must first define:

- Entry Price
- Stop Loss
- Risk Per Trade
- Target Price
- Risk to Reward Ratio

Capital protection comes before profit.
"""


import math


def _is_finite_number(value):
    """Accept finite int/float inputs but reject booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def analyse_intraday_risk(
    entry_price,
    stop_loss,
    target_price,
    setup_score,
    trading_allowed=True
):
    """
    Analyse whether an intraday trade has
    acceptable risk.

    Returns an explainable risk assessment.
    """

    reasons = []
    warnings = []

    # -----------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------

    if not isinstance(trading_allowed, bool):
        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID INPUT",
            "Risk Level": "HIGH",
            "Reasons": ["Trading Allowed flag must be a Boolean."],
            "Warnings": [],
        }

    if not trading_allowed:

        return {
            "Trade Allowed": False,
            "Risk Status": "MARKET NOT SUITABLE",
            "Risk Level": "HIGH",
            "Entry Price": entry_price,
            "Stop Loss": stop_loss,
            "Target Price": target_price,
            "Risk Percentage": 0,
            "Reward Percentage": 0,
            "Risk Reward Ratio": 0,
            "Reasons": [
                "The intraday market environment "
                "does not currently allow trading."
            ],
            "Warnings": []
        }

    numeric_values = {
        "Entry Price": entry_price,
        "Stop Loss": stop_loss,
        "Target Price": target_price,
        "Setup Score": setup_score,
    }
    invalid_fields = [
        field
        for field, value in numeric_values.items()
        if not _is_finite_number(value)
    ]

    if invalid_fields:
        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID INPUT",
            "Risk Level": "HIGH",
            "Reasons": [
                "Expected finite, non-Boolean numeric input(s): "
                + ", ".join(invalid_fields)
            ],
            "Warnings": [],
        }

    if entry_price <= 0:

        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID ENTRY",
            "Risk Level": "HIGH",
            "Reasons": [
                "Entry price must be greater than zero."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # CALCULATE RISK
    # -----------------------------------------

    if stop_loss <= 0:
        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID STOP LOSS",
            "Risk Level": "HIGH",
            "Reasons": ["Stop loss must be greater than zero."],
            "Warnings": [],
        }

    risk_amount = entry_price - stop_loss
    reward_amount = target_price - entry_price

    if risk_amount <= 0:

        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID STOP LOSS",
            "Risk Level": "HIGH",
            "Reasons": [
                "Stop loss must be below the entry "
                "price for a long trade."
            ],
            "Warnings": []
        }

    if reward_amount <= 0:

        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID TARGET",
            "Risk Level": "HIGH",
            "Reasons": [
                "Target price must be above the entry "
                "price for a long trade."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # PERCENTAGES
    # -----------------------------------------

    # Keep unrounded values for decisions; round only for reporting.
    risk_percentage_raw = (
        risk_amount / entry_price
    ) * 100

    reward_percentage_raw = (
        reward_amount / entry_price
    ) * 100

    risk_reward_ratio_raw = (
        reward_amount / risk_amount
    )

    if not all(
        math.isfinite(value)
        for value in (
            risk_percentage_raw,
            reward_percentage_raw,
            risk_reward_ratio_raw,
        )
    ):
        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID CALCULATION",
            "Risk Level": "HIGH",
            "Reasons": ["Calculated risk metrics are not finite."],
            "Warnings": [],
        }

    risk_percentage = round(risk_percentage_raw, 2)
    reward_percentage = round(reward_percentage_raw, 2)
    risk_reward_ratio = round(risk_reward_ratio_raw, 2)

    # -----------------------------------------
    # RISK CLASSIFICATION
    # -----------------------------------------

    if risk_percentage_raw > 2:

        risk_level = "HIGH"

        warnings.append(
            "Stop-loss risk exceeds the preferred "
            "2% intraday limit."
        )

    elif risk_percentage_raw > 1:

        risk_level = "MEDIUM"

        warnings.append(
            "Trade risk is above the preferred "
            "1% capital protection level."
        )

    else:

        risk_level = "LOW"

        reasons.append(
            "Stop-loss risk is within the preferred "
            "intraday range."
        )

    # -----------------------------------------
    # RISK / REWARD EVALUATION
    # -----------------------------------------

    if risk_reward_ratio_raw < 1.5:

        warnings.append(
            "Risk-to-reward ratio is below the "
            "preferred minimum of 1.5."
        )

    else:

        reasons.append(
            "Risk-to-reward ratio is acceptable."
        )

    # -----------------------------------------
    # SETUP QUALITY
    # -----------------------------------------

    if setup_score < 60:

        warnings.append(
            "Trade setup strength is not sufficient."
        )

    else:

        reasons.append(
            "Trade setup strength is acceptable."
        )

    # -----------------------------------------
    # FINAL TRADE DECISION
    # -----------------------------------------

    trade_allowed = True

    if risk_level == "HIGH":

        trade_allowed = False

    if risk_reward_ratio_raw < 1.5:

        trade_allowed = False

    if setup_score < 60:

        trade_allowed = False

    if trade_allowed:

        risk_status = "ACCEPTABLE"

        reasons.append(
            "The trade meets the minimum JKJ "
            "intraday risk requirements."
        )

    else:

        risk_status = "NOT ACCEPTABLE"

        warnings.append(
            "The trade should not be taken until "
            "risk conditions improve."
        )

    return {
        "Trade Allowed": trade_allowed,
        "Risk Status": risk_status,
        "Risk Level": risk_level,
        "Entry Price": round(entry_price, 2),
        "Stop Loss": round(stop_loss, 2),
        "Target Price": round(target_price, 2),
        "Risk Percentage": risk_percentage,
        "Reward Percentage": reward_percentage,
        "Risk Reward Ratio": risk_reward_ratio,
        "Reasons": reasons,
        "Warnings": warnings
    }